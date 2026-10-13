"""prep_shots: cut, grade and gently move every shot, then join them with dissolves -> work/picture.mp4

    python3 prep_shots.py

Each shot: letterbox crop -> lanczos upscale to 6 % over 1920x1080 -> warm nostalgic grade -> a slow drift
(crop window glides across the oversize frame) -> optional gentle slow motion. Shots overlap by XF for the dissolve.
"""
import subprocess
from pathlib import Path

import timeline as TL

OW, OH = int(TL.W * 1.06) // 2 * 2, int(TL.H * 1.06) // 2 * 2
MX, MY = OW - TL.W, OH - TL.H
Path("work/shots").mkdir(parents=True, exist_ok=True)


def drift_expr(kind, dur):
    p = f"min(t/{dur:.3f},1)"
    return {"l": (f"{MX}*(1-{p})", f"{MY}/2"), "r": (f"{MX}*{p}", f"{MY}/2"),
            "u": (f"{MX}/2", f"{MY}*(1-{p})"), "d": (f"{MX}/2", f"{MY}*{p}"),
            "in": (f"{MX}/2", f"{MY}/2")}[kind]


paths, durs = [], []
for i, (name, src, sin, s, e, drift, speed) in enumerate(TL.SHOTS):
    last = i == len(TL.SHOTS) - 1
    out_dur = (e - s) + (0 if last else TL.XF)
    src_dur = out_dur * speed
    x, y = drift_expr(drift, out_dur)
    zoom = ""
    if drift == "in":   # slow push-in: scale up over the shot, keep centred
        zoom = f",scale=w='{OW}*(1+0.05*min(t/{out_dur:.3f},1))':h=-2:eval=frame:flags=lanczos"
        x, y = "(iw-ow)/2", "(ih-oh)/2"
    rate = f"framerate=fps={TL.FPS}" if speed < 0.95 else f"fps={TL.FPS}"   # blend frames for smooth slow motion
    vf = (f"{TL.SRC_CROP},setpts={1/speed:.4f}*PTS,{rate},scale={OW}:{OH}:flags=lanczos{zoom},"
          f"crop={TL.W}:{TL.H}:'{x}':'{y}',{TL.GRADE},unsharp=5:5:0.4,format=yuv420p")
    out = f"work/shots/{i:02d}_{name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sin}", "-t", f"{src_dur + 0.1:.3f}", "-i", f"raw/{src}.mp4",
                    "-vf", vf, "-t", f"{out_dur:.3f}", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                    "-r", str(TL.FPS), out], check=True)
    paths.append(out)
    durs.append(out_dur)
    print(f"  {out}  {out_dur:.2f}s  (src {src}@{sin} x{speed})")

# join with dissolves
inputs, chain, prev, offset = [], [], "[0:v]", 0.0
for p in paths:
    inputs += ["-i", p]
for i in range(1, len(paths)):
    offset += durs[i - 1] - TL.XF
    lbl = f"[v{i}]"
    chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={TL.XF}:offset={offset:.3f}{lbl}")
    prev = lbl
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", prev,
                "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(TL.FPS),
                "work/picture.mp4"], check=True)
print("picture -> work/picture.mp4")
