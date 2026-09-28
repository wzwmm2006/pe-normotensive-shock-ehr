# v2.0.1 - eICU cohort-selection correction release

Version 2.0.1 corrects the eICU cohort-selection procedure used to identify the
earliest eligible ICU stay within each hospital admission. Version 2.0.0
incorrectly used ascending hospital-admission offset at the patient level and
therefore did not represent a valid "first ICU stay" rule. The eICU hospital
admission offset is measured from each unit admission, so inside one hospital
admission the earlier ICU stay carries the larger (less negative) offset and
ascending order selects the later stay; the ICU stay identifier does not encode
chronology either. The corrected analysis selects the earliest eligible ICU stay
within each hospital admission using within-admission visit order. The eICU
primary cohort changes from 1,252 to 1,266 stays. The main scientific conclusions
are unchanged.

## Corrected eICU primary cohort

- 1,266 eligible ICU stays from 1,240 unique patients across 164 hospitals;
- three-domain depth 0/1/2/3: 409/617/180/60;
- lactate evaluable 186 (14.69%);
- creatinine evaluable 221 (17.46%);
- urine output evaluable 750 (59.24%);
- three-domain positive 207;
- fully observed negative 31;
- indeterminate 1,028 (81.20%);
- complete case 60 (4.74%);
- negative reclassification under simulated missing-as-false semantics: 1,028
  (81.20%).

## Site-level structured observability

Hospitals with at least 20 eligible records (13 hospitals, 356 stays):

- all three domains evaluable, median 3.12% (IQR 0.00-10.00%);
- indeterminate classification, median 78.26% (IQR 68.75-90.00%);
- 131 of 164 hospitals had no record with all three domains evaluable.

## Sensitivity analyses

- Broad age-restricted eICU cohort: 1,343 stays, depth 429/650/197/67, positive
  223, fully observed negative 35, indeterminate 1,085, complete case 67.
- Extended pre-index creatinine baseline: creatinine evaluable 745 (58.85%),
  depth 223/504/440/99, positive 218, fully observed negative 55, indeterminate
  993, complete case 99.

## MIMIC-IV

Unchanged. Primary SBP-filtered cohort: 668 admissions and 651 patients, depth
476/111/63/18, lactate 98, creatinine 105, urine output 88, positive 42, fully
observed negative 13, indeterminate 613, complete case 18.

## Selection provenance

An audit of the eICU ICU-stay selection established that 172 hospital admissions
contain more than one eligible PE ICU stay, and in 172 of 172 the earlier ICU stay
carries the larger (less negative) hospital admission offset. No field in eICU
orders ICU stays inside a hospital admission except the unit visit number, and
eICU provides no reliable way to order separate hospital admissions of one
patient. Selection therefore stops at the hospital admission. The 1,266 stays
come from 1,240 patients; the extra stays are additional eligible hospital
admissions of 68 patients. Repeated hospital admissions are not treated as
independent observations in any inferential model, because the analysis is
descriptive.

## Tests

    py -3.12 -m pytest tests -q
    54 passed

## Public-release audit

PASS. No patient-level data, no restricted note text, no credentials and no
local absolute paths. Synthetic examples and aggregate constants only.

## Historical releases

v2.0.0 remains available from its tag and is not modified. It is superseded by
v2.0.1 for final manuscript reproducibility. v1.0.1 remains the historical
single-database release; its version-specific DOI is not attached to this
release.
