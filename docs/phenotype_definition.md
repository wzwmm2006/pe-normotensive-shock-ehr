# Strict Normotensive-Shock Phenotype

## Analysis population

The phenotype is applied after acute pulmonary embolism and blood-pressure ascertainment have been established. The primary study implementation used timestamped emergency-department and intensive-care systolic blood pressures in the 0-24-hour interval after the authoritative imaging index. At least one eligible pressure was required, and fewer than two observations below 90 mmHg were allowed. A stricter sensitivity implementation excluded any observation below 90 mmHg.

## Strict domains

| Domain | Evaluable when | Positive when |
| --- | --- | --- |
| Lactate | At least one valid in-window value | Maximum >2 mmol/L |
| Creatinine change | At least two valid values at distinct in-window times | Maximum later value minus first value >=0.3 mg/dL |
| Urine output | Valid events and complete 24-hour structured observation | Total <720 mL/24 h |
| Cardiac index | Guideline-specified oxygen-saturation-derived value | Minimum <=2.2 L/min/m2; UNKNOWN in the study source |

An evaluable value that does not meet its threshold is FALSE. A criterion that cannot be evaluated is UNKNOWN. Partial urine-output observation is not treated as normal output, and one creatinine measurement is not sufficient for a change criterion.

The published guideline text reports the creatinine-change unit as mg/mL. This implementation retains the numerical threshold of 0.3 but uses mg/dL, consistent with the conventional SCAI shock definition. For cardiac index, the guideline specifies a value derived from peripheral arterial and mixed venous oxygen saturation. MIMIC itemid 228368 is a NICOM measurement and is not treated as an interchangeable source; the cardiac-index state is therefore UNKNOWN for all study records.

## Final state

- POSITIVE: at least one domain is TRUE.
- NEGATIVE: all four domains are FALSE.
- INDETERMINATE: no domain is TRUE and at least one domain is UNKNOWN.

The strict definition does not add broader hemodynamic, neurologic, treatment, respiratory-support, or downstream outcome variables.
