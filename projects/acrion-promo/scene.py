"""scene: Acrion Realty promo (v1). Every frame is a pure function of time t.

    python3 scene.py stills 1.0 3.0 5.0          # check frames -> out/stills/
    python3 scene.py audio                       # music + sfx -> work/mix.wav
    python3 scene.py draft                       # half-res preview -> out/draft.mp4
    python3 scene.py render                      # final -> out/acrion-promo.mp4

Timings and copy live in timeline.py. All graphics are drawn here (no stock or AI images).
"""

import json
import math
import os
import sys
from pathlib import Path

import skia

sys.path.insert(0, str(Path(__file__).resolve().parent / "vibe"))
import audio_kit as ak  # noqa: E402
from motion_kit import (Stage, clamp, ease_in_cubic, ease_in_out_cubic, ease_out_back, ease_out_cubic,  # noqa: E402
                        ease_out_expo, grain, lerp, noise1, prog, pulse, rgb, rrect, shadow, stagger, text,
                        text_width, vignette)

import timeline as TL  # noqa: E402

S = Stage(TL.W, TL.H, fps=TL.FPS, duration=TL.DURATION)
B = S.brand
U = min(TL.W, TL.H) / 1080
W, H, CX = TL.W, TL.H, TL.W / 2
INK, PAPER, GOLD, SAGE = rgb(B, "ink"), rgb(B, "paper"), rgb(B, "lime"), rgb(B, "periwinkle")
NIGHT, SAND, CORAL = rgb(B, "ice"), rgb(B, "blush"), rgb(B, "orange")

# Safe zone (9:16: top 250 px, bottom 420 px, right 140 px clear), scaled to the canvas.
SAFE_T = H * 250 / 1920
SAFE_B = H - H * 420 / 1920
MID = (SAFE_T + SAFE_B) / 2
MAX_W = W - 2 * max(150 * U, 0.08 * W)

HITS = [s[0] for s in TL.SFX if s[1] == "impact"]


def fit(s, font, max_size, max_w=MAX_W, tracking=0.0):
    """Biggest size <= max_size at which s fits in max_w."""
    return min(max_size, max_w / max(1e-6, text_width(s, 100, font, tracking)) * 100)


def shake(t):
    amp = sum(math.exp(-9 * (t - h)) for h in HITS if 0 <= t - h < 0.45)
    return 14 * U * noise1(t * 40) * amp, 14 * U * noise1(t * 40, seed=3) * amp


def h01(*k):
    """Deterministic hash -> [0, 1)."""
    n = 0
    for v in k:
        n = (n * 1000003 + int(v) * 2654435761 + 12345) & 0xFFFFFFFF
        n ^= n >> 15
    return (n * 2246822519 & 0xFFFFFFFF) / 2 ** 32


# ------------------------------------------------------------------ drawing helpers
def grid_bg(c, col, t, alpha=0.06, step=120):
    c.clear(col)
    p = skia.Paint(Color=rgb(B, "paper" if col == INK else "ink", alpha), StrokeWidth=1.5 * U, AntiAlias=True)
    off = (t * 30 * U) % (step * U)
    x = -off
    while x < W:
        c.drawLine(x, 0, x, H, p)
        x += step * U
    y = -off
    while y < H:
        c.drawLine(0, y, W, y, p)
        y += step * U


def house(c, x, y, s, col, alpha=1.0):
    """Simple house icon centred on (x, y), size s."""
    p = skia.Paint(Color=col, AntiAlias=True, Alphaf=clamp(alpha))
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.36, y - s * 0.05, s * 0.72, s * 0.5), p)
    roof = skia.Path()
    roof.moveTo(x - s * 0.5, y)
    roof.lineTo(x, y - s * 0.45)
    roof.lineTo(x + s * 0.5, y)
    roof.close()
    c.drawPath(roof, p)


