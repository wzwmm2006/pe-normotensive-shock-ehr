"""Site-level aggregation tests."""

import pandas as pd

from scripts.phenotype_core import (
    annotate_matrix,
    site_distribution_summary,
    site_level_table,
)


def synthetic_matrix():
    rows = [
        ("s1", "TRUE", "FALSE", "TRUE"),
        ("s1", "FALSE", "FALSE", "FALSE"),
        ("s2", "UNKNOWN", "UNKNOWN", "UNKNOWN"),
        ("s2", "UNKNOWN", "UNKNOWN", "UNKNOWN"),
        ("s3", "FALSE", "FALSE", "FALSE"),
    ]
    frame = pd.DataFrame(rows, columns=["site_key", "lactate_state",
                                        "creatinine_delta_state", "urine_output_state"])
    frame.insert(0, "record_key", [f"r{i}" for i in range(len(frame))])
    return annotate_matrix(frame)


def test_site_level_table_counts_and_percentages():
    table = site_level_table(synthetic_matrix()).set_index("site_key")
    assert list(table.index) == ["s1", "s2", "s3"]
    assert table.loc["s1", "records"] == 2
    assert table.loc["s1", "all_three_evaluable_n"] == 2
    assert table.loc["s1", "all_three_evaluable_pct"] == 100.0
    assert table.loc["s1", "indeterminate_n"] == 0
    assert table.loc["s1", "three_domain_positive_n"] == 1
    assert table.loc["s2", "all_three_evaluable_n"] == 0
    assert table.loc["s2", "indeterminate_n"] == 2
    assert table.loc["s2", "indeterminate_pct"] == 100.0
    assert table.loc["s3", "urine_output_evaluable_n"] == 1


def test_site_distribution_summary_respects_thresholds():
    table = site_level_table(synthetic_matrix())
    summary = site_distribution_summary(table, thresholds=(1, 2, 3))
    counts = dict(zip(summary[summary["metric"] == "indeterminate_pct"]["minimum_site_records"],
                      summary[summary["metric"] == "indeterminate_pct"]["sites"]))
    assert counts == {1: 3, 2: 2, 3: 0}
    records = dict(zip(summary[summary["metric"] == "indeterminate_pct"]["minimum_site_records"],
                       summary[summary["metric"] == "indeterminate_pct"]["records"]))
    assert records == {1: 5, 2: 4, 3: 0}


def test_site_distribution_summary_reports_median_iqr_and_range():
    table = site_level_table(synthetic_matrix())
    summary = site_distribution_summary(table, thresholds=(1,))
    row = summary[summary["metric"] == "indeterminate_pct"].iloc[0]
    values = sorted(table["indeterminate_pct"])
    assert row["median"] == round(float(pd.Series(values).median()), 2)
    assert row["minimum"] == min(values)
    assert row["maximum"] == max(values)
    assert row["iqr_low"] <= row["median"] <= row["iqr_high"]


def test_site_table_never_enters_the_published_aggregate():
    table = site_level_table(synthetic_matrix())
    summary = site_distribution_summary(table, thresholds=(1,))
    for column in summary.columns:
        assert "site_key" not in column
        assert "hospital" not in column
