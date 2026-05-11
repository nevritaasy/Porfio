# Usage

```bash
python reader.py --input resume.pdf --output output.txt [--force-ocr]
python entityRecognition.py
```

**Options:**

- `--input`: PDF file to process (default: `input.pdf`)
- `--output`: Output text file (default: `output.txt`)
- `--force-ocr`: Force OCR extraction

# What It Does

1. **reader.py** - Extracts text from PDFs using native extraction or OCR
2. **entityRecognition.py** - Parses extracted text into sections

# Setup

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Install Tesseract (for OCR):
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Update the path in `reader.py` if needed

3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_lg
   ```
