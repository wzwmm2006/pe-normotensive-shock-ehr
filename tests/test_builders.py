import pandas as pd

from scripts.build_authoritative_pe_index import build_index
from scripts.build_bp_ascertainment import build_bp_matrix
from scripts.build_strict_marker_matrix import build_matrix


def test_authoritative_index_uses_parent_report_time_and_first_positive_report():
    extension = pd.DataFrame(
        {"document_key": ["doc_late", "doc_early"], "acute_positive": [True, True]}
    )
    notes = pd.DataFrame(
        {
            "document_key": ["doc_late", "doc_early"],
            "person_key": ["person_a", "person_a"],
            "encounter_key": ["encounter_a", "encounter_a"],
            "report_time": [pd.Timestamp(10, unit="h"), pd.Timestamp(5, unit="h")],
        }
    )
    result = build_index(extension, notes)
    assert len(result) == 1
    assert result.iloc[0]["document_key"] == "doc_early"
    assert result.iloc[0]["index_time"] == pd.Timestamp(5, unit="h")


def test_bp_ascertainment_combines_sources_and_preserves_primary_rule():
    index = pd.DataFrame(
        {
            "person_key": ["person_a", "person_b"],
            "encounter_key": ["encounter_a", "encounter_b"],
            "index_time": [pd.Timestamp(0, unit="h"), pd.Timestamp(0, unit="h")],
        }
    )
    icu = pd.DataFrame(
        {
            "person_key": ["person_a", "person_a"],
            "encounter_key": ["encounter_a", "encounter_a"],
            "observed_time": [pd.Timestamp(1, unit="h"), pd.Timestamp(2, unit="h")],
            "systolic_bp": [88, 89],
        }
    )
    ed = pd.DataFrame(
        {
            "person_key": ["person_b"],
            "encounter_key": ["encounter_b"],
            "observed_time": [pd.Timestamp(3, unit="h")],
            "systolic_bp": [110],
        }
    )
    result = build_bp_matrix(index, icu, ed).set_index("encounter_key")
    assert not result.loc["encounter_a", "normotensive_primary"]
    assert result.loc["encounter_b", "normotensive_primary"]
    assert result.loc["encounter_b", "ed_sbp_n"] == 1
    assert result.loc["encounter_b", "icu_sbp_n"] == 0


def test_strict_marker_matrix_applies_thresholds_and_evaluability():
    cohort = pd.DataFrame({"record_key": ["A", "B"]})
    events = pd.DataFrame(
        [
            ("A", "lactate", 1, 2.4),
            ("A", "creatinine_delta", 1, 1.0),
            ("A", "creatinine_delta", 5, 1.4),
            ("A", "urine_output", 2, 600),
            ("A", "cardiac_index", 3, 2.4),
            ("B", "lactate", 1, 1.5),
            ("B", "creatinine_delta", 1, 1.0),
            ("B", "urine_output", 2, 900),
        ],
        columns=["record_key", "domain", "hours_from_index", "value"],
    )
    coverage = pd.DataFrame(
        {"record_key": ["A", "B"], "urine_coverage_hours": [24, None]}
    )
    result = build_matrix(cohort, events, coverage).set_index("record_key")
    assert result.loc["A"].to_dict() == {
        "lactate_state": "TRUE",
        "creatinine_delta_state": "TRUE",
        "urine_output_state": "TRUE",
        "cardiac_index_state": "UNKNOWN",
    }
    assert result.loc["B", "lactate_state"] == "FALSE"
    assert result.loc["B", "creatinine_delta_state"] == "UNKNOWN"
    assert result.loc["B", "urine_output_state"] == "UNKNOWN"
    assert result.loc["B", "cardiac_index_state"] == "UNKNOWN"
