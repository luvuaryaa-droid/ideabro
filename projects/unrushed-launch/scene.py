"""scene: Unrushed Studio launch Reel. Every frame is a pure function of time t.

    python3 scene.py stills 1.2 3.6 ...     # check frames -> out/stills/
    python3 scene.py audio                  # music + sfx -> work/mix.wav
    python3 scene.py draft                  # half-res preview -> out/draft.mp4
    python3 scene.py render                 # final -> out/unrushed-launch.mp4
"""

import json
import math
import os
import sys
from pathlib import Path

import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
import audio_kit as ak  # noqa: E402
from motion_kit import (Stage, VideoFrames, clamp, draw_image, ease_in_out_cubic, ease_out_back,  # noqa: E402
                        ease_out_cubic, ease_out_expo, image, lerp, prog, pulse, rgb, rrect, shadow, stagger,
                        text, text_width, wrap)

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
B = S.brand
U = min(TL.W, TL.H) / 1080
PAPER, INK, PINK, BLUE = rgb(B, "paper"), rgb(B, "ink"), rgb(B, "pink"), rgb(B, "blue")
CREAM, NIGHT, WHITE = rgb(B, "cream"), rgb(B, "night"), rgb(B, "white")
CX = TL.W / 2
TOP, BOTTOM = 250 * U, TL.H - 420 * U        # 9:16 safe zone (top 250, bottom 420)
MID = (TOP + BOTTOM) / 2

_VID = {}


def video(key, w, h):
    if key not in _VID:
        _VID[key] = VideoFrames(TL.MEDIA[key], int(w), int(h), fps=TL.FPS)
    return _VID[key]


def fit(s, size, font, max_w):
    return min(size, max_w / max(1, text_width(s, 100, font)) * 100)


def sticker(c, s, cx, cy, size, k, fill=PINK, ink=INK, rot=-3.0, font="mono"):
    """rounded label that bounces on, like the Unrushed 'Sticker' title."""
    if k <= 0:
        return
    w = text_width(s, size, font) + size * 1.4
    h = size * 1.9
    c.save()
    c.translate(cx, cy)
    c.rotate(rot * (2 - k))
    c.scale(k, k)
    shadow(c, -w / 2, -h / 2, w, h, h / 2, blur=18 * U, dy=10 * U, alpha=0.22)
    rrect(c, -w / 2, -h / 2, w, h, h / 2, fill)
    rrect(c, -w / 2, -h / 2, w, h, h / 2, CREAM, stroke=5 * U)
    text(c, s, 0, 0, size=size, font=font, fill=ink)
    c.restore()


def headline(c, lines, lt, y0, size=92, font="display", col=None, gap=1.12):
    for i, s in enumerate(lines):
        k = stagger(lt, i, 0.05, 0.18, 0.45, ease_out_back)
        sz = fit(s, size * U, font, TL.W - 2 * 90 * U - 140 * U)
        text(c, s, CX - 70 * U * 0, y0 + i * sz * gap + (1 - k) * 60 * U, size=sz, font=font,
             fill=col or INK, alpha=clamp(k * 2))


def exit_k(lt, dur, d=0.3):
    return ease_in_out_cubic(prog(lt, dur - d, d))


def phone(c, cx, cy, w, draw_screen, lt, tilt=0.0):
    h = w * 16 / 9 + 40 * U
    k = ease_out_back(prog(lt, 0.0, 0.55))
    c.save()
    c.translate(cx, cy + (1 - k) * 500 * U)
    c.rotate(tilt * (1 - 0.5 * k))
    x, y = -w / 2 - 18 * U, -h / 2
    shadow(c, x, y, w + 36 * U, h, 64 * U, blur=40 * U, dy=24 * U, alpha=0.3)
    rrect(c, x, y, w + 36 * U, h, 64 * U, NIGHT)
    sx, sy, sw, sh = -w / 2, -h / 2 + 20 * U, w, w * 16 / 9
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx, sy, sw, sh), 56 * U, 56 * U), doAntiAlias=True)
    draw_screen(c, sx, sy, sw, sh)
    c.restore()
    c.restore()


# ---------------------------------------------------------------- scenes
VC = MID + 190 * U          # centre of the demo area under the feature header


