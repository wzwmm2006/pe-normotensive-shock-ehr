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

## Corrected pipeline and reproduction gate (v3.0.0)

`scripts/topic1222/` is the corrected implementation behind the released frozen
values. It carries four corrections to the historical v2 pipeline:

1. serial creatinine change is compared in decimal arithmetic, so a rise from
   0.4 to 0.7 mg/dL reaches the inclusive `>= 0.3 mg/dL` threshold instead of
   failing a binary floating-point comparison;
2. the eICU-CRD analysis unit is the ICU stay, and the ICU-stay identifier is
   kept separate from the person identifier, so rule cross-tabulations are never
   pivoted, grouped or de-duplicated by person;
3. every urine-coverage rule (B0 and S1-S3) resets both the positive and the
   negative urine state before the rule is applied and re-derives the three-domain
   classification for every record;
4. the eICU-CRD 24-hour window is 1,440 minutes, because eICU offsets are
   minutes, and is converted to hours only for reporting.

The module reads two standardised, non-restricted files and reproduces the frozen
transformation:

- `scripts/topic1222/contract.py` - the input contract
  (`domain_state_matrix.csv` and `lab_series.csv`);
- `scripts/topic1222/states.py` - the domain and classification logic;
- `scripts/topic1222/gate.py` - the frozen-value comparison;
- `scripts/topic1222/reproduce.py` - the command line.

```
python -m scripts.topic1222.reproduce \
  --matrix private/contract/domain_state_matrix.csv \
  --labs private/contract/lab_series.csv \
  --output-dir outputs/reproduction_gate
```

The command exits 0 only when all 16 frozen metrics match the published values
and writes `reproduction_gate.csv`. The non-identifying aggregate results are in
`results/`; the synthetic input-format sample is
`examples/synthetic_contract_matrix.csv` with `examples/synthetic_contract_labs.csv`.

Reproduction boundary. The pipeline reproduces the frozen transformation from the
standardised inputs. It does not re-derive MIMIC-IV or eICU-CRD source tables.
Rebuilding the standardised inputs from PhysioNet data requires authorized
PhysioNet access and remains governed by the PhysioNet data-use agreements, so a
from-scratch reconstruction of the whole analysis is not claimed. Without the
authorized extract, the synthetic sample exercises the input format and the
command reports a mismatch on purpose.

The corrected pipeline reproduces the frozen manuscript values: MIMIC-IV B0
three-state 43/13/612 and eICU-CRD 207/31/1,028 under B0, 38/12/618 and
79/8/1,179 under S3, with complete case 18 and 60 and direct-positive retention
4 of 36 and 21 of 73 under B0.

## Aggregate regression constants

The public test suite locks the following nonidentifying aggregate values to
detect analysis drift. They contain no record-level material. The values below
describe the historical v2 pipeline (`scripts/`), whose creatinine comparison was
in binary floating point; the corrected pipeline in `scripts/topic1222/`
reproduces the frozen manuscript values, including the MIMIC-IV three-state row
43/13/612 in place of the v2 value 42/13/613. The eICU-CRD values are identical
in both pipelines.

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

Version 3.0.0 is the corrected analysis release. It publishes the non-restricted
implementation that reproduces the frozen two-database results, a standardised
input contract, a synthetic format sample, non-identifying aggregate results, and
an automated reproduction gate. It carries the four corrections listed above.
Version 2.0.2 remains available from its tag and is not an implementation of the
final frozen results. Version 1.0.1 remains the historical single-database
release and is archived at Zenodo under https://doi.org/10.5281/zenodo.22183069.
That DOI identifies v1.0.1 only.