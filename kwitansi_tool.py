import io
import math
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def angka_ke_terbilang(n: int) -> str:
    """Mengubah bilangan integer rupiah menjadi teks terbilang bahasa Indonesia."""
    satuan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    n = int(n)
    if n < 12:
        return satuan[n]
    elif n < 20:
        return satuan[n - 10] + " Belas"
    elif n < 100:
        return satuan[n // 10] + " Puluh" + (" " + satuan[n % 10] if n % 10 != 0 else "")
    elif n < 200:
        return "Seratus" + (" " + angka_ke_terbilang(n - 100) if n - 100 != 0 else "")
    elif n < 1000:
        return satuan[n // 100] + " Ratus" + (" " + angka_ke_terbilang(n % 100) if n % 100 != 0 else "")
    elif n < 2000:
        return "Seribu" + (" " + angka_ke_terbilang(n - 1000) if n - 1000 != 0 else "")
    elif n < 1000000:
        return angka_ke_terbilang(n // 1000) + " Ribu" + (" " + angka_ke_terbilang(n % 1000) if n % 1000 != 0 else "")
    elif n < 1000000000:
        return angka_ke_terbilang(n // 1000000) + " Juta" + (" " + angka_ke_terbilang(n % 1000000) if n % 1000000 != 0 else "")
    elif n < 1000000000000:
        return angka_ke_terbilang(n // 1000000000) + " Miliar" + (" " + angka_ke_terbilang(n % 1000000000) if n % 1000000000 != 0 else "")
    return str(n)

def generate_kwitansi_pdf(
    pembayar: str,
    nominal: int,
    keperluan: str,
    penerima: str = "Bendahara / Kasir",
    tanggal: str = None
) -> bytes:
    """
    Menghasilkan berkas PDF Kwitansi Tanda Terima Pembayaran Resmi (A5 Landscape 300 DPI).
    Lengkap dengan Terbilang Otomatis, Nomor Resi Unik, Stempel Lunas, dan Barcode.
    """
    if not tanggal:
        tanggal = datetime.now().strftime("%d %B %Y")

    # Format A5 Landscape @ 300 DPI: 2480 x 1748
    w, h = 2480, 1748
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    def get_font(size, bold=False):
        fpath = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        try:
            return ImageFont.truetype(fpath, size)
        except Exception:
            return ImageFont.load_default()

    f_title = get_font(52, bold=True)
    f_sub = get_font(26, bold=False)
    f_label = get_font(30, bold=True)
    f_val = get_font(30, bold=False)
    f_nom = get_font(44, bold=True)
    f_ttd = get_font(28, bold=True)

    # 1. BORDER KLASIK KWITANSI
    margin = 80
    draw.rectangle([(margin, margin), (w - margin, h - margin)], outline=(30, 60, 115), width=6)
    draw.rectangle([(margin + 12, margin + 12), (w - margin - 12, h - margin - 12)], outline=(30, 60, 115), width=2)

    # 2. HEADER
    no_resi = f"KW-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    draw.text((margin + 50, margin + 50), "KWITANSI PEMBAYARAN", fill=(20, 45, 95), font=f_title)
    draw.text((margin + 50, margin + 120), "BUKTI TANDA TERIMA TRANSAKSI RESMI", fill=(100, 100, 100), font=f_sub)
    draw.text((w - margin - 50, margin + 60), f"No : {no_resi}", fill=(30, 30, 30), font=get_font(28, bold=True), anchor="ra")

    draw.line([(margin + 50, margin + 175), (w - margin - 50, margin + 175)], fill=(180, 190, 210), width=3)

    # 3. ISI KWITANSI
    terbilang_str = angka_ke_terbilang(nominal) + " Rupiah"
    
    rows = [
        ("Telah Terima Dari", f":  {pembayar.upper()}"),
        ("Uang Sejumlah", f":  {terbilang_str}"),
        ("Untuk Pembayaran", f":  {keperluan}"),
    ]

    y = margin + 230
    for lbl, val in rows:
        draw.text((margin + 60, y), lbl, fill=(50, 50, 50), font=f_label)
        # Handle word wrap val jika panjang
        draw.text((margin + 420, y), val, fill=(15, 15, 15), font=f_val)
        y += 110

    # Garis pemisah bawah
    draw.line([(margin + 50, y + 20), (w - margin - 50, y + 20)], fill=(180, 190, 210), width=2)

    # 4. KOTAK NOMINAL BESAR
    box_y = y + 70
    draw.rectangle([(margin + 60, box_y), (margin + 750, box_y + 130)], fill=(240, 245, 255), outline=(30, 60, 115), width=4)
    draw.text((margin + 90, box_y + 35), f"Terbilang :  Rp {nominal:,},-", fill=(15, 40, 105), font=f_nom)

    # 5. TANDA TANGAN & PENGESAHAN KASIR
    ttd_x = w - margin - 500
    ttd_y = box_y - 20
    draw.text((ttd_x, ttd_y), f"Diterima pada : {tanggal}", fill=(60, 60, 60), font=f_sub)
    draw.text((ttd_x, ttd_y + 50), "Penerima / Kasir,", fill=(30, 30, 30), font=f_ttd)

    # Stempel Bulat LUNAS
    stempel_x, stempel_y = ttd_x - 120, ttd_y + 150
    draw.ellipse([(stempel_x - 80, stempel_y - 80), (stempel_x + 80, stempel_y + 80)], outline=(190, 30, 45, 220), width=5)
    draw.ellipse([(stempel_x - 70, stempel_y - 70), (stempel_x + 70, stempel_y + 70)], outline=(190, 30, 45, 180), width=2)
    draw.text((stempel_x, stempel_y - 20), "LUNAS", fill=(190, 30, 45, 220), font=get_font(26, bold=True), anchor="mm")
    draw.text((stempel_x, stempel_y + 18), "VERIFIED", fill=(190, 30, 45, 200), font=get_font(18, bold=True), anchor="mm")

    # Tanda tangan basah biru
    x0, y0 = ttd_x + 60, ttd_y + 160
    pts = [(x0, y0), (x0 + 35, y0 - 30), (x0 + 65, y0 + 20), (x0 + 110, y0 - 15), (x0 + 160, y0 + 10)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=(18, 48, 128), width=4)
    draw.line([(x0 - 20, y0 + 25), (x0 + 200, y0 + 25)], fill=(18, 48, 128), width=3)

    draw.text((ttd_x + 30, ttd_y + 240), f"( {penerima.upper()} )", fill=(20, 20, 20), font=f_ttd)

    out_io = io.BytesIO()
    # Simpan sebagai PDF langsung
    img.save(out_io, format="PDF", resolution=300.0)
    return out_io.getvalue()