def tower(c, x, base, w, h, k, body, win, lit, seed=0, cols=4, crown=False):
    """A building rising from `base` (k = 0..1 growth). `lit` = fraction of windows lit."""
    hh = h * k
    if hh <= 1:
        return
    rrect(c, x, base - hh, w, hh, 6 * U, body)
    if crown and k > 0.95:
        cr = skia.Path()
        cr.moveTo(x + w * 0.2, base - hh)
        cr.lineTo(x + w * 0.5, base - hh - w * 0.35)
        cr.lineTo(x + w * 0.8, base - hh)
        cr.close()
        c.drawPath(cr, skia.Paint(Color=body, AntiAlias=True))
    pad = w * 0.14
    cw = (w - 2 * pad) / cols
    rows = max(1, int((h - pad) // (cw * 1.15)))
    for r in range(rows):
        wy = base - pad - (r + 1) * cw * 1.15
        if wy < base - hh + pad * 0.6:
            break
        for col in range(cols):
            on = h01(seed, r, col) < lit
            rrect(c, x + pad + col * cw + cw * 0.18, wy, cw * 0.64, cw * 0.8, 2 * U, GOLD if on else win)


SKYLINE = []  # (x, w, h, cols, seed) in U units relative to the canvas
_x = -30.0
for _i in range(11):
    _w = 70 + 70 * h01(91, _i)
    SKYLINE.append((_x, _w, 260 + 420 * h01(17, _i), 3 if _w < 110 else 4, _i))
    _x += _w + 8 + 14 * h01(5, _i)


def skyline(c, t0, lt, base, lit, body=None, win=None, scale=1.0):
    total = SKYLINE[-1][0] + SKYLINE[-1][1]
    off = (W / U - total * scale) / 2
    for i, (x, w, h, cols, sd) in enumerate(SKYLINE):
        k = ease_out_expo(prog(lt, t0 + 0.05 * ((i * 7) % 11), 0.6))
        tower(c, (off + x * scale) * U, base, w * scale * U, h * scale * U, k, body or NIGHT, win or INK, lit,
              seed=sd, cols=cols)


def slam(lt, start, dur=0.28, width=None, s0=1.7, max_w=None):
    """(scale, alpha) for a word that slams in at `start`. With `width` (the text's width at scale 1),
    the overshoot is capped so the word never grows past max_w (default: 86 % of the frame)."""
    k = ease_out_back(prog(lt, start, dur))
    sc = lerp(s0, 1.0, k)
    if width:
        sc = min(sc, max(1.0, (max_w or 0.86 * W) / width))
    return sc, clamp(prog(lt, start, 0.08))


def project_art(c, i, cx, base, k, lit):
    """One illustration per project (no real photos yet): towers + trees, in the card's palette."""
    body, win = INK, NIGHT
    if i == 0:   # garden-side twin towers
        tower(c, cx - 250 * U, base, 210 * U, 520 * U, k, body, win, lit, seed=1)
        tower(c, cx + 40 * U, base, 210 * U, 600 * U, ease_out_expo(clamp(k * 1.15 - 0.1)), body, win, lit, seed=2)
        for j, (tx, r) in enumerate([(-320, 70), (-150, 90), (20, 60), (230, 95), (330, 65)]):
            kk = ease_out_back(clamp(k * 1.4 - 0.25 - 0.06 * j))
            c.drawCircle(cx + tx * U, base - r * 0.7 * U, r * U * kk, skia.Paint(Color=rgb("#2F6B4F"), AntiAlias=True))
    elif i == 1:  # one tall crowned tower + a side wing
        tower(c, cx - 230 * U, base, 190 * U, 360 * U, ease_out_expo(clamp(k * 1.2 - 0.15)), body, win, lit, seed=3)
        tower(c, cx - 30 * U, base, 230 * U, 640 * U, k, body, win, lit, seed=4, crown=True)
        tower(c, cx + 210 * U, base, 140 * U, 280 * U, ease_out_expo(clamp(k * 1.3 - 0.25)), body, win, lit, seed=5,
              cols=3)
    else:        # three stepped towers
        for j, (dx, hh) in enumerate([(-300, 420), (-95, 600), (110, 500)]):
            kk = ease_out_expo(clamp(k * 1.3 - 0.12 * j))
            tower(c, cx + dx * U, base, 190 * U, hh * U, kk, body, win, lit, seed=6 + j)
    c.drawRect(skia.Rect.MakeXYWH(cx - 420 * U, base, 840 * U, 10 * U), skia.Paint(Color=INK, AntiAlias=True))


# ------------------------------------------------------------------ scenes
def s_hook(c, t, lt, dur):
    grid_bg(c, INK, t)
    lines = TL.COPY["hook"]
    starts = [TL.beat(0), TL.beat(1), TL.beat(2), TL.beat(4)]
    sizes = [fit(w, "display", 170 * U) for w in lines]
    gap = 26 * U
    total = sum(s * 1.05 for s in sizes) + gap * (len(lines) - 1)
    y = MID - total / 2
    for i, (w, size, st) in enumerate(zip(lines, sizes, starts)):
        y += size * 0.525
        sc, a = slam(lt, st, width=text_width(w, size, "display"))
        last = i == len(lines) - 1
        if last and lt >= st:
            wb = (text_width(w, size, "display") + 70 * U) * ease_out_expo(prog(lt, st + 0.05, 0.3))
            rrect(c, CX - wb / 2, y - size * 0.62, wb, size * 1.24, 22 * U, GOLD)
        if a > 0:
            text(c, w, CX, y, size=size * sc, font="display", fill=INK if last else PAPER, alpha=a)
        y += size * 0.525 + gap
    # a beat-pulsing house mark above the stack once the question lands
    k = ease_out_back(prog(lt, TL.beat(5), 0.35))
    if k > 0:
        house(c, CX, MID - total / 2 - 150 * U, 120 * U * k * (1 + 0.06 * pulse(t, TL.BPM)), GOLD)


def s_problem(c, t, lt, dur):
    grid_bg(c, PAPER, t, alpha=0.05)
    words = TL.COPY["problem"]
    b = lt / TL.BEAT
    calm = ease_in_cubic(prog(lt, TL.beat(4), 0.35))          # chaos clears on "LET'S MAKE IT SIMPLE"
    for i in range(26):                                       # the noise: too many listings
        k = ease_out_back(prog(lt, 0.04 * i, 0.25)) * (1 - calm)
        if k <= 0:
            continue
        x = (0.1 + 0.8 * h01(3, i)) * W + (b >= 2) * 18 * U * noise1(t * 9 + i)
        y = SAFE_T + (0.05 + 0.9 * h01(4, i)) * (SAFE_B - SAFE_T)
        col = [SAGE, GOLD, SAND, NIGHT][i % 4]
        house(c, x, y, (50 + 50 * h01(5, i)) * U * k, col, alpha=0.9 if b < 2 else 0.45)
    idx = 0 if b < 2 else 1 if b < 4 else 2
    st = [0.0, TL.beat(2), TL.beat(4)][idx]
    lines = words[idx].split("|")
    size = min(fit(ln, "display", 150 * U) for ln in lines)
    lw = max(text_width(ln, size, "display") for ln in lines)
    sc, a = slam(lt, st, 0.22, width=lw, s0=1.15, max_w=lw + 60 * U)
    if idx == 2:
        hk = ease_out_back(prog(lt, st + 0.1, 0.4))
        house(c, CX, MID - 260 * U, 190 * U * hk, GOLD)
    lh = size * 1.12
    bw = max(text_width(ln, size, "display") for ln in lines) + 100 * U
    bh = lh * len(lines) + 70 * U
    y0 = MID + 60 * U - bh / 2
    rrect(c, CX - bw / 2, y0, bw, bh, 40 * U, INK)
    for j, ln in enumerate(lines):
        text(c, ln, CX, y0 + 35 * U + lh * (j + 0.5), size=size * sc, font="display",
             fill=GOLD if idx == 2 else PAPER, alpha=a)


def s_reveal(c, t, lt, dur):
    grid_bg(c, INK, t, alpha=0.05)
    base = H * 0.88
    lit = clamp(0.2 + 0.11 * math.floor(lt / TL.BEAT))
    skyline(c, 0.0, lt, base, lit)
    flash = 1 - prog(lt, 0.0, 0.18)
    if flash > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=rgb(B, "white", 0.85 * flash)))
    size = fit(TL.COPY["brand"], "display", 230 * U)
    sc, a = slam(lt, 0.0, 0.35, width=text_width(TL.COPY["brand"], size, "display"))
    yb = SAFE_T + 260 * U
    text(c, TL.COPY["brand"], CX, yb, size=size * sc, font="display", fill=PAPER, alpha=a)
    k2 = ease_out_expo(prog(lt, TL.beat(1), 0.4))
    text(c, TL.COPY["brand_sub"], CX, yb + size * 0.78, size=54 * U, font="mono", fill=GOLD, tracking=0.6 * k2,
         alpha=k2)
    k3 = ease_out_cubic(prog(lt, TL.beat(4), 0.45))
    tag = TL.COPY["brand_tag"]
    ts = fit(tag, "mono", 30 * U, tracking=0.14)
    text(c, tag, CX, yb + size * 0.78 + 90 * U + (1 - k3) * 30 * U, size=ts, font="mono", fill=PAPER, alpha=k3,
         tracking=0.14)


