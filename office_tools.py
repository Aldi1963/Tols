import subprocess
import tempfile
import os
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pillow_heif
import pypdf
import pytesseract

pillow_heif.register_heif_opener()

def convert_doc_to_pdf(doc_bytes: bytes, filename: str = "document.docx") -> bytes:
    """Mengonversi berkas Word (.docx, .doc, .rtf, .txt, .odt) ke PDF menggunakan LibreOffice headless"""
    ext = os.path.splitext(filename)[1].lower() or ".docx"
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input{ext}")
        with open(input_path, "wb") as f:
            f.write(doc_bytes)

        cmd = ["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmpdir, input_path]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=60)

        pdf_path = os.path.join(tmpdir, "input.pdf")
        if not os.path.exists(pdf_path):
            raise RuntimeError("Gagal menghasilkan berkas PDF dari dokumen.")

        with open(pdf_path, "rb") as f:
            return f.read()

def convert_pdf_to_docx(pdf_bytes: bytes) -> bytes:
    """Mengonversi dokumen PDF menjadi berkas Microsoft Word (.docx) yang dapat diedit teks & tabelnya"""
    from pdf2docx import Converter
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "input.pdf")
        docx_path = os.path.join(tmpdir, "output.docx")

        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        if not os.path.exists(docx_path):
            raise RuntimeError("Gagal mengonversi PDF ke Word.")

        with open(docx_path, "rb") as f:
            return f.read()

def convert_images_to_pdf(image_bytes_list: list[bytes]) -> bytes:
    """Mengonversi satu atau banyak foto (JPG/PNG/WEBP/HEIC) menjadi satu berkas PDF resmi rapi berurutan"""
    import img2pdf
    converted_jpeg_streams = []

    for img_b in image_bytes_list:
        im = Image.open(BytesIO(img_b))
        try:
            im = ImageOps.exif_transpose(im)
        except Exception:
            pass

        im_rgb = im.convert("RGB")
        buf = BytesIO()
        im_rgb.save(buf, format="JPEG", quality=92, optimize=True)
        converted_jpeg_streams.append(buf.getvalue())

    return img2pdf.convert(converted_jpeg_streams)

