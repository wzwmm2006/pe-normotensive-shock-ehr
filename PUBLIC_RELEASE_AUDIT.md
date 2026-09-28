# Public Release Audit

Audit date: 2026-09-28

Repository version: 2.0.2

## Required Findings

PATIENT-LEVEL DATA: NONE

MIMIC RAW DATA: NONE

eICU RAW DATA: NONE

CLINICAL NOTES: NONE

CREDENTIALS: NONE

ABSOLUTE LOCAL PATHS: NONE

RESTRICTED HOSPITAL-LEVEL SOURCE DATA: NONE

SYNTHETIC EXAMPLES ONLY: YES

AGGREGATE RESULTS ONLY: YES

TESTS: PASS (54 passed)

## Scan Scope

The recursive scan covered every tracked source file, configuration template,
metadata dictionary, test, synthetic example, and documentation file. It checked
for restricted source identifiers, source-data rows, patient timestamps,
clinical note text, local Windows and Unix filesystem paths, access keys, tokens,
passwords, cookies, private keys, database files, compressed extracts, and
record-level table formats.

Automated checks are implemented in `tests/test_public_safety.py` and run with
the rest of the suite:

- no restricted or binary data file is present;
- no local absolute filesystem path appears in repository text;
- no patient-key token appears outside the audit documents;
- no credential token appears in code or configuration outside the audit
  documents and the ignore rules;
- no credential-assignment pattern appears in any scanned text file, including
  documentation;
- no pipeline script reads an outcome variable;
- no CSV header carries an outcome or patient-key column;
- every CSV is synthetic or aggregate and has at most 50 rows;
- the ignore rules cover local and restricted locations;
- `CITATION.cff` declares version 2.0.2 and carries no DOI.

Documentation files are exempt from the plain credential-token scan because
ordinary prose legitimately states that the release carries no credentials. They
are not exempt from the credential-assignment scan: `tests/test_public_safety.py`
searches every text file for key-value shapes such as an assigned secret, an API
key, a bearer value or a private-key header, and none is present. The
`/path/to/...` strings in `config/paths.example.yaml` are documented
placeholders, not local filesystem paths. The synthetic example uses invented
record labels A-E with domain states only.

## Record-level material intentionally excluded

- MIMIC-IV, MIMIC-IV-Note, MIMIC-IV-ED, MIMIC-IV-Ext-PE and eICU-CRD source files.
- Patient, encounter, ICU-stay and hospital source identifiers, and any
  per-hospital table.
- Radiology text, discharge summaries, and all clinical note text.
- Patient-level cohort indexes, blood-pressure matrices, domain matrices, and
  classification crosswalks.
- Local database files, compressed extracts, caches, credentials, and completed
  path configuration.
- Internal gate reports and nonpublic engineering audits.

The repository contains public item mappings, generic local input contracts,
analysis code, synthetic tests, and nonidentifying aggregate constants. Site-level
findings are published only as aggregate distributions, never as per-hospital
rows.

## Release Decision

SAFE TO PUSH: YES

No restricted artifact was detected. The release is prepared as GitHub release
v2.0.2. The v1.0.1 DOI is not attached to this version; a v2.0.2 DOI will be
recorded only after Zenodo archives the release.