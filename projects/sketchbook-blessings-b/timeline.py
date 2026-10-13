"""timeline: daily sketchbook spread reel, "unexpected blessings" version B (Instagram 3:4, 14 s, piano only).

Fourth look in the series: warm cream page, art revealed through growing dots (her mark-making), a slow glide
along the wide spread, the three pages fanned together, DM Serif Display + soft lowercase Inter Tight.
Reading time: 0.3 s/word + 0.5 s once a line is complete.
"""
W, H = 1080, 1440          # 3:4
FPS = 24
DURATION = 14.0

SHOTS = [
    (0.0, 3.4, "pause"),       # square page appears dot by dot from the centre: "pause.."
    (3.4, 6.8, "breathe"),     # glide along the wide spread, one slow breath: "take a deep breath"
    (6.8, 10.6, "blessings"),  # the three pages fan out together: "unexpected blessings coming your way"
    (10.6, DURATION, "follow"),# tall page settles, closing line
]
DOTS = 0.7                     # dot-wipe length between shots

CREAM, INK, GOLD, BLUE = "#F6F0E4", "#1B2A5E", "#E9B824", "#2F5BD3"

COPY = {
    "pause": "pause..",
    "breathe": "take a deep breath",
    "bless1": "Unexpected blessings",
    "bless2": "coming your way",
    "follow1": "if you like it, follow for",
    "follow2": "daily sketchbook inspiration",
    "handle": "@the_unrushed.whispers",
}
PAGES = {"square": "assets/page_square.png", "tall": "assets/page_tall.png", "spread": "assets/spread.png"}
SERIF, LIGHT, MED = "DMSerifDisplay-400.ttf", "InterTight-300.ttf", "InterTight-500.ttf"
PIANO = dict(key="C", seed=57)


def cues(music="work/piano.wav"):
    return {"duration": DURATION, "music": {"file": music, "gain_db": 0, "fade_out": 0.0}, "sfx": []}