CARD_BG = [SAGE, GOLD, PAPER]


def s_project(i):
    def draw(c, t, lt, dur):
        c.clear(CARD_BG[i])
        k_in = ease_out_expo(prog(lt, 0.0, 0.32))
        dx = (1 - k_in) * W * 0.6                               # whip in from the right
        push = 1 + 0.05 * ease_in_out_cubic(prog(lt, 0, dur))   # slow push-in
        c.save()
        c.translate(CX + dx, MID)
        c.scale(push, push)
        c.translate(-CX, -MID)
        label = f"PROJECT 0{i + 1}"
        text(c, label, CX, SAFE_T + 40 * U, size=34 * U, font="mono", fill=INK, tracking=0.3)
        base = MID + 260 * U
        kb = ease_out_expo(prog(lt, 0.08, 0.7))
        lit = clamp(0.15 + 0.2 * math.floor(lt / TL.BEAT))
        project_art(c, i, CX, base, kb, lit)
        name = TL.COPY["projects"][i]
        size = fit(name, "display", 118 * U)
        sc, a = slam(lt, TL.beat(1), 0.25, width=text_width(name, size, "display"))
        yn = base + 130 * U
        text(c, name, CX, yn, size=size * sc, font="display", fill=INK, alpha=a)
        sub = TL.COPY["project_subs"][i]
        ks = ease_out_cubic(prog(lt, TL.beat(2), 0.3))
        y2 = yn + size * 0.62 + 40 * U
        if sub:
            text(c, sub, CX, y2, size=fit(sub, "mono", 34 * U, tracking=0.16), font="mono", fill=INK, alpha=ks,
                 tracking=0.16)
            y2 += 64 * U
        city = TL.COPY["city"]
        cw = text_width(city, 30 * U, "mono", 0.2) + 110 * U
        if ks > 0:
            rrect(c, CX - cw / 2, y2 - 32 * U, cw, 64 * U, 32 * U, rgb(B, "ink", ks))
            c.drawCircle(CX - cw / 2 + 36 * U, y2, 9 * U, skia.Paint(Color=GOLD if i != 1 else SAGE, AntiAlias=True, Alphaf=ks))
        text(c, city, CX + 18 * U, y2, size=30 * U, font="mono", fill=PAPER, tracking=0.2, alpha=max(ks, 0.001))
        c.restore()
    return draw


