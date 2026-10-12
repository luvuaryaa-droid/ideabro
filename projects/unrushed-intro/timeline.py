"""timeline: The Unrushed Whispers, 500-follower re-introduction (16:9, 50 s).

The voiceover is built phrase by phrase (build_vo.py -> work/vo.json), so every phrase has an exact start/end.
Shots and captions are anchored to those phrases; nothing is guessed.
"""

import json
import os
from pathlib import Path

W, H = 1920, 1080
if os.environ.get("VIBE_SIZE"):
    W, H = (int(v) for v in os.environ["VIBE_SIZE"].lower().split("x"))
FPS = 24
DURATION = 50.0
VO_START = 1.2            # voice enters after a breath of music
MOOD = "chill"            # soft lo-fi bed, 84 BPM
BPM = 84
MUSIC_SEED = 11

_vo = json.loads((Path(__file__).resolve().parent / "work" / "vo.json").read_text())
PHRASES = {p["id"]: (p["s"] + VO_START, p["e"] + VO_START, p["text"]) for p in _vo["phrases"]}


def ps(pid):
    return PHRASES[pid][0]


def pe(pid):
    return PHRASES[pid][1]


# (start, end, shot). Cuts sit in the pauses between phrases.
SHOTS = [
    (0.0, 4.25, "title"),
    (4.25, 10.3, "five_hundred"),
    (10.3, 12.55, "banker"),
    (12.55, 16.28, "art"),
    (16.28, 18.38, "rain"),
    (18.38, 20.8, "sun"),
    (20.8, 27.6, "belief"),
    (27.6, 29.98, "journey"),
    (29.98, 31.52, "sketchbooks"),
    (31.52, 33.12, "artist_dates"),
    (33.12, 38.7, "artists_way"),
    (38.7, 42.4, "thanks"),
    (42.4, DURATION, "end"),
]
XFADE = 0.45              # gentle dissolve between shots

# Captions = the spoken phrases. The belief shot writes its words on screen, so no caption there.
NO_CAPTION = {"beliefa", "beliefb"}
CAPTIONS = [(s, e, txt) for pid, (s, e, txt) in PHRASES.items() if pid not in NO_CAPTION]

COPY = {
    "title": "the unrushed whispers",
    "title_sub": "a re-introduction",
    "five_hundred": "500",
    "five_hundred_sub": "followers",
    "belief1": "creativity is an",
    "belief2": "antidote to anxiety",
    "belief3": "& the highest form of healing",
    "book1": "The Artist's Way",
    "book2": "Julia Cameron",
    "handle": "@the_unrushed.whispers",
    "end_line": "share it with someone who needs it",
}

# Footage clips cut from the artist's own videos (work/clips, see brief.md for in/out points).
CLIPS = {
    "sun": "work/clips/sun.mp4", "trail": "work/clips/trail.mp4", "bridge": "work/clips/bridge.mp4",
    "sign": "work/clips/sign.mp4", "seeds": "work/clips/seeds.mp4", "rain": "work/clips/rain.mp4",
    "page_glasses": "work/clips/page_glasses.mp4", "page_tulips": "work/clips/page_tulips.mp4",
    "page_figs": "work/clips/page_figs.mp4", "page_hat": "work/clips/page_hat.mp4",
    "page_mosaic": "work/clips/page_mosaic.mp4",
}


def shot_at(t):
    for s, e, name in SHOTS:
        if s <= t < e:
            return name, s, e
    s, e, name = SHOTS[-1]
    return name, s, e


def cues(voice="work/vo.wav", music="work/music.wav"):
    return {"duration": DURATION,
            "voice": {"file": voice, "gain_db": 0, "t": VO_START},
            "music": {"file": music, "gain_db": -11, "duck_db": -8, "fade_out": 3.0},
            "tracks": [{"file": "work/crackle.wav", "t": 0.0, "gain_db": -6}],
            "sfx": [{"t": round(ps("k500a") - 0.2, 3), "kind": "sparkle", "gain_db": -20},
                    {"t": round(ps("thanks") - 0.15, 3), "kind": "sparkle", "gain_db": -20}]}
