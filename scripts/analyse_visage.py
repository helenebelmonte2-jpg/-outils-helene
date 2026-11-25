import sys, json, subprocess, numpy as np, math
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src, out = sys.argv[1], sys.argv[2]
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 10; W, H = 540, 960
opt = vision.FaceLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path="face_landmarker.task"),
      output_face_blendshapes=True, output_facial_transformation_matrixes=True, num_faces=1)
lm = vision.FaceLandmarker.create_from_options(opt)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
res = []; i = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    img = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.frombuffer(b, np.uint8).reshape(H, W, 3))
    r = lm.detect(img); t = i / FPS; i += 1
    if not r.face_blendshapes: res.append([t, None]); continue
    bs = {c.category_name: c.score for c in r.face_blendshapes[0]}
    M = np.array(r.facial_transformation_matrixes[0])
    yaw = math.degrees(math.atan2(M[0, 2], M[2, 2])); pitch = math.degrees(math.asin(-M[1, 2]))
    blink = (bs["eyeBlinkLeft"] + bs["eyeBlinkRight"]) / 2
    down = (bs["eyeLookDownLeft"] + bs["eyeLookDownRight"]) / 2
    side = max(bs["eyeLookOutLeft"], bs["eyeLookOutRight"], bs["eyeLookInLeft"], bs["eyeLookInRight"])
    res.append([t, dict(blink=round(blink, 2), down=round(down, 2), side=round(side, 2), yaw=round(yaw, 1), pitch=round(pitch, 1))])
json.dump(res, open(out, "w"))
print(len(res))
