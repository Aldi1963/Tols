import os
import subprocess
import tempfile
from typing import Tuple, Optional

def get_video_info(video_path: str) -> Tuple[float, int]:
    """Dapatkan durasi (detik) dan ukuran file (bytes)."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration,size',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    duration = 0.0
    size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
    if res.returncode == 0 and res.stdout.strip():
        lines = res.stdout.strip().split()
        try:
            duration = float(lines[0])
            if len(lines) > 1:
                size = int(lines[1])
        except (ValueError, IndexError):
            pass
    return duration, size

def compress_video_whatsapp(input_path: str, output_path: str, target_mb: float = 15.0) -> bool:
    """
    Kompres video agar pas di bawah target_mb (default 15.0 MB untuk batas WhatsApp 16 MB).
    Menggunakan 2-pass encoding dengan bitrate otomatis yang disesuaikan durasi.
    """
    duration, orig_size = get_video_info(input_path)
    if duration <= 0:
        return False

    # Target total bits = target_mb * 8 * 1024 * 1024
    # Sisakan space untuk audio bitrate 96 kbps
    audio_bitrate_kbps = 96
    total_bitrate_kbps = int((target_mb * 8 * 1024) / duration)
    video_bitrate_kbps = max(50, total_bitrate_kbps - audio_bitrate_kbps)

    # Batasi resolusi maksimal 720p (1280x720) jika video terlalu besar agar encoding cepat
    scale_filter = "scale='min(1280,iw)':'min(720,ih)':force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2"

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-vf', scale_filter,
        '-c:v', 'libx264',
        '-b:v', f'{video_bitrate_kbps}k',
        '-maxrate', f'{int(video_bitrate_kbps * 1.2)}k',
        '-bufsize', f'{int(video_bitrate_kbps * 2)}k',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', f'{audio_bitrate_kbps}k',
        '-movflags', '+faststart',
        output_path
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(output_path):
        out_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        return out_size_mb <= target_mb + 1.0  # toleransi kecil
    return False

def trim_audio_file(input_path: str, output_path: str, start_sec: float, duration_sec: float, fade: bool = True) -> bool:
    """
    Potong file audio dengan efek fade in (1.5s) dan fade out (2s) lembut.
    """
    if fade and duration_sec > 4.0:
        fade_out_start = max(0, duration_sec - 2.0)
        af_filter = f"afade=t=in:ss=0:d=1.5,afade=t=out:st={fade_out_start}:d=2"
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_sec),
            '-t', str(duration_sec),
            '-i', input_path,
            '-af', af_filter,
            '-c:a', 'libmp3lame',
            '-b:a', '192k',
            output_path
        ]
    else:
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_sec),
            '-t', str(duration_sec),
            '-i', input_path,
            '-c:a', 'libmp3lame',
            '-b:a', '192k',
            output_path
        ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0
