"""Compare three-state handling with the simulated missing-as-false scenario.

UNKNOWN is mapped to FALSE only as a simulation. The aggregate output reports
the number of records that are apparent negatives under the simulation but
indeterminate under three-state handling. That count is described as negative
reclassification under simulated missing-as-false semantics.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import (
    APPARENT_NEGATIVE,
    FULLY_OBSERVED_NEGATIVE,
    INDETERMINATE,
    POSITIVE,
    annotate_matrix,
)


def analyze(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    annotated = annotate_matrix(frame)
    total = len(annotated)
    three_state = annotated["three_domain_classification"].value_counts()
    simulated = annotated["simulated_missing_as_false_classification"].value_counts()
    reclassified = int(
        annotated["negative_reclassification_under_missing_as_false"].sum())
    rows = [
        ("three_state", "positive", int(three_state.get(POSITIVE, 0))),
        ("three_state", "fully_observed_negative", int(three_state.get(FULLY_OBSERVED_NEGATIVE, 0))),
        ("three_state", "indeterminate", int(three_state.get(INDETERMINATE, 0))),
        ("simulated_missing_as_false", "positive", int(simulated.get(POSITIVE, 0))),
        ("simulated_missing_as_false", "apparent_negative",
         int(simulated.get(APPARENT_NEGATIVE, 0))),
        ("negative_reclassification_under_simulated_missing_as_false",
         "reclassified", reclassified),
    ]
    summary = pd.DataFrame(rows, columns=["section", "metric", "record_n"])
    summary["denominator_n"] = total
    summary["pct"] = (100 * summary["record_n"] / total).round(2) if total else 0.0
    crosswalk = annotated[[
        "record_key", "lactate_state", "creatinine_delta_state", "urine_output_state",
        "three_domain_classification", "simulated_missing_as_false_classification",
        "negative_reclassification_under_missing_as_false"]].copy()
    return crosswalk, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare three-state handling with simulated missing-as-false.")
    parser.add_argument("--input", type=Path, required=True,
                        help="Table with record_key and the three per-domain state columns.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/missingness_semantics"),
                        help="Local destination for the crosswalk and the summary.")
    args = parser.parse_args()

    crosswalk, summary = analyze(pd.read_csv(args.input))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    crosswalk.to_csv(args.output_dir / "classification_crosswalk.csv", index=False)
    summary.to_csv(args.output_dir / "missingness_semantics_summary.csv", index=False)
    print(summary.to_string(index=False))
    print("\nMissing-as-false is a simulated scenario, not an observed system behavior.")


if __name__ == "__main__":
    main()
