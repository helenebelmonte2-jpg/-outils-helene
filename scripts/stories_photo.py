"""Stories lifestyle : photo d'Hélène en plein écran + texte style natif Instagram.
Usage : python3 stories_photo.py <dossier_sortie> <contenu.py>
contenu.py : STORIES = [ {"photo": chemin, "y": 260, "blocs": [(texte, taille, style[, "b"])], "focus": 0.5}, ... ]"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os, sys, runpy
OUT, SRC = sys.argv[1], sys.argv[2]
STORIES = runpy.run_path(SRC)["STORIES"]
W, H = 1080, 1920
PINK = (232, 80, 143); DARK = (43, 34, 40); WHITE = (255, 255, 255)
F = "/usr/share/fonts/opentype/inter/"
FONT = {"xb": F + "Inter-ExtraBold.otf", "b": F + "Inter-Bold.otf"}
STY = {"white": (DARK, WHITE), "pink": (WHITE, PINK), "dark": (WHITE, DARK), "pinktxt": (PINK, WHITE)}

def load(path, focus):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    g = im.convert("L"); w, h = im.size
    rows = [y for y in range(0, h, 4) if max(g.getpixel((x, y)) for x in range(0, w, max(1, w // 40))) > 18]
    if rows and (rows[0] > h * 0.05 or rows[-1] < h * 0.95):   # capture d'écran avec bandes noires
        im = im.crop((0, rows[0] + 4, w, rows[-1] - 4))
    return im

def compose(im, focus, contain):
    if not contain:
        return ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(0.5, focus))
    from PIL import ImageFilter
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    fg = ImageOps.contain(im, (W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, int((H - fg.height) * focus)))
    return bg

def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if d.textlength(t, font=f) > maxw and cur: out.append(cur); cur = word
            else: cur = t
        out.append(cur)
    return out

for i, st in enumerate(STORIES, 1):
    im = compose(load(st["photo"], 0), st.get("focus", 0.5), st.get("contain", False)); d = ImageDraw.Draw(im)
    y = st.get("y", 260)
    for texte, taille, style, *poids in st["blocs"]:
        for a, b in ((" !", " !"), (" ?", " ?"), (" :", " :")): texte = texte.replace(a, b)
        f = ImageFont.truetype(FONT[poids[0] if poids else "xb"], taille); fg, bg = STY[style]
        for ln in wrap(d, texte, f, 860):
            tw = d.textlength(ln, font=f); x = (W - tw) / 2; pad = 22
            d.rounded_rectangle((x - pad, y - pad * 0.55, x + tw + pad, y + taille + pad * 0.75), 18, fill=bg)
            d.text((x, y), ln, font=f, fill=fg); y += taille * 1.32
        y += 40
    im.save(os.path.join(OUT, f"story_{i:02d}.jpg"), quality=92)
