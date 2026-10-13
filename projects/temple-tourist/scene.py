"""scene: graphics layer for ARTIST DATE | Playing Tourist in My Own City. Transparent overlay over work/picture.mp4.

    python3 prep_shots.py                  # picture: graded shots joined with dissolves -> work/picture.mp4
    python3 scene.py stills 2 6 21 40      # check graphics on top of the real picture -> out/stills/
    python3 scene.py audio                 # original clip sound only -> work/mix.wav
    python3 scene.py render                # overlay -> composite -> out/temple-tourist.mp4
    NO_CARDS=1 python3 scene.py render     # same film without the text cards (for the artist's own voiceover)

Layer: cinematic bars, the title, the script as text cards (no voiceover), end card, fade to dark.\nSound: the clips' own recorded sound only.
"""

import json
import os
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
    a = fade_window(t, 0.4, 3.3, 0.9, 0.6)
    if a > 0:
        soft_dark(c, a, H * 0.5, 420 * U)
        spaced(c, TL.TITLE[0], H * 0.44, 34 * U, SERIF, CREAM, a, 0.45)
        text(c, TL.TITLE[1], CX, H * 0.53, size=92 * U, font=SERIF_I, fill=CREAM, alpha=a)

    # the script as text cards (no voiceover): 1-2 lines of serif, lower third, soft shade behind
    for cs, ce, lines in ([] if os.environ.get("NO_CARDS") else TL.CARDS):
        if cs <= t < ce:
            ca = ease_out_cubic(prog(t, cs, 0.5)) * (1 - prog(t, ce - 0.35, 0.35))
            size = min(54 * U, min((W * 0.86) / max(1, text_width(ln, 100, SERIF_I)) * 100 for ln in lines))
            lh = size * 1.32
            y0 = H - TL.BAR * U - 70 * U - lh * (len(lines) - 1)
            soft_dark(c, ca * 0.9, y0 + lh * (len(lines) - 1) / 2, 140 * U + lh * len(lines))
            for j, ln in enumerate(lines):
                rise = (1 - ease_out_cubic(prog(t, cs + 0.12 * j, 0.6))) * 10 * U
                text(c, ln, CX, y0 + j * lh + rise, size=size, font=SERIF_I, fill=CREAM,
                     alpha=ca * ease_out_cubic(prog(t, cs + 0.12 * j, 0.5)))

    # end card over the still pond
    e0 = TL.END_CARD
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
    """No voiceover, no music: each shot's own recorded sound (natural speed), crossfaded under the dissolves,
    gently cleaned (rumble / hiss roll-off) and levelled to -16 LUFS so quiet ambience isn't pushed into hiss."""
    sys.path.insert(0, "vibe")
    from vibelib import loudnorm_filter
    sr = ak.SR
    n = int(TL.DURATION * sr)
    amb = np.zeros((n, 2), np.float32)
    for name, src, sin, s, e, drift, speed in TL.SHOTS:
        d = (e - s) + TL.XF
        tmp = Path(f"work/amb_{name}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sin}", "-t", f"{d:.3f}", "-i", f"raw/{src}.mp4",
                        "-vn", "-af", "highpass=f=70,lowpass=f=11000", "-ar", str(sr), "-ac", "2", str(tmp)], check=True)
        x = ak.read_audio(tmp)
        k = min(int(TL.XF * sr), len(x) // 2)
        env = np.ones(len(x), np.float32)
        env[:k] = np.linspace(0, 1, k)
        env[-k:] = np.minimum(env[-k:], np.linspace(1, 0, k))
        ak.place(amb, x * env[:, None], s, 0.0)
        tmp.unlink()
    fi, fo = int(0.6 * sr), int(1.5 * sr)                  # fade in from / out to silence with the picture
    amb[:fi] *= np.linspace(0, 1, fi)[:, None]
    amb[-fo:] *= np.linspace(1, 0, fo)[:, None]
    ak.write_wav("work/ambience_raw.wav", amb)
    if not getattr(TL, "VOICE_FILE", None):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/ambience_raw.wav", "-af",
                        loudnorm_filter("work/ambience_raw.wav", lufs=-16.0, tp=-1.5), "-ar", str(sr), "work/mix.wav"],
                       check=True)
        print("original sound -> work/mix.wav")
        return
    # the artist's own voiceover on top (cleaned), the original sound underneath, dipping while she speaks
    subprocess.run([sys.executable, "vibe/audio_kit.py", "voice", TL.VOICE_FILE, "-o", "work/voice.wav", "--denoise"],
                   check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/voice.wav", "-af",
                    loudnorm_filter("work/voice.wav", lufs=-16.0, tp=-2.0), "-ar", str(sr), "work/voice_lv.wav"],
                   check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/ambience_raw.wav", "-af",
                    loudnorm_filter("work/ambience_raw.wav", lufs=-24.0, tp=-3.0), "-ar", str(sr), "work/ambience.wav"],
                   check=True)
    cues = {"duration": TL.DURATION,
            "voice": {"file": "work/voice_lv.wav", "gain_db": 0, "t": TL.VOICE_OFFSET},
            "music": {"file": "work/ambience.wav", "gain_db": 0, "duck_db": -6, "fade_out": 1.5},
            "sfx": []}
    Path("work/cues.json").write_text(json.dumps(cues, indent=1))
    subprocess.run([sys.executable, "vibe/audio_kit.py", "mix", "work/cues.json", "-o", "work/mix_raw.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/mix_raw.wav", "-af",
                    loudnorm_filter("work/mix_raw.wav", lufs=-14.0, tp=-1.0), "-ar", str(sr), "work/mix.wav"],
                   check=True)
    print("voice + original sound -> work/mix.wav")


OUT = "out/temple-tourist_clean.mp4" if os.environ.get("NO_CARDS") else "out/temple-tourist.mp4"


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
                        "-shortest", "-movflags", "+faststart", OUT], check=True)
        print("done ->", OUT)
    else:
        sys.exit(__doc__)
