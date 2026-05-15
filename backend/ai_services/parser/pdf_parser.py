from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import pdfplumber
    _PDFPLUMBER_AVAILABLE = True
except ImportError:
    _PDFPLUMBER_AVAILABLE = False

try:
    import fitz  
    _FITZ_AVAILABLE = True
except ImportError:
    _FITZ_AVAILABLE = False

from .image_ocr import ocr_pil_image, is_ocr_available

# Minimum characters required to consider a page "has text"
_MIN_TEXT_CHARS = 30
_OCR_DPI = 300


def _page_quality(text: str) -> str:
    chars = len(text.strip())
    if chars >= 200:
        return "good"
    if chars >= _MIN_TEXT_CHARS:
        return "partial"
    return "poor"


def _render_page_to_pil(fitz_page: "fitz.Page") -> Optional["Image.Image"]:
    try:
        from PIL import Image
        matrix = fitz.Matrix(_OCR_DPI / 72, _OCR_DPI / 72)
        pix = fitz_page.get_pixmap(matrix=matrix)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    except Exception as exc:
        print(f"[pdf_parser] Failed to render page to image: {exc}")
        return None


def _extract_page_with_fallback(
    plumber_page: "pdfplumber.page.Page",
    page_index: int,
    fitz_doc: Optional["fitz.Document"],
    force_ocr: bool,
) -> tuple[str, str]:
    text = ""
    method = "native"

    if not force_ocr and _PDFPLUMBER_AVAILABLE:
        try:
            raw = plumber_page.extract_text()
            if raw:
                text = raw.strip()
        except Exception as exc:
            print(f"[pdf_parser] pdfplumber extract_text failed on page {page_index + 1}: {exc}")

    # Fallback to OCR if native text is insufficient
    if _page_quality(text) == "poor" or force_ocr:
        if is_ocr_available() and fitz_doc is not None and _FITZ_AVAILABLE:
            try:
                fitz_page = fitz_doc[page_index]
                pil_img = _render_page_to_pil(fitz_page)
                if pil_img is not None:
                    ocr_text = ocr_pil_image(pil_img)
                    if len(ocr_text.strip()) > len(text.strip()):
                        text = ocr_text
                        method = "ocr"
            except Exception as exc:
                print(f"[pdf_parser] OCR fallback failed on page {page_index + 1}: {exc}")
                method = "error"
        elif not _FITZ_AVAILABLE and _page_quality(text) == "poor":
            method = "native_poor"

    return text, method


def validate_extraction(pages_data: list[dict]) -> dict:
    total = len(pages_data)
    if total == 0:
        return {
            "total_pages": 0,
            "ocr_pages": 0,
            "empty_pages": 0,
            "avg_chars": 0.0,
            "quality": "poor",
        }

    ocr_pages = sum(1 for p in pages_data if p["method"] == "ocr")
    empty_pages = sum(1 for p in pages_data if len(p["text"].strip()) < _MIN_TEXT_CHARS)
    avg_chars = sum(len(p["text"]) for p in pages_data) / total

    if empty_pages == 0 and avg_chars > 200:
        quality = "good"
    elif empty_pages < total / 2:
        quality = "partial"
    else:
        quality = "poor"

    return {
        "total_pages": total,
        "ocr_pages": ocr_pages,
        "empty_pages": empty_pages,
        "avg_chars": round(avg_chars, 1),
        "quality": quality,
    }


def extract_text_from_pdf(
    pdf_path: str | Path,
    force_ocr: bool = False,
) -> dict:
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not _PDFPLUMBER_AVAILABLE:
        raise ImportError("pdfplumber is not installed. Run: pip install pdfplumber")

    pages_data: list[dict] = []
    fitz_doc: Optional["fitz.Document"] = None

    if _FITZ_AVAILABLE:
        try:
            fitz_doc = fitz.open(str(pdf_path))
        except Exception as exc:
            print(f"[pdf_parser] Could not open PDF with PyMuPDF: {exc}")

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for idx, page in enumerate(pdf.pages):
                try:
                    text, method = _extract_page_with_fallback(
                        page, idx, fitz_doc, force_ocr
                    )
                except Exception as exc:
                    print(f"[pdf_parser] Page {idx + 1} failed completely: {exc}")
                    text, method = "", "error"

                pages_data.append({
                    "page": idx + 1,
                    "text": text,
                    "method": method,
                })
    finally:
        if fitz_doc is not None:
            fitz_doc.close()

    full_text = "\f".join(p["text"] for p in pages_data)
    metadata = validate_extraction(pages_data)

    return {
        "text": full_text,
        "pages_data": pages_data,
        "metadata": metadata,
    }
