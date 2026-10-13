"""timeline: daily sketchbook spread reel, "unexpected blessings" (Instagram 3:4, 14 s, no voice, no captions, piano).

Third look in the series (v1 paper prints, v2 full-bleed camera, this: spiral + iris on navy):
spiral out of a flower's centre -> the tall page breathes once -> an iris opens from the centre onto the spread.
Reading time: 0.3 s/word + 0.5 s after a line is complete.
"""
W, H = 1080, 1440          # 3:4
FPS = 24
DURATION = 14.0

SHOTS = [
    (0.0, 3.2, "pause"),       # inside a flower's centre, spiralling out: "Pause.."
    (3.2, 6.6, "breathe"),     # the tall page breathes in and out once: "take a deep breath"
    (6.6, 10.6, "blessings"),   # iris opens onto the whole spread: "UNEXPECTED BLESSINGS / COMING YOUR WAY"
    (10.6, DURATION, "follow"), # spread lifts, closing line
]
IRIS = 0.9                     # iris-open length at the start of "blessings"

FLOWER = (0.324, 0.42)         # centre of the top flower on the square page (fraction)
NAVY, CREAM, GOLD = "#13235B", "#F7F2E6", "#F2C230"   # from the page: ink blue, paper, the yellow strokes

COPY = {
    "pause": "PAUSE..",
    "breathe": "TAKE A DEEP BREATH",
    "bless1": "UNEXPECTED BLESSINGS",
    "bless2": "COMING YOUR WAY",
    "follow1": "IF YOU LIKE IT, FOLLOW",
    "follow2": "FOR DAILY SKETCHBOOK",
    "follow3": "INSPIRATION",
    "handle": "@the_unrushed.whispers",
}
PAGES = {"square": "assets/page_square.png", "tall": "assets/page_tall.png", "spread": "assets/spread.png"}
LIGHT, BOLD = "JosefinSans-300.ttf", "JosefinSans-600.ttf"
PIANO = dict(key="G", seed=41)


def cues(music="work/piano.wav"):
    return {"duration": DURATION, "music": {"file": music, "gain_db": 0, "fade_out": 0.0}, "sfx": []}
