# Porfio.
**🌐 Part of Your Journey**

Porfio adalah aplikasi berbasis AI yang membantu pengguna menganalisis CV mereka dan pengguna akan mendapatkan rekomendasi pekerjaan yang sesuai, serta saran peningkatan profil karir secara otomatis.

![Next.js](https://img.shields.io/badge/Next.js-16.2-black?style=for-the-badge&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?style=for-the-badge&logo=typescript)
![Express](https://img.shields.io/badge/Express-5.x-green?style=for-the-badge&logo=express)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql)
![Prisma](https://img.shields.io/badge/Prisma-7.x-darkblue?style=for-the-badge&logo=prisma)

## **👥 Kelompok 17 Senior Project**

1. Ketua Kelompok : Nathania Ratnadewi - 23/522605/TK/57712 EDITED
2. Anggota 1    : Raditya Ryan Narotama - 23/518350/TK/57045
3. Anggota 2    : Nevrita Natasya Putriana - 23/514635/TK/56500

--- 

## 🚀 Live Demo

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-Akses%20Sekarang-brightgreen?style=for-the-badge)](http://48.193.42.230)

> Aplikasi sudah dideploy dan dapat diakses langsung tanpa instalasi.
> Daftar akun, upload CV, dan dapatkan analisis profil kamu

| | |
|--|--|
| 🌐 **URL** | [http://48.193.42.230](http://48.193.42.230) |
| 📡 **Status** | ✅ Online |
| 🔓 **Akses** | Publik (butuh registrasi) |

---

## 📋 Deskripsi Aplikasi

**Porfio** adalah platform analisis CV berbasis AI yang memungkinkan pengguna untuk:

- 📤 **Mengunggah CV** dalam format PDF
- 🔍 **Menganalisis konten CV** secara otomatis, mulai dari kontak, pendidikan, pengalaman, skill, proyek, hingga sertifikasi
- 📊 **Mendapatkan skor kualitas CV** berdasarkan kelengkapan dan relevansi
- 💼 **Menerima rekomendasi role pekerjaan** yang paling sesuai dengan profil
- 🤖 **Mendapatkan ringkasan profil, kekuatan, dan area perbaikan** yang dihasilkan oleh AI (Ollama LLM atau rule-based fallback)

> **Porfio** dikembangkan sebagai Senior Project oleh Kelompok 17

---

## 👥 Tim Pengembang

| Nama | NIM | Peran |
|------|-----|-------|
| Nathania Ratnadewi | 23/522605/TK/57712 | Ketua Kelompok |
| Raditya Ryan Narotama | 23/518350/TK/57045 | Anggota |
| Nevrita Natasya Putriana | 23/514635/TK/56500 | Anggota |

---

## ✨ Fitur

| Fitur | Deskripsi |
|-------|-----------|
| 📤 Upload CV | Support format PDF (text-based & scan) |
| 🔬 CV Parsing | Ekstraksi otomatis: nama, kontak, pendidikan, pengalaman, skill, proyek, dan sertifikasi |
| 📊 CV Scoring | Penilaian kualitas CV berdasarkan kelengkapan dan relevansi per-komponen |
| 💼 Job Recommendation | Rekomendasi role pekerjaan beserta missing skills dan saran perbaikan |
| 🤖 AI Summary | Ringkasan profil, kekuatan, dan area peningkatan yang didukung Ollama LLM atau fallback rule-based |
| 🔐 Autentikasi | Register, login, logout dengan session-based auth |
| 📂 Riwayat Analisis | Simpan hasil analisis per-user ke database |

---

## 🛠️ Tech Stack

### Frontend
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| [Next.js](https://nextjs.org/) | 16.2.4 | React Framework (App Router) |
| [React](https://react.dev/) | 19.2.4 | UI Library |
| [TypeScript](https://www.typescriptlang.org/) | 5.x | Type Safety |
| [Tailwind CSS](https://tailwindcss.com/) | 4.x | Styling |
| [Radix UI](https://www.radix-ui.com/) | latest | Headless UI Components |
| [Framer Motion](https://www.framer.com/motion/) | 12.x | Animasi |
| [Recharts](https://recharts.org/) | 2.x | Visualisasi data / chart |
| [React Hook Form](https://react-hook-form.com/) | 7.x | Form management |
| [Lucide React](https://lucide.dev/) | latest | Icon library |
| [next-themes](https://github.com/pacocoursey/next-themes) | 0.4.x | Dark/Light mode |
| [Sonner](https://sonner.emilkowal.ski/) | 2.x | Toast notifications |

### Backend (Node.js API)
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| [Express.js](https://expressjs.com/) | 5.x | Web Framework |
| [TypeScript](https://www.typescriptlang.org/) | 6.x | Type Safety |
| [Prisma ORM](https://www.prisma.io/) | 7.x | Database ORM |
| [PostgreSQL](https://www.postgresql.org/) | 16 | Relational Database |
| [Multer](https://github.com/expressjs/multer) | 2.x | File upload handling |
| [Morgan](https://github.com/expressjs/morgan) | 1.x | HTTP request logger |
| [CORS](https://github.com/expressjs/cors) | 2.x | Cross-Origin Resource Sharing |

### AI Services (Python)
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| [pdfplumber](https://github.com/jsvine/pdfplumber) | ≥0.10.3 | Ekstraksi teks PDF |
| [PyMuPDF](https://pymupdf.readthedocs.io/) | ≥1.23.0 | Parsing PDF lanjutan |
| [pytesseract](https://github.com/madmaze/pytesseract) | ≥0.3.10 | OCR untuk gambar & PDF scan |
| [Pillow](https://python-pillow.org/) | ≥10.0.0 | Pemrosesan gambar |
| [python-docx](https://python-docx.readthedocs.io/) | ≥1.0.0 | Parsing file DOCX |
| [Pydantic](https://docs.pydantic.dev/) | ≥2.4.2 | Data validation & schema |
| [Requests](https://requests.readthedocs.io/) | ≥2.31.0 | HTTP client (Ollama integration) |
| [Ollama](https://ollama.com/) | Qwen 1.5b | Local LLM inference |

---

## 📁 Struktur Folder

```
Porfio/
├── frontend/                  # Aplikasi Next.js (UI)
│   ├── src/
│   │   ├── app/               # App Router Next.js
│   │   │   ├── page.tsx       # Landing page
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── login/         # Halaman login
│   │   │   ├── register/      # Halaman registrasi
│   │   │   ├── dashboard/     # Halaman dashboard
│   │   │   ├── upload-cv/     # Halaman upload CV
│   │   │   ├── analysis/      # Halaman hasil analisis
│   │   │   ├── services/      # API service calls
│   │   │   └── utils/         # Utility functions
│   │   ├── components/        # Komponen UI (shadcn/ui + custom)
│   │   └── lib/               # Shared library & helpers
│   ├── public/                # Static assets
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── backend/                   # API Server (Express + TypeScript)
│   ├── src/
│   │   ├── index.ts           # Entry point server
│   │   ├── routes/            # Route definitions
│   │   │   ├── auth.ts        # Auth routes
│   │   │   ├── file.ts        # File upload routes
│   │   │   ├── scripts.ts     # CV processing routes
│   │   │   └── user.ts        # User routes
│   │   ├── controllers/       # Business logic handlers
│   │   ├── middleware/        # Express middleware
│   │   ├── services/          # External service integrations
│   │   ├── lib/               # Prisma client & utilities
│   │   ├── config/            # App configuration
│   │   └── types/             # TypeScript type definitions
│   ├── prisma/
│   │   └── schema.prisma      # Database schema
│   ├── ai_services/           # AI Processing (Python)
│   │   ├── main.py            # Entry point AI service (CLI)
│   │   ├── parser/            # File parser (PDF)
│   │   ├── extractor/         # Data extractor (kontak, skill, dll)
│   │   ├── scoring/           # CV scoring engine
│   │   ├── recommendation/    # Job recommendation engine
│   │   ├── llm/               # Ollama LLM client & prompt templates
│   │   └── requirements.txt   # Python dependencies
│   ├── uploads/               # Temporary file storage
│   ├── nodemon.json
│   ├── tsconfig.json
│   └── package.json
│
├── docs/                      # Dokumentasi tambahan
├── .env                       # Environment variables (root)
├── .gitignore
└── README.md
```

---

## ⚙️ Cara Instalasi & Menjalankan

### Prasyarat

Pastikan sudah menginstall:
- [Node.js](https://nodejs.org/) v18+
- [Python](https://www.python.org/) 3.10+
- [PostgreSQL](https://www.postgresql.org/) 14+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) *(untuk OCR PDF scan (opsional))*
- [Ollama](https://ollama.com/) *(untuk AI summary berbasis LLM)*

---

### 1. Clone Repository

```bash
git clone https://github.com/nevritaasy/porfio.git
cd porfio
```

---

### 2. Setup Environment Variables

Salin dan sesuaikan file `.env`:

```bash
cp .env.example .env
```

Isi variabel yang dibutuhkan (lihat bagian [Environment Variables](#-environment-variables) di bawah).

---

### 3. Setup Backend (Node.js)

```bash
cd backend
npm install
```

Jalankan migrasi database:

```bash
npx prisma migrate dev --name init
npx prisma generate
```

Jalankan server development:

```bash
npm run dev
```

Server akan berjalan di `http://localhost:8080`

---

### 4. Setup AI Services (Python)

```bash
cd backend/ai_services
pip install -r requirements.txt
```

Uji coba AI service secara manual (opsional):

```bash
# Tanpa Ollama (rule-based fallback)
python main.py --input ../../sample_cv.pdf --output result.json --no-ollama

# Dengan Ollama
python main.py --input ../../sample_cv.pdf --output result.json --use-ollama
```

---

### 5. Setup Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend akan berjalan di `http://localhost:3000`

---

## 🔑 Environment Variables

Buat file `.env` di root project (dan/atau di dalam `backend/`) dengan isi berikut:

```env
# atabase
DB_URL="postgresql://USER:PASSWORD@localhost:5432/porfio_db"

# Ollama 
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=llava

# MinIO (Opsional — untuk object storage) 
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_CV=cv-files
MINIO_SECURE=false

# App 
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
```

| Variabel | Deskripsi | Wajib |
|----------|-----------|-------|
| `DB_URL` | PostgreSQL connection string | ✅ Ya |
| `OLLAMA_BASE_URL` | URL Ollama server lokal | ✅ Ya |
| `OLLAMA_MODEL` | Model LLM untuk teks (misal: `llama3.1:8b`) | ❌ Opsional |
| `OLLAMA_VISION_MODEL` | Model LLM untuk vision/gambar (misal: `llava`) | ❌ Opsional |
| `MINIO_ENDPOINT` | Endpoint MinIO object storage | ❌ Opsional |
| `MINIO_ACCESS_KEY` | MinIO access key | ❌ Opsional |
| `MINIO_SECRET_KEY` | MinIO secret key | ❌ Opsional |
| `MINIO_BUCKET_CV` | Nama bucket MinIO untuk penyimpanan CV | ❌ Opsional |
| `APP_PORT` | Port server backend | ✅ Ya |
| `DEBUG` | Mode debug | ❌ Opsional |

---

## 🔌 API Endpoints

Base URL: `http://localhost:8080/api`

### Auth
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `POST` | `/auth/register` | Registrasi pengguna baru |
| `POST` | `/auth/login` | Login pengguna |
| `POST` | `/auth/logout` | Logout pengguna |

### CV Processing
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `POST` | `/upload-pdf` | Upload file CV (simpan ke storage) |
| `POST` | `/process-pdf` | Upload & proses CV langsung dengan AI |

### User
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/user` | Ambil data profil pengguna |

---

## 🗃️ Database Schema

Aplikasi menggunakan **PostgreSQL** dengan **Prisma ORM**.

```prisma
model User {
  id        String     @id @default(cuid())
  name      String     @unique
  email     String     @unique
  password  String

  analyses  Analysis[]
  sessions  Session[]
}

model Analysis {
  id        String   @id @default(cuid())
  content   Json     // Hasil analisis CV (scores, recommendations, ai_summary)

  userId    String
  user      User     @relation(fields: [userId], references: [id])

  createdAt DateTime @default(now())
}

model Session {
  id         String   @id @default(cuid())
  tokenHash  String   @unique
  userId     String
  user       User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  expiresAt  DateTime
  createdAt  DateTime @default(now())
}
```

---

## 🤖 Alur Kerja AI Services

```
File CV (PDF)
        │
        ▼
   [parser/]   ──► Ekstraksi teks mentah (pdfplumber / PyMuPDF / pytesseract / python-docx)
        │
        ▼
  [extractor/] ──► Ekstraksi terstruktur:
                    - Kontak (nama, email, phone, LinkedIn, GitHub)
                    - Pendidikan
                    - Pengalaman kerja & organisasi
                    - Skills (technical, soft, tools)
                    - Proyek
                    - Sertifikasi & kursus
        │
        ▼
  [scoring/]   ──► Penilaian kualitas CV per komponen (skor 0–100)
        │
        ▼
[recommendation/]─► Pencocokan profil dengan database role pekerjaan
                    + identifikasi missing skills
        │
        ▼
   [llm/]      ──► Generate ringkasan profil, kekuatan, dan area perbaikan
                    (via Ollama LLM — jika tidak tersedia, fallback ke rule-based)
        │
        ▼
   Output JSON  ──► cv_data, scores, job_recommendations, ai_summary, metadata
```

---

## 📄 Lisensi

Senior Project Kelompok 17 Departemen Teknik Elektro dan Teknologi Informasi Fakultas Teknik Universitas Gadjah Mada

