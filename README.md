# 🎓 Tols — Education Verification Suite & Mega Productivity Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram_Bot_API-v20%2B-0088cc.svg)](https://core.telegram.org/bots/api)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()
[![Clipku Pay](https://img.shields.io/badge/Payment-QRIS_Instant_Webhook-blueviolet.svg)]()

> **All-in-One Telegram Bot Suite & Modern Web App**: Platform terlengkap untuk pembuatan dokumen verifikasi akademik & pendidik beresolusi tinggi (lolos deteksi SheerID, Canva Edu, Spotify, Apple Student, GitHub Student), simulasi fisik 3D meja kayu fotorealistis, studio pasfoto AI, suite pengolah PDF ala PDF24, pengunduh video & musik media sosial anti-limit, pemotong klip vertikal 9:16 (Auto Clip), kalkulator kurs valas live, generator kwitansi resmi A5, pengingat VIP otomatis, hingga panel administrasi interaktif dengan analitik tren omzet Matplotlib.

---

## 📑 Daftar Isi
- [Fitur Unggulan Sistem](#-fitur-unggulan-sistem)
  - [1. Dokumen Akademik & Mahasiswa](#1-dokumen-akademik--mahasiswa)
  - [2. Mockup 3D Fotorealistis & Sensor EXIF](#2-mockup-3d-fotorealistis--sensor-exif)
  - [3. Dokumen Guru Canva Edu (13 Negara)](#3-dokumen-guru-canva-edu-13-negara)
  - [4. Kelola Dokumen PDF & Word (Suite PDF24 Terpadu)](#4-kelola-dokumen-pdf--word-suite-pdf24-terpadu)
  - [5. Video Downloader & Auto Clip 9:16 (Bypass Bot & Limit >50MB)](#5-video-downloader--auto-clip-916-bypass-bot--limit-50mb)
  - [6. Pasfoto Studio AI, OCR & Filter CamScanner](#6-pasfoto-studio-ai-ocr--filter-camscanner)
  - [7. Kurs Valas Live & Utilitas Produktivitas](#7-kurs-valas-live--utilitas-produktivitas)
  - [8. Sistem Billing & Webhook Instan QRIS Clipku Pay](#8-sistem-billing--webhook-instan-qris-clipku-pay)
  - [9. Panel Kendali SuperAdmin Interaktif](#9-panel-kendali-superadmin-interaktif)
  - [10. Pemeliharaan Otomatis, Cronjob & Keamanan Server](#10-pemeliharaan-otomatis-cronjob--keamanan-server)
- [Struktur Modul & Direktori Proyek](#-struktur-modul--direktori-proyek)
- [Daftar 25+ Perintah Pintasan Bot (Commands)](#-daftar-25-perintah-pintasan-bot-commands)
- [Panduan Instalasi & Deployment PM2](#-panduan-instalasi--deployment-pm2)
- [Lisensi](#-lisensi)

---

## 🚀 Fitur Unggulan Sistem

### 1. Dokumen Akademik & Mahasiswa
* **KTM Kampus Indonesia Resmi**: UT (Universitas Terbuka), UI, UGM, ITB, dan Universitas Brawijaya (UB) dengan nomor induk mahasiswa (NIM) realistis, barcode/QR code resmi, logo kampus vector ultra HD, pasfoto formal berjas, dan tanda tangan basah rektor.
* **KTM Kampus Internasional (Ivy League & Global Top 10)**: Harvard University (US), MIT Tech (US), Stanford University (US), dan University of Oxford (UK) dengan layout otentik standar internasional.
* **Kartu Pelajar SMA/SMK**: Standar nasional Kementerian Pendidikan Republik Indonesia berlogo Tut Wuri Handayani dan NISN.
* **Surat Keterangan Mahasiswa Aktif (SKMA)**: Format A4 resmi dengan kop surat universitas, nomor surat keluar, stempel cap basah ungu transparan, tanda tangan dekan, dan watermark anti-pemalsuan.
* **Transkrip Nilai / Kartu Hasil Studi (KHS)**: Berkas A4 300 DPI berisi tabel sebaran mata kuliah ber-SKS, indeks prestasi kumulatif (IPK 3.84 predikat *Cum Laude*), dan pengesahan akademik.

### 2. Mockup 3D Fotorealistis & Sensor EXIF
* **Meja Kayu Solid Nyata (*Photorealistic Wood Desk Mockup*)**: Kartu ditempatkan di atas permukaan tekstur kayu solid beresolusi master (`wood_table_master.jpg`), dilengkapi bayangan kontak pekat (*deep contact shadow/ambient occlusion*), bayangan jatuh terarah (*directional cast shadow*), dan pantulan warna hangat meja (*warm color bounce*).
* **Mika Card Holder & Lanyard Resmi**: Kartu dibungkus casing mika transparan dengan jepitan klip besi dan tali gantungan leher (lanyard) bertuliskan identitas kampus.
* **Sudut Pandang Tangan (*Handheld POV*)**: Sudut pengambilan foto realistis seolah kartu sedang digenggam oleh tangan pemiliknya di bawah pencahayaan ruangan alami.
* **Injeksi Metadata EXIF Kamera Asli**: Setiap hasil foto otomatis disuntikkan metadata EXIF kamera smartphone modern (Apple iPhone 14/15 Pro atau Samsung Galaxy S23 Ultra) lengkap dengan model kamera, lensa aperture f/1.8, ISO, focal length, dan timestamp acak agar lolos verifikasi sistem otomatis.

### 3. Dokumen Guru Canva Edu (13 Negara)
Generator dokumen surat tugas, kartu pengajar, dan SK pendidik untuk verifikasi akun Canva for Education / Microsoft Education di 13 negara:
* 🇮🇩 Indonesia (Surat Tugas Kemendikbud & NUPTK)
* 🇺🇸 Amerika Serikat (Teacher ID Card & District Employment Verification)
* 🇬🇧 Britania Raya (UK Department for Education Verification)
* 🇲🇾 Malaysia (Surat Pengesahan Guru Kementerian Pendidikan Malaysia - KPM)
* 🇵🇭 Filipina (DepEd Professional Identification Card)
* 🇹🇭 Thailand, 🇻🇳 Vietnam, 🇸🇬 Singapura, 🇦🇺 Australia, 🇩🇪 Jerman, 🇫🇷 Prancis, 🇮🇳 India, 🇯🇵 Jepang.

### 4. Kelola Dokumen PDF & Word (Suite PDF24 Terpadu)
Integrasi suite pengolah dokumen terlengkap berbasis Ghostscript, PyMuPDF, ReportLab, dan LibreOffice:
* **Word ke PDF & PDF ke Word**: Konversi dua arah berkas `.docx` dan `.pdf` tanpa merusak tata letak font dan tabel.
* **Foto ke PDF & Scanner Heic**: Mengubah foto kamera HP (JPG, PNG, HEIC iPhone) menjadi berkas PDF A4 siap cetak.
* **Kompres PDF Ghostscript**: Pengecilan ukuran dokumen PDF hingga 70–85% lebih ringan tanpa mengorbankan keterbacaan teks.
* **Pecah & Ambil Halaman PDF (Splitter)**: Mengambil rentang halaman tertentu (misal halaman 2–5).
* **Ekstrak Halaman Tunggal**: Memisahkan setiap halaman PDF menjadi berkas tersendiri.
* **Putar Halaman (Rotate PDF)**: Rotasi orientasi halaman (90°, 180°, 270°).
* **Watermark Teks Diagonal Kustom**: Menyematkan stempel teks proteksi dokumen miring semi-transparan.
* **Penomoran Halaman Otomatis**: Menambahkan nomor halaman berformat dinamis *"Halaman X dari Y"* pada footer dokumen.
* **Pembersih Metadata Sensitif**: Menghapus riwayat nama pembuat, software editor, dan tanggal modifikasi dari dokumen PDF.
* **Ekstraktor Gambar PDF**: Mengeluarkan seluruh gambar/foto asli beresolusi tinggi yang tertanam di dalam PDF.
* **Kunci & Enkripsi PDF**: Mengamankan dokumen PDF dengan enkripsi kata sandi pengguna (Password Protection).
* **Buka Sandi PDF**: Menghilangkan proteksi kata sandi pada file PDF milik sendiri.

### 5. Video Downloader & Auto Clip 9:16 (Bypass Bot & Limit >50MB)
Engine unduhan media sosial multi-platform berkecepatan tinggi:
* **Platform Didukung**: TikTok (Video & Slideshow tanpa watermark via TikWM API), Instagram (Reels & Post), YouTube, Facebook Video/Watch, dan Twitter/X.
* **Anti-Bot Protection Bypass YouTube**: Dilengkapi engine scraping oEmbed/NoEmbed dan streaming loader tanpa terblokir pesan *"Sign in to confirm you’re not a bot"*.
* **Solusi Pintar Berkas Besar (>50 MB)**:
  * Tombol **`[ 📥 Unduh Video HD Utuh (Browser) ]`** untuk download langsung via browser tanpa batasan kapasitas 50 MB Telegram.
  * Opsi ekstraksi **`[ 🎵 Unduh Audio MP3 Saja ]`** dan **`[ 📱 Coba Video Hemat (480p) ]`**.
* **Auto Clip 9:16 (Reels/TikTok Maker)**: Mengubah video rekaman lanskap menjadi video vertikal 9:16 dengan latar belakang *dynamic blurred mirror* berbasis akselerasi FFmpeg multi-thread.
* **Auto Splitter 60 Detik**: Memotong video panjang secara otomatis menjadi rangkaian Part 1–3 berdurasi 60 detik bersambung.
* **Kompres Video WhatsApp (<16 MB)**: Kompresi 2-pass encoding untuk mengecilkan video HP berukuran 50–300 MB menjadi **pas di bawah 15 MB** siap dikirim ke WhatsApp tanpa penolakan.
* **Pemotong Audio MP3 (*Ringtone Maker*)**: Potong lagu MP3 pada bagian reff/chorus tertentu lengkap dengan efek *Fade-in* & *Fade-out* halus.

### 6. Pasfoto Studio AI, OCR & Filter CamScanner
* **AI Deep Learning Rembg (U2-Net)**: Hapus latar belakang foto secara otomatis dengan presisi helai rambut.
* **Studio Pasfoto Formal**: Ganti background ke warna resmi Merah KTP (`#DB1514`), Biru Buku Nikah/KTM (`#0B60B0`), Putih Visa (`#FFFFFF`), atau efek studio radial glow.
* **Kompres Pasfoto Target CPNS/BUMN**: Atur ukuran berkas foto pas target 100 KB, 200 KB, atau 500 KB sesuai syarat portal SSCASN BKN.
* **Lembar Cetak Pasfoto 4R**: Menata susunan pasfoto ukuran 2x3, 3x4, dan 4x6 dalam satu lembar cetak foto ukuran 4R siap cetak di studio lab foto.
* **Filter CamScanner Dokumen Kertas**: Normalisasi foto kertas dokumen naskah/ijazah menjadi putih bersih, menajamkan teks hitam, dan mempertahankan keaslian cap stempel berwarna.
* **OCR Foto ke Teks**: Ekstraksi teks otomatis dari foto naskah/dokumen ke teks ketikan chat Telegram.
* **Ekstraktor Tanda Tangan Transparan**: Mengisolasi guratan tinta tanda tangan dari kertas putih menjadi berkas PNG transparan resolusi tinggi.

### 7. Kurs Valas Live & Utilitas Produktivitas
* **Kalkulator Kurs Valas Real-Time**: Data kurs interbank langsung pasar global yang diperbarui otomatis setiap jam dengan smart-caching 15 menit. Mendukung USD, SGD, MYR, EUR, JPY, CNY, AUD, SAR, THB, KRW ke Rupiah (IDR).
  * Deteksi ekspresi chat cerdas: bot langsung merespons jika Anda mengetik `$150`, `50 sgd to idr`, atau `RM 250`.
* **Generator Kwitansi Pembayaran PDF Resmi (A5)**: Pembuat tanda bukti pembayaran resmi dilengkapi nomor kwitansi, tanggal transaksi, nama penerima/pembayar, rincian keperluan, cap lunas, dan **kalimat terbilang rupiah otomatis** (contoh: *"Satu Juta Lima Ratus Ribu Rupiah"*).
* **Pembuat Kontak HP Massal (*VCard / VCF Bulk Saver*)**: Mengubah daftar nomor HP dari chat teks menjadi berkas kontak `.vcf` yang bisa langsung diimpor ke kontak smartphone Android / iOS dengan 1 kali klik.

### 8. Sistem Billing & Webhook Instan QRIS Clipku Pay
* **Metode Pembayaran**: QRIS Real-Time terintegrasi ke payment gateway **Clipku Pay** (`m.clipku.com`).
* **Aktivasi Seketika via Webhook (`https://m.clipku.com/webhook-yowes.php`)**: Detik itu juga setelah pembeli memindai QRIS (BCA, Mandiri, BRI, GoPay, OVO, Dana, ShopeePay), sistem webhook otomatis memverifikasi transaksi, menambahkan kuota cetak atau mengaktifkan status VIP, dan mengirimkan pesan notifikasi lunas ke Telegram pengguna.
* **Sistem Kuota Harian & Referral**: Kuota gratis harian pengguna reset otomatis setiap jam 00:00 WIB, dilengkapi tautan referral unik untuk mendapatkan bonus kuota gratis setiap mengajak teman bergabung.
* **Pengingat Masa Aktif VIP Otomatis (Cronjob H-3 & H-1)**: Bot secara otomatis mengirim pesan pengingat sopan ke pengguna VIP yang masa berlakunya hampir habis beserta tombol instan perpanjangan paket.

### 9. Panel Kendali SuperAdmin Interaktif
Akses eksklusif untuk SuperAdmin ID (`5606826328` / `@cs_kancilpay`):
* **Dashboard Statistik & Grafik Tren Omzet**: Bot otomatis menggambar **grafik batang dan kurva tren 7 hari terakhir (*Matplotlib dark mode*)** yang memvisualisasikan pertumbuhan user baru dan omzet pembayaran QRIS.
* **Aktivasi VIP Interaktif**: Tambah masa aktif VIP instan (+7, +30, +60, +365 hari) melalui antarmuka tombol dialog.
* **Suntik Kuota Interaktif**: Tambah saldo kuota pengguna (+5, +10, +20, +50 kuota) secara langsung.
* **Kendali Billing & Tarif Dinamis**: Ubah harga paket kuota, tarif VIP, durasi paket, kuota harian gratis, dan bonus referral langsung dari menu bot.
* **Pengecekan Profil Pengguna (`/checkuser <id>`)**: Melihat riwayat lengkap transaksi, tanggal kadaluarsa VIP, sisa kuota, dan jumlah dokumen yang telah diterbitkan pengguna.
* **Siaran Pesan Massal (*Broadcast Announcement*)**: Pengiriman pesan pengumuman ke seluruh pengguna dengan fitur pratinjau pesan (*preview*) dan tombol konfirmasi kirim/batal.
* **Pencadangan Database Instan**: Pengiriman snapshot berkas database SQLite `users.db` langsung ke chat Telegram admin.

### 10. Pemeliharaan Otomatis, Cronjob & Keamanan Server
* **Auto-Backup Harian Database**: Skrip `backup_and_clean.py` dijadwalkan via Linux crontab setiap hari pukul 02:00 pagi untuk mencadangkan database pengguna ke chat pribadi Admin.
* **Pembersihan Cache Folder `/tmp`**: Menghapus berkas sementara (video download, gambar render, file audio) yang berumur lebih dari 1 jam untuk mencegah kepenuhan disk VPS.
* **Web Landing Page Modern**: Berkas landing page responsif (*Tailwind CSS dark theme*) di `/web/index.html` siap dipromosikan ke publik.

---

## 🗂️ Struktur Modul & Direktori Proyek

```bash
/home/ubuntu/yowes/
├── bot.py                     # Router utama bot Telegram, Hub 2x2, dan handler interaktif
├── billing.py                 # Manajemen kuota, paket VIP, referral & integrasi API Clipku Pay
├── media_downloader.py        # Engine pengunduh video TikWM, YouTube loader & yt-dlp
├── auto_clipper.py            # Pemotong video vertikal 9:16 & auto-splitter 60s (FFmpeg)
├── media_tools_ext.py         # Engine kompresi video WhatsApp (<16MB) & pemotong lagu MP3
├── currency_service.py        # Layanan kalkulator & smart-caching kurs valas interbank live
├── pdf24_suite.py             # Paket utilitas PDF lengkap (Split, Rotate, Watermark, Page Number, Enkripsi)
├── desk_mockup_generator.py   # Renderer fisik 3D meja kayu fotorealistik, lanyard & POV tangan
├── rembg_service.py           # Engine AI penghapus latar belakang pasfoto U2-Net
├── ktm_generator.py           # Generator kartu tanda mahasiswa Indonesia & kampus global
├── skma_generator.py          # Generator Surat Keterangan Mahasiswa Aktif A4 resmi
├── khs_generator.py           # Generator Transkrip Nilai / Kartu Hasil Studi (KHS) A4 300 DPI
├── office_tools.py            # Konversi Word/PDF/Gambar, ekstraktor tanda tangan, & pasfoto 4R
├── backup_and_clean.py        # Skrip otomatisasi pencadangan database & auto-clean /tmp
├── admin_chart_service.py     # Generator grafik tren pertumbuhan user & omzet Matplotlib
├── web/
│   └── index.html             # Halaman web modern landing page Clipay Bot
├── countries/
│   └── assets/
│       ├── wood_table_master.jpg  # Tekstur foto permukaan kayu solid resolusi master 2048x1365
│       ├── mockups/               # Aset lanyard dan overlay visual kartu
│       └── ttd/                   # Koleksi tanda tangan basah & stempel universitas
└── users.db                   # Database SQLite penyimpanan kuota, user, dan transaksi
```

---

## ⌨️ Daftar 25+ Perintah Pintasan Bot (Commands)

| Perintah | Deskripsi Fungsi |
| :--- | :--- |
| `/start` | Membuka menu navigasi utama (Hub 2x2) dan memeriksa status akun |
| `/help` | Menampilkan panduan lengkap penggunaan seluruh fitur bot |
| `/topup` | Membuka menu pembelian kuota cetak atau aktivasi VIP Unlimited via QRIS |
| `/referral` | Mengambil tautan referral unik untuk mengundang teman |
| `/kurs` | Menampilkan ringkasan tabel kurs mata uang asing ke Rupiah hari ini |
| `/kwitansi` | Membuka form generator kwitansi pembayaran resmi PDF A5 |
| `/vcf` | Mengonversi daftar nomor handphone teks menjadi kontak `.vcf` massal |
| `/scan` | Mengaktifkan filter CamScanner pemutih kertas dokumen & naskah |
| `/autoclip` | Mengubah video rekaman lanskap menjadi klip vertikal 9:16 (TikTok/Reels) |
| `/compresswa` | Mengompres video HP berukuran besar menjadi pas di bawah 15 MB untuk WhatsApp |
| `/trimmp3` | Memotong berkas lagu atau audio MP3 untuk nada dering WhatsApp |
| `/splitpdf` | Memecah atau mengambil rentang halaman tertentu dari berkas PDF |
| `/rotatepdf` | Memutar orientasi halaman berkas PDF (90, 180, 270 derajat) |
| `/watermark` | Membubuhkan stempel watermark teks diagonal pengaman pada PDF |
| `/pagenumber` | Menambahkan penomoran halaman otomatis (*Page N of M*) pada footer PDF |
| `/cleanpdf` | Menghapus seluruh metadata sensitif dan riwayat edit dari berkas PDF |
| `/pdfimages` | Mengekstrak seluruh gambar atau foto yang tertanam di dalam PDF |
| `/protectpdf` | Mengunci dan mengamankan berkas PDF dengan kata sandi (Password) |
| `/doc2pdf` | Mengonversi dokumen Microsoft Word (`.docx`) menjadi PDF resmi |
| `/pdf2doc` | Mengonversi dokumen PDF menjadi berkas Microsoft Word editable |
| `/compresspdf`| Mengecilkan ukuran berkas dokumen PDF menggunakan Ghostscript |
| `/sigextract` | Mengekstrak tanda tangan dari foto kertas menjadi PNG transparan |
| `/pasfoto4r` | Menata pasfoto ukuran 2x3, 3x4, dan 4x6 ke lembar cetak foto 4R |
| `/stats` | *(Admin)* Melihat statistik akun dan grafik tren omzet mingguan Matplotlib |
| `/billing` | *(Admin)* Membuka panel kendali pengaturan harga paket kuota dan VIP |
| `/checkuser` | *(Admin)* Memeriksa detail statistik, kuota, dan masa aktif ID pengguna |
| `/broadcast` | *(Admin)* Mengirimkan pesan siaran massal ke seluruh pengguna bot |

---

## 🛠️ Panduan Instalasi & Deployment PM2

### 1. Kebutuhan Sistem Server (Ubuntu 20.04 / 22.04 LTS)
```bash
sudo apt-get update && sudo apt-get install -y \
    python3 python3-pip python3-venv \
    ffmpeg ghostscript libreoffice \
    libgl1-mesa-glx libglib2.0-0 \
    php8.2-sqlite3 curl git
```

### 2. Konfigurasi Lingkungan Virtual Python
```bash
cd /home/ubuntu/yowes
python3 -m venv venv
source venv/bin/activate
pip install -U pip wheel
pip install python-telegram-bot[http2] httpx pillow pillow-heif \
    pymupdf reportlab matplotlib rembg yt-dlp pexpect
```

### 3. Pengoperasian Daemon Menggunakan PM2
```bash
# Menjalankan bot via PM2
pm2 start venv/bin/python3 --name "yowes-bot" -- bot.py

# Memeriksa status log bot secara real-time
pm2 logs yowes-bot

# Memuat ulang bot setelah pembaruan kode
pm2 reload yowes-bot

# Menyimpan proses agar otomatis berjalan saat VPS reboot
pm2 save
pm2 startup
```

### 4. Menjadwalkan Auto-Backup & Clean Cronjob
Tambahkan jadwal pemeliharaan harian ke crontab server (`crontab -e`):
```bash
# Auto-Backup Database ke Telegram Admin setiap hari pukul 02:00 WIB
0 2 * * * /home/ubuntu/yowes/venv/bin/python3 /home/ubuntu/yowes/backup_and_clean.py backup >> /home/ubuntu/yowes/backup.log 2>&1

# Auto-Clean file temporary di /tmp setiap 6 jam
0 */6 * * * /home/ubuntu/yowes/venv/bin/python3 /home/ubuntu/yowes/backup_and_clean.py clean >> /home/ubuntu/yowes/clean.log 2>&1

# Auto-Reminder Pengingat VIP Expire (H-3 dan H-1) setiap pukul 09:00 WIB
0 9 * * * /home/ubuntu/yowes/venv/bin/python3 /home/ubuntu/yowes/backup_and_clean.py remind_vip >> /home/ubuntu/yowes/remind.log 2>&1
```

---

## 📄 Lisensi
Hak Cipta © 2026 **Aldi Irawan (Tols Project)**.  
Didistribusikan di bawah lisensi resmi [MIT License](LICENSE).
