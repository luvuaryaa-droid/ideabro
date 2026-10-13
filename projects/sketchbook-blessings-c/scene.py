"""scene: "unexpected blessings" version C - paper cut-out, cozy journal (3:4, 14 s). Pure function of time t.

    python3 scene.py stills 1 4 8 12      # check frames -> out/stills/
    python3 scene.py audio                # soft piano (A major) -> work/mix.wav
    python3 scene.py render               # final -> out/sketchbook-blessings-c.mp4

Everything moves in held drawings (12/s): cut-out flowers (cut from her own page, art untouched inside), her pages
taped into a dotted journal on a kraft desk, paper-cut leaves/clouds/confetti with drop shadows, torn paper word
strips in a typewriter face, torn-paper wipes.
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
from motion_kit import (Stage, clamp, ease_in_out_cubic, ease_out_back, ease_out_cubic, grain, lerp, noise1,  # noqa: E402
                        prog, rgb, shadow, typeface, vignette)
from toon_kit import blob, paper_texture, smooth_path, stepped, wobble_points  # noqa: E402

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
KRAFT, PAGEC, INK, BLUE, GOLD, TEAL, PINK = (rgb(c) for c in (TL.KRAFT, TL.PAGE, TL.INK, TL.BLUE, TL.GOLD, TL.TEAL,
                                                              TL.PINK))
DESK = paper_texture(W, H, TL.KRAFT, grain=0.09, seed=11)
JOURNAL = paper_texture(W, H, TL.PAGE, grain=0.05, seed=4)
IMG = {k: skia.Image.open(v) for k, v in TL.PAGES.items()}
CUT = [skia.Image.open(p) for p in TL.CUTS]
SAMPLING = skia.SamplingOptions(skia.CubicResampler.Mitchell())


def h01(*k):
    n = 0
    for v in k:
        n = (n * 1000003 + int(v) * 2654435761 + 12345) & 0xFFFFFFFF
        n ^= n >> 15
    return (n * 2246822519 & 0xFFFFFFFF) / 2 ** 32


# ------------------------------------------------------------------ journal set
def journal(c, ts):
    c.drawImage(DESK, 0, 0)
    m = 46 * U
    rect = skia.Rect.MakeXYWH(m, m, W - 2 * m, H - 2 * m)
    c.save()
    c.rotate(-0.6, CX, H / 2)
    shadow(c, rect.x(), rect.y(), rect.width(), rect.height(), 6 * U, blur=26 * U, dy=12 * U, alpha=0.3)
    c.save()
    c.clipRect(rect, doAntiAlias=True)
    c.drawImage(JOURNAL, 0, 0)
    dot = skia.Paint(Color=skia.Color(120, 100, 80, 70), AntiAlias=True)
    step = 40 * U
    y = rect.top() + step
    while y < rect.bottom():
        x = rect.left() + step
        while x < rect.right():
            c.drawCircle(x, y, 2.1 * U, dot)
            x += step
        y += step
    c.restore()
    c.restore()


def tape(c, x, y, w, h, rot, col, alpha=0.7):
    """Washi tape with torn short ends."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2)]
    for i in range(6):
        pts.append((w / 2 + (4 * U if i % 2 else -2 * U), -h / 2 + h * (i + 1) / 6))
    pts.append((-w / 2, h / 2))
    for i in range(6):
        pts.append((-w / 2 + (3 * U if i % 2 else -3 * U), h / 2 - h * (i + 1) / 6))
    path = skia.Path()
    path.addPoly([skia.Point(*p) for p in pts], True)
    p = skia.Paint(Color=col, AntiAlias=True)
    p.setAlphaf(alpha)
    c.drawPath(path, p)
    c.restore()


def taped_print(c, img, cx, cy, w, rot, scale=1.0, tape_cols=(PINK, TEAL), alpha=1.0):
    h = w * img.height() / img.width()
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(scale, scale)
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    shadow(c, -w / 2, -h / 2, w, h, 4 * U, blur=18 * U, dy=12 * U, alpha=0.32)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), SAMPLING)
    tape(c, -w / 2 + 40 * U, -h / 2 + 4 * U, 150 * U, 40 * U, -38, tape_cols[0])
    tape(c, w / 2 - 40 * U, h / 2 - 4 * U, 150 * U, 40 * U, -38, tape_cols[1])
    if alpha < 1:
        c.restore()
    c.restore()


