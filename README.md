# Structured EHR Computability of Guideline-Derived Hypoperfusion Criteria in Pulmonary Embolism

This repository contains reproducibility code and public-safe metadata for a
two-database study evaluating how completely guideline-derived hypoperfusion
criteria can be reconstructed from structured electronic health record (EHR)
data in pulmonary embolism (PE).

- MIMIC-IV is the primary imaging-linked acute-PE analysis.
- eICU-CRD provides independent multi-hospital replication.
- The primary empirical analysis uses three reconstructable criteria: lactate,
  creatinine change, and urine output.
- Cardiac index is a computability boundary. No structured source available to
  the study carries the measurement provenance the criterion requires, so the
  domain is never scored as observed.
- A structured UNKNOWN means the criterion cannot be evaluated from the
  prespecified structured source inside the prespecified analysis window. It does
  not mean that a measurement was clinically absent.
- Missing-as-false is a simulated semantic scenario, not an observed deployed
  system.

## 1. Overview

The study asks a measurement question, not a prognosis question. Given a
guideline-derived set of hypoperfusion criteria and two independent structured
EHR sources, how many records can be resolved into a definite criterion state,
and does that structured observability behave the same way in a second data
environment?

Two things follow from that question:

1. The primary result is an observability result. Most records cannot be
   evaluated for all three empirically available criteria inside the analysis
   window, and a large share cannot be evaluated for any of them.
2. Treating a non-evaluable criterion as a negative one changes the number of
   resolved negative records. That change is reported as a simulated semantic
   scenario, not as an observed system behaviour and not as a clinical error.

No outcome variable is read anywhere in this repository.

## 2. Study question

> How completely can guideline-derived hypoperfusion criteria in acute pulmonary
> embolism be reconstructed from structured EHR data, and does that structured
> observability transport across two independent EHR data environments?

Explicitly out of scope:

- whether any hypoperfusion criterion was clinically present or absent;
- whether a patient had shock, deterioration, or any downstream outcome;
- whether any hospital delivered good or poor care;
- prevalence comparison between the two cohorts.

## 3. Final v2 design

- Unit of analysis: MIMIC-IV admissions; eICU-CRD first eligible intensive-care
  unit stay per hospital admission.
- Index time: MIMIC-IV uses the earliest acute-positive CTPA report time within
  an encounter. eICU-CRD uses ICU admission as the database-specific index.
- Analysis window: 0 to +24 h relative to the database-specific index.
- Domains scored: lactate, creatinine change, urine output.
- Domain states: TRUE, FALSE, UNKNOWN.
- Classification: POSITIVE (any TRUE), FULLY OBSERVED NEGATIVE (all three FALSE),
  INDETERMINATE (no TRUE and at least one UNKNOWN).
- Blood pressure: an operational analysis filter, applied before classification.
- Cross-database comparison: descriptive transportability of structured
  observability, not prevalence equivalence.

The two cohorts are not clinically identical, and the two index times are not
temporally equivalent. The comparison is descriptive transportability across two
EHR data environments that differ in care setting, index time, and structured
documentation pathways.

## 4. MIMIC cohort

Analysis unit: admissions. Source: physician-adjudicated CTPA-report acute PE
cohort linked to MIMIC-IV-Note radiology reports, with blood-pressure
augmentation from MIMIC-IV chartevents and MIMIC-IV-ED.

| Step | Count |
| --- | --- |
| Source cohort (admissions) | 1,337 |
| SBP observable in the window | 814 |
| SBP-filtered analysis cohort | 668 |
| Distinct patients in the filtered cohort | 651 |

SBP filter rule: at least one eligible timestamped systolic pressure inside the
window, and zero observed systolic pressures below 90 mmHg. The retained
sensitivity rule is fewer than two observed pressures below 90 mmHg.

Three-domain ascertainment depth in the 668-admission cohort:

| Evaluable domains | Records |
| --- | --- |
| 0 | 476 |
| 1 | 111 |
| 2 | 63 |
| 3 | 18 |

Criterion evaluability:

| Criterion | Evaluable | Percentage |
| --- | --- | --- |
| Lactate | 98 | 14.67% |
| Creatinine change | 105 | 15.72% |
| Urine output | 88 | 13.17% |

