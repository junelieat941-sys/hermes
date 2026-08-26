#!/usr/bin/env python3
"""Cute hand-drawn poster cover for the little-robot poem (vector via Pillow)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ASSETS = "/workspaces/hermes-agent/assets"
W, H = 1080, 1350

SANS_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

def font(p, s):
    return ImageFont.truetype(p, s)

# ---- palette (warm, cute) ----
CREAM   = (255, 248, 236)
PEACH   = (255, 224, 196)
MINT    = (168, 224, 205)
SKY     = (150, 206, 235)
BUTTER  = (255, 213, 128)
CORAL   = (255, 148, 120)
INK     = (74, 66, 62)
BODY     = (120, 108, 100)

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img, "RGBA")

# ---- soft gradient sky (cream -> peach) at top ----
for y in range(H):
    t = y / H
    r = int(CREAM[0] + (PEACH[0]-CREAM[0]) * (t*0.6))
    g = int(CREAM[1] + (PEACH[1]-CREAM[1]) * (t*0.6))
    b = int(CREAM[2] + (PEACH[2]-CREAM[2]) * (t*0.6))
    d.line([(0, y), (W, y)], fill=(r, g, b))

# ---- floating dots / bokeh ----
import random
random.seed(7)
for _ in range(46):
    x = random.randint(0, W); y = random.randint(0, int(H*0.9))
    rr = random.randint(4, 16)
    col = random.choice([MINT, SKY, BUTTER, CORAL])
    d.ellipse([x-rr, y-rr, x+rr, y+rr], fill=col + (70,))

# ---- sun ----
d.ellipse([80, 90, 210, 220], fill=BUTTER + (230,))
for i in range(12):
    a = i * math.pi / 6
    cx, cy = 145, 155
    x1 = cx + 78*math.cos(a); y1 = cy + 78*math.sin(a)
    x2 = cx + 104*math.cos(a); y2 = cy + 104*math.sin(a)
    d.line([(x1,y1),(x2,y2)], fill=BUTTER + (200,), width=7)

cx = W // 2

def rrect(box, r, fill, outline=None, w=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)

# ================= CUTE ROBOT =================
robot_top = 360

# ---- antenna ----
d.line([(cx, robot_top-70), (cx, robot_top-10)], fill=INK, width=8)
# little spring coil on the antenna
for i in range(4):
    yy = robot_top-70 + i*6
    d.arc([cx-14, yy-6, cx+14, yy+8], 0, 180, fill=INK, width=5)
d.ellipse([cx-20, robot_top-108, cx+20, robot_top-68], fill=CORAL, outline=INK, width=5)

# ---- head ----
hw, hh = 300, 240
hx0, hy0 = cx-hw//2, robot_top
rrect([hx0, hy0, hx0+hw, hy0+hh], 60, SKY, outline=INK, w=8)
# face screen
rrect([hx0+34, hy0+40, hx0+hw-34, hy0+hh-40], 42, CREAM, outline=INK, w=6)
# eyes (big cute)
ey = hy0+118
for ex in (cx-58, cx+58):
    d.ellipse([ex-34, ey-40, ex+34, ey+40], fill=INK)
    d.ellipse([ex-10, ey-30, ex+18, ey-2], fill=(255,255,255,255))  # highlight
    d.ellipse([ex-24, ey+16, ex-6, ey+32], fill=(255,255,255,180))
# blush
d.ellipse([cx-118, ey+30, cx-78, ey+58], fill=CORAL + (150,))
d.ellipse([cx+78, ey+30, cx+118, ey+58], fill=CORAL + (150,))
# smile
d.arc([cx-42, ey+18, cx+42, ey+78], 20, 160, fill=INK, width=7)

# ---- body ----
bw, bh = 340, 300
bx0, by0 = cx-bw//2, hy0+hh+40
rrect([bx0, by0, bx0+bw, by0+bh], 54, MINT, outline=INK, w=8)
# heart panel
hx, hy = cx, by0+120
d.polygon([(hx, hy+40),(hx-46, hy-6),(hx-46, hy-24)], fill=CORAL)
# draw a proper heart
def heart(cx, cy, s, col):
    pts=[]
    for t in [i*0.02 for i in range(0,315)]:
        x = 16*math.sin(t)**3
        y = 13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        pts.append((cx + x*s, cy - y*s))
    d.polygon(pts, fill=col)
heart(cx, by0+110, 4.2, CORAL)
# tummy buttons
for i, col in enumerate([BUTTER, SKY, CORAL]):
    d.ellipse([cx-70+i*56, by0+210, cx-42+i*56, by0+238], fill=col, outline=INK, width=4)

# ---- SPRING ARMS (star of the poem) ----
def spring_arm(x0, y0, x1, y1, coils=6, amp=26, col=INK):
    pts = []
    steps = coils * 24
    for i in range(steps+1):
        t = i/steps
        x = x0 + (x1-x0)*t
        y = y0 + (y1-y0)*t
        x += amp * math.sin(t * coils * 2*math.pi)
        pts.append((x, y))
    d.line(pts, fill=col, width=9, joint="curve")

# left arm springs up (waving), right arm springs down
spring_arm(bx0+8, by0+70, bx0-70, by0-40, coils=5, amp=22)
d.ellipse([bx0-92, by0-70, bx0-48, by0-26], fill=BUTTER, outline=INK, width=5)  # hand
spring_arm(bx0+bw-8, by0+80, bx0+bw+78, by0+150, coils=5, amp=22)
d.ellipse([bx0+bw+56, by0+130, bx0+bw+100, by0+174], fill=BUTTER, outline=INK, width=5)

# ---- legs / wheels ----
for lx in (cx-80, cx+80):
    d.line([(lx, by0+bh-6),(lx, by0+bh+40)], fill=INK, width=10)
    d.ellipse([lx-34, by0+bh+30, lx+34, by0+bh+98], fill=(120,110,120), outline=INK, width=7)
    d.ellipse([lx-12, by0+bh+52, lx+12, by0+bh+76], fill=CREAM)

# ---- ground shadow ----
d.ellipse([cx-210, by0+bh+92, cx+210, by0+bh+140], fill=(0,0,0,28))

# ================= TITLE =================
title_font = font(SERIF_BOLD, 84)
tt = "小机器人上工了"
tb = d.textbbox((0,0), tt, font=title_font)
tw = tb[2]-tb[0]
ty = H - 250
# soft white plate behind title
d.rounded_rectangle([cx-tw//2-40, ty-24, cx+tw//2+40, ty+128], radius=36,
                    fill=(255,255,255,205))
d.text((cx-tw//2, ty), tt, font=title_font, fill=INK)

# little sparkles around title
for sx, sy, ss in [(cx-tw//2-70, ty+20, 16),(cx+tw//2+52, ty+8, 20),(cx+tw//2+70, ty+96, 12)]:
    d.line([(sx-ss,sy),(sx+ss,sy)], fill=BUTTER, width=6)
    d.line([(sx,sy-ss),(sx,sy+ss)], fill=BUTTER, width=6)

# subtitle
sub_font = font(SANS_BOLD, 34)
st = "一首献给齿轮与弹簧的小诗"
sbb = d.textbbox((0,0), st, font=sub_font)
sw = sbb[2]-sbb[0]
d.text((cx-sw//2, ty+150), st, font=sub_font, fill=BODY)

out = f"{ASSETS}/poem_cover.png"
img.save(out, "PNG")
img.convert("RGB").save(f"{ASSETS}/poem_cover.jpg", "JPEG", quality=92)
print("saved:", out, img.size)
