from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_index(extension_reports: pd.DataFrame, radiology_notes: pd.DataFrame) -> pd.DataFrame:
    required_extension = {"document_key", "acute_positive"}
    required_notes = {"document_key", "person_key", "encounter_key", "report_time"}
    if not required_extension.issubset(extension_reports.columns):
        raise ValueError(f"Extension input requires columns: {sorted(required_extension)}")
    if not required_notes.issubset(radiology_notes.columns):
        raise ValueError(f"Radiology input requires columns: {sorted(required_notes)}")

    positive = extension_reports.loc[
        extension_reports["acute_positive"].astype(str).str.lower().isin({"1", "true", "yes"})
    ]
    linked = positive[["document_key"]].merge(
        radiology_notes[list(required_notes)], on="document_key", how="inner", validate="one_to_one"
    )
    linked["report_time"] = pd.to_datetime(linked["report_time"], errors="raise")
    linked = linked.sort_values(["encounter_key", "report_time", "document_key"])
    index = linked.drop_duplicates("encounter_key", keep="first").copy()
    return index.rename(columns={"report_time": "index_time"})[
        ["person_key", "encounter_key", "document_key", "index_time"]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the authoritative acute-PE index.")
    parser.add_argument("--extension-reports", type=Path, required=True)
    parser.add_argument("--radiology-notes", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = build_index(pd.read_csv(args.extension_reports), pd.read_csv(args.radiology_notes))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} authoritative encounter indexes to {args.output}")


if __name__ == "__main__":
    main()
