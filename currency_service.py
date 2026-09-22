import time
import json
import re
import urllib.request
from typing import Dict, Any, Optional, Tuple

# Cache data kurs agar cepat & tidak over-request
_CACHE_DATA: Optional[Dict[str, Any]] = None
_CACHE_TIME: float = 0.0
CACHE_TTL = 900  # 15 menit

CURRENCY_FLAGS = {
    "USD": "🇺🇸 Dollar Amerika",
    "SGD": "🇸🇬 Dollar Singapura",
    "MYR": "🇲🇾 Ringgit Malaysia",
    "EUR": "🇪🇺 Euro Uni Eropa",
    "JPY": "🇯🇵 Yen Jepang",
    "CNY": "🇨🇳 Yuan China",
    "AUD": "🇦🇺 Dollar Australia",
    "GBP": "🇬🇧 Poundsterling Inggris",
    "SAR": "🇸🇦 Riyal Arab Saudi",
    "THB": "🇹🇭 Baht Thailand",
    "KRW": "🇰🇷 Won Korea Selatan",
    "HKD": "🇭🇰 Dollar Hong Kong",
    "IDR": "🇮🇩 Rupiah Indonesia",
}

def get_exchange_data() -> Optional[Dict[str, Any]]:
    global _CACHE_DATA, _CACHE_TIME
    now = time.time()
    if _CACHE_DATA and (now - _CACHE_TIME < CACHE_TTL):
        return _CACHE_DATA

    url = "https://open.er-api.com/v6/latest/USD"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("result") == "success" and "rates" in data:
                _CACHE_DATA = data
                _CACHE_TIME = now
                return data
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        if _CACHE_DATA:
            return _CACHE_DATA
    return None

def convert_currency(amount: float, from_curr: str, to_curr: str = "IDR") -> Optional[Dict[str, Any]]:
    """Konversi mata uang dari from_curr ke to_curr secara akurat."""
    data = get_exchange_data()
    if not data or "rates" not in data:
        return None

    rates = data["rates"]
    from_curr = from_curr.upper().strip()
    to_curr = to_curr.upper().strip()

    if from_curr not in rates or to_curr not in rates:
        return None

    # Semua rate berbasis USD
    # Nilai dalam USD = amount / rates[from_curr]
    # Nilai dalam to_curr = (amount / rates[from_curr]) * rates[to_curr]
    usd_val = amount / rates[from_curr]
    result_val = usd_val * rates[to_curr]
    rate_single = rates[to_curr] / rates[from_curr]

    return {
        "amount": amount,
        "from_curr": from_curr,
        "to_curr": to_curr,
        "result": result_val,
        "rate_single": rate_single,
        "update_utc": data.get("time_last_update_utc", "Live"),
    }

def get_popular_rates_text() -> str:
    """Menampilkan papan kurs valuta asing populer terhadap Rupiah (IDR)."""
    data = get_exchange_data()
    if not data or "rates" not in data:
        return "⚠️ Gagal mengambil data kurs valas live. Silakan coba sesaat lagi."

    rates = data["rates"]
    usd_to_idr = rates.get("IDR", 17800.0)

    lines = [
        "💱 <b>PAPAN KURS MATA UANG DUNIA REAL-TIME</b>",
        f"<i>Diperbarui langsung dari Pasar Valas Global: {data.get('time_last_update_utc', 'Hari Ini')[:16]} UTC</i>\n",
    ]

    popular = ["USD", "SGD", "MYR", "EUR", "JPY", "CNY", "AUD", "GBP", "SAR", "THB", "KRW"]
    for c in popular:
        if c in rates:
            rate_val = usd_to_idr / rates[c]
            flag_name = CURRENCY_FLAGS.get(c, c)
            if c in ["JPY", "KRW"]:
                lines.append(f"• {flag_name} (100 {c}): <b>Rp {rate_val * 100:,.2f}</b>")
            else:
                lines.append(f"• {flag_name} (1 {c}): <b>Rp {rate_val:,.2f}</b>")

    lines.append("\n💡 <b>Cara Hitung Cepat di Chat:</b>")
    lines.append("Cukup ketik nominal di obrolan bot, contoh:")
    lines.append("• <code>150 usd to idr</code> atau <code>$150</code>")
    lines.append("• <code>50 sgd to idr</code>")
    lines.append("• <code>2000 myr to idr</code>")
    lines.append("• <code>1000000 idr to usd</code>")

    return "\n".join(lines)

def parse_currency_query(text: str) -> Optional[Tuple[float, str, str]]:
    """Mendeteksi query konversi seperti '150 usd to idr', '$50', '50 eur to idr'."""
    text = text.strip().lower()

    # Format 1: $50 atau $ 150
    m_sym = re.match(r"^[\$]\s*([0-9\.,]+)$", text)
    if m_sym:
        try:
            val = float(m_sym.group(1).replace(",", ""))
            return (val, "USD", "IDR")
        except ValueError:
            pass

    # Format 2: RM 50 atau RM50
    m_rm = re.match(r"^rm\s*([0-9\.,]+)$", text)
    if m_rm:
        try:
            val = float(m_rm.group(1).replace(",", ""))
            return (val, "MYR", "IDR")
        except ValueError:
            pass

    # Format 3: 150 usd to idr / 150 usd ke idr
    m_to = re.match(r"^([0-9\.,]+)\s*([a-z]{3})\s*(?:to|ke|=)\s*([a-z]{3})$", text)
    if m_to:
        try:
            val = float(m_to.group(1).replace(",", ""))
            f_c = m_to.group(2).upper()
            t_c = m_to.group(3).upper()
            return (val, f_c, t_c)
        except ValueError:
            pass

    # Format 4: 150 usd / 50 sgd (otomatis to IDR)
    m_single = re.match(r"^([0-9\.,]+)\s*(usd|sgd|myr|eur|jpy|cny|aud|gbp|sar|thb|krw|hkd)$", text)
    if m_single:
        try:
            val = float(m_single.group(1).replace(",", ""))
            f_c = m_single.group(2).upper()
            return (val, f_c, "IDR")
        except ValueError:
            pass

    # Format 5: 500000 idr (otomatis to USD)
    m_idr = re.match(r"^([0-9\.,]+)\s*idr$", text)
    if m_idr:
        try:
            val = float(m_idr.group(1).replace(",", ""))
            return (val, "IDR", "USD")
        except ValueError:
            pass

    return None
