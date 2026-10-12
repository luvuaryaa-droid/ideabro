#!/usr/bin/env python3
"""Start a new edit: create videos/<name>/ as a HyperFrames project and copy the take in.

Usage:
    python scripts/new_video.py my-first-reel --take ~/Downloads/IMG_1234.mov
    python scripts/new_video.py launch-promo --take take.mp4 --format landscape

Formats: portrait (9:16, Reels/TikTok/Shorts, default), landscape (16:9), square (1:1).
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HYPERFRAMES = "hyperframes@0.8.149"  # pinned so every edit renders the same; bump on purpose


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", help="short folder name, e.g. my-first-reel")
    parser.add_argument("--take", type=Path, default=None, help="your recorded video")
    parser.add_argument("--format", choices=["portrait", "landscape", "square"], default="portrait")
    args = parser.parse_args()

    project = ROOT / "videos" / args.name
    if project.exists():
        sys.exit(f"{project} already exists. Pick another name.")
    if args.take and not args.take.exists():
        sys.exit(f"File not found: {args.take}")

    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        sys.exit("Node.js is not installed (npx not found). See README.md -> Install it once.")

    cmd = [npx, "--yes", HYPERFRAMES, "init", args.name, "--non-interactive",
           "--resolution", args.format, "--skip-transcribe"]
    subprocess.run(cmd, cwd=ROOT / "videos", check=True, env={**os.environ, "HYPERFRAMES_SKIP_SKILLS": "1"})

    if args.take:
        dest = project / f"take{args.take.suffix.lower()}"
        shutil.copy2(args.take, dest)
        print(f"Copied your take to {dest}")

    (project / "versions").mkdir(exist_ok=True)
    print(f"\nReady: {project}")
    print("Next: open Claude Code in this repo and paste the 'First prompt' from prompts/PROMPTS.md")


if __name__ == "__main__":
    main()
