#!/bin/bash
# Bash transcribe script for Russian Whisper
# Usage: transcribe <аудиофайл | папка_аудио> [файл_результата | папка_результата] [--segments] [--dry-run]
# Examples:
#   transcribe speech.mp3 transcript.txt
#   transcribe /path/to/audio/files
#   transcribe /path/to/audio/files /path/to/output
#   transcribe /path/to/audio/files /path/to/output --segments

# Find the actual location of this script, even when symlinked
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

# Configuration - find project directory even when script is symlinked
PROJECT_DIR="$SCRIPT_DIR"
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    # If we're symlinked from another directory, try to find the project dir
    PROJECT_DIR=$(dirname "$SCRIPT_DIR")
    if [ ! -d "$PROJECT_DIR/.venv" ]; then
        # One more try - maybe we're in a bin subdirectory?
        PROJECT_DIR=$(dirname "$PROJECT_DIR")
    fi
fi

ENV_DIR="$PROJECT_DIR/.venv"
APP_SCRIPT="$PROJECT_DIR/transcribe.py"

# Check if virtual environment exists
if [ ! -f "$ENV_DIR/bin/python" ]; then
    echo "Virtual environment not found. Please run setup.sh in the project directory first."
    exit 1
fi

# Use Python directly from the virtual environment without activating it
"$ENV_DIR/bin/python" "$APP_SCRIPT" "$@"

# Exit with the same exit code as the Python script
exit $?
