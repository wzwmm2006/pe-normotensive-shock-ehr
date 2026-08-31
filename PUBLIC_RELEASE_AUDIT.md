# Public Release Audit

Audit date: 2026-08-31

Repository version: 1.0.1

## Required Findings

PATIENT-LEVEL DATA: NONE

MIMIC RAW DATA: NONE

CREDENTIALS: NONE

ABSOLUTE LOCAL PATHS: NONE

SYNTHETIC EXAMPLES ONLY: YES

TESTS: PASS (13 passed)

## Scan Scope

The recursive scan covered every tracked source, configuration template, metadata file, test, synthetic example, and documentation file. It checked for restricted source identifiers, source-data rows, patient timestamps, actual local Windows or Unix paths, access keys, tokens, passwords, cookies, private keys, database files, compressed extracts, and patient-level table formats. The `/path/to/...` strings in `config/paths.example.yaml` are documented placeholders, not local filesystem paths.

No unsafe artifact was detected. The four-row example uses synthetic record labels A-D and marker states only.

## Intentionally Excluded

- All MIMIC-IV, MIMIC-IV-Note, MIMIC-IV-ED, and MIMIC-IV-Ext-PE source files.
- All patient and encounter identifiers.
- All radiology text and patient-level timestamps.
- All patient-level cohort indexes, blood-pressure matrices, marker matrices, and classification crosswalks.
- All local database files, compressed extracts, caches, credentials, and completed path configuration.
- Internal manuscript Gate reports and nonpublic engineering audits.

The repository contains public item mappings, generic local input contracts, analysis code, synthetic tests, and nonidentifying aggregate manuscript regression constants. Source-dataset users must obtain independent authorization and keep restricted material outside version control.

## Release Decision

SAFE TO PUSH: YES

The repository was committed and published as GitHub release v1.0.1. The cardiac-index repair excludes the NICOM mapping and contains no patient-level record. Zenodo archived the release as `wzwmm2006/pe-normotensive-shock-ehr-v1.0.1.zip` under DOI `10.5281/zenodo.22183069` (md5: `78af9e1f2e162228b4296d82a2ba76a3`).
