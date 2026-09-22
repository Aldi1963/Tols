from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import math
import random
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
WOOD_ASSET_PATH = BASE_DIR / "countries" / "assets" / "wood_table_master.jpg"

def find_perspective_coeffs(source_pts, target_pts):
    matrix = []
    for p_dst, p_src in zip(target_pts, source_pts):
        matrix.append([p_dst[0], p_dst[1], 1, 0, 0, 0, -p_src[0]*p_dst[0], -p_src[0]*p_dst[1]])
        matrix.append([0, 0, 0, p_dst[0], p_dst[1], 1, -p_src[1]*p_dst[0], -p_src[1]*p_dst[1]])

    B = []
    for p in source_pts:
        B.extend([p[0], p[1]])

    n = 8
    A = matrix
    for i in range(n):
        max_row = i
        for k in range(i + 1, n):
            if abs(A[k][i]) > abs(A[max_row][i]):
                max_row = k
        A[i], A[max_row] = A[max_row], A[i]
        B[i], B[max_row] = B[max_row], B[i]

        pivot = A[i][i]
        if abs(pivot) < 1e-12:
            return None
        for j in range(i, n):
            A[i][j] /= pivot
        B[i] /= pivot

        for r in range(n):
            if r != i:
                factor = A[r][i]
                for c in range(i, n):
                    A[r][c] -= factor * A[i][c]
                B[r] -= factor * B[i]

    return B

def load_flawless_wood_desk(width=2048, height=1365) -> Image.Image:
    if WOOD_ASSET_PATH.exists():
        try:
            w_img = Image.open(WOOD_ASSET_PATH).convert("RGB")
            cur_w, cur_h = w_img.size
            scale = max(width / cur_w, height / cur_h) * 1.35
            new_w, new_h = int(cur_w * scale), int(cur_h * scale)
            w_resized = w_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            w_rot = w_resized.rotate(8, resample=Image.Resampling.BICUBIC, expand=False)
            cx, cy = new_w // 2, new_h // 2
            x0 = cx - width // 2
            y0 = cy - height // 2
            table = w_rot.crop((x0, y0, x0 + width, y0 + height))

            table = table.filter(ImageFilter.GaussianBlur(radius=0.7))
            table = ImageEnhance.Color(table).enhance(1.18)
            table = ImageEnhance.Contrast(table).enhance(1.08)

            # Pencahayaan hangat jendela
            lighting = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            l_draw = ImageDraw.Draw(lighting)
            l_draw.ellipse([(-width * 0.1, -height * 0.2), (width * 0.95, height * 0.85)], fill=(255, 245, 225, 75))
            lighting = lighting.filter(ImageFilter.GaussianBlur(radius=90))

            vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            v_draw = ImageDraw.Draw(vignette)
            for r in range(width, int(width * 0.35), -50):
                alpha = int((1.0 - r / width) * 75)
                v_draw.ellipse([(width - r, height - int(r * 0.7)), (width + r, height + int(r * 0.7))], fill=(10, 6, 3, alpha))
            vignette = vignette.filter(ImageFilter.GaussianBlur(radius=60))

            t_rgba = table.convert("RGBA")
            t_rgba = Image.alpha_composite(t_rgba, lighting)
            t_rgba = Image.alpha_composite(t_rgba, vignette)
            return t_rgba.convert("RGB")
        except Exception as e:
            print(f"Fallback wood: {e}")

    return Image.new("RGB", (width, height), (125, 82, 54))

