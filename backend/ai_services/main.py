import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from parser import parse_cv_file
from extractor import (
    split_sections,
    extract_contact,
    extract_education,
    extract_experience,
    extract_skills,
    extract_projects,
)
from scoring import score_cv
from recommendation import recommend_jobs
from llm import OllamaClient
from llm.prompt_templates import (
    build_profile_summary_prompt,
    build_strengths_prompt,
    build_improvement_prompt,
)

def _generate_fallback_summary(scores: Dict[str, Any], recommendations: list) -> Dict[str, Any]:
    """Generate a rule-based fallback summary when Ollama is unavailable."""
    summary = "Kandidat memiliki profil yang solid "
    
    overall = scores.get("overall_score", 0)
    if overall >= 80:
        summary += "dengan kualifikasi yang sangat baik secara keseluruhan."
    elif overall >= 60:
        summary += "dengan kualifikasi yang memadai untuk banyak peran."
    else:
        summary += "dengan ruang untuk peningkatan di beberapa area."
        
    strengths = []
    if scores.get("skill_score", 0) >= 70:
        strengths.append("Skill set yang kuat")
    if scores.get("experience_score", 0) >= 70:
        strengths.append("Pengalaman kerja yang relevan")
    if scores.get("project_score", 0) >= 70:
        strengths.append("Portofolio proyek yang baik")
    if not strengths:
        strengths = ["Memiliki potensi untuk berkembang di bidang yang diminati"]

    improvements = []
    if scores.get("completeness_score", 0) < 70:
        improvements.append("Lengkapi informasi CV (kontak, profil, dll)")
    
    missing = set()
    for rec in recommendations[:3]:
        missing.update(rec.get("missing_skills", [])[:2])
    
    if missing:
        improvements.append(f"Pelajari skill berikut: {', '.join(list(missing)[:3])}")
    
    if not improvements:
        improvements = ["Pertahankan dan perdalam skill saat ini"]

    return {
        "profile_summary": summary,
        "strengths": strengths,
        "areas_for_improvement": improvements
    }

def process_cv(
    file_path: str,
    use_ollama: bool = False
) -> Dict[str, Any]:
    """Process a CV file and return the complete AI Services response."""
    
    # 1. Parse CV File
    parse_result = parse_cv_file(file_path)
    raw_text = parse_result.get("raw_text", "")
    metadata = {
        "file_type": parse_result.get("file_type", ""),
        "extraction_method": parse_result.get("extraction_method", ""),
        "extraction_quality": parse_result.get("extraction_quality", ""),
        "total_pages": parse_result.get("total_pages", 0)
    }

    # 2. Extract Data
    sections = split_sections(raw_text)
    
    # Mixed sections handled via project/skill extractors directly or pre-split
    # In section_extractor, we handle mixed sections, but here we can just pass
    # the specific section lines to each extractor.
    
    contact = extract_contact(sections.get("header", []))
    education = extract_education(sections.get("education", []))
    experience = extract_experience(sections.get("experience", []))
    projects = extract_projects(sections.get("projects", []))
    
    # Skills need skills section lines, and we can pass raw text for context
    skills = extract_skills(sections.get("skills", []), full_text=raw_text)
    
    # Check for mixed sections that might contain skills or projects
    for sec_name, sec_lines in sections.items():
        if sec_name.startswith("mixed_"):
            # A simple approach is to run extractors on mixed sections as well
            # and merge results.
            mixed_skills = extract_skills(sec_lines, full_text="")
            for k, v in mixed_skills.items():
                skills[k] = sorted(list(set(skills.get(k, []) + v)))
                
            mixed_projects = extract_projects(sec_lines)
            if mixed_projects:
                projects.extend(mixed_projects)
                
            mixed_exp = extract_experience(sec_lines)
            if mixed_exp:
                experience.extend(mixed_exp)

    cv_data = {
        "contact": contact,
        "education": education,
        "experience": experience,
        "skills": skills,
        "projects": projects,
        "certifications": []  # Handled as projects for now or left empty if not explicitly extracted
    }

    # 3. Score CV
    scores = score_cv(cv_data)

    # 4. Recommend Jobs
    job_recommendations = recommend_jobs(cv_data)

    # 5. AI Summary (Ollama or Fallback)
    ai_summary = {}
    if use_ollama:
        ollama = OllamaClient()
        if ollama.is_available():
            summary_prompt = build_profile_summary_prompt(cv_data, scores)
            strengths_prompt = build_strengths_prompt(cv_data, scores)
            improv_prompt = build_improvement_prompt(cv_data, scores, job_recommendations)

            ai_summary = {
                "profile_summary": ollama.generate_profile_summary(summary_prompt) or "",
                "strengths": ollama.generate_strengths(strengths_prompt) or [],
                "areas_for_improvement": ollama.generate_improvements(improv_prompt) or []
            }
        else:
            ai_summary = _generate_fallback_summary(scores, job_recommendations)
    else:
        ai_summary = _generate_fallback_summary(scores, job_recommendations)
        
    # Ensure no None values in ai_summary
    if not ai_summary.get("profile_summary"):
        fallback = _generate_fallback_summary(scores, job_recommendations)
        ai_summary["profile_summary"] = fallback["profile_summary"]
    if not ai_summary.get("strengths"):
        fallback = _generate_fallback_summary(scores, job_recommendations)
        ai_summary["strengths"] = fallback["strengths"]
    if not ai_summary.get("areas_for_improvement"):
        fallback = _generate_fallback_summary(scores, job_recommendations)
        ai_summary["areas_for_improvement"] = fallback["areas_for_improvement"]

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
    
    # Mutually exclusive group for ollama flag
    ollama_group = parser.add_mutually_exclusive_group()
    ollama_group.add_argument("--use-ollama", action="store_true", help="Use Ollama for AI Summary")
    ollama_group.add_argument("--no-ollama", action="store_true", help="Disable Ollama (use fallback)")
    
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    
    # Default to not using Ollama unless explicitly requested
    use_ollama = args.use_ollama

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
