"""eICU builder tests: documented-PE cohort rules and offset handling."""

import pandas as pd

from scripts.build_eicu_documented_pe_cohort import (
    build_documented_pe_cohort,
    problem_leaf,
)
from scripts.build_eicu_sbp_filter import build_sbp_filter
from scripts.build_eicu_three_domain_matrix import standardize_minute_offsets


def patient_frame():
    return pd.DataFrame({
        "record_key": ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"],
        "person_key": ["person_a", "person_a", "person_b", "person_c", "person_d",
                       "person_e", "person_f", "person_g"],
        "hospital_key": ["h1", "h1", "h2", "h2", "h3", "h3", "h4", "h4"],
        "age_years": [60, 60, 70, 17, 55, 55, 80, 66],
        "hospital_admit_offset_minutes": [100, 50, 10, 5, 20, 20, 30, 40],
        "unit_type": ["MICU"] * 8,
    })


def diagnosis_frame():
    return pd.DataFrame({
        "record_key": ["s1", "s2", "s3", "s4", "s5", "s6"],
        "diagnosis_text": [
            "cardiovascular|pulmonary embolism",
            "cardiovascular|pulmonary embolism",
            "cardiovascular|r/o pulmonary embolism",
            "cardiovascular|pulmonary embolism",
            "cardiovascular|suspected pulmonary embolism",
            "cardiovascular|probable pulmonary embolism",
        ],
    })


def test_problem_leaf_uses_the_last_hierarchy_element():
    assert problem_leaf("Cardiovascular|Pulmonary Embolism") == "pulmonary embolism"


def test_cohort_requires_documented_pe_adult_and_excludes_negative_wording():
    cohort = build_documented_pe_cohort(patient_frame(), diagnosis_frame())
    assert set(cohort["record_key"]) == {"s1", "s2"}
    flags = cohort.set_index("record_key")
    assert flags.loc["s1", "pe_history_evidence"] is False or (
        flags.loc["s1", "pe_history_evidence"] == False)  # noqa: E712
    assert not cohort["negative_wording_only"].any()


def test_rule_out_suspected_and_probable_rows_are_flagged_not_admitted():
    cohort = build_documented_pe_cohort(patient_frame(), diagnosis_frame())
    assert "s3" not in set(cohort["record_key"])
    assert "s5" not in set(cohort["record_key"])
    assert "s6" not in set(cohort["record_key"])


def test_underage_and_undocumented_records_are_excluded():
    cohort = build_documented_pe_cohort(patient_frame(), diagnosis_frame())
    assert "s4" not in set(cohort["record_key"])   # age 17
    assert "s7" not in set(cohort["record_key"])   # no PE row


def test_first_eligible_stay_is_the_earliest_admission_per_patient():
    cohort = build_documented_pe_cohort(patient_frame(), diagnosis_frame())
    flags = cohort.set_index("record_key")
    assert flags.loc["s2", "first_eligible_stay"]
    assert not flags.loc["s1", "first_eligible_stay"]
    assert int(cohort["first_eligible_stay"].sum()) == 1


def test_past_history_never_creates_membership_but_is_recorded():
    history = pd.DataFrame({
        "record_key": ["s1", "s8"],
        "history_text": ["history of pulmonary embolism", "pulmonary embolism, resolved"],
    })
    cohort = build_documented_pe_cohort(patient_frame(), diagnosis_frame(), history)
    assert "s8" not in set(cohort["record_key"])
    flags = cohort.set_index("record_key")
    assert bool(flags.loc["s1", "pe_history_evidence"])


def test_sbp_filter_uses_minute_offsets_and_bounds():
    cohort = pd.DataFrame({"record_key": ["r1", "r2", "r3"]})
    periodic = pd.DataFrame({
        "record_key": ["r1", "r1", "r3"],
        "observed_offset_minutes": [60, 120, 30],
        "systolic_bp": [85, 95, 0],
    })
    aperiodic = pd.DataFrame({
        "record_key": ["r2", "r3"],
        "observed_offset_minutes": [30, 1500],
        "systolic_bp": [120, 110],
    })
    result = build_sbp_filter(cohort, periodic, aperiodic).set_index("record_key")

    assert result.loc["r1", "eligible_sbp_n"] == 2
    assert result.loc["r1", "sbp_below_90_n"] == 1
    assert not result.loc["r1", "sbp_filter_pass_zero_below_90"]
    assert result.loc["r1", "sbp_filter_pass_fewer_than_two_below_90"]
    assert result.loc["r1", "invasive_sbp_n"] == 2

    assert result.loc["r2", "sbp_filter_pass_zero_below_90"]
    assert result.loc["r2", "non_invasive_sbp_n"] == 1

    assert not result.loc["r3", "sbp_observable"]


def test_minute_offsets_are_converted_to_hours():
    events = pd.DataFrame({
        "record_key": ["r1", "r1"],
        "domain": ["lactate", "creatinine_delta"],
        "minutes_from_offset": [60, 1440],
        "value": [2.4, 1.4],
    })
    standard = standardize_minute_offsets(events)
    assert list(standard.columns) == ["record_key", "domain", "hours_from_index", "value"]
    assert list(standard["hours_from_index"]) == [1.0, 24.0]