def s_explore(c, t, lt, dur):
    grid_bg(c, INK, t, alpha=0.05)
    tile_w, tile_h = 230 * U, 300 * U
    for i in range(3):
        k = ease_out_back(prog(lt, TL.beat(i) + 0.05, 0.35))
        if k <= 0:
            continue
        x = CX + (i - 1) * (tile_w + 34 * U) - tile_w / 2
        y = SAFE_T + 120 * U + (1 - k) * 120 * U
        shadow(c, x, y, tile_w, tile_h, 24 * U, blur=24 * U, dy=14 * U, alpha=0.35 * k)
        rrect(c, x, y, tile_w, tile_h, 24 * U, CARD_BG[i])
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, tile_w, tile_h), 24 * U, 24 * U))
        c.translate(x + tile_w / 2, y + tile_h * 0.8)
        c.scale(0.3, 0.3)
        project_art(c, i, 0, 0, 1.0, 0.7)
        c.restore()
    words = TL.COPY["explore"]
    sizes = [fit(w, "display", 150 * U) for w in words]
    y = SAFE_T + 120 * U + tile_h + 150 * U
    for i, (w, size) in enumerate(zip(words, sizes)):
        sc, a = slam(lt, TL.beat(i), 0.25, width=text_width(w, size, "display"))
        col = GOLD if i == len(words) - 1 else PAPER
        if a > 0:
            text(c, w, CX, y + size * 0.5, size=size * sc, font="display", fill=col, alpha=a)
        y += size * 1.1