def s_hook(c, t, lt, dur):
    z = 1.08 + 0.06 * lt / dur
    draw_image(c, TL.MEDIA["hook_bg"], CX - TL.W * z / 2, TL.H / 2 - TL.H * z / 2, TL.W * z, TL.H * z)
    c.drawRect(skia.Rect.MakeWH(TL.W, TL.H), skia.Paint(Color=rgb(B, "night", 0.48)))
    a, b = TL.COPY["hook"]
    ka = ease_out_back(prog(lt, 0.0, 0.4))
    sz = fit(a, 170 * U, "display", TL.W - 260 * U)
    text(c, a, CX - 40 * U, MID - 120 * U, size=sz * (0.6 + 0.4 * ka), font="display", fill=CREAM,
         alpha=clamp(ka * 2))
    sticker(c, b, CX - 30 * U, MID + 110 * U, fit(b, 96 * U, "display", TL.W - 420 * U),
            ease_out_back(prog(lt, TL.BEAT * 2, 0.45)), font="display", ink=NIGHT)


def s_problem(c, t, lt, dur):
    c.clear(PAPER)
    a, b = TL.COPY["problem"]
    ka = ease_out_cubic(prog(lt, 0.05, 0.5))
    kb = ease_out_cubic(prog(lt, 0.8, 0.5))
    text(c, a, CX - 40 * U, MID - 90 * U + (1 - ka) * 40 * U, size=fit(a, 120 * U, "hand", TL.W - 300 * U),
         font="hand", fill=INK, alpha=ka)
    text(c, b, CX - 40 * U, MID + 80 * U + (1 - kb) * 40 * U, size=fit(b, 112 * U, "hand", TL.W - 300 * U),
         font="hand", fill=PINK, alpha=kb)


def s_reveal(c, t, lt, dur):
    c.clear(NIGHT)
    r = lerp(0, TL.H, ease_out_expo(prog(lt, 0.0, 0.5)))
    c.drawCircle(CX, MID, r, skia.Paint(Color=PINK, AntiAlias=True))
    bump = 1 + 0.05 * pulse(t, TL.BPM)
    a, b = TL.COPY["brand"]
    sz = fit(a, 230 * U, "display", TL.W - 300 * U)
    ka = ease_out_back(prog(lt, 0.1, 0.4))
    kb = ease_out_back(prog(lt, 0.35, 0.4))
    text(c, a, CX - 40 * U, MID - 120 * U, size=sz * bump * (0.5 + 0.5 * ka), font="display", fill=NIGHT,
         alpha=clamp(ka * 2))
    text(c, b, CX - 40 * U, MID + 90 * U, size=sz * 0.8 * bump * (0.5 + 0.5 * kb), font="display", fill=CREAM,
         alpha=clamp(kb * 2))
    sub = TL.COPY["brand_sub"]
    sticker(c, sub, CX - 40 * U, MID + 300 * U, fit(sub, 44 * U, "mono", TL.W - 480 * U),
            ease_out_back(prog(lt, 0.9, 0.45)), fill=CREAM, ink=NIGHT, rot=2)


def header(c, lt, badge, title, line, bg):
    """feature header: '3 / 8' badge, big title, one plain line."""
    c.clear(bg)
    sticker(c, badge, CX - 40 * U, TOP + 50 * U, 34 * U, ease_out_back(prog(lt, 0.0, 0.35)), fill=NIGHT,
            ink=CREAM, rot=-2)
    kt = ease_out_back(prog(lt, 0.1, 0.4))
    sz = fit(title, 128 * U, "display", TL.W - 300 * U)
    text(c, title, CX - 40 * U, TOP + 180 * U + (1 - kt) * 50 * U, size=sz, font="display", fill=INK,
         alpha=clamp(kt * 2))
    kl = ease_out_cubic(prog(lt, 0.3, 0.45))
    lines = wrap(line, 50 * U, TL.W - 300 * U, "body")
    for i, ln in enumerate(lines):
        text(c, ln, CX - 40 * U, TOP + 290 * U + i * 64 * U, size=50 * U, font="body", fill=INK, alpha=kl)


