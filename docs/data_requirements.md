# Data Requirements

## Restricted source data

MIMIC-IV and eICU-CRD source files are not distributed with this repository.
Keep downloaded tables, note text, derived encounter files, and intermediate
record-level matrices in private, access-controlled storage. The repository
ignores `data/`, `raw/`, `derived/`, `outputs/`, `private/`, database files,
compressed extracts, and the local path configuration.

## Standardized local contracts

The scripts read generic standardized columns so that restricted identifiers
never enter public source code. Build these extracts locally after authorized
access. Keys are local analysis keys, not source identifiers.

### MIMIC-IV acute-PE index

`extension_reports.csv`: `document_key`, `acute_positive`.

`radiology_reports.csv`: `document_key`, `person_key`, `encounter_key`,
`report_time`.

Output: `person_key`, `encounter_key`, `document_key`, `index_time`, where
`index_time` is the earliest acute-positive CTPA report time inside an encounter.

### MIMIC-IV blood pressure

`icu_vitals.csv` and `ed_vitals.csv`: `person_key`, `encounter_key`,
`observed_time`, `systolic_bp` in mmHg.

Use timestamped measurements only. Untimed triage values are not used for the
study window. Values must be greater than 0 and less than 400 mmHg.

Output: the index rows plus the eligibility flag, the retained observation count,
and the number of observed values below 90 mmHg.

### MIMIC-IV three-domain matrix

`cohort.csv` requires `record_key`.

`events.csv`: `record_key`, `domain` (`lactate`, `creatinine_delta`,
`urine_output`), `hours_from_index`, `value` in the unit defined by the
specification. Creatinine rows carry individual measurements; the script
computes the serial change.

`urine_coverage.csv`: `record_key`, `urine_coverage_hours`. Complete urine-output
evaluability requires at least 24 represented hours.

A `cardiac_index` domain may be supplied in generic inputs, but it is never
evaluated without a faithful guideline-specified source mapping, and it never
enters the classification.

### eICU-CRD documented-PE cohort

`patient.csv`: `record_key`, `person_key`, `hospital_key`,
`hospital_admission_key`, `age_years`, `unit_visit_number`, and optionally
`unit_type` and `hospital_admit_offset_minutes`.

`diagnosis.csv`: `record_key`, `diagnosis_text`.

`past_history.csv` (optional): `record_key`, `history_text`. Past-history rows
never create membership; they are carried only as a provenance flag.

Membership requires age at least 18 years and a documented PE problem row, with
rule-out, suspected, and probable wording excluded. The first eligible ICU stay
inside each hospital admission is selected, ordered by `unit_visit_number`.
`hospital_admit_offset_minutes` may be carried for provenance, but it is never
used as chronology.

### eICU-CRD blood pressure

`vital_periodic.csv` (invasive) and `vital_aperiodic.csv` (non-invasive):
`record_key`, `observed_offset_minutes`, `systolic_bp` in mmHg. Offsets are
minutes from ICU admission.

### eICU-CRD three-domain matrix

`cohort.csv` requires `record_key`.

`events.csv`: `record_key`, `domain`, `minutes_from_offset`, `value`.

`urine_coverage.csv`: `record_key`, `urine_coverage_hours`.

Urine-output amounts must already be restricted to the single `intakeOutput`
documentation channel during local standardization. The `nurseCharting` label
with a urine token is a text genitourinary assessment without a numeric volume
and is not an eligible urine-output source; see `docs/structured_observability.md`.

## Source mappings

Public item and field mappings are in `metadata/mimic_variable_dictionary.csv`
and `metadata/eicu_variable_dictionary.csv`. Verify mappings against the exact
dataset versions available locally; item identifiers are stable within a dataset
version but not across all of them.

## Local path configuration

Copy `config/paths.example.yaml` to `config/paths.yaml` and replace the
placeholders. The completed file is ignored by Git and must never be committed.