def cutout(c, i, cx, cy, d, rot=0.0, lift=0.0):
    """A scissor-cut flower with a paper drop shadow; lift = how far it floats above the page."""
    img = CUT[i]
    sh = skia.Paint(ImageFilter=skia.ImageFilters.DropShadowOnly((6 + 14 * lift) * U, (10 + 22 * lift) * U,
                                                                (5 + 8 * lift) * U, (5 + 8 * lift) * U,
                                                                skia.Color(40, 25, 10, 110)))
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    r = skia.Rect.MakeXYWH(-d / 2, -d / 2, d, d)
    c.drawImageRect(img, r, SAMPLING, sh)
    c.drawImageRect(img, r, SAMPLING)
    c.restore()


def leaf(c, x, y, s, rot, col, ts, seed):
    """Paper-cut leaf: two arcs, flat colour, drop shadow."""
    pts = []
    for k in range(9):
        a = math.pi * k / 8
        pts.append((x + s * math.cos(a) * 1.0, y - s * 0.42 * math.sin(a)))
    for k in range(1, 8):
        a = math.pi - math.pi * k / 8
        pts.append((x + s * math.cos(a), y + s * 0.42 * math.sin(a)))
    c.save()
    c.rotate(rot, x, y)
    path = smooth_path(wobble_points(pts, s * 0.02, ts, seed))
    c.drawPath(path, skia.Paint(Color=skia.Color(40, 25, 10, 70), AntiAlias=True,
                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4 * U)))
    c.translate(-4 * U, -6 * U)
    c.drawPath(path, skia.Paint(Color=col, AntiAlias=True))
    c.drawLine(x - s * 0.85, y, x + s * 0.85, y, skia.Paint(Color=skia.Color(255, 255, 255, 90), AntiAlias=True,
                                                            StrokeWidth=2 * U))
    c.restore()


def strip(c, s, cx, cy, size, k, ts, seed, font=None, col=None, paper=None, rot=0.0):
    """A torn paper strip with typewritten words; slides in from below on held drawings."""
    if k <= 0:
        return
    font = font or TL.TYPE
    f = skia.Font(typeface(font), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    tw = f.measureText(s)
    w, h = tw + 70 * U, size * 1.75
    yk = (1 - ease_out_back(k)) * 60 * U
    c.save()
    c.translate(cx, cy + yk)
    c.rotate(rot + 1.5 * noise1(seed + int(ts * 2)))
    pts = []
    n = 26
    for i in range(n + 1):                                  # torn top edge
        pts.append((-w / 2 + w * i / n, -h / 2 + (h01(seed, i) - 0.5) * 7 * U))
    for i in range(n + 1):                                  # torn bottom edge
        pts.append((w / 2 - w * i / n, h / 2 + (h01(seed + 9, i) - 0.5) * 7 * U))
    path = skia.Path()
    path.addPoly([skia.Point(*p) for p in pts], True)
    c.drawPath(path, skia.Paint(Color=skia.Color(40, 25, 10, 80), AntiAlias=True,
                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6 * U)))
    c.translate(0, -5 * U)
    p = skia.Paint(Color=paper if paper is not None else skia.Color(252, 249, 242), AntiAlias=True)
    c.drawPath(path, p)
    m = f.getMetrics()
    tp = skia.Paint(Color=col if col is not None else INK, AntiAlias=True)
    c.drawString(s, -tw / 2, -(m.fAscent + m.fDescent) / 2, f, tp)
    c.restore()


def pop(lt, start, dur=0.35):
    """0..1 placement for paper pieces, on held drawings (already stepped via lt)."""
    k = prog(lt, start, dur)
    return ease_out_back(k) if k > 0 else 0.0


# ------------------------------------------------------------------ shots: (c, t, lt, dur, ts)
SPOTS = [(270, 380, 300, -8), (720, 330, 330, 6), (330, 790, 320, 5), (790, 760, 300, -6)]


