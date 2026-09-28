# Guideline Fidelity

This document records how closely the operational criteria in this repository
match the published guideline, and where they do not.

Source guideline: 2026 AHA/ACC/ACCP/ACEP/CHEST/SCAI/SHM/SIR/SVM/SVN guideline for
the evaluation and management of acute pulmonary embolism, Circulation
2026;153:e977-e1051, DOI 10.1161/CIR.0000000000001415. Verbatim quotations below
are from Figure 2 (printed page e990) and the Section 3.2.2 recommendation
footnote (printed page e993).

Official correction reviewed: Journal of the American College of Cardiology
2026;88(6), DOI 10.1016/j.jacc.2026.06.033. The correction replaces Table 4 and
updates one reference. It does not alter Figure 2, does not alter Section 3.2.2,
and does not correct the creatinine unit.

## 1. Guideline text used

Hypotension (Figure 2 footnote):

> Systolic blood pressure <90 or decrease >40 mm Hg lasting <15 min or responding
> to IV fluids.

Normotensive shock, the definition that carries the hypoperfusion markers
(Section 3.2.2 footnote):

> Normotensive shock is defined as isolated hypoperfusion without hypotension
> identified with any of the following markers: serum lactate >2 mmol/L, urine
> output <720 mL in 24 hours, creatinine increase >=0.3 mg/mL in 24 hours,
> cardiac index <=2.2 L/min/m2 from peripheral arterial and mixed venous
> oxygenation saturation values.

## 2. Blood pressure: computability of each element

The primary analysis applies an operational analysis filter, not the guideline
hypotension construct. The elements do not have equal computability.

| Guideline element | Status | Reason |
| --- | --- | --- |
| Systolic pressure below 90 mmHg | COMPUTABLE | Timestamped systolic pressures exist in both databases. |
| Decrease greater than 40 mmHg | PARTIAL | Computable only under an assumed baseline; the guideline does not state one. |
| Duration below 15 minutes | NOT COMPUTABLE | The interval between a low reading and the next reading at or above 90 mmHg is a charting interval, not a measured duration. |
| Response to intravenous fluids | NOT COMPUTABLE | No coded blood-pressure response to a fluid bolus is recorded in either database. |

Decrease of more than 40 mmHg under three candidate baselines, each of which
assumes something the guideline does not specify:

- B1: running maximum before each later reading, then any later reading;
- B2: first reading as baseline, then any later reading;
- B3: adjacent readings.

| Population | n | B1 | B2 | B3 |
| --- | ---: | ---: | ---: | ---: |
| MIMIC SBP-filtered cohort | 668 | 133 (19.91%) | 57 (8.53%) | 55 (8.23%) |
| eICU broad age-restricted cohort | 1,330 | 742 (55.79%) | 288 (21.65%) | 260 (19.55%) |

The spread between baselines is the point: the same records produce materially
different counts depending on an assumption the guideline leaves open. The
observed interval between a low reading and the next reading at or above
90 mmHg was at or below 15 minutes for nearly every record with such an interval
in both databases, because charting is frequent; that interval cannot be read as
a measured duration of hypotension.

Conclusion: the complete guideline transient-hypotension construct is not
faithfully reconstructable from either structured source. The analysis filter is
therefore defined on the one element that is computable:

- at least one eligible timestamped systolic pressure inside 0 to +24 h after the
  database-specific index, and
- zero observed systolic pressures below 90 mmHg.

The retained sensitivity rule is fewer than two observed systolic pressures below
90 mmHg. The filter is called the `SBP-filtered analysis cohort`. It is not
called guideline normotension, and the guideline hypotension construct is not
claimed to have been reconstructed.

## 3. Creatinine change

The guideline prints `creatinine increase >=0.3 mg/mL in 24 hours`. The printed
unit is internally inconsistent: 0.3 mg/mL equals 30 mg/dL, far outside the range
of a 24-hour creatinine change, while the numeric value 0.3 matches the
conventional absolute-increase threshold of 0.3 mg/dL used in acute kidney injury
and in the SCAI shock definition. No erratum resolving the unit was found.

Operational criterion: increase of at least 0.3 mg/dL within the 0 to +24 h
window, from at least two valid creatinine values at distinct times.

- The unit is an operational substitution, stated as a substitution.
- No erratum is claimed to authorize it.
- Equivalence between the printed text and the operational rule is not asserted.
- The criterion is described as a `guideline-derived operational renal criterion`.

Extended-baseline sensitivity: a reference value from -24 h to 0 h relative to
the index may be paired with a later 0 to +24 h value, provided the pair spans at
most 24 hours. This sensitivity contains the primary rule as a subset and is
reported as sensitivity only.

## 4. Urine output

The guideline contains two different operationalizations in the same source:

- Section 3.2.2 footnote: urine output below 720 mL in 24 hours (absolute);
- Figure 2 footnote: urine output below 0.5 mL/kg/hr (weight-indexed).

These are not identical, and they are not merged here. The operational criterion
is the one in the normotensive-shock definition: below 720 mL per 24 hours, with
complete 24 h structured observation. Absent charting is never treated as zero
output; a record without complete observation is UNKNOWN.

## 5. Cardiac index

The guideline attaches an explicit measurement provenance to the number:
`cardiac index <=2.2 L/min/m2 from peripheral arterial and mixed venous
oxygenation saturation values`. A faithful operationalization therefore requires
paired arterial and mixed venous oxygen-saturation measurements from the same
episode.

- MIMIC-IV: the only closely named structured item is `Cardiac Index (CI NICOM)`,
  itemid 228368. NICOM estimates cardiac index from thoracic bioreactance and
  does not carry the required provenance. The mapping is rejected rather than
  treated as equivalent.
- eICU-CRD: monitor-derived and nurse-entered hemodynamic labels exist, including
  a label named `CI`. They are device output without the required provenance, and
  their values are not quality-controlled.

Faithful cardiac-index mapping available: NO, in both databases. Admissions with
a faithful cardiac-index observation: 0. The domain is therefore UNKNOWN for
every record and is reported as a computability boundary, not as an analyzed
domain.

## 6. Terminology decision

- The four-domain construct is a `guideline-derived operational phenotype`. It is
  not `guideline-faithful`, because one of its four domains cannot be
  operationalized from the selected structured sources.
- The individual criteria are `guideline-derived criteria`.
- The primary empirical analysis is a `three-domain empirical observability
  analysis`, or an analysis of `three potentially observable hypoperfusion
  domains`.
- The three-domain result is never called the complete normotensive-shock
  phenotype.

## 7. Scope of this document

- No equivalence is asserted between any substituted mapping and the literal
  guideline text.
- No threshold was changed inside the analysis.
- No outcome variable is loaded anywhere in this repository.