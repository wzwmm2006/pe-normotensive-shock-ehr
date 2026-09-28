"""Apply the operational blood-pressure analysis filter to the eICU cohort.

Offsets are eICU minute offsets from ICU admission. The observation window is
the first 24 h, and the same plausibility bounds and rule as the MIMIC pipeline
are applied through the shared public core.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import ANALYSIS_WINDOW_HOURS, sbp_filter

OFFSET_COLUMNS = {"record_key", "observed_offset_minutes", "systolic_bp"}
SOURCE_LABELS = {"periodic": "invasive", "aperiodic": "non_invasive"}
MINUTES_PER_HOUR = 60.0


def standardize_offset_vitals(frame: pd.DataFrame, source: str) -> pd.DataFrame:
    if not OFFSET_COLUMNS.issubset(frame.columns):
        raise ValueError(f"{source} vitals require columns: {sorted(OFFSET_COLUMNS)}")
    result = frame[sorted(OFFSET_COLUMNS)].copy()
    result["observed_offset_minutes"] = pd.to_numeric(
        result["observed_offset_minutes"], errors="coerce")
    result["systolic_bp"] = pd.to_numeric(result["systolic_bp"], errors="coerce")
    result["stream"] = SOURCE_LABELS[source]
    return result


def build_sbp_filter(
    cohort: pd.DataFrame, vital_periodic: pd.DataFrame, vital_aperiodic: pd.DataFrame
) -> pd.DataFrame:
    if "record_key" not in cohort.columns:
        raise ValueError("Cohort input requires record_key")
    keys = cohort[["record_key"]].drop_duplicates()
    vitals = pd.concat(
        [standardize_offset_vitals(vital_periodic, "periodic"),
         standardize_offset_vitals(vital_aperiodic, "aperiodic")],
        ignore_index=True,
    )
    vitals = vitals[vitals["record_key"].isin(set(keys["record_key"]))]
    vitals["hours_from_index"] = vitals["observed_offset_minutes"] / MINUTES_PER_HOUR

    rows = []
    for record_key, block in vitals.groupby("record_key", sort=False):
        summary = sbp_filter(block["hours_from_index"], block["systolic_bp"],
                             window_hours=ANALYSIS_WINDOW_HOURS)
        rows.append({
            "record_key": record_key,
            **summary,
            "invasive_sbp_n": int((block["stream"] == "invasive").sum()),
            "non_invasive_sbp_n": int((block["stream"] == "non_invasive").sum()),
        })

    result = keys.merge(pd.DataFrame(rows), on="record_key", how="left")
    for column in ("eligible_sbp_n", "sbp_below_90_n", "invasive_sbp_n", "non_invasive_sbp_n"):
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0).astype(int)
    for column in ("sbp_observable", "sbp_filter_pass_zero_below_90",
                   "sbp_filter_pass_fewer_than_two_below_90"):
        result[column] = result[column].astype("boolean").fillna(False).astype(bool)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply the operational SBP analysis filter to the eICU cohort.")
    parser.add_argument("--cohort", type=Path, required=True,
                        help="Cohort from build_eicu_documented_pe_cohort.py.")
    parser.add_argument("--vital-periodic", type=Path, required=True,
                        help="Local standardized periodic (invasive) blood pressures.")
    parser.add_argument("--vital-aperiodic", type=Path, required=True,
                        help="Local standardized aperiodic (non-invasive) blood pressures.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination CSV for the SBP-filtered cohort.")
    args = parser.parse_args()

    result = build_sbp_filter(pd.read_csv(args.cohort), pd.read_csv(args.vital_periodic),
                              pd.read_csv(args.vital_aperiodic))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    passed = int(result["sbp_filter_pass_zero_below_90"].sum())
    print(f"Wrote blood-pressure ascertainment for {len(result)} stays; {passed} pass the primary filter")


if __name__ == "__main__":
    main()
