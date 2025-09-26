#!/bin/bash
# Development run script for HyprSTT

# Change to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Make sure we're in the right directory
export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

# Run the application in debug mode
python -m src.main