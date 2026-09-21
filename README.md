# 🎓 Tols — Education Verification Suite & Productivity Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram_Bot_API-v20%2B-0088cc.svg)](https://core.telegram.org/bots/api)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **All-in-One Telegram Bot Suite**: Platform terlengkap untuk pembuatan dokumen verifikasi akademik & pendidik beresolusi tinggi (lolos deteksi SheerID, Canva Edu, Spotify, Apple Student, GitHub Student), mockup 3D fotorealistis, peralatan konversi berkas (Word, PDF, OCR), kompresi SSCASN CPNS/BUMN, AI background remover, serta pengunduh video & musik tanpa watermark (TikTok, Instagram, YouTube, Facebook, Twitter).

---

## 📑 Daftar Isi
- [Fitur Utama](#-fitur-utama)
  - [1. Dokumen Akademik & Mahasiswa](#1-dokumen-akademik--mahasiswa)
  - [2. Mockup 3D Fotorealistis & Sensor EXIF](#2-mockup-3d-fotorealistis--sensor-exif)
  - [3. Dokumen Guru Canva Edu (13 Negara)](#3-dokumen-guru-canva-edu-13-negara)
  - [4. Kotak Alat Dokumen & Konverter PDF](#4-kotak-alat-dokumen--konverter-pdf)
  - [5. AI Background Remover & Pasfoto Studio](#5-ai-background-remover--pasfoto-studio)
  - [6. Media & Video Downloader Tanpa Watermark](#6-media--video-downloader-tanpa-watermark)
  - [7. Auto Clip Video 9:16 (TikTok, Reels, Shorts)](#7-auto-clip-video-916-tiktok-reels-shorts)
  - [8. Monetisasi QRIS & Sistem Referral](#8-monetisasi-qris--sistem-referral)
- [Arsitektur & Struktur Proyek](#-arsitektur--struktur-proyek)
- [Persyaratan Sistem](#-persyaratan-sistem)
- [Panduan Instalasi & Menjalankan](#-panduan-instalasi--menjalankan)
- [Konfigurasi Environment](#-konfigurasi-environment)
- [Daftar Perintah Telegram Bot](#-daftar-perintah-telegram-bot)
- [Lisensi](#-lisensi)

---

## 🚀 Fitur Utama

### 1. Dokumen Akademik & Mahasiswa
* **Kartu Tanda Mahasiswa (KTM) Indonesia**:
  * Mendukung: **Universitas Terbuka (UT)**, **Universitas Indonesia (UI)**, **Universitas Gadjah Mada (UGM)**, **Institut Teknologi Bandung (ITB)**, dan **Universitas Brawijaya (UB)**.
  * Dilengkapi logo vektor resmi asli beresolusi tinggi, format NIM valid, barcode Code-128, chip RFID virtual, pasfoto formal berjas/blazer, dan cap stempel biro akademik.
* **KTM Internasional (Ivy League & Oxbridge)**:
  * Harvard University, MIT, Stanford University, dan University of Oxford.
* **Kartu Pelajar SMA / SMK Negeri**:
  * SMAN 1 Jakarta, SMAN 3 Bandung, SMKN 1 Surabaya, SMAN 1 Yogyakarta.
  * Dilengkapi logo resmi Tut Wuri Handayani Kemendikbud dan NISN 10 digit.
* **Surat Keterangan Mahasiswa Aktif (SKMA)**:
  * Format naskah dinas resmi A4 300 DPI berkop dekanat dan bertanda tangan basah.
* **Transkrip Nilai / Kartu Hasil Studi (KHS)**:
  * Lembar hasil studi semester aktif resmi A4 (8 mata kuliah, 22 SKS, IPK 3.84 Cum Laude, stempel dekanat dan tanda tangan Dekan).
* **Mode Pembuatan Kustom**:
  * Pengguna dapat memasukkan nama lengkap sendiri dan mengunggah foto wajah pribadi (otomatis diformalkan oleh AI).

### 2. Mockup 3D Fotorealistis & Sensor EXIF
* **Physical Desk Mockup**: Render simulasi foto fisik kartu di atas meja kerja kayu dengan perspektif kemiringan 3D, bayangan jatuh bertingkat (*ambient occlusion*), dan pantulan cahaya ruangan alami di permukaan PVC.
* **Mika Card Holder + Lanyard**: Render kartu di dalam wadah mika bening ber-seal pres ganda, lubang plong oval, klip logam *stainless steel*, dan tali gantungan resmi kampus.
* **Hand-Held POV**: Simulasi foto fisik kartu sedang dipegang oleh tangan manusia (tampak ibu jari memegang tepian kartu) untuk lolos audit peninjauan manual manusia (*human verification*).
* **Anti-Fraud EXIF Injector**: Setiap hasil foto otomatis disematkan metadata sensor kamera nyata (Apple iPhone 14 Pro / Samsung Galaxy S23 Ultra).

### 3. Dokumen Guru Canva Edu (13 Negara)
Menerbitkan paket lengkap berkas pendidik (Kartu Identitas, SK Pengangkatan, Slip Gaji, Surat Mengajar):
* 🇮🇩 Indonesia (NUPTK, SK Pengangkatan, Surat Mengajar, Slip Gaji)
* 🇳🇱 Belanda (Registerleraar, Arbeidsovereenkomst, DUO Verklaring, School ID)
* 🇺🇸 Amerika Serikat (Teacher ID, Employment Letter, Teaching License)
* 🇬🇧 Inggris (Teacher Registration, School Letter)
* 🇦🇺 Australia | 🇨🇦 Kanada | 🇫🇷 Prancis | 🇪🇸 Spanyol | 🇦🇷 Argentina | 🇲🇽 Meksiko | 🇵🇭 Filipina | 🇹🇭 Thailand | 🇸🇰 Slowakia.

### 4. Kotak Alat Dokumen & Konverter PDF
* **Word ke PDF**: Mengonversi berkas `.docx`, `.doc`, `.rtf`, `.txt` menjadi PDF resmi menggunakan engine LibreOffice headless.
* **PDF ke Word**: Mengonversi dokumen PDF menjadi berkas Microsoft Word editable (`.docx`) mempertahankan teks dan tabel.
* **Foto ke PDF (Single / Multi)**: Menggabungkan 1 atau banyak foto (JPG, PNG, WEBP, HEIC iPhone) menjadi satu dokumen PDF berurutan rapi.
* **Kompres Dokumen PDF**: Memperkecil ukuran berkas PDF menjadi <500KB atau <1MB menggunakan Ghostscript Optimizer.
* **Kompres Foto (CPNS / BUMN)**: Kompresi cerdas *binary search* dengan pilihan target pas: 100 KB, 200 KB (SSCASN BKN), 300 KB, dan 500 KB tanpa membuat foto pecah/buram.
* **Ekstraktor Tanda Tangan Transparan**: Mengisolasi goresan tanda tangan dari foto kertas biasa menjadi format PNG transparan tajam bertinta biru resmi.
* **Gabung Banyak PDF (Merge)**: Menyatukan beberapa berkas PDF menjadi 1 file rapi.
* **Buka Password PDF (Unlock)**: Menghapus proteksi sandi/enkripsi pada e-Statement rekening koran bank atau slip gaji.
* **PDF ke Gambar HD**: Merender setiap halaman PDF menjadi foto JPEG 200 DPI tajam.
* **Lembar Pasfoto 4R Siap Cetak**: Menyusun 1 pasfoto ke dalam selembar kertas foto ukuran 4R (4 pcs 4x6, 4 pcs 3x4, 4 pcs 2x3) 300 DPI siap cetak murah di tempat fotokopi/studio.
* **Scan Foto ke Teks (OCR)**: Ekstraksi teks otomatis dari gambar dokumen menggunakan Tesseract OCR (Bahasa Indonesia & Inggris).

### 5. AI Background Remover & Pasfoto Studio
* Didukung model deep learning **U2-Net** (`rembg`) untuk segmentasi rambut halus dan pakaian tanpa gerigi.
* Pilihan latar belakang pasfoto resmi:
  * 🔴 **Merah**: Standar KTP, SKCK, Pasfoto Kedinasan/CPNS (Pantone 186 C).
  * 🔵 **Biru**: Standar Buku Nikah, Ijazah, KTM Universitas.
  * ⚪ **Putih**: Standar Paspor Internasional & Visa.
  * 🔘 **Abu-Abu**: LinkedIn / Studio Korporat.
  * 🏁 **Transparan PNG**: Objek murni tanpa latar belakang.
* Dilengkapi pencahayaan radial lembut (*Soft Studio Radial Glow*).

### 6. Media & Video Downloader Tanpa Watermark
* **Mendukung Platform**:
  * 🎵 **TikTok**: Video MP4 tanpa watermark, audio musik MP3, serta unduhan album foto slide (*photo carousel*).
  * 📸 **Instagram**: Reels, Video Feed, dan audio MP3.
  * 📘 **Facebook**: Reels & Video Publik HD.
  * ▶️ **YouTube**: Shorts & Video reguler format MP4 dan ekstraksi audio MP3.
  * 🐦 **X (Twitter)**: Video postingan cuitan HD.
* **Interaktif**: Menampilkan thumbnail pratinjau judul dan tombol pilihan kualitas (Video HD, Video Hemat 480p, Audio MP3, atau Cover Foto).
* **Smart Auto-Detect**: Cukup kirim/paste link video langsung ke obrolan bot tanpa perlu membuka menu.

### 7. Auto Clip Video 9:16 (TikTok, Reels, Shorts)
* **Auto-Framing Vertikal Rasio 9:16**:
  * Mengubah video horizontal (YouTube, Facebook, podcast, kajian, atau tutorial) menjadi video vertikal pas layar ponsel (720x1280 / 1080x1920).
  * Dilengkapi efek **Dynamic Blur Background**: Video utama tetap utuh di tengah, dengan latar belakang atas dan bawah bernuansa blur estetik khas akun klip profesional.
* **Mode Pemotongan Klip Cerdas**:
  * ⚡ **Auto Split Bersambung**: Memotong video panjang secara otomatis menjadi klip berdurasi 60 detik berseri (Part 1, Part 2, Part 3) siap unggah bersambung ke TikTok / Reels.
  * 📱 **Klip 30 Detik / 60 Detik Instan**: Mengambil segmen pembuka berdurasi pas untuk konten *hook*.
* **Akselerasi FFmpeg Multi-Thread**:
  * Pemrosesan encoding cepat (*ultrafast preset*) langsung di VPS bertenaga AMD EPYC tanpa membuat server freeze.

### 8. Monetisasi QRIS & Sistem Referral
* **Clipku Pay Integration**: Terintegrasi langsung dengan gateway pembayaran QRIS otomatis seketika (`https://m.clipku.com/api/index.php`).
* **Paket Langganan**:
  * ⚡ **+10 Kuota Cetak**: Rp 5.000 (Masa aktif selamanya).
  * 👑 **VIP Unlimited 30 Hari**: Rp 15.000 (Bebas cetak ribuan dokumen & seluruh tools tanpa kuota).
* **Sistem Referral**:
  * Setiap pengguna memiliki tautan undangan unik (`t.me/<bot>?start=ref_<user_id>`).
  * Bonus **+2 kuota gratis** otomatis masuk ke pengundang saat teman baru bergabung via link.

---

## 📁 Arsitektur & Struktur Proyek

```text
├── bot.py                       # Master Daemon Telegram Bot (PTB v20+)
├── billing.py                   # Modul Database Kuota, VIP & QRIS Clipku Pay
├── ktm_generator.py             # Generator KTM Mahasiswa (UT, UGM, UI, ITB, UB, Ivy League)
├── kartu_pelajar_generator.py   # Generator Kartu Pelajar SMA/SMK Tut Wuri Handayani
├── skma_generator.py            # Generator Surat Keterangan Mahasiswa Aktif (A4)
├── khs_generator.py             # Generator Transkrip Nilai KHS (A4 300 DPI)
├── desk_mockup_generator.py     # Renderer 3D Meja Kayu, Mika Lanyard & POV Tangan
├── exif_helper.py               # Metadata Sensor Kamera Asli (iPhone 14 / S23 Ultra)
├── rembg_service.py             # AI Background Remover & Pasfoto Studio (U2-Net)
├── office_tools.py              # Suite Alat Konversi Dokumen, PDF, Kompres, OCR & 4R
├── media_downloader.py          # Engine Video Downloader No-WM (TikWM & yt-dlp)
├── auto_clipper.py              # Engine Auto Clip Video Vertikal 9:16 & Multi-Part Splitter
├── countries/                   # Modul Generator Pendidik 13 Negara
│   ├── assets/logos/            # Aset Logo Resmi Vektor (UT, UGM, UI, ITB, Kemendikbud)
│   ├── foto_indo/               # Galeri Kurasi Pasfoto Formal Indonesia
│   ├── foto_mhs/                # Pasfoto Mahasiswa & Mahasiswi Resmi
│   └── indonesia/               # Modul Dokumen Guru Indonesia (NUPTK, SK, Slip Gaji)
├── users.db                     # Database SQLite Pengguna & Transaksi (Diabaikan oleh git)
└── requirements.txt             # Daftar Dependensi Python
```

---

## 🛠️ Persyaratan Sistem

* **Operating System**: Linux (Ubuntu 20.04 / 22.04 LTS direkomendasikan), macOS, atau Windows.
* **Python**: Versi `3.10` atau lebih baru.
* **Paket Sistem Tambahan**:
  ```bash
  sudo apt-get update
  sudo apt-get install -y libreoffice-writer-nogui poppler-utils ghostscript qpdf tesseract-ocr tesseract-ocr-ind ffmpeg
  ```

---

## 📦 Panduan Instalasi & Menjalankan

1. **Clone Repositori**:
   ```bash
   git clone https://github.com/Aldi1963/Tols.git
   cd Tols
   ```

2. **Buat & Aktifkan Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependensi Python**:
   ```bash
   pip install --upgrade pip
   pip install python-telegram-bot[job-queue] pillow pillow-heif rembg onnxruntime python-docx pypdf img2pdf pdf2docx pytesseract yt-dlp reportlab pymupdf
   ```

4. **Jalankan Bot**:
   ```bash
   python3 bot.py
   ```

5. **Menjalankan sebagai Daemon Background (PM2)**:
   ```bash
   npm install -g pm2
   pm2 start venv/bin/python3 --name "yowes-bot" -- bot.py
   pm2 save
   pm2 startup
   ```

---

## ⌨️ Daftar Perintah Telegram Bot

| Perintah | Deskripsi |
| :--- | :--- |
| `/start` | Membuka menu utama dengan tampilan compact 2x2 yang lega |
| `/ktm` | Membuka menu pemilihan kampus atau one-shot: `/ktm [KAMPUS] [NAMA]` |
| `/pelajar` | Membuka generator Kartu Pelajar SMA/SMK Negeri |
| `/guru` | Membuka katalog dokumen sertifikat pendidik 13 negara |
| `/rembg` | Membuka AI Background Remover & ganti warna pasfoto resmi |
| `/autoclip` | Membuka Auto Clip Video 9:16 (Vertikal TikTok / Reels) |
| `/dl` | Membuka mode pengunduh video & musik tanpa watermark |
| `/kompres` | Membuka kompresor foto standar SSCASN CPNS 200KB |
| `/komprespdf` | Mengompres dokumen PDF menjadi <500KB / <1MB |
| `/doc2pdf` | Mengonversi dokumen Word (.docx) ke PDF resmi |
| `/pdf2word` | Mengonversi dokumen PDF ke Word editable (.docx) |
| `/foto2pdf` | Menggabungkan foto (JPG/PNG/HEIC) menjadi dokumen PDF |
| `/ocr` | Memindai teks dari foto dokumen (OCR Scanner) |
| `/ttd` | Mengubah foto tanda tangan kertas menjadi PNG transparan |
| `/profil` | Melihat status akun VIP, sisa kuota, dan statistik cetak |
| `/referral` | Mengambil tautan undangan unik (+2 kuota per teman) |
| `/bantuan` | Panduan lengkap tips verifikasi SheerID & Canva Edu |

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi **MIT License** — bebas digunakan, dikembangkan, dan disesuaikan untuk keperluan personal maupun komersial.
