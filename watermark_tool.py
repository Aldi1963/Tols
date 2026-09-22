import io
import math
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple

def apply_watermark_ktm(
    image_bytes: bytes,
    watermark_text: str,
    opacity: int = 110,
    font_size: int = 0
) -> bytes:
    """
    Menempelkan watermark diagonal anti-penyalahgunaan / anti-pinjol
    pada foto KTP / dokumen penting.
    """
    base_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    w, h = base_img.size

    # Buat layer transparan untuk watermark
    txt_layer = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    if font_size <= 0:
        # Skalakan otomatis sesuai lebar gambar
        font_size = max(28, int(w * 0.042))

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    full_text = f"🛡️ {watermark_text.upper()}"
    
    # Render teks miring berulang secara diagonal menutupi seluruh dokumen
    # Menggunakan rotasi layer atau grid
    # Buat stamp single diagonal yang diulang
    diag_len = int(math.hypot(w, h))
    stamp_img = Image.new("RGBA", (diag_len * 2, diag_len * 2), (255, 255, 255, 0))
    s_draw = ImageDraw.Draw(stamp_img)

    step_y = font_size * 5
    step_x = font_size * 14

    for y in range(0, diag_len * 2, step_y):
        offset_x = (y // step_y) % 2 * (step_x // 2)
        for x in range(-step_x, diag_len * 2, step_x):
            # Tinta abu-abu gelap dengan outline putih lembut agar terlihat di background gelap maupun terang
            s_draw.text((x + offset_x - 1, y - 1), full_text, fill=(255, 255, 255, opacity), font=font)
            s_draw.text((x + offset_x + 1, y + 1), full_text, fill=(255, 255, 255, opacity), font=font)
            s_draw.text((x + offset_x, y), full_text, fill=(20, 20, 20, int(opacity * 1.2)), font=font)

    # Rotasi stamp 30 derajat
    rotated_stamp = stamp_img.rotate(28, resample=Image.Resampling.BICUBIC)
    
    # Crop pas ukuran dokumen
    cx, cy = rotated_stamp.width // 2, rotated_stamp.height // 2
    crop_x = cx - w // 2
    crop_y = cy - h // 2
    cropped = rotated_stamp.crop((crop_x, crop_y, crop_x + w, crop_y + h))

    # Blend layer ke gambar asli
    merged = Image.alpha_composite(base_img, cropped)
    rgb_result = merged.convert("RGB")

    out_io = io.BytesIO()
    rgb_result.save(out_io, format="JPEG", quality=95)
    return out_io.getvalue()
