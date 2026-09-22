from typing import Optional, Dict, Any, List
import os
import sys
import logging
import io
import random
import html
from datetime import datetime, date
from pathlib import Path
from PIL import Image

DB_PATH = "/home/ubuntu/yowes/users.db"
from telegram.request import HTTPXRequest
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputFile,
    BotCommand,
    BotCommandScopeDefault,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

YOWES_DIR = Path(__file__).parent
sys.path.insert(0, str(YOWES_DIR))

from countries import get_country, list_countries
from ktm_generator import KtmGenerator
from kartu_pelajar_generator import KartuPelajarGenerator
from skma_generator import SkmaGenerator
from exif_helper import inject_camera_exif, convert_to_pdf
from desk_mockup_generator import render_card_on_desk, render_lanyard_card_holder, render_handheld_pov
from rembg_service import process_hd_rembg, STUDIO_COLORS
from office_tools import (
    convert_doc_to_pdf,
    convert_pdf_to_docx,
    convert_images_to_pdf,
    compress_pdf,
    compress_image_advanced,
    extract_signature_to_transparent,
    merge_pdfs,
    unlock_pdf,
    ocr_image_to_text,
    pdf_to_images_hd,
    create_pasfoto_4r_sheet,
)
from khs_generator import generate_khs_transcript
from media_downloader import is_supported_url, extract_url_from_text, get_media_info, download_media_custom
from billing import (
    init_db,
    get_or_create_user,
    consume_quota,
    create_clipku_payment,
    check_and_apply_payment,
    process_referral,
    get_referral_stats,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8054459863:AAEwC1tj78uDsemA5QkrzZEfKtPcpHqJY3s"

ADMIN_IDS = [5606826328]  # ID Akun Kancilpay

ktm_engine = KtmGenerator()
skma_engine = SkmaGenerator()
pelajar_engine = KartuPelajarGenerator()
init_db()

# Conversation States
CUSTOM_NAME, CUSTOM_PHOTO, CUSTOM_UNIV = range(3)
REMBG_WAIT_PHOTO, REMBG_WAIT_COLOR = range(10, 12)
COMPRESS_WAIT_PHOTO, COMPRESS_WAIT_SIZE = range(20, 22)
DOC2PDF_WAIT_FILE = 30
PDF2DOC_WAIT_FILE = 35
IMG2PDF_WAIT_PHOTOS = 38
COMPRESS_PDF_WAIT_FILE = 42
COMPRESS_PDF_WAIT_LEVEL = 43
SIG_WAIT_PHOTO = 45
MERGE_PDF_WAIT = 50
UNLOCK_PDF_WAIT = 55
OCR_WAIT_PHOTO = 60
PDF2IMG_WAIT = 65
PASFOTO4R_WAIT = 70
DL_VIDEO_WAIT = 80
COMPRESS_WAIT_PHOTO, COMPRESS_WAIT_SIZE = range(20, 22)
DOC2PDF_WAIT_FILE = 30
PDF2DOC_WAIT_FILE = 35
IMG2PDF_WAIT_PHOTOS = 38
COMPRESS_PDF_WAIT_FILE = 42
COMPRESS_PDF_WAIT_LEVEL = 43
SIG_WAIT_PHOTO = 45
MERGE_PDF_WAIT = 50
UNLOCK_PDF_WAIT = 55
OCR_WAIT_PHOTO = 60
PDF2IMG_WAIT = 65
PASFOTO4R_WAIT = 70
DL_VIDEO_WAIT = 80

# Storage cache in memory for active sessions (chat_id -> dict)
SESSION_DOC_CACHE = {}

COUNTRY_FLAGS = {
    "indonesia": "🇮🇩 Indonesia",
    "netherlands": "🇳🇱 Belanda",
    "us": "🇺🇸 Amerika",
    "uk": "🇬🇧 Inggris",
    "australia": "🇦🇺 Australia",
    "canada": "🇨🇦 Kanada",
    "france": "🇫🇷 Prancis",
    "spain": "🇪🇸 Spanyol",
    "argentina": "🇦🇷 Argentina",
    "mexico": "🇲🇽 Meksiko",
    "philippines": "🇵🇭 Filipina",
    "thailand": "🇹🇭 Thailand",
    "slovakia": "🇸🇰 Slowakia",
}
DOC_LABELS = {
    "nuptk_card": "🪪 Kartu NUPTK",
    "payslip": "💵 Slip Gaji (Payslip)",
    "appointment_letter": "📜 SK Pengangkatan Guru",
    "teaching_experience_letter": "📝 Surat Keterangan Mengajar",
    "teacher_id": "🪪 Teacher ID Card",
    "employment_letter": "📜 Employment Letter",
    "teaching_license": "📑 Teaching License",
    "teacher_registration": "📑 Registerleraar Certificaat",
    "employment_contract": "📜 Arbeidsovereenkomst (Kontrak)",
    "duo_declaration": "🏛️ DUO Verklaring Bevoegdheid",
    "school_id": "🪪 School ID Card",
    "installation_statement": "📜 Procès-Verbal d'Installation",
    "iprof_screenshot": "💻 I-Prof Portal Snapshot",
    "bylaws_extract": "📑 Arrêté de Nomination",
    "teaching_certificate": "🎓 Certificat d'Exercice",
    "oct_card": "🪪 OCT Member Card",
    "signed_school_letter": "📜 Signed School Letter",
    "teaching_id": "🪪 Carnet Docente (ID)",
    "employment_certificate": "📜 Certificado de Trabajo",
    "letter_of_employment": "📜 Letter of Employment",
    "contract": "📑 Teaching Contract",
}




FIRST_NAMES_MALE = [
    "ADITYA", "BUDI", "DIMAS", "EKO", "FAJAR", "GILANG", "HENDRA", "ILHAM", 
    "JOKO", "KURNIAWAN", "LUKMAN", "MUHAMMAD", "NUGROHO", "PRATAMA", "RIZKY", 
    "SETIAWAN", "TAUFIK", "WAHYU", "YUDHA", "ZULKARNAEN", "AGUS", "ANDI", "BAYU"
]
FIRST_NAMES_FEMALE = [
    "ANISA", "BELLA", "CITRA", "DEWI", "ENDAH", "FITRI", "GITA", "HANIFAH", 
    "INDAH", "LESTARI", "MAYA", "NURUL", "PUTRI", "RATNA", "SARI", "TIARA", 
    "WULANDARI", "YULIA", "ZAHRA", "DIAN", "RINI", "AYU", "SITI"
]
LAST_NAMES_INDO = [
    "SANTOSO", "PRATAMA", "SAPUTRA", "WIJAYA", "HIDAYAT", "KUSUMA", "NUGRAHA", 
    "UTOMO", "GUNAWAN", "WIBOWO", "PERMANA", "SETIAWAN", "SUHARTONO", "ANGGARA"
]

def get_indonesian_name(gender: str = "Male") -> tuple[str, str]:
    if gender.lower() in ["female", "wanita", "f"]:
        first = random.choice(FIRST_NAMES_FEMALE)
    else:
        first = random.choice(FIRST_NAMES_MALE)
    last = random.choice(LAST_NAMES_INDO)
    return first, last

def get_main_reply_keyboard():
    """Reply Keyboard Utama: Format 2x2 Sangat Lega & Ramping"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎓 BUAT DOKUMEN"), KeyboardButton("🛠️ KOTAK ALAT FILE")],
            [KeyboardButton("👑 PROFIL & VIP"), KeyboardButton("ℹ️ PANDUAN & BANTUAN")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_dokumen_hub_reply_keyboard():
    """Sub-Menu Hub: Seluruh Jenis Pembuatan Dokumen"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎓 KTM Kampus Indonesia"), KeyboardButton("🏛️ ID Kampus Internasional")],
            [KeyboardButton("👨‍🏫 Dokumen Guru (Canva)"), KeyboardButton("🏫 Kartu Pelajar SMA/SMK")],
            [KeyboardButton("✨ Buat Custom (Nama/Foto)"), KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_dl_format_keyboard(session_key: str, is_slideshow: bool = False):
    """Inline Keyboard Pemilihan Format Unduhan Media (HD / Hemat / Musik MP3)"""
    if is_slideshow:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Unduh Semua Slide Foto", callback_data=f"dl_act:slideshow:{session_key}")],
            [InlineKeyboardButton("🎵 Unduh Musik / Audio (MP3)", callback_data=f"dl_act:audio:{session_key}")],
            [InlineKeyboardButton("« Batal", callback_data="main_menu")],
        ])
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Video HD (No Watermark)", callback_data=f"dl_act:video_hd:{session_key}"),
            InlineKeyboardButton("⚡ Video Hemat (480p)", callback_data=f"dl_act:video_sd:{session_key}")
        ],
        [
            InlineKeyboardButton("🎵 Musik / Audio (MP3)", callback_data=f"dl_act:audio:{session_key}"),
            InlineKeyboardButton("✂️ Auto Clip (9:16 Vertikal)", callback_data=f"dl_act:autoclip:{session_key}")
        ],
        [
            InlineKeyboardButton("📸 Unduh Cover / Foto", callback_data=f"dl_act:thumbnail:{session_key}"),
            InlineKeyboardButton("« Batal", callback_data="main_menu")
        ],
    ])

