"""Sensitivity analysis: extended pre-index creatinine baseline.

The primary creatinine rule is unchanged. The sensitivity additionally allows a
reference value from -24 h to 0 h relative to the index, provided the value used
for the later measurement is at most 24 h away. The sensitivity contains the
primary rule as a subset, so it can only increase evaluability.

This is a sensitivity analysis and never the primary result.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import (
    CREATININE_DELTA_POSITIVE_AT,
    FULLY_OBSERVED_NEGATIVE,
    INDETERMINATE,
    POSITIVE,
    annotate_matrix,
    build_three_domain_matrix,
    creatinine_delta_state,
)

SUMMARY_METRICS = ("full_observed_negative",)


def compare(
    record_keys: pd.Series, events: pd.DataFrame, coverage: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    primary = annotate_matrix(
        build_three_domain_matrix(record_keys, events, coverage, extended_baseline=False))
    extended = annotate_matrix(
        build_three_domain_matrix(record_keys, events, coverage, extended_baseline=True))
    detail = pd.DataFrame({
        "record_key": primary["record_key"],
        "creatinine_delta_state_primary": primary["creatinine_delta_state"],
        "creatinine_delta_state_extended": extended["creatinine_delta_state"],
        "three_domain_classification_primary": primary["three_domain_classification"],
        "three_domain_classification_extended": extended["three_domain_classification"],
        "complete_case_classification_primary": primary["complete_case_classification"],
        "complete_case_classification_extended": extended["complete_case_classification"],
    })
    detail["newly_evaluable"] = (
        detail["creatinine_delta_state_primary"].eq("UNKNOWN")
        & detail["creatinine_delta_state_extended"].ne("UNKNOWN"))
    detail["newly_true"] = (
        ~detail["creatinine_delta_state_primary"].eq("TRUE")
        & detail["creatinine_delta_state_extended"].eq("TRUE"))

    total = len(detail)
    rows = []

    def add(section: str, metric: str, value: int) -> None:
        rows.append({
            "section": section, "metric": metric, "record_n": int(value),
            "denominator_n": total, "pct": round(100 * value / total, 2) if total else 0.0,
        })

    add("creatinine_rule", "primary_evaluable",
        int(primary["creatinine_delta_state"].ne("UNKNOWN").sum()))
    add("creatinine_rule", "primary_true",
        int(primary["creatinine_delta_state"].eq("TRUE").sum()))
    add("creatinine_rule", "extended_evaluable",
        int(extended["creatinine_delta_state"].ne("UNKNOWN").sum()))
    add("creatinine_rule", "extended_true",
        int(extended["creatinine_delta_state"].eq("TRUE").sum()))
    add("creatinine_rule", "newly_evaluable", int(detail["newly_evaluable"].sum()))
    add("creatinine_rule", "newly_true", int(detail["newly_true"].sum()))
    add("creatinine_delta_threshold", "positive_at",
        int(CREATININE_DELTA_POSITIVE_AT))
    for label, frame in (("primary", primary), ("extended", extended)):
        counts = frame["three_domain_classification"].value_counts()
        add(f"three_state_{label}", "positive", int(counts.get(POSITIVE, 0)))
        add(f"three_state_{label}", "fully_observed_negative",
            int(counts.get(FULLY_OBSERVED_NEGATIVE, 0)))
        add(f"three_state_{label}", "indeterminate", int(counts.get(INDETERMINATE, 0)))
        add(f"complete_case_{label}", "complete_case",
            int(frame["complete_case_classification"].ne("NOT_CLASSIFIABLE").sum()))
    return detail, pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Creatinine extended-baseline sensitivity analysis.")
    parser.add_argument("--events", type=Path, required=True,
                        help="Events: record_key, domain, hours_from_index, value.")
    parser.add_argument("--coverage", type=Path, required=True,
                        help="Coverage: record_key, urine_coverage_hours.")
    parser.add_argument("--cohort", type=Path, default=None,
                        help="Optional cohort table; defaults to the events record keys.")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("outputs/creatinine_sensitivity"),
                        help="Local destination for the sensitivity outputs.")
    args = parser.parse_args()

    events = pd.read_csv(args.events)
    keys = (pd.read_csv(args.cohort)["record_key"] if args.cohort
            else events["record_key"].drop_duplicates())
    detail, summary = compare(pd.Series(keys).drop_duplicates(), events,
                              pd.read_csv(args.coverage))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "creatinine_sensitivity_records.csv", index=False)
    summary.to_csv(args.output_dir / "creatinine_sensitivity_summary.csv", index=False)
    print(summary.to_string(index=False))
    print("\nThe extended rule is a sensitivity analysis and never the primary result.")


if __name__ == "__main__":
    main()
