"""Reel « Mythe ou vérité – En perte de poids » (TOFU) : voix off (affirmation) puis réponse d'Hélène face caméra.
Mise en page d'après le modèle choisi par Hélène (28/11) : bandeau rose « Mythe ou vérité », bandeau noir
« En perte de poids », « Mythe ✗ » à gauche et « Vérité ✓ » à droite (celui qu'elle choisit s'allume),
affirmation en gros texte blanc au niveau du buste.
Reprend les règles du Reel « Autorisé ou pas » : son nettoyé une fois, jamais d'image figée pendant qu'elle parle,
images où elle ferme les yeux / regarde ailleurs remplacées, son et image assemblés séparément au échantillon près.
Usage : python3 montage_mythe.py BASE.mov VOIX.m4a VISAGE.json SORTIE.mp4"""
import sys, os, re, json, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE, VO, FACEF, OUT = sys.argv[1:5]
W, H = 1080, 1920; FFPS = 30
PINK = (232, 64, 110); WHITE = (255, 255, 255); BLACK = (12, 12, 12)
GREEN = (60, 200, 90); RED = (226, 40, 40)
F = "/usr/share/fonts/opentype/inter/"
XB = lambda s: ImageFont.truetype(F + "Inter-ExtraBold.otf", s)
BD = lambda s: ImageFont.truetype(F + "Inter-Bold.otf", s)
T = tempfile.mkdtemp()

# (affirmation, voix off début/fin, réponse début/fin dans la vidéo, True = vérité)
ITEMS = [
 ("Boire de l'eau glacée fait brûler plus de calories", 0.75, 4.42, 5.37, 6.10, False),
 ("Le citron le matin fait fondre la graisse", 5.28, 8.12, 9.63, 10.42, False),
 ("Manger lentement aide à moins manger", 9.18, 11.69, 12.82, 13.61, True),
 ("Il existe un aliment brûle-graisse miracle", 12.78, 16.36, 16.53, 17.30, False),
 ("Il faut être parfaite tous les jours pour voir des résultats", 18.37, 21.82, 19.56, 20.35, False),
 ("L'alcool peut ralentir ta perte de poids", 23.31, 25.79, 27.04, 27.91, True),
 ("Se fixer des objectifs réalistes aide à tenir sur la durée", 26.97, 30.91, 34.56, 35.42, True),   # sa vraie réponse (29.49) : elle tourne la tête → « Vérité » de la question 9, face caméra
 ("La whey peut t'aider à atteindre tes besoins en protéines", 31.79, 37.09, 31.96, 32.86, True),
 ("Les régimes trop stricts font reprendre le poids perdu", 38.72, 42.97, 34.56, 35.42, True),
 ("Manger des légumes à chaque repas aide à être rassasiée", 44.42, 50.06, 27.04, 27.91, True),   # sa vraie réponse (37.29) : tête tournée → « Vérité » de la question 6
]

