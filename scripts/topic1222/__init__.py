"""Corrected three-domain construction for the Topic1222 PE complete-case study.

Public, non-restricted implementation of the four corrections that separate the
current (v3.0.0) analysis from the historical v2.0.2 release:

1. Serial creatinine change is compared in decimal arithmetic, so a rise from
   0.4 to 0.7 mg/dL reaches the inclusive ``>= 0.3 mg/dL`` threshold instead of
   failing a binary floating-point comparison.
2. The eICU-CRD analysis unit is the intensive-care stay. Person-level
   identifiers are never used to pivot, group or de-duplicate the rule
   cross-tabulations; every count is a count of analysis records.
3. Every urine-coverage rule resets both the positive and the negative urine
   state before the rule is applied, then re-derives the three-domain
   classification for every record.
4. eICU-CRD event offsets are minutes. The 24-hour window is 1,440 minutes and is
   converted to hours only for reporting.

``scripts.topic1222.states`` holds the domain logic, ``scripts.topic1222.contract``
the standardised input contract, and ``scripts.topic1222.gate`` the frozen-result
comparison used by the release gate. ``scripts.topic1222.reproduce`` is the CLI.
"""

from .states import (  # noqa: F401
    CLASSES,
    CREATININE_THRESHOLD_MG_DL,
    DOMAINS,
    LACTATE_THRESHOLD_MMOL_L,
    MINUTES_PER_DAY,
    RULES,
    STATES,
    URINE_POSITIVE_THRESHOLD_ML,
    WINDOW_HOURS,
    analyte_states,
    apply_urine_rule,
    baseline_domain_states,
    classify_records,
    clopper_pearson,
    coverage_ladder,
    creatinine_delta_state,
    creatinine_delta_states,
    creatinine_delta_value,
    direct_positive,
    direct_urine_crosstab,
    full_window_covered,
    lactate_state,
    lactate_states,
    state_transitions,
    summarize_rule,
    three_domain_crosstab,
    to_decimal,
    urine_rule_eligibility,
)
from .contract import (  # noqa: F401
    ANALYTES,
    DATABASES,
    ContractError,
    InputPaths,
    InputSet,
    load_inputs,
    load_labs,
    load_matrix,
)
from .gate import (  # noqa: F401
    DATABASE_ORDER,
    FROZEN_METRICS,
    METRIC_ORDER,
    FrozenMetric,
    compare_metrics,
    extract_metrics,
    gate_passed,
    run_gate,
)

__version__ = "3.0.0"

__all__ = [
    "ANALYTES",
    "CLASSES",
    "CREATININE_THRESHOLD_MG_DL",
    "DATABASES",
    "DATABASE_ORDER",
    "DOMAINS",
    "FROZEN_METRICS",
    "FrozenMetric",
    "LACTATE_THRESHOLD_MMOL_L",
    "METRIC_ORDER",
    "MINUTES_PER_DAY",
    "RULES",
    "STATES",
    "URINE_POSITIVE_THRESHOLD_ML",
    "WINDOW_HOURS",
    "ContractError",
    "InputPaths",
    "InputSet",
    "analyte_states",
    "apply_urine_rule",
    "baseline_domain_states",
    "classify_records",
    "clopper_pearson",
    "compare_metrics",
    "coverage_ladder",
    "creatinine_delta_state",
    "creatinine_delta_states",
    "creatinine_delta_value",
    "direct_positive",
    "direct_urine_crosstab",
    "extract_metrics",
    "full_window_covered",
    "gate_passed",
    "lactate_state",
    "lactate_states",
    "load_inputs",
    "load_labs",
    "load_matrix",
    "run_gate",
    "state_transitions",
    "summarize_rule",
    "three_domain_crosstab",
    "to_decimal",
    "urine_rule_eligibility",
    "__version__",
]