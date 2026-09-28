"""Aggregate regression locks for the v2 two-database release.

These constants are nonidentifying aggregate counts. They contain no record-level
material and exist only to detect analysis drift in the public pipeline.

The eICU locks follow the corrected ICU-stay selection rule: one record per
hospital admission, chosen by unit visit number. See
``docs/cohort_definitions.md``.
"""

import pytest

TOLERANCE = 0.02

MIMIC_SOURCE = {
    "source_records": 1337,
    "sbp_observable": 814,
    "sbp_filter_pass": 668,
    "distinct_patients": 651,
}

MIMIC_PRIMARY = {
    "records": 668,
    "depth": {0: 476, 1: 111, 2: 63, 3: 18},
    "evaluable": {"lactate": 98, "creatinine_delta": 105, "urine_output": 88},
    "evaluable_pct": {"lactate": 14.67, "creatinine_delta": 15.72, "urine_output": 13.17},
    "states": {"positive": 42, "fully_observed_negative": 13, "indeterminate": 613},
    "state_pct": {"positive": 6.29, "fully_observed_negative": 1.95, "indeterminate": 91.77},
    "complete_case": 18,
    "complete_case_pct": 2.69,
    "negative_reclassification": 613,
}

MIMIC_FIRST_ADMISSION = {
    "records": 651,
    "depth": {0: 461, 1: 110, 2: 62, 3: 18},
    "evaluable": {"lactate": 96, "creatinine_delta": 104, "urine_output": 88},
    "states": {"positive": 41, "fully_observed_negative": 13, "indeterminate": 597},
    "complete_case": 18,
}

MIMIC_EXTENDED_CREATININE = {
    "records": 668,
    "evaluable": 185,
    "evaluable_pct": 27.69,
    "true": 11,
    "true_pct": 1.65,
    "depth": {0: 433, 1: 123, 2: 88, 3: 24},
    "states": {"positive": 48, "fully_observed_negative": 17, "indeterminate": 603},
    "complete_case": 24,
}

EICU_SOURCE = {
    "pe_coded_stays": 2880,
    "documented_pe_adult_stays": 2680,
    "first_stay_per_hospital_admission": 2487,
    "sbp_observable": 2454,
    "sbp_filter_pass": 1266,
    "patients": 1240,
    "hospital_admissions": 2487,
    "patients_with_multiple_eligible_hospital_admissions": 68,
    "hospitals_documented": 182,
    "hospitals": 164,
}

EICU_PRIMARY = {
    "records": 1266,
    "depth": {0: 409, 1: 617, 2: 180, 3: 60},
    "evaluable": {"lactate": 186, "creatinine_delta": 221, "urine_output": 750},
    "evaluable_pct": {"lactate": 14.69, "creatinine_delta": 17.46, "urine_output": 59.24},
    "creatinine_true": 13,
    "creatinine_true_pct": 1.03,
    "states": {"positive": 207, "fully_observed_negative": 31, "indeterminate": 1028},
    "state_pct": {"positive": 16.35, "fully_observed_negative": 2.45, "indeterminate": 81.20},
    "complete_case": 60,
    "complete_case_pct": 4.74,
    "negative_reclassification": 1028,
}

EICU_EXTENDED_CREATININE = {
    "records": 1266,
    "evaluable": 745,
    "evaluable_pct": 58.85,
    "true": 34,
    "true_pct": 2.69,
    "depth": {0: 223, 1: 504, 2: 440, 3: 99},
    "states": {"positive": 218, "fully_observed_negative": 55, "indeterminate": 993},
    "complete_case": 99,
}

EICU_BROAD_SENSITIVITY = {
    "records": 1343,
    "depth": {0: 429, 1: 650, 2: 197, 3: 67},
    "evaluable": {"lactate": 207, "creatinine_delta": 244, "urine_output": 794},
    "states": {"positive": 223, "fully_observed_negative": 35, "indeterminate": 1085},
    "complete_case": 67,
}

EICU_SITE_SUMMARY = {
    "minimum_site_records": 20,
    "sites": 13,
    "records": 356,
    "all_three_evaluable_pct": {"median": 3.12, "iqr_low": 0.0, "iqr_high": 10.00,
                                "minimum": 0.0, "maximum": 22.73},
    "indeterminate_pct": {"median": 78.26, "iqr_low": 68.75, "iqr_high": 90.00,
                          "minimum": 54.55, "maximum": 95.65},
    "sites_with_zero_all_three_evaluable": 131,
    "sites_total": 164,
}

