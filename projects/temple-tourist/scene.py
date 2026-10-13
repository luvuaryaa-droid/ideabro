"""scene: graphics layer for ARTIST DATE | Playing Tourist in My Own City. Transparent overlay over work/picture.mp4.

    python3 prep_shots.py                  # picture: graded shots joined with dissolves -> work/picture.mp4
    python3 scene.py stills 2 6 21 40      # check graphics on top of the real picture -> out/stills/
    python3 scene.py audio                 # voice + piano + temple ambience -> work/mix.wav
    python3 scene.py render                # overlay -> composite -> out/temple-tourist.mp4

Layer: cinematic bars, the title, captions in the bottom bar (exact phrase times), end card, fade to dark.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
import audio_kit as ak  # noqa: E402
from motion_kit import Stage, clamp, ease_out_cubic, prog, rgb, text, text_width  # noqa: E402

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
CREAM = rgb("#F6ECDC")
BLACK = skia.Color(10, 8, 6)
SERIF, SERIF_I = "InstrumentSerif-400.ttf", "InstrumentSerif-400-italic.ttf"


def fade_window(t, s, e, fin=0.6, fout=0.6):
    return ease_out_cubic(prog(t, s, fin)) * (1 - prog(t, e - fout, fout))


def soft_dark(c, a, cy, h):
    """A soft dark band behind title text so it reads over any shot."""
    if a <= 0:
        return
    sh = skia.GradientShader.MakeLinear([skia.Point(0, cy - h / 2), skia.Point(0, cy + h / 2)],
                                        [skia.Color(10, 8, 6, 0), skia.Color(10, 8, 6, int(110 * a)),
                                         skia.Color(10, 8, 6, 0)], [0.0, 0.5, 1.0])
    c.drawRect(skia.Rect.MakeXYWH(0, cy - h / 2, W, h), skia.Paint(Shader=sh))


def spaced(c, s, y, size, font, col, alpha, tracking):
    text(c, s, CX, y, size=size, font=font, fill=col, alpha=alpha, tracking=tracking)


def draw(c, t):
    c.clear(skia.ColorTRANSPARENT)
    bars = skia.Paint(Color=BLACK)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, TL.BAR * U), bars)
    c.drawRect(skia.Rect.MakeXYWH(0, H - TL.BAR * U, W, TL.BAR * U), bars)

    # title over the opening shot
    a = fade_window(t, 0.5, 3.6, 0.9, 0.7)
    if a > 0:
        soft_dark(c, a, H * 0.5, 420 * U)
        spaced(c, TL.TITLE[0], H * 0.44, 34 * U, SERIF, CREAM, a, 0.45)
        text(c, TL.TITLE[1], CX, H * 0.53, size=92 * U, font=SERIF_I, fill=CREAM, alpha=a)

    # captions in the bottom bar, one at a time, exactly on their phrase
    caps = sorted(TL.CAPTIONS)
    for i, (s, e, txt) in enumerate(caps):
        nxt = caps[i + 1][0] - 0.1 if i + 1 < len(caps) else TL.DURATION
        end = min(e + 0.4, nxt)
        if s - 0.1 <= t < end:
            ca = ease_out_cubic(prog(t, s - 0.1, 0.2)) * (1 - prog(t, end - 0.2, 0.2))
            size = min(42 * U, (W * 0.9) / max(1, text_width(txt, 100, SERIF_I)) * 100)
            text(c, txt, CX, H - TL.BAR * U / 2, size=size, font=SERIF_I, fill=CREAM, alpha=0.95 * ca)

    # end card over the still pond
    e0 = TL.SHOTS[-1][3] + 0.5
    a = fade_window(t, e0, TL.DURATION - 0.3, 0.9, 0.01)
    if a > 0:
        soft_dark(c, a, H * 0.5, 380 * U)
        spaced(c, TL.TITLE[0], H * 0.46, 40 * U, SERIF, CREAM, a, 0.45)
        text(c, TL.HANDLE, CX, H * 0.545, size=44 * U, font=SERIF_I, fill=CREAM, alpha=0.9 * a)

    f = prog(t, TL.DURATION - 0.9, 0.9)                     # close to dark
    if f > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=BLACK, Alphaf=clamp(f)))
    f0 = 1 - prog(t, 0, 0.6)                                 # open from dark
    if f0 > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=BLACK, Alphaf=clamp(f0)))


def build_audio():
    """Voice on top, soft piano under it (ducked), and each shot's own ambience crossfaded quietly beneath."""
    sr = ak.SR
    n = int(TL.DURATION * sr)
    amb = np.zeros((n, 2), np.float32)
    for name, src, sin, s, e, drift, speed in TL.SHOTS:
        d = (e - s) + TL.XF
        tmp = Path(f"work/amb_{name}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sin}", "-t", f"{d * speed:.3f}", "-i", f"raw/{src}.mp4",
                        "-vn", "-af", f"atempo={max(0.5, speed):.3f},highpass=f=90,lowpass=f=9000",
                        "-ar", str(sr), "-ac", "2", str(tmp)], check=True)
        x = ak.read_audio(tmp)
        k = int(TL.XF * sr)
        env = np.ones(len(x), np.float32)
        env[:k] = np.linspace(0, 1, min(k, len(x)))
        env[-k:] = np.minimum(env[-k:], np.linspace(1, 0, k))
        ak.place(amb, x * env[:, None], s, 0.0)
        tmp.unlink()
    ak.write_wav("work/ambience.wav", amb)
    subprocess.run([sys.executable, "../sketchbook-pause/piano.py", str(TL.DURATION + 0.5), "8", "F"], check=True,
                   cwd=".")
    cues = {"duration": TL.DURATION,
            "voice": {"file": "work/vo.wav", "gain_db": 0, "t": TL.VO_START},
            "music": {"file": "work/piano.wav", "gain_db": -12, "duck_db": -6, "fade_out": 2.5},
            "tracks": [{"file": "work/ambience.wav", "t": 0.0, "gain_db": -4}],
            "sfx": []}
    Path("work/cues.json").write_text(json.dumps(cues, indent=1))
    subprocess.run([sys.executable, "vibe/audio_kit.py", "mix", "work/cues.json", "-o", "work/mix.wav"], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        times = [float(x) for x in sys.argv[2:]] or [2.0, 6.0, 21.0, 40.5]
        S.stills(draw, times, under="work/picture.mp4")
    elif cmd == "audio":
        build_audio()
    elif cmd == "render":
        if not Path("work/mix.wav").exists():
            build_audio()
        S.render(draw, "work/overlay.mov", alpha=True)
        subprocess.run([sys.executable, "vibe/overlay.py", "work/picture.mp4", "work/overlay.mov",
                        "-o", "work/composite.mp4"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/composite.mp4", "-i", "work/mix.wav",
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-movflags", "+faststart", "out/temple-tourist.mp4"], check=True)
        print("done -> out/temple-tourist.mp4")
    else:
        sys.exit(__doc__)
