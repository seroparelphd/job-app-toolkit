# Job Discovery Workflow

How to find roles worth applying to. This runs BEFORE the 7-step application workflow.

## When to run

- When actively searching for new roles
- On a regular cadence if doing ongoing sweeps
- After a rejection (re-sweep the company's open roles)

## Search parameters

Pull from your ground truth and profile config:

- **Salary floor:** comp range max must reach your floor (surface `$190K-$220K`, skip `$180K-$199K`)
- **Location:** your acceptable locations only
- **Coding bar:** flag engineering-heavy roles if your day job is not coding-heavy
- **Publication gap:** flag roles requiring venue-specific papers you don't have
- **Cooldowns:** companies with reapplication waiting periods
- **Exclusions:** companies on your blocklist

## Search sources

| Source | Notes |
|--------|-------|
| Company careers pages | Check target companies directly |
| Job boards | LinkedIn Jobs, Indeed, Glassdoor, BuiltIn, Wellfound |
| Domain-specific boards | AI safety boards, research institution listings |
| Aggregators | Ladders, FlexJobs (employer names may be anonymized) |

## Vetting each result

For every hit, extract:
- Company, title, req ID, location, salary range
- Coding bar: LOW / MEDIUM / HIGH
- Publication requirement
- YOE and degree requirements
- Fit score (see `workflow/evaluation_rubric.md`)

## Deduplication

Before surfacing a role:
1. Check your application log -- have you already applied?
2. Check cooldowns and exclusions
3. Check variant registry -- is this already in progress?

## Output format

Ranked table, sorted by fit score:

| # | Role | Company | Comp | Location | Fit | Coding Bar | Gaps | Status |
|---|------|---------|------|----------|-----|------------|------|--------|

Include: direct apply URL, honest gap flags, recommended apply order.

Do NOT: surface roles below salary floor, recommend blocked companies without flagging, pitch engineering roles without coding bar flag.

## After the sweep

- You decide which roles to pursue. Those enter the 7-step workflow.
- Log discovered roles with status "discovered"
- Declined roles get no further action
