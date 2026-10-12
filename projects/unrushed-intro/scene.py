"""scene: The Unrushed Whispers, 500-follower re-introduction. Every frame is a pure function of time t.

    python3 scene.py stills 2 7 11 ...     # check frames -> out/stills/
    python3 scene.py audio                 # music + crackle + voice -> work/mix.wav
    python3 scene.py draft                 # half-res preview -> out/draft.mp4
    python3 scene.py render                # final -> out/unrushed-intro.mp4

Look: a cozy sketchbook. Cream paper, the artist's own footage and drawings as taped prints, hand-drawn doodles
that draw themselves on (12 drawings/s), handwritten captions. Footage is shown as-is (no grading).
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
import audio_kit as ak  # noqa: E402
from motion_kit import (Stage, VideoFrames, clamp, ease_in_out_cubic, ease_out_back, ease_out_cubic,  # noqa: E402
                        grain, lerp, noise1, prog, rgb, shadow, text, text_width, vignette)
from toon_kit import draw_on, hatch_fill, paper_texture, smooth_path, stepped, wobble_points  # noqa: E402

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
B = S.brand
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
INK, PAPERC, WHITE = rgb(B, "ink"), rgb(B, "paper"), rgb(B, "white")
OCHRE, TEAL, LEAF, TERRA, BLUSH = rgb(B, "lime"), rgb(B, "periwinkle"), rgb(B, "ice"), rgb(B, "orange"), rgb(B, "blush")

PAPER = paper_texture(W, H, B["colors"]["paper"], grain=0.07)
VF = {k: VideoFrames(v, fps=TL.FPS) for k, v in TL.CLIPS.items()}
CAT = skia.Image.open("assets/sketch_cat.png")
PORTRAIT = skia.Image.open("assets/sketch_portrait.png")
PRINT_Y = 455 * U          # prints sit above the caption line
CAP_Y = H - 118 * U


# ------------------------------------------------------------------ helpers
def write(c, s, x, y, size, font, col, k, align="center", alpha=1.0):
    """Handwriting reveal: the text appears left to right, stepped like drawings."""
    if k <= 0:
        return
    w = text_width(s, size, font)
    x0 = x - w / 2 if align == "center" else x
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x0 - 20 * U, y - size, (w + 40 * U) * clamp(k), size * 2))
    text(c, s, x, y, size=size, font=font, fill=col, align=align, alpha=alpha)
    c.restore()


def fit(s, font, max_size, max_w):
    return min(max_size, max_w / max(1e-6, text_width(s, 100, font)) * 100)


def doodle(c, pts, col, width, k, ts, seed=0, closed=False, amp=None):
    """A hand-drawn stroke that draws itself on (k = 0..1) and boils slightly."""
    if k <= 0 or len(pts) < 2:
        return
    amp = 1.6 * U if amp is None else amp
    p = smooth_path(wobble_points(pts, amp, ts, seed, closed), closed)
    seg = draw_on(p, k)
    for j, (wf, a) in enumerate([(1.0, 0.92), (0.55, 0.5)]):
        c.drawPath(seg if j == 0 else draw_on(smooth_path(wobble_points(pts, amp * 1.4, ts, seed + 7, closed), closed), k),
                   skia.Paint(Color=col, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * wf,
                              StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, Alphaf=a))


def poly(pts, per=10):
    """Straight-edged doodle: points along every edge, so smoothing keeps the corners crisp."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        out += [(lerp(x0, x1, i / per), lerp(y0, y1, i / per)) for i in range(per)]
    return out + [pts[-1]]


def heart_pts(cx, cy, s, n=28):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s / 32, cy + y * s / 32))
    return pts


def circle_pts(cx, cy, rx, ry=None, n=24, start=0.0, turns=1.0):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(start + turns * 2 * math.pi * i / n), cy + ry * math.sin(start + turns * 2 * math.pi * i / n))
            for i in range(n + 1)]


def wavy(x0, x1, y, amp, n=14):
    return [(lerp(x0, x1, i / n), y + amp * math.sin(i * 1.3)) for i in range(n + 1)]


def tape(c, x, y, w, h, rot, col):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.Paint(Color=col, Alphaf=0.62, AntiAlias=True))
    c.restore()


