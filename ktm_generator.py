"""
KTM & Student ID Generator (Indonesia & International Ivy League / Oxbridge)
High Definition & Realistic dengan Logo Resmi, Tanda Tangan Basah Nyata,
Pasfoto Formal, Barcode, Chip RFID, dan Stempel Pengesahan.
"""

from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import os
import math
from pathlib import Path
from countries.utils import load_font, generate_initials_avatar

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "countries" / "assets"
LOGOS_DIR = ASSETS_DIR / "logos"
MHS_FOTO_DIR = BASE_DIR / "countries" / "foto_mhs"
INDO_FOTO_DIR = BASE_DIR / "countries" / "foto_indo"
FALLBACK_FOTO_DIR = BASE_DIR / "countries" / "foto"

UNIVERSITIES_ID = [
    {
        "code": "UT",
        "name": "UNIVERSITAS TERBUKA",
        "kemen": "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI",
        "city": "Tangerang Selatan",
        "country": "Indonesia",
        "logo_file": "logo_ut.png",
        "header_bg": (0, 51, 141),      # Biru UT
        "accent_color": (255, 209, 0),  # Kuning Emas UT
        "accent_dark": (0, 40, 115),
        "domain": "ut.ac.id",
        "nim_len": 9,
        "is_official_logo": True,
        "rektor_name": "Prof. Ojat Darojat, M.Bus., Ph.D.",
        "jabatan_ttd": "Rektor Universitas Terbuka",
    },
    {
        "code": "UI",
        "name": "UNIVERSITAS INDONESIA",
        "kemen": "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI",
        "city": "Depok",
        "country": "Indonesia",
        "logo_file": "logo_ui.png",
        "header_bg": (26, 36, 56),
        "accent_color": (255, 204, 0),
        "accent_dark": (180, 130, 0),
        "domain": "ui.ac.id",
        "nim_len": 10,
        "is_official_logo": True,
        "rektor_name": "Prof. Ari Kuncoro, S.E., M.A., Ph.D.",
        "jabatan_ttd": "Direktur Pendidikan & Akademik",
    },
    {
        "code": "UGM",
        "name": "UNIVERSITAS GADJAH MADA",
        "kemen": "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI",
        "city": "Yogyakarta",
        "country": "Indonesia",
        "logo_file": "logo_ugm.png",
        "header_bg": (15, 45, 95),
        "accent_color": (212, 160, 23),
        "accent_dark": (13, 71, 161),
        "domain": "ugm.ac.id",
        "nim_len": 10,
        "is_official_logo": True,
        "rektor_name": "Prof. dr. Ova Emilia, M.Med.Ed., Sp.OG(K).",
        "jabatan_ttd": "Direktur Administrasi Akademik",
    },
    {
        "code": "ITB",
        "name": "INSTITUT TEKNOLOGI BANDUNG",
        "kemen": "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI",
        "city": "Bandung",
        "country": "Indonesia",
        "logo_file": "logo_itb.png",
        "header_bg": (10, 35, 70),
        "accent_color": (0, 168, 232),
        "accent_dark": (0, 95, 145),
        "domain": "itb.ac.id",
        "nim_len": 8,
        "is_official_logo": True,
        "rektor_name": "Prof. Reini Wirahadikusumah, Ph.D.",
        "jabatan_ttd": "Direktur Pendidikan ITB",
    },
    {
        "code": "UB",
        "name": "UNIVERSITAS BRAWIJAYA",
        "kemen": "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI",
        "city": "Malang",
        "country": "Indonesia",
        "logo_file": None,
        "header_bg": (18, 42, 82),
        "accent_color": (245, 185, 20),
        "accent_dark": (12, 60, 120),
        "domain": "ub.ac.id",
        "nim_len": 11,
        "is_official_logo": False,
        "rektor_name": "Prof. Widodo, S.Si., M.Si., Ph.D.Med.Sc.",
        "jabatan_ttd": "Wakil Rektor Bidang Akademik",
    },
]

