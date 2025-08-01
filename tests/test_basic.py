"""
Basic tests for the chess opening recommendation system.
"""

from pathlib import Path

import pytest
import yaml

# Import our components
from src.core.pgn_parser import PGNParser, Game, GameMove
from src.classification.mistake_classifier import MistakeClassifier
from src.recommendation.recommendation_engine import RecommendationEngine


def load_test_config():
    """Load test configuration."""
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        # Default test config
        return {
            'analysis': {
                'min_moves': 5,
                'max_moves': 50,
                'max_games': 10
            },
            'mistake_thresholds': {
                'blunder': -200,
                'mistake': -100,
                'inaccuracy': -50,
                'ok': 0
            },
            'recommendation': {
                'top_openings': 5,
                'min_games_per_opening': 1,
                'confidence_threshold': 0.7
            }
        }


def test_pgn_parser():
    """Test PGN parser functionality."""
    config = load_test_config()
    parser = PGNParser(config)

    # Test with empty games list
    games = []
    df = parser.games_to_dataframe(games)
    assert len(df) == 0


def test_mistake_classifier():
    """Test mistake classifier functionality."""
    config = load_test_config()
    classifier = MistakeClassifier(config)

    # Test move classification
    mistake_type = classifier.classify_move(100, 50)  # -50 centipawns
    assert mistake_type == 'inaccuracy'

    mistake_type = classifier.classify_move(100, -50)  # -150 centipawns
    assert mistake_type == 'mistake'

    mistake_type = classifier.classify_move(100, -250)  # -350 centipawns
    assert mistake_type == 'blunder'


def test_recommendation_engine():
    """Test recommendation engine functionality."""
    config = load_test_config()
    engine = RecommendationEngine(config)

    # Test with empty stats
    recommendations = engine.generate_recommendations({})
    assert len(recommendations) == 0

    # Test with sample stats
    sample_stats = {
        'Sicilian Defense': {
            'total_moves': 50,
            'blunder_rate': 0.1,
            'mistake_rate': 0.2,
            'inaccuracy_rate': 0.3,
            'good_move_rate': 0.4
        }
    }

    recommendations = engine.generate_recommendations(sample_stats)
    assert len(recommendations) > 0


def test_game_dataclass():
    """Test Game dataclass functionality."""
    game = Game(
        game_id="test_game",
        white_player="Player1",
        black_player="Player2",
        result="1-0"
    )

    assert game.game_id == "test_game"
    assert game.white_player == "Player1"
    assert game.black_player == "Player2"
    assert game.result == "1-0"
    assert len(game.moves) == 0


def test_game_move_dataclass():
    """Test GameMove dataclass functionality."""
    move = GameMove(
        game_id="test_game",
        move_number=1,
        player="white",
        fen_before=(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        ),
        fen_after=(
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        ),
        move_uci="e2e4",
        move_san="e4"
    )

    assert move.game_id == "test_game"
    assert move.move_number == 1
    assert move.player == "white"
    assert move.move_uci == "e2e4"
    assert move.move_san == "e4"


if __name__ == "__main__":
    pytest.main([__file__])