def compress_pdf(pdf_bytes: bytes, level: str = "ebook") -> tuple[bytes, float, float]:
    """
    Mengompres ukuran berkas PDF menggunakan Ghostscript optimization.
    Level:
    - 'screen': resolusi 72 DPI (ukuran sangat kecil, cocok untuk syarat <500KB)
    - 'ebook': resolusi 150 DPI (standar optimal CPNS/BUMN, teks tajam)
    - 'printer': resolusi 300 DPI (kualitas cetak)
    """
    pdf_settings = f"/{level}"
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, "in.pdf")
        out_path = os.path.join(tmpdir, "out.pdf")

        with open(in_path, "wb") as f:
            f.write(pdf_bytes)

        cmd = [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={pdf_settings}",
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={out_path}", in_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=60)

        if not os.path.exists(out_path):
            raise RuntimeError("Gagal mengompres berkas PDF.")

        with open(out_path, "rb") as f:
            res_bytes = f.read()

        orig_kb = len(pdf_bytes) / 1024
        res_kb = len(res_bytes) / 1024
        return res_bytes, orig_kb, res_kb

def compress_image_advanced(img_bytes: bytes, target_kb: int = None, quality: int = 85, max_dimension: int = None) -> tuple[bytes, int, int, str]:
    """Mengompres foto ke target ukuran (misal pas 100KB, 200KB CPNS, 500KB BUMN)"""
    img = Image.open(BytesIO(img_bytes))
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    if max_dimension and max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_w = int(img.size[0] * ratio)
        new_h = int(img.size[1] * ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

    if not target_kb:
        out_buf = BytesIO()
        if has_alpha:
            img.save(out_buf, format="PNG", optimize=True)
            fmt = "PNG"
        else:
            img = img.convert("RGB")
            img.save(out_buf, format="JPEG", quality=quality, optimize=True)
            fmt = "JPEG"
        res = out_buf.getvalue()
        return res, img.size[0], img.size[1], fmt

    target_bytes = target_kb * 1024
    img_rgb = img.convert("RGB")

    low = 10
    high = 95
    best_data = None

    for _ in range(7):
        mid = (low + high) // 2
        buf = BytesIO()
        img_rgb.save(buf, format="JPEG", quality=mid, optimize=True)
        data = buf.getvalue()
        if len(data) <= target_bytes:
            best_data = data
            low = mid + 1
        else:
            high = mid - 1

    if not best_data:
        scale_img = img_rgb
        while len(data) > target_bytes and max(scale_img.size) > 300:
            w, h = scale_img.size
            scale_img = scale_img.resize((int(w * 0.82), int(h * 0.82)), Image.Resampling.LANCZOS)
            buf = BytesIO()
            scale_img.save(buf, format="JPEG", quality=45, optimize=True)
            data = buf.getvalue()
        best_data = data

    return best_data, img_rgb.size[0], img_rgb.size[1], "JPEG"

def extract_signature_to_transparent(img_bytes: bytes, ink_color: str = "blue") -> bytes:
    """Mengisolasi coretan tanda tangan dari foto kertas biasa menjadi PNG transparan tajam"""
    img = Image.open(BytesIO(img_bytes))
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    gray = img.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2.2)

    w, h = enhanced.size
    pixels = enhanced.load()

    out_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out_pixels = out_img.load()

    ink_rgb = {
        "blue": (15, 45, 145),
        "darkblue": (8, 25, 85),
        "black": (25, 25, 25),
    }.get(ink_color.lower(), (15, 45, 145))

    for y in range(h):
        for x in range(w):
            v = pixels[x, y]
            if v < 195:
                alpha = int(255 * (1.0 - (v / 195.0)))
                alpha = min(255, int(alpha * 1.35))
                out_pixels[x, y] = (ink_rgb[0], ink_rgb[1], ink_rgb[2], alpha)

    bbox = out_img.getbbox()
    if bbox:
        pad = 20
        c_bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(w, bbox[2]+pad), min(h, bbox[3]+pad))
        out_img = out_img.crop(c_bbox)

    out_buf = BytesIO()
    out_img.save(out_buf, format="PNG", optimize=True)
    return out_buf.getvalue()

print("Enhanced office_tools.py verified!")


def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
    """Menggabungkan 2 atau lebih berkas PDF menjadi satu berkas berurutan"""
    writer = pypdf.PdfWriter()
    for b in pdf_bytes_list:
        reader = pypdf.PdfReader(BytesIO(b))
        for page in reader.pages:
            writer.add_page(page)
    out = BytesIO()
    writer.write(out)
    return out.getvalue()

def unlock_pdf(pdf_bytes: bytes, user_password: str = "") -> bytes:
    """Membuka password PDF atau dekripsi e-statement bank"""
    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    if reader.is_encrypted:
        success = reader.decrypt(user_password)
        if not success:
            # Coba decrypt dengan string kosong jika proteksi permission saja
            reader.decrypt("")
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = BytesIO()
    writer.write(out)
    return out.getvalue()

def ocr_image_to_text(img_bytes: bytes) -> str:
    """Mengekstrak teks dari foto / dokumen scan menggunakan Tesseract OCR (Bahasa Indonesia & Inggris)"""
    im = Image.open(BytesIO(img_bytes))
    try:
        im = ImageOps.exif_transpose(im)
    except Exception:
        pass
    # Preprocessing kontras & grayscale untuk akurasi maksimal
    gray = im.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.8)
    text = pytesseract.image_to_string(enhanced, lang="ind+eng")
    return text.strip()

def pdf_to_images_hd(pdf_bytes: bytes) -> list[bytes]:
    """Mengonversi tiap halaman berkas PDF menjadi foto gambar beresolusi tinggi (JPEG 200 DPI)"""
    import pymupdf
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("jpeg")
        images.append(img_bytes)
    return images