# ---------- habillage ----------
def glow_text(im, xy, text, font, glow, fill=WHITE, alpha=255, anchor="mm"):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text(xy, text, font=font, fill=glow + (255,), anchor=anchor, stroke_width=10, stroke_fill=glow + (255,))
    lay = lay.filter(ImageFilter.GaussianBlur(16))
    d = ImageDraw.Draw(lay); d.text(xy, text, font=font, fill=fill + (255,), anchor=anchor, stroke_width=2, stroke_fill=glow + (255,))
    if alpha < 255: lay.putalpha(lay.getchannel("A").point(lambda v: v * alpha // 255))
    im.alpha_composite(lay)

def cross(im, cx, cy, s, alpha):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for (a, b) in [((cx - s, cy - s), (cx + s, cy + s)), ((cx - s, cy + s), (cx + s, cy - s))]:
        d.line([a, b], fill=RED + (255,), width=int(s * 0.55))
        for p in (a, b): d.ellipse((p[0] - s * 0.27, p[1] - s * 0.27, p[0] + s * 0.27, p[1] + s * 0.27), fill=RED + (255,))
    if alpha < 255: lay.putalpha(lay.getchannel("A").point(lambda v: v * alpha // 255))
    im.alpha_composite(lay)

def check(im, cx, cy, s, alpha):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), int(s * 0.35), fill=(80, 190, 70, 255))
    pts = [(cx - s * 0.55, cy + s * 0.02), (cx - s * 0.15, cy + s * 0.45), (cx + s * 0.6, cy - s * 0.45)]
    d.line(pts, fill=WHITE + (255,), width=int(s * 0.28), joint="curve")
    if alpha < 255: lay.putalpha(lay.getchannel("A").point(lambda v: v * alpha // 255))
    im.alpha_composite(lay)

def header(im, state):
    d = ImageDraw.Draw(im)
    f1 = XB(84); t1 = "Mythe ou vérité"; w1 = d.textlength(t1, font=f1)
    d.rounded_rectangle(((W - w1) / 2 - 44, 150, (W + w1) / 2 + 44, 274), 30, fill=PINK + (255,))
    d.text((W / 2, 212), t1, font=f1, fill=WHITE, anchor="mm")
    f2 = XB(50); t2 = "En perte de poids"; w2 = d.textlength(t2, font=f2)
    d.rounded_rectangle(((W - w2) / 2 - 30, 274, (W + w2) / 2 + 30, 350), 18, fill=BLACK + (255,))
    d.text((W / 2, 312), t2, font=f2, fill=WHITE, anchor="mm")
    # Mythe ✗ (gauche) / Vérité ✓ (droite) : pendant sa réponse, le bon côté s'allume, l'autre s'efface
    am = 255 if state in (None, "M") else 70; av = 255 if state in (None, "V") else 70
    fm = XB(92 if state == "M" else 82); fv = XB(92 if state == "V" else 82)
    glow_text(im, (215, 412), "Mythe", fm, (240, 60, 120), alpha=am)
    cross(im, 430, 412, 34 if state == "M" else 30, am)
    glow_text(im, (800, 412), "Vérité", fv, (60, 220, 90), alpha=av)
    check(im, 1010, 412, 40 if state == "V" else 36, av)

def statement(im, text, y=1190):
    d = ImageDraw.Draw(im); f = XB(68)
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > 900 and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for k, ln in enumerate(lines): ds.text((W / 2 + 3, y + k * 84 + 5), ln, font=f, fill=(0, 0, 0, 200), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 200))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    for k, ln in enumerate(lines): d.text((W / 2, y + k * 84), ln, font=f, fill=WHITE, anchor="mm", stroke_width=2, stroke_fill=(30, 30, 30))

def overlay(name, text, state):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); header(im, state); statement(im, text)
    p = f"{T}/{name}.png"; im.save(p); return p

# ---------- son ----------
def clean_track(src, name):
    raw = f"{T}/{name}_raw.wav"; out = f"{T}/{name}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-af", "highpass=f=80,afftdn=nr=12:nf=-40:tn=1,loudnorm=I=-16:TP=-1.5",
                    "-ar", "48000", "-ac", "2", raw], check=True)
    log = subprocess.run(["ffmpeg", "-i", raw, "-af", "silencedetect=n=-42dB:d=0.35", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    expr = [f"between(t,{a + 0.12:.3f},{b - 0.12:.3f})" for a, b in zip(st, en + [1e6]) if b - a > 0.34]
    vol = f"volume='if({'+'.join(expr)},0.03,1)':eval=frame" if expr else "anull"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", vol, out], check=True)
    return out
BASE_A = clean_track(BASE, "base"); VO_A = clean_track(VO, "vo")
def vo_tight(k, v0, v1):
    """Phrase de la voix off sans les blancs de plus de 0,3 s (moins d'attente, moins d'images figées)."""
    log = subprocess.run(["ffmpeg", "-ss", f"{v0}", "-to", f"{v1}", "-i", VO_A, "-af", "silencedetect=n=-33dB:d=0.25", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    pieces, cur = [], 0.0
    for x, y in zip(st, en):
        if x > cur: pieces.append((cur, x + 0.1))
        cur = max(cur, y - 0.1)
    if cur < v1 - v0: pieces.append((cur, v1 - v0))
    if not pieces: pieces = [(0, v1 - v0)]
    sel = "+".join(f"between(t,{x:.3f},{y:.3f})" for x, y in pieces)
    out = f"{T}/vo_{k}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{v0}", "-to", f"{v1}", "-i", VO_A, "-af", f"aselect='{sel}',asetpts=N/SR/TB", out], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
    return out, d

# ---------- visage ----------
FACE = json.load(open(FACEF))
def bad_frame(d):
    return d is None or d["blink"] > 0.3 or d["side"] > 0.5 or d["yaw"] < -24 or d["yaw"] > 4 or d["down"] > 0.72
BAD = [bad_frame(d) for _, d in FACE]
BAD = [any(BAD[max(0, k - 2):k + 3]) for k in range(len(BAD))]
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", BASE, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                 capture_output=True).stdout, np.int16).astype(np.float32) / 32768
hop = 16000 // FFPS
RMS = [20 * np.log10(np.sqrt(np.mean(a[k * hop:(k + 1) * hop] ** 2)) + 1e-9) for k in range(len(a) // hop)]
SP = [r > -38 for r in RMS]
SPEAK = [any(SP[max(0, k - 4):k + 5]) for k in range(len(SP))]
BADQ = [any(BAD[max(0, k - 8):k + 9]) for k in range(len(BAD))]   # plans d'écoute : aucune mauvaise image, avec une marge de 8 images (tête qui se retourne)
BAD = [b and not (k < len(SPEAK) and SPEAK[k]) for k, b in enumerate(BAD)]   # quand elle parle : jamais figé

def frame_plan(t0, dur):
    f0 = round(t0 * FFPS); n = round(dur * FFPS); idx = list(range(f0, f0 + n))
    good = [k for k in idx if k < len(BAD) and not BAD[k]]
    if not good: return [[f0, f0 + n - 1, 0]], 0
    lead = idx.index(good[0]); runs = []
    for k in idx[lead:]:
        if k < len(BAD) and not BAD[k]:
            if runs and runs[-1][2] == 0 and runs[-1][1] == k - 1: runs[-1][1] = k
            else: runs.append([k, k, 0])
        else: runs[-1][2] += 1
    return runs, lead

ANSW = [(i[3] - 0.35, i[4] + 0.35) for i in ITEMS]; USED = []
_log = subprocess.run(["ffmpeg", "-i", BASE, "-map", "0:a", "-af", "silencedetect=n=-32dB:d=0.3", "-f", "null", "-"], capture_output=True, text=True).stderr
_st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", _log)]; _en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", _log)]
VOICE = [(b - 0.15, c + 0.15) for b, c in zip(_en, _st[1:])]      # moments où elle parle (entre deux silences)
def _best(n, strict=True):
    best = None
    for f0 in range(15, len(BADQ) - n - 15, 3):
        t0, t1 = f0 / FFPS, (f0 + n) / FFPS
        if any(x < t1 and t0 < y for x, y in ANSW + VOICE): continue
        if strict and any(BADQ[f0:f0 + n]): continue          # d'abord : uniquement des plans 100 % face caméra
        fr = [FACE[k][1] for k in range(f0, f0 + n)]
        sc = 20 * sum(BADQ[f0:f0 + n]) / n + sum(d["jaw"] + d["blink"] + abs(d["yaw"] + 8) / 25 for d in fr if d) / n
        sc += 1.5 * sum(max(0, min(t1, y) - max(t0, x)) for x, y in USED) / (n / FFPS)
        if best is None or sc < best[0]: best = (sc, t0, sum(BADQ[f0:f0 + n]) / n)
    if best is None and strict: return _best(n, False)
    if best is None: return (99, 1.0, 1.0)
    return best
BOOM = {}
def pick_listen(dur):
    """Plan long sans assez de bonnes images : « aller-retour » d'un bon plan deux fois plus court
    (elle écoute sans bouger : on ne voit pas la différence, et pas d'image figée)."""
    n = round(dur * FFPS); b = _best(n)
    if b[2] > 0:
        for k in (2, 3, 4):                     # aller-retour (ou aller-retour-aller…) d'un plan 100 % face caméra
            b2 = _best(n // k + 1)
            if b2[2] == 0:
                USED.append((b2[1], b2[1] + dur / k)); BOOM[round(b2[1], 3)] = k; return b2[1]
    USED.append((b[1], b[1] + dur)); return b[1]
def _old_pick_listen(dur):
    """Plan d'écoute pendant la voix off : en dehors de ses réponses, le plus de bonnes images possible
    (yeux ouverts, face caméra, bouche fermée) ; les quelques défauts restants sont remplacés par une bonne image."""
    n = round(dur * FFPS); best = None
    for f0 in range(15, len(BADQ) - n - 15, 3):
        t0, t1 = f0 / FFPS, (f0 + n) / FFPS
        if any(x < t1 and t0 < y for x, y in ANSW + VOICE): continue
        fr = [FACE[k][1] for k in range(f0, f0 + n)]
        sc = 20 * sum(BADQ[f0:f0 + n]) / n + sum(d["jaw"] + d["blink"] + abs(d["yaw"] + 8) / 25 for d in fr if d) / n
        sc += 1.5 * sum(max(0, min(t1, y) - max(t0, x)) for x, y in USED) / dur     # éviter de répéter le même plan
        if best is None or sc < best[0]: best = (sc, t0)
    USED.append((best[1], best[1] + dur)); return best[1]

def clip(i, vt0, dur, png, audio):
    out = f"{T}/c{i:02d}.mp4"; dur = round(dur * FFPS) / FFPS
    runs, lead = frame_plan(vt0, dur); f0 = round(vt0 * FFPS)
    g = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FFPS},split={len(runs)}" + "".join(f"[s{j}]" for j in range(len(runs)))
    parts = []
    if BOOM.get(round(vt0, 3)) and audio[0] != "base":
        kk = BOOM[round(vt0, 3)]; nf = round(dur * FFPS); h = nf // kk + 1
        g = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FFPS},trim=end_frame={h},setpts=PTS-STARTPTS,split={kk}" + "".join(f"[s{j}]" for j in range(kk))
        parts = [f"[s{j}]{'reverse' if j % 2 else 'null'},setpts=PTS-STARTPTS[r{j}]" for j in range(kk)]; runs = [[f0, f0 + h - 1, 0]]; lead = 0
        vf = g + ";" + ";".join(parts) + ";" + "".join(f"[r{j}]" for j in range(kk)) + f"concat=n={kk}:v=1:a=0,trim=end_frame={nf}[v];[v][1:v]overlay=0:0[vo]"
    for j, (x, y, hold) in enumerate(runs):
        opts = ([f"start_mode=clone:start={lead}"] if j == 0 and lead else []) + ([f"stop_mode=clone:stop={hold}"] if hold else [])
        tp = (",tpad=" + ":".join(opts)) if opts else ""          # UN SEUL tpad par morceau
        parts.append(f"[s{j}]trim=start_frame={x - f0}:end_frame={y - f0 + 1},setpts=PTS-STARTPTS{tp}[r{j}]")
    if not (BOOM.get(round(vt0, 3)) and audio[0] != "base"): vf = g + ";" + ";".join(parts) + ";" + "".join(f"[r{j}]" for j in range(len(runs))) + f"concat=n={len(runs)}:v=1:a=0[v];[v][1:v]overlay=0:0[vo]"
    lag = 0.025 if audio[0] == "base" else 0.0
    src_a = {"vo": VO_A, "base": BASE_A}.get(audio[0], audio[0])
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{vt0:.3f}", "-t", f"{dur + 0.2:.3f}", "-i", BASE, "-i", png,
           "-ss", f"{audio[1] + lag:.3f}", "-t", f"{dur:.3f}", "-i", src_a]
    ns = round(dur * 48000)
    af = f"[2:a]aresample=48000,afade=t=in:d=0.04,afade=t=out:st={max(dur - 0.06, 0):.3f}:d=0.06,apad,atrim=end_sample={ns}[a]"
    cmd += ["-filter_complex", vf + ";" + af, "-map", "[vo]", "-frames:v", str(round(dur * FFPS)),
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-an", out,
            "-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out[:-4] + ".wav"]
    subprocess.run(cmd, check=True)
    nb = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames",
                             "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip())
    assert nb == round(dur * FFPS), f"clip {i} : {nb} images au lieu de {round(dur * FFPS)}"
    print(f"clip {i:02d} {audio[0]} image {vt0:.2f}s +{dur:.2f}s, figées : {lead + sum(r[2] for r in runs)}")
    return out

clips = []
for k, (txt, v0, v1, a0, a1, ok) in enumerate(ITEMS, 1):
    vf, vd = vo_tight(k, v0, v1)
    clips.append(clip(len(clips), pick_listen(vd), vd, overlay(f"q{k}", txt, None), (vf, 0.0)))
    clips.append(clip(len(clips), a0, a1 - a0, overlay(f"a{k}", txt, "V" if ok else "M"), ("base", a0)))
open(f"{T}/v.txt", "w").write("".join(f"file '{c}'\n" for c in clips))
open(f"{T}/a.txt", "w").write("".join(f"file '{c[:-4]}.wav'\n" for c in clips))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{T}/v.txt", "-f", "concat", "-safe", "0", "-i", f"{T}/a.txt",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
print("OK", OUT)
