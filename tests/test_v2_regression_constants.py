"""Aggregate regression locks for the v2 two-database release.

These constants are nonidentifying aggregate counts. They contain no record-level
material and exist only to detect analysis drift in the public pipeline.
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
    "documented_pe_adult_stays": 2680,
    "first_eligible_documented_stays": 2411,
    "sbp_observable": 2380,
    "sbp_filter_pass": 1252,
    "patients": 1252,
    "hospitals": 164,
}

EICU_PRIMARY = {
    "records": 1252,
    "depth": {0: 393, 1: 623, 2: 179, 3: 57},
    "evaluable": {"lactate": 179, "creatinine_delta": 215, "urine_output": 758},
    "evaluable_pct": {"lactate": 14.30, "creatinine_delta": 17.17, "urine_output": 60.54},
    "states": {"positive": 204, "fully_observed_negative": 26, "indeterminate": 1022},
    "state_pct": {"positive": 16.29, "fully_observed_negative": 2.08, "indeterminate": 81.63},
    "complete_case": 57,
    "complete_case_pct": 4.55,
    "negative_reclassification": 1022,
}

EICU_EXTENDED_CREATININE = {
    "records": 1252,
    "evaluable": 709,
    "evaluable_pct": 56.63,
    "true": 34,
    "true_pct": 2.72,
    "depth": {0: 225, 1: 500, 2: 435, 3: 92},
    "states": {"positive": 214, "fully_observed_negative": 47, "indeterminate": 991},
    "complete_case": 92,
}

EICU_BROAD_AGE_RESTRICTED = {
    "records": 1329,
    "depth": {0: 415, 1: 654, 2: 195, 3: 65},
    "evaluable": {"lactate": 201, "creatinine_delta": 238, "urine_output": 800},
    "states": {"positive": 219, "fully_observed_negative": 31, "indeterminate": 1079},
    "complete_case": 65,
}

EICU_SITE_SUMMARY = {
    "minimum_site_records": 20,
    "sites": 12,
    "records": 334,
    "all_three_evaluable_pct": {"median": 3.96, "iqr_low": 2.34, "iqr_high": 11.20,
                                "minimum": 0.0, "maximum": 18.60},
    "indeterminate_pct": {"median": 80.37, "iqr_low": 68.59, "iqr_high": 87.11,
                          "minimum": 60.00, "maximum": 95.45},
    "sites_with_zero_all_three_evaluable": 133,
    "sites_total": 164,
}

EICU_DESCRIPTORS = {
    "records": 1252,
    "age_mean": 61.44,
    "age_sd": 16.35,
    "age_median": 63.0,
    "age_iqr_low": 50.0,
    "age_iqr_high": 74.0,
    "age_minimum": 18.0,
    "age_maximum": 89.0,
    "female": 573,
    "female_pct": 45.77,
    "male": 678,
    "male_pct": 54.15,
    "sex_unknown": 1,
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
    assert MIMIC_EXTENDED_CREATININE["true"] > MIMIC_EXTENDED_CREATININE["true"] - 1
    assert sum(MIMIC_EXTENDED_CREATININE["depth"].values()) == MIMIC_EXTENDED_CREATININE["records"]
    assert sum(MIMIC_EXTENDED_CREATININE["states"].values()) == MIMIC_EXTENDED_CREATININE["records"]


def test_eicu_source_and_primary_locks():
    assert EICU_SOURCE["documented_pe_adult_stays"] == 2680
    assert EICU_SOURCE["first_eligible_documented_stays"] == 2411
    assert EICU_SOURCE["sbp_observable"] == 2380
    assert EICU_SOURCE["patients"] == EICU_SOURCE["sbp_filter_pass"]
    assert EICU_SOURCE["sbp_filter_pass"] == EICU_PRIMARY["records"]
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
    assert EICU_PRIMARY["records"] == 1252
    assert EICU_PRIMARY["records"] != EICU_BROAD_AGE_RESTRICTED["records"]
    assert EICU_BROAD_AGE_RESTRICTED["records"] == 1329


def test_eicu_extended_creatinine_sensitivity_is_monotone():
    assert EICU_EXTENDED_CREATININE["records"] == EICU_PRIMARY["records"]
    assert EICU_EXTENDED_CREATININE["evaluable"] > EICU_PRIMARY["evaluable"]["creatinine_delta"]
    assert sum(EICU_EXTENDED_CREATININE["depth"].values()) == EICU_EXTENDED_CREATININE["records"]
    assert sum(EICU_EXTENDED_CREATININE["states"].values()) == EICU_EXTENDED_CREATININE["records"]
    assert EICU_EXTENDED_CREATININE["complete_case"] > EICU_PRIMARY["complete_case"]


def test_eicu_site_summary_locks():
    summary = EICU_SITE_SUMMARY
    assert summary["sites"] == 12
    assert summary["records"] == 334
    assert summary["sites_with_zero_all_three_evaluable"] == 133
    assert summary["sites_total"] == 164
    all_three = summary["all_three_evaluable_pct"]
    assert all_three["minimum"] == 0.0
    assert all_three["iqr_low"] < all_three["median"] < all_three["iqr_high"] < all_three["maximum"]
    indeterminate = summary["indeterminate_pct"]
    assert indeterminate["minimum"] < indeterminate["median"] < indeterminate["maximum"]
    assert 60.0 <= indeterminate["minimum"]
    assert indeterminate["maximum"] <= 100.0


def test_eicu_descriptor_locks():
    descriptors = EICU_DESCRIPTORS
    assert descriptors["female"] + descriptors["male"] + descriptors["sex_unknown"] == 1252
    assert abs(descriptors["female_pct"] - 100 * descriptors["female"] / 1252) < TOLERANCE
    assert abs(descriptors["male_pct"] - 100 * descriptors["male"] / 1252) < TOLERANCE
    assert descriptors["age_iqr_low"] < descriptors["age_median"] < descriptors["age_iqr_high"]
    assert descriptors["age_minimum"] >= 18
    assert abs(descriptors["age_sd"] - 16.35) < TOLERANCE
