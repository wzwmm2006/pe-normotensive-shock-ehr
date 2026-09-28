"""Shared public phenotype logic for the v2 two-database analysis.

The primary empirical construct is a three-domain set of guideline-derived
hypoperfusion criteria:

    lactate, creatinine change, urine output

A guideline-compatible cardiac index cannot be reconstructed from the
structured sources available to this study. It is carried as a computability
boundary (see phenotype/four_domain_boundary_spec.yaml) and never enters the
primary classification.

Every criterion is TRUE, FALSE, or UNKNOWN. UNKNOWN means that the criterion
cannot be evaluated from the prespecified structured source inside the
prespecified analysis window. UNKNOWN never means that a measurement was
clinically absent, and it is never an assertion about care delivered.

No function in this module reads a database, a file path, or an outcome
variable. Callers pass standardized local extracts.
"""

from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence

import pandas as pd

THREE_DOMAINS = ("lactate", "creatinine_delta", "urine_output")
BOUNDARY_DOMAIN = "cardiac_index"
STATES = frozenset({"TRUE", "FALSE", "UNKNOWN"})

ANALYSIS_WINDOW_HOURS = (0.0, 24.0)
LACTATE_POSITIVE_ABOVE = 2.0
CREATININE_DELTA_POSITIVE_AT = 0.3
CREATININE_BASELINE_WINDOW_HOURS = (-24.0, 0.0)
CREATININE_MAX_PAIR_SPAN_HOURS = 24.0
URINE_POSITIVE_BELOW_ML = 720.0
URINE_COMPLETE_HOURS = 24.0

SBP_HYPOTENSION_BELOW = 90.0
SBP_PLAUSIBLE_ABOVE = 0.0
SBP_PLAUSIBLE_BELOW = 400.0

POSITIVE = "POSITIVE"
FULLY_OBSERVED_NEGATIVE = "FULLY_OBSERVED_NEGATIVE"
INDETERMINATE = "INDETERMINATE"
NOT_CLASSIFIABLE = "NOT_CLASSIFIABLE"
APPARENT_NEGATIVE = "APPARENT_NEGATIVE"

BOUNDARY_STATE = "UNKNOWN"
BOUNDARY_REASON = (
    "Guideline-compatible cardiac index requires peripheral arterial and mixed "
    "venous oxygen-saturation provenance. No structured source available to the "
    "study satisfies that measurement requirement, so this domain is a "
    "computability boundary and not an empirical domain."
)


