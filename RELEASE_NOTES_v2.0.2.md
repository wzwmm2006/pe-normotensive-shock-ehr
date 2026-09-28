# v2.0.2 - Documentation provenance clarification

Version 2.0.2 clarifies the documentation of repeated hospital admissions in the
corrected eICU replication cohort. No analysis code, cohort membership, aggregate
result, or scientific conclusion has changed from v2.0.1.

The primary eICU cohort remains 1,266 eligible ICU stays from 1,240 unique
patients across 164 hospitals. Separate eligible hospital admissions for the same
patient are retained because eICU does not provide reliable chronology across
distinct health-system stays. The previously reported count of 68 patients refers
to the pre-SBP eligible hospital-admission pool, not to the final SBP-filtered
primary cohort.

All v2.0.1 numerical results remain unchanged.

## Release chain

| Version | Content |
| --- | --- |
| v2.0.2 | Documentation provenance clarification. Results identical to v2.0.1. |
| v2.0.1 | Corrected eICU cohort-selection procedure and re-frozen counts. |
| v2.0.0 | First two-database release; eICU stay selection was not a valid first-stay rule. |
| v1.0.0, v1.0.1 | Single-database releases. Historical, unchanged. |

## Tests

    py -3.12 -m pytest tests -q
    54 passed

## Public-release audit

PASS. No patient-level data, no restricted note text, no credentials and no
local absolute paths. Synthetic examples and aggregate constants only.
