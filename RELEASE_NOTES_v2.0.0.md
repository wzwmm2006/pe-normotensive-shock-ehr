# v2.0.0 - Two-database computability and external-replication release

> Superseded by v2.0.1, which repairs the eICU ICU-stay selection. The counts in
> this file describe the v2.0.0 tag and are retained as the historical record.


This release accompanies the redesigned two-database analysis of structured-EHR
computability of guideline-derived hypoperfusion criteria in pulmonary embolism.
The primary empirical analysis evaluates lactate, creatinine change and urine
output in MIMIC-IV and independently replicates structured observability in an
adult documented-PE eICU-CRD cohort across 164 hospitals. Cardiac index is
retained as a computability boundary rather than treated as an empirically
observed fourth domain.

## Major changes

- Primary empirical analysis focuses on lactate, creatinine change and urine
  output.
- Cardiac index is treated as a computability boundary because
  guideline-compatible provenance cannot be faithfully reconstructed.
- MIMIC primary SBP-filtered cohort: 668 admissions.
- Independent eICU replication: 1,252 adult documented-PE first ICU stays
  across 164 hospitals.
- Complete three-domain structured observability: 2.69 percent in MIMIC and
  4.55 percent in eICU.
- Indeterminate three-domain state: 91.77 percent and 81.63 percent
  respectively.
- Site-level structured-observability variation and a creatinine-timing
  sensitivity analysis were added.
- UNKNOWN always refers to structured-source evaluability and never to clinical
  non-measurement.
- No source patient-level data are redistributed.

## Tests

    py -3.12 -m pytest tests -q
    51 passed

## Public-release audit

PASS. No patient-level data, no restricted note text, no credentials and no
local absolute paths. Synthetic examples and aggregate constants only.

## Historical release

v1.0.1 remains available as the single-database definition-fidelity release.
The version-specific DOI minted for v1.0.1 is not attached to this release.
