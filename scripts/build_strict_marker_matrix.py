from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import MARKERS


def marker_state(values: pd.DataFrame, marker: str, coverage_hours: float | None) -> str:
    if marker == "cardiac_index":
        # The available NICOM item does not match the guideline-specified
        # oxygen-saturation-derived cardiac index, so this domain stays unknown.
        return "UNKNOWN"
    domain = values[values["domain"] == marker].copy()
    domain = domain[domain["hours_from_index"].between(0, 24, inclusive="both")]
    domain["value"] = pd.to_numeric(domain["value"], errors="coerce")
    domain = domain[domain["value"].notna()]

    if marker == "lactate":
        if domain.empty:
            return "UNKNOWN"
        return "TRUE" if domain["value"].max() > 2 else "FALSE"
    if marker == "creatinine_delta":
        domain = domain.sort_values("hours_from_index").drop_duplicates("hours_from_index")
        if len(domain) < 2:
            return "UNKNOWN"
        first = float(domain.iloc[0]["value"])
        later_max = float(domain.iloc[1:]["value"].max())
        return "TRUE" if later_max - first >= 0.3 else "FALSE"
    if marker == "urine_output":
        domain = domain[domain["value"] >= 0]
        if domain.empty or coverage_hours is None or pd.isna(coverage_hours) or coverage_hours < 24:
            return "UNKNOWN"
        return "TRUE" if domain["value"].sum() < 720 else "FALSE"
    raise ValueError(f"Unknown marker: {marker}")


def build_matrix(cohort: pd.DataFrame, events: pd.DataFrame, coverage: pd.DataFrame) -> pd.DataFrame:
    if "record_key" not in cohort.columns:
        raise ValueError("Cohort input requires record_key")
    required_events = {"record_key", "domain", "hours_from_index", "value"}
    if not required_events.issubset(events.columns):
        raise ValueError(f"Events input requires columns: {sorted(required_events)}")
    if not {"record_key", "urine_coverage_hours"}.issubset(coverage.columns):
        raise ValueError("Coverage input requires record_key and urine_coverage_hours")
    invalid_domains = set(events["domain"].dropna()) - set(MARKERS)
    if invalid_domains:
        raise ValueError(f"Unexpected event domains: {sorted(invalid_domains)}")

    coverage_map = coverage.set_index("record_key")["urine_coverage_hours"].to_dict()
    rows = []
    for key in cohort["record_key"].drop_duplicates():
        record_events = events[events["record_key"] == key]
        row = {"record_key": key}
        for marker in MARKERS:
            state = marker_state(record_events, marker, coverage_map.get(key))
            row[f"{marker}_state"] = state
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the four-domain TRUE/FALSE/UNKNOWN matrix.")
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_matrix(
        pd.read_csv(args.cohort), pd.read_csv(args.events), pd.read_csv(args.coverage)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote strict marker states for {len(result)} records to {args.output}")


if __name__ == "__main__":
    main()
