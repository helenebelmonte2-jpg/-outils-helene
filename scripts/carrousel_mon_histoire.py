from PIL import Image, ImageDraw, ImageFont, ImageOps
import sys, os
OUT = sys.argv[1]
W, H = 1080, 1350
CREAM = (255, 245, 248); PINK = (232, 80, 143); DARK = (43, 34, 40); SOFT = (250, 222, 233); WHITE=(255,255,255)
F = "/usr/share/fonts/opentype/inter/"
def font(n, s): return ImageFont.truetype(F + n, s)
XB = lambda s: font("Inter-ExtraBold.otf", s)
RG = lambda s: font("Inter-Medium.otf", s)

def rich_lines(d, text, f, maxw):
    # text: words, *mot* = pink. returns list of lines of (word, pink)
    lines, cur, w = [], [], 0
    space = d.textlength(" ", font=f)
    for para in text.split("\n"):
        for tok in para.split(" "):
            pink = tok.startswith("*") or (cur and cur[-1][2] and not cur[-1][0].endswith("*"))
            raw = tok
            word = tok.replace("*", "")
            tw = d.textlength(word, font=f)
            if cur and w + space + tw > maxw:
                lines.append(cur); cur, w = [], 0
            cur.append((word, None, raw)); w += (space if len(cur) > 1 else 0) + tw
        lines.append(cur); cur, w = [], 0
    # resolve pink spans
    out, inside = [], False
    for ln in lines:
        o = []
        for word, _, raw in ln:
            start = raw.startswith("*"); r2 = raw.rstrip(".,…:;!?"); end = r2.endswith("*") and len(r2) > 1
            p = inside or start
            o.append((word, p))
            if start and not end: inside = True
            elif end: inside = False
        out.append(o)
    return out

def draw_rich(d, text, f, y, color=DARK, maxw=880, lh=1.25, align="left", x0=100, accent=None):
    lines = rich_lines(d, text, f, maxw)
    space = d.textlength(" ", font=f)
    size = f.size
    for ln in lines:
        lw = sum(d.textlength(w, font=f) for w, _ in ln) + space * max(len(ln) - 1, 0)
        x = x0 if align == "left" else (W - lw) / 2
        for w, p in ln:
            d.text((x, y), w, font=f, fill=(accent or PINK) if p else color)
            x += d.textlength(w, font=f) + space
        y += size * lh
    return y

def base(i, n, bg=CREAM):
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    # dots
    tot = n * 26
    x = (W - tot) / 2
    for k in range(n):
        c = PINK if k == i else (SOFT if bg == CREAM else (255, 255, 255, 120))
        if bg != CREAM: c = WHITE if k == i else (240, 160, 195)
        d.ellipse((x, H - 70, x + 12, H - 58), fill=c); x += 26
    d.text((W / 2, H - 120), "@helene_belmonte", font=RG(28), fill=(PINK if bg == CREAM else WHITE), anchor="mm")
    return im, d

