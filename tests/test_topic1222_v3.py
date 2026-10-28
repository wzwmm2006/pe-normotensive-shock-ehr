"""Correction and regression tests for the released v3.0.0 analysis module.

The module under test is ``scripts.topic1222``. Every input used here is either
the invented synthetic contract in ``examples/`` or a small frame written to a
temporary directory, so the tests never touch a restricted source table.

One test locks the published metrics as literal constants, so a silent change to
``scripts.topic1222.gate`` cannot make the release gate pass on wrong numbers.
Four further tests pin the four corrections that separate this implementation
from the historical v2.0.2 code. The synthetic contract necessarily reports FAIL
on the frozen comparison, because it is a format sample and not the authorized
extract; the CLI test asserts exactly that behaviour.
"""

import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd

from scripts.topic1222 import (
    FROZEN_METRICS,
    apply_urine_rule,
    classify_records,
    coverage_ladder,
    creatinine_delta_state,
    creatinine_delta_value,
    full_window_covered,
    load_inputs,
    three_domain_crosstab,
    urine_rule_eligibility,
)
from scripts.topic1222.contract import InputPaths

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_MATRIX = ROOT / "examples" / "synthetic_contract_matrix.csv"
EXAMPLE_LABS = ROOT / "examples" / "synthetic_contract_labs.csv"

B0 = "B0_full24_any_event"
S3 = "S3_span20_gap4"

PUBLISHED = {
    ("eligible_records", "MIMIC-IV"): "668",
    ("eligible_records", "eICU-CRD"): "1266",
    ("b0_complete_case_records", "MIMIC-IV"): "18",
    ("b0_complete_case_records", "eICU-CRD"): "60",
    ("direct_positive_records", "MIMIC-IV"): "36",
    ("direct_positive_records", "eICU-CRD"): "73",
    ("b0_direct_positive_retained", "MIMIC-IV"): "4 of 36",
    ("b0_direct_positive_retained", "eICU-CRD"): "21 of 73",
    ("b0_three_state_positive_negative_unresolved", "MIMIC-IV"): "43/13/612",
    ("b0_three_state_positive_negative_unresolved", "eICU-CRD"): "207/31/1028",
    ("s3_complete_case_records", "MIMIC-IV"): "15",
    ("s3_complete_case_records", "eICU-CRD"): "14",
    ("s3_direct_positive_retained", "MIMIC-IV"): "3 of 36",
    ("s3_direct_positive_retained", "eICU-CRD"): "6 of 73",
    ("s3_three_state_positive_negative_unresolved", "MIMIC-IV"): "38/12/618",
    ("s3_three_state_positive_negative_unresolved", "eICU-CRD"): "79/8/1179",
}

URINE_FIELDS = (
    "records_valid_in_window",
    "first_hours",
    "last_hours",
    "max_gap_hours",
    "observed_span_hours",
    "total_ml",
    "unit_window_minutes",
)


def example_inputs():
    return load_inputs(InputPaths(matrix=EXAMPLE_MATRIX, labs=EXAMPLE_LABS))


def urine_frame(minutes, complete=None, index=("R1",)):
    frame = pd.DataFrame(
        {
            "records_valid_in_window": [24.0],
            "first_hours": [1.0],
            "last_hours": [23.0],
            "max_gap_hours": [2.0],
            "observed_span_hours": [22.0],
            "total_ml": [500.0],
            "unit_window_minutes": [minutes],
        },
        index=list(index),
    )
    if complete is not None:
        frame["window_complete"] = pd.Series([complete], index=list(index), dtype="boolean")
    return frame


def test_published_metrics_are_locked_to_the_manuscript_values():
    observed = {(metric.metric, metric.database): metric.frozen for metric in FROZEN_METRICS}
    assert observed == PUBLISHED


def test_correction_1_creatinine_boundary_is_compared_in_decimal():
    hours = [1.0, 8.0]
    values = [0.4, 0.7]
    # Binary floating point misses the inclusive boundary this correction targets.
    assert 0.7 - 0.4 < 0.3
    assert creatinine_delta_value(hours, values) == Decimal("0.3")
    assert creatinine_delta_state(hours, values) == "TRUE"
    # A rise that genuinely stays below the threshold is still negative.
    assert creatinine_delta_state([1.0, 8.0], [0.4, 0.69]) == "FALSE"


