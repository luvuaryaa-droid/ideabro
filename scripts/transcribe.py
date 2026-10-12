#!/usr/bin/env python3
"""Ears: transcribe a video with faster-whisper, one timestamp per word.

Usage:
    python scripts/transcribe.py videos/my-reel/take.mp4
    python scripts/transcribe.py take.mp4 --model small --language en --names "Ideabro,Claude"

Writes <video>.words.json next to the video:
    {"source": ..., "language": ..., "duration": ..., "names": [...],
     "words": [{"start": 5.32, "end": 5.74, "word": "zoom"}, ...],
     "segments": [{"start": ..., "end": ..., "text": ...}, ...]}

Also writes <video>.words.txt in the "4.68s -> 5.12s  First," format that is easy
to read. Names passed with --names are stored in the JSON so Claude can fix their
spelling in the transcript and captions (Whisper spells names the way they sound).
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path, help="video or audio file")
    parser.add_argument("--model", default="small", help="tiny, base, small, medium, large-v3 (default: small)")
    parser.add_argument("--language", default=None, help="language code, e.g. en, es, pt (default: auto-detect)")
    parser.add_argument("--names", default="", help="comma-separated names/brands that must be spelled right")
    parser.add_argument("--out", type=Path, default=None, help="output JSON path (default: <video>.words.json)")
    args = parser.parse_args()

    if not args.video.exists():
        sys.exit(f"File not found: {args.video}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper is not installed. Run: python -m pip install -r requirements.txt")

    names = [n.strip() for n in args.names.split(",") if n.strip()]
    out = args.out or args.video.with_suffix(".words.json")

    print(f"Loading Whisper model '{args.model}' (downloads on first use)...", file=sys.stderr)
    model = WhisperModel(args.model, device="auto", compute_type="auto")
    segments, info = model.transcribe(
        str(args.video),
        language=args.language,
        word_timestamps=True,
        vad_filter=False,  # keep real pause lengths so dead air can be cut precisely
        initial_prompt=", ".join(names) if names else None,  # nudges spelling of names
    )

    words, segs = [], []
    for seg in segments:
        segs.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()})
        for w in seg.words or []:
            words.append({"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word.strip(),
                          "probability": round(w.probability, 3)})
            print(f"{w.start:6.2f}s -> {w.end:6.2f}s  {w.word.strip()}", file=sys.stderr)

    data = {
        "source": args.video.name,
        "language": info.language,
        "duration": round(info.duration, 2),
        "names": names,
        "words": words,
        "segments": segs,
    }
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    out.with_suffix(".txt").write_text(
        "\n".join(f"{w['start']:.2f}s -> {w['end']:.2f}s  {w['word']}" for w in words) + "\n", encoding="utf-8"
    )
    print(f"Saved {len(words)} words to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
