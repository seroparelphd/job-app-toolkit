"""
Resume linter: catches recurring failures BEFORE building the PDF.

Configurable via:
- banned_skills: list of skills to flag (loaded from config or passed directly)
- allowed_skills: list of known-good skills
- contact_fields: dict of {field_name: regex_pattern} for contact info validation
- statistical_terms: terms banned from non-research experience sections
- corrections_path: path to corrections_log.json for learned rules

The linter runs structural checks (em dashes, bullet formatting, capitalization),
content checks (banned skills, statistical claims in wrong sections), and all
learned corrections from the self-improvement engine.
"""

import re
import yaml
from pathlib import Path

from .learn import lint_from_corrections


# Default banned skills — tools/libraries the candidate hasn't used
DEFAULT_BANNED_SKILLS = [
    "networkx", "spacy", "nltk", "click", "typer",
    "jupyter", "jupyterlab", "statsmodels", "joblib",
    "hugging face transformers", "transformers",
    "weights & biases", "wandb", "mlflow",
    "postgresql", "bigquery", "aws", "s3", "ec2",
    "docker", "github actions",
]

# Default skill redundancy sets — near-synonyms that shouldn't appear together
DEFAULT_SKILL_REDUNDANCY_SETS = [
    {"bash", "shell scripting", "shell", "unix", "linux"},
    {"git", "version control"},
    {"jupyter", "jupyterlab", "notebook"},
]

# Statistical terms banned from industry experience bullets
DEFAULT_STATISTICAL_TERMS = [
    "statistical analysis", "statistical data analysis",
    "statistical modeling", "statistical test",
    "anova", "mixed-effects", "deseq2", "limma",
]


def _load_banned_skills(config_path: Path | None = None) -> list[str]:
    """Load banned skills from YAML config or return defaults."""
    if config_path and config_path.exists():
        try:
            data = yaml.safe_load(config_path.read_text())
            if isinstance(data, dict) and "banned" in data:
                return [s.lower() for s in data["banned"]]
        except Exception:
            pass
    return DEFAULT_BANNED_SKILLS


def _load_skill_redundancy_sets(config_path: Path | None = None) -> list[set[str]]:
    """Load skill redundancy sets from config or return defaults."""
    if config_path and config_path.exists():
        try:
            data = yaml.safe_load(config_path.read_text())
            if isinstance(data, dict) and "redundancy_sets" in data:
                return [set(s) for s in data["redundancy_sets"]]
        except Exception:
            pass
    return DEFAULT_SKILL_REDUNDANCY_SETS


def lint_resume_md(
    md_path: Path,
    banned_skills: list[str] | None = None,
    banned_skills_config: Path | None = None,
    contact_fields: dict[str, str] | None = None,
    statistical_terms: list[str] | None = None,
    skill_redundancy_sets: list[set[str]] | None = None,
    industry_role_pattern: str | None = None,
    corrections_path: Path | None = None,
) -> list[str]:
    """
    Lint a resume markdown file. Returns list of errors (empty = clean).

    Args:
        md_path: Path to the resume markdown file.
        banned_skills: List of skills to flag. Overrides config file.
        banned_skills_config: Path to banned_skills.yaml.
        contact_fields: Dict of {label: regex} for required contact info.
        statistical_terms: Terms banned from industry experience sections.
        skill_redundancy_sets: Sets of near-synonym skills to flag.
        industry_role_pattern: Regex to identify the industry role section
            where statistical terms are banned (PhD stats are fine).
        corrections_path: Path to corrections_log.json.
    """
    text = md_path.read_text()
    errors = []

    # Resolve config
    if banned_skills is None:
        banned_skills = _load_banned_skills(banned_skills_config)
    if statistical_terms is None:
        statistical_terms = DEFAULT_STATISTICAL_TERMS
    if skill_redundancy_sets is None:
        skill_redundancy_sets = _load_skill_redundancy_sets(banned_skills_config)

    # --- Structural checks ---

    # 1. Em dash check (U+2014)
    if "\u2014" in text:
        errors.append("EM DASH found in source MD — use commas/colons, never em dashes")

    # 2. En dash in source (U+2013) — pandoc converts -- to en dash in PDF, that's OK,
    #    but a literal en dash in the MD source is usually a mistake
    if "\u2013" in text:
        # Allow in date range context (digit–digit)
        non_date_endash = re.sub(r"\d\u2013\d", "", text)
        if "\u2013" in non_date_endash:
            errors.append(
                "EN DASH (U+2013) found in source MD — "
                "use -- for date ranges, pandoc converts to en dash in PDF"
            )

    # 3. Model names should be lowercase in body text
    if re.search(r"\bLogistic Regression\b|\bRandom Forest\b", text):
        errors.append("Model names capitalized — use lowercase: 'logistic regression', 'random forest'")

    # --- Content checks ---

    # 4. Banned skills
    lower = text.lower()
    for skill in banned_skills:
        if skill.lower() in lower:
            errors.append(f"BANNED SKILL in resume: {skill}")

    # 5. Statistical claims in industry experience bullets
    if industry_role_pattern:
        industry_match = re.search(industry_role_pattern, text, re.IGNORECASE | re.DOTALL)
        if industry_match:
            # Extract bullet lines from the matched industry section
            industry_text = industry_match.group(1) if industry_match.lastindex else industry_match.group(0)
            industry_bullets = re.findall(r"^\s*-\s+(.+)$", industry_text, re.MULTILINE)
            industry_text_joined = " ".join(industry_bullets).lower()
            for term in statistical_terms:
                if term in industry_text_joined:
                    errors.append(
                        f"STATISTICAL CLAIM in industry experience bullet: '{term}' — "
                        f"these belong in PhD/research sections only"
                    )

    # 6. Experience bullets ending with period
    exp_section = re.search(r"## Experience(.*?)(?=## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if exp_section:
        bullets = re.findall(r"^\s*-\s+(.+)$", exp_section.group(1), re.MULTILINE)
        for b in bullets:
            b = b.strip()
            if b.endswith(".") and not b.endswith("et al."):
                errors.append(f"Bullet ends with period: '{b[:60]}...' — remove terminal period")
                break  # one is enough to flag

    # 7. Contact info validation
    if contact_fields:
        for field, pattern in contact_fields.items():
            if not re.search(pattern, text, re.IGNORECASE):
                errors.append(f"Missing contact field: {field}")

    # 8. Technical Skills redundancy
    skills_section = re.search(r"## Technical Skills(.*?)(?=## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if skills_section:
        skill_lines = re.findall(
            r"^\s*-\s+\*\*[^*]+?:\*\*\s*(.+)$",
            skills_section.group(1),
            re.MULTILINE | re.IGNORECASE,
        )
        for line in skill_lines:
            line_lower = line.lower()
            for redundancy_set in skill_redundancy_sets:
                found = []
                for s in sorted(redundancy_set, key=len, reverse=True):
                    if s in line_lower:
                        if any(s in longer for longer in found):
                            continue
                        found.append(s)
                if len(found) >= 2:
                    errors.append(
                        f"Technical Skills redundancy: {', '.join(found)} in same bullet — "
                        f"these are near-synonyms, use at most one"
                    )
                    break

    # 9. Run learned corrections from corrections_log.json
    errors.extend(lint_from_corrections(text, "resume", corrections_path))

    return errors
