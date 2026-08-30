from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def standardize_vitals(frame: pd.DataFrame, source: str) -> pd.DataFrame:
    required = {"person_key", "encounter_key", "observed_time", "systolic_bp"}
    if not required.issubset(frame.columns):
        raise ValueError(f"{source} input requires columns: {sorted(required)}")
    result = frame[list(required)].copy()
    result["observed_time"] = pd.to_datetime(result["observed_time"], errors="coerce")
    result["systolic_bp"] = pd.to_numeric(result["systolic_bp"], errors="coerce")
    result["source"] = source
    return result


def build_bp_matrix(index: pd.DataFrame, icu_vitals: pd.DataFrame, ed_vitals: pd.DataFrame) -> pd.DataFrame:
    required_index = {"person_key", "encounter_key", "index_time"}
    if not required_index.issubset(index.columns):
        raise ValueError(f"Index input requires columns: {sorted(required_index)}")
    cohort = index[list(required_index)].copy()
    cohort["index_time"] = pd.to_datetime(cohort["index_time"], errors="raise")

    vitals = pd.concat(
        [standardize_vitals(icu_vitals, "ICU"), standardize_vitals(ed_vitals, "ED")],
        ignore_index=True,
    )
    linked = vitals.merge(cohort, on=["person_key", "encounter_key"], how="inner")
    linked["hours_from_index"] = (
        linked["observed_time"] - linked["index_time"]
    ).dt.total_seconds() / 3600
    eligible = linked[
        linked["hours_from_index"].between(0, 24, inclusive="both")
        & linked["systolic_bp"].gt(0)
        & linked["systolic_bp"].lt(400)
    ].copy()
    eligible["below_90"] = eligible["systolic_bp"] < 90

    counts = eligible.groupby("encounter_key").agg(
        eligible_sbp_n=("systolic_bp", "size"),
        sbp_below_90_n=("below_90", "sum"),
        minimum_sbp=("systolic_bp", "min"),
    )
    provenance = eligible.pivot_table(
        index="encounter_key", columns="source", values="systolic_bp", aggfunc="size", fill_value=0
    ).rename(columns={"ICU": "icu_sbp_n", "ED": "ed_sbp_n"})
    result = cohort.merge(counts, on="encounter_key", how="left").merge(
        provenance, on="encounter_key", how="left"
    )
    for column in ("eligible_sbp_n", "sbp_below_90_n", "icu_sbp_n", "ed_sbp_n"):
        if column not in result:
            result[column] = 0
        result[column] = result[column].fillna(0).astype(int)
    result["bp_observable"] = result["eligible_sbp_n"] > 0
    result["normotensive_primary"] = result["bp_observable"] & (result["sbp_below_90_n"] < 2)
    result["normotensive_stricter"] = result["bp_observable"] & (result["sbp_below_90_n"] == 0)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Combine ED and ICU blood-pressure ascertainment.")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--icu-vitals", type=Path, required=True)
    parser.add_argument("--ed-vitals", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_bp_matrix(
        pd.read_csv(args.index), pd.read_csv(args.icu_vitals), pd.read_csv(args.ed_vitals)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote blood-pressure ascertainment for {len(result)} encounters to {args.output}")


if __name__ == "__main__":
    main()