Three-domain classification:

| State | Records | Percentage |
| --- | --- | --- |
| Positive | 42 | 6.29% |
| Fully observed negative | 13 | 1.95% |
| Indeterminate | 613 | 91.77% |

Complete case (all three criteria evaluable): 18 of 668 (2.69%).

`Fully observed negative` means all three empirical criteria were evaluated and
none was positive. It is not a statement that the complete guideline construct
was negative.

Sensitivity analyses (see `docs/reproducibility.md`):

- First eligible admission per patient (651 admissions): depth 461/110/62/18;
  evaluable 96/104/88; states 41/13/597; complete case 18.
- Extended pre-index creatinine baseline: creatinine evaluable 185 (27.69%),
  creatinine positive 11; depth 433/123/88/24; states 48/17/603; complete case 24.

## 5. eICU replication cohort

Analysis unit: first eligible ICU stay per hospital admission. Cohort name: eICU
diagnosis-coded documented-PE cohort. This cohort is diagnosis coded. It is not
imaging confirmed and is never described as imaging confirmed.

Membership rules: age at least 18 years; a documented PE problem row; explicit
rule-out, suspected, and probable wording excluded; past-history rows never
create membership; first eligible ICU stay per hospital admission.

| Step | Count |
| --- | --- |
| Documented-PE adult ICU stays | 2,680 |
| First eligible documented stay per hospital admission | 2,487 |
| SBP observable in the window | 2,454 |
| SBP-filtered analysis cohort | 1,266 |
| Distinct patients | 1,240 |
| Distinct hospital admissions | 2,487 |
| Hospitals | 164 |

Cohort descriptors (n = 1,266): age mean 61.34 (SD 16.36), median 63 (IQR
50-74, range 18-89); female 583 (46.05%); male 682 (53.87%); sex not recorded 1.

Three-domain ascertainment depth:

| Evaluable domains | Records |
| --- | --- |
| 0 | 409 |
| 1 | 617 |
| 2 | 180 |
| 3 | 60 |

Criterion evaluability:

| Criterion | Evaluable | Percentage |
| --- | --- | --- |
| Lactate | 186 | 14.69% |
| Creatinine change | 221 | 17.46% |
| Urine output | 750 | 59.24% |

Three-domain classification:

| State | Records | Percentage |
| --- | --- | --- |
| Positive | 207 | 16.35% |
| Fully observed negative | 31 | 2.45% |
| Indeterminate | 1,028 | 81.20% |

Complete case: 60 of 1,266 (4.74%). Negative reclassification under simulated
missing-as-false semantics: 1,028 of 1,266 (81.20%).

Sensitivity analyses:

- Broad age-restricted eICU cohort (n = 1,343), retained as sensitivity only:
  depth 429/650/197/67; evaluable 207/244/794; states 223/35/1,085; complete
  case 67.
- Extended pre-index creatinine baseline: creatinine evaluable 745 (58.85%),
  creatinine positive 34; depth 223/504/440/99; states 218/55/993; complete
  case 99.

## 6. Guideline-derived criteria

Within 0 to +24 h of the database-specific index:

- lactate above 2 mmol/L (maximum evaluable in-window value);
- creatinine increase of at least 0.3 mg/dL between two valid measurements at
  distinct times;
- urine output below 720 mL/24 h with complete 24 h structured observation.

Terminology notes:

- The published guideline prints the creatinine-change unit as mg/mL. This
  implementation keeps the numerical threshold of 0.3 and uses mg/dL, consistent
  with conventional AKI and SCAI usage. It is an operational adaptation and is not
  described as a literal guideline transcription.
- The construct is called a `guideline-derived operational phenotype`. It is not
  called `guideline-faithful`, because one guideline domain cannot be faithfully
  operationalized from the available structured sources.
- Absent charting is never treated as zero urine output.

## 7. Cardiac-index boundary

The guideline cardiac-index criterion requires a value derived from peripheral
arterial and mixed venous oxygen-saturation measurements, at or below
2.2 L/min/m2.