UNIVERSITIES_GLOBAL = [
    {
        "code": "HARVARD",
        "name": "HARVARD UNIVERSITY",
        "kemen": "FACULTY OF ARTS AND SCIENCES",
        "city": "Cambridge, MA",
        "country": "United States",
        "logo_file": None,
        "header_bg": (165, 28, 48),     # Harvard Crimson
        "accent_color": (255, 255, 255),
        "accent_dark": (120, 20, 35),
        "domain": "harvard.edu",
        "nim_len": 8,
        "is_official_logo": False,
        "rektor_name": "Alan M. Garber, Ph.D.",
        "jabatan_ttd": "Office of the University Registrar",
    },
    {
        "code": "MIT",
        "name": "MASSACHUSETTS INSTITUTE OF TECHNOLOGY",
        "kemen": "OFFICE OF THE REGISTRAR",
        "city": "Cambridge, MA",
        "country": "United States",
        "logo_file": None,
        "header_bg": (117, 0, 20),      # MIT Cardinal Red
        "accent_color": (155, 160, 165), # MIT Silver Gray
        "accent_dark": (90, 0, 15),
        "domain": "mit.edu",
        "nim_len": 9,
        "is_official_logo": False,
        "rektor_name": "Sally Kornbluth, Ph.D.",
        "jabatan_ttd": "Dean for Undergraduate Education",
    },
    {
        "code": "STANFORD",
        "name": "STANFORD UNIVERSITY",
        "kemen": "OFFICE OF THE UNIVERSITY REGISTRAR",
        "city": "Stanford, CA",
        "country": "United States",
        "logo_file": None,
        "header_bg": (140, 21, 21),     # Stanford Cardinal
        "accent_color": (245, 245, 240),
        "accent_dark": (100, 15, 15),
        "domain": "stanford.edu",
        "nim_len": 8,
        "is_official_logo": False,
        "rektor_name": "Richard Saller, Ph.D.",
        "jabatan_ttd": "Registrar and Student Affairs",
    },
    {
        "code": "OXFORD",
        "name": "UNIVERSITY OF OXFORD",
        "kemen": "ACADEMIC SERVICES AND UNIVERSITY REGISTRY",
        "city": "Oxford",
        "country": "United Kingdom",
        "logo_file": None,
        "header_bg": (0, 33, 71),       # Oxford Blue
        "accent_color": (195, 165, 105), # Oxford Gold
        "accent_dark": (0, 20, 50),
        "domain": "ox.ac.uk",
        "nim_len": 7,
        "is_official_logo": False,
        "rektor_name": "Professor Irene Tracey, CBE, FMedSci",
        "jabatan_ttd": "Academic Registrar",
    },
]

ALL_UNIVERSITIES = UNIVERSITIES_ID + UNIVERSITIES_GLOBAL

UT_PROGRAMS = [
    ("Fakultas Sains dan Teknologi (FST)", "S1 - Sistem Informasi"),
    ("Fakultas Sains dan Teknologi (FST)", "S1 - Sains Data"),
    ("Fakultas Sains dan Teknologi (FST)", "S1 - Matematika"),
    ("Fakultas Ekonomi dan Bisnis (FEB)", "S1 - Manajemen"),
    ("Fakultas Ekonomi dan Bisnis (FEB)", "S1 - Akuntansi"),
    ("Fakultas Ekonomi dan Bisnis (FEB)", "S1 - Ekonomi Pembangunan"),
    ("Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik (FHISIP)", "S1 - Ilmu Komunikasi"),
    ("Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik (FHISIP)", "S1 - Ilmu Hukum"),
    ("Fakultas Hukum, Ilmu Sosial, dan Ilmu Politik (FHISIP)", "S1 - Ilmu Administrasi Bisnis"),
    ("Fakultas Keguruan dan Ilmu Pendidikan (FKIP)", "S1 - Pendidikan Bahasa Inggris"),
]

