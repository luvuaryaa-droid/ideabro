#!/bin/bash
# Cloud sessions start from a fresh container: reinstall the Vibe Editing toolkit.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

if ! ldconfig -p | grep -q libEGL.so.1; then
  (apt-get install -y -q libegl1 libgl1 >/dev/null 2>&1 || \
   (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libgl1 >/dev/null 2>&1)) || \
   echo "warning: could not install libegl1/libgl1 (needed by skia-python)" >&2
fi

python3 -m pip install -q -r "$CLAUDE_PROJECT_DIR/requirements.txt" 2>&1 | grep -vi "warning" || true
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/vibe-vfx/scripts/doctor.py" --kit all | tail -n 3