def get_khs_univ_reply_keyboard():
    """Reply Keyboard Pemilihan Kampus untuk Cetak Transkrip Nilai (KHS)"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📊 KHS Universitas Terbuka (UT)"), KeyboardButton("📊 KHS Univ. Indonesia (UI)")],
            [KeyboardButton("📊 KHS Univ. Gadjah Mada (UGM)"), KeyboardButton("📊 KHS ITB Bandung")],
            [KeyboardButton("📊 KHS Univ. Brawijaya (UB)"), KeyboardButton("« KEMBALI KE KOTAK ALAT")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_tools_hub_reply_keyboard():
    """Sub-Menu Hub: Seluruh Alat File, Konversi, Foto & Media Video"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎬 DOWNLOAD VIDEO (NO WM)"), KeyboardButton("✂️ Auto Clip Video (9:16)")],
            [KeyboardButton("💱 KURS VALAS LIVE"), KeyboardButton("✂️ Hapus BG & Pasfoto AI")],
            [KeyboardButton("📄 Word ke PDF"), KeyboardButton("📝 PDF ke Word")],
            [KeyboardButton("📝 PDF ke Word"), KeyboardButton("🖼️ Foto ke PDF")],
            [KeyboardButton("🖼️ Foto ke PDF"), KeyboardButton("📸 PDF ke Gambar HD")],
            [KeyboardButton("📑 Gabung PDF (Merge)"), KeyboardButton("🔓 Buka Password PDF")],
            [KeyboardButton("🗜️ Kompres Dokumen PDF"), KeyboardButton("🗜️ Kompres Foto (CPNS)")],
            [KeyboardButton("🖨️ Pasfoto 4R Siap Cetak"), KeyboardButton("🔍 Scan Foto ke Teks (OCR)")],
            [KeyboardButton("🖋️ Tanda Tangan Transparan"), KeyboardButton("📊 Transkrip Nilai (KHS)")],
            [KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_profile_hub_reply_keyboard():
    """Sub-Menu Hub: Akun, VIP, Kuota, & Referral"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("⚡ Beli +10 Kuota (Rp 5.000)"), KeyboardButton("👑 Beli VIP 30 Hari (Rp 15.000)")],
            [KeyboardButton("🎁 Ambil Tautan Referral"), KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_rembg_colors_reply_keyboard():
    """Reply Keyboard Pemilihan Warna Background Pasfoto HD"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🔴 MERAH (KTP/SKCK)"), KeyboardButton("🔵 BIRU (IJAZAH/UT)")],
            [KeyboardButton("⚪ PUTIH (PASPOR/VISA)"), KeyboardButton("🔘 ABU-ABU STUDIO")],
            [KeyboardButton("⚫ HITAM ELEGAN"), KeyboardButton("🏁 TRANSPARAN PNG")],
            [KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_ktm_reply_keyboard():
    """Reply Keyboard Pemilihan Kampus Indonesia"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎓 Universitas Terbuka (UT)"), KeyboardButton("🎓 Univ. Indonesia (UI)")],
            [KeyboardButton("🎓 Univ. Gadjah Mada (UGM)"), KeyboardButton("🎓 ITB Bandung")],
            [KeyboardButton("🎓 Univ. Brawijaya (UB)"), KeyboardButton("🎲 Kampus Acak")],
            [KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_ktm_global_reply_keyboard():
    """Reply Keyboard Pemilihan Kampus Internasional"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🏛️ Harvard Univ (US)"), KeyboardButton("🏛️ MIT Tech (US)")],
            [KeyboardButton("🏛️ Stanford Univ (US)"), KeyboardButton("🏛️ Univ of Oxford (UK)")],
            [KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_pelajar_reply_keyboard():
    """Reply Keyboard Pemilihan Sekolah SMA/SMK"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🏫 SMAN 1 Jakarta"), KeyboardButton("🏫 SMAN 3 Bandung")],
            [KeyboardButton("🏫 SMKN 1 Surabaya"), KeyboardButton("🏫 SMAN 1 Yogyakarta")],
            [KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_guru_reply_keyboard():
    """Reply Keyboard Pemilihan 13 Negara Lengkap dalam Grid 4 Kolom Rapi & Seimbang"""
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton("🇮🇩 Indonesia"),
                KeyboardButton("🇳🇱 Belanda"),
                KeyboardButton("🇺🇸 Amerika"),
                KeyboardButton("🇬🇧 Inggris"),
            ],
            [
                KeyboardButton("🇦🇺 Australia"),
                KeyboardButton("🇨🇦 Kanada"),
                KeyboardButton("🇫🇷 Prancis"),
                KeyboardButton("🇪🇸 Spanyol"),
            ],
            [
                KeyboardButton("🇦🇷 Argentina"),
                KeyboardButton("🇲🇽 Meksiko"),
                KeyboardButton("🇵🇭 Filipina"),
                KeyboardButton("🇹🇭 Thailand"),
            ],
            [
                KeyboardButton("🇸🇰 Slowakia"),
                KeyboardButton("« KEMBALI KE MENU UTAMA"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_guru_docs_reply_keyboard(country_code: str):
    """Reply Keyboard Pilihan Dokumen setelah memilih Negara"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📦 CETAK SEMUA DOKUMEN (PAKET LENGKAP)")],
            [KeyboardButton("🪪 Kartu Identitas Guru"), KeyboardButton("📜 SK Pengangkatan")],
            [KeyboardButton("💵 Slip Gaji (Payslip)"), KeyboardButton("📝 Surat Mengajar")],
            [KeyboardButton("« PILIH NEGARA LAIN"), KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_card_action_reply_keyboard():
    """Reply Keyboard Aksi setelah kartu selesai dicetak"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📸 FOTO DI MEJA"), KeyboardButton("🪪 MIKA + LANYARD")],
            [KeyboardButton("🖐️ PEGANG TANGAN (POV)"), KeyboardButton("📜 CETAK SKMA")],
            [KeyboardButton("📊 TRANSKRIP NILAI (KHS)"), KeyboardButton("📥 UNDUH PDF (300 DPI)")],
            [KeyboardButton("📁 UNDUH HD PNG"), KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_billing_reply_keyboard():
    """Reply Keyboard Paket Kuota & VIP"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("⚡ Beli +10 Kuota (Rp 5.000)"), KeyboardButton("👑 Beli VIP 30 Hari (Rp 15.000)")],
            [KeyboardButton("« KEMBALI KE MENU UTAMA")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def get_pelajar_keyboard():
    buttons = [
        [
            InlineKeyboardButton("🏫 SMAN 1 Jakarta", callback_data="gen_pelajar:SMAN1_JKT"),
            InlineKeyboardButton("🏫 SMAN 3 Bandung", callback_data="gen_pelajar:SMAN3_BDG"),
        ],
        [
            InlineKeyboardButton("🏫 SMKN 1 Surabaya", callback_data="gen_pelajar:SMKN1_SBY"),
            InlineKeyboardButton("🏫 SMAN 1 Yogyakarta", callback_data="gen_pelajar:SMAN1_YOG"),
        ],
        [InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_ktm_id_keyboard():
    buttons = [
        [
            InlineKeyboardButton("🎓 Universitas Terbuka (UT)", callback_data="gen_ktm:UT"),
            InlineKeyboardButton("🎓 Univ. Indonesia (UI)", callback_data="gen_ktm:UI"),
        ],
        [
            InlineKeyboardButton("🎓 Univ. Gadjah Mada (UGM)", callback_data="gen_ktm:UGM"),
            InlineKeyboardButton("🎓 ITB Bandung", callback_data="gen_ktm:ITB"),
        ],
        [
            InlineKeyboardButton("🎓 Univ. Brawijaya (UB)", callback_data="gen_ktm:UB"),
            InlineKeyboardButton("🎲 Kampus Acak", callback_data="gen_ktm:RANDOM"),
        ],
        [InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_ktm_global_keyboard():
    buttons = [
        [
            InlineKeyboardButton("🏛️ Harvard Univ (US)", callback_data="gen_ktm:HARVARD"),
            InlineKeyboardButton("🏛️ MIT Tech (US)", callback_data="gen_ktm:MIT"),
        ],
        [
            InlineKeyboardButton("🏛️ Stanford Univ (US)", callback_data="gen_ktm:STANFORD"),
            InlineKeyboardButton("🏛️ Univ of Oxford (UK)", callback_data="gen_ktm:OXFORD"),
        ],
        [InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_countries_keyboard():
    buttons = []
    countries = list_countries()
    row = []
    for c in countries:
        label = COUNTRY_FLAGS.get(c, c.upper())
        row.append(InlineKeyboardButton(label, callback_data="sel_c:" + c))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")

    # Cek referral
    if context.args and len(context.args) > 0:
        arg = context.args[0]
        if arg.startswith("ref_"):
            try:
                referrer_id = int(arg.replace("ref_", ""))
                if process_referral(referrer_id, user.id):
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 <b>Selamat! Teman Baru Bergabung!</b>\nPengguna <b>{html.escape(user.first_name or 'Seseorang')}</b> telah bergabung melalui tautan undangan Anda.\n🎁 Anda mendapatkan bonus <b>+2 Kuota Pembuatan Dokumen Gratis</b>!\nGunakan perintah /profil untuk mengecek sisa kuota Anda.",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.warning(f"Gagal kirim notif ke referrer {referrer_id}: {e}")
            except Exception as e:
                logger.warning(f"Error parsing referral arg: {e}")

    
    # Otomatis cek apakah ada deposit/topup QRIS yang sudah lunas tetapi belum ter-update
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT order_id FROM topups WHERE user_id = ? AND status = 'PENDING' ORDER BY id DESC LIMIT 1", (user.id,))
        pend_row = cur.fetchone()
        conn.close()
        if pend_row:
            check_and_apply_payment(pend_row[0])
            u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")
    except Exception as e:
        logger.warning(f"Auto-check payment exception: {e}")

    name = html.escape(user.first_name or "Pengguna")
    vip_status = "👑 VIP UNLIMITED" if u_data["is_vip"] else "Standar (Gratis)"
    username_str = f"@{user.username}" if user.username else "-"

    quota_info = "Unlimited" if u_data["is_vip"] else f"{u_data['quota_left']}x"
    vip_badge = "👑 VIP UNLIMITED" if u_data["is_vip"] else "Standar (Gratis)"

    caption = f"""🎓 <b>Education Verification Suite</b>
Halo <b>{name}</b> (<code>{user.id}</code>)

👑 <b>Status:</b> {vip_badge} • <b>Kuota:</b> {quota_info}
📊 <b>Produktivitas:</b> {u_data['total_generated']} dokumen diterbitkan
🛡️ <b>Proteksi:</b> Anti-Fraud EXIF • Tinta Basah • 3D Mockup

<i>Silakan pilih layanan yang ingin digunakan pada menu di bawah:</i>"""

    # HANYA kirim pesan ber-ReplyKeyboardMarkup di bawah HP (TIDAK ADA inline button di chat!)
    await update.message.reply_text(
        caption,
        reply_markup=get_main_reply_keyboard(),
        parse_mode="HTML"
    )

async def profil_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")
    status_text = "👑 <b>VIP AKTIF (Unlimited)</b>" if u_data["is_vip"] else "Standar (Gratis)"
    exp_text = f"\nMasa Aktif VIP: {u_data['vip_until'][:10]}" if (u_data["is_vip"] and u_data["vip_until"]) else ""

    text = (
        f"👤 <b>Profil Pengguna:</b>\n"
        f"• Nama: {html.escape(user.first_name or '')}\n"
        f"• ID Telegram: <code>{user.id}</code>\n"
        f"• Status: {status_text}{exp_text}\n"
        f"• Kuota Cetak Hari Ini: <b>{u_data['quota_left']}x</b>\n"
        f"• Total Dokumen Dibuat: <b>{u_data['total_generated']} berkas</b>\n\n"
        "<i>Ingin cetak tanpa batas? Beli paket VIP via QRIS instan Clipku Pay!</i>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Beli Kuota / VIP", callback_data="menu_billing")],
        [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
    ])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")

    # 1. Navigasi Menu Utama
    if data.startswith("dl_act:"):
        parts = data.split(":")
        mode = parts[1]
        session_key = parts[2]
        info = MEDIA_DL_SESSIONS.get(session_key)

        if mode == "autoclip":
            if not info:
                await query.message.reply_text("⚠️ Sesi unduhan telah kedaluwarsa. Silakan kirimkan kembali tautan video Anda.")
                return
            clip_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Auto Split (Tiap 60 Detik Part 1-3)", callback_data=f"clip_opt:split60:{session_key}")],
                [InlineKeyboardButton("📱 Klip 30 Detik Pertama (9:16 Vertikal)", callback_data=f"clip_opt:first30:{session_key}")],
                [InlineKeyboardButton("📱 Klip 60 Detik Pertama (9:16 Vertikal)", callback_data=f"clip_opt:first60:{session_key}")],
                [InlineKeyboardButton("« Kembali ke Format", callback_data=f"dl_preview_back:{session_key}")],
            ])
            await query.message.reply_text(
                f"✂️ <b>AUTO CLIPPER 9:16 (TIKTOK / REELS / SHORTS)</b>\n\n"
                f"• Judul: <b>{html.escape(info['title'][:70])}</b>\n\n"
                f"Pilih mode klip otomatis yang diinginkan:",
                reply_markup=clip_kb,
                parse_mode="HTML"
            )
            return

        if not info:
            await query.message.reply_text("⚠️ Sesi unduhan telah kedaluwarsa. Silakan kirimkan kembali tautan video Anda.")
            return

    if data.startswith("clip_opt:"):
        parts = data.split(":")
        opt = parts[1]
        session_key = parts[2]
        info = MEDIA_DL_SESSIONS.get(session_key)
        if not info:
            await query.message.reply_text("⚠️ Sesi video telah kedaluwarsa.")
            return

        await query.message.reply_text("⏳ <i>Sedang mengunduh sumber video & memproses Auto Clip 9:16 (Vertikal Blur)...</i>", parse_mode="HTML")
        try:
            import auto_clipper
            import tempfile
            # Unduh video sumber terlebih dahulu
            res_vid = download_media_custom(info['url'], mode="video_hd", tikwm_cache=info.get('tikwm_data'))
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f_src:
                f_src.write(res_vid['data'])
                src_tmp = f_src.name

            dur_total = auto_clipper.get_video_duration(src_tmp)

            if opt == "split60":
                out_dir = tempfile.mkdtemp()
                splits = auto_clipper.auto_split_video(src_tmp, out_dir, segment_length=60.0, max_segments=3, to_vertical=True)
                if not splits:
                    await query.message.reply_text("❌ Gagal membagi klip video.")
                else:
                    await query.message.reply_text(f"✅ Berhasil membuat <b>{len(splits)} Part Klip Vertikal 9:16</b>! Mengirim berkas...", parse_mode="HTML")
                    for s in splits:
                        with open(s['path'], 'rb') as f_part:
                            part_bytes = f_part.read()
                        bio = io.BytesIO(part_bytes)
                        bio.name = f"{res_vid['title'][:30]}_Part{s['part']}.mp4"
                        bio.seek(0)
                        cap = f"✂️ <b>Part {s['part']} (Durasi {s['time_str']})</b>\n🎬 {html.escape(res_vid['title'][:60])}\n📱 Format Siap TikTok / Reels (9:16)"
                        await context.bot.send_video(chat_id=query.message.chat_id, video=bio, caption=cap, parse_mode="HTML")
                        os.remove(s['path'])
                    os.rmdir(out_dir)

            elif opt in ["first30", "first60"]:
                dur_clip = 30.0 if opt == "first30" else 60.0
                out_clip = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                ok = auto_clipper.clip_video_segment(src_tmp, out_clip, start_sec=0.0, duration_sec=dur_clip, to_vertical=True)
                if ok:
                    with open(out_clip, 'rb') as f_c:
                        c_bytes = f_c.read()
                    bio = io.BytesIO(c_bytes)
                    bio.name = f"{res_vid['title'][:30]}_Klip_{int(dur_clip)}s.mp4"
                    bio.seek(0)
                    cap = f"✂️ <b>Klip {int(dur_clip)} Detik Vertikal 9:16 Selesai!</b>\n🎬 {html.escape(res_vid['title'][:60])}\n📱 Siap Diunggah ke TikTok / IG Reels / YouTube Shorts"
                    await context.bot.send_video(chat_id=query.message.chat_id, video=bio, caption=cap, parse_mode="HTML")
                    os.remove(out_clip)
                else:
                    await query.message.reply_text("❌ Gagal merender klip vertikal.")

            os.remove(src_tmp)
            await query.message.reply_text("Klip selesai! Silakan pilih alat lain di bawah:", reply_markup=get_tools_hub_reply_keyboard())
        except Exception as e:
            logger.error(f"Error clip_opt: {e}", exc_info=True)
            await query.message.reply_text(f"❌ Gagal memproses klip: {e}", reply_markup=get_tools_hub_reply_keyboard())
        return

    if data.startswith("dl_preview_back:"):
        session_key = data.split(":")[1]
        info = MEDIA_DL_SESSIONS.get(session_key)
        if info:
            kb = get_dl_format_keyboard(session_key, is_slideshow=info.get('is_slideshow', False))
            await query.message.reply_text("Pilih format unduhan:", reply_markup=kb)
        return

    if data.startswith("dl_act:"):
        parts = data.split(":")
        mode = parts[1]
        session_key = parts[2]
        info = MEDIA_DL_SESSIONS.get(session_key)
        mode_names = {
            "video_hd": "Video HD (Tanpa Watermark)",
            "video_sd": "Video Hemat Kuota (480p)",
            "audio": "Audio / Musik MP3",
            "thumbnail": "Cover / Thumbnail HD",
            "slideshow": "Seluruh Slide Foto",
        }
        chosen_label = mode_names.get(mode, "Media")
        await query.message.reply_text(f"⏳ <i>Sedang memproses dan mengunduh {chosen_label}...</i>", parse_mode="HTML")

        try:
            res = download_media_custom(info['url'], mode=mode, tikwm_cache=info.get('tikwm_data'))

            if res['type'] == 'video':
                bio = io.BytesIO(res['data'])
                bio.name = res['filename']
                bio.seek(0)
                caption = (
                    f"🎬 <b>Video Berhasil Diunduh!</b>\n\n"
                    f"• Judul: <b>{html.escape(res['title'][:70])}</b>\n"
                    f"• Kualitas: <b>{chosen_label}</b>\n"
                    f"• Ukuran: <b>{res['filesize_mb']:.1f} MB</b>"
                )
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=bio,
                    caption=caption,
                    duration=res.get('duration', 0),
                    parse_mode="HTML"
                )

            elif res['type'] == 'audio':
                bio = io.BytesIO(res['data'])
                bio.name = res['filename']
                bio.seek(0)
                caption = f"🎵 <b>{html.escape(res['title'][:70])}</b>\nAudio Musik Resmi • MP3 Asli"
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=bio,
                    title=res['title'][:60],
                    performer=res.get('performer', 'Media Sound'),
                    duration=res.get('duration', 0),
                    caption=caption,
                    parse_mode="HTML"
                )

            elif res['type'] == 'image':
                bio = io.BytesIO(res['data'])
                bio.name = res['filename']
                bio.seek(0)
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=bio,
                    caption=f"📸 <b>Cover Sampul Video HD:</b> {html.escape(res['title'][:60])}",
                    parse_mode="HTML"
                )

            elif res['type'] == 'slideshow':
                imgs = res.get('images', [])
                await query.message.reply_text(f"📸 Mengirimkan <b>{len(imgs)} foto slide</b> tanpa watermark...", parse_mode="HTML")
                for i, img_b in enumerate(imgs):
                    bio = io.BytesIO(img_b)
                    bio.name = f"Slide_{i+1}.jpg"
                    bio.seek(0)
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=bio, caption=f"📸 Slide {i+1} / {len(imgs)}")

            await query.message.reply_text("Unduhan selesai! Silakan pilih alat lain pada menu di bawah:", reply_markup=get_tools_hub_reply_keyboard())
        except Exception as e:
            logger.error(f"Error dl_act: {e}", exc_info=True)
            await query.message.reply_text(f"❌ Gagal memproses unduhan: {e}", reply_markup=get_tools_hub_reply_keyboard())

    elif data == "main_menu":
        user_tg = query.from_user
        name_tg = html.escape(user_tg.first_name or "Pengguna")
        vip_status = "👑 VIP UNLIMITED" if u_data["is_vip"] else "Standar (Gratis)"
        username_str = f"@{user_tg.username}" if user_tg.username else "-"

        quota_info = "Unlimited" if u_data["is_vip"] else f"{u_data['quota_left']}x"
        vip_badge = "👑 VIP UNLIMITED" if u_data["is_vip"] else "Standar (Gratis)"

        text = f"""🎓 <b>Education Verification Suite</b>
Halo <b>{name_tg}</b> (<code>{user_tg.id}</code>)

👑 <b>Status:</b> {vip_badge} • <b>Kuota:</b> {quota_info}
📊 <b>Produktivitas:</b> {u_data['total_generated']} dokumen diterbitkan
🛡️ <b>Proteksi:</b> Anti-Fraud EXIF • Tinta Basah • 3D Mockup

<i>Silakan pilih layanan yang ingin digunakan pada menu di bawah:</i>"""

        await query.edit_message_text(
            text,
            reply_markup=get_main_menu_keyboard(u_data["is_vip"], u_data["quota_left"]),
            parse_mode="HTML"
        )

    elif data == "menu_teachers":
        text = "🌍 <b>Pilih Negara Pendidik / Guru:</b>\nTersedia dokumen verifikasi resmi untuk 13 negara:"
        await query.edit_message_text(text, reply_markup=get_countries_keyboard(), parse_mode="HTML")

    elif data == "menu_ktm_id":
        text = (
            "🎓 <b>Pusat Pembuatan Kartu Mahasiswa (KTM) Kampus Indonesia:</b>\n\n"
            "Dilengkapi lambang resmi beresolusi tinggi, tanda tangan basah tinta biru, "
            "dan pasfoto berjas formal rapi berlatar biru.\n\n"
            "Silakan pilih universitas:"
        )
        await query.edit_message_text(text, reply_markup=get_ktm_id_keyboard(), parse_mode="HTML")

    elif data == "menu_ktm_global":
        text = (
            "🏛️ <b>Student Identity Card (International Colleges):</b>\n\n"
            "Kartu identitas mahasiswa berstandar kampus terkemuka Amerika Serikat dan Inggris (Ivy League & Oxbridge) "
            "untuk verifikasi fasilitas edukasi global.\n\n"
            "Silakan pilih universitas:"
        )
        await query.edit_message_text(text, reply_markup=get_ktm_global_keyboard(), parse_mode="HTML")

    elif data == "menu_help":
        help_text = (
            "ℹ️ <b>Panduan Penggunaan Bot:</b>\n\n"
            "1. <b>Verifikasi Canva Edu</b>:\n"
            "   Pilih menu <i>Dokumen Guru</i> &rarr; pilih <i>Paket Lengkap</i> &rarr; unggah berkas NUPTK atau SK Pengangkatan ke formulir Canva.\n\n"
            "2. <b>Verifikasi Spotify / GitHub Student</b>:\n"
            "   Pilih menu <i>Kartu Mahasiswa (KTM)</i> &rarr; pilih kampus &rarr; gunakan tombol <b>Unduh File PDF / Dokumen</b> agar terkirim dalam resolusi 300 DPI.\n\n"
            "3. <b>Surat Keterangan Aktif (SKMA)</b>:\n"
            "   Setelah mencetak KTM, tekan tombol <i>📜 Cetak Surat Keterangan Aktif Kuliah</i> untuk bukti kedua verifikasi SheerID.\n\n"
            "4. <b>Anti-Fraud Sensor EXIF</b>:\n"
            "   Setiap file JPEG yang dihasilkan otomatis membawa metadata kamera Apple iPhone 14 Pro nyata."
        )
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali ke Menu", callback_data="main_menu")]])
        await query.edit_message_text(help_text, reply_markup=kb, parse_mode="HTML")

    # 2. Billing & Clipku Pay
    elif data == "menu_billing":
        text = (
            "💳 <b>Pusat Langganan & Top Up Kuota</b>\n"
            "Didukung pembayaran QRIS otomatis seketika melalui <b>Clipku Pay</b>:\n\n"
            "• <b>Paket Tambahan 10 Kuota</b>: Rp 5.000\n"
            "  <i>Masa aktif kuota selamanya tanpa batas waktu.</i>\n\n"
            "• <b>Paket VIP Unlimited (30 Hari)</b>: Rp 15.000\n"
            "  <i>Bebas cetak ribuan dokumen apa saja tanpa potongan kuota.</i>\n\n"
            "Pilih paket yang ingin diaktifkan:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ Beli +10 Kuota (Rp 5.000)", callback_data="buy_pkg:quota_10")],
            [InlineKeyboardButton("👑 Beli VIP Unlimited 30 Hari (Rp 15.000)", callback_data="buy_pkg:vip_30d")],
            [InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="main_menu")],
        ])
        await query.edit_message_text(text, reply_markup=kb, parse_mode="HTML")

    elif data.startswith("buy_pkg:"):
        pkg_type = data.split(":")[1]
        await query.edit_message_text("⏳ <i>Menghubungi gateway Clipku Pay untuk membuat tagihan QRIS...</i>", parse_mode="HTML")
        res = create_clipku_payment(user.id, pkg_type, user.first_name or "User")

        if res.get("success"):
            order_id = res["order_id"]
            amount = res["amount"]
            pay_url = res["payment_url"]

            text = (
                "🧾 <b>Tagihan Pembayaran Berhasil Dibuat!</b>\n\n"
                f"• Order ID: <code>{order_id}</code>\n"
                f"• Total Bayar: <b>Rp {amount:,}</b>\n"
                "• Metode: QRIS (BCA, DANA, GoPay, OVO, ShopeePay, LinkAja, Mandiri)\n\n"
                "Silakan klik tombol <b>Bayar Sekarang</b> di bawah untuk membuka halaman pembayaran QRIS, lalu tekan <b>Cek Status Pembayaran</b> setelah menyelesaikan transfer."
            )
            pay_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 Bayar Sekarang (Buka QRIS)", url=pay_url)],
                [InlineKeyboardButton("🔄 Cek Status Pembayaran", callback_data=f"chk_pay:{order_id}")],
                [InlineKeyboardButton("« Batal", callback_data="menu_billing")],
            ])
            await query.edit_message_text(text, reply_markup=pay_kb, parse_mode="HTML")
        else:
            await query.edit_message_text(
                f"❌ Gagal membuat pembayaran: {html.escape(res.get('error', 'Terjadi kesalahan sistem'))}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali", callback_data="menu_billing")]]),
                parse_mode="HTML"
            )

    elif data.startswith("chk_pay:"):
        order_id = data.split(":")[1]
        check_res = check_and_apply_payment(order_id)

        if check_res.get("success"):
            msg = check_res.get("message", "Pembayaran Sukses!")
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("« Mulai Cetak Dokumen", callback_data="main_menu")]])
            await query.edit_message_text(f"✅ {msg}", reply_markup=kb, parse_mode="HTML")
        else:
            msg = check_res.get("message", "Pembayaran belum terdeteksi. Silakan coba sesaat lagi.")
            pay_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Cek Status Lagi", callback_data=f"chk_pay:{order_id}")],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
            ])
            await query.edit_message_text(f"⏱️ <b>Status Pembayaran:</b>\n\n{msg}", reply_markup=pay_kb, parse_mode="HTML")

    # 3. Pembuatan KTM Otomatis
    elif data == "menu_pelajar":
            text = (
                "🏫 <b>Pusat Pembuatan Kartu Tanda Pelajar (SMA / SMK Negeri Favorit):</b>\n\n"
                "Dilengkapi logo resmi Tut Wuri Handayani Kemendikbud, format NISN 10 digit Dapodik, "
                "jurusan MIPA/IPS atau kejuruan SMK, barcode, RFID chip, serta tanda tangan & stempel dinas Kepala Sekolah.\n\n"
                "Silakan pilih sekolah:"
            )
            await query.edit_message_text(text, reply_markup=get_pelajar_keyboard(), parse_mode="HTML")

    elif data.startswith("gen_pelajar:"):
        sch_code = data.split(":")[1]

        # Cek Kuota
        if not u_data["is_vip"] and u_data["quota_left"] <= 0:
            text = "⚠️ <b>Kuota Cetak Harian Anda Telah Habis!</b>\n\nSilakan top up kuota atau aktifkan paket VIP."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Beli Kuota / VIP", callback_data="menu_billing")]])
            await query.edit_message_text(text, reply_markup=kb, parse_mode="HTML")
            return

        await query.edit_message_text("⏳ <b>Sedang merender Kartu Pelajar resmi...</b>\n• Menghubungkan basis data NPSN & Dapodik\n• Memasang stempel dinas Kepala Sekolah...", parse_mode="HTML")

        try:
            first_names_m = ["Dimas", "Ahmad", "Fajar", "Bagus", "Rizky", "Aditya", "Bayu", "Arif", "Hendra"]
            first_names_f = ["Siti", "Nur", "Putri", "Dian", "Anisa", "Dewi", "Rini", "Ayu", "Fitri"]
            last_names = ["Prasetyo", "Santoso", "Saputra", "Hidayat", "Kusuma", "Wibowo", "Nugroho", "Setiawan"]

            is_female = random.choice([True, False])
            first = random.choice(first_names_f if is_female else first_names_m)
            last = random.choice(last_names)
            gender_param = "Female" if is_female else "Male"

            ktpel_png = pelajar_engine.generate(first, last, school_code=sch_code, gender=gender_param)
            ktpel_exif = inject_camera_exif(ktpel_png)
            consume_quota(user.id)

            session_key = f"{user.id}_last_pelajar"
            SESSION_DOC_CACHE[session_key] = {
                "png_bytes": ktpel_png,
                "exif_bytes": ktpel_exif,
                "first": first,
                "last": last,
                "univ_code": sch_code,
                "type": "KTPEL",
            }

            caption = (
                f"✅ <b>Kartu Tanda Pelajar Berhasil Dibuat!</b>\n\n"
                f"🏫 <b>Sekolah:</b> {sch_code.replace('_', ' ')}\n"
                f"👤 <b>Nama Siswa:</b> {first} {last} ({gender_param})\n"
                "🏷️ <b>Status:</b> Peserta Didik Aktif Kemendikbud\n"
                "📸 <b>Anti-Fraud:</b> Disertai EXIF Sensor Kamera Smartphone\n"
                "🖋️ <b>Legalitas:</b> Cap Stempel Dinas & Tanda Tangan Kepala Sekolah\n\n"
                "<i>Silakan pilih opsi unduhan atau foto di atas meja:</i>"
            )

            bio = io.BytesIO(ktpel_exif)
            bio.name = f"KTPEL_{sch_code}_{first}_{last}.jpg"
            bio.seek(0)

            act_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 FOTO FISIK DI ATAS MEJA (3D MOCKUP)", callback_data=f"desk_mockup:{session_key}")],
                [
                    InlineKeyboardButton("📥 Unduh PDF", callback_data=f"dl_pdf:{session_key}"),
                    InlineKeyboardButton("📁 Unduh Gambar HD", callback_data=f"dl_raw:{session_key}")
                ],
                [InlineKeyboardButton("🔄 Buat Sekolah Lain", callback_data="menu_pelajar")],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
            ])

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=bio,
                caption=caption,
                reply_markup=act_kb,
                parse_mode="HTML"
            )
            await query.message.delete()

        except Exception as e:
            logger.error(f"Error generating Kartu Pelajar: {e}", exc_info=True)
            await query.message.reply_text(f"❌ Gagal membuat kartu pelajar: {html.escape(str(e))}")

    elif data.startswith("gen_ktm:"):
        univ_code = data.split(":")[1]
        if univ_code == "RANDOM":
            univ_code = None

        # Cek Kuota
        if not u_data["is_vip"] and u_data["quota_left"] <= 0:
            text = (
                "⚠️ <b>Kuota Cetak Harian Anda Telah Habis!</b>\n\n"
                "Kuota gratis (3x per hari) Anda sudah terpakai seluruhnya. "
                "Silakan tunggu hingga reset besok atau beli paket tambahan melalui Clipku Pay:"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Tambah Kuota / VIP", callback_data="menu_billing")],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
            ])
            await query.edit_message_text(text, reply_markup=kb, parse_mode="HTML")
            return

        await query.edit_message_text(
            "⏳ <b>Sedang merender Kartu Tanda Mahasiswa (KTM)...</b>\n"
            "• Menyematkan lambang resmi institusi\n"
            "• Memasang pasfoto formal & tanda tangan basah\n"
            "• Menyuntikkan metadata EXIF kamera profesional...",
            parse_mode="HTML"
        )

        try:
            first_names_m = ["Dimas", "Ahmad", "Fajar", "Bagus", "Rizky", "Aditya", "Bayu", "Arif", "Hendra"]
            first_names_f = ["Siti", "Nur", "Putri", "Dian", "Anisa", "Dewi", "Rini", "Ayu", "Fitri"]
            last_names = ["Prasetyo", "Santoso", "Saputra", "Hidayat", "Kusuma", "Wibowo", "Nugroho", "Setiawan"]

            is_female = random.choice([True, False])
            first = random.choice(first_names_f if is_female else first_names_m)
            last = random.choice(last_names)
            gender_param = "Female" if is_female else "Male"

            ktm_png_bytes = ktm_engine.generate(first, last, univ_code=univ_code, gender=gender_param)
            
            # Suntikkan Anti-Fraud EXIF kamera
            ktm_exif_bytes = inject_camera_exif(ktm_png_bytes)

            # Kurangi kuota
            consume_quota(user.id)

            # Simpan ke cache sesi untuk unduhan PDF/PNG
            session_key = f"{user.id}_last_ktm"
            SESSION_DOC_CACHE[session_key] = {
                "png_bytes": ktm_png_bytes,
                "exif_bytes": ktm_exif_bytes,
                "first": first,
                "last": last,
                "univ_code": univ_code or "UT",
                "type": "KTM",
            }

            u_target = "Universitas Terbuka (UT)" if (univ_code == "UT" or univ_code is None) else univ_code
            caption = (
                f"✅ <b>Kartu Tanda Mahasiswa (KTM) Berhasil Dibuat!</b>\n\n"
                f"🏛️ <b>Universitas:</b> {u_target}\n"
                f"👤 <b>Nama:</b> {first} {last} ({gender_param})\n"
                "🎓 <b>Jenjang:</b> Strata 1 (S1) Mahasiswa Aktif\n"
                "📸 <b>Anti-Fraud:</b> Disertai Metadata Sensor Kamera Nyata\n"
                "🖋️ <b>Legalitas:</b> Tanda Tangan Basah & Cap Biro Akademik\n\n"
                "<i>Gunakan tombol di bawah untuk mengunduh versi PDF / PNG tanpa kompresi, atau mencetak Surat Keterangan Aktif (SKMA):</i>"
            )

            bio = io.BytesIO(ktm_exif_bytes)
            bio.name = f"KTM_{univ_code or 'UT'}_{first}_{last}.jpg"
            bio.seek(0)

            act_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 FOTO FISIK DI ATAS MEJA (3D MOCKUP)", callback_data=f"desk_mockup:{session_key}")],
                [
                    InlineKeyboardButton("📥 Unduh PDF", callback_data=f"dl_pdf:{session_key}"),
                    InlineKeyboardButton("📁 Unduh Gambar HD", callback_data=f"dl_raw:{session_key}")
                ],
                [InlineKeyboardButton("📜 Cetak Surat Keterangan Aktif (SKMA)", callback_data=f"gen_skma:{session_key}")],
                [InlineKeyboardButton("🔄 Buat Kampus Lain", callback_data="menu_ktm_id")],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
            ])

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=bio,
                caption=caption,
                reply_markup=act_kb,
                parse_mode="HTML"
            )
            await query.message.delete()

        except Exception as e:
            logger.error(f"Error generating KTM: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ Terjadi kesalahan saat membuat KTM: {html.escape(str(e))}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali", callback_data="menu_ktm_id")]]),
                parse_mode="HTML"
            )

    # 4. Cetak Surat Keterangan Mahasiswa Aktif (SKMA)
    elif data.startswith("gen_skma:"):
        session_key = data.split(":")[1]
        cache = SESSION_DOC_CACHE.get(session_key)
        
        full_name = f"{cache['first']} {cache['last']}" if cache else f"{user.first_name or 'Mahasiswa'}"
        univ_code = cache.get("univ_code", "UT") if cache else "UT"

        await query.message.reply_text("⏳ <i>Sedang menerbitkan Surat Keterangan Mahasiswa Aktif (SKMA) resmi...</i>", parse_mode="HTML")

        try:
            skma_bytes = skma_engine.generate(full_name=full_name, univ_code=univ_code)
            skma_exif = inject_camera_exif(skma_bytes)

            skma_key = f"{user.id}_last_skma"
            SESSION_DOC_CACHE[skma_key] = {
                "png_bytes": skma_bytes,
                "exif_bytes": skma_exif,
                "first": full_name.replace(" ", "_"),
                "last": "SKMA",
                "univ_code": univ_code,
                "type": "SKMA",
            }

            caption = (
                f"📜 <b>Surat Keterangan Mahasiswa Aktif (SKMA) Diterbitkan!</b>\n\n"
                f"👤 <b>Atas Nama:</b> {full_name}\n"
                f"🏛️ <b>Institusi:</b> Universitas Terbuka (UT)\n"
                "📑 <b>Fungsi:</b> Bukti kedua pendaftaran resmi (Proof of Enrollment) verifikasi SheerID / GitHub Student.\n"
                "🖋️ <b>Pengesahan:</b> Cap Basah & Tanda Tangan Direktur Akademik"
            )

            bio = io.BytesIO(skma_exif)
            bio.name = f"SKMA_{full_name.replace(' ', '_')}.jpg"
            bio.seek(0)

            sk_kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📥 Unduh SKMA PDF", callback_data=f"dl_pdf:{skma_key}"),
                    InlineKeyboardButton("📁 Unduh Dokumen Asli (PNG)", callback_data=f"dl_raw:{skma_key}")
                ],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
            ])

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=bio,
                caption=caption,
                reply_markup=sk_kb,
                parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"Error generating SKMA: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ Gagal menerbitkan SKMA: {html.escape(str(e))}",
                parse_mode="HTML"
            )

    # 5. Unduh Dokumen Tanpa Kompresi (PDF / PNG Asli)
    
    # Handler: Foto Fisik Kartu di Atas Meja (Desk Mockup)
    
    # Handler: Mockup Tali Lanyard & Mika Card Holder
    elif data.startswith("lanyard_mockup:"):
        session_key = data.split(":")[1]
        cache = SESSION_DOC_CACHE.get(session_key)
        if not cache:
            await query.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan buat ulang kartu.")
            return

        await query.message.reply_text("⏳ <i>Sedang merender kartu di dalam mika card holder transparan + tali lanyard kampus resmi...</i>", parse_mode="HTML")

        try:
            univ_code = cache.get("univ_code", "UT")
            lanyard_bytes = render_lanyard_card_holder(cache["png_bytes"], univ_code=univ_code)
            lanyard_exif = inject_camera_exif(lanyard_bytes)

            bio = io.BytesIO(lanyard_exif)
            bio.name = f"LANYARD_HOLDER_{cache['first']}_{cache['last']}.jpg"
            bio.seek(0)

            caption = """🪪 <b>Mockup Mika Card Holder + Tali Lanyard Kampus</b>

✓ Wadah mika plastik transparan dengan lubang oval & tepian pres seal
✓ Pengait klip logam stainless steel & ring gantungan mika
✓ Tali lanyard kampus resmi dengan jahitan tepi & warna identitas
✓ Metadata sensor kamera smartphone asli (iPhone / Samsung)

<i>Tampak seperti kartu fisik mahasiswa yang siap dipakai ke kampus!</i>"""

            ret_kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🖐️ Pegang Tangan (POV)", callback_data=f"handheld_mockup:{session_key}"),
                    InlineKeyboardButton("📸 Foto Meja (Desk)", callback_data=f"desk_mockup:{session_key}"),
                ],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")]
            ])

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=bio,
                caption=caption,
                reply_markup=ret_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error rendering lanyard mockup: {e}", exc_info=True)
            await query.message.reply_text(f"❌ Gagal merender lanyard: {html.escape(str(e))}")

    # Handler: Mockup Sedang Dipegang Tangan (Handheld POV)
    elif data.startswith("handheld_mockup:"):
        session_key = data.split(":")[1]
        cache = SESSION_DOC_CACHE.get(session_key)
        if not cache:
            await query.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan buat ulang kartu.")
            return

        await query.message.reply_text("⏳ <i>Sedang merender simulasi foto kartu dipegang tangan orang (POV) dengan pencahayaan ruangan...</i>", parse_mode="HTML")

        try:
            hand_bytes = render_handheld_pov(cache["png_bytes"])
            hand_exif = inject_camera_exif(hand_bytes)

            bio = io.BytesIO(hand_exif)
            bio.name = f"HANDHELD_POV_{cache['first']}_{cache['last']}.jpg"
            bio.seek(0)

            caption = """🖐️ <b>Foto Fisik Sedang Dipegang Tangan (Hand-Held POV)</b>

✓ Tampak ibu jari (thumb) memegang tepian fisik kartu secara alami
✓ Efek kedalaman bayangan kartu terangkat dari meja
✓ Pantulan kilau blitz/lampu ruangan alami di permukaan PVC
✓ Disuntikkan EXIF sensor kamera smartphone asli

<i>Sangat ampuh melewati audit manual manusia (human inspection review)!</i>"""

            ret_kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪪 Mika + Lanyard", callback_data=f"lanyard_mockup:{session_key}"),
                    InlineKeyboardButton("📸 Foto Meja (Desk)", callback_data=f"desk_mockup:{session_key}"),
                ],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")]
            ])

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=bio,
                caption=caption,
                reply_markup=ret_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error rendering handheld mockup: {e}", exc_info=True)
            await query.message.reply_text(f"❌ Gagal merender handheld POV: {html.escape(str(e))}")

    # Handler: Menu Referral (Undang Teman)
    elif data == "menu_referral":
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        user_id = query.from_user.id
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        stats = get_referral_stats(user_id)

        text = f"""🎁 <b>PROGRAM REFERRAL: UNDANG TEMAN DAPAT KUOTA!</b>

Bagikan tautan undangan unik Anda kepada teman, grup, atau komunitas.
Setiap 1 orang yang bergabung lewat tautan Anda, Anda akan mendapatkan <b>+2 Kuota Cetak Gratis</b> langsung masuk ke akun Anda!

📊 <b>Statistik Anda:</b>
• Teman Berhasil Bergabung: <b>{stats['count']} orang</b>
• Kuota Tersedia: <b>{stats['quota']}x cetak</b>

🔗 <b>Tautan Undangan Anda:</b>
<code>{ref_link}</code>

<i>(Klik tautan di atas untuk menyalin, lalu bagikan ke teman Anda)</i>"""

        ref_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Bagikan ke Telegram", url=f"https://t.me/share/url?url={ref_link}&text=Ayo%20buat%20dokumen%20pendidik%20dan%20KTM%20mahasiswa%20resmi%20beresolusi%20tinggi%20di%20bot%20ini!")],
            [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")]
        ])

        await query.message.edit_text(text, reply_markup=ref_kb, parse_mode="HTML")
        return

    elif data.startswith("desk_mockup:"):
        session_key = data.split(":")[1]
        cache = SESSION_DOC_CACHE.get(session_key)
        if not cache:
            await query.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan buat ulang kartu.")
            return

        await query.message.reply_text("⏳ <i>Sedang merender simulasi foto fisik kartu di atas meja kayu dengan sudut 3D & pencahayaan alami...</i>", parse_mode="HTML")

        try:
            desk_bytes = render_card_on_desk(cache["png_bytes"])
            desk_exif = inject_camera_exif(desk_bytes)

            bio = io.BytesIO(desk_exif)
            bio.name = f"FOTO_MEJA_{cache['first']}_{cache['last']}.jpg"
            bio.seek(0)

            caption = "📸 <b>Foto Fisik Kartu di Atas Meja (Physical Desk Mockup)</b>\n\n✓ Perspektif kemiringan 3D alami\n✓ Dual-stage drop shadow & ambient occlusion\n✓ Pantulan cahaya ruangan halus pada permukaan PVC\n✓ Disuntikkan EXIF sensor kamera smartphone asli\n\n<i>Sangat efektif lolos verifikasi manual human review.</i>"

            desk_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("« Kembali ke Pilihan Dokumen", callback_data="main_menu")]
            ])

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=bio,
                caption=caption,
                reply_markup=desk_kb,
                parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"Error rendering desk mockup: {e}", exc_info=True)
            await query.message.reply_text(f"❌ Gagal membuat mockup meja: {html.escape(str(e))}")

    elif data.startswith("dl_pdf:"):
        session_key = data.split(":")[1]
        cache = SESSION_DOC_CACHE.get(session_key)
        if not cache:
            await query.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan cetak ulang dokumen.")
            return

        pdf_bytes = convert_to_pdf(cache["png_bytes"])
        bio = io.BytesIO(pdf_bytes)
        bio.name = f"{cache['type']}_{cache['first']}_{cache['last']}.pdf"
        bio.seek(0)

        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=bio,
            caption=f"📄 <b>Berkas PDF Siap Cetak (300 DPI)</b>\nDokumen: {cache['type']} - {cache['first']} {cache['last']}",
            parse_mode="HTML"
        )

    elif data.startswith("dl_raw:"):
        session_key = data.split(":")[1]
        cache = SESSION_DOC_CACHE.get(session_key)
        if not cache:
            await query.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan cetak ulang dokumen.")
            return

        bio = io.BytesIO(cache["png_bytes"])
        bio.name = f"{cache['type']}_{cache['first']}_{cache['last']}_HD.png"
        bio.seek(0)

        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=bio,
            caption=f"📁 <b>Berkas Gambar PNG Asli (Resolusi Penuh Tanpa Kompresi)</b>\nDokumen: {cache['type']}",
            parse_mode="HTML"
        )

    # 6. Pemilihan Dokumen Guru (13 Negara)
    elif data.startswith("sel_c:"):
        country_code = data.split(":")[1]
        context.user_data["country"] = country_code

        gen_cls = get_country(country_code)
        gen = gen_cls()
        doc_types = gen.get_document_types()

        c_name = html.escape(COUNTRY_FLAGS.get(country_code, country_code.upper()))

        buttons = []
        buttons.append([InlineKeyboardButton("📦 CETAK SEMUA DOKUMEN (PAKET LENGKAP)", callback_data="gen_doc:all")])

        for dt in doc_types:
            label = DOC_LABELS.get(dt, dt.replace("_", " ").title())
            buttons.append([InlineKeyboardButton(label, callback_data="gen_doc:" + dt)])

        buttons.append([InlineKeyboardButton("« Ganti Negara", callback_data="menu_teachers")])

        text = (
            f"Negara Terpilih: <b>{c_name}</b>\n\n"
            f"Tersedia <b>{len(doc_types)} jenis dokumen</b> resmi untuk negara ini.\n"
            "Silakan pilih dokumen satuan, atau pilih <b>📦 Paket Lengkap</b> untuk mencetak semua dokumen sekaligus dengan identitas yang seragam:"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")

    elif data.startswith("gen_doc:"):
        target_doc = data.split(":")[1]
        country_code = context.user_data.get("country", "indonesia")

        # Cek Kuota
        if not u_data["is_vip"] and u_data["quota_left"] <= 0:
            text = (
                "⚠️ <b>Kuota Cetak Harian Anda Telah Habis!</b>\n\n"
                "Silakan beli paket kuota tambahan atau VIP unlimited untuk melanjutkan."
            )
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Beli Kuota / VIP", callback_data="menu_billing")]])
            await query.edit_message_text(text, reply_markup=kb, parse_mode="HTML")
            return

        gen_cls = get_country(country_code)
        gen = gen_cls()
        available_types = gen.get_document_types()
        docs_to_generate = available_types if target_doc == "all" else [target_doc]

        await query.edit_message_text(
            f"⏳ <b>Sedang memproses {len(docs_to_generate)} dokumen pendidik...</b>\n"
            "Sistem sedang merender grafis beresolusi tinggi dan menyematkan metadata EXIF...",
            parse_mode="HTML"
        )

        try:
            first = random.choice(gen.first_names) if gen.first_names else "Budi"
            last = random.choice(gen.last_names) if gen.last_names else "Santoso"
            school = random.choice(gen.schools) if gen.schools else {"name": "National High School"}
            position = random.choice(gen.positions) if gen.positions else "Teacher"

            first_lower = first.lower()
            female_clues = ['siti', 'nur', 'sri', 'dewi', 'putri', 'anisa', 'ratna', 'dian', 'rini', 'tri', 'endang', 'maya', 'fitri', 'ayu', 'wulandari', 'mary', 'sarah', 'jessica', 'emily', 'anna', 'emma', 'claire', 'marie', 'elena']
            gender = 'Female' if any(c in first_lower for c in female_clues) else 'Male'

            gen._current_person_id = f"{first.lower()}_{last.lower()}"
            gen._current_gender = gender

            day = random.randint(1, 28)
            month = random.randint(1, 12)
            year = random.randint(1976, 1996)
            dob = f"{day:02d}/{month:02d}/{year}"

            school_name = html.escape(str(school.get("name", "Sekolah")))
            full_name = html.escape(first + " " + last)
            pos_label = html.escape(str(position))
            country_label = html.escape(COUNTRY_FLAGS.get(country_code, country_code.upper()))

            consume_quota(user.id)

            for dt in docs_to_generate:
                img_bytes = gen.generate_document(dt, first, last, school, position, dob)
                doc_label = html.escape(DOC_LABELS.get(dt, dt.replace("_", " ").title()))

                # Suntikkan Anti-Fraud EXIF kamera
                img_exif = inject_camera_exif(img_bytes)

                caption = (
                    f"✅ <b>{doc_label}</b>\n\n"
                    f"👤 <b>Nama:</b> {full_name} ({gender})\n"
                    f"🏫 <b>Sekolah:</b> {school_name}\n"
                    f"💼 <b>Jabatan:</b> {pos_label}\n"
                    f"🌍 <b>Negara:</b> {country_label}"
                )

                bio = io.BytesIO(img_exif)
                bio.name = f"{country_code}_{dt}_{first}_{last}.jpg"
                bio.seek(0)

                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=bio,
                    caption=caption,
                    parse_mode="HTML"
                )

            again_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Buat Lagi", callback_data="sel_c:" + country_code)],
                [InlineKeyboardButton("🌍 Ganti Negara", callback_data="menu_teachers")],
                [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
            ])

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"🎉 <b>Selesai!</b> {len(docs_to_generate)} berkas dokumen pendidik telah dikirim lengkap.",
                reply_markup=again_kb,
                parse_mode="HTML"
            )
            await query.message.delete()

        except Exception as e:
            logger.error(f"Error generating teacher doc: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ Terjadi kesalahan: {html.escape(str(e))}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali", callback_data="menu_teachers")]]),
                parse_mode="HTML"
            )


