# job-app-toolkit

A self-improving resume and cover letter pipeline. Built after a 17-version resume cycle that shouldn't have happened.

## What it does

Lints your resume and cover letter markdown, builds PDFs via pandoc, measures actual line-fill in the rendered PDF using PyMuPDF, detects cross-document redundancy between your resume/CL/application responses, and learns from every correction you make so the same mistake never happens twice.

## The problem it solves

1. **The churn.** You shorten a bullet to fix line-fill, introduce a banned skill, fix the skill, break the line-fill again. 17 versions later, you've lost track of what's verified and what was improvised.

2. **The AI tells.** If you use an LLM to help draft, the output contains identifiable patterns: em dashes, tricolons, "foster", "holistic", "It's not X, it's Y." Hiring managers increasingly recognize these.

3. **The guessing.** Character-counting to predict line wrapping doesn't work. Font kerning, URL breaking, and margins are non-linear. You need to measure the actual PDF.

## Key features

- **Self-improvement loop:** every correction becomes a permanent lint rule via `corrections_log.json`. You fix a mistake once, the linter catches it forever. ([docs/SELF_IMPROVEMENT.md](docs/SELF_IMPROVEMENT.md))

- **AI trope detection:** comprehensive, curated ban list of AI writing patterns, from structural tells (tricolons, rhetorical questions) to diction ("delve", "tapestry", "foster"). ([rules/ai_writing_tropes.md](rules/ai_writing_tropes.md))

- **PyMuPDF line-fill measurement:** reads actual rendered glyph bounding boxes, groups wrapped lines into paragraphs, reports exact fill percentages. No more guessing. ([docs/LINE_FILL.md](docs/LINE_FILL.md))

- **Cross-document redundancy:** SequenceMatcher at 0.75 threshold flags sentence-level overlap between resume, cover letter, and application questions. Your three documents should complement each other, not echo.

- **Ground truth pattern:** one canonical file of verified facts. Every resume variant starts from ground truth, never from another variant. Factual corrections propagate forward.

## Quick start

```bash
# Install
pip install .

# Or with ATS keyword checking (requires pypdf)
pip install ".[ats]"

# Lint a resume
jat lint Resume__My_Role.md

# Lint app questions with cross-doc overlap check
jat lint-aq Application_Questions.md --resume Resume__My_Role.md --cl Cover_Letter__My_Role.md

# Check cross-document redundancy
jat crosscheck /path/to/app_dir/

# Full build (lint + PDF + line-fill)
jat build /path/to/app_dir/

# Measure line-fill on an existing PDF
jat line-fill Resume.pdf

# Learn a new correction
jat learn no_leverage "Don't use 'leverage'" --pattern "(?i)\bleverag" --files resume,cover_letter

# List all corrections
jat corrections
```

## Setup

1. Copy `config/profile.example.yaml` to `config/profile.yaml` and fill in your info
2. Copy `config/ground_truth.example.md` to `config/ground_truth.md` and populate with verified facts
3. Copy `config/banned_skills.example.yaml` to `config/banned_skills.yaml` and customize
4. Start applying. Run `jat learn` after every correction. Watch the linter get smarter.

## Architecture

```
toolkit/           Python modules (lint, line-fill, crosscheck, learn, build, CLI)
config/            User-specific config (gitignored) + example templates (tracked)
rules/             Writing rules: AI tropes, resume structure, CL structure, checklist
workflow/          Methodology docs: 7-step workflow, discovery, evaluation, variants
templates/         Markdown skeletons for resume, CL, per-app README, retrospective
examples/          Anonymized sample application showing the full workflow output
docs/              Deep dives: philosophy, self-improvement loop, line-fill methodology
```

## Dependencies

- **Python 3.10+**
- **PyMuPDF** (`pip install PyMuPDF`) -- PDF line-fill measurement
- **pandoc + pdflatex** -- PDF generation (system packages)
- **pypdf** (optional) -- ATS keyword checking

## Philosophy

See [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) for the full story. The short version: ground truth as single source, self-improvement as the core innovation, measurement over estimation.

## License

MIT
