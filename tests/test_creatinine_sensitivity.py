"""Creatinine timing sensitivity tests."""

import pandas as pd
import pytest

from scripts.phenotype_core import creatinine_delta_state, creatinine_delta_value
from scripts.run_creatinine_timing_sensitivity import compare


def test_primary_rule_requires_two_distinct_in_window_values():
    assert creatinine_delta_value([1], [1.0]) is None
    assert creatinine_delta_state([1], [1.0]) == "UNKNOWN"
    assert creatinine_delta_value([1, 5], [1.0, 1.4]) == pytest.approx(0.4)
    assert creatinine_delta_state([1, 5], [1.0, 1.4]) == "TRUE"
    assert creatinine_delta_state([1, 5], [1.0, 1.2]) == "FALSE"


def test_measurements_outside_the_window_do_not_score():
    assert creatinine_delta_state([30, 40], [1.0, 1.9]) == "UNKNOWN"
    assert creatinine_delta_state([-6, -2], [1.0, 1.9], extended_baseline=True) == "UNKNOWN"


def test_pre_index_baseline_is_a_sensitivity_only():
    hours, values = [-6, 4], [1.0, 1.4]
    assert creatinine_delta_state(hours, values) == "UNKNOWN"
    assert creatinine_delta_state(hours, values, extended_baseline=True) == "TRUE"


def test_pair_span_limit_is_enforced():
    assert creatinine_delta_state([-20, 5], [1.0, 1.9], extended_baseline=True) == "UNKNOWN"
    assert creatinine_delta_state([-19, 5], [1.0, 1.9], extended_baseline=True) == "TRUE"


def test_extended_rule_contains_the_primary_rule():
    cases = [
        ([1, 5], [1.0, 1.4]),
        ([1, 5], [1.0, 1.2]),
        ([-6, 4], [1.0, 1.4]),
        ([-2, 3], [1.4, 1.0]),
        ([2], [2.0]),
        ([], []),
    ]
    for hours, values in cases:
        primary = creatinine_delta_state(hours, values)
        extended = creatinine_delta_state(hours, values, extended_baseline=True)
        if primary == "TRUE":
            assert extended == "TRUE"
        if primary != "UNKNOWN":
            assert extended != "UNKNOWN"


def synthetic_inputs():
    keys = pd.Series(["r1", "r2", "r3"])
    events = pd.DataFrame(
        [
            ("r1", "creatinine_delta", 1, 1.0),
            ("r1", "creatinine_delta", 5, 1.4),
            ("r2", "creatinine_delta", -6, 1.0),
            ("r2", "creatinine_delta", 4, 1.6),
            ("r3", "lactate", 2, 3.0),
        ],
        columns=["record_key", "domain", "hours_from_index", "value"],
    )
    coverage = pd.DataFrame({"record_key": ["r1", "r2", "r3"],
                             "urine_coverage_hours": [24, 24, 24]})
    return keys, events, coverage


def test_sensitivity_comparison_summary_arithmetic():
    keys, events, coverage = synthetic_inputs()
    detail, summary = compare(keys, events, coverage)
    lookup = {(row.section, row.metric): int(row.record_n) for row in summary.itertuples()}

    assert lookup[("creatinine_rule", "primary_evaluable")] == 1
    assert lookup[("creatinine_rule", "extended_evaluable")] == 2
    assert lookup[("creatinine_rule", "newly_evaluable")] == 1
    assert lookup[("creatinine_rule", "primary_true")] == 1
    assert lookup[("creatinine_rule", "extended_true")] == 2
    assert lookup[("creatinine_rule", "newly_true")] == 1
    assert lookup[("three_state_primary", "positive")] == 2
    assert lookup[("three_state_extended", "positive")] == 3
    assert lookup[("complete_case_primary", "complete_case")] == 0

    assert len(detail) == 3
    assert detail["newly_evaluable"].sum() == 1
