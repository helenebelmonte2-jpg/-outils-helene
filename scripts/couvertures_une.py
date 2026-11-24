"""Couvertures de stories à la une (1080x1920, icône au centre, fond rose)."""
from PIL import Image, ImageDraw, ImageFont
import os, sys
OUT = sys.argv[1]
W, H = 1080, 1920; cx, cy = W // 2, H // 2
BG1, BG2 = (243, 196, 212), (232, 80, 143); WHITE = (255, 255, 255)
F = ImageFont.truetype("modeles/fonts/lora-latin-600-italic.woff", 460)
LW = 26
def base():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=tuple(int(BG1[k] + (BG2[k] - BG1[k]) * t) for k in range(3)))
    d.ellipse((cx - 330, cy - 330, cx + 330, cy + 330), outline=WHITE, width=10)
    return im, d
def qui(d):
    d.ellipse((cx - 85, cy - 200, cx + 85, cy - 30), outline=WHITE, width=LW)
    d.arc((cx - 190, cy + 10, cx + 190, cy + 390), 180, 360, fill=WHITE, width=LW)
def programme(d):
    d.rounded_rectangle((cx - 150, cy - 190, cx + 150, cy + 200), 30, outline=WHITE, width=LW)
    d.rounded_rectangle((cx - 70, cy - 225, cx + 70, cy - 160), 20, fill=WHITE)
    # coeur
    x, y = cx, cy + 20
    d.polygon([(x, y + 90), (x - 95, y - 5), (x - 95, y - 45), (x - 55, y - 85), (x, y - 50), (x + 55, y - 85), (x + 95, y - 45), (x + 95, y - 5)], fill=WHITE)
def clientes(d):
    d.rounded_rectangle((cx - 210, cy - 170, cx + 210, cy + 110), 60, outline=WHITE, width=LW)
    d.polygon([(cx - 120, cy + 100), (cx - 160, cy + 200), (cx - 40, cy + 100)], fill=WHITE)
    for i in (-1, 0, 1):
        x = cx + i * 115; y = cy - 30
        pts = []
        import math
        for k in range(10):
            r = 50 if k % 2 == 0 else 21; a = -math.pi / 2 + k * math.pi / 5
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        d.polygon(pts, fill=WHITE)
def astuces(d):
    d.ellipse((cx - 150, cy - 230, cx + 150, cy + 70), outline=WHITE, width=LW)
    d.rounded_rectangle((cx - 75, cy + 60, cx + 75, cy + 150), 15, outline=WHITE, width=LW)
    d.line((cx - 55, cy + 195, cx + 55, cy + 195), fill=WHITE, width=LW)
    for a, b in [((cx, cy - 300), (cx, cy - 265)), ((cx - 215, cy - 160), (cx - 185, cy - 140)), ((cx + 215, cy - 160), (cx + 185, cy - 140))]:
        d.line((a, b), fill=WHITE, width=18)
def assiettes(d):
    d.ellipse((cx - 170, cy - 170, cx + 170, cy + 170), outline=WHITE, width=LW)
    d.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), outline=WHITE, width=14)
    d.line((cx - 250, cy - 170, cx - 250, cy + 190), fill=WHITE, width=20)
    for dx in (-30, 0, 30): d.line((cx - 250 + dx, cy - 170, cx - 250 + dx, cy - 80), fill=WHITE, width=12)
    d.ellipse((cx + 220, cy - 175, cx + 280, cy - 40), fill=WHITE); d.line((cx + 250, cy - 60, cx + 250, cy + 190), fill=WHITE, width=20)
def faq(d):
    d.text((cx, cy + 10), "?", font=F, fill=WHITE, anchor="mm")
ICONS = [("qui_suis_je", qui), ("mon_programme", programme), ("retours_clientes", clientes),
         ("astuces", astuces), ("mes_assiettes", assiettes), ("faq", faq)]
for name, fn in ICONS:
    im, d = base(); fn(d); im.save(os.path.join(OUT, f"une_{name}.png"))
