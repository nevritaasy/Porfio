import pdfplumber as plm
import pytesseract as pt
from PIL import Image

import platform
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Input PDF file")
parser.add_argument("--output", help="Output text file")
parser.add_argument("--force-ocr", action="store_true", help="Force OCR extraction")

args = parser.parse_args()

INPUT_FILE = args.input or "input.pdf"
OUTPUT_FILE = args.output or "output.txt"
FORCE_OCR = args.force_ocr

def _findTesseract():
    env_path = __import__("os").environ.get("TESSERACT_CMD")
    if env_path:
        return env_path
 
    system = platform.system()
    candidates = {
        "Windows": [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"../tesseract/tesseract.exe",
        ],
        "Darwin":  ["/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"],
        "Linux":   ["/usr/bin/tesseract", "/usr/local/bin/tesseract"],
    }
    for path in candidates.get(system, []):
        if __import__("os").path.isfile(path):
            return path
    return "tesseract"  # fallback: assume it's on PATH
 
pt.pytesseract.tesseract_cmd = _findTesseract()
OCR_DPI = 300


def page_has_text(page):
    return bool(page.get_text().strip())


def extract_native(page):
    return page.get_text()


def extract_ocr(page):
    pix = page.get_pixmap(dpi=OCR_DPI)

    img = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    text = pt.image_to_string(img, lang="eng+ind")

    return text


def process_page(page, force_ocr=False):

    if not force_ocr:
        text = extract_native(page)

        if text.strip():
            return text, "native"

    return extract_ocr(page), "ocr"


def process_document(input_pdf, output_file, force_ocr=False):
 
    if not __import__("os").path.isfile(input_pdf):
        print(f"[ERROR] File not found: {input_pdf}")
        raise FileNotFoundError(input_pdf)
 
    pages_data = []
    page_count = 0
 
    with plm.open(input_pdf) as doc, open(output_file, "wb") as out:
 
        for page in doc:
 
            try:
                text, method = process_page(page, force_ocr)
            except Exception as e:
                print(f"[WARN] Page {page_count + 1} failed: {e}, skipping.")
                text, method = "", "error"
 
            pages_data.append({
                "page":   page_count + 1,
                "text":   text,
                "method": method,
            })
 
            out.write(text.encode("utf8"))
            out.write(b"\x0C")  # page delimiter
 
            page_count += 1
 
    return page_count, pages_data
 
 
def validate_extraction(pages_data):
    total       = len(pages_data)
    ocr_pages   = sum(1 for p in pages_data if p["method"] == "ocr")
    empty_pages = sum(1 for p in pages_data if len(p["text"].strip()) < 20)
    avg_chars   = sum(len(p["text"]) for p in pages_data) / total if total else 0
 
    if empty_pages == 0 and avg_chars > 200:
        quality = "good"
    elif empty_pages < total / 2:
        quality = "partial"
    else:
        quality = "poor"
 
    return {
        "total_pages": total,
        "ocr_pages":   ocr_pages,
        "empty_pages": empty_pages,
        "avg_chars":   round(avg_chars, 1),
        "quality":     quality,
    }
 
 
def main():
 
    pages, pages_data = process_document(
        INPUT_FILE,
        OUTPUT_FILE,
        force_ocr=FORCE_OCR
    )
 
    report = validate_extraction(pages_data)
 
    print(f"Processed {pages} pages")
    print(f"Quality:   {report['quality'].upper()}")
    print(f"OCR pages: {report['ocr_pages']}/{report['total_pages']}")
 
    if report["quality"] == "poor":
        print("[WARN] Poor extraction quality. Try --force-ocr.")
 
 
if __name__ == "__main__":
    main()