- In MIMIC-IV the only closely named structured item is `Cardiac Index (CI NICOM)`
  (itemid 228368). NICOM is a bioreactance measurement and does not carry the
  required provenance. The mapping is rejected rather than treated as equivalent.
- In eICU-CRD, monitor-derived and nurse-entered labels exist, including a label
  named `CI`. They are device output and are not interpretable as the
  guideline-specified measurement.

Consequence: a required domain of the four-domain construct is UNKNOWN for every
record. A four-domain fully observed negative state and a four-domain
complete-case state are therefore structurally impossible, and those zero counts
are not reported as independent empirical evidence. See
`phenotype/four_domain_boundary_spec.yaml`.

## 8. Structured observability states

- TRUE: the criterion is evaluable inside the window and meets its positive
  threshold.
- FALSE: the criterion is evaluable inside the window and does not meet its
  positive threshold.
- UNKNOWN: the criterion cannot be evaluated from the prespecified structured
  source inside the prespecified analysis window.

UNKNOWN is a statement about structured source coverage. It is not a statement
about clinical measurement, documentation quality, or care delivered.

Classification rules are stated in
`phenotype/three_domain_observability_spec.yaml`. The simulated missing-as-false
scenario maps UNKNOWN to FALSE before the OR rule and is reported only as
`negative reclassification under simulated missing-as-false semantics`.

## 9. Repository structure

```
config/paths.example.yaml             local path template (placeholders only)
phenotype/three_domain_observability_spec.yaml   primary specification
phenotype/four_domain_boundary_spec.yaml         cardiac-index boundary
metadata/mimic_variable_dictionary.csv           public MIMIC mappings
metadata/eicu_variable_dictionary.csv            public eICU mappings
docs/data_requirements.md                        input contracts
docs/cohort_definitions.md                       cohort construction
docs/phenotype_definition.md                     criterion operationalization
docs/structured_observability.md                 observability and channel audit
docs/guideline_fidelity.md                       guideline-fidelity assessment
docs/missingness_semantics.md                    classification scenarios
docs/reproducibility.md                          ordered workflow and constants
docs/release_v2.md                               release contents and DOI policy
scripts/phenotype_core.py                        shared logic
scripts/build_mimic_*.py                         MIMIC cohort, filter, matrix
scripts/build_eicu_*.py                          eICU cohort, filter, matrix
scripts/run_*.py                                 classification and sensitivity
scripts/generate_v2_aggregate_outputs.py         cross-database aggregates
tests/                                           synthetic and aggregate tests
examples/synthetic_three_domain_example.csv      synthetic records only
```

## 10. Data requirements

MIMIC-IV and eICU-CRD source data are not redistributed. Authorized users must
obtain access through PhysioNet, complete the required training, and keep source
extracts in private storage. The scripts read standardized local extracts with
generic keys, so restricted identifiers never enter version control. Contracts
are in `docs/data_requirements.md`; local paths are configured from
`config/paths.example.yaml`.

## 11. Reproduction

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Standardize local extracts, then:

