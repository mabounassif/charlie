"""
Stockfish evaluation component for chess position analysis.
Handles position evaluation using the Stockfish engine.
"""

import chess
import chess.engine
from typing import Dict, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StockfishEvaluator:
    """Evaluates chess positions using Stockfish engine."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.stockfish_path = config['engine']['stockfish_path']
        self.evaluation_depth = config['engine']['evaluation_depth']
        self.time_limit = config['engine']['time_limit']
        self.engine = None
        
        # Verify Stockfish exists
        if not Path(self.stockfish_path).exists():
            raise FileNotFoundError(f"Stockfish not found at {self.stockfish_path}")
    
    def __enter__(self):
        """Context manager entry."""
        self._start_engine()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._stop_engine()
    
    def _start_engine(self):
        """Start the Stockfish engine."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            logger.info("Stockfish engine started successfully")
        except Exception as e:
            logger.error(f"Failed to start Stockfish engine: {e}")
            raise
    
    def _stop_engine(self):
        """Stop the Stockfish engine."""
        if self.engine:
            self.engine.quit()
            logger.info("Stockfish engine stopped")
    
    def evaluate_position(self, board: chess.Board) -> Optional[float]:
        """
        Evaluate a chess position using Stockfish.
        
        Args:
            board: Chess board position to evaluate
            
        Returns:
            Evaluation score in centipawns (positive = white advantage)
        """
        if not self.engine:
            self._start_engine()
        
        try:
            result = self.engine.analyse(
                board, 
                chess.engine.Limit(depth=self.evaluation_depth, time=self.time_limit)
            )
            
            score = result["score"].relative.score(mate_score=10000)
            return score
            
        except Exception as e:
            logger.warning(f"Failed to evaluate position: {e}")
            return None
    
    def evaluate_move(self, board: chess.Board, move: chess.Move) -> Tuple[Optional[float], Optional[float]]:
        """
        Evaluate a position before and after a move.
        
        Args:
            board: Chess board before the move
            move: Move to evaluate
            
        Returns:
            Tuple of (evaluation_before, evaluation_after) in centipawns
        """
        # Evaluate position before move
        eval_before = self.evaluate_position(board)
        
        # Make the move
        board.push(move)
        eval_after = self.evaluate_position(board)
        
        # Undo the move
        board.pop()
        
        return eval_before, eval_after
    
    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Get the best move for a position according to Stockfish.
        
        Args:
            board: Chess board position
            
        Returns:
            Best move as chess.Move object
        """
        if not self.engine:
            self._start_engine()
        
        try:
            result = self.engine.play(
                board, 
                chess.engine.Limit(depth=self.evaluation_depth, time=self.time_limit)
            )
            return result.move
            
        except Exception as e:
            logger.warning(f"Failed to get best move: {e}")
            return None
    
    def evaluate_game_moves(self, moves_data: list) -> list:
        """
        Evaluate all moves in a game dataset.
        
        Args:
            moves_data: List of move dictionaries with 'fen_before' and 'move_uci'
            
        Returns:
            List of moves with added evaluation data
        """
        evaluated_moves = []
        
        for move_data in moves_data:
            try:
                board = chess.Board(move_data['fen_before'])
                move = chess.Move.from_uci(move_data['move_uci'])
                
                eval_before, eval_after = self.evaluate_move(board, move)
                
                # Add evaluation data to move
                move_data['evaluation_before'] = eval_before
                move_data['evaluation_after'] = eval_after
                
                evaluated_moves.append(move_data)
                
            except Exception as e:
                logger.warning(f"Failed to evaluate move {move_data.get('move_uci', 'unknown')}: {e}")
                move_data['evaluation_before'] = None
                move_data['evaluation_after'] = None
                evaluated_moves.append(move_data)
        
        return evaluated_moves
    
    def get_engine_info(self) -> Dict:
        """Get information about the Stockfish engine."""
        if not self.engine:
            return {"status": "not_started"}
        
        try:
            # Get engine info
            info = {}
            if hasattr(self.engine, 'id'):
                info['name'] = self.engine.id.get('name', 'Unknown')
                info['author'] = self.engine.id.get('author', 'Unknown')
            
            info['depth'] = self.evaluation_depth
            info['time_limit'] = self.time_limit
            
            return info
            
        except Exception as e:
            logger.warning(f"Failed to get engine info: {e}")
            return {"status": "error", "error": str(e)} 