# Missing-Data Semantics

The same marker states can produce different classifications depending on how unavailable criteria are represented.

## Missing-as-false

UNKNOWN is mapped to FALSE. The final rule is binary: any TRUE is POSITIVE and every other record is NEGATIVE. This repository uses missing-as-false only as a deterministic simulation. It is not evidence that any identified clinical system uses this behavior.

## Complete-case

All four domains must be observed. A complete record is POSITIVE if any domain is TRUE and NEGATIVE if all are FALSE. Every incomplete record is NOT_CLASSIFIABLE. This approach preserves the observed/unknown distinction but discards partial information that can establish positivity.

## Uncertainty-aware three-state

TRUE, FALSE, and UNKNOWN are retained. Any TRUE establishes POSITIVE. Four FALSE values establish NEGATIVE. A record with no TRUE and at least one UNKNOWN remains INDETERMINATE.

## Classification-certainty inflation

The descriptive comparison counts records labeled NEGATIVE under missing-as-false but INDETERMINATE under uncertainty-aware logic. It measures disagreement between computational implementations, not disagreement with an independent clinical reference standard.
