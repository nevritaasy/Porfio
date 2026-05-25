# Extract and categorize skills 

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

_DICT_PATH = Path(__file__).parent.parent / "recommendation" / "skill_dictionary.json"

_SKILL_DICT: dict[str, list[str]] | None = None


def _load_skill_dict() -> dict[str, list[str]]:
    global _SKILL_DICT
    if _SKILL_DICT is not None:
        return _SKILL_DICT

    try:
        with open(_DICT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _SKILL_DICT = {
            category: [s.lower() for s in skills]
            for category, skills in data.items()
        }
        return _SKILL_DICT
    except Exception as exc:
        print(f"[skill_extractor] Could not load skill dictionary: {exc}", file=sys.stderr)
        _SKILL_DICT = {
            "technical_skills": [],
            "soft_skills": [],
            "tools": [],
            "languages": [],
        }
        return _SKILL_DICT


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_skills(
    section_lines: list[str],
    full_text: Optional[str] = None,
) -> dict[str, list[str]]:
    skill_dict = _load_skill_dict()

    skills_text = " ".join(
        ln for ln in section_lines if not ln.startswith("__SECTION_LABEL__:")
    )
    search_corpus = _normalize_text(skills_text)
    if full_text:
        search_corpus += " " + _normalize_text(full_text)

    try:
        with open(_DICT_PATH, "r", encoding="utf-8") as f:
            raw_dict: dict[str, list[str]] = json.load(f)
    except Exception:
        raw_dict = {k: [] for k in skill_dict}

    results: dict[str, list[str]] = {
        "technical_skills": [],
        "soft_skills": [],
        "tools": [],
        "languages": [],
    }

    for category, skills_lower in skill_dict.items():
        if category not in results:
            continue

        raw_skills = raw_dict.get(category, [])
        found: set[str] = set()

        for idx, skill_lower in enumerate(skills_lower):
            pattern = r"(?<![a-z])" + re.escape(skill_lower) + r"(?![a-z])"
            if re.search(pattern, search_corpus):
                original = raw_skills[idx] if idx < len(raw_skills) else skill_lower.title()
                found.add(original)

        results[category] = sorted(found, key=str.lower)

    all_found_lower = {s.lower() for cat in results.values() for s in cat}
    
    # Synonym normalization (idk ini buat apa but it works...)
    if "github" in all_found_lower or "gitlab" in all_found_lower:
        if "Git" not in results["tools"] and "git" not in all_found_lower:
            results["tools"].append("Git")
            
    if any(db in all_found_lower for db in ["postgresql", "mysql", "mongodb", "redis"]):
        if "SQL" not in results["technical_skills"] and "sql" not in all_found_lower:
            results["technical_skills"].append("SQL")
            
    if "javascript" in all_found_lower:
        if "JavaScript" not in results["technical_skills"]:
            results["technical_skills"].append("JavaScript")
            
    for cat, skills in results.items():
        unique_skills = {}
        for s in skills:
            if s.lower() not in unique_skills:
                unique_skills[s.lower()] = s
        results[cat] = sorted(unique_skills.values(), key=str.lower)

    return results
