from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from scripts.run_leave_one_out import analyze as leave_one_out
from scripts.run_missingness_semantics import analyze as semantics
from scripts.run_recovery_frontier import analyze as recovery


def generate(input_path: Path, output_dir: Path) -> None:
    frame = pd.read_csv(input_path)
    _, semantics_summary = semantics(frame)
    burden, scenarios, frontier = recovery(frame)
    dependency = leave_one_out(frame)

    output_dir.mkdir(parents=True, exist_ok=True)
    semantics_summary.to_csv(output_dir / "implementation_semantics.csv", index=False)
    burden.to_csv(output_dir / "missing_domain_burden.csv", index=False)
    scenarios.to_csv(output_dir / "recovery_scenarios.csv", index=False)
    frontier.to_csv(output_dir / "optimized_recovery_frontier.csv", index=False)
    dependency.to_csv(output_dir / "leave_one_out.csv", index=False)

    pivot = semantics_summary.pivot(index="implementation", columns="category", values="record_n").fillna(0)
    pivot.plot(kind="bar", stacked=True, color=["#D79A2B", "#667085", "#C85C5C", "#3A7D44"])
    plt.ylabel("Records")
    plt.xlabel("")
    plt.title("Classification under three missing-data implementations")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / "implementation_semantics.png", dpi=300)
    plt.close()

    plt.bar(frontier["domains_restored"], frontier["recoverable_pct"], color="#278C82")
    plt.xlabel("Domains restored")
    plt.ylabel("Structurally recoverable incomplete records (%)")
    plt.xticks([1, 2, 3, 4])
    plt.title("Optimized structural recovery frontier")
    plt.tight_layout()
    plt.savefig(output_dir / "recovery_frontier.png", dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate aggregate tables and figures.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/manuscript"))
    args = parser.parse_args()
    generate(args.input, args.output_dir)
    print(f"Wrote aggregate tables and figures to {args.output_dir}")


if __name__ == "__main__":
    main()
