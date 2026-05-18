# Date parsing utilities: month names, date range., etc.

from __future__ import annotations

import re
from typing import Optional

try:
    import dateutil.parser as _dateutil_parser
    _DATEUTIL_AVAILABLE = True
except ImportError:
    _DATEUTIL_AVAILABLE = False

_ID_MONTH_MAP: dict[str, str] = {
    "januari": "January",
    "februari": "February",
    "maret": "March",
    "april": "April",
    "mei": "May",
    "juni": "June",
    "juli": "July",
    "agustus": "August",
    "september": "September",
    "oktober": "October",
    "november": "November",
    "desember": "December",
}

_PRESENT_TOKENS = {"present", "current", "sekarang", "now", "hingga sekarang", "sampai sekarang"}

YEAR = r"(?:19|20)\d{2}"
MONTH_EN = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
MONTH_ID = (
    r"(?:Januari|Februari|Maret|April|Mei|Juni|"
    r"Juli|Agustus|September|Oktober|November|Desember)"
)
MONTH = rf"(?:{MONTH_EN}|{MONTH_ID})"
DAY = r"\d{1,2}(?:st|nd|rd|th)?"

MONTH_YEAR = rf"(?:{MONTH}\.?\s+{YEAR})"
FULL_DATE = rf"(?:{MONTH}\.?\s+{DAY},?\s+{YEAR})"
YEAR_ONLY = rf"(?:{YEAR})"
NUMERIC_DATE = r"\d{1,2}[/\-]\d{4}|\d{4}[/\-]\d{1,2}"

DATE_TOKEN = rf"(?:{FULL_DATE}|{MONTH_YEAR}|{NUMERIC_DATE}|{YEAR_ONLY})"

PRESENT_TOKEN = r"(?:Present|Current|Sekarang|Now|Hingga\s+Sekarang|Sampai\s+Sekarang)"

DATE_RANGE = rf"""
(?:{DATE_TOKEN})
\s*
(?:-|–|to|s\.?d\.?|hingga|sampai)
\s*
(?:{PRESENT_TOKEN}|{DATE_TOKEN})
"""

_RE_DATE_TOKEN = re.compile(DATE_TOKEN, re.IGNORECASE)
_RE_DATE_RANGE = re.compile(DATE_RANGE, re.IGNORECASE | re.VERBOSE)
_RE_RANGE_SEP = re.compile(
    r"\s*(?:-|–|to|s\.?d\.?|hingga|sampai)\s*",
    re.IGNORECASE,
)


def _translate_indonesian_months(text: str) -> str:
    for id_month, en_month in _ID_MONTH_MAP.items():
        text = re.sub(rf"\b{id_month}\b", en_month, text, flags=re.IGNORECASE)
    return text


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None

    token = date_str.strip().lower()

    if any(p in token for p in _PRESENT_TOKENS):
        return "Present"

    translated = _translate_indonesian_months(date_str)

    if _DATEUTIL_AVAILABLE:
        try:
            dt = _dateutil_parser.parse(translated, fuzzy=True, default=None)
            if dt:
                return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    year_match = re.search(YEAR, date_str)
    if year_match:
        return year_match.group()

    return date_str


def extract_date_range(text: str) -> Optional[str]:
    match = _RE_DATE_RANGE.search(text)
    if match:
        return match.group().strip()

    match = _RE_DATE_TOKEN.search(text)
    if match:
        return match.group().strip()

    return None


def parse_date_range(date_str: Optional[str]) -> dict[str, Optional[str]]:
    if not date_str:
        return {"start": None, "end": None}

    parts = _RE_RANGE_SEP.split(date_str, maxsplit=1)

    if len(parts) >= 2:
        return {
            "start": normalize_date(parts[0].strip()),
            "end": normalize_date(parts[-1].strip()),
        }

    return {
        "start": normalize_date(date_str.strip()),
        "end": None,
    }


def calculate_months_between(start: Optional[str], end: Optional[str]) -> int:
    if not start:
        return 0

    import datetime

    def _to_date(s: Optional[str]) -> Optional[datetime.date]:
        if not s:
            return None
        if s == "Present":
            return datetime.date.today()
        try:
            if len(s) == 4 and s.isdigit():
                return datetime.date(int(s), 1, 1)
            return datetime.date.fromisoformat(s[:10])
        except Exception:
            # Try extracting just the year
            m = re.search(r"\d{4}", s)
            if m:
                return datetime.date(int(m.group()), 1, 1)
            return None

    d_start = _to_date(start)
    d_end = _to_date(end) if end else datetime.date.today()

    if d_start is None or d_end is None:
        return 0

    diff = (d_end.year - d_start.year) * 12 + (d_end.month - d_start.month)
    return max(0, diff)