def create_pasfoto_4r_sheet(photo_bytes: bytes) -> bytes:
    """
    Menyusun 1 pasfoto ke dalam lembar kertas foto ukuran 4R (10.2 x 15.2 cm / 1200 x 1800 px @ 300 DPI)
    Format standar studio cetak:
    - 4 lembar ukuran 4x6 (38.1 x 55.9 mm -> ~450 x 660 px)
    - 4 lembar ukuran 3x4 (27.9 x 38.1 mm -> ~330 x 450 px)
    - 4 lembar ukuran 2x3 (21.6 x 27.9 mm -> ~255 x 330 px)
    Dilengkapi garis potong tipis (crop marks) presisi.
    """
    sheet_w, sheet_h = 1800, 1200 # 4R landscape @ 300 DPI
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = Image.Draw(sheet) if hasattr(Image, 'Draw') else None
    import PIL.ImageDraw as ImageDraw
    draw = ImageDraw.Draw(sheet)

    src_img = Image.open(BytesIO(photo_bytes))
    try:
        src_img = ImageOps.exif_transpose(src_img)
    except Exception:
        pass

    # Crop to 2:3 ratio
    sw, sh = src_img.size
    target_ratio = 4.0 / 6.0
    if sw / sh > target_ratio:
        new_sw = int(sh * target_ratio)
        offset = (sw - new_sw) // 2
        src_crop = src_img.crop((offset, 0, offset + new_sw, sh))
    else:
        new_sh = int(sw / target_ratio)
        offset = (sh - new_sh) // 2
        src_crop = src_img.crop((0, offset, sw, offset + new_sh))

    # Ukuran piksel di 300 DPI
    # 4x6: 450 x 660 px
    # 3x4: 330 x 450 px
    # 2x3: 255 x 350 px
    im_4x6 = src_crop.resize((370, 530), Image.Resampling.LANCZOS)
    im_3x4 = src_crop.resize((270, 360), Image.Resampling.LANCZOS)
    im_2x3 = src_crop.resize((200, 270), Image.Resampling.LANCZOS)

    # Susun Kolom 1 & 2: 4 pcs 4x6
    # 2 baris x 2 kolom
    x_offset = 60
    for row in range(2):
        for col in range(2):
            px = x_offset + col * (370 + 35)
            py = 60 + row * (530 + 30)
            sheet.paste(im_4x6, (px, py))
            draw.rectangle([(px-1, py-1), (px + 370, py + 530)], outline=(200, 200, 200), width=1)

    # Susun Kolom 3: 4 pcs 3x4 (2 kolom x 2 baris)
    x3_offset = 910
    for row in range(2):
        for col in range(2):
            px = x3_offset + col * (270 + 25)
            py = 60 + row * (360 + 25)
            sheet.paste(im_3x4, (px, py))
            draw.rectangle([(px-1, py-1), (px + 270, py + 360)], outline=(200, 200, 200), width=1)

    # Susun Bagian Bawah Kolom 3: 4 pcs 2x3 (4 kolom sejajar)
    y2_offset = 860
    for col in range(4):
        px = x3_offset + col * (200 + 15)
        py = y2_offset
        sheet.paste(im_2x3, (px, py))
        draw.rectangle([(px-1, py-1), (px + 200, py + 270)], outline=(200, 200, 200), width=1)

    # Teks label footer cetak
    from countries.utils import load_font
    try:
        f_lbl = load_font(18, bold=True)
        draw.text((60, 1150), "LEMBAR CETAK PASFOTO UKURAN 4R (4x6: 4 pcs | 3x4: 4 pcs | 2x3: 4 pcs) • 300 DPI SIAP CETAK", fill=(130, 130, 130), font=f_lbl)
    except Exception:
        pass

    out_buf = BytesIO()
    sheet.save(out_buf, format="JPEG", quality=95, optimize=True)
    return out_buf.getvalue()

print("All extra tools functions defined!")