def photo(c, img, cx, cy, w, h, rot=0.0, push=1.0, alpha=1.0, border=16, tapes=True, tape_col=None):
    """A printed photo taped onto the page: white border, soft shadow, content pushed in slowly."""
    if alpha <= 0:
        return
    b = border * U
    c.save()
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    c.translate(cx, cy)
    c.rotate(rot)
    shadow(c, -w / 2 - b, -h / 2 - b, w + 2 * b, h + 2 * b, 4 * U, blur=22 * U, dy=12 * U, alpha=0.28)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 - b, -h / 2 - b, w + 2 * b, h + 2 * b), skia.Paint(Color=WHITE, AntiAlias=True))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), doAntiAlias=True)
    iw, ih = img.width(), img.height()
    sc = max(w / iw, h / ih) * push
    dw, dh = iw * sc, ih * sc
    c.drawImageRect(img, skia.Rect.MakeXYWH(-dw / 2, -dh / 2, dw, dh), skia.SamplingOptions(skia.FilterMode.kLinear))
    c.restore()
    if tapes:
        tc = tape_col if tape_col is not None else BLUSH
        tape(c, -w / 2 + 30 * U, -h / 2 - 4 * U, 120 * U, 34 * U, -38, tc)
        tape(c, w / 2 - 30 * U, -h / 2 - 4 * U, 120 * U, 34 * U, 38, tc)
    if alpha < 1:
        c.restore()
    c.restore()


def push(lt, dur, amt=0.05):
    return 1 + amt * ease_in_out_cubic(prog(lt, 0, dur + TL.XFADE))


def clip(name, lt):
    return VF[name].at(max(0.0, lt))


def settle(lt, d=0.6):
    """Prints drop onto the page: tiny scale + fade settle."""
    k = ease_out_cubic(prog(lt, 0, d))
    return k, lerp(1.04, 1.0, k)