UPBJJ_CITIES = [
    "Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Semarang", "Malang", 
    "Medan", "Makassar", "Denpasar", "Palembang", "Pekanbaru", "Banjarmasin"
]

def get_indonesian_student_photo(size: Tuple[int, int], gender: str) -> Image.Image:
    # Kumpulkan seluruh variasi foto Indonesia berdasarkan gender
    candidates = []
    
    # 1. Koleksi foto_indo (pria: p1, p2, p4, p7, p8, p10 | wanita: w1, w2, w3, w4, w5)
    prefix = "w" if gender == "Female" else "p"
    if INDO_FOTO_DIR.exists():
        candidates.extend([p for p in INDO_FOTO_DIR.glob(f"{prefix}*.png") if p.is_file()])
        
    # 2. Tambahkan foto master foto_mhs
    mhs_file = "wanita_indo.png" if gender == "Female" else "pria_indo.png"
    if (MHS_FOTO_DIR / mhs_file).exists():
        candidates.append(MHS_FOTO_DIR / mhs_file)

    # 3. Fallback jika masih kosong
    if not candidates and FALLBACK_FOTO_DIR.exists():
        candidates.extend([p for p in FALLBACK_FOTO_DIR.glob(f"{prefix}*.png") if p.is_file()])

    if candidates:
        chosen_path = random.choice(candidates)
        try:
            im = Image.open(chosen_path).convert("RGB")
            return im.resize(size, Image.Resampling.LANCZOS)
        except Exception:
            pass
    return None


