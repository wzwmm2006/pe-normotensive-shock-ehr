"""Assemble the v2 aggregate outputs for the two-database study.

The output is aggregate only. The MIMIC and eICU cohorts are not clinically
identical: cross-database comparison describes transportability of structured
observability and is not a prevalence comparison.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import summarize_three_domain

CROSS_DATABASE_METRICS = [
    ("A_ASCERTAINMENT_DEPTH", "evaluable_domains_0", "depth_0_pct"),
    ("A_ASCERTAINMENT_DEPTH", "evaluable_domains_1", "depth_1_pct"),
    ("A_ASCERTAINMENT_DEPTH", "evaluable_domains_2", "depth_2_pct"),
    ("A_ASCERTAINMENT_DEPTH", "evaluable_domains_3", "depth_3_pct"),
    ("B_DOMAIN_EVALUABILITY", "lactate_evaluable", "lactate_evaluable_pct"),
    ("B_DOMAIN_EVALUABILITY", "creatinine_delta_evaluable", "creatinine_evaluable_pct"),
    ("B_DOMAIN_EVALUABILITY", "urine_output_evaluable", "urine_output_evaluable_pct"),
    ("C_THREE_STATE", "positive", "three_domain_positive_pct"),
    ("C_THREE_STATE", "fully_observed_negative", "fully_observed_negative_pct"),
    ("C_THREE_STATE", "indeterminate", "indeterminate_pct"),
    ("E_COMPLETE_CASE", "complete_case_evaluable", "complete_case_pct"),
    ("D_SIMULATED_MISSING_AS_FALSE", "negative_reclassification",
     "negative_reclassification_pct"),
]


def cross_database_row(database: str, frame: pd.DataFrame) -> list[dict]:
    summary = summarize_three_domain(frame, database)
    lookup = {(row.section, row.metric): row for row in summary.itertuples()}
    total = int(lookup[("0_COHORT", "records")].record_n)
    rows = [{"database": database, "metric": "analysis_records",
             "record_n": total, "denominator_n": total, "pct": 100.0}]
    for section, metric, label in CROSS_DATABASE_METRICS:
        record = lookup[(section, metric)]
        rows.append({"database": database, "metric": label,
                     "record_n": int(record.record_n),
                     "denominator_n": int(record.denominator_n),
                     "pct": float(record.pct)})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble aggregate two-database v2 outputs.")
    parser.add_argument("--mimic-matrix", type=Path, required=True,
                        help="MIMIC three-domain matrix.")
    parser.add_argument("--eicu-matrix", type=Path, required=True,
                        help="eICU three-domain matrix.")
    parser.add_argument("--mimic-sbp-filter", type=Path, default=None,
                        help="Optional MIMIC SBP-filter table for observability counts.")
    parser.add_argument("--eicu-sbp-filter", type=Path, default=None,
                        help="Optional eICU SBP-filter table for observability counts.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/v2_aggregate"),
                        help="Destination for the aggregate outputs.")
    args = parser.parse_args()

    matrices = {"MIMIC-IV": pd.read_csv(args.mimic_matrix),
                "eICU-CRD": pd.read_csv(args.eicu_matrix)}
    summary = pd.concat(
        [summarize_three_domain(frame, database) for database, frame in matrices.items()],
        ignore_index=True)
    summary.insert(0, "database", summary["cohort"])
    summary = summary.drop(columns=["cohort"])

    cross = pd.concat(
        [pd.DataFrame(cross_database_row(database, frame))
         for database, frame in matrices.items()],
        ignore_index=True)

    for database, path in (("MIMIC-IV", args.mimic_sbp_filter),
                           ("eICU-CRD", args.eicu_sbp_filter)):
        if path is None:
            continue
        sbp = pd.read_csv(path)
        total = len(sbp)
        for metric, column in (("sbp_observable_records", "sbp_observable"),
                               ("sbp_filter_pass_records",
                                "sbp_filter_pass_zero_below_90")):
            if column not in sbp.columns:
                continue
            count = int(sbp[column].astype(bool).sum())
            cross = pd.concat([cross, pd.DataFrame([{
                "database": database, "metric": metric, "record_n": count,
                "denominator_n": total,
                "pct": round(100 * count / total, 2) if total else 0.0}])],
                ignore_index=True)
    cross = cross.sort_values(["database", "metric"]).reset_index(drop=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_dir / "v2_cohort_summary.csv", index=False)
    cross.to_csv(args.output_dir / "v2_cross_database_table.csv", index=False)
    print(cross.to_string(index=False))
    print("\nCross-database comparison describes transportability, not equivalence.")


if __name__ == "__main__":
    main()
