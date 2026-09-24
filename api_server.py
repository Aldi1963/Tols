"""
api_server.py — High Performance FastAPI Web API Server untuk Ekosistem Tols / Yowes Suite
Port: 8008
Swagger UI Docs: http://43.133.138.219:8008/docs atau https://m.clipku.com/tols-api/docs
"""

import os
import sys
import io
import time
import tempfile
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import engine internal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import currency_service
import media_downloader
import pdf24_suite
import rembg_service
import desk_mockup_generator
import ktm_generator

DB_PATH = os.path.join(BASE_DIR, "users.db")

app = FastAPI(
    title="Tols Education & Media Web API",
    description=(
        "**Official REST API Engine untuk Ekosistem Tols Suite**.\n\n"
        "Menyediakan endpoint pembuatan dokumen verifikasi akademik (KTM, SKMA, KHS), "
        "mockup 3D fotorealistis meja kayu, konversi dokumen PDF24, AI pasfoto U2-Net, "
        "kalkulator kurs valas real-time interbank, serta social media downloader tanpa batas."
    ),
    version="1.0.0",
    root_path="/tols-api",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Aktifkan CORS agar bisa dipanggil dari domain mana saja
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== HELPER AUTH API KEY ====================
def verify_api_token(authorization: Optional[str] = Header(None)):
    """Verifikasi token developer: Authorization: Bearer <KEY> (opsional / public preview)"""
    return True

# ==================== ROOT / HEALTH ====================
@app.get("/", tags=["Status"])
def root_endpoint():
    return {
        "status": "online",
        "service": "Tols Education & Productivity Web API",
        "version": "1.0.0",
        "documentation": "/docs",
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health", tags=["Status"])
def health_check():
    return {"status": "ok", "db_available": os.path.exists(DB_PATH)}

# ==================== 1. KURS VALAS LIVE API ====================
@app.get("/api/v1/currency/rates", tags=["Kurs Valas"])
def get_all_currency_rates():
    """Mengambil seluruh data kurs mata uang asing ke Rupiah (IDR) secara live."""
    try:
        rates = currency_service.get_live_rates()
        return {
            "success": True,
            "base": "IDR",
            "rates": rates,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/currency/convert", tags=["Kurs Valas"])
def convert_currency_amount(
    amount: float = Query(..., description="Nominal uang yang ingin dikonversi"),
    from_curr: str = Query("USD", description="Kode mata uang asal (USD, SGD, MYR, EUR, dll)"),
    to_curr: str = Query("IDR", description="Kode mata uang tujuan (default: IDR)")
):
    """Konversi nominal mata uang asing ke IDR atau sebaliknya secara akurat."""
    res = currency_service.convert_currency(amount, from_curr.upper(), to_curr.upper())
    if not res:
        raise HTTPException(status_code=400, detail="Mata uang tidak didukung atau terjadi kesalahan server.")
    return {
        "success": True,
        "input_amount": amount,
        "from_currency": from_curr.upper(),
        "to_currency": to_curr.upper(),
        "conversion_result": res["result"],
        "rate_single": res["rate_single"],
    }

# ==================== 2. MEDIA DOWNLOADER API ====================
@app.get("/api/v1/downloader/info", tags=["Media Downloader"])
def get_media_metadata(url: str = Query(..., description="Tautan video TikTok, IG, YT, FB, atau Twitter")):
    """Mendapatkan judul, nama uploader, thumbnail cover, dan durasi video tanpa download."""
    if not media_downloader.is_supported_url(url):
        raise HTTPException(status_code=400, detail="URL tidak didukung.")
    try:
        info = media_downloader.get_media_info(url)
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/downloader/download", tags=["Media Downloader"])
def download_media_stream(
    url: str = Query(..., description="Tautan video"),
    mode: str = Query("video_hd", description="Pilihan mode: video_hd, video_sd, audio, thumbnail")
):
    """Download berkas video HD / SD / MP3 audio langsung dari server."""
    try:
        res = media_downloader.download_media_custom(url, mode=mode)
        if res.get('direct_url'):
            return {"success": True, "direct_download_url": res['direct_url'], "title": res['title']}
        
        media_bytes = res.get('data')
        if not media_bytes:
            raise HTTPException(status_code=500, detail="Gagal mengunduh berkas media.")
            
        mime = "audio/mpeg" if res['type'] == 'audio' else ("image/jpeg" if res['type'] == 'image' else "video/mp4")
        return Response(
            content=media_bytes,
            media_type=mime,
            headers={"Content-Disposition": f"attachment; filename=\"{res['filename']}\""}
        )
    except Exception as e:
        err_msg = str(e)
        if "OVERSIZE_50MB:" in err_msg:
            direct_link = err_msg.split("OVERSIZE_50MB:")[1].strip()
            return {"success": True, "direct_download_url": direct_link, "message": "File exceeds 50MB, use direct link"}
        raise HTTPException(status_code=500, detail=err_msg)

# ==================== 3. AI PASFOTO & BACKGROUND REMOVER ====================
@app.post("/api/v1/photo/remove-bg", tags=["AI Foto Studio"])
async def remove_photo_background(file: UploadFile = File(..., description="Unggah foto objek")):
    """Menghapus latar belakang foto menggunakan deep learning AI U2-Net (Output PNG transparan)."""
    img_bytes = await file.read()
    try:
        no_bg_bytes = rembg_service.remove_bg(img_bytes)
        return Response(
            content=no_bg_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=\"nobg_transparent.png\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/photo/formal-studio", tags=["AI Foto Studio"])
async def formalize_photo_studio(
    file: UploadFile = File(..., description="Unggah pasfoto"),
    bg_color: str = Form("red", description="Pilihan warna: red (Merah KTP), blue (Biru Nikah/KTM), white (Putih)")
):
    """Mengubah latar belakang pasfoto ke warna studio resmi (Merah KTP / Biru / Putih)."""
    img_bytes = await file.read()
    color_map = {
        "red": (219, 21, 20),
        "blue": (11, 96, 176),
        "white": (255, 255, 255),
    }
    rgb = color_map.get(bg_color.lower(), (219, 21, 20))
    try:
        res_bytes = rembg_service.formalize_pasfoto(img_bytes, bg_color=rgb)
        return Response(
            content=res_bytes,
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename=\"pasfoto_{bg_color}.jpg\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 4. SUITE PDF24 LENGKAP ====================
@app.post("/api/v1/pdf/split", tags=["Suite PDF24"])
async def split_pdf_pages(
    file: UploadFile = File(..., description="Berkas PDF"),
    page_range: str = Form("1-3", description="Rentang halaman (contoh: '1-3' atau '2,4,6')")
):
    """Memecah atau mengambil rentang halaman tertentu dari berkas PDF."""
    pdf_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f_in:
        f_in.write(pdf_bytes)
        in_path = f_in.name

    out_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    try:
        ok = pdf24_suite.split_pdf(in_path, out_path, page_range)
        if not ok or not os.path.exists(out_path):
            raise HTTPException(status_code=400, detail="Gagal memproses rentang halaman PDF.")
        with open(out_path, "rb") as f_out:
            res_data = f_out.read()
        return Response(
            content=res_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"split_{page_range}.pdf\""}
        )
    finally:
        if os.path.exists(in_path): os.remove(in_path)
        if os.path.exists(out_path): os.remove(out_path)

@app.post("/api/v1/pdf/watermark", tags=["Suite PDF24"])
async def watermark_pdf_document(
    file: UploadFile = File(..., description="Berkas PDF"),
    watermark_text: str = Form("DOKUMEN RESMI", description="Teks watermark diagonal")
):
    """Membubuhkan teks watermark diagonal semi-transparan pada setiap halaman PDF."""
    pdf_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f_in:
        f_in.write(pdf_bytes)
        in_path = f_in.name

    out_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    try:
        ok = pdf24_suite.add_watermark_pdf(in_path, out_path, watermark_text)
        if not ok or not os.path.exists(out_path):
            raise HTTPException(status_code=400, detail="Gagal membubuhkan watermark.")
        with open(out_path, "rb") as f_out:
            res_data = f_out.read()
        return Response(
            content=res_data,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=\"watermarked.pdf\""}
        )
    finally:
        if os.path.exists(in_path): os.remove(in_path)
        if os.path.exists(out_path): os.remove(out_path)

@app.post("/api/v1/pdf/protect", tags=["Suite PDF24"])
async def protect_pdf_password(
    file: UploadFile = File(..., description="Berkas PDF"),
    password: str = Form(..., description="Kata sandi pembuka berkas")
):
    """Mengunci dan mengenkripsi berkas PDF dengan password."""
    pdf_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f_in:
        f_in.write(pdf_bytes)
        in_path = f_in.name

    out_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    try:
        ok = pdf24_suite.protect_pdf(in_path, out_path, password)
        if not ok or not os.path.exists(out_path):
            raise HTTPException(status_code=400, detail="Gagal mengenkripsi berkas PDF.")
        with open(out_path, "rb") as f_out:
            res_data = f_out.read()
        return Response(
            content=res_data,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=\"protected.pdf\""}
        )
    finally:
        if os.path.exists(in_path): os.remove(in_path)
        if os.path.exists(out_path): os.remove(out_path)

# ==================== 6. WATERMARK KTP & AI ENHANCER API ====================
@app.post("/api/v1/photo/watermark-ktp", tags=["Proteksi KTP & Foto"])
async def api_watermark_ktp(
    file: UploadFile = File(..., description="Unggah foto KTP/SIM/Identitas"),
    keperluan: str = Form("HANYA UNTUK VERIFIKASI RESMI", description="Keperluan penggunaan dokumen")
):
    """Membubuhkan teks watermark diagonal anti-pinjol pada foto KTP/kartu identitas."""
    img_bytes = await file.read()
    try:
        import suite_advanced_tools
        tgl_now = time.strftime("%d/%m/%Y")
        res_bytes = suite_advanced_tools.add_watermark_ktp_secure(img_bytes, keperluan, tgl_now)
        return Response(
            content=res_bytes,
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=\"ktp_watermarked.jpg\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/photo/enhance", tags=["Proteksi KTP & Foto"])
async def api_enhance_photo(
    file: UploadFile = File(..., description="Unggah foto buram/dokumen lama"),
    sharpness: float = Form(2.2, description="Tingkat penajaman (1.5 - 3.0)")
):
    """Meningkatkan ketajaman, menghilangkan blur halus, dan merekonstruksi kontur foto."""
    img_bytes = await file.read()
    try:
        import suite_advanced_tools
        res_bytes = suite_advanced_tools.enhance_photo_hd(img_bytes, factor_sharpness=sharpness)
        return Response(
            content=res_bytes,
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=\"photo_enhanced.jpg\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tools/qrcode", tags=["Utilitas & Bisnis"])
def api_generate_qr(
    text: str = Query(..., description="Isi teks atau link URL"),
    fill_color: str = Query("#0051C3", description="Warna QR Code hex")
):
    """Menghasilkan QR Code modern beresolusi tinggi dengan modul sudut rounded."""
    try:
        import suite_advanced_tools
        res_bytes = suite_advanced_tools.generate_custom_qr_code(text, color_fill=fill_color)
        return Response(
            content=res_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=\"qrcode.png\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tools/flowchart", tags=["Utilitas & Bisnis"])
def api_generate_flowchart(
    steps: List[str] = Query(..., description="Daftar urutan langkah alur"),
    title: str = Query("DIAGRAM ALUR PROSES", description="Judul bagan")
):
    """Merender bagan alur proses (Flowchart vertikal) beresolusi tinggi secara instan."""
    try:
        import suite_advanced_tools
        res_bytes = suite_advanced_tools.generate_flowchart_image(steps, title=title)
        return Response(
            content=res_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=\"flowchart.png\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 5. GENERATOR MOCKUP MEJA KAYU 3D ====================
@app.post("/api/v1/mockup/wood-desk", tags=["Mockup 3D"])
async def generate_wood_desk_mockup_endpoint(
    card_image: UploadFile = File(..., description="Unggah foto/desain kartu identitas")
):
    """Menempatkan kartu di atas meja kayu solid fotorealistis dengan bayangan kontak pekat."""
    card_bytes = await card_image.read()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_card:
        f_card.write(card_bytes)
        card_path = f_card.name

    out_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
    try:
        res = desk_mockup_generator.generate_photorealistic_wood_desk_mockup(card_path, out_path)
        if not res or not os.path.exists(out_path):
            raise HTTPException(status_code=500, detail="Gagal merender mockup 3D.")
        with open(out_path, "rb") as f_out:
            mockup_bytes = f_out.read()
        return Response(
            content=mockup_bytes,
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=\"mockup_wood_desk.jpg\""}
        )
    finally:
        if os.path.exists(card_path): os.remove(card_path)
        if os.path.exists(out_path): os.remove(out_path)
