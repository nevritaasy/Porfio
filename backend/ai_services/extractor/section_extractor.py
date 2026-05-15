# Split CV text into sections

from __future__ import annotations

import re

_INVISIBLE_CHARS = ["\u200b", "\u200c", "\u200d", "\ufeff"]

_SECTION_KEYWORD_MAP: list[tuple[str, list[str]]] = [
    ("education", [
        "education", "academic background", "academic history",
        "educational background", "qualifications", "academic qualification",
        "pendidikan", "riwayat pendidikan", "latar belakang pendidikan",
    ]),
    ("experience", [
        "experience", "work experience", "professional experience", "employment history",
        "internship experience", "internship", "work history",
        "organization experience", "organizational experience", "organizational experiences",
        "volunteer experience", "leadership experience", "career history",
        "pengalaman kerja", "riwayat kerja", "pengalaman organisasi",
        "pengalaman magang", "pengalaman",
    ]),
    ("skills", [
        "skills", "competencies", "technical skills", "core competencies",
        "hard skills", "soft skills", "tools", "languages",
        "keahlian", "kemampuan", "kompetensi", "keterampilan",
    ]),
    ("projects", [
        "projects", "project", "personal projects", "relevant projects",
        "side projects", "portfolio", "project experience",
        "proyek", "projek", "portofolio proyek", "portofolio",
    ]),
    ("certifications", [
        "certifications", "certification", "licenses", "awards", "achievements",
        "courses", "training", "certificate",
        "sertifikasi", "sertifikat", "penghargaan", "pelatihan", "kursus",
    ]),
    ("interest", [
        "interest", "interests", "hobbies",
        "minat", "hobi"
    ]),
    ("summary", [
        "summary", "profile", "objective", "about me", "professional summary",
        "career objective",
        "ringkasan", "profil", "tentang saya", "deskripsi diri",
    ]),
]

# Combined-section patterns (Jika ada, biasanya user mix their project, interests, achievement, etc)
_COMBINED_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"projects?.+skills|skills.+projects?", re.I), "mixed_projects_skills"),
    (re.compile(r"skills?.+interest|interest.+skills?", re.I), "mixed_skills_interests"),
    (re.compile(r"skills?.+achieve|achieve.+skills?", re.I), "mixed_skills_achievements"),
    (re.compile(r"skills?.+experience|experience.+skills?", re.I), "mixed_skills_experience"),
    (re.compile(r"achieve.+experience|experience.+achieve", re.I), "mixed_achievements_experience"),
    (re.compile(
        r"(skills?|projects?|experience|achieve|interest|certif|award)"
        r".{0,25}"
        r"(skills?|projects?|experience|achieve|interest|certif|award)",
        re.I,
    ), "mixed_other"),
]

# Subsection signals within mixed sections
_SUBSECTION_SIGNALS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^(hard skills?|technical skills?)\s*[:\-\u2022\ue801]", re.I), "skills"),
    (re.compile(r"^(soft skills?)\s*[:\-]", re.I), "skills"),
    (re.compile(r"^(skills?|competenc|keahlian|kemampuan)\s*[:\-]", re.I), "skills"),
    (re.compile(r"^(interest|interests?|minat)\s*[:\-]", re.I), "interests"),
    (re.compile(r"^(achievement|achievements?|award|awards?|certif)\s*[:\-]?", re.I), "achievements"),
    (re.compile(r"^(course|courses?|training|pelatihan)\s*[:\(\-]", re.I), "achievements"),
    (re.compile(r".+\(\d{4}\)\s*:", re.I), "projects"),
]

RE_PROJECT_ENTRY = re.compile(r".+\(\d{4}\)\s*:", re.I)


def normalize_text(text: str) -> list[str]:
    for char in _INVISIBLE_CHARS:
        text = text.replace(char, "")
    lines = text.split("\n")
    return [line.strip() for line in lines if line.strip()]


def _is_section_header(line: str) -> bool:
    clean = line.strip()
    if not clean or len(clean.split()) > 8:
        return False
    if clean[-1] in ".,?":
        return False
    return True


def detect_section_type(line: str) -> str | None:
    if not _is_section_header(line):
        return None

    low = line.lower().strip()

    for pattern, tag in _COMBINED_PATTERNS:
        if pattern.search(low):
            return tag

    for canonical, keywords in _SECTION_KEYWORD_MAP:
        if low in keywords or any(low.startswith(kw) or low.endswith(kw) for kw in keywords):
             if len(low.split()) <= 4:
                 return canonical

    return None


def _content_type_of_line(line: str) -> str | None:
    for pattern, sub_type in _SUBSECTION_SIGNALS:
        if pattern.match(line):
            return sub_type
    return None


def split_mixed_section(lines: list[str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {
        "skills": [],
        "projects": [],
        "achievements": [],
        "interests": [],
        "experience": [],
    }

    state = "skills"
    for line in lines:
        if line.startswith("__SECTION_LABEL__:"):
            label = line.replace("__SECTION_LABEL__:", "").lower()
            if "project" in label:
                state = "projects"
            elif "achieve" in label or "course" in label or "award" in label:
                state = "achievements"
            break

    merged: list[str] = []
    for line in lines:
        if line.startswith("__SECTION_LABEL__:"):
            continue
        sub = _content_type_of_line(line)
        if merged and sub is None and not RE_PROJECT_ENTRY.match(line) and line and not line[0].isupper():
            merged[-1] += " " + line
            continue
        merged.append(line)

    for line in merged:
        sub = _content_type_of_line(line)
        if sub:
            state = sub
        if RE_PROJECT_ENTRY.match(line):
            state = "projects"
        buckets[state].append(line)

    return buckets


def split_sections(text: str) -> dict[str, list[str]]:
    lines = normalize_text(text)
    sections: dict[str, list[str]] = {}
    current_section = "header"
    sections[current_section] = []

    stop_keywords = {
        "projects", "skills", "hard skills", "soft skills", "interest",
        "languages", "tools", "portfolio"
    }

    for line in lines:
        tag = detect_section_type(line)
        
        if tag:
            current_section = tag
            sections.setdefault(current_section, [])
            sections[current_section].append("__SECTION_LABEL__:" + line)
            continue
      
        clean_line_lower = line.strip().lower()
        if clean_line_lower in stop_keywords and len(line.split()) <= 2:
            if "project" in clean_line_lower or "portfolio" in clean_line_lower:
                current_section = "projects"
            elif "skill" in clean_line_lower or "tool" in clean_line_lower or "language" in clean_line_lower:
                current_section = "skills"
            elif "interest" in clean_line_lower:
                current_section = "interest"
            
            sections.setdefault(current_section, [])
            sections[current_section].append("__SECTION_LABEL__:" + line)
            continue

        sections.setdefault(current_section, [])
        sections[current_section].append(line)

    return sections
