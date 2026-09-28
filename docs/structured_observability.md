# Structured Observability

## 1. What is measured

Structured observability is whether a guideline-derived criterion can be
evaluated from a prespecified structured source inside a prespecified analysis
window. It is not a statement about clinicians, documentation quality, or care.

Domain states:

- TRUE: the criterion is evaluable inside the window and meets its positive
  threshold.
- FALSE: the criterion is evaluable inside the window and does not meet its
  positive threshold.
- UNKNOWN: the criterion cannot be evaluated from the prespecified structured
  source inside the window.

UNKNOWN is never mapped to FALSE in the primary analysis, and absent charting is
never treated as a negative measurement.

## 2. Structured sources per domain

| Domain | MIMIC-IV channel | eICU-CRD channel |
| --- | --- | --- |
| Lactate | laboratory events, itemid 50813, mmol/L | laboratory table, lactate with a mmol/L system unit |
| Creatinine change | laboratory events, itemid 50912, mg/dL | laboratory table, creatinine with a mg/dL system unit |
| Urine output | output events across twelve urine itemids, with irrigant volume sign-corrected | intakeOutput urine cell paths only, summed from `cellvaluenumeric` |

## 3. Ascertainment depth

Depth is the number of the three domains that are evaluable for a record.

MIMIC-IV, SBP-filtered cohort (n = 668):

| Evaluable domains | Records |
| --- | ---: |
| 0 | 476 |
| 1 | 111 |
| 2 | 63 |
| 3 | 18 |

eICU-CRD, documented-PE SBP-filtered cohort (n = 1,252):

| Evaluable domains | Records |
| --- | ---: |
| 0 | 393 |
| 1 | 623 |
| 2 | 179 |
| 3 | 57 |

Domain evaluability:

| Domain | MIMIC n (%) | eICU n (%) |
| --- | ---: | ---: |
| Lactate | 98 (14.67%) | 179 (14.30%) |
| Creatinine change | 105 (15.72%) | 215 (17.17%) |
| Urine output | 88 (13.17%) | 758 (60.54%) |

## 4. Classification states

| State | Rule | MIMIC n (%) | eICU n (%) |
| --- | --- | ---: | ---: |
| Positive | at least one domain TRUE | 42 (6.29%) | 204 (16.29%) |
| Fully observed negative | all three domains FALSE | 13 (1.95%) | 26 (2.08%) |
| Indeterminate | no TRUE and at least one UNKNOWN | 613 (91.77%) | 1,022 (81.63%) |

Complete case (all three domains evaluable): 18 of 668 (2.69%) in MIMIC and 57
of 1,252 (4.55%) in eICU.

`Fully observed negative` means that every empirical domain was evaluated and
none was positive. It is not a negative result for the complete guideline
construct, which includes a domain that cannot be operationalized here.

## 5. Simulated missing-as-false

Under the simulated scenario, UNKNOWN is mapped to FALSE before the OR rule.
Records that are indeterminate under three-state handling become apparent
negatives: 613 of 668 (91.77%) in MIMIC and 1,022 of 1,252 (81.63%) in eICU.

This is a simulated computational scenario. It is not an observed deployed
system, not a diagnostic error, and not a statement about clinical measurement.
The preferred phrasing is `negative reclassification under simulated
missing-as-false semantics`.

## 6. Documentation-channel audit

### 6.1 Urine output in eICU

`nurseCharting` was read in full (151,604,232 rows).

- Rows carrying a urine token anywhere in the label: 340,611 rows across 14,174
  stays, all from the single label combination `Other Vital Signs and
  Infusions || Genitourinary Assessment || Value`.
- Rows carrying an explicit urine-output phrase such as `urine output` or
  `urinary output`: 0 rows across 0 stays.
- Rows eligible for the primary urine-output definition (a numeric urine volume):
  0.
- In the primary analysis window of the primary cohort, the same label carries
  313 rows across 53 stays and still 0 numeric values.

Conclusion: in eICU, urine volume is charted in `intakeOutput` alone. The
`nurseCharting` label is a text genitourinary assessment without a numeric
volume, so it is not a second quantitative channel, and no `nurseCharting` value
entered the urine-output calculation. The eICU urine criterion has a single
documentation channel.

### 6.2 Cardiac-index labels in eICU

- A label named `CI` exists database-wide: 188,225 rows across 5,894 stays under
  an invasive category and 8,168 rows across 1,031 stays under a vital-signs
  category, 196,393 rows in total.
- In the primary analysis window of the primary cohort, the same label carries
  30 rows across 2 stays, with values from 1.6 to 4.7.
- Database-wide values run up to 69.0, which is not a plausible cardiac index.

These are monitor and device outputs. They do not carry the peripheral-arterial
and mixed-venous oxygen-saturation provenance the guideline criterion requires,
and they are not quality-controlled. The label is therefore not used, and the
cardiac-index domain remains UNKNOWN for every record in both databases. See
`docs/guideline_fidelity.md`.

## 7. Between-hospital variation in eICU

For hospitals with at least 20 records in the documented-PE SBP-filtered cohort
(12 hospitals, 334 records):

| Metric | Median | IQR | Range |
| --- | ---: | --- | --- |
| All three domains evaluable | 3.96% | 2.34-11.20% | 0-18.60% |
| Indeterminate classification | 80.37% | 68.59-87.11% | 60.00-95.45% |

Among all 164 hospitals in the cohort, 133 had no record with all three domains
evaluable.

This spread describes variation in structured-data capture. It is not a quality
ranking, and no hospital is described as delivering better or worse care. The
per-hospital table is local working material; only aggregate distributions are
published.

## 8. Interpretation limits

- Structured UNKNOWN does not mean the measurement was clinically absent.
- Cross-database differences in single-domain evaluability, most visibly for
  urine output, are architecture differences and are not compared for
  prevalence.
- The cohorts differ in index time, care setting, and case mix; the comparison is
  descriptive transportability of structured observability.
- No outcome variable is used anywhere in this repository.