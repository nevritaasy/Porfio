import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from parser import parse_cv_file
from extractor import (
    split_sections,
    split_mixed_section,
    extract_contact,
    extract_education,
    extract_experience,
    extract_skills,
    extract_projects,
    extract_certifications,
)
from scoring import score_cv
from recommendation import recommend_jobs
from llm import OllamaClient
from llm.prompt_templates import (
    build_profile_summary_prompt,
    build_strengths_prompt,
    build_improvement_prompt,
)


def _configure_utf8_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


_configure_utf8_stdio()

def _generate_fallback_summary(scores: dict, recommendations: list, cv_data: dict | None = None) -> dict:
    # Generate a rule-based fallback summary when Ollama is unavailable.
    cv_data = cv_data or {}
    summary = _build_grounded_profile_summary(cv_data)
    strengths = _build_grounded_strengths(cv_data)
    improvements = _build_grounded_improvements(cv_data, recommendations)

    return {
        "profile_summary": summary,
        "strengths": strengths,
        "areas_for_improvement": improvements,
    }


_EXPERIENCE_CONTAMINATION_RE = re.compile(
    r"\b(?:soft\s+skills?|hard\s+skills?|course|courses?|certification|"
    r"certifications?|certificate|certificates?|training|trainings?)\b",
    re.IGNORECASE,
)


def _is_contaminated_experience(exp: dict) -> bool:
    company = exp.get("company") or ""
    role = exp.get("role") or ""
    return bool(
        _EXPERIENCE_CONTAMINATION_RE.search(company)
        or _EXPERIENCE_CONTAMINATION_RE.search(role)
    )


def _filter_experience_entries(experience: list[dict]) -> list[dict]:
    filtered: list[dict] = []
    for idx, exp in enumerate(experience, start=1):
        if _is_contaminated_experience(exp):
            print(
                f"[validation][warning] removed non-experience item #{idx}: "
                f"company={(exp.get('company') or '')!r}, role={(exp.get('role') or '')!r}",
                file=sys.stderr,
            )
            continue
        filtered.append(exp)
    return filtered


def _log_parsing_validation(cv_data: dict) -> None:
    skills = cv_data.get("skills", {}) or {}
    experience = cv_data.get("experience", []) or []
    projects = cv_data.get("projects", []) or []
    certifications = cv_data.get("certifications", []) or []

    print("[validation] candidate_name:", (cv_data.get("contact") or {}).get("name") or "-", file=sys.stderr)
    print("[validation] experience_count:", len(experience), file=sys.stderr)
    print("[validation] projects_count:", len(projects), file=sys.stderr)
    print("[validation] certifications_courses_count:", len(certifications), file=sys.stderr)
    print("[validation] technical_skills_count:", len(skills.get("technical_skills", []) or []), file=sys.stderr)
    print("[validation] soft_skills_count:", len(skills.get("soft_skills", []) or []), file=sys.stderr)

    for idx, exp in enumerate(experience, start=1):
        company = exp.get("company") or ""
        role = exp.get("role") or ""
        if _EXPERIENCE_CONTAMINATION_RE.search(company) or _EXPERIENCE_CONTAMINATION_RE.search(role):
            print(
                f"[validation][warning] experience #{idx} may contain non-experience heading: "
                f"company={company!r}, role={role!r}",
                file=sys.stderr,
            )


def _education_institution(cv_data: dict) -> str:
    education = cv_data.get("education") or []
    if not education:
        return ""
    institution = (education[0].get("institution") or "").strip()
    return institution.split(" - ")[0].strip() or institution


def _display_name(raw_name: str) -> str:
    if not raw_name:
        return "Kandidat"
    return raw_name.title() if raw_name.isupper() else raw_name


def _primary_study_field(cv_data: dict) -> str:
    education = cv_data.get("education") or []
    if not education:
        return ""
    edu = education[0] or {}
    field = (edu.get("field") or "").strip()
    if field:
        field = field.split(",")[0].strip()
        field = re.sub(r"\s*\([^)]*\)", "", field).strip()
        return field
    return (edu.get("degree") or "").strip()


