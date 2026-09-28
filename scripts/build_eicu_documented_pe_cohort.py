"""Build the eICU diagnosis-coded documented pulmonary-embolism ICU cohort.

This cohort is diagnosis coded. It is not imaging confirmed, and it is not
described as imaging confirmed.

Membership rules:

- age at least 18 years;
- a documented pulmonary-embolism problem row;
- explicit rule-out, suspected and probable wording removed;
- past-history rows never create membership;
- the first eligible ICU stay per patient is selected.

Patient columns: record_key, person_key, hospital_key, age_years,
hospital_admit_offset_minutes, unit_type (optional)
Diagnosis columns: record_key, diagnosis_text
Past-history columns: record_key, history_text (optional, provenance only)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

PE_TEXT = "pulmonary embolism"
RULE_OUT_TEXT = "r/o pulmonary embolism"
NEGATIVE_LEAF_PREFIXES = ("suspected", "probable")
MIN_AGE_YEARS = 18

PATIENT_COLUMNS = {"record_key", "person_key", "hospital_key", "age_years",
                   "hospital_admit_offset_minutes"}
DIAGNOSIS_COLUMNS = {"record_key", "diagnosis_text"}


def problem_leaf(text: object) -> str:
    """Last element of the diagnosis hierarchy, lowercased."""
    return str(text).lower().split("|")[-1].strip()


def classify_problem_rows(diagnosis: pd.DataFrame) -> pd.DataFrame:
    """Reduce diagnosis rows to per-record pulmonary-embolism wording flags."""
    if not DIAGNOSIS_COLUMNS.issubset(diagnosis.columns):
        raise ValueError(f"Diagnosis input requires columns: {sorted(DIAGNOSIS_COLUMNS)}")
    rows = diagnosis.copy()
    rows["diagnosis_text"] = rows["diagnosis_text"].astype(str).str.lower()
    rows["is_pe"] = rows["diagnosis_text"].str.contains(PE_TEXT, regex=False, na=False)
    rows["is_rule_out"] = rows["diagnosis_text"].str.contains(RULE_OUT_TEXT, regex=False, na=False)
    rows["leaf"] = rows["diagnosis_text"].map(problem_leaf)
    rows["is_negative_wording"] = rows["leaf"].str.startswith(NEGATIVE_LEAF_PREFIXES)
    rows["is_documented_pe"] = rows["is_pe"] & ~rows["is_rule_out"] & ~rows["is_negative_wording"]
    grouped = rows.groupby("record_key").agg(
        pe_rows=("is_pe", "sum"),
        documented_pe_rows=("is_documented_pe", "sum"),
        negative_wording_rows=("is_negative_wording", "sum"),
    )
    return grouped.reset_index()


def build_documented_pe_cohort(
    patient: pd.DataFrame,
    diagnosis: pd.DataFrame,
    past_history: pd.DataFrame | None = None,
    minimum_age_years: int = MIN_AGE_YEARS,
) -> pd.DataFrame:
    if not PATIENT_COLUMNS.issubset(patient.columns):
        raise ValueError(f"Patient input requires columns: {sorted(PATIENT_COLUMNS)}")

    cohort = patient.copy()
    cohort["age_years"] = pd.to_numeric(cohort["age_years"], errors="coerce")
    cohort["hospital_admit_offset_minutes"] = pd.to_numeric(
        cohort["hospital_admit_offset_minutes"], errors="coerce")

    flags = classify_problem_rows(diagnosis)
    cohort = cohort.merge(flags, on="record_key", how="left")
    for column in ("pe_rows", "documented_pe_rows", "negative_wording_rows"):
        cohort[column] = cohort[column].fillna(0).astype(int)
    cohort["has_documented_pe"] = cohort["documented_pe_rows"] > 0
    cohort["negative_wording_only"] = (~cohort["has_documented_pe"]) & (cohort["pe_rows"] > 0)
    cohort["adult"] = cohort["age_years"] >= minimum_age_years

    if past_history is not None and len(past_history):
        history = past_history.copy()
        history_text = history["history_text"].astype(str).str.lower()
        history = history[history_text.str.contains(PE_TEXT, regex=False, na=False)]
        cohort["pe_history_evidence"] = cohort["record_key"].isin(set(history["record_key"]))
    else:
        cohort["pe_history_evidence"] = False

    eligible = cohort[cohort["adult"] & cohort["has_documented_pe"]].copy()
    eligible = eligible.sort_values(
        ["person_key", "hospital_admit_offset_minutes", "record_key"])
    eligible["first_eligible_stay"] = ~eligible["person_key"].duplicated(keep="first")
    return eligible.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the eICU documented-PE ICU cohort.")
    parser.add_argument("--patient", type=Path, required=True,
                        help="Local standardized patient table.")
    parser.add_argument("--diagnosis", type=Path, required=True,
                        help="Local standardized problem-list diagnosis table.")
    parser.add_argument("--past-history", type=Path, default=None,
                        help="Optional past-history table, used only as a provenance flag.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination CSV for the cohort.")
    args = parser.parse_args()

    past_history = pd.read_csv(args.past_history) if args.past_history else None
    cohort = build_documented_pe_cohort(
        pd.read_csv(args.patient), pd.read_csv(args.diagnosis), past_history)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cohort.to_csv(args.output, index=False)
    first = int(cohort["first_eligible_stay"].sum())
    print(f"Wrote {len(cohort)} documented-PE adult stays; {first} are first eligible stays")


if __name__ == "__main__":
    main()
