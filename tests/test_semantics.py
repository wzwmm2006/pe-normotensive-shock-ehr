import pandas as pd

from scripts.phenotype_core import (
    classify_complete_case,
    classify_missing_as_false,
    classify_uncertainty_aware,
)


def row(lactate, creatinine, urine, cardiac):
    return {
        "lactate_state": lactate,
        "creatinine_delta_state": creatinine,
        "urine_output_state": urine,
        "cardiac_index_state": cardiac,
    }


def test_true_or_unknown_is_positive():
    record = row("TRUE", "UNKNOWN", "UNKNOWN", "UNKNOWN")
    assert classify_uncertainty_aware(record) == "POSITIVE"


def test_all_false_is_negative():
    record = row("FALSE", "FALSE", "FALSE", "FALSE")
    assert classify_uncertainty_aware(record) == "NEGATIVE"


def test_false_and_unknown_is_indeterminate():
    record = row("FALSE", "UNKNOWN", "UNKNOWN", "UNKNOWN")
    assert classify_uncertainty_aware(record) == "INDETERMINATE"


def test_all_unknown_is_indeterminate():
    record = row("UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN")
    assert classify_uncertainty_aware(record) == "INDETERMINATE"


def test_missing_as_false_behavior():
    record = row("FALSE", "UNKNOWN", "UNKNOWN", "UNKNOWN")
    assert classify_missing_as_false(record) == "NEGATIVE"


def test_complete_case_behavior():
    incomplete = row("TRUE", "UNKNOWN", "UNKNOWN", "UNKNOWN")
    complete = row("TRUE", "FALSE", "FALSE", "FALSE")
    assert classify_complete_case(incomplete) == "NOT_CLASSIFIABLE"
    assert classify_complete_case(complete) == "POSITIVE"


def test_public_synthetic_example_has_expected_crosswalk():
    data = pd.read_csv("examples/synthetic_marker_example.csv").set_index("record_key")
    records = data.to_dict("index")
    assert classify_uncertainty_aware(records["A"]) == "POSITIVE"
    assert classify_uncertainty_aware(records["B"]) == "NEGATIVE"
    assert classify_uncertainty_aware(records["C"]) == "INDETERMINATE"
    assert classify_uncertainty_aware(records["D"]) == "INDETERMINATE"
    assert classify_missing_as_false(records["C"]) == "NEGATIVE"
    assert classify_complete_case(records["A"]) == "NOT_CLASSIFIABLE"