def chip_row(c, words, y, lt, t0=0.6, size=40):
    size *= U
    ws = [text_width(w, size, "mono") + 56 * U for w in words]
    gap = 18 * U
    total = sum(ws) + gap * (len(ws) - 1)
    if total > TL.W - 260 * U:                 # shrink to fit inside the safe width
        f = (TL.W - 260 * U) / total
        size, ws, gap, total = size * f, [w * f for w in ws], gap * f, TL.W - 260 * U
    x = CX - 40 * U - total / 2
    h = size * 1.9
    for i, (w, wd) in enumerate(zip(words, ws)):
        k = stagger(lt, i, t0, TL.BEAT / 2, 0.35, ease_out_back)
        if k > 0:
            c.save()
            c.translate(x + wd / 2, y)
            c.scale(k, k)
            rrect(c, -wd / 2, -h / 2, wd, h, h / 2, [PINK, BLUE, CREAM, PINK][i % 4])
            text(c, w, 0, 0, size=size, font="mono", fill=CREAM if i % 4 == 1 else NIGHT)
            c.restore()
        x += wd + gap


def card(c, cx, cy, w, h, lt, draw_in, rot=0.0, t0=0.15):
    k = ease_out_back(prog(lt, t0, 0.5))
    if k <= 0:
        return
    c.save()
    c.translate(cx, cy + (1 - k) * 400 * U)
    c.rotate(rot * (2 - k))
    shadow(c, -w / 2, -h / 2, w, h, 28 * U, blur=32 * U, alpha=0.28)
    rrect(c, -w / 2 - 14 * U, -h / 2 - 14 * U, w + 28 * U, h + 28 * U, 34 * U, CREAM)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 20 * U, 20 * U), True)
    draw_in(c, -w / 2, -h / 2, w, h)
    c.restore()
    c.restore()


def badge_for(name):
    return f"{TL.FEATURES.index(name) + 1} / {len(TL.FEATURES)}"


def s_styles(c, t, lt, dur):
    cp = TL.COPY["styles"]
    header(c, lt, cp["badge"], cp["title"], cp["line"], PAPER)
    out = exit_k(lt, dur)
    for i, key in enumerate(["styles2", "styles"]):
        img = image(TL.MEDIA[key])
        w = 700 * U
        h = w * img.height() / img.width()
        card(c, CX - 40 * U + (i * 2 - 1) * 26 * U - out * TL.W, VC + 40 * U, w, h, lt,
             lambda cc, x, y, ww, hh, k=key: draw_image(cc, TL.MEDIA[k], x, y, ww, hh, cover=False),
             rot=-4 if i == 0 else 3, t0=0.3 + i * 0.25)
    kt = prog(lt, 2.2, 0.6)                      # the "pick a number" tap
    if 0 < kt < 1:
        c.drawCircle(CX - 230 * U, VC - 60 * U, lerp(10, 90, ease_out_cubic(kt)) * U,
                     skia.Paint(Color=rgb(B, "pink", 1 - kt), Style=skia.Paint.kStroke_Style,
                                StrokeWidth=10 * U, AntiAlias=True))


def video_screen(key, offset=0.0):
    def draw(cc, x, y, w, h, lt):
        cc.drawImage(video(key, w, h).at(offset + lt), x, y)
    return draw


def s_edit(c, t, lt, dur):
    cp = TL.COPY["f_edit"]
    header(c, lt, badge_for("f_edit"), cp["title"], cp["line"], CREAM)
    scr = video_screen("f_edit", 0.2)
    phone(c, CX - 40 * U, VC - 40 * U, 360 * U, lambda cc, x, y, w, h: scr(cc, x, y, w, h, lt), lt, tilt=-3)
    chip_row(c, cp["chips"], BOTTOM - 20 * U, lt, t0=0.9)


def s_cinematic(c, t, lt, dur):
    cp = TL.COPY["f_cinematic"]
    header(c, lt, badge_for("f_cinematic"), cp["title"], cp["line"], PAPER)
    w = 820 * U
    h = w * 880 / 1920
    scr = video_screen("f_cinematic")
    card(c, CX - 40 * U, VC - 30 * U, w, h, lt, lambda cc, x, y, ww, hh: scr(cc, x, y, ww, hh, lt), rot=-2)
    chip_row(c, cp["chips"], VC + h / 2 + 140 * U, lt, t0=0.9, size=44)


