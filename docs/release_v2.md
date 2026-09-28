# Release v2.0.0

## What this release is

Version 2.0.0 is the two-database computability and external-replication release.
The primary empirical analysis asks how completely guideline-derived
hypoperfusion criteria in pulmonary embolism can be reconstructed from structured
EHR data, and whether that structured observability behaves the same way in a
second data environment.

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
- Creatinine-timing and first-admission-per-patient sensitivities were added.
- The recovery frontier, leave-one-marker-out dependence, and the
  classification-certainty-inflation framing were removed. The simulation is now
  described as `negative reclassification under simulated missing-as-false
  semantics`.
- Terminology was revised so that a structured UNKNOWN is never equated with
  clinical non-measurement.

## Primary results

| Quantity | MIMIC-IV (n = 668) | eICU-CRD (n = 1,252) |
| --- | ---: | ---: |
| SBP-filtered analysis cohort | 668 admissions, 651 patients | 1,252 stays, 1,252 patients, 164 hospitals |
| Depth 0/1/2/3 | 476/111/63/18 | 393/623/179/57 |
| Positive | 42 (6.29%) | 204 (16.29%) |
| Fully observed negative | 13 (1.95%) | 26 (2.08%) |
| Indeterminate | 613 (91.77%) | 1,022 (81.63%) |
| Complete case | 18 (2.69%) | 57 (4.55%) |

## Historical release

v1.0.1 remains available and unchanged. It is the single-database
definition-fidelity repair release and is archived at Zenodo under
https://doi.org/10.5281/zenodo.22183069. That version-specific DOI identifies
v1.0.1 only and must not be used to cite v2.0.0.

## DOI policy

Do not attach the v1.0.1 DOI to v2.0.0, and do not create a v2.0.0 DOI before
Zenodo has archived the release. After Zenodo mints the v2.0.0 DOI, add it to
the Citation section of `README.md` and to `CITATION.cff` in a small follow-up
commit, or leave the DOI to the Zenodo record. Do not move the `v2.0.0` tag.