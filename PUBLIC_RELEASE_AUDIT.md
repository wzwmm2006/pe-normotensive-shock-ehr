# Public Release Audit

Audit date: 2026-08-30

Repository version: 0.1.0

## Required Findings

PATIENT-LEVEL DATA: NONE

MIMIC RAW DATA: NONE

CREDENTIALS: NONE

ABSOLUTE LOCAL PATHS: NONE

SYNTHETIC EXAMPLES ONLY: YES

TESTS: PASS (13 passed)

## Scan Scope

The recursive scan covered tracked-candidate source code, configuration templates, metadata, tests, examples, and documentation. It checked for restricted source identifiers, source-data rows, patient timestamps, local Windows paths, access keys, tokens, passwords, cookies, private keys, database files, compressed extracts, and patient-level table formats.

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

The repository is safe for code review and a GitHub v0.1.0 branch or commit history. No GitHub push, public release, archival deposit, or DOI creation was performed during this audit.
