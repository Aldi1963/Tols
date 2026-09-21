import os
import re
import math
import subprocess
import tempfile
from typing import Optional, Dict, Any, List

def parse_time_to_seconds(t_str: str) -> Optional[float]:
    """Parse string waktu seperti '01:30', '1:30', '90', '00:01:30' ke detik."""
    t_str = t_str.strip().replace('：', ':').replace('.', ':')
    parts = t_str.split(':')
    try:
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    except ValueError:
        return None
    return None

def format_seconds_to_time(secs: float) -> str:
    """Format detik ke format MM:SS atau HH:MM:SS."""
    secs = int(secs)
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def get_video_duration(video_path: str) -> float:
    """Dapatkan durasi video dalam detik menggunakan ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        try:
            return float(res.stdout.strip())
        except ValueError:
            pass
    return 0.0

def clip_video_segment(
    input_path: str,
    output_path: str,
    start_sec: float,
    duration_sec: float,
    to_vertical: bool = True,
    vertical_style: str = "blur"  # "blur" atau "crop"
) -> bool:
    """
    Potong klip video dari start_sec sepanjang duration_sec.
    Menggunakan preset ultrafast agar cepat dan responsif.
    """
    if to_vertical:
        if vertical_style == "crop":
            # Center crop ke 9:16
            filter_complex = "crop=ih*9/16:ih:(iw-ow)/2:0,scale=720:1280"
        else:
            # Blur background mode: 720x1280 (HD vertikal standar TikTok/Reels hemat kuota & super cepat)
            filter_complex = (
                "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=20:5[bg];"
                "[0:v]scale=720:-2:force_original_aspect_ratio=decrease[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2"
            )
        
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_sec),
            '-t', str(duration_sec),
            '-i', input_path,
            '-filter_complex', filter_complex,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '24',
            '-c:a', 'aac', '-b:a', '128k',
            output_path
        ]
    else:
        # Potong langsung cepat
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_sec),
            '-t', str(duration_sec),
            '-i', input_path,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '24',
            '-c:a', 'aac', '-b:a', '128k',
            output_path
        ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0

def auto_split_video(
    input_path: str,
    output_dir: str,
    segment_length: float = 60.0,
    max_segments: int = 5,
    to_vertical: bool = True
) -> List[Dict[str, Any]]:
    """
    Otomatis memotong video panjang menjadi beberapa bagian (Part 1, Part 2, dll).
    Maksimal max_segments agar tidak membebani Telegram upload.
    """
    total_duration = get_video_duration(input_path)
    if total_duration <= 0:
        return []

    num_segments = min(int(math.ceil(total_duration / segment_length)), max_segments)
    results = []

    for i in range(num_segments):
        start = i * segment_length
        dur = min(segment_length, total_duration - start)
        if dur <= 3.0:
            break
        
        part_no = i + 1
        out_filename = f"clip_part_{part_no:02d}.mp4"
        out_path = os.path.join(output_dir, out_filename)
        
        ok = clip_video_segment(
            input_path=input_path,
            output_path=out_path,
            start_sec=start,
            duration_sec=dur,
            to_vertical=to_vertical,
            vertical_style="blur"
        )
        if ok:
            results.append({
                "part": part_no,
                "path": out_path,
                "start": start,
                "duration": dur,
                "time_str": f"{format_seconds_to_time(start)} - {format_seconds_to_time(start + dur)}"
            })

    return results
