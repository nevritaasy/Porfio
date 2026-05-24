# Prompt templates

from __future__ import annotations

import json


def _display_name(name: str) -> str:
    return name.title() if name and name.isupper() else name


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


def _compact_experience(exp_entries: list[dict]) -> list[dict]:
    compact: list[dict] = []
    for exp in exp_entries[:5]:
        compact.append({
            "company": exp.get("company"),
            "role": exp.get("role"),
            "date_range": exp.get("date_range"),
            "descriptions": exp.get("descriptions", [])[:4],
        })
    return compact


def _relevant_recommendations(recommendations: list[dict]) -> list[dict]:
    relevant_categories = {"Data & Analytics", "Product & Business", "Engineering & Technology"}
    relevant: list[dict] = []
    for rec in recommendations:
        if rec.get("category") in relevant_categories or rec.get("match_score", 0) >= 40:
            relevant.append({
                "role": rec.get("role"),
                "category": rec.get("category"),
                "match_score": rec.get("match_score"),
                "matched_skills": rec.get("matched_skills", [])[:5],
                "missing_skills": rec.get("missing_skills", [])[:5],
            })
    return relevant[:4]


def build_profile_summary_prompt(cv_data: dict, scores: dict) -> str:
    contact = cv_data.get("contact", {})
    name = _display_name(contact.get("name") or "Kandidat")

    edu_list = cv_data.get("education", [])
    edu = edu_list[0] if edu_list else {}
    degree = edu.get("degree") or ""
    field  = edu.get("field")  or ""
    institution = edu.get("institution") or ""
    institution = institution.split(" - ")[0].strip()

    exp_entries = cv_data.get("experience", [])

    tech_skills = _normalize_text_list(cv_data.get("skills", {}).get("technical_skills", []))[:5]
    soft_skills = _normalize_text_list(cv_data.get("skills", {}).get("soft_skills", []))[:6]
    tools = _normalize_text_list(cv_data.get("skills", {}).get("tools", []))[:4]
    skills_str  = ", ".join(tech_skills + tools) or "tidak terdeteksi"
    certs = [c.get("name") for c in cv_data.get("certifications", [])[:3] if c.get("name")]
    experience_json = json.dumps(_compact_experience(exp_entries), ensure_ascii=False)

    prompt = (
        f"Kamu adalah penulis ringkasan CV yang faktual dan ringkas.\n\n"
        f"FAKTA CV YANG BOLEH DIGUNAKAN:\n"
        f"- Nama kandidat: {name}\n"
        f"- Degree: {degree or '-'}\n"
        f"- Bidang studi: {field or '-'}\n"
        f"- Institusi pendidikan, gunakan persis jika disebut: {institution or '-'}\n"
        f"- Keahlian utama yang terdeteksi: {skills_str}\n\n"
        f"- Soft skills terdeteksi: {', '.join(soft_skills) or '-'}\n"
        f"- Course/certification: {', '.join(certs) or '-'}\n"
        f"- Experience detail JSON: {experience_json}\n\n"
        f"INSTRUKSI:\n"
        f"1. Tulis profile_summary dalam Bahasa Indonesia natural dan profesional, maksimal 2-3 kalimat.\n"
        f"2. JANGAN menggunakan format daftar (list), poin-poin (bullet points), atau format biodata.\n"
        f"3. Gunakan sudut pandang orang ketiga: nama kandidat, 'ia', atau 'kandidat'. JANGAN memakai kata 'Saya', 'aku', 'kami', atau 'kita'.\n"
        f"4. JANGAN menyebut jumlah tahun pengalaman kecuali durasinya dihitung jelas dari date_range; jika ragu, jangan sebut angka tahun.\n"
        f"5. JANGAN menambah informasi yang tidak ada di fakta CV di atas.\n"
        f"6. JANGAN menyebutkan skor CV, angka metrik yang tidak ada di data, atau kalimat pembuka.\n"
        f"7. Gunakan nama universitas dari field 'Institusi pendidikan' secara persis, jangan membuat frasa baru seperti menggabungkan nama kandidat dengan universitas.\n"
        f"8. JANGAN gunakan ejaan nama yang berbeda dari '{name}', dan jangan menulis nama kandidat dengan huruf kapital semua kecuali data aslinya memang diminta apa adanya.\n"
        f"9. Hindari kata promosi berlebihan seperti 'inovatif', 'spesialis', 'ahli', 'unggul', atau 'berkualitas' kecuali ada bukti eksplisit di CV.\n"
        f"10. Setiap klaim pengalaman harus dapat ditunjuk ke role/descriptions di Experience detail JSON.\n"
        f"11. DILARANG menyebut nama, bidang studi, skill, tools, project, institusi, atau pengalaman yang tidak muncul pada data CV.\n"
        f"12. DILARANG menggunakan contoh kandidat tertentu sebagai referensi output.\n"
        f"13. Jangan menyebut domain spesifik seperti biomedical, finance, HR, marketing, software engineering, data, AI, atau bidang lain kecuali domain tersebut memang muncul dari field education, skills, projects, experience, atau rekomendasi role.\n"
        f"14. Jika bidang studi atau skill pengguna tidak cukup jelas, gunakan frasa netral seperti 'bidang yang relevan dengan profil kandidat' atau 'area karier yang sesuai dengan pengalaman dan keahlian kandidat'.\n"
    )
    return prompt


