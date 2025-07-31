"""
Recommendation engine for chess opening study.
Generates personalized recommendations based on mistake analysis.
"""

from typing import Dict, List, Tuple
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates personalized opening study recommendations."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.top_openings = config['recommendation']['top_openings']
        self.min_games_per_opening = config['recommendation']['min_games_per_opening']
        self.confidence_threshold = config['recommendation']['confidence_threshold']
    
    def generate_recommendations(self, opening_mistake_stats: Dict) -> List[Dict]:
        """
        Generate opening study recommendations based on mistake statistics.
        
        Args:
            opening_mistake_stats: Dictionary with mistake stats per opening
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        for opening, stats in opening_mistake_stats.items():
            # Skip openings with too few games
            if stats['total_moves'] < self.min_games_per_opening:
                continue
            
            # Calculate priority score based on mistake rates
            priority_score = self._calculate_priority_score(stats)
            
            if priority_score > 0:
                recommendation = {
                    'opening': opening,
                    'priority_score': priority_score,
                    'total_moves': stats['total_moves'],
                    'blunder_rate': stats.get('blunder_rate', 0.0),
                    'mistake_rate': stats.get('mistake_rate', 0.0),
                    'inaccuracy_rate': stats.get('inaccuracy_rate', 0.0),
                    'good_move_rate': stats.get('good_move_rate', 0.0),
                    'recommendation_type': self._get_recommendation_type(stats),
                    'study_focus': self._get_study_focus(stats),
                    'confidence': self._calculate_confidence(stats)
                }
                recommendations.append(recommendation)
        
        # Sort by priority score (highest first)
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Return top recommendations
        return recommendations[:self.top_openings]
    
    def _calculate_priority_score(self, stats: Dict) -> float:
        """
        Calculate priority score for an opening based on mistake rates.
        Higher score = higher priority for study.
        """
        blunder_rate = stats.get('blunder_rate', 0.0)
        mistake_rate = stats.get('mistake_rate', 0.0)
        inaccuracy_rate = stats.get('inaccuracy_rate', 0.0)
        total_moves = stats.get('total_moves', 0)
        
        # Weight different mistake types
        # Blunders are most important, then mistakes, then inaccuracies
        weighted_score = (3.0 * blunder_rate + 
                         2.0 * mistake_rate + 
                         1.0 * inaccuracy_rate)
        
        # Boost score for openings with more games (more confidence)
        confidence_boost = min(total_moves / 50.0, 1.0)  # Cap at 1.0
        
        return weighted_score * (1.0 + confidence_boost)
    
    def _get_recommendation_type(self, stats: Dict) -> str:
        """Determine the type of recommendation based on mistake patterns."""
        blunder_rate = stats.get('blunder_rate', 0.0)
        mistake_rate = stats.get('mistake_rate', 0.0)
        inaccuracy_rate = stats.get('inaccuracy_rate', 0.0)
        
        if blunder_rate > 0.15:  # More than 15% blunders
            return "critical_weakness"
        elif mistake_rate > 0.25:  # More than 25% mistakes
            return "major_weakness"
        elif inaccuracy_rate > 0.4:  # More than 40% inaccuracies
            return "moderate_weakness"
        else:
            return "minor_improvement"
    
    def _get_study_focus(self, stats: Dict) -> List[str]:
        """Determine what aspects to focus on when studying this opening."""
        focus_areas = []
        
        blunder_rate = stats.get('blunder_rate', 0.0)
        mistake_rate = stats.get('mistake_rate', 0.0)
        inaccuracy_rate = stats.get('inaccuracy_rate', 0.0)
        
        if blunder_rate > 0.1:
            focus_areas.append("tactical_awareness")
            focus_areas.append("calculation")
        
        if mistake_rate > 0.2:
            focus_areas.append("positional_understanding")
            focus_areas.append("opening_principles")
        
        if inaccuracy_rate > 0.3:
            focus_areas.append("move_quality")
            focus_areas.append("planning")
        
        if not focus_areas:
            focus_areas.append("general_improvement")
        
        return focus_areas
    
    def _calculate_confidence(self, stats: Dict) -> float:
        """Calculate confidence level for the recommendation."""
        total_moves = stats.get('total_moves', 0)
        
        # More moves = higher confidence
        confidence = min(total_moves / 100.0, 1.0)
        
        return confidence
    
    def generate_study_plan(self, recommendations: List[Dict]) -> Dict:
        """
        Generate a comprehensive study plan from recommendations.
        
        Args:
            recommendations: List of opening recommendations
            
        Returns:
            Dictionary with study plan
        """
        study_plan: Dict = {
            'total_recommendations': len(recommendations),
            'priority_openings': [],
            'study_schedule': {},
            'focus_areas': set(),
            'estimated_time': 0
        }
        
        for i, rec in enumerate(recommendations):
            # Add to priority openings
            study_plan['priority_openings'].append({
                'rank': i + 1,
                'opening': rec['opening'],
                'priority_score': rec['priority_score'],
                'recommendation_type': rec['recommendation_type'],
                'study_focus': rec['study_focus']
            })
            
            # Add focus areas
            focus_areas_set = study_plan['focus_areas']
            if isinstance(focus_areas_set, set):
                focus_areas_set.update(rec['study_focus'])
            
            # Estimate study time (in hours)
            if rec['recommendation_type'] == 'critical_weakness':
                study_time = 8  # 8 hours for critical weaknesses
            elif rec['recommendation_type'] == 'major_weakness':
                study_time = 6  # 6 hours for major weaknesses
            elif rec['recommendation_type'] == 'moderate_weakness':
                study_time = 4  # 4 hours for moderate weaknesses
            else:
                study_time = 2  # 2 hours for minor improvements
            
            estimated_time = study_plan['estimated_time']
            if isinstance(estimated_time, int):
                study_plan['estimated_time'] = estimated_time + study_time
        
        # Convert set to list for JSON serialization
        focus_areas_set = study_plan['focus_areas']
        if isinstance(focus_areas_set, set):
            study_plan['focus_areas'] = list(focus_areas_set)
        
        return study_plan
    
    def format_recommendations(self, recommendations: List[Dict]) -> str:
        """
        Format recommendations as a human-readable string.
        
        Args:
            recommendations: List of recommendation dictionaries
            
        Returns:
            Formatted string with recommendations
        """
        if not recommendations:
            return "No specific recommendations at this time."
        
        output = "🎯 CHESS OPENING STUDY RECOMMENDATIONS\n"
        output += "=" * 50 + "\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            output += f"{i}. {rec['opening']}\n"
            output += f"   Priority Score: {rec['priority_score']:.2f}\n"
            output += f"   Type: {rec['recommendation_type'].replace('_', ' ').title()}\n"
            output += f"   Focus: {', '.join(rec['study_focus'])}\n"
            output += f"   Confidence: {rec['confidence']:.1%}\n"
            output += f"   Moves Analyzed: {rec['total_moves']}\n"
            output += f"   Blunder Rate: {rec['blunder_rate']:.1%}\n"
            output += f"   Mistake Rate: {rec['mistake_rate']:.1%}\n"
            output += f"   Inaccuracy Rate: {rec['inaccuracy_rate']:.1%}\n\n"
        
        return output 