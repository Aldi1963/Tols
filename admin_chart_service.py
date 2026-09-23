import io
import sqlite3
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_admin_stats_chart(db_path: str = "/home/ubuntu/yowes/users.db") -> bytes:
    """
    Menghasilkan grafik statistik tren pertumbuhan mingguan:
    - User baru terdaftar
    - Transaksi topup & omzet
    - Total berkas yang diterbitkan
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Dapatkan 7 hari terakhir
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    date_labels = [d.strftime("%d %b") for d in dates]

    users_count = []
    revenue_count = []

    for d in dates:
        d_str = d.strftime("%Y-%m-%d")
        # Hitung user baru per hari
        cur.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (f"{d_str}%",))
        users_count.append(cur.fetchone()[0])

        # Hitung omzet topup sukses per hari
        cur.execute("SELECT COALESCE(SUM(amount), 0) FROM topups WHERE status = 'PAID' AND created_at LIKE ?", (f"{d_str}%",))
        revenue_count.append(cur.fetchone()[0] / 1000.0) # Dalam ribuan Rp

    conn.close()

    # Buat figure dengan 2 subplot
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    fig.patch.set_facecolor('#1e1e2e')
    ax1.set_facecolor('#24273a')
    ax2.set_facecolor('#24273a')

    # Subplot 1: User Baru
    bars1 = ax1.bar(date_labels, users_count, color='#8aadf4', width=0.5, label='User Baru')
    ax1.set_ylabel('Pengguna', color='#cad3f5', fontsize=11, fontweight='bold')
    ax1.set_title('📊 TREN PERTUMBUHAN MINGGUAN YOWES BOT', color='#f4dbd6', fontsize=14, fontweight='bold', pad=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    for bar in bars1:
        yval = bar.get_height()
        if yval > 0:
            ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, int(yval), ha='center', va='bottom', color='#cad3f5', fontsize=10, fontweight='bold')

    # Subplot 2: Omzet Topup (Ribu Rupiah)
    ax2.plot(date_labels, revenue_count, color='#a6da95', marker='o', linewidth=2.5, markersize=7, label='Omzet (Ribu Rp)')
    ax2.fill_between(date_labels, revenue_count, color='#a6da95', alpha=0.15)
    ax2.set_ylabel('Omzet (Ribu Rp)', color='#cad3f5', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Tanggal', color='#cad3f5', fontsize=11, fontweight='bold')
    ax2.grid(linestyle='--', alpha=0.3)
    for x, y in zip(date_labels, revenue_count):
        if y > 0:
            ax2.annotate(f"Rp {int(y)}k", (x, y), textcoords="offset points", xytext=(0, 8), ha='center', color='#a6da95', fontsize=10, fontweight='bold')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf.getvalue()
