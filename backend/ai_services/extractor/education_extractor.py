
# Extract education: institution, degree, field, GPA

from __future__ import annotations

import re

from .date_utils import extract_date_range, parse_date_range, DATE_RANGE, DATE_TOKEN, NUMERIC_DATE
from .section_extractor import split_mixed_section

RE_DEGREE = re.compile(
    r"\b(Bachelor|Master|PhD|Doctorate|Doctor\s+of|"
    r"B\.?\s*S\.?|M\.?\s*S\.?|B\.?\s*A\.?|M\.?\s*A\.?|"
    r"B\.?Eng\.?|M\.?Eng\.?|B\.?Tech\.?|M\.?Tech\.?|"
    r"Associate|Diploma|Certificate|D\.?\s*III|D\.?\s*IV|"
    r"Sarjana|S\.?\s*Kom\.?|S\.?\s*T\.?|S\.?\s*Pd\.?|S\.?\s*E\.?|"
    r"Undergraduate|Graduate)\b",
    re.IGNORECASE,
)

RE_GPA = re.compile(
    r"(?:GPA|IPK|CGPA|Cumulative\s+GPA)\s*[:\-]?\s*([0-5][.,]\d{1,2})(?:\s*(?:/|out\s+of)\s*[0-5][.,]\d{1,2})?|"
    r"\b([0-4][.,]\d{1,2})\s*/\s*[0-5][.,]\d{1,2}\b",
    re.IGNORECASE
)

_RE_INLINE_DATE = re.compile(
    DATE_RANGE + r"|" + DATE_TOKEN + r"|" + NUMERIC_DATE,
    re.IGNORECASE | re.VERBOSE,
)

BULLET = re.compile(r"^[\u2022\u2023\u25E6\u2043\u2219•\-\*]\s*")


def _split_blocks(section_lines: list[str]) -> list[str]:
    clean_lines = [
        ln for ln in section_lines
        if not ln.startswith("__SECTION_LABEL__:")
    ]
    if not clean_lines:
        return []

    re_range = re.compile(
        DATE_RANGE + r"|" + NUMERIC_DATE,
        re.IGNORECASE | re.VERBOSE,
    )

    entry_starts: list[int] = []
    for i, line in enumerate(clean_lines):
        if not re_range.search(line):
            continue
        if re.match(r"^[\u2022\u2023\u25E6\u2043\u2219•\-\*]\s*", line):
            continue
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


def _parse_education_block(block: str) -> dict | None:
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        return None

    first_line = lines[0]
    date_str = extract_date_range(first_line)

    org_part = _RE_INLINE_DATE.sub("", first_line).strip() if date_str else first_line
    org_part = org_part.strip(" ,|–-")

    if not date_str:
        for ln in lines[1:]:
            date_str = extract_date_range(ln)
            if date_str:
                break

    degree: str | None = None
    field: str | None = None
    
    gpa: str | None = None
    gpa_match = RE_GPA.search(block)
    if gpa_match:
        raw_gpa = gpa_match.group(1) or gpa_match.group(2)
        if raw_gpa:
            val = raw_gpa.replace(",", ".")
            full_match = gpa_match.group(0)
            if "/" in full_match or "out of" in full_match.lower():
                gpa = f"{val}/4.00" 
            else:
                gpa = val
            
            block = block.replace(full_match, "").strip()
            org_part = org_part.replace(full_match, "").strip()
            org_part = org_part.strip(" ,|-")
            lines = [ln.strip() for ln in block.split("\n") if ln.strip()]

    for ln in lines[1:]:
        m = RE_DEGREE.search(ln)
        if m:
            parts = re.split(r"\s+(?:of|in|,)\s+", ln, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 2:
                degree = parts[0].strip(" ,|-")
                field = parts[1].strip(" ,|-")
            else:
                degree = ln.strip(" ,|-")
            break

    if not org_part:
        return None

    return {
        "institution": org_part or None,
        "degree": degree,
        "field": field,
        "date_range": parse_date_range(date_str),
        "gpa": gpa,
    }


def extract_education(section_lines: list[str]) -> list[dict]:
    blocks = _split_blocks(section_lines)
    results = []
    for block in blocks:
        if not block.strip():
            continue
        parsed = _parse_education_block(block)
        if parsed:
            results.append(parsed)

    return results
