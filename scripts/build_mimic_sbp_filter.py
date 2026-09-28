"""Apply the operational blood-pressure analysis filter to the MIMIC cohort.

The filter is a documented analysis filter, not a reconstruction of guideline
normotension. See docs/guideline_fidelity.md.

Primary rule: at least one eligible SBP inside 0-24 h and zero observed SBP
below 90 mmHg. The retained sensitivity is fewer than two observed SBP values
below 90 mmHg.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.phenotype_core import ANALYSIS_WINDOW_HOURS, sbp_filter

VITAL_COLUMNS = {"person_key", "encounter_key", "observed_time", "systolic_bp"}
INDEX_COLUMNS = {"person_key", "encounter_key", "index_time"}
SOURCE_LABELS = {"ICU": "icu", "ED": "ed"}


def standardize_vitals(frame: pd.DataFrame, source: str) -> pd.DataFrame:
    if not VITAL_COLUMNS.issubset(frame.columns):
        raise ValueError(f"{source} input requires columns: {sorted(VITAL_COLUMNS)}")
    result = frame[sorted(VITAL_COLUMNS)].copy()
    result["observed_time"] = pd.to_datetime(result["observed_time"], errors="coerce")
    result["systolic_bp"] = pd.to_numeric(result["systolic_bp"], errors="coerce")
    result["source"] = SOURCE_LABELS[source]
    return result


def build_sbp_filter(
    index: pd.DataFrame, icu_vitals: pd.DataFrame, ed_vitals: pd.DataFrame
) -> pd.DataFrame:
    if not INDEX_COLUMNS.issubset(index.columns):
        raise ValueError(f"Index input requires columns: {sorted(INDEX_COLUMNS)}")
    cohort = index[sorted(INDEX_COLUMNS)].copy()
    cohort["index_time"] = pd.to_datetime(cohort["index_time"], errors="raise")

    vitals = pd.concat(
        [standardize_vitals(icu_vitals, "ICU"), standardize_vitals(ed_vitals, "ED")],
        ignore_index=True,
    )
    linked = vitals.merge(cohort, on=["person_key", "encounter_key"], how="inner")
    linked["hours_from_index"] = (
        linked["observed_time"] - linked["index_time"]
    ).dt.total_seconds() / 3600

    rows = []
    for (person_key, encounter_key, index_time), block in linked.groupby(
            ["person_key", "encounter_key", "index_time"], sort=False):
        summary = sbp_filter(block["hours_from_index"], block["systolic_bp"],
                             window_hours=ANALYSIS_WINDOW_HOURS)
        rows.append({
            "person_key": person_key,
            "encounter_key": encounter_key,
            "index_time": index_time,
            **summary,
            "icu_sbp_n": int((block["source"] == "icu").sum()),
            "ed_sbp_n": int((block["source"] == "ed").sum()),
        })
    result = cohort.merge(pd.DataFrame(rows), on=["person_key", "encounter_key", "index_time"],
                          how="left")
    for column in ("eligible_sbp_n", "sbp_below_90_n", "icu_sbp_n", "ed_sbp_n"):
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0).astype(int)
    for column in ("sbp_observable", "sbp_filter_pass_zero_below_90",
                   "sbp_filter_pass_fewer_than_two_below_90"):
        result[column] = result[column].astype("boolean").fillna(False).astype(bool)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply the operational SBP analysis filter to the MIMIC cohort.")
    parser.add_argument("--index", type=Path, required=True,
                        help="Encounter-level index from build_mimic_pe_index.py.")
    parser.add_argument("--icu-vitals", type=Path, required=True,
                        help="Local standardized ICU blood pressures.")
    parser.add_argument("--ed-vitals", type=Path, required=True,
                        help="Local standardized emergency-department blood pressures.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination CSV for the filtered cohort.")
    args = parser.parse_args()

    result = build_sbp_filter(pd.read_csv(args.index), pd.read_csv(args.icu_vitals),
                              pd.read_csv(args.ed_vitals))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    passed = int(result["sbp_filter_pass_zero_below_90"].sum())
    print(f"Wrote blood-pressure ascertainment for {len(result)} encounters; {passed} pass the primary filter")


if __name__ == "__main__":
    main()