def sh_pause(c, t, lt, dur, ts):
    journal(c, ts)
    for i, (x, y, d, r) in enumerate(SPOTS):                      # flowers placed by hand, one by one
        k = pop(lt, 0.15 + 0.38 * i, 0.4)
        if k > 0:
            lift = 1 - clamp(k)
            cutout(c, i, x * U, y * U - lift * 50 * U, d * U * (0.85 + 0.15 * k), rot=r + lift * 12, lift=lift)
    for j, (x, y, s, r, col) in enumerate([(520, 560, 70, 30, TEAL), (930, 520, 60, -40, GOLD),
                                           (140, 600, 58, 60, BLUE), (560, 1000, 64, -20, GOLD)]):
        if pop(lt, 1.4 + 0.12 * j) > 0:
            leaf(c, x * U, y * U, s * U * pop(lt, 1.4 + 0.12 * j), r, col, ts, 20 + j)
    strip(c, TL.COPY["pause"], CX, 1180 * U, 92 * U, prog(lt, 1.0, 0.45), ts, 1, rot=-2)


def cloud(c, x, y, s, ts, seed):
    for j, (dx, dy, rr) in enumerate([(-0.55, 0.1, 0.42), (0, -0.12, 0.55), (0.55, 0.08, 0.4)]):
        blob(c, x + dx * s, y + dy * s, rr * s, skia.Color(252, 249, 242), ts, seed=seed + j, style="paper",
             boil=s * 0.01)


def sh_breathe(c, t, lt, dur, ts):
    journal(c, ts)
    for j, (x, y, s, sp) in enumerate([(150, 220, 120, 26), (900, 300, 100, -20)]):   # paper clouds drift
        cloud(c, x * U + sp * lt * U, y * U, s * U, ts, 40 + 5 * j)
    taped_print(c, IMG["tall"], CX + 40 * U, 640 * U, 640 * U, rot=2.5, tape_cols=(GOLD, PINK))
    breath = math.sin(math.pi * clamp(lt / dur))                   # the cut flower breathes in, then out
    cutout(c, 1, 250 * U, 1000 * U, (250 + 50 * breath) * U, rot=-10 + 4 * breath, lift=0.3 + 0.5 * breath)
    strip(c, TL.COPY["breathe"], CX + 60 * U, 1230 * U, 64 * U, prog(lt, 0.35, 0.45), ts, 2, rot=1.5)


def confetti(c, lt, ts, n=26):
    cols = [BLUE, GOLD, TEAL, PINK]
    for i in range(n):
        x = (0.08 + 0.84 * h01(70, i)) * W + 30 * U * math.sin(lt * 1.3 + i)
        y = -80 * U + ((lt - 0.4 - 0.8 * h01(71, i)) * (160 + 90 * h01(72, i)) * U)
        if y < -60 * U or y > 960 * U:
            continue
        rot = lt * 90 * (h01(73, i) - 0.5)
        s = (14 + 12 * h01(74, i)) * U
        col = cols[i % 4]
        if i % 3 == 0:
            leaf(c, x, y, s * 1.4, rot, col, ts, 80 + i)
        else:
            c.save()
            c.rotate(rot, x, y)
            c.drawCircle(x + 3 * U, y + 5 * U, s * 0.6, skia.Paint(Color=skia.Color(40, 25, 10, 60), AntiAlias=True))
            c.drawCircle(x, y, s * 0.6, skia.Paint(Color=col, AntiAlias=True))
            c.restore()


def sh_blessings(c, t, lt, dur, ts):
    journal(c, ts)
    confetti(c, lt, ts)                                            # behind the print: never over her art
    k = pop(lt, 0.05, 0.45)
    taped_print(c, IMG["spread"], CX, 560 * U - (1 - clamp(k)) * 40 * U, 900 * U, rot=-2,
                scale=0.9 + 0.1 * k, tape_cols=(TEAL, GOLD), alpha=clamp(k * 1.5))
    strip(c, TL.COPY["bless1"], CX, 1030 * U, 66 * U, prog(lt, 0.5, 0.45), ts, 3, rot=-1.5)
    strip(c, TL.COPY["bless2"], CX + 80 * U, 1150 * U, 56 * U, prog(lt, 0.85, 0.45), ts, 4, rot=2,
          col=BLUE)