def s_fix(c, t, lt, dur):
    cp = TL.COPY["f_fix"]
    header(c, lt, badge_for("f_fix"), cp["title"], cp["line"], CREAM)
    img = image(TL.MEDIA["before"])
    w = 620 * U
    h = w * img.height() / img.width()
    wipe = ease_in_out_cubic(prog(lt, 1.0, 1.4))

    def draw_in(cc, x, y, ww, hh):
        draw_image(cc, TL.MEDIA["before"], x, y, ww, hh)
        cc.save()
        cc.clipRect(skia.Rect.MakeXYWH(x, y, ww * wipe, hh))
        draw_image(cc, TL.MEDIA["after"], x, y, ww, hh)
        cc.restore()
        if 0 < wipe < 1:
            cc.drawRect(skia.Rect.MakeXYWH(x + ww * wipe - 3 * U, y, 6 * U, hh), skia.Paint(Color=CREAM))
    card(c, CX - 40 * U, VC - 20 * U, w, h, lt, draw_in, rot=2)
    label = cp["after"] if wipe > 0.5 else cp["before"]
    sticker(c, label, CX - 40 * U, VC + h / 2 + 70 * U, 40 * U, ease_out_back(prog(lt, 0.6, 0.35)),
            fill=PINK if wipe > 0.5 else rgb("#DDC654"), ink=NIGHT, rot=-2)


def s_nofilm(c, t, lt, dur):
    cp = TL.COPY["f_nofilm"]
    header(c, lt, badge_for("f_nofilm"), cp["title"], cp["line"], PAPER)
    scr = video_screen("f_nofilm")
    phone(c, CX - 40 * U, VC + 10 * U, 380 * U, lambda cc, x, y, w, h: scr(cc, x, y, w, h, lt), lt, tilt=3)


def s_teach(c, t, lt, dur):
    cp = TL.COPY["f_teach"]
    header(c, lt, badge_for("f_teach"), cp["title"], cp["line"], CREAM)
    w = 640 * U
    h = 420 * U
    card(c, CX - 40 * U, VC - 130 * U, w, h, lt,
         lambda cc, x, y, ww, hh: draw_image(cc, TL.MEDIA["wide"], x, y, ww, hh), rot=-2)
    # step badges on the painting
    for i in range(3):
        k = ease_out_back(prog(lt, 0.8 + i * 0.25, 0.35))
        if k > 0:
            bx, by = CX - 40 * U - w / 2 + 70 * U + i * 120 * U, VC - 130 * U - h / 2 + 60 * U
            c.drawCircle(bx, by, 40 * U * k, skia.Paint(Color=PINK, AntiAlias=True))
            text(c, str(i + 1), bx, by, size=46 * U * k, font="display", fill=NIGHT)
    # "Colours I used" swatches (picked from the painting by the Teaching Kit)
    ky = VC + 210 * U
    text(c, cp["card"], CX - 40 * U, ky - 20 * U, size=64 * U, font="hand", fill=INK,
         alpha=ease_out_cubic(prog(lt, 1.4, 0.4)))
    n = len(cp["colors"])
    for i, hx in enumerate(cp["colors"]):
        k = ease_out_back(prog(lt, 1.6 + i * TL.BEAT / 3, 0.35))
        x = CX - 40 * U + (i - (n - 1) / 2) * 140 * U
        if k > 0:
            c.drawCircle(x, ky + 110 * U, 56 * U * k, skia.Paint(Color=rgb(hx), AntiAlias=True))
            c.drawCircle(x, ky + 110 * U, 56 * U * k, skia.Paint(Color=CREAM, Style=skia.Paint.kStroke_Style,
                                                                 StrokeWidth=6 * U, AntiAlias=True))


def s_sell(c, t, lt, dur):
    cp = TL.COPY["f_sell"]
    header(c, lt, badge_for("f_sell"), cp["title"], cp["line"], PAPER)
    phone(c, CX - 40 * U, VC - 20 * U, 360 * U,
          lambda cc, x, y, w, h: draw_image(cc, TL.MEDIA["f_sell"], x, y, w, h), lt, tilt=-3)
    sticker(c, cp["tag"], CX + 170 * U, VC - 200 * U, 44 * U, ease_out_back(prog(lt, 1.0, 0.4)), rot=8)
    text(c, cp["note"], CX - 40 * U, BOTTOM - 10 * U, size=36 * U, font="body", fill=INK,
         alpha=ease_out_cubic(prog(lt, 1.2, 0.4)))


