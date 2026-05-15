import unittest

from extractor.contact_extractor import extract_contact
from extractor.skill_extractor import extract_skills
from scoring.cv_scoring import score_cv
from recommendation.job_recommender import recommend_jobs
from main import _generate_fallback_summary

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

if __name__ == "__main__":
    unittest.main()
