"""
Application question linter with cross-document overlap detection.

Checks app question responses for:
- Internal source notes / comments that shouldn't be submitted
- Banned words
- Unhyphenated compound modifiers
- Learned corrections from corrections_log.json
- Sentence-level overlap with resume and cover letter (via crosscheck module)
"""

import re
from pathlib import Path

from .learn import lint_from_corrections
from .crosscheck import check_cross_doc_overlap


# Compound modifiers that should be hyphenated when used before a noun
DEFAULT_COMPOUNDS = [
    "multi turn", "post training", "cross domain", "subject matter",
    "cross functional", "large scale", "real world", "end to end",
]


def lint_app_questions(
    aq_path: Path,
    resume_path: Path | None = None,
    cl_path: Path | None = None,
    banned_words: list[str] | None = None,
    compound_modifiers: list[str] | None = None,
    corrections_path: Path | None = None,
) -> list[str]:
    """
    Lint application question responses.

    Args:
        aq_path: Path to the app questions markdown file.
        resume_path: Optional resume path for cross-doc overlap check.
        cl_path: Optional cover letter path for cross-doc overlap check.
        banned_words: Words to flag. Defaults to ["vibe"].
        compound_modifiers: Unhyphenated compounds to flag.
        corrections_path: Path to corrections_log.json.

    Returns:
        List of error strings (empty = clean).
    """
    text = aq_path.read_text()
    errors = []

    if banned_words is None:
        banned_words = ["vibe"]
    if compound_modifiers is None:
        compound_modifiers = DEFAULT_COMPOUNDS

    # 1. Source notes / internal comments
    if re.search(r"(?i)^---\s*$", text, re.MULTILINE):
        parts = text.split("---")
        if len(parts) > 1 and re.search(
            r"(?i)(source|note|ground.truth|career.advisor|internal)", parts[-1]
        ):
            errors.append(
                "INTERNAL SOURCE NOTE found after --- separator — remove before submission"
            )

    # 2. Banned words
    for word in banned_words:
        if re.search(rf"(?i)\b{re.escape(word)}\b", text):
            errors.append(f"BANNED WORD '{word}' found in app questions")

    # 3. Unhyphenated compound modifiers
    for compound in compound_modifiers:
        if compound.lower() in text.lower():
            hyphenated = compound.replace(" ", "-")
            errors.append(f"UNHYPHENATED COMPOUND: '{compound}' should be '{hyphenated}'")

    # 4. Run learned corrections
    errors.extend(lint_from_corrections(text, "app_questions", corrections_path))

    # 5. Cross-document overlap
    if resume_path or cl_path:
        files = {"app_questions": aq_path}
        if resume_path and resume_path.exists():
            files["resume"] = resume_path
        if cl_path and cl_path.exists():
            files["cover_letter"] = cl_path
        overlaps = check_cross_doc_overlap(files)
        if overlaps:
            errors.append(
                f"CROSS-DOC OVERLAP: {len(overlaps)} sentence(s) redundant with resume/CL"
            )
            for o in overlaps[:3]:  # show max 3
                errors.append(f"  {o}")

    return errors
