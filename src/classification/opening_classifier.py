"""
Opening classifier for chess games.
Identifies chess openings from move sequences using ECO codes.
"""

from typing import Dict, List, Any
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class OpeningClassifier:
    """Classifies chess openings from move sequences."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        # Simple opening database - in practice, you'd use a more comprehensive one
        self.opening_database = self._load_opening_database()

    def _load_opening_database(self) -> Dict[str, str]:
        """
        Load a basic opening database with common openings.
        In practice, you'd use a comprehensive database like chess-openings.
        """
        return {
            # King's Pawn Openings
            "e4 e5": "C20-C99 King's Pawn Game",
            "e4 e5 Nf3": "C40 King's Knight Opening",
            "e4 e5 Nf3 Nc6": "C50 Giuoco Piano",
            "e4 e5 Nf3 Nc6 Bc4": "C50 Giuoco Piano",
            "e4 e5 Nf3 Nc6 Bc4 Bc5": "C50 Giuoco Piano",
            "e4 e5 Nf3 Nc6 Bb5": "C60 Ruy Lopez",
            "e4 e5 Nf3 Nc6 Bb5 a6": "C60 Ruy Lopez",
            "e4 e5 Nf3 Nc6 Bb5 a6 Ba4": "C60 Ruy Lopez",
            # Sicilian Defense
            "e4 c5": "B20 Sicilian Defense",
            "e4 c5 Nf3": "B20 Sicilian Defense",
            "e4 c5 Nf3 d6": "B40 Sicilian Defense",
            "e4 c5 Nf3 d6 d4": "B40 Sicilian Defense",
            "e4 c5 Nf3 d6 d4 cxd4": "B40 Sicilian Defense",
            "e4 c5 Nf3 d6 d4 cxd4 Nxd4": "B40 Sicilian Defense",
            # French Defense
            "e4 e6": "C00 French Defense",
            "e4 e6 d4": "C00 French Defense",
            "e4 e6 d4 d5": "C00 French Defense",
            "e4 e6 d4 d5 e5": "C00 French Defense",
            # Caro-Kann Defense
            "e4 c6": "B10 Caro-Kann Defense",
            "e4 c6 d4": "B10 Caro-Kann Defense",
            "e4 c6 d4 d5": "B10 Caro-Kann Defense",
            # Queen's Pawn Openings
            "d4": "D00 Queen's Pawn Game",
            "d4 d5": "D00 Queen's Pawn Game",
            "d4 d5 c4": "D20 Queen's Gambit",
            "d4 d5 c4 dxc4": "D20 Queen's Gambit",
            "d4 d5 c4 e6": "D30 Queen's Gambit Declined",
            "d4 Nf6": "A40 Queen's Pawn Game",
            "d4 Nf6 c4": "A40 Queen's Pawn Game",
            "d4 Nf6 c4 e6": "E00 Indian Game",
            "d4 Nf6 c4 g6": "E60 King's Indian Defense",
            # English Opening
            "c4": "A10 English Opening",
            "c4 e5": "A10 English Opening",
            "c4 Nf6": "A10 English Opening",
            "c4 e6": "A10 English Opening",
        }

    def classify_opening(self, moves: List[str]) -> str:
        """
        Classify opening from a list of moves.

        Args:
            moves: List of moves in UCI format

        Returns:
            Opening name and ECO code
        """
        if not moves:
            return "Unknown Opening"

        # Convert UCI moves to SAN for matching
        try:
            import chess

            board = chess.Board()
            san_moves: List[str] = []

            for move_uci in moves[:10]:  # Limit to first 10 moves
                move = chess.Move.from_uci(move_uci)
                san_move = board.san(move)
                san_moves.append(san_move)
                board.push(move)

                # Check if we have a match
                move_sequence = " ".join(san_moves)
                if move_sequence in self.opening_database:
                    return self.opening_database[move_sequence]

            # If no exact match, try partial matches
            for i in range(len(san_moves) - 1, 0, -1):
                partial_sequence = " ".join(san_moves[:i])
                if partial_sequence in self.opening_database:
                    return self.opening_database[partial_sequence]

            return "Unknown Opening"

        except Exception as e:
            logger.warning(f"Failed to classify opening: {e}")
            return "Unknown Opening"

    def classify_game_openings(
        self, games_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Classify openings for a list of games.

        Args:
            games_data: List of game dictionaries with moves

        Returns:
            List of games with opening classification
        """
        classified_games: List[Dict[str, Any]] = []

        for game_data in games_data:
            moves = game_data.get("moves", [])
            opening = self.classify_opening(moves)
            game_data["opening"] = opening
            classified_games.append(game_data)

        return classified_games

    def get_opening_stats(
        self, games_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate statistics about openings in a dataset.

        Args:
            games_data: List of games with opening classifications

        Returns:
            Dictionary with opening statistics
        """
        opening_counts: Dict[str, int] = defaultdict(int)
        opening_results: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"wins": 0, "losses": 0, "draws": 0}
        )

        for game in games_data:
            opening = game.get("opening", "Unknown")
            result = game.get("result", "*")

            opening_counts[opening] += 1

            if result == "1-0":
                opening_results[opening]["wins"] += 1
            elif result == "0-1":
                opening_results[opening]["losses"] += 1
            elif result == "1/2-1/2":
                opening_results[opening]["draws"] += 1

        # Calculate win rates
        stats: Dict[str, Dict[str, Any]] = {}
        for opening, count in opening_counts.items():
            results = opening_results[opening]
            total = results["wins"] + results["losses"] + results["draws"]

            stats[opening] = {
                "total_games": count,
                "wins": results["wins"],
                "losses": results["losses"],
                "draws": results["draws"],
                "win_rate": results["wins"] / total if total > 0 else 0.0,
                "draw_rate": results["draws"] / total if total > 0 else 0.0,
                "loss_rate": results["losses"] / total if total > 0 else 0.0,
            }

        return stats
