# Philosophy

## The problem

You're applying to jobs. You write a resume, build a PDF, notice a bullet wraps to 1.3 lines. You shorten it. Now it's 0.8 lines. You add a word. Now it wraps to 1.4 lines. You try a different word. Now the linter catches an em dash you didn't realize was there. You fix it. Now the line-fill changed again.

This is version 7. By version 14, you've introduced a statistical claim that doesn't belong in that section. By version 17, you've lost track of which bullet came from your actual experience and which was improvised to hit a line-fill target.

This toolkit exists because of a real 17-version resume cycle. Not because the resume was bad, but because the process had no guardrails.

## Core ideas

### Ground truth as single source

Every resume bullet must be traceable to a verified claim in one canonical file. When you tailor a resume for a new role, you start from ground truth, not from a previous variant. When you fix a factual error, you fix it in ground truth and rebuild forward. You never copy bullets between variants.

This is the boring idea that prevents the expensive mistake.

### Self-improvement as the core innovation

Every correction you make during an application cycle becomes a permanent, machine-enforced lint rule for the next one. You misspell a compound modifier, fix it manually, then run `jat learn` with a regex pattern. Next application, the linter catches it automatically.

The corrections log is structured JSON, not prose. Each entry has: an ID, a date, which application surfaced it, a regex pattern, which file types it applies to, and who caught it (you, a reviewer, an ATS check). Over time, the linter gets smarter because you got smarter.

This is the opposite of the standard approach, which is to write a style guide and hope you remember it. The toolkit remembers for you.

### Measurement over estimation

Line-fill -- whether a resume bullet fills its line cleanly or leaves an ugly orphan -- is the biggest time sink in resume formatting. The standard approach is to count characters and guess. But font kerning, URL line-breaking, and margin interactions make character counts unreliable.

This toolkit measures the actual rendered PDF. Using PyMuPDF, it reads the bounding boxes of every text span, groups wrapped lines into paragraphs, estimates the column width from the 90th percentile of line widths, and reports the exact fill percentage of each bullet's last line. When it says a bullet is at 43% fill, that's what the PDF actually shows.

### AI trope detection

If you use an LLM to help draft application materials, the output will contain identifiable AI writing patterns: em dashes for emphasis, tricolons (lists of three), rhetorical questions, "It's not X, it's Y" constructions, corporate buzzwords like "foster" and "holistic." Hiring managers increasingly recognize these patterns.

The `rules/ai_writing_tropes.md` file is a comprehensive, curated list of these patterns. The linter checks for the structural ones automatically (em dashes, model name capitalization). The rest serve as a pre-send checklist.

### Cross-document uniqueness

Your resume, cover letter, and application question responses should tell complementary parts of the same story, not echo each other. The crosscheck tool uses SequenceMatcher at a 0.75 similarity threshold to flag sentence-level redundancy between documents.

## What this is not

This is not a resume template service or an AI resume writer. It's a quality assurance pipeline for people who write their own materials and want to stop making the same mistakes twice.
