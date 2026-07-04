"""
PDF line-fill measurement using PyMuPDF (fitz).

Measures actual rendered glyph widths in the PDF to detect orphan lines --
bullets that wrap to a second (or third) line but leave the last line mostly
empty. This is the biggest time sink in resume formatting: a bullet that
wraps to 1.3 lines looks sloppy, and guessing character counts doesn't work
because font kerning, URL breaking, and margin interactions are non-linear.

The solution: measure the PDF directly.

Method:
1. Extract all text spans with bounding boxes via PyMuPDF
2. Group visually contiguous lines into paragraphs (bullets)
3. Estimate the text column width from the 90th percentile line width
4. For each multi-line paragraph, compute fill = last_line_width / column_width
5. Flag orphans where fill < floor (default 60%)

Bullet detection filters out job headers, skills sections, education entries,
and publications (which naturally have short last lines) to avoid false positives.
"""

import re
from pathlib import Path
from collections import defaultdict


def _measure_pdf_lines_fitz(pdf_path: Path) -> tuple[list[dict], int, int]:
    """
    Measure actual rendered text line widths using PyMuPDF.

    Returns:
        Tuple of (lines, page_count, total_chars) where lines is a list of
        dicts with keys: page, y0, text, x0, x1, width.
    """
    import fitz  # PyMuPDF

    doc = fitz.open(str(pdf_path))
    all_lines = []
    total_chars = 0
    page_count = len(doc)

    for page_idx in range(page_count):
        page = doc[page_idx]
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
        for b in blocks:
            if b.get("type") != 0:  # 0 = text block
                continue
            for line in b.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).strip()
                if not text:
                    continue
                x0 = min(s["bbox"][0] for s in spans)
                x1 = max(s["bbox"][2] for s in spans)
                y0 = line["bbox"][1]
                all_lines.append({
                    "page": page_idx + 1,
                    "y0": y0,
                    "text": text,
                    "x0": x0,
                    "x1": x1,
                    "width": x1 - x0,
                })
                total_chars += len(text)

    doc.close()
    return all_lines, page_count, total_chars


def _group_wrapped_lines(lines: list[dict]) -> list[list[dict]]:
    """
    Group visually contiguous lines into paragraphs/bullets.

    Lines on the same page that are close vertically and maintain or increase
    their left indent are grouped together. A leftward jump in x0 or a large
    vertical gap signals a new paragraph.

    Returns:
        List of paragraphs, each a list of line dicts in reading order.
    """
    if not lines:
        return []

    lines = sorted(lines, key=lambda ln: (ln["page"], ln["y0"], ln["x0"]))
    paras = []
    cur = [lines[0]]

    for ln in lines[1:]:
        prev = cur[-1]
        # New page = new paragraph
        if ln["page"] != prev["page"]:
            paras.append(cur)
            cur = [ln]
            continue
        dy = ln["y0"] - prev["y0"]
        # Same paragraph if: close vertically AND not a leftward jump
        # (wrapped bullet continuations indent further right)
        if dy < 16 and ln["x0"] >= prev["x0"] - 5:
            cur.append(ln)
        else:
            paras.append(cur)
            cur = [ln]

    if cur:
        paras.append(cur)
    return paras


