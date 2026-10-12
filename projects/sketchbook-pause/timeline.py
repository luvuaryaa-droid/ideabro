"""timeline: daily sketchbook spread reel (Instagram 3:4, 12 s, no voice, no captions, soft piano only).

Reading time rule: 0.3 s per word + 0.5 s, counted from when a line has finished writing on.
"""
import os

W, H = 1080, 1440          # 3:4
if os.environ.get("VIBE_SIZE"):
    W, H = (int(v) for v in os.environ["VIBE_SIZE"].lower().split("x"))
FPS = 24
DURATION = 12.0
XFADE = 0.5

# (start, end, shot)
SHOTS = [
    (0.0, 3.0, "pause"),      # the clock page: "Pause.."
    (3.0, 6.0, "breathe"),    # the toast page breathes in and out: "take a deep breath"
    (6.0, 8.4, "blessed"),    # the whole spread: "you are blessed."
    (8.4, DURATION, "follow"),  # spread stays: "if you like it, follow for daily sketchbook inspiration"
]

COPY = {
    "pause": "Pause..",
    "breathe": "take a deep breath",
    "blessed": "you are blessed.",
    "follow1": "if you like it,",
    "follow2": "follow for daily",
    "follow3": "sketchbook inspiration",
    "handle": "@the_unrushed.whispers",
}

PAGES = {"clock": "assets/page_clock.png", "toast": "assets/page_toast.png", "spread": "assets/spread.png"}


def shot_at(t):
    for s, e, name in SHOTS:
        if s <= t < e:
            return name, s, e
    s, e, name = SHOTS[-1]
    return name, s, e


def cues(music="work/piano.wav"):
    return {"duration": DURATION, "music": {"file": music, "gain_db": 0, "fade_out": 0.0}, "sfx": []}