def render_card_on_desk(card_image_bytes: bytes) -> bytes:
    """
    FOTO FISIK ASLI KARTU DI ATAS MEJA KAYU (Ultra Photorealistic with Ambient Color Bounce):
    1. Ambient Light Bounce dari meja kayu cokelat ke kartu (Color Bleed Integration)
    2. Zero black edges pada kanvas
    3. Sudut rounded PVC bersih 32px
    4. Oklusi kontak pekat menempel erat di serat meja
    """
    card_raw = Image.open(BytesIO(card_image_bytes)).convert("RGBA")
    cw, ch = card_raw.size

    # Ambient Light Bounce: Cahaya hangat kayu memantul lembut ke dasar kartu (Warm Teak Bounce)
    bounce_layer = Image.new("RGBA", (cw, ch), (145, 95, 55, 0))
    b_draw = ImageDraw.Draw(bounce_layer)
    # Gradasi pantulan dari bawah ke atas kartu
    for y in range(int(ch * 0.5), ch, 4):
        f = (y - ch * 0.5) / (ch * 0.5)
        op = int(f * 32)
        b_draw.line([(0, y), (cw, y)], fill=(155, 105, 60, op))
    bounce_layer = bounce_layer.filter(ImageFilter.GaussianBlur(radius=15))
    card_integrated = Image.alpha_composite(card_raw, bounce_layer)

    # Sentuhan temperatur kehangatan ruangan secara umum
    room_tint = Image.new("RGBA", (cw, ch), (255, 246, 230, 22))
    card_warmed = Image.alpha_composite(card_integrated, room_tint)

    # Mask sudut membulat presisi tinggi
    corner_mask = Image.new("L", (cw, ch), 0)
    cm_draw = ImageDraw.Draw(corner_mask)
    cm_draw.rounded_rectangle([(0, 0), (cw, ch)], radius=32, fill=255)
    
    card_clean = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    card_clean.paste(card_warmed, (0, 0), mask=corner_mask)

    # Kilau pantulan cahaya ruangan alami di permukaan kartu
    glare = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glare)
    g_draw.polygon([(-cw * 0.2, ch * 0.35), (cw * 0.6, -ch * 0.2), (cw * 0.95, -ch * 0.2), (-cw * 0.2, ch * 0.85)], fill=(255, 252, 240, 36))
    glare = glare.filter(ImageFilter.GaussianBlur(radius=30))
    card_pvc = Image.alpha_composite(card_clean, glare)

    dw, dh = 2048, 1365
    desk = load_flawless_wood_desk(dw, dh)

    # Koordinat sudut kartu di atas meja
    src_pts = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
    p0 = (430, 315)
    p1 = (1580, 230)
    p2 = (1495, 1025)
    p3 = (315, 1110)
    dst_pts = [p0, p1, p2, p3]

    coeffs = find_perspective_coeffs(src_pts, dst_pts)

    # SISTEM BAYANGAN MULTI-LAYER (Deep Ambient Occlusion & Directional Falloff)
    shadow_layer = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)

    # A. Bayangan penumbra jatuh arah kanan-bawah (cahaya jendela lembut)
    sh_diff_pts = [(pt[0] + 52, pt[1] + 66) for pt in dst_pts]
    s_draw.polygon(sh_diff_pts, fill=(0, 0, 0, 140))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=38))

    # B. Bayangan menengah (Mid Directional Shadow)
    sh_mid = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sm_draw = ImageDraw.Draw(sh_mid)
    sh_mid_pts = [(pt[0] + 22, pt[1] + 28) for pt in dst_pts]
    sm_draw.polygon(sh_mid_pts, fill=(0, 0, 0, 190))
    sh_mid = sh_mid.filter(ImageFilter.GaussianBlur(radius=16))

    # C. Oklusi Kontak Gelap Pekat (Ultra-Deep Contact Occlusion)
    sh_contact = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sh_c_draw = ImageDraw.Draw(sh_contact)
    sh_c_draw.line([(p3[0] + 6, p3[1] + 8), (p2[0] + 6, p2[1] + 8)], fill=(0, 0, 0, 255), width=28)
    sh_c_draw.line([(p2[0] + 6, p2[1] + 8), (p1[0] + 6, p1[1] + 8)], fill=(0, 0, 0, 255), width=24)
    sh_c_draw.line([(p0[0] + 3, p0[1] + 4), (p3[0] + 3, p3[1] + 4)], fill=(0, 0, 0, 240), width=16)
    sh_c_draw.line([(p1[0] + 3, p1[1] + 4), (p0[0] + 3, p0[1] + 4)], fill=(0, 0, 0, 220), width=12)
    sh_c_pts = [(pt[0] + 4, pt[1] + 5) for pt in dst_pts]
    sh_c_draw.polygon(sh_c_pts, fill=(0, 0, 0, 255))
    sh_contact = sh_contact.filter(ImageFilter.GaussianBlur(radius=6.0))

    # Gabungkan bayangan ke meja kayu
    desk_rgba = desk.convert("RGBA")
    desk_rgba.paste(shadow_layer, (0, 0), shadow_layer)
    desk_rgba.paste(sh_mid, (0, 0), sh_mid)
    desk_rgba.paste(sh_contact, (0, 0), sh_contact)

    # Transformasi kartu dengan filter bicubic halus
    warped_card = card_pvc.transform((dw, dh), Image.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)

    # Mask kartu bersih tanpa artefak
    mask_dw = corner_mask.transform((dw, dh), Image.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
    mask_dw = mask_dw.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Tempel kartu ke meja kayu
    desk_rgba.paste(warped_card, (0, 0), mask=mask_dw)

    final_rgb = desk_rgba.convert("RGB")

    # Grain optik sensor kamera nyata (Apple iPhone 14 Pro sensor simulation)
    noise_layer = Image.new("RGB", (dw, dh), (128, 128, 128))
    n_draw = ImageDraw.Draw(noise_layer)
    for _ in range(15000):
        nx = random.randint(0, dw - 1)
        ny = random.randint(0, dh - 1)
        nv = random.randint(105, 150)
        n_draw.point((nx, ny), fill=(nv, nv, nv))
    noise_layer = noise_layer.filter(ImageFilter.GaussianBlur(radius=0.5))
    final_rgb = Image.blend(final_rgb, noise_layer, alpha=0.018)

    out_buf = BytesIO()
    final_rgb.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()

def render_lanyard_card_holder(card_image_bytes: bytes, univ_code: str = "UT") -> bytes:
    card_raw = Image.open(BytesIO(card_image_bytes)).convert("RGBA")
    cw, ch = card_raw.size

    lanyard_colors = {
        "UT": ((0, 60, 150), (255, 215, 0), "UNIVERSITAS TERBUKA"),
        "UI": ((245, 195, 0), (20, 20, 20), "UNIVERSITAS INDONESIA"),
        "UGM": ((18, 48, 98), (215, 165, 35), "UNIVERSITAS GADJAH MADA"),
        "ITB": ((0, 110, 185), (255, 255, 255), "INSTITUT TEKNOLOGI BANDUNG"),
        "UB": ((15, 35, 75), (245, 185, 20), "UNIVERSITAS BRAWIJAYA"),
    }
    ribbon_bg, ribbon_text_c, univ_name = lanyard_colors.get(univ_code.upper(), ((30, 45, 80), (240, 240, 240), "STUDENT CARD"))

    dw, dh = 2048, 1365
    desk = load_flawless_wood_desk(dw, dh)

    mika_pad_x = 24
    mika_pad_y = 24
    mika_head_h = 130
    holder_w = cw + (mika_pad_x * 2)
    holder_h = ch + (mika_pad_y * 2) + mika_head_h

    holder_layer = Image.new("RGBA", (holder_w, holder_h), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(holder_layer)

    h_draw.rounded_rectangle([(0, 0), (holder_w, holder_h)], radius=32, fill=(255, 255, 255, 35), outline=(255, 255, 255, 160), width=4)
    h_draw.rounded_rectangle([(8, 8), (holder_w - 8, holder_h - 8)], radius=26, outline=(240, 245, 255, 90), width=2)

    hole_w, hole_h = 140, 38
    hx0 = (holder_w - hole_w) // 2
    hy0 = 36
    h_draw.rounded_rectangle([(hx0, hy0), (hx0 + hole_w, hy0 + hole_h)], radius=18, fill=(0, 0, 0, 0), outline=(255, 255, 255, 210), width=3)

    card_paste_y = mika_head_h + mika_pad_y
    holder_layer.paste(card_raw, (mika_pad_x, card_paste_y), card_raw)

    glare_mika = Image.new("RGBA", (holder_w, holder_h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glare_mika)
    g_draw.polygon([(0, 80), (holder_w - 200, 0), (holder_w, 200), (0, holder_h - 100)], fill=(255, 255, 255, 38))
    glare_mika = glare_mika.filter(ImageFilter.GaussianBlur(radius=20))
    holder_layer.paste(glare_mika, (0, 0), glare_mika)

    src_pts = [(0, 0), (holder_w, 0), (holder_w, holder_h), (0, holder_h)]
    p0 = (460, 210)
    p1 = (1620, 260)
    p2 = (1520, 1190)
    p3 = (320, 1110)
    dst_pts = [p0, p1, p2, p3]

    coeffs = find_perspective_coeffs(src_pts, dst_pts)

    sh_diff = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(sh_diff)
    sh_pts = [(pt[0] + 30, pt[1] + 40) for pt in dst_pts]
    sh_draw.polygon(sh_pts, fill=(0, 0, 0, 140))
    sh_diff = sh_diff.filter(ImageFilter.GaussianBlur(radius=36))

    warped_holder = holder_layer.transform((dw, dh), Image.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)

    comp = desk.convert("RGBA")
    comp.paste(sh_diff, (0, 0), sh_diff)

    lanyard_layer = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    l_draw = ImageDraw.Draw(lanyard_layer)

    clip_x = (p0[0] + p1[0]) // 2
    clip_y = (p0[1] + p1[1]) // 2 + 15

    ribbon_w = 42
    sh_ribbon = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sr_draw = ImageDraw.Draw(sh_ribbon)
    sr_draw.line([(clip_x + 18, clip_y + 20), (clip_x - 180 + 18, -40 + 20)], fill=(0, 0, 0, 120), width=ribbon_w)
    sr_draw.line([(clip_x + 18, clip_y + 20), (clip_x + 220 + 18, -40 + 20)], fill=(0, 0, 0, 120), width=ribbon_w)
    sh_ribbon = sh_ribbon.filter(ImageFilter.GaussianBlur(radius=16))
    comp.paste(sh_ribbon, (0, 0), sh_ribbon)

    l_draw.line([(clip_x, clip_y), (clip_x - 180, -40)], fill=ribbon_bg, width=ribbon_w)
    l_draw.line([(clip_x, clip_y), (clip_x + 220, -40)], fill=ribbon_bg, width=ribbon_w)
    l_draw.line([(clip_x - 16, clip_y), (clip_x - 196, -40)], fill=ribbon_text_c, width=2)
    l_draw.line([(clip_x + 16, clip_y), (clip_x - 164, -40)], fill=ribbon_text_c, width=2)
    l_draw.line([(clip_x - 16, clip_y), (clip_x + 204, -40)], fill=ribbon_text_c, width=2)
    l_draw.line([(clip_x + 16, clip_y), (clip_x + 236, -40)], fill=ribbon_text_c, width=2)

    clip_w, clip_h = 36, 52
    l_draw.rounded_rectangle([(clip_x - clip_w//2, clip_y - 15), (clip_x + clip_w//2, clip_y + clip_h - 15)], radius=8, fill=(210, 215, 225, 255), outline=(140, 145, 155, 255), width=3)
    l_draw.line([(clip_x - clip_w//4, clip_y - 10), (clip_x - clip_w//4, clip_y + clip_h - 20)], fill=(255, 255, 255, 230), width=3)
    l_draw.ellipse([(clip_x - 16, clip_y + 24), (clip_x + 16, clip_y + 56)], outline=(170, 175, 185, 255), width=4)

    comp.paste(warped_holder, (0, 0), warped_holder)
    comp.paste(lanyard_layer, (0, 0), lanyard_layer)

    final_rgb = comp.convert("RGB").filter(ImageFilter.SMOOTH_MORE)
    noise_layer = Image.new("RGB", (dw, dh), (128, 128, 128))
    n_draw = ImageDraw.Draw(noise_layer)
    for _ in range(25000):
        nx = random.randint(0, dw - 1)
        ny = random.randint(0, dh - 1)
        nv = random.randint(90, 165)
        n_draw.point((nx, ny), fill=(nv, nv, nv))
    noise_layer = noise_layer.filter(ImageFilter.GaussianBlur(radius=0.7))
    final_rgb = Image.blend(final_rgb, noise_layer, alpha=0.035)

    out_buf = BytesIO()
    final_rgb.save(out_buf, format="JPEG", quality=94)
    return out_buf.getvalue()

def render_handheld_pov(card_image_bytes: bytes) -> bytes:
    card_raw = Image.open(BytesIO(card_image_bytes)).convert("RGBA")
    cw, ch = card_raw.size

    dw, dh = 2048, 1365
    desk = load_flawless_wood_desk(dw, dh)

    src_pts = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
    p0 = (380, 260)
    p1 = (1490, 210)
    p2 = (1420, 1020)
    p3 = (280, 1090)
    dst_pts = [p0, p1, p2, p3]

    coeffs = find_perspective_coeffs(src_pts, dst_pts)

    sh_diff = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(sh_diff)
    sh_pts = [(pt[0] + 45, pt[1] + 65) for pt in dst_pts]
    sh_draw.polygon(sh_pts, fill=(0, 0, 0, 110))
    sh_diff = sh_diff.filter(ImageFilter.GaussianBlur(radius=48))

    warped_card = card_raw.transform((dw, dh), Image.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)

    glare_layer = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glare_layer)
    g_draw.polygon([(p0[0] + 80, p0[1] + 30), (p1[0] - 100, p1[1] + 50), (p2[0] - 400, p2[1] - 80), (p3[0] + 120, p3[1] - 60)], fill=(255, 255, 255, 45))
    glare_layer = glare_layer.filter(ImageFilter.GaussianBlur(radius=30))

    comp = desk.convert("RGBA")
    comp.paste(sh_diff, (0, 0), sh_diff)
    comp.paste(warped_card, (0, 0), warped_card)
    comp.paste(glare_layer, (0, 0), glare_layer)

    hand_layer = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(hand_layer)

    thumb_x, thumb_y = p2[0] - 65, p2[1] - 130
    thumb_sh = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    tsh_draw = ImageDraw.Draw(thumb_sh)
    tsh_draw.ellipse([(thumb_x - 30, thumb_y - 25), (thumb_x + 95, thumb_y + 160)], fill=(0, 0, 0, 100))
    thumb_sh = thumb_sh.filter(ImageFilter.GaussianBlur(radius=12))
    comp.paste(thumb_sh, (0, 0), thumb_sh)

    skin_base = (202, 153, 118, 255)
    skin_shadow = (168, 118, 88, 255)
    skin_highlight = (226, 178, 142, 255)

    h_draw.polygon([(thumb_x + 20, thumb_y + 40), (dw, dh - 60), (dw, dh), (thumb_x - 10, dh)], fill=skin_base)
    h_draw.ellipse([(thumb_x - 35, thumb_y - 30), (thumb_x + 75, thumb_y + 130)], fill=skin_base, outline=skin_shadow, width=2)
    h_draw.ellipse([(thumb_x - 15, thumb_y - 10), (thumb_x + 45, thumb_y + 90)], fill=skin_highlight)
    nail_color = (235, 195, 185, 240)
    nail_white = (250, 240, 240, 255)
    h_draw.ellipse([(thumb_x - 20, thumb_y - 18), (thumb_x + 25, thumb_y + 35)], fill=nail_color, outline=(190, 140, 130, 200), width=1)
    h_draw.arc([(thumb_x - 20, thumb_y - 18), (thumb_x + 25, thumb_y + 35)], start=180, end=360, fill=nail_white, width=2)

    hand_layer = hand_layer.filter(ImageFilter.GaussianBlur(radius=1.2))
    comp.paste(hand_layer, (0, 0), hand_layer)

    final_rgb = comp.convert("RGB").filter(ImageFilter.SMOOTH_MORE)
    noise_layer = Image.new("RGB", (dw, dh), (128, 128, 128))
    n_draw = ImageDraw.Draw(noise_layer)
    for _ in range(25000):
        nx = random.randint(0, dw - 1)
        ny = random.randint(0, dh - 1)
        nv = random.randint(90, 165)
        n_draw.point((nx, ny), fill=(nv, nv, nv))
    noise_layer = noise_layer.filter(ImageFilter.GaussianBlur(radius=0.7))
    final_rgb = Image.blend(final_rgb, noise_layer, alpha=0.035)

    out_buf = BytesIO()
    final_rgb.save(out_buf, format="JPEG", quality=94)
    return out_buf.getvalue()
