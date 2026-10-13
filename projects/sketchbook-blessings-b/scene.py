"""scene: daily sketchbook reel "unexpected blessings", version B (3:4, 14 s). Every frame is a pure function of t.

    python3 scene.py stills 1 4 8 12      # check frames -> out/stills/
    python3 scene.py audio                # soft piano (C major) -> work/mix.wav
    python3 scene.py render               # final -> out/sketchbook-blessings-b.mp4

Look: warm cream page; the artist's pages (untouched) revealed through a field of growing dots, a slow glide along
the wide spread, the three pages fanned together; DM Serif Display with soft lowercase Inter Tight.
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
from motion_kit import (Stage, clamp, ease_in_out_cubic, ease_out_back, ease_out_cubic, grain, lerp, prog,  # noqa: E402
                        rgb, shadow, text_width, typeface, vignette)
from toon_kit import paper_texture  # noqa: E402

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
CREAM, INK, GOLD, BLUE = rgb(TL.CREAM), rgb(TL.INK), rgb(TL.GOLD), rgb(TL.BLUE)
PAPER = paper_texture(W, H, TL.CREAM, grain=0.05)
IMG = {k: skia.Image.open(v) for k, v in TL.PAGES.items()}
SAMPLING = skia.SamplingOptions(skia.CubicResampler.Mitchell())
MARGIN = 0.07 * W


# ------------------------------------------------------------------ type
def line(c, s, cx, y, size, font, col, k, rise=16):
    """Whole line fades and rises into place (k = 0..1)."""
    if k <= 0:
        return
    f = skia.Font(typeface(font), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    w = f.measureText(s)
    m = f.getMetrics()
    p = skia.Paint(Color=col, AntiAlias=True)
    p.setAlphaf(clamp(k))
    c.drawString(s, cx - w / 2, y - (m.fAscent + m.fDescent) / 2 + (1 - ease_out_cubic(k)) * rise * U, f, p)


def words(c, s, cx, y, size, font, col, t0, lt, each=0.12, dur=0.5):
    """Word-by-word fade-in, centred."""
    f = skia.Font(typeface(font), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    parts = s.split(" ")
    sp = f.measureText(" ")
    widths = [f.measureText(p) for p in parts]
    x = cx - (sum(widths) + sp * (len(parts) - 1)) / 2
    m = f.getMetrics()
    base = y - (m.fAscent + m.fDescent) / 2
    for i, (p_, w) in enumerate(zip(parts, widths)):
        k = ease_out_cubic(prog(lt, t0 + i * each, dur))
        if k > 0:
            pt = skia.Paint(Color=col, AntiAlias=True)
            pt.setAlphaf(k)
            c.drawString(p_, x, base + (1 - k) * 14 * U, f, pt)
        x += w + sp


def fit(s, font, max_size, max_w=W - 2 * MARGIN):
    return min(max_size, max_w / max(1e-6, text_width(s, 100, font)) * 100)


# ------------------------------------------------------------------ dot field mask (her mark-making)
def dot_mask(c, k, cx, cy, step=46, seed=3):
    """Clip path made of dots that grow outward from (cx, cy); k = 0..1 fully covers the frame."""
    path = skia.Path()
    s = step * U
    maxd = math.hypot(max(cx, W - cx), max(cy, H - cy))
    for gy in range(-1, int(H / s) + 2):
        for gx in range(-1, int(W / s) + 2):
            x = gx * s + (s / 2 if gy % 2 else 0)
            y = gy * s
            d = math.hypot(x - cx, y - cy) / maxd
            jitter = 0.08 * ((math.sin(gx * 12.9 + gy * 78.2 + seed) * 43758.5) % 1)
            r = clamp((k * 1.35 - d * 0.9 - jitter) / 0.35) * s * 0.78
            if r > 0.5:
                path.addCircle(x, y, r)
    return path


# ------------------------------------------------------------------ pieces
def print_card(c, img, cx, cy, w, rot=0.0, scale=1.0, alpha=1.0):
    h = w * img.height() / img.width()
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(scale, scale)
    shadow(c, -w / 2, -h / 2, w, h, 8 * U, blur=30 * U, dy=18 * U, alpha=0.28 * alpha)
    p = skia.Paint()
    p.setAlphaf(alpha)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), SAMPLING, p)
    c.restore()


def gold_rule(c, cx, y, w, k):
    if k <= 0:
        return
    p = skia.Paint(Color=GOLD, AntiAlias=True, StrokeWidth=4 * U, StrokeCap=skia.Paint.kRound_Cap)
    c.drawLine(cx - w / 2 * k, y, cx + w / 2 * k, y, p)


# ------------------------------------------------------------------ shots: (c, t, lt, dur)
def sh_pause(c, t, lt, dur):
    c.drawImage(PAPER, 0, 0)
    k = ease_in_out_cubic(prog(lt, 0.1, 1.6))
    w = 860 * U
    c.save()
    c.clipPath(dot_mask(c, k, CX, 560 * U), doAntiAlias=True)
    print_card(c, IMG["square"], CX, 560 * U, w, scale=1 + 0.03 * ease_in_out_cubic(prog(lt, 0, dur + 0.7)))
    c.restore()
    line(c, TL.COPY["pause"], CX, 1185 * U, 120 * U, TL.SERIF, INK, prog(lt, 1.0, 0.8))
    gold_rule(c, CX, 1270 * U, 160 * U, ease_out_cubic(prog(lt, 1.5, 0.6)))


def sh_breathe(c, t, lt, dur):
    c.drawImage(PAPER, 0, 0)
    img = IMG["spread"]
    breath = math.sin(math.pi * clamp(lt / dur))
    h = 820 * U * (1 + 0.05 * breath)                 # a window onto the wide spread, gliding left to right
    s = h / img.height()
    vis_w = W - 2 * MARGIN
    x_off = lerp(0, img.width() * s - vis_w, ease_in_out_cubic(prog(lt, 0, dur + 0.7)))
    top = 140 * U + (820 * U - h) / 2
    shadow(c, MARGIN, top, vis_w, h, 6 * U, blur=30 * U, dy=18 * U, alpha=0.28)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(MARGIN, top, vis_w, h), doAntiAlias=True)
    c.drawImageRect(img, skia.Rect.MakeXYWH(MARGIN - x_off, top, img.width() * s, h), SAMPLING)
    c.restore()
    size = fit(TL.COPY["breathe"], TL.SERIF, 104 * U)
    words(c, TL.COPY["breathe"], CX, 1150 * U, size, TL.SERIF, INK, 0.35, lt, each=0.16, dur=0.6)
    # breath dots: five small dots that fill and empty with the breath
    for i in range(5):
        r = (6 + 5 * breath) * U
        p = skia.Paint(Color=BLUE if i != 2 else GOLD, AntiAlias=True)
        p.setAlphaf(ease_out_cubic(prog(lt, 1.0 + 0.08 * i, 0.4)))
        c.drawCircle(CX + (i - 2) * 34 * U, 1260 * U, r, p)


def fan(c, lt, settle=1.0):
    k = [ease_out_back(prog(lt, 0.05 + 0.18 * i, 0.7)) for i in range(3)]
    print_card(c, IMG["tall"], CX - 250 * U, 520 * U + (1 - k[0]) * 60 * U, 470 * U, rot=lerp(0, -9, k[0]),
               alpha=clamp(k[0] * 1.5))
    print_card(c, IMG["square"], CX + 250 * U, 520 * U + (1 - k[1]) * 60 * U, 500 * U, rot=lerp(0, 8, k[1]),
               alpha=clamp(k[1] * 1.5))
    print_card(c, IMG["spread"], CX, 600 * U + (1 - k[2]) * 60 * U, 820 * U * settle, rot=lerp(0, -1.5, k[2]),
               alpha=clamp(k[2] * 1.5))


def sh_blessings(c, t, lt, dur):
    c.drawImage(PAPER, 0, 0)
    fan(c, lt)
    s1 = fit(TL.COPY["bless1"], TL.SERIF, 104 * U)
    line(c, TL.COPY["bless1"], CX, 1080 * U, s1, TL.SERIF, INK, prog(lt, 0.6, 0.7))
    s2 = fit(TL.COPY["bless2"], TL.LIGHT, 64 * U)
    line(c, TL.COPY["bless2"], CX, 1185 * U, s2, TL.LIGHT, INK, prog(lt, 1.0, 0.7))
    gold_rule(c, CX, 1260 * U, 220 * U, ease_out_cubic(prog(lt, 1.4, 0.6)))
    # a few gold dashes drifting up around the fan, like her yellow strokes
    p = skia.Paint(Color=GOLD, AntiAlias=True, StrokeWidth=5 * U, StrokeCap=skia.Paint.kRound_Cap)
    for i in range(14):
        h1 = (math.sin(i * 12.99 + 4) * 43758.5) % 1
        h2 = (math.sin(i * 78.23 + 4) * 1234.5) % 1
        x = W * (0.08 + 0.84 * h1)
        y = 900 * U - ((lt * 60 * U * (0.6 + h2)) + 700 * U * h2) % (780 * U)
        a = 2 * math.pi * h2 + lt
        p.setAlphaf(0.7 * ease_out_cubic(prog(lt, 0.8, 0.6)))
        c.drawLine(x - 8 * U * math.cos(a), y - 8 * U * math.sin(a), x + 8 * U * math.cos(a), y + 8 * U * math.sin(a), p)


def sh_follow(c, t, lt, dur):
    c.drawImage(PAPER, 0, 0)
    up = ease_in_out_cubic(prog(lt, 0, 0.9))
    c.save()
    c.translate(CX, 600 * U)
    c.scale(lerp(1.0, 0.82, up), lerp(1.0, 0.82, up))
    c.translate(-CX, -600 * U + lerp(0, -110, up) * U)
    fan(c, 99)
    c.restore()
    if lt < 0.6:
        c.saveLayerAlpha(None, int(255 * (1 - prog(lt, 0, 0.5))))
        line(c, TL.COPY["bless1"], CX, 1080 * U, fit(TL.COPY["bless1"], TL.SERIF, 104 * U), TL.SERIF, INK, 1)
        line(c, TL.COPY["bless2"], CX, 1185 * U, fit(TL.COPY["bless2"], TL.LIGHT, 64 * U), TL.LIGHT, INK, 1)
        c.restore()
    s = fit(TL.COPY["follow2"], TL.SERIF, 82 * U)
    line(c, TL.COPY["follow1"], CX, 1010 * U, 52 * U, TL.LIGHT, INK, prog(lt, 0.55, 0.6))
    line(c, TL.COPY["follow2"], CX, 1100 * U, s, TL.SERIF, BLUE, prog(lt, 0.85, 0.7))
    gold_rule(c, CX, 1175 * U, 200 * U, ease_out_cubic(prog(lt, 1.3, 0.5)))
    line(c, TL.COPY["handle"], CX, H - MARGIN - 30 * U, 38 * U, TL.MED, INK, 0.8 * prog(lt, 1.3, 0.6))


SHOT_FN = {"pause": sh_pause, "breathe": sh_breathe, "blessings": sh_blessings, "follow": sh_follow}


def draw_shot(c, idx, t):
    s, e, name = TL.SHOTS[idx]
    SHOT_FN[name](c, t, t - s, e - s)


def draw(c, t):
    idx = next((i for i, (s, e, _) in enumerate(TL.SHOTS) if s <= t < e), len(TL.SHOTS) - 1)
    s, e, name = TL.SHOTS[idx]
    if idx > 0 and name != "follow" and t - s < TL.DOTS:
        # dot wipe: the new shot appears through growing dots over the old one
        draw_shot(c, idx - 1, t)
        c.save()
        c.clipPath(dot_mask(c, ease_in_out_cubic((t - s) / TL.DOTS), CX, H / 2, step=60, seed=idx), doAntiAlias=True)
        draw_shot(c, idx, t)
        c.restore()
    else:
        draw_shot(c, idx, t)
    for f in (1 - prog(t, 0, 0.5), prog(t, TL.DURATION - 0.4, 0.4)):
        if f > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=CREAM, Alphaf=clamp(f)))


def post(a, t):
    return grain(vignette(a, 0.1), 0.014, int(t * TL.FPS))


def build_audio():
    subprocess.run([sys.executable, "piano.py", str(TL.DURATION + 0.2), str(TL.PIANO["seed"]), TL.PIANO["key"]],
                   check=True)
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
        S.render(draw, "out/sketchbook-blessings-b.mp4", audio="work/mix.wav", post=post)
    else:
        sys.exit(__doc__)
