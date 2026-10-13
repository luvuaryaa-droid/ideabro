"""timeline: ARTIST DATE | Playing Tourist in My Own City (16:9, 42.5 s).

Voice is built phrase by phrase (build_vo.py -> work/vo.json) so captions and cuts sit on exact phrase times.
Footage: two phone clips (raw/temple.mp4, raw/temple2.mp4), landscape 720x404 letterboxed in 9:16 files.
"""
import json
from pathlib import Path

W, H = 1920, 1080
FPS = 24
DURATION = 42.5
VO_START = 4.0
XF = 0.6                       # dissolve length between shots
BAR = 103                      # cinematic bars (top + bottom) -> ~2.2:1 picture
SRC_CROP = "crop=720:404:0:438"
GRADE = ("eq=contrast=0.95:saturation=0.9:gamma=1.03,"
         "colorbalance=rs=0.07:gs=0.01:bs=-0.07:rm=0.05:bm=-0.05:rh=0.03:bh=-0.05,"
         "curves=master='0/0.05 0.5/0.52 1/0.96'")

_vo = json.loads((Path(__file__).resolve().parent / "work" / "vo.json").read_text())
PHRASES = {p["id"]: (round(p["s"] + VO_START, 3), round(p["e"] + VO_START, 3), p["text"]) for p in _vo["phrases"]}

# shot: (name, source, source_in, start, end, drift, speed)
#   drift = slow camera move across the frame: 'l', 'r', 'u', 'd', 'in'  ; speed < 1 = gentle slow motion
SHOTS = [
    ("title",    "temple",  0.0,  0.0,  3.4, "r",  0.7),   # temple + shrine in the garden: title
    ("street",   "temple2", 51.0, 3.4,  8.4, "l",  0.85),    # "...thirty years living in" - the everyday city
    ("spire",    "temple2", 10.0, 8.4,  10.8, "u", 1.0),    # "I went to a temple in my own city,"
    ("tank",     "temple",  55.5, 10.8, 12.8, "r", 1.0),    # "a place I have visited before,"
    ("path",     "temple",  27.0, 12.8, 17.1, "in", 1.0),   # "perhaps passed by a thousand times..."
    ("walk",     "temple",  17.0, 17.1, 20.1, "l", 1.0),    # "I wasn't rushing to get somewhere else."
    ("shadow",   "temple",  10.4, 20.1, 22.6, "in", 1.0),   # "I was there simply to be there..."
    ("sitting",  "temple",  3.0,  22.6, 24.8, "r", 1.0),    # "present."
    ("carvings", "temple2", 35.0, 24.8, 27.0, "l", 1.0),    # "To notice the colours, the details,"
    ("offering", "temple2", 22.0, 27.0, 29.0, "r", 1.0),    # "the little things..."
    ("nandi",    "temple2", 40.0, 29.0, 30.6, "in", 1.0),   # "...I might otherwise walk past."
    ("pond",     "temple2", 4.0,  30.6, 33.4, "in", 1.0),   # "To stand still for a moment"
    ("pillars",  "temple2", 45.0, 33.4, 35.6, "r", 1.0),    # "and let the place be more than..."
    ("toward",   "temple",  73.45, 35.6, 38.2, "in", 0.85),  # "...familiar corner of my city."  (walking toward us)
    ("end",      "temple",  41.0, 38.2, DURATION, "in", 0.9),  # the pond and tree: end card
]

TITLE = ("ARTIST DATE", "Playing Tourist in My Own City")
HANDLE = "@the_unrushed.whispers"
CAPTIONS = [(s, e, txt) for s, e, txt in PHRASES.values()]
