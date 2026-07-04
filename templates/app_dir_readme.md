# [Company] -- [Role Title]

## Role Details

- **Company:** [Company Name]
- **Position:** [Full Title]
- **Req ID:** [If available]
- **Location:** [City / Remote]
- **Compensation:** [Range]
- **Portal:** [Application URL]

## Fit Assessment

**Tier:** [1/2/3] | **Score:** [X/100]

**Strengths:**
- [What aligns well]

**Gaps:**
- [What doesn't match, and whether it's a hard or soft gap]

**Coding bar:** [LOW / MEDIUM / HIGH]

## Files

| Document | File |
|----------|------|
| Resume MD | `Resume__[Role]__[Name].md` |
| Cover Letter MD | `Cover_Letter__[Role]__[Name].md` |
| Resume PDF | `[Name]_Resume_[Company]_[Role].pdf` |
| Cover Letter PDF | `[Name]_Cover_Letter_[Company]_[Role].pdf` |
| JD | `JD.txt` |

## Build Commands

```bash
# Resume
pandoc "Resume__[Role]__[Name].md" \
  -o "[Name]_Resume_[Company]_[Role].pdf" \
  --pdf-engine=pdflatex \
  -V geometry:margin=0.55in -V fontsize=11pt -V pagestyle=empty \
  -V colorlinks=true -V linkcolor=black -V urlcolor=black \
  -V "header-includes=\usepackage[T1]{fontenc}\usepackage{lmodern}"

# Cover Letter
pandoc "Cover_Letter__[Role]__[Name].md" \
  -o "[Name]_Cover_Letter_[Company]_[Role].pdf" \
  --pdf-engine=pdflatex \
  -V geometry:margin=0.8in -V fontsize=11pt -V pagestyle=empty \
  -V colorlinks=true -V linkcolor=black -V urlcolor=black \
  -V "header-includes=\usepackage[T1]{fontenc}\usepackage{lmodern}"
```

## Review Links

- Resume GDoc: [URL]
- CL GDoc: [URL]
- Drive folder: [URL]

## Timeline

- **Applied:** [Date]
- **Follow-up due:** [Date, 10-14 business days]

## Notes

[Any tailoring decisions, keyword emphasis, framing choices.]
