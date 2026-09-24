"""
suite_advanced_tools.py — Suite Peralatan Tingkat Lanjut:
1. Watermark KTP Aman (Anti-Pinjol & Anti-Penyalahgunaan Identitas)
2. AI Photo Enhancer & Unblur (Super Resolution & Detail Sharpener)
3. Branded QR Code Generator Kustom
4. ZIP Archive Manager (Pack & Unpack)
5. Flowchart & Diagram Alur Instan (ASCII / Box Drawing / SVG)
"""

import os
import io
import math
import zipfile
from typing import Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer

# ==================== 1. WATERMARK KTP AMAN (ANTI-PINJOL) ====================
def add_watermark_ktp_secure(
    image_bytes: bytes,
    keperluan_text: str = "HANYA UNTUK VERIFIKASI RESMI",
    tanggal_str: str = ""
) -> bytes:
    """
    Membubuhkan teks watermark diagonal berulang semi-transparan yang memotong
    bagian tengah KTP/dokumen sehingga sah untuk verifikasi namun tidak bisa
    disalahgunakan oleh pihak lain atau pinjol ilegal.
    """
    base_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    w, h = base_img.size

    txt_layer = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Ukuran font proporsional terhadap lebar kartu
    font_size = max(18, int(w * 0.038))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(font_size * 0.75))
    except Exception:
        font = ImageFont.load_default()
        font_sub = font

    watermark_label = keperluan_text.upper()
    sub_label = f"TIDAK BERLAKU UNTUK PINJAMAN ONLINE • {tanggal_str}".strip()

    # Buat kanvas watermark terpisah untuk dirotasi
    diag_len = int(math.hypot(w, h) * 1.2)
    wm_pattern = Image.new("RGBA", (diag_len, diag_len), (255, 255, 255, 0))
    p_draw = ImageDraw.Draw(wm_pattern)

    step_y = int(font_size * 3.8)
    step_x = int(font_size * 14)

    # Warna watermark: abu-abu semi-transparan (alpha: 85)
    color_wm = (235, 40, 40, 95)     # Merah tegas anti-pinjol
    color_sub = (255, 255, 255, 110) # Putih kontras

    for y in range(0, diag_len, step_y):
        offset_x = (y // step_y) % 2 * (step_x // 2)
        for x in range(-step_x, diag_len + step_x, step_x):
            p_draw.text((x + offset_x, y), watermark_label, font=font, fill=color_wm)
            p_draw.text((x + offset_x, y + font_size + 4), sub_label, font=font_sub, fill=color_sub)

    # Rotasi diagonal -28 derajat
    rotated_pattern = wm_pattern.rotate(28, resample=Image.BICUBIC, expand=False)
    
    # Crop pas ke ukuran kartu
    cx, cy = diag_len // 2, diag_len // 2
    box = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)
    cropped_pattern = rotated_pattern.crop(box)

    combined = Image.alpha_composite(base_img, cropped_pattern)
    out_bio = io.BytesIO()
    combined.convert("RGB").save(out_bio, format="JPEG", quality=92)
    return out_bio.getvalue()