def test_correction_2_two_stays_of_one_person_remain_two_records(tmp_path):
    stays = [
        ("S1", [24.0, 1.0, 23.0, 2.0, 22.0, 400.0, 2880.0]),
        ("S2", [24.0, 1.0, 23.0, 2.0, 22.0, 900.0, 2880.0]),
    ]
    rows = []
    for key, urine in stays:
        for domain in ("lactate", "creatinine_delta", "urine_output"):
            row = {
                "database": "eICU-CRD",
                "record_key": key,
                "domain": domain,
                "state": "UNKNOWN",
                # Both stays belong to the same source person. The analysis unit
                # is the stay, so this column must never merge the two records.
                "source_person": "P1",
            }
            if domain == "urine_output":
                for name, value in zip(URINE_FIELDS, urine):
                    row[name] = value
            rows.append(row)

    matrix = tmp_path / "domain_state_matrix.csv"
    labs = tmp_path / "lab_series.csv"
    pd.DataFrame(rows).to_csv(matrix, index=False)
    pd.DataFrame(
        [{"database": "eICU-CRD", "record_key": "S1", "analyte": "lactate",
          "offset_hours": 2.0, "value": 1.0}]
    ).to_csv(labs, index=False)

    inputs = load_inputs(InputPaths(matrix=matrix, labs=labs))
    states = inputs.corrected_states("eICU-CRD")
    ladder = coverage_ladder(states, inputs.urine_table("eICU-CRD"), "eICU-CRD")

    assert list(states.index) == ["S1", "S2"]
    assert set(ladder["denominator_N"]) == {2}
    assert set(ladder["urine_evaluable_N"]) == {2}


def test_correction_3_every_rule_resets_both_urine_states():
    inputs = example_inputs()
    states = inputs.corrected_states("MIMIC-IV")
    urine = inputs.urine_table("MIMIC-IV")
    baseline = apply_urine_rule(states, urine, B0)
    strictest = apply_urine_rule(states, urine, S3)

    # A2 is a negative record at B0 and A3 a positive one; both lose their state.
    assert baseline.loc["A2", "urine_output"] == "FALSE"
    assert strictest.loc["A2", "urine_output"] == "UNKNOWN"
    assert baseline.loc["A3", "urine_output"] == "TRUE"
    assert strictest.loc["A3", "urine_output"] == "UNKNOWN"

    eligible = urine_rule_eligibility(urine)[S3]
    assert (strictest.loc[~eligible, "urine_output"] == "UNKNOWN").all()
    assert (strictest.loc[eligible, "urine_output"] != "UNKNOWN").all()

    # The three-state classification follows the reset urine state.
    assert classify_records(baseline).loc["A2"] == "NEGATIVE"
    assert classify_records(strictest).loc["A2"] == "UNRESOLVED"
    assert classify_records(baseline).loc["A3"] == "POSITIVE"
    assert classify_records(strictest).loc["A3"] == "UNRESOLVED"


def test_correction_4_the_24_hour_window_is_1440_minutes():
    assert bool(full_window_covered(urine_frame(1439.0)).loc["R1"]) is False
    assert bool(full_window_covered(urine_frame(1440.0)).loc["R1"]) is True
    assert bool(full_window_covered(urine_frame(2880.0)).loc["R1"]) is True
    # An explicit coverage flag takes precedence over the summed duration.
    assert bool(full_window_covered(urine_frame(60.0, complete=True)).loc["R1"]) is True
    assert bool(full_window_covered(urine_frame(2880.0, complete=False)).loc["R1"]) is False


def test_example_contract_loads_and_crosstabs_partition_records():
    matrix = pd.read_csv(EXAMPLE_MATRIX)
    labs = pd.read_csv(EXAMPLE_LABS)
    assert len(matrix) <= 50
    assert len(labs) <= 50
    inputs = example_inputs()
    assert inputs.databases == ("MIMIC-IV", "eICU-CRD")
    for database in inputs.databases:
        states = inputs.corrected_states(database)
        urine = inputs.urine_table(database)
        crosstab = three_domain_crosstab(states, urine, database)
        assert crosstab.groupby("rule")["N"].sum().eq(len(states)).all()


def test_reproduction_cli_reports_a_failed_comparison_on_the_sample(tmp_path):
    output = tmp_path / "gate"
    relaxed = subprocess.run(
        [
            sys.executable, "-m", "scripts.topic1222.reproduce",
            "--matrix", str(EXAMPLE_MATRIX),
            "--labs", str(EXAMPLE_LABS),
            "--output-dir", str(output),
            "--allow-mismatch",
        ],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert relaxed.returncode == 0, relaxed.stderr
    assert "REPRODUCTION GATE  : FAILED" in relaxed.stdout
    table = pd.read_csv(output / "reproduction_gate.csv")
    assert list(table.columns) == ["metric", "database", "frozen", "computed", "status"]
    assert len(table) == len(PUBLISHED)
    assert set(table["status"]) == {"FAIL"}

    strict = subprocess.run(
        [
            sys.executable, "-m", "scripts.topic1222.reproduce",
            "--matrix", str(EXAMPLE_MATRIX),
            "--labs", str(EXAMPLE_LABS),
        ],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert strict.returncode == 1
    assert "REPRODUCTION GATE  : FAILED" in strict.stdout


def test_reproduction_cli_reports_a_broken_contract(tmp_path):
    broken = tmp_path / "lab_series.csv"
    broken.write_text(
        "database,record_key,analyte\nMIMIC-IV,A1,lactate\n", encoding="utf-8"
    )
    result = subprocess.run(
        [
            sys.executable, "-m", "scripts.topic1222.reproduce",
            "--matrix", str(EXAMPLE_MATRIX),
            "--labs", str(broken),
        ],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 2
    assert "INPUT CONTRACT ERROR" in result.stderr