from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math
import random
import os
from pathlib import Path

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

def create_photorealistic_desk(width=2048, height=1365):
    img = Image.new("RGB", (width, height), (75, 48, 30))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        light_factor = 1.0 - (y / height) * 0.35
        r_base = int(88 * light_factor)
        g_base = int(54 * light_factor)
        b_base = int(34 * light_factor)
        draw.line([(0, y), (width, y)], fill=(r_base, g_base, b_base))

    for y in range(0, height, 3):
        variance = int(math.sin(y * 0.08) * 12 + math.cos(y * 0.02) * 8)
        color_w = (max(0, min(255, 78 + variance)), max(0, min(255, 48 + variance)), max(0, min(255, 30 + variance)))
        draw.line([(0, y), (width, y)], fill=color_w, width=2)

    img = img.filter(ImageFilter.GaussianBlur(radius=5.5))
    return img

def render_card_on_desk(card_image_bytes: bytes) -> bytes:
    """Simulasi foto kartu fisik di atas meja kayu dengan sudut miring 3D & ambient occlusion"""
    card_raw = Image.open(BytesIO(card_image_bytes)).convert("RGBA")
    cw, ch = card_raw.size

    # Efek laminasi PVC halus
    glare = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glare)
    g_draw.polygon([(0, int(ch * 0.35)), (int(cw * 0.65), 0), (cw, int(ch * 0.25)), (0, ch)], fill=(255, 255, 255, 24))
    glare = glare.filter(ImageFilter.GaussianBlur(radius=32))

    card_pvc = Image.alpha_composite(card_raw, glare)

    dw, dh = 2048, 1365
    desk = create_photorealistic_desk(dw, dh)

    src_pts = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
    p0 = (420, 290)
    p1 = (1560, 210)
    p2 = (1490, 980)
    p3 = (310, 1070)
    dst_pts = [p0, p1, p2, p3]

    coeffs = find_perspective_coeffs(src_pts, dst_pts)

    shadow_combined = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sh_diff = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sh1_draw = ImageDraw.Draw(sh_diff)
    sh1_pts = [(pt[0] + 32, pt[1] + 42) for pt in dst_pts]
    sh1_draw.polygon(sh1_pts, fill=(0, 0, 0, 130))
    sh_diff = sh_diff.filter(ImageFilter.GaussianBlur(radius=38))

    sh_ao = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    sh2_draw = ImageDraw.Draw(sh_ao)
    sh2_pts = [(pt[0] + 8, pt[1] + 10) for pt in dst_pts]
    sh2_draw.polygon(sh2_pts, fill=(0, 0, 0, 200))
    sh_ao = sh_ao.filter(ImageFilter.GaussianBlur(radius=10))

    shadow_combined.paste(sh_diff, (0, 0), sh_diff)
    shadow_combined.paste(sh_ao, (0, 0), sh_ao)

    warped_card = card_pvc.transform((dw, dh), Image.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)

    rim_layer = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(rim_layer)
    rim_pts = [(pt[0] + 3, pt[1] + 4) for pt in dst_pts]
    r_draw.polygon(rim_pts, outline=(235, 238, 245, 190), width=2)
    rim_layer = rim_layer.filter(ImageFilter.GaussianBlur(radius=1))

    final_img = desk.convert("RGBA")
    final_img.paste(shadow_combined, (0, 0), shadow_combined)
    final_img.paste(rim_layer, (0, 0), rim_layer)
    final_img.paste(warped_card, (0, 0), warped_card)

    final_rgb = final_img.convert("RGB").filter(ImageFilter.SMOOTH_MORE)

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
    desk = create_photorealistic_desk(dw, dh)

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
    desk = create_photorealistic_desk(dw, dh)

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
