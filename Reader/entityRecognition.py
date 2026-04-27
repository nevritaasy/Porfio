import argparse
import json
import re
import sys
from pathlib import Path

import dateutil.parser as dateutil_parser

import spacy as sp
from spacy.language import Language
from spacy.schemas import ConfigSchemaNlp

from reader import FORCE_OCR, process_document
from scoring import calculate_score


# Date Logic, these stuff so ugly 🥀
# Raw Components
YEAR = r"(?:19|20)\d{2}"
MONTH = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
DAY = r"\d{1,2}(?:st|nd|rd|th)?"

# Format Patterns
MONTH_YEAR = rf"(?:{MONTH}\s+{YEAR})"
FULL_DATE = rf"(?:{MONTH}\s+{DAY},?\s+{YEAR})"
YEAR_ONLY = rf"(?:{YEAR})"
NUMERIC_DATE = r"\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}"


DATE_TOKEN = rf"(?:{FULL_DATE}|{MONTH_YEAR}|{YEAR_ONLY}|{NUMERIC_DATE})"

DATE_RANGE = rf"""
(?:{DATE_TOKEN})
\s*
(?:-|–|to)
\s*
(?:Present|Current|{DATE_TOKEN})
"""


def normalizeDate(date_str):
    if not date_str:
        return None
    
    token = date_str.strip().lower()
    if "present" in token or "current" in token:
        return "Present"

    try:
        dt = dateutil_parser.parse(date_str, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str

def extractDate(text):
    match = re.search(DATE_RANGE, text, re.IGNORECASE | re.VERBOSE)
    if match:
        return match.group().strip()

    # Fallback single date
    match = re.search(DATE_TOKEN, text, re.IGNORECASE)
    if match:
        return match.group().strip()

    return None

def parseDate(date_str):
    if not date_str:
        return {"start": None, "end": None}

    # Split by the range separators
    parts = re.split(r"\s*(?:-|–|to)\s*", date_str, maxsplit=1, flags=re.IGNORECASE)

    if len(parts) >= 2:
        return {
            "start": normalizeDate(parts[0]),
            "end": normalizeDate(parts[-1]) 
        }

    # Single date fallback
    return {
        "start": normalizeDate(date_str),
        "end": None
    }

###################################################################
#                                                                 #                  
#                         Section Stuff                           #
#                                                                 #  
###################################################################
INVISIBLE_CHARS = [
        "\u200b",  # zero width space
        "\u200c",  # zero width non-joiner
        "\u200d",  # zero width joiner
        "\ufeff"   # zero width no-break space (BOM)
    ]

def normalizeText(text):
    for char in INVISIBLE_CHARS:
        text = text.replace(char, "")

    lines = text.split("\n")
    return [line.strip() for line in lines if line.strip()]


_SECTION_KEYWORD_MAP = [
    ("education", [
        "education", "academic background", "academic history",
        "qualifications", "academic qualification",
        "pendidikan", "riwayat pendidikan", "latar belakang pendidikan",
    ]),
    ("experience", [
        "work experience", "professional experience", "employment history",
        "internship experience", "internship", "work history",
        "organizational experience", "organizational experiences",
        "volunteer experience", "leadership experience", "career history",
        "pengalaman kerja", "riwayat kerja", "pengalaman organisasi",
        "pengalaman",
    ]),
    ("experience", ["experience"]),
    ("projects", [
        "projects", "project", "personal projects", "relevant projects",
        "portfolio", "proyek", "projek",
    ]),
    ("skills", [
        "skills", "competencies", "technical skills", "core competencies",
        "keahlian", "kemampuan", "kompetensi",
    ]),
]
 
# Combined header that mentions 2+ content types.
_COMBINED_PATTERNS = [
    (re.compile(r"projects?.+skills|skills.+projects?",     re.I), "mixed_projects_skills"),
    (re.compile(r"skills?.+interest|interest.+skills?",     re.I), "mixed_skills_interests"),
    (re.compile(r"skills?.+achieve|achieve.+skills?",       re.I), "mixed_skills_achievements"),
    (re.compile(r"skills?.+experience|experience.+skills?", re.I), "mixed_skills_experience"),
    (re.compile(r"achieve.+experience|experience.+achieve", re.I), "mixed_achievements_experience"),
    (re.compile(
        r"(skills?|projects?|experience|achieve|interest|certif|award)"
        r".{0,25}"
        r"(skills?|projects?|experience|achieve|interest|certif|award)",
        re.I), "mixed_other"),
]
 
 
def _isSectionHeader(line):
    clean = line.strip()
    if not clean or len(clean.split()) > 8:
        return False
    if clean[-1] in ".,?":
        return False
    return True


def detectSectionType(line):
    if not _isSectionHeader(line):
        return None

    low = line.lower()

    # Combined patterns
    for pattern, tag in _COMBINED_PATTERNS:
        if pattern.search(low):
            return tag

    # Keyword match (EN + ID)
    for canonical, keywords in _SECTION_KEYWORD_MAP:
        if any(kw in low for kw in keywords):
            return canonical

    return None

def splitSections(text):
    lines = normalizeText(text)
    sections: dict  = {}
    current_section = "header"
    sections[current_section] = []
 
    for line in lines:
        tag = detectSectionType(line)
        if tag:
            current_section = tag
            sections.setdefault(current_section, [])
            sections[current_section].append("__SECTION_LABEL__:" + line)
            continue
 
        sections.setdefault(current_section, [])
        sections[current_section].append(line)
 
    return sections

_SUBSECTION_SIGNALS = [
    (re.compile(r"^(hard skills?|technical skills?)\s*[:\-\u2022\ue801]", re.I), "skills"),
    (re.compile(r"^(soft skills?)\s*[:\-]", re.I), "skills"),
    (re.compile(r"^(skills?|competenc|keahlian|kemampuan)\s*[:\-]", re.I), "skills"),
    (re.compile(r"^(interest|interests?|minat)\s*[:\-]", re.I), "interests"),
    (re.compile(r"^(achievement|achievements?|award|awards?|certif)\s*[:\-]?",re.I), "achievements"),
    (re.compile(r"^(course|courses?|training|pelatihan)\s*[:\(\-]", re.I), "achievements"),
    (re.compile(r".+\(\d{4}\)\s*:", re.I), "projects"),
]
 
RE_PROJECT_ENTRY = re.compile(r".+\(\d{4}\)\s*:", re.I)
 
 
def _contentTypeOfLine(line: str) -> str | None:
    for pattern, sub_type in _SUBSECTION_SIGNALS:
        if pattern.match(line):
            return sub_type
    return None
 
 
def splitMixedSection(lines: list) -> dict:
    buckets: dict = {
        "skills":       [],
        "projects":     [],
        "achievements": [],
        "interests":    [],
        "experience":   [],
    }
 
    # Infer initial state from section label if possible
    state = "skills"
    for line in lines:
        if line.startswith("__SECTION_LABEL__:"):
            label = line.replace("__SECTION_LABEL__:", "").lower()
            if "project" in label:
                state = "projects"
            elif "achieve" in label or "course" in label or "award" in label:
                state = "achievements"
            break
 
    # First pass: merge wrapped continuation lines
    merged: list = []
    for line in lines:
        if line.startswith("__SECTION_LABEL__:"):
            continue
        sub = _contentTypeOfLine(line)
        if (merged
                and sub is None
                and not RE_PROJECT_ENTRY.match(line)
                and line and not line[0].isupper()):
            merged[-1] += " " + line
            continue
        merged.append(line)
 
    # Second pass: assign to buckets
    for line in merged:
        sub = _contentTypeOfLine(line)
        if sub:
            state = sub
        if RE_PROJECT_ENTRY.match(line):
            state = "projects"
        buckets[state].append(line)
 
    return buckets


def splitBlocks(section_lines):
    clean_lines = [
        line for line in section_lines
        if not line.startswith("__HEADER__:") and not line.startswith("__SECTION_LABEL__:")
    ]
    if not clean_lines:
        return []
 
    RE_RANGE = re.compile(
        DATE_RANGE + r"|" + NUMERIC_DATE,
        re.IGNORECASE | re.VERBOSE,
    )
 
    entry_starts = []
    for i, line in enumerate(clean_lines):
        if not RE_RANGE.search(line):
            continue
        # Skip description bullets
        if re.match(r"^[\u2022\u2023\u25E6\u2043\u2219•\-\*]\s*", line):
            continue
        # Skip long description lines
        if len(line) > 120:
            continue
        entry_starts.append(i)
 
    if not entry_starts:
        return ["\n".join(clean_lines)]
 
    blocks = []
    for idx, start in enumerate(entry_starts):
        end = entry_starts[idx + 1] if idx + 1 < len(entry_starts) else len(clean_lines)
        block_lines = clean_lines[start:end]
        if block_lines:
            blocks.append("\n".join(block_lines))
 
    return blocks

###################################################################
#                                                                 #                  
#                   Entity Recognition Stuff                      #
#                                                                 #  
###################################################################
_NLP = None
 
def getNlp():
    global _NLP
    if _NLP is None:
        ConfigSchemaNlp.model_rebuild(_types_namespace={"Language": Language})
        try:
            _NLP = sp.load("en_core_web_lg")
        except OSError:
            try:
                _NLP = sp.load("en_core_web_md")
            except OSError:
                _NLP = sp.load("en_core_web_sm")
    return _NLP
 
 
def entityRecognition(text):
    nlp = getNlp()
    doc = nlp(text)
    return doc.ents
 
###################################################################
#                                                                 #
#                       Header Parsing                            #
#                                                                 #
###################################################################
RE_EMAIL    = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")
RE_PHONE    = re.compile(r"(?:\+?\d[\d\s\-().]{7,}\d)")
RE_LINKEDIN = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
RE_GITHUB   = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)
 
