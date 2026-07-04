# Resume Writing Rules

## Bullet structure
- Action + Result, measurable where possible
- No period at end of experience bullets
- Summary sentences end with periods
- Acronyms spelled out on first use
- Model names lowercase: "logistic regression", "random forest"

## Line-fill

The biggest time sink in resume formatting. A bullet that wraps to 1.3 lines looks sloppy, and guessing character counts doesn't work because font kerning, URL breaking, and margin interactions are non-linear.

**Target:** 0.9-1.0 / 1.9-2.0 lines, >=90% fill
**Acceptable:** 1 full line (>=95%) OR 2 full lines with last line >=60-75%
**FORBIDDEN:** 1.3, 1.5, 1.7, 2.3 line orphans

### Measurement

Use `jat line-fill resume.pdf` to measure actual rendered glyph widths via PyMuPDF. Do not eyeball or count characters.

The tool reads actual bounding boxes, groups wrapped lines into paragraphs, computes `fill = last_line_width / column_width`, and flags orphans with exact percentages.

### Editing for fill

- **Too short (fill < 0.90):** append meaning-preserving qualifiers, but de-duplicate across bullets (don't repeat the same qualifier 3x in the same role block)
- **Orphan wrap (fill < 0.60 or 1.3-1.7 lines):** trim low-value modifiers first (very, successfully, various, parentheticals)
- **Technical Skills:** same fill targets apply. Watch for redundant terms (bash, shell scripting, Unix = 3x the same skill)
- **Stop oscillation early:** accept 2.0 lines at 70% fill vs chasing perfect 1.0. The 17-version churn problem was caused by ignoring this rule.
- **Measure in PDF, not MD:** font kerning, URL breaking, and margin interactions make character-count prediction unreliable

### GDocs vs PDF line-fill

If your reviewer reads in Google Docs, not the PDF, tune for both:
- ~95 chars = 1 line in GDocs (11pt, default margins)
- ~195-200 chars = 2 lines in GDocs
- A bullet that looks clean in the PDF may orphan in GDocs

## Content rules

- No inflated metrics or inflated years of experience
- Maintain a statistical analysis boundary: restrict certain statistical claims to sections where the candidate actually did that work
- No internal codenames or proprietary tool names
- Check for Project vs Experience section redundancy
- Publications: italicize journal name, include DOI
- Technical Skills: categorized bullet points, NOT a comma-run paragraph. Check against your allowed/banned skills lists in `config/banned_skills.yaml`

## Page structure

- 2 pages for resume, 1 page for cover letter
- <=2-3 blank lines at end — not 1.3 pages of content on a 2-page resume
- 11pt, consistent bullet style

## AI writing tells

- No em dashes, ever. `grep -n '\u2014\|\u2013' file.md` before every build.
- No tricolons / lists of three. Rewrite to max 2 items or restructure as a clause.
- Full banned-tropes list: `rules/ai_writing_tropes.md`
- Pre-send scan required before finalizing any document.
