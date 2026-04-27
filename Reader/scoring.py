def calculate_score(cv):
    skills = cv.get("skills", [])
    experience = cv.get("experience", [])
    education = cv.get("education", [])

    # Skill score: 40 points max, 1.5 points per skill
    skill_score = min(len(skills) * 1.5, 40)

   # Experience score: 30 points max, 3 points per year of experience
    exp_score = min(len(experience) * 3, 30)

    # Education score: 20 points max, 10 points for having education, +5 for degree, +5 for GPA
    edu_score = 0
    if education:
        edu_score = 10

        if any(e.get("degree") for e in education):
            edu_score += 5

        if any(e.get("gpa") for e in education):
            edu_score += 5

    edu_score = min(edu_score, 20)

    # Education completeness: 10 points max, 2 points for email, 2 points for phone, 3 points for experience, 3 points for education
    completeness = 0

    if cv.get("contact", {}).get("email"):
        completeness += 2
    if cv.get("contact", {}).get("phone"):
        completeness += 2
    if cv.get("experience"):
        completeness += 3
    if cv.get("education"):
        completeness += 3

    completeness = min(completeness, 10)

    total = skill_score + exp_score + edu_score + completeness

    return round(min(total, 100), 1)