EICU_DESCRIPTORS = {
    "records": 1266,
    "age_mean": 61.34,
    "age_sd": 16.36,
    "age_median": 63.0,
    "age_iqr_low": 50.0,
    "age_iqr_high": 74.0,
    "age_minimum": 18.0,
    "age_maximum": 89.0,
    "female": 583,
    "female_pct": 46.05,
    "male": 682,
    "male_pct": 53.87,
    "sex_unknown": 1,
}

EICU_FIRST_STAY_SELECTION = {
    "hospital_admissions_with_multiple_eligible_icu_stays": 172,
    "admissions_where_earlier_stay_has_larger_hospital_admit_offset": 172,
    "frozen_legacy_rule_records": 1252,
    "frozen_legacy_overlap_with_corrected_rule": 1162,
    "corrected_minus_legacy_records": 1266,
}


def check_counts(block, keys=("records",)):
    for key in keys:
        assert block[key] > 0


def test_mimic_primary_locks():
    assert sum(MIMIC_PRIMARY["depth"].values()) == MIMIC_PRIMARY["records"]
    assert sum(MIMIC_PRIMARY["states"].values()) == MIMIC_PRIMARY["records"]
    assert set(MIMIC_PRIMARY["evaluable"]) == {"lactate", "creatinine_delta", "urine_output"}
    assert MIMIC_PRIMARY["negative_reclassification"] == MIMIC_PRIMARY["states"]["indeterminate"]
    for domain, pct in MIMIC_PRIMARY["evaluable_pct"].items():
        expected = 100 * MIMIC_PRIMARY["evaluable"][domain] / MIMIC_PRIMARY["records"]
        assert abs(pct - expected) < TOLERANCE
    for state, pct in MIMIC_PRIMARY["state_pct"].items():
        expected = 100 * MIMIC_PRIMARY["states"][state] / MIMIC_PRIMARY["records"]
        assert abs(pct - expected) < TOLERANCE


def test_mimic_source_and_current_population_locks():
    assert MIMIC_SOURCE["source_records"] == 1337
    assert MIMIC_SOURCE["sbp_observable"] == 814
    assert MIMIC_SOURCE["sbp_filter_pass"] == MIMIC_PRIMARY["records"]
    assert MIMIC_SOURCE["distinct_patients"] == MIMIC_FIRST_ADMISSION["records"]


def test_mimic_first_admission_sensitivity_is_close_to_the_primary_result():
    assert MIMIC_FIRST_ADMISSION["records"] < MIMIC_PRIMARY["records"]
    assert sum(MIMIC_FIRST_ADMISSION["depth"].values()) == MIMIC_FIRST_ADMISSION["records"]
    assert sum(MIMIC_FIRST_ADMISSION["states"].values()) == MIMIC_FIRST_ADMISSION["records"]
    primary = MIMIC_PRIMARY["states"]["indeterminate"] / MIMIC_PRIMARY["records"]
    first = MIMIC_FIRST_ADMISSION["states"]["indeterminate"] / MIMIC_FIRST_ADMISSION["records"]
    assert abs(primary - first) < 0.01


def test_mimic_extended_creatinine_sensitivity_is_monotone():
    assert MIMIC_EXTENDED_CREATININE["records"] == MIMIC_PRIMARY["records"]
    assert MIMIC_EXTENDED_CREATININE["evaluable"] > MIMIC_PRIMARY["evaluable"]["creatinine_delta"]
    assert MIMIC_EXTENDED_CREATININE["complete_case"] > MIMIC_PRIMARY["complete_case"]
    assert sum(MIMIC_EXTENDED_CREATININE["depth"].values()) == MIMIC_EXTENDED_CREATININE["records"]
    assert sum(MIMIC_EXTENDED_CREATININE["states"].values()) == MIMIC_EXTENDED_CREATININE["records"]