# -------------------------------------------------------------
# FLOW: Custom Name & Photo (ConversationHandler)
# -------------------------------------------------------------

async def custom_flow_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "✍️ <b>Mode Kustom: Buat Dokumen dengan Identitas Anda Sendiri</b>\n\n"
        "Langkah 1 dari 3:\n"
        "Silakan ketik dan kirimkan <b>Nama Lengkap Anda</b> (contoh: <i>Muhammad Rizky Pratama</i>):"
    )
    cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batalkan", callback_data="cancel_custom")]])
    await query.edit_message_text(text, reply_markup=cancel_kb, parse_mode="HTML")
    return CUSTOM_NAME


async def custom_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    if len(user_input) < 3:
        await update.message.reply_text("⚠️ Nama terlalu pendek. Silakan ketik nama lengkap Anda:")
        return CUSTOM_NAME

    parts = user_input.split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else "Pratama"

    context.user_data["custom_first"] = first_name
    context.user_data["custom_last"] = last_name

    text = (
        f"✅ Nama tercatat: <b>{first_name} {last_name}</b>\n\n"
        "Langkah 2 dari 3:\n"
        "Silakan <b>kirimkan foto wajah Anda</b> (pasfoto formal/selfie rapi).\n\n"
        "<i>Tips: Bot akan otomatis memotong dan menyesuaikan foto ke bingkai kartu mahasiswa resmi.</i>\n"
        "<i>Jika tidak ingin menggunakan foto pribadi, ketik /lewati untuk memakai foto model formal bot.</i>"
    )
    await update.message.reply_text(text, parse_mode="HTML")
    return CUSTOM_PHOTO