def extractName(lines):
    # Look for the first line that is likely a name
    for line in lines:
        line = line.strip()

        if not line:
            continue

        if RE_EMAIL.search(line) or RE_PHONE.search(line):
            continue

        if len(line.split()) > 6:
            continue

        # If the line is all uppercase, it's likely a name
        if line.isupper():
            return line

        if all(word[0].isupper() for word in line.split() if word.isalpha()):
            return line

    # Fallback to Spacy NER if no clear name line found
    nlp = getNlp()
    text = " ".join(lines[:10])
    doc = nlp(text)

    persons = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]

    if persons:
        return max(persons, key=len)

    return None
 
def parseHeader(header_lines):
    text = "\n".join(header_lines)
 
    email    = RE_EMAIL.search(text)
    phone    = RE_PHONE.search(text)
    linkedin = RE_LINKEDIN.search(text)
    github   = RE_GITHUB.search(text)
 
    return {
        "name":     extractName(header_lines),
        "email":    email.group() if email else None,
        "phone":    phone.group().strip() if phone else None,
        "linkedin": linkedin.group() if linkedin else None,
        "github":   github.group() if github else None,
    }
 
 
###################################################################
#                                                                 #
#                     Experience Parsing                          #
#                                                                 #
###################################################################
BULLET = re.compile(r"^[\u2022\u2023\u25E6\u2043\u2219•\-\*]\s*")
 
