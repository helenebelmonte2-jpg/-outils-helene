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
d = ImageDraw.Draw(canvas, "RGBA"); cx = 1100
def center(y, txt, f, col): d.text((cx, y), txt, font=f, fill=col, anchor="mm")
VAR = sys.argv[3] if len(sys.argv) > 3 else "promesse"
def brush(y, t, size=64):
    f = L(size); tw = d.textlength(t, font=f)
    d.rounded_rectangle((cx - tw / 2 - 28, y - 32, cx + tw / 2 + 28, y + 42), 30, fill=PINKBRUSH)
    center(y, t, f, WINE)
def bouton(y, txt="Écris-moi « DÉCLIC » en message"):
    f = P(600, 32); tw = d.textlength(txt, font=f)
    d.rounded_rectangle((cx - tw / 2 - 36, y - 32, cx + tw / 2 + 36, y + 32), 32, fill=BTN)
    center(y, txt, f, (255, 255, 255))
def check(x, y):
    d.ellipse((x - 17, y - 17, x + 17, y + 17), fill=BTN)
    d.line((x - 8, y + 1, x - 2, y + 8, x + 9, y - 7), fill=(255, 255, 255), width=5, joint="curve")
if VAR == "promesse":
    center(110, "COACH EN RÉÉQUILIBRAGE ALIMENTAIRE", P(500, 28), (150, 80, 100))
    brush(205, "Perds jusqu’à 10 kg en 3 mois"); brush(300, "sans te prendre la tête")
    center(392, "même avec une vie de dingue", P(500, 42), DARK); bouton(487)
elif VAR == "question":
    center(120, "Tu as déjà TOUT essayé pour perdre du poids ?", P(500, 38), DARK)
    brush(215, "Et si le problème,"); brush(305, "c’était la méthode ?")
    center(395, "Rééquilibrage alimentaire adapté à TA vie, sans frustration", P(300, 30), DARK); bouton(475)
elif VAR == "soignante":
    center(110, "AIDE-SOIGNANTE & COACH EN RÉÉQUILIBRAGE ALIMENTAIRE", P(500, 26), (150, 80, 100))
    brush(200, "10 kg perdus, jamais repris", 62); brush(292, "même avec mes horaires de nuit", 56)
    center(385, "Je t’aide à faire pareil, à ton rythme", P(500, 40), DARK); bouton(475)
elif VAR == "melange":
    center(115, "COACH EN RÉÉQUILIBRAGE ALIMENTAIRE", P(500, 28), (150, 80, 100))
    brush(210, "10 kg perdus, jamais repris", 66)
    center(312, "Je t’aide à faire pareil, sans te prendre la tête :", P(500, 32), DARK)
    items = ["Sans régime", "Sans frustration", "Adapté à ton rythme"]; f = P(500, 28)
    widths = [d.textlength(t, font=f) + 48 for t in items]; gap = 26
    x = cx - (sum(widths) + gap * 2) / 2
    for t, w in zip(items, widths):
        check(x + 17, 375); d.text((x + 45, 375), t, font=f, fill=DARK, anchor="lm"); x += w + gap
    bouton(470)
elif VAR == "checklist":
    center(115, "COACH EN RÉÉQUILIBRAGE ALIMENTAIRE", P(500, 28), (150, 80, 100))
    brush(205, "Perds jusqu’à 10 kg en 3 mois", 62)
    items = ["Sans régime", "Sans frustration", "Adapté à ton rythme"]; f = P(500, 28)
    widths = [d.textlength(t, font=f) + 48 for t in items]; gap = 26
    x = cx - (sum(widths) + gap * 2) / 2
    for t, w in zip(items, widths):
        check(x + 17, 315); d.text((x + 45, 315), t, font=f, fill=DARK, anchor="lm"); x += w + gap
    bouton(430)
canvas.save(OUT)
