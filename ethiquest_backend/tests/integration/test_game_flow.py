import pytest
from datetime import datetime
import uuid
from typing import Dict, Any

from app.services.db_service import DBService
from app.core.game.game_logic import GameLogic
from app.core.ai.scenario_generator import ScenarioGenerator
from app.core.analytics.pattern_analyzer import PatternAnalyzer
from app.core.ai.ai_service import AIService
from app.models.database import Player, GameState, Decision, Scenario
from app.config import get_settings

class TestGameFlow:
    """Integration tests for complete game flow"""

    @pytest.fixture
    async def game_services(self, test_db_service: DBService):
        """Initialize all required game services"""
        settings = get_settings()
        pattern_analyzer = PatternAnalyzer()
        ai_service = AIService(settings)
        scenario_generator = ScenarioGenerator(settings, pattern_analyzer)
        game_logic = GameLogic(settings, pattern_analyzer)
        
        return {
            "db": test_db_service,
            "game_logic": game_logic,
            "scenario_generator": scenario_generator,
            "pattern_analyzer": pattern_analyzer,
            "ai_service": ai_service
        }

    @pytest.mark.asyncio
    async def test_complete_game_flow(self, game_services: Dict[str, Any]):
        """Test complete game flow from player creation to decision analysis"""
        # 1. Create new player
        player_data = {
            "username": f"test_player_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "status": "active"
        }
        
        player = await game_services["db"].create_player(player_data)
        assert player.id is not None

        # 2. Initialize game state
        game_state = await game_services["game_logic"].initialize_game_state(player)
        assert game_state.financial_resources == get_settings().STARTING_CAPITAL

        # 3. Generate first scenario
        scenario = await game_services["scenario_generator"].generate_scenario(
            game_state=game_state,
            player=player
        )
        assert scenario.id is not None
        assert len(scenario.possible_approaches) > 0

        # 4. Make decision
        decision = {
            "player_id": player.id,
            "scenario_id": scenario.id,
            "choice_made": scenario.possible_approaches[0].id,
            "rationale": "Test decision rationale",
            "time_spent": 30
        }
        
        # Process decision
        updated_state, impacts = await game_services["game_logic"].process_decision(
            game_state=game_state,
            scenario=scenario,
            decision=decision
        )
        
        assert updated_state is not None
        assert impacts is not None

        # 5. Store decision
        stored_decision = await game_services["db"].create_decision(
            player_id=player.id,
            scenario_id=scenario.id,
            decision=decision
        )
        assert stored_decision.id is not None

        # 6. Analyze patterns
        decisions = await game_services["db"].get_player_decisions(player.id)
        patterns = game_services["pattern_analyzer"].analyze_patterns(
            decisions=decisions,
            current_level=player.current_level
        )
        assert patterns is not None

        # 7. Generate next scenario based on patterns
        next_scenario = await game_services["scenario_generator"].generate_scenario(
            game_state=updated_state,
            player=player
        )
        assert next_scenario.id is not None
        
        # Verify scenario adapts to player patterns
        assert next_scenario.difficulty_level >= scenario.difficulty_level

    @pytest.mark.asyncio
    async def test_stakeholder_impact_flow(self, game_services: Dict[str, Any]):
        """Test stakeholder impact calculations through decision flow"""
        # 1. Create player and initial state
        player = await game_services["db"].create_player({
            "username": f"test_player_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "created_at": datetime.utcnow(),
            "status": "active"
        })
        
        game_state = await game_services["game_logic"].initialize_game_state(player)

        # 2. Generate scenario focused on stakeholder impact
        scenario = await game_services["scenario_generator"].generate_scenario(
            game_state=game_state,
            player=player
        )

        # 3. Make decision with specific stakeholder impacts
        decision = {
            "player_id": player.id,
            "scenario_id": scenario.id,
            "choice_made": scenario.possible_approaches[0].id,
            "rationale": "Prioritizing employee satisfaction",
            "time_spent": 45,
            "stakeholder_focus": "employees"
        }

        # 4. Process decision and check stakeholder impacts
        updated_state, impacts = await game_services["game_logic"].process_decision(
            game_state=game_state,
            scenario=scenario,
            decision=decision
        )

        # Verify stakeholder satisfaction changes
        assert updated_state.stakeholder_satisfaction != game_state.stakeholder_satisfaction
        
        # Store results
        await game_services["db"].update_game_state(player.id, updated_state.dict())

    @pytest.mark.asyncio
    async def test_ethical_progression_flow(self, game_services: Dict[str, Any]):
        """Test ethical decision making progression"""
        # 1. Setup player and initial state
        player = await game_services["db"].create_player({
            "username": f"test_player_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "created_at": datetime.utcnow(),
            "status": "active"
        })
        
        game_state = await game_services["game_logic"].initialize_game_state(player)

        # 2. Make series of ethical decisions
        for _ in range(3):
            # Generate scenario
            scenario = await game_services["scenario_generator"].generate_scenario(
                game_state=game_state,
                player=player
            )

            # Make ethical decision
            decision = {
                "player_id": player.id,
                "scenario_id": scenario.id,
                "choice_made": scenario.possible_approaches[0].id,
                "rationale": "Prioritizing ethical considerations",
                "time_spent": 60,
                "ethical_focus": True
            }

            # Process decision
            game_state, impacts = await game_services["game_logic"].process_decision(
                game_state=game_state,
                scenario=scenario,
                decision=decision
            )

            # Store decision
            await game_services["db"].create_decision(
                player_id=player.id,
                scenario_id=scenario.id,
                decision=decision
            )

        # 3. Analyze ethical progression
        decisions = await game_services["db"].get_player_decisions(player.id)
        patterns = game_services["pattern_analyzer"].analyze_patterns(
            decisions=decisions,
            current_level=player.current_level
        )

        assert patterns.ethical_alignment > 0.5

    @pytest.mark.asyncio
    async def test_crisis_management_flow(self, game_services: Dict[str, Any]):
        """Test crisis management scenario flow"""
        # 1. Setup player and game state
        player = await game_services["db"].create_player({
            "username": f"test_player_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "created_at": datetime.utcnow(),
            "status": "active"
        })
        
        game_state = await game_services["game_logic"].initialize_game_state(player)

        # 2. Create crisis scenario
        crisis_scenario = await game_services["scenario_generator"].generate_scenario(
            game_state=game_state,
            player=player,
            scenario_type="crisis"
        )

        assert crisis_scenario.difficulty_level > 0.7
        assert len(crisis_scenario.stakeholders_affected) > 1

        # 3. Make crisis decision
        decision = {
            "player_id": player.id,
            "scenario_id": crisis_scenario.id,
            "choice_made": crisis_scenario.possible_approaches[0].id,
            "rationale": "Immediate crisis response",
            "time_spent": 30,
            "crisis_response": True
        }

        # 4. Process crisis decision
        updated_state, impacts = await game_services["game_logic"].process_decision(
            game_state=game_state,
            scenario=crisis_scenario,
            decision=decision
        )

        # 5. Verify crisis impacts
        assert "crisis_handled" in updated_state.metadata
        assert len(updated_state.active_challenges) > 0

    @pytest.mark.asyncio
    async def test_performance_metrics_flow(self, game_services: Dict[str, Any]):
        """Test performance metrics tracking through game flow"""
        # 1. Setup initial state
        player = await game_services["db"].create_player({
            "username": f"test_player_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "created_at": datetime.utcnow(),
            "status": "active"
        })
        
        game_state = await game_services["game_logic"].initialize_game_state(player)
        initial_metrics = game_state.dict()

        # 2. Play through multiple scenarios
        for _ in range(3):
            scenario = await game_services["scenario_generator"].generate_scenario(
                game_state=game_state,
                player=player
            )

            decision = {
                "player_id": player.id,
                "scenario_id": scenario.id,
                "choice_made": scenario.possible_approaches[0].id,
                "rationale": "Performance test decision",
                "time_spent": 45
            }

            game_state, _ = await game_services["game_logic"].process_decision(
                game_state=game_state,
                scenario=scenario,
                decision=decision
            )

        # 3. Compare metrics
        final_metrics = game_state.dict()
        
        # Verify resource changes
        assert final_metrics["financial_resources"] != initial_metrics["financial_resources"]
        assert final_metrics["reputation_points"] != initial_metrics["reputation_points"]
        
        # Verify progression
        assert final_metrics["experience_points"] > initial_metrics["experience_points"]