def _ordered_technical_skills(cv_data: dict) -> list[str]:
    skills = cv_data.get("skills", {}) or {}

    technical = skills.get("technical_skills", []) or []
    tools = skills.get("tools", []) or []
    languages = skills.get("languages", []) or []

    combined = technical + tools + languages

    ordered = []
    seen = set()

    for skill in combined:
        if not skill:
            continue

        normalized = str(skill).strip()
        key = normalized.lower()

        if key in seen:
            continue

        ordered.append(normalized)
        seen.add(key)

    return ordered[:8]


def _format_list(items: list[str]) -> str:
    clean = [item for item in items if item]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    return ", ".join(clean[:-1]) + f", dan {clean[-1]}"


def _normalize_text_list(values: list | None) -> list[str]:
    if not values:
        return []
    normalized: list[str] = []
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            normalized.append(text)
    return normalized


def _experience_focuses(cv_data: dict) -> list[str]:
    corpus = " ".join(
        " ".join(
            _normalize_text_list(
                [exp.get("role"), exp.get("company"), *(exp.get("descriptions") or [])]
            )
        )
        for exp in cv_data.get("experience", []) or []
    ).lower()
    focuses: list[str] = []
    if any(term in corpus for term in ["budget", "expense", "financial", "fund allocation", "treasurer"]):
        focuses.append("keuangan")
    if any(term in corpus for term in ["environmental", "green campaigns", "environment"]):
        focuses.append("lingkungan")
    if any(term in corpus for term in ["event", "committee", "logistics", "competition", "coordination"]):
        focuses.append("koordinasi acara")
    return focuses[:3]


def _has_contact_portfolio(cv_data: dict) -> bool:
    contact = cv_data.get("contact") or {}
    return bool(contact.get("linkedin") or contact.get("github") or contact.get("portfolio"))


def _build_grounded_profile_summary(cv_data: dict) -> str:
    name = _display_name((cv_data.get("contact") or {}).get("name") or "")
    field = _primary_study_field(cv_data)
    institution = _education_institution(cv_data)
    tech = _format_list(_ordered_technical_skills(cv_data))
    focuses = _format_list(_experience_focuses(cv_data))

    if field and institution:
        first = f"{name} adalah mahasiswa {field} di {institution}"
    elif institution:
        first = f"{name} adalah kandidat dengan latar belakang pendidikan di {institution}"
    else:
        first = f"{name} adalah kandidat dengan pengalaman dan keterampilan yang tercantum di CV"

    if focuses:
        first += f" dengan pengalaman organisasi di bidang {focuses}."
    else:
        first += "."

    second_parts = []
    if tech:
        second_parts.append(f"memiliki dasar teknis dalam {tech}")
    exp_corpus = " ".join(
        " ".join(_normalize_text_list(exp.get("descriptions") or []))
        for exp in cv_data.get("experience", []) or []
    ).lower()
    org_capabilities: list[str] = []
    if any(term in exp_corpus for term in ["budget", "expense", "financial", "fund allocation"]):
        org_capabilities.append("mengelola anggaran")
    if any(term in exp_corpus for term in ["coordinated", "coordination", "execution", "delegated"]):
        org_capabilities.append("koordinasi tim")
    if "stakeholder" in exp_corpus or "communication" in exp_corpus:
        org_capabilities.append("komunikasi stakeholder")
    if org_capabilities:
        second_parts.append(f"pengalaman {_format_list(org_capabilities)}")

    if second_parts:
        return first + " Ia " + ", serta ".join(second_parts) + "."
    return first


def _build_grounded_strengths(cv_data: dict) -> list[str]:
    tech = _format_list(_ordered_technical_skills(cv_data))
    soft = (cv_data.get("skills") or {}).get("soft_skills", []) or []
    soft_focus = [skill for skill in ["Communication", "Leadership", "Planning", "Time Management"] if skill in soft]

    strengths = [
        "Memiliki pengalaman organisasi yang kuat dalam pengelolaan anggaran, koordinasi acara, dan kerja tim.",
    ]
    if tech:
        strengths.append(
            f"Memiliki dasar teknis yang relevan dengan rekomendasi role teratas, seperti {tech}."
        )
    if soft_focus:
        strengths.append(
            f"Menunjukkan kemampuan {_format_list([s.lower() for s in soft_focus])} melalui berbagai peran kepanitiaan dan organisasi."
        )
    return strengths[:3]


