"""MIMIC builder tests: cohort index, blood-pressure filter, three-domain matrix."""

import pandas as pd

from scripts.build_mimic_pe_index import build_pe_index
from scripts.build_mimic_sbp_filter import build_sbp_filter
from scripts.phenotype_core import build_three_domain_matrix


def test_index_uses_the_earliest_positive_parent_report():
    extension = pd.DataFrame(
        {"document_key": ["late", "early", "negative"],
         "acute_positive": [True, True, False]}
    )
    radiology = pd.DataFrame(
        {
            "document_key": ["late", "early", "negative"],
            "person_key": ["person_a"] * 3,
            "encounter_key": ["encounter_a"] * 3,
            "report_time": [pd.Timestamp(20, unit="h"), pd.Timestamp(6, unit="h"),
                            pd.Timestamp(2, unit="h")],
        }
    )
    index = build_pe_index(extension, radiology)
    assert len(index) == 1
    assert index.iloc[0]["document_key"] == "early"
    assert index.iloc[0]["index_time"] == pd.Timestamp(6, unit="h")


def test_sbp_filter_combines_ed_and_icu_and_keeps_provenance():
    index = pd.DataFrame({
        "person_key": ["person_a", "person_b", "person_c"],
        "encounter_key": ["encounter_a", "encounter_b", "encounter_c"],
        "index_time": [pd.Timestamp(0, unit="h")] * 3,
    })
    icu = pd.DataFrame({
        "person_key": ["person_a", "person_a"],
        "encounter_key": ["encounter_a"] * 2,
        "observed_time": [pd.Timestamp(1, unit="h"), pd.Timestamp(2, unit="h")],
        "systolic_bp": [88, 89],
    })
    ed = pd.DataFrame({
        "person_key": ["person_b", "person_c"],
        "encounter_key": ["encounter_b", "encounter_c"],
        "observed_time": [pd.Timestamp(3, unit="h"), pd.Timestamp(30, unit="h")],
        "systolic_bp": [110, 95],
    })
    result = build_sbp_filter(index, icu, ed).set_index("encounter_key")

    assert result.loc["encounter_a", "sbp_observable"]
    assert result.loc["encounter_a", "sbp_below_90_n"] == 2
    assert not result.loc["encounter_a", "sbp_filter_pass_zero_below_90"]
    assert not result.loc["encounter_a", "sbp_filter_pass_fewer_than_two_below_90"]
    assert result.loc["encounter_a", "icu_sbp_n"] == 2

    assert result.loc["encounter_b", "sbp_filter_pass_zero_below_90"]
    assert result.loc["encounter_b", "ed_sbp_n"] == 1
    assert result.loc["encounter_b", "icu_sbp_n"] == 0

    assert not result.loc["encounter_c", "sbp_observable"]
    assert not result.loc["encounter_c", "sbp_filter_pass_zero_below_90"]


def test_sbp_filter_applies_plausibility_bounds_and_window():
    index = pd.DataFrame({
        "person_key": ["person_a"],
        "encounter_key": ["encounter_a"],
        "index_time": [pd.Timestamp(0, unit="h")],
    })
    icu = pd.DataFrame({
        "person_key": ["person_a"] * 4,
        "encounter_key": ["encounter_a"] * 4,
        "observed_time": [pd.Timestamp(1, unit="h"), pd.Timestamp(2, unit="h"),
                          pd.Timestamp(3, unit="h"), pd.Timestamp(40, unit="h")],
        "systolic_bp": [0, 420, 120, 80],
    })
    ed = pd.DataFrame(columns=["person_key", "encounter_key", "observed_time", "systolic_bp"])
    result = build_sbp_filter(index, icu, ed).set_index("encounter_key")
    assert result.loc["encounter_a", "eligible_sbp_n"] == 1
    assert result.loc["encounter_a", "sbp_filter_pass_zero_below_90"]


def test_three_domain_matrix_applies_thresholds_and_evaluability():
    cohort = pd.DataFrame({"record_key": ["A", "B", "C"]})
    events = pd.DataFrame(
        [
            ("A", "lactate", 1, 2.4),
            ("A", "creatinine_delta", 1, 1.0),
            ("A", "creatinine_delta", 5, 1.4),
            ("A", "urine_output", 2, 600),
            ("B", "lactate", 1, 1.5),
            ("B", "creatinine_delta", 1, 1.0),
            ("B", "urine_output", 2, 900),
            ("C", "lactate", 30, 3.0),
        ],
        columns=["record_key", "domain", "hours_from_index", "value"],
    )
    coverage = pd.DataFrame({"record_key": ["A", "B", "C"],
                             "urine_coverage_hours": [24, None, 24]})
    matrix = build_three_domain_matrix(cohort["record_key"], events, coverage)
    result = matrix.set_index("record_key")

    assert result.loc["A", "lactate_state"] == "TRUE"
    assert result.loc["A", "creatinine_delta_state"] == "TRUE"
    assert result.loc["A", "urine_output_state"] == "TRUE"
    assert result.loc["A", "three_domain_depth"] == 3
    assert result.loc["A", "three_domain_classification"] == "POSITIVE"

    assert result.loc["B", "lactate_state"] == "FALSE"
    assert result.loc["B", "creatinine_delta_state"] == "UNKNOWN"
    assert result.loc["B", "urine_output_state"] == "UNKNOWN"
    assert result.loc["B", "three_domain_classification"] == "INDETERMINATE"

    assert result.loc["C", "lactate_state"] == "UNKNOWN"
    assert result.loc["C", "three_domain_depth"] == 0

    assert set(result["cardiac_index_boundary_state"]) == {"UNKNOWN"}
