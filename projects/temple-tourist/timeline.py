"""timeline: ARTIST DATE | Playing Tourist in My Own City (16:9, 77 s).

Voice is built phrase by phrase (build_vo.py -> work/vo.json) so captions and cuts sit on exact phrase times.
Footage: two phone clips (raw/temple.mp4, raw/temple2.mp4), landscape 720x404 letterboxed in 9:16 files.
"""
import json
from pathlib import Path

W, H = 1920, 1080
FPS = 24
DURATION = 77.0
VO_START = 3.6
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
    ("title",     "temple",  0.0,   0.0,  3.3, "r",  0.7),   # temple + shrine in the garden: title
    ("street",    "temple2", 51.0,  3.3,  8.0, "l",  0.85),  # "...thirty years living in" - the everyday city
    ("spire",     "temple2", 10.0,  8.0, 10.3, "u",  1.0),   # "I went to a temple in my own city,"
    ("tank",      "temple",  55.5, 10.3, 12.25, "r", 1.0),   # "a place I have visited before,"
    ("path",      "temple",  27.0, 12.25, 16.6, "in", 1.0),  # "perhaps passed by a thousand times..."
    ("walk",      "temple",  17.0, 16.6, 19.6, "l",  1.0),   # "I wasn't rushing..."  (you, walking towards camera)
    ("shadow",    "temple",  10.4, 19.6, 22.2, "in", 1.0),   # "I was there simply to be there..."
    ("sitting",   "temple",  3.0,  22.2, 24.3, "r",  1.0),   # "present."  (you on the lawn)
    ("carvings",  "temple2", 35.0, 24.3, 26.6, "l",  1.0),   # "To notice the colours, the details,"
    ("redtree",   "temple",  50.5, 26.6, 28.2, "in", 1.0),   # "the little things..."
    ("nandi",     "temple2", 40.0, 28.2, 30.1, "in", 1.0),   # "...I might otherwise walk past."
    ("pond",      "temple2", 4.0,  30.1, 32.0, "in", 1.0),   # "To stand still for a moment"
    ("pillars",   "temple2", 45.0, 32.0, 34.5, "r",  1.0),   # "and let the place be more than..."
    ("offering",  "temple2", 18.0, 34.5, 37.0, "l",  1.0),   # "...familiar corner of my city."
    ("sitting2",  "temple",  5.3,  37.0, 39.9, "in", 0.7),   # "It's strange how familiarity works."  (you on the lawn)
    ("lakepath",  "temple",  22.0, 39.9, 42.8, "r",  1.0),   # "We live in a place for years, sometimes decades,"
    ("trees",     "temple",  8.0,  42.8, 45.3, "in", 0.6),   # "and slowly stop seeing it."
    ("spire2",    "temple",  63.0, 45.3, 48.1, "u",  1.0),   # "We know the roads, the landmarks, the turns to take."
    ("lamp",      "temple",  68.5, 48.1, 51.2, "l",  0.75),  # "But do we really see them?"
    ("shadow2",   "temple2", 0.0,  51.2, 54.3, "in", 1.0),   # "Today, I wondered how many little things I had missed"
    ("offering2", "temple2", 24.0, 54.3, 57.6, "r",  1.0),   # "simply because I thought I already knew this place."
    ("farpath",   "temple",  32.5, 57.6, 61.2, "in", 1.0),   # "And perhaps that's what an Artist Date is about."
    ("pillars2",  "temple2", 48.1,  61.2, 63.4, "l", 1.0),   # "Stepping outside your usual routine"
    ("spire3",    "temple2", 13.0, 63.4, 66.2, "in", 0.85),  # "and meeting the familiar with fresh eyes."
    ("tank2",     "temple",  58.3, 66.2, 70.0, "l",  1.0),   # "Perhaps I don't always need a new place to find inspiration."
    ("toward",    "temple",  73.45, 70.0, 73.0, "in", 0.72), # "Perhaps I just need to become a beginner again."  (you, walking towards camera)
    ("end",       "temple",  41.0, 73.0, DURATION, "in", 0.9),  # the pond and tree: end card
]

TITLE = ("ARTIST DATE", "Playing Tourist in My Own City")
HANDLE = "@the_unrushed.whispers"
# No voiceover: the script is shown as on-screen text cards (1-2 lines), each starting on its phrase time
# (the shots were cut to these phrase times) and staying up until the next card. Reading time >= 0.3 s/word + 0.5 s.
CARD_GROUPS = [["thirty"], ["temple", "before"], ["passed"], ["rushing"], ["simply", "present"],
               ["colours", "little"], ["still", "corner"], ["strange"], ["years", "seeing"], ["roads", "really"],
               ["today", "knew"], ["about"], ["routine", "fresh"], ["new"], ["beginner"]]
END_CARD = 74.6
CARD_START = {"thirty": 3.4, "temple": 8.1, "passed": 13.0, "routine": 61.6}   # rebalanced so every card gets its reading time
CARDS = []
for _i, _g in enumerate(CARD_GROUPS):
    _st = lambda k: CARD_START.get(k, PHRASES[k][0] - 0.1)  # noqa: E731
    _s = _st(_g[0])
    _e = (_st(CARD_GROUPS[_i + 1][0]) - 0.15) if _i + 1 < len(CARD_GROUPS) else END_CARD - 0.2
    CARDS.append((_s, _e, [PHRASES[k][2] for k in _g]))
