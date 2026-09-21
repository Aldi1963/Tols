"""
Indonesia data and document generators

Indonesian teacher verification requirements:
1. Payslip (Slip Gaji)
2. Teaching Experience Letter (Surat Keterangan Mengajar)
3. NUPTK Card (Kartu NUPTK)
4. Appointment Letter (SK Pengangkatan)
"""

from typing import Dict, List
from ..base import CountryGenerator
from ..utils import get_profile_photo, generate_initials_avatar
from PIL import Image, ImageDraw, ImageFont
from ..utils import load_font
from datetime import datetime
import random


# Indonesia Schools Database
DEFAULT_INDONESIA_SCHOOLS = [
    {"name": "SMA Negeri 3 Jakarta", "address": "Jl. Setiabudi Tengah No. 1", "city": "Jakarta Selatan", "province": "DKI Jakarta", "postcode": "12910", "phone": "021-5209516", "npsn": "20100521", "domain": "sman3jakarta.sch.id"},
    {"name": "SMA Negeri 8 Jakarta", "address": "Jl. Taman Bukit Duri No. 1", "city": "Jakarta Selatan", "province": "DKI Jakarta", "postcode": "12840", "phone": "021-8292202", "npsn": "20100538", "domain": "sman8jakarta.sch.id"},
    {"name": "SMA Negeri 5 Surabaya", "address": "Jl. Kusuma Bangsa No. 21", "city": "Surabaya", "province": "Jawa Timur", "postcode": "60272", "phone": "031-5342094", "npsn": "20532619", "domain": "sman5surabaya.sch.id"},
    {"name": "SMA Negeri 1 Yogyakarta", "address": "Jl. HOS Cokroaminoto No. 10", "city": "Yogyakarta", "province": "DI Yogyakarta", "postcode": "55224", "phone": "0274-512375", "npsn": "20403280", "domain": "sman1yogyakarta.sch.id"},
    {"name": "SMA Negeri 3 Bandung", "address": "Jl. Belitung No. 8", "city": "Bandung", "province": "Jawa Barat", "postcode": "40261", "phone": "022-4231046", "npsn": "20219151", "domain": "sman3bandung.sch.id"},
    {"name": "SMA Negeri 1 Semarang", "address": "Jl. Taman Menteri Supeno No. 1", "city": "Semarang", "province": "Jawa Tengah", "postcode": "50134", "phone": "024-3540306", "npsn": "20329797", "domain": "sman1semarang.sch.id"},
    {"name": "SMA Negeri 5 Medan", "address": "Jl. Williem Iskandar Pasar V", "city": "Medan", "province": "Sumatera Utara", "postcode": "20222", "phone": "061-6627590", "npsn": "10210752", "domain": "sman5medan.sch.id"},
    {"name": "SMA Negeri 1 Denpasar", "address": "Jl. Pucang Gading No. 5", "city": "Denpasar", "province": "Bali", "postcode": "80226", "phone": "0361-424533", "npsn": "50100116", "domain": "sman1denpasar.sch.id"},
    {"name": "SMA Negeri 3 Malang", "address": "Jl. Sultan Agung No. 7", "city": "Malang", "province": "Jawa Timur", "postcode": "65119", "phone": "0341-326454", "npsn": "20533534", "domain": "sman3malang.sch.id"},
    {"name": "SMA Negeri 2 Palembang", "address": "Jl. Jenderal Ahmad Yani", "city": "Palembang", "province": "Sumatera Selatan", "postcode": "30126", "phone": "0711-352790", "npsn": "10604558", "domain": "sman2palembang.sch.id"},
]

# Indonesia Names
INDONESIA_FIRST_NAMES = [
    "Ahmad", "Budi", "Citra", "Dewi", "Eka", "Fitri", "Gunawan", "Hadi",
    "Indra", "Joko", "Kartika", "Lestari", "Made", "Nur", "Putra", "Rina",
    "Sari", "Taufik", "Usman", "Vera", "Wati", "Yanto", "Zahra", "Agus",
    "Dian", "Fajar", "Haryo", "Ismail", "Lina", "Maya", "Ratna", "Wulan"
]

INDONESIA_LAST_NAMES = [
    "Wijaya", "Santoso", "Kusuma", "Pratama", "Hidayat", "Setiawan", "Saputra", "Rahmawati",
    "Putra", "Putri", "Susanto", "Utomo", "Lestari", "Handayani", "Wibowo", "Suryanto",
    "Nugroho", "Kurniawan", "Hermawan", "Prasetyo", "Suharto", "Rahma", "Anggraini", "Fitria",
    "Permana", "Hakim", "Subhan", "Nurdin", "Irawan", "Mahendra", "Purnama", "Safitri"
]

# Indonesia Teaching Positions
INDONESIA_TEACHING_POSITIONS = [
    "Guru Matematika",
    "Guru Bahasa Indonesia",
    "Guru Bahasa Inggris",
    "Guru Fisika",
    "Guru Kimia",
    "Guru Biologi",
    "Guru Ekonomi",
    "Guru Sejarah",
    "Guru Geografi",
    "Guru Seni Budaya",
    "Guru Pendidikan Jasmani",
    "Guru BK (Bimbingan Konseling)",
    "Wakil Kepala Sekolah",
    "Guru Mata Pelajaran",
]


