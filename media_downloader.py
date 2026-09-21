import os
import tempfile
import yt_dlp
import re
import urllib.request
import json
import subprocess

def is_supported_url(url: str) -> bool:
    patterns = [
        r'(https?://(?:www\.|vm\.|vt\.)?tiktok\.com/[^\s]+)',
        r'(https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[^\s]+)',
        r'(https?://(?:www\.|fb\.|web\.|m\.)?facebook\.com/[^\s]+)',
        r'(https?://(?:www\.)?fb\.watch/[^\s]+)',
        r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[^\s]+)',
        r'(https?://(?:www\.)?(?:twitter\.com|x\.com)/[^\s]+/status/[^\s]+)',
    ]
    return any(re.search(p, url, re.IGNORECASE) for p in patterns)

def extract_url_from_text(text: str) -> str:
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else None

def get_media_info(url: str) -> dict:
    """
    Mengambil informasi pratinjau media (Judul, Thumbnail, Durasi, Platform, dan Tipe Konten)
    secara instan tanpa mengunduh seluruh berkas video terlebih dahulu.
    """
    url_lower = url.lower()

    # 1. TikTok via TikWM API (Sangat cepat ~1 detik)
    if 'tiktok.com' in url_lower:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        req = urllib.request.Request(
            "https://www.tikwm.com/api/",
            data=f"url={url}".encode('utf-8'),
            headers=headers
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            if data.get('code') == 0:
                v = data.get('data', {})
                title = v.get('title') or "TikTok Media"
                is_images = bool(v.get('images'))
                return {
                    'url': url,
                    'platform': 'TikTok',
                    'title': title,
                    'duration': int(v.get('duration') or 0),
                    'thumbnail': v.get('cover') or '',
                    'is_slideshow': is_images,
                    'images_count': len(v.get('images') or []),
                    'has_music': bool(v.get('music')),
                    'author': v.get('author', {}).get('nickname', ''),
                    'tikwm_data': v
                }
        except Exception:
            pass

    # 2. Instagram, Facebook, YouTube, Twitter via yt-dlp metadata
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'socket_timeout': 15,
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        platform = 'YouTube' if 'youtu' in url_lower else ('Instagram' if 'instagram' in url_lower else ('Facebook' if 'fb' in url_lower or 'facebook' in url_lower else 'Twitter/X'))
        return {
            'url': url,
            'platform': platform,
            'title': info.get('title') or f"{platform} Video",
            'duration': int(info.get('duration') or 0),
            'thumbnail': info.get('thumbnail') or '',
            'is_slideshow': False,
            'images_count': 0,
            'has_music': True,
            'author': info.get('uploader') or '',
            'tikwm_data': None
        }

def download_media_custom(url: str, mode: str = "video_hd", tikwm_cache: dict = None) -> dict:
    """
    Mengunduh media sesuai pilihan pengguna:
    - 'video_hd': Video kualitas tertinggi tanpa watermark
    - 'video_sd': Video hemat kuota (480p)
    - 'audio': Musik / Sound saja (MP3)
    - 'thumbnail': Gambar sampul cover video
    - 'slideshow': Mengunduh seluruh slide foto TikTok
    """
    url_lower = url.lower()

    # --- JIKA TIKTOK ---
    if 'tiktok.com' in url_lower:
        v_data = tikwm_cache
        if not v_data:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            req = urllib.request.Request(
                "https://www.tikwm.com/api/",
                data=f"url={url}".encode('utf-8'),
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                d = json.loads(resp.read().decode('utf-8'))
                v_data = d.get('data', {})

        title = v_data.get('title') or "TikTok Content"
        clean_title = re.sub(r'[\\/*?:"<>|]', '', title)[:50]

        headers_dl = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        # A. Mode Audio MP3
        if mode == "audio":
            music_url = v_data.get('music')
            if not music_url:
                raise RuntimeError("Audio musik tidak ditemukan pada postingan ini.")
            req = urllib.request.Request(music_url, headers=headers_dl)
            with urllib.request.urlopen(req, timeout=30) as resp:
                audio_bytes = resp.read()
            return {
                'type': 'audio',
                'data': audio_bytes,
                'filename': f"TikTok_Audio_{clean_title}.mp3",
                'title': title,
                'performer': v_data.get('music_info', {}).get('author') or 'TikTok Sound',
                'duration': int(v_data.get('duration') or 0),
            }

        # B. Mode Thumbnail / Cover
        if mode == "thumbnail":
            cov_url = v_data.get('origin_cover') or v_data.get('cover')
            if not cov_url:
                raise RuntimeError("Cover tidak ditemukan.")
            req = urllib.request.Request(cov_url, headers=headers_dl)
            with urllib.request.urlopen(req, timeout=20) as resp:
                img_bytes = resp.read()
            return {
                'type': 'image',
                'data': img_bytes,
                'filename': f"Cover_{clean_title}.jpg",
                'title': title
            }

        # C. Mode Slideshow Foto
        if mode == "slideshow" or (v_data.get('images') and mode != "audio"):
            images = v_data.get('images', [])
            downloaded_imgs = []
            for idx, img_url in enumerate(images):
                req = urllib.request.Request(img_url, headers=headers_dl)
                with urllib.request.urlopen(req, timeout=20) as resp:
                    downloaded_imgs.append(resp.read())
            return {
                'type': 'slideshow',
                'images': downloaded_imgs,
                'title': title,
                'music_url': v_data.get('music')
            }

        # D. Mode Video HD / SD
        play_url = v_data.get('hdplay') if (mode == "video_hd" and v_data.get('hdplay')) else v_data.get('play')
        if not play_url:
            play_url = v_data.get('play') or v_data.get('wmplay')

        req = urllib.request.Request(play_url, headers=headers_dl)
        with urllib.request.urlopen(req, timeout=60) as resp:
            video_bytes = resp.read()

        size_mb = len(video_bytes) / (1024 * 1024)
        if size_mb > 49.5:
            raise RuntimeError(f"Ukuran video ({size_mb:.1f} MB) melampaui batas upload bot Telegram 50 MB.")

        return {
            'type': 'video',
            'data': video_bytes,
            'filename': f"TikTok_{clean_title}.mp4",
            'title': title,
            'duration': int(v_data.get('duration') or 0),
            'filesize_mb': size_mb,
            'platform': 'TikTok'
        }

    # --- JIKA INSTAGRAM / YOUTUBE / FACEBOOK / TWITTER ---
    with tempfile.TemporaryDirectory() as tmpdir:
        out_tmpl = os.path.join(tmpdir, "%(id)s.%(ext)s")

        if mode == "audio":
            ydl_opts = {
                'outtmpl': out_tmpl,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
            }
        elif mode == "video_sd":
            ydl_opts = {
                'outtmpl': out_tmpl,
                'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
            }
        else: # video_hd
            ydl_opts = {
                'outtmpl': out_tmpl,
                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Media')
            clean_title = re.sub(r'[\\/*?:"<>|]', '', title)[:50]
            duration = int(info.get('duration') or 0)

            # Cari file hasil download
            found_file = None
            for fname in os.listdir(tmpdir):
                target_ext = '.mp3' if mode == 'audio' else '.mp4'
                if fname.endswith(target_ext) or fname.endswith('.mkv') or fname.endswith('.webm'):
                    found_file = os.path.join(tmpdir, fname)
                    break

            if not found_file or not os.path.exists(found_file):
                raise RuntimeError("Gagal memproses berkas media.")

            size_mb = os.path.getsize(found_file) / (1024 * 1024)
            if size_mb > 49.5:
                raise RuntimeError(f"Ukuran berkas ({size_mb:.1f} MB) melampaui batas kirim Telegram 50 MB.")

            with open(found_file, 'rb') as f:
                res_bytes = f.read()

            if mode == "audio":
                return {
                    'type': 'audio',
                    'data': res_bytes,
                    'filename': f"{clean_title}.mp3",
                    'title': title,
                    'performer': info.get('uploader') or 'Media Audio',
                    'duration': duration,
                }
            else:
                return {
                    'type': 'video',
                    'data': res_bytes,
                    'filename': f"{clean_title}.mp4",
                    'title': title,
                    'duration': duration,
                    'filesize_mb': size_mb,
                    'platform': 'Media'
                }

print("Interactive media_downloader.py verified!")
