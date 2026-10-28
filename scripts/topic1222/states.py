"""Domain states and urine-coverage rules for the corrected Topic1222 analysis.

This module implements the four corrections that separate the v3.0.0
implementation from the historical v2.0.2 code:

1. A serial creatinine rise is compared in decimal arithmetic, so an increase
   from 0.4 to 0.7 mg/dL meets the inclusive >= 0.3 mg/dL threshold instead of
   failing a binary floating-point comparison.
2. The eICU-CRD analysis unit is the ICU stay. Person-level keys are never used
   to pivot, group or de-duplicate the rule cross-tabulations: every count is a
   count of analysis records.
3. Every urine-coverage rule resets both the positive and the negative urine
   state before the rule is applied, and the three-domain classification is then
   re-derived for every record.
4. eICU-CRD event offsets are minutes. The 24-hour window is 1,440 minutes and is
   converted to hours only for reporting.

Terminology follows the manuscript: a domain is evaluable when the prespecified
structured source can be read inside the prespecified window, and a structured
UNKNOWN never means that a measurement was clinically absent.
"""

from decimal import Decimal

import numpy as np
import pandas as pd
from scipy.stats import beta

DOMAINS = ("lactate", "creatinine_delta", "urine_output")
STATES = ("TRUE", "FALSE", "UNKNOWN")
CLASSES = ("POSITIVE", "NEGATIVE", "UNRESOLVED")

RULES = (
    "B0_full24_any_event",
    "S1_endpoints",
    "S2_endpoints_gap4",
    "S3_span20_gap4",
)

WINDOW_HOURS = (0.0, 24.0)
LACTATE_THRESHOLD_MMOL_L = Decimal("2")
CREATININE_THRESHOLD_MG_DL = Decimal("0.3")
URINE_POSITIVE_THRESHOLD_ML = Decimal("720")

# eICU-CRD offsets are minutes. One day is 1,440 minutes, not 24 units of a
# field that happens to be named after hours.
MINUTES_PER_DAY = 1440
OFFSET_UNITS = {"MIMIC-IV": "hours", "eICU-CRD": "minutes"}

LACTATE_ANALYTE = "lactate"
CREATININE_ANALYTE = "creatinine"


def to_decimal(value):
    """Return a Decimal for a numeric value without binary-float drift."""
    return Decimal(str(value))


def _finite(value):
    try:
        return value is not None and np.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _finite_column(frame, column):
    return frame[column].map(_finite)


def lactate_state(values):
    """Operational lactate state from the values observed inside the window."""
    measured = [to_decimal(v) for v in values if _finite(v)]
    if not measured:
        return "UNKNOWN"
    return "TRUE" if max(measured) > LACTATE_THRESHOLD_MMOL_L else "FALSE"


def creatinine_delta_value(hours, values, window=WINDOW_HOURS):
    """Serial creatinine change in mg/dL, or None when the pair is unevaluable.

    The reference is the lowest finite value at the earliest observed offset and
    the index value is the highest finite value at a strictly later offset. At
    least two distinct offsets are required. Repeated results at one offset are
    resolved deterministically, lowest as reference and highest as index, so an
    ambiguous pair never silently changes the classification. The difference is
    computed with :class:`decimal.Decimal` so that an increase of 0.4 to
    0.7 mg/dL reaches the inclusive >= 0.3 mg/dL threshold exactly; this is
    correction 1 of the release.
    """
    pairs = [
        (float(hour), to_decimal(value))
        for hour, value in zip(hours, values)
        if _finite(value) and _finite(hour)
        and window[0] <= float(hour) <= window[1]
    ]
    offsets = sorted({hour for hour, _ in pairs})
    if len(offsets) < 2:
        return None
    first_hour = offsets[0]
    baseline = min(value for hour, value in pairs if hour == first_hour)
    later = [value for hour, value in pairs if hour > first_hour]
    return max(later) - baseline


def creatinine_delta_state(hours, values, threshold=CREATININE_THRESHOLD_MG_DL,
                           window=WINDOW_HOURS):
    """TRUE / FALSE / UNKNOWN for the serial creatinine-change criterion."""
    delta = creatinine_delta_value(hours, values, window)
    if delta is None:
        return "UNKNOWN"
    return "TRUE" if delta >= threshold else "FALSE"


def lactate_state_for_pairs(hours, values, window=WINDOW_HOURS):
    """Window-restricted wrapper around :func:`lactate_state`."""
    inside = [value for hour, value in zip(hours, values)
              if _finite(hour) and window[0] <= float(hour) <= window[1]]
    return lactate_state(inside)


def creatinine_delta_state_for_pairs(hours, values, window=WINDOW_HOURS):
    """Window-restricted wrapper around :func:`creatinine_delta_state`."""
    return creatinine_delta_state(hours, values, window=window)


