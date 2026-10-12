#!/usr/bin/env python3
"""Eyes: pull still frames from a video with FFmpeg so Claude can look at the shot.

Usage:
    python scripts/frames.py videos/my-reel/take.mp4            # 1 frame per second
    python scripts/frames.py take.mp4 --fps 2                   # 2 frames per second
    python scripts/frames.py take.mp4 --at 0:07 12.5            # specific moments only

Frames go to <video folder>/frames/<video name>/, named by their time in the video
(e.g. t0007.00.jpg = 7.00 s), so a frame can be matched to the word timings.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def to_seconds(t):
    parts = [float(p) for p in str(t).split(":")]
    secs = 0.0
    for p in parts:
        secs = secs * 60 + p
    return secs


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path)
    parser.add_argument("--fps", type=float, default=1.0, help="frames per second (default: 1)")
    parser.add_argument("--at", nargs="+", default=None, help="only grab these times (seconds or m:ss)")
    parser.add_argument("--width", type=int, default=720, help="frame width in px (default: 720)")
    parser.add_argument("--out", type=Path, default=None, help="output folder")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("FFmpeg is not installed. See README.md -> Install it once.")
    if not args.video.exists():
        sys.exit(f"File not found: {args.video}")

    out = args.out or args.video.parent / "frames" / args.video.stem
    out.mkdir(parents=True, exist_ok=True)
    scale = f"scale={args.width}:-2"

    if args.at:
        for t in args.at:
            secs = to_seconds(t)
            target = out / f"t{secs:07.2f}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(secs), "-i", str(args.video),
                            "-frames:v", "1", "-vf", scale, "-q:v", "3", str(target)], check=True)
    else:
        tmp = out / "_f%05d.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(args.video),
                        "-vf", f"fps={args.fps},{scale}", "-q:v", "3", str(tmp)], check=True)
        # Rename to timestamps. With the fps filter, frame n (1-based) sits at (n - 0.5) / fps,
        # we label it with its window start (n - 1) / fps.
        for f in sorted(out.glob("_f*.jpg")):
            n = int(f.stem[2:])
            f.replace(out / f"t{(n - 1) / args.fps:07.2f}.jpg")

    count = len(list(out.glob("t*.jpg")))
    print(f"{count} frames in {out}")


if __name__ == "__main__":
    main()
