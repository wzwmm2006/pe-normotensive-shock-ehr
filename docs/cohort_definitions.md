# Cohort Definitions

The two cohorts answer the same measurement question from different data
architectures. They are not clinically identical, they use different index times,
and they are never compared for prevalence.

## MIMIC-IV acute PE cohort

- Data source: physician-adjudicated CTPA-report acute PE extension linkage
  combined with MIMIC-IV-Note radiology report times, MIMIC-IV chartevents vital
  signs, and MIMIC-IV-ED vital signs.
- Analysis unit: admission.
- Index time: earliest acute-positive CTPA report time inside an encounter.
- Source cohort: 1,337 admissions.
- SBP observable inside 0-24 h: 814 admissions.
- SBP-filtered analysis cohort: 668 admissions, 651 distinct patients.

SBP filter rule: at least one eligible timestamped systolic pressure inside the
window and zero observed systolic pressures below 90 mmHg. The retained
sensitivity rule is fewer than two observed pressures below 90 mmHg.

Admissions excluded because at least one observed systolic pressure fell below
90 mmHg: 146 of the 814 observable admissions. The affected admissions are
distributed across emergency-department-only, intensive-care, and combined
provenance; the largest share carries both emergency-department and
intensive-care observations. No outcome variable was examined for this audit.

Repeat admissions: 15 patients contribute more than one eligible admission, for
17 additional admissions. Restricting to the first eligible admission per patient
gives 651 admissions and does not materially change the three-domain result.

## eICU-CRD documented-PE cohort

- Data source: eICU-CRD diagnosis problem list, patient table, vitalPeriodic and
  vitalAperiodic blood pressures, laboratory table, and intakeOutput.
- Analysis unit: first eligible ICU stay per patient.
- Index time: ICU admission.
- Cohort name: eICU diagnosis-coded documented-PE cohort. The cohort is diagnosis
  coded and is not imaging confirmed.

Construction:

1. Start from PE-coded ICU stays.
2. Require age at least 18 years.
3. Require a documented PE problem row.
4. Exclude explicit rule-out, suspected, and probable wording.
5. Never create membership from past-history rows.
6. Select the first eligible ICU stay per patient.

| Step | Count |
| --- | --- |
| PE-coded ICU stays (broad source) | 2,880 |
| Distinct patients in the broad source | 2,592 |
| Documented-PE adult ICU stays | 2,680 |
| First eligible documented stay per patient | 2,411 |
| Distinct patients | 2,411 |
| Hospitals in the first-stay pool | 182 |
| SBP observable inside the first 24 h | 2,380 |
| SBP-filtered analysis cohort | 1,252 |
| Distinct patients | 1,252 |
| Hospitals in the filtered cohort | 164 |

Patients younger than 18 years removed by the age rule: 3 of the 2,880 broad
source stays, 3 of the 2,592 patient-level pool, and 1 of the 1,329 broad
age-restricted cohort. The broad age-restricted cohort (n = 1,329) is retained as
a sensitivity analysis only and is not the primary eICU cohort.

Exclusions after the SBP rule: 31 stays had no eligible blood-pressure
observation, and 1,128 stays had at least one observed systolic pressure below
90 mmHg.

## Recorded cohort descriptors

MIMIC-IV, SBP-filtered cohort (n = 668 admissions):

| Descriptor | Value |
| --- | --- |
| Age, mean (SD), years | 60.3 (16.9) |
| Age, median (IQR), years | 63.0 (49.0-73.0) |
| Age, range, years | 18-99 |
| Female, n (%) | 343 (51.3%) |
| Male, n (%) | 325 (48.7%) |
| Sex not recorded, n (%) | 0 (0.0%) |
| Any ICU stay during the admission, n (%) | 262 (39.2%) |
| Exactly one linked emergency-department stay, n (%) | 591 (88.5%) |
| No linked emergency-department stay, n (%) | 77 (11.5%) |

The upper part of the MIMIC age range contains deidentified ages at the source
ceiling: 11 admissions (1.6%) carry the ceiling value rather than an exact age.

eICU-CRD, documented-PE SBP-filtered cohort (n = 1,252 stays):

| Descriptor | Value |
| --- | --- |
| Age, mean (SD), years | 61.44 (16.35) |
| Age, median (IQR), years | 63 (50-74) |
| Age, range, years | 18-89 |
| Female, n (%) | 573 (45.77%) |
| Male, n (%) | 678 (54.15%) |
| Sex not recorded, n (%) | 1 (0.08%) |
| ICU stay, n (%) | 1,252 (100%) by construction |
| Hospitals | 164 |

ICU type distribution in the eICU cohort: Med-Surg ICU 749 (59.82%), MICU 132
(10.54%), Cardiac ICU 119 (9.50%), CCU-CTICU 83 (6.63%), SICU 68 (5.43%), CSICU
40 (3.19%), Neuro ICU 38 (3.04%), CTICU 23 (1.84%).

## Cross-database comparison rule

Cross-database results describe transportability of structured observability.
They are not an equivalence test and not a prevalence comparison. No outcome
variable is examined in either cohort.