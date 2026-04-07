#!/bin/bash
set -e

PROJECT_DIR="$HOME/botlarim"
cd "$PROJECT_DIR"

# Optional: activate virtualenv if present
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
  source "$PROJECT_DIR/.venv/bin/activate"
fi

exec python -u bot_python.py
