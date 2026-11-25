"""Reel « Autorisé ou pas autorisé ? » : voix off (aliment) puis réponse d'Hélène face caméra.
Usage : python3 montage_autorise.py BASE.mov VOIX.m4a SORTIE.mp4"""
import sys, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE, VO, OUT = sys.argv[1:4]
W, H = 1080, 1920
PINK = (232, 80, 143); WHITE = (255, 255, 255); DARK = (43, 34, 40)
GREEN = (46, 160, 90); RED = (214, 58, 58)
F = "/usr/share/fonts/opentype/inter/"
XB = lambda s: ImageFont.truetype(F + "Inter-ExtraBold.otf", s)
BD = lambda s: ImageFont.truetype(F + "Inter-Bold.otf", s)
T = tempfile.mkdtemp()
PHOTOS = os.path.join(os.path.dirname(OUT), "photos_aliments")
FILES = {"JUS D'ORANGE": "jus", "GRANOLA": "granola", "ŒUF": "oeuf", "SMOOTHIE": "smoothie", "AVOCAT": "avocat",
         "FROMAGE BLANC": "fromage_blanc", "GALETTE DE RIZ": "galette_riz", "RIZ BLANC": "riz_blanc", "SALADE COMPOSÉE DU COMMERCE": "salade_commerce"}

def photo_card(im, food, cy=1540, size=420):
    """Photo de l'aliment dans une carte blanche arrondie, au niveau de ses mains (demande d'Hélène)."""
    f = os.path.join(PHOTOS, FILES[food] + ".png")
    if not os.path.exists(f): return
    ph = Image.open(f).convert("RGB").resize((size, size), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
    x, y = (W - size) // 2, cy - size // 2; pad = 18
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x - pad + 8, y - pad + 14, x + size + pad + 8, y + size + pad + 14), 44, fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((x - pad, y - pad, x + size + pad, y + size + pad), 44, fill=(255, 255, 255, 255))
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size, size), 32, fill=255)
    im.paste(ph, (x, y), m)

# (aliment, voix off début/fin, réponse début/fin, verdict, précision)
# (aliment, voix off début/fin, réponse début/fin, verdict, précision, plan d'écoute)
# Le « plan d'écoute » = un moment où Hélène regarde bien la caméra (jamais en bas / sur le côté)
ITEMS = [
 ("JUS D'ORANGE", 0.0, 2.3, 21.2, 24.4, False, "Trop sucré et pas du tout de fibres", 17.2),
 ("GRANOLA", 2.5, 3.8, 29.7, 31.6, False, "", 28.4),
 ("ŒUF", 4.5, 5.8, 35.7, 36.7, True, "", 68.6),
 ("SMOOTHIE", 6.1, 7.5, 39.2, 40.0, False, "", 37.6),
 ("AVOCAT", 8.2, 9.1, 44.9, 46.9, True, "Mais attention à la quantité", 70.0),
 ("FROMAGE BLANC", 9.7, 10.9, 50.85, 52.4, True, "", 18.2),
 ("GALETTE DE RIZ", 11.7, 12.7, 59.4, 62.8, False, "Ça n'a pas d'intérêt, ça ne cale vraiment pas", 9.0),
 ("RIZ BLANC", 13.3, 14.2, 68.15, 69.0, True, "", 8.0),
 ("SALADE COMPOSÉE DU COMMERCE", 15.0, 16.62, 69.7, 71.7, False, "", 17.6),
]
OUTRO_VO = (16.6, 19.4); OUTRO = (83.7, 86.2)

def box_text(d, y, text, f, fg, bg, maxw=920, pad=26):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    for ln in lines:
        tw = d.textlength(ln, font=f); x = (W - tw) / 2
        d.rounded_rectangle((x - pad, y - pad * 0.6, x + tw + pad, y + f.size + pad * 0.8), 22, fill=bg)
        d.text((x, y), ln, font=f, fill=fg); y += f.size * 1.35
    return y

