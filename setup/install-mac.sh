#!/usr/bin/env bash
# One-time install for macOS. Needs Homebrew (https://brew.sh).
# Run from the repo root:  bash setup/install-mac.sh
set -euo pipefail

if ! command -v brew >/dev/null; then
  echo "Homebrew is missing. Install it from https://brew.sh, then re-run this script." >&2
  exit 1
fi

echo "==> Node.js, FFmpeg, Python, whisper-cpp"
brew install node ffmpeg python whisper-cpp

echo "==> faster-whisper (used by scripts/transcribe.py)"
python3 -m pip install --user -r requirements.txt || \
  echo "pip install failed; HyperFrames can still transcribe with whisper-cpp (npx hyperframes transcribe)."

if ! command -v claude >/dev/null; then
  echo "==> Claude Code"
  curl -fsSL https://claude.ai/install.sh | bash
fi

echo "==> HyperFrames plugin for Claude Code"
claude plugin marketplace add heygen-com/hyperframes || true
claude plugin install hyperframes@hyperframes || true

echo "==> Chrome for rendering"
npx --yes hyperframes@0.8.149 browser ensure || true

echo
python3 scripts/check_setup.py --doctor || true
echo
echo "Done. Open a NEW terminal so your computer finds the new tools."
