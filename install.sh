#!/bin/bash

echo "Setting up Chess Opening Recommendation System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/processed
mkdir -p models
mkdir -p logs

# Download Stockfish if not present
if ! command -v stockfish &> /dev/null; then
    echo "Stockfish not found. Please install Stockfish:"
    echo "Ubuntu/Debian: sudo apt-get install stockfish"
    echo "macOS: brew install stockfish"
    echo "Windows: Download from https://stockfishchess.org/download/"
fi

# Update config with Stockfish path
if command -v stockfish &> /dev/null; then
    STOCKFISH_PATH=$(which stockfish)
    echo "Found Stockfish at: $STOCKFISH_PATH"
    # Update config.yaml with the correct path
    sed -i "s|stockfish_path: \".*\"|stockfish_path: \"$STOCKFISH_PATH\"|" config.yaml
fi

echo "Setup complete! Activate the virtual environment with:"
echo "source venv/bin/activate"
echo ""
echo "To run the analysis:"
echo "python src/main.py --pgn-file data/games/your_games.pgn" 