def _states_from_pairs(pairs, function, keys, key_column):
    rows = {}
    for key, block in pairs.groupby(key_column, sort=False):
        rows[key] = function(block["offset_hours"].tolist(), block["value"].tolist())
    series = pd.Series(rows, dtype="object")
    series.name = "state"
    return series.reindex(pd.Index(keys)).fillna("UNKNOWN")


def analyte_states(lab_series, analyte, record_keys, key_column="record_key",
                   offset_column="offset_hours", value_column="value",
                   window=WINDOW_HOURS):
    """Re-derive one laboratory domain state for every analysis record.

    ``lab_series`` follows the standardised contract: one row per measured result
    with the analyte name and the offset in hours from the database-specific
    index. Records without an evaluable pair, including records with no result,
    are returned as UNKNOWN.
    """
    frame = lab_series[
        lab_series["analyte"].astype(str).str.strip().str.lower().eq(analyte)
    ]
    frame = frame[
        _finite_column(frame, offset_column) & _finite_column(frame, value_column)
    ]
    frame = frame[frame[key_column].isin(list(record_keys))]
    pairs = frame[[key_column, offset_column, value_column]].rename(
        columns={offset_column: "offset_hours", value_column: "value"}
    )
    function = (lactate_state_for_pairs if analyte == LACTATE_ANALYTE
                else creatinine_delta_state_for_pairs)
    return _states_from_pairs(pairs, function, record_keys, key_column)


def lactate_states(lab_series, record_keys, **kwargs):
    """Lactate states for the given analysis records."""
    return analyte_states(lab_series, LACTATE_ANALYTE, record_keys, **kwargs)


def creatinine_delta_states(lab_series, record_keys, **kwargs):
    """Serial creatinine-change states for the given analysis records."""
    return analyte_states(lab_series, CREATININE_ANALYTE, record_keys, **kwargs)


def full_window_covered(urine):
    """Resolve the 24-hour intensive-care observation requirement.

    ``unit_window_minutes`` holds the observed intensive-care unit window in
    minutes, so 1,440 minutes is the 24-hour requirement (correction 4). When the
    source also supplies an explicit ``window_complete`` flag it takes precedence,
    because overlapping or spliced intensive-care intervals can make a summed
    duration disagree with the flagged window.
    """
    minutes_rule = urine["unit_window_minutes"].ge(MINUTES_PER_DAY)
    minutes_rule = minutes_rule.fillna(False).astype(bool)
    if "window_complete" not in urine.columns:
        return minutes_rule
    explicit = urine["window_complete"].astype("boolean")
    resolved = explicit.fillna(pd.Series(minutes_rule, index=urine.index).astype("boolean"))
    return resolved.fillna(False).astype(bool)


def urine_rule_eligibility(urine):
    """Boolean eligibility for each urine-coverage rule.

    ``urine`` must be indexed like the domain state table and must provide the
    standardised urine coverage fields: ``records_valid_in_window``,
    ``first_hours``, ``last_hours``, ``max_gap_hours``, ``observed_span_hours``,
    ``unit_window_minutes`` and, optionally, ``window_complete``.
    """
    any_event = urine["records_valid_in_window"].gt(0)
    full_window = full_window_covered(urine)
    base = any_event & full_window
    endpoint = base & urine["first_hours"].le(4) & urine["last_hours"].ge(20)
    gap = endpoint & urine["max_gap_hours"].le(4)
    span20 = gap & urine["observed_span_hours"].ge(20)
    return pd.DataFrame(
        {
            "B0_full24_any_event": base,
            "S1_endpoints": endpoint,
            "S2_endpoints_gap4": gap,
            "S3_span20_gap4": span20,
        }
    )


def apply_urine_rule(states, urine, rule):
    """Reset the urine domain and re-derive it under one coverage rule.

    Both the positive and the negative urine state are cleared first, so a record
    that was evaluable under a looser rule cannot keep its earlier state when a
    stricter rule applies. This is correction 3 of the release.
    """
    if rule not in RULES:
        raise ValueError("unknown urine rule: " + str(rule))
    eligible = urine_rule_eligibility(urine)[rule].reindex(states.index)
    eligible = eligible.fillna(False).astype(bool)
    total = urine["total_ml"].reindex(states.index)
    frame = states.copy()
    frame["urine_output"] = "UNKNOWN"
    frame.loc[eligible & total.lt(float(URINE_POSITIVE_THRESHOLD_ML)), "urine_output"] = "TRUE"
    frame.loc[eligible & total.ge(float(URINE_POSITIVE_THRESHOLD_ML)), "urine_output"] = "FALSE"
    return frame


def classify_records(states):
    """Three-state classification: any TRUE, all FALSE, otherwise unresolved."""
    positive = states.eq("TRUE").any(axis=1)
    negative = states.eq("FALSE").all(axis=1)
    return pd.Series(
        np.select([positive, negative], ["POSITIVE", "NEGATIVE"], default="UNRESOLVED"),
        index=states.index,
        name="classification",
    )


