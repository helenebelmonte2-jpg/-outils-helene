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

def photo_card(im, food, cy=1420, size=420):
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
 ("JUS D'ORANGE", 1.1, 2.36, 21.2, 24.32, False, "Trop sucré et pas du tout de fibres", 17.2),
 ("GRANOLA", 3.05, 3.93, 29.7, 30.65, False, "", 28.4),
 ("ŒUF", 4.85, 5.5, 35.7, 36.57, True, "", 68.6),
 ("SMOOTHIE", 6.14, 7.68, 39.2, 39.99, False, "", 37.6),
 ("AVOCAT", 8.32, 9.03, 44.9, 46.85, True, "Mais attention à la quantité", 70.0),
 ("FROMAGE BLANC", 10.05, 10.98, 50.85, 51.8, True, "", 18.2),
 ("GALETTE DE RIZ", 11.82, 12.7, 59.4, 62.74, False, "Ça n'a pas d'intérêt, ça ne cale vraiment pas", 9.0),
 ("RIZ BLANC", 13.51, 14.27, 68.15, 68.95, True, "", 8.0),
 # Salade : dans la vidéo, il n'y a pas de « pas autorisé » après « riz blanc » → on reprend celui du smoothie (39.2), avec un peu de temps après
 ("SALADE COMPOSÉE DU COMMERCE", 15.03, 16.94, 39.2, 40.5, False, "", 17.6),
]
OUTRO_VO = (16.6, 19.4); OUTRO = (83.7, 86.05)

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

def draw_hook(d):
    """Hook permanent en haut pendant tout le Reel (demande d'Hélène, 25/11) : plus aucun autre texte en haut."""
    box_text(d, 190, "Pour perdre du poids…", BD(52), WHITE, PINK)
    box_text(d, 290, "AUTORISÉ ou PAS AUTORISÉ ?", XB(62), WHITE, PINK, maxw=1010)

