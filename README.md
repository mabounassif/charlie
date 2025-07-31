# Chess Opening Recommendation System

A personalized chess study system that analyzes your games, identifies weaknesses, and recommends specific openings and variations to study.

## Overview

This system combines:
- **Maia-2 models** for move prediction and opponent modeling
- **Stockfish engine** for position evaluation
- **Mistake classification** to identify weaknesses
- **Opening analysis** to correlate mistakes with specific openings
- **Recommendation engine** to suggest study priorities

## Architecture

```
PNG Files (Your Games)
        │
┌───────▼────────┐
│   PGN Parser   │ ← parses games to move list
└───────┬────────┘
        ▼
   Position-by-position analysis
        │
┌────────▼────────┐
│  Maia Model Eval │ ← predicts your move
└────────┬────────┘
        ▼
┌────────▼────────┐
│ Stockfish Eval  │ ← evaluates positions
└────────┬────────┘
        ▼
┌────────▼────────┐
│ Mistake Tagger  │ ← labels move quality
└────────┬────────┘
        ▼
┌────────▼────────┐
│  ECO Classifier │ ← tags openings
└────────┬────────┘
        ▼
┌────────▼────────┐
│ Recommendation   │ ← suggests study priorities
└─────────────────┘
```

## Project Structure

```
chess-recommender/
├── data/                   # PGN files and processed data
├── models/                 # Maia models and checkpoints
├── src/
│   ├── core/              # Core analysis components
│   ├── evaluation/        # Stockfish integration
│   ├── classification/    # Mistake and opening classification
│   ├── recommendation/    # Recommendation engine
│   └── visualization/     # Charts and heatmaps
├── notebooks/             # Jupyter notebooks for exploration
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
└── config.yaml           # Configuration settings
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download Stockfish and update the path in `config.yaml`

3. Place your PGN files in `data/games/`

4. Run the analysis:
```bash
python src/main.py --pgn-file data/games/your_games.pgn
```

## Development Phases

### Phase 1: Baseline System (Weeks 1-3)
- [x] Project structure
- [ ] PGN parser and game analysis
- [ ] Maia model integration
- [ ] Stockfish evaluation
- [ ] Mistake classification
- [ ] Opening tagging
- [ ] Basic recommendations

### Phase 2: Opponent Modeling (Weeks 4-6)
- [ ] Opponent Maia model training
- [ ] Game simulation framework
- [ ] Opening effectiveness analysis

### Phase 3: RL Framework (Stretch Goal)
- [ ] Policy optimization for opening selection
- [ ] Automated study plan generation

### Phase 4: Extended Analysis
- [ ] Midgame motif detection
- [ ] Endgame classification
- [ ] Comprehensive study plans

## Configuration

Edit `config.yaml` to customize:
- Stockfish engine path
- Maia model paths
- Evaluation depth
- Mistake classification thresholds
- Output formats

## License

MIT License 