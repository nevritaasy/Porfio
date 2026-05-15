from __future__ import annotations

# Weights
WEIGHTS: dict[str, float] = {
    "skill_score": 0.35,
    "experience_score": 0.20,
    "education_score": 0.15,
    "project_score": 0.15,
    "completeness_score": 0.15,
}

# Points per skill per category 
SKILL_POINTS: dict[str, float] = {
    "technical_skills": 4.0,   
    "tools": 3.0,
    "languages": 3.0,
    "soft_skills": 2.0,
}

SKILL_CAP: float = 100.0
SKILL_IN_CONTEXT_MULTIPLIER: float = 1.3

# Experience
EXP_FULL_SCORE_MONTHS: int = 60       
EXP_FALLBACK_PTS_PER_ENTRY: float = 15.0
EXP_FALLBACK_CAP: float = 100.0

# Education
EDU_POINTS: dict[str, float] = {
    "has_institution": 20.0,
    "has_degree": 25.0,
    "has_field": 15.0,
    "has_date": 15.0,
    "has_gpa": 25.0,
}

# Project
PROJECT_BASE_PTS: float = 15.0         
PROJECT_HAS_DESC_BONUS: float = 10.0   
PROJECT_SKILL_BONUS_PER: float = 5.0  
PROJECT_CAP: float = 100.0

# Completeness
COMPLETENESS_POINTS: dict[str, float] = {
    "name": 10.0,
    "email": 10.0,
    "phone": 10.0,
    "linkedin_or_github": 10.0,
    "portfolio": 5.0,
    "education": 15.0,
    "skills": 15.0,
    "experience": 15.0,
    "projects": 10.0,
}
