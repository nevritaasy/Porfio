import re
from dateutil import parser

import spacy as sp
# from spacy.matcher import Matcher
from spacy.language import Language
from spacy.schemas import ConfigSchemaNlp

from reader import FORCE_OCR, process_document


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
        dt = parser.parse(date_str, fuzzy=True)
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
SECTION_HEADERS = {
    "experience": ["experience", "work experience", "professional experience"],
    "education": ["education", "academic background"],
    "skills": ["skills", "competencies"],
}

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

def detectSections(line): 
    line_clean = line.lower().strip() 

    if len(line_clean.split()) > 4:
    ## Original with the 'or' condition, which was too aggressive and caused false negatives:
    # if len(line_clean.split()) > 6 or any(char in line_clean for char in ".,;"): 
        return None
    
    for section, headers in SECTION_HEADERS.items():
        if any(header in line_clean for header in headers):
            return section
        
    return None

def splitSections(text):
    lines = normalizeText(text)
    sections = {}
    current_section = "header"
    sections[current_section] = []

    for line in lines:
        isSection = detectSections(line)

        if isSection: 
            current_section = isSection
            if current_section not in sections:
                sections[current_section] = []
            # Label Marking
            sections[current_section].append("__SECTION_LABEL__:" + line)
            continue 
    
        sections[current_section].append(line)

    return sections

def splitBlocks(section_lines):
    # 1. Cleanup
    clean_lines = [
        line for line in section_lines 
        if not line.startswith("__HEADER__:") and not line.startswith("__SECTION_LABEL__:")
    ]
    if not clean_lines: return []

    # 2. Find all date indices
    anchor_indices = [i for i, line in enumerate(clean_lines) if extractDate(line)]
    if not anchor_indices: return ["\n".join(clean_lines)]

    # 3. Calculate Global Offset (Distance from first date to the Org Name)
    global_offset = anchor_indices[0] 
    
    blocks = []
    last_org_header = []

    for i in range(len(anchor_indices)):
        current_anchor = anchor_indices[i]
        
        # Calculate where this 'entry' starts based on the first date's pattern
        start_idx = max(0, current_anchor - global_offset)
        
        # Determine end of this chunk
        if i + 1 < len(anchor_indices):
            end_idx = max(0, anchor_indices[i+1] - global_offset)
        else:
            end_idx = len(clean_lines)

        current_content = clean_lines[start_idx:end_idx]

        # --- THE FIX: Header Detection ---
        # If the first line of this block DOES NOT contain a date, 
        # it's likely a new Organization. Save it.
        if not extractDate(current_content[0]):
            # This is a 'Main' block (Company + Role)
            last_org_header = current_content[:global_offset] 
            blocks.append("\n".join(current_content))
        else:
            # This is a 'Sub' block (Role change within same Company)
            # We 'Prepend' the last known organization header to this block
            combined_block = last_org_header + current_content
            blocks.append("\n".join(combined_block))

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
        # Work around a spaCy+pydantic schema initialization issue.
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

if __name__ == "__main__":
    with open('output.txt', 'r', encoding='utf-8') as file:
        content = file.read()

    # 1. Split the raw text into sections (Experience, Education, etc.)
    all_sections = splitSections(content)

    for section_name, lines in all_sections.items():
        # Skip the generic "header" section if it's empty or just contact info
        if not lines:
            continue
            
        print(f"\n{'='*20} SECTION: {section_name.upper()} {'='*20}")

        # 2. Divide this specific section into logical blocks (jobs/degrees)
        blocks = splitBlocks(lines)

        if not blocks:
            print("No distinct blocks found.")
            continue

        # 3. Print each block
        for i, block_text in enumerate(blocks, 1):
            print(f"\n[Block {i}]")
            # Indent the block text for readability
            indented_text = "\n".join(f"  {line}" for line in block_text.splitlines())
            print(indented_text)
            
            # Optional: Run NER on the block to see identified entities
            # entities = entityRecognition(block_text)
            # print(f"  Entities: {[(ent.text, ent.label_) for ent in entities]}")

    print(f"\n{'='*55}")