def check_pdf_line_fill(
    pdf_path: Path,
    target_fill: float = 0.90,
    floor_fill: float = 0.60,
    expected_pages: int | None = None,
    min_chars: int = 3000,
) -> list[str]:
    """
    Measure actual rendered line-fill in a resume/CL PDF using PyMuPDF.

    For each wrapped paragraph (typically a bullet), measures the last line's
    width as a fraction of the full text column width.

    Targets:
        - 0.9-1.0 / 1.9-2.0 lines, >=90% fill
        - Acceptable: 1 full line (>=95%) or 2 full lines with last >=60-75%
        - FORBIDDEN: 1.3, 1.5, 1.7, 2.3 line orphans

    Args:
        pdf_path: Path to the PDF file.
        target_fill: Target minimum fill ratio (default 0.90).
        floor_fill: Absolute minimum fill ratio before flagging orphan (default 0.60).
        expected_pages: Expected page count (e.g., 2 for resume, 1 for CL).
        min_chars: Minimum extracted characters for ATS parseability (default 3000).

    Returns:
        List of warning strings (empty = clean).
    """
    try:
        lines, page_count, total_chars = _measure_pdf_lines_fitz(pdf_path)
    except ImportError:
        return ["PyMuPDF not installed — run: pip install PyMuPDF"]
    except Exception as e:
        # Attempt pypdf fallback for basic checks
        try:
            from pypdf import PdfReader

            r = PdfReader(str(pdf_path))
            text = "\n".join((p.extract_text() or "") for p in r.pages)
            page_count = len(r.pages)
            total_chars = len(text)
            warnings = []
            long_lines = [ln for ln in text.split("\n") if len(ln) > 109]
            if long_lines:
                warnings.append(
                    f"{len(long_lines)} line(s) > 109 chars "
                    f"(pypdf fallback — install PyMuPDF for accurate measurement)"
                )
            return warnings
        except Exception as e2:
            return [f"Could not read PDF: {e} / fallback: {e2}"]

    warnings = []

    # Page count check
    if expected_pages is not None and page_count != expected_pages:
        warnings.append(f"PDF has {page_count} pages — expected {expected_pages}")
    else:
        # Infer from filename
        name_lower = pdf_path.name.lower()
        if "resume" in name_lower and page_count != 2:
            warnings.append(f"Resume PDF has {page_count} pages — expected 2")
        if "cover" in name_lower and "letter" in name_lower and page_count != 1:
            warnings.append(f"Cover letter PDF has {page_count} pages — expected 1")

    # ATS parseability
    if total_chars < min_chars:
        warnings.append(
            f"Only {total_chars} chars extracted — ATS parseability risk (expected {min_chars}+)"
        )

    # Group into paragraphs
    paras = _group_wrapped_lines(lines)

    # Estimate text column width per page (90th percentile line width)
    page_widths: dict[int, list[float]] = defaultdict(list)
    for ln in lines:
        page_widths[ln["page"]].append(ln["width"])
    col_width: dict[int, float] = {}
    for pg, widths in page_widths.items():
        widths.sort()
        idx = max(0, int(len(widths) * 0.90) - 1)
        col_width[pg] = widths[idx] if widths else 500

    # Check each multi-line paragraph
    orphan_count = 0
    short_count = 0

    for para in paras:
        if len(para) < 2:
            continue

        # Bullet detection: first line starts with bullet marker
        first_text = para[0]["text"].lstrip()
        is_bullet = first_text.startswith(("•", "-", "–"))
        x0_first = para[0]["x0"]

        # Skip non-bullet paragraphs at low indent (headers, education entries)
        if not is_bullet and x0_first < 48:
            continue

        text = " ".join(ln["text"] for ln in para)
        if len(text) < 60:
            continue

        # Skip Technical Skills lines
        if re.match(
            r"^\s*[•\-]\s*(Programming|ML Evaluation|Research|"
            r"Software Engineering|Tools|Languages|Frameworks)\s*:",
            text,
        ):
            continue

        # Skip publication entries (contain PMID, doi, year patterns)
        if "PMID" in text or "doi.org" in text:
            continue

        last = para[-1]
        pg = last["page"]
        fill = last["width"] / col_width.get(pg, 500)
        n_lines = len(para)

        if fill < floor_fill:
            orphan_count += 1
            preview = (text[:55] + "...") if len(text) > 55 else text
            preview = re.sub(r"^[•\-–]\s*", "", preview)
            warnings.append(
                f"ORPHAN p{pg} L{n_lines} fill={fill:.0%} — \"{preview}\" — "
                f"target >={target_fill:.0%}, floor >={floor_fill:.0%}"
            )
        elif fill < target_fill:
            short_count += 1

    if short_count and not orphan_count:
        warnings.append(
            f"{short_count} paragraph(s) with last-line fill "
            f"{floor_fill:.0%}-{target_fill:.0%} (below target, above floor) — "
            f"acceptable but not ideal"
        )

    # Check for em dashes in extracted text
    full_text = " ".join(ln["text"] for ln in lines)
    if "\u2014" in full_text:
        warnings.append("EM DASH found in PDF text — check source MD and rebuild")
    if "\\hfill" in full_text:
        warnings.append("\\hfill literal in PDF text — pandoc build failed, check MD source")

    return warnings