def overlay(name, draw, food=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if food: photo_card(im, food)
    d = ImageDraw.Draw(im); draw_hook(d); draw(d)
    p = f"{T}/{name}.png"; im.save(p); return p

def clean_track(src, name):
    """Débruitage + volume réglé UNE fois sur toute la piste (avant : réglé clip par clip, ce qui
    faisait monter le bruit de fond dans les passages sans parole). Entre les phrases : bruit baissé de 30 dB, avec fondus."""
    import re
    raw = f"{T}/{name}_raw.wav"; out = f"{T}/{name}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-af", "highpass=f=80,afftdn=nr=12:nf=-40:tn=1,loudnorm=I=-16:TP=-1.5",
                    "-ar", "48000", "-ac", "2", raw], check=True)
    log = subprocess.run(["ffmpeg", "-i", raw, "-af", "silencedetect=n=-42dB:d=0.35", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    expr = []
    for a, b in zip(st, en + [1e6]):
        a, b = a + 0.12, b - 0.12          # on garde 0,12 s autour de la voix
        if b - a > 0.1: expr.append(f"between(t,{a:.3f},{b:.3f})")
    vol = f"volume='if({'+'.join(expr) or '0'},0.03,1)':eval=frame" if expr else "anull"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", vol, out], check=True)
    return out

BASE_A = clean_track(BASE, "base_clean"); VO_A = clean_track(VO, "vo_clean")

# ---- Visage : jamais les yeux fermés, jamais le regard en bas / sur le côté (demande d'Hélène) ----
# visage_base.json = analyse image par image (scripts/analyse_visage.py, 30 i/s) : clignement, regard, rotation de la tête
import json, re
FACE = json.load(open(os.path.join(os.path.dirname(OUT), "visage_base.json"))); FFPS = 30
def bad_frame(d):
    return d is None or d["blink"] > 0.3 or d["side"] > 0.5 or d["yaw"] < -17 or d["yaw"] > 10 or d["down"] > 0.78
BAD = [bad_frame(d) for _, d in FACE]
BAD = [any(BAD[max(0, k - 2):k + 3]) for k in range(len(BAD))]      # marge de 2 images autour

def frame_plan(t0, dur):
    """Liste de (image source de début, image source de fin, nb d'images figées après) : chaque
    image « mauvaise » est remplacée par la dernière image où elle regarde bien la caméra."""
    f0 = round(t0 * FFPS); n = round(dur * FFPS); idx = list(range(f0, f0 + n))
    good = [k for k in idx if k < len(BAD) and not BAD[k]]
    if not good: return [(f0, f0 + n - 1, 0)], 0
    lead = idx.index(good[0])                 # début mauvais : on fige la 1re bonne image
    runs = []
    for k in idx[lead:]:
        if k < len(BAD) and not BAD[k]:
            if runs and runs[-1][2] == 0 and runs[-1][1] == k - 1: runs[-1][1] = k
            else: runs.append([k, k, 0])
        else: runs[-1][2] += 1
    return runs, lead

def speech_spans():
    log = subprocess.run(["ffmpeg", "-i", BASE, "-af", "silencedetect=n=-40dB:d=0.3", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [0.0] + [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)] + [1e6]
    return [(a - 0.3, b + 0.3) for a, b in zip(st, en) if b > a and not (a == 0.0 and b == en[0] and b > 5)]
SPEECH = speech_spans(); USED = []
def pick_listen(dur):
    """Plan d'écoute (pendant la voix off) : bouche fermée, yeux ouverts, face caméra, pas déjà utilisé."""
    n = round(dur * FFPS); best = None
    for f0 in range(round(1.0 * FFPS), min(len(BAD), round(90.5 * FFPS)) - n, 3):   # après 90,5 s elle s'avance pour couper la caméra
        t0, t1 = f0 / FFPS, (f0 + n) / FFPS
        if any(BAD[f0:f0 + n]): continue
        if any(a < t1 and t0 < b for a, b in SPEECH + USED): continue
        sc = sum(FACE[k][1]["blink"] + abs(FACE[k][1]["yaw"] + 6) / 20 + FACE[k][1]["side"] for k in range(f0, f0 + n)) / n
        if best is None or sc < best[0]: best = (sc, t0)
    if best is None:                       # plus de plan neuf : on accepte de réutiliser un plan
        USED.clear(); return pick_listen(dur)
    USED.append((best[1], best[1] + dur)); return best[1]

def clip(i, vt0, dur, png, audio):
    """vt0 = début de l'image dans la vidéo ; audio = ("base", t) | ("vo", t) | "mute"."""
    out = f"{T}/c{i:02d}.mp4"
    runs, lead = frame_plan(vt0, dur)
    f0 = round(vt0 * FFPS)
    parts = []; g = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FFPS},split={len(runs)}" + "".join(f"[s{j}]" for j in range(len(runs)))
    for j, (a, b, hold) in enumerate(runs):
        lp = f",tpad=start_mode=clone:start={lead}" if j == 0 and lead else ""
        hp = f",tpad=stop_mode=clone:stop={hold}" if hold else ""
        parts.append(f"[s{j}]trim=start_frame={a - f0}:end_frame={b - f0 + 1},setpts=PTS-STARTPTS{lp}{hp}[r{j}]")
    vf = g + ";" + ";".join(parts) + ";" + "".join(f"[r{j}]" for j in range(len(runs))) + f"concat=n={len(runs)}:v=1:a=0[v];[v][1:v]overlay=0:0[vo]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{vt0:.3f}", "-t", f"{dur + 0.2:.3f}", "-i", BASE, "-i", png]
    if audio == "mute":
        cmd += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
    else:
        cmd += ["-ss", f"{audio[1]:.3f}", "-t", f"{dur:.3f}", "-i", VO_A if audio[0] == "vo" else BASE_A]
    af = f"[2:a]afade=t=in:d=0.04,afade=t=out:st={max(dur-0.06,0):.3f}:d=0.06,apad[a]"
    cmd += ["-filter_complex", vf + ";" + af, "-map", "[vo]", "-map", "[a]", "-t", f"{dur:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", out]
    subprocess.run(cmd, check=True)
    print(f"clip {i:02d} image {vt0:.2f}s +{dur:.2f}s, images figées : {lead + sum(r[2] for r in runs)}")
    return out

clips = []
# Hook (muet, sans bruit de fond)
hook = overlay("hook", lambda d: None)
clips.append(clip(0, pick_listen(2.5), 2.5, hook, "mute"))
for k, (food, v0, v1, a0, a1, ok, note, l0) in enumerate(ITEMS, 1):
    q = overlay(f"q{k}", lambda d: None, food=food)
    clips.append(clip(len(clips), pick_listen(v1 - v0), v1 - v0, q, ("vo", v0)))
    clips.append(clip(len(clips), a0, a1 - a0, overlay(f"a{k}", lambda d: None, food=food), ("base", a0)))
# Outro : la voix off (« et t'abonner à mon compte »), puis ta réponse
# Outro : sans la voix off « et t'abonner à mon compte », directement ta phrase
def profil_card(im, cy=1340, w=980):
    """À la fin : son profil Instagram (capture nettoyée profil_carte.png), demande d'Hélène."""
    f = os.path.join(os.path.dirname(OUT), "profil_carte.png")
    if not os.path.exists(f): return
    pc = Image.open(f).convert("RGB"); h = round(pc.height * w / pc.width)
    pc = pc.resize((w, h), Image.LANCZOS); x, y = (W - w) // 2, cy - h // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x + 6, y + 12, x + w + 6, y + h + 12), 40, fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), 40, fill=255)
    im.paste(pc, (x, y), m)
    ImageDraw.Draw(im).rounded_rectangle((x, y, x + w, y + h), 40, outline=PINK, width=6)

def outro_png():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); profil_card(im); draw_hook(ImageDraw.Draw(im))
    p = f"{T}/oa.png"; im.save(p); return p
oa = outro_png()
# À la fin, elle regarde sur le côté pendant toute sa phrase → on garde SA voix, sur un plan où elle regarde la caméra
d1 = OUTRO[1] - OUTRO[0]; d2 = 90.3 - 89.45
clips.append(clip(len(clips), pick_listen(d1), d1, oa, ("base", OUTRO[0])))
clips.append(clip(len(clips), pick_listen(d2), d2, oa, ("base", 89.45)))   # « … de conseils »
lst = f"{T}/list.txt"; open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", OUT], check=True)
print("OK", OUT)
