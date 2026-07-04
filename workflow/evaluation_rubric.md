# Job Evaluation Rubric

How to evaluate any job listing against your profile.

## Profile snapshot

Maintain a current snapshot of what you have and don't have. Update when your profile changes materially.

### Structure

**Have:** education, current role, technical expertise, publications, skills, domain knowledge.

**Don't have:** be honest about gaps -- missing venue publications, production engineering experience, management experience, domain-specific skills you lack.

**Partial:** areas where you have transferable but not direct experience.

## Evaluation process

### Step 1: Hard filters (binary pass/fail)

| Filter | Rule |
|--------|------|
| Salary | Comp range max >= your floor |
| Location | Acceptable location or remote policy |
| Cooldown | No active waiting period |
| Already applied | Not in your application log |
| Exclusions | Not on your blocklist |

Any fail = Skip.

### Step 2: Requirement mapping

Extract every requirement from the JD. Separate required from preferred. Map each:

- **Pass** -- you clearly have this (cite the specific experience)
- **Fail** -- you clearly don't have this
- **Partial** -- transferable experience (explain what transfers and what's missing)

A fail on a required qualification is a hard gap. A fail on a preferred qualification is noted but not disqualifying.

### Step 3: Fit scoring

Score on five dimensions (1-5 each):

| Dimension | Weight | 1 (weak) | 3 (moderate) | 5 (strong) |
|-----------|--------|----------|--------------|------------|
| Core alignment | 40% | No overlap | Some requirements match | JD describes your actual job |
| Coding bar | 25% | Production SWE required | "Strong Python" preferred | Research focus, code optional |
| Publication gap | 15% | Top venue pubs required | Pubs preferred | No pub requirement |
| Seniority match | 10% | 7+ yrs or management required | 3-5 yrs post-PhD | Entry-level |
| Domain relevance | 10% | Unrelated domain | Adjacent domain | Direct match |

Composite score: weighted average x 20 = score out of 100.

### Tier assignment

- **Tier 1 (75+):** Strong alignment, manageable gaps. Apply.
- **Tier 2 (60-74):** Good fit on paper, but gaps need a closer look.
- **Tier 3 (<60):** Wrong fit or too many gaps. Skip.

### Step 4: Output

For each role:

```
[Company] -- [Title] ([Location], [Comp])
Tier: [1/2/3] | Score: [X/100]

REQUIRED:
  Pass: [Requirement] -- [evidence]
  Partial: [Requirement] -- [what transfers, what's missing]
  Fail: [Requirement] -- [gap] <-- HARD GAP

PREFERRED:
  Pass: [Preference] -- [evidence]
  Fail: [Preference] -- [gap, not disqualifying]

Gaps: [honest summary]
Apply link: [URL]
```

For batch evaluations, group by tier and lead with Tier 1.
