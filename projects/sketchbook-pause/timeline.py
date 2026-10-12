"""timeline: daily sketchbook spread reel v2 (Instagram 3:4, 12 s, no voice, no captions, soft piano only).

v2 look: full-bleed and cinematic. A slow camera travels through the actual pages (no paper, no tape),
elegant serif words fade in letter by letter, warm light leaks between moments.
Reading time rule: 0.3 s per word + 0.5 s after a line is complete.
"""
import os

W, H = 1080, 1440          # 3:4
if os.environ.get("VIBE_SIZE"):
    W, H = (int(v) for v in os.environ["VIBE_SIZE"].lower().split("x"))
FPS = 24
DURATION = 12.0

# (start, end, shot)
SHOTS = [
    (0.0, 3.1, "pause"),       # close on the clock face, pulling back: "Pause.."
    (3.1, 6.3, "breathe"),     # on the yolk, the camera breathes in and out once: "take a deep breath"
    (6.3, 8.7, "blessed"),     # the whole spread revealed over its own blurred glow: "you are blessed."
    (8.7, DURATION, "follow"), # spread settles up, closing words below
]
LEAK = 0.55                    # warm light-leak transition length (centred on each cut)

# camera: focus point (fraction of the page) and zoom (1 = page height fills the frame)
CAM = {
    "pause":   dict(img="clock", focus=((0.33, 0.46), (0.40, 0.50)), zoom=(1.75, 1.12)),
    "breathe": dict(img="toast", focus=((0.45, 0.55), (0.45, 0.55)), zoom=(1.18, 1.18)),
}
BREATH_ZOOM = 0.16             # how far the camera "inhales" on the yolk
YOLK = (0.445, 0.545)          # yolk centre on the toast page (fraction)

COPY = {
    "pause": "Pause..",
    "breathe": "take a deep breath",
    "blessed": "you are blessed.",
    "follow1": "if you like it,",
    "follow2": "follow for daily",
    "follow3": "sketchbook inspiration",
    "handle": "@the_unrushed.whispers",
}

PAGES = {"clock": "assets/page_clock.png", "toast": "assets/page_toast.png", "spread": "assets/spread.png",
         "spread_blur": "assets/spread_blur.png"}
SERIF = "InstrumentSerif-400-italic.ttf"
SERIF_UP = "InstrumentSerif-400.ttf"
PIANO = dict(key="D", seed=21)


def cues(music="work/piano.wav"):
    return {"duration": DURATION, "music": {"file": music, "gain_db": 0, "fade_out": 0.0}, "sfx": []}
