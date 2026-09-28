# Reproducibility

## Environment

The analysis was validated with Python 3.12.10. Package versions are pinned in
`requirements.txt`.

## Ordered workflow

1. Obtain authorized access to the required PhysioNet datasets.
2. Keep source data and derived record-level files in private, access-controlled
   storage outside the repository.
3. Copy `config/paths.example.yaml` to `config/paths.yaml` and set local paths;
   the copied file is ignored by Git.
4. Standardize the local extracts to the contracts in `docs/data_requirements.md`.
5. Construct the database-specific PE cohorts
   (`scripts/build_mimic_pe_index.py`, `scripts/build_eicu_documented_pe_cohort.py`).
6. Apply the SBP analysis filter
   (`scripts/build_mimic_sbp_filter.py`, `scripts/build_eicu_sbp_filter.py`).
7. Build the three-domain matrices
   (`scripts/build_mimic_three_domain_matrix.py`,
   `scripts/build_eicu_three_domain_matrix.py`).
8. Classify TRUE / FALSE / UNKNOWN and summarize
   (`scripts/run_three_state_classification.py`).
9. Compare three-state handling with the simulated missing-as-false scenario
   (`scripts/run_missingness_semantics.py`).
10. Summarize between-hospital observability
    (`scripts/run_site_level_observability.py`).
11. Run the creatinine-timing sensitivity
    (`scripts/run_creatinine_timing_sensitivity.py`), assemble cross-database
    aggregates (`scripts/generate_v2_aggregate_outputs.py`), run the test suite,
    and complete the public-release audit.

The cardiac-index domain has no step in this workflow. It is a boundary only; see
`phenotype/four_domain_boundary_spec.yaml`.

## Aggregate regression constants

The public test suite locks the following nonidentifying aggregate values to
detect analysis drift. They contain no record-level material.

MIMIC-IV, SBP-filtered primary cohort:

- records 668; distinct patients 651;
- depth 0/1/2/3: 476/111/63/18;
- evaluable lactate/creatinine/urine: 98/105/88;
- states positive/fully observed negative/indeterminate: 42/13/613;
- complete case 18;
- negative reclassification under simulated missing-as-false: 613.

MIMIC-IV, first eligible admission per patient (sensitivity):

- records 651; depth 461/110/62/18; evaluable 96/104/88; states 41/13/597;
  complete case 18.

MIMIC-IV, extended creatinine baseline (sensitivity):

- records 668; creatinine evaluable 185 (27.69%), creatinine positive 11;
  depth 433/123/88/24; states 48/17/603; complete case 24.

eICU-CRD, documented-PE SBP-filtered primary cohort:

- records 1,266; patients 1,240; hospitals 164;
- depth 0/1/2/3: 409/617/180/60;
- evaluable lactate/creatinine/urine: 186/221/750;
- states positive/fully observed negative/indeterminate: 207/31/1,028;
- complete case 60; negative reclassification under simulated missing-as-false:
  1,028.

eICU-CRD, broad age-restricted cohort (sensitivity only):

- records 1,343; depth 429/650/197/67; evaluable 207/244/794; states
  223/35/1,085; complete case 67.

eICU-CRD, extended creatinine baseline (sensitivity):

- records 1,266; creatinine evaluable 745 (58.85%), creatinine positive 34;
  depth 223/504/440/99; states 218/55/993; complete case 99.

eICU-CRD, hospitals with at least 20 records (n = 356 records, 13 hospitals):

- all three domains evaluable, median 3.12% (IQR 0.00-10.00%, range 0-22.73%);
- indeterminate, median 78.26% (IQR 68.75-90.00%, range 54.55-95.65%);
- hospitals with no all-three-evaluable record: 131 of 164.

## Reproducible and nonredistributable components

The phenotype logic, public item mappings, input contracts, analysis scripts,
tests, and synthetic example are public. Source database tables, note text,
record keys, intermediate record-level matrices, and per-hospital tables are not
distributed. Authorized users can rebuild them inside their own secure
environment.

## Cross-database interpretation

The MIMIC-IV and eICU-CRD cohorts are not clinically identical. They differ in
data source, index time, care setting, and case definition. The cross-database
analysis is a descriptive comparison of structured observability, not a
prevalence comparison and not an equivalence test.

## Release status

Version 2.0.1 is the two-database computability and external-replication release
and corresponds to the redesigned study. It repairs the eICU ICU-stay selection
used in v2.0.0; the corrected primary cohort is 1,266 ICU stays in 1,240 patients
across 164 hospitals. Version 1.0.1 remains the historical single-database
release and is archived at Zenodo under https://doi.org/10.5281/zenodo.22183069.
That DOI identifies v1.0.1 only.