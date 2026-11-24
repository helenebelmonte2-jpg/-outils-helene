"""Stories « On dit souvent que… » v2 – style natif Instagram, 1 idée par story,
place laissée pour un sticker quiz (Vrai/Faux) puis réponse sur la story suivante."""
from PIL import Image, ImageDraw, ImageFont
import os, sys

OUT = sys.argv[1]
W, H = 1080, 1920
PINK = (232, 80, 143); DARK = (43, 34, 40); WHITE = (255, 255, 255); CREAM = (255, 245, 248)
F = "/usr/share/fonts/opentype/inter/"
XB = lambda s: ImageFont.truetype(F + "Inter-ExtraBold.otf", s)
BD = lambda s: ImageFont.truetype(F + "Inter-Bold.otf", s)

def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > maxw and cur:
                out.append(cur); cur = w
            else:
                cur = t
        out.append(cur)
    return out

def boxed(d, text, f, y, fg, bg, maxw=860, pad=22, lh=1.32):
    """Texte centré avec un fond arrondi par ligne (comme l'outil texte d'Instagram)."""
    for ln in wrap(d, text, f, maxw):
        if not ln:
            y += f.size * 0.6; continue
        tw = d.textlength(ln, font=f)
        x = (W - tw) / 2
        d.rounded_rectangle((x - pad, y - pad * 0.55, x + tw + pad, y + f.size + pad * 0.75), 18, fill=bg)
        d.text((x, y), ln, font=f, fill=fg)
        y += f.size * lh
    return y

def gradient(c1, c2):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3)))
    return im

def handle(d, light=True):
    d.text((W / 2, H - 260), "@helene_belmonte", font=BD(30), fill=WHITE if light else PINK, anchor="mm")

MYTHS = [
    ("Pour maigrir, il faut manger moins",
     "Il faut manger MIEUX.\nDes repas qui calent = moins de fringales, moins de craquages."),
    ("Manger le soir fait grossir",
     "C'est ta journée entière qui compte, pas l'heure.\nTu bosses de nuit ? Tu manges quand tu peux, et c'est OK."),
    ("Si je craque, j'ai tout gâché",
     "Un écart ne fait pas grossir.\nC'est abandonner qui fait reprendre.\nAu repas suivant, on reprend. Sans culpabilité."),
]

i = 1
for faux, vrai in MYTHS:
    # Story A : l'idée reçue + place pour le quiz
    im = gradient((58, 44, 52), (28, 20, 26)); d = ImageDraw.Draw(im)
    boxed(d, "On dit souvent que…", BD(46), 360, DARK, WHITE)
    boxed(d, "« " + faux + " »", XB(80), 520, WHITE, PINK, maxw=880)
    handle(d)
    im.save(os.path.join(OUT, f"story_{i:02d}.png")); i += 1
    # Story B : la réponse
    im = gradient((240, 104, 160), (214, 60, 125)); d = ImageDraw.Draw(im)
    boxed(d, "En réalité…", XB(64), 380, PINK, WHITE)
    boxed(d, vrai, XB(58), 560, DARK, WHITE, maxw=880)
    handle(d)
    im.save(os.path.join(OUT, f"story_{i:02d}.png")); i += 1

# Story finale : CTA
im = gradient((240, 104, 160), (214, 60, 125)); d = ImageDraw.Draw(im)
y = boxed(d, "Laquelle on t'a déjà dite ?", XB(76), 420, DARK, WHITE)
y = boxed(d, "Écris-moi DÉCLIC en message", XB(60), y + 90, WHITE, DARK)
boxed(d, "et je t'envoie mon test gratuit pour comprendre ce qui bloque ta perte de poids", BD(44), y + 40, DARK, WHITE)
handle(d)
im.save(os.path.join(OUT, f"story_{i:02d}.png"))
