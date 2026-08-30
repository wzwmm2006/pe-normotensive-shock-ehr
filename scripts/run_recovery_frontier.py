from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import (
    MARKERS,
    classify_uncertainty_aware,
    missing_domains,
    optimized_recovery_frontier,
    recovery_scenarios,
)


def analyze(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    records = frame.to_dict("records")
    incomplete = [row for row in records if classify_uncertainty_aware(row) == "INDETERMINATE"]
    burden_counts = Counter(len(missing_domains(row)) for row in incomplete)
    burden = pd.DataFrame(
        [
            {
                "missing_domains": count,
                "incomplete_n": burden_counts.get(count, 0),
                "incomplete_pct": (
                    100 * burden_counts.get(count, 0) / len(incomplete) if incomplete else 0.0
                ),
            }
            for count in range(1, len(MARKERS) + 1)
        ]
    )
    all_scenarios = pd.DataFrame(
        [row for size in range(1, len(MARKERS) + 1) for row in recovery_scenarios(records, size)]
    )
    frontier = pd.DataFrame(optimized_recovery_frontier(records))
    return burden, all_scenarios, frontier


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate structural observability recovery.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/recovery"))
    args = parser.parse_args()
    burden, scenarios, frontier = analyze(pd.read_csv(args.input))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    burden.to_csv(args.output_dir / "missing_domain_burden.csv", index=False)
    scenarios.to_csv(args.output_dir / "recovery_scenarios.csv", index=False)
    frontier.to_csv(args.output_dir / "optimized_recovery_frontier.csv", index=False)
    print(frontier.to_string(index=False))


if __name__ == "__main__":
    main()