class IndonesiaGenerator(CountryGenerator):
    """Indonesia-specific document generator"""
    
    # Mapping untuk nama file yang lebih jelas
    DOCUMENT_NAMES = {
        "payslip": "Slip_Gaji",
        "teaching_experience_letter": "Surat_Keterangan_Mengajar",
        "nuptk_card": "Kartu_NUPTK",
        "appointment_letter": "SK_Pengangkatan"
    }
    
    def get_country_name(self) -> str:
        return "Indonesia"
    
    def get_country_code(self) -> str:
        return "indonesia"
    
    def get_schools_data(self) -> List[Dict]:
        return DEFAULT_INDONESIA_SCHOOLS
    
    def get_first_names(self) -> List[str]:
        return INDONESIA_FIRST_NAMES
    
    def get_last_names(self) -> List[str]:
        return INDONESIA_LAST_NAMES
    
    def get_positions(self) -> List[str]:
        return INDONESIA_TEACHING_POSITIONS
    
    def get_document_types(self) -> List[str]:
        return ["payslip", "teaching_experience_letter", "nuptk_card", "appointment_letter"]
    
    def get_document_name(self, doc_type: str) -> str:
        """Get friendly Indonesian name for document type"""
        return self.DOCUMENT_NAMES.get(doc_type, doc_type)
    
    def generate_document(self, doc_type: str, first: str, last: str, 
                         school: Dict, position: str, dob: str) -> bytes:
        """Generate Indonesia document"""
        if doc_type == "payslip":
            return self._generate_payslip(first, last, school, position)
        elif doc_type == "teaching_experience_letter":
            return self._generate_teaching_experience_letter(first, last, school, position)
        elif doc_type == "nuptk_card":
            return self._generate_nuptk_card(first, last, school, position, dob)
        elif doc_type == "appointment_letter":
            return self._generate_appointment_letter(first, last, school, position)
        else:
            raise ValueError(f"Unknown document type: {doc_type}")
    
    def _generate_payslip(self, first: str, last: str, school: Dict, position: str) -> bytes:
        """Generate Slip Gaji (Payslip)"""
        w, h = 2480, 3508
        img = Image.new('RGB', (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font_title = load_font("arialbd", 56)
            font_header = load_font("arialbd", 42)
            font_normal = load_font("arial", 36)
            font_bold = load_font("arialbd", 36)
            font_small = load_font("arial", 30)
        except:
            font_title = font_header = font_normal = font_bold = font_small = ImageFont.load_default()
        
        # Red and white header (Indonesian flag colors)
        draw.rectangle([(0, 0), (w, 60)], fill=(220, 20, 60))
        draw.rectangle([(0, 60), (w, 120)], fill=(255, 255, 255))
        
        # Title
        y = 180
        draw.text((w//2, y), "SLIP GAJI PEGAWAI", fill=(220, 20, 60), font=font_title, anchor="mm")
        
        # School info box
        y = 280
        draw.rectangle([(150, y), (w-150, y+280)], fill=(250, 248, 245), outline=(220, 20, 60), width=4)
        
        y += 40
        draw.text((w//2, y), school["name"].upper(), fill=(0, 0, 0), font=font_header, anchor="mm")
        y += 55
        draw.text((w//2, y), school["address"], fill=(80, 80, 80), font=font_normal, anchor="mm")
        y += 50
        draw.text((w//2, y), f"{school['city']}, {school['province']} {school['postcode']}", 
                 fill=(80, 80, 80), font=font_normal, anchor="mm")
        y += 50
        draw.text((w//2, y), f"NPSN: {school['npsn']} | Telp: {school['phone']}", 
                 fill=(100, 100, 100), font=font_small, anchor="mm")
        
        # Period info
        y += 120
        current_month = datetime.now().strftime("%B %Y")
        slip_number = f"SG/{random.randint(1000, 9999)}/{datetime.now().strftime('%m/%Y')}"
        
        info_items = [
            ("Nomor Slip:", slip_number),
            ("Periode:", current_month),
            ("", ""),
        ]
        
        for label, value in info_items:
            if label:
                draw.text((250, y), label, fill=(100, 100, 100), font=font_bold)
                draw.text((700, y), value, fill=(0, 0, 0), font=font_normal)
                y += 60
            else:
                y += 30
        
        # Employee data
        y += 20
        draw.rectangle([(150, y), (w-150, y+60)], fill=(220, 20, 60))
        draw.text((w//2, y+30), "DATA PEGAWAI", fill=(255, 255, 255), font=font_header, anchor="mm")
        
        y += 100
        nip = f"19{random.randint(70, 99)}{random.randint(10, 12)}{random.randint(10, 28)}{random.randint(100000, 999999)}"
        
        employee_data = [
            ("Nama", f"{first} {last}"),
            ("NIP", nip),
            ("Jabatan", position),
            ("Golongan/Ruang", f"III/{chr(random.randint(97, 100))}"),
        ]
        
        for label, value in employee_data:
            draw.text((250, y), label, fill=(100, 100, 100), font=font_bold)
            draw.text((700, y), value, fill=(0, 0, 0), font=font_normal)
            y += 60
        
        # Salary details
        y += 60
        draw.rectangle([(150, y), (w-150, y+60)], fill=(220, 20, 60))
        draw.text((w//2, y+30), "RINCIAN PENGHASILAN", fill=(255, 255, 255), font=font_header, anchor="mm")
        
        y += 100
        base_salary = random.randint(4500000, 8500000)
        allowance = random.randint(1500000, 3000000)
        total = base_salary + allowance
        
        # Income section
        income_items = [
            ("Gaji Pokok", f"Rp {base_salary:,}"),
            ("Tunjangan Profesi", f"Rp {allowance:,}"),
            ("Tunjangan Kinerja", f"Rp {random.randint(500000, 1500000):,}"),
        ]
        
        for label, value in income_items:
            draw.text((250, y), label, fill=(0, 0, 0), font=font_normal)
            draw.text((w-300, y), value, fill=(0, 0, 0), font=font_normal, anchor="ra")
            y += 55
        
        # Total
        y += 30
        draw.line([(200, y), (w-200, y)], fill=(220, 20, 60), width=4)
        y += 50
        draw.text((250, y), "TOTAL PENGHASILAN BRUTO", fill=(0, 0, 0), font=font_bold)
        draw.text((w-300, y), f"Rp {total:,}", fill=(220, 20, 60), font=font_bold, anchor="ra")
        
        # Deductions
        y += 100
        draw.rectangle([(150, y), (w-150, y+60)], fill=(100, 100, 100))
        draw.text((w//2, y+30), "POTONGAN", fill=(255, 255, 255), font=font_header, anchor="mm")
        
        y += 100
        deduction_items = [
            ("Iuran Wajib Pegawai (IWP)", f"Rp {int(total * 0.045):,}"),
            ("PPh Pasal 21", f"Rp {int(total * 0.05):,}"),
        ]
        
        for label, value in deduction_items:
            draw.text((250, y), label, fill=(0, 0, 0), font=font_normal)
            draw.text((w-300, y), value, fill=(0, 0, 0), font=font_normal, anchor="ra")
            y += 55
        
        total_deduction = int(total * 0.095)
        net_salary = total - total_deduction
        
        # Net salary
        y += 30
        draw.line([(200, y), (w-200, y)], fill=(100, 100, 100), width=4)
        y += 50
        draw.text((250, y), "PENGHASILAN BERSIH", fill=(0, 0, 0), font=font_bold)
        draw.text((w-300, y), f"Rp {net_salary:,}", fill=(0, 128, 0), font=font_bold, anchor="ra")
        
        # Signature
        y = h - 550
        draw.text((w//2, y), f"{school['city']}, {datetime.now().strftime('%d %B %Y')}", 
                 fill=(80, 80, 80), font=font_normal, anchor="mm")
        
        y += 100
        draw.text((w-600, y), "Bendahara", fill=(0, 0, 0), font=font_bold, anchor="mm")
        
        y += 150
        draw.line([(w-800, y), (w-400, y)], fill=(0, 0, 0), width=2)
        y += 40
        draw.text((w-600, y), "NIP. " + nip[:18], fill=(80, 80, 80), font=font_small, anchor="mm")
        
        # Footer
        y = h - 150
        draw.line([(150, y), (w-150, y)], fill=(220, 20, 60), width=3)
        y += 40
        draw.text((w//2, y), "Dokumen ini dicetak secara otomatis dan sah tanpa tanda tangan basah", 
                 fill=(120, 120, 120), font=font_small, anchor="mm")
        
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _generate_teaching_experience_letter(self, first: str, last: str, school: Dict, position: str) -> bytes:
        """Generate Surat Keterangan Mengajar"""
        w, h = 2480, 3508
        img = Image.new('RGB', (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font_title = load_font("arialbd", 52)
            font_header = load_font("arialbd", 44)
            font_normal = load_font("arial", 36)
            font_bold = load_font("arialbd", 36)
            font_small = load_font("arial", 30)
        except:
            font_title = font_header = font_normal = font_bold = font_small = ImageFont.load_default()
        
        # Header with Indonesian colors
        draw.rectangle([(0, 0), (w, 40)], fill=(220, 20, 60))
        draw.rectangle([(0, 40), (w, 80)], fill=(255, 255, 255))
        
        # School header
        y = 140
        draw.text((w//2, y), school["name"].upper(), fill=(0, 0, 0), font=font_title, anchor="mm")
        y += 65
        draw.text((w//2, y), school["address"], fill=(80, 80, 80), font=font_normal, anchor="mm")
        y += 50
        draw.text((w//2, y), f"{school['city']}, {school['province']} {school['postcode']}", 
                 fill=(80, 80, 80), font=font_normal, anchor="mm")
        y += 45
        draw.text((w//2, y), f"Telp: {school['phone']} | NPSN: {school['npsn']}", 
                 fill=(100, 100, 100), font=font_small, anchor="mm")
        
        # Decorative line
        y += 60
        draw.rectangle([(200, y), (w-200, y+6)], fill=(220, 20, 60))
        
        # Document title
        y += 100
        draw.rectangle([(150, y), (w-150, y+100)], fill=(250, 245, 240))
        draw.text((w//2, y+50), "SURAT KETERANGAN MENGAJAR", fill=(220, 20, 60), font=font_header, anchor="mm")
        
        # Reference number
        y += 150
        ref_number = f"Nomor: {random.randint(100, 999)}/SK-Guru/{datetime.now().strftime('%m/%Y')}"
        draw.text((w//2, y), ref_number, fill=(0, 0, 0), font=font_bold, anchor="mm")
        
        # Content
        y += 120
        content_lines = [
            "Yang bertanda tangan di bawah ini Kepala Sekolah",
            f"{school['name']}, menerangkan bahwa:",
        ]
        
        for line in content_lines:
            draw.text((w//2, y), line, fill=(60, 60, 60), font=font_normal, anchor="mm")
            y += 55
        
        y += 50
        nuptk = f"{random.randint(1000, 9999)} {random.randint(7000, 7999)} {random.randint(6000, 6999)} {random.randint(1000, 9999)}"
        
        teacher_data = [
            ("Nama", f": {first} {last}"),
            ("NUPTK", f": {nuptk}"),
            ("Jabatan", f": {position}"),
            ("Masa Kerja", f": {random.randint(3, 15)} Tahun"),
            ("Status", f": Guru Tetap"),
        ]
        
        for label, value in teacher_data:
            draw.text((500, y), label, fill=(0, 0, 0), font=font_bold)
            draw.text((900, y), value, fill=(0, 0, 0), font=font_normal)
            y += 65
        
        y += 80
        cert_text = [
            "Yang bersangkutan adalah guru tetap di sekolah kami sejak tahun",
            f"{datetime.now().year - random.randint(3, 15)} dan masih aktif mengajar hingga saat ini.",
            "",
            "Demikian surat keterangan ini dibuat untuk dapat dipergunakan",
            "sebagaimana mestinya.",
        ]
        
        for line in cert_text:
            draw.text((w//2, y), line, fill=(60, 60, 60), font=font_normal, anchor="mm")
            y += 55 if line else 30
        
        # Signature
        y += 100
        draw.text((w//2, y), f"{school['city']}, {datetime.now().strftime('%d %B %Y')}", 
                 fill=(80, 80, 80), font=font_normal, anchor="mm")
        
        y += 80
        draw.text((w-600, y), "Kepala Sekolah", fill=(0, 0, 0), font=font_bold, anchor="mm")
        
        # Stamp placeholder
        stamp_x = w - 600
        stamp_y = y + 120
        draw.ellipse([(stamp_x-90, stamp_y-90), (stamp_x+90, stamp_y+90)], outline=(220, 20, 60), width=8)
        draw.text((stamp_x, stamp_y), "CAP", fill=(220, 20, 60), font=font_header, anchor="mm")
        
        y += 200
        draw.line([(w-800, y), (w-400, y)], fill=(0, 0, 0), width=3)
        y += 45
        draw.text((w-600, y), school['name'][:25], fill=(0, 0, 0), font=font_small, anchor="mm")
        y += 40
        draw.text((w-600, y), f"NIP. 19{random.randint(70, 85)}{random.randint(10,12)}{random.randint(10,28)} {random.randint(100000, 999999)} {random.randint(1, 2)} {random.randint(100, 999)}", 
                 fill=(80, 80, 80), font=font_small, anchor="mm")
        
        # Footer
        y = h - 120
        draw.line([(150, y), (w-150, y)], fill=(220, 20, 60), width=3)
        y += 45
        draw.text((w//2, y), f"Dokumen resmi {school['name']}", 
                 fill=(120, 120, 120), font=font_small, anchor="mm")
        
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _generate_nuptk_card(self, first: str, last: str, school: Dict, position: str, dob: str) -> bytes:
        """Generate Kartu NUPTK - Versi Presisi & Rapi Tanpa Tabrakan"""
        w, h = 1920, 1080
        img = Image.new('RGB', (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font_title = load_font(46, bold=True)
            font_header = load_font(34, bold=True)
            font_name = load_font(38, bold=True)
            font_label = load_font(24, bold=False)
            font_value = load_font(28, bold=True)
            font_small = load_font(20, bold=False)
            font_tiny = load_font(16, bold=False)
        except:
            font_title = font_header = font_name = font_label = font_value = font_small = font_tiny = ImageFont.load_default()
        
        # 1. Background gradient halus
        for i in range(h):
            alpha = i / h
            r = int(248 + (255 - 248) * alpha)
            g = int(250 + (255 - 250) * alpha)
            b = int(255 - 5 * alpha)
            draw.line([(0, i), (w, i)], fill=(r, g, b))
        
        # 2. Header Bendera Merah Putih Indonesia
        draw.rectangle([(0, 0), (w, 85)], fill=(205, 25, 35))
        draw.rectangle([(0, 85), (w, 105)], fill=(255, 255, 255))
        draw.line([(0, 105), (w, 105)], fill=(210, 160, 40), width=4)
        
        # Bingkai luar kartu
        draw.rectangle([(12, 12), (w-12, h-12)], outline=(205, 25, 35), width=6)
        draw.rectangle([(22, 22), (w-22, h-22)], outline=(210, 170, 50), width=2)
        
        # Header Teks Resmi
        draw.text((w//2, 45), "REPUBLIK INDONESIA", fill=(255, 255, 255), font=font_header, anchor="mm")
        draw.text((w//2, 140), "KEMENTERIAN PENDIDIKAN, KEBUDAYAAN, RISET, DAN TEKNOLOGI", fill=(30, 41, 59), font=font_label, anchor="mm")
        
        # Banner Judul Kartu NUPTK
        draw.rectangle([(80, 175), (w-80, 245)], fill=(205, 25, 35))
        draw.text((w//2, 210), "KARTU NOMOR UNIK PENDIDIK DAN TENAGA KEPENDIDIKAN", fill=(255, 255, 255), font=font_title, anchor="mm")
        
        # 3. Foto Profil Guru (Kiri)
        photo_size = (280, 360)
        photo_x, photo_y = 90, 280
        
        # Deteksi gender dari nama depan untuk mencocokkan foto
        first_lower = first.lower()
        female_clues = ['siti', 'nur', 'sri', 'dewi', 'putri', 'anisa', 'ratna', 'dian', 'rini', 'tri', 'endang', 'maya', 'fitri', 'ayu', 'wulandari']
        gender = 'Female' if any(c in first_lower for c in female_clues) else 'Male'
        
        # Frame Foto
        draw.rectangle([(photo_x-6, photo_y-6), (photo_x+photo_size[0]+6, photo_y+photo_size[1]+6)], fill=(255, 255, 255), outline=(205, 25, 35), width=4)
        photo = get_profile_photo(photo_size, person_id=f"{first}_{last}", gender=gender)
        if photo is None:
            photo = generate_initials_avatar(first, last, photo_size, bg_color=(205, 25, 35))
        img.paste(photo, (photo_x, photo_y))
        draw.rectangle([(photo_x, photo_y), (photo_x+photo_size[0], photo_y+photo_size[1])], outline=(210, 170, 50), width=2)
        
        # 4. Box NUPTK (Di samping foto)
        nuptk_box_x = 410
        nuptk_box_y = 280
        nuptk_w = w - nuptk_box_x - 90
        nuptk = f"{random.randint(1000, 9999)} {random.randint(7000, 7999)} {random.randint(6000, 6999)} {random.randint(1000, 9999)}"
        
        draw.rectangle([(nuptk_box_x, nuptk_box_y), (nuptk_box_x+nuptk_w, nuptk_box_y+85)], fill=(253, 248, 245), outline=(205, 25, 35), width=3)
        draw.rectangle([(nuptk_box_x, nuptk_box_y), (nuptk_box_x+nuptk_w, nuptk_box_y+32)], fill=(205, 25, 35))
        draw.text((nuptk_box_x + nuptk_w//2, nuptk_box_y+16), "NOMOR NUPTK NASIONAL", fill=(255, 255, 255), font=font_small, anchor="mm")
        draw.text((nuptk_box_x + nuptk_w//2, nuptk_box_y+58), nuptk, fill=(205, 25, 35), font=font_header, anchor="mm")
        
        # 5. Biodata Guru (Disusun Presisi di bawah Box NUPTK)
        # Parse DOB untuk generate NIP yang sinkron
        try:
            parts = dob.split('/')
            dob_clean = f"{int(parts[2]):04d}{int(parts[1]):02d}{int(parts[0]):02d}"
        except:
            dob_clean = "19880512"
            dob = "12/05/1988"
        
        nip_gender_code = "2" if gender == "Female" else "1"
        nip = f"{dob_clean} {random.randint(2010, 2019)}{random.randint(1, 12):02d} {nip_gender_code} {random.randint(101, 999)}"
        gender_text = "PEREMPUAN" if gender == "Female" else "LAKI-LAKI"
        
        biodata = [
            ("Nama Lengkap", f"{first} {last}".upper()),
            ("NIP / NIK", nip),
            ("Tempat, Tgl Lahir", f"{random.choice(['Jakarta', 'Bandung', 'Surabaya', 'Semarang', 'Yogyakarta', 'Medan'])}, {dob}"),
            ("Jenis Kelamin", gender_text),
            ("Satuan Pendidikan", school["name"].upper()),
            ("Status / Jabatan", f"AKTIF  •  {position.upper()}"),
        ]
        
        bio_y = 390
        for label, val in biodata:
            # Label bar (abu-abu halus)
            draw.text((nuptk_box_x, bio_y), label, fill=(100, 116, 139), font=font_label, anchor="lt")
            draw.text((nuptk_box_x + 280, bio_y), ":", fill=(71, 85, 105), font=font_label, anchor="lt")
            draw.text((nuptk_box_x + 305, bio_y - 2), val, fill=(15, 23, 42), font=font_value, anchor="lt")
            bio_y += 54
        
        # 6. Bagian Bawah: QR Code (Kiri) + Kotak Masa Berlaku (Tengah) + Stempel Dinas (Kanan)
        footer_y = 750
        
        # QR Code Simulator
        qr_x = 90
        qr_size = 180
        draw.rectangle([(qr_x, footer_y), (qr_x+qr_size, footer_y+qr_size)], fill=(255, 255, 255), outline=(15, 23, 42), width=3)
        # Inner QR Pattern
        grid_s = 10
        cell_s = qr_size // grid_s
        for r_i in range(grid_s):
            for c_i in range(grid_s):
                # Sudut khas QR
                is_corner = (r_i < 3 and c_i < 3) or (r_i < 3 and c_i >= grid_s-3) or (r_i >= grid_s-3 and c_i < 3)
                if is_corner or random.random() > 0.45:
                    draw.rectangle([(qr_x + c_i*cell_s, footer_y + r_i*cell_s), (qr_x + (c_i+1)*cell_s - 1, footer_y + (r_i+1)*cell_s - 1)], fill=(15, 23, 42))
        draw.text((qr_x + qr_size//2, footer_y + qr_size + 18), "VERIFIKASI RESMI", fill=(100, 116, 139), font=font_tiny, anchor="mm")
        
        # Kotak Masa Berlaku Kartu (Diletakkan di Tengah Tanpa Menimpa Biodata!)
        box_mb_x = 320
        box_mb_w = 700
        box_mb_h = 160
        draw.rectangle([(box_mb_x, footer_y), (box_mb_x+box_mb_w, footer_y+box_mb_h)], fill=(255, 255, 255), outline=(210, 170, 50), width=3)
        draw.rectangle([(box_mb_x, footer_y), (box_mb_x+box_mb_w, footer_y+40)], fill=(254, 243, 199))
        draw.text((box_mb_x + box_mb_w//2, footer_y + 20), "MASA BERLAKU KARTU PENDIDIK", fill=(180, 83, 9), font=font_label, anchor="mm")
        
        issue_year = datetime.now().year
        valid_start = f"01-07-{issue_year - 1}"
        valid_end = f"30-06-{issue_year + 4}"
        
        draw.text((box_mb_x + 180, footer_y + 70), "Tanggal Terbit", fill=(100, 116, 139), font=font_small, anchor="mm")
        draw.text((box_mb_x + 180, footer_y + 115), valid_start, fill=(205, 25, 35), font=font_value, anchor="mm")
        draw.line([(box_mb_x + 350, footer_y + 55), (box_mb_x + 350, footer_y + 145)], fill=(226, 232, 240), width=2)
        draw.text((box_mb_x + 520, footer_y + 70), "Berlaku Sampai", fill=(100, 116, 139), font=font_small, anchor="mm")
        draw.text((box_mb_x + 520, footer_y + 115), valid_end, fill=(205, 25, 35), font=font_value, anchor="mm")
        
        # Stempel Dinas Kemendikbudristek (Kanan Bawah)
        st_x = w - 380
        st_y = footer_y + 80
        draw.ellipse([(st_x-85, st_y-85), (st_x+85, st_y+85)], outline=(205, 25, 35), width=5)
        draw.ellipse([(st_x-70, st_y-70), (st_x+70, st_y+70)], outline=(205, 25, 35), width=2)
        draw.text((st_x, st_y - 28), "KEMENDIKBUD", fill=(205, 25, 35), font=font_small, anchor="mm")
        draw.text((st_x, st_y), "★ RISTEK ★", fill=(205, 25, 35), font=font_tiny, anchor="mm")
        draw.text((st_x, st_y + 28), "PUSDATIN", fill=(205, 25, 35), font=font_small, anchor="mm")
        
        # Legal Bar Footer
        draw.line([(50, h-45), (w-50, h-45)], fill=(226, 232, 240), width=2)
        serial_no = f"NUPTK/{dob_clean}/{random.randint(100000, 999999)}"
        draw.text((w//2, h-25), f"Dokumen Resmi Kemendikbudristek RI • Sistem Informasi Manajemen Pendidik • No. Registrasi: {serial_no}", fill=(148, 163, 184), font=font_tiny, anchor="mm")
        
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()
    
    def _generate_appointment_letter(self, first: str, last: str, school: Dict, position: str) -> bytes:
        """Generate SK Pengangkatan Guru - Standar Naskah Dinas Sempurna & Autentik"""
        w, h = 2480, 3508
        img = Image.new('RGB', (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font_kop_pemda = load_font(40, bold=True)
            font_kop_dinas = load_font(44, bold=True)
            font_school = load_font(52, bold=True)
            font_kop_sub = load_font(30, bold=False)
            font_title = load_font(42, bold=True)
            font_h1 = load_font(36, bold=True)
            font_normal = load_font(32, bold=False)
            font_bold = load_font(32, bold=True)
            font_small = load_font(26, bold=False)
            font_sig = load_font(36, bold=True)
        except:
            font_kop_pemda = font_kop_dinas = font_school = font_kop_sub = font_title = font_h1 = font_normal = font_bold = font_small = font_sig = ImageFont.load_default()
        
        # 1. KOP SURAT RESMI
        y = 130
        draw.text((w//2, y), f"PEMERINTAH PROVINSI {school.get('province', 'DKI JAKARTA').upper()}", fill=(0, 0, 0), font=font_kop_pemda, anchor="mm")
        y += 50
        draw.text((w//2, y), "DINAS PENDIDIKAN", fill=(0, 0, 0), font=font_kop_dinas, anchor="mm")
        y += 62
        draw.text((w//2, y), school["name"].upper(), fill=(0, 0, 0), font=font_school, anchor="mm")
        y += 52
        draw.text((w//2, y), school["address"] + f", {school.get('city', '')}", fill=(40, 40, 40), font=font_kop_sub, anchor="mm")
        y += 42
        draw.text((w//2, y), f"Kode Pos: {school.get('postcode', '12910')} | Telepon: {school.get('phone', '021-5209516')}", fill=(50, 50, 50), font=font_kop_sub, anchor="mm")
        y += 38
        draw.text((w//2, y), f"Laman: www.{school.get('domain', 'sekolah.sch.id')} • Pos-el: info@{school.get('domain', 'sekolah.sch.id')}", fill=(60, 60, 60), font=font_small, anchor="mm")
        
        # Garis Kop Ganda Resmi
        y += 45
        draw.line([(180, y), (w-180, y)], fill=(0, 0, 0), width=6)
        draw.line([(180, y+8), (w-180, y+8)], fill=(0, 0, 0), width=2)
        
        # 2. JUDUL KEPUTUSAN KEPALA SEKOLAH
        y += 85
        draw.text((w//2, y), "KEPUTUSAN KEPALA " + school["name"].upper(), fill=(0, 0, 0), font=font_title, anchor="mm")
        y += 50
        sk_year = datetime.now().year
        sk_no = f"Nomor : {random.randint(101, 899)} / 421.3 / SK-Guru / {sk_year}"
        draw.text((w//2, y), sk_no, fill=(0, 0, 0), font=font_bold, anchor="mm")
        
        y += 60
        draw.text((w//2, y), "TENTANG", fill=(0, 0, 0), font=font_h1, anchor="mm")
        y += 50
        draw.text((w//2, y), f"PENGANGKATAN GURU TETAP ({position.upper()})", fill=(0, 0, 0), font=font_h1, anchor="mm")
        y += 50
        draw.text((w//2, y), "PADA " + school["name"].upper(), fill=(0, 0, 0), font=font_h1, anchor="mm")
        
        y += 75
        draw.text((w//2, y), "KEPALA " + school["name"].upper() + ",", fill=(0, 0, 0), font=font_h1, anchor="mm")
        
        # 3. KONSIDERANS TABULAR DENGAN INDENTASI PRESISI
        left = 220
        col_colon = left + 200
        col_item = left + 240
        col_text = left + 280
        
        y += 80
        # Menimbang
        draw.text((left, y), "Menimbang", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_colon, y), ":", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_item, y), "a.", fill=(0, 0, 0), font=font_normal, anchor="lt")
        draw.text((col_text, y), f"bahwa untuk kelancaran proses pembelajaran pada {school['name']},", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 42
        draw.text((col_text, y), "dipandang perlu mengangkat tenaga pendidik yang berkualitas;", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 50
        draw.text((col_item, y), "b.", fill=(0, 0, 0), font=font_normal, anchor="lt")
        draw.text((col_text, y), f"bahwa Saudara/i {first} {last} dipandang memenuhi syarat untuk diangkat", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 42
        draw.text((col_text, y), f"sebagai {position} pada {school['name']};", fill=(0, 0, 0), font=font_normal, anchor="lt")
        
        # Mengingat
        y += 65
        draw.text((left, y), "Mengingat", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_colon, y), ":", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_item, y), "1.", fill=(0, 0, 0), font=font_normal, anchor="lt")
        draw.text((col_text, y), "Undang-Undang Nomor 20 Tahun 2003 tentang Sistem Pendidikan Nasional;", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 44
        draw.text((col_item, y), "2.", fill=(0, 0, 0), font=font_normal, anchor="lt")
        draw.text((col_text, y), "Undang-Undang Nomor 14 Tahun 2005 tentang Guru dan Dosen;", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 44
        draw.text((col_item, y), "3.", fill=(0, 0, 0), font=font_normal, anchor="lt")
        draw.text((col_text, y), "Peraturan Pemerintah Nomor 74 Tahun 2008 tentang Guru;", fill=(0, 0, 0), font=font_normal, anchor="lt")
        
        # 4. MEMUTUSKAN & MENETAPKAN
        y += 80
        draw.text((w//2, y), "MEMUTUSKAN:", fill=(0, 0, 0), font=font_h1, anchor="mm")
        y += 60
        draw.text((left, y), "Menetapkan", fill=(0, 0, 0), font=font_bold, anchor="lt"); draw.text((col_colon, y), ":", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_colon, y), ":", fill=(0, 0, 0), font=font_bold, anchor="lt")
        
        y += 55
        # KESATU
        draw.text((left, y), "KESATU", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_colon, y), ":", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_item, y), "Mengangkat terhitung mulai tanggal 01 Juli " + str(sk_year - random.randint(1, 4)) + " kepada:", fill=(0, 0, 0), font=font_normal, anchor="lt")
        
        y += 50
        draw.text((col_item + 40, y), "Nama Lengkap", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_item + 380, y), f": {first} {last}", fill=(0, 0, 0), font=font_bold, anchor="lt")
        y += 44
        draw.text((col_item + 40, y), "Jabatan Tugas", fill=(0, 0, 0), font=font_normal, anchor="lt")
        draw.text((col_item + 380, y), f": {position}", fill=(0, 0, 0), font=font_bold, anchor="lt")
        y += 44
        draw.text((col_item + 40, y), "Unit Kerja", fill=(0, 0, 0), font=font_normal, anchor="lt")
        draw.text((col_item + 380, y), f": {school['name']}", fill=(0, 0, 0), font=font_normal, anchor="lt")
        
        # KEDUA
        y += 60
        draw.text((left, y), "KEDUA", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_colon, y), ":", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_item, y), "Kepada yang bersangkutan diberikan hak gaji dan tunjangan kerja sesuai", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 40
        draw.text((col_item, y), "dengan ketentuan dan peraturan perundang-undangan yang berlaku.", fill=(0, 0, 0), font=font_normal, anchor="lt")
        
        # KETIGA
        y += 55
        draw.text((left, y), "KETIGA", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_colon, y), ":", fill=(0, 0, 0), font=font_bold, anchor="lt")
        draw.text((col_item, y), "Surat Keputusan ini berlaku sejak tanggal ditetapkan, dan apabila terdapat", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 40
        draw.text((col_item, y), "kekeliruan akan diadakan perbaikan sebagaimana mestinya.", fill=(0, 0, 0), font=font_normal, anchor="lt")
        
        # 5. TANDA TANGAN RESMI + STEMPEL BULAT TIDAK TERPOTONG (KANAN BAWAH)
        y = h - 680
        ttd_x = w - 850
        draw.text((ttd_x, y), f"Ditetapkan di : {school.get('city', 'Jakarta')}", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 42
        draw.text((ttd_x, y), f"Pada tanggal  : {datetime.now().strftime('%d %B %Y')}", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 55
        draw.text((ttd_x, y), "Kepala " + school["name"] + ",", fill=(0, 0, 0), font=font_bold, anchor="lt")
        
        # Pejabat Kepala Sekolah (Dipilih yang namanya berbeda dengan guru yang diangkat)
        all_kepsek = ["Dr. H. Bambang Sugiarto, M.Pd.", "Dra. Hj. Sri Wahyuni, M.M.", "Drs. H. Mulyadi, M.Pd.", "Drs. Eko Prasetyo, M.Pd.", "Dr. Hendra Gunawan, S.Pd., M.Si."]
        valid_kepsek = [k for k in all_kepsek if first.lower() not in k.lower()]
        kepsek_name = random.choice(valid_kepsek if valid_kepsek else all_kepsek)
        kepsek_nip = f"19{random.randint(68, 79)}{random.randint(1, 12):02d}{random.randint(1, 28):02d} {random.randint(1992, 2003)}{random.randint(1, 12):02d} 1 {random.randint(101, 999)}"
        
        # Goresan Tanda Tangan Basah Biru Tua Otentik (Realistic Signature Stroke)
        sig_base_x = ttd_x + 60
        sig_base_y = y + 130
        pen_color = (24, 43, 115) # Tinta pulpen basah biru tua resmi
        
        # Stroke tanda tangan dinamis
        draw.arc([sig_base_x, sig_base_y - 45, sig_base_x + 140, sig_base_y + 45], start=160, end=380, fill=pen_color, width=4)
        draw.line([(sig_base_x + 30, sig_base_y + 35), (sig_base_x + 90, sig_base_y - 65)], fill=pen_color, width=4)
        draw.line([(sig_base_x + 90, sig_base_y - 65), (sig_base_x + 120, sig_base_y + 25)], fill=pen_color, width=4)
        draw.arc([sig_base_x + 110, sig_base_y - 20, sig_base_x + 220, sig_base_y + 35], start=20, end=260, fill=pen_color, width=4)
        draw.line([(sig_base_x + 180, sig_base_y + 10), (sig_base_x + 340, sig_base_y - 15)], fill=pen_color, width=5)
        draw.line([(sig_base_x + 310, sig_base_y - 10), (sig_base_x + 380, sig_base_y + 15)], fill=pen_color, width=3)
        
        # Stempel Resmi Sekolah Berwarna Merah (Proporsional & Teks Lengkap)
        st_x = ttd_x + 120
        st_y = y + 130
        draw.ellipse([(st_x-115, st_y-115), (st_x+115, st_y+115)], outline=(205, 25, 35), width=6)
        draw.ellipse([(st_x-100, st_y-100), (st_x+100, st_y+100)], outline=(205, 25, 35), width=2)
        draw.text((st_x, st_y - 45), "DINAS PENDIDIKAN", fill=(205, 25, 35), font=font_small, anchor="mm")
        draw.text((st_x, st_y), "★ KEPALA SEKOLAH ★", fill=(205, 25, 35), font=font_small, anchor="mm")
        
        # Nama sekolah diringkas rapi agar tidak terpotong
        sch_stamp = school["name"].upper()
        if len(sch_stamp) > 22:
            sch_stamp = sch_stamp[:22]
        draw.text((st_x, st_y + 45), sch_stamp, fill=(205, 25, 35), font=font_small, anchor="mm")
        
        y += 240
        draw.text((ttd_x, y), kepsek_name, fill=(0, 0, 0), font=font_sig, anchor="lt")
        y += 45
        draw.line([(ttd_x, y), (ttd_x + 550, y)], fill=(0, 0, 0), width=3)
        y += 12
        draw.text((ttd_x, y), f"NIP. {kepsek_nip}", fill=(0, 0, 0), font=font_normal, anchor="lt")
        y += 42
        draw.text((ttd_x, y), "Pangkat/Gol: Pembina Utama Muda, IV/c", fill=(50, 50, 50), font=font_small, anchor="lt")
        
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()