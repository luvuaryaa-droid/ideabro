"""Builds work/vo.wav phrase by phrase so every caption has an exact time (no transcription needed).
    python3 build_vo.py [speed] [gap_scale]   -> work/vo.wav + work/vo.json
"""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf
sys.path.insert(0, "vibe")
from tts import ensure_models, trim
from kokoro_onnx import Kokoro

VOICE = "af_heart"
speed = float(sys.argv[1]) if len(sys.argv) > 1 else 0.9
gap_scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
k = Kokoro(*ensure_models())
lines = json.loads(Path("script.json").read_text())
chunks, meta, t, sr = [], [], 0.0, 24000
for pid, text, gap in lines:
    x, sr = k.create(text, voice=VOICE, speed=speed, lang="en-us")
    x = trim(np.asarray(x, np.float32), sr, pad=0.03)
    meta.append({"id": pid, "text": text, "s": round(t, 3), "e": round(t + len(x) / sr, 3)})
    chunks += [x, np.zeros(int(gap * gap_scale * sr), np.float32)]
    t += len(x) / sr + gap * gap_scale
full = np.concatenate(chunks)
sf.write("work/vo.wav", full, sr)
Path("work/vo.json").write_text(json.dumps({"voice": VOICE, "speed": speed, "duration": round(len(full) / sr, 3),
                                            "phrases": meta}, indent=1))
words = sum(len(m["text"].split()) for m in meta)
print(f"{len(meta)} phrases, {words} words, voice {len(full)/sr:.1f}s at speed {speed}")
