"""scene: Unrushed Studio install tutorial (16:9). Every frame is a pure function of time t.

    python3 make_vo.py                      # voice lines + real durations (run first)
    python3 scene.py stills 5 30 ...        # check frames -> out/stills/
    python3 scene.py audio                  # voice + music + sfx -> work/mix.wav
    python3 scene.py render                 # final -> out/unrushed-install.mp4
    python3 scene.py chapters               # YouTube chapter list
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
import audio_kit as ak  # noqa: E402
from motion_kit import (Stage, clamp, draw_image, image, ease_in_out_cubic, ease_out_back, ease_out_cubic,  # noqa: E402
                        lerp, prog, rgb, rrect, shadow, text, text_width, wrap)

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
B = S.brand
U = min(TL.W, TL.H) / 1080
PAPER, INK, PINK, BLUE = rgb(B, "paper"), rgb(B, "ink"), rgb(B, "pink"), rgb(B, "blue")
CREAM, NIGHT, WHITE = rgb(B, "cream"), rgb(B, "night"), rgb(B, "white")
M = TL.W * 0.05                       # 16:9 safe margin 5 %
TERM_BG = rgb("#1F1A24")
STEPS = ["open", "attach", "repo", "install"]


# ---------------------------------------------------------------- helpers
def check(c, x, y, s, col=PINK, k=1.0):
    """vector check mark, (x, y) = left-middle, s = height."""
    if k <= 0:
        return
    p = skia.Path()
    p.moveTo(x, y)
    p.lineTo(x + s * 0.35, y + s * 0.35)
    p.lineTo(x + s * 0.95, y - s * 0.45)
    m = skia.PathMeasure(p, False)
    seg = skia.Path()
    m.getSegment(0, m.getLength() * clamp(k), seg, True)
    c.drawPath(seg, skia.Paint(Color=col, Style=skia.Paint.kStroke_Style, StrokeWidth=s * 0.2,
                               StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, AntiAlias=True))


def ctext(c, s, x, y, size, col, font="code", alpha=1.0):
    """left-aligned text where every ✓ is drawn as a vector check."""
    parts = s.split("✓")
    for i, part in enumerate(parts):
        if part:
            text(c, part, x, y, size=size, font=font, fill=col, align="left", alpha=alpha)
            x += text_width(part, size, font)
        if i < len(parts) - 1:
            check(c, x + size * 0.1, y, size * 0.8, PINK, alpha)
            x += size * 1.1


def typed(s, since, cps=22):
    n = int(clamp(since * cps, 0, len(s)))
    return s[:n], n < len(s)


def window(c, x, y, w, h, title, dark=False, k=1.0):
    if k <= 0:
        return
    c.save()
    c.translate(x + w / 2, y + h / 2 + (1 - k) * 120 * U)
    c.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
    c.translate(-(x + w / 2), -(y + h / 2))
    shadow(c, x, y, w, h, 24 * U, blur=36 * U, dy=18 * U, alpha=0.25 * k)
    rrect(c, x, y, w, h, 24 * U, TERM_BG if dark else WHITE)
    rrect(c, x, y, w, 58 * U, 24 * U, rgb("#2C2533") if dark else rgb("#EFE7EA"))
    c.drawRect(skia.Rect.MakeXYWH(x, y + 34 * U, w, 24 * U), skia.Paint(Color=rgb("#2C2533") if dark else rgb("#EFE7EA")))
    for i, col in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        c.drawCircle(x + 34 * U + i * 30 * U, y + 29 * U, 9 * U, skia.Paint(Color=rgb(col), AntiAlias=True))
    text(c, title, x + w / 2, y + 30 * U, size=26 * U, font="body", fill=CREAM if dark else INK)
    c.restore()


def folder_icon(c, x, y, s, col=BLUE, label=None, lab_col=INK):
    rrect(c, x, y + s * 0.12, s * 0.45, s * 0.2, s * 0.06, col)
    rrect(c, x, y + s * 0.2, s, s * 0.7, s * 0.08, col)
    if label:
        lines = wrap(label, 20 * U, s * 1.5, "body")
        for i, ln in enumerate(lines[:2]):
            text(c, ln, x + s / 2, y + s * 1.08 + i * 24 * U, size=20 * U, font="body", fill=lab_col)


def file_icon(c, x, y, s, col, tag):
    rrect(c, x + s * 0.12, y, s * 0.76, s, s * 0.08, WHITE)
    rrect(c, x + s * 0.12, y, s * 0.76, s, s * 0.08, rgb(B, "ink", 0.3), stroke=2 * U)
    rrect(c, x + s * 0.2, y + s * 0.6, s * 0.6, s * 0.24, s * 0.05, col)
    text(c, tag, x + s / 2, y + s * 0.72, size=s * 0.15, font="mono", fill=CREAM)


def keycap(c, x, y, s, label, k=1.0):
    if k <= 0:
        return
    w = max(s, text_width(label, s * 0.42, "code") + s * 0.5)
    c.save()
    c.translate(x + w / 2, y + s / 2)
    c.scale(k, k)
    shadow(c, -w / 2, -s / 2, w, s, s * 0.18, blur=10 * U, dy=6 * U, alpha=0.3)
    rrect(c, -w / 2, -s / 2, w, s, s * 0.18, CREAM)
    rrect(c, -w / 2, -s / 2, w, s, s * 0.18, INK, stroke=3 * U)
    text(c, label, 0, 0, size=s * 0.42, font="code", fill=INK)
    c.restore()
    return w


def sticker(c, s, cx, cy, size, k, fill=PINK, ink=NIGHT, rot=-2.0, font="mono"):
    if k <= 0:
        return
    w = text_width(s, size, font) + size * 1.4
    h = size * 1.9
    c.save()
    c.translate(cx, cy)
    c.rotate(rot * (2 - k))
    c.scale(k, k)
    shadow(c, -w / 2, -h / 2, w, h, h / 2, blur=14 * U, dy=8 * U, alpha=0.2)
    rrect(c, -w / 2, -h / 2, w, h, h / 2, fill)
    text(c, s, 0, 0, size=size, font=font, fill=ink)
    c.restore()


def items(key):
    return TL.SCENE_INFO[key][3]


def shown(key, t):
    """[(i, item, seconds since its line started)] for lines that have started."""
    out = []
    for i, (_txt, it) in enumerate(items(key)):
        k = TL.item_k(key, i, t)
        if k >= 0 and it is not None:
            out.append((i, it, k))
    return out


# ---------------------------------------------------------------- layout pieces
PANEL_X = 820 * U                       # demo panel on the right
PANEL_W = TL.W - M - PANEL_X
PANEL_Y, PANEL_H = 110 * U, 720 * U


def left_column(c, key, lt):
    chap, title, _view, _ = TL.SCENE_INFO[key]
    if chap:
        sticker(c, chap.upper(), M + text_width(chap.upper(), 30 * U, "mono") / 2 + 30 * U, 170 * U, 30 * U,
                ease_out_back(prog(lt, 0.05, 0.35)), fill=NIGHT, ink=CREAM)
    kt = ease_out_cubic(prog(lt, 0.15, 0.45))
    lines = wrap(title, 92 * U, PANEL_X - M - 60 * U, "display")
    for i, ln in enumerate(lines):
        text(c, ln, M, 300 * U + i * 104 * U + (1 - kt) * 30 * U, size=92 * U, font="display", fill=INK,
             align="left", alpha=kt)
    # step progress
    if key in STEPS or key == "ready":
        cur = STEPS.index(key) if key in STEPS else len(STEPS)
        for i in range(len(STEPS)):
            x = M + i * 64 * U
            y = 300 * U + len(lines) * 104 * U + 30 * U
            done = i < cur
            col = PINK if i == cur else (INK if done else rgb(B, "ink", 0.18))
            c.drawCircle(x + 22 * U, y, 22 * U, skia.Paint(Color=col, AntiAlias=True))
            if done:
                check(c, x + 12 * U, y, 18 * U, CREAM)
            else:
                text(c, str(i + 1), x + 22 * U, y, size=24 * U, font="display",
                     fill=NIGHT if i == cur else CREAM)


def caption(c, t):
    ln = TL.line_at(t)
    if not ln:
        return
    s, e, key, i, txt, _ = ln
    k = ease_out_cubic(prog(t - s, 0, 0.25)) * (1 - ease_out_cubic(prog(t - e, 0, 0.3)))
    if k <= 0:
        return
    size = 36 * U
    lines = wrap(txt, size, TL.W - 2 * M - 120 * U, "body")
    h = len(lines) * size * 1.35 + 34 * U
    w = max(text_width(x, size, "body") for x in lines) + 70 * U
    y = TL.H - M - h + 10 * U
    rrect(c, TL.W / 2 - w / 2, y, w, h, 22 * U, rgb(B, "night", 0.86 * k))
    for j, x in enumerate(lines):
        text(c, x, TL.W / 2, y + 17 * U + size * 0.68 + j * size * 1.35, size=size, font="body", fill=CREAM,
             alpha=k)


# ---------------------------------------------------------------- views
def v_title(c, key, t, lt, dur):
    c.clear(NIGHT)
    z = 1.02 + 0.04 * lt / dur
    sq = 620 * U * z
    c.save()
    c.translate(TL.W - M - 330 * U, TL.H / 2 - 40 * U)
    c.rotate(4)
    shadow(c, -sq / 2, -sq / 2, sq, sq, 20 * U, blur=40 * U, alpha=0.4)
    rrect(c, -sq / 2 - 14 * U, -sq / 2 - 14 * U, sq + 28 * U, sq + 28 * U, 26 * U, CREAM)
    draw_image(c, "raw/clock.jpg", -sq / 2, -sq / 2, sq, sq)
    c.restore()
    title = TL.SCENE_INFO[key][1]
    kt = ease_out_back(prog(lt, 0.2, 0.5))
    for i, ln in enumerate(wrap(title, 120 * U, 980 * U, "display")):
        text(c, ln, M, 330 * U + i * 132 * U + (1 - kt) * 40 * U, size=120 * U, font="display", fill=PINK,
             align="left", alpha=clamp(kt * 2))
    for i, it, k in shown(key, t):
        sticker(c, it, M + text_width(it, 34 * U, "mono") / 2 + 40 * U, 680 * U, 34 * U,
                ease_out_back(prog(k, 0, 0.4)), fill=CREAM, rot=-2)


def v_checklist(c, key, t, lt, dur):
    c.clear(PAPER)
    left_column(c, key, lt)
    window(c, PANEL_X, PANEL_Y, PANEL_W, PANEL_H, "Checklist", k=ease_out_back(prog(lt, 0.2, 0.5)))
    rows = shown(key, t)
    for r, (i, it, k) in enumerate(rows):
        y = PANEL_Y + 170 * U + r * 150 * U
        kk = ease_out_back(prog(k, 0, 0.4))
        rrect(c, PANEL_X + 70 * U, y - 40 * U, 80 * U, 80 * U, 18 * U, CREAM)
        rrect(c, PANEL_X + 70 * U, y - 40 * U, 80 * U, 80 * U, 18 * U, INK, stroke=4 * U)
        check(c, PANEL_X + 88 * U, y, 46 * U, PINK, prog(k, 0.3, 0.4))
        text(c, it, PANEL_X + 190 * U, y, size=50 * U * (0.8 + 0.2 * kk), font="body", fill=INK, align="left",
             alpha=clamp(kk * 2))


def v_files(c, key, t, lt, dur):
    c.clear(PAPER)
    left_column(c, key, lt)
    window(c, PANEL_X, PANEL_Y, PANEL_W, PANEL_H, "Downloads", k=ease_out_back(prog(lt, 0.2, 0.5)))
    st = {i: k for i, it, k in shown(key, t)}
    x0, y0 = PANEL_X + 60 * U, PANEL_Y + 110 * U
    if 0 in st:
        kz = ease_out_back(prog(st[0], 0, 0.4))
        c.save()
        c.translate(x0 + 60 * U, y0 + 60 * U)
        c.scale(kz, kz)
        file_icon(c, -60 * U, -60 * U, 120 * U, BLUE, "ZIP")
        c.restore()
        text(c, items(key)[0][1], x0 + 150 * U, y0 + 60 * U, size=30 * U, font="code", fill=INK, align="left",
             alpha=kz)
    if 1 in st:
        kf = ease_out_back(prog(st[1], 0.3, 0.4))
        if kf > 0:
            c.save()
            c.translate(x0 + 60 * U, y0 + 230 * U)
            c.scale(kf, kf)
            folder_icon(c, -60 * U, -60 * U, 120 * U, PINK)
            c.restore()
            text(c, "Unrushed-Studio-Complete-v1.0", x0 + 150 * U, y0 + 230 * U, size=30 * U, font="code",
                 fill=INK, align="left", alpha=kf)
    if 2 in st:
        k2 = st[2]
        names = ["START-HERE.pdf", "STYLE-MENU.html"] + [f"unrushed-{n}" for n in
                                                        ["edit", "cinematic", "fix", "nofilm", "teach", "sell",
                                                         "everywhere", "batch"]]
        hi = st.get(3, -1) >= 0
        for j, nm in enumerate(names):
            kj = ease_out_back(prog(k2, 0.2 + j * 0.12, 0.35))
            if kj <= 0:
                continue
            col, row = j % 5, j // 5
            gx = x0 + 20 * U + col * 190 * U
            gy = y0 + 380 * U + row * 150 * U
            c.save()
            c.translate(gx + 45 * U, gy + 40 * U)
            c.scale(kj, kj)
            if j < 2:
                file_icon(c, -40 * U, -40 * U, 80 * U, NIGHT if j == 0 else PINK, "PDF" if j == 0 else "HTML")
            else:
                if hi:
                    rrect(c, -60 * U, -56 * U, 120 * U, 150 * U, 18 * U, rgb(B, "pink", 0.35))
                folder_icon(c, -40 * U, -40 * U, 80 * U, BLUE)
            c.restore()
            text(c, nm, gx + 45 * U, gy + 112 * U, size=19 * U, font="code", fill=INK)


def term_lines(key, t):
    """terminal transcript: [(kind, text, since)]"""
    out = []
    for i, it, k in shown(key, t):
        kind, s = it if isinstance(it, tuple) else ("note", it)
        out.append((kind, s, k))
    return out


def draw_term(c, x, y, w, h, rows, title="Terminal", k=1.0, prompt="$ "):
    window(c, x, y, w, h, title, dark=True, k=k)
    if k < 1:
        return
    size = 34 * U
    ly = y + 120 * U
    rows = rows[-8:]
    for n, (kind, s, since) in enumerate(rows):
        if kind == "cmd":
            shown_s, typing = typed(s, since - 0.2)
            last = n == len(rows) - 1
            cur = "▌" if typing or (last and int(since * 2) % 2 == 0) else ""
            ctext(c, prompt + shown_s + cur, x + 44 * U, ly, size, CREAM)
        elif kind == "ok":
            ctext(c, s, x + 44 * U, ly, size, rgb("#9BE7A8"), alpha=clamp(since * 3))
        elif kind in ("mac", "win"):
            tag = "Mac" if kind == "mac" else "Windows"
            rrect(c, x + 44 * U, ly - 22 * U, text_width(tag, 24 * U, "mono") + 30 * U, 44 * U, 22 * U,
                  PINK if kind == "mac" else BLUE)
            text(c, tag, x + 59 * U, ly, size=24 * U, font="mono", fill=NIGHT if kind == "mac" else CREAM,
                 align="left")
            ctext(c, s, x + 74 * U + text_width(tag, 24 * U, "mono") + 20 * U, ly, size, CREAM,
                  alpha=clamp(since * 3))
        else:  # note
            ctext(c, "# " + s, x + 44 * U, ly, size * 0.9, rgb("#B9A8C4"), alpha=clamp(since * 3))
        ly += 78 * U


def v_terminal(c, key, t, lt, dur):
    c.clear(PAPER)
    left_column(c, key, lt)
    draw_term(c, PANEL_X, PANEL_Y, PANEL_W, PANEL_H, term_lines(key, t),
              title="Terminal / PowerShell", k=ease_out_back(prog(lt, 0.2, 0.5)))


def v_browser(c, key, t, lt, dur, title, bar_label):
    c.clear(PAPER)
    left_column(c, key, lt)
    kw = ease_out_back(prog(lt, 0.2, 0.5))
    window(c, PANEL_X, PANEL_Y, PANEL_W, PANEL_H, title, k=kw)
    if kw < 1:
        return
    st = {}
    for i, it, k in shown(key, t):
        st[it[0]] = (it[1], k)
    # path bar
    bx, by, bw = PANEL_X + 30 * U, PANEL_Y + 80 * U, PANEL_W - 60 * U
    rrect(c, bx, by, bw, 64 * U, 14 * U, rgb("#F6F0F2"))
    rrect(c, bx, by, bw, 64 * U, 14 * U, rgb(B, "ink", 0.25), stroke=2 * U)
    path = ""
    if "path" in st:
        path, _ = typed(st["path"][0], st["path"][1] - 0.4, cps=14)
    text(c, path or bar_label, bx + 24 * U, by + 32 * U, size=28 * U, font="code",
         fill=INK if path else rgb(B, "ink", 0.4), align="left")
    # one-time terminal line
    if "cmd" in st:
        s, k = st["cmd"]
        draw_term_strip(c, PANEL_X + 30 * U, PANEL_Y + 170 * U, PANEL_W - 60 * U, s, k)
    # keys
    if "keys" in st and "drag" not in st:
        s, k = st["keys"]
        x = PANEL_X + PANEL_W / 2 - 170 * U
        for j, cap in enumerate(s.split()):
            w = keycap(c, x, PANEL_Y + 300 * U, 100 * U, cap, ease_out_back(prog(k, 0.1 + j * 0.25, 0.3)))
            x += (w or 100 * U) + 24 * U
    # folders dropped in
    if "drag" in st:
        k = st["drag"][1]
        for j in range(8):
            kj = ease_in_out_cubic(prog(k, 0.15 + j * 0.18, 0.6))
            col, row = j % 4, j // 4
            tx = PANEL_X + 90 * U + col * 220 * U
            ty = PANEL_Y + 300 * U + row * 190 * U
            sx, sy = PANEL_X - 260 * U, PANEL_Y + 500 * U
            x, y = lerp(sx, tx, kj), lerp(sy, ty, kj) - math.sin(kj * math.pi) * 120 * U
            if kj > 0:
                folder_icon(c, x, y, 100 * U, BLUE)
                if kj >= 1:
                    names = ["edit", "cinematic", "fix", "nofilm", "teach", "sell", "everywhere", "batch"]
                    text(c, f"unrushed-{names[j]}", x + 50 * U, y + 115 * U, size=19 * U, font="code", fill=INK)
    if "check" in st:
        s, k = st["check"]
        s = s.replace("✓", "").strip()
        kk = ease_out_back(prog(k, 0, 0.4))
        cx, cy = PANEL_X + PANEL_W / 2, PANEL_Y + PANEL_H - 70 * U
        sticker(c, s, cx, cy, 30 * U, kk, fill=CREAM, font="code", rot=0)
        check(c, cx + text_width(s, 30 * U, "code") / 2 + 50 * U, cy, 36 * U, PINK, prog(k, 0.3, 0.4))


def draw_term_strip(c, x, y, w, s, since):
    k = ease_out_cubic(prog(since, 0, 0.3))
    rrect(c, x, y, w, 90 * U, 16 * U, rgb("#1F1A24", None, k))
    shown_s, typing = typed(s, since - 0.3)
    ctext(c, "$ " + shown_s + ("▌" if typing else ""), x + 30 * U, y + 45 * U, 32 * U, CREAM, alpha=k)


def v_finder(c, key, t, lt, dur):
    v_browser(c, key, t, lt, dur, "Finder", "Go to folder…")


def v_explorer(c, key, t, lt, dur):
    v_browser(c, key, t, lt, dur, "File Explorer", "Address bar")


def v_chat(c, key, t, lt, dur):
    c.clear(PAPER)
    left_column(c, key, lt)
    kw = ease_out_back(prog(lt, 0.2, 0.5))
    window(c, PANEL_X, PANEL_Y, PANEL_W, PANEL_H, "Claude Code", dark=True, k=kw)
    if kw < 1:
        return
    ly = PANEL_Y + 120 * U
    for i, it, k in shown(key, t):
        kind, s = it
        if kind == "cmd":
            sh, typing = typed(s, k - 0.2)
            ctext(c, "$ " + sh + ("▌" if typing else ""), PANEL_X + 44 * U, ly, 32 * U, CREAM)
            ly += 90 * U
        elif kind == "you":
            sh, typing = typed(s, k - 0.2)
            w = PANEL_W - 88 * U
            rrect(c, PANEL_X + 44 * U, ly - 34 * U, w, 68 * U, 14 * U, rgb("#2C2533"))
            ctext(c, "> " + sh + ("▌" if typing else ""), PANEL_X + 70 * U, ly, 32 * U, CREAM)
            ly += 100 * U
        elif kind == "claude":
            kk = clamp(k * 2)
            text(c, "●", PANEL_X + 50 * U, ly, size=26 * U, font="code", fill=PINK, align="left", alpha=kk)
            ctext(c, "I have 8 Unrushed skills:", PANEL_X + 90 * U, ly, 30 * U, CREAM, font="body", alpha=kk)
            names = s.split(", ")
            for j, nm in enumerate(names):
                kj = clamp((k - 0.3 - j * 0.12) * 4)
                col, row = j % 2, j // 2
                x = PANEL_X + 90 * U + col * 470 * U
                y = ly + 56 * U + row * 50 * U
                check(c, x, y, 24 * U, PINK, kj)
                ctext(c, nm, x + 40 * U, y, 28 * U, CREAM, font="body", alpha=kj)
            ly += 56 * U + 4 * 50 * U + 40 * U


def v_tips(c, key, t, lt, dur):
    c.clear(PAPER)
    left_column(c, key, lt)
    rows = shown(key, t)
    for r, (i, it, k) in enumerate(rows):
        kk = ease_out_back(prog(k, 0, 0.45))
        if kk <= 0:
            continue
        y = PANEL_Y + 60 * U + r * 190 * U
        c.save()
        c.translate(PANEL_X + PANEL_W / 2, y + 70 * U + (1 - kk) * 80 * U)
        c.rotate((-1.5 if r % 2 else 1.5) * (2 - kk))
        w, h = PANEL_W, 140 * U
        shadow(c, -w / 2, -h / 2, w, h, 26 * U, blur=20 * U, alpha=0.18)
        rrect(c, -w / 2, -h / 2, w, h, 26 * U, [CREAM, WHITE, CREAM][r % 3])
        rrect(c, -w / 2, -h / 2, 20 * U, h, 10 * U, [PINK, BLUE, PINK][r % 3])
        lines = wrap(it, 40 * U, w - 120 * U, "code")
        for j, ln in enumerate(lines):
            ctext(c, ln, -w / 2 + 60 * U, (j - (len(lines) - 1) / 2) * 50 * U, 40 * U, INK)
        c.restore()


def v_end(c, key, t, lt, dur):
    c.clear(NIGHT)
    k = ease_out_back(prog(lt, 0.2, 0.5))
    text(c, "YOU'RE READY TO WORK", TL.W / 2, TL.H / 2 - 140 * U, size=130 * U * (0.7 + 0.3 * k), font="display",
         fill=PINK, alpha=clamp(k * 2))
    k2 = ease_out_back(prog(lt, 2.0, 0.5))
    sticker(c, "Open Claude · ask · paint", TL.W / 2, TL.H / 2 + 40 * U, 36 * U, k2,
            fill=CREAM, rot=-1.5)
    k3 = ease_out_cubic(prog(lt, 3.5, 0.6))
    text(c, "Paint first. Your posts come out of your painting time.", TL.W / 2, TL.H / 2 + 190 * U,
         size=56 * U, font="hand", fill=CREAM, alpha=k3)
    text(c, "UNRUSHED STUDIO", TL.W / 2, TL.H - M - 160 * U, size=40 * U, font="display", fill=PINK, alpha=k3)


WEB_SCENES = ["open", "attach", "repo", "install", "ready"]
SKILL_NAMES = ["Unrushed Edit", "Cinematic Studio", "Footage Fixer", "No-Film Studio", "Teaching Kit",
               "Sell Your Art", "Post Everywhere", "Batch & Library"]


def web_items(t):
    """every item from the web scenes whose line has started: [(kind, text, since)]"""
    out = []
    for key in WEB_SCENES:
        for i, (_txt, it) in enumerate(items(key)):
            k = TL.item_k(key, i, t)
            if k >= 0 and it is not None:
                out.append((it[0], it[1], k))
    return out


def bubble(c, x, y, w, lines, size, fill, ink, font="body"):
    h = len(lines) * size * 1.35 + 30 * U
    rrect(c, x, y, w, h, 22 * U, fill)
    for j, ln in enumerate(lines):
        text(c, ln, x + 26 * U, y + 15 * U + size * 0.68 + j * size * 1.35, size=size, font=font, fill=ink,
             align="left")
    return h


def v_web(c, key, t, lt, dur):
    c.clear(PAPER)
    left_column(c, key, lt)
    x, y, w, h = PANEL_X, PANEL_Y - 20 * U, PANEL_W, PANEL_H + 40 * U
    kw = 1.0 if key != "open" else ease_out_back(prog(lt, 0.2, 0.5))
    window(c, x, y, w, h, "Claude Code", k=kw)
    if kw < 1:
        return
    its = web_items(t)
    st = {}
    for kind, s_, k in its:
        st.setdefault(kind, []).append((s_, k))
    # address bar
    bx, by, bw = x + 30 * U, y + 76 * U, w - 60 * U
    rrect(c, bx, by, bw, 54 * U, 27 * U, rgb("#F6F0F2"))
    url = ""
    if "url" in st:
        url, _ = typed(st["url"][0][0], st["url"][0][1] - 0.6, cps=12)
    text(c, url or "Search or enter address", bx + 30 * U, by + 27 * U, size=26 * U, font="code",
         fill=INK if url else rgb(B, "ink", 0.35), align="left")
    # chat column, newest at the bottom; older messages scroll up
    cx0, cw = x + 40 * U, w - 80 * U
    msgs = []
    for kind, s_, k in its:
        if kind in ("attach", "you", "claude", "install", "styles"):
            msgs.append((kind, s_, k))
    blocks = []
    for kind, s_, k in msgs:
        size = 28 * U
        if kind == "attach":
            blocks.append((kind, s_, k, 86 * U))
        elif kind == "you":
            ln = wrap(s_, size, cw * 0.7 - 52 * U, "body")
            blocks.append((kind, ln, k, len(ln) * size * 1.35 + 30 * U))
        elif kind == "claude":
            ln = wrap(s_, size, cw * 0.85 - 52 * U, "body")
            blocks.append((kind, ln, k, len(ln) * size * 1.35 + 30 * U))
        elif kind == "install":
            blocks.append((kind, None, k, 4 * 46 * U + 90 * U))
        elif kind == "styles":
            blocks.append((kind, None, k, 400 * U))
    top, bottom = by + 80 * U, y + h - 110 * U
    total = sum(b[3] + 22 * U for b in blocks)
    cy = bottom - total
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, top, w, bottom - top))
    for kind, data, k, bh in blocks:
        ka = clamp(k * 3)
        yy = cy + (1 - ease_out_cubic(clamp(k * 3))) * 30 * U
        if kind == "attach":
            ww = text_width(data, 24 * U, "code") + 130 * U
            xx = cx0 + cw - ww
            rrect(c, xx, yy, ww, bh, 18 * U, CREAM)
            rrect(c, xx, yy, ww, bh, 18 * U, rgb(B, "ink", 0.2), stroke=2 * U)
            file_icon(c, xx + 18 * U, yy + 14 * U, 58 * U, BLUE, "ZIP")
            text(c, data, xx + 96 * U, yy + bh / 2, size=24 * U, font="code", fill=INK, align="left", alpha=ka)
        elif kind == "you":
            sh = data
            bw_ = max(text_width(l_, 28 * U, "body") for l_ in sh) + 52 * U
            bubble(c, cx0 + cw - bw_, yy, bw_, sh, 28 * U, PINK, NIGHT)
        elif kind == "claude":
            bw_ = max(text_width(l_, 28 * U, "body") for l_ in data) + 52 * U
            bubble(c, cx0, yy, bw_, data, 28 * U, rgb("#F3EEF0"), INK)
        elif kind == "install":
            rrect(c, cx0, yy, cw * 0.92, bh, 22 * U, rgb("#F3EEF0"))
            text(c, "Installing the skills…", cx0 + 26 * U, yy + 36 * U, size=28 * U, font="body", fill=INK,
                 align="left")
            for j, nm in enumerate(SKILL_NAMES):
                kj = clamp((k - 0.6 - j * 0.45) * 3)
                col, row = j % 2, j // 2
                px, py = cx0 + 30 * U + col * cw * 0.45, yy + 90 * U + row * 46 * U
                check(c, px, py, 26 * U, PINK, kj)
                text(c, nm, px + 40 * U, py, size=26 * U, font="body", fill=INK, align="left",
                     alpha=0.35 + 0.65 * kj)
        elif kind == "styles":
            img = image("raw/styles_egg.png")
            ih = bh - 20 * U
            iw = ih * img.width() / img.height()
            rrect(c, cx0, yy, iw + 20 * U, bh, 18 * U, rgb("#F3EEF0"))
            draw_image(c, img, cx0 + 10 * U, yy + 10 * U, iw, ih, cover=False)
        cy += bh + 22 * U
    c.restore()
    # input box
    iy = y + h - 90 * U
    rrect(c, x + 30 * U, iy, w - 60 * U, 64 * U, 32 * U, rgb("#F6F0F2"))
    pending = ""
    for kind, s_, k in its:
        if kind == "you" and k < 1.2:
            pending, _ = typed(s_, k, cps=26)
    text(c, pending or "Reply to Claude…", x + 64 * U, iy + 32 * U, size=26 * U, font="body",
         fill=INK if pending else rgb(B, "ink", 0.35), align="left")
    # note pill under the window
    if "note" in st and key == "open":
        s_, k = st["note"][-1]
        sticker(c, s_, x + w / 2, y + h / 2, 32 * U, ease_out_back(prog(k, 0, 0.4)), fill=CREAM, rot=0, font="code")
    # repository dialog
    if "repo" in st and "install" not in st:
        name, k = st["repo"][0]
        kd = ease_out_back(prog(k, 0, 0.45))
        dw, dh = 640 * U, 360 * U
        c.save()
        c.translate(x + w / 2, y + h / 2)
        c.scale(kd, kd)
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.Paint(Color=rgb(B, "night", 0.25)))
        shadow(c, -dw / 2, -dh / 2, dw, dh, 26 * U, blur=30 * U, alpha=0.3)
        rrect(c, -dw / 2, -dh / 2, dw, dh, 26 * U, WHITE)
        text(c, "New repository", -dw / 2 + 40 * U, -dh / 2 + 56 * U, size=36 * U, font="mono", fill=INK,
             align="left")
        rrect(c, -dw / 2 + 40 * U, -dh / 2 + 100 * U, dw - 80 * U, 64 * U, 14 * U, rgb("#F6F0F2"))
        nm, _ = typed(name, k - 0.4, cps=14)
        text(c, nm, -dw / 2 + 64 * U, -dh / 2 + 132 * U, size=28 * U, font="code", fill=INK, align="left")
        on = ease_in_out_cubic(prog(k, 2.4, 0.3))
        text(c, "Private", -dw / 2 + 40 * U, -dh / 2 + 220 * U, size=30 * U, font="body", fill=INK, align="left")
        tx = dw / 2 - 140 * U
        rrect(c, tx, -dh / 2 + 200 * U, 96 * U, 46 * U, 23 * U, PINK if on > 0.5 else rgb(B, "ink", 0.2))
        c.drawCircle(tx + lerp(23, 73, on) * U, -dh / 2 + 223 * U, 18 * U, skia.Paint(Color=WHITE, AntiAlias=True))
        bwid = 180 * U
        press = 1 - 0.06 * clamp(1 - abs(k - 3.6) * 4)
        rrect(c, dw / 2 - 40 * U - bwid * press, dh / 2 - 90 * U, bwid * press, 60 * U, 30 * U, NIGHT)
        text(c, "Create", dw / 2 - 40 * U - bwid * press / 2, dh / 2 - 60 * U, size=28 * U, font="mono",
             fill=CREAM)
        c.restore()
    # permission prompt
    if "allow" in st:
        s_, k = st["allow"][0]
        if k < 3.2:
            ka = ease_out_back(prog(k, 0, 0.4)) * (1 - ease_out_cubic(prog(k, 2.7, 0.4)))
            pw, ph = 560 * U, 170 * U
            c.save()
            c.translate(x + w / 2, y + h - 200 * U)
            c.scale(ka, ka)
            shadow(c, -pw / 2, -ph / 2, pw, ph, 22 * U, blur=24 * U, alpha=0.3)
            rrect(c, -pw / 2, -ph / 2, pw, ph, 22 * U, WHITE)
            rrect(c, -pw / 2, -ph / 2, pw, ph, 22 * U, PINK, stroke=4 * U)
            text(c, "Claude wants to save the skills", 0, -ph / 2 + 46 * U, size=28 * U, font="body", fill=INK)
            press = 1 - 0.08 * clamp(1 - abs(k - 1.6) * 4)
            rrect(c, -90 * U * press, 10 * U, 180 * U * press, 56 * U, 28 * U, PINK)
            text(c, "Allow", 0, 38 * U, size=28 * U, font="mono", fill=NIGHT)
            c.restore()


VIEWS = {"title": v_title, "checklist": v_checklist, "files": v_files, "terminal": v_terminal,
         "finder": v_finder, "explorer": v_explorer, "chat": v_chat, "tips": v_tips, "end": v_end,
         "web": v_web}


def draw(c, t):
    key, lt, dur = TL.scene_at(t)
    VIEWS[TL.SCENE_INFO[key][2]](c, key, t, lt, dur)
    caption(c, t)


# ---------------------------------------------------------------- sound
def build_voice():
    import wave
    sr = 24000
    out = np.zeros(int(TL.DURATION * sr) + sr, np.float32)
    for s, e, key, i, _txt, _ in TL.LINES:
        w = wave.open(f"work/vo/{TL.line_id(key, i)}.wav")
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        w.close()
        a = int(s * sr)
        out[a:a + len(x)] += x[: len(out) - a]
    out = out[: int(TL.DURATION * sr)]
    w = wave.open("work/voice.wav", "wb")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    w.close()
    return "work/voice.wav"


def build_audio():
    import subprocess
    Path("work").mkdir(exist_ok=True)
    ak.write_wav("work/music.wav", ak.music_bed(TL.MOOD, seconds=TL.DURATION, bpm=TL.BPM, intro_bars=0))
    Path("work/cues.json").write_text(json.dumps(TL.cues(voice=build_voice()), indent=1))
    subprocess.run([sys.executable, "vibe/audio_kit.py", "mix", "work/cues.json", "-o", "work/mix.wav"], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        times = [float(x) for x in sys.argv[2:]] or [e - 1.0 for s, e, _ in TL.SCENES]
        S.stills(draw, times)
    elif cmd == "audio":
        build_audio()
    elif cmd == "draft":
        S.render(draw, "out/draft.mp4", audio="work/mix.wav", draft=True)
    elif cmd == "render":
        if not Path("work/mix.wav").exists():
            build_audio()
        S.render(draw, "out/unrushed-install.mp4", audio="work/mix.wav")
    elif cmd == "chapters":
        print("\n".join(TL.chapters()))
    else:
        sys.exit(__doc__)
