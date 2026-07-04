"""
CLI entry point for job-app-toolkit.

Usage:
    jat lint <resume.md>             Lint a resume markdown file
    jat lint-aq <questions.md>       Lint app questions (with cross-doc overlap)
    jat crosscheck <app_dir>         Cross-document redundancy check
    jat build <app_dir>              Full build: lint + PDF + line-fill
    jat learn <id> <desc>            Learn a new correction rule
    jat corrections                  List all learned corrections
    jat line-fill <file.pdf>         Measure PDF line-fill only
"""

import sys
import json
import glob
from pathlib import Path


def _find_corrections_path() -> Path | None:
    """Look for corrections_log.json in common locations."""
    candidates = [
        Path("config/corrections_log.json"),
        Path("corrections_log.json"),
        Path(__file__).parent.parent / "config" / "corrections_log.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def cmd_lint(args: list[str]) -> int:
    """Lint a resume markdown file."""
    from .lint import lint_resume_md

    if not args:
        print("Usage: jat lint <resume.md>")
        return 1

    md_path = Path(args[0])
    if not md_path.exists():
        print(f"File not found: {md_path}")
        return 1

    errors = lint_resume_md(md_path, corrections_path=_find_corrections_path())
    if errors:
        print("LINT FAIL:")
        for e in errors:
            print(f"  x {e}")
        return 1
    print("OK Lint clean")
    return 0


def cmd_lint_aq(args: list[str]) -> int:
    """Lint application questions with optional cross-doc overlap check."""
    from .lint_aq import lint_app_questions

    if not args:
        print("Usage: jat lint-aq <questions.md> [--resume r.md] [--cl cl.md]")
        return 1

    aq_path = Path(args[0])
    resume_path = cl_path = None

    rest = args[1:]
    for i, arg in enumerate(rest):
        if arg == "--resume" and i + 1 < len(rest):
            resume_path = Path(rest[i + 1])
        if arg == "--cl" and i + 1 < len(rest):
            cl_path = Path(rest[i + 1])

    errors = lint_app_questions(
        aq_path, resume_path, cl_path,
        corrections_path=_find_corrections_path(),
    )
    if errors:
        print("APP QUESTIONS LINT FAIL:")
        for e in errors:
            print(f"  x {e}")
        return 1
    print("OK App questions lint clean")
    return 0


def cmd_crosscheck(args: list[str]) -> int:
    """Cross-document redundancy check."""
    from .crosscheck import check_cross_doc_overlap

    if not args:
        print("Usage: jat crosscheck <app_dir>")
        return 1

    app_dir = Path(args[0])
    files = {}
    for pattern, label in [
        ("Resume__*.md", "resume"),
        ("Cover_Letter__*.md", "cover_letter"),
        ("Application_Questions*.md", "app_questions"),
    ]:
        matches = glob.glob(str(app_dir / pattern))
        if matches:
            files[label] = Path(sorted(matches)[-1])

    if len(files) < 2:
        print(f"Need at least 2 documents, found {len(files)}: {list(files.keys())}")
        return 1

    overlaps = check_cross_doc_overlap(files)
    if overlaps:
        print(f"CROSS-DOC OVERLAP: {len(overlaps)} redundant sentence(s)")
        for o in overlaps:
            print(f"  x {o}")
        return 1
    print(f"OK Cross-doc check clean ({len(files)} documents compared)")
    return 0


def cmd_build(args: list[str]) -> int:
    """Full build: lint + PDF + line-fill."""
    from .build import build_application

    if not args:
        print("Usage: jat build <app_dir>")
        return 1

    report = build_application(
        Path(args[0]),
        corrections_path=_find_corrections_path(),
    )
    print(json.dumps(report, indent=2))
    return 1 if report.get("lint_errors") else 0


def cmd_learn(args: list[str]) -> int:
    """Learn a new correction rule."""
    from .learn import learn_correction, load_corrections

    if len(args) < 2:
        print(
            "Usage: jat learn <rule_id> <description> "
            "[--pattern <regex>] [--files type1,type2] [--severity error|warning]"
        )
        return 1

    rule_id = args[0]
    description = args[1]
    pattern = None
    file_types = None
    severity = "error"

    rest = args[2:]
    for i, arg in enumerate(rest):
        if arg == "--pattern" and i + 1 < len(rest):
            pattern = rest[i + 1]
        if arg == "--files" and i + 1 < len(rest):
            file_types = rest[i + 1].split(",")
        if arg == "--severity" and i + 1 < len(rest):
            severity = rest[i + 1]

    corrections_path = _find_corrections_path()
    entry = learn_correction(
        rule_id, description, pattern, file_types, severity,
        corrections_path=corrections_path,
    )
    total = len(load_corrections(corrections_path))
    print(f"OK Learned rule '{rule_id}': {description}")
    print(f"  Total corrections: {total}")
    return 0


def cmd_corrections(args: list[str]) -> int:
    """List all learned corrections."""
    from .learn import load_corrections

    corrections = load_corrections(_find_corrections_path())
    subcmd = args[0] if args else "list"

    if subcmd == "count":
        print(f"{len(corrections)} corrections logged")
    else:
        for c in corrections:
            status = (
                "OVERRIDE"
                if c.get("severity") == "override"
                else c.get("severity", "error").upper()
            )
            desc = c.get("description", "")[:80]
            print(f"  [{status}] {c['id']}: {c.get('rule', '')} — {desc}")
        print(f"\nTotal: {len(corrections)}")
    return 0


def cmd_line_fill(args: list[str]) -> int:
    """Measure PDF line-fill only."""
    from .line_fill import check_pdf_line_fill

    if not args:
        print("Usage: jat line-fill <file.pdf>")
        return 1

    pdf_path = Path(args[0])
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return 1

    warnings = check_pdf_line_fill(pdf_path)
    if warnings:
        for w in warnings:
            print(f"  ! {w}")
        return 1
    print("OK Line-fill clean")
    return 0


COMMANDS = {
    "lint": cmd_lint,
    "lint-aq": cmd_lint_aq,
    "crosscheck": cmd_crosscheck,
    "build": cmd_build,
    "learn": cmd_learn,
    "corrections": cmd_corrections,
    "line-fill": cmd_line_fill,
}


def main():
    """CLI entry point."""
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: jat <command> [args...]")
        print(f"Commands: {', '.join(COMMANDS.keys())}")
        sys.exit(0 if sys.argv[-1] in ("-h", "--help") else 1)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Commands: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    sys.exit(COMMANDS[cmd](sys.argv[2:]))


if __name__ == "__main__":
    main()
