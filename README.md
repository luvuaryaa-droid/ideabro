# Vibe Editing System · Ideabro Studio

**Let Claude edit your videos.** Claude Code + HyperFrames · Whisper · FFmpeg · no editing app.

Film yourself talking, drop the file in a folder and tell Claude what you want on screen.
Claude listens to every word (Whisper), looks at your frames (FFmpeg), plans the edit, builds it
as code with [HyperFrames](https://github.com/heygen-com/hyperframes) and renders an MP4.
The full guide is in [`docs/vibe-editing-system.md`](docs/vibe-editing-system.md).

```
01 You film → 02 Claude listens → 03 Claude looks → 04 Claude builds → 05 You review, Claude renders
```

## What's in this repo

| Path | What it is |
| --- | --- |
| `CLAUDE.md` | Rules Claude reads every session: the edit loop and your **house style** (names, colors, safe zone). Edit the "House style" section to match your brand. |
| `.claude/settings.json` | Registers the HyperFrames plugin for this folder, so Claude Code offers to install it. |
| `prompts/PROMPTS.md` | Every prompt from the guide, ready to paste. |
| `scripts/check_setup.py` | Checks Node.js, FFmpeg, Python, Whisper, Claude Code (+ `--doctor`). |
| `scripts/new_video.py` | Creates `videos/<name>/` as a HyperFrames project and copies your take in. |
| `scripts/transcribe.py` | Ears: word-by-word transcript → `take.words.json`. |
| `scripts/frames.py` | Eyes: still frames (1 per second, or at given times). |
| `setup/` | One-time install scripts for Mac and Windows. |
| `brand/` `refs/` `music/` `sfx/` | Your logo, style references, music and sound effects. |
| `videos/` | One folder per edit. |

Footage, audio and renders are git-ignored, so they stay on your computer.

## 1 · Install it once (about 15 minutes)

You need: Claude Code (Claude Pro or higher), Node.js 22+, FFmpeg, Python 3 and Whisper.
HyperFrames downloads its own Chrome for rendering.

**Mac** (with [Homebrew](https://brew.sh)):

```bash
bash setup/install-mac.sh
```

**Windows** (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File setup\install-windows.ps1
```

<details><summary>Or by hand</summary>

```bash
# Claude Code
curl -fsSL https://claude.ai/install.sh | bash        # Mac
irm https://claude.ai/install.ps1 | iex               # Windows

# Node.js, FFmpeg, Python
brew install node ffmpeg python                       # Mac
winget install OpenJS.NodeJS.LTS                      # Windows
winget install Gyan.FFmpeg
winget install Python.Python.3.13

# Whisper
python -m pip install -r requirements.txt             # faster-whisper (both)
brew install whisper-cpp                              # Mac: lets HyperFrames transcribe on its own

# HyperFrames plugin for Claude
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```
</details>

Then open a **new terminal** and check:

```bash
python scripts/check_setup.py --doctor
```

Or let Claude do it: open Claude Code in this folder and paste the "Let Claude install the rest"
prompt from `prompts/PROMPTS.md`.

## 2 · Make your first edit

1. Film one take (tripod, light on your face, quiet room, 2 seconds of the empty room at the end).
2. Create the project:
   ```bash
   python scripts/new_video.py my-first-reel --take path/to/your-video.mp4
   ```
3. Start Claude Code in this folder (`claude`) and paste the **First prompt** from
   `prompts/PROMPTS.md`, then **Plan first**, then **Captions** and **Cut the dead air**.
4. Watch the preview in your browser, send notes with times ("At 0:07 ..."), then say **"render it"**.

## Habits

- One change per message, always with the time.
- Say what you want to see, not how to code it.
- Approve the plan before the build. Rough cut first, effects after.
- Ask Claude to save a version before each round of notes.
- If something fails: `python scripts/check_setup.py --doctor` and paste the error to Claude.

---

Adapted and redesigned by Ideabro Studio from "Let Claude Edit Your Videos" by @pauloshimas,
The Creator Stack (2026).
