# PE Normotensive Shock EHR Phenotype

## Overview

This repository contains the computable phenotype specification and reproducibility code accompanying the manuscript:

> Computability of Guideline-Defined Normotensive Shock in Acute Pulmonary Embolism: Effects of Missing-Data Semantics in Structured EHRs

The code reconstructs the strict four-domain phenotype, compares three treatments of unavailable criteria, calculates the structural recovery frontier, quantifies positive-classification dependence, and generates aggregate tables and figures. Version 1.0.1 is the definition-fidelity repair release for manuscript submission.

## Scientific problem

The strict phenotype is a disjunctive rule: one observed positive criterion can establish a positive state. A confident negative state requires all four qualifying alternatives to be observed and negative. When observation is incomplete, UNKNOWN is not equivalent to FALSE. The exact amount of incomplete ascertainment depends on the local data architecture; the logical distinction does not.

## Strict phenotype

Within 0-24 hours after the authoritative pulmonary embolism index:

- lactate greater than 2 mmol/L;
- creatinine increase of at least 0.3 mg/dL within 24 hours;
- urine output below 720 mL/24 h; or
- cardiac index at most 2.2 L/min/m2 derived from peripheral arterial and mixed venous oxygen saturation values.

The published guideline reports the creatinine-change unit as mg/mL. The study retained the numerical threshold of 0.3 and used mg/dL, consistent with the conventional SCAI shock definition. The available MIMIC mapping for cardiac index was itemid 228368 (`Cardiac Index (CI NICOM)`), which did not match the guideline-specified measurement provenance. The mapping is excluded and the cardiac-index domain remains UNKNOWN in the study implementation.

The executable specification is in [`phenotype/normotensive_shock_spec.yaml`](phenotype/normotensive_shock_spec.yaml).

## Computational semantics

- **Missing-as-false:** maps UNKNOWN to FALSE before applying the OR rule. This is a simulated implementation scenario and is not attributed to a particular clinical system.
- **Complete-case:** classifies only records with all four domains observed.
- **Uncertainty-aware three-state:** preserves TRUE, FALSE, and UNKNOWN; assigns POSITIVE for any TRUE, NEGATIVE only for four FALSE values, and INDETERMINATE otherwise.

## Repository structure

- `phenotype/`: machine-readable phenotype specification.
- `config/`: local path template; the completed configuration is ignored by Git.
- `metadata/`: variable and source mapping without patient data.
- `scripts/`: cohort provenance, blood-pressure ascertainment, marker-state construction, semantics, recovery, dependence, and output generation.
- `tests/`: synthetic logic tests and aggregate manuscript regression tests.
- `docs/`: data contracts and reproducibility notes.
- `examples/`: synthetic marker-state records only.

## Data requirements

This repository does not distribute MIMIC or PhysioNet data. Users must independently obtain authorized access to the relevant dataset versions, complete required training, and comply with applicable data-use terms. Source data must remain in private, access-controlled storage and must never be committed to this repository.

The public scripts use standardized local column names so that restricted identifiers remain outside version control. See [`docs/data_requirements.md`](docs/data_requirements.md) for the input contracts and [`config/paths.example.yaml`](config/paths.example.yaml) for local path configuration.

## Reproduction

Use Python 3.12.10. From the repository root:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
cp config/paths.example.yaml config/paths.yaml
```

Prepare authorized local source extracts using the contracts in `docs/data_requirements.md`, then run:

```bash
python -m scripts.build_authoritative_pe_index \
  --extension-reports data/extension_reports.csv \
  --radiology-notes data/radiology_notes.csv \
  --output derived/authoritative_index.csv

python -m scripts.build_bp_ascertainment \
  --index derived/authoritative_index.csv \
  --icu-vitals data/icu_vitals.csv \
  --ed-vitals data/ed_vitals.csv \
  --output derived/bp_ascertainment.csv

python -m scripts.build_strict_marker_matrix \
  --cohort data/normotensive_cohort.csv \
  --events data/strict_marker_events.csv \
  --coverage data/urine_coverage.csv \
  --output derived/strict_marker_matrix.csv

python -m scripts.generate_manuscript_outputs \
  --input derived/strict_marker_matrix.csv \
  --output-dir outputs/manuscript
```

Run the fully public synthetic example without restricted data:

```bash
python -m scripts.run_missingness_semantics \
  --input examples/synthetic_marker_example.csv \
  --output-dir outputs/synthetic_semantics
```

## Testing

```bash
pytest -q
```

Tests use synthetic marker states and nonidentifying aggregate manuscript constants only.

## Citation

Repository citation metadata are provided in [`CITATION.cff`](CITATION.cff). The version-specific Zenodo DOI for v1.0.1 will be added after archival deposit.

## License

Repository code is released under the MIT License. This license applies only to the code and documentation authored for this repository. It grants no rights to MIMIC, PhysioNet, or any other source dataset.

## Data use

Users are responsible for PhysioNet credentialing, secure storage, and compliance with all source-dataset terms. Do not open an issue containing patient rows, identifiers, timestamps, or restricted source extracts.
