# Brief: temple-tourist

- **Title:** ARTIST DATE | Playing Tourist in My Own City
- **Vibe:** cozy, nostalgic, cinematic
- **Format:** 16:9 (1920×1080) @ 24 fps, 77 s (v2: full script) (the footage is landscape 720×404, letterboxed in 9:16 phone files)
- **Voice:** none (v2, user: "keep the original sound, no voice over"). The script is shown as 15 serif text cards.
  The AI read in `build_vo.py` is only used to pace the cards and cuts (work/vo.json); it is not in the mix.
- **Script edits:** "passed by thousand times" -> "passed by a thousand times"; "30" spoken as "thirty". Otherwise verbatim.
- **Look:** warm nostalgic grade (lifted blacks, warm mids), slow drifts/push-ins, 0.6 s dissolves, ~2.2:1 bars,
  Instrument Serif title and captions.
- **Sound:** only the clips' own recorded sound, crossfaded shot to shot, cleaned (70 Hz–11 kHz), −16 LUFS
  (quiet ambience, not pushed into hiss). No music.
- **Pipeline:** `prep_shots.py` (picture) -> `scene.py audio` -> `scene.py render` (graphics overlay + mux).

- **Must keep:** shots of the artist sitting on the lawn and walking towards camera (used twice each).