# ------------------------------------------------------------------ shots: draw(c, t, lt, dur, ts)
def sh_title(c, t, lt, dur, ts):
    sun_r = 46 * U
    cx, cy = CX, 300 * U
    doodle(c, circle_pts(cx, cy, sun_r), OCHRE, 7 * U, prog(lt, 0.15, 0.7), ts, seed=1)
    for i in range(10):
        a = i / 10 * 2 * math.pi
        r0, r1 = sun_r + 18 * U, sun_r + 46 * U
        doodle(c, [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
               OCHRE, 6 * U, prog(lt, 0.7 + 0.05 * i, 0.2), ts, seed=10 + i)
    size = fit(TL.COPY["title"], "display", 150 * U, W * 0.8)
    write(c, TL.COPY["title"], CX, 480 * U, size, "display", INK, ease_in_out_cubic(prog(lt, 0.4, 1.8)))
    doodle(c, wavy(CX - 330 * U, CX + 330 * U, 565 * U, 5 * U), TERRA, 5 * U, prog(lt, 2.1, 0.7), ts, seed=3)
    text(c, TL.COPY["title_sub"], CX, 640 * U, size=46 * U, font="serif", fill=INK,
         alpha=ease_out_cubic(prog(lt, 2.4, 0.8)))


def sh_five_hundred(c, t, lt, dur, ts):
    k, sc = settle(lt)
    photo(c, PORTRAIT, 640 * U, PRINT_Y, 600 * U, 655 * U, rot=-2.5, push=push(lt, dur) * sc, alpha=k)
    x, y = 1360 * U, 400 * U
    kn = ease_in_out_cubic(prog(lt, 0.45, 1.1))
    write(c, TL.COPY["five_hundred"], x, y, 260 * U, "display", OCHRE, kn)
    doodle(c, circle_pts(x, y + 8 * U, 250 * U, 150 * U, n=30, start=-2.2, turns=1.08), TERRA, 6 * U,
           prog(lt, 1.4, 0.9), ts, seed=4)
    write(c, TL.COPY["five_hundred_sub"], x, y + 210 * U, 76 * U, "body", INK, prog(lt, 2.2, 0.8))
    for i, (hx, hy, s) in enumerate([(1090, 230, 46), (1640, 250, 36), (1620, 640, 52)]):
        doodle(c, heart_pts(hx * U, hy * U, s * U), TERRA if i != 1 else OCHRE, 5 * U, prog(lt, 2.8 + 0.35 * i, 0.6),
               ts, seed=20 + i, closed=False)


def sh_banker(c, t, lt, dur, ts):
    cx, top, wd = CX, 220 * U, 560 * U
    base = top + 430 * U
    kk = lambda a, d=0.45: prog(lt, a, d)  # noqa: E731
    doodle(c, poly([(cx - wd / 2 - 20 * U, top + 120 * U), (cx, top), (cx + wd / 2 + 20 * U, top + 120 * U),
                    (cx - wd / 2 - 20 * U, top + 120 * U)]), INK, 6 * U, kk(0.0, 0.6), ts, seed=30)
    doodle(c, [(cx - wd / 2, top + 150 * U), (cx + wd / 2, top + 150 * U)], INK, 6 * U, kk(0.45), ts, seed=31)
    for i in range(4):
        x = cx - wd / 2 + 70 * U + i * (wd - 140 * U) / 3
        doodle(c, [(x, top + 170 * U), (x, base - 30 * U)], INK, 9 * U, kk(0.6 + 0.12 * i, 0.35), ts, seed=32 + i)
    doodle(c, [(cx - wd / 2 - 30 * U, base), (cx + wd / 2 + 30 * U, base)], INK, 6 * U, kk(1.1), ts, seed=37)
    doodle(c, [(cx - wd / 2 - 60 * U, base + 26 * U), (cx + wd / 2 + 60 * U, base + 26 * U)], INK, 6 * U, kk(1.3),
           ts, seed=38)
    for i in range(3):                                   # a little stack of coins, in ochre
        doodle(c, circle_pts(cx + 400 * U, base - 14 * U - i * 26 * U, 52 * U, 14 * U, n=20), OCHRE, 5 * U,
               kk(1.4 + 0.15 * i, 0.4), ts, seed=40 + i)


def sh_art(c, t, lt, dur, ts):
    k, sc = settle(lt)
    photo(c, CAT, CX, PRINT_Y, 640 * U, 640 * U, rot=1.6, push=push(lt, dur) * sc, alpha=k, tape_col=OCHRE)
    for i, (sx, sy) in enumerate([(520, 230), (1420, 300), (1440, 640), (500, 660)]):
        kk = prog(lt, 0.9 + 0.3 * i, 0.4)
        for a in range(4):
            ang = a * math.pi / 4
            r = 26 * U
            doodle(c, [(sx * U - r * math.cos(ang), sy * U - r * math.sin(ang)),
                       (sx * U + r * math.cos(ang), sy * U + r * math.sin(ang))], LEAF, 5 * U, kk, ts, seed=50 + i * 4 + a)


def sh_rain(c, t, lt, dur, ts):
    k, sc = settle(lt)
    photo(c, clip("rain", lt), CX, PRINT_Y, 600 * U, 600 * U, rot=-1.6, push=push(lt, dur) * sc, alpha=k,
          tape_col=TEAL)
    for i in range(14):                                  # hand-drawn rain on the page
        x = (300 + 1320 * ((i * 0.618) % 1)) * U
        if 560 * U < x < 1360 * U:
            continue
        y0 = (180 + ((i * 97 + boil(ts) * 23) % 520)) * U
        doodle(c, [(x, y0), (x - 14 * U, y0 + 46 * U)], TEAL, 4 * U, prog(lt, 0.2 + 0.05 * i, 0.2), ts, seed=60 + i)


def boil(ts):
    return int(round(ts * 12))


def sh_sun(c, t, lt, dur, ts):
    k, sc = settle(lt)
    photo(c, clip("sun", lt), CX, PRINT_Y, 1180 * U, 590 * U, rot=1.0, push=push(lt, dur) * sc, alpha=k)
    cx, cy = 1540 * U, 170 * U
    doodle(c, circle_pts(cx, cy, 34 * U), OCHRE, 6 * U, prog(lt, 0.5, 0.6), ts, seed=70)
    for i in range(8):
        a = i / 8 * 2 * math.pi
        doodle(c, [(cx + 48 * U * math.cos(a), cy + 48 * U * math.sin(a)), (cx + 70 * U * math.cos(a), cy + 70 * U * math.sin(a))],
               OCHRE, 5 * U, prog(lt, 0.9 + 0.05 * i, 0.2), ts, seed=71 + i)


def sh_belief(c, t, lt, dur, ts):
    k, sc = settle(lt)
    photo(c, clip("page_tulips", lt), 560 * U, 470 * U, 600 * U, 590 * U, rot=-2.2, push=push(lt, dur, 0.04) * sc,
          alpha=k, tape_col=OCHRE)
    x = 1000 * U
    maxw = W - x - 90 * U
    a0 = TL.ps("beliefa") - (t - lt)                    # phrase times, local to this shot
    b0 = TL.ps("beliefb") - (t - lt)
    s1 = fit(TL.COPY["belief1"], "display", 92 * U, maxw)
    s2 = fit(TL.COPY["belief2"], "display", 104 * U, maxw)
    s3 = fit(TL.COPY["belief3"], "body", 80 * U, maxw)
    write(c, TL.COPY["belief1"], x, 330 * U, s1, "display", INK, prog(lt, a0, 1.3), align="left")
    write(c, TL.COPY["belief2"], x, 455 * U, s2, "display", TERRA, prog(lt, a0 + 1.5, 1.9), align="left")
    w2 = text_width(TL.COPY["belief2"], s2, "display")
    doodle(c, wavy(x, x + w2, 515 * U, 5 * U), OCHRE, 6 * U, prog(lt, a0 + 3.4, 0.6), ts, seed=80)
    write(c, TL.COPY["belief3"], x, 620 * U, s3, "body", TEAL, prog(lt, b0, 1.6), align="left")
    for i in range(5):                                   # a small flower, drawn when "healing" lands
        a = i / 5 * 2 * math.pi
        doodle(c, circle_pts(1780 * U + 26 * U * math.cos(a), 760 * U + 26 * U * math.sin(a), 18 * U, n=12), OCHRE,
               4 * U, prog(lt, b0 + 1.4 + 0.08 * i, 0.3), ts, seed=81 + i)
    doodle(c, [(1780 * U, 790 * U), (1772 * U, 880 * U)], LEAF, 5 * U, prog(lt, b0 + 1.3, 0.3), ts, seed=88)


def sh_journey(c, t, lt, dur, ts):
    k, sc = settle(lt)
    photo(c, clip("trail", lt), CX, PRINT_Y, 1180 * U, 590 * U, rot=-1.0, push=push(lt, dur) * sc, alpha=k)
    pts = [(250 * U, 900 * U), (420 * U, 860 * U), (560 * U, 905 * U), (700 * U, 870 * U)]
    doodle(c, pts, TERRA, 5 * U, prog(lt, 0.4, 1.2), ts, seed=90)
    doodle(c, [(680 * U, 850 * U), (705 * U, 870 * U), (680 * U, 892 * U)], TERRA, 5 * U, prog(lt, 1.6, 0.3), ts, seed=91)


def sh_sketchbooks(c, t, lt, dur, ts):
    k, sc = settle(lt, 0.4)
    photo(c, clip("page_glasses", lt), CX, PRINT_Y, 620 * U, 614 * U, rot=2.0, push=push(lt, dur, 0.03) * sc, alpha=k,
          tape_col=TEAL)


def sh_artist_dates(c, t, lt, dur, ts):
    k, sc = settle(lt, 0.4)
    photo(c, clip("bridge", lt), CX, PRINT_Y, 1180 * U, 590 * U, rot=1.2, push=push(lt, dur) * sc, alpha=k)


def sh_artists_way(c, t, lt, dur, ts):
    bx, by, bw, bh = 560 * U, 450 * U, 400 * U, 520 * U
    corners = [(bx - bw / 2, by - bh / 2), (bx + bw / 2, by - bh / 2), (bx + bw / 2, by + bh / 2),
               (bx - bw / 2, by + bh / 2), (bx - bw / 2, by - bh / 2)]
    cover = smooth_path(wobble_points(poly(corners)[:-1], 2 * U, ts, 100, True), True)
    kf = ease_out_cubic(prog(lt, 1.0, 0.7))
    if kf > 0:
        hatch_fill(c, cover, OCHRE, ts, spacing=14 * U, width=5 * U, seed=101, alpha=0.55 * kf)
    rect = [(bx - bw / 2, by - bh / 2), (bx + bw / 2, by - bh / 2), (bx + bw / 2, by + bh / 2), (bx - bw / 2, by + bh / 2),
            (bx - bw / 2, by - bh / 2)]
    doodle(c, poly(rect), INK, 6 * U, prog(lt, 0.1, 1.0), ts, seed=102)
    doodle(c, [(bx - bw / 2 + 34 * U, by - bh / 2), (bx - bw / 2 + 34 * U, by + bh / 2)], INK, 5 * U,
           prog(lt, 0.9, 0.3), ts, seed=103)
    write(c, TL.COPY["book1"], bx + 16 * U, by - 40 * U, fit(TL.COPY["book1"], "display", 72 * U, bw - 70 * U), "display",
          INK, prog(lt, 1.4, 1.0))
    write(c, TL.COPY["book2"], bx + 16 * U, by + 60 * U, 46 * U, "serif", INK, prog(lt, 2.2, 0.8))
    c0 = TL.ps("bookc") - (t - lt)                      # "and books like it": two more books join the stack
    for i, (ox, oy, ww, hh) in enumerate([(-250, 60, 120, 400), (-360, 100, 100, 330)]):
        x0, y1 = bx - bw / 2 + ox * U + 120 * U, by + bh / 2
        pts = [(x0, y1), (x0, y1 - hh * U), (x0 + ww * U, y1 - hh * U), (x0 + ww * U, y1), (x0, y1)]
        doodle(c, poly(pts), TEAL if i == 0 else TERRA, 5 * U, prog(lt, c0 + 0.15 * i, 0.6), ts, seed=110 + i)
    k, sc = settle(lt - 0.5)
    photo(c, clip("seeds", lt), 1350 * U, 470 * U, 760 * U, 380 * U, rot=2.4, push=push(lt, dur) * sc, alpha=k)


def sh_thanks(c, t, lt, dur, ts):
    pages = [("page_figs", 470, -4.0, OCHRE), ("page_hat", 960, 1.5, TEAL), ("page_mosaic", 1450, 3.5, BLUSH)]
    for i, (nm, x, rot, tc) in enumerate(pages):
        kp = ease_out_back(prog(lt, 0.1 + 0.35 * i, 0.5))
        if kp <= 0:
            continue
        img = clip(nm, lt - 0.35 * i)
        hh = 470 * U
        ww = hh * img.width() / img.height()
        photo(c, img, x * U, PRINT_Y + (1 - kp) * 40 * U, ww * kp, hh * kp, rot=rot, alpha=clamp(kp), tape_col=tc)
    for i, (hx, hy, s) in enumerate([(700, 150, 40), (1210, 140, 34), (960, 850, 0)]):
        if s:
            doodle(c, heart_pts(hx * U, hy * U, s * U), TERRA, 5 * U, prog(lt, 1.3 + 0.3 * i, 0.5), ts, seed=120 + i)


def sh_end(c, t, lt, dur, ts):
    doodle(c, heart_pts(CX, 290 * U, 70 * U), TERRA, 7 * U, prog(lt, 0.2, 1.0), ts, seed=130)
    hs = fit(TL.COPY["handle"], "display", 120 * U, W * 0.8)
    write(c, TL.COPY["handle"], CX, 470 * U, hs, "display", INK, ease_in_out_cubic(prog(lt, 0.5, 1.6)))
    doodle(c, wavy(CX - 300 * U, CX + 300 * U, 545 * U, 5 * U), OCHRE, 6 * U, prog(lt, 2.0, 0.6), ts, seed=131)
    after = TL.pe("shareb") - (t - lt) + 0.3             # written once the spoken line (and its caption) is done
    write(c, TL.COPY["end_line"], CX, 660 * U, 70 * U, "body", TEAL, prog(lt, after, 1.4))
    for i in range(5):
        a = i / 5 * 2 * math.pi
        doodle(c, circle_pts(CX + 22 * U * math.cos(a), 790 * U + 22 * U * math.sin(a), 15 * U, n=12), OCHRE, 4 * U,
               prog(lt, after + 1.2 + 0.08 * i, 0.3), ts, seed=140 + i)


SHOTS = {"title": sh_title, "five_hundred": sh_five_hundred, "banker": sh_banker, "art": sh_art, "rain": sh_rain,
         "sun": sh_sun, "belief": sh_belief, "journey": sh_journey, "sketchbooks": sh_sketchbooks,
         "artist_dates": sh_artist_dates, "artists_way": sh_artists_way, "thanks": sh_thanks, "end": sh_end}


def captions(c, t):
    caps = sorted(TL.CAPTIONS)
    for i, (s, e, txt) in enumerate(caps):
        # each caption is fully gone before the next one starts (no overlapping lines)
        nxt = caps[i + 1][0] - 0.12 if i + 1 < len(caps) else TL.DURATION
        out_end = min(e + 0.35, nxt)
        out_dur = min(0.25, max(0.06, out_end - e))
        if s - 0.12 <= t < out_end:
            a = ease_out_cubic(prog(t, s - 0.12, 0.2)) * (1 - prog(t, out_end - out_dur, out_dur))
            size = fit(txt, "body", 66 * U, W * 0.86)
            text(c, txt, CX, CAP_Y, size=size, font="body", fill=INK, alpha=0.92 * a)


def draw_shot(c, idx, t):
    s, e, name = TL.SHOTS[idx]
    lt = t - s
    SHOTS[name](c, t, lt, e - s, stepped(t, 12))


def draw(c, t):
    c.drawImage(PAPER, 0, 0)
    idx = next((i for i, (s, e, _) in enumerate(TL.SHOTS) if s <= t < e), len(TL.SHOTS) - 1)
    draw_shot(c, idx, t)
    s = TL.SHOTS[idx][0]
    if idx > 0 and t - s < TL.XFADE:                      # outgoing shot dissolves away over the new one
        a = 1 - ease_in_out_cubic((t - s) / TL.XFADE)
        c.saveLayerAlpha(None, int(255 * a))
        c.drawImage(PAPER, 0, 0)
        draw_shot(c, idx - 1, t)
        c.restore()
    captions(c, t)
    fade = prog(t, TL.DURATION - 1.0, 1.0)               # end on the empty page
    if fade > 0:
        c.saveLayerAlpha(None, int(255 * fade))
        c.drawImage(PAPER, 0, 0)
        c.restore()


def post(a, t):
    return grain(vignette(a, 0.16), 0.02, int(t * TL.FPS))


def build_audio():
    Path("work").mkdir(exist_ok=True)
    bar = 4 * 60 / TL.BPM
    ak.write_wav("work/music.wav", ak.music_bed(TL.MOOD, bars=math.ceil(TL.DURATION / bar) + 1, bpm=TL.BPM,
                                                intro_bars=1, seed=TL.MUSIC_SEED))
    rng = np.random.default_rng(5)                        # soft vinyl crackle for the nostalgic warmth
    n = int(TL.DURATION * ak.SR)
    cr = np.zeros(n, np.float32)
    for i in rng.integers(0, n - 200, int(TL.DURATION * 18)):
        cr[i:i + 40] += rng.normal(0, 1, 40).astype(np.float32) * np.exp(-np.arange(40) / 6) * rng.uniform(0.05, 0.4)
    hiss = rng.normal(0, 0.004, n).astype(np.float32)
    cr = ak.filt(cr + hiss, "lp", 5000)
    cr = cr / (np.max(np.abs(cr)) + 1e-9) * 0.08
    ak.write_wav("work/crackle.wav", np.stack([cr, cr], 1))
    Path("work/cues.json").write_text(json.dumps(TL.cues(), indent=1))
    import subprocess
    subprocess.run([sys.executable, "vibe/audio_kit.py", "mix", "work/cues.json", "-o", "work/mix.wav"], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        times = [float(x) for x in sys.argv[2:]] or [s + (e - s) * 0.7 for s, e, _ in TL.SHOTS]
        S.stills(draw, times, post=post)
    elif cmd == "audio":
        build_audio()
    elif cmd == "draft":
        S.render(draw, "out/draft.mp4", audio="work/mix.wav", draft=True)
    elif cmd == "render":
        if not Path("work/mix.wav").exists():
            build_audio()
        S.render(draw, "out/unrushed-intro.mp4", audio="work/mix.wav", post=post)
    else:
        sys.exit(__doc__)
