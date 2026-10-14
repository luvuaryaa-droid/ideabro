"""make_vo: warm voice for every tutorial line -> work/vo/<line>.wav + work/vo_durations.json.

Same voice as the launch Reel (Kokoro hf_beta, English pronunciation, warming EQ). Lines that already
exist with the same text are skipped, so re-running after a script edit only redoes what changed.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

import timeline as TL

WARM = "equalizer=f=180:t=q:w=1:g=3,equalizer=f=3500:t=q:w=1.5:g=-2,highshelf=f=9000:g=-3,aecho=0.8:0.3:25:0.06"
OUT = Path("work/vo")
OUT.mkdir(parents=True, exist_ok=True)
done_p = Path("work/vo_done.json")
done = json.loads(done_p.read_text()) if done_p.exists() else {}

c = Path.home() / ".cache/ideabro-vibe/kokoro"
k = Kokoro(str(c / "kokoro-v1.0.onnx"), str(c / "voices-v1.0.bin"))
style = sum(w * k.get_voice_style(v) for v, w in TL.VOICE_MIX.items())
durs = {}
for key, _c, _t, _v, lines in TL.SCRIPT:
    for i, (txt, _item) in enumerate(lines):
        lid = TL.line_id(key, i)
        wav = OUT / f"{lid}.wav"
        if done.get(lid) != txt or not wav.exists():
            x, sr = k.create(txt, voice=style, speed=TL.VO_SPEED, lang="en-us")
            x = np.asarray(x, np.float32)
            nz = np.flatnonzero(np.abs(x) > 0.01)
            x = x[max(0, nz[0] - 600): nz[-1] + 2400] if len(nz) else x
            raw = OUT / f"{lid}_raw.wav"
            sf.write(str(raw), x, sr)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", WARM, "-ac", "1",
                            "-sample_fmt", "s16", str(wav)], check=True)
            raw.unlink()
            done[lid] = txt
        info = sf.info(str(wav))
        durs[lid] = round(info.frames / info.samplerate, 3)
        print(f"  {lid:14s} {durs[lid]:5.2f}s  {txt[:70]}")
Path("work/vo_durations.json").write_text(json.dumps(durs, indent=1))
done_p.write_text(json.dumps(done, indent=1))
print(f"total speech {sum(durs.values()):.1f}s")
