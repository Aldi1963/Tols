from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
import rembg

STUDIO_COLORS = {
    "transparan": None,
    "merah": (219, 32, 44),       # Merah KTP resmi (Pantone 186 C)
    "biru": (26, 82, 175),        # Biru pasfoto ijazah / UT resmi
    "putih": (255, 255, 255),     # Putih bersih paspor / visa
    "abu": (210, 215, 222),       # Abu-abu studio profesional
    "hitam": (20, 22, 26),        # Hitam elegan
}

def process_hd_rembg(image_bytes: bytes, color_key: str = "transparan", studio_glow: bool = True) -> bytes:
    """
    Menghapus background foto dan mengganti dengan warna pilihan dalam resolusi asli (Full HD)
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    orig_w, orig_h = img.size

    # 1. Hapus background menggunakan AI rembg U2-Net
    cutout = rembg.remove(img)

    # 2. Jika transparan murni, langsung simpan PNG resolusi penuh
    target_bg_color = STUDIO_COLORS.get(color_key.lower())
    if target_bg_color is None:
        out_buf = BytesIO()
        cutout.save(out_buf, format="PNG", optimize=True)
        return out_buf.getvalue(), orig_w, orig_h

    # 3. Jika warna solid / studio glow
    bg = Image.new("RGB", (orig_w, orig_h), target_bg_color)
    
    if studio_glow and color_key in ["merah", "biru"]:
        # Tambahkan soft radial studio glow dari pusat atas (efek lampu studio foto profesional)
        cx, cy = orig_w // 2, int(orig_h * 0.40)
        b_draw = ImageDraw.Draw(bg)
        max_r = int(max(orig_w, orig_h) * 0.65)
        for r in range(max_r, 40, -15):
            factor = 1.0 - (r / max_r)
            r_c = min(255, int(target_bg_color[0] + (255 - target_bg_color[0]) * 0.28 * factor))
            g_c = min(255, int(target_bg_color[1] + (255 - target_bg_color[1]) * 0.28 * factor))
            b_c = min(255, int(target_bg_color[2] + (255 - target_bg_color[2]) * 0.28 * factor))
            b_draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(r_c, g_c, b_c))
        bg = bg.filter(ImageFilter.GaussianBlur(radius=int(orig_w * 0.015)))

    # 4. Composite cutout di atas background
    bg.paste(cutout, (0, 0), cutout)

    out_buf = BytesIO()
    # Simpan sebagai PNG kualitas tinggi tanpa kompresi
    bg.save(out_buf, format="PNG", optimize=True)
    return out_buf.getvalue(), orig_w, orig_h

print("HD Rembg processor ready!")