def draw_wet_signature(width: int = 340, height: int = 150, ink_color=(15, 35, 115, 240), seed_val: int = None) -> Image.Image:
    if seed_val:
        random.seed(seed_val)
    
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    start_x = random.randint(30, 60)
    start_y = random.randint(height // 2 - 10, height // 2 + 20)
    points = [(start_x, start_y)]

    peak_y = random.randint(18, 35)
    dip_y = random.randint(height - 45, height - 25)
    points.append((start_x + random.randint(18, 30), peak_y))
    points.append((start_x + random.randint(35, 50), dip_y))
    points.append((start_x + random.randint(48, 65), height // 2))

    cur_x = points[-1][0]
    loops = random.randint(3, 5)
    for _ in range(loops):
        cur_x += random.randint(18, 28)
        loop_y = (height // 2) + random.randint(-18, 18)
        points.append((cur_x, loop_y))

    end_x = cur_x + random.randint(25, 45)
    end_y = random.randint(25, 45)
    points.append((end_x, end_y))

    under_pts = [
        (start_x + random.randint(10, 25), height - random.randint(20, 30)),
        (width // 2 + random.randint(-15, 15), height - random.randint(18, 26)),
        (end_x + random.randint(15, 30), height - random.randint(25, 35))
    ]

    def render_spline(pts: List[Tuple[float, float]], base_w: int = 3):
        fine = []
        for i in range(len(pts) - 1):
            p0 = pts[max(0, i - 1)]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[min(len(pts) - 1, i + 2)]
            steps = 14
            for s in range(steps):
                t = s / float(steps)
                tx = 0.5 * ((2*p1[0]) + (-p0[0] + p2[0])*t + (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0])*t*t + (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0])*t*t*t)
                ty = 0.5 * ((2*p1[1]) + (-p0[1] + p2[1])*t + (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1])*t*t + (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1])*t*t*t)
                fine.append((tx, ty))

        for k in range(len(fine) - 1):
            p_a = fine[k]
            p_b = fine[k + 1]
            w_stroke = base_w + math.sin(k * 0.35) * 0.8
            draw.line([p_a, p_b], fill=ink_color, width=max(1, int(round(w_stroke))))

    render_spline(points, base_w=random.choice([3, 4]))
    render_spline(under_pts, base_w=2)

    dot_pos = (under_pts[-1][0] + random.randint(8, 14), under_pts[-1][1] + random.randint(-4, 4))
    draw.ellipse([(dot_pos[0]-2, dot_pos[1]-2), (dot_pos[0]+2, dot_pos[1]+2)], fill=ink_color)

    random.seed()
    return img


class KtmGenerator:
    """Generator Kartu Tanda Mahasiswa (KTM) Indonesia & Global"""

    def __init__(self):
        self.universities_id = UNIVERSITIES_ID
        self.universities_global = UNIVERSITIES_GLOBAL
        self.all_universities = ALL_UNIVERSITIES

    def list_universities(self) -> List[Dict]:
        return self.universities_id

    def list_global_universities(self) -> List[Dict]:
        return self.universities_global

    def generate(
        self,
        first_name: str,
        last_name: str,
        univ_code: str = "UT",
        major_info: tuple = None,
        gender: str = "Random",
        custom_photo: Image.Image = None,
    ) -> bytes:
        univ = None
        if univ_code:
            for u in self.all_universities:
                if u["code"].upper() == univ_code.upper():
                    univ = u
                    break
        if not univ:
            univ = self.universities_id[0]

        is_global = univ.get("country") != "Indonesia"

        if univ["code"] == "UT":
            if not major_info:
                major_info = random.choice(UT_PROGRAMS)
            fakultas, prodi = major_info
            upbjj_kota = random.choice(UPBJJ_CITIES)
        elif is_global:
            fakultas = "Department of Computer Science"
            prodi = "B.S. in Computer Science"
            upbjj_kota = univ["city"]
        else:
            fakultas = "Fakultas Ilmu Komputer"
            prodi = "S1 - Teknik Informatika"
            upbjj_kota = univ["city"]

        w, h = 1920, 1120
        img = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        try:
            f_kemen = load_font(20, bold=True)
            f_univ = load_font(38, bold=True)
            f_title = load_font(26, bold=True)
            f_nim = load_font(38, bold=True)
            f_label = load_font(24, bold=False)
            f_val = load_font(28, bold=True)
            f_small = load_font(20, bold=False)
            f_tiny = load_font(16, bold=False)
        except Exception:
            f_kemen = f_univ = f_title = f_nim = f_label = f_val = f_small = f_tiny = ImageFont.load_default()

        for y_i in range(h):
            ratio = y_i / h
            r_c = int(248 + (255 - 248) * ratio)
            g_c = int(251 + (255 - 251) * ratio)
            b_c = int(255 - 5 * ratio)
            draw.line([(0, y_i), (w, y_i)], fill=(r_c, g_c, b_c))

        header_h = 195
        h_bg = univ["header_bg"]
        accent_c = univ["accent_color"]
        draw.rectangle([(0, 0), (w, header_h)], fill=h_bg)
        draw.rectangle([(0, header_h), (w, header_h + 14)], fill=accent_c)

        draw.rectangle([(10, 10), (w - 10, h - 10)], outline=h_bg, width=4)
        draw.rectangle([(18, 18), (w - 18, h - 18)], outline=accent_c, width=2)

        # Logo UT / University Badge
        logo_placed = False
        logo_path = LOGOS_DIR / (univ.get("logo_file") or "")
        if univ.get("logo_file") and logo_path.exists():
            try:
                logo_raw = Image.open(logo_path).convert("RGBA")
                lw, lh = logo_raw.size
                target_lh = 135
                target_lw = int(lw * (target_lh / lh))
                logo_resized = logo_raw.resize((target_lw, target_lh), Image.Resampling.LANCZOS)
                
                badge_center_x = 115
                badge_center_y = header_h // 2
                draw.ellipse(
                    [(badge_center_x - 72, badge_center_y - 72), (badge_center_x + 72, badge_center_y + 72)],
                    fill=(255, 255, 255),
                    outline=accent_c,
                    width=3
                )
                img.paste(logo_resized, (badge_center_x - target_lw // 2, badge_center_y - target_lh // 2), logo_resized)
                logo_placed = True
            except Exception:
                logo_placed = False

        if not logo_placed:
            lx, ly = 115, header_h // 2
            draw.ellipse([(lx - 65, ly - 65), (lx + 65, ly + 65)], fill=accent_c)
            draw.ellipse([(lx - 58, ly - 58), (lx + 58, ly + 58)], fill=h_bg)
            draw.text((lx, ly), univ["code"][:4], fill=accent_c, font=f_univ, anchor="mm")

        text_x = 215
        draw.text((text_x, 42), univ["kemen"], fill=accent_c, font=f_kemen, anchor="lm")
        draw.text((text_x, 88), univ["name"], fill=(255, 255, 255), font=f_univ, anchor="lm")
        sub_title = "STUDENT IDENTITY CARD  •  OFFICIAL RECORD" if is_global else "KARTU TANDA MAHASISWA  •  STUDENT IDENTITY CARD"
        draw.text((text_x, 142), sub_title, fill=(225, 235, 255), font=f_title, anchor="lm")

        # Pasfoto Mahasiswa (Custom Photo jika dikirim user, atau kurasi foto Indonesia)
        p_w, p_h = 320, 420
        p_x, p_y = 90, 250

        first_lower = first_name.lower()
        female_clues = ["siti", "nur", "sri", "dewi", "putri", "anisa", "ratna", "dian", "rini", "tri", "endang", "maya", "fitri", "ayu", "wulandari", "sarah"]
        if gender == "Random":
            gender = "Female" if any(c in first_lower for c in female_clues) else "Male"

        draw.rectangle([(p_x - 6, p_y - 6), (p_x + p_w + 6, p_y + p_h + 6)], fill=(255, 255, 255), outline=h_bg, width=3)
        
        if custom_photo is not None:
            photo = custom_photo.resize((p_w, p_h), Image.Resampling.LANCZOS)
        else:
            photo = get_indonesian_student_photo((p_w, p_h), gender=gender)
            if photo is None:
                photo = generate_initials_avatar(first_name, last_name, (p_w, p_h), bg_color=h_bg)

        img.paste(photo, (p_x, p_y))
        draw.rectangle([(p_x, p_y), (p_x + p_w, p_y + p_h)], outline=accent_c, width=2)

        # Tanda Tangan Basah Mahasiswa
        sign_label = "Student Signature:" if is_global else "Tanda Tangan Pemegang Kartu:"
        draw.text((p_x + p_w // 2, p_y + p_h + 20), sign_label, fill=(100, 116, 139), font=f_small, anchor="mm")
        
        sig_seed = sum(ord(c) for c in f"{first_name}{last_name}") + 101
        mhs_signature = draw_wet_signature(width=p_w, height=110, ink_color=(10, 30, 100, 235), seed_val=sig_seed)
        img.paste(mhs_signature, (p_x, p_y + p_h + 32), mhs_signature)
        draw.line([(p_x + 20, p_y + p_h + 145), (p_x + p_w - 20, p_y + p_h + 145)], fill=(148, 163, 184), width=2)

        info_x = 470
        current_year = datetime.now().year
        angkatan = random.randint(current_year - 3, current_year - 1)
        valid_until = angkatan + 5

        if univ["code"] == "UT":
            nim = f"0{random.randint(40, 49)}{random.randint(100000, 999999)}"
        elif is_global:
            nim = str(random.randint(10000000, 99999999))
        else:
            nim = f"{str(angkatan)[-2:]}{random.randint(10, 99)}{random.randint(100000, 999999)}"

        y_pos = 250
        nim_box_w = w - info_x - 90

        nim_label = "STUDENT IDENTIFICATION NUMBER (ID)" if is_global else "NOMOR INDUK MAHASISWA (NIM)"
        draw.rectangle([(info_x, y_pos), (info_x + nim_box_w, y_pos + 82)], fill=(240, 246, 255), outline=h_bg, width=3)
        draw.rectangle([(info_x, y_pos), (info_x + nim_box_w, y_pos + 28)], fill=h_bg)
        draw.text((info_x + nim_box_w // 2, y_pos + 14), nim_label, fill=(255, 255, 255), font=f_small, anchor="mm")
        draw.text((info_x + nim_box_w // 2, y_pos + 55), nim, fill=univ["accent_dark"], font=f_nim, anchor="mm")

        y_pos += 115
        full_name = f"{first_name} {last_name}".upper()
        tgl_lahir = f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(1998, 2004)}"

        if is_global:
            details = [
                ("Full Name", full_name),
                ("Date of Birth", tgl_lahir),
                ("Degree & Major", prodi.upper()),
                ("Academic Division", fakultas.upper()),
                ("Enrollment Status", "UNDERGRADUATE • ACTIVE STUDENT"),
                ("Academic Year", f"{angkatan} - {valid_until}"),
                ("Valid Through", f"JUNE {valid_until}"),
            ]
        elif univ["code"] == "UT":
            details = [
                ("Nama Lengkap", full_name),
                ("Tempat, Tgl Lahir", f"{upbjj_kota.upper()}, {tgl_lahir}"),
                ("Program Studi", prodi.upper()),
                ("Fakultas", fakultas.upper()),
                ("UPBJJ - UT", f"UT {upbjj_kota.upper()}"),
                ("Jenjang / Status", "STRATA 1 (S1)  •  MAHASISWA AKTIF"),
                ("Masa Berlaku", f"31 AGUSTUS {valid_until}"),
            ]
        else:
            details = [
                ("Nama Lengkap", full_name),
                ("Tempat, Tgl Lahir", f"{upbjj_kota.upper()}, {tgl_lahir}"),
                ("Program Studi", prodi.upper()),
                ("Fakultas", fakultas.upper()),
                ("Jenjang / Status", "STRATA 1 (S1)  •  MAHASISWA AKTIF"),
                ("Tahun Angkatan", f"{angkatan} / {angkatan + 1}"),
                ("Masa Berlaku", f"31 AGUSTUS {valid_until}"),
            ]

        for label, val in details:
            draw.text((info_x, y_pos), label, fill=(100, 116, 139), font=f_label, anchor="lt")
            draw.text((info_x + 230, y_pos), ":", fill=(71, 85, 105), font=f_label, anchor="lt")
            
            c_val = (15, 23, 42)
            if label in ["Nama Lengkap", "Full Name", "Program Studi", "UPBJJ - UT", "Degree & Major"]:
                c_val = (0, 45, 120) if not is_global else (120, 20, 35)
            draw.text((info_x + 255, y_pos - 2), val, fill=c_val, font=f_val, anchor="lt")
            y_pos += 52

        bottom_y = 860

        bc_x = 90
        bc_w = 340
        bc_h = 95
        draw.rectangle([(bc_x, bottom_y), (bc_x + bc_w, bottom_y + bc_h)], fill=(255, 255, 255), outline=(200, 205, 215), width=1)
        
        cur_bx = bc_x + 18
        random.seed(int(nim[:7]))
        while cur_bx < (bc_x + bc_w - 18):
            bw = random.choice([2, 3, 5])
            draw.rectangle([(cur_bx, bottom_y + 10), (cur_bx + bw, bottom_y + bc_h - 24)], fill=(15, 23, 42))
            cur_bx += bw + random.choice([2, 4, 5])
        random.seed()
        draw.text((bc_x + bc_w // 2, bottom_y + bc_h - 12), f"*{nim}*", fill=(15, 23, 42), font=f_small, anchor="mm")

        chip_x = 470
        chip_y = bottom_y + 8
        draw.rectangle([(chip_x, chip_y), (chip_x + 115, chip_y + 82)], fill=(234, 179, 8), outline=(180, 130, 0), width=2)
        draw.line([(chip_x + 38, chip_y), (chip_x + 38, chip_y + 82)], fill=(180, 130, 0), width=2)
        draw.line([(chip_x + 78, chip_y), (chip_x + 78, chip_y + 82)], fill=(180, 130, 0), width=2)
        draw.line([(chip_x, chip_y + 41), (chip_x + 115, chip_y + 41)], fill=(180, 130, 0), width=2)
        draw.text((chip_x + 57, chip_y + 100), "SECURE RFID", fill=(140, 150, 160), font=f_tiny, anchor="mm")

        st_box_x = w - 460
        st_box_y = bottom_y - 20

        issued_text = f"Issued: Sept 01, {angkatan}" if is_global else f"{upbjj_kota}, 01 September {angkatan}"
        draw.text((st_box_x + 150, st_box_y), issued_text, fill=(71, 85, 105), font=f_small, anchor="mm")
        draw.text((st_box_x + 150, st_box_y + 24), univ["jabatan_ttd"], fill=(15, 23, 42), font=f_label, anchor="mm")

        pejabat_sig = draw_wet_signature(width=300, height=100, ink_color=(15, 40, 125, 240), seed_val=999)
        img.paste(pejabat_sig, (st_box_x, st_box_y + 35), pejabat_sig)

        stamp_center_x = st_box_x + 90
        stamp_center_y = st_box_y + 80
        stamp_col = (40, 20, 130, 200)

        stamp_layer = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        stamp_draw = ImageDraw.Draw(stamp_layer)
        stamp_draw.ellipse([(stamp_center_x - 72, stamp_center_y - 72), (stamp_center_x + 72, stamp_center_y + 72)], outline=stamp_col, width=4)
        stamp_draw.ellipse([(stamp_center_x - 60, stamp_center_y - 60), (stamp_center_x + 60, stamp_center_y + 60)], outline=stamp_col, width=2)
        stamp_top = "OFFICIAL REGISTRAR" if is_global else "BIRO AKADEMIK"
        stamp_draw.text((stamp_center_x, stamp_center_y - 25), stamp_top, fill=stamp_col, font=f_tiny, anchor="mm")
        stamp_draw.text((stamp_center_x, stamp_center_y), f"★ {univ['code'][:4]} ★", fill=stamp_col, font=f_small, anchor="mm")
        stamp_bot = "VERIFIED" if is_global else "TERDAFTAR"
        stamp_draw.text((stamp_center_x, stamp_center_y + 25), stamp_bot, fill=stamp_col, font=f_tiny, anchor="mm")
        
        img.paste(Image.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, 0)), stamp_layer), (0, 0), stamp_layer)

        draw.text((st_box_x + 150, st_box_y + 135), univ["rektor_name"], fill=(15, 23, 42), font=f_val, anchor="mm")
        draw.line([(st_box_x + 20, st_box_y + 148), (st_box_x + 280, st_box_y + 148)], fill=(15, 23, 42), width=2)
        nip_text = "REG-ID: 19680324199303" if is_global else "NIP. 196803241993031002"
        draw.text((st_box_x + 150, st_box_y + 162), nip_text, fill=(71, 85, 105), font=f_small, anchor="mm")

        draw.line([(40, h - 45), (w - 40, h - 45)], fill=(226, 232, 240), width=2)
        footer_t = f"OFFICIAL ELECTRONIC STUDENT RECORD • {univ['name']} • VERIFY: HTTPS://PORTAL.{univ['domain']}/VERIFY/{nim}" if is_global else f"KARTU TANDA MAHASISWA ELEKTRONIK • DITERBITKAN OLEH {univ['name']} • VERIFIKASI RESMI: HTTPS://SIA.{univ['domain']}/VERIFY/{nim}"
        draw.text((w // 2, h - 22), footer_t, fill=(148, 163, 184), font=f_tiny, anchor="mm")

        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format="PNG", quality=95)
        return buf.getvalue()
