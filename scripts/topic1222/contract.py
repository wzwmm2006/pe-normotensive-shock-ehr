"""Standardised, non-restricted input contract for the Topic1222 pipeline.

The release does not redistribute source data. A reader with authorized
PhysioNet access writes the two comma-separated files described below from their
own source extract, then runs the pipeline against them. The contract is the
boundary of reproduction: the pipeline reproduces the frozen transformation from
these standardised inputs, not the licensed extraction that produced them.

``domain_state_matrix.csv`` - one row per database x analysis record x domain:

    database               MIMIC-IV or eICU-CRD
    record_key             analysis record: a hospital admission in MIMIC-IV, an
                           intensive-care stay in eICU-CRD
    domain                 lactate, creatinine_delta or urine_output
    state                  TRUE, FALSE or UNKNOWN; the baseline domain state
    records_valid_in_window  count of usable events inside the 0-24 hour window
    first_hours            hours from the index to the first usable in-window event
    last_hours             hours from the index to the last usable in-window event
    max_gap_hours          largest gap in hours between consecutive usable events
    observed_span_hours    last_hours minus first_hours
    total_ml               summed recorded urine volume in the window
    unit_window_minutes    observed intensive-care unit window in minutes, where
                           1,440 minutes is the 24-hour requirement (eICU-CRD
                           event offsets are minutes, not hours)
    window_complete        optional explicit 24-hour coverage flag where the
                           source provides one (MIMIC-IV); when present and not
                           empty it takes precedence over ``unit_window_minutes``

``lab_series.csv`` - one row per usable measured result inside the window:

    database, record_key, analyte, offset_hours, value

``analyte`` is ``lactate`` or ``creatinine``. ``offset_hours`` is the offset from
the database-specific index, already converted to hours when the source records
minutes. Records absent from ``lab_series`` are UNKNOWN, never FALSE. The
pipeline re-derives the lactate state and the serial creatinine criterion from
this series; the matrix supplies the urine domain and the record enumeration.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .states import (
    DOMAINS,
    STATES,
    creatinine_delta_states,
    lactate_states,
)

DATABASES = ("MIMIC-IV", "eICU-CRD")
ANALYTES = ("lactate", "creatinine")

MATRIX_REQUIRED = (
    "database",
    "record_key",
    "domain",
    "state",
    "records_valid_in_window",
    "first_hours",
    "last_hours",
    "max_gap_hours",
    "observed_span_hours",
    "total_ml",
    "unit_window_minutes",
)
MATRIX_OPTIONAL = ("window_complete",)
LAB_REQUIRED = ("database", "record_key", "analyte", "offset_hours", "value")

URINE_FIELDS = (
    "records_valid_in_window",
    "first_hours",
    "last_hours",
    "max_gap_hours",
    "observed_span_hours",
    "total_ml",
    "unit_window_minutes",
)


class ContractError(ValueError):
    """Raised when an input file does not follow the standardised contract."""


@dataclass(frozen=True)
class InputPaths:
    """Locations of the two standardised input files."""

    matrix: Path
    labs: Path


def _require_columns(frame, columns, name):
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ContractError(
            name + " is missing required columns: " + ", ".join(missing)
        )


def _numeric(frame, columns, name):
    for column in columns:
        try:
            frame[column] = pd.to_numeric(frame[column])
        except (TypeError, ValueError) as error:
            raise ContractError(
                name + " column '" + column + "' is not numeric"
            ) from error
    return frame


def _categorical(frame, column, allowed, name):
    values = set(frame[column].dropna().astype(str).unique())
    unknown = sorted(values - set(allowed))
    if unknown:
        raise ContractError(
            name + " column '" + column + "' carries unsupported values: "
            + ", ".join(unknown)
        )
    if frame[column].isna().any():
        raise ContractError(name + " column '" + column + "' has empty entries")
    return frame


def _read_csv(path, name):
    path = Path(path)
    if not path.is_file():
        raise ContractError(name + " not found at " + path.name)
    frame = pd.read_csv(path, low_memory=False)
    if frame.empty:
        raise ContractError(name + " is empty")
    return frame


def load_matrix(path):
    """Load and validate the standardised domain state matrix."""
    frame = _read_csv(path, "domain_state_matrix.csv")
    _require_columns(frame, MATRIX_REQUIRED, "domain_state_matrix.csv")
    frame = _numeric(
        frame,
        (
            "records_valid_in_window",
            "first_hours",
            "last_hours",
            "max_gap_hours",
            "observed_span_hours",
            "total_ml",
            "unit_window_minutes",
        ),
        "domain_state_matrix.csv",
    )
    _categorical(frame, "database", DATABASES, "domain_state_matrix.csv")
    _categorical(frame, "domain", DOMAINS, "domain_state_matrix.csv")
    _categorical(frame, "state", STATES, "domain_state_matrix.csv")
    frame["record_key"] = frame["record_key"].astype(str)
    if frame["record_key"].eq("").any():
        raise ContractError("domain_state_matrix.csv has an empty record_key")
    duplicated = frame.duplicated(["database", "record_key", "domain"])
    if duplicated.any():
        raise ContractError(
            "domain_state_matrix.csv repeats a database/record_key/domain key "
            + str(int(duplicated.sum())) + " times"
        )
    counts = frame.groupby(["database", "record_key"])["domain"].nunique()
    incomplete = counts[counts.ne(len(DOMAINS))]
    if len(incomplete):
        example = incomplete.index[0]
        raise ContractError(
            "domain_state_matrix.csv must carry all three domains for every "
            "record; " + str(len(incomplete)) + " records do not (for example "
            + str(example) + ")"
        )
    for column in ("unit_window_minutes",):
        if frame[column].isna().all():
            raise ContractError(
                "domain_state_matrix.csv column '" + column + "' is entirely empty"
            )
    return frame


def load_labs(path):
    """Load and validate the standardised laboratory series."""
    frame = _read_csv(path, "lab_series.csv")
    _require_columns(frame, LAB_REQUIRED, "lab_series.csv")
    frame = _numeric(frame, ("offset_hours", "value"), "lab_series.csv")
    _categorical(frame, "database", DATABASES, "lab_series.csv")
    frame["analyte"] = frame["analyte"].astype(str).str.strip().str.lower()
    _categorical(frame, "analyte", ANALYTES, "lab_series.csv")
    frame["record_key"] = frame["record_key"].astype(str)
    if frame["offset_hours"].isna().any() or frame["value"].isna().any():
        raise ContractError(
            "lab_series.csv must carry a finite offset_hours and value on every row"
        )
    return frame


class InputSet:
    """Validated standardised inputs and their per-database analysis tables."""

    def __init__(self, matrix, labs):
        self.matrix = matrix
        self.labs = labs
        self.databases = tuple(
            database for database in DATABASES
            if database in set(matrix["database"])
        )

    def selected(self, database):
        frame = self.matrix[self.matrix["database"].eq(database)]
        return frame if not frame.empty else self._unknown_database(database)

    @staticmethod
    def _unknown_database(database):
        raise ContractError("no records for database " + str(database))

    def lab_series(self, database):
        return self.labs[self.labs["database"].eq(database)].copy()

    def urine_table(self, database):
        """Urine coverage attributes indexed by analysis record."""
        urine = self.selected(database)
        urine = urine[urine["domain"].eq("urine_output")]
        columns = ["record_key"] + list(URINE_FIELDS)
        if "window_complete" in urine.columns:
            columns = columns + ["window_complete"]
        return urine[columns].set_index("record_key").sort_index()

    def wide_states(self, database):
        """Baseline TRUE / FALSE / UNKNOWN state table indexed by record key."""
        frame = self.selected(database)
        wide = frame.pivot(index="record_key", columns="domain", values="state")
        wide = wide[list(DOMAINS)].sort_index()
        if wide.isna().any().any():
            raise ContractError(
                "domain_state_matrix.csv does not cover every domain for every "
                "record in " + str(database)
            )
        return wide

    def corrected_states(self, database):
        """Baseline states with both laboratory domains re-derived.

        The lactate state and the serial creatinine criterion are recomputed from
        ``lab_series``, the latter in decimal arithmetic so that a rise from
        0.4 to 0.7 mg/dL reaches the inclusive >= 0.3 mg/dL threshold (correction
        1). The urine domain is carried from the standardised matrix at its
        baseline state and is reset for every coverage rule by
        :func:`scripts.topic1222.states.apply_urine_rule` (correction 3).
        """
        wide = self.wide_states(database)
        labs = self.lab_series(database)
        lactate = lactate_states(labs, wide.index).reindex(wide.index)
        creatinine = creatinine_delta_states(labs, wide.index).reindex(wide.index)
        wide = wide.copy()
        wide["lactate"] = lactate
        wide["creatinine_delta"] = creatinine
        return wide


def load_inputs(paths):
    """Load and validate the two standardised input files."""
    if not isinstance(paths, InputPaths):
        raise ContractError("load_inputs expects InputPaths")
    return InputSet(load_matrix(paths.matrix), load_labs(paths.labs))