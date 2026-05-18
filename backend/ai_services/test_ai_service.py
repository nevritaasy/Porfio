import unittest
import json

from extractor.contact_extractor import extract_contact
from extractor.skill_extractor import extract_skills
from extractor.experience_extractor import extract_experience
from extractor.certification_extractor import extract_certifications
from scoring.cv_scoring import score_cv
from recommendation.job_recommender import recommend_jobs
from main import _generate_fallback_summary, _sanitize_ai_summary

class TestAIServices(unittest.TestCase):

    def test_contact_extraction(self):
        header_lines = [
            "John Doe",
            "johndoe@email.com",
            "+6281234567890",
            "linkedin.com/in/johndoe",
            "github.com/johndoe"
        ]
        result = extract_contact(header_lines)
        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["email"], "johndoe@email.com")
        self.assertEqual(result["phone"], "+6281234567890")
        self.assertTrue(result["linkedin"] is not None)
        self.assertTrue(result["github"] is not None)

    def test_skill_extraction(self):
        section_lines = [
            "I have experience with Python, JavaScript, and React.",
            "I also use SQL for database management and Git for version control."
        ]
        result = extract_skills(section_lines)
        
        self.assertIn("Python", result.get("technical_skills", []))
        self.assertIn("JavaScript", result.get("technical_skills", []))
        self.assertIn("React", result.get("technical_skills", []))
        self.assertIn("SQL", result.get("technical_skills", []))
        self.assertIn("Git", result.get("tools", []))

    def test_scoring_and_recommendation(self):
        # Dummy CV Data
        cv_data = {
            "contact": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "123456789",
                "linkedin": "linkedin.com/in/jane",
                "github": "github.com/jane"
            },
            "education": [
                {
                    "institution": "University of Technology",
                    "degree": "Bachelor",
                    "field": "Computer Science",
                    "date_range": {"start": "2018-09-01", "end": "2022-06-01"},
                    "gpa": "3.8"
                }
            ],
            "experience": [
                {
                    "company": "Tech Corp",
                    "role": "Frontend Developer",
                    "date_range": {"start": "2022-07-01", "end": "Present"},
                    "descriptions": [
                        "Developed web applications using React and TypeScript.",
                        "Collaborated with UI/UX designers using Figma."
                    ]
                }
            ],
            "skills": {
                "technical_skills": ["HTML", "CSS", "JavaScript", "React", "TypeScript"],
                "soft_skills": ["Communication", "Teamwork"],
                "tools": ["Git", "Figma"],
                "languages": ["English"]
            },
            "projects": [
                {
                    "name": "Personal Portfolio",
                    "year": "2023",
                    "date_range": {"start": "2023", "end": None},
                    "description": "Built a portfolio using Next.js and Tailwind CSS.",
                    "related_skills": ["Next.js", "Tailwind CSS"]
                }
            ]
        }

        # Test Scoring
        scores = score_cv(cv_data)
        self.assertIn("overall_score", scores)
        self.assertIn("skill_score", scores)
        self.assertIn("experience_score", scores)
        self.assertTrue(scores["overall_score"] > 0)

        # Test Recommendation
        recs = recommend_jobs(cv_data)
        self.assertTrue(len(recs) > 0)
        top_rec = recs[0]
        self.assertIn("role", top_rec)
        self.assertIn("match_score", top_rec)
        self.assertEqual(top_rec["role"], "Frontend Developer")

        # Test Fallback Summary output structure
        summary = _generate_fallback_summary(scores, recs)
        self.assertIn("profile_summary", summary)
        self.assertIn("strengths", summary)
        self.assertIn("areas_for_improvement", summary)
        
        # Test final structure conceptually
        final_output = {
             "cv_data": cv_data,
             "scores": scores,
             "job_recommendations": recs,
             "ai_summary": summary,
             "metadata": {"file_type": "pdf", "extraction_method": "native", "extraction_quality": "good", "total_pages": 1}
        }
        self.assertIn("cv_data", final_output)
        self.assertIn("scores", final_output)
        self.assertIn("job_recommendations", final_output)
        self.assertIn("ai_summary", final_output)
        self.assertIn("metadata", final_output)
        
    def test_gpa_extraction(self):
        from extractor.education_extractor import _parse_education_block
        
        block1 = "Universitas Gadjah Mada\nInformation Engineering, Faculty of Engineering, 3.31/4.00"
        res1 = _parse_education_block(block1)
        self.assertEqual(res1["gpa"], "3.31/4.00")
        
        block2 = "ITB\nTeknik Informatika\nIPK: 3,31/4,00"
        res2 = _parse_education_block(block2)
        self.assertEqual(res2["gpa"], "3.31/4.00")
        
    def test_parsing_quality_score(self):
        cv_data_bad = {
             "experience": [
                 {"company": "My Project", "descriptions": ["Hard skills: Python"]}
             ]
        }
        scores = score_cv(cv_data_bad)
        self.assertTrue(scores["parsing_quality_score"] < 100)
        
    def test_skill_normalization(self):
        section_lines = [
            "I use GitHub for version control.",
            "I have experience in PostgreSQL."
        ]
        result = extract_skills(section_lines)
        self.assertIn("Git", result.get("tools", []))
        self.assertIn("SQL", result.get("technical_skills", []))

    def test_experience_stops_before_course_and_skills(self):
        section_lines = [
            "Example Organization - Jakarta Jan 2024 - Present",
            "Event Coordinator",
            "Coordinated event program design and execution",
            "Course (2025): Web Development Fundamentals",
            "Soft Skills: Leadership Teamwork",
            "Hard Skills: Python, JavaScript",
        ]
        experience = extract_experience(section_lines)
        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["company"], "Example Organization")
        combined = " ".join([experience[0].get("role") or ""] + experience[0].get("descriptions", []))
        self.assertNotIn("Course", combined)
        self.assertNotIn("Soft Skills", combined)
        self.assertNotIn("Hard Skills", combined)

        certifications = extract_certifications(["Course (2025): Web Development Fundamentals"])
        self.assertEqual(certifications[0]["name"], "Web Development Fundamentals")

    def test_ai_summary_sanitizer_removes_first_person_and_unsupported_years(self):
        cv_data = {
            "contact": {"name": "SAMPLE CANDIDATE"},
            "education": [
                {
                    "institution": "Sample University - City",
                    "degree": "Bachelor",
                    "field": "Information Systems",
                }
            ],
        }
        ai_summary = {
            "profile_summary": (
                "SAMPLE CANDIDATE adalah mahasiswa dari Sample Candidate University. "
                "Saya memiliki pengalaman 5 tahun dan menguasai Python."
            ),
            "strengths": [],
            "areas_for_improvement": [],
        }
        result = _sanitize_ai_summary(ai_summary, cv_data)
        summary = result["profile_summary"]
        self.assertNotIn("Saya", summary)
        self.assertNotIn("5 tahun", summary)

    def test_ai_summary_sanitizer_replaces_ungrounded_candidate_output(self):
        cv_data = {
            "contact": {
                "name": "SAMPLE CANDIDATE",
                "linkedin": None,
                "github": None,
                "portfolio": None,
            },
            "education": [
                {
                    "institution": "Sample University - City",
                    "degree": "Bachelor",
                    "field": "Information Systems",
                }
            ],
            "experience": [
                {
                    "company": "Student Association",
                    "role": "Treasurer",
                    "descriptions": [
                        "Managed budget planning, expense tracking, and financial reporting",
                        "Coordinated fund allocation for events and activities",
                        "Collaborated with members and leaders to ensure program success",
                    ],
                },
                {
                    "company": "Campus Event",
                    "role": "Event Chair",
                    "descriptions": [
                        "Led planning, coordination, and execution of the event",
                        "Oversaw budgeting, logistics, and stakeholder communication",
                    ],
                },
            ],
            "skills": {
                "technical_skills": ["Python", "SQL", "JavaScript"],
                "soft_skills": ["Communication", "Leadership", "Planning", "Time Management"],
            },
            "projects": [],
            "certifications": [{"name": "Web Development Fundamentals"}],
        }

        ai_summary = {
            "profile_summary": (
                "SAMPLE CANDIDATE memiliki keterampilan spesialis dan bekerja secara inovatif."
            ),
            "strengths": [
                "Kemampuan dalam pemrograman berkualitas dengan pengetahuan teks.",
                "Keadaan yang baik dalam menerima tantangan.",
            ],
            "areas_for_improvement": [
                "Pelajari dan praktikkan pengetahuan Anda tentang HR proses.",
                "Menjadi ahli dalam Microsoft Excel sangat penting.",
            ],
        }

        recommendations = [
            {"role": "Frontend Developer", "category": "Software Engineering", "missing_skills": ["React"]},
            {"role": "Backend Developer", "category": "Software Engineering", "missing_skills": ["REST API"]},
            {"role": "Data Analyst", "category": "Data & Analytics", "missing_skills": ["SQL", "Data Visualization"]},
        ]

        result = _sanitize_ai_summary(ai_summary, cv_data, recommendations)

        self.assertNotIn("spesialis", result["profile_summary"].lower())
        self.assertNotIn("inovatif", result["profile_summary"].lower())
        self.assertNotIn("pengetahuan teks", " ".join(result["strengths"]).lower())
        self.assertNotIn("hr proses", " ".join(result["areas_for_improvement"]).lower())
        self.assertNotIn("biomedical", json.dumps(result).lower())
        self.assertLessEqual(len(result["areas_for_improvement"]), 4)
        
if __name__ == "__main__":
    unittest.main()