def s_everywhere(c, t, lt, dur):
    cp = TL.COPY["f_everywhere"]
    header(c, lt, badge_for("f_everywhere"), cp["title"], cp["line"], CREAM)
    shapes = cp["shapes"]
    hmax = 300 * U
    pos = [(-260, -170), (40, -170), (290, -170), (-140, 190), (230, 190)]
    for i, (lab, a, b) in enumerate(shapes):
        k = ease_out_back(prog(lt, 0.5 + i * TL.BEAT / 2, 0.4))
        if k <= 0:
            continue
        h = hmax if b >= a else hmax * b / a * 1.4
        w = h * a / b
        cx, cy = CX - 40 * U + pos[i][0] * U, VC + pos[i][1] * U
        c.save()
        c.translate(cx, cy)
        c.scale(k, k)
        shadow(c, -w / 2, -h / 2, w, h, 16 * U, blur=20 * U, alpha=0.22)
        rrect(c, -w / 2 - 8 * U, -h / 2 - 8 * U, w + 16 * U, h + 16 * U, 18 * U, NIGHT)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h))
        draw_image(c, TL.MEDIA["square"], -w / 2, -h / 2, w, h)
        c.restore()
        sticker(c, lab, 0, h / 2 + 20 * U, 30 * U, 1.0, fill=PINK, rot=0)
        c.restore()


def s_batch(c, t, lt, dur):
    cp = TL.COPY["f_batch"]
    header(c, lt, badge_for("f_batch"), cp["title"], cp["line"], PAPER)
    pics = [TL.MEDIA["tall"], TL.MEDIA["square"], TL.MEDIA["wide"], TL.MEDIA["before"], TL.MEDIA["after"],
            TL.MEDIA["tall"]]
    sort = ease_in_out_cubic(prog(lt, 1.0, 1.0))
    tw, th = 190 * U, 190 * U
    for i, p in enumerate(pics):
        k = ease_out_back(prog(lt, 0.3 + i * 0.08, 0.35))
        if k <= 0:
            continue
        # messy pile -> two neat rows
        a = (i * 137) % 360
        mx = CX - 40 * U + math.cos(math.radians(a)) * 170 * U
        my = VC - 40 * U + math.sin(math.radians(a)) * 120 * U
        row, col = i % 2, i // 2
        nx = CX - 40 * U + (col - 1) * (tw + 30 * U) + 80 * U
        ny = VC - 140 * U + row * (th + 120 * U)
        x, y = lerp(mx, nx, sort), lerp(my, ny, sort)
        c.save()
        c.translate(x, y)
        c.rotate(lerp((i * 53) % 30 - 15, 0, sort))
        c.scale(k, k)
        shadow(c, -tw / 2, -th / 2, tw, th, 14 * U, blur=16 * U, alpha=0.25)
        rrect(c, -tw / 2 - 8 * U, -th / 2 - 8 * U, tw + 16 * U, th + 16 * U, 16 * U, CREAM)
        draw_image(c, p, -tw / 2, -th / 2, tw, th)
        c.restore()
    for r, lab in enumerate(cp["rows"]):
        text(c, lab, CX - 40 * U - (tw + 30 * U) - 30 * U, VC - 140 * U + r * (th + 120 * U), size=46 * U,
             font="hand", fill=INK, align="right", alpha=sort)


def s_how(c, t, lt, dur):
    c.clear(INK)
    steps = TL.COPY["how"]
    for i, s in enumerate(steps):
        k = stagger(lt, i, 0.1, TL.BEAT * 1.1, 0.4, ease_out_back)
        y = MID - 220 * U + i * 220 * U
        c.drawCircle(CX - 330 * U, y, 52 * U * k, skia.Paint(Color=PINK, AntiAlias=True))
        text(c, str(i + 1), CX - 330 * U, y, size=60 * U * k, font="display", fill=NIGHT)
        lines = wrap(s, 64 * U, 560 * U, "hand")
        for j, ln in enumerate(lines):
            text(c, ln, CX - 250 * U, y + (j - (len(lines) - 1) / 2) * 66 * U, size=64 * U, font="hand",
                 fill=CREAM, align="left", alpha=clamp(k * 2))


