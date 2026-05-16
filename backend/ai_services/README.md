# Porfio AI Services
Modul ini untuk memproses file CV (PDF, DOCX, Image), mengekstrak data penting, menghitung skor kualitas CV, dan memberikan rekomendasi role pekerjaan yang sesuai.

## Struktur Folder

- `parser/`: Modul untuk membaca file mentah (PDF text-based, OCR, DOCX) menjadi teks.
- `extractor/`: Modul untuk mengekstrak entitas spesifik dari teks (Contact, Education, Experience, Skills, Projects).
- `scoring/`: Modul untuk menghitung skor komponen CV.
- `recommendation/`: Modul untuk mencocokkan profil CV dengan peran pekerjaan (berisi database role dan skill).
- `llm/`: Modul integrasi opsional dengan Ollama untuk menghasilkan ringkasan dan saran secara natural.

## Instalasi

```bash
pip install -r requirements.txt
```
> **Catatan**: Jika mau mencoba fitur OCR untuk gambar atau PDF hasil scan, pastikan Tesseract OCR sudah terinstall.

## Cara Menjalankan

Modul ini memiliki CLI `main.py` yang dapat dijalankan secara langsung.

### Menjalankan Tanpa Ollama

```bash
python main.py --input ../../sample_cv.pdf --output result.json --no-ollama
```
Hasil AI (profile summary, strengths, improvement) akan di-generate menggunakan sistem rule-based fallback.

### Menjalankan Dengan Ollama 

```bash
python main.py --input ../../sample_cv.pdf --output result.json --use-ollama
```
Modul ini akan mencoba menghubungi `http://localhost:11434` menggunakan model `qwen2.5:1.5b`. Jika Ollama unavailable, sistem akan **secara otomatis fallback** ke versi rule-based.