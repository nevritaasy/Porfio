# CV Parser: PDF, DOCX, JPG/JPEG/PNG

from __future__ import annotations

from pathlib import Path

from .pdf_parser import extract_text_from_pdf
from .docx_parser import extract_text_from_docx
from .image_ocr import ocr_image_file


def parse_cv_file(
    file_path: str | Path,
    force_ocr: bool = False,
) -> dict:
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    # PDF
    if suffix == ".pdf":
        result = extract_text_from_pdf(file_path, force_ocr=force_ocr)
        meta = result.get("metadata", {})
        pages_data = result.get("pages_data", [])

        methods = [p.get("method", "native") for p in pages_data]
        dominant = "ocr" if methods.count("ocr") > len(methods) / 2 else "native"

        return {
            "raw_text": result.get("text", ""),
            "file_type": "pdf",
            "extraction_method": dominant,
            "extraction_quality": meta.get("quality", "poor"),
            "total_pages": meta.get("total_pages", 0),
        }

    # DOCX
    elif suffix in {".docx", ".doc"}:
        result = extract_text_from_docx(file_path)
        meta = result.get("metadata", {})
        return {
            "raw_text": result.get("text", ""),
            "file_type": "docx",
            "extraction_method": "docx",
            "extraction_quality": meta.get("quality", "poor"),
            "total_pages": 1,
        }

    # IMAGE (JPG/PNG/JPEG)
    elif suffix in {".jpg", ".jpeg", ".png"}:
        text, method = ocr_image_file(file_path)
        quality = "good" if len(text) > 200 else ("partial" if len(text) > 50 else "poor")
        return {
            "raw_text": text,
            "file_type": "image",
            "extraction_method": method,
            "extraction_quality": quality,
            "total_pages": 1,
        }

    else:
        raise ValueError(
            f"Unsupported file type: '{suffix}'. "
            "Supported: .pdf, .docx, .doc, .jpg, .jpeg, .png"
        )
