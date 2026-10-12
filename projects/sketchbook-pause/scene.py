"""scene: daily sketchbook spread reel v2 (3:4, 12 s). Every frame is a pure function of time t.

    python3 scene.py stills 1 4 7 11      # check frames -> out/stills/
    python3 scene.py audio                # soft piano -> work/mix.wav
    python3 scene.py render               # final -> out/sketchbook-pause.mp4

v2: full-bleed, cinematic. The camera travels through the artist's real pages (pixels untouched, only framed and
moved), serif words fade in letter by letter, warm light leaks hide the cuts. No voice, no captions.
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
B = S.brand
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
CREAM = rgb("#FBF3E6")
GOLD = rgb("#F2C46B")
NIGHT = rgb("#1C1410")
IMG = {k: skia.Image.open(v) for k, v in TL.PAGES.items()}
SAMPLING = skia.SamplingOptions(skia.CubicResampler.Mitchell())
MARGIN = 0.06 * W


# ------------------------------------------------------------------ camera
def cam(c, img, fx, fy, zoom):
    """Fill the frame with `img`, centred on (fx, fy) (fractions), `zoom` x cover. Returns page->screen mapping."""
    iw, ih = img.width(), img.height()
    s = max(W / iw, H / ih) * zoom
    sw, sh = W / s, H / s
    x0 = clamp(fx * iw - sw / 2, 0, iw - sw)
    y0 = clamp(fy * ih - sh / 2, 0, ih - sh)
    c.drawImageRect(img, skia.Rect.MakeXYWH(x0, y0, sw, sh), skia.Rect.MakeWH(W, H), SAMPLING)
    return lambda px, py: ((px * iw - x0) * s, (py * ih - y0) * s)


def bottom_shade(c, strength=0.55, start=0.55):
    """Soft dark gradient at the bottom so cream words read over busy collage."""
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, H * start), skia.Point(0, H)],
        [skia.Color(28, 20, 16, 0), skia.Color(28, 20, 16, int(255 * strength))]))
    c.drawRect(skia.Rect.MakeWH(W, H), p)


# ------------------------------------------------------------------ type
def reveal(c, s, cx, y, size, font, col, lt, t0, per=0.06, dur=0.6, rise=18):
    """Serif line that fades in letter by letter, each letter rising slightly into place. Centred on cx."""
    f = skia.Font(typeface(font), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    w = text_width(s, size, font)
    x = cx - w / 2
    m = f.getMetrics()
    base = y - (m.fAscent + m.fDescent) / 2
    for i, ch in enumerate(s):
        k = ease_out_cubic(prog(lt, t0 + i * per, dur))
        adv = f.measureText(ch)
        if k > 0 and ch != " ":
            yy = base + (1 - k) * rise * U
            sh = skia.Paint(Color=skia.Color(20, 12, 8, int(150 * k)), AntiAlias=True,
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.06))
            c.drawString(ch, x, yy + size * 0.03, f, sh)
            p = skia.Paint(Color=col, AntiAlias=True)
            p.setAlphaf(k)
            c.drawString(ch, x, yy, f, p)
        x += adv
    return t0 + len(s) * per + dur          # time the line is complete


def fit(s, font, max_size, max_w=W - 2 * MARGIN):
    return min(max_size, max_w / max(1e-6, text_width(s, 100, font)) * 100)


# ------------------------------------------------------------------ light
def light_leak(c, t, amount):
    """Warm film light leak: two soft radial glows drifting across, screen-blended."""
    if amount <= 0:
        return
    for j, (bx, by, r, colr) in enumerate([(0.15, 0.25, 0.9, (255, 196, 128)), (0.85, 0.7, 0.75, (255, 150, 90))]):
        cx = W * (bx + 0.25 * math.sin(t * 0.9 + j * 2))
        cy = H * (by + 0.08 * math.cos(t * 0.7 + j))
        shader = skia.GradientShader.MakeRadial(
            skia.Point(cx, cy), H * r,
            [skia.Color(*colr, int(255 * clamp(amount) * 0.85)), skia.Color(*colr, 0)])
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=shader, BlendMode=skia.BlendMode.kScreen))


def leak_amount(t):
    a = 0.0
    for tc in (TL.SHOTS[1][0], TL.SHOTS[2][0]):
        a = max(a, 1 - abs(t - tc) / (TL.LEAK / 2))
    a = max(a, 0.3 * (1 - abs(t - (TL.SHOTS[2][0] + 0.6)) / 0.6))   # a gentle golden wash on "blessed"
    return ease_in_out_cubic(clamp(a))


# ------------------------------------------------------------------ shots: (c, t, lt, dur)
def sh_pause(c, t, lt, dur):
    k = ease_in_out_cubic(prog(lt, 0, dur + 0.3))
    cm = TL.CAM["pause"]
    (fx0, fy0), (fx1, fy1) = cm["focus"]
    cam(c, IMG["clock"], lerp(fx0, fx1, k), lerp(fy0, fy1, k), lerp(*cm["zoom"], k))
    bottom_shade(c, 0.5, 0.6)
    reveal(c, TL.COPY["pause"], CX, H * 0.82, 190 * U, TL.SERIF, CREAM, lt, 0.7, per=0.09, dur=0.7)


def sh_breathe(c, t, lt, dur):
    breath = math.sin(math.pi * clamp(lt / 3.0))             # one slow breath: in, then out
    cm = TL.CAM["breathe"]
    to_screen = cam(c, IMG["toast"], *TL.YOLK, cm["zoom"][0] + TL.BREATH_ZOOM * breath)
    yx, yy = to_screen(*TL.YOLK)
    for j, (r0, a0) in enumerate([(150, 0.6), (210, 0.3)]):   # breathing rings around the yolk
        r = (r0 + 120 * breath) * U
        p = skia.Paint(Color=CREAM, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=(6 - 2 * j) * U)
        p.setAlphaf(a0 * ease_out_cubic(prog(lt, 0.2, 0.6)))
        c.drawCircle(yx, yy, r, p)
    bottom_shade(c, 0.6, 0.55)
    s = fit(TL.COPY["breathe"], TL.SERIF, 120 * U)
    reveal(c, TL.COPY["breathe"], CX, H * 0.84, s, TL.SERIF, CREAM, lt, 0.35, per=0.045, dur=0.6)


def spread_card(c, cy, w, scale, alpha=1.0):
    img = IMG["spread"]
    h = w * img.height() / img.width()
    c.save()
    c.translate(CX, cy)
    c.scale(scale, scale)
    shadow(c, -w / 2, -h / 2, w, h, 10 * U, blur=40 * U, dy=22 * U, alpha=0.5 * alpha)
    p = skia.Paint()
    p.setAlphaf(alpha)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), SAMPLING, p)
    c.restore()


def sh_blessed(c, t, lt, dur):
    bk = 1 + 0.06 * (1 - ease_out_cubic(prog(lt, 0, 3.0)))
    c.save()
    c.translate(CX, H / 2)
    c.scale(bk, bk)
    c.translate(-CX, -H / 2)
    c.drawImage(IMG["spread_blur"], 0, 0)
    c.restore()
    k = ease_out_cubic(prog(lt, 0.05, 1.0))
    spread_card(c, 600 * U, 960 * U, lerp(1.12, 1.0, k), alpha=k)
    s = fit(TL.COPY["blessed"], TL.SERIF, 150 * U)
    reveal(c, TL.COPY["blessed"], CX, 1130 * U, s, TL.SERIF, CREAM, lt, 0.55, per=0.06, dur=0.65)


def sh_follow(c, t, lt, dur):
    c.drawImage(IMG["spread_blur"], 0, 0)
    up = ease_in_out_cubic(prog(lt, 0, 0.9))
    spread_card(c, lerp(600, 450, up) * U, 960 * U, lerp(1.0, 0.86, up))
    # "you are blessed." gently leaves as the closing words arrive
    if lt < 0.6:
        c.saveLayerAlpha(None, int(255 * (1 - prog(lt, 0, 0.5))))
        s = fit(TL.COPY["blessed"], TL.SERIF, 150 * U)
        reveal(c, TL.COPY["blessed"], CX, 1130 * U, s, TL.SERIF, CREAM, 99, 0)
        c.restore()
    y = 900 * U
    reveal(c, TL.COPY["follow1"], CX, y, 66 * U, TL.SERIF, CREAM, lt, 0.4, per=0.035, dur=0.5)
    s2 = fit(TL.COPY["follow3"], TL.SERIF_UP, 104 * U)
    reveal(c, TL.COPY["follow2"], CX, y + 112 * U, s2, TL.SERIF_UP, CREAM, lt, 0.75, per=0.03, dur=0.5)
    reveal(c, TL.COPY["follow3"], CX, y + 225 * U, s2, TL.SERIF, GOLD, lt, 1.1, per=0.03, dur=0.5)
    hk = ease_out_cubic(prog(lt, 1.9, 0.6))
    if hk > 0:
        c.saveLayerAlpha(None, int(255 * 0.85 * hk))
        reveal(c, TL.COPY["handle"], CX, H - MARGIN - 30 * U, 42 * U, TL.SERIF_UP, CREAM, 99, 0)
        c.restore()


SHOT_FN = {"pause": sh_pause, "breathe": sh_breathe, "blessed": sh_blessed, "follow": sh_follow}


def draw_shot(c, idx, t):
    s, e, name = TL.SHOTS[idx]
    SHOT_FN[name](c, t, t - s, e - s)


def draw(c, t):
    idx = next((i for i, (s, e, _) in enumerate(TL.SHOTS) if s <= t < e), len(TL.SHOTS) - 1)
    draw_shot(c, idx, t)
    s = TL.SHOTS[idx][0]
    if idx > 0 and TL.SHOTS[idx][2] != "follow" and t - s < 0.3:   # short dissolve under the light leak
        c.saveLayerAlpha(None, int(255 * (1 - ease_in_out_cubic((t - s) / 0.3))))
        draw_shot(c, idx - 1, t)
        c.restore()
    light_leak(c, t, leak_amount(t))
    for f in (1 - prog(t, 0, 0.6), prog(t, TL.DURATION - 0.45, 0.45)):   # open from / close to warm dark
        if f > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=NIGHT, Alphaf=clamp(f)))


def post(a, t):
    return grain(vignette(a, 0.28), 0.022, int(t * TL.FPS))


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
        S.render(draw, "out/sketchbook-pause.mp4", audio="work/mix.wav", post=post)
    else:
        sys.exit(__doc__)
