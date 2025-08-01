"""
Mistake classifier for chess moves.
Classifies moves as blunders, mistakes, inaccuracies, or good moves.
"""

from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)


class MistakeClassifier:
    """Classifies chess moves based on evaluation changes."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.thresholds = config["mistake_thresholds"]

        # Validate thresholds
        if not all(
            key in self.thresholds for key in [
                "blunder", "mistake", "inaccuracy", "ok"
            ]
        ):
            raise ValueError("Missing required mistake thresholds in config")

    def classify_move(
        self, eval_before: Optional[float], eval_after: Optional[float]
    ) -> str:
        """
        Classify a move based on evaluation change.

        Args:
            eval_before: Evaluation before the move (centipawns)
            eval_after: Evaluation after the move (centipawns)

        Returns:
            Classification: 'blunder', 'mistake', 'inaccuracy', or 'ok'
        """
        if eval_before is None or eval_after is None:
            return "unknown"

        # Calculate evaluation change
        eval_change = eval_after - eval_before

        # Classify based on thresholds
        if eval_change <= self.thresholds["blunder"]:
            return "blunder"
        elif eval_change <= self.thresholds["mistake"]:
            return "mistake"
        elif eval_change <= self.thresholds["inaccuracy"]:
            return "inaccuracy"
        else:
            return "ok"

    def classify_moves_batch(
        self, moves_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Classify a batch of moves.

        Args:
            moves_data: List of move dictionaries with evaluation data

        Returns:
            List of moves with added mistake_type field
        """
        classified_moves: List[Dict[str, Any]] = []

        for move_data in moves_data:
            eval_before = move_data.get("evaluation_before")
            eval_after = move_data.get("evaluation_after")

            mistake_type = self.classify_move(eval_before, eval_after)
            move_data["mistake_type"] = mistake_type

            classified_moves.append(move_data)

        return classified_moves

    def get_mistake_stats(
        self, moves_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics about mistakes in a dataset.

        Args:
            moves_data: List of classified moves

        Returns:
            Dictionary with mistake statistics
        """
        stats: Dict[str, Any] = {
            "total_moves": len(moves_data),
            "blunders": 0,
            "mistakes": 0,
            "inaccuracies": 0,
            "good_moves": 0,
            "unknown": 0,
        }

        for move in moves_data:
            mistake_type = move.get("mistake_type", "unknown")
            if mistake_type in stats:
                stats[mistake_type] += 1

        # Calculate percentages
        total = stats["total_moves"]
        if total > 0:
            stats["blunder_rate"] = stats["blunders"] / total
            stats["mistake_rate"] = stats["mistakes"] / total
            stats["inaccuracy_rate"] = stats["inaccuracies"] / total
            stats["good_move_rate"] = stats["good_moves"] / total
        else:
            stats["blunder_rate"] = 0.0
            stats["mistake_rate"] = 0.0
            stats["inaccuracy_rate"] = 0.0
            stats["good_move_rate"] = 0.0

        return stats

    def get_mistake_by_opening(
        self, moves_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate mistake statistics grouped by opening.

        Args:
            moves_data: List of classified moves with opening information

        Returns:
            Dictionary with mistake stats per opening
        """
        opening_stats: Dict[str, Dict[str, Any]] = {}

        for move in moves_data:
            opening = move.get("opening", "Unknown")
            mistake_type = move.get("mistake_type", "unknown")

            if opening not in opening_stats:
                opening_stats[opening] = {
                    "total_moves": 0,
                    "blunders": 0,
                    "mistakes": 0,
                    "inaccuracies": 0,
                    "good_moves": 0,
                    "unknown": 0,
                }

            opening_stats[opening]["total_moves"] += 1
            if mistake_type in opening_stats[opening]:
                opening_stats[opening][mistake_type] += 1

        # Calculate rates for each opening
        for opening, stats in opening_stats.items():
            total = stats["total_moves"]
            if total > 0:
                stats["blunder_rate"] = stats["blunders"] / total
                stats["mistake_rate"] = stats["mistakes"] / total
                stats["inaccuracy_rate"] = stats["inaccuracies"] / total
                stats["good_move_rate"] = stats["good_moves"] / total
            else:
                stats["blunder_rate"] = 0.0
                stats["mistake_rate"] = 0.0
                stats["inaccuracy_rate"] = 0.0
                stats["good_move_rate"] = 0.0

        return opening_stats
