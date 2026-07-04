"""
Self-improvement engine: learn corrections from each application cycle
and auto-enforce them as lint rules on every future build.

Every mistake becomes a permanent, machine-enforced check. The corrections log
is a structured JSON file where each entry has a rule ID, description, optional
regex pattern, applicable file types, and severity. The `lint_from_corrections()`
function loads these at lint time and runs every pattern against the document text.

Usage:
    # Learn a new rule
    jat learn no_leverage "Do not use 'leverage' in application materials" \
        --pattern "(?i)\\bleverag" --files resume,cover_letter

    # List all learned rules
    jat corrections
"""

import json
import datetime
import re
from pathlib import Path


DEFAULT_CORRECTIONS_PATH = Path(__file__).parent.parent / "config" / "corrections_log.json"


def _resolve_corrections_path(corrections_path: Path | None = None) -> Path:
    """Resolve the corrections log path, falling back to default."""
    if corrections_path and corrections_path.exists():
        return corrections_path
    return DEFAULT_CORRECTIONS_PATH


def load_corrections(corrections_path: Path | None = None) -> list[dict]:
    """Load structured corrections from the log file."""
    path = _resolve_corrections_path(corrections_path)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def lint_from_corrections(
    text: str,
    file_type: str,
    corrections_path: Path | None = None,
) -> list[str]:
    """
    Run all regex-based learned rules from corrections_log.json against text.

    Args:
        text: Document text to check.
        file_type: One of "resume", "cover_letter", "app_questions".
        corrections_path: Optional path to corrections_log.json.

    Returns:
        List of error strings (empty = clean).
    """
    errors = []
    for rule in load_corrections(corrections_path):
        # Skip overrides (they disable old rules, not add new checks)
        if rule.get("severity") == "override":
            continue
        pattern = rule.get("pattern")
        if not pattern:
            continue
        # Check file type applicability
        applicable_types = rule.get("file_types")
        if applicable_types and file_type not in applicable_types:
            continue
        try:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                errors.append(
                    f"[LEARNED:{rule['id']}] {rule['rule']}: "
                    f"{rule['description']} — found {len(matches)} match(es)"
                )
        except re.error:
            pass  # skip malformed patterns
    return errors


def learn_correction(
    rule_id: str,
    description: str,
    pattern: str | None = None,
    file_types: list[str] | None = None,
    severity: str = "error",
    application: str = "manual",
    caught_by: str = "user_feedback",
    corrections_path: Path | None = None,
) -> dict:
    """
    Add a new correction to the log. If rule_id already exists, updates it.

    Args:
        rule_id: Unique identifier for the rule (e.g., "no_leverage").
        description: Human-readable description of what the rule catches.
        pattern: Optional regex pattern to match against document text.
        file_types: List of file types this applies to. Defaults to all.
        severity: "error", "warning", "process", or "override".
        application: Which application triggered this correction.
        caught_by: Who or what caught the issue.
        corrections_path: Optional path to corrections_log.json.

    Returns:
        The new or updated correction entry.
    """
    path = _resolve_corrections_path(corrections_path)
    corrections = load_corrections(path)

    existing_ids = {c["id"] for c in corrections}
    if rule_id in existing_ids:
        # Update existing rule
        for c in corrections:
            if c["id"] == rule_id:
                c["description"] = description
                if pattern is not None:
                    c["pattern"] = pattern
                if file_types is not None:
                    c["file_types"] = file_types
                c["severity"] = severity
                c["date"] = datetime.date.today().isoformat()
                entry = c
                break
    else:
        entry = {
            "id": rule_id,
            "date": datetime.date.today().isoformat(),
            "application": application,
            "category": "content",
            "rule": rule_id,
            "description": description,
            "pattern": pattern,
            "file_types": file_types or ["resume", "cover_letter", "app_questions"],
            "severity": severity,
            "caught_by": caught_by,
        }
        corrections.append(entry)

    path.write_text(json.dumps(corrections, indent=2))
    return entry


def list_corrections(corrections_path: Path | None = None) -> list[dict]:
    """Return all corrections for display."""
    return load_corrections(corrections_path)
