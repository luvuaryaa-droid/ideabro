#!/usr/bin/env python3
"""Check everything the Vibe Editing System needs, with versions.

Usage:
    python scripts/check_setup.py           # quick check
    python scripts/check_setup.py --doctor  # also run `npx hyperframes doctor`
"""
import argparse
import shutil
import subprocess
import sys


def version(cmd):
    exe = shutil.which(cmd[0]) or shutil.which(cmd[0] + ".cmd")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, timeout=60)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except Exception as e:  # noqa: BLE001
        return f"found, but failed to run ({e})"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doctor", action="store_true", help="also run npx hyperframes doctor")
    args = parser.parse_args()

    ok = True

    def report(name, found, hint, required=True):
        nonlocal ok
        mark = "OK " if found else ("MISSING" if required else "optional")
        print(f"  [{mark:^8}] {name:<16} {found or hint}")
        if required and not found:
            ok = False

    print("Vibe Editing System setup check\n")
    report("Python", sys.version.split()[0], "")

    node = version(["node", "--version"])
    if node and node.lstrip("v").split(".")[0].isdigit() and int(node.lstrip("v").split(".")[0]) < 22:
        node = None
        report("Node.js 22+", None, "Node.js is older than 22. Install the LTS from https://nodejs.org")
    else:
        report("Node.js 22+", node, "install the LTS from https://nodejs.org")

    report("FFmpeg", version(["ffmpeg", "-version"]), "Mac: brew install ffmpeg · Windows: winget install Gyan.FFmpeg")
    report("Claude Code", version(["claude", "--version"]), "https://claude.com/product/claude-code")

    try:
        import faster_whisper  # noqa: F401
        fw = f"faster-whisper {faster_whisper.__version__}"
    except ImportError:
        fw = None
    wc = version(["whisper-cli", "--help"]) and "whisper-cpp (whisper-cli)"
    whisper = fw or wc
    report("Whisper", whisper, "python -m pip install -r requirements.txt  (Mac alt: brew install whisper-cpp)")

    report("Git", version(["git", "--version"]), "optional on Windows: https://git-scm.com", required=False)

    print()
    if args.doctor:
        npx = shutil.which("npx") or shutil.which("npx.cmd")
        if npx:
            print("Running npx hyperframes doctor...\n")
            subprocess.run([npx, "--yes", "hyperframes@0.8.149", "doctor"])
        else:
            print("Skipping hyperframes doctor: npx not found.")

    print("All required tools found." if ok else "Some tools are missing. Install them, open a new terminal, re-run this.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
