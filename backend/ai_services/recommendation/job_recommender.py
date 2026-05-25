# Job recommendation: Match a CV profile to job roles and ranked recommendations
# Output: top 3–5 role recommendations with match score, matched/missing skills, and reasons

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

# Paths to data files
_ROLES_PATH = Path(__file__).parent / "job_roles.json"
_DICT_PATH = Path(__file__).parent / "skill_dictionary.json"

_JOB_ROLES: list[dict] | None = None


def _load_job_roles() -> list[dict]:
    global _JOB_ROLES
    if _JOB_ROLES is not None:
        return _JOB_ROLES
    try:
        with open(_ROLES_PATH, "r", encoding="utf-8") as f:
            _JOB_ROLES = json.load(f)
    except Exception as exc:
        print(f"[job_recommender] Could not load job_roles.json: {exc}", file=sys.stderr)
        _JOB_ROLES = []
    return _JOB_ROLES


def _flatten_skills(skills: dict) -> set[str]:
    flat: set[str] = set()
    for category_skills in skills.values():
        if isinstance(category_skills, list):
            flat.update(s.lower() for s in category_skills)
    return flat


def _collect_context_skills(cv_data: dict) -> set[str]:
    context: set[str] = set()
    for exp in cv_data.get("experience", []):
        for desc in exp.get("descriptions", []):
            context.update(w.strip().lower() for w in re.split(r"[\s,;]+", desc))
    for proj in cv_data.get("projects", []):
        for skill in proj.get("related_skills", []):
            context.add(skill.lower())
        desc = proj.get("description") or ""
        context.update(w.strip().lower() for w in re.split(r"[\s,;]+", desc))
    return context


def _score_role(
    role: dict,
    user_skills: set[str],
    context_skills: set[str],
) -> tuple[float, list[str], list[str]]:
    required: list[str] = [s.lower() for s in role.get("required_skills", [])]
    optional: list[str] = [s.lower() for s in role.get("optional_skills", [])]

    matched_req: list[str] = []
    missing_req: list[str] = []
    matched_opt: list[str] = []

    for skill in required:
        if skill in user_skills or skill in context_skills:
            matched_req.append(skill)
        else:
            missing_req.append(skill)

    for skill in optional:
        if skill in user_skills or skill in context_skills:
            matched_opt.append(skill)

    # Required skills: 70%
    req_ratio = len(matched_req) / max(len(required), 1)
    # Optional skills: 30%
    opt_ratio = len(matched_opt) / max(len(optional), 1)

    raw_score = req_ratio * 70.0 + opt_ratio * 30.0

    matched_skills_display = [s.title() for s in (matched_req + matched_opt)]
    missing_skills_display = [s.title() for s in missing_req]

    return round(raw_score, 1), matched_skills_display, missing_skills_display


def _build_reason(
    role: dict,
    matched_skills: list[str],
    missing_skills: list[str],
    match_score: float,
) -> str:
    role_name = role["role"]
    category = role["category"]

    if match_score >= 80:
        strength = "sangat cocok"
    elif match_score >= 60:
        strength = "cukup cocok"
    elif match_score >= 40:
        strength = "berpotensi cocok"
    else:
        strength = "perlu pengembangan lebih lanjut untuk"

    matched_str = ", ".join(matched_skills[:4]) if matched_skills else "tidak ada skill yang terdeteksi"
    reason = (
        f"Profil Anda {strength} untuk posisi {role_name} di bidang {category}. "
        f"Skill yang relevan: {matched_str}."
    )
    if missing_skills:
        missing_str = ", ".join(missing_skills[:3])
        reason += f" Skill yang perlu ditingkatkan: {missing_str}."
    return reason


def _build_improvement_suggestions(
    role: dict,
    missing_skills: list[str],
) -> list[str]:
    suggestions: list[str] = []
    if missing_skills:
        for skill in missing_skills[:3]:
            suggestions.append(f"Pelajari {skill} untuk memenuhi persyaratan utama role ini.")
    if role.get("optional_skills"):
        top_optional = role["optional_skills"][:2]
        for skill in top_optional:
            suggestions.append(f"Mempelajari {skill} akan meningkatkan daya saing Anda.")
    if not suggestions:
        suggestions.append("Pertahankan dan perdalam skill yang sudah dimiliki.")
    return suggestions


def recommend_jobs(
    cv_data: dict,
    top_n: int = 5,
) -> list[dict]:
    job_roles = _load_job_roles()
    if not job_roles:
        return []

    user_skills = _flatten_skills(cv_data.get("skills", {}))
    context_skills = _collect_context_skills(cv_data)

    scored: list[dict] = []
    for role in job_roles:
        match_score, matched_skills, missing_skills = _score_role(
            role, user_skills, context_skills
        )
        reason = _build_reason(role, matched_skills, missing_skills, match_score)
        suggestions = _build_improvement_suggestions(role, missing_skills)

        scored.append({
            "role": role["role"],
            "category": role["category"],
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "reason": reason,
            "improvement_suggestions": suggestions,
        })

    # Ranked
    scored.sort(key=lambda x: (-x["match_score"], x["role"]))

    return scored[:top_n]
