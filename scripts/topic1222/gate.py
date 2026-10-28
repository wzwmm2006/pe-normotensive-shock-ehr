"""Frozen-result gate for the released Topic1222 analysis.

The eight published metrics below are the frozen values reported in the
manuscript. ``run_gate`` recomputes them from the standardised inputs and compares
the recomputed values with the frozen ones. A release is only verified when every
row reports PASS.

The gate compares string renderings so that composite metrics such as
``4 of 36`` and ``43/13/612`` are checked exactly, without rounding.
"""

from dataclasses import dataclass

import pandas as pd

from .states import RULES, coverage_ladder

BASELINE_RULE = "B0_full24_any_event"
STRICTEST_RULE = "S3_span20_gap4"


@dataclass(frozen=True)
class FrozenMetric:
    """One frozen metric value for one database."""

    metric: str
    database: str
    frozen: str


FROZEN_METRICS = (
    FrozenMetric("eligible_records", "MIMIC-IV", "668"),
    FrozenMetric("eligible_records", "eICU-CRD", "1266"),
    FrozenMetric("b0_complete_case_records", "MIMIC-IV", "18"),
    FrozenMetric("b0_complete_case_records", "eICU-CRD", "60"),
    FrozenMetric("direct_positive_records", "MIMIC-IV", "36"),
    FrozenMetric("direct_positive_records", "eICU-CRD", "73"),
    FrozenMetric("b0_direct_positive_retained", "MIMIC-IV", "4 of 36"),
    FrozenMetric("b0_direct_positive_retained", "eICU-CRD", "21 of 73"),
    FrozenMetric("b0_three_state_positive_negative_unresolved", "MIMIC-IV", "43/13/612"),
    FrozenMetric("b0_three_state_positive_negative_unresolved", "eICU-CRD", "207/31/1028"),
    FrozenMetric("s3_complete_case_records", "MIMIC-IV", "15"),
    FrozenMetric("s3_complete_case_records", "eICU-CRD", "14"),
    FrozenMetric("s3_direct_positive_retained", "MIMIC-IV", "3 of 36"),
    FrozenMetric("s3_direct_positive_retained", "eICU-CRD", "6 of 73"),
    FrozenMetric("s3_three_state_positive_negative_unresolved", "MIMIC-IV", "38/12/618"),
    FrozenMetric("s3_three_state_positive_negative_unresolved", "eICU-CRD", "79/8/1179"),
)

METRIC_ORDER = tuple(dict.fromkeys(metric.metric for metric in FROZEN_METRICS))
DATABASE_ORDER = tuple(dict.fromkeys(metric.database for metric in FROZEN_METRICS))


def retention(rule_row):
    return str(int(rule_row["direct_positive_retained_N"])) + " of " + str(
        int(rule_row["direct_positive_N"])
    )


def three_state(rule_row):
    return "/".join(
        str(int(rule_row[key]))
        for key in ("positive_N", "negative_N", "unresolved_N")
    )


def extract_metrics(inputs):
    """Recompute the published metrics for every database in the inputs."""
    rows = []
    for database in DATABASE_ORDER:
        states = inputs.corrected_states(database)
        urine = inputs.urine_table(database)
        ladder = coverage_ladder(states, urine, database).set_index("rule")
        baseline = ladder.loc[BASELINE_RULE]
        strictest = ladder.loc[STRICTEST_RULE]
        rows.extend(
            [
                ("eligible_records", database, str(int(len(states)))),
                ("b0_complete_case_records", database,
                 str(int(baseline["complete_case_N"]))),
                ("direct_positive_records", database,
                 str(int(baseline["direct_positive_N"]))),
                ("b0_direct_positive_retained", database, retention(baseline)),
                ("b0_three_state_positive_negative_unresolved", database,
                 three_state(baseline)),
                ("s3_complete_case_records", database,
                 str(int(strictest["complete_case_N"]))),
                ("s3_direct_positive_retained", database, retention(strictest)),
                ("s3_three_state_positive_negative_unresolved", database,
                 three_state(strictest)),
            ]
        )
    computed = pd.DataFrame(rows, columns=["metric", "database", "computed"])
    computed["metric"] = pd.Categorical(computed["metric"], METRIC_ORDER, ordered=True)
    computed["database"] = pd.Categorical(
        computed["database"], DATABASE_ORDER, ordered=True
    )
    return computed.sort_values(["database", "metric"]).reset_index(drop=True)


def compare_metrics(computed):
    """Compare recomputed metrics with the frozen values."""
    frozen = pd.DataFrame(
        [
            {"metric": metric.metric, "database": metric.database,
             "frozen": metric.frozen}
            for metric in FROZEN_METRICS
        ]
    )
    merged = frozen.merge(computed, on=["metric", "database"], how="outer")
    merged["status"] = [
        "PASS" if str(left) == str(right) and not pd.isna(left) else "FAIL"
        for left, right in zip(merged["frozen"], merged["computed"])
    ]
    return merged


def run_gate(inputs):
    """Recompute the published metrics and compare them with the frozen values."""
    comparison = compare_metrics(extract_metrics(inputs))
    comparison = comparison[
        ["metric", "database", "frozen", "computed", "status"]
    ].reset_index(drop=True)
    return comparison


def gate_passed(comparison):
    """True when every frozen metric matches the recomputed value."""
    return bool(comparison["status"].eq("PASS").all())