def build_strengths_prompt(cv_data: dict, scores: dict) -> str:
    contact = cv_data.get("contact", {})
    name = _display_name(contact.get("name") or "Kandidat")

    tech_skills = _normalize_text_list(cv_data.get("skills", {}).get("technical_skills", []))[:6]
    soft_skills = _normalize_text_list(cv_data.get("skills", {}).get("soft_skills", []))[:4]
    tools = _normalize_text_list(cv_data.get("skills", {}).get("tools", []))[:4]
    proj_names = _normalize_text_list([p.get("name") for p in cv_data.get("projects", [])[:3]])
    exp_roles = _normalize_text_list([e.get("role") for e in cv_data.get("experience", [])[:3]])

    tech_str  = ", ".join(tech_skills) or "tidak ada"
    soft_str  = ", ".join(soft_skills) or "tidak ada"
    tools_str = ", ".join(tools) or "tidak ada"
    proj_str  = ", ".join(proj_names) or "tidak ada"
    exp_str   = ", ".join(exp_roles) or "tidak ada"

    exp_details = json.dumps(_compact_experience(cv_data.get("experience", [])), ensure_ascii=False)

    prompt = (
        f"Kamu adalah penulis evaluasi CV yang faktual dan menggunakan Bahasa Indonesia profesional.\n\n"
        f"DATA KANDIDAT '{name}':\n"
        f"- Keahlian Teknis: {tech_str}\n"
        f"- Soft Skills: {soft_str}\n"
        f"- Tools/Platform: {tools_str}\n"
        f"- Proyek yang Dikerjakan: {proj_str}\n"
        f"- Pengalaman/Role: {exp_str}\n\n"
        f"- Detail Experience JSON: {exp_details}\n\n"
        f"INSTRUKSI:\n"
        f"1. Tuliskan maksimal 3 strengths utama kandidat berdasarkan data di atas.\n"
        f"2. Setiap poin harus berupa 1 kalimat natural, konkret, dan profesional.\n"
        f"3. JANGAN memulai dengan kalimat pengantar (misalnya 'Berikut adalah...').\n"
        f"4. JANGAN gunakan format markdown seperti bintang (**) atau tanda pagar (##).\n"
        f"5. JANGAN memakai frasa aneh seperti 'pengetahuan teks', 'pemrograman berkualitas', atau 'keadaan yang baik'.\n"
        f"6. JANGAN mengarang skill atau proyek yang tidak ada di data.\n"
        f"7. Hindari kata promosi berlebihan seperti 'inovatif', 'spesialis', 'ahli', 'unggul', atau 'berkualitas' kecuali ada bukti eksplisit di data.\n"
        f"8. DILARANG menyebut domain, bidang, skill, tools, atau project yang tidak muncul pada data kandidat.\n"
        f"9. Strengths harus diturunkan dari kombinasi data berikut: keahlian teknis, soft skills, tools, project, experience, dan role yang pernah dijalankan.\n"
        f"10. Jika data kandidat lebih kuat di organisasi, tekankan koordinasi, komunikasi, administrasi, leadership, atau teamwork sesuai data.\n"
        f"11. Jika data kandidat lebih kuat di teknis, tekankan skill teknis, tools, project, atau pengalaman teknis sesuai data.\n"
        f"12. Jangan gunakan contoh kandidat tertentu sebagai pola output.\n"
    )
    return prompt