slides = [
 ("cover", "J'ai eu *peur de manger* pendant des années.", "Voici mon histoire"),
 ("txt", "01", "Adolescente, j'étais *très complexée.*\n\nAu lycée, j'ai pris *beaucoup de poids.*"),
 ("txt", "02", "Puis la vie a fait des siennes. Des *hauts*, des *bas*…\n\nEt la nourriture est devenue *mon refuge.*"),
 ("txt", "03", "Je ne mangeais plus parce que j'avais faim.\n\nJe mangeais *mes émotions* : le stress, la fatigue, la tristesse, parfois même la joie."),
 ("txt", "04", "J'ai fait appel à *plusieurs coachs.*\n\nJe perdais du poids… puis *je reprenais tout.*\n\nEt à chaque repas, *j'avais peur de manger.*"),
 ("txt", "05", "Aide-soignante, *horaires décalés*, journées à rallonge, repas sur le pouce…\n\nAucune méthode n'était faite pour *MA vie.*"),
 ("pink", "Le déclic", "J'ai enfin compris que la privation ne servait à rien."),
 ("photo", "", "Grâce au *rééquilibrage alimentaire*, j'ai perdu *du poids.*\n\nEt je ne l'ai *jamais repris.*"),
 ("photo", "Aujourd'hui", "Je n'ai *plus peur de manger.* Je me fais *plaisir à chaque repas.*\n\nEt j'ai trouvé un sport que j'aime, qui me donne envie de me lever le matin."),
 ("pink", "Ma plus belle décision", "Prendre du temps pour moi et investir en moi."),
 ("cta", "", ""),
]
n = len(slides)
for i, (kind, a, b) in enumerate(slides):
    if kind == "cover":
        im, d = base(i, n, PINK)
        d.text((100, 300), "MON HISTOIRE", font=XB(34), fill=(255, 210, 228))
        y = 380
        for ln in rich_lines(d, a, XB(92), 880):
            x = 100
            for w, p in ln:
                d.text((x, y), w, font=XB(92), fill=DARK if p else WHITE)
                x += d.textlength(w + " ", font=XB(92))
            y += 115
        d.rounded_rectangle((100, y + 60, 100 + d.textlength(b + "  →", font=XB(40)) + 60, y + 140), 40, fill=WHITE)
        d.text((130, y + 100), b + "  →", font=XB(40), fill=PINK, anchor="lm")
        R = 330; cx, cy = W - 100 - R // 2, H - 170 - R // 2      # sa photo de profil « jardin » en rond (26/11)
        pr = Image.open("contenus/photos/photo_profil_finale.jpg").convert("RGB").resize((R, R), Image.LANCZOS)
        mk = Image.new("L", (R, R), 0); ImageDraw.Draw(mk).ellipse((0, 0, R, R), fill=255)
        d.ellipse((cx - R // 2 - 10, cy - R // 2 - 10, cx + R // 2 + 10, cy + R // 2 + 10), fill=WHITE)
        im.paste(pr, (cx - R // 2, cy - R // 2), mk)
    elif kind == "txt":
        im, d = base(i, n)
        d.text((100, 200), a, font=XB(60 if len(a) > 2 else 110), fill=SOFT if len(a) <= 2 else PINK)
        draw_rich(d, b, XB(66), 380, maxw=880, lh=1.28)
    elif kind == "pink":
        im, d = base(i, n, PINK)
        d.text((W / 2, 380), a.upper(), font=XB(44), fill=(255, 210, 228), anchor="mm")
        d.text((W / 2, 300), "“", font=XB(200), fill=WHITE, anchor="mm")
        y = 480
        lines = rich_lines(d, b, XB(78), 860)
        for ln in lines:
            t = " ".join(w for w, _ in ln)
            d.text((W / 2, y), t, font=XB(78), fill=WHITE, anchor="mm"); y += 100
    elif kind == "photo":
        im, d = base(i, n)
        # slide 8 : photo salle ; slide « Aujourd'hui » : photo veste kaki bras croisés (choix 26/11)
        if a == "Aujourd'hui":
            ph = ImageOps.exif_transpose(Image.open("contenus/photos/photo_banniere_originale.jpg").convert("RGB")); fx, fw = 0.32, 0.56
        else:
            ph = ImageOps.exif_transpose(Image.open(os.path.join(os.path.dirname(OUT), "photo.jpg")).convert("RGB")); fx, fw = 0.47, 0.42
        pw, phh = ph.size
        PW = 500; cw = int(pw * fw); ch = min(phh, int(cw * H / PW)); cw = int(ch * PW / H)
        x0 = int(pw * fx); y0 = 0
        ph = ph.crop((x0, y0, x0 + cw, y0 + ch)).resize((PW, H), Image.LANCZOS)
        im.paste(ph, (W - PW, 0))
        d = ImageDraw.Draw(im)
        # redraw handle/dots on the left column
        d.rectangle((0, H - 140, W - PW, H), fill=CREAM)
        tot = n * 22; xx = ((W - PW) - tot) / 2
        for k in range(n):
            d.ellipse((xx, H - 70, xx + 10, H - 60), fill=PINK if k == i else SOFT); xx += 22
        d.text(((W - PW) / 2, H - 115), "@helene_belmonte", font=RG(26), fill=PINK, anchor="mm")
        if a: d.text((60, 200), a, font=XB(52), fill=PINK)
        draw_rich(d, b, XB(54 if not a else 46), 330, maxw=W - PW - 120, lh=1.25, x0=60)
    elif kind == "cta":
        im, d = base(i, n, PINK)
        d.text((W / 2, 300), "Tu te reconnais ?", font=XB(80), fill=WHITE, anchor="mm")
        y = draw_rich(d, "Ce n'est pas un manque de volonté. Ton poids raconte *ton histoire.*", RG(44), 420, color=WHITE, maxw=860, align="center", accent=DARK)
        d.rounded_rectangle((110, y + 50, W - 110, y + 300), 40, fill=WHITE)
        d.text((W / 2, y + 110), "Commente", font=XB(44), fill=DARK, anchor="mm")
        d.text((W / 2, y + 185), "DÉCLIC", font=XB(96), fill=PINK, anchor="mm")
        d.text((W / 2, y + 260), "et je t'envoie mon test gratuit", font=RG(36), fill=DARK, anchor="mm")
        d.text((W / 2, y + 400), "Pas de régime. Pas de frustration.", font=XB(42), fill=WHITE, anchor="mm")
        d.text((W / 2, y + 460), "Pas de culpabilité.", font=XB(42), fill=WHITE, anchor="mm")
    im.save(os.path.join(os.path.dirname(OUT), f"carrousel_{i+1:02d}.png"))
