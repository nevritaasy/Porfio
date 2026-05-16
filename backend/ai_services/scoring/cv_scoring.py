"""
Scoring components:
  - Skill Score       (35%)
  - Experience Score  (20%)
  - Education Score   (15%)
  - Project Score     (15%)
  - Completeness Score(15%)

Final Score = weighted average of all components, scaled to 0–100.
"""

from __future__ import annotations

import re
from typing import Optional

from .scoring_rules import (
    WEIGHTS,
    SKILL_POINTS,
    SKILL_CAP,
    SKILL_IN_CONTEXT_MULTIPLIER,
    EXP_FULL_SCORE_MONTHS,
    EXP_FALLBACK_PTS_PER_ENTRY,
    EXP_FALLBACK_CAP,
    EDU_POINTS,
    PROJECT_BASE_PTS,
    PROJECT_HAS_DESC_BONUS,
    PROJECT_SKILL_BONUS_PER,
    PROJECT_CAP,
    COMPLETENESS_POINTS,
)

try:
    from ..extractor.date_utils import calculate_months_between
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from extractor.date_utils import calculate_months_between

def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _context_skills(cv_data: dict) -> set[str]:
    context: set[str] = set()

    for exp in cv_data.get("experience", []):
        for desc in exp.get("descriptions", []):
            for word in re.split(r"[\s,;]+", desc.lower()):
                context.add(word.strip())

    for proj in cv_data.get("projects", []):
        for skill in proj.get("related_skills", []):
            context.add(skill.lower())
        desc = proj.get("description") or ""
        for word in re.split(r"[\s,;]+", desc.lower()):
            context.add(word.strip())

    return context

def _score_skills(cv_data: dict) -> float:
    skills: dict = cv_data.get("skills", {})
    if not skills:
        return 0.0

    context = _context_skills(cv_data)
    raw_points = 0.0

    for category, pts_per in SKILL_POINTS.items():
        for skill in skills.get(category, []):
            pts = pts_per
            if skill.lower() in context:
                pts *= SKILL_IN_CONTEXT_MULTIPLIER
            raw_points += pts

    return _clamp(raw_points / SKILL_CAP * 100.0)


def _score_experience(cv_data: dict) -> float:
    experience: list[dict] = cv_data.get("experience", [])
    if not experience:
        return 0.0

    total_months = 0
    entries_with_dates = 0

    for exp in experience:
        date_range: dict = exp.get("date_range", {}) or {}
        start = date_range.get("start")
        end = date_range.get("end")
        if start:
            months = calculate_months_between(start, end)
            if months > 0:
                total_months += months
                entries_with_dates += 1

    if entries_with_dates > 0:
        # Duration-based scoring
        score = (total_months / EXP_FULL_SCORE_MONTHS) * 100.0
    else:
        # Fallback: count-based
        raw = len(experience) * EXP_FALLBACK_PTS_PER_ENTRY
        score = (raw / EXP_FALLBACK_CAP) * 100.0

    return _clamp(score)


def _score_education(cv_data: dict) -> float:
    education: list[dict] = cv_data.get("education", [])
    if not education:
        return 0.0

    best_score = 0.0
    for edu in education:
        pts = 0.0
        if edu.get("institution"):
            pts += EDU_POINTS["has_institution"]
        if edu.get("degree"):
            pts += EDU_POINTS["has_degree"]
        if edu.get("field"):
            pts += EDU_POINTS["has_field"]
        date_range = edu.get("date_range") or {}
        if date_range.get("start") or date_range.get("end"):
            pts += EDU_POINTS["has_date"]
        if edu.get("gpa"):
            pts += EDU_POINTS["has_gpa"]
        best_score = max(best_score, pts)

    return _clamp(best_score)


def _score_projects(cv_data: dict) -> float:
    projects: list[dict] = cv_data.get("projects", [])
    if not projects:
        return 0.0

    raw = 0.0
    for proj in projects:
        pts = PROJECT_BASE_PTS
        if proj.get("description"):
            pts += PROJECT_HAS_DESC_BONUS
        related = proj.get("related_skills", [])
        pts += min(len(related) * PROJECT_SKILL_BONUS_PER, 20.0)
        raw += pts

    return _clamp(raw / PROJECT_CAP * 100.0)


def _score_completeness(cv_data: dict) -> float:
    contact: dict = cv_data.get("contact", {}) or {}
    pts = 0.0

    if contact.get("name"):
        pts += COMPLETENESS_POINTS["name"]
    if contact.get("email"):
        pts += COMPLETENESS_POINTS["email"]
    if contact.get("phone"):
        pts += COMPLETENESS_POINTS["phone"]
    if contact.get("linkedin") or contact.get("github"):
        pts += COMPLETENESS_POINTS["linkedin_or_github"]
    if contact.get("portfolio"):
        pts += COMPLETENESS_POINTS["portfolio"]
    if cv_data.get("education"):
        pts += COMPLETENESS_POINTS["education"]
    if cv_data.get("skills") and any(
        cv_data["skills"].get(k) for k in ("technical_skills", "soft_skills", "tools", "languages")
    ):
        pts += COMPLETENESS_POINTS["skills"]
    if cv_data.get("experience"):
        pts += COMPLETENESS_POINTS["experience"]
    if cv_data.get("projects"):
        pts += COMPLETENESS_POINTS["projects"]
    if cv_data.get("certifications"):
        pts += COMPLETENESS_POINTS["certifications"]

    return _clamp(pts)

