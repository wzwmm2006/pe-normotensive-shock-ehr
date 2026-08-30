# Data Requirements

## Restricted source data

MIMIC and PhysioNet source files are not included. Keep all downloaded tables, notes, derived encounter files, and intermediate matrices in private storage. The repository ignores `data/`, `raw/`, `derived/`, `outputs/`, database files, compressed extracts, and local configuration.

## Local standardization

The scripts accept generic keys so restricted identifiers do not enter public source code. Create these standardized inputs locally after authorized access.

### Acute-positive extension reports

Required columns:

- `document_key`: local report linkage key;
- `acute_positive`: Boolean acute-positive CTPA label.

### Parent radiology reports

Required columns:

- `document_key`;
- `person_key`;
- `encounter_key`;
- `report_time`: authoritative parent radiology time.

### ED and ICU systolic blood pressure

Required columns:

- `person_key`;
- `encounter_key`;
- `observed_time`;
- `systolic_bp` in mmHg.

Use timestamped measurements only. Do not use an untimed triage value for the study window.

### Strict-marker events

Required columns:

- `record_key`: local analysis-record key;
- `domain`: one of `lactate`, `creatinine_delta`, `urine_output`, or `cardiac_index`;
- `hours_from_index`: event time relative to the authoritative PE index;
- `value`: numeric value in the unit defined by the phenotype specification.

The creatinine rows contain individual creatinine values; the script calculates the serial change. Urine-output values contain nonnegative event amounts. Apply any source-specific correction mapping during authorized local standardization before the public script is run.

### Urine observation coverage

Required columns:

- `record_key`;
- `urine_coverage_hours`: represented structured observation duration.

Complete urine-output evaluability requires at least 24 represented hours.

## Source mappings

The public item and field mappings are listed in `metadata/variable_dictionary.csv`. Users should verify mappings against the exact source-dataset versions available to them.
