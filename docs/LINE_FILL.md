# PDF Line-Fill Measurement

Deep dive on the PyMuPDF-based line-fill measurement methodology.

## The problem

Resume bullets should fill their lines cleanly. A bullet that wraps to 1.3 lines (the second line is only 30% full) looks sloppy. But predicting line-fill from character counts is unreliable because:

- Font kerning varies by character pair
- URLs break at different points depending on hyphenation rules
- Margin interactions with indented bullets are non-linear
- Bold text, italics, and special characters change width unpredictably

The standard approach -- "keep bullets under 110 characters" -- produces false positives and false negatives. The previous version of this tool used pypdf character extraction with a 109-character threshold, which generated warnings like "5 line(s) > 109 chars" with zero actionable information.

## The solution: measure the PDF directly

### Step 1: Extract text spans with bounding boxes

Using PyMuPDF (`fitz`), extract every text span from the PDF with its bounding box coordinates:

```python
page = doc[page_idx]
blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
for block in blocks:
    for line in block["lines"]:
        for span in line["spans"]:
            # span["bbox"] = (x0, y0, x1, y1) in points
            # span["text"] = the actual text
```

Each span gives us the exact rendered position and width of a piece of text.

### Step 2: Group lines into paragraphs

Visually contiguous lines (close vertically, maintaining or increasing left indent) are grouped into paragraphs. A leftward jump in x-position or a large vertical gap signals a new paragraph.

The key insight: wrapped bullet continuations indent further right than the bullet marker. So a line at x0=53pt followed by a line at x0=58pt is the same bullet, but a line at x0=53pt followed by x0=39pt is a new section header.

### Step 3: Estimate column width

The text column width is estimated as the 90th percentile of all line widths on each page. This filters out headings, short lines, and other outliers while capturing the actual available text width.

### Step 4: Compute fill ratio

For each multi-line paragraph:
```
fill = last_line_width / column_width
```

### Step 5: Flag orphans

| Fill | Verdict |
|------|---------|
| >= 90% | Clean -- line is full |
| 60-89% | Below target but acceptable |
| < 60% | ORPHAN -- needs editing |

## Filtering false positives

Not everything that wraps should be measured:

- **Job headers** (low left indent, x0 < 48pt) -- these wrap differently and aren't bullets
- **Technical Skills lines** ("Programming:", "ML Evaluation:") -- keyword inventories that wrap naturally
- **Publication entries** (contain PMID, DOI) -- citations with naturally short last lines
- **Education entries** -- degree/institution/year lines
- **Short paragraphs** (< 60 chars joined) -- not enough text to worry about

Previous versions flagged 6+ false positives per run from these categories.

## Editing based on measurements

The tool reports exact fill percentages, which makes editing targeted:

- **fill < 60%:** trim the bullet. Remove low-value modifiers (very, successfully, various), parentheticals, or redundant qualifiers.
- **fill 60-89%:** consider growing. Add meaning-preserving qualifiers, but don't repeat the same one across bullets.
- **Oscillation trap:** if you've been going back and forth between 0.7 and 1.3 lines, accept 2.0 lines at 70% fill. The 17-version churn was caused by perfectionism on single-line targets, not by measurement inaccuracy.

## Dependencies

- **Required:** PyMuPDF (`pip install PyMuPDF`)
- **Fallback:** pypdf (`pip install pypdf`) -- character-count heuristic, much less accurate
