"""Monte un MOFU au format option C (structure Jonathan + rose Hélène).
Usage : python3 mofu.py SOURCE DEBUT FIN "Ligne 1 du hook" "Ligne 2 du hook :" SORTIE.mp4 [mots_roses]
- Les mots du hook entre [crochets] passent dans un petit bandeau rose. Ex. : "Tu as [TOUT essayé] pour maigrir ?"
- mots_roses : liste séparée par des virgules (mots du sous-titre à afficher en rose).
- Source horizontale (YouTube). Sous-titres mot à mot générés automatiquement (faster-whisper)."""
import sys, os, re, subprocess, tempfile, numpy as np
from PIL import Image, ImageDraw, ImageFont

src, t0, t1, h1, h2, out = sys.argv[1:7]
pinkwords = {w.strip().lower() for w in (sys.argv[7] if len(sys.argv) > 7 else "").split(",") if w.strip()}
t0, t1 = float(t0), float(t1)
W, H = 1080, 1920; VY0, VH = 607, 718
PINK = (232, 80, 143); WHITE = (255, 255, 255)
F = "/usr/share/fonts/opentype/inter/"
FB = ImageFont.truetype(F + "Inter-Bold.otf", 46)
FS = ImageFont.truetype(F + "Inter-Bold.otf", 44)
tmp = tempfile.mkdtemp()

# 1. Fond noir + hook (image fixe)
bg = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(bg)
def hook_line(y, text):
    parts = [(p, i % 2 == 1) for i, p in enumerate(re.split(r"\[|\]", text)) if p]
    sp = 10
    tw = sum(d.textlength(p, font=FB) + (2 * sp if k else 0) for p, k in parts); x = (W - tw) / 2
    for p, k in parts:
        w = d.textlength(p, font=FB)
        if k:
            x += sp; d.rounded_rectangle((x - 12, y - 10, x + w + 12, y + 58), 14, fill=PINK)
            d.text((x, y), p, font=FB, fill=WHITE); x += w + sp
        else:
            d.text((x, y), p, font=FB, fill=WHITE); x += w
hook_line(450, h1); hook_line(525, h2)
bg.save(f"{tmp}/bg.png")

# 2. Transcription mot à mot (ou réutilisation d'une transcription existante : variable WORDS=transcript.json)
if os.environ.get("WORDS"):
    import json
    words = [(w[0] - t0, w[1] - t0, w[2].strip()) for sg in json.load(open(os.environ["WORDS"])) for w in sg["words"]
             if w[0] >= t0 - 0.05 and w[1] <= t1 + 0.05 and w[2].strip()]
else:
  audio = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", src,
    "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
  from faster_whisper import WhisperModel
  model = WhisperModel("small", compute_type="int8")
  segs, _ = model.transcribe(audio, language="fr", word_timestamps=True)
  words = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words if w.word.strip()]

# 2b. Recoller les morceaux de mots coupés par la transcription (« aujourd 'hui », « j 'ai »)
merged = []
for w in words:
    if merged and (w[2][:1] in "'’-" or merged[-1][2][-1:] in "'’"):
        merged[-1] = (merged[-1][0], w[1], merged[-1][2] + w[2])
    else:
        merged.append(w)
words = [(a, b, t.replace(" '", "'")) for a, b, t in merged]

# 3. Sous-titres : 1 à 2 mots par image (PNG transparents) + liste d'overlays
chunks, i = [], 0
while i < len(words):
    a = words[i]; txt = a[2]; end = a[1]
    if i + 1 < len(words) and len(a[2]) + len(words[i + 1][2]) <= 12 and words[i + 1][0] - a[1] < 0.15:
        txt += " " + words[i + 1][2]; end = words[i + 1][1]; i += 1
    chunks.append((a[0], end, txt)); i += 1
inputs, filters, last = [], [], "[v]"
for k, (s, e, txt) in enumerate(chunks):
    im = Image.new("RGBA", (500, 80), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    key = re.sub(r"[^\wàâäéèêëîïôöùûüç'-]", "", txt.lower())
    col = PINK if any(p in key for p in pinkwords) else WHITE
    dd.text((250 + 2, 42 + 3), txt, font=FS, fill=(0, 0, 0, 120), anchor="mm")
    dd.text((250, 42), txt, font=FS, fill=col, anchor="mm", stroke_width=3, stroke_fill=(30, 20, 25, 230))
    im.save(f"{tmp}/s{k}.png"); inputs += ["-i", f"{tmp}/s{k}.png"]
    nxt = chunks[k + 1][0] if k + 1 < len(chunks) else e + 0.3
    filters.append(f"{last}[{k + 2}:v]overlay=530:1015:enable='between(t,{s:.3f},{min(nxt - 0.01, e + 0.6):.3f})'[o{k}]"); last = f"[o{k}]"

crop = os.environ.get("CROP")  # ex. "812:530:250:0" pour enlever des sous-titres incrustés
fc = (f"[0:v]{'crop=' + crop + ',' if crop else ''}scale={W}:{VH}:force_original_aspect_ratio=increase,crop={W}:{VH},setsar=1[vid];"
      f"[1:v][vid]overlay=0:{VY0}[v];" + ";".join(filters))
cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-to", str(t1), "-i", src, "-loop", "1", "-i", f"{tmp}/bg.png",
       *inputs, "-filter_complex", fc, "-map", last if filters else "[v]", "-map", "0:a?", "-shortest",
       "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True)
print("OK", out, len(chunks), "sous-titres")
