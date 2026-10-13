# Brief: temple-tourist

- **Title:** ARTIST DATE | Playing Tourist in My Own City
- **Vibe:** cozy, nostalgic, cinematic
- **Format:** 16:9 (1920×1080) @ 24 fps, 42.5 s (the footage is landscape 720×404, letterboxed in 9:16 phone files)
- **Voice:** AI (Kokoro `af_heart`, 0.86) reading the user's script, built phrase by phrase (`script.json`, `build_vo.py`);
  replace with the artist's own recording when available. Captions: English, in the bottom cinematic bar.
- **Script edits:** "passed by thousand times" -> "passed by a thousand times"; "30" spoken as "thirty". Otherwise verbatim.
- **Look:** warm nostalgic grade (lifted blacks, warm mids), slow drifts/push-ins, 0.6 s dissolves, ~2.2:1 bars,
  Instrument Serif title and captions.
- **Sound:** voice on top; original soft piano (F major, `../sketchbook-pause/piano.py`) ducked; each shot's own
  temple ambience crossfaded underneath; −14 LUFS.
- **Pipeline:** `prep_shots.py` (picture) -> `scene.py audio` -> `scene.py render` (graphics overlay + mux).
