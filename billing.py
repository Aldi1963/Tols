import sqlite3
from datetime import datetime, date
import urllib.request
import json
import os

DB_PATH = "/home/ubuntu/yowes/users.db"
CLIPKU_API_URL = "https://m.clipku.com/api/index.php"
CLIPKU_API_KEY = "pk_59dad270be0e1dcefd31f9d636712e7b"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        quota_left INTEGER DEFAULT 3,
        last_quota_date TEXT,
        is_vip INTEGER DEFAULT 0,
        vip_until TEXT,
        total_generated INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS topups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_id TEXT UNIQUE,
        amount INTEGER,
        package_type TEXT,
        status TEXT DEFAULT 'PENDING',
        payment_url TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(user_id: int, username: str = "", first_name: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today_str = date.today().isoformat()

    cur.execute("SELECT user_id, quota_left, last_quota_date, is_vip, vip_until, total_generated FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if not row:
        now_str = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO users (user_id, username, first_name, quota_left, last_quota_date, is_vip, vip_until, total_generated, created_at) VALUES (?, ?, ?, 3, ?, 0, NULL, 0, ?)",
            (user_id, username, first_name, today_str, now_str)
        )
        conn.commit()
        user_data = {
            "user_id": user_id,
            "quota_left": 3,
            "is_vip": False,
            "vip_until": None,
            "total_generated": 0
        }
    else:
        q_left = row[1]
        last_date = row[2]
        is_vip = bool(row[3])
        vip_until = row[4]
        tot_gen = row[5]

        # Reset daily quota jika hari berganti
        if last_date != today_str:
            q_left = max(3, q_left)  # reset ke minimal 3
            cur.execute("UPDATE users SET quota_left = ?, last_quota_date = ?, username = ?, first_name = ? WHERE user_id = ?",
                        (q_left, today_str, username, first_name, user_id))
            conn.commit()

        # Cek expired VIP
        if is_vip and vip_until:
            try:
                exp = datetime.fromisoformat(vip_until)
                if datetime.now() > exp:
                    is_vip = False
                    cur.execute("UPDATE users SET is_vip = 0 WHERE user_id = ?", (user_id,))
                    conn.commit()
            except Exception:
                pass

        user_data = {
            "user_id": user_id,
            "quota_left": q_left,
            "is_vip": is_vip,
            "vip_until": vip_until,
            "total_generated": tot_gen
        }

    conn.close()
    return user_data

def consume_quota(user_id: int) -> bool:
    """Mengurangi 1 kuota jika bukan VIP"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT quota_left, is_vip FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False

    q_left, is_vip = row[0], bool(row[1])
    if is_vip:
        cur.execute("UPDATE users SET total_generated = total_generated + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True

    if q_left > 0:
        cur.execute("UPDATE users SET quota_left = quota_left - 1, total_generated = total_generated + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

def create_clipku_payment(user_id: int, package_type: str, user_name: str) -> dict:
    """Membuat transaksi pembayaran via Clipku Pay API"""
    if package_type == "quota_10":
        amount = 5000
        desc = "Paket Tambahan 10 Kuota Cetak Dokumen"
    elif package_type == "vip_30d":
        amount = 15000
        desc = "Paket VIP Unlimited Cetak Dokumen (30 Hari)"
    else:
        amount = 5000
        desc = "Paket Kuota Dokumen Edu"

    payload = {
        "amount": amount,
        "product_name": desc,
        "customer_name": user_name or f"User {user_id}",
        "customer_email": f"user{user_id}@clipku.bot",
        "customer_phone": "081234567890",
        "payment_method": "qris"
    }

    req = urllib.request.Request(
        f"{CLIPKU_API_URL}?action=create_transaction",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {CLIPKU_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("success"):
                tx = data["data"]
                order_id = tx["order_id"]
                pay_url = tx["payment_url"]

                # Simpan ke tabel topups
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO topups (user_id, order_id, amount, package_type, status, payment_url, created_at) VALUES (?, ?, ?, ?, 'PENDING', ?, ?)",
                    (user_id, order_id, amount, package_type, pay_url, datetime.now().isoformat())
                )
                conn.commit()
                conn.close()

                return {
                    "success": True,
                    "order_id": order_id,
                    "amount": amount,
                    "payment_url": pay_url
                }
            else:
                return {"success": False, "error": data.get("error", "Gagal membuat transaksi")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_and_apply_payment(order_id: str) -> dict:
    """Mengecek status pembayaran ke Clipku Pay dan menambah kuota jika sukses"""
    req = urllib.request.Request(
        f"{CLIPKU_API_URL}?action=get_transaction&order_id={order_id}",
        headers={
            "Authorization": f"Bearer {CLIPKU_API_KEY}",
            "User-Agent": USER_AGENT
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("success"):
                tx = data["data"]
                status = tx["status"].upper()

                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT user_id, package_type, status FROM topups WHERE order_id = ?", (order_id,))
                topup = cur.fetchone()

                if not topup:
                    conn.close()
                    return {"success": False, "message": "Transaksi tidak ditemukan di bot."}

                user_id, pkg_type, current_status = topup[0], topup[1], topup[2]

                if current_status == "PAID":
                    conn.close()
                    return {"success": True, "already_applied": True, "status": "PAID", "message": "Transaksi ini sudah berhasil diproses sebelumnya."}

                if status == "PAID":
                    cur.execute("UPDATE topups SET status = 'PAID' WHERE order_id = ?", (order_id,))
                    
                    if pkg_type == "quota_10":
                        cur.execute("UPDATE users SET quota_left = quota_left + 10 WHERE user_id = ?", (user_id,))
                        msg = "🎉 Pembayaran Terverifikasi! Kuota Anda bertambah +10 dokumen."
                    elif pkg_type == "vip_30d":
                        from datetime import timedelta
                        vip_end = (datetime.now() + timedelta(days=30)).isoformat()
                        cur.execute("UPDATE users SET is_vip = 1, vip_until = ? WHERE user_id = ?", (vip_end, user_id))
                        msg = "👑 Selamat! Akun Anda aktif sebagai VIP UNLIMITED (30 Hari Bebas Cetak)."
                    else:
                        cur.execute("UPDATE users SET quota_left = quota_left + 5 WHERE user_id = ?", (user_id,))
                        msg = "🎉 Pembayaran sukses! Kuota Anda telah ditambahkan."

                    conn.commit()
                    conn.close()
                    return {"success": True, "status": "PAID", "message": msg}
                else:
                    conn.close()
                    return {"success": False, "status": status, "message": f"Status pembayaran saat ini masih: {status}. Mohon selesaikan pembayaran QRIS Anda."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def process_referral(referrer_id: int, new_user_id: int) -> bool:
    """Memproses bonus referral: +2 kuota ke pengundang jika pengguna baru belum pernah terdaftar"""
    if referrer_id == new_user_id:
        return False

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # Cek apakah user pengundang valid
        cur.execute("SELECT user_id, quota_left FROM users WHERE user_id = ?", (referrer_id,))
        ref_row = cur.fetchone()
        if not ref_row:
            return False

        # Cek apakah user baru sudah punya referred_by
        cur.execute("SELECT referred_by FROM users WHERE user_id = ?", (new_user_id,))
        u_row = cur.fetchone()
        if u_row and u_row[0] is not None:
            return False  # Sudah pernah di-refer sebelumnya

        # Catat referred_by pada user baru
        cur.execute("UPDATE users SET referred_by = ? WHERE user_id = ?", (referrer_id, new_user_id))
        # Tambah +2 kuota ke pengundang dan catat counter
        cur.execute("UPDATE users SET quota_left = quota_left + 2, referral_count = COALESCE(referral_count, 0) + 1 WHERE user_id = ?", (referrer_id,))
        conn.commit()
        return True
    except Exception as e:
        print("Referral error:", e)
        return False
    finally:
        conn.close()

def get_referral_stats(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(referral_count, 0), quota_left FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"count": row[0], "quota": row[1]}
    return {"count": 0, "quota": 0}
