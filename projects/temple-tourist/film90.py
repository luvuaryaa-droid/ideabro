"""film90: the "90s movie" version of the temple film (clean: no captions; the artist's voice + original sound).

    python3 film90.py        -> out/temple-tourist_90s.mp4

Built from the full-quality picture (work/picture.mp4, no text) and the existing mix (work/mix.wav):
  1. 90s title cards (Courier Prime, "presents"-style opening, end card + "fin.") as a transparent overlay
  2. a dust & scratch plate (procedural, seeded): dark specks and hairs, occasional bright vertical scratch
  3. film-print chain: gate weave, Kodak-ish print grade (faded blacks, warm highs, cool lows, softer colour),
     red halation around highlights, exposure flicker, heavy luma grain, vignette, slight softness,
     2.39:1 letterbox
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "vibe")
from motion_kit import Stage, clamp, ease_out_cubic, prog, rgb, text  # noqa: E402
from vibelib import FrameWriter  # noqa: E402

import timeline as TL  # noqa: E402

W, H, FPS, DUR = TL.W, TL.H, TL.FPS, TL.DURATION
BAR = int(round((H - W / 2.39) / 2))          # 2.39:1 scope letterbox
CREAM = rgb("#F3E9D2")
MONO, MONO_B = "CourierPrime-400.ttf", "CourierPrime-700.ttf"
END0 = TL.END_CARD


def fade(t, s, e, fin=0.8, fout=0.8):
    return ease_out_cubic(prog(t, s, fin)) * (1 - prog(t, e - fout, fout))


def titles(c, t):
    import skia
    c.clear(skia.ColorTRANSPARENT)
    a = fade(t, 0.3, 1.9, 0.5, 0.45)            # "the unrushed whispers presents"
    if a > 0:
        text(c, "the unrushed whispers presents", W / 2, H * 0.5, size=34, font=MONO, fill=CREAM, alpha=a,
             tracking=0.12)
    a = fade(t, 1.8, 3.35, 0.45, 0.4)           # the title
    if a > 0:
        text(c, "ARTIST DATE", W / 2, H * 0.46, size=84, font=MONO_B, fill=CREAM, alpha=a, tracking=0.3)
        text(c, "playing tourist in my own city", W / 2, H * 0.56, size=36, font=MONO, fill=CREAM, alpha=a,
             tracking=0.1)
    a = fade(t, END0 + 0.2, DUR + 1, 0.8, 0.01)
    if a > 0:
        text(c, "ARTIST DATE", W / 2, H * 0.44, size=60, font=MONO_B, fill=CREAM, alpha=a, tracking=0.3)
        text(c, "@the_unrushed.whispers", W / 2, H * 0.52, size=34, font=MONO, fill=CREAM, alpha=a, tracking=0.06)
        text(c, "fin.", W / 2, H * 0.61, size=30, font=MONO, fill=CREAM, alpha=a * ease_out_cubic(prog(t, END0 + 1.2,
                                                                                                    0.6)))


def dust_plate(path, w=960, h=540):
    """Grey 128 = neutral. Dark specks/hairs (dust on the print), rare bright vertical scratches."""
    rng = np.random.default_rng(1994)
    n = int(DUR * FPS)
    yy, xx = np.mgrid[0:h, 0:w]
    scratch_x, scratch_left = None, 0
    with FrameWriter(path, w, h, FPS, crf=12) as fw:
        for i in range(n):
            f = np.full((h, w), 128.0, np.float32)
            for _ in range(rng.poisson(5)):                       # specks
                x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(0.8, 2.6)
                f -= 90 * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * r * r))
            if rng.random() < 0.12:                               # a hair
                x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
                ang, ln = rng.uniform(0, np.pi), rng.uniform(15, 45)
                for k in np.linspace(0, 1, 60):
                    x = x0 + ln * k * np.cos(ang) + 4 * np.sin(k * 6)
                    y = y0 + ln * k * np.sin(ang)
                    if 0 <= int(x) < w and 0 <= int(y) < h:
                        f[int(y), int(x)] -= 70
            if scratch_left <= 0 and rng.random() < 0.025:          # a scratch that lasts a few frames
                scratch_x, scratch_left = rng.uniform(0.1, 0.9) * w, int(rng.integers(4, 14))
            if scratch_left > 0:
                sx = scratch_x + rng.normal(0, 0.6)
                f += 55 * np.exp(-((xx - sx) ** 2) / 1.2) * (0.6 + 0.4 * rng.random())
                scratch_left -= 1
            g = np.clip(f, 0, 255).astype(np.uint8)
            fw.write(np.stack([g, g, g], -1))


def main():
    Path("out").mkdir(exist_ok=True)
    S = Stage(W, H, fps=FPS, duration=DUR)
    print("titles ...")
    S.render(titles, "work/titles90.mov", alpha=True)
    print("dust plate ...")
    dust_plate("work/dust90.mp4")
    print("film print ...")
    weave = ("crop=1904:1070:x='8+2.5*sin(n*0.83)+1.5*sin(n*2.71)+1.2*sin(n*7.3)':"
             "y='5+1.8*sin(n*1.37)+1.2*sin(n*3.9)',scale=1920:1080:flags=bicubic")
    grade = ("eq=contrast=0.9:saturation=0.8,"
             "curves=r='0/0.07 0.25/0.26 0.5/0.53 0.8/0.84 1/0.97':g='0/0.06 0.5/0.5 1/0.95':"
             "b='0/0.1 0.5/0.47 1/0.86',"
             "colorbalance=rs=-0.03:bs=0.05:rm=0.03:bm=-0.02:rh=0.05:gh=0.01:bh=-0.06")
    graph = (
        f"[0:v][1:v]overlay=0:0:format=auto,format=rgb24,{weave},{grade},split[a][b];"
        "[b]curves=all='0/0 0.72/0 1/1',gblur=sigma=16,colorchannelmixer=rr=1:gg=0.3:bb=0.12[h];"
        "[a][h]blend=all_mode=screen:all_opacity=0.32,"
        "eq=brightness='0.012*sin(n*1.9)+0.008*sin(n*7.1)':eval=frame,"
        "gblur=sigma=0.55,format=yuv420p,noise=c0s=16:c0f=t+u,format=rgb24[f];"
        "[2:v]scale=1920:1080,format=rgb24[d];"
        "[f][d]blend=all_mode=grainmerge,vignette=PI/4.2,"
        f"drawbox=x=0:y=0:w=iw:h={BAR}:color=black:t=fill,drawbox=x=0:y=ih-{BAR}:w=iw:h={BAR}:color=black:t=fill,"
        "fade=t=in:st=0:d=0.6,fade=t=out:st=" + f"{DUR - 0.9:.2f}" + ":d=0.9,format=yuv420p[v]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/picture.mp4", "-i", "work/titles90.mov",
                    "-i", "work/dust90.mp4", "-i", "work/mix.wav", "-filter_complex", graph,
                    "-map", "[v]", "-map", "3:a", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                    "-tune", "grain", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-shortest",
                    "-movflags", "+faststart", "out/temple-tourist_90s.mp4"], check=True)
    print("done -> out/temple-tourist_90s.mp4")


if __name__ == "__main__":
    main()
