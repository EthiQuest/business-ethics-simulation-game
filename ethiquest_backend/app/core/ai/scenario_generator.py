from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from .prompt_templates import ScenarioPrompt
from .ai_service import AIService
from ..models.scenario import Scenario, Approach, Impact
from ..models.game_state import GameState
from ..models.player import PlayerHistory
from ..analytics.pattern_analyzer import PatternAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class ScenarioContext:
    """Context data for scenario generation"""
    company_size: str
    industry: str
    market_position: str
    current_challenges: List[str]
    stakeholder_satisfaction: Dict[str, float]
    recent_decisions: List[Dict]
    learning_patterns: Dict[str, any]

class ScenarioGenerator:
    """Generates ethical business scenarios using AI"""
    
    def __init__(self, ai_service: AIService, pattern_analyzer: PatternAnalyzer):
        self.ai_service = ai_service
        self.pattern_analyzer = pattern_analyzer
        
    async def generate_scenario(
        self,
        game_state: GameState,
        player_history: PlayerHistory
    ) -> Scenario:
        """Generate a new scenario based on game state and player history"""
        try:
            # Build context for AI
            context = self._build_context(game_state, player_history)
            
            # Generate base scenario
            scenario = await self._generate_base_scenario(context)
            
            # Enrich with game mechanics
            enriched_scenario = self._enrich_scenario(scenario, game_state)
            
            # Validate final scenario
            self._validate_scenario(enriched_scenario)
            
            return enriched_scenario
            
        except Exception as e:
            logger.error(f"Error generating scenario: {str(e)}")
            return self._get_fallback_scenario(game_state)

    def _build_context(
        self,
        game_state: GameState,
        player_history: PlayerHistory
    ) -> ScenarioContext:
        """Build context for AI prompt based on current state"""
        
        # Analyze player's decision patterns
        learning_patterns = self.pattern_analyzer.analyze_patterns(
            player_history.decisions,
            game_state.current_level
        )
        
        return ScenarioContext(
            company_size=game_state.company_size,
            industry=game_state.industry,
            market_position=game_state.market_position,
            current_challenges=game_state.active_challenges,
            stakeholder_satisfaction=game_state.stakeholder_satisfaction,
            recent_decisions=player_history.get_recent_decisions(5),
            learning_patterns=learning_patterns
        )

    async def _generate_base_scenario(self, context: ScenarioContext) -> Scenario:
        """Generate base scenario using AI"""
        
        # Build prompt from context
        prompt = ScenarioPrompt.build_prompt(
            context=context,
            difficulty=self._calculate_difficulty(context)
        )
        
        try:
            # Get AI response
            ai_response = await self.ai_service.generate_scenario(prompt)
            
            # Parse and validate AI response
            scenario = self._parse_ai_response(ai_response)
            
            return scenario
            
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            raise

    def _enrich_scenario(self, scenario: Scenario, game_state: GameState) -> Scenario:
        """Enrich base scenario with game mechanics"""
        
        # Calculate mechanical impacts
        impacts = self._calculate_impacts(scenario.approaches, game_state)
        
        # Add time pressure
        time_constraint = self._calculate_time_constraint(
            scenario.category,
            game_state.current_level
        )
        
        # Add hidden factors
        hidden_factors = self._generate_hidden_factors(scenario, game_state)
        
        # Calculate risk levels
        risk_levels = self._calculate_risk_levels(impacts)
        
        # Add achievement opportunities
        achievements = self._identify_achievements(scenario, game_state)
        
        return Scenario(
            id=scenario.id,
            title=scenario.title,
            description=scenario.description,
            category=scenario.category,
            stakeholders_affected=scenario.stakeholders_affected,
            approaches=scenario.approaches,
            impacts=impacts,
            time_constraint=time_constraint,
            hidden_factors=hidden_factors,
            risk_levels=risk_levels,
            potential_achievements=achievements,
            created_at=datetime.utcnow()
        )

    def _calculate_difficulty(self, context: ScenarioContext) -> float:
        """Calculate appropriate difficulty level"""
        base_difficulty = len(context.learning_patterns.get('mastered_concepts', [])) * 0.1
        
        # Adjust for recent performance
        recent_success_rate = self.pattern_analyzer.calculate_recent_success_rate(
            context.recent_decisions
        )
        difficulty_modifier = (recent_success_rate - 0.5) * 0.2
        
        return min(1.0, max(0.1, base_difficulty + difficulty_modifier))

    def _parse_ai_response(self, ai_response: Dict) -> Scenario:
        """Parse and validate AI response into scenario structure"""
        try:
            # Basic validation
            required_fields = ['title', 'description', 'stakeholders_affected', 'approaches']
            for field in required_fields:
                if field not in ai_response:
                    raise ValueError(f"Missing required field: {field}")

            # Parse approaches
            approaches = [
                Approach(
                    title=a['title'],
                    description=a['description'],
                    impacts=Impact(**a.get('impacts', {}))
                )
                for a in ai_response['approaches']
            ]

            return Scenario(
                title=ai_response['title'],
                description=ai_response['description'],
                stakeholders_affected=ai_response['stakeholders_affected'],
                approaches=approaches,
                category=ai_response.get('category', 'general'),
                hidden_factors=ai_response.get('hidden_factors', [])
            )

        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            raise ValueError("Invalid AI response format")

    def _validate_scenario(self, scenario: Scenario):
        """Validate final scenario before returning"""
        try:
            assert len(scenario.approaches) >= 2, "Scenario must have at least 2 approaches"
            assert len(scenario.stakeholders_affected) > 0, "Must affect at least one stakeholder"
            assert all(a.impacts for a in scenario.approaches), "All approaches must have impacts"
            
            # Validate impact ranges
            for approach in scenario.approaches:
                for impact_value in approach.impacts.__dict__.values():
                    assert -100 <= impact_value <= 100, "Impact values must be between -100 and 100"
                    
        except AssertionError as e:
            logger.error(f"Scenario validation failed: {str(e)}")
            raise ValueError("Invalid scenario structure")

    def _get_fallback_scenario(self, game_state: GameState) -> Scenario:
        """Return a pre-defined scenario if generation fails"""
        return Scenario(
            title="Supply Chain Ethics Decision",
            description="A key supplier has been found using questionable labor practices...",
            category="supply_chain",
            stakeholders_affected=["employees", "community", "investors"],
            approaches=[
                Approach(
                    title="Immediate Termination",
                    description="Cut ties immediately to protect reputation",
                    impacts=Impact(reputation=10, financial=-20)
                ),
                Approach(
                    title="Engagement and Reform",
                    description="Work with supplier to improve practices",
                    impacts=Impact(reputation=5, financial=-5)
                )
            ],
            hidden_factors=[
                "Supplier's community dependence",
                "Market alternatives availability"
            ],
            created_at=datetime.utcnow()
        )