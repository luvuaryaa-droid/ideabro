"""scene: daily sketchbook spread reel, "unexpected blessings" (3:4, 13 s). Every frame is a pure function of time t.

    python3 scene.py stills 1 4 7 11      # check frames -> out/stills/
    python3 scene.py audio                # soft piano (G major) -> work/mix.wav
    python3 scene.py render               # final -> out/sketchbook-blessings.mp4

Look: deep navy taken from the artist's ink, her pages untouched (only framed, turned and moved), letter-spaced
capitals in Josefin Sans, a circular iris reveal and drifting gold dashes echoing her yellow strokes.
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
from motion_kit import (Stage, clamp, ease_in_out_cubic, ease_out_cubic, grain, lerp, prog, rgb, shadow,  # noqa: E402
                        text_width, typeface, vignette)

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
NAVY, CREAM, GOLD = rgb(TL.NAVY), rgb(TL.CREAM), rgb(TL.GOLD)
IMG = {k: skia.Image.open(v) for k, v in TL.PAGES.items()}
SAMPLING = skia.SamplingOptions(skia.CubicResampler.Mitchell())
MARGIN = 0.07 * W


# ------------------------------------------------------------------ type
def spaced(c, s, cx, y, size, font, col, k, track=0.32, glow=0.0):
    """Letter-spaced capitals, each letter fading in left to right (k = 0..1 over the whole line)."""
    if k <= 0:
        return
    f = skia.Font(typeface(font), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    adv = [f.measureText(ch) + track * size for ch in s]
    w = sum(adv) - track * size
    x = cx - w / 2
    m = f.getMetrics()
    base = y - (m.fAscent + m.fDescent) / 2
    n = max(1, len(s))
    for i, ch in enumerate(s):
        a = clamp(k * (n + 4) / 5 - i / 5)                # each letter fades over ~5 letters' worth of k
        if a > 0 and ch != " ":
            if glow > 0:
                g = skia.Paint(Color=GOLD, AntiAlias=True,
                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.35))
                g.setAlphaf(a * glow)
                c.drawString(ch, x, base, f, g)
            sh = skia.Paint(Color=skia.Color(8, 12, 40), AntiAlias=True,
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.08))
            sh.setAlphaf(0.55 * a)
            c.drawString(ch, x, base + size * 0.04, f, sh)
            p = skia.Paint(Color=col, AntiAlias=True)
            p.setAlphaf(a)
            c.drawString(ch, x, base, f, p)
        x += adv[i]


def fit(s, font, max_size, track=0.32, max_w=W - 2 * MARGIN):
    w100 = text_width(s, 100, font) + track * 100 * (len(s) - 1)
    return min(max_size, max_w / w100 * 100)


def band(c, cy, h, a):
    """Soft navy band behind words over busy art."""
    if a <= 0:
        return
    sh = skia.GradientShader.MakeLinear([skia.Point(0, cy - h / 2), skia.Point(0, cy + h / 2)],
                                        [skia.Color(19, 35, 91, 0), skia.Color(19, 35, 91, int(200 * a)),
                                         skia.Color(19, 35, 91, 0)], [0.0, 0.5, 1.0])
    c.drawRect(skia.Rect.MakeXYWH(0, cy - h / 2, W, h), skia.Paint(Shader=sh))


# ------------------------------------------------------------------ gold dashes (her yellow strokes, drifting)
def dashes(c, t, alpha, n=34, seed=7):
    if alpha <= 0:
        return
    p = skia.Paint(Color=GOLD, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=5 * U,
                   StrokeCap=skia.Paint.kRound_Cap)
    for i in range(n):
        h1 = (math.sin(i * 12.9898 + seed) * 43758.5453) % 1
        h2 = (math.sin(i * 78.233 + seed) * 12345.678) % 1
        h3 = (math.sin(i * 39.425 + seed) * 9876.54) % 1
        x = W * h1 + 30 * U * math.sin(t * 0.6 + i)
        y = (H * (h2 - 0.06 * t * (0.5 + h3))) % H
        ang = 2 * math.pi * h3 + t * 0.4
        tw = 0.5 + 0.5 * math.sin(t * 2.2 + i * 1.7)                  # twinkle
        keep = clamp((0.62 * H - y) / (0.06 * H))                     # stay clear of the words below
        p.setAlphaf(clamp(alpha * (0.25 + 0.6 * tw) * keep))
        d = 9 * U
        c.drawLine(x - d * math.cos(ang), y - d * math.sin(ang), x + d * math.cos(ang), y + d * math.sin(ang), p)


# ------------------------------------------------------------------ camera
def view(c, img, fx, fy, cover_zoom, rot_deg=0.0):
    """Fill the frame with img centred on (fx, fy) (fractions), zoomed (1 = cover), optionally turned."""
    iw, ih = img.width(), img.height()
    s = max(W / iw, H / ih) * cover_zoom
    c.save()
    c.translate(CX, H / 2)
    c.rotate(rot_deg)
    c.scale(s, s)
    c.translate(-fx * iw, -fy * ih)
    c.drawImageRect(img, skia.Rect.MakeWH(iw, ih), SAMPLING)
    c.restore()


def card(c, img, cx, cy, w, scale=1.0, alpha=1.0):
    h = w * img.height() / img.width()
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    shadow(c, -w / 2, -h / 2, w, h, 10 * U, blur=46 * U, dy=26 * U, alpha=0.55 * alpha)
    p = skia.Paint()
    p.setAlphaf(alpha)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), SAMPLING, p)
    c.restore()


# ------------------------------------------------------------------ shots: (c, t, lt, dur)
def sh_pause(c, t, lt, dur):
    k = ease_in_out_cubic(prog(lt, 0, dur + 0.4))
    zoom = lerp(5.2, 1.25, k)                                         # from inside the flower's eye, out
    fx, fy = TL.FLOWER
    view(c, IMG["square"], lerp(fx, 0.46, k * 0.6), lerp(fy, 0.48, k * 0.6), zoom, rot_deg=lerp(-28, 0, k))
    band(c, H * 0.8, 360 * U, ease_out_cubic(prog(lt, 0.5, 0.8)))
    spaced(c, TL.COPY["pause"], CX, H * 0.8, 120 * U, TL.BOLD, CREAM, prog(lt, 0.9, 1.1), track=0.4)


def sh_breathe(c, t, lt, dur):
    breath = math.sin(math.pi * clamp(lt / dur))                      # one slow breath: in, then out
    view(c, IMG["tall"], 0.5, 0.5, 1.06 + 0.13 * breath)
    band(c, H * 0.82, 360 * U, ease_out_cubic(prog(lt, 0.2, 0.7)))
    s = fit(TL.COPY["breathe"], TL.BOLD, 76 * U, track=0.3)
    spaced(c, TL.COPY["breathe"], CX, H * 0.82, s, TL.BOLD, CREAM, prog(lt, 0.35, 1.2), track=0.3)
    # a thin ring that grows and shrinks with the breath, around the words
    p = skia.Paint(Color=CREAM, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6 * U)
    p.setAlphaf(0.9 * ease_out_cubic(prog(lt, 0.3, 0.6)))
    r = (330 + 150 * breath) * U
    c.drawCircle(CX, H * 0.82 - 10 * U, r, p)


def blessings_bg(c, t, lt):
    c.clear(NAVY)
    dashes(c, t, ease_out_cubic(prog(lt, 0.3, 1.2)))


def sh_blessings(c, t, lt, dur):
    blessings_bg(c, t, lt)
    k = ease_out_cubic(prog(lt, 0.1, 1.1))
    card(c, IMG["spread"], CX, 560 * U, 950 * U, scale=lerp(1.08, 1.0, k), alpha=clamp(k * 1.4))
    y = 1035 * U
    s1 = fit(TL.COPY["bless1"], TL.BOLD, 84 * U, track=0.18)
    spaced(c, TL.COPY["bless1"], CX, y, s1, TL.BOLD, GOLD, prog(lt, 0.45, 0.9), track=0.18, glow=0.35)
    s2 = fit(TL.COPY["bless2"], TL.LIGHT, 64 * U, track=0.34)
    spaced(c, TL.COPY["bless2"], CX, y + 110 * U, s2, TL.LIGHT, CREAM, prog(lt, 0.9, 0.8), track=0.34)


def sh_follow(c, t, lt, dur):
    blessings_bg(c, t, lt + 3)
    up = ease_in_out_cubic(prog(lt, 0, 0.9))
    card(c, IMG["spread"], CX, lerp(560, 430, up) * U, 950 * U, scale=lerp(1.0, 0.86, up))
    if lt < 0.6:                                                       # the blessing line hands over gently
        c.saveLayerAlpha(None, int(255 * (1 - prog(lt, 0, 0.5))))
        y = 1035 * U
        spaced(c, TL.COPY["bless1"], CX, y, fit(TL.COPY["bless1"], TL.BOLD, 84 * U, track=0.18), TL.BOLD, GOLD, 1,
               track=0.18, glow=0.35)
        spaced(c, TL.COPY["bless2"], CX, y + 110 * U, fit(TL.COPY["bless2"], TL.LIGHT, 64 * U, track=0.34),
               TL.LIGHT, CREAM, 1, track=0.34)
        c.restore()
    y = 880 * U
    s = fit(TL.COPY["follow2"], TL.LIGHT, 58 * U, track=0.28)
    spaced(c, TL.COPY["follow1"], CX, y, s, TL.LIGHT, CREAM, prog(lt, 0.3, 0.6), track=0.28)
    spaced(c, TL.COPY["follow2"], CX, y + 92 * U, s, TL.LIGHT, CREAM, prog(lt, 0.55, 0.6), track=0.28)
    spaced(c, TL.COPY["follow3"], CX, y + 200 * U, 88 * U, TL.BOLD, GOLD, prog(lt, 0.8, 0.7), track=0.3, glow=0.3)
    hk = ease_out_cubic(prog(lt, 1.4, 0.6))
    if hk > 0:
        f = skia.Font(typeface(TL.LIGHT), 36 * U)
        w = f.measureText(TL.COPY["handle"])
        p = skia.Paint(Color=CREAM, AntiAlias=True)
        p.setAlphaf(0.85 * hk)
        c.drawString(TL.COPY["handle"], CX - w / 2, H - MARGIN - 20 * U, f, p)


SHOT_FN = {"pause": sh_pause, "breathe": sh_breathe, "blessings": sh_blessings, "follow": sh_follow}


def draw_shot(c, idx, t):
    s, e, name = TL.SHOTS[idx]
    SHOT_FN[name](c, t, t - s, e - s)


def draw(c, t):
    idx = next((i for i, (s, e, _) in enumerate(TL.SHOTS) if s <= t < e), len(TL.SHOTS) - 1)
    s, e, name = TL.SHOTS[idx]
    if name == "blessings" and t - s < TL.IRIS:
        # iris: the new shot opens as a growing circle from the centre, over the old one
        draw_shot(c, idx - 1, t)
        r = ease_in_out_cubic((t - s) / TL.IRIS) * math.hypot(W, H) * 0.55
        c.save()
        path = skia.Path()
        path.addCircle(CX, H / 2, max(1.0, r))
        c.clipPath(path, doAntiAlias=True)
        draw_shot(c, idx, t)
        c.restore()
        ring = skia.Paint(Color=GOLD, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4 * U)
        ring.setAlphaf(0.8 * (1 - (t - s) / TL.IRIS))
        c.drawCircle(CX, H / 2, r, ring)
    elif idx > 0 and name == "breathe" and t - s < 0.5:              # soft dissolve pause -> breathe
        draw_shot(c, idx, t)
        c.saveLayerAlpha(None, int(255 * (1 - ease_in_out_cubic((t - s) / 0.5))))
        draw_shot(c, idx - 1, t)
        c.restore()
    else:
        draw_shot(c, idx, t)
    for f in (1 - prog(t, 0, 0.6), prog(t, TL.DURATION - 0.4, 0.4)):   # open from / close to navy
        if f > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=NAVY, Alphaf=clamp(f)))


def post(a, t):
    return grain(vignette(a, 0.22), 0.016, int(t * TL.FPS))


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
        S.render(draw, "out/sketchbook-blessings.mp4", audio="work/mix.wav", post=post)
    else:
        sys.exit(__doc__)