def _build_grounded_improvements(cv_data: dict, recommendations: list[dict] | None = None) -> list[str]:
    improvements: list[str] = []
    seen = set()

    def add_suggestion(text: str) -> None:
        if not text:
            return

        clean = text.strip()
        key = clean.lower()

        if key not in seen:
            improvements.append(clean)
            seen.add(key)

    # Prioritaskan missing skills dari rekomendasi role teratas
    for rec in (recommendations or [])[:5]:
        role = rec.get("role") or "role yang direkomendasikan"

        for skill in rec.get("missing_skills", []) or []:
            add_suggestion(
                f"Pelajari {skill} untuk meningkatkan kecocokan dengan role {role}."
            )

            if len(improvements) >= 4:
                return improvements[:4]

    # Jika rekomendasi punya improvement_suggestions
    for rec in (recommendations or [])[:5]:
        for suggestion in rec.get("improvement_suggestions", []) or []:
            add_suggestion(suggestion)

            if len(improvements) >= 4:
                return improvements[:4]

    # Saran kelengkapan CV 
    contact = cv_data.get("contact") or {}

    if not (contact.get("linkedin") or contact.get("github") or contact.get("portfolio")):
        add_suggestion(
            "Tambahkan LinkedIn, GitHub, atau portfolio agar pengalaman dan hasil project lebih mudah dinilai."
        )

    if not cv_data.get("projects"):
        add_suggestion(
            "Tambahkan project yang relevan dengan role pekerjaan yang ingin dituju, lengkap dengan teknologi yang digunakan dan hasil yang dicapai."
        )

    if not cv_data.get("certifications"):
        add_suggestion(
            "Tambahkan course atau certification yang relevan dengan role pekerjaan yang direkomendasikan jika tersedia."
        )

    add_suggestion(
        "Perjelas deskripsi pengalaman dan project dengan peran, tools, teknologi, serta impact yang terukur."
    )

    return improvements[:4]


_UNSUPPORTED_CLAIMS_RE = re.compile(
    r"\b(?:ahli|spesialis|spesial|inovatif|unggul|berkualitas|mendalam|expert)\b",
    re.IGNORECASE,
)

_UNNATURAL_PHRASES_RE = re.compile(
    r"(pengetahuan teks|pemrograman berkualitas|keadaan yang baik|hr proses|"
    r"recruitment|payroll|performance management|jangan malu|biaya organisasi|"
    r"progresivitas|berita pribadi|pengetahuan khusus|proyek dan penelitian|"
    r"keberanian untuk menyelesaikan tantangan|C\+\+,\s*C\+\+|"
    r"kedudukan dan kontrol akhir|festival kesehatan|pameran akademi|"
    r"proyek-acara|menguasai bidang|memelihara keberhasilan|"
    r"membuktikan kemampuannya|bidang administrasi|cocok untuk peran|"
    r"bidang STEM|organisasi pendidikan|content writer|diagnosa|"
    r"memberi tahu evaluasi)",
    re.IGNORECASE,
)


