"""timeline: Unrushed Studio install tutorial (16:9, ~4.5 min, YouTube).

Voice-led: every scene is a list of spoken lines. make_vo.py renders each line, then this file builds the
timing from the real line lengths, so picture, captions and sound always agree.
Each line can carry a visual "item" that appears on screen when that line starts.
Steps follow START-HERE.md and unrushed-edit/references/install.md exactly.
"""

import json
import os
from pathlib import Path

W, H = 1920, 1080          # 16:9 YouTube
if os.environ.get("VIBE_SIZE"):
    W, H = (int(v) for v in os.environ["VIBE_SIZE"].lower().split("x"))
FPS = 30
BPM = 84
BEAT = 60.0 / BPM
MOOD = "chill"
VOICE_MIX = {"hf_beta": 1.0}   # the artist's pick from the launch Reel
VO_SPEED = 0.95
GAP, PAD_IN, PAD_OUT = 0.6, 1.0, 1.8

# (key, chapter label, title, view, [(spoken line, on-screen item), ...])
# views: title, checklist, files, terminal, finder, explorer, chat, tips, end
SCRIPT = [
    ("intro", "", "How to install Unrushed Studio", "title", [
        ("Hi! In this video, I'll show you how to install Unrushed Studio, step by step.", None),
        ("It takes about ten minutes, and you only do it once.", "About 10 minutes · only once"),
        ("After that, your painting time turns into Reels, carousels and more.", None),
    ]),
    ("need", "Before you start", "What you need", "checklist", [
        ("First, here's what you need.", None),
        ("A Mac or a Windows computer.", "A Mac or Windows computer"),
        ("Claude Code, installed on that computer.", "Claude Code"),
        ("Python 3, and ffmpeg. They're both free.", "Python 3 + ffmpeg (free)"),
        ("Don't worry if you don't have them yet. I'll show you how.", None),
    ]),
    ("unzip", "Step 1", "Download and unzip", "files", [
        ("Step one. Download the zip file you bought.", "Unrushed-Studio-Complete-v1.0.zip"),
        ("Double-click it to unzip. You'll get a folder.", "folder"),
        ("Inside, there's a Start Here guide, the Style Menu, and eight folders that start with unrushed.",
         "contents"),
        ("Those eight folders are the skills.", "highlight"),
    ]),
    ("open_term", "Step 2", "Open a terminal", "terminal", [
        ("Step two. Open a terminal. It's a window where you type commands.", None),
        ("On a Mac, press Command and Space, type Terminal, and press Enter.", ("mac", "⌘ Space → Terminal")),
        ("On Windows, open the Start menu, type PowerShell, and press Enter.", ("win", "Start → PowerShell")),
        ("Now type ffmpeg dash version, and press Enter.", ("cmd", "ffmpeg -version")),
        ("Then type python3 dash dash version. On Windows, type python instead.", ("cmd", "python3 --version")),
        ("If both show a version number, skip to step four.", ("ok", "ffmpeg version 7.x · Python 3.12")),
    ]),
    ("tools", "Step 3", "Install ffmpeg and Python", "terminal", [
        ("Step three, only if something was missing.", None),
        ("On a Mac, first install Homebrew from brew dot s h. Copy the one line from the site into Terminal.",
         ("note", "brew.sh → copy the one line")),
        ("Then type: brew install ffmpeg python.", ("cmd", "brew install ffmpeg python")),
        ("On Windows, type: winget install Gyan dot FFmpeg.", ("cmd", "winget install Gyan.FFmpeg")),
        ("And: winget install Python dot Python dot three twelve.", ("cmd", "winget install Python.Python.3.12")),
        ("Then close PowerShell, and open it again, so it finds the new tools.", ("note", "Close and reopen PowerShell")),
        ("Run the version checks again. Now you should see both.", ("ok", "ffmpeg ✓   Python ✓")),
    ]),
    ("claude", "Step 4", "Get Claude Code", "terminal", [
        ("Step four. If you don't have Claude Code yet, install it with the official guide.",
         ("note", "docs.claude.com → Claude Code")),
        ("When it's ready, typing claude in the terminal opens it.", ("cmd", "claude")),
        ("Type slash exit, or close the window, to leave it for now.", ("cmd", "/exit")),
    ]),
    ("copy_mac", "Step 5 · Mac", "Copy the skills into place", "finder", [
        ("Step five. Copy the skills to where Claude looks for them. First, on a Mac.", None),
        ("In Terminal, type this line once. It makes the skills folder if it isn't there yet.",
         ("cmd", "mkdir -p ~/.claude/skills")),
        ("Now open Finder. Press Command, Shift and G, to go to a folder.", ("keys", "⌘ ⇧ G")),
        ("Type tilde, slash, dot claude, slash skills, and press Enter.", ("path", "~/.claude/skills")),
        ("Drag all eight unrushed folders into this window.", ("drag", None)),
        ("Each folder sits straight inside skills. Not in another folder.", ("check", "skills/unrushed-edit ✓")),
    ]),
    ("copy_win", "Step 5 · Windows", "Copy the skills into place", "explorer", [
        ("On Windows, open PowerShell and type this line once.", ("cmd", "mkdir $HOME\\.claude\\skills")),
        ("Then open File Explorer, and click the address bar at the top.", None),
        ("Type percent user profile percent, backslash, dot claude, backslash skills, and press Enter.",
         ("path", "%USERPROFILE%\\.claude\\skills")),
        ("Drag all eight unrushed folders into this window.", ("drag", None)),
    ]),
    ("extras", "Step 6 · optional", "Captions and extras", "terminal", [
        ("Step six is optional, but I recommend it.", None),
        ("For captions, type: pip install faster-whisper.", ("cmd", "pip install faster-whisper")),
        ("For face framing and photo alignment, type: pip install opencv-python.",
         ("cmd", "pip install opencv-python")),
        ("On Windows, start these with python dash m pip.", ("note", "Windows: python -m pip install …")),
        ("The first captioned video downloads a speech model once. After that, it works offline.",
         ("note", "Needs internet once, then offline")),
    ]),
    ("first", "Step 7", "Your first run", "chat", [
        ("Step seven. Let's try it.", None),
        ("In the terminal, go to the folder with your painting videos, and type claude.",
         ("cmd", "cd Paintings  →  claude")),
        ("Ask: what Unrushed skills do you have?", ("you", "What Unrushed skills do you have?")),
        ("Claude lists all eight. That means they're installed.", ("claude", "Unrushed Edit, Cinematic Studio, Footage Fixer, No-Film Studio, Teaching Kit, Sell Your Art, Post Everywhere, Batch & Library")),
        ("Now say: show me the styles on my painting. Then pick a number from each picture.",
         ("you", "Show me the styles on my painting.")),
    ]),
    ("app", "Another way", "Using the Claude app", "tips", [
        ("Using the Claude app instead of Claude Code? You can still use the skills.", None),
        ("Zip one skill folder, and add it as a skill in Claude's settings.", "Zip a skill folder → add it in Settings"),
        ("For videos, Claude Code is better, because your files stay on your computer.",
         "Claude Code is best for video"),
    ]),
    ("help", "If something goes wrong", "Quick fixes", "tips", [
        ("If something doesn't work, check these.", None),
        ("ffmpeg not found? Close the terminal, and open it again.", "“ffmpeg not found” → reopen the terminal"),
        ("Claude can't see the skills? Check the folder is dot claude, with the dot, and the eight folders sit right inside skills.",
         "Skills missing → .claude/skills/unrushed-…"),
        ("And steps can change between Claude versions. If anything looks different, check docs dot claude dot com.",
         "Something looks different → docs.claude.com"),
    ]),
    ("outro", "", "You're ready to work", "end", [
        ("That's it. You're ready.", None),
        ("Open the Style Menu, choose your look, and go paint. Your posts come out of your painting time.", None),
    ]),
]

