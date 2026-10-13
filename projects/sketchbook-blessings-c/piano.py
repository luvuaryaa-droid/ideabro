"""piano: original soft solo piano for the sketchbook reel (no drums, no samples).

    python3 piano.py [seconds] [seed] [F|D|G|C|A]   -> work/piano.wav

Additive piano tone (slightly stretched partials, two detuned strings, hammer softness), slow broken chords
in F major (Fmaj7 - Dm9 - Bbmaj7 - Csus/F), a sustained left hand, and a long soft room reverb.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.signal import fftconvolve

SR = 48000


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano_note(m, dur, vel=0.5, seed=0):
    rng = np.random.default_rng(seed)
    f0 = midi_hz(m)
    n = int(dur * SR)
    t = np.arange(n) / SR
    B = 0.00035                                      # string stiffness -> slightly sharp upper partials
    x = np.zeros(n)
    for k in range(1, 11):
        fk = k * f0 * np.sqrt(1 + B * k * k)
        if fk > SR / 2.2:
            break
        amp = (vel ** (0.6 + 0.12 * k)) / k ** 1.25    # soft touch = fewer bright partials
        decay = 0.55 + 0.35 * k + f0 / 900
        for det in (-0.7, 0.7):                       # two strings, a hair apart (cents)
            ff = fk * 2 ** (det / 1200)
            x += amp * np.sin(2 * np.pi * ff * t + rng.uniform(0, 6.28)) * (
                0.7 * np.exp(-decay * t) + 0.3 * np.exp(-decay * 0.25 * t))
    attack = np.clip(t / 0.006, 0, 1)
    release = np.clip((dur - t) / 0.25, 0, 1)
    return (x * attack * release * 0.18).astype(np.float32)


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    j = min(len(buf), i + len(clip))
    if i < len(buf):
        buf[i:j] += clip[: j - i] * gain


def reverb(x, seconds=2.6, mix=0.32, seed=4):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = []
    for ch in range(2):
        ir = rng.normal(0, 1, n) * np.exp(-t * 3.2 / seconds * 2.2)
        ir[: int(0.012 * SR)] = 0                        # pre-delay
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = fftconvolve(x, ir)[: len(x)]
        out.append((1 - mix) * x + mix * wet * 0.9)
    return np.stack(out, 1)


def main():
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 12.5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    rng = np.random.default_rng(seed)
    key = sys.argv[3] if len(sys.argv) > 3 else "F"
    if key == "D":                                        # v2 piece: D major, slower and sparser, with a melody
        beat = 60 / 60
        prog = [(38, [62, 66, 69, 73, 74]),               # Dmaj7
                (35, [59, 62, 66, 69, 71]),               # Bm7
                (31, [59, 62, 66, 67, 71]),               # Gmaj7
                (33, [57, 62, 64, 69, 76])]               # Asus
        melody = [(0.0, 78), (2.0, 76), (4.0, 74), (5.5, 73), (8.0, 71), (10.0, 74), (11.0, 73)]
    elif key == "A":                                      # journal piece: A major, 56 BPM, warm low register, music-box top
        beat = 60 / 56
        prog = [(33, [57, 61, 64, 68, 69]),               # Amaj7
                (30, [54, 57, 61, 64, 66]),               # F#m7
                (26, [54, 57, 62, 64, 66]),               # Dmaj9
                (28, [56, 59, 62, 64, 71])]               # E6sus
        melody = [(0.0, 76), (2.0, 73), (3.0, 81), (5.0, 78), (6.0, 76), (8.0, 73), (9.0, 76), (11.0, 81)]
    elif key == "C":                                      # second blessings piece: C major, 58 BPM, music-box high melody
        beat = 60 / 58
        prog = [(36, [60, 64, 67, 71, 72]),               # Cmaj7
                (33, [57, 60, 64, 67, 69]),               # Am7
                (29, [57, 60, 64, 65, 69]),               # Fmaj7
                (31, [59, 62, 65, 67, 74])]               # G7sus feel
        melody = [(0.0, 79), (1.0, 76), (2.0, 84), (4.0, 81), (5.0, 79), (6.0, 77), (8.0, 76), (9.5, 79), (11.0, 84)]
    elif key == "G":                                      # blessings piece: G major, 63 BPM, rising hopeful melody
        beat = 60 / 63
        prog = [(43, [62, 66, 67, 71, 74]),               # Gmaj7
                (40, [59, 62, 64, 67, 71]),               # Em7
                (36, [60, 64, 67, 71, 72]),               # Cmaj7
                (38, [62, 66, 69, 72, 74])]               # D (lifting home)
        melody = [(0.0, 74), (1.5, 76), (3.0, 78), (4.0, 79), (6.0, 76), (8.0, 74), (9.0, 76), (10.5, 79), (12.0, 81)]
    else:
        beat = 60 / 66                                    # v1 piece: F major, 66 BPM
        prog = [(41, [60, 64, 65, 69, 72]),               # Fmaj7
                (38, [57, 60, 62, 65, 69]),               # Dm9
                (34, [58, 62, 65, 69, 70]),               # Bbmaj7
                (41, [60, 65, 67, 72, 77])]               # Csus over F (resolving home)
        melody = []
    n = int((seconds + 3.0) * SR)
    buf = np.zeros(n, np.float32)
    bar = 4 * beat
    t0 = 0.25
    nbars = int(np.ceil((seconds - t0) / bar))           # keep playing the progression for the whole piece
    for b in range(nbars):
        bass, chord = prog[b % len(prog)]
        tb = t0 + b * bar
        if tb > seconds:
            break
        place(buf, piano_note(bass, 4.5, 0.42, seed + b), tb, 0.9)
        place(buf, piano_note(bass + 12, 4.0, 0.3, seed + 10 + b), tb + 0.02, 0.5)
        pattern = [0, 2, 3, 4, 3, 2, 1, 2] if b % 2 == 0 else [0, 1, 3, 4, 2, 3, 1, 4]
        step = beat / 2
        if melody:                                        # sparser: quarter notes, fewer tones
            pattern, step = [0, 1, 2, 3], beat
        for i, idx in enumerate(pattern):                 # gentle broken chord, humanised
            tt = tb + i * step + rng.normal(0, 0.012)
            vel = 0.30 + 0.08 * (i % 4 == 0) + rng.normal(0, 0.02)
            place(buf, piano_note(chord[idx], 2.6, max(0.18, vel), seed + 100 + b * 8 + i), tt, 0.75)
    for mt, mn in melody:                                  # a quiet singing line on top
        tt = t0 + mt * beat + rng.normal(0, 0.01)
        if tt < seconds - 0.8:
            place(buf, piano_note(mn, 3.2, 0.38, 500 + mn), tt, 0.85)
    end = t0 + max(nbars, 4) * bar                         # final soft high note to close (4-bar pieces unchanged)
    if end < seconds + 1:
        place(buf, piano_note(84, 3.0, 0.25, 999), min(end, seconds - 1.5), 0.5)
    x = reverb(buf.astype(np.float64))
    x = x[: int(seconds * SR)]
    fade = int(1.4 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    x /= np.max(np.abs(x)) + 1e-9
    x *= 0.6
    Path("work").mkdir(exist_ok=True)
    import soundfile as sf
    sf.write("work/piano.wav", x.astype(np.float32), SR)
    print(f"piano -> work/piano.wav ({seconds:.1f}s)")


if __name__ == "__main__":
    main()
