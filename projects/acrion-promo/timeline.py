"""timeline: the single source of truth for acrion-promo (Acrion Realty promo, v1).

Picture (scene.py) and sound (audio cues) both read from here. Never hard-code a time anywhere else.
128 BPM "hype" bed, 12 bars = 22.5 s. Every scene starts on a bar line, every hit on a beat.
"""

import os

W, H = 1080, 1920          # 9:16
if os.environ.get("VIBE_SIZE"):
    W, H = (int(v) for v in os.environ["VIBE_SIZE"].lower().split("x"))
FPS = 30
BPM = 128
BEAT = 60.0 / BPM          # 0.469 s
BAR = 4 * BEAT             # 1.875 s
BARS = 12
DURATION = BARS * BAR      # 22.5 s
MOOD = "hype"
MUSIC_SEED = 7


def beat(n):
    return n * BEAT


def bar(n):
    return n * BAR


# (start, end, scene name)
SCENES = [
    (bar(0), bar(2), "hook"),
    (bar(2), bar(4), "problem"),
    (bar(4), bar(6), "reveal"),
    (bar(6), bar(7), "project0"),
    (bar(7), bar(8), "project1"),
    (bar(8), bar(9), "project2"),
    (bar(9), bar(10), "explore"),
    (bar(10), bar(12), "endcard"),
]

# On-screen copy. Facts only from public sources: the company name, the city and the project names
# listed on acrionrealty.com. No prices, sizes or claims until the client supplies them.
COPY = {
    "hook": ["STILL", "SEARCHING", "FOR THE", "RIGHT HOME?"],
    "problem": ["TOO MANY|OPTIONS.", "ZERO|CLARITY.", "LET'S MAKE|IT SIMPLE."],   # | = line break
    "brand": "ACRION",
    "brand_sub": "REALTY",
    "brand_tag": "RESIDENTIAL HOMES · BHUBANESWAR",
    "projects": ["VAISHNO GREENS", "URBAN MAJESTIC", "ANANTAM"],
    "project_subs": ["", "", "BY MOTWANI PROJECT"],
    "city": "BHUBANESWAR",
    "explore": ["EXPLORE", "EVERY", "PROJECT"],
    "end_title": ["FIND YOUR", "HOME"],
    "cta": "acrionrealty.com",
}

# Sound effects: (time, kind, gain_db[, dur]). Whooshes start ~0.3 s before the cut; the riser ends on the reveal.
SFX = [
    (beat(0), "impact", -5),
    (beat(1), "pop", -9),
    (beat(2), "pop", -9),
    (beat(4), "impact", -4),
    (bar(2) - 0.3, "whoosh", -9),
    (bar(2) + beat(2), "pop", -9),
    (bar(3), "pop", -8),
    (bar(4) - 1.6, "riser", -10, 1.6),
    (bar(4), "impact", -3),
    (bar(4), "bass_drop", -6),
    (bar(4) + beat(4), "sparkle", -11),
] + [(bar(6 + i) - 0.3, "whoosh", -10) for i in range(4)] + [
    (bar(10) - 0.3, "whoosh", -9),
    (bar(10), "impact", -5),
    (bar(10) + beat(3), "ding", -10),
]


def scene_at(t):
    for s, e, name in SCENES:
        if s <= t < e:
            return name, t - s, e - s
    s, e, name = SCENES[-1]
    return name, t - s, e - s


def cues(voice=None, music="work/music.wav"):
    """cues.json payload for: python3 vibe/audio_kit.py mix work/cues.json"""
    sfx = []
    for item in SFX:
        d = {"t": round(item[0], 3), "kind": item[1], "gain_db": item[2]}
        if len(item) > 3:
            d["dur"] = item[3]
        sfx.append(d)
    c = {"duration": DURATION, "music": {"file": music, "gain_db": -7, "duck_db": -10, "fade_out": 1.2}, "sfx": sfx}
    if voice:
        c["voice"] = {"file": voice, "gain_db": 0}
    return c
