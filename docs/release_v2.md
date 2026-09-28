# Release v2.0.2

## What this release is

Version 2.0.1 is the two-database computability and external-replication release.
The primary empirical analysis asks how completely guideline-derived
hypoperfusion criteria in pulmonary embolism can be reconstructed from structured
EHR data, and whether that structured observability behaves the same way in a
second data environment.

## What changed in v2.0.2

Documentation only. No analysis code, cohort membership, aggregate result or
scientific conclusion changed from v2.0.1.

- The primary eICU cohort remains 1,266 eligible ICU stays from 1,240 unique
  patients across 164 hospitals.
- Separate eligible hospital admissions for the same patient are retained because
  eICU does not provide reliable chronology across distinct health-system stays.
- The 68-patient count refers to the pre-SBP eligible hospital-admission pool,
  not to the final SBP-filtered primary cohort.
- The per-patient restriction is no longer described as a sensitivity cohort.
- The creatinine-timing sensitivity applies to both databases; the
  first-admission-per-patient sensitivity applies to MIMIC-IV only.

## What changed in v2.0.1

v2.0.1 is a cohort-selection repair on top of v2.0.0. It changes the eICU stay
selection and the eICU aggregate counts. It does not change the MIMIC analysis
and it does not change the scientific conclusion.

- The eICU replication unit is the first eligible ICU stay inside each hospital
  admission, ordered by the unit visit number counted within that admission.
- An audit established that the eICU hospital admission offset is measured from
  each unit admission, so the earlier ICU stay of an admission carries the larger
  (less negative) offset and ordering that field ascending selects the later
  stay. The ICU stay identifier does not encode chronology either. Neither field
  is used as chronology, and eICU provides no reliable way to order separate
  hospital admissions of one patient, so selection stops at the hospital
  admission.
- Corrected eICU primary cohort: 1,266 ICU stays in 1,240 patients across 164
  hospitals, replacing the v2.0.0 figure of 1,252 stays.
- The three-domain result is unchanged in substance. Indeterminate remains about
  four fifths of the cohort.
- v2.0.0 remains available from its tag and is not modified.

## What changed from v1.0.1

- Primary empirical analysis moved from four-domain phenotype classification to
  the three domains with a faithful structured source: lactate, creatinine
  change, and urine output.
- Cardiac index became a computability boundary. It never enters the primary
  classification, and the four-domain zero counts are documented as structurally
  implied rather than as independent evidence.
- The blood-pressure rule became an explicit analysis filter. The complete
  guideline transient-hypotension construct is not reconstructable from either
  structured source.
- eICU-CRD multi-hospital replication was added, including site-level
  observability summaries.
- Creatinine-timing sensitivity was added in both databases, and a
  first-admission-per-patient sensitivity was added for MIMIC-IV.
- The recovery frontier, leave-one-marker-out dependence, and the
  classification-certainty-inflation framing were removed. The simulation is now
  described as `negative reclassification under simulated missing-as-false
  semantics`.
- Terminology was revised so that a structured UNKNOWN is never equated with
  clinical non-measurement.

## Primary results

| Quantity | MIMIC-IV (n = 668) | eICU-CRD (n = 1,266) |
| --- | ---: | ---: |
| SBP-filtered analysis cohort | 668 admissions, 651 patients | 1,266 stays, 1,240 patients, 164 hospitals |
| Depth 0/1/2/3 | 476/111/63/18 | 409/617/180/60 |
| Positive | 42 (6.29%) | 207 (16.35%) |
| Fully observed negative | 13 (1.95%) | 31 (2.45%) |
| Indeterminate | 613 (91.77%) | 1,028 (81.20%) |
| Complete case | 18 (2.69%) | 60 (4.74%) |

The v2.0.0 release reported 1,252 eICU stays, depth 393/623/179/57 and 1,022
indeterminate. Those values are superseded by the table above and are retained
only in the `v2.0.0` tag and its release notes.

## Historical releases

v2.0.1 and v2.0.0 remain available from their tags and are not modified. They are
superseded by v2.0.2 for final manuscript reproducibility.

v1.0.1 remains available and unchanged. It is the single-database
definition-fidelity repair release and is archived at Zenodo under
https://doi.org/10.5281/zenodo.22183069. That version-specific DOI identifies
v1.0.1 only and must not be used to cite v2.0.2.

## DOI policy

Do not attach the v1.0.1 DOI to v2.0.2, and do not create a v2.0.2 DOI before
Zenodo has archived the release. After Zenodo mints the v2.0.2 DOI, add it to the
Citation section of `README.md` and to `CITATION.cff` in a small follow-up commit,
or leave the DOI to the Zenodo record. Do not move the `v2.0.0`, `v2.0.1` or
`v2.0.2` tag.
