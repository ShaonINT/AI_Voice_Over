#!/usr/bin/env bash
# Voice Clone Studio — one-time setup script (macOS Apple Silicon)
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "==> Voice Clone Studio setup"
echo "    Project directory: $PROJECT_DIR"
echo ""

# 1. Check / install Homebrew
if ! command -v brew >/dev/null 2>&1; then
    echo "==> Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Make brew available in this script's PATH
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "==> Homebrew already installed."
fi

# 2. Install system deps: ffmpeg + python 3.11
echo "==> Installing ffmpeg and python@3.11 (skips if already installed)..."
brew install ffmpeg python@3.11 || true

PYTHON_BIN="$(brew --prefix)/opt/python@3.11/bin/python3.11"
if [ ! -x "$PYTHON_BIN" ]; then
    # Fallback if brew layout differs
    PYTHON_BIN="$(which python3.11 || true)"
fi
if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
    echo "ERROR: python3.11 not found. Try: brew install python@3.11"
    exit 1
fi
echo "    Using Python at: $PYTHON_BIN"

# 3. Create virtual env
if [ ! -d ".venv" ]; then
    echo "==> Creating Python virtual environment in .venv/"
    "$PYTHON_BIN" -m venv .venv
fi

# 4. Activate and install requirements
echo "==> Installing Python packages (this takes a few minutes)..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Make folders
mkdir -p samples output

echo ""
echo "==> Setup complete."
echo ""
echo "Next steps:"
echo "  1. Record a voice sample (see VOICE_SAMPLES_GUIDE.md), drop into samples/"
echo "  2. Run:   bash run.sh"
echo "  3. The first launch will download ~2 GB of model weights."
