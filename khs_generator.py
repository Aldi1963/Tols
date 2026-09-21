import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from countries.utils import load_font

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "countries" / "assets"
LOGOS_DIR = ASSETS_DIR / "logos"

def draw_wet_signature_simple(draw, start_pos, ink_color=(18, 48, 128, 255)):
    x0, y0 = start_pos
    pts = [(x0, y0), (x0+25, y0-20), (x0+45, y0+15), (x0+70, y0-10), (x0+110, y0+5), (x0+145, y0-15)]
    for i in range(len(pts)-1):
        draw.line([pts[i], pts[i+1]], fill=ink_color, width=3)
    draw.line([(x0-10, y0+18), (x0+165, y0+18)], fill=ink_color, width=2)

def generate_khs_transcript(first_name: str, last_name: str, univ_code: str = "UT") -> bytes:
    """
    Menghasilkan Lembar Transkrip Nilai / Kartu Hasil Studi (KHS) Semester Aktif Resmi (A4 300 DPI)
    Lengkap dengan Kop Universitas, Tabel Mata Kuliah, Nilai A/B, Bobot SKS, IPK, dan TTD Dekanat.
    """
    w, h = 2480, 3508  # A4 @ 300 DPI
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    f_kemen = load_font(26, bold=True)
    f_univ = load_font(44, bold=True)
    f_title = load_font(36, bold=True)
    f_sub = load_font(24, bold=False)
    f_body = load_font(24, bold=False)
    f_bold = load_font(24, bold=True)
    f_table = load_font(22, bold=False)
    f_table_b = load_font(22, bold=True)

    # 1. KOP SURAT
    univ_data = {
        "UT": ("UNIVERSITAS TERBUKA", "Jl. Cabe Raya, Pondok Cabe, Pamulang, Tangerang Selatan 15418", "logo_ut.png"),
        "UI": ("UNIVERSITAS INDONESIA", "Kampus UI Depok, Jawa Barat 16424 - Telp. (021) 7867222", "logo_ui.png"),
        "UGM": ("UNIVERSITAS GADJAH MADA", "Bulaksumur, Caturtunggal, Depok, Sleman, D.I. Yogyakarta 55281", "logo_ugm.png"),
        "ITB": ("INSTITUT TEKNOLOGI BANDUNG", "Jl. Ganesa No. 10, Lb. Siliwangi, Coblong, Kota Bandung 40132", "logo_itb.png"),
        "UB": ("UNIVERSITAS BRAWIJAYA", "Jl. Veteran, Ketawanggede, Lowokwaru, Kota Malang, Jawa Timur 65145", "logo_ub.png"),
    }.get(univ_code.upper(), ("UNIVERSITAS TERBUKA", "Jl. Cabe Raya, Pondok Cabe, Tangerang Selatan", "logo_ut.png"))

    u_name, u_addr, u_logo = univ_data

    # Logo Kop
    logo_path = LOGOS_DIR / u_logo
    if logo_path.exists():
        try:
            l_img = Image.open(logo_path).convert("RGBA")
            l_w, l_h = l_img.size
            tar_h = 240
            tar_w = int(l_w * (tar_h / l_h))
            l_res = l_img.resize((tar_w, tar_h), Image.Resampling.LANCZOS)
            img.paste(l_res, (180, 140), l_res)
        except Exception:
            pass

    # Teks Kop Tengah
    draw.text((w//2, 145), "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI", fill=(20, 20, 20), font=f_kemen, anchor="mm")
    draw.text((w//2, 210), u_name, fill=(10, 35, 95), font=f_univ, anchor="mm")
    draw.text((w//2, 275), "FAKULTAS SAINS DAN TEKNOLOGI • SISTEM INFORMASI AKADEMIK", fill=(50, 50, 50), font=f_sub, anchor="mm")
    draw.text((w//2, 325), u_addr, fill=(90, 90, 90), font=load_font(20, bold=False), anchor="mm")

    # Garis Pembatas Ganda Kop
    draw.line([(160, 390), (w - 160, 390)], fill=(0, 0, 0), width=5)
    draw.line([(160, 402), (w - 160, 402)], fill=(0, 0, 0), width=2)

    # 2. JUDUL DOKUMEN
    draw.text((w//2, 470), "TRANSKRIP HASIL STUDI SEMESTER (KHS)", fill=(15, 30, 75), font=f_title, anchor="mm")
    draw.text((w//2, 525), "SEMESTER GENAP TAHUN AKADEMIK 2025/2026", fill=(60, 60, 60), font=f_sub, anchor="mm")

    # 3. BIODATA MAHASISWA (2 KOLOM RAPI)
    nim_val = f"04{random.randint(1000000, 9999999)}" if univ_code == "UT" else f"23{random.randint(10000000, 99999999)}"
    biodata_left = [
        ("NIM", f":  {nim_val}"),
        ("Nama Lengkap", f":  {first_name.upper()} {last_name.upper()}"),
        ("Program Studi", f":  S1 - Sistem Informasi"),
    ]
    biodata_right = [
        ("Fakultas", ":  Fakultas Sains dan Teknologi"),
        ("Jenjang / Kelas", ":  Strata 1 (S1) / Reguler"),
        ("Status Akademik", ":  Mahasiswa Aktif Terdaftar"),
    ]

    by = 580
    for label, val in biodata_left:
        draw.text((220, by), label, fill=(40, 40, 40), font=f_bold)
        draw.text((440, by), val, fill=(10, 10, 10), font=f_bold)
        by += 45

    by = 580
    for label, val in biodata_right:
        draw.text((1320, by), label, fill=(40, 40, 40), font=f_bold)
        draw.text((1600, by), val, fill=(10, 10, 10), font=f_bold)
        by += 45

    # 4. TABEL MATA KULIAH (22 SKS, IPK 3.82)
    ty = 740
    th = 55
    tx0 = 160
    tx_w = w - 320

    # Header Tabel
    draw.rectangle([(tx0, ty), (tx0 + tx_w, ty + th)], fill=(235, 240, 250), outline=(120, 140, 170), width=2)
    draw.text((tx0 + 40, ty + 28), "NO", fill=(20, 30, 60), font=f_table_b, anchor="mm")
    draw.text((tx0 + 170, ty + 28), "KODE MK", fill=(20, 30, 60), font=f_table_b, anchor="mm")
    draw.text((tx0 + 640, ty + 28), "NAMA MATA KULIAH", fill=(20, 30, 60), font=f_table_b, anchor="mm")
    draw.text((tx0 + 1280, ty + 28), "SKS", fill=(20, 30, 60), font=f_table_b, anchor="mm")
    draw.text((tx0 + 1480, ty + 28), "NILAI", fill=(20, 30, 60), font=f_table_b, anchor="mm")
    draw.text((tx0 + 1720, ty + 28), "BOBOT", fill=(20, 30, 60), font=f_table_b, anchor="mm")
    draw.text((tx0 + 2000, ty + 28), "SKS x B", fill=(20, 30, 60), font=f_table_b, anchor="mm")

    courses = [
        ("MSIM4101", "Algoritma & Pemrograman Lanjut", 3, "A", "4.0", "12.0"),
        ("MSIM4202", "Struktur Data & Analisis Algoritma", 3, "A", "4.0", "12.0"),
        ("MSIM4205", "Sistem Manajemen Basis Data (DBMS)", 3, "A-", "3.7", "11.1"),
        ("MSIM4301", "Rekayasa Perangkat Lunak Terapan", 3, "A", "4.0", "12.0"),
        ("MSIM4308", "Jaringan Komputer & Keamanan Siber", 3, "B+", "3.5", "10.5"),
        ("MSIM4312", "Interaksi Manusia dan Komputer (UI/UX)", 2, "A", "4.0", "8.0"),
        ("MKDU4111", "Kewarganegaraan & Etika Profesi", 2, "A", "4.0", "8.0"),
        ("MSIM4403", "Kecerdasan Artifisial & Data Mining", 3, "A", "4.0", "12.0"),
    ]

    curr_y = ty + th
    for idx, (code, name, sks, grade, bobot, total_b) in enumerate(courses):
        bg_row = (255, 255, 255) if idx % 2 == 0 else (248, 250, 254)
        draw.rectangle([(tx0, curr_y), (tx0 + tx_w, curr_y + th)], fill=bg_row, outline=(190, 200, 220), width=1)
        draw.text((tx0 + 40, curr_y + 28), str(idx + 1), fill=(30, 30, 30), font=f_table, anchor="mm")
        draw.text((tx0 + 170, curr_y + 28), code, fill=(30, 30, 30), font=f_table_b, anchor="mm")
        draw.text((tx0 + 280, curr_y + 15), name, fill=(20, 20, 20), font=f_table)
        draw.text((tx0 + 1280, curr_y + 28), str(sks), fill=(30, 30, 30), font=f_table, anchor="mm")
        draw.text((tx0 + 1480, curr_y + 28), grade, fill=(15, 40, 110), font=f_table_b, anchor="mm")
        draw.text((tx0 + 1720, curr_y + 28), bobot, fill=(30, 30, 30), font=f_table, anchor="mm")
        draw.text((tx0 + 2000, curr_y + 28), total_b, fill=(30, 30, 30), font=f_table_b, anchor="mm")
        curr_y += th

    # Baris Total & IPK
    draw.rectangle([(tx0, curr_y), (tx0 + tx_w, curr_y + 60)], fill=(230, 238, 250), outline=(120, 140, 170), width=2)
    draw.text((tx0 + 640, curr_y + 30), "JUMLAH / TOTAL PRESTASI AKADEMIK", fill=(10, 30, 75), font=f_bold, anchor="mm")
    draw.text((tx0 + 1280, curr_y + 30), "22 SKS", fill=(10, 30, 75), font=f_bold, anchor="mm")
    draw.text((tx0 + 2000, curr_y + 30), "85.60", fill=(10, 30, 75), font=f_bold, anchor="mm")

    # Kotak Ringkasan IPK
    ry = curr_y + 90
    draw.rounded_rectangle([(tx0, ry), (tx0 + 950, ry + 160)], radius=16, fill=(255, 255, 255), outline=(15, 50, 120), width=2)
    draw.text((tx0 + 35, ry + 30), "• Indeks Prestasi Semester (IPS)", fill=(50, 50, 50), font=f_bold)
    draw.text((tx0 + 550, ry + 30), ":  3.89 (Sangat Memuaskan)", fill=(10, 35, 115), font=f_bold)
    draw.text((tx0 + 35, ry + 75), "• Indeks Prestasi Kumulatif (IPK)", fill=(50, 50, 50), font=f_bold)
    draw.text((tx0 + 550, ry + 75), ":  3.84 (Cum Laude)", fill=(10, 35, 115), font=f_bold)
    draw.text((tx0 + 35, ry + 120), "• Beban Maksimum SKS Berikutnya", fill=(50, 50, 50), font=f_bold)
    draw.text((tx0 + 550, ry + 120), ":  24 SKS", fill=(10, 35, 115), font=f_bold)

    # 5. PENGESAHAN DEKANAT & CAP DINAS
    sy = ry + 220
    draw.text((w - 680, sy), "Ditetapkan di : Tangerang Selatan", fill=(40, 40, 40), font=f_body)
    draw.text((w - 680, sy + 40), "Pada tanggal  : 15 Februari 2026", fill=(40, 40, 40), font=f_body)
    draw.text((w - 680, sy + 85), "Dekan Fakultas Sains dan Teknologi,", fill=(20, 20, 20), font=f_bold)

    # Tanda Tangan Basah
    draw_wet_signature_simple(draw, (w - 620, sy + 180), ink_color=(15, 38, 125, 240))

    # Stempel Dinas Ungu
    stempel_x, stempel_y = w - 740, sy + 175
    draw.ellipse([(stempel_x-80, stempel_y-80), (stempel_x+80, stempel_y+80)], outline=(110, 35, 150, 210), width=4)
    draw.ellipse([(stempel_x-70, stempel_y-70), (stempel_x+70, stempel_y+70)], outline=(110, 35, 150, 180), width=2)
    draw.text((stempel_x, stempel_y - 20), "DEKANAT", fill=(110, 35, 150, 210), font=load_font(18, bold=True), anchor="mm")
    draw.text((stempel_x, stempel_y + 15), "TERDAFTAR", fill=(110, 35, 150, 210), font=load_font(16, bold=True), anchor="mm")

    draw.text((w - 680, sy + 250), "Dr. Subekti Nurhadi, M.Si.", fill=(10, 10, 10), font=load_font(26, bold=True))
    draw.text((w - 680, sy + 290), "NIP. 197405121999031001", fill=(60, 60, 60), font=f_body)

    out_buf = BytesIO()
    img.save(out_buf, format="PNG", optimize=True)
    return out_buf.getvalue()

print("KHS Transcript generator defined successfully!")
