"""Command-line reproduction gate for the corrected Topic1222 analysis.

Usage::

    python -m scripts.topic1222.reproduce \
        --matrix private/contract/domain_state_matrix.csv \
        --labs private/contract/lab_series.csv \
        --output-dir outputs/reproduction_gate

The runner loads the two standardised contract files described in
``scripts/topic1222/contract.py``, recomputes the published metrics, prints a
PASS / FAIL table and writes ``reproduction_gate.csv``. It exits with status 0
only when every frozen metric matches the published value.

``--allow-mismatch`` prints the same table and exits 0. Use it when the inputs
are a format sample rather than the authorized extract, so that the samples in
``examples/`` can be exercised without pretending they reproduce the study.

The runner reads only the standardised contract. It never reads, downloads or
rebuilds a restricted source table.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .contract import ContractError, InputPaths, load_inputs
from .gate import gate_passed, run_gate

OUTPUT_NAME = "reproduction_gate.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.topic1222.reproduce",
        description=(
            "Recompute the frozen Topic1222 metrics from the standardised input "
            "contract and compare them with the published values."
        ),
    )
    parser.add_argument(
        "--matrix",
        required=True,
        type=Path,
        help="domain_state_matrix.csv of the standardised input contract",
    )
    parser.add_argument(
        "--labs",
        required=True,
        type=Path,
        help="lab_series.csv of the standardised input contract",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        type=Path,
        help="directory that receives " + OUTPUT_NAME,
    )
    parser.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="exit 0 even when a frozen metric does not match",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        inputs = load_inputs(InputPaths(matrix=args.matrix, labs=args.labs))
    except ContractError as error:
        print("INPUT CONTRACT ERROR: " + str(error), file=sys.stderr)
        return 2

    comparison = run_gate(inputs)
    print(comparison.to_string(index=False))
    passed = gate_passed(comparison)
    failed = comparison[~comparison["status"].eq("PASS")]

    print()
    print("databases in inputs : " + ", ".join(inputs.databases))
    print("metrics compared   : " + str(len(comparison)))
    print("metrics failed     : " + str(len(failed)))
    print("REPRODUCTION GATE  : " + ("PASSED" if passed else "FAILED"))
    if not passed:
        for row in failed.itertuples(index=False):
            print(
                "  mismatch: "
                + str(row.metric)
                + " ["
                + str(row.database)
                + "] published="
                + str(row.frozen)
                + " recomputed="
                + str(row.computed)
            )

    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        target = args.output_dir / OUTPUT_NAME
        comparison.to_csv(target, index=False)
        print("written            : " + str(target))

    if passed or args.allow_mismatch:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())