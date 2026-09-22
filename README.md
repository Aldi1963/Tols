# 🎓 Tols — Education Verification Suite & Mega Productivity Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram_Bot_API-v20%2B-0088cc.svg)](https://core.telegram.org/bots/api)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **All-in-One Telegram Bot Suite**: Platform terlengkap untuk pembuatan dokumen verifikasi akademik & pendidik beresolusi tinggi (lolos deteksi SheerID, Canva Edu, Spotify, Apple Student, GitHub Student), mockup fisik 3D fotorealistis, studio pasfoto AI, suite dokumen & PDF profesional, pengunduh video/musik tanpa watermark, pemotong video vertikal 9:16 (Auto Clip), kalkulator kurs valas live, kwitansi pembayaran resmi, kontak saver VCF, hingga proteksi watermark KTP anti-pinjol.

---

## 📑 Daftar Isi
- [Fitur Utama](#-fitur-utama)
  - [1. Dokumen Akademik & Mahasiswa](#1-dokumen-akademik--mahasiswa)
  - [2. Mockup 3D Fotorealistis & Sensor EXIF](#2-mockup-3d-fotorealistis--sensor-exif)
  - [3. Dokumen Guru Canva Edu (13 Negara)](#3-dokumen-guru-canva-edu-13-negara)
  - [4. Kelola Dokumen PDF & Word](#4-kelola-dokumen-pdf--word)
  - [5. Video Downloader & Auto Clip 9:16](#5-video-downloader--auto-clip-916)
  - [6. Foto Studio, OCR & Proteksi Privasi](#6-foto-studio-ocr--proteksi-privasi)
  - [7. Kurs Valas Live & Utilitas Bisnis](#7-kurs-valas-live--utilitas-bisnis)
  - [8. Sistem Kuota, VIP & Pembayaran QRIS](#8-sistem-kuota-vip--pembayaran-qris)
  - [9. Keamanan Server & Auto-Backup](#9-keamanan-server--auto-backup)
- [Arsitektur & Struktur Direktori](#-arsitektur--struktur-direktori)
- [Persyaratan Sistem & Dependensi](#-persyaratan-sistem--dependensi)
- [Panduan Instalasi & Deployment PM2](#-panduan-instalasi--deployment-pm2)
- [Daftar Perintah Telegram Bot](#-daftar-perintah-telegram-bot)
- [Lisensi](#-lisensi)

---

## 🚀 Fitur Utama

### 1. Dokumen Akademik & Mahasiswa
* **Kartu Tanda Mahasiswa (KTM) Kampus Indonesia**:
  * Didukung: **Universitas Terbuka (UT)**, **Universitas Indonesia (UI)**, **Universitas Gadjah Mada (UGM)**, **Institut Teknologi Bandung (ITB)**, dan **Universitas Brawijaya (UB)**.
  * Dilengkapi lambang vektor resmi resolusi tinggi, format NIM valid, barcode Code-128, RFID chip virtual, pasfoto formal jas/blazer Indonesia, cap biro akademik, dan tanda tangan basah.
* **KTM Kampus Internasional (Ivy League & Oxbridge)**:
  * Harvard University (US), MIT (US), Stanford University (US), dan University of Oxford (UK).
* **Kartu Pelajar SMA / SMK Negeri**:
  * SMAN 1 Jakarta, SMAN 3 Bandung, SMKN 1 Surabaya, SMAN 1 Yogyakarta lengkap dengan lambang Tut Wuri Handayani Kemendikbud & NISN valid.
* **Surat Keterangan Mahasiswa Aktif (SKMA)**:
  * Naskah dinas resmi format A4 (300 DPI) berkop Dekanat, nomor surat legal, dan tanda tangan basah pimpinan.
* **Transkrip Nilai / Kartu Hasil Studi (KHS)**:
  * Lembar hasil studi semester aktif resmi A4 (8 mata kuliah, 22 SKS, IPK 3.84 Cum Laude, stempel dinas ungu Dekanat, dan tanda tangan Dekan).
* **Mode Pembuatan Kustom**:
  * Pengguna dapat menginput nama lengkap sendiri serta mengunggah pasfoto pribadi.

### 2. Mockup 3D Fotorealistis & Sensor EXIF
* **Physical Desk Mockup**: Render simulasi foto fisik kartu di atas meja kerja kayu dengan perspektif kemiringan 3D, bayangan bertingkat (*ambient occlusion*), dan pantulan cahaya ruangan alami di permukaan PVC.
* **Mika Card Holder + Lanyard**: Render kartu di dalam wadah mika bening ber-seal pres ganda, lubang plong oval, klip logam *stainless steel*, dan tali gantungan tenun resmi kampus.
* **Hand-Held POV**: Simulasi foto fisik kartu sedang dipegang oleh tangan manusia (tampak ibu jari memegang tepian kartu) untuk lolos peninjauan manual manusia (*human review*).
* **Anti-Fraud EXIF Injector**: Setiap foto dokumen otomatis disuntikkan metadata sensor kamera asli ponsel (Apple iPhone 14 Pro / Samsung Galaxy S23 Ultra).

### 3. Dokumen Guru Canva Edu (13 Negara)
Menerbitkan paket lengkap berkas pendidik (Kartu Identitas, SK Pengangkatan, Slip Gaji, Surat Mengajar):
* 🇮🇩 Indonesia (NUPTK, SK Pengangkatan, Surat Mengajar, Slip Gaji)
* 🇳🇱 Belanda (Registerleraar, Arbeidsovereenkomst, DUO Verklaring, School ID)
* 🇺🇸 Amerika Serikat (Teacher ID, Employment Letter, Teaching License)
* 🇬🇧 Inggris (Teacher Registration, School Letter)
* 🇦🇺 Australia | 🇨🇦 Kanada | 🇫🇷 Prancis | 🇪🇸 Spanyol | 🇦🇷 Argentina | 🇲🇽 Meksiko | 🇵🇭 Filipina | 🇹🇭 Thailand | 🇸🇰 Slowakia.

### 4. Kelola Dokumen PDF & Word (PDF24 Complete Suite)
* **Word ke PDF**: Mengonversi berkas `.docx`, `.doc`, `.rtf`, `.txt` menjadi PDF resmi via LibreOffice headless.
* **PDF ke Word**: Mengonversi dokumen PDF menjadi berkas Microsoft Word editable (`.docx`) mempertahankan tata letak teks dan tabel.
* **Foto ke PDF (Single / Multi)**: Menggabungkan banyak foto (JPG, PNG, WEBP, Apple HEIC) menjadi satu dokumen PDF rapi.
* **PDF ke Gambar HD**: Merender setiap halaman berkas PDF menjadi foto JPEG tajam 200 DPI.
* **Gabung Banyak PDF (Merge)**: Menyatukan berkas-berkas PDF terpisah menjadi 1 file utuh berurutan.
* **Pecah & Ambil Halaman PDF (Splitter)**: Memotong dan mengekstrak halaman tertentu (misal halaman `1-3, 5`) dari PDF tebal tanpa merusak format.
* **Putar Halaman PDF (Rotate PDF)**: Memutar seluruh lembar PDF yang miring/terbalik sebesar 90 derajat searah jarum jam secara instan.
* **Hapus Halaman PDF (Remove Pages)**: Membuang halaman kosong, rusak, atau tidak terpakai (contoh input: `2` atau `1, 3, 5`).
* **Beri Nomor Halaman (Add Page Numbers)**: Menyematkan nomor urut resmi (*'Halaman 1 dari N'*) di bagian bawah lembar PDF standar skripsi/laporan dinas.
* **Kunci Password PDF (Protect PDF)**: Mengunci berkas rahasia dengan enkripsi kata sandi kuat AES-128.
* **Buka Password PDF (Unlock PDF)**: Menghapus proteksi sandi/enkripsi pada e-Statement rekening koran bank atau slip gaji.
* **Ekstrak Gambar dari PDF**: Mengambil dan mengunduh seluruh foto/gambar asli resolusi penuh yang tertanam di dalam dokumen PDF.
* **Kompres Dokumen PDF**: Memperkecil ukuran berkas PDF menjadi <500KB atau <1MB menggunakan Ghostscript Optimizer.

### 5. Video Downloader & Auto Clip 9:16
* **Multi-Platform Video Downloader**:
  * 🎵 **TikTok**: Video MP4 tanpa watermark, audio musik MP3, serta album foto slide.
  * 📸 **Instagram**: Reels, Video Feed, dan audio latar.
  * 📘 **Facebook**: Reels & Video Publik HD.
  * ▶️ **YouTube**: Shorts & Video reguler format MP4 dan ekstraksi audio MP3.
  * 🐦 **X / Twitter**: Video postingan cuitan HD.
* **Auto Clip Video Vertikal 9:16 (TikTok, Reels, Shorts)**:
  * **Auto-Framing 9:16**: Mengubah video horizontal menjadi vertikal dengan latar belakang *Dynamic Blur* estetik.
  * **Auto Split Bersambung**: Memotong video panjang secara otomatis menjadi klip 60 detik berseri (Part 1, Part 2, Part 3) siap upload.
  * **Klip 30s & 60s Instan**: Memotong klip pembuka (*hook*) secara otomatis bertenaga akselerasi multi-thread FFmpeg.

### 6. Foto Studio, OCR & Proteksi Privasi
* **Filter Scanner Dokumen Kertas (CamScanner)**:
  * Mengubah foto kamera HP yang gelap/kuning menjadi hasil scan putih bersih layaknya mesin scanner kantor.
  * Menghilangkan bayangan kertas dan jari tangan serta mempertajam tinta tulisan.
* **Stempel Watermark KTP Aman (Anti-Pinjol)**:
  * Menempelkan tulisan stempel watermark diagonal semi-transparan rapat (contoh: *"VERIFIKASI REKENING BANK - 22/09/2026"*) pada foto KTP/SIM/KK agar aman dari penyalahgunaan pihak ketiga.
* **AI Background Remover & Pasfoto Studio HD (U2-Net)**:
  * Segmentasi helai rambut presisi tinggi dengan model deep learning U2-Net.
  * Pilihan latar pasfoto resmi: 🔴 Merah KTP (Pantone 186 C), 🔵 Biru Ijazah/UT, ⚪ Putih Visa, 🔘 Abu-Abu Studio, dan 🏁 Transparan PNG dengan efek *Soft Radial Glow*.
* **Kompres Foto Pas Target (CPNS / BUMN)**:
  * Kompresi cerdas biner dengan pilihan target pas: 100 KB, 200 KB (SSCASN BKN), 300 KB, dan 500 KB tanpa pecah.
* **Pasfoto 4R Siap Cetak**:
  * Mengomposisikan 1 pasfoto ke dalam selembar kertas foto ukuran 4R (4 pcs 4x6, 4 pcs 3x4, 4 pcs 2x3) 300 DPI siap cetak murah.
* **Scan Foto ke Teks (OCR)**:
  * Ekstraksi teks dari foto dokumen menggunakan Tesseract OCR (Bahasa Indonesia & Inggris).
* **Ekstraktor Tanda Tangan Transparan**:
  * Mengisolasi tanda tangan dari foto kertas biasa menjadi format PNG transparan tajam bertinta biru dinas.

### 7. Kurs Valas Live & Utilitas Bisnis
* **Kalkulator Kurs Valas Real-Time**:
  * Terhubung langsung ke pasar valuta asing global per jam (*Live Market Data*).
  * **Deteksi Cerdas di Chat**: Cukup ketik `$150`, `50 sgd to idr`, `2000 myr`, atau `1000000 idr to usd` di chat bot untuk menghitung nilai tukar seketika.
  * Papan kurs harian lengkap: USD, SGD, MYR, EUR, JPY, CNY, AUD, GBP, SAR, THB, KRW terhadap Rupiah.
* **Generator Kwitansi Pembayaran Resmi (PDF A5)**:
  * Format ringkas: `Nama Pembayar | Nominal | Untuk Pembayaran`.
  * Otomatis menghasilkan PDF Kwitansi A5 300 DPI lengkap dengan kalimat terbilang rupiah otomatis (*"Dua Juta Lima Ratus Ribu Rupiah"*), nomor bukti unik, stempel LUNAS merah, dan tanda tangan kasir.
* **Pembuat File Kontak HP Otomatis (VCF Bulk Saver)**:
  * Mengonversi daftar puluhan/ratusan nomor WhatsApp menjadi 1 berkas kontak `.vcf`.
  * Sekali ketuk di ponsel, seluruh kontak langsung tersimpan otomatis ke buku telepon Google Contacts / iPhone.

### 8. Sistem Kuota, VIP & Pembayaran QRIS
* **Integrasi Clipku Pay**: Pembayaran otomatis seketika melalui gateway QRIS resmi (`https://m.clipku.com/api/index.php`).
* **Paket Langganan**:
  * ⚡ **+10 Kuota Cetak**: Rp 5.000 (Masa aktif permanen).
  * 👑 **VIP Unlimited 30 Hari**: Rp 15.000 (Bebas cetak ribuan dokumen & seluruh tools tanpa kuota).
* **Sistem Referral Hadiah Kuota**:
  * Tautan undangan unik (`t.me/<bot>?start=ref_<user_id>`).
  * Bonus **+2 kuota gratis** otomatis masuk ke pengundang saat ada pengguna baru bergabung.

### 9. Keamanan Server & Auto-Backup
* **Auto-Backup Database SQLite ke Telegram Admin**:
  * Terjadwal otomatis via Crontab setiap hari pukul 02:00.
  * Mengirimkan snapshot aman berkas `users.db` langsung ke chat Telegram Admin (`@cs_kancilpay`).
* **Auto-Cleaner Temporary Storage**:
  * Membersihkan berkas video/audio/gambar sementara di direktori `/tmp` setiap jam agar memori dan SSD VPS tetap lega.

---

## 📁 Arsitektur & Struktur Direktori

```text
├── bot.py                       # Master Daemon Telegram Bot (PTB v20+ & Hub Router)
├── billing.py                   # Sistem Kuota, VIP & Pembayaran QRIS Clipku Pay
├── backup_and_clean.py          # Crontab Auto-Backup SQLite ke Telegram & Temp Cleaner
├── currency_service.py          # Engine Kurs Valuta Asing Real-Time & Query Detector
├── watermark_tool.py            # Engine Stempel Watermark KTP Anti-Pinjol
├── pdf_splitter_tool.py         # Engine Pemecah & Pengambil Halaman Dokumen PDF
├── pdf24_suite.py               # Complete PDF24 Tools Engine (Rotate, Delete, Numbering, Protect, Extract)
├── kwitansi_tool.py             # Engine Pembuat Kwitansi Pembayaran Resmi PDF A5
├── vcf_saver_tool.py            # Engine Pembuat Berkas Kontak HP Bulk (.vcf)
├── doc_scanner_tool.py          # Filter Magic Color Dokumen Kertas (CamScanner)
├── smart_suit_formalizer.py     # AI Studio Pasfoto Formalizer (Soft Radial Glow)
├── auto_clipper.py              # Engine Pemotong Video Vertikal 9:16 & Multi-Part Splitter
├── media_downloader.py          # Engine Video Downloader No-WM (TikWM & yt-dlp)
├── office_tools.py              # Suite Konversi Dokumen, Ghostscript, OCR & Pasfoto 4R
├── ktm_generator.py             # Generator KTM Kampus Indonesia & Global
├── kartu_pelajar_generator.py   # Generator Kartu Pelajar SMA/SMK Tut Wuri Handayani
├── skma_generator.py            # Generator Surat Keterangan Mahasiswa Aktif (A4)
├── khs_generator.py             # Generator Transkrip Nilai KHS (A4 300 DPI)
├── desk_mockup_generator.py     # Renderer 3D Meja Kayu, Mika Lanyard & POV Tangan
├── exif_helper.py               # Metadata Sensor Kamera Asli (iPhone 14 / S23 Ultra)
├── rembg_service.py             # AI Background Remover (U2-Net)
├── countries/                   # Modul Generator Dokumen Pendidik 13 Negara
│   ├── assets/logos/            # Aset Logo Vektor Resmi (UT, UGM, UI, ITB, Tut Wuri)
│   ├── foto_indo/               # Galeri Kurasi Pasfoto Formal Berjas Indonesia
│   └── foto_mhs/                # Pasfoto Mahasiswa/Mahasiswi Formal
└── requirements.txt             # Daftar Dependensi Python Lengkap
```

---

## 🛠️ Persyaratan Sistem & Dependensi

* **Sistem Operasi**: Linux (Ubuntu 20.04 / 22.04 LTS direkomendasikan), macOS, atau Windows.
* **Python**: Versi `3.10` atau lebih baru.
* **Paket Sistem Linux**:
  ```bash
  sudo apt-get update
  sudo apt-get install -y libreoffice-writer-nogui poppler-utils ghostscript qpdf tesseract-ocr tesseract-ocr-ind ffmpeg
  ```

---

## 📦 Panduan Instalasi & Deployment PM2

1. **Clone Repositori**:
   ```bash
   git clone https://github.com/Aldi1963/Tols.git
   cd Tols
   ```

2. **Setup Virtual Environment & Install Dependensi**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install python-telegram-bot[job-queue] pillow pillow-heif rembg onnxruntime python-docx pypdf img2pdf pdf2docx pytesseract yt-dlp reportlab pymupdf numpy
   ```

3. **Jalankan Bot dengan PM2 Daemon**:
   ```bash
   npm install -g pm2
   pm2 start venv/bin/python3 --name "yowes-bot" -- bot.py
   pm2 save
   pm2 startup
   ```

---

## ⌨️ Daftar Perintah Telegram Bot

| Perintah | Deskripsi Layanan |
| :--- | :--- |
| `/start` | Membuka menu utama compact berformat Hub 2x2 yang lega di HP |
| `/ktm` | Menerbitkan KTM kampus atau one-shot: `/ktm [KAMPUS] [NAMA]` |
| `/pelajar` | Membuka generator Kartu Pelajar SMA/SMK Negeri |
| `/guru` | Membuka katalog dokumen sertifikat pendidik 13 negara |
| `/khs` | Menerbitkan Transkrip Nilai / Kartu Hasil Studi resmi A4 300 DPI |
| `/dl` | Mengunduh video tanpa watermark (TikTok, IG Reels, YT, FB, X) |
| `/autoclip` | Memotong video menjadi vertikal rasio 9:16 (TikTok / Shorts) |
| `/watermark`| Menempelkan stempel watermark pengaman KTP anti-pinjol |
| `/splitpdf` | Memecah dan mengambil nomor halaman tertentu dari berkas PDF |
| `/rotatepdf` | Memutar seluruh halaman dokumen PDF sebesar 90 derajat |
| `/removepages` | Menghapus lembaran halaman tertentu dari dokumen PDF |
| `/numberpdf` | Menyematkan nomor urut halaman resmi di bawah lembar PDF |
| `/protectpdf` | Mengunci dokumen PDF dengan proteksi kata sandi AES-128 |
| `/extractimages` | Mengambil seluruh foto/gambar asli yang tertanam di dalam PDF |
| `/kwitansi` | Menerbitkan PDF Kwitansi Pembayaran Resmi A5 terbilang otomatis |
| `/vcf` | Mengonversi daftar nomor HP menjadi berkas kontak telepon `.vcf` |
| `/scan` | Membersihkan foto dokumen/kertas kamera HP (CamScanner Filter) |
| `/kurs` | Menampilkan papan nilai tukar kurs valas dunia real-time |
| `/rembg` | AI Background Remover & ganti warna pasfoto resmi |
| `/kompres` | Mengompres foto pas target CPNS (100KB, 200KB, 300KB, 500KB) |
| `/komprespdf`| Mengompres ukuran berkas PDF menjadi <500KB / <1MB |
| `/doc2pdf` | Mengonversi dokumen Word (.docx) ke PDF resmi |
| `/pdf2word` | Mengonversi dokumen PDF ke format Word editable (.docx) |
| `/profil` | Melihat status langganan VIP, sisa kuota, dan statistik cetak |
| `/referral` | Mengambil tautan undangan unik (+2 kuota gratis per teman) |
| `/bantuan` | Panduan lengkap verifikasi SheerID & Canva Edu |

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi **MIT License** — bebas digunakan, dikembangkan, dan disesuaikan untuk keperluan personal maupun komersial.
