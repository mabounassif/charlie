#!/usr/bin/env python3
"""
Web application for the Chess Opening Recommendation System.
Provides a simple web interface for uploading and analyzing PGN files.
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename

# Import our components
from core.pgn_parser import PGNParser
from evaluation.stockfish_evaluator import StockfishEvaluator
from classification.mistake_classifier import MistakeClassifier
from classification.opening_classifier import OpeningClassifier
from recommendation.recommendation_engine import RecommendationEngine

# Load configuration
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chess Opening Recommendation System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .upload-form { border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
        .results { margin-top: 20px; }
        .error { color: red; }
        .success { color: green; }
        .loading { display: none; }
    </style>
</head>
<body>
    <h1>Chess Opening Recommendation System</h1>
    
    <div class="upload-form">
        <h2>Upload PGN File</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="pgn_file" accept=".pgn" required>
            <br><br>
            <button type="submit">Analyze Games</button>
        </form>
    </div>

    <div class="loading" id="loading">
        <h3>Analyzing your games... This may take a few minutes.</h3>
        <p>Processing moves with Stockfish engine...</p>
    </div>

    <div class="results" id="results"></div>

    <script>
        document.querySelector('form').addEventListener('submit', function() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';
        });
    </script>
</body>
</html>
"""

def analyze_games_from_file(pgn_file_path: str) -> Dict[str, Any]:
    """
    Run the complete analysis pipeline on a PGN file.
    
    Args:
        pgn_file_path: Path to PGN file
        
    Returns:
        Dictionary with analysis results
    """
    results: Dict[str, Any] = {}
    
    try:
        # Step 1: Parse PGN file
        logger.info("Step 1: Parsing PGN file...")
        parser = PGNParser(config)
        games = parser.parse_pgn_file(pgn_file_path)
        results['games_parsed'] = len(games)
        logger.info(f"Parsed {len(games)} games")
        
        if len(games) == 0:
            return {"error": "No games found in PGN file"}
        
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
                'moves': game_moves,
                'result': game.result
            }
            games_data.append(game_data)
        
        opening_results = opening_classifier.classify_games_batch(games_data)
        results['opening_analysis'] = opening_results
        logger.info(f"Opening classification complete")
        
        # Step 5: Generate recommendations
        logger.info("Step 5: Generating recommendations...")
        recommendation_engine = RecommendationEngine(config)
        recommendations = recommendation_engine.generate_recommendations(
            classified_moves, opening_results, mistake_stats
        )
        results['recommendations'] = recommendations
        logger.info(f"Recommendations generated")
        
        return results
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}

@app.route('/', methods=['GET'])
def index():
    """Serve the main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/', methods=['POST'])
def upload_file():
    """Handle file upload and analysis."""
    if 'pgn_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['pgn_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pgn'):
        return jsonify({'error': 'Please upload a PGN file'}), 400
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pgn') as tmp_file:
            file.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Analyze the games
        results = analyze_games_from_file(tmp_file_path)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Railway."""
    return jsonify({'status': 'healthy', 'service': 'chess-recommender'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 