def s_endcard(c, t, lt, dur):
    c.clear(NIGHT)
    k = ease_out_expo(prog(lt, 0.0, 0.6))
    c.drawCircle(CX, MID, lerp(0, TL.H, k), skia.Paint(Color=INK, AntiAlias=True))
    a, b = TL.COPY["brand"]
    ka = ease_out_back(prog(lt, 0.1, 0.45))
    text(c, f"{a} {b}", CX - 40 * U, TOP + 90 * U, size=fit(f"{a} {b}", 110 * U, "display", TL.W - 300 * U),
         font="display", fill=PINK, alpha=clamp(ka * 2))
    kp = ease_out_back(prog(lt, 0.5, 0.5))
    cw, ch = 720 * U, 480 * U
    if kp > 0:
        c.save()
        c.translate(CX - 40 * U, MID - 20 * U)
        c.scale(kp, kp)
        c.rotate(-2)
        shadow(c, -cw / 2, -ch / 2, cw, ch, 50 * U, blur=40 * U, alpha=0.35)
        rrect(c, -cw / 2, -ch / 2, cw, ch, 50 * U, CREAM)
        lab = TL.COPY["price_label"]
        text(c, lab, 0, -ch / 2 + 70 * U, size=fit(lab, 38 * U, "mono", cw - 80 * U), font="mono", fill=INK)
        bump = 1 + 0.04 * pulse(t, TL.BPM)
        text(c, TL.COPY["price"], 0, 10 * U, size=230 * U * bump, font="display", fill=NIGHT)
        was = f"then {TL.COPY['price_was']}"
        fs = 56 * U
        ww = text_width(was, fs, "body")
        pre = text_width("then ", fs, "body")
        yy = ch / 2 - 70 * U
        text(c, was, 0, yy, size=fs, font="body", fill=INK)
        sk = ease_out_cubic(prog(lt, 1.2, 0.3))
        c.drawLine(-ww / 2 + pre, yy, -ww / 2 + pre + (ww - pre) * sk, yy,
                   skia.Paint(Color=PINK, StrokeWidth=7 * U, AntiAlias=True))
        c.restore()
    ke = ease_out_cubic(prog(lt, 1.6, 0.5))
    text(c, TL.COPY["edit_only"], CX - 40 * U, MID + 290 * U, size=44 * U, font="body", fill=CREAM, alpha=ke)
    kc = ease_out_back(prog(lt, 1.9, 0.45))
    sticker(c, TL.COPY["cta"], CX - 40 * U, MID + 420 * U, 60 * U, kc, rot=2)
    tag = TL.COPY["tagline"]
    kt = ease_out_cubic(prog(lt, 2.6, 0.6))
    text(c, tag, CX - 40 * U, BOTTOM - 20 * U, size=fit(tag, 52 * U, "hand", TL.W - 300 * U), font="hand",
         fill=CREAM, alpha=kt)


SCENES = {"hook": s_hook, "problem": s_problem, "reveal": s_reveal, "styles": s_styles,
          "f_edit": s_edit, "f_cinematic": s_cinematic, "f_fix": s_fix, "f_nofilm": s_nofilm,
          "f_teach": s_teach, "f_sell": s_sell, "f_everywhere": s_everywhere, "f_batch": s_batch,
          "how": s_how, "endcard": s_endcard}


def draw(c, t):
    name, lt, dur = TL.scene_at(t)
    SCENES[name](c, t, lt, dur)


def build_audio():
    Path("work").mkdir(exist_ok=True)
    ak.write_wav("work/music.wav", ak.music_bed(TL.MOOD, seconds=TL.DURATION, bpm=TL.BPM, intro_bars=0))
    Path("work/cues.json").write_text(json.dumps(TL.cues(), indent=1))
    import subprocess
    subprocess.run([sys.executable, "vibe/audio_kit.py", "mix", "work/cues.json", "-o", "work/mix.wav"], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        times = [float(x) for x in sys.argv[2:]] or [s + (e - s) * 0.75 for s, e, _ in TL.SCENES]
        S.stills(draw, times)
    elif cmd == "audio":
        build_audio()
    elif cmd == "draft":
        S.render(draw, "out/draft.mp4", audio="work/mix.wav", draft=True)
    elif cmd == "render":
        if not Path("work/mix.wav").exists():
            build_audio()
        suffix = f"_{TL.W}x{TL.H}" if os.environ.get("VIBE_SIZE") else ""
        S.render(draw, f"out/unrushed-launch{suffix}.mp4", audio="work/mix.wav")
    else:
        sys.exit(__doc__)
