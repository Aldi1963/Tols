import io
import re
from typing import List, Tuple, Union, Optional
from pypdf import PdfReader, PdfWriter
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ==================== 1. ROTATE PDF PAGES (PUTAR HALAMAN) ====================
def rotate_pdf_pages(pdf_bytes: bytes, angle: int = 90) -> bytes:
    """Memutar seluruh halaman PDF (90, 180, atau 270 derajat searah jarum jam)."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    out_io = io.BytesIO()
    writer.write(out_io)
    return out_io.getvalue()

# ==================== 2. PROTECT PDF (KUNCI DENGAN PASSWORD) ====================
def protect_pdf_with_password(pdf_bytes: bytes, user_password: str) -> bytes:
    """Mengunci dokumen PDF dengan enkripsi password (standar AES-128)."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(user_password=user_password, owner_password=None)
    out_io = io.BytesIO()
    writer.write(out_io)
    return out_io.getvalue()

# ==================== 3. DELETE / REMOVE PDF PAGES (HAPUS HALAMAN) ====================
def remove_pdf_pages(pdf_bytes: bytes, pages_to_remove_str: str) -> Tuple[bool, Union[bytes, str], int]:
    """Menghapus halaman tertentu dari PDF (contoh input: '2' atau '1, 3, 5')."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_p = len(reader.pages)
        if total_p == 0:
            return False, "File PDF tidak memiliki halaman.", 0

        # Parse nomor halaman yang ingin dihapus (1-based)
        delete_set = set()
        for part in pages_to_remove_str.replace(" ", "").split(","):
            if "-" in part:
                sub = part.split("-")
                s, e = int(sub[0]), int(sub[1])
                for i in range(min(s, e), max(s, e) + 1):
                    if 1 <= i <= total_p:
                        delete_set.add(i)
            elif part.isdigit():
                num = int(part)
                if 1 <= num <= total_p:
                    delete_set.add(num)

        if not delete_set:
            return False, f"Nomor halaman tidak valid. Dokumen memiliki {total_p} halaman.", 0

        if len(delete_set) >= total_p:
            return False, "Tidak dapat menghapus semua halaman dalam dokumen.", 0

        writer = PdfWriter()
        kept_count = 0
        for idx in range(total_p):
            page_no = idx + 1
            if page_no not in delete_set:
                writer.add_page(reader.pages[idx])
                kept_count += 1

        out_io = io.BytesIO()
        writer.write(out_io)
        return True, out_io.getvalue(), len(delete_set)
    except Exception as e:
        return False, str(e), 0

# ==================== 4. ADD PAGE NUMBERS (TAMBAH NOMOR HALAMAN) ====================
def add_page_numbers_to_pdf(pdf_bytes: bytes, position: str = "bottom-center") -> bytes:
    """Menambahkan penomoran halaman resmi di pojok/tengah bawah lembar PDF."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    writer = PdfWriter()

    for idx, page in enumerate(reader.pages):
        page_no = idx + 1
        page_w = float(page.mediabox.width)
        page_h = float(page.mediabox.height)

        # Buat canvas nomor halaman transparan
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_w, page_h))
        can.setFont("Helvetica", 10)
        can.setFillColor(colors.HexColor("#333333"))

        num_text = f"Halaman {page_no} dari {total_pages}"
        text_w = can.stringWidth(num_text, "Helvetica", 10)

        # Posisi koordinat
        if position == "bottom-right":
            x = page_w - text_w - 36
        elif position == "bottom-left":
            x = 36
        else:  # bottom-center
            x = (page_w - text_w) / 2.0

        y = 24  # 24 pt dari batas bawah
        can.drawString(x, y, num_text)
        can.save()

        packet.seek(0)
        num_reader = PdfReader(packet)
        page.merge_page(num_reader.pages[0])
        writer.add_page(page)

    out_io = io.BytesIO()
    writer.write(out_io)
    return out_io.getvalue()

# ==================== 5. EXTRACT IMAGES FROM PDF (EXTRAK GAMBAR) ====================
def extract_images_from_pdf(pdf_bytes: bytes, max_images: int = 15) -> List[Tuple[str, bytes]]:
    """Mengekstrak seluruh file gambar asli (JPG/PNG) yang tertanam di dalam PDF."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    images = []
    seen_xrefs = set()

    for pno in range(len(doc)):
        page = doc[pno]
        img_list = page.get_images(full=True)
        for img_info in img_list:
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            base_img = doc.extract_image(xref)
            img_bytes = base_img["image"]
            ext = base_img["ext"]
            filename = f"gambar_hal_{pno+1}_{xref}.{ext}"
            images.append((filename, img_bytes))

            if len(images) >= max_images:
                break
        if len(images) >= max_images:
            break

    doc.close()
    return images
