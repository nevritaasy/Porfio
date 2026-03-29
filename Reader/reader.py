import pymupdf as pmp
import pytesseract as pt
from PIL import Image

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Input PDF file")
parser.add_argument("--output", help="Output text file")
parser.add_argument("--force-ocr", action="store_true", help="Force OCR extraction")

args = parser.parse_args()

INPUT_FILE = args.input or "input.pdf"
OUTPUT_FILE = args.output or "output.txt"
FORCE_OCR = args.force_ocr

pt.pytesseract.tesseract_cmd = r"../tesseract/tesseract.exe"
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

    text = pt.image_to_string(img, lang="eng")

    return text


def process_page(page, force_ocr=False):

    if not force_ocr:
        text = extract_native(page)

        if text.strip():
            return text

    return extract_ocr(page)


def process_document(input_pdf, output_file, force_ocr=False):

    page_count = 0

    with pmp.open(input_pdf) as doc, open(output_file, "wb") as out:

        for page in doc:

            text = process_page(page, force_ocr)

            out.write(text.encode("utf8"))
            out.write(b"\x0C")  # page delimiter

            page_count += 1

    return page_count

def validate_extraction(): return 0;

def main():

    pages = process_document(
        INPUT_FILE,
        OUTPUT_FILE,
        force_ocr=FORCE_OCR
    )

    print(f"Processed {pages} pages")


if __name__ == "__main__":
    main()