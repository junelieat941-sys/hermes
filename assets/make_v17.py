#!/usr/bin/env python3
"""Cover: 惊鸿 — LOOP-series dark triptych cover."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math
import numpy as np

ASSETS = "/workspaces/hermes-agent/assets/new videos"
W, H = 1280, 720

SANS_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

def font(p, s):
    return ImageFont.truetype(p, s)

DARK   = (12, 14, 18)
MID    = (42, 44, 52)
ACCENT = (120, 210, 255)
SOFT   = (230, 235, 240)
WHITE  = (255, 255, 255)

def load_hero(path):
    img = Image.open(path).convert("RGB")
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(1.10)
    return img

def cover_crop_offset(img, tw, th, yoff=0.0):
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = int((nh - th) * (0.5 + yoff))
    top = max(0, min(nh - th, top))
    return img.crop((left, top, left + tw, top + th))

hero_src = load_hero(f"{ASSETS}/v17_hero.jpg")

base = Image.new("RGB", (W, H), DARK)
bd = ImageDraw.Draw(base)
for y in range(H):
    t = y / H
    r = int(DARK[0] + (MID[0]-DARK[0]) * t)
    g = int(DARK[1] + (MID[1]-DARK[1]) * t)
    b = int(DARK[2] + (MID[2]-DARK[2]) * t)
    bd.line([(0, y), (W, y)], fill=(r, g, b))

canvas = base

hero_w = 560
hero_x = W - hero_w
hero = cover_crop_offset(hero_src, hero_w, H, yoff=-0.02)
hero_rgba = hero.convert("RGBA")

left_f = 120
xs = np.arange(hero_w)
ax = np.clip(xs / left_f, 0, 1)
alpha = np.tile((ax * 255).astype("uint8"), (H, 1))
mask = Image.fromarray(alpha, "L")
canvas.paste(hero_rgba, (hero_x, 0), mask)

draw = ImageDraw.Draw(canvas, "RGBA")

kicker_font = font(SANS_BOLD, 30)
draw.rounded_rectangle([70, 88, 104, 126], radius=8, fill=ACCENT)
draw.text((118, 88), "DARK · GLANCE", font=kicker_font, fill=SOFT)

title_font = font(SERIF_BOLD, 190)
draw.text((62, 148), "惊鸿", font=title_font, fill=WHITE)
en_font = font(SANS_BOLD, 78)
draw.text((68, 392), "GLANCE", font=en_font, fill=ACCENT)

draw.line([(70, 496), (520, 496)], fill=WHITE + (90,), width=3)

tag_font = font(SANS_BOLD, 38)
draw.text((68, 516), "一眼万年 · 惊鸿一瞥", font=tag_font, fill=SOFT)

for sx, sy, ss in [(480, 180, 18), (520, 300, 14)]:
    draw.line([(sx-ss,sy),(sx+ss,sy)], fill=ACCENT, width=6)
    draw.line([(sx,sy-ss),(sx,sy+ss)], fill=ACCENT, width=6)

def heart(cx, cy, s, col):
    pts=[]
    for i in range(0, 315):
        t = i*0.02
        x = 16*math.sin(t)**3
        y = 13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        pts.append((cx + x*s, cy - y*s))
    draw.polygon(pts, fill=col)

tag2_font = font(SANS_BOLD, 30)
draw.text((68, 570), "at first glance", font=tag2_font, fill=SOFT)
_tb = draw.textbbox((0, 0), "at first glance", font=tag2_font)
heart(68 + (_tb[2]-_tb[0]) + 34, 588, 2.4, ACCENT)

for k in range(1, 3):
    lx = hero_x + hero_w * k // 3
    draw.line([(lx, 0), (lx, H)], fill=(60, 40, 34, 130), width=8)
    draw.line([(lx, 0), (lx, H)], fill=(255, 255, 255, 235), width=3)

pcx, pcy, pr = hero_x + hero_w // 2, int(H * 0.72), 56
draw.ellipse([pcx - pr - 4, pcy - pr - 4, pcx + pr + 4, pcy + pr + 4], fill=(10, 12, 16, 130))
draw.ellipse([pcx - pr, pcy - pr, pcx + pr, pcy + pr], fill=(255, 255, 255, 235))
tri = [(pcx - 18, pcy - 27), (pcx - 18, pcy + 27), (pcx + 30, pcy)]
draw.polygon(tri, fill=ACCENT)

vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-200, -160, W + 200, H + 160], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(170))
dark = Image.new("RGB", (W, H), (10, 12, 16))
canvas = Image.composite(canvas, dark, vig)

out = f"{ASSETS}/cover_v17.png"
canvas.save(out, "PNG")
canvas.convert("RGB").save(f"{ASSETS}/cover_v17.jpg", "JPEG", quality=92)
print("saved:", out, canvas.size)