def _neutralize_text(text: str) -> str:
    replacements = {
        r"\bspesialis\b": "memiliki dasar",
        r"\bspesial\b": "relevan",
        r"\bahli\b": "memiliki dasar",
        r"\binovatif\b": "terstruktur",
        r"\bunggul\b": "baik",
        r"\bberkualitas\b": "relevan",
        r"pengetahuan teks": "dasar teknis",
        r"pemrograman berkualitas": "dasar pemrograman",
        r"Keadaan yang baik": "Kemampuan yang baik",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _has_bad_ai_language(text: str) -> bool:
    return bool(_UNSUPPORTED_CLAIMS_RE.search(text) or _UNNATURAL_PHRASES_RE.search(text))


def _sanitize_ai_summary(
    ai_summary: dict,
    cv_data: dict,
    recommendations: list[dict] | None = None,
) -> dict:
    raw_name: str = (cv_data.get("contact") or {}).get("name") or ""
    display_name = _display_name(raw_name)
    summary_text: str = ai_summary.get("profile_summary") or ""
    summary_text = re.sub(r"\s+", " ", summary_text).strip()
    summary_had_bad_language = _has_bad_ai_language(summary_text)
    summary_text = summary_text.replace(raw_name, display_name) if raw_name else summary_text

    institution = _education_institution(cv_data)
    first_name = display_name.split()[0] if display_name else ""
    if institution and first_name and "gadjah mada" in institution.lower():
        summary_text = re.sub(
            rf"\b{re.escape(first_name)}\s+Gadjah\s+Mada\b",
            institution,
            summary_text,
            flags=re.IGNORECASE,
        )

    sentences = re.split(r"(?<=[.!?])\s+", summary_text)
    cleaned_sentences: list[str] = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if re.search(
            r"\b(?:pengalaman\s+\d+\s+tahun|\d+\s+tahun\s+pengalaman|berpengalaman\s+\d+\s+tahun)\b",
            sentence,
            re.IGNORECASE,
        ):
            continue
        sentence = re.sub(r"\bSaya\s+", f"{display_name} ", sentence, flags=re.IGNORECASE)
        sentence = re.sub(r"\b(saya|aku|kami|kita)\b", display_name, sentence, flags=re.IGNORECASE)
        sentence = _neutralize_text(sentence)
        cleaned_sentences.append(sentence)

    summary_text = " ".join(cleaned_sentences[:3]).strip()
    if summary_had_bad_language or _has_bad_ai_language(summary_text):
        summary_text = _build_grounded_profile_summary(cv_data)

    if raw_name and raw_name.lower() not in summary_text.lower() and display_name.lower() not in summary_text.lower():
        summary_text = f"{display_name} {summary_text[:1].lower()}{summary_text[1:]}" if summary_text else display_name

    if not summary_text or summary_text == display_name:
        summary_text = _build_grounded_profile_summary(cv_data)

    ai_summary["profile_summary"] = summary_text

    raw_strengths = [item.strip() for item in (ai_summary.get("strengths") or []) if item and item.strip()]
    strengths_had_bad_language = any(_has_bad_ai_language(item) for item in raw_strengths)
    strengths = [_neutralize_text(item) for item in raw_strengths]
    if (
        len(strengths) != 3
        or strengths_had_bad_language
        or any(_has_bad_ai_language(item) or ":" in item for item in strengths)
    ):
        strengths = _build_grounded_strengths(cv_data)
    ai_summary["strengths"] = strengths[:3]

    raw_improvements = [
        item.strip()
        for item in (ai_summary.get("areas_for_improvement") or [])
        if item and item.strip()
    ]
    improvements_had_bad_language = any(_has_bad_ai_language(item) for item in raw_improvements)
    improvements = [_neutralize_text(item) for item in raw_improvements]
    irrelevant_improvement = re.compile(
        r"\b(?:hr process|hr proses|recruitment|payroll|performance management|"
        r"interpersonal skills|microsoft office)\b",
        re.IGNORECASE,
    )
    if (
        len(improvements) > 4
        or improvements_had_bad_language
        or any(
            _has_bad_ai_language(item)
            or irrelevant_improvement.search(item)
            or ":" in item
            or re.search(r"\bAnda\b", item)
            for item in improvements
        )
        or not improvements
    ):
        improvements = _build_grounded_improvements(cv_data, recommendations)
    ai_summary["areas_for_improvement"] = improvements[:4]
    return ai_summary

def process_cv(
    file_path: str,
    use_ollama: bool = False
) -> Dict[str, Any]:
    # Parse CV File
    parse_result = parse_cv_file(file_path)
    raw_text = parse_result.get("raw_text", "")
    metadata = {
        "file_type": parse_result.get("file_type", ""),
        "extraction_method": parse_result.get("extraction_method", ""),
        "extraction_quality": parse_result.get("extraction_quality", ""),
        "total_pages": parse_result.get("total_pages", 0)
    }

    # Extract Data
    sections = split_sections(raw_text)
    
    contact = extract_contact(sections.get("header", []))
    education = extract_education(sections.get("education", []))
    experience = extract_experience(sections.get("experience", []))
    projects = extract_projects(sections.get("projects", []))
    certifications = extract_certifications(sections.get("certifications", []))
    
    # Skills need skills section lines, and we can pass raw text for context
    skills = extract_skills(sections.get("skills", []), full_text=raw_text)
    
    # Check for mixed sections that might contain skills or projects
    for sec_name, sec_lines in sections.items():
        if sec_name.startswith("mixed_"):
            split_mixed = split_mixed_section(sec_lines)
            mixed_skills = extract_skills(split_mixed.get("skills", []), full_text="")
            for k, v in mixed_skills.items():
                skills[k] = sorted(list(set(skills.get(k, []) + v)))
                
            mixed_projects = extract_projects(split_mixed.get("projects", []))
            if mixed_projects:
                projects.extend(mixed_projects)
                
            mixed_certs = extract_certifications(split_mixed.get("achievements", []))
            if mixed_certs:
                certifications.extend(mixed_certs)

            mixed_exp = extract_experience(split_mixed.get("experience", []))
            if mixed_exp:
                experience.extend(mixed_exp)

    experience = _filter_experience_entries(experience)

    cv_data = {
        "contact": contact,
        "education": education,
        "experience": experience,
        "skills": skills,
        "projects": projects,
        "certifications": certifications
    }

    _log_parsing_validation(cv_data)

    # Recommend Jobs
    job_recommendations = recommend_jobs(cv_data)

    # Score CV
    scores = score_cv(cv_data, recommendations=job_recommendations)

    # AI Summary (Ollama or Fallback)
    ai_summary: dict = {}
    if use_ollama:
        ollama = OllamaClient()
        if ollama.is_available():
            summary_prompt = build_profile_summary_prompt(cv_data, scores)
            strengths_prompt = build_strengths_prompt(cv_data, scores)
            improv_prompt = build_improvement_prompt(cv_data, scores, job_recommendations)

            profile_summary = ollama.generate_profile_summary(summary_prompt)
            strengths      = ollama.generate_strengths(strengths_prompt)
            improvements   = ollama.generate_improvements(improv_prompt)

            # Fall back per-field if Ollama returned nothing useful
            fallback = _generate_fallback_summary(scores, job_recommendations, cv_data)
            ai_summary = {
                "profile_summary": profile_summary or fallback["profile_summary"],
                "strengths": strengths or fallback["strengths"],
                "areas_for_improvement": improvements or fallback["areas_for_improvement"],
            }
        else:
            ai_summary = _generate_fallback_summary(scores, job_recommendations, cv_data)
    else:
        ai_summary = _generate_fallback_summary(scores, job_recommendations, cv_data)

    # Final validation & cleanup
    ai_summary = _sanitize_ai_summary(ai_summary, cv_data, job_recommendations)

    return {
        "cv_data": cv_data,
        "scores": scores,
        "job_recommendations": job_recommendations,
        "ai_summary": ai_summary,
        "metadata": metadata
    }

def main():
    parser = argparse.ArgumentParser(description="Porfio AI Services - CV Analyzer")
    parser.add_argument("--input", required=True, help="Path to input CV file (PDF, DOCX, Image)")
    parser.add_argument("--output", help="Path to output JSON file (optional)")
    
    ollama_group = parser.add_mutually_exclusive_group()
    ollama_group.add_argument("--use-ollama", action="store_true", help="Use Ollama for AI Summary")
    ollama_group.add_argument("--no-ollama", action="store_true", help="Disable Ollama (use fallback)")
    
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    
    # Default to not using Ollama unless explicitly requested
    use_ollama = True # Hardcode true

    try:
        result = process_cv(input_path, use_ollama=use_ollama)
        
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"Result successfully saved to {output_path}")
        else:
            print(json_output)
            
    except Exception as e:
        print(f"Error processing CV: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
