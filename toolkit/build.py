"""
End-to-end application build: lint, PDF generation, line-fill check.

Orchestrates the full pipeline:
1. Lint the resume and cover letter markdown files
2. Build PDFs via pandoc + pdflatex
3. Run line-fill measurement on generated PDFs
4. Optionally run ATS keyword check

Requires pandoc and pdflatex installed on the system.
"""

import subprocess
import glob
from pathlib import Path

from .lint import lint_resume_md
from .learn import lint_from_corrections
from .line_fill import check_pdf_line_fill


def build_application(
    app_dir: Path,
    resume_glob: str = "Resume__*.md",
    cl_glob: str = "Cover_Letter__*.md",
    resume_margin: str = "0.55in",
    cl_margin: str = "0.8in",
    font_size: str = "11pt",
    corrections_path: Path | None = None,
    **lint_kwargs,
) -> dict:
    """
    Build resume + CL PDFs with full lint and line-fill checks.

    Args:
        app_dir: Path to the application directory containing MD files.
        resume_glob: Glob pattern for resume markdown files.
        cl_glob: Glob pattern for cover letter markdown files.
        resume_margin: Page margin for resume PDF.
        cl_margin: Page margin for cover letter PDF.
        font_size: Font size for PDFs.
        corrections_path: Path to corrections_log.json.
        **lint_kwargs: Additional arguments passed to lint_resume_md().

    Returns:
        Dict with keys: resume_pdf, cl_pdf, lint_errors, pdf_warnings, ats.
        If lint fails, returns lint_errors and build_skipped=True.
    """
    resume_files = glob.glob(str(app_dir / resume_glob))
    cl_files = glob.glob(str(app_dir / cl_glob))

    if not resume_files or not cl_files:
        return {"error": f"Missing MD files in {app_dir}"}

    resume_md_path = Path(resume_files[0])
    cl_md_path = Path(cl_files[0])

    # 1. Lint resume
    lint_errors = lint_resume_md(
        resume_md_path,
        corrections_path=corrections_path,
        **lint_kwargs,
    )

    # 2. Lint cover letter (basic checks)
    cl_text = cl_md_path.read_text()
    if "\u2014" in cl_text:
        lint_errors.append("CL: EM DASH found")
    excited_count = cl_text.lower().count("excited")
    if excited_count > 1:
        lint_errors.append(f"CL: 'excited' appears {excited_count}x — target <=1")
    lint_errors.extend(lint_from_corrections(cl_text, "cover_letter", corrections_path))

    if lint_errors:
        return {"lint_errors": lint_errors, "build_skipped": True}

    # 3. Build PDFs
    resume_pdf = app_dir / resume_md_path.with_suffix(".pdf").name
    cl_pdf = app_dir / cl_md_path.with_suffix(".pdf").name

    for md_path, pdf_path, margin in [
        (resume_md_path, resume_pdf, resume_margin),
        (cl_md_path, cl_pdf, cl_margin),
    ]:
        cmd = [
            "pandoc", str(md_path), "-o", str(pdf_path),
            "--pdf-engine=pdflatex",
            "-V", f"geometry:margin={margin}",
            "-V", f"fontsize={font_size}",
            "-V", "colorlinks=true",
            "-V", "linkcolor=black",
            "-V", "urlcolor=black",
            "-V", "pagestyle=empty",
            "-V", r"header-includes=\usepackage[T1]{fontenc}\usepackage{lmodern}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(app_dir))
        if result.returncode != 0:
            lint_errors.append(f"pandoc failed for {md_path.name}: {result.stderr[:200]}")
            return {"lint_errors": lint_errors, "build_skipped": True}

    # 4. PDF line-fill warnings
    pdf_warnings = check_pdf_line_fill(resume_pdf) + check_pdf_line_fill(cl_pdf)

    return {
        "resume_pdf": str(resume_pdf),
        "cl_pdf": str(cl_pdf),
        "lint_errors": [],
        "pdf_warnings": pdf_warnings,
        "ats": {},  # caller supplies required_keywords via ats.check_ats_keywords()
    }