def _is_number(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != "" and value.strip().lower() not in {"nan", "none"}
    try:
        return not math.isnan(float(value))
    except (TypeError, ValueError):
        return False


def _numbers(values: Iterable[object]) -> list[float]:
    return [float(value) for value in values if _is_number(value)]


def _pairs(hours: Iterable[object], values: Iterable[object]) -> list[tuple[float, float]]:
    paired = [
        (float(hour), float(value))
        for hour, value in zip(hours, values)
        if _is_number(hour) and _is_number(value)
    ]
    return sorted(paired, key=lambda item: item[0])


def lactate_state(values: Iterable[object]) -> str:
    """Evaluable with at least one in-window value; positive above 2 mmol/L."""
    valid = _numbers(values)
    if not valid:
        return "UNKNOWN"
    return "TRUE" if max(valid) > LACTATE_POSITIVE_ABOVE else "FALSE"


def _primary_creatinine_delta(pairs: Sequence[tuple[float, float]]) -> float | None:
    low, high = ANALYSIS_WINDOW_HOURS
    in_window = [item for item in pairs if low <= item[0] <= high]
    if len({hour for hour, _ in in_window}) < 2:
        return None
    reference_hour, reference_value = in_window[0]
    later = [value for hour, value in in_window if hour > reference_hour]
    if not later:
        return None
    return max(later) - reference_value


def _pre_index_creatinine_delta(pairs: Sequence[tuple[float, float]]) -> float | None:
    low, high = ANALYSIS_WINDOW_HOURS
    baseline_low, baseline_high = CREATININE_BASELINE_WINDOW_HOURS
    best: float | None = None
    for hour, value in pairs:
        if not low <= hour <= high:
            continue
        baselines = [
            baseline_value
            for baseline_hour, baseline_value in pairs
            if baseline_low <= baseline_hour <= baseline_high
            and baseline_hour < hour
            and (hour - baseline_hour) <= CREATININE_MAX_PAIR_SPAN_HOURS
        ]
        if baselines:
            delta = value - min(baselines)
            best = delta if best is None else max(best, delta)
    return best


def creatinine_delta_value(
    hours: Iterable[object], values: Iterable[object], extended_baseline: bool = False
) -> float | None:
    """Serial change over the primary rule, optionally with a pre-index baseline.

    Primary rule: earliest valid value in 0-24 h as the reference and the
    maximum strictly later value in the same window; at least two distinct
    measurement times are required.

    Extended-baseline sensitivity: a subtraction pair may also take its
    reference from -24 h to 0 h, provided the two values are at most 24 h
    apart. The sensitivity contains the primary rule as a subset.
    """
    pairs = _pairs(hours, values)
    primary = _primary_creatinine_delta(pairs)
    if not extended_baseline:
        return primary
    pre_index = _pre_index_creatinine_delta(pairs)
    candidates = [item for item in (primary, pre_index) if item is not None]
    return max(candidates) if candidates else None


def creatinine_delta_state(
    hours: Iterable[object], values: Iterable[object], extended_baseline: bool = False
) -> str:
    """Positive when the serial change reaches 0.3 mg/dL.

    The published guideline prints 0.3 mg/mL; this operational adaptation uses
    0.3 mg/dL, consistent with standard acute-kidney-injury and SCAI usage.
    """
    delta = creatinine_delta_value(hours, values, extended_baseline=extended_baseline)
    if delta is None:
        return "UNKNOWN"
    return "TRUE" if delta >= CREATININE_DELTA_POSITIVE_AT else "FALSE"


def urine_output_state(amounts: Iterable[object], coverage_hours: object) -> str:
    """Evaluable with a complete 24 h observation and at least one valid event.

    Amounts are expected to be already corrected and nonnegative. An absent
    charted value is not a zero amount, and partial observation is not treated
    as normal output.
    """
    if not _is_number(coverage_hours) or float(coverage_hours) < URINE_COMPLETE_HOURS:
        return "UNKNOWN"
    valid = [value for value in _numbers(amounts) if value >= 0]
    if not valid:
        return "UNKNOWN"
    return "TRUE" if sum(valid) < URINE_POSITIVE_BELOW_ML else "FALSE"


def three_domain_states(
    lactate_values: Iterable[object] = (),
    creatinine_hours: Iterable[object] = (),
    creatinine_values: Iterable[object] = (),
    urine_amounts: Iterable[object] = (),
    urine_coverage_hours: object = None,
    extended_baseline: bool = False,
) -> dict[str, str]:
    return {
        "lactate_state": lactate_state(lactate_values),
        "creatinine_delta_state": creatinine_delta_state(
            creatinine_hours, creatinine_values, extended_baseline=extended_baseline
        ),
        "urine_output_state": urine_output_state(urine_amounts, urine_coverage_hours),
    }


def normalize_states(record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS) -> dict[str, str]:
    states = {}
    for domain in domains:
        value = str(record[f"{domain}_state"]).upper()
        if value not in STATES:
            raise ValueError(f"Invalid {domain} state: {value}")
        states[domain] = value
    return states


def ascertainment_depth(
    record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS
) -> int:
    states = normalize_states(record, domains)
    return sum(1 for state in states.values() if state != "UNKNOWN")


def classify_three_domain(
    record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS
) -> str:
    states = normalize_states(record, domains)
    if "TRUE" in states.values():
        return POSITIVE
    if all(state == "FALSE" for state in states.values()):
        return FULLY_OBSERVED_NEGATIVE
    return INDETERMINATE


def simulate_missing_as_false(
    record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS
) -> str:
    """Simulated scenario only. UNKNOWN is mapped to FALSE before the OR rule."""
    states = normalize_states(record, domains)
    return POSITIVE if "TRUE" in states.values() else APPARENT_NEGATIVE


def negative_reclassification(
    record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS
) -> bool:
    """Apparent negative under simulated missing-as-false but indeterminate otherwise."""
    return (
        simulate_missing_as_false(record, domains) == APPARENT_NEGATIVE
        and classify_three_domain(record, domains) == INDETERMINATE
    )


def complete_case_classification(
    record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS
) -> str:
    states = normalize_states(record, domains)
    if "UNKNOWN" in states.values():
        return NOT_CLASSIFIABLE
    return POSITIVE if "TRUE" in states.values() else FULLY_OBSERVED_NEGATIVE


def missing_domains(
    record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS
) -> frozenset[str]:
    states = normalize_states(record, domains)
    return frozenset(domain for domain, state in states.items() if state == "UNKNOWN")


def missing_domain_burden(
    record: Mapping[str, object], domains: Sequence[str] = THREE_DOMAINS
) -> int:
    return len(missing_domains(record, domains))


def sbp_filter(
    hours: Iterable[object],
    systolic_values: Iterable[object],
    window_hours: tuple[float, float] = ANALYSIS_WINDOW_HOURS,
) -> dict[str, object]:
    """Operational blood-pressure analysis filter.

    The complete guideline transient-hypotension construct is not faithfully
    reconstructable from structured charting, so this rule is documented as an
    analysis filter and not as guideline normotension. See docs/guideline_fidelity.md.
    """
    eligible = [
        (float(hour), float(value))
        for hour, value in zip(hours, systolic_values)
        if _is_number(hour)
        and _is_number(value)
        and window_hours[0] <= float(hour) <= window_hours[1]
        and SBP_PLAUSIBLE_ABOVE < float(value) < SBP_PLAUSIBLE_BELOW
    ]
    below = sum(1 for _, value in eligible if value < SBP_HYPOTENSION_BELOW)
    observable = len(eligible) > 0
    return {
        "sbp_observable": observable,
        "eligible_sbp_n": len(eligible),
        "sbp_below_90_n": below,
        "sbp_min": min((value for _, value in eligible), default=float("nan")),
        "sbp_filter_pass_zero_below_90": observable and below == 0,
        "sbp_filter_pass_fewer_than_two_below_90": observable and below < 2,
    }


def build_three_domain_matrix(
    record_keys: Iterable[object],
    events: pd.DataFrame,
    coverage: pd.DataFrame,
    extended_baseline: bool = False,
) -> pd.DataFrame:
    """Build the public three-domain matrix from a standardized event contract.

    events columns: record_key, domain, hours_from_index, value
    coverage columns: record_key, urine_coverage_hours
    """
    required_events = {"record_key", "domain", "hours_from_index", "value"}
    if not required_events.issubset(events.columns):
        raise ValueError(f"Events input requires columns: {sorted(required_events)}")
    if not {"record_key", "urine_coverage_hours"}.issubset(coverage.columns):
        raise ValueError("Coverage input requires record_key and urine_coverage_hours")
    unexpected = set(events["domain"].dropna()) - set(THREE_DOMAINS) - {BOUNDARY_DOMAIN}
    if unexpected:
        raise ValueError(f"Unexpected event domains: {sorted(unexpected)}")

    events = events.copy()
    events["hours_from_index"] = pd.to_numeric(events["hours_from_index"], errors="coerce")
    coverage_map = coverage.set_index("record_key")["urine_coverage_hours"].to_dict()
    window_low, window_high = ANALYSIS_WINDOW_HOURS
    rows = []
    for key in pd.Series(list(record_keys)).drop_duplicates():
        record = events[events["record_key"] == key]
        in_window = record[record["hours_from_index"].between(window_low, window_high)]
        creatinine = record[record["domain"] == "creatinine_delta"]
        states = three_domain_states(
            lactate_values=in_window.loc[in_window["domain"] == "lactate", "value"],
            creatinine_hours=creatinine["hours_from_index"],
            creatinine_values=creatinine["value"],
            urine_amounts=in_window.loc[in_window["domain"] == "urine_output", "value"],
            urine_coverage_hours=coverage_map.get(key),
            extended_baseline=extended_baseline,
        )
        rows.append({"record_key": key, **states, "cardiac_index_boundary_state": BOUNDARY_STATE})
    return annotate_matrix(pd.DataFrame(rows))


def annotate_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    """Add the three-domain classification columns to a state table.

    Input columns: record_key and the three per-domain state columns.
    """
    required = {"record_key", *(f"{domain}_state" for domain in THREE_DOMAINS)}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"State input requires columns: {sorted(missing)}")
    result = frame.copy()
    records = result.to_dict("records")
    result["three_domain_depth"] = [ascertainment_depth(record) for record in records]
    result["three_domain_classification"] = [
        classify_three_domain(record) for record in records]
    result["simulated_missing_as_false_classification"] = [
        simulate_missing_as_false(record) for record in records]
    result["negative_reclassification_under_missing_as_false"] = [
        negative_reclassification(record) for record in records]
    result["complete_case_classification"] = [
        complete_case_classification(record) for record in records]
    result["missing_domain_burden"] = [missing_domain_burden(record) for record in records]
    return result


