# Prompts · Vibe Editing System

Copy, swap the words in `[brackets]`, send one at a time. Replace `videos/[name]/take.mp4` with
your project folder (created by `python scripts/new_video.py [name] --take your-video.mp4`).

## Setup

### Let Claude install the rest

```text
I want you to edit my videos with HyperFrames. Check if this computer has Node.js 22 or newer, FFmpeg, Python 3 and Whisper (faster-whisper on Windows, whisper-cpp on Mac). Install anything that is missing, and ask me before each install. Then run claude plugin marketplace add heygen-com/hyperframes and claude plugin install hyperframes@hyperframes, and run npx hyperframes doctor. Fix whatever it flags and finish with a list of what is installed, with versions.
```

### Test your shot first

Film 5 seconds and drop it in the folder.

```text
Here is a 5-second test clip, test.mp4. Pull a few frames and check the shot before I record the real take: is my face well lit, is the background far enough to cut me out cleanly, and is anything important too close to the edges? Tell me exactly what to fix.
```

## The edit loop

### 1 · First prompt (eyes and ears)

```text
My video is videos/[name]/take.mp4. Transcribe it with Whisper, with a timestamp for every word, and save the words and times to take.words.json. Then use FFmpeg to pull one frame per second and look at the frames. Tell me what I say, when I say it and what is in the shot at each moment. These names must be spelled right: [your name, brand, product].
```

### 2 · Plan first

```text
Before you build anything, write a beat sheet for this edit as a table: start and end time, my exact words, what appears on screen, where the text sits, and the sound. Format: vertical 9:16 for Reels. Keep all text out of the bottom 20% of the screen and away from the right edge, where the app buttons are. Wait for my OK before you build.
```

### 3 · Notes that work

One change per line, always with the time.

```text
At 0:07 the logo covers my face. Move it next to my hand and make it 20% smaller.
From 0:12 to 0:14 the captions go too fast. Show two words at a time.
The zoom at 0:21 lands late. Start it on the word "now".
```

### 4 · Render

```text
Render it.
```

## Everyday edits

### Captions — the one to start with

```text
Add captions word by word, synced to the transcript. Two or three words on screen at a time, bold and white, with the key word of each sentence in [color]. Place them at about 65% of the screen height.
```

### Cut the dead air — after the transcript

```text
Cut every pause longer than 0.3 seconds and every breath, using the word timings. Never cut inside a word, and keep a short beat before each punchline. Tell me the new length.
```

### Punch-in zooms — keep them rare

```text
Punch in 1.2x on the key word of each sentence, hold for two seconds, then ease back out. No more than one zoom every five seconds.
```

### Title card + name tag

```text
Open with a title card in big bold type: "[your hook]". Hold it for two seconds, then cut to me. Add a lower third with my name and [@handle] the first time I speak.
```

### Pop-ups — your image in brand/

```text
When I say "[word]", pop up brand/[image.png] next to me for two seconds with a small bounce. It must never cover my face.
```

### Music + sound effects — your files in music/ and sfx/

```text
Add music/[music.mp3] under my voice at a low volume, and lower it further while I talk. Put a whoosh on every zoom and a pop on every pop-up, using the files in the sfx folder. Never the same sound twice in a row.
```

### Reframe for Reels — for horizontal takes

```text
Reframe this 16:9 video to 9:16 for Reels and keep my face centered the whole time.
```

## Show-off edits

Say these lines on camera, word for word. Claude finds them in the transcript and builds on that word.

| Effect | Say on camera | You need |
| --- | --- | --- |
| Logo on your hand, then at the camera | "Zoom in on my hand and put the [brand] logo right here, in 3D." … "Now throw it straight at the camera!" | Logo (SVG/PNG) in `brand/`. Hold your open hand still for 1 second. |
| Split the scene into layers | "Now split the scene into layers: the wall, me, and the text." … "Now hide my layer." … "Okay, bring me back." | 2-second clean plate of the empty room; distance from the wall. |
| Split-screen explainer | "Put me in a frame on the right, and on the left, show how a reel goes viral." | A clear topic + 2–3 short points right after. |
| Your reels floating in 3D | "Back to full screen. Now float my best reels behind me, in 3D." | Your videos in a folder. |
| An object comes to life | "Last one: grab the camera from my shelf and open it up." … "Now put it back… and take my picture!" | A second clean plate without the object; a pose on "picture". |

Tip: ask Claude for a twist on every effect you add.

## Any style you want

### Show it an example — references in refs/

```text
In the refs folder there are screenshots and a short clip of a motion graphics style I like. Pull frames from the clip and study the layout, the fonts, the colors, how things move and the pacing. Describe the style back to me in five bullet points and wait for my OK. Then build something similar for my video, based on what I say and in my brand colors. Similar, not a copy.
```

### Just name it

```text
Edit this video like a cinematic movie trailer.
Turn this video into a Vox-style documentary explainer.
```

Other famous styles: Apple-style product reveal · Breaking news broadcast · Retro 80s VHS tape.
Mix both: "movie trailer style, with titles like the ones in refs/titles.png".

## Batches

```text
Make three versions of this edit with the same timing and style: captions in English, in Spanish and in Portuguese. Translate the captions only, keep my voice, and render all three.
```

## Fix it fast

| Problem | Say |
| --- | --- |
| Names spelled wrong | Add them to "Names" in `CLAUDE.md`, or list them in the first prompt. |
| Text hidden by app buttons | "Nothing in the bottom 20% of the screen or near the right edge." |
| Effect lands late | "Start the [effect] on the word '[word]'." |
| Looks wrong but Claude says done | "Snapshot the frame at 0:07 and check it yourself." |
| Preview or render fails | Run `python scripts/check_setup.py --doctor`, paste the error to Claude. |
| A change broke something | "Go back to v[n] in versions/." (Claude saves a version before each round.) |
