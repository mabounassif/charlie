"""
PGN Parser for chess game analysis.
Handles parsing of PGN files and extraction of game data.
"""

import chess.pgn
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class GameMove:
    """Represents a single move in a game with context."""
    game_id: str
    move_number: int
    player: str  # 'white' or 'black'
    fen_before: str
    fen_after: str
    move_uci: str
    move_san: str
    evaluation_before: Optional[float] = None
    evaluation_after: Optional[float] = None
    mistake_type: Optional[str] = None


@dataclass
class Game:
    """Represents a complete chess game."""
    game_id: str
    white_player: str
    black_player: str
    result: str
    date: Optional[str] = None
    event: Optional[str] = None
    site: Optional[str] = None
    moves: List[GameMove] = field(default_factory=list)


class PGNParser:
    """Parser for PGN files with game and move extraction."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_moves = config['analysis']['min_moves']
        self.max_moves = config['analysis']['max_moves']
        self.max_games = config['analysis']['max_games']
    
    def parse_pgn_file(self, pgn_path: str) -> List[Game]:
        """
        Parse a PGN file and extract games.
        
        Args:
            pgn_path: Path to the PGN file
            
        Returns:
            List of Game objects
        """
        games = []
        game_count = 0
        
        with open(pgn_path) as f:
            while True:
                if game_count >= self.max_games:
                    logger.info(f"Reached maximum games limit: {self.max_games}")
                    break
                    
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                parsed_game = self._parse_single_game(game, game_count)
                if parsed_game and len(parsed_game.moves) >= self.min_moves:
                    games.append(parsed_game)
                    game_count += 1
                
        logger.info(f"Parsed {len(games)} games from {pgn_path}")
        return games
    
    def _parse_single_game(self, pgn_game, game_id: int) -> Optional[Game]:
        """Parse a single PGN game into our Game format."""
        try:
            # Extract game metadata
            headers = pgn_game.headers
            
            game = Game(
                game_id=f"game_{game_id}",
                white_player=headers.get('White', 'Unknown'),
                black_player=headers.get('Black', 'Unknown'),
                result=headers.get('Result', '*'),
                date=headers.get('Date', None),
                event=headers.get('Event', None),
                site=headers.get('Site', None)
            )
            
            # Extract moves
            board = pgn_game.board()
            move_count = 0
            
            for move in pgn_game.mainline_moves():
                if move_count >= self.max_moves:
                    break
                    
                fen_before = board.fen()
                move_san = board.san(move)
                board.push(move)
                fen_after = board.fen()
                
                game_move = GameMove(
                    game_id=game.game_id,
                    move_number=move_count // 2 + 1,
                    player='white' if move_count % 2 == 0 else 'black',
                    fen_before=fen_before,
                    fen_after=fen_after,
                    move_uci=move.uci(),
                    move_san=move_san
                )
                
                game.moves.append(game_move)
                move_count += 1
            
            return game
            
        except Exception as e:
            logger.warning(f"Failed to parse game {game_id}: {e}")
            return None
    
    def games_to_dataframe(self, games: List[Game]) -> pd.DataFrame:
        """
        Convert list of games to a pandas DataFrame for analysis.
        
        Args:
            games: List of Game objects
            
        Returns:
            DataFrame with all moves from all games
        """
        all_moves = []
        
        for game in games:
            for move in game.moves:
                move_dict = {
                    'game_id': move.game_id,
                    'white_player': game.white_player,
                    'black_player': game.black_player,
                    'result': game.result,
                    'date': game.date,
                    'event': game.event,
                    'site': game.site,
                    'move_number': move.move_number,
                    'player': move.player,
                    'fen_before': move.fen_before,
                    'fen_after': move.fen_after,
                    'move_uci': move.move_uci,
                    'move_san': move.move_san,
                    'evaluation_before': move.evaluation_before,
                    'evaluation_after': move.evaluation_after,
                    'mistake_type': move.mistake_type
                }
                all_moves.append(move_dict)
        
        return pd.DataFrame(all_moves)
    
    def save_processed_games(self, games: List[Game], output_path: str):
        """Save processed games to a pickle file for later use."""
        import pickle
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            pickle.dump(games, f)
        
        logger.info(f"Saved {len(games)} processed games to {output_path}")
    
    def load_processed_games(self, input_path: str) -> List[Game]:
        """Load processed games from a pickle file."""
        import pickle
        
        with open(input_path, 'rb') as f:
            games = pickle.load(f)
        
        logger.info(f"Loaded {len(games)} processed games from {input_path}")
        return games 