from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import leave_one_marker_out


def analyze(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(leave_one_marker_out(frame.to_dict("records")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate positive-classification dependence.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("outputs/leave_one_out.csv"))
    args = parser.parse_args()
    result = analyze(pd.read_csv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
