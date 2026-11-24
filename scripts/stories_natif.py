"""Générateur de stories au style natif Instagram (texte avec fond arrondi par ligne).
Usage : python3 stories_natif.py <dossier_sortie> <fichier_contenu.py>
Le fichier de contenu définit STORIES = [ {"bg": "dark"|"pink", "blocs": [(texte, taille, style), ...]}, ... ]
style : "white" (texte foncé sur fond blanc), "pink" (blanc sur rose), "dark" (blanc sur foncé)."""
from PIL import Image, ImageDraw, ImageFont
import os, sys, runpy

OUT, SRC = sys.argv[1], sys.argv[2]
STORIES = runpy.run_path(SRC)["STORIES"]
W, H = 1080, 1920
PINK = (232, 80, 143); DARK = (43, 34, 40); WHITE = (255, 255, 255)
F = "/usr/share/fonts/opentype/inter/"
FONT = {"xb": F + "Inter-ExtraBold.otf", "b": F + "Inter-Bold.otf"}
STY = {"white": (DARK, WHITE), "pink": (WHITE, PINK), "dark": (WHITE, DARK), "pinktxt": (PINK, WHITE)}
BG = {"dark": ((58, 44, 52), (28, 20, 26)), "pink": ((240, 104, 160), (214, 60, 125))}

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

def gradient(c1, c2):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3)))
    return im

for i, st in enumerate(STORIES, 1):
    im = gradient(*BG[st["bg"]]); d = ImageDraw.Draw(im)
    y = st.get("y", 380)
    for texte, taille, style, *poids in st["blocs"]:
        f = ImageFont.truetype(FONT[poids[0] if poids else "xb"], taille)
        fg, bgc = STY[style]
        for ln in wrap(d, texte, f, 880):
            if not ln:
                y += taille * 0.6; continue
            tw = d.textlength(ln, font=f); x = (W - tw) / 2; pad = 22
            d.rounded_rectangle((x - pad, y - pad * 0.55, x + tw + pad, y + taille + pad * 0.75), 18, fill=bgc)
            d.text((x, y), ln, font=f, fill=fg)
            y += taille * 1.32
        y += 70
    d.text((W / 2, H - 260), "@helene_belmonte", font=ImageFont.truetype(FONT["b"], 30), fill=WHITE, anchor="mm")
    im.save(os.path.join(OUT, f"story_{i:02d}.png"))
