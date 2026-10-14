"""make_vo: warm explainer voice lines -> work/vo_<scene>.wav (local Kokoro, no account).

The voice is a blend of Kokoro styles (TL.VOICE_MIX) spoken with English pronunciation, then warmed
with a gentle EQ. Run: python3 make_vo.py, then python3 scene.py audio.
"""
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

import timeline as TL

WARM = "equalizer=f=180:t=q:w=1:g=3,equalizer=f=3500:t=q:w=1.5:g=-2,highshelf=f=9000:g=-3,aecho=0.8:0.3:25:0.06"

c = Path.home() / ".cache/ideabro-vibe/kokoro"
k = Kokoro(str(c / "kokoro-v1.0.onnx"), str(c / "voices-v1.0.bin"))
style = sum(w * k.get_voice_style(v) for v, w in TL.VOICE_MIX.items())
for key, line in TL.VO:
    x, sr = k.create(line, voice=style, speed=TL.VO_SPEED, lang="en-us")
    x = np.asarray(x, np.float32)
    nz = np.flatnonzero(np.abs(x) > 0.01)
    x = x[max(0, nz[0] - 600): nz[-1] + 2400] if len(nz) else x
    raw = f"work/vo_{key}_raw.wav"
    sf.write(raw, x, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", WARM, "-ar", str(sr), "-ac", "1",
                    "-sample_fmt", "s16", f"work/vo_{key}.wav"], check=True)
    print(f"  {key:13s} {len(x) / sr:4.2f}s  {line}")
