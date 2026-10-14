"""timeline: Unrushed Studio install tutorial, the easy way (16:9, YouTube). Detailed version: work/timeline_detailed.py

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
GAP, PAD_IN, PAD_OUT = 0.5, 0.8, 1.4

# (key, chapter label, title, view, [(spoken line, on-screen item), ...])
# views: title, checklist, files, terminal, finder, explorer, chat, tips, end
SCRIPT = [
    ("intro", "", "Install Unrushed Studio the easy way", "title", [
        ("Installing Unrushed Studio is simple. Claude does it for you.", "No terminal · no commands"),
        ("Here's how, in four steps.", None),
    ]),
    ("open", "Step 1", "Open Claude Code", "web", [
        ("Step one. Open Claude Code. On the web, go to claude dot ai slash code.", ("url", "claude.ai/code")),
        ("Or use the Code tab in the Claude desktop app.", ("note", "or: Claude desktop app → Code")),
    ]),
    ("attach", "Step 2", "Attach the zip and ask", "web", [
        ("Step two. Attach the Unrushed Studio zip you bought.", ("attach", "Unrushed-Studio-Complete-v1.0.zip")),
        ("And type: read this and install it.", ("you", "Read this and install it.")),
    ]),
    ("repo", "Step 3", "Create a private repository", "web", [
        ("Step three. Claude asks where to keep the skills. Create a new repository.",
         ("claude", "Where should I keep the skills? Pick or create a repository.")),
        ("Give it a name, and make it private. The skills are yours, not for everyone.",
         ("repo", "my-unrushed-skills")),
    ]),
    ("install", "Step 4", "Claude installs it", "web", [
        ("Step four. Claude reads the files, checks them, and installs all eight skills on its own.",
         ("install", None)),
        ("If it asks for permission to save, tap Allow.", ("allow", None)),
        ("The skills now live in your repository, ready in every session.", ("claude", "Done. All 8 Unrushed skills are installed.")),
    ]),
    ("ready", "You're ready", "Try it", "web", [
        ("Now just ask: show me the styles on my painting.", ("you", "Show me the styles on my painting.")),
        ("Pick a number from each picture. That's your look, saved for every Reel.", ("styles", None)),
    ]),
    ("outro", "", "You're ready to work", "end", [
        ("That's it. Open Claude, ask, and go paint.", None),
        ("Your posts come out of your painting time.", None),
    ]),
]

# chapter list for the YouTube description (filled from the timing below)
CHAPTER_KEYS = ["intro", "open", "attach", "repo", "install", "ready", "outro"]


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
