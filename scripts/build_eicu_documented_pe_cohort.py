"""Build the eICU diagnosis-coded documented pulmonary-embolism ICU cohort.

The cohort is diagnosis coded. It is not imaging confirmed, and it is never
described as imaging confirmed.

Membership rules:

- age at least 18 years;
- a documented pulmonary-embolism problem row;
- explicit rule-out, suspected and probable wording removed;
- past-history rows never create membership;
- one record per hospital admission: the earliest eligible PE ICU stay inside
  each hospital admission, ordered by unit visit number.

Ordering rule and its limit
---------------------------

eICU ``hospitalAdmitOffset`` is measured from each unit admission, so inside one
hospital admission the earlier ICU stay carries the larger (less negative)
offset and sorting that field ascending selects the later stay. It is therefore
never used to order stays.

The eICU unit-stay identifier column does not encode chronology either. The only
within-admission ordering field used here is the unit visit number, which counts
ICU stays inside one hospital admission (1 is the first).

eICU does not provide a reliable way to order separate hospital admissions for
one patient, so this builder does not attempt it: the analysis unit is the ICU
stay of a hospital admission. A per-patient restriction, if needed, must be
applied downstream and reported as a sensitivity analysis.

Patient columns: record_key, person_key, hospital_key, hospital_admission_key,
age_years, unit_visit_number (optional: unit_type, gender,
hospital_admit_offset_minutes for provenance only)
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

PATIENT_COLUMNS = {"record_key", "person_key", "hospital_key",
                   "hospital_admission_key", "age_years", "unit_visit_number"}
OPTIONAL_PATIENT_COLUMNS = {"unit_type", "gender", "hospital_admit_offset_minutes"}
DIAGNOSIS_COLUMNS = {"record_key", "diagnosis_text"}
PAST_HISTORY_COLUMNS = {"record_key", "history_text"}


def documented_pe_flags(diagnosis: pd.DataFrame) -> pd.DataFrame:
    """Return per-stay PE documentation counts using the study wording rules."""
    if not DIAGNOSIS_COLUMNS.issubset(diagnosis.columns):
        raise ValueError(f"Diagnosis input requires columns: {sorted(DIAGNOSIS_COLUMNS)}")
    rows = diagnosis[["record_key", "diagnosis_text"]].copy()
    text = rows.diagnosis_text.astype(str).str.lower()
    rows["is_pe"] = text.str.contains(PE_TEXT, na=False, regex=False)
    rows["leaf"] = text.str.split("|").str[-1]
    rows["is_rule_out"] = text.str.contains(RULE_OUT_TEXT, na=False, regex=False)
    rows["is_negative_wording"] = rows.leaf.str.startswith(NEGATIVE_LEAF_PREFIXES)
    pe = rows[rows.is_pe]
    flags = pd.DataFrame({"record_key": sorted(rows.record_key.unique())})
    summary = pe.groupby("record_key").agg(
        pe_rows=("leaf", "size"),
        rule_out_rows=("is_rule_out", "sum"),
        negative_wording_rows=("is_negative_wording", "sum"),
    )
    flags = flags.merge(summary, on="record_key", how="left")
    for column in ("pe_rows", "rule_out_rows", "negative_wording_rows"):
        flags[column] = flags[column].fillna(0).astype(int)
    flags["documented_pe_rows"] = (
        flags.pe_rows - flags.rule_out_rows - flags.negative_wording_rows)
    flags["has_documented_pe"] = flags.documented_pe_rows > 0
    return flags


def first_stay_per_hospital_admission(eligible: pd.DataFrame) -> pd.DataFrame:
    """Keep the earliest eligible ICU stay of each hospital admission.

    Ordering uses the unit visit number only. Hospital admission offsets and
    record keys are never used as chronology.
    """
    ordered = eligible.sort_values(
        ["person_key", "hospital_admission_key", "unit_visit_number", "record_key"],
        kind="stable")
    selected = ordered.drop_duplicates(
        subset=["person_key", "hospital_admission_key"], keep="first").copy()
    selected["selected_first_stay_in_hospital_admission"] = True
    return selected


def build(patient: pd.DataFrame, diagnosis: pd.DataFrame,
          past_history: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not PATIENT_COLUMNS.issubset(patient.columns):
        missing = sorted(PATIENT_COLUMNS - set(patient.columns))
        raise ValueError(f"Patient input requires columns: {missing}")
    if not DIAGNOSIS_COLUMNS.issubset(diagnosis.columns):
        raise ValueError(f"Diagnosis input requires columns: {sorted(DIAGNOSIS_COLUMNS)}")

    frame = patient.copy()
    frame["age_years"] = pd.to_numeric(frame.age_years, errors="coerce")
    frame["unit_visit_number"] = pd.to_numeric(frame.unit_visit_number, errors="coerce")
    if frame.unit_visit_number.isna().any():
        raise ValueError("unit_visit_number is required for every ICU stay")

    flags = documented_pe_flags(diagnosis)
    frame = frame.merge(flags, on="record_key", how="left")
    frame["has_documented_pe"] = frame.has_documented_pe.fillna(False).astype(bool)
    frame["adult"] = frame.age_years >= MIN_AGE_YEARS

    if past_history is not None and not past_history.empty:
        if not PAST_HISTORY_COLUMNS.issubset(past_history.columns):
            raise ValueError(
                f"Past-history input requires columns: {sorted(PAST_HISTORY_COLUMNS)}")
        history_keys = set(past_history[
            past_history.history_text.astype(str).str.lower().str.contains(
                PE_TEXT, na=False, regex=False)].record_key)
        frame["pe_in_past_history"] = frame.record_key.isin(history_keys)
    else:
        frame["pe_in_past_history"] = False

    eligible = frame[frame.adult & frame.has_documented_pe].copy()
    selected = first_stay_per_hospital_admission(eligible)

    history_only = int((frame.pe_in_past_history & ~frame.has_documented_pe).sum())
    flow = pd.DataFrame([
        ("patient_rows", len(frame), "all supplied ICU stays"),
        ("pe_coded_stays", int(frame.pe_rows.gt(0).sum()),
         "diagnosis text contains pulmonary embolism"),
        ("documented_pe_adult_stays", len(eligible),
         "age at least 18 and a documented PE problem row"),
        ("selected_first_stay_per_hospital_admission", len(selected),
         "smallest unit visit number within each hospital admission"),
        ("distinct_patients", int(selected.person_key.nunique()), "distinct person_key"),
        ("distinct_hospital_admissions", int(selected.hospital_admission_key.nunique()),
         "distinct hospital_admission_key"),
        ("distinct_hospitals", int(selected.hospital_key.nunique()), "distinct hospital_key"),
        ("stays_with_pe_in_past_history_only", history_only,
         "past-history rows never create membership"),
    ], columns=["stage", "value", "operational_rule"])
    return selected, flow


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patient", type=Path, required=True,
                        help="Local standardized patient table.")
    parser.add_argument("--diagnosis", type=Path, required=True,
                        help="Local standardized problem-list diagnosis table.")
    parser.add_argument("--past-history", type=Path, default=None,
                        help="Optional past-history table, used only as a provenance flag.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Destination CSV for the primary cohort.")
    parser.add_argument("--flow-output", type=Path, default=None,
                        help="Optional destination CSV for the cohort flow table.")
    args = parser.parse_args()

    patient = pd.read_csv(args.patient, low_memory=False)
    diagnosis = pd.read_csv(args.diagnosis, low_memory=False)
    past_history = (pd.read_csv(args.past_history, low_memory=False)
                    if args.past_history else None)

    selected, flow = build(patient, diagnosis, past_history)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(args.output, index=False)
    if args.flow_output:
        args.flow_output.parent.mkdir(parents=True, exist_ok=True)
        flow.to_csv(args.flow_output, index=False)
    print(flow.to_string(index=False))


if __name__ == "__main__":
    main()