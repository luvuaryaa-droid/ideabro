"""scene: daily sketchbook spread reel (3:4, 12 s). Every frame is a pure function of time t.

    python3 scene.py stills 1 4 7 11      # check frames -> out/stills/
    python3 scene.py audio                # soft piano -> work/mix.wav
    python3 scene.py render               # final -> out/sketchbook-pause.mp4

The artist's pages are shown exactly as photographed (no filters, no cropping of the art), as prints on cream paper.
Words are handwritten on screen (no voice, no captions).
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
from motion_kit import (Stage, clamp, ease_in_out_cubic, ease_out_cubic, grain, lerp, prog, rgb, shadow, text,  # noqa: E402
                        text_width, vignette)
from toon_kit import draw_on, paper_texture, smooth_path, stepped, wobble_points  # noqa: E402

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
B = S.brand
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
INK, OCHRE, TEAL, TERRA, BLUSH, LEAF = (rgb(B, r) for r in ("ink", "lime", "periwinkle", "orange", "blush", "ice"))
PAPER = paper_texture(W, H, B["colors"]["paper"], grain=0.07)
IMG = {k: skia.Image.open(v) for k, v in TL.PAGES.items()}
MARGIN = 0.06 * W          # feed safe zone: 6 % all round


# ------------------------------------------------------------------ helpers
def write(c, s, x, y, size, font, col, k, alpha=1.0):
    """Handwriting reveal, left to right, stepped like drawings."""
    if k <= 0:
        return
    w = text_width(s, size, font)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x - w / 2 - 20 * U, y - size, (w + 40 * U) * clamp(k), size * 2))
    text(c, s, x, y, size=size, font=font, fill=col, alpha=alpha)
    c.restore()


def fit(s, font, max_size, max_w=W - 2 * MARGIN):
    return min(max_size, max_w / max(1e-6, text_width(s, 100, font)) * 100)


def doodle(c, pts, col, width, k, ts, seed=0, closed=False):
    if k <= 0:
        return
    p = smooth_path(wobble_points(pts, 1.5 * U, ts, seed, closed), closed)
    c.drawPath(draw_on(p, k), skia.Paint(Color=col, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                                         StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, Alphaf=0.9))


def wavy(x0, x1, y, amp, n=14):
    return [(lerp(x0, x1, i / n), y + amp * math.sin(i * 1.3)) for i in range(n + 1)]


def sparkle(c, x, y, r, col, k, ts, seed):
    for a in range(4):
        ang = a * math.pi / 4
        doodle(c, [(x - r * math.cos(ang), y - r * math.sin(ang)), (x + r * math.cos(ang), y + r * math.sin(ang))],
               col, 4 * U, k, ts, seed + a)


def tape(c, x, y, w, h, rot, col):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.Paint(Color=col, Alphaf=0.6, AntiAlias=True))
    c.restore()


def print_(c, img, cx, cy, w, rot=0.0, scale=1.0, alpha=1.0, tape_col=None):
    """The page photo as a print: whole image (its own white mat included), soft shadow, washi tape."""
    if alpha <= 0:
        return
    h = w * img.height() / img.width()
    c.save()
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(scale, scale)
    shadow(c, -w / 2, -h / 2, w, h, 6 * U, blur=24 * U, dy=14 * U, alpha=0.25)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
    if tape_col is not None:
        tape(c, -w / 2 + 40 * U, -h / 2 + 6 * U, 130 * U, 36 * U, -36, tape_col)
        tape(c, w / 2 - 40 * U, -h / 2 + 6 * U, 130 * U, 36 * U, 36, tape_col)
    if alpha < 1:
        c.restore()
    c.restore()


def drift(lt, dur, amt=0.04):
    return 1 + amt * ease_in_out_cubic(prog(lt, 0, dur + TL.XFADE))


# ------------------------------------------------------------------ shots: (c, t, lt, dur, ts)
def sh_pause(c, t, lt, dur, ts):
    k = ease_out_cubic(prog(lt, 0, 0.9))
    print_(c, IMG["clock"], CX, 560 * U, 860 * U, rot=-1.5, scale=lerp(1.03, 1.0, k) * drift(lt, dur), alpha=k,
           tape_col=TEAL)
    write(c, TL.COPY["pause"], CX, 1180 * U, 130 * U, "display", INK, ease_in_out_cubic(prog(lt, 0.6, 1.0)))


def sh_breathe(c, t, lt, dur, ts):
    breath = math.sin(math.pi * clamp(lt / 3.0))          # one slow breath: in, then out
    k = ease_out_cubic(prog(lt, 0, 0.6))
    print_(c, IMG["toast"], CX, 560 * U, 830 * U, rot=1.4, scale=(1 + 0.035 * breath), alpha=k, tape_col=OCHRE)
    s = fit(TL.COPY["breathe"], "display", 104 * U)
    write(c, TL.COPY["breathe"], CX, 1180 * U, s, "display", INK, ease_in_out_cubic(prog(lt, 0.35, 1.1)))
    w = text_width(TL.COPY["breathe"], s, "display")
    doodle(c, wavy(CX - w / 2, CX + w / 2, 1245 * U, 6 * U), TEAL, 6 * U, prog(lt, 1.5, 0.8), ts, seed=5)


def sh_blessed(c, t, lt, dur, ts):
    k = ease_out_cubic(prog(lt, 0, 0.7))
    print_(c, IMG["spread"], CX, 600 * U, 980 * U, rot=-0.8, scale=lerp(0.97, 1.0, k), alpha=k, tape_col=BLUSH)
    s = fit(TL.COPY["blessed"], "display", 130 * U)
    write(c, TL.COPY["blessed"], CX, 1100 * U, s, "display", TERRA, ease_in_out_cubic(prog(lt, 0.4, 1.0)))
    for i, (x, y) in enumerate([(170, 1010), (910, 1015), (870, 1190)]):
        sparkle(c, x * U, y * U, 22 * U, OCHRE, prog(lt, 1.3 + 0.2 * i, 0.3), ts, seed=10 + 4 * i)


def sh_follow(c, t, lt, dur, ts):
    up = ease_in_out_cubic(prog(lt, 0, 0.8))               # the spread lifts to make room for the words
    print_(c, IMG["spread"], CX, lerp(600, 470, up) * U, 980 * U, rot=-0.8, scale=lerp(1.0, 0.92, up),
           tape_col=BLUSH)
    y = 905 * U
    write(c, TL.COPY["follow1"], CX, y, 74 * U, "body", INK, prog(lt, 0.15, 0.45))
    s2 = fit(TL.COPY["follow3"], "display", 104 * U)
    write(c, TL.COPY["follow2"], CX, y + 105 * U, s2, "display", INK, prog(lt, 0.55, 0.45))
    write(c, TL.COPY["follow3"], CX, y + 215 * U, s2, "display", TERRA, prog(lt, 0.95, 0.6))
    w3 = text_width(TL.COPY["follow3"], s2, "display")
    doodle(c, wavy(CX - w3 / 2, CX + w3 / 2, y + 275 * U, 6 * U), OCHRE, 6 * U, prog(lt, 1.5, 0.5), ts, seed=30)
    text(c, TL.COPY["handle"], CX, H - MARGIN - 20 * U, size=46 * U, font="body", fill=TEAL,
         alpha=ease_out_cubic(prog(lt, 1.7, 0.5)))


SHOT_FN = {"pause": sh_pause, "breathe": sh_breathe, "blessed": sh_blessed, "follow": sh_follow}


def draw_shot(c, idx, t):
    s, e, name = TL.SHOTS[idx]
    SHOT_FN[name](c, t, t - s, e - s, stepped(t, 12))


def draw(c, t):
    c.drawImage(PAPER, 0, 0)
    idx = next((i for i, (s, e, _) in enumerate(TL.SHOTS) if s <= t < e), len(TL.SHOTS) - 1)
    draw_shot(c, idx, t)
    s = TL.SHOTS[idx][0]
    # dissolve the outgoing shot; the spread -> follow change is one continuous move, so no dissolve there
    if idx > 0 and t - s < TL.XFADE and TL.SHOTS[idx][2] != "follow":
        a = 1 - ease_in_out_cubic((t - s) / TL.XFADE)
        c.saveLayerAlpha(None, int(255 * a))
        c.drawImage(PAPER, 0, 0)
        draw_shot(c, idx - 1, t)
        c.restore()
    fade_in = 1 - prog(t, 0, 0.5)
    fade_out = prog(t, TL.DURATION - 0.35, 0.35)
    for f in (fade_in, fade_out):
        if f > 0:
            c.saveLayerAlpha(None, int(255 * f))
            c.drawImage(PAPER, 0, 0)
            c.restore()


def post(a, t):
    return grain(vignette(a, 0.14), 0.018, int(t * TL.FPS))


def build_audio():
    subprocess.run([sys.executable, "piano.py", str(TL.DURATION + 0.2)], check=True)
    Path("work/cues.json").write_text(json.dumps(TL.cues(), indent=1))
    subprocess.run([sys.executable, "vibe/audio_kit.py", "mix", "work/cues.json", "-o", "work/mix.wav"], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        times = [float(x) for x in sys.argv[2:]] or [s + (e - s) * 0.8 for s, e, _ in TL.SHOTS]
        S.stills(draw, times, post=post)
    elif cmd == "audio":
        build_audio()
    elif cmd == "render":
        if not Path("work/mix.wav").exists():
            build_audio()
        S.render(draw, "out/sketchbook-pause.mp4", audio="work/mix.wav", post=post)
    else:
        sys.exit(__doc__)
