"""Détoure une photo portrait (MODNet, Apache-2.0) → PNG transparent.
Usage : python3 detourer.py entree.jpg sortie.png"""
import sys, numpy as np, onnxruntime as ort
from PIL import Image, ImageOps
from huggingface_hub import hf_hub_download
src, out = sys.argv[1], sys.argv[2]
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB"); W, H = im.size
sess = ort.InferenceSession(hf_hub_download("Xenova/modnet", "onnx/model.onnx"))
inp = sess.get_inputs()[0]
r = 512 / max(W, H); w, h = int(W * r) // 32 * 32, int(H * r) // 32 * 32
x = (np.asarray(im.resize((w, h), Image.BILINEAR), np.float32) / 255 - 0.5) / 0.5
x = x.transpose(2, 0, 1)[None]
m = sess.run(None, {inp.name: x})[0][0, 0]
alpha = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
res = im.copy(); res.putalpha(alpha); res.save(out)
print(im.size, inp.shape)
