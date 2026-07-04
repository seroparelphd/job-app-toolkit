# Application Workflow

The full pipeline from job description to submitted application. Seven steps, in order.

## 1. Vet the role

Before writing anything, check whether the role is worth applying to.

**Hard filters (binary pass/fail):**
- Salary: does the comp range max reach your floor?
- Location: acceptable city or remote policy?
- Cooldowns: have you applied to this company recently?
- Already applied: check your application log
- Exclusions: is this company on your blocklist?

**Soft assessment:**
- Coding bar: how much day-to-day coding does the JD describe?
- Publication requirements: do they require venue-specific papers you don't have?
- Seniority: does the YOE requirement match your experience?
- Domain: is the core work aligned with your actual expertise?

If the role fails vetting, note why and move on. Don't draft materials for roles that don't pass.

## 2. Read ground truth

Before writing a single bullet, open:
- `config/ground_truth.md` -- your verified facts about your experience
- The target JD -- extract required skills, preferred skills, degree, location, req number

**Project representation rule:** if you list a project, open the source repo and verify every claim (architecture, performance numbers, tech stack). Don't list libraries that aren't in requirements.txt.

## 3. Draft resume

- Tailor bullets to JD keywords (see `rules/resume_rules.md`)
- Start from ground truth, NOT from a prior resume variant
- Run the linter before building: `jat lint Resume__*.md`

## 4. Draft cover letter

- See `rules/cover_letter_rules.md` for the full checklist
- Research stats framing: question then 2 methods with context then map to role
- No AI writing tells (see `rules/ai_writing_tropes.md`)

## 5. Build PDFs

```bash
jat build /path/to/app_dir
```

This runs: lint, pandoc PDF build (resume + CL), and PDF line-fill check.

- Toolchain: pandoc + pdflatex only
- Resume: 2 pages, 0.55in margins, 11pt
- Cover letter: 1 page, 0.8in margins, 11pt
- Both: T1 fontenc, lmodern, black link colors, no page numbers

## 6. Review and sync

After building PDFs:
1. Check line-fill: `jat line-fill Resume.pdf`
2. Check cross-doc redundancy: `jat crosscheck /path/to/app_dir`
3. If using Google Docs for review: sync MD text into GDocs (see `workflow/gdoc_sync.md`)
4. Upload final PDFs to your file storage

**Sync order (always):** MD -> PDF -> review doc -> cloud storage

## 7. Submit and track

- Get sign-off before submitting (never auto-submit)
- Log the submission: company, role, date, portal, file links
- Set a follow-up reminder for 10-14 business days

## Operating rules

1. **Ground truth first.** Verify against source repos before writing any bullet.
2. **Run the linter before every PDF build.** It catches recurring failures automatically.
3. **No AI writing tells.** See `rules/ai_writing_tropes.md`. Pre-send scan required.
4. **Statistical analysis boundary.** Keep statistical claims in the sections where you actually did that work.
5. **Project representation.** Open the source repo. Don't merge projects. Don't list libraries you didn't use.
6. **PDF toolchain: pandoc + pdflatex only.** With T1 fontenc for ATS text extraction compatibility.
7. **Line-fill: measure in the PDF, not the markdown.** Font kerning is non-linear.
8. **One directory per application.** Never copy bullets from one variant to another.
9. **Get approval before submitting.** Every time.
