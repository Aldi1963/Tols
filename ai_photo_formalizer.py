"""
Professional AI Background Replacer & Studio Formalizer
Menggunakan deep learning U2-Net AI (rembg) untuk:
1. Menghapus background foto apapun secara otomatis dengan segmentasi helai rambut presisi tinggi
2. Mengganti latar belakang dengan Gradasi Studio Pasfoto Resmi (Biru UT / Merah KTP)
3. Hasil ultra-clean tanpa artefak halo atau lingkaran kasar
"""

from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
import math
import rembg

SUIT_BLUE_BG = (22, 68, 140)    # Biru pasfoto resmi
SUIT_RED_BG = (178, 24, 34)     # Merah pasfoto KTP tahun ganjil

def replace_background_studio(user_image: Image.Image, bg_color: str = "blue", target_size: tuple = (320, 420)) -> Image.Image:
    """
    Menghapus background foto pengguna dan memasang background pasfoto studio resmi bergradasi halus
    """
    tw, th = target_size
    base_color = SUIT_RED_BG if bg_color.lower() == "red" else SUIT_BLUE_BG

    # 1. Hapus background menggunakan AI rembg U2-Net
    cutout = rembg.remove(user_image)

    # 2. Buat background studio resmi dengan pencahayaan radial lembut (Soft Studio Glow)
    bg = Image.new("RGB", (tw, th), base_color)
    b_draw = ImageDraw.Draw(bg)

    cx, cy = tw // 2, int(th * 0.42)
    max_radius = int(math.hypot(tw, th) * 0.75)
    
    # Render gradasi halus dari pusat kepala
    for r in range(max_radius, 20, -10):
        factor = 1.0 - (r / max_radius)
        r_c = min(255, int(base_color[0] + (255 - base_color[0]) * 0.28 * factor))
        g_c = min(255, int(base_color[1] + (255 - base_color[1]) * 0.28 * factor))
        b_c = min(255, int(base_color[2] + (255 - base_color[2]) * 0.28 * factor))
        b_draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(r_c, g_c, b_c))

    bg = bg.filter(ImageFilter.GaussianBlur(radius=8))

    # 3. Scale cutout subjek agar pas di frame pasfoto
    cw, ch = cutout.size
    scale = (th * 0.88) / ch
    new_cw = int(cw * scale)
    new_ch = int(ch * scale)
    resized_cutout = cutout.resize((new_cw, new_ch), Image.Resampling.LANCZOS)

    # Paste di tengah bawah
    pos_x = (tw - new_cw) // 2
    pos_y = th - new_ch

    bg.paste(resized_cutout, (pos_x, pos_y), resized_cutout)
    return bg
