from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import (
    MARKERS,
    classify_complete_case,
    classify_missing_as_false,
    classify_uncertainty_aware,
    missing_domains,
)


def analyze(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    records = frame.to_dict("records")
    crosswalk = frame.copy()
    crosswalk["missing_as_false"] = [classify_missing_as_false(row) for row in records]
    crosswalk["complete_case"] = [classify_complete_case(row) for row in records]
    crosswalk["uncertainty_aware"] = [classify_uncertainty_aware(row) for row in records]
    crosswalk["n_missing_domains"] = [len(missing_domains(row)) for row in records]
    rows = []
    categories = {
        "missing_as_false": ("POSITIVE", "NEGATIVE"),
        "complete_case": ("POSITIVE", "NEGATIVE", "NOT_CLASSIFIABLE"),
        "uncertainty_aware": ("POSITIVE", "NEGATIVE", "INDETERMINATE"),
    }
    for implementation, labels in categories.items():
        for label in labels:
            count = int((crosswalk[implementation] == label).sum())
            rows.append(
                {
                    "implementation": implementation,
                    "category": label,
                    "record_n": count,
                    "record_pct": 100 * count / len(crosswalk) if len(crosswalk) else 0.0,
                }
            )
    return crosswalk, pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare three missing-data implementations.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/semantics"))
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    required = {f"{marker}_state" for marker in MARKERS}
    if not required.issubset(frame.columns):
        raise ValueError(f"Input requires columns: {sorted(required)}")
    crosswalk, summary = analyze(frame)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    crosswalk.to_csv(args.output_dir / "classification_crosswalk.csv", index=False)
    summary.to_csv(args.output_dir / "implementation_semantics.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
