"""
Cross-document redundancy detection using SequenceMatcher.

Compares sentences across resume, cover letter, and app questions to ensure
each document tells a unique part of the same story. Flags sentence pairs
above a similarity threshold (default 0.75).

The idea: your resume, cover letter, and application responses should
complement each other, not echo each other. A hiring manager reading all
three shouldn't see the same sentence reworded slightly across documents.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher


def _extract_sentences(text: str, min_length: int = 40) -> list[str]:
    """
    Split text into sentences, filtering very short ones and metadata lines.

    Strips markdown headers, skill inventory lines (- **Label:** ...), and
    LaTeX formatting lines (\\hfill, etc.) before splitting on sentence boundaries.
    """
    # Remove markdown headers and metadata
    text = re.sub(r"^#.*$", "", text, flags=re.MULTILINE)
    # Remove skills lines (- **Label:** content)
    text = re.sub(r"^\s*-\s+\*\*[^*]+:\*\*.*$", "", text, flags=re.MULTILINE)
    # Remove LaTeX formatting
    text = re.sub(r"^[A-Za-z ]+\\\\hfill.*$", "", text, flags=re.MULTILINE)
    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) >= min_length]


def check_cross_doc_overlap(
    files: dict[str, Path],
    threshold: float = 0.75,
) -> list[str]:
    """
    Check for sentence-level overlap between documents.

    Args:
        files: Dict mapping document labels to file paths.
            E.g., {"resume": Path(...), "cover_letter": Path(...)}
        threshold: SequenceMatcher ratio above which sentences are flagged
            as redundant. Default 0.75 (75% similar).

    Returns:
        List of warning strings describing overlapping sentences.
    """
    warnings = []
    doc_sentences: dict[str, list[str]] = {}

    for label, path in files.items():
        if path.exists():
            doc_sentences[label] = _extract_sentences(path.read_text())

    labels = list(doc_sentences.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a_label, b_label = labels[i], labels[j]
            for sa in doc_sentences[a_label]:
                for sb in doc_sentences[b_label]:
                    ratio = SequenceMatcher(None, sa.lower(), sb.lower()).ratio()
                    if ratio >= threshold:
                        preview_a = (sa[:60] + "...") if len(sa) > 60 else sa
                        preview_b = (sb[:60] + "...") if len(sb) > 60 else sb
                        warnings.append(
                            f"OVERLAP ({ratio:.0%}) {a_label} <-> {b_label}:\n"
                            f'  A: "{preview_a}"\n'
                            f'  B: "{preview_b}"'
                        )
    return warnings
