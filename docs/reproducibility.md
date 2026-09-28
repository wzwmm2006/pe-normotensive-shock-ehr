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

- records 1,252; patients 1,252; hospitals 164;
- depth 0/1/2/3: 393/623/179/57;
- evaluable lactate/creatinine/urine: 179/215/758;
- states positive/fully observed negative/indeterminate: 204/26/1,022;
- complete case 57; negative reclassification under simulated missing-as-false:
  1,022.

eICU-CRD, broad age-restricted cohort (sensitivity only):

- records 1,329; depth 415/654/195/65; evaluable 201/238/800; states
  219/31/1,079; complete case 65.

eICU-CRD, extended creatinine baseline (sensitivity):

- records 1,252; creatinine evaluable 709 (56.63%), creatinine positive 34;
  depth 225/500/435/92; states 214/47/991; complete case 92.

eICU-CRD, hospitals with at least 20 records (n = 334 records, 12 hospitals):

- all three domains evaluable, median 3.96% (IQR 2.34-11.20%, range 0-18.60%);
- indeterminate, median 80.37% (IQR 68.59-87.11%, range 60.00-95.45%);
- hospitals with no all-three-evaluable record: 133 of 164.

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

Version 2.0.0 is the two-database computability and external-replication release
and corresponds to the redesigned study. Version 1.0.1 remains the historical
single-database release and is archived at Zenodo under
https://doi.org/10.5281/zenodo.22183069. That DOI identifies v1.0.1 only.