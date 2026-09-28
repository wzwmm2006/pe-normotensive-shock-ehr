"""Describe site-level structured observability for a multi-hospital cohort.

The per-site table is local working material and is not published: it is keyed
to source hospital identifiers. The published output is the aggregate
distribution of site-level observability, which carries no site identifier.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import (
    annotate_matrix,
    site_distribution_summary,
    site_level_table,
)

CLASSIFICATION_COLUMNS = {
    "three_domain_depth", "three_domain_classification",
    "simulated_missing_as_false_classification",
    "negative_reclassification_under_missing_as_false",
    "complete_case_classification", "missing_domain_burden",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise site-level three-domain observability.")
    parser.add_argument("--input", type=Path, required=True,
                        help="Matrix carrying a site key and the three per-domain state columns.")
    parser.add_argument("--site-column", default="site_key",
                        help="Column holding the anonymous site key (default: site_key).")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/site_level"),
                        help="Local destination for the site table and the published distribution.")
    parser.add_argument("--thresholds", type=int, nargs="+", default=[10, 20, 30],
                        help="Minimum site record counts to summarise.")
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    if CLASSIFICATION_COLUMNS - set(frame.columns):
        frame = annotate_matrix(frame)
    if args.site_column not in frame.columns:
        raise ValueError(f"Input requires the site column {args.site_column!r}")

    table = site_level_table(frame, site_column=args.site_column)
    summary = site_distribution_summary(table, thresholds=args.thresholds)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output_dir / "site_level_local.csv", index=False)
    summary.to_csv(args.output_dir / "site_level_distribution_summary.csv", index=False)
    print(summary.to_string(index=False))
    print("\nThe per-site table is local working material and must not be committed.")


if __name__ == "__main__":
    main()