async def custom_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        try:
            user_im = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
            context.user_data["custom_photo"] = user_im
        except Exception:
            context.user_data["custom_photo"] = None
    else:
        context.user_data["custom_photo"] = None

    return await ask_custom_university(update, context)


async def custom_photo_skipped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["custom_photo"] = None
    return await ask_custom_university(update, context)


async def ask_custom_university(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Langkah 3 dari 3:\n"
        "Silakan pilih <b>Universitas</b> yang Anda inginkan:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 UNIVERSITAS TERBUKA (UT)", callback_data="c_univ:UT")],
        [InlineKeyboardButton("🎓 UNIVERSITAS INDONESIA (UI)", callback_data="c_univ:UI")],
        [InlineKeyboardButton("🎓 UNIVERSITAS GADJAH MADA (UGM)", callback_data="c_univ:UGM")],
        [InlineKeyboardButton("🎓 INSTITUT TEKNOLOGI BANDUNG (ITB)", callback_data="c_univ:ITB")],
        [InlineKeyboardButton("🏛️ HARVARD UNIVERSITY (US)", callback_data="c_univ:HARVARD")],
        [InlineKeyboardButton("🏛️ UNIVERSITY OF OXFORD (UK)", callback_data="c_univ:OXFORD")],
        [InlineKeyboardButton("❌ Batalkan", callback_data="cancel_custom")],
    ])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")
    return CUSTOM_UNIV


async def custom_univ_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel_custom":
        await query.edit_message_text("❌ Pembuatan kustom dibatalkan.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Menu Utama", callback_data="main_menu")]]))
        return ConversationHandler.END

    univ_code = data.split(":")[1]
    first = context.user_data.get("custom_first", "Budi")
    last = context.user_data.get("custom_last", "Santoso")
    user_photo = context.user_data.get("custom_photo")

    await query.edit_message_text("⏳ <i>Sedang mencetak KTM Kustom dengan foto & identitas Anda...</i>", parse_mode="HTML")

    try:
        ktm_png = ktm_engine.generate(first, last, univ_code=univ_code, custom_photo=user_photo)
        ktm_exif = inject_camera_exif(ktm_png)

        session_key = f"{query.from_user.id}_custom_ktm"
        SESSION_DOC_CACHE[session_key] = {
            "png_bytes": ktm_png,
            "exif_bytes": ktm_exif,
            "first": first,
            "last": last,
            "univ_code": univ_code,
            "type": "KTM_CUSTOM",
        }

        caption = (
            f"🎉 <b>KTM Kustom Berhasil Dibuat!</b>\n\n"
            f"👤 <b>Nama Anda:</b> {first} {last}\n"
            f"🏛️ <b>Universitas:</b> {univ_code}\n"
            "📸 <b>Foto:</b> Pasfoto Personal Anda\n"
            "🖋️ <b>Tanda Tangan & Cap:</b> Tinta Basah Terverifikasi"
        )

        bio = io.BytesIO(ktm_exif)
        bio.name = f"KTM_CUSTOM_{first}_{last}.jpg"
        bio.seek(0)

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 FOTO FISIK DI ATAS MEJA (3D MOCKUP)", callback_data=f"desk_mockup:{session_key}")],
            [
                InlineKeyboardButton("📥 Unduh PDF", callback_data=f"dl_pdf:{session_key}"),
                InlineKeyboardButton("📁 Unduh Gambar HD", callback_data=f"dl_raw:{session_key}")
            ],
            [InlineKeyboardButton("📜 Cetak Surat Keterangan Aktif (SKMA)", callback_data=f"gen_skma:{session_key}")],
            [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
        ])

        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=bio,
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
        await query.message.delete()

    except Exception as e:
        logger.error(f"Error in custom KTM: {e}", exc_info=True)
        await query.message.reply_text(f"❌ Terjadi kesalahan: {html.escape(str(e))}")

    return ConversationHandler.END


async def cancel_custom_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("❌ Proses pembuatan kustom dibatalkan.")
    else:
        await update.message.reply_text("❌ Proses pembuatan kustom dibatalkan.")
    return ConversationHandler.END



async def ktm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /ktm [UNIV] [NAMA] atau buka menu KTM"""
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")

    args = context.args
    if not args:
        text = (
            "🎓 <b>Pusat Pembuatan Kartu Mahasiswa (KTM) Kampus Indonesia:</b>\n\n"
            "Dilengkapi lambang resmi beresolusi tinggi, tanda tangan basah tinta biru, "
            "dan pasfoto berjas formal rapi berlatar biru.\n\n"
            "Silakan pilih universitas:"
        )
        await update.message.reply_text(text, reply_markup=get_ktm_id_keyboard(), parse_mode="HTML")
        return

    # One-shot generator: /ktm UGM Budi Santoso
    univ_code = args[0].upper()
    valid_codes = [u["code"] for u in ktm_engine.universities_id] + [u["code"] for u in ktm_engine.universities_global]
    if univ_code not in valid_codes:
        univ_code = "UT"
        full_name = " ".join(args)
    else:
        full_name = " ".join(args[1:]) if len(args) > 1 else (user.first_name or "Mahasiswa")

    # Cek kuota
    if not u_data["is_vip"] and u_data["quota_left"] <= 0:
        await update.message.reply_text("⚠️ <b>Kuota Cetak Harian Anda Telah Habis!</b>\nSilakan gunakan /kuota untuk top up.", parse_mode="HTML")
        return

    name_parts = full_name.split(maxsplit=1)
    first = name_parts[0].upper()
    last = name_parts[1].upper() if len(name_parts) > 1 else "MAHASISWA"

    await update.message.reply_text(f"⏳ <i>Membuat KTM {univ_code} atas nama {first} {last}...</i>", parse_mode="HTML")
    try:
        png_bytes = ktm_engine.generate(first_name=first, last_name=last, univ_code=univ_code)
        consume_quota(user.id)

        session_key = f"{user.id}_{int(datetime.now().timestamp())}"
        SESSION_DOC_CACHE[session_key] = {
            "type": "ktm",
            "png_bytes": png_bytes,
            "first": first,
            "last": last,
            "univ_code": univ_code,
        }

        jpeg_bytes = inject_camera_exif(png_bytes)
        bio = io.BytesIO(jpeg_bytes)
        bio.name = f"KTM_{univ_code}_{first}_{last}.jpg"
        bio.seek(0)

        act_kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📸 Foto di Meja", callback_data=f"desk_mockup:{session_key}"),
                InlineKeyboardButton("🪪 Mika + Lanyard", callback_data=f"lanyard_mockup:{session_key}"),
                InlineKeyboardButton("🖐️ Pegang Tangan", callback_data=f"handheld_mockup:{session_key}")
            ],
            [
                InlineKeyboardButton("📜 Cetak SKMA", callback_data=f"skma:{session_key}"),
                InlineKeyboardButton("📥 Unduh PDF", callback_data=f"dl_pdf:{session_key}"),
                InlineKeyboardButton("📁 Unduh HD", callback_data=f"dl_raw:{session_key}")
            ],
            [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")],
        ])

        caption = f"✅ <b>KTM {univ_code} Berhasil Diterbitkan!</b>\n\n• Nama: <b>{first} {last}</b>\n• Format: Ultra HD 300 DPI\n• EXIF Kamera: Apple iPhone 14 Pro"
        await update.message.reply_photo(photo=bio, caption=caption, reply_markup=act_kb, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error quick ktm: {e}")
        await update.message.reply_text(f"❌ Gagal membuat KTM: {e}")


async def pelajar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /pelajar"""
    text = (
        "🏫 <b>Pusat Pembuatan Kartu Tanda Pelajar (SMA / SMK Negeri Favorit):</b>\n\n"
        "Dilengkapi logo resmi Tut Wuri Handayani Kemendikbud, tanda tangan basah Kepala Sekolah, "
        "stempel dinas sekolah, dan NISN 10 digit resmi.\n\n"
        "Silakan pilih sekolah:"
    )
    await update.message.reply_text(text, reply_markup=get_pelajar_keyboard(), parse_mode="HTML")


async def guru_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /guru"""
    text = (
        "👨‍🏫 <b>Pusat Pembuatan Dokumen Sertifikat Guru (Canva Edu):</b>\n\n"
        "Pilih negara lembaga pendidik untuk menghasilkan Kartu NUPTK, Surat Keputusan Pengangkatan, "
        "dan Surat Keterangan Mengajar resmi:"
    )
    await update.message.reply_text(text, reply_markup=get_countries_keyboard(), parse_mode="HTML")


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /referral"""
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    user_id = update.effective_user.id
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    stats = get_referral_stats(user_id)

    text = f"""🎁 <b>PROGRAM REFERRAL: UNDANG TEMAN DAPAT KUOTA!</b>

Bagikan tautan undangan unik Anda kepada teman, grup, atau komunitas.
Setiap 1 orang yang bergabung lewat tautan Anda, Anda akan mendapatkan <b>+2 Kuota Cetak Gratis</b> langsung masuk ke akun Anda!

📊 <b>Statistik Anda:</b>
• Teman Berhasil Bergabung: <b>{stats['count']} orang</b>
• Kuota Tersedia: <b>{stats['quota']}x cetak</b>

🔗 <b>Tautan Undangan Anda:</b>
<code>{ref_link}</code>

<i>(Klik tautan di atas untuk menyalin, lalu bagikan ke teman Anda)</i>"""

    ref_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Bagikan ke Telegram", url=f"https://t.me/share/url?url={ref_link}&text=Ayo%20buat%20dokumen%20pendidik%20dan%20KTM%20mahasiswa%20resmi%20beresolusi%20tinggi%20di%20bot%20ini!")],
        [InlineKeyboardButton("« Menu Utama", callback_data="main_menu")]
    ])
    await update.message.reply_text(text, reply_markup=ref_kb, parse_mode="HTML")


