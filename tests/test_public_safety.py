"""Public-release safety scan over the repository working tree.

Tokens that describe restricted identifiers are assembled from fragments so that
this file does not itself contain the literal strings it searches for.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRECTORIES = {
    ".git", ".pytest_cache", "__pycache__", ".venv", "venv", "node_modules",
    "outputs", "derived", "data", "raw", "cache", "private", "source",
    "final_qa_private",
}
FORBIDDEN_SUFFIXES = (
    ".gz", ".zip", ".7z", ".parquet", ".feather", ".db", ".sqlite", ".duckdb",
    ".dta", ".sas7bdat", ".rds", ".pkl", ".h5",
)
BACKSLASH = chr(92)
LOCAL_PATH_MARKERS = (
    "D:" + BACKSLASH,
    "C:" + BACKSLASH,
    "C:/Us" + "ers",
    "/Us" + "ers/",
    "/ho" + "me/",
)
PATIENT_KEY_TOKENS = (
    "subject" + "_id",
    "hadm" + "_id",
    "stay" + "_id",
    "patientunit" + "stayid",
    "unique" + "pid",
)
CREDENTIAL_TOKENS = (
    "pass" + "word",
    "sec" + "ret",
    "tok" + "en",
    "cred" + "ential",
    "coo" + "kie",
)
OUTCOME_TOKENS = (
    "mortal" + "ity",
    "hospital_expire" + "_flag",
    "death" + "time",
    "diedin" + "hospital",
    "unitdischarge" + "status",
    "discharge" + "status",
    "vasopressor" + "_outcome",
)
SELF = "test_public_safety.py"
PATIENT_TOKEN_EXEMPT = {SELF, "PUBLIC_RELEASE_AUDIT.md"}
CREDENTIAL_TOKEN_EXEMPT = {SELF, "PUBLIC_RELEASE_AUDIT.md", ".gitignore"}
CREDENTIAL_TOKEN_EXEMPT_SUFFIXES = {".md"}
SKIP_TEXT_SUFFIXES = {".png", ".jpg", ".jpeg", ".pdf", ".ico", ".woff", ".svg"}
MAX_CSV_ROWS = 50


def repository_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in SKIP_DIRECTORIES for part in relative.parts[:-1]):
            continue
        if path.name in SKIP_DIRECTORIES:
            continue
        yield path, relative


def text_files():
    for path, relative in repository_files():
        if path.suffix.lower() in SKIP_TEXT_SUFFIXES:
            continue
        yield path, relative


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_no_restricted_or_binary_data_files_are_present():
    offenders = [str(relative) for path, relative in repository_files()
                 if path.name.lower().endswith(FORBIDDEN_SUFFIXES)]
    assert offenders == []


def test_no_local_absolute_paths_in_repository_text():
    offenders = []
    for path, relative in text_files():
        text = read(path)
        for marker in LOCAL_PATH_MARKERS:
            if marker in text:
                offenders.append(f"{relative}: {marker}")
    assert offenders == []


def test_patient_key_tokens_stay_out_of_the_release():
    offenders = []
    for path, relative in text_files():
        if path.name in PATIENT_TOKEN_EXEMPT:
            continue
        text = read(path).lower()
        for token in PATIENT_KEY_TOKENS:
            if token in text:
                offenders.append(f"{relative}: {token}")
    assert offenders == []


def test_credential_tokens_stay_out_of_the_release():
    offenders = []
    for path, relative in text_files():
        if path.name in CREDENTIAL_TOKEN_EXEMPT:
            continue
        if path.suffix.lower() in CREDENTIAL_TOKEN_EXEMPT_SUFFIXES:
            continue
        text = read(path).lower()
        for token in CREDENTIAL_TOKENS:
            if token in text:
                offenders.append(f"{relative}: {token}")
    assert offenders == []


def test_no_pipeline_script_reads_an_outcome_variable():
    offenders = []
    for path, relative in repository_files():
        if path.suffix.lower() != ".py" or path.name == SELF:
            continue
        text = read(path).lower()
        for token in OUTCOME_TOKENS:
            if token in text:
                offenders.append(f"{relative}: {token}")
    assert offenders == []


def test_no_csv_header_carries_an_outcome_or_patient_key_column():
    for path, relative in repository_files():
        if path.suffix.lower() != ".csv":
            continue
        header = " ".join(str(column).lower() for column in pd.read_csv(path, nrows=1).columns)
        for token in OUTCOME_TOKENS + PATIENT_KEY_TOKENS:
            assert token not in header, f"{relative} header carries {token}"


def test_every_csv_is_synthetic_or_aggregate():
    for path, relative in repository_files():
        if path.suffix.lower() != ".csv":
            continue
        frame = pd.read_csv(path)
        assert len(frame) <= MAX_CSV_ROWS, f"{relative} carries {len(frame)} rows"


def test_gitignore_covers_local_and_restricted_locations():
    rules = read(ROOT / ".gitignore")
    for required in ("data/", "outputs/", "derived/", "config/paths.yaml",
                     "*.parquet", "*.gz", "__pycache__/"):
        assert required in rules, required


def test_citation_does_not_attach_an_old_or_unminted_version_doi():
    citation = read(ROOT / "CITATION.cff")
    assert "version: 2.0.0" in citation
    assert "\ndoi:" not in citation