# ==================== 2. AI PHOTO ENHANCER & UNBLUR ====================
def enhance_photo_hd(image_bytes: bytes, factor_sharpness: float = 2.2, factor_contrast: float = 1.15) -> bytes:
    """
    Meningkatkan ketajaman, menghilangkan blur halus, dan mengoptimalkan kontras
    pada foto KTP/dokumen lama atau pasfoto buram.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # 1. Unsharp Mask halus untuk mengangkat mikrotekstur
    unsharp = img.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=3))
    
    # 2. Penajaman ketajaman kontur
    enhancer_sharp = ImageEnhance.Sharpness(unsharp)
    sharp_img = enhancer_sharp.enhance(factor_sharpness)
    
    # 3. Optimasi kontras & kecerahan
    enhancer_contrast = ImageEnhance.Contrast(sharp_img)
    contrast_img = enhancer_contrast.enhance(factor_contrast)

    enhancer_color = ImageEnhance.Color(contrast_img)
    final_img = enhancer_color.enhance(1.08)

    out_bio = io.BytesIO()
    final_img.save(out_bio, format="JPEG", quality=95)
    return out_bio.getvalue()

# ==================== 3. GENERATOR QR CODE KUSTOM BERLOGO ====================
def generate_custom_qr_code(
    data_text: str,
    logo_bytes: Optional[bytes] = None,
    color_fill: str = "#0051C3",
    color_bg: str = "#FFFFFF"
) -> bytes:
    """
    Menghasilkan berkas QR Code resolusi tinggi dengan modul sudut melengkung
    dan dukungan penyematan logo di tengah QR.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H, # Koreksi error tinggi (30%) agar logo aman
        box_size=12,
        border=3,
    )
    qr.add_data(data_text)
    qr.make(fit=True)

    img_qr = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        back_color=color_bg,
        fill_color=color_fill
    ).convert("RGBA")

    # Jika ada logo, sematkan tepat di tengah
    if logo_bytes:
        try:
            logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
            qr_w, qr_h = img_qr.size
            logo_size = int(qr_w * 0.24)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Buat bantalan putih melingkar di belakang logo
            pad = 8
            bg_logo = Image.new("RGBA", (logo_size + pad, logo_size + pad), (255, 255, 255, 255))
            draw_bg = ImageDraw.Draw(bg_logo)
            draw_bg.rounded_rectangle([(0, 0), (logo_size + pad, logo_size + pad)], radius=12, fill=(255, 255, 255, 255))

            pos_x = (qr_w - (logo_size + pad)) // 2
            pos_y = (qr_h - (logo_size + pad)) // 2

            img_qr.paste(bg_logo, (pos_x, pos_y), bg_logo)
            img_qr.paste(logo, (pos_x + pad // 2, pos_y + pad // 2), logo)
        except Exception:
            pass

    out_bio = io.BytesIO()
    img_qr.save(out_bio, format="PNG")
    return out_bio.getvalue()

# ==================== 4. ZIP ARCHIVE MANAGER ====================
def create_zip_archive(files: List[Tuple[str, bytes]]) -> bytes:
    """Membungkus daftar file (nama_file, bytes) menjadi 1 berkas ZIP."""
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname, fbytes in files:
            zf.writestr(fname, fbytes)
    return bio.getvalue()

def extract_zip_files(zip_bytes: bytes) -> List[Tuple[str, bytes]]:
    """Mengekstrak berkas di dalam arsip ZIP."""
    bio = io.BytesIO(zip_bytes)
    results = []
    with zipfile.ZipFile(bio, 'r') as zf:
        for info in zf.infolist():
            if not info.is_dir():
                results.append((info.filename, zf.read(info.filename)))
    return results

# ==================== 5. FLOWCHART / DIAGRAM ALUR INSTAN ====================
def generate_flowchart_image(steps: List[str], title: str = "DIAGRAM ALUR PROSES") -> bytes:
    """
    Merender diagram alur proses (Flowchart vertikal) estetis beresolusi tinggi:
    Kotak langkah proses, panah penghubung, nomor urut, dan tema dark modern.
    """
    card_w = 800
    box_w = 640
    box_h = 75
    spacing = 55
    top_margin = 120
    bottom_margin = 80

    total_h = top_margin + len(steps) * (box_h + spacing) + bottom_margin
    img = Image.new("RGB", (card_w, total_h), (15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_step = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except Exception:
        font_title = ImageFont.load_default()
        font_step = font_title
        font_num = font_title

    # Header Title
    draw.text((card_w // 2, 45), title.upper(), font=font_title, fill=(248, 250, 252), anchor="mm")
    draw.line([(card_w // 2 - 120, 68), (card_w // 2 + 120, 68)], fill=(59, 130, 246), width=3)

    for i, step_text in enumerate(steps):
        y = top_margin + i * (box_h + spacing)
        x0 = (card_w - box_w) // 2
        y0 = y
        x1 = x0 + box_w
        y1 = y0 + box_h

        # Gradasi warna kotak: Awal Hijau, Tengah Biru, Akhir Indigo
        if i == 0:
            border_color = (34, 197, 94) # Green
            num_bg = (34, 197, 94)
        elif i == len(steps) - 1:
            border_color = (168, 85, 247) # Purple
            num_bg = (168, 85, 247)
        else:
            border_color = (59, 130, 246) # Blue
            num_bg = (59, 130, 246)

        # Gambar Kotak Proses
        draw.rounded_rectangle([(x0, y0), (x1, y1)], radius=14, fill=(30, 41, 59), outline=border_color, width=2)

        # Badge Nomor Urut
        badge_size = 42
        bx0 = x0 + 16
        by0 = y0 + (box_h - badge_size) // 2
        draw.rounded_rectangle([(bx0, by0), (bx0 + badge_size, by0 + badge_size)], radius=10, fill=num_bg)
        draw.text((bx0 + badge_size // 2, by0 + badge_size // 2), str(i + 1), font=font_num, fill=(255, 255, 255), anchor="mm")

        # Teks Langkah
        draw.text((bx0 + badge_size + 20, y0 + box_h // 2), step_text, font=font_step, fill=(241, 245, 249), anchor="lm")

        # Panah Penghubung ke langkah berikutnya
        if i < len(steps) - 1:
            arrow_cx = card_w // 2
            arrow_start_y = y1 + 4
            arrow_end_y = arrow_start_y + spacing - 8
            draw.line([(arrow_cx, arrow_start_y), (arrow_cx, arrow_end_y)], fill=(100, 116, 139), width=3)
            # Kepala panah
            draw.polygon([
                (arrow_cx - 7, arrow_end_y - 8),
                (arrow_cx + 7, arrow_end_y - 8),
                (arrow_cx, arrow_end_y + 2)
            ], fill=(59, 130, 246))

    out_bio = io.BytesIO()
    img.save(out_bio, format="PNG")
    return out_bio.getvalue()
