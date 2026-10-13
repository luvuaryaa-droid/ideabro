"""timeline: "unexpected blessings" version C - paper cut-out, cozy journal (Instagram 3:4, 14 s, piano only).

Kraft desk + dotted journal page, washi tape, the artist's flowers cut out of her page with scissor edges,
paper-cut leaves and confetti, words on torn paper strips in a typewriter face. All motion on 12 drawings/s.
"""
W, H = 1080, 1440          # 3:4
FPS = 24
DURATION = 14.0
STEP = 12                  # drawings per second (stop-motion feel)

SHOTS = [
    (0.0, 3.4, "pause"),       # cut-out flowers are placed on the journal page one by one: "pause.."
    (3.4, 6.8, "breathe"),     # the tall page taped in, paper clouds drift, a flower breathes: "take a deep breath"
    (6.8, 10.6, "blessings"),  # the spread taped in, paper confetti falls: "unexpected blessings coming your way"
    (10.6, DURATION, "follow"),
]
TEAR = 0.55                    # torn-paper wipe between shots

KRAFT, PAGE, INK, BLUE, GOLD, TEAL, PINK = "#C9A57B", "#F4ECDC", "#2B2A33", "#2950C8", "#EDBE2B", "#5CC3C1", "#E9A7A0"

COPY = {
    "pause": "pause..",
    "breathe": "take a deep breath",
    "bless1": "unexpected blessings",
    "bless2": "coming your way",
    "follow1": "if you like it, follow for",
    "follow2": "daily sketchbook inspiration",
    "handle": "@the_unrushed.whispers",
}
PAGES = {"square": "assets/page_square.png", "tall": "assets/page_tall.png", "spread": "assets/spread.png"}
CUTS = [f"assets/cut_{i}.png" for i in range(4)]
TYPE, HAND = "SpecialElite-400.ttf", "Caveat-700.ttf"
PIANO = dict(key="A", seed=66)


def cues(music="work/piano.wav"):
    return {"duration": DURATION, "music": {"file": music, "gain_db": 0, "fade_out": 0.0}, "sfx": []}
