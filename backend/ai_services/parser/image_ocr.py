from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Optional

from PIL import Image

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False


def _find_tesseract() -> str:
    env_path = os.environ.get("TESSERACT_CMD")
    if env_path and Path(env_path).is_file():
        return env_path

    system = platform.system()
    candidates: dict[str, list[str]] = {
        "Windows": [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(
                os.environ.get("USERNAME", "")
            ),
        ],
        "Darwin": [
            "/opt/homebrew/bin/tesseract",
            "/usr/local/bin/tesseract",
        ],
        "Linux": [
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ],
    }

    for path in candidates.get(system, []):
        if Path(path).is_file():
            return path

    return "tesseract"  


def _setup_tesseract() -> bool:
    if not _TESSERACT_AVAILABLE:
        return False
    pytesseract.pytesseract.tesseract_cmd = _find_tesseract()
    return True


_TESSERACT_READY: bool = _setup_tesseract()


def ocr_image_file(image_path: str | Path, lang: str = "eng+ind") -> tuple[str, str]:
    if not _TESSERACT_READY:
        return "", "error"

    try:
        img = Image.open(str(image_path))
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip(), "ocr"
    except Exception as exc:
        print(f"[image_ocr] OCR failed for {image_path}: {exc}")
        return "", "error"


def ocr_pil_image(image: "Image.Image", lang: str = "eng+ind") -> str:
    if not _TESSERACT_READY:
        return ""

    try:
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as exc:
        print(f"[image_ocr] OCR on PIL image failed: {exc}")
        return ""


def is_ocr_available() -> bool:
    return _TESSERACT_READY