def test_eicu_source_and_primary_locks():
    assert EICU_SOURCE["pe_coded_stays"] == 2880
    assert EICU_SOURCE["documented_pe_adult_stays"] == 2680
    assert EICU_SOURCE["first_stay_per_hospital_admission"] == 2487
    assert EICU_SOURCE["sbp_observable"] == 2454
    assert EICU_SOURCE["sbp_filter_pass"] == EICU_PRIMARY["records"]
    assert EICU_SOURCE["sbp_filter_pass"] < EICU_SOURCE["sbp_observable"]
    assert EICU_SOURCE["patients"] < EICU_SOURCE["sbp_filter_pass"]
    assert EICU_SOURCE["hospitals"] == 164
    assert sum(EICU_PRIMARY["depth"].values()) == EICU_PRIMARY["records"]
    assert sum(EICU_PRIMARY["states"].values()) == EICU_PRIMARY["records"]
    assert EICU_PRIMARY["negative_reclassification"] == EICU_PRIMARY["states"]["indeterminate"]
    for domain, pct in EICU_PRIMARY["evaluable_pct"].items():
        expected = 100 * EICU_PRIMARY["evaluable"][domain] / EICU_PRIMARY["records"]
        assert abs(pct - expected) < TOLERANCE
    for state, pct in EICU_PRIMARY["state_pct"].items():
        expected = 100 * EICU_PRIMARY["states"][state] / EICU_PRIMARY["records"]
        assert abs(pct - expected) < TOLERANCE


def test_eicu_primary_uses_the_documented_pe_cohort_not_the_broad_cohort():
    assert EICU_PRIMARY["records"] == 1266
    assert EICU_PRIMARY["records"] != EICU_BROAD_SENSITIVITY["records"]
    assert EICU_BROAD_SENSITIVITY["records"] == 1343
    assert EICU_BROAD_SENSITIVITY["records"] > EICU_PRIMARY["records"]


def test_eicu_extended_creatinine_sensitivity_is_monotone():
    assert EICU_EXTENDED_CREATININE["records"] == EICU_PRIMARY["records"]
    assert EICU_EXTENDED_CREATININE["evaluable"] > EICU_PRIMARY["evaluable"]["creatinine_delta"]
    assert EICU_EXTENDED_CREATININE["true"] > EICU_PRIMARY["creatinine_true"]
    assert sum(EICU_EXTENDED_CREATININE["depth"].values()) == EICU_EXTENDED_CREATININE["records"]
    assert sum(EICU_EXTENDED_CREATININE["states"].values()) == EICU_EXTENDED_CREATININE["records"]
    assert EICU_EXTENDED_CREATININE["complete_case"] > EICU_PRIMARY["complete_case"]


def test_eicu_first_stay_selection_locks():
    selection = EICU_FIRST_STAY_SELECTION
    assert selection["hospital_admissions_with_multiple_eligible_icu_stays"] == 172
    assert (selection["admissions_where_earlier_stay_has_larger_hospital_admit_offset"]
            == selection["hospital_admissions_with_multiple_eligible_icu_stays"])
    assert selection["frozen_legacy_rule_records"] == 1252
    assert selection["corrected_minus_legacy_records"] == EICU_PRIMARY["records"]
    assert selection["frozen_legacy_overlap_with_corrected_rule"] < EICU_PRIMARY["records"]
    indeterminate_legacy = 1022 / selection["frozen_legacy_rule_records"]
    indeterminate_corrected = (EICU_PRIMARY["states"]["indeterminate"]
                               / EICU_PRIMARY["records"])
    assert abs(indeterminate_legacy - indeterminate_corrected) < 0.01


def test_eicu_site_summary_locks():
    summary = EICU_SITE_SUMMARY
    assert summary["sites"] == 13
    assert summary["records"] == 356
    assert summary["sites_with_zero_all_three_evaluable"] == 131
    assert summary["sites_total"] == 164
    all_three = summary["all_three_evaluable_pct"]
    assert all_three["minimum"] == 0.0
    assert all_three["iqr_low"] <= all_three["median"] <= all_three["iqr_high"] < all_three["maximum"]
    indeterminate = summary["indeterminate_pct"]
    assert indeterminate["minimum"] < indeterminate["median"] < indeterminate["maximum"]
    assert 50.0 <= indeterminate["minimum"]
    assert indeterminate["maximum"] <= 100.0


def test_eicu_descriptor_locks():
    descriptors = EICU_DESCRIPTORS
    total = descriptors["records"]
    assert descriptors["female"] + descriptors["male"] + descriptors["sex_unknown"] == total
    assert abs(descriptors["female_pct"] - 100 * descriptors["female"] / total) < TOLERANCE
    assert abs(descriptors["male_pct"] - 100 * descriptors["male"] / total) < TOLERANCE
    assert descriptors["age_iqr_low"] < descriptors["age_median"] < descriptors["age_iqr_high"]
    assert descriptors["age_minimum"] >= 18
    assert abs(descriptors["age_sd"] - 16.36) < TOLERANCE