"""Three-state logic tests: TRUE / FALSE / UNKNOWN and their consequences."""

import pandas as pd

from scripts.phenotype_core import (
    APPARENT_NEGATIVE,
    INDETERMINATE,
    FULLY_OBSERVED_NEGATIVE,
    POSITIVE,
    ascertainment_depth,
    classify_three_domain,
    complete_case_classification,
    missing_domain_burden,
    negative_reclassification,
    simulate_missing_as_false,
    three_domain_states,
)


def record(lactate, creatinine, urine):
    return {
        "lactate_state": lactate,
        "creatinine_delta_state": creatinine,
        "urine_output_state": urine,
    }


def test_one_true_is_positive_even_with_unknowns():
    assert classify_three_domain(record("TRUE", "UNKNOWN", "UNKNOWN")) == POSITIVE


def test_all_false_is_fully_observed_negative():
    assert classify_three_domain(record("FALSE", "FALSE", "FALSE")) == FULLY_OBSERVED_NEGATIVE


def test_false_with_unknown_is_indeterminate():
    assert classify_three_domain(record("FALSE", "UNKNOWN", "UNKNOWN")) == INDETERMINATE


def test_all_unknown_is_indeterminate():
    assert classify_three_domain(record("UNKNOWN", "UNKNOWN", "UNKNOWN")) == INDETERMINATE


def test_missing_as_false_is_simulated_and_maps_unknown_to_false():
    assert simulate_missing_as_false(record("FALSE", "UNKNOWN", "UNKNOWN")) == APPARENT_NEGATIVE
    assert simulate_missing_as_false(record("UNKNOWN", "UNKNOWN", "UNKNOWN")) == APPARENT_NEGATIVE
    assert simulate_missing_as_false(record("TRUE", "UNKNOWN", "UNKNOWN")) == POSITIVE


def test_negative_reclassification_requires_simulated_negative_and_indeterminate():
    assert negative_reclassification(record("FALSE", "UNKNOWN", "UNKNOWN")) is True
    assert negative_reclassification(record("FALSE", "FALSE", "FALSE")) is False
    assert negative_reclassification(record("TRUE", "UNKNOWN", "UNKNOWN")) is False


def test_complete_case_requires_all_three_domains():
    assert complete_case_classification(record("TRUE", "UNKNOWN", "UNKNOWN")) == "NOT_CLASSIFIABLE"
    assert complete_case_classification(record("TRUE", "FALSE", "FALSE")) == POSITIVE
    assert complete_case_classification(record("FALSE", "FALSE", "FALSE")) == FULLY_OBSERVED_NEGATIVE


def test_depth_and_missing_burden_are_complementary():
    states = [
        ("UNKNOWN", "UNKNOWN", "UNKNOWN"),
        ("FALSE", "UNKNOWN", "UNKNOWN"),
        ("FALSE", "FALSE", "UNKNOWN"),
        ("FALSE", "FALSE", "FALSE"),
    ]
    for lactate, creatinine, urine in states:
        entry = record(lactate, creatinine, urine)
        assert ascertainment_depth(entry) + missing_domain_burden(entry) == 3


def test_synthetic_example_crosswalk_is_stable():
    frame = pd.read_csv("examples/synthetic_three_domain_example.csv")
    assert list(frame["record_key"]) == ["A", "B", "C", "D", "E"]
    expected = {
        "A": (POSITIVE, POSITIVE, False),
        "B": (FULLY_OBSERVED_NEGATIVE, APPARENT_NEGATIVE, False),
        "C": (INDETERMINATE, APPARENT_NEGATIVE, True),
        "D": (INDETERMINATE, APPARENT_NEGATIVE, True),
        "E": (POSITIVE, POSITIVE, False),
    }
    for entry in frame.to_dict("records"):
        key = entry["record_key"]
        assert classify_three_domain(entry) == expected[key][0]
        assert simulate_missing_as_false(entry) == expected[key][1]
        assert negative_reclassification(entry) is expected[key][2]


def test_domain_evaluators_use_thresholds_and_window_rules():
    states = three_domain_states(
        lactate_values=[1.2, 1.8],
        creatinine_hours=[1, 5],
        creatinine_values=[1.0, 1.1],
        urine_amounts=[900],
        urine_coverage_hours=24,
    )
    assert states == {
        "lactate_state": "FALSE",
        "creatinine_delta_state": "FALSE",
        "urine_output_state": "FALSE",
    }


def test_unavailable_measurement_is_unknown_not_false():
    states = three_domain_states()
    assert set(states.values()) == {"UNKNOWN"}
