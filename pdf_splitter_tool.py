import io
from pypdf import PdfReader, PdfWriter
from typing import List, Tuple, Union

def parse_page_range(range_str: str, max_pages: int) -> List[int]:
    """
    Mengurai format halaman seperti '1-3, 5, 8-10' menjadi daftar index 0-based.
    """
    pages_to_extract = set()
    parts = range_str.replace(" ", "").split(",")

    for p in parts:
        if not p:
            continue
        if "-" in p:
            sub = p.split("-")
            try:
                start = int(sub[0])
                end = int(sub[1])
                # Clamp ke batas halaman
                start = max(1, min(start, max_pages))
                end = max(1, min(end, max_pages))
                if start <= end:
                    for i in range(start, end + 1):
                        pages_to_extract.add(i - 1)
                else:
                    for i in range(end, start + 1):
                        pages_to_extract.add(i - 1)
            except ValueError:
                pass
        else:
            try:
                num = int(p)
                if 1 <= num <= max_pages:
                    pages_to_extract.add(num - 1)
            except ValueError:
                pass

    return sorted(list(pages_to_extract))

def split_pdf_pages(pdf_bytes: bytes, page_query: str) -> Tuple[bool, Union[bytes, str], int]:
    """
    Memecah dan mengambil halaman tertentu dari PDF.
    Mengembalikan: (status_sukses, pdf_bytes_atau_error_msg, total_halaman_diekstrak)
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        if total_pages == 0:
            return False, "File PDF tidak memiliki halaman.", 0

        target_indices = parse_page_range(page_query, total_pages)
        if not target_indices:
            return False, f"Halaman tidak valid. Dokumen ini memiliki {total_pages} halaman (Contoh format: 1-3 atau 1, 4, 7).", 0

        writer = PdfWriter()
        for idx in target_indices:
            writer.add_page(reader.pages[idx])

        out_io = io.BytesIO()
        writer.write(out_io)
        out_bytes = out_io.getvalue()
        return True, out_bytes, len(target_indices)

    except Exception as e:
        return False, f"Terjadi kesalahan saat memproses PDF: {e}", 0
