"""Couverture Facebook 1640x624 à partir de l'ancienne bannière (photo + décor gardés, ancien texte effacé)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, cv2, sys
SRC, OUT = sys.argv[1], sys.argv[2]
W, H = 1640, 624
FD = "modeles/fonts/"
P = lambda w, s: ImageFont.truetype(FD + f"poppins-latin-{w}-normal.woff", s)
L = lambda s: ImageFont.truetype(FD + "lora-latin-600-italic.woff", s)
DARK = (59, 40, 42); WINE = (142, 44, 72); PINKBRUSH = (242, 201, 211, 210); BTN = (194, 85, 122)

cap = Image.open(SRC).convert("RGB")
g = cap.convert("L"); rows = [y for y in range(cap.height) if g.getpixel((cap.width // 2, y)) > 30]
ban = cap.crop((0, rows[0] + 1, cap.width, rows[-1]))
bw, bh = ban.size
# 1. Effacer l'ancien texte : on repeint la zone texte (inpainting) puis on adoucit
a = cv2.cvtColor(np.array(ban), cv2.COLOR_RGB2BGR)
m = np.zeros(a.shape[:2], np.uint8)
x0, x1 = int(bw * 0.34), int(bw * 0.99); y0, y1 = int(bh * 0.07), int(bh * 0.93)
m[y0:y1, x0:x1] = 255
m[int(bh * 0.74):y1, x0:int(bw * 0.40)] = 0   # ne pas toucher au bras
small = cv2.resize(a, None, fx=0.25, fy=0.25); ms = cv2.resize(m, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
inp = cv2.inpaint(small, ms, 12, cv2.INPAINT_TELEA)
inp = cv2.GaussianBlur(cv2.resize(inp, (bw, bh), interpolation=cv2.INTER_CUBIC), (0, 0), 18)
feather = np.clip(cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 12) * 1.15, 0, 1)[..., None]
a = (a * (1 - feather) + inp * feather).astype(np.uint8)
ban = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
# 2. Mise au format 1640x624
s = max(W / bw, H / bh); ban = ban.resize((int(bw * s) + 1, int(bh * s) + 1), Image.LANCZOS)
canvas = ban.crop(((ban.width - W) // 2, (ban.height - H) // 2, (ban.width - W) // 2 + W, (ban.height - H) // 2 + H))
d = ImageDraw.Draw(canvas, "RGBA"); cx = 1110
def center(y, txt, f, col): d.text((cx, y), txt, font=f, fill=col, anchor="mm")
center(95, "J’aide les femmes débordées à", P(300, 44), DARK)
for y, t in [(185, "perdre jusqu’à 10 kg"), (280, "en 90 jours, sans frustration")]:
    f = L(70); tw = d.textlength(t, font=f)
    d.rounded_rectangle((cx - tw / 2 - 28, y - 30, cx + tw / 2 + 28, y + 40), 30, fill=PINKBRUSH)
    center(y, t, f, WINE)
center(372, "même avec des horaires décalés", P(500, 40), DARK)
center(428, "Rééquilibrage alimentaire  ·  Sport  ·  Mental", P(300, 30), DARK)
btn = "Écris-moi « DÉCLIC » en message"; f = P(600, 30); tw = d.textlength(btn, font=f)
d.rounded_rectangle((cx - tw / 2 - 34, 475, cx + tw / 2 + 34, 535), 30, fill=BTN)
center(505, btn, f, (255, 255, 255))
canvas.save(OUT)