def _score_parsing_quality(cv_data: dict) -> float:
    score = 100.0
    
    # Check experience
    for exp in cv_data.get("experience", []):
        company = str(exp.get("company", "")).lower()
        if "project" in company or "portfolio" in company:
            score -= 20.0
            
        for desc in exp.get("descriptions", []):
            desc_lower = desc.lower()
            if "hard skill" in desc_lower or "soft skill" in desc_lower or "interest" in desc_lower or "technical skill" in desc_lower:
                score -= 15.0

    # Check projects
    for proj in cv_data.get("projects", []):
        desc = str(proj.get("description", "")).lower()
        if "hard skill" in desc or "soft skill" in desc or "interest" in desc or "technical skill" in desc:
            score -= 15.0
            
    return _clamp(score)

def _generate_explanation(scores: dict) -> str:
    parts: list[str] = []

    skill = scores["skill_score"]
    if skill >= 80:
        parts.append("Skill set sangat kuat.")
    elif skill >= 50:
        parts.append("Skill set cukup baik, masih ada ruang untuk berkembang.")
    else:
        parts.append("Skill set perlu diperluas dan diperkuat.")

    exp = scores["experience_score"]
    if exp >= 80:
        parts.append("Pengalaman kerja sangat solid.")
    elif exp >= 40:
        parts.append("Pengalaman kerja cukup, pertimbangkan menambah deskripsi dan durasi.")
    else:
        parts.append("Pengalaman kerja masih terbatas; tambahkan magang atau volunteer experience.")

    edu = scores["education_score"]
    if edu >= 75:
        parts.append("Latar belakang pendidikan lengkap.")
    elif edu >= 40:
        parts.append("Informasi pendidikan ada, tapi belum lengkap (degree, field, atau GPA mungkin hilang).")
    else:
        parts.append("Informasi pendidikan sangat minim.")

    proj = scores["project_score"]
    if proj >= 70:
        parts.append("Portofolio proyek sangat baik.")
    elif proj >= 30:
        parts.append("Ada beberapa proyek; tambahkan deskripsi dan teknologi yang digunakan.")
    else:
        parts.append("Tambahkan proyek pribadi atau open-source untuk memperkuat CV.")

    comp = scores["completeness_score"]
    if comp >= 80:
        parts.append("CV terisi dengan sangat lengkap.")
    elif comp >= 50:
        parts.append("CV cukup lengkap; pertimbangkan menambahkan LinkedIn, GitHub, atau portfolio.")
    else:
        parts.append("CV masih banyak bagian yang kosong; lengkapi contact dan semua seksi utama.")

    return " ".join(parts)

# Main entry point
def score_cv(cv_data: dict, recommendations: list = None) -> dict:
    skill_score = _score_skills(cv_data)
    experience_score = _score_experience(cv_data)
    education_score = _score_education(cv_data)
    project_score = _score_projects(cv_data)
    completeness_score = _score_completeness(cv_data)
    parsing_quality_score = _score_parsing_quality(cv_data)

    overall = (
        skill_score * WEIGHTS["skill_score"]
        + experience_score * WEIGHTS["experience_score"]
        + education_score * WEIGHTS["education_score"]
        + project_score * WEIGHTS["project_score"]
        + completeness_score * WEIGHTS["completeness_score"]
    )
 
    if parsing_quality_score < 100:
        overall = overall * (0.5 + 0.5 * (parsing_quality_score / 100.0))

    # Apply realistic deductions for typical missing parts
    contact = cv_data.get("contact", {}) or {}
    if not contact.get("portfolio"):
        overall -= 4.0
    if not cv_data.get("certifications"):
        overall -= 3.0
    
    # Deduct for missing skills from top recommendation
    if recommendations:
        missing = recommendations[0].get("missing_skills", [])
        overall -= min(len(missing) * 2.0, 8.0)

    scores = {
        "overall_score": round(_clamp(overall), 1),
        "skill_score": round(skill_score, 1),
        "experience_score": round(experience_score, 1),
        "education_score": round(education_score, 1),
        "project_score": round(project_score, 1),
        "completeness_score": round(completeness_score, 1),
        "parsing_quality_score": round(parsing_quality_score, 1),
    }

    scores["explanation"] = _generate_explanation(scores)
    return scores