async def bantuan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /bantuan"""
    help_text = (
        "ℹ️ <b>Panduan Penggunaan Bot:</b>\n\n"
        "1. <b>Verifikasi Canva Edu</b>:\n"
        "   Pilih menu <i>Guru / Canva Edu</i> &rarr; pilih <i>Paket Lengkap</i> &rarr; unggah berkas NUPTK atau SK Pengangkatan ke formulir Canva.\n\n"
        "2. <b>Verifikasi Spotify / GitHub Student</b>:\n"
        "   Pilih menu <i>KTM Indonesia</i> &rarr; pilih kampus &rarr; gunakan tombol <b>Unduh File PDF / Dokumen</b> agar terkirim dalam resolusi 300 DPI.\n\n"
        "3. <b>Surat Keterangan Aktif (SKMA)</b>:\n"
        "   Setelah mencetak KTM, tekan tombol <i>📜 Cetak SKMA</i> untuk bukti kedua verifikasi SheerID.\n\n"
        "4. <b>Anti-Fraud Sensor EXIF</b>:\n"
        "   Setiap file JPEG yang dihasilkan otomatis membawa metadata kamera Apple iPhone 14 Pro nyata."
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("« Kembali ke Menu", callback_data="main_menu")]])
    await update.message.reply_text(help_text, reply_markup=kb, parse_mode="HTML")


async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah Admin /stats untuk melihat metrik bot"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
    vip_users = cur.fetchone()[0]
    cur.execute("SELECT SUM(total_generated) FROM users")
    total_gen = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM topups WHERE status = 'SUCCESS'")
    paid_row = cur.fetchone()
    total_paid_orders, total_revenue = paid_row[0], paid_row[1]
    conn.close()

    text = (
        "👑 <b>PANEL STATISTIK ADMIN YOWES</b>\n\n"
        f"👥 Total Pengguna Terdaftar: <b>{total_users:,} orang</b>\n"
        f"⭐ Pengguna VIP Aktif: <b>{vip_users:,} orang</b>\n"
        f"📑 Total Dokumen Dihasilkan: <b>{total_gen:,} berkas</b>\n\n"
        f"💳 <b>Finansial (Clipku Pay):</b>\n"
        f"• Total Transaksi Sukses: <b>{total_paid_orders:,}</b>\n"
        f"• Total Omzet Masuk: <b>Rp {total_revenue:,}</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def admin_addquota_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah Admin /addquota [USER_ID] [JUMLAH]"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Format: <code>/addquota [USER_ID] [JUMLAH]</code>", parse_mode="HTML")
        return

    try:
        target_id = int(args[0])
        qty = int(args[1])
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE users SET quota_left = quota_left + ? WHERE user_id = ?", (qty, target_id))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"✅ Sukses menambahkan <b>+{qty} kuota</b> ke user ID <code>{target_id}</code>!", parse_mode="HTML")
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"🎁 <b>Admin telah menambahkan +{qty} Kuota Gratis ke akun Anda!</b>\nGunakan perintah /profil untuk cek sisa kuota.",
                parse_mode="HTML"
            )
        except Exception:
            pass
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal: {e}")


async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah Admin /broadcast [PESAN]"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    args = context.args
    if not args:
        await update.message.reply_text("Format: <code>/broadcast [PESAN_PENGUMUMAN]</code>", parse_mode="HTML")
        return

    msg_text = " ".join(args)
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = [r[0] for r in cur.fetchall()]
    conn.close()

    sent = 0
    await update.message.reply_text(f"📢 <i>Mengirim pesan ke {len(users)} pengguna...</i>", parse_mode="HTML")
    for u in users:
        try:
            await context.bot.send_message(chat_id=u, text=f"📢 <b>PENGUMUMAN RESMI:</b>\n\n{msg_text}", parse_mode="HTML")
            sent += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Broadcast selesai! Berhasil terkirim ke <b>{sent}/{len(users)}</b> pengguna.", parse_mode="HTML")



async def setup_bot_commands(application: Application):
    """Mendaftarkan menu tombol biru ☰ Menu di pojok kiri bawah Telegram"""
    commands = [
        BotCommand("start", "🏠 Menu Utama & Katalog Layanan"),
        BotCommand("ktm", "🎓 Cetak KTM Kampus Cepat"),
        BotCommand("pelajar", "🏫 Cetak Kartu Pelajar SMA/SMK"),
        BotCommand("guru", "👨‍🏫 Dokumen Guru (Canva Edu)"),
        BotCommand("rembg", "✂️ Hapus & Ganti BG Pasfoto AI"),
        BotCommand("referral", "🎁 Tautan Undangan (+2 Kuota)"),
        BotCommand("profil", "👤 Cek Sisa Kuota & Akun"),
        BotCommand("dl", "🎬 Download Video No WM (TT/IG/FB/YT)"),
        BotCommand("bantuan", "ℹ️ Panduan Verifikasi"),
    ]
    await application.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("Bot commands registered successfully via setMyCommands!")




def generate_all_for_country(country_code: str):
    """Menghasilkan seluruh dokumen resmi pendidik untuk negara terpilih dengan profil seragam"""
    gen_cls = get_country(country_code)
    gen = gen_cls()

    first = random.choice(gen.first_names) if gen.first_names else "John"
    last = random.choice(gen.last_names) if gen.last_names else "Smith"
    school = random.choice(gen.schools) if gen.schools else {"name": "National High School"}
    position = random.choice(gen.positions) if gen.positions else "Teacher"

    day = random.randint(1, 28)
    month = random.randint(1, 12)
    year = random.randint(1972, 1995)
    dob = f"{day:02d}/{month:02d}/{year}"

    docs = {}
    doc_types = gen.get_document_types()
    for dt in doc_types:
        try:
            b = gen.generate_document(dt, first, last, school, position, dob)
            docs[dt] = b
        except Exception as e:
            logger.error(f"Error {dt} for {country_code}: {e}")

    docs['_teacher'] = {
        'first_name': first,
        'last_name': last,
        'school_name': school.get('name', 'School'),
        'dob': dob,
        'position': position
    }
    return docs

def generate_single_for_country(country_code: str, target_doc: str):
    """Menghasilkan satu dokumen resmi pendidik untuk negara terpilih"""
    gen_cls = get_country(country_code)
    gen = gen_cls()

    first = random.choice(gen.first_names) if gen.first_names else "John"
    last = random.choice(gen.last_names) if gen.last_names else "Smith"
    school = random.choice(gen.schools) if gen.schools else {"name": "National High School"}
    position = random.choice(gen.positions) if gen.positions else "Teacher"

    day = random.randint(1, 28)
    month = random.randint(1, 12)
    year = random.randint(1972, 1995)
    dob = f"{day:02d}/{month:02d}/{year}"

    available = gen.get_document_types()
    if target_doc not in available and available:
        target_doc = available[0]

    b = gen.generate_document(target_doc, first, last, school, position, dob)
    return b, target_doc, first, last, school



# ==================== HANDLER GENERATOR KTM DARI REPLY KEYBOARD ====================

async def handle_generate_ktm_action(update: Update, context: ContextTypes.DEFAULT_TYPE, univ_code = None):
    """Menerbitkan KTM resmi langsung dari tombol Reply Keyboard"""
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")

    if not u_data["is_vip"] and u_data["quota_left"] <= 0:
        await update.message.reply_text(
            "⚠️ <b>Kuota Cetak Harian Anda Telah Habis!</b>\n\n"
            "Kuota gratis Anda sudah terpakai. Silakan isi ulang kuota atau langganan VIP di menu 👑 PROFIL & VIP.",
            reply_markup=get_main_reply_keyboard(),
            parse_mode="HTML"
        )
        return

    status_msg = await update.message.reply_text(
        "⏳ <b>Sedang merender Kartu Tanda Mahasiswa (KTM)...</b>\n"
        "• Menyematkan lambang resmi institusi\n"
        "• Memasang pasfoto formal & tanda tangan basah\n"
        "• Menyuntikkan metadata EXIF sensor kamera iPhone...",
        parse_mode="HTML"
    )

    try:
        first_names_m = ["Dimas", "Ahmad", "Fajar", "Bagus", "Rizky", "Aditya", "Bayu", "Arif", "Hendra"]
        first_names_f = ["Siti", "Nur", "Putri", "Dian", "Anisa", "Dewi", "Rini", "Ayu", "Fitri"]
        last_names = ["Prasetyo", "Santoso", "Saputra", "Hidayat", "Kusuma", "Wibowo", "Nugroho", "Setiawan"]

        is_female = random.choice([True, False])
        first = random.choice(first_names_f if is_female else first_names_m)
        last = random.choice(last_names)
        gender_param = "Female" if is_female else "Male"

        ktm_png_bytes = ktm_engine.generate(first, last, univ_code=univ_code, gender=gender_param)
        ktm_exif_bytes = inject_camera_exif(ktm_png_bytes)

        if not u_data["is_vip"]:
            decrement_quota(user.id)
            track_document_generated(user.id, "KTM", univ_code or "UT")

        session_key = f"{user.id}_{int(datetime.now().timestamp())}"
        SESSION_DOC_CACHE[session_key] = {
            "png_bytes": ktm_png_bytes,
            "exif_bytes": ktm_exif_bytes,
            "first": first,
            "last": last,
            "univ_code": univ_code or "UT",
            "type": "KTM",
        }
        context.user_data["last_session_key"] = session_key

        univ_display_names = {
            "UT": "Universitas Terbuka (UT)",
            "UI": "Universitas Indonesia (UI)",
            "UGM": "Universitas Gadjah Mada (UGM)",
            "ITB": "Institut Teknologi Bandung (ITB)",
            "UB": "Universitas Brawijaya (UB)",
            "HARVARD": "Harvard University (US)",
            "MIT": "Massachusetts Institute of Technology (US)",
            "STANFORD": "Stanford University (US)",
            "OXFORD": "University of Oxford (UK)",
        }
        u_target = univ_display_names.get(univ_code, univ_code or "Universitas Terbuka (UT)")

        caption = (
            f"✅ <b>Kartu Tanda Mahasiswa (KTM) Berhasil Dibuat!</b>\n\n"
            f"🏛️ <b>Universitas:</b> {u_target}\n"
            f"👤 <b>Nama:</b> {first} {last} ({gender_param})\n"
            f"🎓 <b>Jenjang:</b> Strata 1 (S1) Mahasiswa Aktif\n"
            f"📸 <b>Anti-Fraud:</b> Disertai Metadata Sensor Kamera Nyata\n"
            f"🖋️ <b>Legalitas:</b> Tanda Tangan Basah & Cap Biro Akademik\n\n"
            f"👇 <b>Pilih mockup fisik (Meja, Lanyard, POV) atau unduh berkas pada tombol di bawah:</b>"
        )

        bio = io.BytesIO(ktm_exif_bytes)
        bio.name = f"KTM_{univ_code or 'UT'}_{first}_{last}.jpg"
        bio.seek(0)

        await update.message.reply_photo(
            photo=bio,
            caption=caption,
            reply_markup=get_card_action_reply_keyboard(),
            parse_mode="HTML"
        )
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error generating KTM from reply button: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Terjadi kesalahan: {html.escape(str(e))}", parse_mode="HTML")


async def handle_buy_pkg_action(update: Update, context: ContextTypes.DEFAULT_TYPE, pkg_type: str):
    """Membuat tagihan pembayaran QRIS Clipku Pay langsung dari Reply Keyboard"""
    user = update.effective_user
    status_msg = await update.message.reply_text("⏳ <i>Menghubungi gateway Clipku Pay untuk membuat tagihan QRIS...</i>", parse_mode="HTML")
    
    res = create_clipku_payment(user.id, pkg_type, user.first_name or "User")
    if res.get("success"):
        order_id = res["order_id"]
        amount = res["amount"]
        pay_url = res["payment_url"]
        pkg_name = "+10 Kuota Cetak (Permanen)" if pkg_type == "quota_10" else "👑 VIP Unlimited 30 Hari"

        text = (
            "🧾 <b>TAGIHAN PEMBAYARAN QRIS RESMI</b>\n\n"
            f"• Paket: <b>{pkg_name}</b>\n"
            f"• Order ID: <code>{order_id}</code>\n"
            f"• Total Bayar: <b>Rp {amount:,}</b>\n"
            "• Metode: QRIS Real-time (BCA, DANA, GoPay, OVO, ShopeePay, Mandiri)\n\n"
            "Ketuk tombol <b>📲 Bayar Sekarang (QRIS)</b> di bawah untuk melakukan pembayaran, "
            "lalu tekan <b>🔄 Cek Status Pembayaran</b> setelah transfer selesai."
        )
        pay_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Bayar Sekarang (Buka QRIS)", url=pay_url)],
            [InlineKeyboardButton("🔄 Cek Status Pembayaran", callback_data=f"chk_pay:{order_id}")],
            [InlineKeyboardButton("« Tutup", callback_data="main_menu")],
        ])
        await update.message.reply_text(text, reply_markup=pay_kb, parse_mode="HTML")
        await status_msg.delete()
    else:
        err_msg = res.get("error", "Terjadi kesalahan sistem")
        await status_msg.edit_text(f"❌ Gagal membuat pembayaran: {html.escape(err_msg)}", parse_mode="HTML")

async def reply_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Router Hub 2x2: Bersih, Cepat, dan Sangat Lega di Layar HP"""
    text = update.message.text.strip()
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")

    
    # Smart Auto-Detect Kurs Mata Uang (contoh: '$150', '50 sgd to idr', '2000 myr')
    import currency_service
    curr_parsed = currency_service.parse_currency_query(text)
    if curr_parsed:
        amt, f_curr, t_curr = curr_parsed
        res = currency_service.convert_currency(amt, f_curr, t_curr)
        if res:
            res_val = res['result']
            single_val = res['rate_single']
            if t_curr == "IDR":
                res_formatted = f"Rp {res_val:,.2f}"
                single_formatted = f"Rp {single_val:,.2f}"
            else:
                res_formatted = f"{res_val:,.2f} {t_curr}"
                single_formatted = f"{single_val:,.4f} {t_curr}"

            f_name = currency_service.CURRENCY_FLAGS.get(f_curr, f_curr)
            t_name = currency_service.CURRENCY_FLAGS.get(t_curr, t_curr)
            msg = (
                f"💱 <b>HASIL KONVERSI KURS VALAS REAL-TIME</b>\n\n"
                f"• Nominal: <b>{amt:,.2f} {f_curr}</b> ({f_name})\n"
                f"• Hasil Tukar: <b>{res_formatted}</b> ({t_name})\n\n"
                f"📊 <b>Nilai Tukar Saat Ini:</b>\n"
                f"1 {f_curr} = <b>{single_formatted}</b>\n"
                f"<i>Data pasar valuta asing global live per jam.</i>"
            )
            await update.message.reply_text(msg, parse_mode="HTML")
            return

    # Smart Auto-Detect Video Links (TikTok, IG, FB, YT, X) langsung dari chat
    if is_supported_url(text):
        url = extract_url_from_text(text)
        await process_media_link_preview(update, context, url)
        return

    # Navigasi Utama
    if text in ["« KEMBALI KE MENU UTAMA", "🏠 MENU UTAMA", "« MENU UTAMA"]:
        await start_command(update, context)
        return

    # 2. Handler Klik Kampus Indonesia & Internasional (Reply Keyboard)
    ktm_map = {
        "🎓 Universitas Terbuka (UT)": "UT",
        "🎓 Univ. Indonesia (UI)": "UI",
        "🎓 Univ. Gadjah Mada (UGM)": "UGM",
        "🎓 ITB Bandung": "ITB",
        "🎓 Univ. Brawijaya (UB)": "UB",
        "🎲 Kampus Acak": None,
        "🏛️ Harvard Univ (US)": "HARVARD",
        "🏛️ MIT Tech (US)": "MIT",
        "🏛️ Stanford Univ (US)": "STANFORD",
        "🏛️ Univ of Oxford (UK)": "OXFORD",
    }
    if text in ktm_map:
        await handle_generate_ktm_action(update, context, ktm_map[text])
        return

    # ==================== HUB 1: 🎓 BUAT DOKUMEN ====================
    elif text == "🎓 BUAT DOKUMEN":
        msg = (
            "🎓 <b>PUSAT PEMBUATAN DOKUMEN & KARTU IDENTITAS</b>\n\n"
            "Silakan pilih jenis dokumen yang ingin Anda buat pada menu di bawah:\n"
            "• <b>KTM Kampus Indonesia</b>: Kartu Mahasiswa UT, UI, UGM, ITB, UB\n"
            "• <b>ID Kampus Internasional</b>: Harvard, MIT, Stanford, Oxford\n"
            "• <b>Dokumen Guru (Canva)</b>: Berkas sertifikasi pendidik 13 negara\n"
            "• <b>Kartu Pelajar</b>: SMA / SMK Negeri Tut Wuri Handayani\n"
            "• <b>Buat Custom</b>: Menggunakan nama & pasfoto Anda sendiri"
        )
        await update.message.reply_text(msg, reply_markup=get_dokumen_hub_reply_keyboard(), parse_mode="HTML")
        return

    elif text == "🎓 KTM Kampus Indonesia":
        msg = "🎓 <b>Pilih Universitas Indonesia:</b>\nKetuk kampus pada tombol di bawah untuk langsung menerbitkan kartu:"
        await update.message.reply_text(msg, reply_markup=get_ktm_reply_keyboard(), parse_mode="HTML")
        return

    elif text == "🏛️ ID Kampus Internasional":
        msg = "🏛️ <b>Pilih Kampus Internasional (Ivy League & Oxbridge):</b>"
        await update.message.reply_text(msg, reply_markup=get_ktm_global_reply_keyboard(), parse_mode="HTML")
        return

    elif text in ["👨‍🏫 Dokumen Guru (Canva)", "👨‍🏫 GURU (CANVA EDU)"]:
        msg = "🌍 <b>Pilih Negara Lembaga Pendidik (13 Negara):</b>"
        await update.message.reply_text(msg, reply_markup=get_guru_reply_keyboard(), parse_mode="HTML")
        return

    elif text == "🏫 Kartu Pelajar SMA/SMK":
        msg = "🏫 <b>Pilih Sekolah Menengah (SMA / SMK Negeri):</b>"
        await update.message.reply_text(msg, reply_markup=get_pelajar_reply_keyboard(), parse_mode="HTML")
        return

    elif text == "✨ Buat Custom (Nama/Foto)":
        await update.message.reply_text(
            "✍️ <b>Mode Pembuatan Kustom:</b>\nKetikkan nama lengkap Anda sekarang (contoh: <code>ADITYA PRATAMA</code>):",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True),
            parse_mode="HTML"
        )
        context.user_data["awaiting_custom_name"] = True
        return

    # Handler Papan Kurs Valuta Asing Real-Time
    elif text in ["💱 KURS VALAS LIVE", "💱 Kurs Valas Live", "💱 KURS VALAS", "/kurs", "/forex"]:
        import currency_service
        rates_board = currency_service.get_popular_rates_text()
        await update.message.reply_text(rates_board, parse_mode="HTML")
        return

    # Handler Transkrip Nilai (KHS)
    elif text in ["📊 Transkrip Nilai (KHS)", "📊 TRANSKRIP NILAI (KHS)", "📊 Transkrip Nilai", "/khs"]:
        await khs_menu_handler(update, context)
        return

    elif text in ["📊 KHS Universitas Terbuka (UT)", "KHS UT"]:
        await khs_generate_handler(update, context, "UT")
        return

    elif text in ["📊 KHS Univ. Indonesia (UI)", "KHS UI"]:
        await khs_generate_handler(update, context, "UI")
        return

    elif text in ["📊 KHS Univ. Gadjah Mada (UGM)", "KHS UGM"]:
        await khs_generate_handler(update, context, "UGM")
        return

    elif text in ["📊 KHS ITB Bandung", "KHS ITB"]:
        await khs_generate_handler(update, context, "ITB")
        return

    elif text in ["📊 KHS Univ. Brawijaya (UB)", "KHS UB"]:
        await khs_generate_handler(update, context, "UB")
        return

    elif text in ["« KEMBALI KE KOTAK ALAT", "« KOTAK ALAT"]:
        await update.message.reply_text("🛠️ <b>KOTAK ALAT FILE, KONVERSI & FOTO</b>", reply_markup=get_tools_hub_reply_keyboard(), parse_mode="HTML")
        return

    # ==================== HUB 2: 🛠️ KOTAK ALAT FILE ====================
    elif text in ["🛠️ KOTAK ALAT FILE", "🛠️ KOTAK ALAT & KONVERSI", "🛠️ ALAT DOKUMEN & FOTO"]:
        msg = (
            "🛠️ <b>KOTAK ALAT FILE, KONVERSI & FOTO</b>\n\n"
            "Pilih alat produktivitas yang ingin Anda gunakan langsung pada tombol di bawah:"
        )
        await update.message.reply_text(msg, reply_markup=get_tools_hub_reply_keyboard(), parse_mode="HTML")
        return

    # ==================== HUB 3: 👑 PROFIL & VIP ====================
    elif text in ["👑 PROFIL & VIP", "💰 SALDO & VIP", "💰 SALDO & KUOTA"]:
        vip_status = "👑 <b>VIP UNLIMITED</b> (Aktif)" if u_data["is_vip"] else "Standar (Gratis)"
        exp_text = f"\n• Masa Aktif VIP: {u_data['vip_until'][:10]}" if (u_data["is_vip"] and u_data["vip_until"]) else ""
        stats = get_referral_stats(user.id)

        msg = (
            f"👤 <b>Informasi Akun & Saldo Kuota:</b>\n"
            f"• ID Pengguna: <code>{user.id}</code>\n"
            f"• Status Layanan: {vip_status}{exp_text}\n"
            f"• Sisa Kuota Cetak: <b>{'Unlimited' if u_data['is_vip'] else str(u_data['quota_left']) + 'x'}</b>\n"
            f"• Total Dokumen Diterbitkan: <b>{u_data['total_generated']} berkas</b>\n"
            f"• Teman Diundang: <b>{stats['count']} orang</b>\n\n"
            "💳 <b>Pusat Top Up (QRIS Otomatis Clipku Pay):</b>\n"
            "• <b>+10 Kuota Cetak</b>: Rp 5.000 (Permanen Tanpa Expired)\n"
            "• <b>VIP Unlimited 30 Hari</b>: Rp 15.000 (Bebas Cetak Ribuan Berkas)\n\n"
            "Pilih paket pada tombol di bawah untuk mendapatkan link bayar QRIS:"
        )
        await update.message.reply_text(msg, reply_markup=get_profile_hub_reply_keyboard(), parse_mode="HTML")
        return

    # Handler Tombol Pembelian Paket Kuota / VIP dari Reply Keyboard
    elif text in ["⚡ Beli +10 Kuota (Rp 5.000)", "⚡ Beli +10 Kuota", "Beli Kuota"]:
        await handle_buy_pkg_action(update, context, "quota_10")
        return

    elif text in ["👑 Beli VIP 30 Hari (Rp 15.000)", "👑 Beli VIP 30 Hari", "Beli VIP"]:
        await handle_buy_pkg_action(update, context, "vip_30d")
        return

    elif text == "🎁 Ambil Tautan Referral":
        await referral_command(update, context)
        return

    # ==================== HUB 4: ℹ️ PANDUAN & BANTUAN ====================
    elif text in ["ℹ️ PANDUAN & BANTUAN", "ℹ️ PANDUAN", "ℹ️ BANTUAN"]:
        await bantuan_command(update, context)
        return

    # 5. Handler Klik Negara Pendidik (13 Negara)
    country_btn_map = {
        "🇮🇩 Indonesia": "indonesia",
        "🇳🇱 Belanda": "netherlands",
        "🇺🇸 Amerika": "us",
        "🇬🇧 Inggris": "uk",
        "🇦🇺 Australia": "australia",
        "🇨🇦 Kanada": "canada",
        "🇫🇷 Prancis": "france",
        "🇪🇸 Spanyol": "spain",
        "🇦🇷 Argentina": "argentina",
        "🇲🇽 Meksiko": "mexico",
        "🇵🇭 Filipina": "philippines",
        "🇹🇭 Thailand": "thailand",
        "🇸🇰 Slowakia": "slovakia",
    }

    if text in country_btn_map:
        c_code = country_btn_map[text]
        context.user_data["active_country"] = c_code
        c_obj = get_country(c_code)
        c_name = COUNTRY_FLAGS.get(c_code, c_code.upper())

        msg = (
            f"🌍 <b>Negara Terpilih: {c_name}</b>\n\n"
            "Silakan pilih jenis dokumen yang ingin dicetak pada tombol di bawah layar Anda, "
            "atau pilih <b>📦 CETAK SEMUA DOKUMEN</b> untuk mencetak seluruh berkas sekaligus:"
        )
        await update.message.reply_text(msg, reply_markup=get_guru_docs_reply_keyboard(c_code), parse_mode="HTML")
        return

    elif text == "« PILIH NEGARA LAIN":
        await guru_command(update, context)
        return

    elif text == "📦 CETAK SEMUA DOKUMEN (PAKET LENGKAP)":
        c_code = context.user_data.get("active_country", "indonesia")
        if not u_data["is_vip"] and u_data["quota_left"] <= 0:
            await update.message.reply_text("⚠️ Kuota habis! Silakan isi ulang di menu 💰 SALDO & KUOTA.", reply_markup=get_main_reply_keyboard())
            return

        c_name = COUNTRY_FLAGS.get(c_code, c_code.upper())
        await update.message.reply_text(f"⏳ <i>Menerbitkan seluruh paket dokumen guru untuk {c_name}...</i>", parse_mode="HTML")

        try:
            docs = generate_all_for_country(c_code)
            consume_quota(user.id)
            teacher = docs.get("_teacher", {})
            t_name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip() or "Guru"

            await update.message.reply_text(
                f"✅ <b>Seluruh Dokumen {c_name} Berhasil Diterbitkan!</b>\n\n"
                f"• Nama Pendidik: <b>{t_name}</b>\n"
                f"• Sekolah: <b>{teacher.get('school_name', '-')}</b>\n"
                f"• Status Verifikasi: Siap Unggah Canva Edu / Apple Teacher\n"
                f"Sedang mengirimkan berkas...",
                parse_mode="HTML"
            )

            for d_name, d_bytes in docs.items():
                if d_name.startswith("_"):
                    continue
                d_label = DOC_LABELS.get(d_name, d_name.replace("_", " ").title())
                bio = io.BytesIO(d_bytes)
                bio.name = f"{c_code.upper()}_{d_name}_{t_name.replace(' ', '_')}.png"
                bio.seek(0)
                await update.message.reply_document(document=bio, caption=f"📑 {d_label}")

            await update.message.reply_text("Pilih dokumen lain atau kembali ke menu utama:", reply_markup=get_guru_reply_keyboard())
        except Exception as e:
            logger.error(f"Error gen all docs: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Gagal: {e}", reply_markup=get_guru_reply_keyboard())
        return

    elif text in ["🪪 Kartu Identitas Guru", "📜 SK Pengangkatan", "💵 Slip Gaji (Payslip)", "📝 Surat Mengajar"]:
        c_code = context.user_data.get("active_country", "indonesia")
        if not u_data["is_vip"] and u_data["quota_left"] <= 0:
            await update.message.reply_text("⚠️ Kuota habis! Silakan isi ulang di menu 💰 SALDO & KUOTA.", reply_markup=get_main_reply_keyboard())
            return

        c_name = COUNTRY_FLAGS.get(c_code, c_code.upper())
        doc_type_map = {
            "🪪 Kartu Identitas Guru": "teacher_id" if c_code != "indonesia" else "nuptk_card",
            "📜 SK Pengangkatan": "appointment_letter" if c_code == "indonesia" else ("employment_letter" if c_code == "us" else "employment_contract"),
            "💵 Slip Gaji (Payslip)": "payslip",
            "📝 Surat Mengajar": "teaching_experience_letter" if c_code == "indonesia" else ("teaching_license" if c_code == "us" else "teacher_registration"),
        }
        target_doc = doc_type_map.get(text, "teacher_id")

        await update.message.reply_text(f"⏳ <i>Menerbitkan {text} ({c_name})...</i>", parse_mode="HTML")
        try:
            d_bytes, final_type, first, last, school = generate_single_for_country(c_code, target_doc)
            consume_quota(user.id)
            d_label = DOC_LABELS.get(final_type, text)

            bio = io.BytesIO(d_bytes)
            bio.name = f"{c_code.upper()}_{final_type}_{first}_{last}.png"
            bio.seek(0)
            await update.message.reply_document(
                document=bio,
                caption=f"✅ <b>{d_label} ({c_name}) Resmi</b>\n• Pendidik: <b>{first} {last}</b>\n• Sekolah: <b>{school.get('name', 'School')}</b>\n✓ Format Resolusi Penuh HD\n✓ Tanda Tangan & Cap Institusi Otentik",
                reply_markup=get_guru_docs_reply_keyboard(c_code),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error generating single doc: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Gagal: {e}", reply_markup=get_guru_docs_reply_keyboard(c_code))
        return

    # 10. Aksi Pembuatan Kartu Pelajar dari Tombol Bawah
    pelajar_map = {
        "🏫 SMAN 1 Jakarta": "SMAN1_JKT",
        "🏫 SMAN 3 Bandung": "SMAN3_BDG",
        "🏫 SMKN 1 Surabaya": "SMKN1_SBY",
        "🏫 SMAN 1 Yogyakarta": "SMAN1_YOG",
    }
    if text in pelajar_map:
        sch_key = pelajar_map[text]
        if not u_data["is_vip"] and u_data["quota_left"] <= 0:
            await update.message.reply_text("⚠️ Kuota habis! Pilih 💰 SALDO & KUOTA.", reply_markup=get_main_reply_keyboard())
            return

        gender = random.choice(["Male", "Female"])
        first, last = get_indonesian_name(gender)
        await update.message.reply_text(f"⏳ <i>Mencetak Kartu Pelajar untuk {first} {last}...</i>", parse_mode="HTML")

        try:
            png_bytes = pelajar_engine.generate(first_name=first, last_name=last, school_code=sch_key, gender=gender)
            consume_quota(user.id)

            session_key = f"{user.id}_{int(datetime.now().timestamp())}"
            SESSION_DOC_CACHE[session_key] = {
                "type": "pelajar",
                "png_bytes": png_bytes,
                "first": first,
                "last": last,
                "univ_code": "SCH",
            }
            context.user_data["last_session_key"] = session_key

            jpeg_bytes = inject_camera_exif(png_bytes)
            bio = io.BytesIO(jpeg_bytes)
            bio.name = f"KARTU_PELAJAR_{sch_key}_{first}.jpg"
            bio.seek(0)

            caption = (
                f"✅ <b>Kartu Pelajar Berhasil Diterbitkan!</b>\n\n"
                f"• Siswa: <b>{first} {last}</b>\n"
                f"• Sekolah: <b>{sch_key.replace('_', ' ')}</b>\n"
                f"• Logo: Tut Wuri Handayani Resmi\n\n"
                f"👇 <b>Pilih efek foto fisik atau unduh dokumen pada tombol di bawah:</b>"
            )
            await update.message.reply_photo(
                photo=bio,
                caption=caption,
                reply_markup=get_card_action_reply_keyboard(),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error generating Pelajar: {e}")
            await update.message.reply_text(f"❌ Gagal: {e}", reply_markup=get_main_reply_keyboard())
        return

    # 11. Aksi Efek Foto Mockup & Unduh Berkas dari Tombol Bawah
    last_key = context.user_data.get("last_session_key")
    cache = SESSION_DOC_CACHE.get(last_key) if last_key else None

    if text == "📸 FOTO DI MEJA":
        if not cache:
            await update.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan buat kartu baru.", reply_markup=get_main_reply_keyboard())
            return
        await update.message.reply_text("⏳ <i>Merender foto fisik kartu di atas meja kerja kayu 3D...</i>", parse_mode="HTML")
        desk_bytes = render_card_on_desk(cache["png_bytes"])
        desk_exif = inject_camera_exif(desk_bytes)
        bio = io.BytesIO(desk_exif)
        bio.name = f"FOTO_MEJA_{cache['first']}_{cache['last']}.jpg"
        bio.seek(0)
        await update.message.reply_photo(
            photo=bio,
            caption="📸 <b>Foto Fisik di Atas Meja (Desk Mockup)</b>\n✓ Perspektif kemiringan 3D alami\n✓ EXIF kamera iPhone 14 Pro",
            reply_markup=get_card_action_reply_keyboard(),
            parse_mode="HTML"
        )
        return

    elif text == "🪪 MIKA + LANYARD":
        if not cache:
            await update.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan buat kartu baru.", reply_markup=get_main_reply_keyboard())
            return
        await update.message.reply_text("⏳ <i>Merender kartu di dalam mika card holder + tali lanyard resmi...</i>", parse_mode="HTML")
        lanyard_bytes = render_lanyard_card_holder(cache["png_bytes"], univ_code=cache.get("univ_code", "UT"))
        lanyard_exif = inject_camera_exif(lanyard_bytes)
        bio = io.BytesIO(lanyard_exif)
        bio.name = f"LANYARD_{cache['first']}_{cache['last']}.jpg"
        bio.seek(0)
        await update.message.reply_photo(
            photo=bio,
            caption="🪪 <b>Mockup Mika Card Holder + Tali Lanyard Resmi</b>\n✓ Wadah mika berlubang oval & klip logam perak\n✓ Tali tenun kampus resmi",
            reply_markup=get_card_action_reply_keyboard(),
            parse_mode="HTML"
        )
        return

    elif text == "🖐️ PEGANG TANGAN (POV)":
        if not cache:
            await update.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan buat kartu baru.", reply_markup=get_main_reply_keyboard())
            return
        await update.message.reply_text("⏳ <i>Merender foto kartu sedang dipegang tangan orang (POV)...</i>", parse_mode="HTML")
        hand_bytes = render_handheld_pov(cache["png_bytes"])
        hand_exif = inject_camera_exif(hand_bytes)
        bio = io.BytesIO(hand_exif)
        bio.name = f"HAND_POV_{cache['first']}_{cache['last']}.jpg"
        bio.seek(0)
        await update.message.reply_photo(
            photo=bio,
            caption="🖐️ <b>Foto Fisik Sedang Dipegang Tangan (POV)</b>\n✓ Tampak jempol memegang tepian fisik kartu\n✓ Sangat ampuh lolos verifikasi manual manusia",
            reply_markup=get_card_action_reply_keyboard(),
            parse_mode="HTML"
        )
        return

    elif text == "📜 CETAK SKMA":
        if not cache:
            await update.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa. Silakan buat kartu baru.", reply_markup=get_main_reply_keyboard())
            return
        await update.message.reply_text("⏳ <i>Menerbitkan Surat Keterangan Mahasiswa Aktif (SKMA) resmi...</i>", parse_mode="HTML")
        skma_png = skma_engine.generate(full_name=f"{cache['first']} {cache['last']}", univ_code=cache.get("univ_code", "UT"))
        bio = io.BytesIO(skma_png)
        bio.name = f"SKMA_{cache['first']}_{cache['last']}.png"
        bio.seek(0)
        await update.message.reply_document(
            document=bio,
            caption="📜 <b>Surat Keterangan Mahasiswa Aktif (SKMA) Resmi (A4)</b>\n✓ Kop resmi universitas, nomor surat legal, dan tanda tangan basah dekanat",
            reply_markup=get_card_action_reply_keyboard(),
            parse_mode="HTML"
        )
        return

    elif text == "📥 UNDUH PDF (300 DPI)":
        if not cache:
            await update.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa.", reply_markup=get_main_reply_keyboard())
            return
        pdf_bytes = convert_to_pdf(cache["png_bytes"])
        bio = io.BytesIO(pdf_bytes)
        bio.name = f"{cache['type'].upper()}_{cache['first']}_{cache['last']}.pdf"
        bio.seek(0)
        await update.message.reply_document(document=bio, caption="📥 <b>Dokumen Format PDF Resmi (Vector Print Ready)</b>", reply_markup=get_card_action_reply_keyboard(), parse_mode="HTML")
        return

    elif text == "📁 UNDUH HD PNG":
        if not cache:
            await update.message.reply_text("⚠️ Berkas sesi telah kedaluwarsa.", reply_markup=get_main_reply_keyboard())
            return
        bio = io.BytesIO(cache["png_bytes"])
        bio.name = f"{cache['type'].upper()}_{cache['first']}_{cache['last']}.png"
        bio.seek(0)
        await update.message.reply_document(document=bio, caption="📁 <b>Berkas Asli Resolusi Penuh PNG (Tanpa Kompresi)</b>", reply_markup=get_card_action_reply_keyboard(), parse_mode="HTML")
        return

    # Tangani input nama custom jika sedang menunggu
    if context.user_data.get("awaiting_custom_name"):
        context.user_data["awaiting_custom_name"] = False
        parts = text.split(maxsplit=1)
        first = parts[0].upper()
        last = parts[1].upper() if len(parts) > 1 else "MAHASISWA"
        context.user_data["custom_first"] = first
        context.user_data["custom_last"] = last
        await update.message.reply_text(
            f"✅ Nama tercatat: <b>{first} {last}</b>\n\nSekarang, silakan pilih universitas pada tombol di bawah:",
            reply_markup=get_ktm_reply_keyboard(),
            parse_mode="HTML"
        )
        return



async def rembg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memulai proses Hapus Background & Ganti Warna Studio"""
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")

    # Cek kuota
    if not u_data["is_vip"] and u_data["quota_left"] <= 0:
        await update.message.reply_text(
            "⚠️ <b>Kuota Anda Habis!</b>\n\n"
            "Fitur Hapus Background AI HD memerlukan 1 kuota per foto (atau aktifkan VIP Unlimited 30 Hari).\n"
            "Silakan pilih menu <b>💰 SALDO & KUOTA</b> untuk top up.",
            reply_markup=get_main_reply_keyboard(),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    status_str = "👑 <b>VIP Unlimited</b> (Bebas Gunakan)" if u_data["is_vip"] else f"⚡ Sisa Kuota: <b>{u_data['quota_left']}x</b> (1 kuota / proses)"
    msg = (
        "✂️ <b>AI BACKGROUND REMOVER & STUDIO FORMALIZER (ULTRA HD)</b>\n\n"
        "Fitur cerdas berbasis AI Deep Learning U2-Net untuk:\n"
        "✓ <i>Menghapus background foto apapun secara instan</i>\n"
        "✓ <i>Segmentasi rambut & lekuk pakaian sangat presisi</i>\n"
        "✓ <i>Ganti latar belakang pasfoto resmi (Merah KTP, Biru Ijazah, Putih Visa, Transparan PNG)</i>\n"
        "✓ <i>Kualitas Output: HD Asli Tanpa Kompresi</i>\n\n"
        f"Status: {status_str}\n\n"
        "📸 <b>Silakan kirimkan FOTO yang ingin diproses sekarang:</b>\n"
        "<i>(Kirim sebagai foto biasa atau kirim sebagai file/dokumen agar kualitas HD maksimal)</i>"
    )
    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True),
        parse_mode="HTML"
    )
    return REMBG_WAIT_PHOTO


async def rembg_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menerima foto yang dikirim pengguna"""
    user = update.effective_user

    # Cek apakah user mengirim tombol batal
    if update.message.text and update.message.text.strip() == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    raw_bytes = None
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await photo_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("image/"):
        doc_file = await update.message.document.get_file()
        buf = io.BytesIO()
        await doc_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    else:
        await update.message.reply_text("⚠️ Berkas yang dikirim bukan gambar/foto yang valid. Silakan kirim foto atau ketik /batal.")
        return REMBG_WAIT_PHOTO

    context.user_data["rembg_raw_image"] = raw_bytes

    msg = (
        "✅ <b>Foto Berhasil Diterima!</b>\n\n"
        "Silakan pilih <b>Warna Latar Belakang</b> yang Anda inginkan pada tombol di bawah:\n"
        "• 🔴 <b>Merah</b>: Standar KTP, SKCK, Pasfoto CPNS/Kedinasan\n"
        "• 🔵 <b>Biru</b>: Standar Buku Nikah, Ijazah, Kartu Mahasiswa\n"
        "• ⚪ <b>Putih</b>: Paspor Internasional, Visa, Dokumen Kedutaan\n"
        "• 🔘 <b>Abu-Abu</b>: Profil Perusahaan, LinkedIn Studio\n"
        "• 🏁 <b>Transparan PNG</b>: Objek tanpa latar belakang (stiker/desain)"
    )
    await update.message.reply_text(msg, reply_markup=get_rembg_colors_reply_keyboard(), parse_mode="HTML")
    return REMBG_WAIT_COLOR


async def rembg_color_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memproses foto dengan AI dan mengirimkan hasilnya dalam HD"""
    text = update.message.text.strip()
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")

    if text == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    color_map = {
        "🔴 MERAH (KTP/SKCK)": "merah",
        "🔵 BIRU (IJAZAH/UT)": "biru",
        "⚪ PUTIH (PASPOR/VISA)": "putih",
        "🔘 ABU-ABU STUDIO": "abu",
        "⚫ HITAM ELEGAN": "hitam",
        "🏁 TRANSPARAN PNG": "transparan",
    }
    selected_color = color_map.get(text, "transparan")
    raw_bytes = context.user_data.get("rembg_raw_image")

    if not raw_bytes:
        await update.message.reply_text("⚠️ Sesi foto kedaluwarsa. Silakan mulai ulang.", reply_markup=get_main_reply_keyboard())
        return ConversationHandler.END

    await update.message.reply_text("⏳ <i>Sedang memproses foto dengan AI Deep Learning U2-Net (Deteksi helai rambut & render latar belakang HD)...</i>", parse_mode="HTML")

    try:
        processed_bytes, out_w, out_h = process_hd_rembg(raw_bytes, color_key=selected_color)
        consume_quota(user.id)

        color_title = selected_color.upper() if selected_color != "transparan" else "TRANSPARAN (NO BG)"
        caption = (
            f"✨ <b>Hasil AI Background Remover HD Selesai!</b>\n\n"
            f"• Mode: <b>{color_title}</b>\n"
            f"• Resolusi Asli: <b>{out_w} x {out_h} px (Ultra HD)</b>\n"
            f"• Algoritma: U2-Net Precise Silhouette Isolation\n\n"
            f"<i>Berkas dikirim sebagai dokumen tanpa kompresi agar ketajaman 100% terjaga.</i>"
        )

        ext = "png"
        bio = io.BytesIO(processed_bytes)
        bio.name = f"PASFOTO_HD_{selected_color.upper()}_{user.id}.{ext}"
        bio.seek(0)

        # Kirim preview foto
        if selected_color != "transparan":
            bio_preview = io.BytesIO(processed_bytes)
            bio_preview.seek(0)
            await update.message.reply_photo(photo=bio_preview, caption=f"📸 Preview: <b>{color_title}</b>", parse_mode="HTML")

        # Kirim dokumen asli HD tanpa kompresi Telegram
        await update.message.reply_document(
            document=bio,
            caption=caption,
            reply_markup=get_main_reply_keyboard(),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Rembg error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Terjadi kesalahan saat memproses: {e}", reply_markup=get_main_reply_keyboard())
        return ConversationHandler.END



# ==================== EXTRA PRODUCTIVITY TOOLS ====================

async def tools_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan sub-menu Alat Dokumen & Foto Produktivitas"""
    msg = (
        "🛠️ <b>KOTAK ALAT PRODUKTIVITAS & DOKUMEN</b>\n\n"
        "Silakan pilih alat yang ingin Anda gunakan pada tombol di bawah:\n\n"
        "• <b>📄 Konversi Word ke PDF</b>: Mengubah file .docx/.doc menjadi PDF rapi berstandar cetak.\n"
        "• <b>🗜️ Kompres Foto</b>: Memperkecil ukuran berkas foto pas 100KB/200KB untuk upload CPNS, BUMN, & Kedinasan.\n"
        "• <b>🖋️ Tanda Tangan Transparan</b>: Memisahkan goresan tanda tangan dari foto kertas menjadi PNG transparan tajam.\n"
        "• <b>📊 Transkrip Nilai (KHS)</b>: Menerbitkan lembar nilai semester aktif berkop universitas resmi."
    )
    await update.message.reply_text(msg, reply_markup=get_tools_reply_keyboard(), parse_mode="HTML")


# 1. Konversi Word ke PDF
async def doc2pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📄 <b>KONVERSI DOKUMEN WORD KE PDF RESMI</b>\n\n"
        "Kirimkan berkas dokumen Anda sekarang (format <code>.docx</code>, <code>.doc</code>, <code>.rtf</code>, atau <code>.txt</code>).\n"
        "Sistem akan langsung mengonversinya menjadi dokumen PDF beresolusi tinggi tanpa merusak tata letak font."
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return DOC2PDF_WAIT_FILE

async def doc2pdf_file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    if not update.message.document:
        await update.message.reply_text("⚠️ Mohon kirimkan berkas sebagai <b>File Dokumen</b> (.docx / .doc).")
        return DOC2PDF_WAIT_FILE

    doc = update.message.document
    filename = doc.file_name or "document.docx"
    await update.message.reply_text(f"⏳ <i>Mengonversi {html.escape(filename)} ke format PDF...</i>", parse_mode="HTML")

    try:
        f = await doc.get_file()
        buf = io.BytesIO()
        await f.download_to_memory(buf)
        raw_doc = buf.getvalue()

        pdf_bytes = convert_doc_to_pdf(raw_doc, filename=filename)
        out_name = os.path.splitext(filename)[0] + ".pdf"

        bio = io.BytesIO(pdf_bytes)
        bio.name = out_name
        bio.seek(0)

        caption = f"✅ <b>Konversi Berhasil!</b>\n• Nama: <code>{out_name}</code>\n• Ukuran: {len(pdf_bytes)/1024:.1f} KB"
        await update.message.reply_document(document=bio, caption=caption, reply_markup=get_tools_reply_keyboard(), parse_mode="HTML")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Doc2pdf error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Gagal mengonversi dokumen: {e}", reply_markup=get_tools_reply_keyboard())
        return ConversationHandler.END


# 2. Kompres Foto Khusus CPNS/BUMN
async def compress_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🗜️ <b>KOMPRES FOTO KHUSUS CPNS, BUMN, & KEDINASAN</b>\n\n"
        "Memperkecil ukuran berkas foto agar lolos batas maksimal upload tanpa membuat foto buram atau pecah.\n\n"
        "📸 <b>Silakan kirimkan FOTO yang ingin dikompres sekarang:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return COMPRESS_WAIT_PHOTO

async def compress_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    raw_bytes = None
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await photo_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("image/"):
        doc_file = await update.message.document.get_file()
        buf = io.BytesIO()
        await doc_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    else:
        await update.message.reply_text("⚠️ Mohon kirimkan foto atau berkas gambar yang valid.")
        return COMPRESS_WAIT_PHOTO

    context.user_data["comp_raw_image"] = raw_bytes
    orig_kb = len(raw_bytes) / 1024

    msg = (
        f"✅ <b>Foto Diterima!</b> (Ukuran Asli: <b>{orig_kb:.1f} KB</b>)\n\n"
        "Pilih target batas ukuran yang Anda butuhkan pada tombol di bawah:\n"
        "• <b>🎯 Target 100 KB</b>: Untuk pasfoto kartu ujian & portal instansi ketat\n"
        "• <b>🎯 Target 200 KB</b>: Standar mutlak upload SSCASN CPNS / BUMN\n"
        "• <b>🎯 Target 300 KB / 500 KB</b>: Standar upload KTP & berkas ijazah\n"
        "• <b>⚡ Kompres Maksimal</b>: Menjaga kejernihan foto dengan ukuran hemat"
    )
    await update.message.reply_text(msg, reply_markup=get_compress_sizes_reply_keyboard(), parse_mode="HTML")
    return COMPRESS_WAIT_SIZE

async def compress_size_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    raw_bytes = context.user_data.get("comp_raw_image")
    if not raw_bytes:
        await update.message.reply_text("⚠️ Sesi foto kedaluwarsa. Silakan mulai ulang.", reply_markup=get_tools_reply_keyboard())
        return ConversationHandler.END

    target_map = {
        "🎯 Target 100 KB": 95,
        "🎯 Target 200 KB (CPNS)": 195,
        "🎯 Target 300 KB": 290,
        "🎯 Target 500 KB (BUMN)": 485,
        "⚡ Kompres Maksimal (High Quality)": None,
    }
    tar_kb = target_map.get(text, 195)
    await update.message.reply_text("⏳ <i>Mengompres gambar dengan algoritma pengoptimalan kualitas...</i>", parse_mode="HTML")

    try:
        c_bytes, w, h, fmt = compress_image_advanced(raw_bytes, target_kb=tar_kb, quality=85)
        out_kb = len(c_bytes) / 1024

        bio = io.BytesIO(c_bytes)
        bio.name = f"FOTO_KOMPRES_{int(out_kb)}KB.{fmt.lower()}"
        bio.seek(0)

        caption = (
            f"✅ <b>Foto Berhasil Dikompres!</b>\n\n"
            f"• Ukuran Akhir: <b>{out_kb:.1f} KB</b>\n"
            f"• Resolusi: {w} x {h} px\n"
            f"• Format: {fmt}\n\n"
            f"<i>Berkas siap diunggah ke portal pendaftaran SSCASN CPNS / BUMN.</i>"
        )
        await update.message.reply_document(document=bio, caption=caption, reply_markup=get_tools_reply_keyboard(), parse_mode="HTML")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Compress error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Terjadi kesalahan: {e}", reply_markup=get_tools_reply_keyboard())
        return ConversationHandler.END


# 3. Tanda Tangan Transparan
async def sig_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🖋️ <b>EKSTRAKTOR TANDA TANGAN TRANSPARAN</b>\n\n"
        "Foto tanda tangan Anda di secarik kertas putih, lalu kirimkan ke sini.\n"
        "Sistem AI akan membersihkan bayangan kertas, memotong latar belakang menjadi <b>PNG Transparan Murni</b>, dan mempertajam goresan tinta biru resmi.\n\n"
        "📸 <b>Silakan kirimkan FOTO tanda tangan Anda sekarang:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return SIG_WAIT_PHOTO

async def sig_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    raw_bytes = None
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await photo_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("image/"):
        doc_file = await update.message.document.get_file()
        buf = io.BytesIO()
        await doc_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    else:
        await update.message.reply_text("⚠️ Mohon kirimkan foto tanda tangan yang jelas.")
        return SIG_WAIT_PHOTO

    await update.message.reply_text("⏳ <i>Menghapus latar belakang kertas & mempertajam tinta basah...</i>", parse_mode="HTML")

    try:
        sig_bytes = extract_signature_to_transparent(raw_bytes, ink_color="blue")
        bio = io.BytesIO(sig_bytes)
        bio.name = f"TANDA_TANGAN_TRANSPARAN_{update.effective_user.id}.png"
        bio.seek(0)

        caption = (
            "✅ <b>Tanda Tangan Transparan Berhasil Dibuat!</b>\n\n"
            "✓ Latar belakang transparan murni (PNG)\n"
            "✓ Tinta biru resmi dipertajam\n"
            "✓ Siap disematkan langsung ke dokumen Word / PDF / Excel"
        )
        await update.message.reply_document(document=bio, caption=caption, reply_markup=get_tools_reply_keyboard(), parse_mode="HTML")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Signature error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Gagal memproses: {e}", reply_markup=get_tools_reply_keyboard())
        return ConversationHandler.END



# ==================== VIDEO DOWNLOADER (NO WATERMARK) ====================

# Cache sesi media download (session_key -> dict info)
MEDIA_DL_SESSIONS = {}

async def process_media_link_preview(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Mengambil info pratinjau video secara instan dan menampilkan menu pemilihan format (HD, SD, MP3)"""
    status_msg = await update.message.reply_text("⏳ <i>Menganalisis tautan media & menyiapkan pilihan format...</i>", parse_mode="HTML")

    try:
        info = get_media_info(url)
        session_key = f"{update.effective_user.id}_{int(datetime.now().timestamp())}"
        MEDIA_DL_SESSIONS[session_key] = info

        dur_text = f" • Durasi: <b>{info['duration']} detik</b>" if info['duration'] else ""
        author_text = f" • Pembuat: <b>{html.escape(info['author'])}</b>\n" if info['author'] else ""
        content_type = "📸 Slide Foto & Musik" if info['is_slideshow'] else "🎬 Video"

        caption = (
            f"🎬 <b>{info['platform']} {content_type} Ditemukan!</b>\n\n"
            f"• Judul: <b>{html.escape(info['title'][:75])}</b>\n"
            f"{author_text}"
            f"• Platform: <b>{info['platform']}</b>{dur_text}\n\n"
            "👇 <b>Silakan pilih format yang ingin Anda unduh:</b>"
        )

        kb = get_dl_format_keyboard(session_key, is_slideshow=info['is_slideshow'])

        # Kirim preview cover jika tersedia
        if info.get('thumbnail'):
            try:
                await update.message.reply_photo(photo=info['thumbnail'], caption=caption, reply_markup=kb, parse_mode="HTML")
                await status_msg.delete()
                return
            except Exception:
                pass

        await status_msg.edit_text(caption, reply_markup=kb, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error fetching media info: {e}", exc_info=True)
        await status_msg.edit_text(
            f"❌ <b>Gagal mengambil informasi media:</b>\n{html.escape(str(e))}\n\nPastikan tautan bersifat publik (tidak di-private).",
            parse_mode="HTML"
        )


async def dl_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Membuka mode pengunduh video tanpa watermark"""
    msg = (
        "🎬 <b>PENGUNDUH MEDIA & VIDEO TANPA WATERMARK</b>\n\n"
        "Mendukung unduhan bebas watermark dalam berbagai format:\n"
        "• 🎵 <b>TikTok</b> (Video HD, Slide Foto, & Musik MP3)\n"
        "• 📸 <b>Instagram</b> (Reels, Video Feed, Audio MP3)\n"
        "• 📘 <b>Facebook</b> (Reels & Video Publik HD)\n"
        "• ▶️ <b>YouTube</b> (Shorts, Video MP4, Audio MP3)\n"
        "• 🐦 <b>X / Twitter</b> (Video Postingan HD)\n\n"
        "🔗 <b>Silakan kirimkan TAUTAN / LINK video Anda sekarang:</b>"
    )
    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True),
        parse_mode="HTML"
    )
    return DL_VIDEO_WAIT


async def dl_video_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if text in ["« KEMBALI KE MENU UTAMA", "« KEMBALI KE KOTAK ALAT", "« MENU UTAMA"]:
        await start_command(update, context)
        return ConversationHandler.END

    url = extract_url_from_text(text)
    if not url:
        await update.message.reply_text("⚠️ Tidak ditemukan tautan yang valid dalam pesan Anda. Silakan kirimkan link video (TikTok, IG Reels, FB, atau YouTube).")
        return DL_VIDEO_WAIT

    await process_media_link_preview(update, context, url)
    return ConversationHandler.END

# ==================== EXTRA SUITE TOOLS IMPLEMENTATIONS ====================

# 1. GABUNG PDF (MERGE)
async def merge_pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["merge_pdf_queue"] = []
    msg = (
        "📑 <b>GABUNGKAN BEBERAPA BERKAS PDF (MERGE PDF)</b>\\n\\n"
        "Satukan berkas PDF Anda (misal: <i>CV + Ijazah + Transkrip + Sertifikat</i>) menjadi satu file PDF utuh berurutan.\\n\\n"
        "📎 <b>Kirimkan satu per satu berkas PDF Anda sekarang:</b>\\n"
        "<i>(Setelah semua berkas terkirim, ketuk tombol '✅ GABUNGKAN SEKARANG' di bawah)</i>"
    )
    kb = ReplyKeyboardMarkup([
        [KeyboardButton("✅ GABUNGKAN SEKARANG")],
        [KeyboardButton("« KEMBALI KE MENU UTAMA")],
    ], resize_keyboard=True, is_persistent=True)
    await update.message.reply_text(msg, reply_markup=kb, parse_mode="HTML")
    return MERGE_PDF_WAIT

async def merge_pdf_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if text == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    queue = context.user_data.get("merge_pdf_queue", [])

    if text == "✅ GABUNGKAN SEKARANG":
        if len(queue) < 2:
            await update.message.reply_text("⚠️ Anda harus mengirimkan minimal <b>2 berkas PDF</b> untuk digabungkan.", parse_mode="HTML")
            return MERGE_PDF_WAIT

        await update.message.reply_text(f"⏳ <i>Menggabungkan {len(queue)} berkas PDF menjadi satu dokumen utuh...</i>", parse_mode="HTML")
        try:
            merged_bytes = merge_pdfs(queue)
            bio = io.BytesIO(merged_bytes)
            bio.name = f"DOKUMEN_GABUNGAN_{len(queue)}_FILE.pdf"
            bio.seek(0)

            caption = (
                f"✅ <b>Penggabungan PDF Berhasil!</b>\\n\\n"
                f"• Total Berkas Digabung: <b>{len(queue)} file</b>\\n"
                f"• Ukuran Akhir: <b>{len(merged_bytes)/1024:.1f} KB</b>\\n"
                f"✓ Berkas siap dilampirkan untuk pendaftaran kerja / CPNS."
            )
            context.user_data["merge_pdf_queue"] = []
            await update.message.reply_document(document=bio, caption=caption, reply_markup=get_tools_hub_reply_keyboard(), parse_mode="HTML")
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Merge PDF error: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Gagal menggabungkan PDF: {e}", reply_markup=get_tools_hub_reply_keyboard())
            return ConversationHandler.END

    if update.message.document and (update.message.document.file_name or "").lower().endswith(".pdf"):
        doc = update.message.document
        f = await doc.get_file()
        buf = io.BytesIO()
        await f.download_to_memory(buf)
        queue.append(buf.getvalue())
        context.user_data["merge_pdf_queue"] = queue
        await update.message.reply_text(f"📥 PDF ke-<b>{len(queue)}</b> (<code>{html.escape(doc.file_name)}</code>) berhasil ditambahkan!\\nKirim PDF berikutnya atau ketuk <b>[ ✅ GABUNGKAN SEKARANG ]</b>.", parse_mode="HTML")
        return MERGE_PDF_WAIT
    else:
        await update.message.reply_text("⚠️ Mohon kirimkan berkas berformat PDF (.pdf).")
        return MERGE_PDF_WAIT


# 2. BUKA PASSWORD PDF (UNLOCK)
async def unlock_pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🔓 <b>BUKA PASSWORD / DEKRIPSI DOKUMEN PDF</b>\\n\\n"
        "Menghapus proteksi password pada slip gaji, e-Statement rekening koran bank (BCA, Mandiri, BNI, BRI), "
        "agar dokumen tidak terkunci saat dilampirkan ke formulir pendaftaran.\\n\\n"
        "📎 <b>Silakan kirimkan BERKAS PDF yang terkunci sekarang:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return UNLOCK_PDF_WAIT

async def unlock_pdf_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if text == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    if update.message.document and (update.message.document.file_name or "").lower().endswith(".pdf"):
        doc = update.message.document
        await update.message.reply_text(f"⏳ <i>Membuka proteksi berkas {html.escape(doc.file_name)}...</i>", parse_mode="HTML")
        try:
            f = await doc.get_file()
            buf = io.BytesIO()
            await f.download_to_memory(buf)
            raw_pdf = buf.getvalue()

            unlocked_bytes = unlock_pdf(raw_pdf)
            bio = io.BytesIO(unlocked_bytes)
            bio.name = f"UNLOCKED_{doc.file_name}"
            bio.seek(0)

            caption = (
                f"✅ <b>Dokumen PDF Berhasil Dibuka!</b>\\n\\n"
                f"• Berkas: <code>{html.escape(doc.file_name)}</code>\\n"
                f"✓ Proteksi enkripsi / batasan cetak telah dihapus\\n"
                f"✓ Berkas kini bebas dibuka tanpa kata sandi."
            )
            await update.message.reply_document(document=bio, caption=caption, reply_markup=get_tools_hub_reply_keyboard(), parse_mode="HTML")
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Unlock PDF error: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Gagal: {e}\\nJika file membutuhkan password khusus nasabah, pastikan formatnya valid.", reply_markup=get_tools_hub_reply_keyboard())
            return ConversationHandler.END
    else:
        await update.message.reply_text("⚠️ Kirimkan berkas dalam format PDF.")
        return UNLOCK_PDF_WAIT


# 3. SCAN FOTO KE TEKS (OCR SCANNER)
async def ocr_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🔍 <b>SCAN FOTO / DOKUMEN KE TEKS (OCR SCANNER)</b>\\n\\n"
        "Ekstrak teks dari foto dokumen, buku, invoice, atau screenshot secara otomatis tanpa perlu mengetik ulang.\\n\\n"
        "📸 <b>Silakan kirimkan FOTO dokumen yang ingin disalin teksnya:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return OCR_WAIT_PHOTO

async def ocr_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    raw_bytes = None
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await photo_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    elif update.message.document and (update.message.document.mime_type or "").startswith("image/"):
        doc_file = await update.message.document.get_file()
        buf = io.BytesIO()
        await doc_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    else:
        await update.message.reply_text("⚠️ Kirimkan foto dokumen atau berkas gambar.")
        return OCR_WAIT_PHOTO

    await update.message.reply_text("⏳ <i>Membaca teks dari gambar dengan AI Tesseract OCR...</i>", parse_mode="HTML")
    try:
        extracted_text = ocr_image_to_text(raw_bytes)
        if not extracted_text:
            extracted_text = "⚠️ Tidak ada teks yang terdeteksi secara jelas pada gambar. Pastikan foto tegak lurus dan pencahayaan cukup."

        header = "📝 <b>HASIL PEMINDAIAN TEKS (OCR):</b>\\n\\n"
        await update.message.reply_text(header + extracted_text, reply_markup=get_tools_hub_reply_keyboard(), parse_mode="HTML")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"OCR error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Terjadi kesalahan: {e}", reply_markup=get_tools_hub_reply_keyboard())
        return ConversationHandler.END


