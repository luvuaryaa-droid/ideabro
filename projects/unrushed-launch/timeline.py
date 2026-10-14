"""timeline: the single source of truth for projects/unrushed-launch (Unrushed Studio launch Reel, 50 s).

Picture (scene.py) and sound (audio cues) both read from here. Never hard-code a time anywhere else.
"""

import os

W, H = 1080, 1920          # 9:16
if os.environ.get("VIBE_SIZE"):
    W, H = (int(v) for v in os.environ["VIBE_SIZE"].lower().split("x"))
FPS = 30
BPM = 96                   # 1 beat = 0.625 s, 1 bar = 2.5 s
BEAT = 60.0 / BPM
BAR = 4 * BEAT
DURATION = 20 * BAR        # 50 s = 20 bars
MOOD = "playful"

# (scene, length in beats); every scene starts on a beat, the big ones on bar lines
_PLAN = [
    ("hook", 4), ("problem", 4), ("reveal", 4),
    ("styles", 6),
    ("f_edit", 6), ("f_cinematic", 6), ("f_fix", 6), ("f_nofilm", 6),
    ("f_teach", 6), ("f_sell", 6), ("f_everywhere", 6), ("f_batch", 6),
    ("how", 6), ("endcard", 8),
]
SCENES, _b = [], 0
for _name, _n in _PLAN:
    SCENES.append((_b * BEAT, (_b + _n) * BEAT, _name))
    _b += _n
assert abs(_b * BEAT - DURATION) < 1e-6, "plan must fill the whole Reel"

# claims and prices exactly as the artist gave them (sales page + launch price 699)
COPY = {
    "hook": ["YOU PAINT.", "CLAUDE EDITS."],
    "problem": ["One free evening.", "Paint it... or edit it?"],
    "brand": ["UNRUSHED", "STUDIO"],
    "brand_sub": "8 Claude skills made for artists",
    "styles": {"badge": "START HERE", "title": "STYLE MENU",
               "line": "38 styles shown moving. Pick a number, no editing words."},
    "f_edit": {"title": "UNRUSHED EDIT", "line": "One painting session becomes four Reels.",
               "chips": ["Timelapse", "Slow cut", "Reveal", "Voice story"]},
    "f_cinematic": {"title": "CINEMATIC STUDIO", "line": "Film looks, your painting as B-roll, clean voice.",
                    "chips": ["Film looks", "B-roll", "Name card"]},
    "f_fix": {"title": "FOOTAGE FIXER", "line": "True paint colours. No flicker. Steady shots.",
              "before": "Lamp light", "after": "Fixed"},
    "f_nofilm": {"title": "NO-FILM STUDIO", "line": "Just one photo? Get a slow tour of the details."},
    "f_teach": {"title": "TEACHING KIT", "line": "Tutorials with steps, materials and your colours.",
                "card": "Colours I used", "colors": ["#0B1A2D", "#9E6D51", "#5D2927", "#6D524B", "#BFAE9F"]},
    "f_sell": {"title": "SELL YOUR ART", "line": "On a wall at true size, with price and status.",
               "tag": "AVAILABLE", "note": "illustrated mockup"},
    "f_everywhere": {"title": "POST EVERYWHERE", "line": "Carousels, every video shape, YouTube, thumbnails.",
                     "shapes": [("9:16", 9, 16), ("4:5", 4, 5), ("1:1", 1, 1), ("16:9", 16, 9), ("2:3", 2, 3)]},
    "f_batch": {"title": "BATCH & LIBRARY", "line": "Sorts your camera roll. Edits a whole week at once.",
                "rows": ["Session 1", "Session 2"]},
    "how": ["Download the skills.", "Run them in Claude.", "Ready to work."],
    "price_label": "LAUNCH PRICE · ALL 8 SKILLS",
    "price": "₹699",
    "price_was": "₹1,499",
    "edit_only": "Unrushed Edit alone: ₹399",
    "cta": "LINK IN BIO",
    "tagline": "Paint first. Your posts come out of your painting time.",
}
FEATURES = ["f_edit", "f_cinematic", "f_fix", "f_nofilm", "f_teach", "f_sell", "f_everywhere", "f_batch"]

# demo media: every picture was made by the Unrushed skills from the artist's own painting / video
MEDIA = {
    "hook_bg": "raw/clock.jpg",
    "tall": "raw/egg.jpg",
    "wide": "raw/clock.jpg",
    "square": "raw/egg.jpg",
    "styles": "raw/new_captions-sheet.png",
    "styles2": "raw/new_titles-sheet.png",
    "f_edit": "raw/new_sticker_reel.mp4",
    "f_cinematic": "raw/film_clip.mp4",
    "before": "raw/new_before.png",
    "after": "raw/new_after.png",
    "f_nofilm": "raw/new_tour.mp4",
    "f_sell": "raw/new_mockup_story.png",
}


def start(name):
    return next(s for s, e, n in SCENES if n == name)


SFX = [(0.0, "impact", -5), (BEAT * 2, "pop", -8)]
for _s, _e, _n in SCENES[1:]:
    SFX.append((_s - 0.3, "whoosh", -10))
SFX += [(start("reveal") + 0.05, "impact", -4), (start("endcard") + 0.4, "sparkle", -9)]
SFX += [(start(f) + 0.2, "pop", -11) for f in FEATURES]


def scene_at(t):
    for s, e, name in SCENES:
        if s <= t < e:
            return name, t - s, e - s
    s, e, name = SCENES[-1]
    return name, t - s, e - s


def cues(voice=None, music="work/music.wav"):
    c = {"duration": DURATION, "music": {"file": music, "gain_db": -9, "duck_db": -10, "fade_out": 2.0},
         "sfx": [{"t": round(t, 3), "kind": k, "gain_db": g} for t, k, g in SFX]}
    if voice:
        c["voice"] = {"file": voice, "gain_db": 0}
    return c

# explainer voiceover: one line per scene, starts on its scene (or just after the previous line ends)
VOICE_MIX = {"hf_beta": 1.0}   # warm Indian female voice (artist picked sample 3)
VO_SPEED = 1.05
VO = [
    ("hook", "You paint. Claude edits."),
    ("problem", "One free evening. Paint it, or edit it?"),
    ("reveal", "Meet Unrushed Studio. Eight skills for artists."),
    ("styles", "Start with the Style Menu. See a look, pick a number."),
    ("f_edit", "Unrushed Edit turns one painting into four Reels."),
    ("f_cinematic", "Cinematic Studio gives your talking clips a film look."),
    ("f_fix", "Footage Fixer brings back your true paint colours."),
    ("f_nofilm", "Just one photo? No-Film Studio makes a slow tour of the details."),
    ("f_teach", "The Teaching Kit builds tutorials, with the colours you used."),
    ("f_sell", "Sell Your Art puts your painting on a wall, at true size."),
    ("f_everywhere", "Post Everywhere makes carousels, and every video shape."),
    ("f_batch", "And Batch sorts your camera roll, and edits a whole week."),
    ("how", "Download. Run. And you are ready to work."),
    ("endcard", "All eight skills, just six hundred ninety-nine rupees. Link in bio."),
]
