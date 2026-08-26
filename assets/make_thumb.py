#!/usr/bin/env python3
"""Design an attractive 16:9 YouTube thumbnail from the video's hero frame."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

ASSETS = "/workspaces/hermes-agent/assets"
W, H = 1280, 720

SANS_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

def font(path, size):
    return ImageFont.truetype(path, size)

def load_hero(path):
    img = Image.open(path).convert("RGB")
    # slight contrast/saturation boost for punch
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.12)
    return img

def cover_crop(img, tw, th):
    """Scale+crop to fill tw x th (like CSS object-fit: cover)."""
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))

# ---- base canvas ----
canvas = Image.new("RGB", (W, H), (12, 14, 18))

hero_src = load_hero(f"{ASSETS}/thumb_src/t_0.2.png")

def cover_crop_offset(img, tw, th, yoff=0.0):
    """cover-fit but bias the vertical crop (yoff<0 keeps more headroom at top)."""
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = int((nh - th) * (0.5 + yoff))
    top = max(0, min(nh - th, top))
    return img.crop((left, top, left + tw, top + th))

# RIGHT: full-bleed hero panel (dominant subject) — extra headroom so raised hands aren't clipped
hero_w = 560
hero = cover_crop_offset(hero_src, hero_w, H, yoff=-0.30)
canvas.paste(hero, (W - hero_w, 0))

# LEFT background: blurred, darkened version of hero for cohesive palette
bg = cover_crop(hero_src, W, H).filter(ImageFilter.GaussianBlur(28))
bg = ImageEnhance.Brightness(bg).enhance(0.42)
canvas.paste(bg, (0, 0), Image.new("L", (W, H), 255) if False else None)
# recompose: bg on left region only, keep hero on right
final = Image.new("RGB", (W, H))
final.paste(bg, (0, 0))
final.paste(hero, (W - hero_w, 0))
canvas = final

draw = ImageDraw.Draw(canvas, "RGBA")

# gradient seam between blurred bg and hero (fade hero's left edge into bg)
seam_x = W - hero_w
grad_w = 220
for i in range(grad_w):
    a = int(255 * (1 - i / grad_w))
    draw.line([(seam_x + i, 0), (seam_x + i, H)], fill=(12, 14, 18, a))

# left dark scrim for text legibility
scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(scrim)
for x in range(0, 760):
    a = int(150 * max(0, 1 - x / 760))
    sd.line([(x, 0), (x, H)], fill=(6, 8, 12, a))
canvas = Image.alpha_composite(canvas.convert("RGBA"), scrim).convert("RGB")
draw = ImageDraw.Draw(canvas, "RGBA")

# ---- top accent kicker ----
accent = (120, 210, 255)
kicker_font = font(SANS_BOLD, 32)
draw.rectangle([70, 92, 98, 130], fill=accent)
draw.text((114, 90), "CHILL POP · VISUAL LOOP", font=kicker_font, fill=(214, 234, 246))

# ---- big title (serif, fashion-editorial) ----
title_font = font(SERIF_BOLD, 190)
draw.text((60, 150), "循环", font=title_font, fill=(255, 255, 255))
# EN subtitle overlaid
en_font = font(SANS_BOLD, 78)
draw.text((66, 396), "L O O P", font=en_font, fill=accent)

# thin rule
draw.line([(70, 500), (600, 500)], fill=(255, 255, 255, 90), width=2)

# ---- tagline ----
tag_font = font(SANS_BOLD, 40)
draw.text((68, 524), "六秒钟的光 · 三联同步", font=tag_font, fill=(230, 238, 244))

# ---- triptych motif: 3 clear vertical dividers over hero (nods to the layout) ----
for k in range(1, 3):
    lx = (W - hero_w) + hero_w * k // 3
    draw.line([(lx, 0), (lx, H)], fill=(255, 255, 255, 130), width=3)

# ---- play button over hero (universal video cue) — placed low to avoid the face ----
pcx, pcy, pr = W - hero_w // 2, int(H * 0.72), 52
draw.ellipse([pcx - pr, pcy - pr, pcx + pr, pcy + pr], fill=(255, 255, 255, 210))
tri = [(pcx - 17, pcy - 26), (pcx - 17, pcy + 26), (pcx + 28, pcy)]
draw.polygon(tri, fill=(18, 20, 26, 255))

# subtle vignette
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-200, -160, W + 200, H + 160], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(180))
dark = Image.new("RGB", (W, H), (0, 0, 0))
canvas = Image.composite(canvas, dark, vig)

out = f"{ASSETS}/thumbnail.png"
canvas.save(out, "PNG")
out_jpg = f"{ASSETS}/thumbnail.jpg"
canvas.convert("RGB").save(out_jpg, "JPEG", quality=92)
print("saved:", out)
print("size:", canvas.size)