def overlay(name, draw, food=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if food: photo_card(im, food)
    d = ImageDraw.Draw(im); draw(d)
    p = f"{T}/{name}.png"; im.save(p); return p

def clip(i, src_t0, src_t1, png, audio="base", vo=None, freeze=0.0):
    out = f"{T}/c{i:02d}.mp4"; dur = src_t1 - src_t0
    pad = f",tpad=start_mode=clone:start_duration={freeze}" if freeze else ""
    vf = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30{pad}[v];[v][1:v]overlay=0:0[vo]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(src_t0 + freeze), "-t", str(dur), "-i", BASE, "-i", png]
    if freeze:
        cmd += ["-ss", str(src_t0), "-t", str(dur), "-i", BASE]
    CLEAN = "highpass=f=80,afftdn=nr=8:nf=-40:tn=1,loudnorm=I=-16:TP=-1.5"   # débruitage doux, sans « gate » (sinon la voix sonne coupée)
    if audio == "vo":
        cmd += ["-ss", str(vo[0]), "-t", str(dur), "-i", VO]
        af = f"[2:a]{CLEAN},afade=t=in:d=0.04,apad[a]"
    elif audio == "mute":
        cmd += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
        af = "[2:a]anull[a]"
    elif freeze:
        af = f"[2:a]{CLEAN},afade=t=in:d=0.04,afade=t=out:st={max(dur-0.06,0):.3f}:d=0.06,apad[a]"
    else:
        af = f"[0:a]{CLEAN},afade=t=in:d=0.04,afade=t=out:st={max(dur-0.06,0):.3f}:d=0.06,apad[a]"
    cmd += ["-filter_complex", vf + ";" + af, "-map", "[vo]", "-map", "[a]", "-t", str(dur),
            "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", out]
    subprocess.run(cmd, check=True); return out

clips = []
# Hook
hook = overlay("hook", lambda d: (box_text(d, 190, "Pour perdre du poids…", BD(52), DARK, WHITE),
                                  box_text(d, 300, "AUTORISÉ ou PAS AUTORISÉ ?", XB(78), WHITE, PINK)))
clips.append(clip(0, 7.5, 10.0, hook, audio="mute"))   # début sans le bruit de fond
for k, (food, v0, v1, a0, a1, ok, note, l0) in enumerate(ITEMS, 1):
    d_vo = v1 - v0
    q = overlay(f"q{k}", lambda d, food=food: box_text(d, 200, food, XB(92), WHITE, PINK), food=food)
    clips.append(clip(len(clips), l0, l0 + d_vo, q, audio="vo", vo=(v0, v1)))
    def ans(d, food=food, ok=ok, note=note):
        y = box_text(d, 190, food, XB(70), PINK, WHITE)
        y = box_text(d, y + 30, "AUTORISÉ" if ok else "PAS AUTORISÉ", XB(96), WHITE, GREEN if ok else RED)
        if note: box_text(d, y + 20, note, BD(50), DARK, WHITE)   # sous le verdict, jamais en bas
    fz = {"JUS D'ORANGE": 0.3, "FROMAGE BLANC": 0.5, "GALETTE DE RIZ": 0.55}.get(food, 0.0)   # elle tourne la tête juste avant : image figée face caméra
    clips.append(clip(len(clips), a0, a1 + 0.2, overlay(f"a{k}", ans, food=food), freeze=fz))
# Outro : la voix off (« et t'abonner à mon compte »), puis ta réponse
# Outro : sans la voix off « et t'abonner à mon compte », directement ta phrase
oa = overlay("oa", lambda d: box_text(d, 200, "Abonne-toi à @helene_belmonte", XB(70), WHITE, PINK))
clips.append(clip(len(clips), OUTRO[0], OUTRO[1], oa))
clips.append(clip(len(clips), 88.0, 90.5, oa))   # « … de conseils » (on saute le blanc au milieu)
lst = f"{T}/list.txt"; open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", OUT], check=True)
print("OK", OUT)
