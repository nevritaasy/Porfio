# Extract project entries: name, year/date, description, related_skills

from __future__ import annotations

import json
import re
from pathlib import Path

from .date_utils import extract_date_range, parse_date_range

BULLET = re.compile(r"^[\u2022\u2023\u25E6\u2043\u2219•\-\*]\s*")
RE_PROJECT_YEAR = re.compile(r"^[A-Za-z].+?\((\d{4})\)\s*:", re.I)
RE_YEAR_IN_PARENS = re.compile(r"\((\d{4})\)")
RE_ICON_CHARS = re.compile(r"[\ue800-\uf8ff]+")

_DICT_PATH = Path(__file__).parent.parent / "recommendation" / "skill_dictionary.json"


def _load_all_skills_flat() -> list[str]:
    try:
        with open(_DICT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills: list[str] = []
        for cat_skills in data.values():
            skills.extend(s.lower() for s in cat_skills)
        return skills
    except Exception:
        return []


_ALL_SKILLS: list[str] = []


def _find_related_skills(text: str) -> list[str]:
    global _ALL_SKILLS
    if not _ALL_SKILLS:
        _ALL_SKILLS = _load_all_skills_flat()

    text_lower = text.lower()
    found: set[str] = set()
    for skill in _ALL_SKILLS:
        pattern = r"(?<![a-z])" + re.escape(skill) + r"(?![a-z])"
        if re.search(pattern, text_lower):
            found.add(skill.title())
    return sorted(found, key=str.lower)


def _parse_project_block(block: str) -> dict | None:
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        return None

    first_line = lines[0]
    first_lower = first_line.lower()

    if any(kw in first_lower for kw in ["course", "training", "certification", "pelatihan", "sertif"]):
        return None

    year_match = RE_PROJECT_YEAR.search(first_line)
    year_in_parens = RE_YEAR_IN_PARENS.search(first_line)

    # Extract project name
    if year_match:
        name = re.split(r"\s*\(", first_line)[0].strip()
        year = year_match.group(1)
    else:
        name = first_line
        year = year_in_parens.group(1) if year_in_parens else None

    name = RE_ICON_CHARS.sub("", name).strip()

    date_str = extract_date_range(first_line)
    date_range = parse_date_range(date_str) if date_str else {"start": year, "end": None}

    desc_parts: list[str] = []
    if ":" in first_line:
        after_colon = first_line.split(":", 1)[1].strip()
        if after_colon:
            desc_parts.append(after_colon)

    stop_words = ["hard skill", "soft skill", "technical skill", "interest", "tools", "languages"]
    
    for ln in lines[1:]:
        ln_lower = ln.lower().strip()
        if any(ln_lower.startswith(sw) for sw in stop_words):
            break
        desc_parts.append(BULLET.sub("", ln).strip())

    description = " ".join(p for p in desc_parts if p) or None
    related_skills = _find_related_skills(
        (description or "") + " " + name
    )

    if not name:
        return None

    return {
        "name": name,
        "year": year,
        "date_range": date_range,
        "description": description,
        "related_skills": related_skills,
    }


def extract_projects(section_lines: list[str]) -> list[dict]:
    clean = [
        ln for ln in section_lines
        if not ln.startswith("__SECTION_LABEL__:")
    ]
    if not clean:
        return []

    raw_blocks: list[list[str]] = []
    current: list[str] = []

    for line in clean:
        if RE_PROJECT_YEAR.search(line) and current:
            raw_blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        raw_blocks.append(current)

    results: list[dict] = []
    for block_lines in raw_blocks:
        parsed = _parse_project_block("\n".join(block_lines))
        if parsed:
            results.append(parsed)

    return results
