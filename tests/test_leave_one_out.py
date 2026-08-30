from scripts.phenotype_core import leave_one_marker_out


def record(lactate, creatinine, urine, cardiac):
    return {
        "lactate_state": lactate,
        "creatinine_delta_state": creatinine,
        "urine_output_state": urine,
        "cardiac_index_state": cardiac,
    }


def test_leave_one_out_counts_unique_positive_support():
    records = [
        record("TRUE", "FALSE", "FALSE", "UNKNOWN"),
        record("TRUE", "FALSE", "TRUE", "UNKNOWN"),
        record("FALSE", "FALSE", "TRUE", "UNKNOWN"),
        record("FALSE", "FALSE", "FALSE", "UNKNOWN"),
    ]
    result = {row["removed_marker"]: row for row in leave_one_marker_out(records)}
    assert result["lactate"]["positive_n"] == 3
    assert result["lactate"]["positives_lost_n"] == 1
    assert result["urine_output"]["positives_lost_n"] == 1
    assert result["creatinine_delta"]["positives_lost_n"] == 0
    assert result["cardiac_index"]["positives_lost_n"] == 0
