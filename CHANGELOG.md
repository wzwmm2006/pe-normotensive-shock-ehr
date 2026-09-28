# Changelog

## v2.0.2

Documentation provenance clarification. No analysis code, cohort membership,
aggregate result or scientific conclusion changed from v2.0.1.

- The repeated-admission provenance of the eICU replication cohort was clarified.
- The primary eICU cohort remains 1,266 eligible ICU stays from 1,240 unique
  patients across 164 hospitals.
- The 68-patient count for patients contributing more than one eligible hospital
  admission was scoped to the pre-SBP eligible hospital-admission pool, not to
  the final SBP-filtered primary cohort.
- The per-patient restriction is no longer described as a sensitivity cohort.
- The creatinine-timing sensitivity is described as applying to both databases;
  the first-admission-per-patient sensitivity is described as MIMIC-IV only.

## v2.0.1

Cohort-selection repair for the eICU replication.

- The eICU analysis unit is the first eligible ICU stay inside each hospital
  admission, ordered by the unit visit number counted within that admission.
- An audit established that the eICU hospital admission offset is measured from
  each unit admission, so the earlier ICU stay of an admission carries the larger
  (less negative) offset and ordering that field ascending selects the later
  stay. The ICU stay identifier does not encode chronology either. Neither field
  is used as chronology.
- Corrected eICU primary cohort: 1,266 ICU stays in 1,240 patients across 164
  hospitals, replacing the v2.0.0 figure of 1,252 stays.
- Corrected eICU primary counts: depth 409/617/180/60; positive 207 (16.35%);
  fully observed negative 31 (2.45%); indeterminate 1,028 (81.20%); complete case
  60 (4.74%).
- The eICU broad-cohort sensitivity and the creatinine-timing sensitivity were
  recomputed on the corrected selection.
- MIMIC analysis and the scientific conclusion are unchanged.
- v2.0.0 remains available from its tag and is not modified.

## v2.0.0

Two-database computability and external-replication release.

- Primary empirical analysis moved from four-domain phenotype classification to
  three-domain structured observability: lactate, creatinine change, urine output.
- Cardiac index converted from an executable domain into a computability
  boundary; the complete four-domain construct is not fully reconstructable from
  the selected structured sources.
- Operational blood-pressure analysis filter replaces any claim of complete
  guideline normotension reconstruction.
- MIMIC primary SBP-filtered cohort: 668 admissions.
- eICU multi-hospital replication added: 1,252 adult documented-PE first ICU
  stays across 164 hospitals.
- Site-level structured-observability analysis added.
- Creatinine extended-baseline timing sensitivity added.
- MIMIC first-admission-per-patient sensitivity added.
- Terminology revised so that a structured UNKNOWN is never equated with
  clinical non-measurement.
- Recovery frontier and leave-one-marker-out analyses removed from the
  scientific narrative and from the public analysis code.
- v1.0.1 preserved as the historical single-database release.

## v1.0.1

Definition-fidelity repair for the original single-database manuscript release.

## v1.0.0

Original manuscript submission release.
