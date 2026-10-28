# Release v3.0.0

## What this release is

Version 3.0.0 is the corrected analysis release for the two-database study of
structured observability of guideline-derived hypoperfusion criteria in pulmonary
embolism. It publishes the non-restricted implementation that reproduces the
frozen manuscript results, a standardised input contract, a synthetic
input-format sample, non-identifying aggregate results, and an automated
reproduction gate.

## What changed in v3.0.0

Corrected analysis code and a public reproduction gate. No scientific result,
table, conclusion, terminology or reference changed. One frozen aggregate changed
because a defect in the analysis code was corrected.

1. Serial creatinine change is compared in decimal arithmetic, so a rise from
   0.4 to 0.7 mg/dL reaches the inclusive `>= 0.3 mg/dL` threshold. The v2
   binary floating-point comparison missed the boundary. This reclassified one
   MIMIC-IV record; the B0 three-state row moved from 42/13/613 to 43/13/612.
   eICU-CRD is unchanged.
2. The eICU-CRD analysis unit is the ICU stay. The ICU-stay identifier is kept
   separate from the person identifier, and person-level identifiers are never
   used to pivot, group or de-duplicate the rule cross-tabulations.
3. Every urine-coverage rule (B0 and S1-S3) resets both the positive and the
   negative urine state before the rule is applied and re-derives the three-domain
   classification for every record.
4. The eICU-CRD 24-hour window is 1,440 minutes, because eICU offsets are
   minutes, and is converted to hours only for reporting.

## What was published

- `scripts/topic1222/` - the corrected implementation (domain logic, input
  contract, frozen-value gate, command line).
- `examples/synthetic_contract_matrix.csv`, `examples/synthetic_contract_labs.csv`
  - a synthetic input-format sample with invented record labels.
- `results/` - non-identifying aggregate results.
- `tests/test_topic1222_v3.py` - correction and frozen-value locks.

## Primary results reproduced

| Metric | MIMIC-IV | eICU-CRD |
| --- | ---: | ---: |
| Primary cohort (eligible records) | 668 | 1,266 |
| B0 complete case | 18 | 60 |
| Direct-positive laboratory evidence | 36 | 73 |
| B0 direct-positive retention | 4 of 36 | 21 of 73 |
| B0 three-state | 43/13/612 | 207/31/1,028 |
| S3 complete case | 15 | 14 |
| S3 direct-positive retention | 3 of 36 | 6 of 73 |
| S3 three-state | 38/12/618 | 79/8/1,179 |

## Reproduction boundary

The pipeline reproduces the frozen transformation from the standardised inputs in
`scripts/topic1222/contract.py`. It does not re-derive MIMIC-IV or eICU-CRD
source tables. Rebuilding the standardised inputs from PhysioNet data requires
authorized PhysioNet access, so a from-scratch reconstruction of the whole
analysis is not claimed.

## Historical releases

v2.0.2, v2.0.1 and v2.0.0 remain available from their tags and are not modified.
They are superseded by v3.0.0 for manuscript reproducibility. v1.0.1 remains the
single-database release archived at Zenodo under
https://doi.org/10.5281/zenodo.22183069; that DOI identifies v1.0.1 only and must
not be used to cite v3.0.0.

## DOI policy

Do not attach the v1.0.1 DOI to v3.0.0, and do not create a v3.0.0 DOI before
Zenodo has archived the release. Do not move the `v2.0.0`, `v2.0.1`, `v2.0.2` or
`v3.0.0` tag.