# 4. PDF KE GAMBAR HD
async def pdf2img_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📸 <b>KONVERSI PDF KE GAMBAR HD (300 DPI)</b>\\n\\n"
        "Mengubah setiap halaman berkas PDF Anda menjadi foto gambar resolusi tajam.\\n\\n"
        "📎 <b>Silakan kirimkan BERKAS PDF Anda sekarang:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return PDF2IMG_WAIT

async def pdf2img_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    if update.message.document and (update.message.document.file_name or "").lower().endswith(".pdf"):
        doc = update.message.document
        await update.message.reply_text(f"⏳ <i>Merender halaman PDF {html.escape(doc.file_name)} menjadi foto HD...</i>", parse_mode="HTML")
        try:
            f = await doc.get_file()
            buf = io.BytesIO()
            await f.download_to_memory(buf)
            raw_pdf = buf.getvalue()

            images = pdf_to_images_hd(raw_pdf)
            await update.message.reply_text(f"✅ Berhasil merender <b>{len(images)} halaman</b>. Mengirimkan berkas...", parse_mode="HTML")

            for idx, img_b in enumerate(images):
                bio = io.BytesIO(img_b)
                bio.name = f"HALAMAN_{idx+1}.jpg"
                bio.seek(0)
                await update.message.reply_document(document=bio, caption=f"📸 Halaman {idx+1}")

            await update.message.reply_text("Selesai!", reply_markup=get_tools_hub_reply_keyboard())
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"PDF to IMG error: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Gagal: {e}", reply_markup=get_tools_hub_reply_keyboard())
            return ConversationHandler.END
    else:
        await update.message.reply_text("⚠️ Kirimkan berkas PDF.")
        return PDF2IMG_WAIT


