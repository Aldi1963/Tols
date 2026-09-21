"""
Kartu Tanda Pelajar (KTPel / Student ID SMA-SMK Indonesia) Generator
CR-80 High Definition PVC dengan Logo Resmi Tut Wuri Handayani, Pasfoto Pelajar Berseragam Putih Abu-Abu,
NISN 10 Digit Resmi, Barcode Code128, Tanda Tangan Basah Kepala Sekolah & Stempel Dinas.
"""

from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import os
import math
from pathlib import Path
from countries.utils import load_font, generate_initials_avatar
from ktm_generator import LOGOS_DIR, draw_wet_signature, get_indonesian_student_photo

SCHOOLS_DATA = [
    {
        "code": "SMAN1_JKT",
        "name": "SMA NEGERI 1 JAKARTA",
        "dinas": "PEMERINTAH PROVINSI DKI JAKARTA",
        "dinas_sub": "DINAS PENDIDIKAN DAN KEBUDAYAAN",
        "city": "Jakarta Pusat",
        "npsn": "20101589",
        "color": (20, 55, 125),      # Biru Tua SMAN 1
        "accent": (235, 185, 25),    # Emas
        "headmaster": "Drs. H. Mulyadi, M.Pd.",
        "nip": "196905141995121001",
    },
    {
        "code": "SMAN3_BDG",
        "name": "SMA NEGERI 3 BANDUNG",
        "dinas": "PEMERINTAH DAERAH PROVINSI JAWA BARAT",
        "dinas_sub": "DINAS PENDIDIKAN WILAYAH VII",
        "city": "Kota Bandung",
        "npsn": "20219742",
        "color": (15, 60, 110),
        "accent": (245, 190, 30),
        "headmaster": "H. Iwan Hermawan, S.Pd., M.M.",
        "nip": "197103221997021003",
    },
    {
        "code": "SMKN1_SBY",
        "name": "SMK NEGERI 1 SURABAYA",
        "dinas": "PEMERINTAH PROVINSI JAWA TIMUR",
        "dinas_sub": "DINAS PENDIDIKAN CABANG SURABAYA",
        "city": "Kota Surabaya",
        "npsn": "20532588",
        "color": (12, 75, 95),       # Teal SMK
        "accent": (250, 195, 35),
        "headmaster": "Dr. H. Anton Wahyudi, S.T., M.T.",
        "nip": "197408101999031004",
    },
    {
        "code": "SMAN1_YOG",
        "name": "SMA NEGERI 1 YOGYAKARTA",
        "dinas": "PEMERINTAH DAERAH DAERAH ISTIMEWA YOGYAKARTA",
        "dinas_sub": "DINAS PENDIDIKAN, PEMUDA, DAN OLAHRAGA",
        "city": "Kota Yogyakarta",
        "npsn": "20403161",
        "color": (25, 45, 85),
        "accent": (230, 175, 20),
        "headmaster": "Drs. Jumadi, M.Si.",
        "nip": "196811201994031005",
    },
]

JURUSAN_LIST = [
    ("MIPA", "Matematika dan Ilmu Pengetahuan Alam"),
    ("IPS", "Ilmu Pengetahuan Sosial"),
    ("RPL", "Rekayasa Perangkat Lunak"),
    ("TKJ", "Teknik Komputer dan Jaringan"),
    ("AKL", "Akuntansi dan Keuangan Lembaga"),
]

