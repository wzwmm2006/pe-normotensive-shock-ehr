from __future__ import annotations

from itertools import combinations
from typing import Iterable, Mapping, Sequence


MARKERS = (
    "lactate",
    "creatinine_delta",
    "urine_output",
    "cardiac_index",
)
STATES = frozenset({"TRUE", "FALSE", "UNKNOWN"})


def normalize_states(record: Mapping[str, str]) -> dict[str, str]:
    states = {marker: str(record[f"{marker}_state"]).upper() for marker in MARKERS}
    invalid = {marker: state for marker, state in states.items() if state not in STATES}
    if invalid:
        raise ValueError(f"Invalid marker states: {invalid}")
    return states


def classify_missing_as_false(record: Mapping[str, str]) -> str:
    states = normalize_states(record)
    return "POSITIVE" if "TRUE" in states.values() else "NEGATIVE"


def classify_complete_case(record: Mapping[str, str]) -> str:
    states = normalize_states(record)
    if "UNKNOWN" in states.values():
        return "NOT_CLASSIFIABLE"
    return "POSITIVE" if "TRUE" in states.values() else "NEGATIVE"


def classify_uncertainty_aware(record: Mapping[str, str]) -> str:
    states = normalize_states(record)
    if "TRUE" in states.values():
        return "POSITIVE"
    if all(state == "FALSE" for state in states.values()):
        return "NEGATIVE"
    return "INDETERMINATE"


def missing_domains(record: Mapping[str, str]) -> frozenset[str]:
    states = normalize_states(record)
    return frozenset(marker for marker, state in states.items() if state == "UNKNOWN")


def structurally_recoverable(record: Mapping[str, str], restored: Iterable[str]) -> bool:
    restored_set = frozenset(restored)
    unknown = missing_domains(record)
    return classify_uncertainty_aware(record) == "INDETERMINATE" and unknown.issubset(restored_set)


def recovery_scenarios(
    records: Sequence[Mapping[str, str]], domains_restored: int
) -> list[dict[str, object]]:
    if domains_restored not in range(1, len(MARKERS) + 1):
        raise ValueError("domains_restored must be between 1 and 4")
    incomplete = [
        record for record in records
        if classify_uncertainty_aware(record) == "INDETERMINATE"
    ]
    rows = []
    for restored in combinations(MARKERS, domains_restored):
        recoverable = sum(structurally_recoverable(record, restored) for record in incomplete)
        rows.append(
            {
                "domains_restored": domains_restored,
                "restored_domains": ";".join(restored),
                "recoverable_n": recoverable,
                "incomplete_n": len(incomplete),
                "recoverable_pct": 100 * recoverable / len(incomplete) if incomplete else 0.0,
            }
        )
    return rows


def optimized_recovery_frontier(
    records: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    frontier = []
    for size in range(1, len(MARKERS) + 1):
        scenarios = recovery_scenarios(records, size)
        maximum = max(row["recoverable_n"] for row in scenarios)
        best = [row for row in scenarios if row["recoverable_n"] == maximum]
        frontier.append(
            {
                "domains_restored": size,
                "best_combination": " OR ".join(str(row["restored_domains"]) for row in best),
                "tied_best_combinations": len(best),
                "recoverable_n": maximum,
                "incomplete_n": best[0]["incomplete_n"],
                "recoverable_pct": best[0]["recoverable_pct"],
            }
        )
    return frontier


def leave_one_marker_out(records: Sequence[Mapping[str, str]]) -> list[dict[str, object]]:
    positive = [record for record in records if classify_uncertainty_aware(record) == "POSITIVE"]
    rows = []
    for removed in MARKERS:
        lost = 0
        for record in positive:
            states = normalize_states(record)
            if states[removed] == "TRUE" and not any(
                state == "TRUE" for marker, state in states.items() if marker != removed
            ):
                lost += 1
        rows.append(
            {
                "removed_marker": removed,
                "positive_n": len(positive),
                "positives_lost_n": lost,
                "positives_lost_pct": 100 * lost / len(positive) if positive else 0.0,
            }
        )
    return rows
