# Ini template prompt buat Ollama (pakai B Indo yes)

from __future__ import annotations


def build_profile_summary_prompt(cv_data: dict, scores: dict) -> str:
    contact = cv_data.get("contact", {})
    name = contact.get("name") or "Kandidat"

    skills_flat: list[str] = []
    for cat in ("technical_skills", "soft_skills", "tools"):
        skills_flat.extend(cv_data.get("skills", {}).get(cat, [])[:5])

    exp_count = len(cv_data.get("experience", []))
    edu = cv_data.get("education", [{}])[0] if cv_data.get("education") else {}
    degree = edu.get("degree") or "tidak disebutkan"
    field = edu.get("field") or ""
    institution = edu.get("institution") or "tidak disebutkan"
    overall = scores.get("overall_score", 0)

    skills_str = ", ".join(skills_flat) or "tidak terdeteksi"

    prompt = (
        f"Kamu adalah asisten profesional analisis CV. "
        f"Buatkan ringkasan profil singkat (2-3 kalimat) dalam Bahasa Indonesia "
        f"yang profesional untuk kandidat berikut:\n\n"
        f"Nama: {name}\n"
        f"Pendidikan: {degree} {field} dari {institution}\n"
        f"Pengalaman kerja: {exp_count} entri\n"
        f"Skill utama: {skills_str}\n"
        f"Skor CV: {overall}/100\n\n"
        f"Tulis ringkasan yang menarik dan jujur. Jangan tambahkan informasi yang tidak ada."
    )
    return prompt

# 3 User's strengths
def build_strengths_prompt(cv_data: dict, scores: dict) -> str:
    skills_flat: list[str] = []
    for cat in ("technical_skills", "tools"):
        skills_flat.extend(cv_data.get("skills", {}).get(cat, [])[:6])

    proj_count = len(cv_data.get("projects", []))
    exp_count = len(cv_data.get("experience", []))
    skill_score = scores.get("skill_score", 0)
    project_score = scores.get("project_score", 0)
    skills_str = ", ".join(skills_flat) or "tidak terdeteksi"

    prompt = (
        f"Kamu adalah asisten profesional analisis CV. "
        f"Sebutkan 3 kekuatan utama kandidat ini dalam bentuk poin-poin singkat "
        f"(gunakan Bahasa Indonesia):\n\n"
        f"Skill terdeteksi: {skills_str}\n"
        f"Jumlah pengalaman kerja: {exp_count}\n"
        f"Jumlah proyek: {proj_count}\n"
        f"Skill score: {skill_score}/100\n"
        f"Project score: {project_score}/100\n\n"
        f"Format: daftar poin, setiap poin maksimal 1 kalimat. Jangan bertele-tele."
    )
    return prompt

# Suggest for user about their CV or missing skills
def build_improvement_prompt(cv_data: dict, scores: dict, recommendations: list[dict]) -> str:
    missing_skills: list[str] = []
    for rec in recommendations[:3]:
        missing_skills.extend(rec.get("missing_skills", [])[:2])
    missing_str = ", ".join(set(missing_skills[:6])) or "tidak ada"

    comp_score = scores.get("completeness_score", 0)
    exp_score = scores.get("experience_score", 0)

    prompt = (
        f"Kamu adalah asisten profesional analisis CV. "
        f"Berikan 3 saran perbaikan yang konkret dan actionable untuk kandidat ini "
        f"(gunakan Bahasa Indonesia):\n\n"
        f"Skor kelengkapan CV: {comp_score}/100\n"
        f"Skor pengalaman: {exp_score}/100\n"
        f"Skill yang belum dimiliki untuk role yang direkomendasikan: {missing_str}\n\n"
        f"Format: daftar poin, setiap poin maksimal 1-2 kalimat. Fokus pada hal yang bisa dilakukan segera."
    )
    return prompt

# Why candidate match for the role
def build_role_reason_prompt(
    role_name: str,
    matched_skills: list[str],
    missing_skills: list[str],
    match_score: float,
) -> str:
    matched_str = ", ".join(matched_skills[:5]) or "tidak ada"
    missing_str = ", ".join(missing_skills[:3]) or "tidak ada"

    prompt = (
        f"Kamu adalah asisten profesional analisis CV. "
        f"Jelaskan dalam 2-3 kalimat mengapa kandidat ini cocok (atau tidak cocok) "
        f"untuk posisi {role_name} (gunakan Bahasa Indonesia):\n\n"
        f"Match score: {match_score}/100\n"
        f"Skill yang dimiliki dan relevan: {matched_str}\n"
        f"Skill yang belum dimiliki: {missing_str}\n\n"
        f"Jangan lebih dari 3 kalimat. Bersikaplah jujur dan konstruktif."
    )
    return prompt
