# Reproducibility

## Environment

The study code was validated with Python 3.12.10. Package versions are pinned in `requirements.txt`.

## Ordered workflow

1. Obtain authorized access to the required PhysioNet datasets.
2. Store source data outside the repository or under an ignored private directory.
3. Create `config/paths.yaml` from the example and set local paths.
4. Standardize source extracts to the contracts in `data_requirements.md`.
5. Build the authoritative imaging index.
6. Combine ED and ICU blood-pressure ascertainment.
7. Apply the prespecified normotensive rule.
8. Build the four-domain TRUE/FALSE/UNKNOWN matrix.
9. Run implementation-semantics, recovery-frontier, and leave-one-out analyses.
10. Generate aggregate manuscript tables and figures.
11. Run `pytest -q` and complete the public-release audit before sharing code.

## Aggregate manuscript regression constants

The public test suite records the following nonidentifying aggregate values to detect analysis drift:

- analysis population: 719;
- depth 0/1/2/3/4: 488/131/75/25/0;
- uncertainty-aware states positive/indeterminate/negative: 49/670/0;
- missing-as-false certainty-inflation count: 670;
- missing-domain burden 1/2/3/4: 17/52/113/488;
- incomplete records requiring at least two restored domains: 653;
- best single-domain recovery ceiling: 17;
- definite-positive classifications lost after lactate removal: 32.

These constants contain no patient-level records and are used only as regression locks.

## Reproducible versus nonredistributable components

The phenotype logic, item mappings, input contracts, analysis scripts, tests, and synthetic example are public. Source MIMIC tables, notes, local record keys, intermediate encounter matrices, and patient-level outputs are intentionally excluded. Authorized users can recreate those components within their own secure environment.

## Release status

Version 1.0.1 is the definition-fidelity repair release for manuscript submission and is archived at Zenodo under DOI `10.5281/zenodo.22183069`. The version-specific DOI identifies the exact GitHub release used for the repaired manuscript package.
