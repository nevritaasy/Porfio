# Extract contact information from CV header text: name, email, phone, linkedin, github, portfolio.

from __future__ import annotations

import re
from typing import Optional

# Regex patterns 
RE_EMAIL = re.compile(r"[\w.+\-]+@[\w.\-]+\.[a-zA-Z]{2,}")
RE_PHONE = re.compile(
    r"(?:\+?[\d][\d\s\-().]{7,}\d)"
)
RE_LINKEDIN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+", re.IGNORECASE)
RE_GITHUB = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+", re.IGNORECASE)
RE_PORTFOLIO = re.compile(
    r"(?:https?://)[^\s,<>\"']+",
    re.IGNORECASE,
)

# Patterns that indicate not a name
_NOT_NAME_PATTERNS = [
    RE_EMAIL,
    RE_PHONE,
    RE_LINKEDIN,
    RE_GITHUB,
    re.compile(r"http", re.IGNORECASE),
    re.compile(r"@"),
]


def _is_likely_name(line: str) -> bool:
    line = line.strip()
    if not line:
        return False

    # Skip lines that match contact patterns
    for pattern in _NOT_NAME_PATTERNS:
        if pattern.search(line):
            return False

    words = line.split()

    # Skip lines that are too long or too short
    if not (1 <= len(words) <= 6):
        return False

    # Skip lines with digits (likely phone/date)
    if any(ch.isdigit() for ch in line):
        return False

    # Capitalized words is likely a name heading
    if line.isupper() and len(words) >= 1:
        return True

    # Title-case words is likely a name
    alpha_words = [w for w in words if w.isalpha()]
    if alpha_words and all(w[0].isupper() for w in alpha_words):
        return True

    return False


def _extract_name(lines: list[str]) -> Optional[str]:
    for line in lines[:15]:
        clean = line.strip()
        if _is_likely_name(clean):
            return clean.rstrip(".,;:")

    return None


def _extract_portfolio(text: str, linkedin: Optional[str], github: Optional[str]) -> Optional[str]:
    for match in RE_PORTFOLIO.finditer(text):
        url = match.group()
        lower = url.lower()
        if "linkedin.com" in lower or "github.com" in lower:
            continue
        return url
    return None


def extract_contact(header_lines: list[str]) -> dict:
    text = "\n".join(header_lines)

    email_m = RE_EMAIL.search(text)
    phone_m = RE_PHONE.search(text)
    linkedin_m = RE_LINKEDIN.search(text)
    github_m = RE_GITHUB.search(text)

    linkedin = linkedin_m.group() if linkedin_m else None
    github = github_m.group() if github_m else None
    portfolio = _extract_portfolio(text, linkedin, github)

    return {
        "name": _extract_name(header_lines),
        "email": email_m.group() if email_m else None,
        "phone": phone_m.group().strip() if phone_m else None,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
    }
