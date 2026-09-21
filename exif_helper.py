"""
EXIF Metadata Injector
Menyuntikkan metadata EXIF kamera nyata (Apple iPhone 14 Pro / Samsung Galaxy S23 Ultra)
ke dalam berkas JPEG sehingga terbaca sebagai foto jepretan kamera asli oleh sistem verifikasi SheerID, Persona, dll.
"""

from io import BytesIO
from datetime import datetime
from PIL import Image
import random
import piexif

CAMERA_PROFILES = [
    {
        "make": "Apple",
        "model": "iPhone 14 Pro",
        "software": "17.5.1",
        "lens_model": "iPhone 14 Pro back triple camera 6.86mm f/1.78",
        "focal_length": (686, 100),
        "f_number": (178, 100),
        "iso": 80,
    },
    {
        "make": "Apple",
        "model": "iPhone 15",
        "software": "17.6",
        "lens_model": "iPhone 15 back dual camera 5.96mm f/1.6",
        "focal_length": (596, 100),
        "f_number": (160, 100),
        "iso": 100,
    },
    {
        "make": "Samsung",
        "model": "SM-S918B",  # Galaxy S23 Ultra
        "software": "S918BXXU3BWJM",
        "lens_model": "Samsung S23 Ultra 6.3mm f/1.7",
        "focal_length": (630, 100),
        "f_number": (170, 100),
        "iso": 125,
    }
]

def inject_camera_exif(image_bytes: bytes, quality: int = 96) -> bytes:
    """
    Mengubah gambar ke JPEG dan menyuntikkan metadata EXIF kamera profesional
    """
    try:
        im = Image.open(BytesIO(image_bytes)).convert("RGB")
        cam = random.choice(CAMERA_PROFILES)
        now = datetime.now()
        dt_str = now.strftime("%Y:%m:%d %H:%M:%S")

        zeroth_ifd = {
            piexif.ImageIFD.Make: cam["make"],
            piexif.ImageIFD.Model: cam["model"],
            piexif.ImageIFD.Software: cam["software"],
            piexif.ImageIFD.DateTime: dt_str,
            piexif.ImageIFD.Orientation: 1,
            piexif.ImageIFD.XResolution: (300, 1),
            piexif.ImageIFD.YResolution: (300, 1),
            piexif.ImageIFD.ResolutionUnit: 2,
        }

        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: dt_str,
            piexif.ExifIFD.DateTimeDigitized: dt_str,
            piexif.ExifIFD.ExposureTime: (1, random.choice([60, 100, 125, 200])),
            piexif.ExifIFD.FNumber: cam["f_number"],
            piexif.ExifIFD.ISOSpeedRatings: cam["iso"],
            piexif.ExifIFD.FocalLength: cam["focal_length"],
            piexif.ExifIFD.LensModel: cam["lens_model"],
            piexif.ExifIFD.Flash: 0,
            piexif.ExifIFD.ColorSpace: 1,
            piexif.ExifIFD.ExposureProgram: 2,
            piexif.ExifIFD.MeteringMode: 5,
        }

        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": {}, "1st": {}, "thumbnail": None}
        exif_bytes = piexif.dump(exif_dict)

        out_buf = BytesIO()
        im.save(out_buf, format="JPEG", quality=quality, exif=exif_bytes)
        return out_buf.getvalue()
    except Exception as e:
        # Fallback jika gagal suntik exif: kembalikan original
        return image_bytes

def convert_to_pdf(image_bytes: bytes, filename: str = "document.pdf") -> bytes:
    """Mengonversi gambar menjadi dokumen PDF resolusi penuh siap kirim"""
    im = Image.open(BytesIO(image_bytes)).convert("RGB")
    pdf_buf = BytesIO()
    im.save(pdf_buf, format="PDF", resolution=300.0)
    return pdf_buf.getvalue()