def sh_follow(c, t, lt, dur, ts):
    journal(c, ts)
    up = ease_in_out_cubic(prog(lt, 0, 0.6))
    taped_print(c, IMG["spread"], CX, lerp(560, 430, up) * U, 900 * U, rot=-2, scale=lerp(1.0, 0.86, up),
                tape_cols=(TEAL, GOLD))
    cutout(c, 3, 900 * U, 640 * U, 210 * U, rot=12, lift=0.4)
    if lt < 0.5:
        c.saveLayerAlpha(None, int(255 * (1 - prog(lt, 0, 0.4))))
        strip(c, TL.COPY["bless1"], CX, 1030 * U, 66 * U, 1, ts, 3, rot=-1.5)
        strip(c, TL.COPY["bless2"], CX + 80 * U, 1150 * U, 56 * U, 1, ts, 4, rot=2, col=BLUE)
        c.restore()
    strip(c, TL.COPY["follow1"], CX, 930 * U, 52 * U, prog(lt, 0.45, 0.4), ts, 5, rot=-1)
    strip(c, TL.COPY["follow2"], CX, 1050 * U, 54 * U, prog(lt, 0.75, 0.4), ts, 6, rot=1.2, col=BLUE)
    # little paper tag with the handle, hand-lettered
    hk = pop(lt, 1.15, 0.4)
    if hk > 0:
        c.save()
        c.translate(CX, 1210 * U + (1 - clamp(hk)) * 40 * U)
        c.rotate(-3)
        f = skia.Font(typeface(TL.HAND), 50 * U)
        w = f.measureText(TL.COPY["handle"]) + 60 * U
        shadow(c, -w / 2, -38 * U, w, 76 * U, 8 * U, blur=10 * U, dy=8 * U, alpha=0.3)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -38 * U, w, 76 * U), 8 * U, 8 * U),
                    skia.Paint(Color=GOLD, AntiAlias=True))
        c.drawCircle(-w / 2 + 22 * U, 0, 7 * U, skia.Paint(Color=KRAFT, AntiAlias=True))
        c.drawString(TL.COPY["handle"], -w / 2 + 44 * U, 16 * U, f, skia.Paint(Color=INK, AntiAlias=True))
        c.restore()


SHOT_FN = {"pause": sh_pause, "breathe": sh_breathe, "blessings": sh_blessings, "follow": sh_follow}


def draw_shot(c, idx, t):
    s, e, name = TL.SHOTS[idx]
    ts = stepped(t, TL.STEP)
    SHOT_FN[name](c, t, stepped(t - s, TL.STEP), e - s, ts)


def torn_edge_path(x_edge, seed):
    """Region to the left of a vertical torn edge at x_edge."""
    path = skia.Path()
    path.moveTo(-10, -10)
    n = 40
    for i in range(n + 1):
        y = H * i / n
        path.lineTo(x_edge + (h01(seed, i) - 0.5) * 34 * U, y)
    path.lineTo(-10, H + 10)
    path.close()
    return path


def draw(c, t):
    idx = next((i for i, (s, e, _) in enumerate(TL.SHOTS) if s <= t < e), len(TL.SHOTS) - 1)
    s, e, name = TL.SHOTS[idx]
    if idx > 0 and name != "follow" and t - s < TL.TEAR:
        # torn-paper wipe: the new page is revealed behind a torn edge sweeping right
        k = ease_in_out_cubic(stepped(t - s, TL.STEP) / TL.TEAR)
        draw_shot(c, idx - 1, t)
        c.save()
        c.clipPath(torn_edge_path(lerp(-60 * U, W + 60 * U, k), 90 + idx), doAntiAlias=True)
        draw_shot(c, idx, t)
        c.restore()
    else:
        draw_shot(c, idx, t)
    for f in (1 - prog(t, 0, 0.5), prog(t, TL.DURATION - 0.4, 0.4)):
        if f > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=KRAFT, Alphaf=clamp(f)))


def post(a, t):
    return grain(vignette(a, 0.2), 0.02, int(stepped(t, TL.STEP) * TL.STEP))


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
        S.render(draw, "out/sketchbook-blessings-c.mp4", audio="work/mix.wav", post=post)
    else:
        sys.exit(__doc__)