# 5. PASFOTO 4R SIAP CETAK
async def pasfoto4r_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🖨️ <b>LEMBAR PASFOTO 4R SIAP CETAK</b>\\n\\n"
        "Menyusun 1 pasfoto Anda ke dalam 1 lembar kertas foto ukuran 4R (10x15 cm / 300 DPI):\\n"
        "• 4 lembar ukuran 4x6\\n"
        "• 4 lembar ukuran 3x4\\n"
        "• 4 lembar ukuran 2x3\\n\\n"
        "📸 <b>Silakan kirimkan PASFOTO Anda sekarang:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE MENU UTAMA")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return PASFOTO4R_WAIT

async def pasfoto4r_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() == "« KEMBALI KE MENU UTAMA":
        await start_command(update, context)
        return ConversationHandler.END

    raw_bytes = None
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await photo_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    elif update.message.document and (update.message.document.mime_type or "").startswith("image/"):
        doc_file = await update.message.document.get_file()
        buf = io.BytesIO()
        await doc_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    else:
        await update.message.reply_text("⚠️ Kirimkan foto.")
        return PASFOTO4R_WAIT

    await update.message.reply_text("⏳ <i>Menyusun lembar foto 4R dengan presisi garis potong 300 DPI...</i>", parse_mode="HTML")
    try:
        sheet_bytes = create_pasfoto_4r_sheet(raw_bytes)
        bio = io.BytesIO(sheet_bytes)
        bio.name = "LEMBAR_PASFOTO_4R_SIAP_CETAK.jpg"
        bio.seek(0)

        caption = (
            "✅ <b>Lembar Pasfoto 4R Selesai!</b>\\n\\n"
            "• Isi: 4 pcs (4x6) + 4 pcs (3x4) + 4 pcs (2x3)\\n"
            "• Standar Cetak: 300 DPI High Resolution\\n"
            "• Siap dibawa ke tempat print foto / studio fotokopi."
        )
        # Kirim preview
        bio_prev = io.BytesIO(sheet_bytes)
        bio_prev.seek(0)
        await update.message.reply_photo(photo=bio_prev, caption="📸 Pratinjau Lembar Cetak 4R")

        # Kirim berkas HD asli
        await update.message.reply_document(document=bio, caption=caption, reply_markup=get_tools_hub_reply_keyboard(), parse_mode="HTML")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"4R error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Gagal: {e}", reply_markup=get_tools_hub_reply_keyboard())
        return ConversationHandler.END

# ==================== NEW ADVANCED CONVERTERS ====================

# 1. PDF ke Word (.docx)
async def pdf2doc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📝 <b>KONVERSI PDF KE MICROSOFT WORD (.DOCX)</b>\\n\\n"
        "Ubah berkas PDF Anda menjadi dokumen Word yang teks, tabel, dan formatnya dapat diedit kembali secara langsung.\\n\\n"
        "📎 <b>Silakan kirimkan BERKAS PDF Anda sekarang:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE KOTAK ALAT")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return PDF2DOC_WAIT_FILE

async def pdf2doc_file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() in ["« KEMBALI KE KOTAK ALAT", "« KEMBALI KE MENU UTAMA"]:
        await start_command(update, context)
        return ConversationHandler.END

    if not update.message.document or not (update.message.document.file_name or "").lower().endswith(".pdf"):
        await update.message.reply_text("⚠️ Mohon kirimkan berkas berformat <b>PDF</b> (.pdf).")
        return PDF2DOC_WAIT_FILE

    doc = update.message.document
    filename = doc.file_name or "document.pdf"
    await update.message.reply_text(f"⏳ <i>Sedang mengonversi {html.escape(filename)} menjadi Word (.docx)...</i>", parse_mode="HTML")

    try:
        f = await doc.get_file()
        buf = io.BytesIO()
        await f.download_to_memory(buf)
        pdf_bytes = buf.getvalue()

        docx_bytes = convert_pdf_to_docx(pdf_bytes)
        out_name = os.path.splitext(filename)[0] + ".docx"

        bio = io.BytesIO(docx_bytes)
        bio.name = out_name
        bio.seek(0)

        caption = f"✅ <b>Konversi ke Word Selesai!</b>\\n• Nama Berkas: <code>{out_name}</code>\\n• Ukuran: {len(docx_bytes)/1024:.1f} KB\\n✓ Teks & tabel siap diedit di Microsoft Word / Google Docs"
        await update.message.reply_document(document=bio, caption=caption, reply_markup=get_doc_convert_reply_keyboard(), parse_mode="HTML")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"PDF to Word error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Gagal mengonversi: {e}", reply_markup=get_doc_convert_reply_keyboard())
        return ConversationHandler.END