def summarize_three_domain(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    """Aggregate counts for one cohort. Input is a matrix from this module."""
    total = len(frame)
    rows: list[dict[str, object]] = []

    def add(section: str, metric: str, value: int) -> None:
        rows.append({
            "cohort": label,
            "section": section,
            "metric": metric,
            "record_n": int(value),
            "denominator_n": int(total),
            "pct": round(100 * value / total, 2) if total else float("nan"),
        })

    add("0_COHORT", "records", total)
    depth = frame["three_domain_depth"].value_counts()
    for depth_value in range(4):
        add("A_ASCERTAINMENT_DEPTH", f"evaluable_domains_{depth_value}",
            int(depth.get(depth_value, 0)))
    for domain in THREE_DOMAINS:
        states = frame[f"{domain}_state"]
        add("B_DOMAIN_EVALUABILITY", f"{domain}_evaluable", int(states.ne("UNKNOWN").sum()))
        add("B_DOMAIN_EVALUABILITY", f"{domain}_TRUE", int(states.eq("TRUE").sum()))
    classification = frame["three_domain_classification"].value_counts()
    add("C_THREE_STATE", "positive", int(classification.get(POSITIVE, 0)))
    add("C_THREE_STATE", "fully_observed_negative",
        int(classification.get(FULLY_OBSERVED_NEGATIVE, 0)))
    add("C_THREE_STATE", "indeterminate", int(classification.get(INDETERMINATE, 0)))
    simulated = frame["simulated_missing_as_false_classification"].value_counts()
    add("D_SIMULATED_MISSING_AS_FALSE", "positive", int(simulated.get(POSITIVE, 0)))
    add("D_SIMULATED_MISSING_AS_FALSE", "apparent_negative",
        int(simulated.get(APPARENT_NEGATIVE, 0)))
    add("D_SIMULATED_MISSING_AS_FALSE", "negative_reclassification",
        int(frame["negative_reclassification_under_missing_as_false"].sum()))
    complete = frame["complete_case_classification"].value_counts()
    add("E_COMPLETE_CASE", "complete_case_evaluable",
        int(complete.get(POSITIVE, 0) + complete.get(FULLY_OBSERVED_NEGATIVE, 0)))
    add("E_COMPLETE_CASE", "complete_case_positive", int(complete.get(POSITIVE, 0)))
    add("E_COMPLETE_CASE", "complete_case_negative",
        int(complete.get(FULLY_OBSERVED_NEGATIVE, 0)))
    return pd.DataFrame(rows)


def site_level_table(frame: pd.DataFrame, site_column: str = "site_key") -> pd.DataFrame:
    """One row per anonymous site. Local-use output only; not for publication."""
    rows = []
    for site, block in frame.groupby(site_column):
        total = len(block)
        rows.append({
            site_column: site,
            "records": total,
            "lactate_evaluable_n": int(block["lactate_state"].ne("UNKNOWN").sum()),
            "creatinine_evaluable_n": int(block["creatinine_delta_state"].ne("UNKNOWN").sum()),
            "urine_output_evaluable_n": int(block["urine_output_state"].ne("UNKNOWN").sum()),
            "all_three_evaluable_n": int(block["three_domain_depth"].eq(3).sum()),
            "indeterminate_n": int(block["three_domain_classification"].eq(INDETERMINATE).sum()),
            "three_domain_positive_n": int(
                block["three_domain_classification"].eq(POSITIVE).sum()),
        })
    table = pd.DataFrame(rows).sort_values(site_column).reset_index(drop=True)
    for column in ("lactate_evaluable", "creatinine_evaluable", "urine_output_evaluable",
                   "all_three_evaluable", "indeterminate", "three_domain_positive"):
        table[f"{column}_pct"] = (100 * table[f"{column}_n"] / table["records"]).round(2)
    return table


def site_distribution_summary(
    table: pd.DataFrame, thresholds: Sequence[int] = (10, 20, 30)
) -> pd.DataFrame:
    """Publishable aggregate distribution of site-level observability."""
    metrics = ("lactate_evaluable_pct", "creatinine_evaluable_pct",
               "urine_output_evaluable_pct", "all_three_evaluable_pct",
               "indeterminate_pct")
    rows = []
    for threshold in thresholds:
        subset = table[table["records"] >= threshold]
        for metric in metrics:
            values = subset[metric]
            rows.append({
                "minimum_site_records": threshold,
                "sites": len(subset),
                "records": int(subset["records"].sum()),
                "metric": metric,
                "median": round(float(values.median()), 2) if len(values) else float("nan"),
                "iqr_low": round(float(values.quantile(.25)), 2) if len(values) else float("nan"),
                "iqr_high": round(float(values.quantile(.75)), 2) if len(values) else float("nan"),
                "minimum": round(float(values.min()), 2) if len(values) else float("nan"),
                "maximum": round(float(values.max()), 2) if len(values) else float("nan"),
            })
    return pd.DataFrame(rows)
