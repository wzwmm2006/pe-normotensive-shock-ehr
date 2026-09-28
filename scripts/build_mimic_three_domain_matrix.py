"""Build the MIMIC three-domain structured-observability matrix.

Events carry standardized hours relative to the index time. The cardiac-index
domain never enters the classification; it is written as a boundary field only
(see phenotype/four_domain_boundary_spec.yaml).

Events columns: record_key, domain, hours_from_index, value
Coverage columns: record_key, urine_coverage_hours
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import build_three_domain_matrix


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the MIMIC three-domain TRUE/FALSE/UNKNOWN matrix.")
    parser.add_argument("--cohort", type=Path, required=True,
                        help="Cohort records to score; requires record_key.")
    parser.add_argument("--events", type=Path, required=True,
                        help="Standardized events: record_key, domain, hours_from_index, value.")
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
    matrix = build_three_domain_matrix(
        cohort["record_key"], pd.read_csv(args.events), pd.read_csv(args.coverage),
        extended_baseline=args.extended_baseline,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(args.output, index=False)
    print(f"Wrote three-domain states for {len(matrix)} records to {args.output}")


if __name__ == "__main__":
    main()
