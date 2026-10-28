# v3.0.0 - Corrected analysis code and public reproduction gate

Version 3.0.0 publishes the public, non-restricted Python implementation that
reproduces the frozen two-database results in the manuscript, together with a
standardised input contract, a synthetic input-format sample, non-identifying
aggregate results, and an automated reproduction gate. It supersedes v2.0.2 for
manuscript reproducibility. Older tags are retained unchanged.

## What changed from v2.0.2

Four defects in the v2 analysis code are corrected here. Each correction changes
how a domain state is derived; only the first changes a frozen count.

1. **Serial creatinine change is compared in decimal arithmetic.** A rise from
   0.4 to 0.7 mg/dL must reach the inclusive `>= 0.3 mg/dL` threshold. In binary
   floating point `0.7 - 0.4 = 0.29999999999999993`, so the v2 comparison missed
   the boundary. The corrected comparison accepts the rise. This reclassified one
   MIMIC-IV record, and the frozen MIMIC-IV B0 three-state row moved from
   42/13/613 to 43/13/612. eICU-CRD is unchanged.
2. **The eICU-CRD analysis unit is the ICU stay, not the person.** The ICU-stay
   identifier is kept separate from the person identifier. Person-level
   identifiers are never used to pivot, group or de-duplicate the rule
   cross-tabulations, so two eligible stays of one person remain two records.
3. **Every urine-coverage rule (B0 and S1-S3) resets both the positive and the
   negative urine state before the rule is applied,** then re-derives the
   three-domain classification for every record. In v2 a record could carry a
   stale urine state from a different coverage rule.
4. **The eICU-CRD 24-hour window is 1,440 minutes.** eICU event offsets are
   recorded in minutes, so the full-window test is `>= 1440` minutes, inclusive,
   converted to hours only for reporting. In v2 the minute total was compared
   against 24 as if it were hours.

## Frozen results reproduced by this release

| Metric | MIMIC-IV | eICU-CRD |
| --- | ---: | ---: |
| Primary cohort (eligible records) | 668 | 1,266 |
| B0 complete case | 18 | 60 |
| Direct-positive laboratory evidence | 36 | 73 |
| B0 direct-positive retention | 4 of 36 | 21 of 73 |
| B0 three-state (positive / negative / unresolved) | 43/13/612 | 207/31/1,028 |
| S3 complete case | 15 | 14 |
| S3 direct-positive retention | 3 of 36 | 6 of 73 |
| S3 three-state (positive / negative / unresolved) | 38/12/618 | 79/8/1,179 |

## Reproduction gate

The reproduction gate recomputes the eight metrics above for both databases (16
comparisons in total) from the standardised input contract:

    python -m scripts.topic1222.reproduce \
      --matrix private/contract/domain_state_matrix.csv \
      --labs private/contract/lab_series.csv \
      --output-dir outputs/reproduction_gate

The command exits 0 only when every frozen metric matches and writes
`reproduction_gate.csv`. On the authorized extract, all 16 metrics PASS.

## Reproduction boundary

The published pipeline reproduces the frozen transformation from the standardised
inputs described in `scripts/topic1222/contract.py`. It does not redistribute or
re-derive MIMIC-IV or eICU-CRD source tables. Rebuilding the standardised inputs
from PhysioNet data requires authorized PhysioNet access and remains governed by
the PhysioNet data-use agreements, so a from-scratch reconstruction of the whole
analysis is not claimed. The synthetic sample in `examples/synthetic_contract_*.csv`
exercises the input format and makes the gate report a mismatch on purpose.

## Tests

    py -3.12 -m pytest -q
    62 passed

`tests/test_topic1222_v3.py` locks the 16 frozen metrics as literal constants and
pins the four corrections. `tests/test_public_safety.py` scans the working tree
for restricted identifiers, credentials and local absolute paths.

## Public-release audit

PASS. No patient-level data, no restricted note text, no credentials and no local
absolute paths. Synthetic examples and aggregate results only. See
`PUBLIC_RELEASE_AUDIT.md`.

## Release chain

| Version | Content |
| --- | --- |
| v3.0.0 | Corrected analysis code, standardised input contract, public reproduction gate. Supersedes v2.0.2 for manuscript reproducibility. |
| v2.0.2 | Documentation provenance clarification. Results identical to v2.0.1. |
| v2.0.1 | Corrected eICU cohort-selection procedure and re-frozen counts. |
| v2.0.0 | First two-database release. |
| v1.0.0, v1.0.1 | Single-database releases. Historical, unchanged. |