def parseExperienceBlock(block):
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        return {}

    date_str = extractDate(block)

    # Find the line that contains the date to help determine company/role
    date_line_idx = None
    for i, ln in enumerate(lines):
        if extractDate(ln):
            date_line_idx = i
            break

    company = None
    role = None
    desc_lines = []

    if date_line_idx is None:
        company = clean_company(lines[0]) if len(lines) > 0 else None
        role = lines[1] if len(lines) > 1 else None
        desc_lines = lines[2:]

    else:
        # Case 1: Company - Date - Role
        if date_line_idx == 1:
            company = clean_company(lines[0])
            role = lines[2] if len(lines) > 2 else None
            desc_lines = lines[3:]

        # Case 2: Company - Role - Date
        elif date_line_idx >= 2:
            company = clean_company(lines[0])
            role = lines[1]
            desc_lines = lines[date_line_idx + 1:]

        else:
            company = clean_company(lines[0])
            desc_lines = lines[1:]

    # Fallback: if role still None, maybe first line is role and company missing
    if role is None and desc_lines:
        role = desc_lines[0]
        desc_lines = desc_lines[1:]

    descriptions = [BULLET.sub("", ln) for ln in desc_lines if len(ln) > 3]

    return {
        "company": company,
        "role": role,
        "date_range": parseDate(date_str),
        "descriptions": descriptions,
    }

