#!/usr/bin/env bash
# Voice Clone Studio — launcher
set -e
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run 'bash setup.sh' first."
    exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Launching Voice Clone Studio at http://127.0.0.1:7860"
echo "    (Ctrl+C in this window to stop the server when you're done)"
python app.py
