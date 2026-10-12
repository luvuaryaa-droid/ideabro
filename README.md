# Vibe Editing System · Ideabro Studio

**Direct the vibe. Let AI do the keyframes.**

Claude Code makes your videos in code: motion graphics, VFX on real footage, AI-footage films, handmade-style
animation, sound design, and hundreds of personalised videos from a spreadsheet. You describe what you want,
approve a plan and a few stills, and Claude renders the MP4.

## The six skills

Claude picks the right one from what you ask (rules in `CLAUDE.md`). They live in `.claude/skills/`.

| Skill | Makes |
|---|---|
| `vibe-motion-graphics` | showreels, explainers, kinetic type, logo reveals, animated charts, transparent lower-third / title packs, quote posts, loops |
| `vibe-bulk-videos` | one template → many videos: CSV personalisation, every format, every language, content series, ad variants |
| `vibe-audio-videos` | original music & SFX, AI voiceover (incl. Hindi), voice clean-up, audiograms, visualisers, beat-synced edits |
| `vibe-vfx` | background removal, text behind you, layer splits, tracking, particles, cinematic grade, slow-mo, "say it and it happens" |
| `vibe-ai-footage` | Veo / Sora / Kling / Runway clips → a film that doesn't look AI; faceless YouTube / Shorts |
| `vibe-stylised-animation` | claymation, crayon, paper-cut, whiteboard, mascots, kids' stories, generative art |

Talking-head reels can also be edited the HyperFrames way: see [`docs/vibe-editing-system.md`](docs/vibe-editing-system.md)
and `prompts/PROMPTS.md`.

Everything is generated locally: music and sound effects are synthesised by `audio_kit`, voices come from Kokoro,
fonts from Google Fonts (OFL). No stock assets, no Content ID claims.

## Install once

You need **Python 3.9+**, **FFmpeg**, **Node.js 22+** (only for HyperFrames / WebGL scenes) and **Claude Code**.

```bash
# Mac
bash setup/install-mac.sh
# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File setup\install-windows.ps1
```

Then install the toolkit and check it:

```bash
python3 -m pip install -r requirements.txt          # Linux also: sudo apt install libegl1 libgl1
python3 .claude/skills/vibe-vfx/scripts/doctor.py --kit all
```

The first AI voiceover downloads the Kokoro model (~330 MB); the first cutout downloads a matte model;
the first transcription downloads a Whisper model. In Claude Code cloud sessions `.claude/hooks/session-start.sh`
reinstalls everything automatically.

## Make a video

1. Start Claude Code in this folder (`claude`) and say what you want, e.g.
   *"Make a 20-second 9:16 logo reveal for Ideabro with a hype soundtrack."*
2. Claude creates `projects/<name>/` and fills `brief.md` with you. Drop footage, logos and data into `raw/`.
3. Approve the beat table, then the stills (style frames), then a fast draft.
4. Say **"render it"**. Deliverables land in `projects/<name>/out/`, exported per platform.

By hand, the same steps are:

```bash
python3 .claude/skills/vibe-motion-graphics/scripts/new_project.py projects/my-reel --kind motion --format 9:16 --duration 20
cd projects/my-reel
python3 scene.py stills      # check frames
python3 scene.py audio       # music + SFX
python3 scene.py draft       # half-res preview
python3 scene.py render      # final
python3 vibe/export.py out/my-reel.mp4 --preset reels,youtube
```

## Repo layout

| Path | What it is |
|---|---|
| `CLAUDE.md` | Studio rules: skill routing, the Vibe Loop, Ideabro house style |
| `.claude/skills/` | The six Vibe Editing skills (each with `scripts/`, `reference/`, `templates/`) |
| `.claude/hooks/session-start.sh` | Reinstalls the toolkit in cloud sessions |
| `projects/` | One folder per video (footage, work files and renders stay out of git) |
| `docs/`, `prompts/`, `scripts/`, `videos/` | The HyperFrames talking-head workflow from the original guide |
| `brand/`, `refs/`, `music/`, `sfx/` | Shared logos, style references and audio you own |

## Habits

- Approve the plan before the build, and stills before the render.
- One change per message, with the time ("at 0:07").
- Say what you want to see, not how to code it.
- Personal data (CSVs for bulk videos) never gets committed.

---

Adapted and redesigned by Ideabro Studio from "Let Claude Edit Your Videos" by @pauloshimas,
The Creator Stack (2026).