def direct_positive(states):
    """Records with a directly observed positive laboratory criterion."""
    return states[["lactate", "creatinine_delta"]].eq("TRUE").any(axis=1)


def clopper_pearson(k, n):
    """Exact binomial interval used for the reported retention percentages."""
    if n == 0:
        return (float("nan"), float("nan"))
    low = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    high = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return (low, high)


def summarize_rule(states, urine, database, rule, direct=None):
    """One row of the published coverage-and-retention ladder."""
    revised = apply_urine_rule(states, urine, rule)
    eligible = urine_rule_eligibility(urine)[rule].reindex(states.index)
    eligible = eligible.fillna(False).astype(bool)
    complete_case = revised.ne("UNKNOWN").all(axis=1)
    positive = revised.eq("TRUE").any(axis=1)
    negative = revised.eq("FALSE").all(axis=1)
    direct = (direct_positive(states) if direct is None
              else direct.reindex(states.index).fillna(False).astype(bool))
    direct_total = int(direct.sum())
    retained = int((direct & complete_case).sum())
    low, high = (clopper_pearson(retained, direct_total) if direct_total
                 else (float("nan"), float("nan")))
    return {
        "database": database,
        "rule": rule,
        "denominator_N": len(revised),
        "urine_evaluable_N": int(eligible.sum()),
        "urine_positive_N": int(revised["urine_output"].eq("TRUE").sum()),
        "urine_negative_N": int(revised["urine_output"].eq("FALSE").sum()),
        "positive_N": int(positive.sum()),
        "negative_N": int(negative.sum()),
        "unresolved_N": int((~positive & ~negative).sum()),
        "complete_case_N": int(complete_case.sum()),
        "direct_positive_N": direct_total,
        "direct_positive_retained_N": retained,
        "direct_positive_excluded_N": direct_total - retained,
        "urine_only_positive_N": int((~direct & revised["urine_output"].eq("TRUE")).sum()),
        "retention_pct": 100 * retained / direct_total if direct_total else float("nan"),
        "retention_ci_low_pct": 100 * low,
        "retention_ci_high_pct": 100 * high,
    }


def coverage_ladder(states, urine, database):
    """The four-rule coverage-and-retention ladder for one database."""
    direct = direct_positive(states)
    rows = [summarize_rule(states, urine, database, rule, direct) for rule in RULES]
    return pd.DataFrame(rows)


def baseline_domain_states(states, database):
    """Baseline TRUE / FALSE / UNKNOWN counts per domain."""
    rows = []
    for domain in DOMAINS:
        for state in STATES:
            rows.append(
                {
                    "database": database,
                    "domain": domain,
                    "state": state,
                    "N": int(states[domain].eq(state).sum()),
                    "denominator_N": len(states),
                }
            )
    return pd.DataFrame(rows)


def direct_urine_crosstab(states, urine, database):
    """Direct laboratory positivity against the urine state for every rule."""
    direct = direct_positive(states)
    rows = []
    for rule in RULES:
        revised = apply_urine_rule(states, urine, rule)
        for value in (False, True):
            for state in STATES:
                rows.append(
                    {
                        "database": database,
                        "rule": rule,
                        "direct_positive": value,
                        "urine_state": state,
                        "N": int((direct.eq(value) & revised["urine_output"].eq(state)).sum()),
                        "denominator_N": len(states),
                    }
                )
    return pd.DataFrame(rows)


def three_domain_crosstab(states, urine, database):
    """Every lactate / creatinine / urine combination for every rule."""
    rows = []
    for rule in RULES:
        revised = apply_urine_rule(states, urine, rule)
        for lactate in STATES:
            for creatinine in STATES:
                for urine_state in STATES:
                    mask = (
                        revised["lactate"].eq(lactate)
                        & revised["creatinine_delta"].eq(creatinine)
                        & revised["urine_output"].eq(urine_state)
                    )
                    rows.append(
                        {
                            "database": database,
                            "rule": rule,
                            "lactate": lactate,
                            "creatinine": creatinine,
                            "urine": urine_state,
                            "N": int(mask.sum()),
                            "denominator_N": len(states),
                        }
                    )
    return pd.DataFrame(rows)


def state_transitions(states, urine, database):
    """Classification changes from the B0 baseline to each rule."""
    baseline = classify_records(states)
    rows = []
    for rule in RULES:
        revised = classify_records(apply_urine_rule(states, urine, rule))
        for before in CLASSES:
            for after in CLASSES:
                mask = baseline.eq(before) & revised.eq(after)
                rows.append(
                    {
                        "database": database,
                        "rule": rule,
                        "baseline_state": before,
                        "revised_state": after,
                        "N": int(mask.sum()),
                        "denominator_N": len(states),
                    }
                )
    return pd.DataFrame(rows)