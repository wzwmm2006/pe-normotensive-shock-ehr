# Phenotype Definition

## Scope

The primary empirical analysis evaluates three guideline-derived hypoperfusion
criteria that can be operationalized from structured sources:

1. lactate above 2 mmol/L;
2. creatinine increase of at least 0.3 mg/dL within the window;
3. urine output below 720 mL per 24 hours with complete structured observation.

A fourth guideline criterion, cardiac index at or below 2.2 L/min/m2 from
peripheral arterial and mixed venous oxygen-saturation values, cannot be
operationalized from either structured source and is reported as a computability
boundary. See `phenotype/four_domain_boundary_spec.yaml` and
`docs/guideline_fidelity.md`.

The machine-readable specification is
`phenotype/three_domain_observability_spec.yaml`.

## Analysis population and window

The phenotype is applied inside the SBP-filtered analysis cohort, which is built
before any domain is evaluated:

- MIMIC-IV: admissions with at least one eligible timestamped systolic pressure
  in the 0 to +24 h window after the acute-PE imaging index, and zero observed
  systolic pressures below 90 mmHg.
- eICU-CRD: first eligible documented-PE ICU stay per hospital admission with
  the same rule applied over the first 24 h after ICU admission.

The blood-pressure rule is an operational analysis filter. It is not a
reconstruction of the guideline hypotension construct, because the greater than
40 mmHg decrease, the sub-15-minute duration, and the response to intravenous
fluids cannot be faithfully computed. See `docs/guideline_fidelity.md`.

## Domain operationalization

| Domain | Evaluable when | Positive when |
| --- | --- | --- |
| Lactate | at least one valid in-window value | maximum in-window value above 2 mmol/L |
| Creatinine change | at least two valid values at distinct in-window times | maximum later value minus earliest in-window value at least 0.3 mg/dL |
| Urine output | valid events and complete 24 h structured observation | 24 h total below 720 mL |

An evaluable criterion that does not meet its threshold is FALSE. A criterion
that cannot be evaluated is UNKNOWN. Partial urine observation is not treated as
normal output, and a single creatinine value cannot establish a change.

Unit note. The published guideline prints the creatinine-change unit as mg/mL.
This implementation keeps the numeric threshold of 0.3 and uses mg/dL, which
matches conventional acute-kidney-injury and SCAI usage. It is an operational
adaptation, not a literal transcription, and no erratum is claimed. The criterion
is called a `guideline-derived operational renal criterion`.

## Classification

- Positive: at least one domain is TRUE.
- Fully observed negative: all three domains are FALSE.
- Indeterminate: no domain is TRUE and at least one domain is UNKNOWN.

`Fully observed negative` is a statement about the three empirical domains only.
It is not a negative result for the complete four-domain guideline construct.

## Excluded variables

The phenotype does not add mean arterial pressure, Glasgow Coma Scale,
vasopressor use, ventilation, mortality, or any other downstream outcome. No
outcome variable is read anywhere in this repository.