# Extract work/internship/organizational experiences

from __future__ import annotations

import re

from .date_utils import extract_date_range, parse_date_range, DATE_RANGE, DATE_TOKEN, NUMERIC_DATE

BULLET = re.compile(r"^[\u2022\u2023\u25E6\u2043\u2219•\-\*]\s*")

# Matches lines like "Porfio Project (2025): ..."
RE_PROJECT_LINE = re.compile(r".{2,}(?:project|portofolio|portfolio).{0,30}\(\d{4}\)", re.IGNORECASE)

# Icon / Private Use Area unicode chars (e.g. custom font icons in PDF)
RE_ICON_CHARS = re.compile(r"[\ue800-\uf8ff]")

_RE_RANGE_OR_DATE = re.compile(
    DATE_RANGE + r"|" + NUMERIC_DATE,
    re.IGNORECASE | re.VERBOSE,
)

_RE_ANY_DATE = re.compile(DATE_TOKEN, re.IGNORECASE)

_NON_EXPERIENCE_PREFIX = re.compile(
    r"^(?:soft\s+skills?|hard\s+skills?|skills?|technical\s+skills?|tools?|"
    r"course|courses?|certification|certifications?|certificate|certificates?|"
    r"training|trainings?)\b",
    re.IGNORECASE,
)

_NON_EXPERIENCE_TERMS = re.compile(
    r"\b(?:soft\s+skills?|hard\s+skills?|technical\s+skills?|course|courses?|"
    r"certification|certifications?|certificate|certificates?|training|trainings?)\b",
    re.IGNORECASE,
)


def _is_experience_stop_line(line: str) -> bool:
    clean = BULLET.sub("", line).strip()
    if not clean:
        return False
    if not _NON_EXPERIENCE_PREFIX.match(clean):
        return False

    if re.match(
        r"^(?:soft\s+skills?|hard\s+skills?|skills?|technical\s+skills?|tools?)\s*[:\-]",
        clean,
        re.IGNORECASE,
    ):
        return True
    if re.match(
        r"^(?:course|courses?|certification|certifications?|certificate|certificates?|training|trainings?)\s*(?:[:\-\(]|$)",
        clean,
        re.IGNORECASE,
    ):
        return True
    return len(clean.split()) <= 3


def _split_blocks(section_lines: list[str]) -> list[str]:
    clean_lines: list[str] = []
    for ln in section_lines:
        if ln.startswith("__SECTION_LABEL__:"):
            continue
        if _is_experience_stop_line(ln):
            break
        clean_lines.append(ln)

    if not clean_lines:
        return []

    entry_starts: list[int] = []
    for i, line in enumerate(clean_lines):
        if not _RE_RANGE_OR_DATE.search(line):
            continue
        if BULLET.match(line):
            continue
        if len(line) > 160:
            continue
        entry_starts.append(i)

    if not entry_starts:
        return ["\n".join(clean_lines)]

    blocks: list[str] = []
    for idx, start in enumerate(entry_starts):
        end = entry_starts[idx + 1] if idx + 1 < len(entry_starts) else len(clean_lines)
        block_lines = clean_lines[start:end]
        if block_lines:
            blocks.append("\n".join(block_lines))

    return blocks


def _clean_company(line: str) -> str:
    line = re.sub(DATE_RANGE, "", line, flags=re.IGNORECASE | re.VERBOSE)
    line = re.sub(DATE_TOKEN, "", line, flags=re.IGNORECASE)
    # Remove icon / private-use unicode characters
    line = RE_ICON_CHARS.sub("", line)
    parts = line.split(" - ")
    line = parts[0] if parts else line
    return line.strip(" ,|-")


def _parse_experience_block(block: str) -> dict | None:
    lines: list[str] = []
    for ln in block.split("\n"):
        clean = ln.strip()
        if not clean:
            continue
        if _is_experience_stop_line(clean):
            break
        lines.append(clean)

    if not lines:
        return None

    date_str = extract_date_range(block)

    date_line_idx: int | None = None
    for i, ln in enumerate(lines):
        if extract_date_range(ln):
            date_line_idx = i
            break

    company: str | None = None
    role: str | None = None
    desc_lines: list[str] = []

    # If no date in first line, search remaining lines
    if date_line_idx is None:
        company = _clean_company(lines[0]) if lines else None
        role = lines[1] if len(lines) > 1 else None
        desc_lines = lines[2:]

    elif date_line_idx == 0:
        company = _clean_company(lines[0])
        role = lines[1] if len(lines) > 1 else None
        desc_lines = lines[2:]

    elif date_line_idx == 1:
        company = _clean_company(lines[0])
        role = lines[2] if len(lines) > 2 else None
        desc_lines = lines[3:]

    else:
        company = _clean_company(lines[0])
        role = lines[1] if len(lines) > 1 else None
        desc_lines = lines[date_line_idx + 1:]

    # Fallback: if role is still None, take from desc_lines
    if role is None and desc_lines:
        role = desc_lines[0]
        desc_lines = desc_lines[1:]

    descriptions = [BULLET.sub("", ln).strip() for ln in desc_lines if len(ln.strip()) > 3]

    if not company and not role and not descriptions:
        return None
        
    # Skip if it looks like a skills, course, certification, or interests section
    first_line_lower = lines[0].lower()
    if _NON_EXPERIENCE_TERMS.search(first_line_lower):
        return None
    if "interest" in first_line_lower or "hobbies" in first_line_lower:
        return None
    if _NON_EXPERIENCE_TERMS.search(company or "") or _NON_EXPERIENCE_TERMS.search(role or ""):
        return None

    if RE_PROJECT_LINE.search(lines[0]):
        return None
    if re.search(r"project.{0,30}\(\d{4}\)", (company or "").lower()):
        return None
    if "project" in (company or "").lower() and not date_str:
        return None
    proj_desc_count = sum(1 for d in descriptions if RE_PROJECT_LINE.search(d))
    if proj_desc_count >= 2:
        return None

    return {
        "company": company,
        "role": role,
        "date_range": parse_date_range(date_str),
        "descriptions": descriptions,
    }


def extract_experience(section_lines: list[str]) -> list[dict]:
    blocks = _split_blocks(section_lines)
    results: list[dict] = []
    for block in blocks:
        if not block.strip():
            continue
        parsed = _parse_experience_block(block)
        if parsed:
            results.append(parsed)
    return results
