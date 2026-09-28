"""Build the eICU three-domain structured-observability matrix.

Events are supplied with eICU minute offsets from ICU admission and converted to
hours here. Urine-output amounts must already be restricted to the single
intakeOutput documentation channel during local standardization.

Events columns: record_key, domain, minutes_from_offset, value
Coverage columns: record_key, urine_coverage_hours
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import build_three_domain_matrix

EVENT_COLUMNS = {"record_key", "domain", "minutes_from_offset", "value"}
MINUTES_PER_HOUR = 60.0


def standardize_minute_offsets(events: pd.DataFrame) -> pd.DataFrame:
    """Convert eICU minute offsets into hours relative to the ICU admission index."""
    if not EVENT_COLUMNS.issubset(events.columns):
        raise ValueError(f"Events input requires columns: {sorted(EVENT_COLUMNS)}")
    result = events[sorted(EVENT_COLUMNS)].copy()
    result["hours_from_index"] = pd.to_numeric(
        result["minutes_from_offset"], errors="coerce") / MINUTES_PER_HOUR
    return result[["record_key", "domain", "hours_from_index", "value"]]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the eICU three-domain TRUE/FALSE/UNKNOWN matrix.")
    parser.add_argument("--cohort", type=Path, required=True,
                        help="SBP-filtered cohort to score; requires record_key.")
    parser.add_argument("--events", type=Path, required=True,
                        help="Standardized events: record_key, domain, minutes_from_offset, value.")
    parser.add_argument("--coverage", type=Path, required=True,
                        help="Urine observation coverage: record_key, urine_coverage_hours.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination CSV for the three-domain matrix.")
    parser.add_argument("--extended-baseline", action="store_true",
                        help="Use the prespecified extended creatinine baseline sensitivity.")
    args = parser.parse_args()

    cohort = pd.read_csv(args.cohort)
    if "record_key" not in cohort.columns:
        raise ValueError("Cohort input requires record_key")
    events = standardize_minute_offsets(pd.read_csv(args.events))
    matrix = build_three_domain_matrix(
        cohort["record_key"], events, pd.read_csv(args.coverage),
        extended_baseline=args.extended_baseline,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(args.output, index=False)
    print(f"Wrote three-domain states for {len(matrix)} stays to {args.output}")


if __name__ == "__main__":
    main()
