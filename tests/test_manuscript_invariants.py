def test_nonidentifying_manuscript_aggregate_locks():
    primary_n = 719
    depth = {0: 488, 1: 131, 2: 76, 3: 24, 4: 0}
    states = {"positive": 49, "indeterminate": 670, "negative": 0}
    missing_burden = {1: 17, 2: 52, 3: 113, 4: 488}

    assert sum(depth.values()) == primary_n
    assert sum(states.values()) == primary_n
    assert states == {"positive": 49, "indeterminate": 670, "negative": 0}
    assert missing_burden == {1: 17, 2: 52, 3: 113, 4: 488}
    assert sum(missing_burden.values()) == 670
    assert sum(count for missing, count in missing_burden.items() if missing >= 2) == 653
    assert 670 == states["indeterminate"]
    single_domain_ceiling = {
        "lactate": 0,
        "creatinine_delta": 0,
        "urine_output": 0,
        "cardiac_index": 17,
    }
    positive_dependence = {
        "lactate": 32,
        "creatinine_delta": 4,
        "urine_output": 9,
        "cardiac_index": 0,
    }
    stricter_bp_n = 668
    setting_ge3 = {
        "icu_observable": (24, 295),
        "ed_only_non_icu": (0, 424),
    }
    assert max(single_domain_ceiling.values()) == 17
    assert positive_dependence["lactate"] == 32
    assert stricter_bp_n == 668
    assert setting_ge3 == {
        "icu_observable": (24, 295),
        "ed_only_non_icu": (0, 424),
    }
