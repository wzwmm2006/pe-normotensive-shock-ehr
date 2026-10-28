# Changelog

## v3.0.0

Corrected analysis code and public reproduction gate.

- Publishes the non-restricted Python implementation (`scripts/topic1222/`) that
  reproduces the frozen two-database results, together with a standardised input
  contract, a synthetic format sample, non-identifying aggregate results in
  `results/`, and an automated reproduction gate
  (`scripts/topic1222/reproduce.py`).
- Correction 1: serial creatinine change is compared in decimal arithmetic. A
  rise from 0.4 to 0.7 mg/dL reaches the inclusive >= 0.3 mg/dL threshold, which
  the earlier binary floating-point comparison missed. eICU-CRD is unaffected;
  MIMIC-IV reclassifies one record, so its B0 three-state row moves from the
  v2.0.2 value 42/13/613 to 43/13/612.
- Correction 2: the eICU-CRD analysis unit is the ICU stay. The ICU-stay
  identifier is kept separate from the person identifier, and person-level
  identifiers are never used to pivot, group or de-duplicate the rule
  cross-tabulations.
- Correction 3: every urine-coverage rule (B0 and S1-S3) resets both the positive
  and the negative urine state before the rule is applied, then re-derives the
  three-domain classification for every record.
- Correction 4: the eICU-CRD 24-hour window is 1,440 minutes. eICU offsets are
  minutes, so the full-window test is `>= 1440` minutes, inclusive, converted to
  hours only for reporting.
- Frozen values are unchanged from v2.0.2 apart from the MIMIC-IV three-state
  row: primary cohorts 668 and 1,266; direct-positive laboratory evidence 36 and
  73; complete case 18 and 60; B0 retention 4 of 36 and 21 of 73; B0 three-state
  43/13/612 and 207/31/1,028; S3 complete case 15 and 14; S3 retention 3 of 36
  and 6 of 73; S3 three-state 38/12/618 and 79/8/1,179.
- The v2.0.2 tag is retained unchanged and is not an implementation of the final
  results. The scripts under `scripts/` other than `scripts/topic1222/` are the
  historical v2 pipeline; `scripts/topic1222/` is the corrected pipeline behind
  the released frozen values.

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