def build_improvement_prompt(cv_data: dict, scores: dict, recommendations: list[dict]) -> str:
    contact = cv_data.get("contact", {})
    name = _display_name(contact.get("name") or "Kandidat")

    missing_skills: list[str] = []
    top_roles: list[str] = []
    relevant_recs = _relevant_recommendations(recommendations)
    for rec in relevant_recs:
        role = rec.get("role")
        if role is not None:
            top_roles.append(str(role).strip())
        for sk in rec.get("missing_skills", [])[:2]:
            if sk is None:
                continue
            skill = str(sk).strip()
            if skill and skill not in missing_skills:
                missing_skills.append(skill)
    missing_str = ", ".join(missing_skills[:5]) or "tidak ada"
    roles_str   = ", ".join(top_roles[:3]) or "tidak diketahui"

    comp_score = scores.get("completeness_score", 0)
    exp_score  = scores.get("experience_score", 0)
    has_portfolio = bool(cv_data.get("contact", {}).get("portfolio"))
    proj_count = len(cv_data.get("projects", []))
    recs_json = json.dumps(relevant_recs, ensure_ascii=False)
    cert_names = [c.get("name") for c in cv_data.get("certifications", []) if c.get("name")]

    prompt = (
        f"Kamu adalah mentor karier yang memberikan saran perbaikan CV yang membangun.\n\n"
        f"KONDISI KANDIDAT '{name}':\n"
        f"- Punya URL Portfolio di CV: {'Ya' if has_portfolio else 'Belum Ada'}\n"
        f"- Jumlah project terdeteksi: {proj_count}\n"
        f"- Course/certification terdeteksi: {', '.join(cert_names) or '-'}\n"
        f"- Rekomendasi Role Karier Teratas: {roles_str}\n"
        f"- Keahlian (Skill) yang Belum Dimiliki untuk Role Tersebut: {missing_str}\n\n"
        f"- Job recommendations relevan JSON: {recs_json}\n\n"
        f"INSTRUKSI:\n"
        f"1. Berikan maksimal 3-4 saran perbaikan yang konkret agar kandidat lebih siap kerja.\n"
        f"2. Setiap saran harus berupa 1 kalimat langsung menggunakan bahasa Indonesia yang natural, mengalir, dan profesional (jangan gunakan terjemahan kaku).\n"
        f"3. JANGAN merekomendasikan sosial media pribadi (Instagram, Facebook, TikTok).\n"
        f"4. JANGAN mengambil saran dari role dengan match_score rendah atau role yang tidak termasuk rekomendasi teratas.\n"
        f"5. JANGAN mulai dengan kalimat pembuka (langsung tulis sarannya saja).\n"
        f"6. JANGAN gunakan markdown seperti bintang (**) atau tanda pagar (##).\n"
        f"7. Prioritaskan saran berdasarkan missing_skills dari rekomendasi role teratas, kelengkapan portfolio/GitHub/LinkedIn, dokumentasi project, course/certification, dan pengalaman yang relevan dengan role teratas.\n"
        f"8. JANGAN memberi saran HR process, recruitment, payroll, performance management, atau interpersonal skills kecuali role HR adalah rekomendasi paling kuat dan sangat relevan.\n"
        f"9. DILARANG menyebut domain, role, skill, project, atau bidang yang tidak muncul pada CV atau rekomendasi role teratas.\n"
        f"10. Jika tidak ada missing_skills yang jelas, berikan saran umum yang aman seperti memperjelas deskripsi project, menambahkan portfolio, menambahkan sertifikasi relevan, atau memperjelas impact pengalaman.\n"
        f"11. Jangan gunakan contoh kandidat tertentu sebagai pola output.\n"
    )
    return prompt


def build_role_reason_prompt(
    role_name: str,
    matched_skills: list[str],
    missing_skills: list[str],
    match_score: float,
) -> str:
    matched_str = ", ".join(matched_skills[:5]) or "tidak ada"
    missing_str = ", ".join(missing_skills[:3]) or "tidak ada"

    prompt = (
        f"Kamu adalah asisten analisis CV yang objektif.\n\n"
        f"DATA PENCOCOKAN:\n"
        f"- Posisi: {role_name}\n"
        f"- Match score: {match_score}/100\n"
        f"- Skill yang dimiliki dan relevan: {matched_str}\n"
        f"- Skill yang belum dimiliki: {missing_str}\n\n"
        f"INSTRUKSI:\n"
        f"1. Jelaskan dalam 2-3 kalimat mengapa kandidat cocok atau tidak cocok untuk posisi ini.\n"
        f"2. Gunakan Bahasa Indonesia yang profesional.\n"
        f"3. JANGAN mengarang skill atau pengalaman yang tidak ada di data.\n"
        f"4. Bersikaplah jujur dan konstruktif.\n"
    )
    return prompt