def s_endcard(c, t, lt, dur):
    grid_bg(c, INK, t, alpha=0.05)
    ring = ease_out_expo(prog(lt, 0.0, 0.7))
    if ring < 1:
        c.drawCircle(CX, MID, ring * H * 0.7, skia.Paint(Color=rgb(B, "lime", 1 - ring), AntiAlias=True,
                                                         Style=skia.Paint.kStroke_Style, StrokeWidth=60 * U))
    skyline(c, -1.0, lt + 1.0, H * 0.97, 0.75, scale=0.55)    # small lit skyline, already built
    t1, t2 = TL.COPY["end_title"]
    s1 = fit(t1, "display", 110 * U)
    s2 = fit(t2, "display", 250 * U)
    y = SAFE_T + 300 * U
    sc, a = slam(lt, 0.0, 0.25, width=text_width(t1, s1, "display"))
    text(c, t1, CX, y, size=s1 * sc, font="display", fill=PAPER, alpha=a)
    sc, a = slam(lt, TL.beat(1), 0.3, width=text_width(t2, s2, "display") * 1.03)
    text(c, t2, CX, y + s1 * 0.6 + s2 * 0.55, size=s2 * sc * (1 + 0.03 * pulse(t, TL.BPM)), font="display",
         fill=GOLD, alpha=a)
    yb = y + s1 * 0.6 + s2 * 1.15 + 70 * U
    kb = ease_out_cubic(prog(lt, TL.beat(2), 0.35))
    text(c, "ACRION REALTY", CX, yb + (1 - kb) * 30 * U, size=fit("ACRION REALTY", "display", 64 * U), font="display",
         fill=PAPER, alpha=kb)
    kc = ease_out_back(prog(lt, TL.beat(3), 0.4))
    cta = TL.COPY["cta"]
    cs = 46 * U
    cw = text_width(cta, cs, "mono", 0.04) + 120 * U
    ch = 112 * U
    yc = yb + 110 * U
    if kc > 0:
        rrect(c, CX - cw * kc / 2, yc, cw * kc, ch, ch / 2, GOLD)
        text(c, cta, CX, yc + ch / 2, size=cs * clamp(kc, 0, 1.2), font="mono", fill=INK, tracking=0.04)
    kd = ease_out_cubic(prog(lt, TL.beat(4), 0.4))
    text(c, TL.COPY["city"], CX, yc + ch + 60 * U, size=30 * U, font="mono", fill=SAGE, tracking=0.3, alpha=kd)


SCENES = {"hook": s_hook, "problem": s_problem, "reveal": s_reveal, "project0": s_project(0),
          "project1": s_project(1), "project2": s_project(2), "explore": s_explore, "endcard": s_endcard}


def draw(c, t):
    name, lt, dur = TL.scene_at(t)
    sx, sy = shake(t)
    c.save()
    c.translate(sx, sy)
    SCENES[name](c, t, lt, dur)
    c.restore()


def post(a, t):
    return grain(vignette(a, 0.18), 0.018, int(t * TL.FPS))


def build_audio():
    Path("work").mkdir(exist_ok=True)
    ak.write_wav("work/music.wav", ak.music_bed(TL.MOOD, bars=TL.BARS, bpm=TL.BPM, intro_bars=0, seed=TL.MUSIC_SEED))
    Path("work/cues.json").write_text(json.dumps(TL.cues(), indent=1))
    import subprocess
    subprocess.run([sys.executable, "vibe/audio_kit.py", "mix", "work/cues.json", "-o", "work/mix.wav"], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        times = [float(x) for x in sys.argv[2:]] or [s + (e - s) * 0.7 for s, e, _ in TL.SCENES]
        S.stills(draw, times, post=post)
    elif cmd == "audio":
        build_audio()
    elif cmd == "draft":
        S.render(draw, "out/draft.mp4", audio="work/mix.wav", draft=True)
    elif cmd == "render":
        if not Path("work/mix.wav").exists():
            build_audio()
        suffix = f"_{TL.W}x{TL.H}" if os.environ.get("VIBE_SIZE") else ""
        S.render(draw, f"out/acrion-promo{suffix}.mp4", audio="work/mix.wav", post=post)
    else:
        sys.exit(__doc__)
