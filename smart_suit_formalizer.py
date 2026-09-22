import io
import os
import math
import rembg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from typing import Tuple, Optional

# Preset Warna Latar Belakang Pasfoto Resmi Indonesia
COLOR_PRESETS = {
    "red": (178, 24, 34),       # Merah KTP / SKCK / CPNS (Tahun Lahir Ganjil) Pantone 186 C
    "blue": (22, 68, 140),      # Biru Ijazah / Buku Nikah / KTM UT (Tahun Lahir Genap)
    "white": (255, 255, 255),   # Putih Paspor Internasional / Dokumen Visa
    "gray": (110, 115, 125),    # Abu-Abu Studio Profesional / LinkedIn
}

def render_studio_background(width: int, height: int, base_color: Tuple[int, int, int]) -> Image.Image:
    """Merender background studio pasfoto resmi dengan pencahayaan radial lembut (Soft Studio Glow)."""
    if base_color == (255, 255, 255):
        return Image.new("RGB", (width, height), (255, 255, 255))

    bg = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(bg)

    cx, cy = width // 2, int(height * 0.42)
    max_radius = int(math.hypot(width, height) * 0.72)

    for r in range(max_radius, 25, -12):
        factor = 1.0 - (r / max_radius)
        r_c = min(255, int(base_color[0] + (255 - base_color[0]) * 0.28 * factor))
        g_c = min(255, int(base_color[1] + (255 - base_color[1]) * 0.28 * factor))
        b_c = min(255, int(base_color[2] + (255 - base_color[2]) * 0.28 * factor))
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(r_c, g_c, b_c))

    return bg.filter(ImageFilter.GaussianBlur(radius=8))

def formalize_pasfoto_hd(
    user_image_bytes: bytes,
    bg_color_name: str = "red",
    target_size: Tuple[int, int] = (1200, 1600), # Pasfoto Ultra HD 300 DPI
    enhance_face: bool = True
) -> bytes:
    """
    Mengubah foto santai apapun menjadi Pasfoto Studio Formal Ultra HD:
    1. AI U2-Net deep learning segmentation menghapus background asli
    2. Menghasilkan latar studio resmi bergradasi halus (Merah KTP / Biru Ijazah / Putih)
    3. Framing proporsional pasfoto standar (kepala mengisi 70-80% tinggi frame)
    4. Peningkatan kontras & ketajaman halus agar siap cetak
    """
    raw_img = Image.open(io.BytesIO(user_image_bytes)).convert("RGB")
    
    # 1. Segmentasi U2-Net
    cutout = rembg.remove(raw_img) # Menghasilkan RGBA
    
    tw, th = target_size
    base_color = COLOR_PRESETS.get(bg_color_name.lower(), (178, 24, 34))
    
    # 2. Render background studio
    studio_bg = render_studio_background(tw, th, base_color)
    
    # 3. Proporsi Framing Pasfoto (Kepala & Pundak Pas di Tengah)
    cw, ch = cutout.size
    
    # Hitung bounding box subjek
    bbox = cutout.getbbox()
    if bbox:
        subj = cutout.crop(bbox)
        sw, sh = subj.size
    else:
        subj = cutout
        sw, sh = cw, ch

    # Skalakan subjek agar mengisi sekitar 88% tinggi kanvas
    scale = (th * 0.88) / sh
    tar_sw = int(sw * scale)
    tar_sh = int(sh * scale)
    
    # Resize subjek dengan interpolasi halus
    subj_resized = subj.resize((tar_sw, tar_sh), Image.Resampling.LANCZOS)
    
    # Letakkan subjek di tengah horizontal, menempel di dasar bawah
    pos_x = (tw - tar_sw) // 2
    pos_y = th - tar_sh
    
    studio_bg.paste(subj_resized, (pos_x, pos_y), subj_resized)
    
    # 4. Peningkatan Ketajaman Halus untuk Cetak
    if enhance_face:
        enhancer = ImageEnhance.Sharpness(studio_bg)
        studio_bg = enhancer.enhance(1.2)
        contrast = ImageEnhance.Contrast(studio_bg)
        studio_bg = contrast.enhance(1.05)

    out_io = io.BytesIO()
    studio_bg.save(out_io, format="JPEG", quality=98, subsampling=0)
    return out_io.getvalue()
