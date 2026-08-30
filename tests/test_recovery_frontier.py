from scripts.phenotype_core import optimized_recovery_frontier, recovery_scenarios


def record(lactate, creatinine, urine, cardiac):
    return {
        "lactate_state": lactate,
        "creatinine_delta_state": creatinine,
        "urine_output_state": urine,
        "cardiac_index_state": cardiac,
    }


def test_recovery_frontier_uses_unknown_domain_subsets():
    records = [
        record("FALSE", "FALSE", "FALSE", "UNKNOWN"),
        record("FALSE", "FALSE", "UNKNOWN", "UNKNOWN"),
        record("FALSE", "UNKNOWN", "UNKNOWN", "UNKNOWN"),
        record("UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"),
    ]
    single = recovery_scenarios(records, 1)
    cardiac = next(row for row in single if row["restored_domains"] == "cardiac_index")
    assert cardiac["recoverable_n"] == 1

    pairwise = recovery_scenarios(records, 2)
    urine_cardiac = next(
        row for row in pairwise if row["restored_domains"] == "urine_output;cardiac_index"
    )
    assert urine_cardiac["recoverable_n"] == 2

    frontier = optimized_recovery_frontier(records)
    assert [row["recoverable_n"] for row in frontier] == [1, 2, 3, 4]
