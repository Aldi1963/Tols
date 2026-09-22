import io
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def apply_camscanner_filter(image_bytes: bytes, mode: str = "magic_color") -> bytes:
    """
    Mengubah foto dokumen/kertas kamera HP menjadi hasil scan jernih:
    - magic_color: Latar kertas diputihkan bersih, tinta dipertajam, warna stempel/kop tetap hidup
    - bw: Hitam putih tajam fotokopi resmi
    - grayscale: Grayscale bergradasi halus
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    if mode == "bw":
        # Grayscale + Adaptive Thresholding simulasi
        gray = img.convert("L")
        # Gaussian blur background untuk estimasi pencahayaan
        bg = gray.filter(ImageFilter.GaussianBlur(radius=25))
        # Normalisasi: (gray / bg) * 255
        g_arr = np.array(gray, dtype=np.float32)
        bg_arr = np.array(bg, dtype=np.float32)
        norm = np.clip((g_arr / (bg_arr + 1e-5)) * 255.0, 0, 255).astype(np.uint8)
        
        # Otsu or standard high contrast
        res_img = Image.fromarray(norm)
        enhancer = ImageEnhance.Contrast(res_img)
        res_img = enhancer.enhance(2.0)
        enhancer_sharp = ImageEnhance.Sharpness(res_img)
        res_img = enhancer_sharp.enhance(1.8)
        
        out_io = io.BytesIO()
        res_img.convert("RGB").save(out_io, format="JPEG", quality=95)
        return out_io.getvalue()
        
    elif mode == "magic_color":
        # Magic Color: Latar putih bersih, saturasi warna tanda tangan/stempel/logo tetap terjaga
        # 1. Estimasi background channel per channel
        rgb_arr = np.array(img, dtype=np.float32)
        gray = img.convert("L")
        bg_gray = np.array(gray.filter(ImageFilter.GaussianBlur(radius=30)), dtype=np.float32)
        
        # Hilangkan bayangan kertas
        ratio = 255.0 / (bg_gray + 1e-5)
        # Kurangi intensitas rasio agar tidak over-exposed pada foto terang
        ratio = np.clip(ratio, 0.9, 1.8)
        
        norm_rgb = np.clip(rgb_arr * ratio[:, :, np.newaxis], 0, 255).astype(np.uint8)
        res_img = Image.fromarray(norm_rgb)
        
        # Tingkatkan kontras dan ketajaman
        contrast = ImageEnhance.Contrast(res_img)
        res_img = contrast.enhance(1.4)
        
        sharpness = ImageEnhance.Sharpness(res_img)
        res_img = sharpness.enhance(1.6)
        
        color = ImageEnhance.Color(res_img)
        res_img = color.enhance(1.2)
        
        out_io = io.BytesIO()
        res_img.save(out_io, format="JPEG", quality=95)
        return out_io.getvalue()

    else:
        # Grayscale standard enhanced
        gray = img.convert("L")
        contrast = ImageEnhance.Contrast(gray)
        res_img = contrast.enhance(1.5)
        out_io = io.BytesIO()
        res_img.convert("RGB").save(out_io, format="JPEG", quality=95)
        return out_io.getvalue()
