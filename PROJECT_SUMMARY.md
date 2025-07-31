# Chess Opening Recommendation System - Project Summary

## 🎯 Project Overview

This project implements a personalized chess opening recommendation system that analyzes your games, identifies weaknesses, and suggests specific openings and variations to study. The system combines Maia-2 models, Stockfish evaluation, and machine learning to provide data-driven study recommendations.

## 🏗️ Architecture

The system follows a modular architecture with these core components:

### 1. **PGN Parser** (`src/core/pgn_parser.py`)
- Parses chess games from PGN format
- Extracts moves, positions, and game metadata
- Converts games to structured data for analysis

### 2. **Stockfish Evaluator** (`src/evaluation/stockfish_evaluator.py`)
- Integrates with Stockfish chess engine
- Evaluates positions and moves
- Provides centipawn scores for mistake classification

### 3. **Mistake Classifier** (`src/classification/mistake_classifier.py`)
- Classifies moves as blunders, mistakes, inaccuracies, or good moves
- Uses configurable thresholds based on evaluation changes
- Calculates mistake statistics per opening

### 4. **Opening Classifier** (`src/classification/opening_classifier.py`)
- Identifies chess openings from move sequences
- Uses ECO codes and opening databases
- Groups games by opening for analysis

### 5. **Recommendation Engine** (`src/recommendation/recommendation_engine.py`)
- Generates personalized study recommendations
- Calculates priority scores based on mistake patterns
- Creates comprehensive study plans

## 📊 Analysis Pipeline

```
PNG Files → Parser → Stockfish Evaluation → Mistake Classification → Opening Classification → Recommendations
```

1. **Parse PGN files** containing your chess games
2. **Evaluate positions** using Stockfish engine
3. **Classify mistakes** based on evaluation changes
4. **Identify openings** for each game
5. **Generate recommendations** for study priorities

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd chess-recommender

# Run the installation script
./install.sh

# Activate virtual environment
source venv/bin/activate
```

### Basic Usage
```bash
# Run analysis on your PGN file
python src/main.py --pgn-file data/games/your_games.pgn

# Or use the sample games for testing
python src/main.py --pgn-file data/games/sample_games.pgn
```

### Configuration
Edit `config.yaml` to customize:
- Stockfish engine path
- Evaluation depth and time limits
- Mistake classification thresholds
- Recommendation parameters

## 📈 Output

The system generates:

1. **Detailed Analysis** (`analysis_results.json`)
   - Game statistics
   - Mistake analysis per opening
   - Opening performance metrics

2. **Study Recommendations** (`recommendations.txt`)
   - Prioritized opening list
   - Study focus areas
   - Estimated study time

3. **Study Plan** (included in JSON output)
   - Ranked openings to study
   - Focus areas (tactical, positional, etc.)
   - Time estimates for each opening

## 🎯 Key Features

### Personalized Analysis
- Analyzes your specific games and playing style
- Identifies your weakest openings
- Suggests study priorities based on your mistakes

### Data-Driven Recommendations
- Uses Stockfish evaluation for objective analysis
- Considers mistake frequency and severity
- Provides confidence levels for recommendations

### Comprehensive Study Plans
- Suggests specific openings to study
- Identifies focus areas (tactics, strategy, etc.)
- Estimates study time requirements

## 🔧 Technical Details

### Dependencies
- **python-chess**: Chess game parsing and move generation
- **Stockfish**: Position evaluation engine
- **PyTorch**: Machine learning framework (for future Maia integration)
- **Pandas/NumPy**: Data processing and analysis
- **Matplotlib/Seaborn**: Visualization (future feature)

### Configuration
The system is highly configurable through `config.yaml`:
- Engine settings (depth, time limits)
- Mistake thresholds (blunder, mistake, inaccuracy)
- Analysis parameters (max games, min moves)
- Recommendation settings (top openings, confidence)

## 🚧 Future Enhancements

### Phase 2: Opponent Modeling
- Train Maia models on opponent games
- Simulate games between your model and opponent models
- Analyze opening effectiveness against specific opponents

### Phase 3: Reinforcement Learning
- Implement RL framework for opening selection
- Optimize study recommendations through simulation
- Continuous improvement based on results

### Phase 4: Extended Analysis
- Midgame motif detection
- Endgame classification and study
- Comprehensive study plans including tactics and strategy

## 📝 Example Output

```
🎯 CHESS OPENING STUDY RECOMMENDATIONS
==================================================

1. Sicilian Defense
   Priority Score: 2.45
   Type: Critical Weakness
   Focus: tactical_awareness, calculation
   Confidence: 85.0%
   Moves Analyzed: 150
   Blunder Rate: 18.7%
   Mistake Rate: 25.3%
   Inaccuracy Rate: 32.0%

2. French Defense
   Priority Score: 1.87
   Type: Major Weakness
   Focus: positional_understanding, opening_principles
   Confidence: 72.0%
   Moves Analyzed: 89
   Blunder Rate: 12.4%
   Mistake Rate: 22.5%
   Inaccuracy Rate: 28.1%
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Or run individual tests:
```bash
python -m pytest tests/test_basic.py::test_mistake_classifier
```

## 📚 Usage Examples

### Jupyter Notebook
See `notebooks/example_analysis.ipynb` for interactive analysis and visualization.

### Command Line
```bash
# Basic analysis
python src/main.py --pgn-file games.pgn

# With custom config
python src/main.py --pgn-file games.pgn --config custom_config.yaml

# Verbose logging
python src/main.py --pgn-file games.pgn --log-level DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Stockfish not found**
   - Install Stockfish: `sudo apt-get install stockfish`
   - Update path in `config.yaml`

2. **Missing dependencies**
   - Run: `pip install -r requirements.txt`

3. **Memory issues with large PGN files**
   - Reduce `max_games` in config
   - Process files in smaller batches

### Getting Help

- Check the logs in `chess_analysis.log`
- Run with `--log-level DEBUG` for detailed output
- Review the example notebook for usage patterns

---

**Note**: This is a baseline implementation. The Maia-2 model integration and RL framework are planned for future phases. The current system provides a solid foundation for personalized chess study recommendations based on Stockfish evaluation and mistake analysis. 