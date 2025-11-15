#!/bin/bash
# Install TUI dependencies for HyprSTT

echo "Installing TUI dependencies for HyprSTT..."
echo ""

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "WARNING: Not in a virtual environment."
    echo "It's recommended to use a virtual environment."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Installing Textual and Rich..."
pip install textual>=0.47.0 rich>=13.7.0

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ TUI dependencies installed successfully!"
    echo ""
    echo "You can now run the TUI with:"
    echo "  ./hyprstt-tui"
    echo ""
    echo "Or install the package and use:"
    echo "  pip install -e ."
    echo "  hyprstt-tui"
else
    echo ""
    echo "✗ Installation failed. Please check the error messages above."
    exit 1
fi
