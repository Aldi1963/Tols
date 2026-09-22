import re
from typing import List, Tuple

def parse_contacts_text(raw_text: str) -> List[Tuple[str, str]]:
    """
    Mengurai daftar nama & nomor HP dari teks bebas.
    Mendukung format:
    - Budi: 08123456789
    - 08123456789 Budi
    - Budi - 08123456789
    - Budi, 08123456789
    - Hanya nomor HP satu per satu
    """
    contacts = []
    lines = raw_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Cari pola nomor HP (dimulai dengan 08, 62, +62)
        match = re.search(r"(\+?62[\d\-\s]{8,15}|08[\d\-\s]{8,13})", line)
        if match:
            phone_raw = match.group(1)
            # Bersihkan spasi dan tanda hubung dari nomor HP
            phone_clean = re.sub(r"[\-\s]", "", phone_raw)
            if phone_clean.startswith("08"):
                phone_clean = "+628" + phone_clean[2:]
            elif phone_clean.startswith("62"):
                phone_clean = "+" + phone_clean

            # Ambil sisa teks sebagai nama
            name_part = line.replace(match.group(0), "").strip()
            name_clean = re.sub(r"^[\s\-:,\.]+|[\s\-:,\.]+$", "", name_part)

            if not name_clean:
                name_clean = f"Kontak {len(contacts) + 1}"

            contacts.append((name_clean, phone_clean))

    return contacts

def generate_vcf_file(contacts: List[Tuple[str, str]]) -> bytes:
    """
    Menghasilkan berkas vCard (.vcf) standar vCard 3.0 yang kompatibel 100%
    dengan Google Contacts, Android, dan Apple iOS / iPhone.
    """
    vcf_lines = []
    for name, phone in contacts:
        vcf_lines.append("BEGIN:VCARD")
        vcf_lines.append("VERSION:3.0")
        vcf_lines.append(f"FN:{name}")
        vcf_lines.append(f"N:{name};;;;")
        vcf_lines.append(f"TEL;TYPE=CELL:{phone}")
        vcf_lines.append("END:VCARD")

    return "\n".join(vcf_lines).encode("utf-8")
