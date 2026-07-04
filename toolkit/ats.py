"""
ATS (Applicant Tracking System) keyword checker.

Extracts text from a PDF and counts keyword occurrences against expected
frequencies derived from the job description. Useful for ensuring your
resume hits the right keywords without over-stuffing.

Requires pypdf: pip install pypdf
"""

from pathlib import Path


def check_ats_keywords(
    pdf_path: Path,
    required_keywords: dict[str, int | tuple[int, int]],
) -> dict[str, dict]:
    """
    Check keyword counts in PDF against JD requirements.

    Args:
        pdf_path: Path to the PDF to check.
        required_keywords: Dict mapping keywords to expected counts.
            Values can be:
            - int: minimum count (no maximum)
            - tuple (min, max): expected count range

    Returns:
        Dict mapping each keyword to {"found": int, "expected": str, "pass": bool}.

    Raises:
        ImportError: If pypdf is not installed.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(
            "pypdf is required for ATS keyword checking. "
            "Install with: pip install pypdf"
        )

    reader = PdfReader(str(pdf_path))
    text = " ".join((p.extract_text() or "") for p in reader.pages).lower()

    results = {}
    for kw, spec in required_keywords.items():
        if isinstance(spec, tuple):
            min_c, max_c = spec
        else:
            min_c, max_c = spec, 999
        found = text.count(kw.lower())
        passed = min_c <= found <= max_c
        results[kw] = {
            "found": found,
            "expected": f"{min_c}-{max_c}" if max_c < 999 else f">={min_c}",
            "pass": passed,
        }
    return results
