"""
SKMA (Surat Keterangan Mahasiswa Aktif) Generator
Menghasilkan Surat Resmi Keterangan Aktif Kuliah (Proof of Enrollment)
berstandar naskah dinas universitas Indonesia dan internasional untuk SheerID / GitHub Student / Canva.
"""

from typing import Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import os
import math
from pathlib import Path
from countries.utils import load_font
from ktm_generator import LOGOS_DIR, draw_wet_signature

class SkmaGenerator:
    """Generator Surat Keterangan Mahasiswa Aktif"""

    def generate(
        self,
        full_name: str,
        nim: str = None,
        univ_code: str = "UT",
        prodi: str = None,
        fakultas: str = None,
        upbjj: str = "Jakarta",
    ) -> bytes:
        # Resolusi Standar A4 300 DPI (2480 x 3508)
        w, h = 2480, 3508
        img = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Fonts
        f_kemen = load_font(40, bold=True)
        f_univ = load_font(56, bold=True)
        f_sub = load_font(32, bold=False)
        f_title = load_font(50, bold=True)
        f_nomor = load_font(34, bold=False)
        f_body = load_font(38, bold=False)
        f_body_bold = load_font(38, bold=True)
        f_small = load_font(30, bold=False)

        current_year = datetime.now().year
        if not nim:
            nim = f"0{random.randint(40, 49)}{random.randint(100000, 999999)}"
        if not prodi:
            prodi = "Sistem Informasi"
        if not fakultas:
            fakultas = "Fakultas Sains dan Teknologi"

        # 1. KOP SURAT RESMI
        margin_x = 180
        top_y = 120

        # Pasang Logo UT
        logo_path = LOGOS_DIR / "logo_ut.png"
        if logo_path.exists():
            try:
                logo_raw = Image.open(logo_path).convert("RGBA")
                lw, lh = logo_raw.size
                t_lh = 280
                t_lw = int(lw * (t_lh / lh))
                logo_resized = logo_raw.resize((t_lw, t_lh), Image.Resampling.LANCZOS)
                img.paste(logo_resized, (margin_x, top_y + 10), logo_resized)
            except Exception:
                pass

        kop_x = margin_x + 320
        draw.text((kop_x, top_y + 20), "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI", fill=(15, 23, 42), font=f_kemen, anchor="lt")
        draw.text((kop_x, top_y + 75), "UNIVERSITAS TERBUKA", fill=(0, 51, 141), font=f_univ, anchor="lt")
        draw.text((kop_x, top_y + 155), f"UNIT PROGRAM BELAJAR JARAK JAUH (UPBJJ - UT) {upbjj.upper()}", fill=(15, 23, 42), font=f_sub, anchor="lt")
        draw.text((kop_x, top_y + 205), f"Jalan Ahmad Yani No. 45 {upbjj} • Laman: https://www.ut.ac.id • Pos-el: ut-{upbjj.lower()}@ecampus.ut.ac.id", fill=(100, 116, 139), font=f_small, anchor="lt")

        # Garis Kop Ganda
        line_y = top_y + 320
        draw.line([(margin_x, line_y), (w - margin_x, line_y)], fill=(0, 51, 141), width=6)
        draw.line([(margin_x, line_y + 12), (w - margin_x, line_y + 12)], fill=(255, 209, 0), width=3)

        # 2. JUDUL NASKAH DINAS
        title_y = line_y + 140
        draw.text((w // 2, title_y), "SURAT KETERANGAN MAHASISWA AKTIF", fill=(15, 23, 42), font=f_title, anchor="mm")
        nomor_sk = f"Nomor: B/{random.randint(1100, 9900)}/UN31.WR1/PK.01.00/{current_year}"
        draw.text((w // 2, title_y + 60), nomor_sk, fill=(51, 65, 85), font=f_nomor, anchor="mm")
        draw.line([(w // 2 - 380, title_y + 28), (w // 2 + 380, title_y + 28)], fill=(15, 23, 42), width=3)

        # 3. KONSIDERANS PEMBUKA
        y = title_y + 160
        draw.text(
            (margin_x, y),
            "Pimpinan Universitas Terbuka dengan ini menerangkan dengan sebenarnya bahwa:",
            fill=(15, 23, 42),
            font=f_body,
            anchor="lt"
        )

        # 4. TABEL BIODATA MAHASISWA
        y += 90
        bio_x = margin_x + 80
        col_w = 480

        fields = [
            ("Nama Lengkap", full_name.upper()),
            ("Nomor Induk Mahasiswa (NIM)", nim),
            ("Tempat, Tanggal Lahir", f"{upbjj}, {random.randint(1,28):02d}/{random.randint(1,12):02d}/{random.randint(1999, 2004)}"),
            ("Fakultas", fakultas),
            ("Program Studi", f"S1 - {prodi}"),
            ("Jenjang Pendidikan", "Strata Satu (S1)"),
            ("Semester / Tahun Akademik", f"Ganjil / Genap Tahun Akademik {current_year}/{current_year + 1}"),
            ("Status Akademik", "AKTIF KULIAH"),
        ]

        for label, val in fields:
            draw.text((bio_x, y), label, fill=(51, 65, 85), font=f_body, anchor="lt")
            draw.text((bio_x + col_w, y), ":", fill=(51, 65, 85), font=f_body, anchor="lt")
            draw.text((bio_x + col_w + 40, y), val, fill=(15, 23, 42), font=f_body_bold, anchor="lt")
            y += 82

        # 5. DIKTUM KETERANGAN KEAKTIFAN
        y += 40
        par1 = (
            f"Adalah benar yang bersangkutan saat ini tercatat sebagai mahasiswa aktif jenjang Sarjana (S1) pada Program Studi "
            f"{prodi}, {fakultas} Universitas Terbuka pada Tahun Akademik {current_year}/{current_year + 1}, serta berkelakuan baik "
            "dan tidak sedang menjalani sanksi akademik."
        )

        par2 = (
            "Surat keterangan ini diterbitkan secara sah atas permohonan yang bersangkutan sebagai bukti pemenuhan verifikasi "
            "status mahasiswa aktif (Student Enrollment Verification), permohonan fasilitas/diskon pendidikan, dan/atau keperluan "
            "akademik resmi lainnya."
        )

        par3 = (
            "Demikian surat keterangan ini dibuat dengan sebenarnya untuk dapat dipergunakan sebagaimana mestinya."
        )

        def wrap_draw_text(text: str, start_y: int, max_w: int = w - 2*margin_x, line_h: int = 58) -> int:
            words = text.split()
            lines = []
            cur = ""
            for w_item in words:
                test = (cur + " " + w_item).strip()
                bbox = draw.textbbox((0, 0), test, font=f_body)
                if (bbox[2] - bbox[0]) <= max_w:
                    cur = test
                else:
                    lines.append(cur)
                    cur = w_item
            if cur:
                lines.append(cur)

            cur_y = start_y
            for line in lines:
                draw.text((margin_x, cur_y), line, fill=(15, 23, 42), font=f_body, anchor="lt")
                cur_y += line_h
            return cur_y

        y = wrap_draw_text(par1, y) + 40
        y = wrap_draw_text(par2, y) + 40
        y = wrap_draw_text(par3, y) + 80

        # 6. PENGESAHAN REKTORAT / DEKANAT (KANAN BAWAH)
        sign_x = w - margin_x - 750
        sign_y = y + 20

        today_id = datetime.now().strftime("%d September %Y")
        draw.text((sign_x, sign_y), f"{upbjj}, {today_id}", fill=(15, 23, 42), font=f_body, anchor="lt")
        draw.text((sign_x, sign_y + 55), "a.n. Rektor Universitas Terbuka", fill=(51, 65, 85), font=f_body, anchor="lt")
        draw.text((sign_x, sign_y + 110), "Direktur Administrasi Akademik & Kelulusan,", fill=(15, 23, 42), font=f_body_bold, anchor="lt")

        # Tanda Tangan Basah Pejabat Kampus
        sig_img = draw_wet_signature(width=480, height=160, ink_color=(15, 40, 130, 240), seed_val=882)
        img.paste(sig_img, (sign_x + 40, sign_y + 160), sig_img)

        # Stempel Basah Institusi (Menimpa tanda tangan)
        st_cx = sign_x + 120
        st_cy = sign_y + 240
        st_col = (40, 20, 135, 195)

        stamp_layer = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        s_draw = ImageDraw.Draw(stamp_layer)
        s_draw.ellipse([(st_cx - 130, st_cy - 130), (st_cx + 130, st_cy + 130)], outline=st_col, width=6)
        s_draw.ellipse([(st_cx - 110, st_cy - 110), (st_cx + 110, st_cy + 110)], outline=st_col, width=3)
        s_draw.text((st_cx, st_cy - 45), "KEMENTERIAN PENDIDIKAN", fill=st_col, font=f_small, anchor="mm")
        s_draw.text((st_cx, st_cy), "★ UNIVERSITAS TERBUKA ★", fill=st_col, font=f_nomor, anchor="mm")
        s_draw.text((st_cx, st_cy + 45), "BIRO AKADEMIK", fill=st_col, font=f_small, anchor="mm")
        img.paste(Image.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, 0)), stamp_layer), (0, 0), stamp_layer)

        # Nama & NIP Pejabat
        sign_end_y = sign_y + 350
        draw.text((sign_x, sign_end_y), "Dr. Fauzi Rahman, S.Kom., M.Cs.", fill=(15, 23, 42), font=f_univ, anchor="lt")
        draw.line([(sign_x, sign_end_y + 70), (sign_x + 650, sign_end_y + 70)], fill=(15, 23, 42), width=3)
        draw.text((sign_x, sign_end_y + 85), "NIP. 197508122002121003", fill=(51, 65, 85), font=f_body, anchor="lt")

        # 7. QR CODE VERIFIKASI RESMI (KIRI BAWAH)
        qr_x = margin_x
        qr_y = sign_y + 40
        draw.rectangle([(qr_x, qr_y), (qr_x + 280, qr_y + 280)], outline=(203, 213, 225), width=2)
        
        # QR Grid pattern
        random.seed(int(nim[:7]))
        for qx in range(qr_x + 20, qr_x + 260, 20):
            for qy in range(qr_y + 20, qr_y + 260, 20):
                if random.choice([True, False]):
                    draw.rectangle([(qx, qy), (qx + 16, qy + 16)], fill=(15, 23, 42))
        random.seed()
        # Corner blocks QR
        for cx, cy in [(qr_x + 20, qr_y + 20), (qr_x + 200, qr_y + 20), (qr_x + 20, qr_y + 200)]:
            draw.rectangle([(cx, cy), (cx + 50, cy + 50)], fill=(15, 23, 42))
            draw.rectangle([(cx + 10, cy + 10), (cx + 40, cy + 40)], fill=(255, 255, 255))
            draw.rectangle([(cx + 18, cy + 18), (cx + 32, cy + 32)], fill=(15, 23, 42))

        draw.text((qr_x + 140, qr_y + 310), "Pindai untuk Verifikasi Keabsahan", fill=(100, 116, 139), font=f_small, anchor="mm")
        draw.text((qr_x + 140, qr_y + 350), f"https://sia.ut.ac.id/verify/{nim}", fill=(0, 51, 141), font=f_small, anchor="mm")

        # 8. FOOTER RESMI
        draw.line([(margin_x, h - 160), (w - margin_x, h - 160)], fill=(226, 232, 240), width=2)
        draw.text(
            (w // 2, h - 110),
            "Dokumen ini sah dan diterbitkan secara resmi melalui Sistem Informasi Akademik Universitas Terbuka (SIA-UT).",
            fill=(148, 163, 184),
            font=f_small,
            anchor="mm"
        )

        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format="PNG", quality=95)
        return buf.getvalue()
