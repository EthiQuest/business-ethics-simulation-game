from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
import math
import random

from ..models.game_state import GameState
from ..models.player import Player
from ..models.scenario import Scenario, Decision
from ..analytics.pattern_analyzer import PatternAnalyzer
from ..config import Settings

logger = logging.getLogger(__name__)

@dataclass
class GameAction:
    """Represents a player's action in the game"""
    type: str
    value: float
    timestamp: datetime
    impacts: Dict[str, float]
    metadata: Dict[str, any]

class GameLogic:
    """Core game mechanics and rules engine"""

    def __init__(
        self,
        settings: Settings,
        pattern_analyzer: PatternAnalyzer
    ):
        self.settings = settings
        self.pattern_analyzer = pattern_analyzer
        
        # Initialize game constants from settings
        self.RESOURCE_DECAY_RATE = 0.05  # 5% decay per turn
        self.REPUTATION_MULTIPLIER = 1.5
        self.LEVEL_XP_REQUIREMENT = 1000  # Base XP needed for level up
        self.STAKEHOLDER_MEMORY_DURATION = 5  # Turns stakeholders remember decisions

    async def initialize_game_state(self, player: Player) -> GameState:
        """Create initial game state for new player"""
        try:
            return GameState(
                player_id=player.id,
                company_size='small',
                financial_resources=self.settings.STARTING_CAPITAL,
                human_resources=self.settings.STARTING_EMPLOYEES,
                reputation=self.settings.INITIAL_REPUTATION,
                stakeholder_satisfaction={
                    stakeholder: 50.0  # Neutral satisfaction
                    for stakeholder in self.settings.STAKEHOLDER_TYPES
                },
                market_share=5.0,  # Starting market share
                sustainability_rating='C',
                active_challenges=[],
                ongoing_events=[],
                current_level=1,
                experience_points=0,
                last_update=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error initializing game state: {str(e)}")
            raise

    async def process_decision(
        self,
        game_state: GameState,
        scenario: Scenario,
        decision: Decision
    ) -> Tuple[GameState, Dict[str, float]]:
        """Process a player's decision and update game state"""
        try:
            # Calculate immediate impacts
            immediate_impacts = self._calculate_decision_impacts(
                decision,
                scenario,
                game_state
            )
            
            # Apply impacts to game state
            updated_state = await self._apply_impacts(
                game_state,
                immediate_impacts
            )
            
            # Process any triggered events
            events = self._check_triggered_events(updated_state, immediate_impacts)
            if events:
                updated_state = await self._handle_events(updated_state, events)
            
            # Calculate and award experience points
            xp_gained = self._calculate_experience_points(
                decision,
                immediate_impacts,
                scenario.difficulty_level
            )
            updated_state.experience_points += xp_gained
            
            # Check for level up
            updated_state = await self._check_level_up(updated_state)
            
            # Update stakeholder memories
            updated_state = self._update_stakeholder_memories(
                updated_state,
                decision,
                immediate_impacts
            )
            
            return updated_state, immediate_impacts
            
        except Exception as e:
            logger.error(f"Error processing decision: {str(e)}")
            raise

    def _calculate_decision_impacts(
        self,
        decision: Decision,
        scenario: Scenario,
        game_state: GameState
    ) -> Dict[str, float]:
        """Calculate the immediate impacts of a decision"""
        impacts = {}
        
        # Base impacts from scenario
        for stakeholder, impact in decision.impacts.items():
            base_impact = impact * scenario.difficulty_level
            
            # Modify based on current game state
            modifier = self._calculate_impact_modifier(
                stakeholder,
                game_state
            )
            
            impacts[stakeholder] = base_impact * modifier
        
        # Calculate resource impacts
        impacts['financial'] = self._calculate_financial_impact(
            decision,
            game_state
        )
        impacts['reputation'] = self._calculate_reputation_impact(
            decision,
            impacts
        )
        
        return impacts

    async def _apply_impacts(
        self,
        game_state: GameState,
        impacts: Dict[str, float]
    ) -> GameState:
        """Apply calculated impacts to game state"""
        updated_state = game_state.copy()
        
        # Update resources
        updated_state.financial_resources += impacts.get('financial', 0)
        updated_state.reputation += impacts.get('reputation', 0)
        
        # Update stakeholder satisfaction
        for stakeholder in self.settings.STAKEHOLDER_TYPES:
            if stakeholder in impacts:
                current = updated_state.stakeholder_satisfaction[stakeholder]
                change = impacts[stakeholder]
                # Ensure satisfaction stays within 0-100 range
                updated_state.stakeholder_satisfaction[stakeholder] = max(
                    0,
                    min(100, current + change)
                )
        
        # Update market metrics
        updated_state.market_share = self._calculate_new_market_share(
            updated_state,
            impacts
        )
        
        # Update sustainability rating
        updated_state.sustainability_rating = self._calculate_sustainability_rating(
            updated_state
        )
        
        return updated_state

    def _calculate_impact_modifier(
        self,
        stakeholder: str,
        game_state: GameState
    ) -> float:
        """Calculate modifier for impact based on game state"""
        base_modifier = 1.0
        
        # Consider current satisfaction
        satisfaction = game_state.stakeholder_satisfaction[stakeholder]
        if satisfaction < 30:
            base_modifier *= 1.2  # Bigger impact when satisfaction is low
        elif satisfaction > 70:
            base_modifier *= 0.8  # Smaller impact when satisfaction is high
            
        # Consider company size
        size_modifiers = {
            'small': 1.2,
            'medium': 1.0,
            'large': 0.8
        }
        base_modifier *= size_modifiers[game_state.company_size]
        
        return base_modifier

    def _calculate_financial_impact(
        self,
        decision: Decision,
        game_state: GameState
    ) -> float:
        """Calculate financial impact of decision"""
        base_impact = decision.impacts.get('financial', 0)
        
        # Scale with company size
        size_multipliers = {
            'small': 0.5,
            'medium': 1.0,
            'large': 2.0
        }
        scaled_impact = base_impact * size_multipliers[game_state.company_size]
        
        # Consider market share
        market_multiplier = 1 + (game_state.market_share / 100)
        
        return scaled_impact * market_multiplier

    def _calculate_reputation_impact(
        self,
        decision: Decision,
        impacts: Dict[str, float]
    ) -> float:
        """Calculate reputation impact based on stakeholder impacts"""
        # Weight stakeholder impacts for reputation
        weights = {
            'employees': 0.3,
            'customers': 0.3,
            'community': 0.2,
            'environment': 0.1,
            'investors': 0.1
        }
        
        weighted_impact = sum(
            impacts.get(stakeholder, 0) * weight
            for stakeholder, weight in weights.items()
        )
        
        return weighted_impact * self.REPUTATION_MULTIPLIER

    def _calculate_new_market_share(
        self,
        game_state: GameState,
        impacts: Dict[str, float]
    ) -> float:
        """Calculate new market share based on impacts"""
        current_share = game_state.market_share
        
        # Consider reputation and financial impacts
        reputation_change = impacts.get('reputation', 0) * 0.1
        financial_change = impacts.get('financial', 0) / game_state.financial_resources
        
        # Calculate change in market share
        share_change = (reputation_change + financial_change) * 0.5
        
        # Ensure realistic bounds (0-100)
        return max(0, min(100, current_share + share_change))

    def _calculate_sustainability_rating(self, game_state: GameState) -> str:
        """Calculate sustainability rating based on game state"""
        # Consider environmental impact and community relations
        environmental_score = game_state.stakeholder_satisfaction['environment']
        community_score = game_state.stakeholder_satisfaction['community']
        
        # Calculate overall score
        overall_score = (environmental_score * 0.6) + (community_score * 0.4)
        
        # Convert to letter rating
        if overall_score >= 90:
            return 'A+'
        elif overall_score >= 80:
            return 'A'
        elif overall_score >= 70:
            return 'B+'
        elif overall_score >= 60:
            return 'B'
        elif overall_score >= 50:
            return 'C+'
        elif overall_score >= 40:
            return 'C'
        else:
            return 'D'

    def _calculate_experience_points(
        self,
        decision: Decision,
        impacts: Dict[str, float],
        difficulty: float
    ) -> int:
        """Calculate experience points earned from decision"""
        base_xp = 100  # Base XP for any decision
        
        # Bonus for difficulty
        difficulty_bonus = base_xp * difficulty
        
        # Bonus for balanced decision (considering multiple stakeholders)
        stakeholder_count = sum(1 for impact in impacts.values() if abs(impact) > 0)
        balance_bonus = base_xp * (stakeholder_count / len(self.settings.STAKEHOLDER_TYPES))
        
        # Bonus for positive impacts
        impact_bonus = sum(
            impact for impact in impacts.values()
            if impact > 0
        ) * 0.5
        
        total_xp = base_xp + difficulty_bonus + balance_bonus + impact_bonus
        return int(total_xp)

    async def _check_level_up(self, game_state: GameState) -> GameState:
        """Check and process level up if needed"""
        current_level = game_state.current_level
        xp_needed = self._calculate_xp_needed(current_level)
        
        if game_state.experience_points >= xp_needed:
            game_state.current_level += 1
            # Could add level-up bonuses here
            logger.info(f"Player leveled up to {game_state.current_level}")
            
        return game_state

    def _calculate_xp_needed(self, level: int) -> int:
        """Calculate XP needed for next level"""
        return int(self.LEVEL_XP_REQUIREMENT * (1.5 ** (level - 1)))

    def _update_stakeholder_memories(
        self,
        game_state: GameState,
        decision: Decision,
        impacts: Dict[str, float]
    ) -> GameState:
        """Update stakeholder memories of past decisions"""
        # Update stakeholder memories (could be used for future decisions)
        for stakeholder in self.settings.STAKEHOLDER_TYPES:
            if stakeholder in impacts:
                memory = {
                    'decision_type': decision.type,
                    'impact': impacts[stakeholder],
                    'timestamp': datetime.utcnow()
                }
                
                if 'stakeholder_memories' not in game_state.metadata:
                    game_state.metadata['stakeholder_memories'] = {}
                    
                if stakeholder not in game_state.metadata['stakeholder_memories']:
                    game_state.metadata['stakeholder_memories'][stakeholder] = []
                    
                memories = game_state.metadata['stakeholder_memories'][stakeholder]
                memories.append(memory)
                
                # Keep only recent memories
                recent_memories = [
                    m for m in memories
                    if (datetime.utcnow() - m['timestamp']).days < self.STAKEHOLDER_MEMORY_DURATION
                ]
                
                game_state.metadata['stakeholder_memories'][stakeholder] = recent_memories
                
        return game_state

    def _check_triggered_events(
        self,
        game_state: GameState,
        impacts: Dict[str, float]
    ) -> List[Dict]:
        """Check for events triggered by game state changes"""
        triggered_events = []
        
        # Check for stakeholder events
        for stakeholder, satisfaction in game_state.stakeholder_satisfaction.items():
            if satisfaction < 30:
                triggered_events.append({
                    'type': 'stakeholder_crisis',
                    'stakeholder': stakeholder,
                    'severity': 'high',
                    'description': f"Critical {stakeholder} satisfaction level"
                })
        
        # Check for financial events
        if game_state.financial_resources < self.settings.STARTING_CAPITAL * 0.2:
            triggered_events.append({
                'type': 'financial_crisis',
                'severity': 'high',
                'description': "Critical financial situation"
            })
        
        # Check for reputation events
        if game_state.reputation < 30:
            triggered_events.append({
                'type': 'reputation_crisis',
                'severity': 'high',
                'description': "Critical reputation level"
            })
        
        return triggered_events

    async def _handle_events(
        self,
        game_state: GameState,
        events: List[Dict]
    ) -> GameState:
        """Handle triggered events"""
        for event in events:
            # Add event to ongoing events if not already present
            if event not in game_state.ongoing_events:
                game_state.ongoing_events.append(event)
                
            # Could add immediate consequences here
            logger.info(f"New event triggered: {event['type']}")
            
        return game_state