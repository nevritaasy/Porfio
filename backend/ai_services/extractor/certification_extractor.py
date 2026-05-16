# Extract certifications, courses, and training entries

from __future__ import annotations

import re

from .date_utils import extract_date_range, parse_date_range

BULLET = re.compile(r"^[\u2022\u2023\u25E6\u2043\u2219\-\*]\s*")

_ENTRY_PREFIX = re.compile(
    r"^(?P<type>course|courses?|training|trainings?|certification|certifications?|"
    r"certificate|certificates?|license|licenses?|award|awards?|achievement|achievements?|"
    r"pelatihan|kursus|sertifikasi|sertifikat)"
    r"\s*(?:\((?P<year>(?:19|20)\d{2})\))?\s*[:\-]?\s*(?P<name>.*)$",
    re.IGNORECASE,
)

_STOP_PREFIX = re.compile(
    r"^(?:soft\s+skills?|hard\s+skills?|skills?|technical\s+skills?|tools?|"
    r"projects?|experience|education|interest|interests?)\s*[:\-]?$",
    re.IGNORECASE,
)


def _is_new_entry(line: str) -> bool:
    return bool(_ENTRY_PREFIX.match(BULLET.sub("", line).strip()))


def _parse_certification_block(block_lines: list[str]) -> dict | None:
    lines = [BULLET.sub("", ln).strip() for ln in block_lines if ln.strip()]
    if not lines:
        return None

    first = lines[0]
    match = _ENTRY_PREFIX.match(first)
    cert_type = None
    year = None
    name = first

    if match:
        cert_type = match.group("type").lower()
        year = match.group("year")
        name = match.group("name").strip() or first

    date_str = extract_date_range(first) or year
    descriptions = [ln for ln in lines[1:] if not _STOP_PREFIX.match(ln)]

    if not name:
        return None

    return {
        "name": name,
        "type": cert_type,
        "issuer": None,
        "date_range": parse_date_range(date_str),
        "descriptions": descriptions,
    }


def extract_certifications(section_lines: list[str]) -> list[dict]:
    clean: list[str] = []
    for ln in section_lines:
        if ln.startswith("__SECTION_LABEL__:"):
            continue
        stripped = ln.strip()
        if not stripped or _STOP_PREFIX.match(stripped):
            continue
        clean.append(stripped)

    if not clean:
        return []

    blocks: list[list[str]] = []
    current: list[str] = []
    for line in clean:
        if _is_new_entry(line) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)

    results: list[dict] = []
    for block in blocks:
        parsed = _parse_certification_block(block)
        if parsed:
            results.append(parsed)
    return results