# Clean company names by removing date tokens and trailing info
def clean_company(line):
    line = re.sub(DATE_RANGE, "", line, flags=re.I | re.VERBOSE)
    line = re.sub(DATE_TOKEN, "", line, flags=re.I)

    parts = line.split(" - ")
    if parts:
        line = parts[0]

    return line.strip(" ,")

def parseExperience(section_lines):
    blocks = splitBlocks(section_lines)
    return [parseExperienceBlock(b) for b in blocks if b.strip()]
 
 
###################################################################
#                                                                 #
#                     Education Parsing                           #
#                                                                 #
###################################################################
DEGREE_KW = re.compile(
    r"\b(Bachelor|Master|PhD|Doctorate|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|"
    r"B\.?Eng|M\.?Eng|Associate|Diploma|Certificate|S\.?Kom|S\.?T\.?|D\.?III|"
    r"Undergraduate|Graduate)\b",
    re.IGNORECASE,
)
GPA = re.compile(r"(?:GPA\s*[:\-]?\s*)?([\d]+\.[\d]+)\s*/\s*[\d]+\.[\d]+")
 
def parseEducationBlock(block):
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        return {}
 
    first_line = lines[0]
    date_str   = extractDate(first_line)
    INLINE_DATE = re.compile(DATE_RANGE + r"|" + DATE_TOKEN, re.IGNORECASE)
    org_part   = INLINE_DATE.sub("", first_line).strip() if date_str else first_line
 
    degree, field = None, None
    gpa_match = GPA.search(block)
 
    # Search all lines for a degree keyword
    for ln in lines[1:]:
        m = DEGREE_KW.search(ln)
        if m:
            parts = re.split(r"\s+(?:of|in|,)\s+", ln, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 2:
                degree, field = parts[0].strip(), parts[1].strip()
            else:
                degree = ln
            break
 
    return {
        "institution": org_part,
        "degree":      degree,
        "field":       field,
        "date_range":  parseDate(date_str),
        "gpa":         gpa_match.group(1) if gpa_match else None,
    }
 
def parseEducation(section_lines):
    blocks = splitBlocks(section_lines)
    return [parseEducationBlock(b) for b in blocks if b.strip()]
 
###################################################################
#                                                                 #
#                       Skills Parsing                            #
#                                                                 #
###################################################################
def parseSkills(section_lines):
    text = " ".join(
        ln for ln in section_lines if not ln.startswith("__SECTION_LABEL__:")
    )

    text = re.sub(r"(hard|soft)?\s*skills?\s*[:\-]", "", text, flags=re.I)

    items = re.split(r"[,|•;\n]+|\s{2,}|(?<=\w)\s(?=[A-Z])", text)

    clean = []
    for item in items:
        item = item.strip()

        # Filter out very short/long items
        if len(item) < 2 or len(item) > 40:
            continue

        clean.append(item)

    return clean

###################################################################
#                                                                 #
#                       Projects Parsing                          #
#                                                                 #
###################################################################
RE_PROJECT_YEAR = re.compile(r"^[A-Z].+\((\d{4})\)\s*:", re.I)
 
def parseProjectBlock(block):
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        return {}
 
    first_line  = lines[0]
    first_line_lower = first_line.lower()

    if any(k in first_line_lower for k in ["course", "training", "certification", "pelatihan"]):
        return {}

    year_match  = RE_PROJECT_YEAR.search(first_line)
    name        = re.split(r"\s*\(", first_line)[0].strip() if year_match else first_line
    # Strip trailing icon chars
    name        = re.sub(r"[\ue800-\uf8ff]+", "", name).strip()
    year        = year_match.group(1) if year_match and year_match.groups() else None
 
    desc_parts = []
    if ":" in first_line:
        after_colon = first_line.split(":", 1)[1].strip()
        if after_colon:
            desc_parts.append(after_colon)
    for ln in lines[1:]:
        desc_parts.append(BULLET.sub("", ln))
 
    return {
        "name":        name,
        "year":        year,
        "description": " ".join(desc_parts).strip() or None,
    }
 
def parseProjects(section_lines):
    clean = [
        ln for ln in section_lines
        if not ln.startswith("__SECTION_LABEL__:")
    ]
    if not clean:
        return []

    raw_blocks = []
    current = []
    for line in clean:
        if RE_PROJECT_YEAR.search(line) and current:
            raw_blocks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        raw_blocks.append("\n".join(current))

    projects = []
    for b in raw_blocks:
        parsed = parseProjectBlock(b)
        if parsed:   # hanya ambil yang valid
            projects.append(parsed)

    return projects

###################################################################
#                                                                 #
#                        Master Parser                            #
#                                                                 #
###################################################################
def parseCV(text):
    sections = splitSections(text)
 
    # Collect lines per content type, starting from dedicated sections
    exp_lines   = list(sections.get("experience", []))
    edu_lines   = list(sections.get("education",  []))
    skill_lines = list(sections.get("skills",     []))
    proj_lines  = list(sections.get("projects",   []))
 
    # Then look into mixed sections and split them 
    for key, lines in sections.items():
        if not key.startswith("mixed_"):
            continue
        buckets = splitMixedSection(lines)
        skill_lines += buckets["skills"]
        proj_lines  += buckets["projects"]
        exp_lines   += buckets["experience"]
        skill_lines += buckets["achievements"]
 
    result = {
        "contact":    parseHeader(sections.get("header", [])),
        "experience": parseExperience(exp_lines),
        "education":  parseEducation(edu_lines),
        "skills":     parseSkills(skill_lines),
    }
 
    if proj_lines:
        result["projects"] = parseProjects(proj_lines)
 
    return result

# MAIN
if __name__ == "__main__":
    import pdfplumber
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input PDF file")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()

    PDF_FILE = args.input or "input.pdf"
    OUTPUT_FILE = args.output or "entities.json"


    with pdfplumber.open(PDF_FILE) as pdf:
        pages = []
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
        content = "\n".join(pages)
 
    # Debug: print section blocks
    all_sections = splitSections(content)
 
    for section_name, lines in all_sections.items():
        if not lines:
            continue
 
        print(f"\n{'='*20} SECTION: {section_name.upper()} {'='*20}")
        blocks = splitBlocks(lines)
 
        if not blocks:
            print("  No distinct blocks found.")
            continue
 
        for i, block_text in enumerate(blocks, 1):
            print(f"\n  [Block {i}]")
            for line in block_text.splitlines():
                print(f"    {line}")
 
    print(f"\n{'='*55}")
 
    # Structured JSON output
    result = parseCV(content)
    score = calculate_score(result)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
 
    print(f"\nStructured output saved to {OUTPUT_FILE}")
    print(f"  Name:       {result['contact']['name']}")
    print(f"  Email:      {result['contact']['email']}")
    print(f"  Experience: {len(result['experience'])} entries")
    print(f"  Education:  {len(result['education'])} entries")
    print(f"  Skills:     {len(result['skills'])} items")
    print(f"  Score:      {score}/100")
    if "projects" in result:
        print(f"  Projects:   {len(result['projects'])} entries")
    else:
        print(f"  Projects:   (no section found)")