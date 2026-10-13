"""timeline: ARTIST DATE | Playing Tourist in My Own City (16:9, 77 s).

Voice is built phrase by phrase (build_vo.py -> work/vo.json) so captions and cuts sit on exact phrase times.
Footage: two phone clips (raw/temple.mp4, raw/temple2.mp4), landscape 720x404 letterboxed in 9:16 files.
"""
import json
from pathlib import Path

W, H = 1920, 1080
FPS = 24
DURATION = 86.0
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
SHOTS = [   # v3: every scene appears exactly once; timed to the artist's own voiceover (raw/voice.mp3)
    ("title"    , "temple"  ,   0.00,   0.00,      3.3, "r"  , 0.7),
    ("street"   , "temple2" ,  51.00,   3.30,      9.3, "l"  , 0.735),
    ("spire"    , "temple2" ,  10.00,   9.30,    11.83, "u"  , 1.0),
    ("tank"     , "temple"  ,  55.50,  11.83,    14.08, "r"  , 1.0),
    ("farpath"  , "temple"  ,  27.00,  14.08,    20.07, "in" , 1.0),
    ("canopy"   , "temple3" ,   0.00,  20.07,    22.38, "r"  , 0.8),
    ("shadow"   , "temple"  ,  10.40,  22.38,    24.67, "in" , 1.0),
    ("sitting"  , "temple"  ,   3.00,  24.67,    27.56, "r"  , 0.8),
    ("carvings" , "temple2" ,  35.00,  27.56,    29.71, "l"  , 1.0),
    ("redtree"  , "temple"  ,  50.50,  29.71,    31.47, "in" , 1.0),
    ("nandi"    , "temple2" ,  40.00,  31.47,    33.24, "in" , 1.0),
    ("pond"     , "temple2" ,   4.00,  33.24,    35.82, "in" , 1.0),
    ("pillars"  , "temple2" ,  45.00,  35.82,    39.41, "r"  , 1.0),
    ("lawn"     , "temple4" ,   0.00,  39.41,    44.16, "in" , 0.8),
    ("lakepath" , "temple"  ,  22.00,  44.16,    48.09, "r"  , 1.0),
    ("garden"   , "temple3" ,  27.00,  48.09,    52.88, "l"  , 1.0),
    ("lamp"     , "temple"  ,  68.50,  52.88,    56.07, "l"  , 0.72),
    ("looking"  , "temple3" ,   9.00,  56.07,    63.22, "in" , 1.0),
    ("treepond" , "temple"  ,  40.00,  63.22,    71.47, "in" , 1.0),
    ("offering" , "temple2" ,  18.00,  71.47,    78.54, "r"  , 1.0),
    ("walk"     , "temple"  ,  17.05,  78.54, DURATION, "in" , 0.643),
]
# per-source letterbox crop (phone files are 9:16 with the 16:9 picture in the middle; temple3/4 are landscape)
SRC_CROPS = {"temple": "crop=720:404:0:438", "temple2": "crop=720:404:0:438",
             "temple3": "crop=720:404:0:1", "temple4": "crop=2160:1215:0:0"}

TITLE = ("ARTIST DATE", "Playing Tourist in My Own City")
HANDLE = "@the_unrushed.whispers"
# No voiceover: the script is shown as on-screen text cards (1-2 lines), each starting on its phrase time
# (the shots were cut to these phrase times) and staying up until the next card. Reading time >= 0.3 s/word + 0.5 s.
CARD_GROUPS = [["thirty"], ["temple", "before"], ["passed"], ["rushing"], ["simply", "present"],
               ["colours", "little"], ["still", "corner"], ["strange"], ["years", "seeing"], ["roads", "really"],
               ["today", "knew"], ["about"], ["routine", "fresh"], ["new"], ["beginner"]]
END_CARD = 83.0
# The artist's own voiceover: raw/voice.mp3 placed at VOICE_OFFSET. Line starts (s, in the recording) were found
# with an offline Whisper pass (sherpa-onnx base.en) + the breaths between lines; see work/voice_segments.json.
VOICE_FILE = "raw/voice.mp3"
VOICE_OFFSET = 3.0
VOICE_LINES = {"thirty": 0.4, "temple": 6.3, "passed": 11.94, "rushing": 17.06, "simply": 19.46, "colours": 23.7, "still": 29.36, "strange": 37.32, "years": 40.08, "roads": 46.38, "today": 52.9, "about": 60.94, "routine": 64.38, "new": 71.26, "beginner": 75.56}
VOICE_END = 79.30
CARDS = []
for _i, _g in enumerate(CARD_GROUPS):
    _s = VOICE_LINES[_g[0]] + VOICE_OFFSET - 0.1
    _e = (VOICE_LINES[CARD_GROUPS[_i + 1][0]] + VOICE_OFFSET - 0.25) if _i + 1 < len(CARD_GROUPS) else VOICE_END + VOICE_OFFSET + 0.4
    CARDS.append((_s, _e, [PHRASES[k][2] for k in _g]))
