# Missing-Data Semantics

A disjunctive criterion set behaves differently depending on how a non-evaluable
domain is represented. This document defines the handling used in this
repository and the terminology that goes with it.

## UNKNOWN

UNKNOWN means the criterion cannot be evaluated from the prespecified structured
source inside the prespecified analysis window.

UNKNOWN does not mean:

- the measurement was not made clinically;
- the result was not documented clinically;
- the information was unavailable to treating clinicians.

Those are different claims, and this study does not make them. Only the first
statement, structured-source evaluability, is supported by the data used here.

## Three-state handling (primary)

TRUE, FALSE, and UNKNOWN are retained.

- Positive: at least one domain is TRUE.
- Fully observed negative: all three domains are FALSE.
- Indeterminate: no domain is TRUE and at least one domain is UNKNOWN.

This is the primary classification in this repository.

## Complete case

Only records with all three domains evaluable are classified; every other record
is not classifiable. Complete case requires all three empirical domains, and it
is reported because it is the strictest requirement, not because it is the
preferred implementation. Discarding partially evaluated records also discards
records that a single positive domain would have resolved.

## Simulated missing-as-false

UNKNOWN is mapped to FALSE before the OR rule, so the rule becomes binary: any
TRUE is positive and every other record is an apparent negative.

This is a simulated computational scenario. It is not an observed deployed
system and not evidence about any particular clinical information system.

Reported quantity: records that are indeterminate under three-state handling but
apparent negatives under the simulation.

- Preferred wording: `negative reclassification under simulated missing-as-false
  semantics`.
- Do not use: classification-certainty inflation, misclassification,
  false-negative rate, or diagnostic error. Those phrases assert a comparison
  against a clinical reference standard that this study does not have.

## Cross-database totals

| Quantity | MIMIC (n = 668) | eICU (n = 1,266) |
| --- | ---: | ---: |
| Indeterminate under three-state handling | 613 (91.77%) | 1,028 (81.20%) |
| Negative reclassification under simulated missing-as-false | 613 (91.77%) | 1,028 (81.20%) |

Positive and fully observed negative states are unaffected by the simulation,
because they are already resolved under three-state handling.