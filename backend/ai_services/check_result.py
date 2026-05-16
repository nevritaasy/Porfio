import json

with open("result.json", encoding="utf-8") as f:
    r = json.load(f)

s = r["scores"]
print("=== SCORES ===")
print("  overall_score:         ", s["overall_score"])
print("  skill_score:           ", s["skill_score"])
print("  experience_score:      ", s["experience_score"])
print("  project_score:         ", s["project_score"])
print("  completeness_score:    ", s["completeness_score"])
print("  parsing_quality_score: ", s["parsing_quality_score"])

print()
print("=== EXPERIENCE (" + str(len(r["cv_data"]["experience"])) + " entries) ===")
for e in r["cv_data"]["experience"]:
    print("  [" + str(e.get("company","")) + "] - " + str(e.get("role","")))
    for d in e.get("descriptions", [])[:1]:
        print("    > " + d[:100])

print()
print("=== PROJECTS (" + str(len(r["cv_data"]["projects"])) + " entries) ===")
for p in r["cv_data"]["projects"]:
    print("  " + str(p.get("name","")))

print()
ai = r["ai_summary"]
print("=== AI SUMMARY ===")
print("profile_summary:", ai["profile_summary"][:200])
print()
print("strengths:")
for item in ai["strengths"]:
    print("  - " + item[:120])
print()
print("areas_for_improvement:")
for item in ai["areas_for_improvement"]:
    print("  - " + item[:120])
