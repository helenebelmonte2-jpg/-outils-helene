"""Reel « Autorisé ou pas autorisé ? » : voix off (aliment) puis réponse d'Hélène face caméra.
Usage : python3 montage_autorise.py BASE.mov VOIX.m4a SORTIE.mp4"""
import sys, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
BASE, VO, OUT = sys.argv[1:4]
W, H = 1080, 1920
PINK = (232, 80, 143); WHITE = (255, 255, 255); DARK = (43, 34, 40)
GREEN = (46, 160, 90); RED = (214, 58, 58)
F = "/usr/share/fonts/opentype/inter/"
XB = lambda s: ImageFont.truetype(F + "Inter-ExtraBold.otf", s)
BD = lambda s: ImageFont.truetype(F + "Inter-Bold.otf", s)
T = tempfile.mkdtemp()

# (aliment, voix off début/fin, réponse début/fin, verdict, précision)
ITEMS = [
 ("JUS D'ORANGE", 0.0, 2.3, 21.2, 24.4, False, "Trop sucré et pas du tout de fibres"),
 ("GRANOLA", 2.5, 3.8, 29.7, 31.6, False, ""),
 ("ŒUF", 4.5, 5.8, 35.7, 36.7, True, ""),
 ("SMOOTHIE", 6.1, 7.5, 39.0, 40.0, False, ""),
 ("AVOCAT", 8.2, 9.1, 44.9, 46.9, True, "Mais attention à la quantité"),
 ("FROMAGE BLANC", 9.7, 10.9, 50.7, 52.4, True, ""),
 ("GALETTE DE RIZ", 11.7, 12.7, 59.3, 62.8, False, "Ça n'a pas d'intérêt, ça ne cale vraiment pas"),
 ("RIZ BLANC", 13.3, 14.2, 67.2, 68.9, True, ""),
 ("SALADE COMPOSÉE DU COMMERCE", 15.0, 16.62, 69.7, 71.7, False, ""),
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

def overlay(name, draw):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); draw(d)
    p = f"{T}/{name}.png"; im.save(p); return p

def clip(i, src_t0, src_t1, png, audio="base", vo=None):
    out = f"{T}/c{i:02d}.mp4"; dur = src_t1 - src_t0
    vf = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30[v];[v][1:v]overlay=0:0[vo]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(src_t0), "-t", str(dur), "-i", BASE, "-i", png]
    if audio == "vo":
        cmd += ["-ss", str(vo[0]), "-t", str(dur), "-i", VO]
        af = "[2:a]loudnorm=I=-16:TP=-1.5,apad[a]"
    else:
        af = "[0:a]highpass=f=80,loudnorm=I=-16:TP=-1.5,apad[a]"
    cmd += ["-filter_complex", vf + ";" + af, "-map", "[vo]", "-map", "[a]", "-t", str(dur),
            "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", out]
    subprocess.run(cmd, check=True); return out

clips = []
# Hook
hook = overlay("hook", lambda d: (box_text(d, 190, "Pour perdre du poids…", BD(52), DARK, WHITE),
                                  box_text(d, 300, "AUTORISÉ ou PAS AUTORISÉ ?", XB(78), WHITE, PINK)))
clips.append(clip(0, 17.5, 20.0, hook))
for k, (food, v0, v1, a0, a1, ok, note) in enumerate(ITEMS, 1):
    d_vo = v1 - v0
    q = overlay(f"q{k}", lambda d, food=food: box_text(d, 200, food, XB(92), WHITE, PINK))
    clips.append(clip(len(clips), a0 - d_vo, a0, q, audio="vo", vo=(v0, v1)))
    def ans(d, food=food, ok=ok, note=note):
        y = box_text(d, 190, food, XB(70), PINK, WHITE)
        y = box_text(d, y + 30, "AUTORISÉ" if ok else "PAS AUTORISÉ", XB(96), WHITE, GREEN if ok else RED)
        if note: box_text(d, y + 20, note, BD(50), DARK, WHITE)   # sous le verdict, jamais en bas
    clips.append(clip(len(clips), a0, a1, overlay(f"a{k}", ans)))
# Outro : la voix off (« et t'abonner à mon compte »), puis ta réponse
# Outro : sans la voix off « et t'abonner à mon compte », directement ta phrase
clips.append(clip(len(clips), OUTRO[0], OUTRO[1], overlay("oa", lambda d: box_text(d, 200, "Abonne-toi à @helene_belmonte", XB(70), WHITE, PINK))))
lst = f"{T}/list.txt"; open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", OUT], check=True)
print("OK", OUT)
