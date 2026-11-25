"""Ajoute des sous-titres blancs « normaux » (sans couleur) sur une vidéo finie.
Le texte exact est fourni ; les temps viennent de la transcription automatique (alignement mot à mot).
Usage : python3 soustitres.py ENTREE.mp4 SORTIE.mp4 TEXTE.txt [Y]"""
import sys, re, json, subprocess, tempfile, difflib, numpy as np
from PIL import Image, ImageDraw, ImageFont
SRC, OUT, TXT = sys.argv[1:4]; Y = int(sys.argv[4]) if len(sys.argv) > 4 else 1700
W, H = 1080, 1920
F = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 54)
T = tempfile.mkdtemp()
norm = lambda w: re.sub(r"[^a-zàâäéèêëîïôöùûüçœ]", "", w.lower().replace("œ", "oe"))
words = open(TXT).read().split()
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
from faster_whisper import WhisperModel
segs, _ = WhisperModel("small", compute_type="int8").transcribe(a, language="fr", word_timestamps=True, condition_on_previous_text=False)
hyp = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words if w.word.strip()]
# Alignement texte exact <-> mots reconnus
sm = difflib.SequenceMatcher(None, [norm(w) for w in words], [norm(h[2]) for h in hyp], autojunk=False)
times = [None] * len(words)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1): times[i1 + k] = hyp[j1 + k][:2]
    elif tag == "replace" and j2 > j1:
        st, en = hyp[j1][0], hyp[j2 - 1][1]; n = i2 - i1
        for k in range(n): times[i1 + k] = (st + (en - st) * k / n, st + (en - st) * (k + 1) / n)
# combler les trous par interpolation
for i, t in enumerate(times):
    if t is None:
        prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
        nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), prev + 0.4)
        times[i] = (prev, max(prev + 0.15, nxt))
# Les temps de la transcription sont parfois en avance : un sous-titre ne commence jamais avant que la voix commence
hop = 160; env = np.array([np.sqrt(np.mean(a[k:k + hop] ** 2)) for k in range(0, len(a) - hop, hop)])
lvl = 20 * np.log10(env + 1e-9)
voice = [bool(np.all(lvl[k:k + 5] > -30)) for k in range(len(lvl))]   # vraie voix = au moins 50 ms au-dessus de -30 dB (pas un petit bruit)
def snap(t):
    k = int(t * 100)
    if k < len(voice) and any(voice[max(0, k - 3):k + 3]): return t
    for j in range(k, min(len(voice), k + 90)):
        if voice[j]: return j / 100
    return t
for i, (st, en) in enumerate(times):
    st2 = snap(st); times[i] = (st2, max(en, st2 + 0.15))
# Groupes de 1 à 3 mots (coupure sur la ponctuation et les pauses)
chunks, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    long = sum(len(words[j]) for j in cur) > 16
    pause = i + 1 < len(words) and times[i + 1][0] - times[i][1] > 0.25
    if len(cur) == 3 or long or w[-1] in ",.!?:" or pause or i == len(words) - 1:
        chunks.append(cur); cur = []
inputs, filt, last = [], [], "[0:v]"
for k, c in enumerate(chunks):
    txt = " ".join(words[j] for j in c); s0 = times[c[0]][0]
    e0 = times[c[-1]][1]; nxt = times[chunks[k + 1][0]][0] if k + 1 < len(chunks) else e0 + 0.4
    e0 = min(max(e0, s0 + 0.35), nxt) if nxt > s0 else e0
    im = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((W / 2, 60), txt, font=F, fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
    p = f"{T}/s{k}.png"; im.save(p); inputs += ["-i", p]
    filt.append(f"{last}[{k + 1}:v]overlay=0:{Y}:enable='between(t,{s0:.3f},{e0:.3f})'[o{k}]"); last = f"[o{k}]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, *inputs, "-filter_complex", ";".join(filt), "-map", last, "-map", "0:a",
                "-c:v", "libx264", "-crf", "23", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", OUT], check=True)
print("OK", OUT, len(chunks), "sous-titres")