# chapter list for the YouTube description (filled from the timing below)
CHAPTER_KEYS = ["intro", "need", "unzip", "open_term", "tools", "claude", "copy_mac", "copy_win", "extras",
                "first", "app", "help", "outro"]


def line_id(key, i):
    return f"{key}_{i:02d}"


def _durations():
    p = Path(__file__).resolve().parent / "work" / "vo_durations.json"
    return json.loads(p.read_text()) if p.exists() else {}


def build():
    """scenes [(start, end, key)] and lines [(start, end, key, i, text, item)] from real voice lengths."""
    d = _durations()
    scenes, lines, t = [], [], 0.0
    for key, _chap, _title, _view, ls in SCRIPT:
        s0 = t
        t += PAD_IN
        for i, (txt, item) in enumerate(ls):
            dur = d.get(line_id(key, i), max(1.5, len(txt.split()) / 2.6))
            lines.append((t, t + dur, key, i, txt, item))
            t += dur + GAP
        t += PAD_OUT - GAP
        scenes.append((s0, t, key))
    return scenes, lines, t


SCENES, LINES, DURATION = build()
SCENE_INFO = {k: (chap, title, view, ls) for k, chap, title, view, ls in SCRIPT}

SFX = [(s + 0.05, "whoosh", -14) for s, e, k in SCENES[1:]]


def scene_at(t):
    for s, e, name in SCENES:
        if s <= t < e:
            return name, t - s, e - s
    s, e, name = SCENES[-1]
    return name, t - s, e - s


def line_at(t):
    for ln in LINES:
        if ln[0] - 0.05 <= t < ln[1] + GAP:
            return ln
    return None


def item_k(key, i, t):
    """seconds since line i of scene key started (negative if not yet)."""
    for s, e, k, j, *_ in LINES:
        if k == key and j == i:
            return t - s
    return -1


def chapters():
    out = []
    for s, e, k in SCENES:
        m, sec = divmod(int(s), 60)
        chap, title = SCENE_INFO[k][0], SCENE_INFO[k][1]
        out.append(f"{m}:{sec:02d} " + (f"{chap}: {title}" if chap else title))
    return out


def cues(voice=None, music="work/music.wav"):
    c = {"duration": DURATION, "music": {"file": music, "gain_db": -14, "duck_db": -10, "fade_out": 3.0},
         "sfx": [{"t": round(t, 3), "kind": k, "gain_db": g} for t, k, g in SFX]}
    if voice:
        c["voice"] = {"file": voice, "gain_db": 0}
    return c
