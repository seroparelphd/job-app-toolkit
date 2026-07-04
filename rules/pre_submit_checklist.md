# Pre-Submit Checklist

## Step 0: Self-Improvement Check

Before building, load and review learned corrections:
```bash
jat corrections
```
Any new rules added since the last application are auto-enforced.

## Step 1: Lint Everything

```bash
# Resume
jat lint Resume__*.md

# App questions (with cross-doc overlap check)
jat lint-aq Application_Questions*.md --resume Resume__*.md --cl Cover_Letter__*.md

# Cross-document redundancy (all docs in the directory)
jat crosscheck .
```

## Step 2: Build PDFs

```bash
# Resume (0.55in margins, black links)
pandoc Resume__*.md -o Resume_Final.pdf \
  --pdf-engine=pdflatex -V geometry:margin=0.55in -V fontsize=11pt \
  -V pagestyle=empty -V colorlinks=true -V linkcolor=black -V urlcolor=black \
  -V "header-includes=\usepackage[T1]{fontenc}\usepackage{lmodern}"

# Cover Letter (0.8in margins, black links)
pandoc Cover_Letter__*.md -o Cover_Letter_Final.pdf \
  --pdf-engine=pdflatex -V geometry:margin=0.8in -V fontsize=11pt \
  -V pagestyle=empty -V colorlinks=true -V linkcolor=black -V urlcolor=black \
  -V "header-includes=\usepackage[T1]{fontenc}\usepackage{lmodern}"
```

## Step 3: Verify

- [ ] Resume PDF: 2 pages, contact info present, no statistical claims in wrong sections, no em dashes
- [ ] Cover letter PDF: 1 page, framing correct, no em dashes, no AI writing tics
- [ ] App questions: no internal source notes, complementary to resume/CL (not redundant)
- [ ] PDF line-fill: all bullets fit 1.0 or 2.0 full lines, no orphans
- [ ] Compound modifiers hyphenated correctly
- [ ] ATS keywords present from the JD
- [ ] All documents in sync (MD matches PDF matches any review docs)

## Step 4: Submit

- [ ] Get sign-off before submitting
- [ ] Log the submission (company, role, date, portal, file links)

## Step 5: Post-Submit Retrospective

After submission, capture any corrections made during the session:
```bash
# Add a new learned rule
jat learn "<rule_id>" "<description>" --pattern "<regex>" --files resume,cover_letter

# Verify it stored
jat corrections count
```

## File Organization

```
applications/<year>-<company>-<role>/
  README.md
  Resume__<Role>__<Name>.md
  Cover_Letter__<Role>__<Name>.md
  Application_Questions_Draft.md    (if applicable)
  Resume_Final.pdf
  Cover_Letter_Final.pdf
  JD.txt
  archive/                          (old versions)
```