```bash
python -m scripts.build_mimic_pe_index \
  --extension-reports private/mimic/extension_reports.csv \
  --radiology-reports private/mimic/radiology_reports.csv \
  --output derived/mimic_pe_index.csv

python -m scripts.build_mimic_sbp_filter \
  --index derived/mimic_pe_index.csv \
  --icu-vitals private/mimic/icu_vitals.csv \
  --ed-vitals private/mimic/ed_vitals.csv \
  --output derived/mimic_sbp_filter.csv

python -m scripts.build_mimic_three_domain_matrix \
  --cohort derived/mimic_sbp_filter.csv \
  --events private/mimic/events.csv \
  --coverage private/mimic/urine_coverage.csv \
  --output derived/mimic_matrix.csv

python -m scripts.build_eicu_documented_pe_cohort \
  --patient private/eicu/patient.csv \
  --diagnosis private/eicu/diagnosis.csv \
  --past-history private/eicu/past_history.csv \
  --output derived/eicu_cohort.csv

python -m scripts.build_eicu_sbp_filter \
  --cohort derived/eicu_cohort.csv \
  --vital-periodic private/eicu/vital_periodic.csv \
  --vital-aperiodic private/eicu/vital_aperiodic.csv \
  --output derived/eicu_sbp_filter.csv

python -m scripts.build_eicu_three_domain_matrix \
  --cohort derived/eicu_sbp_filter.csv \
  --events private/eicu/events.csv \
  --coverage private/eicu/urine_coverage.csv \
  --output derived/eicu_matrix.csv

python -m scripts.run_three_state_classification \
  --input derived/mimic_matrix.csv --output-dir outputs/mimic_three_state

python -m scripts.run_missingness_semantics \
  --input derived/eicu_matrix.csv --output-dir outputs/eicu_semantics

python -m scripts.run_site_level_observability \
  --input derived/eicu_matrix.csv --site-column site_key --output-dir outputs/site_level

python -m scripts.run_creatinine_timing_sensitivity \
  --events private/mimic/events.csv \
  --coverage private/mimic/urine_coverage.csv \
  --cohort derived/mimic_sbp_filter.csv \
  --output-dir outputs/creatinine_sensitivity

python -m scripts.generate_v2_aggregate_outputs \
  --mimic-matrix derived/mimic_matrix.csv \
  --eicu-matrix derived/eicu_matrix.csv \
  --output-dir outputs/v2_aggregate
```

The synthetic example runs without any restricted data:

```bash
python -m scripts.run_missingness_semantics \
  --input examples/synthetic_three_domain_example.csv \
  --output-dir outputs/synthetic_semantics
```

## 12. Testing

```bash
python -m pytest -q
```

The public suite uses synthetic records and nonidentifying aggregate constants
only. It does not require restricted source data.

## 13. Public-data safety

This repository contains no patient-level rows, no note text, no restricted
identifiers, no credentials, and no local absolute paths. Aggregate counts and
synthetic examples are the only data artifacts. See `PUBLIC_RELEASE_AUDIT.md`
and the automated scan in `tests/test_public_safety.py`.

## 14. Version history

- **v2.0.2** - documentation provenance clarification for the corrected eICU
  replication. The description of repeated hospital admissions was clarified and
  the 68-patient count was scoped to the pre-SBP eligible pool. No analysis code,
  cohort membership, aggregate result or scientific conclusion changed from
  v2.0.1.
- **v2.0.1** - superseded by v2.0.2 for final manuscript reproducibility. Cohort-selection repair. The eICU replication cohort is selected
  per hospital admission, ordered by the unit visit number inside the admission.
  An audit showed that the hospital admission offset is measured from each unit
  admission and that the ICU stay identifier does not encode chronology, so
  neither can order stays inside an admission. The corrected primary cohort is
  1,266 ICU stays in 1,240 patients across 164 hospitals, and the three-domain
  result is unchanged in substance.
- **v2.0.0** - superseded by v2.0.1 for final manuscript reproducibility. The
  v2.0.0 tag is retained unchanged; its eICU cohort used a stay-selection rule
  that is corrected in v2.0.1. two-database structured-observability and external-replication
  release. Primary empirical analysis moved from the four-domain phenotype to
  three empirical domains; cardiac index became a computability boundary; an
  operational SBP analysis filter replaced the claim of complete guideline
  normotension reconstruction; eICU-CRD multi-hospital replication and site-level
  observability were added.
- **v1.0.1** - definition-fidelity repair for the original single-database
  manuscript. Historical release, archived at Zenodo under
  https://doi.org/10.5281/zenodo.22183069. That version-specific DOI identifies
  the v1.0.1 code only and does not describe v2.0.0.
- **v1.0.0** - original manuscript submission release.

Historical releases remain recoverable from their Git tags.

## 15. Citation

Citation metadata are in `CITATION.cff`. A v2.0.2 Zenodo DOI will be added once
the release has been archived. Until then, cite the GitHub release `v2.0.2`.

## 16. License

Repository code and documentation are released under the MIT License. The license
grants no rights to MIMIC-IV, eICU-CRD, PhysioNet, or any other source dataset.
Users are responsible for credentialing, secure storage, and compliance with all
source-dataset terms. Do not open an issue containing patient rows, identifiers,
timestamps, or restricted source extracts.