class KartuPelajarGenerator:
    """Generator Kartu Pelajar SMA/SMK Indonesia"""

    def __init__(self):
        self.schools = SCHOOLS_DATA

    def generate(
        self,
        first_name: str,
        last_name: str,
        school_code: str = "SMAN1_JKT",
        jurusan_info: tuple = None,
        gender: str = "Random",
        custom_photo: Image.Image = None,
    ) -> bytes:
        sch = None
        for s in self.schools:
            if s["code"] == school_code:
                sch = s
                break
        if not sch:
            sch = self.schools[0]

        is_smk = "SMK" in sch["name"]
        if not jurusan_info:
            if is_smk:
                jurusan_info = random.choice([
                    ("RPL", "Rekayasa Perangkat Lunak"),
                    ("TKJ", "Teknik Komputer dan Jaringan"),
                    ("AKL", "Akuntansi dan Keuangan Lembaga")
                ])
            else:
                jurusan_info = random.choice([
                    ("MIPA", "Matematika dan Ilmu Alam"),
                    ("IPS", "Ilmu Pengetahuan Sosial")
                ])
        jur_code, jur_name = jurusan_info
        jurusan_label = "Konsentrasi Keahlian" if is_smk else "Peminatan / Jurusan"

        w, h = 1920, 1120
        img = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Fonts
        f_gov = load_font(20, bold=True)
        f_sch = load_font(38, bold=True)
        f_sub = load_font(24, bold=True)
        f_nisn = load_font(38, bold=True)
        f_label = load_font(24, bold=False)
        f_val = load_font(28, bold=True)
        f_small = load_font(20, bold=False)
        f_tiny = load_font(16, bold=False)

        # 1. Background Kartu Halus
        for y_i in range(h):
            ratio = y_i / h
            r_c = int(250 + (255 - 250) * ratio)
            g_c = int(252 + (255 - 252) * ratio)
            b_c = int(255 - 4 * ratio)
            draw.line([(0, y_i), (w, y_i)], fill=(r_c, g_c, b_c))

        # 2. Header Bar Sekolah
        header_h = 200
        draw.rectangle([(0, 0), (w, header_h)], fill=sch["color"])
        draw.rectangle([(0, header_h), (w, header_h + 12)], fill=sch["accent"])

        # Border Luar PVC
        draw.rectangle([(10, 10), (w - 10, h - 10)], outline=sch["color"], width=4)
        draw.rectangle([(18, 18), (w - 18, h - 18)], outline=sch["accent"], width=2)

        # 3. Logo Tut Wuri Handayani Resmi (Kiri Atas)
        tut_wuri_path = LOGOS_DIR / "tut_wuri.png"
        if tut_wuri_path.exists():
            try:
                logo_raw = Image.open(tut_wuri_path).convert("RGBA")
                lw, lh = logo_raw.size
                t_lh = 145
                t_lw = int(lw * (t_lh / lh))
                logo_resized = logo_raw.resize((t_lw, t_lh), Image.Resampling.LANCZOS)
                
                badge_x = 115
                badge_y = header_h // 2
                draw.ellipse(
                    [(badge_x - 72, badge_y - 72), (badge_x + 72, badge_y + 72)],
                    fill=(255, 255, 255),
                    outline=sch["accent"],
                    width=3
                )
                img.paste(logo_resized, (badge_x - t_lw // 2, badge_y - t_lh // 2), logo_resized)
            except Exception:
                pass

        # Teks Header
        text_x = 215
        draw.text((text_x, 38), f"{sch['dinas']} • {sch['dinas_sub']}", fill=sch["accent"], font=f_gov, anchor="lt")
        draw.text((text_x, 78), sch["name"], fill=(255, 255, 255), font=f_sch, anchor="lt")
        draw.text((text_x, 140), f"KARTU TANDA PELAJAR  •  NPSN: {sch['npsn']}", fill=(225, 235, 255), font=f_sub, anchor="lt")

        # 4. Pasfoto Pelajar (Kiri)
        p_w, p_h = 320, 420
        p_x, p_y = 90, 255

        first_lower = first_name.lower()
        female_clues = ["siti", "nur", "sri", "dewi", "putri", "anisa", "ratna", "dian", "rini", "tri", "endang", "maya", "fitri", "ayu", "wulandari", "sarah"]
        if gender == "Random":
            gender = "Female" if any(c in first_lower for c in female_clues) else "Male"

        draw.rectangle([(p_x - 6, p_y - 6), (p_x + p_w + 6, p_y + p_h + 6)], fill=(255, 255, 255), outline=sch["color"], width=3)
        if custom_photo is not None:
            photo = custom_photo.resize((p_w, p_h), Image.Resampling.LANCZOS)
        else:
            photo = get_indonesian_student_photo((p_w, p_h), gender=gender)
            if photo is None:
                photo = generate_initials_avatar(first_name, last_name, (p_w, p_h), bg_color=sch["color"])
        img.paste(photo, (p_x, p_y))
        draw.rectangle([(p_x, p_y), (p_x + p_w, p_y + p_h)], outline=sch["accent"], width=2)

        # Tanda Tangan Pelajar
        draw.text((p_x + p_w // 2, p_y + p_h + 20), "Tanda Tangan Siswa:", fill=(100, 116, 139), font=f_small, anchor="mm")
        sig_seed = sum(ord(c) for c in f"{first_name}{last_name}") + 77
        siswa_sig = draw_wet_signature(width=p_w, height=110, ink_color=(10, 30, 100, 235), seed_val=sig_seed)
        img.paste(siswa_sig, (p_x, p_y + p_h + 32), siswa_sig)
        draw.line([(p_x + 20, p_y + p_h + 145), (p_x + p_w - 20, p_y + p_h + 145)], fill=(148, 163, 184), width=2)

        # 5. NISN & Biodata Siswa (Kanan)
        current_year = datetime.now().year
        # Format NISN 10 digit resmi (3 digit akhir tahun lahir + 7 digit acak)
        nisn = f"00{random.randint(6, 8)}{random.randint(1000000, 9999999)}"
        nis = f"{random.randint(11000, 99000)}"

        info_x = 470
        y_pos = 255
        box_w = w - info_x - 90

        # Kotak NISN
        draw.rectangle([(info_x, y_pos), (info_x + box_w, y_pos + 82)], fill=(240, 246, 255), outline=sch["color"], width=3)
        draw.rectangle([(info_x, y_pos), (info_x + box_w, y_pos + 28)], fill=sch["color"])
        draw.text((info_x + box_w // 2, y_pos + 14), "NOMOR INDUK SISWA NASIONAL (NISN)", fill=(255, 255, 255), font=f_small, anchor="mm")
        draw.text((info_x + box_w // 2, y_pos + 55), nisn, fill=sch["color"], font=f_nisn, anchor="mm")

        # Rincian Biodata
        y_pos += 115
        full_name = f"{first_name} {last_name}".upper()
        tgl_lahir = f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(2006, 2008)}"
        valid_until = current_year + 2

        details = [
            ("Nama Lengkap", full_name),
            ("Nomor Induk Siswa (NIS)", nis),
            ("Tempat, Tgl Lahir", f"{sch['city'].upper()}, {tgl_lahir}"),
            ((jurusan_label), f"{jur_code} - {jur_name.upper()}"),
            ("Status Keaktifan", "PESERTA DIDIK AKTIF"),
            ("Tahun Ajaran", f"{current_year}/{current_year + 1}"),
            ("Masa Berlaku", f"30 JUNI {valid_until}"),
        ]

        for label, val in details:
            draw.text((info_x, y_pos), label, fill=(100, 116, 139), font=f_label, anchor="lt")
            draw.text((info_x + 330, y_pos), ":", fill=(71, 85, 105), font=f_label, anchor="lt")
            
            c_val = (15, 23, 42)
            if label in ["Nama Lengkap", "Peminatan / Jurusan", "Konsentrasi Keahlian"]:
                c_val = sch["color"]
            draw.text((info_x + 360, y_pos - 2), val, fill=c_val, font=f_val, anchor="lt")
            y_pos += 52

        # 6. Barcode NISN & RFID
        bottom_y = 860
        bc_x = 90
        bc_w = 340
        bc_h = 95
        draw.rectangle([(bc_x, bottom_y), (bc_x + bc_w, bottom_y + bc_h)], fill=(255, 255, 255), outline=(200, 205, 215), width=1)
        
        cur_bx = bc_x + 18
        random.seed(int(nisn[:7]))
        while cur_bx < (bc_x + bc_w - 18):
            bw = random.choice([2, 3, 5])
            draw.rectangle([(cur_bx, bottom_y + 10), (cur_bx + bw, bottom_y + bc_h - 24)], fill=(15, 23, 42))
            cur_bx += bw + random.choice([2, 4, 5])
        random.seed()
        draw.text((bc_x + bc_w // 2, bottom_y + bc_h - 12), f"*{nisn}*", fill=(15, 23, 42), font=f_small, anchor="mm")

        # RFID Sim Chip
        chip_x = 470
        chip_y = bottom_y + 8
        draw.rectangle([(chip_x, chip_y), (chip_x + 115, chip_y + 82)], fill=(234, 179, 8), outline=(180, 130, 0), width=2)
        draw.line([(chip_x + 38, chip_y), (chip_x + 38, chip_y + 82)], fill=(180, 130, 0), width=2)
        draw.line([(chip_x + 78, chip_y), (chip_x + 78, chip_y + 82)], fill=(180, 130, 0), width=2)
        draw.line([(chip_x, chip_y + 41), (chip_x + 115, chip_y + 41)], fill=(180, 130, 0), width=2)
        draw.text((chip_x + 57, chip_y + 100), "STUDENT RFID", fill=(140, 150, 160), font=f_tiny, anchor="mm")

        # 7. Pengesahan Kepala Sekolah & Stempel Dinas
        st_box_x = w - 460
        st_box_y = bottom_y - 20

        draw.text((st_box_x + 150, st_box_y), f"{sch['city']}, 15 Juli {current_year}", fill=(71, 85, 105), font=f_small, anchor="mm")
        draw.text((st_box_x + 150, st_box_y + 24), "Kepala Sekolah,", fill=(15, 23, 42), font=f_label, anchor="mm")

        pejabat_sig = draw_wet_signature(width=300, height=100, ink_color=(15, 40, 125, 240), seed_val=612)
        img.paste(pejabat_sig, (st_box_x, st_box_y + 35), pejabat_sig)

        # Stempel Dinas Sekolah Ungu/Biru
        stamp_center_x = st_box_x + 90
        stamp_center_y = st_box_y + 80
        stamp_col = (40, 20, 130, 200)

        stamp_layer = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        stamp_draw = ImageDraw.Draw(stamp_layer)
        stamp_draw.ellipse([(stamp_center_x - 72, stamp_center_y - 72), (stamp_center_x + 72, stamp_center_y + 72)], outline=stamp_col, width=4)
        stamp_draw.ellipse([(stamp_center_x - 60, stamp_center_y - 60), (stamp_center_x + 60, stamp_center_y + 60)], outline=stamp_col, width=2)
        stamp_draw.text((stamp_center_x, stamp_center_y - 25), "DINAS PENDIDIKAN", fill=stamp_col, font=f_tiny, anchor="mm")
        stamp_draw.text((stamp_center_x, stamp_center_y), f"★ {sch['code'][:5]} ★", fill=stamp_col, font=f_small, anchor="mm")
        stamp_draw.text((stamp_center_x, stamp_center_y + 25), "TERAKREDITASI A", fill=stamp_col, font=f_tiny, anchor="mm")
        
        img.paste(Image.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, 0)), stamp_layer), (0, 0), stamp_layer)

        draw.text((st_box_x + 150, st_box_y + 135), sch["headmaster"], fill=(15, 23, 42), font=f_val, anchor="mm")
        draw.line([(st_box_x + 20, st_box_y + 148), (st_box_x + 280, st_box_y + 148)], fill=(15, 23, 42), width=2)
        draw.text((st_box_x + 150, st_box_y + 162), f"NIP. {sch['nip']}", fill=(71, 85, 105), font=f_small, anchor="mm")

        # Footer
        draw.line([(40, h - 45), (w - 40, h - 45)], fill=(226, 232, 240), width=2)
        draw.text(
            (w // 2, h - 22),
            f"KARTU TANDA PELAJAR RESMI • DAPODIK KEMENDIKBUD • VERIFIKASI NISN: HTTPS://NISN.DATA.KEMDIKBUD.GO.ID/PAGE/DATA?NISN={nisn}",
            fill=(148, 163, 184),
            font=f_tiny,
            anchor="mm",
        )

        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format="PNG", quality=95)
        return buf.getvalue()