# 2. Foto ke PDF (Mendukung JPG, PNG, WEBP, HEIC iPhone)
async def img2pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["img2pdf_queue"] = []
    msg = (
        "🖼️ <b>KONVERSI FOTO / SCAN KE DOKUMEN PDF RESMI</b>\\n\\n"
        "Dapat menggabungkan 1 atau banyak lembar foto menjadi satu berkas PDF rapi berurutan (KTP, Ijazah, Surat Keterangan, Transkrip).\\n"
        "Mendukung format JPG, PNG, WEBP, dan HEIC (kamera iPhone).\\n\\n"
        "📸 <b>Kirimkan satu per satu atau sekaligus foto dokumen Anda:</b>\\n"
        "<i>(Setelah selesai mengirim foto, ketik atau ketuk tombol 'SELESAI & JADIKAN PDF' di bawah)</i>"
    )
    kb = ReplyKeyboardMarkup([
        [KeyboardButton("✅ SELESAI & JADIKAN PDF")],
        [KeyboardButton("« KEMBALI KE KOTAK ALAT")],
    ], resize_keyboard=True, is_persistent=True)
    await update.message.reply_text(msg, reply_markup=kb, parse_mode="HTML")
    return IMG2PDF_WAIT_PHOTOS

async def img2pdf_photos_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if text in ["« KEMBALI KE KOTAK ALAT", "« KEMBALI KE MENU UTAMA"]:
        await start_command(update, context)
        return ConversationHandler.END

    queue = context.user_data.get("img2pdf_queue", [])

    if text == "✅ SELESAI & JADIKAN PDF":
        if not queue:
            await update.message.reply_text("⚠️ Anda belum mengirimkan foto apapun. Silakan kirim minimal 1 foto terlebih dahulu.")
            return IMG2PDF_WAIT_PHOTOS

        await update.message.reply_text(f"⏳ <i>Menggabungkan {len(queue)} foto menjadi satu dokumen PDF resmi...</i>", parse_mode="HTML")
        try:
            pdf_bytes = convert_images_to_pdf(queue)
            bio = io.BytesIO(pdf_bytes)
            bio.name = f"DOKUMEN_GABUNGAN_{len(queue)}_HALAMAN.pdf"
            bio.seek(0)

            caption = (
                f"✅ <b>Dokumen PDF Berhasil Diterbitkan!</b>\\n\\n"
                f"• Total Halaman: <b>{len(queue)} halaman</b>\\n"
                f"• Ukuran Berkas: <b>{len(pdf_bytes)/1024:.1f} KB</b>\\n"
                f"✓ Berkas PDF terstandarisasi cetak rapi"
            )
            context.user_data["img2pdf_queue"] = []
            await update.message.reply_document(document=bio, caption=caption, reply_markup=get_doc_convert_reply_keyboard(), parse_mode="HTML")
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Image to PDF error: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Gagal membuat PDF: {e}", reply_markup=get_doc_convert_reply_keyboard())
            return ConversationHandler.END

    raw_bytes = None
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await photo_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()
    elif update.message.document and (update.message.document.mime_type or "").startswith("image/"):
        doc_file = await update.message.document.get_file()
        buf = io.BytesIO()
        await doc_file.download_to_memory(buf)
        raw_bytes = buf.getvalue()

    if raw_bytes:
        queue.append(raw_bytes)
        context.user_data["img2pdf_queue"] = queue
        await update.message.reply_text(
            f"📥 Foto ke-<b>{len(queue)}</b> berhasil ditambahkan!\\nKirim foto berikutnya atau ketuk <b>[ ✅ SELESAI & JADIKAN PDF ]</b> jika sudah semua.",
            parse_mode="HTML"
        )
        return IMG2PDF_WAIT_PHOTOS
    else:
        await update.message.reply_text("⚠️ Berkas yang dikirim bukan foto. Kirim foto dokumen Anda.")
        return IMG2PDF_WAIT_PHOTOS


# 3. Kompres PDF (Ghostscript Optimization)
async def compress_pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🗜️ <b>KOMPRES UKURAN DOKUMEN PDF (CPNS / BUMN)</b>\\n\\n"
        "Perkecil ukuran dokumen PDF yang terlalu besar (misal 3MB–10MB menjadi di bawah 500KB / 1MB) tanpa merusak kejelasan teks.\\n\\n"
        "📎 <b>Silakan kirimkan BERKAS PDF yang ingin dikompres sekarang:</b>"
    )
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("« KEMBALI KE KOTAK ALAT")]], resize_keyboard=True, is_persistent=True), parse_mode="HTML")
    return COMPRESS_PDF_WAIT_FILE

async def compress_pdf_file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() in ["« KEMBALI KE KOTAK ALAT", "« KEMBALI KE MENU UTAMA"]:
        await start_command(update, context)
        return ConversationHandler.END

    if not update.message.document or not (update.message.document.file_name or "").lower().endswith(".pdf"):
        await update.message.reply_text("⚠️ Mohon kirimkan berkas dalam format <b>PDF</b> (.pdf).")
        return COMPRESS_PDF_WAIT_FILE

    doc = update.message.document
    f = await doc.get_file()
    buf = io.BytesIO()
    await f.download_to_memory(buf)
    pdf_bytes = buf.getvalue()
    context.user_data["comp_pdf_bytes"] = pdf_bytes
    context.user_data["comp_pdf_orig_name"] = doc.file_name or "document.pdf"

    orig_size_kb = len(pdf_bytes) / 1024
    msg = (
        f"✅ <b>Berkas PDF Diterima!</b> (Ukuran Asli: <b>{orig_size_kb:.1f} KB</b>)\\n\\n"
        "Pilih tingkat kompresi pada tombol di bawah layar:\\n"
        "• <b>🎯 Standar CPNS / BUMN (150 DPI)</b>: Sangat direkomendasikan untuk portal SSCASN (teks tajam, ukuran hemat)\\n"
        "• <b>📉 Kompres Ekstrem (72 DPI)</b>: Jika syarat upload sangat kecil (<500 KB)\\n"
        "• <b>⚡ Kompres Ringan (300 DPI)</b>: Mengoptimalkan ukuran dengan kualitas cetak maksimal"
    )
    await update.message.reply_text(msg, reply_markup=get_compress_pdf_levels_reply_keyboard(), parse_mode="HTML")
    return COMPRESS_PDF_WAIT_LEVEL

async def compress_pdf_level_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in ["« KEMBALI KE KOTAK ALAT", "« KEMBALI KE MENU UTAMA"]:
        await start_command(update, context)
        return ConversationHandler.END

    level_map = {
        "🎯 Standar CPNS / BUMN (Optimal / 150 DPI)": "ebook",
        "📉 Kompres Ekstrem (Ukuran Sangat Kecil / 72 DPI)": "screen",
        "⚡ Kompres Ringan (Kualitas Cetak / 300 DPI)": "printer",
    }
    selected_level = level_map.get(text, "ebook")
    raw_pdf = context.user_data.get("comp_pdf_bytes")
    orig_name = context.user_data.get("comp_pdf_orig_name", "document.pdf")

    if not raw_pdf:
        await update.message.reply_text("⚠️ Sesi kedaluwarsa. Silakan ulangi.", reply_markup=get_tools_category_reply_keyboard())
        return ConversationHandler.END

    await update.message.reply_text("⏳ <i>Mengompres dokumen PDF dengan Ghostscript Optimizer...</i>", parse_mode="HTML")
    try:
        res_bytes, orig_kb, res_kb = compress_pdf(raw_pdf, level=selected_level)
        out_name = f"KOMPRES_{int(res_kb)}KB_" + orig_name

        bio = io.BytesIO(res_bytes)
        bio.name = out_name
        bio.seek(0)

        hemat_persen = max(0, int(((orig_kb - res_kb) / orig_kb) * 100)) if orig_kb > 0 else 0
        caption = (
            f"✅ <b>Dokumen PDF Berhasil Dikompres!</b>\\n\\n"
            f"• Ukuran Sebelum: <b>{orig_kb:.1f} KB</b>\\n"
            f"• Ukuran Sesudah: <b>{res_kb:.1f} KB</b>\\n"
            f"• Ruang Hemat: <b>{hemat_persen}% lebih ringan</b>\\n\\n"
            f"<i>Berkas siap diunggah ke portal CPNS/BUMN.</i>"
        )
        await update.message.reply_document(document=bio, caption=caption, reply_markup=get_compress_category_reply_keyboard(), parse_mode="HTML")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Compress PDF error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Terjadi kesalahan saat kompres PDF: {e}", reply_markup=get_compress_category_reply_keyboard())
        return ConversationHandler.END

# ==================== HANDLER TRANSKRIP NILAI (KHS) ====================

async def khs_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan pilihan kampus untuk cetak Transkrip Nilai (KHS)"""
    msg = (
        "📊 <b>CETAK TRANSKRIP NILAI / KARTU HASIL STUDI (KHS)</b>\n\n"
        "Dokumen naskah akademik resmi A4 (300 DPI) berisikan:\n"
        "• Kop resmi Universitas & Kementerian Sains Teknologi\n"
        "• Tabel 8 Mata Kuliah (22 SKS, Nilai A/A-/B+, Bobot SKS)\n"
        "• Indeks Prestasi Kumulatif: <b>IPK 3.84 (Cum Laude)</b>\n"
        "• Tanda tangan basah Dekan & Cap Stempel Ungu Dekanat\n"
        "• Sensor metadata EXIF asli kamera HP (Anti-Fraud)\n\n"
        "👇 <b>Silakan pilih universitas pada tombol di bawah:</b>"
    )
    await update.message.reply_text(msg, reply_markup=get_khs_univ_reply_keyboard(), parse_mode="HTML")

async def khs_generate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, univ_code: str):
    """Menerbitkan lembar KHS resmi berdasarkan universitas"""
    user = update.effective_user
    u_data = get_or_create_user(user.id, user.username or "", user.first_name or "")
    if not u_data["is_vip"] and u_data["quota_left"] <= 0:
        await update.message.reply_text("⚠️ <b>Kuota cetak Anda habis!</b>\nSilakan isi ulang kuota di menu 👑 PROFIL & VIP.", parse_mode="HTML")
        return

    status_msg = await update.message.reply_text("⏳ <i>Sedang menyusun naskah akademik & merender Transkrip Nilai (KHS) 300 DPI...</i>", parse_mode="HTML")

    try:
        from khs_generator import generate_khs_transcript
        
        # Ambil nama user atau acak
        f_name = user.first_name or "Aditya"
        l_name = user.last_name or "Pratama"
        
        khs_png = generate_khs_transcript(first_name=f_name, last_name=l_name, univ_code=univ_code)
        khs_exif = inject_camera_exif(khs_png)

        # Simpan ke cache
        khs_key = f"{user.id}_last_khs"
        SESSION_DOC_CACHE[khs_key] = {
            "png_bytes": khs_png,
            "exif_bytes": khs_exif,
            "univ_code": univ_code,
            "name": f"{f_name} {l_name}",
            "type": "khs"
        }

        # Potong kuota
        if not u_data["is_vip"]:
            decrement_quota(user.id)
            track_document_generated(user.id, "KHS", univ_code)

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📥 Unduh KHS PDF", callback_data=f"dl_pdf:{khs_key}"),
                InlineKeyboardButton("📁 Unduh Gambar HD (PNG)", callback_data=f"dl_raw:{khs_key}")
            ],
            [InlineKeyboardButton("« Selesai", callback_data="main_menu")]
        ])

        caption = (
            f"✅ <b>Transkrip Nilai (KHS) Resmi Berhasil Diterbitkan!</b>\n\n"
            f"• Mahasiswa: <b>{html.escape(f_name.upper())} {html.escape(l_name.upper())}</b>\n"
            f"• Kampus: <b>{univ_code}</b>\n"
            f"• Prestasi: <b>22 SKS • IPK 3.84 (Cum Laude)</b>\n"
            f"• Format: <b>Lembar A4 Resmi 300 DPI</b>\n"
            f"• Legalitas: Tanda Tangan Dekanat + Stempel Dinas\n"
            f"• Keamanan: Anti-Fraud EXIF iPhone 14 Pro Verified"
        )

        bio = io.BytesIO(khs_exif)
        bio.name = f"KHS_{univ_code}_{f_name}.png"
        bio.seek(0)

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=bio,
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML"
        )
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error generating KHS: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ <b>Gagal menerbitkan KHS:</b> {e}", parse_mode="HTML")

def main():
    print("Starting Comprehensive Yowes Bot...")
    req_settings = HTTPXRequest(
        read_timeout=180.0,
        write_timeout=180.0,
        connect_timeout=60.0,
        media_write_timeout=300.0, # 5 menit untuk upload video besar hingga 50MB
    )
    app = Application.builder().token(BOT_TOKEN).request(req_settings).post_init(setup_bot_commands).build()

    # Conversation handler untuk custom name & photo
    custom_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(custom_flow_start, pattern="^start_custom_flow$")],
        states={
            CUSTOM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_name_received)],
            CUSTOM_PHOTO: [
                MessageHandler(filters.PHOTO, custom_photo_received),
                CommandHandler("lewati", custom_photo_skipped),
                MessageHandler(filters.TEXT, custom_photo_skipped),
            ],
            CUSTOM_UNIV: [CallbackQueryHandler(custom_univ_received, pattern="^c_univ:")],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_custom_handler, pattern="^cancel_custom$"),
            CommandHandler("batal", cancel_custom_handler),
        ],
        per_message=False,
    )

    # Conversation handler untuk AI Background Remover
    rembg_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(✂️ HAPUS BG & GANTI WARNA|✂️ Hapus BG & Pasfoto AI)$"), rembg_start),
            CommandHandler("rembg", rembg_start),
        ],
        states={
            REMBG_WAIT_PHOTO: [
                MessageHandler(filters.PHOTO | (filters.Document.ALL & filters.Document.MimeType("image/*")), rembg_photo_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, rembg_photo_received),
            ],
            REMBG_WAIT_COLOR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, rembg_color_received),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cancel_custom_handler),
            MessageHandler(filters.Regex("^« KEMBALI KE MENU UTAMA$"), start_command),
        ],
        per_message=False,
    )

    # Conversation handler untuk Word ke PDF
    doc2pdf_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(📄 KONVERSI WORD KE PDF|📄 Word ke PDF)$"), doc2pdf_start),
            CommandHandler("doc2pdf", doc2pdf_start),
        ],
        states={
            DOC2PDF_WAIT_FILE: [
                MessageHandler(filters.Document.ALL, doc2pdf_file_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, doc2pdf_file_received),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cancel_custom_handler),
            MessageHandler(filters.Regex("^« KEMBALI KE MENU UTAMA$"), start_command),
        ],
        per_message=False,
    )

    # Conversation handler untuk Kompres Foto
    compress_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(🗜️ KOMPRES FOTO \(CPNS/BUMN\)|🗜️ Kompres Foto \(CPNS\))$"), compress_start),
            CommandHandler("kompres", compress_start),
        ],
        states={
            COMPRESS_WAIT_PHOTO: [
                MessageHandler(filters.PHOTO | (filters.Document.ALL & filters.Document.MimeType("image/*")), compress_photo_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, compress_photo_received),
            ],
            COMPRESS_WAIT_SIZE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, compress_size_received),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cancel_custom_handler),
            MessageHandler(filters.Regex("^« KEMBALI KE MENU UTAMA$"), start_command),
        ],
        per_message=False,
    )

    # Conversation handler untuk Tanda Tangan Transparan
    sig_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(🖋️ TANDA TANGAN TRANSPARAN|🖋️ Tanda Tangan Transparan)$"), sig_start),
            CommandHandler("ttd", sig_start),
        ],
        states={
            SIG_WAIT_PHOTO: [
                MessageHandler(filters.PHOTO | (filters.Document.ALL & filters.Document.MimeType("image/*")), sig_photo_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sig_photo_received),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cancel_custom_handler),
            MessageHandler(filters.Regex("^« KEMBALI KE MENU UTAMA$"), start_command),
        ],
        per_message=False,
    )

    # Conversation Handler Video Downloader
    dl_video_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(🎬 DOWNLOAD VIDEO \(NO WM\)|🎬 DOWNLOAD VIDEO|✂️ Auto Clip Video \(9:16\)|✂️ Auto Clip Video)$"), dl_video_start),
            CommandHandler("download", dl_video_start),
            CommandHandler("dl", dl_video_start),
        ],
        states={
            DL_VIDEO_WAIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, dl_video_process),
            ],
        },
        fallbacks=[
            CommandHandler("batal", cancel_custom_handler),
            MessageHandler(filters.Regex("^« KEMBALI KE MENU UTAMA$"), start_command),
        ],
        per_message=False,
    )

    app.add_handler(custom_conv)
    app.add_handler(rembg_conv)
    app.add_handler(doc2pdf_conv)
    app.add_handler(compress_conv)
    app.add_handler(sig_conv)
    app.add_handler(dl_video_conv)

    # Merge PDF
    merge_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📑 Gabung PDF \\(Merge\\)$"), merge_pdf_start),
            CommandHandler("mergepdf", merge_pdf_start),
        ],
        states={MERGE_PDF_WAIT: [MessageHandler(filters.ALL, merge_pdf_received)]},
        fallbacks=[CommandHandler("batal", cancel_custom_handler)],
        per_message=False,
    )
    app.add_handler(merge_conv)

    # Unlock PDF
    unlock_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔓 Buka Password PDF$"), unlock_pdf_start),
            CommandHandler("unlockpdf", unlock_pdf_start),
        ],
        states={UNLOCK_PDF_WAIT: [MessageHandler(filters.ALL, unlock_pdf_received)]},
        fallbacks=[CommandHandler("batal", cancel_custom_handler)],
        per_message=False,
    )
    app.add_handler(unlock_conv)

    # OCR Scanner
    ocr_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔍 Scan Foto ke Teks \\(OCR\\)$"), ocr_start),
            CommandHandler("ocr", ocr_start),
        ],
        states={OCR_WAIT_PHOTO: [MessageHandler(filters.ALL, ocr_photo_received)]},
        fallbacks=[CommandHandler("batal", cancel_custom_handler)],
        per_message=False,
    )
    app.add_handler(ocr_conv)

    # PDF to Images
    pdf2img_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📸 PDF ke Gambar HD$"), pdf2img_start),
            CommandHandler("pdf2img", pdf2img_start),
        ],
        states={PDF2IMG_WAIT: [MessageHandler(filters.ALL, pdf2img_received)]},
        fallbacks=[CommandHandler("batal", cancel_custom_handler)],
        per_message=False,
    )
    app.add_handler(pdf2img_conv)

    # Pasfoto 4R
    pasfoto4r_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🖨️ Pasfoto 4R Siap Cetak$"), pasfoto4r_start),
            CommandHandler("pasfoto4r", pasfoto4r_start),
        ],
        states={PASFOTO4R_WAIT: [MessageHandler(filters.ALL, pasfoto4r_received)]},
        fallbacks=[CommandHandler("batal", cancel_custom_handler)],
        per_message=False,
    )
    app.add_handler(pasfoto4r_conv)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("profil", profil_command))
    app.add_handler(CommandHandler("ktm", ktm_command))
    app.add_handler(CommandHandler("pelajar", pelajar_command))
    app.add_handler(CommandHandler("guru", guru_command))
    app.add_handler(CommandHandler("referral", referral_command))
    app.add_handler(CommandHandler("bantuan", bantuan_command))
    app.add_handler(CommandHandler("dl", dl_video_start))
    app.add_handler(CommandHandler("khs", khs_menu_handler))
    app.add_handler(CommandHandler("kurs", lambda u, c: u.message.reply_text(currency_service.get_popular_rates_text(), parse_mode="HTML")))
    app.add_handler(CommandHandler("autoclip", dl_video_start))

    # Admin commands
    app.add_handler(CommandHandler("stats", admin_stats_command))
    app.add_handler(CommandHandler("addquota", admin_addquota_command))
    app.add_handler(CommandHandler("broadcast", admin_broadcast_command))

    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_button_handler))

    print("Bot polling running smoothly...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
