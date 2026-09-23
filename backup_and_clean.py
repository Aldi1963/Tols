import os
import sys
import glob
import time
import shutil
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("/home/ubuntu/yowes")
DB_PATH = BASE_DIR / "users.db"
ADMIN_ID = 5606826328

def get_bot_token():
    bot_py = BASE_DIR / "bot.py"
    if bot_py.exists():
        with open(bot_py, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("BOT_TOKEN") and "=" in line:
                    parts = line.split("=", 1)
                    return parts[1].strip().strip('"\';')
    return None

def send_telegram_message(token: str, chat_id: int, text: str):
    """Helper kirim pesan Telegram langsung via urllib"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True
    except Exception as e:
        print(f"Error sending msg to {chat_id}: {e}")
        return False

def check_and_notify_expiring_vip():
    """
    Memeriksa akun VIP yang akan kedaluwarsa dalam H-3 dan H-1,
    lalu mengirimkan pesan pengingat sopan dengan link perpanjang.
    """
    token = get_bot_token()
    if not token or not DB_PATH.exists():
        return

    import json
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.now()
    # Dapatkan seluruh user VIP aktif
    cur.execute("SELECT user_id, first_name, vip_until FROM users WHERE is_vip = 1 AND vip_until IS NOT NULL")
    vip_users = cur.fetchall()

    notified_count = 0
    for u_id, f_name, v_until in vip_users:
        try:
            exp_date = datetime.fromisoformat(v_until)
            diff = exp_date - now
            days_left = diff.days

            # Notifikasi H-3 (antara 2 dan 3 hari)
            if 2 <= days_left <= 3:
                msg = (
                    f"⏰ <b>Pemberitahuan Masa Aktif VIP (H-3)</b>\n\n"
                    f"Halo <b>{f_name or 'Pengguna'}</b>! 👋\n"
                    f"Masa langganan 👑 <b>VIP UNLIMITED</b> Anda akan berakhir dalam <b>{days_left} hari</b> (pada {v_until[:10]}).\n\n"
                    "Agar akses bebas cetak ribuan dokumen & seluruh kotak alat tanpa batas tetap aktif, Anda dapat memperpanjang paket VIP kapan saja melalui menu <b>👑 PROFIL & VIP</b>."
                )
                send_telegram_message(token, u_id, msg)
                notified_count += 1

            # Notifikasi H-1 (kurang dari 24 jam)
            elif 0 <= days_left <= 1:
                msg = (
                    f"⚠️ <b>Perhatian: Masa Aktif VIP Berakhir Besok! (H-1)</b>\n\n"
                    f"Halo <b>{f_name or 'Pengguna'}</b>! 👋\n"
                    f"Masa langganan 👑 <b>VIP UNLIMITED</b> Anda berakhir besok pada <b>{v_until[:10]}</b>.\n\n"
                    "Segera perpanjang langganan Anda melalui tombol <b>👑 Beli VIP 30 Hari</b> pada menu profil untuk menghindari gangguan layanan."
                )
                send_telegram_message(token, u_id, msg)
                notified_count += 1

        except Exception as e:
            print(f"Error checking vip for {u_id}: {e}")

    conn.close()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VIP Reminder: {notified_count} pengguna dikirimi pengingat.")

def clean_temp_files(max_age_seconds=3600):
    now = time.time()
    patterns = [
        "/tmp/*.mp4", "/tmp/*.mp3", "/tmp/*.m4a", "/tmp/*.part",
        "/tmp/*.webm", "/tmp/test_*.png", "/tmp/test_*.jpg",
        "/tmp/clip_part_*.mp4", "/tmp/FOTO_MEJA_*.jpg",
        "/tmp/LANYARD_*.jpg", "/tmp/HAND_POV_*.jpg", "/tmp/KTM_*.jpg",
        "/tmp/SKMA_*.jpg", "/tmp/KHS_*.png"
    ]
    deleted_count = 0
    deleted_bytes = 0

    for pat in patterns:
        for fpath in glob.glob(pat):
            try:
                st = os.stat(fpath)
                if now - st.st_mtime > max_age_seconds:
                    size = st.st_size
                    os.remove(fpath)
                    deleted_count += 1
                    deleted_bytes += size
            except Exception as e:
                print(f"Error removing {fpath}: {e}")

    mb_saved = deleted_bytes / (1024 * 1024)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Temp Cleaner: Menghapus {deleted_count} berkas temporary ({mb_saved:.2f} MB dibebaskan).")
    return deleted_count, mb_saved

def backup_database_to_telegram():
    token = get_bot_token()
    if not token or not DB_PATH.exists():
        return False

    total_users = 0
    total_vip = 0
    total_docs = 0

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        total_vip = c.fetchone()[0]

        c.execute("SELECT SUM(total_generated) FROM users")
        row = c.fetchone()
        total_docs = row[0] if row and row[0] else 0
        conn.close()
    except Exception as e:
        print(f"Error reading db stats: {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"users_backup_{timestamp}.db"
    backup_path = f"/tmp/{backup_filename}"

    try:
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(backup_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
    except Exception as e:
        shutil.copy2(DB_PATH, backup_path)

    db_size_kb = os.path.getsize(backup_path) / 1024

    caption = (
        f"🗄️ <b>Laporan Auto-Backup Database Yowes Bot</b>\n\n"
        f"• Waktu Backup: <code>{datetime.now().strftime('%d %B %Y, %H:%M:%S')}</code>\n"
        f"• Ukuran Database: <b>{db_size_kb:.1f} KB</b>\n"
        f"• Total Terdaftar: <b>{total_users} pengguna</b>\n"
        f"• Pengguna VIP Aktif: <b>{total_vip} akun</b>\n"
        f"• Total Dokumen Terbit: <b>{total_docs} berkas</b>\n\n"
        f"✓ <i>Snapshot SQLite aman & data tersimpan utuh di chat Admin.</i>"
    )

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    boundary = "----WebKitFormBoundary" + str(int(time.time()))
    body = bytearray()

    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{ADMIN_ID}\r\n'.encode('utf-8'))

    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="parse_mode"\r\n\r\nHTML\r\n'.encode('utf-8'))

    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))

    with open(backup_path, "rb") as f:
        doc_bytes = f.read()

    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="document"; filename="{backup_filename}"\r\n'.encode('utf-8'))
    body.extend(b'Content-Type: application/x-sqlite3\r\n\r\n')
    body.extend(doc_bytes)
    body.extend(b'\r\n')
    body.extend(f"--{boundary}--\r\n".encode('utf-8'))

    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "YowesBotBackup/1.0"
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return True
    except Exception as e:
        print(f"Gagal kirim backup: {e}")
        return False

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action in ["clean", "all"]:
        clean_temp_files()
    if action in ["backup", "all"]:
        backup_database_to_telegram()
    if action in ["remind_vip", "all"]:
        check_and_notify_expiring_vip()
