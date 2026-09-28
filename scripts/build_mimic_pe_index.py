"""Build the MIMIC acute pulmonary-embolism index.

The index time is the earliest acute-positive CTPA report time inside an
encounter. The acute-positive label comes from the extension report linkage and
the authoritative time comes from the parent radiology report.

Inputs are standardized local extracts. No restricted identifier is read and no
outcome variable is used.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

EXTENSION_COLUMNS = {"document_key", "acute_positive"}
RADIOLOGY_COLUMNS = {"document_key", "person_key", "encounter_key", "report_time"}
OUTPUT_COLUMNS = ["person_key", "encounter_key", "document_key", "index_time"]
POSITIVE_LABELS = {"1", "true", "yes"}


def build_pe_index(
    extension_reports: pd.DataFrame, radiology_reports: pd.DataFrame
) -> pd.DataFrame:
    if not EXTENSION_COLUMNS.issubset(extension_reports.columns):
        raise ValueError(f"Extension input requires columns: {sorted(EXTENSION_COLUMNS)}")
    if not RADIOLOGY_COLUMNS.issubset(radiology_reports.columns):
        raise ValueError(f"Radiology input requires columns: {sorted(RADIOLOGY_COLUMNS)}")

    positive = extension_reports[
        extension_reports["acute_positive"].astype(str).str.strip().str.lower().isin(POSITIVE_LABELS)
    ]
    linked = positive[["document_key"]].merge(
        radiology_reports[sorted(RADIOLOGY_COLUMNS)], on="document_key", how="inner",
        validate="one_to_one",
    )
    linked["report_time"] = pd.to_datetime(linked["report_time"], errors="raise")
    linked = linked.sort_values(["encounter_key", "report_time", "document_key"])
    index = linked.drop_duplicates("encounter_key", keep="first").copy()
    return index.rename(columns={"report_time": "index_time"})[OUTPUT_COLUMNS]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the MIMIC acute-PE index.")
    parser.add_argument("--extension-reports", type=Path, required=True,
                        help="Local standardized extension reports with document_key and acute_positive.")
    parser.add_argument("--radiology-reports", type=Path, required=True,
                        help="Local standardized radiology reports with document_key, person_key, encounter_key, report_time.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination CSV for the encounter-level index.")
    args = parser.parse_args()

    result = build_pe_index(pd.read_csv(args.extension_reports), pd.read_csv(args.radiology_reports))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} encounter indexes to {args.output}")


if __name__ == "__main__":
    main()
