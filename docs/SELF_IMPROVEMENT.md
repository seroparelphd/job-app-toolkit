# Self-Improvement Loop

The core innovation of this toolkit: every correction becomes a permanent lint rule.

## How it works

### 1. During an application session

You're drafting a resume. A reviewer catches that you used "leverage" (corporate buzzword). You fix it manually. Then:

```bash
jat learn no_leverage "Do not use 'leverage' in application materials" \
    --pattern "(?i)\bleverag" \
    --files resume,cover_letter,app_questions \
    --severity error
```

### 2. The correction is stored

In `config/corrections_log.json`:

```json
{
    "id": "no_leverage",
    "date": "2026-07-04",
    "application": "manual",
    "category": "content",
    "rule": "no_leverage",
    "description": "Do not use 'leverage' in application materials",
    "pattern": "(?i)\\bleverag",
    "file_types": ["resume", "cover_letter", "app_questions"],
    "severity": "error",
    "caught_by": "user_feedback"
}
```

### 3. Next application, it's automatic

When you run `jat lint Resume.md` on your next application, the linter loads every entry from corrections_log.json and runs each regex pattern against the text. If "leverage" appears, you get:

```
LINT FAIL:
  x [LEARNED:no_leverage] no_leverage: Do not use 'leverage' in application materials — found 1 match(es)
```

No manual recall needed. The system remembers.

## Correction entry fields

| Field | Purpose |
|-------|---------|
| `id` | Unique identifier (also used as rule name) |
| `date` | When the correction was learned |
| `application` | Which application cycle surfaced it |
| `category` | `content`, `formatting`, `process`, `cross_doc` |
| `rule` | Human-readable rule name |
| `description` | What the rule catches and why |
| `pattern` | Regex pattern (null for process-only rules) |
| `file_types` | Which documents to check: `resume`, `cover_letter`, `app_questions` |
| `severity` | `error` (blocks), `warning` (flags), `process` (reminder), `override` (disables a prior rule) |
| `caught_by` | Who found the issue: `user_feedback`, `reviewer`, `ats_check`, `session_observation` |

## Override mechanism

Sometimes a rule is too strict. The `override` severity disables a prior rule without deleting it:

```json
{
    "id": "work_is_acceptable",
    "description": "The word 'work' is acceptable. Previous lint rule was overly strict.",
    "severity": "override"
}
```

Override entries are skipped during linting -- they exist as documentation of the decision.

## Post-submission retrospective

After every submission, review corrections made during the session:

1. Were any fixes applied manually that aren't yet in corrections_log.json?
2. For each: run `jat learn` with an appropriate pattern
3. Run `jat corrections count` to verify

The goal: zero recurring mistakes. If you fix something once, you should never have to fix it again.

## Accumulation over time

After 5 applications, you might have 15 learned rules. After 20 applications, 40+. Each one is a specific, concrete lesson: not "write better" but "don't use 'leverage', don't end bullets with periods, don't put statistical claims in your industry experience section."

The corrections log is your institutional memory for job applications. It compounds.
