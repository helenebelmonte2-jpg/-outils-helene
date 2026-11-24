"""Stories « Fausse croyance / Vraie croyance » – format 1080x1920."""
from PIL import Image, ImageDraw, ImageFont
import os, sys

OUT = sys.argv[1]
W, H = 1080, 1920
CREAM = (255, 245, 248); PINK = (232, 80, 143); DARK = (43, 34, 40)
GREY = (150, 135, 142); SOFT = (250, 222, 233); WHITE = (255, 255, 255)
RED = (214, 69, 69); GREEN = (46, 170, 110)
F = "/usr/share/fonts/opentype/inter/"
XB = lambda s: ImageFont.truetype(F + "Inter-ExtraBold.otf", s)
MD = lambda s: ImageFont.truetype(F + "Inter-Medium.otf", s)

def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if d.textlength(t.replace("*", ""), font=f) > maxw and cur:
                lines.append(cur); cur = w
            else:
                cur = t
        lines.append(cur)
    return lines

def draw_lines(d, lines, f, y, color, accent=None, lh=1.25, strike=None):
    inside = False
    for ln in lines:
        words = ln.split(" ")
        total = d.textlength(ln.replace("*", ""), font=f)
        x = (W - total) / 2
        for k, w in enumerate(words):
            start = w.startswith("*"); r = w.rstrip(".,…:;!?'"); end = r.endswith("*") and len(r) > 1
            p = inside or start
            clean = w.replace("*", "")
            d.text((x, y), clean, font=f, fill=(accent if (p and accent) else color))
            x += d.textlength(clean + (" " if k < len(words) - 1 else ""), font=f)
            if start and not end: inside = True
            elif end: inside = False
        if strike:
            mid = y + f.size * 0.55
            d.line(((W - total) / 2 - 10, mid, (W + total) / 2 + 10, mid), fill=strike, width=7)
        y += f.size * lh
    return y

def badge(d, cx, cy, ok):
    r = 46
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN if ok else RED)
    if ok:
        d.line((cx - 22, cy + 2, cx - 6, cy + 20, cx + 24, cy - 18), fill=WHITE, width=12, joint="curve")
    else:
        d.line((cx - 18, cy - 18, cx + 18, cy + 18), fill=WHITE, width=12)
        d.line((cx - 18, cy + 18, cx + 18, cy - 18), fill=WHITE, width=12)

def footer(d, i, n, light=False):
    tot = n * 28; x = (W - tot) / 2
    for k in range(n):
        c = (WHITE if k == i else (240, 160, 195)) if light else (PINK if k == i else SOFT)
        d.ellipse((x, H - 250, x + 14, H - 236), fill=c); x += 28
    d.text((W / 2, H - 300), "@helene_belmonte", font=MD(32), fill=WHITE if light else PINK, anchor="mm")

MYTHS = [
    ("Pour maigrir, il faut manger moins.",
     "Il faut manger *mieux* : des repas qui *calent* (protéines, fibres, légumes). Manger trop peu, c'est la porte ouverte aux *craquages*."),
    ("Il faut supprimer le pain et les féculents.",
     "Les féculents complets *calent* et donnent de l'*énergie*. Ce qui compte, c'est la *quantité* et ce qu'il y a autour dans l'assiette."),
    ("Manger le soir fait grossir.",
     "C'est ta *journée entière* qui compte, pas l'heure. Quand on travaille de *nuit*, on mange quand on peut, et c'est OK."),
    ("Il faut faire beaucoup de sport pour perdre du poids.",
     "C'est surtout l'*assiette* qui fait la différence. Le sport aide, mais *marcher* suffit pour commencer."),
    ("Si je craque, j'ai tout gâché.",
     "Un écart ne fait pas grossir. C'est *abandonner* qui fait reprendre. Au repas suivant, *on reprend*, sans culpabilité."),
]
n = len(MYTHS) + 2

# 1. Intro
im = Image.new("RGB", (W, H), PINK); d = ImageDraw.Draw(im)
d.text((W / 2, 520), "ON DIT SOUVENT QUE…", font=XB(46), fill=(255, 210, 228), anchor="mm")
y = draw_lines(d, wrap(d, "5 idées reçues qui bloquent ta perte de poids", XB(96), 900), XB(96), 600, WHITE, lh=1.15)
d.rounded_rectangle((170, y + 70, W - 170, y + 190), 60, fill=WHITE)
d.text((W / 2, y + 130), "Tu y crois encore ?", font=XB(48), fill=PINK, anchor="mm")
d.text((W / 2, y + 290), "Tape pour voir  →", font=MD(40), fill=WHITE, anchor="mm")
footer(d, 0, n, light=True)
im.save(os.path.join(OUT, "story_01.png"))

# 2-6. Myths
for k, (faux, vrai) in enumerate(MYTHS):
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    d.text((W / 2, 300), f"{k + 1} / {len(MYTHS)}", font=XB(40), fill=SOFT, anchor="mm")
    badge(d, W / 2, 420, False)
    d.text((W / 2, 520), "On dit souvent que…", font=XB(46), fill=RED, anchor="mm")
    y = draw_lines(d, wrap(d, "«\u00a0" + faux.rstrip(".") + "\u00a0»", XB(64), 860), XB(64), 590, GREY, strike=RED)
    top = y + 60
    vl = wrap(d, vrai, XB(54), 820)
    d.rounded_rectangle((70, top, W - 70, top + 270 + len(vl) * 54 * 1.3 + 70), 50, fill=PINK)
    badge(d, W / 2, top + 100, True)
    d.text((W / 2, top + 200), "En réalité…", font=XB(46), fill=WHITE, anchor="mm")
    draw_lines(d, wrap(d, vrai, XB(54), 820), XB(54), top + 270, WHITE, accent=DARK, lh=1.3)
    footer(d, k + 1, n)
    im.save(os.path.join(OUT, f"story_{k + 2:02d}.png"))

# 7. CTA
im = Image.new("RGB", (W, H), PINK); d = ImageDraw.Draw(im)
y = draw_lines(d, wrap(d, "Laquelle on t'a déjà dite ?", XB(88), 880), XB(88), 480, WHITE, lh=1.15)
d.text((W / 2, y + 60), "Réponds-moi en message, je lis tout", font=MD(40), fill=WHITE, anchor="mm")
box = y + 180
d.rounded_rectangle((110, box, W - 110, box + 330), 50, fill=WHITE)
d.text((W / 2, box + 75), "Écris-moi", font=XB(50), fill=DARK, anchor="mm")
d.text((W / 2, box + 170), "DÉCLIC", font=XB(120), fill=PINK, anchor="mm")
d.text((W / 2, box + 265), "et je t'envoie mon test gratuit", font=MD(40), fill=DARK, anchor="mm")
d.text((W / 2, box + 450), "Pas de régime. Pas de frustration.", font=XB(44), fill=WHITE, anchor="mm")
d.text((W / 2, box + 515), "Pas de culpabilité.", font=XB(44), fill=WHITE, anchor="mm")
footer(d, n - 1, n, light=True)
im.save(os.path.join(OUT, f"story_{n:02d}.png"))
