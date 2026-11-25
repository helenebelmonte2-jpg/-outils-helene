"""Cartes « profil » (fin des Reels) à partir des captures d'écran de ses comptes, nettoyées :
sans les boutons que seule Hélène voit (bulle de pensée, +, appareil photo, menus).
Usage : python3 cartes_profil.py DOSSIER   (capture_facebook.png / capture_tiktok.png → profil_carte_facebook.png / _tiktok.png)"""
import sys, os
from PIL import Image, ImageDraw
D = sys.argv[1]
S = 1290 / 923                      # captures 1290 px, coordonnées mesurées sur l'affichage 923 px
P = lambda *v: tuple(round(x * S) for x in v)
PHOTO = "contenus/photos/photo_profil_finale.jpg"

def avatar(im, cx, cy, r, ring, bg):
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), fill=bg)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ring, width=8)
    ph = Image.open(PHOTO).convert("RGB").resize((2 * r - 28, 2 * r - 28), Image.LANCZOS)
    m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).ellipse((0, 0) + ph.size, fill=255)
    im.paste(ph, (cx - r + 14, cy - r + 14), m)

# ---- Facebook ----
fb = Image.open(os.path.join(D, "capture_facebook.png")).convert("RGB")
y0, y1 = P(143)[0], P(885)[0]
c = fb.crop((0, y0, 1290, y1)); W = 1290
panel = P(565)[0] - y0                                  # haut du panneau blanc
ban = Image.open("contenus/2026-11-24_couverture_facebook/couverture_melange_hd.png").convert("RGB")
h = panel + 60; w = round(ban.width * h / ban.height); ban = ban.resize((w, h), Image.LANCZOS)
c.paste(ban.crop((0, 0, W, h)), (0, 0))                 # sa bannière propre à la place du haut de la capture
d = ImageDraw.Draw(c)
d.rounded_rectangle((0, panel, W, panel + 200), 56, fill=(255, 255, 255))
cx, cy = P(462)[0], P(515)[0] - y0
avatar(c, cx, cy, P(170)[0], (170, 170, 175), (255, 255, 255))
x0, yy0, x1, yy1 = P(820, 700, 900, 780); d.rectangle((x0, yy0 - y0, x1, yy1 - y0), fill=(255, 255, 255))   # menu ⌄
c.save(os.path.join(D, "profil_carte_facebook.png"))

# ---- TikTok ----
tk = Image.open(os.path.join(D, "capture_tiktok.png")).convert("RGB")
y0, y1 = P(228)[0], P(622)[0]
c = tk.crop((0, y0, 1290, y1)); d = ImageDraw.Draw(c); bg = tk.getpixel((640, 470))
x0, yy0, x1, yy1 = P(262, 255, 300, 295); d.rectangle((x0, yy0 - y0, x1, yy1 - y0), fill=bg)            # flèche ▾
d.rectangle((P(640)[0], 0, 1290, P(500)[0] - y0), fill=bg)                                                 # bulle + badge
avatar(c, P(785)[0], P(365)[0] - y0, P(112)[0], (225, 225, 228), bg)
c.save(os.path.join(D, "profil_carte_tiktok.png"))
print("OK")
