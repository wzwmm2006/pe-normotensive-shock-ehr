# v2.0.1 - Cohort-selection repair for the eICU replication

This release accompanies the redesigned two-database analysis of structured-EHR
computability of guideline-derived hypoperfusion criteria in pulmonary embolism.
The primary empirical analysis evaluates lactate, creatinine change and urine
output in MIMIC-IV, and independently replicates structured observability in an
adult documented-PE eICU-CRD cohort across 164 hospitals. Cardiac index is
retained as a computability boundary rather than treated as an empirically
observed fourth domain.

## What this release repairs

An audit of the eICU ICU-stay selection found that the v2.0.0 builder ordered
stays by the hospital admission offset, which is measured from each unit
admission, so inside one hospital admission the earlier ICU stay carries the
larger offset and ascending order selects the later stay. The ICU stay identifier
does not encode chronology either. Neither field is now used as chronology.

The eICU analysis unit is the first eligible ICU stay inside each hospital
admission, ordered by the unit visit number counted within that admission.

## Corrected eICU primary cohort

- 1,266 ICU stays in 1,240 patients across 164 hospitals, replacing the v2.0.0
  figure of 1,252 stays.
- Depth 0/1/2/3: 409/617/180/60.
- Criterion evaluability: lactate 186 (14.69%), creatinine 221 (17.46%), urine
  output 750 (59.24%).
- Positive 207 (16.35%), fully observed negative 31 (2.45%), indeterminate 1,028
  (81.20%).
- Complete case 60 (4.74%). Negative reclassification under simulated
  missing-as-false semantics: 1,028 (81.20%).

The scientific conclusion is unchanged: structured observability of the
guideline-derived criteria is incomplete in both data environments, and explicit
UNKNOWN handling remains material.

## MIMIC-IV

The MIMIC-IV analysis is unchanged. Primary SBP-filtered cohort: 668 admissions
and 651 patients, depth 476/111/63/18, positive 42, fully observed negative 13,
indeterminate 613, complete case 18.

## Tests

    py -3.12 -m pytest tests -q
    54 passed

## Public-release audit

PASS. No patient-level data, no restricted note text, no credentials and no
local absolute paths. Synthetic examples and aggregate constants only.

## Historical releases

v2.0.0 remains available from its tag and is not modified. v1.0.1 remains the
historical single-database release. The version-specific DOI minted for v1.0.1 is
not attached to this release.
