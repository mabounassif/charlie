#!/usr/bin/env python3
"""
Main entry point for the Chess Opening Recommendation System.
Orchestrates the entire analysis pipeline.
"""

import argparse
import logging
import yaml
import json
from pathlib import Path
from typing import Dict, List

# Import our components
from core.pgn_parser import PGNParser
from evaluation.stockfish_evaluator import StockfishEvaluator
from classification.mistake_classifier import MistakeClassifier
from classification.opening_classifier import OpeningClassifier
from recommendation.recommendation_engine import RecommendationEngine


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('chess_analysis.log'),
            logging.StreamHandler()
        ]
    )


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def analyze_games(pgn_path: str, config: Dict) -> Dict:
    """
    Run the complete analysis pipeline.
    
    Args:
        pgn_path: Path to PGN file
        config: Configuration dictionary
        
    Returns:
        Dictionary with analysis results
    """
    logger = logging.getLogger(__name__)
    results = {}
    
    try:
        # Step 1: Parse PGN file
        logger.info("Step 1: Parsing PGN file...")
        parser = PGNParser(config)
        games = parser.parse_pgn_file(pgn_path)
        results['games_parsed'] = len(games)
        logger.info(f"Parsed {len(games)} games")
        
        # Step 2: Evaluate positions with Stockfish
        logger.info("Step 2: Evaluating positions with Stockfish...")
        with StockfishEvaluator(config) as evaluator:
            # Convert games to moves for evaluation
            all_moves = []
            for game in games:
                for move in game.moves:
                    move_dict = {
                        'game_id': move.game_id,
                        'fen_before': move.fen_before,
                        'move_uci': move.move_uci,
                        'player': move.player
                    }
                    all_moves.append(move_dict)
            
            # Evaluate all moves
            evaluated_moves = evaluator.evaluate_game_moves(all_moves)
            results['moves_evaluated'] = len(evaluated_moves)
            logger.info(f"Evaluated {len(evaluated_moves)} moves")
        
        # Step 3: Classify mistakes
        logger.info("Step 3: Classifying mistakes...")
        mistake_classifier = MistakeClassifier(config)
        classified_moves = mistake_classifier.classify_moves_batch(evaluated_moves)
        mistake_stats = mistake_classifier.get_mistake_stats(classified_moves)
        results['mistake_stats'] = mistake_stats
        logger.info(f"Mistake classification complete")
        
        # Step 4: Classify openings
        logger.info("Step 4: Classifying openings...")
        opening_classifier = OpeningClassifier(config)
        
        # Group moves by game for opening classification
        games_data = []
        for game in games:
            game_moves = [move.move_uci for move in game.moves]
            game_data = {
                'game_id': game.game_id,
                'result': game.result,
                'moves': game_moves
            }
            games_data.append(game_data)
        
        classified_games = opening_classifier.classify_game_openings(games_data)
        opening_stats = opening_classifier.get_opening_stats(classified_games)
        results['opening_stats'] = opening_stats
        logger.info(f"Opening classification complete")
        
        # Step 5: Generate recommendations
        logger.info("Step 5: Generating recommendations...")
        recommendation_engine = RecommendationEngine(config)
        
        # Combine opening and mistake data
        opening_mistake_stats = {}
        for move in classified_moves:
            game_id = move['game_id']
            opening = "Unknown Opening"  # Default
            
            # Find the game and its opening
            for game_data in classified_games:
                if game_data['game_id'] == game_id:
                    opening = game_data.get('opening', 'Unknown Opening')
                    break
            
            if opening not in opening_mistake_stats:
                opening_mistake_stats[opening] = {
                    'total_moves': 0,
                    'blunders': 0,
                    'mistakes': 0,
                    'inaccuracies': 0,
                    'good_moves': 0,
                    'unknown': 0
                }
            
            opening_mistake_stats[opening]['total_moves'] += 1
            mistake_type = move.get('mistake_type', 'unknown')
            if mistake_type in opening_mistake_stats[opening]:
                opening_mistake_stats[opening][mistake_type] += 1
        
        # Calculate rates for each opening
        for opening, stats in opening_mistake_stats.items():
            total = stats['total_moves']
            if total > 0:
                stats['blunder_rate'] = stats['blunders'] / total
                stats['mistake_rate'] = stats['mistakes'] / total
                stats['inaccuracy_rate'] = stats['inaccuracies'] / total
                stats['good_move_rate'] = stats['good_moves'] / total
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(opening_mistake_stats)
        study_plan = recommendation_engine.generate_study_plan(recommendations)
        
        results['recommendations'] = recommendations
        results['study_plan'] = study_plan
        results['opening_mistake_stats'] = opening_mistake_stats
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        return results
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


def save_results(results: Dict, output_dir: str) -> None:
    """Save analysis results to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save detailed results as JSON
    with open(output_path / 'analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save recommendations as text
    if 'recommendations' in results:
        recommendation_engine = RecommendationEngine({})  # Empty config for formatting
        formatted_recs = recommendation_engine.format_recommendations(results['recommendations'])
        
        with open(output_path / 'recommendations.txt', 'w') as f:
            f.write(formatted_recs)
    
    print(f"Results saved to {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Chess Opening Recommendation System")
    parser.add_argument("--pgn-file", required=True, help="Path to PGN file")
    parser.add_argument("--config", default="config.yaml", help="Configuration file")
    parser.add_argument("--output-dir", default="data/processed", help="Output directory")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = load_config(args.config)
    
    # Run analysis
    logger.info("Starting chess analysis...")
    results = analyze_games(args.pgn_file, config)
    
    # Save results
    save_results(results, args.output_dir)
    
    # Print summary
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE")
    print("="*50)
    print(f"Games analyzed: {results['games_parsed']}")
    print(f"Moves evaluated: {results['moves_evaluated']}")
    print(f"Recommendations generated: {len(results['recommendations'])}")
    
    if 'study_plan' in results:
        plan = results['study_plan']
        print(f"Estimated study time: {plan['estimated_time']} hours")
        print(f"Focus areas: {', '.join(plan['focus_areas'])}")
    
    print(f"\nResults saved to: {args.output_dir}")
    print("Check recommendations.txt for detailed recommendations")


if __name__ == "__main__":
    main() 