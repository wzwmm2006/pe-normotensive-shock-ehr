"""eICU builder tests: cohort rules, stay selection, and offset handling.

The selection tests cover the repair made after the first-stay provenance
audit: the analysis unit is the earliest eligible ICU stay inside each hospital
admission, ordered by unit visit number, and hospital admission offset is never
used as chronology.
"""

import pandas as pd
import pytest

from scripts.build_eicu_documented_pe_cohort import (
    build,
    documented_pe_flags,
    first_stay_per_hospital_admission,
)
from scripts.build_eicu_sbp_filter import build_sbp_filter
from scripts.build_eicu_three_domain_matrix import standardize_minute_offsets


def patient_frame():
    return pd.DataFrame({
        "record_key": ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"],
        "person_key": ["person_a", "person_a", "person_b", "person_b", "person_c",
                       "person_d", "person_e", "person_f", "person_g"],
        "hospital_key": ["h1", "h1", "h2", "h2", "h3", "h3", "h4", "h4", "h5"],
        "hospital_admission_key": ["ha1", "ha1", "ha2", "ha3", "ha4", "ha5", "ha6",
                                   "ha7", "ha8"],
        "age_years": [60, 60, 70, 70, 17, 55, 80, 66, 44],
        "unit_visit_number": [2, 1, 1, 1, 1, 1, 1, 1, 1],
        # Deliberately reversed: the later ICU stay carries the less negative
        # offset, exactly as eICU documents it.
        "hospital_admit_offset_minutes": [-1440, -60, -30, -20, -10, -5, -8, -9, -7],
        "unit_type": ["MICU"] * 9,
    })


def diagnosis_frame():
    return pd.DataFrame({
        "record_key": ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"],
        "diagnosis_text": [
            "cardiovascular|pulmonary embolism",
            "cardiovascular|pulmonary embolism",
            "cardiovascular|pulmonary embolism",
            "cardiovascular|pulmonary embolism",
            "cardiovascular|pulmonary embolism",
            "cardiovascular|r/o pulmonary embolism",
            "cardiovascular|suspected pulmonary embolism",
            "cardiovascular|probable pulmonary embolism",
            "cardiovascular|pulmonary embolism|clinically suspected",
        ],
    })


def test_documented_pe_flags_match_the_study_wording_rules():
    flags = documented_pe_flags(diagnosis_frame()).set_index("record_key")
    assert bool(flags.loc["s1", "has_documented_pe"])
    assert not bool(flags.loc["s6", "has_documented_pe"])   # rule-out
    assert not bool(flags.loc["s7", "has_documented_pe"])   # leaf suspected
    assert not bool(flags.loc["s8", "has_documented_pe"])   # leaf probable
    # "clinically suspected" is not a rule-out, suspected-leaf or probable-leaf
    # entry, so it stays documented, exactly as in the frozen analysis.
    assert bool(flags.loc["s9", "has_documented_pe"])
    assert flags.loc["s6", "rule_out_rows"] == 1
    assert flags.loc["s7", "negative_wording_rows"] == 1


def test_selection_uses_unit_visit_number_not_hospital_admit_offset():
    patient = patient_frame()
    diagnosis = diagnosis_frame()
    cohort, _ = build(patient, diagnosis)
    selected = set(cohort.record_key)
    # person_a has two eligible ICU stays in one hospital admission; the first
    # ICU stay of that admission is s2 (visit 1), even though s1 has the larger
    # hospital admission offset.
    assert "s2" in selected
    assert "s1" not in selected


def test_selection_keeps_one_record_per_patient_hospital_admission():
    patient = patient_frame()
    cohort, flow = build(patient, diagnosis_frame())
    assert cohort.record_key.nunique() == len(cohort)
    assert (cohort.groupby(["person_key", "hospital_admission_key"]).size() == 1).all()
    # person_b has two separate hospital admissions, both documented.
    assert {"s3", "s4"} <= set(cohort.record_key)
    assert int(flow.set_index("stage").loc[
        "selected_first_stay_per_hospital_admission", "value"]) == len(cohort)


def test_selection_does_not_use_record_key_as_chronology():
    patient = patient_frame()
    diagnosis = diagnosis_frame()
    flipped = patient.copy()
    flipped["record_key"] = ["z9", "z8", "z7", "z6", "z5", "z4", "z3", "z2", "z1"]
    flipped_diagnosis = diagnosis.copy()
    flipped_diagnosis["record_key"] = flipped["record_key"]
    cohort, _ = build(flipped, flipped_diagnosis)
    # person_a keeps the visit-1 stay, whose record key is now z8.
    assert "z8" in set(cohort.record_key)
    assert "z9" not in set(cohort.record_key)


def test_underage_undocumented_and_history_only_records_are_excluded():
    history = pd.DataFrame({
        "record_key": ["s1", "s9"],
        "history_text": ["history of pulmonary embolism", "pulmonary embolism, remote"],
    })
    cohort, flow = build(patient_frame(), diagnosis_frame(), history)
    assert "s5" not in set(cohort.record_key)   # age 17
    assert "s6" not in set(cohort.record_key)   # rule-out only
    assert "s7" not in set(cohort.record_key)   # suspected leaf
    assert flow.set_index("stage").loc["stays_with_pe_in_past_history_only", "value"] == 0
    assert bool(cohort.set_index("record_key").loc["s9", "pe_in_past_history"])


def test_first_stay_helper_requires_a_unit_visit_number():
    patient = patient_frame().drop(columns=["unit_visit_number"])
    with pytest.raises(ValueError):
        build(patient, diagnosis_frame())


def test_first_stay_helper_is_idempotent():
    patient = patient_frame()
    eligible = patient.merge(documented_pe_flags(diagnosis_frame()), on="record_key")
    eligible = eligible[eligible.age_years >= 18]
    selected = first_stay_per_hospital_admission(eligible)
    again = first_stay_per_hospital_admission(selected)
    assert set(selected.record_key) == set(again.record_key)


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