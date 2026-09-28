"""Classify a three-domain matrix under TRUE/FALSE/UNKNOWN semantics.

Writes a record-level crosswalk and an aggregate cohort summary. The
record-level output is local working material and must stay outside version
control, because it is keyed to records.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import annotate_matrix, summarize_three_domain

CLASSIFICATION_COLUMNS = [
    "three_domain_depth", "three_domain_classification",
    "simulated_missing_as_false_classification",
    "negative_reclassification_under_missing_as_false",
    "complete_case_classification", "missing_domain_burden",
]


def classify(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing = set(CLASSIFICATION_COLUMNS) - set(frame.columns)
    annotated = annotate_matrix(frame) if missing else frame.copy()
    if "cohort" in annotated.columns:
        parts = [summarize_three_domain(block, str(label))
                 for label, block in annotated.groupby("cohort", sort=True)]
        summary = pd.concat(parts, ignore_index=True)
    else:
        summary = summarize_three_domain(annotated, "all_records")
    return annotated, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify a three-domain matrix under three-state semantics.")
    parser.add_argument("--input", type=Path, required=True,
                        help="Three-domain matrix or a table with record_key and the three state columns.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/three_state"),
                        help="Local destination for the record crosswalk and the summary.")
    args = parser.parse_args()

    annotated, summary = classify(pd.read_csv(args.input))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    annotated.to_csv(args.output_dir / "record_classification_crosswalk.csv", index=False)
    summary.to_csv(args.output_dir / "three_state_summary.csv", index=False)
    print(summary.to_string(index=False))
    print("\nRecord-level output is local working material and must not be committed.")


if __name__ == "__main__":
    main()
