from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
import logging
from datetime import datetime

from ...core.game.game_logic import GameLogic
from ...core.ai.scenario_generator import ScenarioGenerator
from ...models.scenario import (
    Scenario,
    ScenarioResponse,
    Decision,
    DecisionResponse
)
from ...models.game_state import GameState
from ...services.db_service import DBService
from ...core.cache.cache_service import CacheService
from ...core.analytics.pattern_analyzer import PatternAnalyzer
from ...config import Settings, get_settings

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
logger = logging.getLogger(__name__)

# Dependency injection
async def get_services(
    settings: Settings = Depends(get_settings),
    db: DBService = Depends(DBService.get_instance),
    cache: CacheService = Depends(CacheService.get_instance),
    pattern_analyzer: PatternAnalyzer = Depends(PatternAnalyzer.get_instance),
):
    game_logic = GameLogic(settings, pattern_analyzer)
    scenario_generator = ScenarioGenerator(settings, pattern_analyzer)
    return {
        "db": db,
        "cache": cache,
        "game_logic": game_logic,
        "scenario_generator": scenario_generator,
        "pattern_analyzer": pattern_analyzer
    }

@router.get("/generate", response_model=ScenarioResponse)
async def generate_scenario(
    player_id: str,
    difficulty: Optional[float] = None,
    services: dict = Depends(get_services)
):
    """Generate a new scenario for the player"""
    try:
        # Check cache first
        cache_key = f"scenario:{player_id}:{datetime.utcnow().strftime('%Y%m%d')}"
        cached_scenario = await services["cache"].get_scenario(cache_key)
        if cached_scenario:
            return ScenarioResponse(**cached_scenario)

        # Get player's game state and history
        game_state = await services["db"].get_game_state(player_id)
        if not game_state:
            raise HTTPException(
                status_code=404,
                detail="Player game state not found"
            )

        # Get player's decision history
        decisions = await services["db"].get_player_decisions(player_id)
        
        # Analyze patterns for personalization
        patterns = services["pattern_analyzer"].analyze_patterns(decisions)

        # Generate scenario
        scenario = await services["scenario_generator"].generate_scenario(
            game_state=game_state,
            player_patterns=patterns,
            difficulty=difficulty
        )

        # Store scenario in database
        stored_scenario = await services["db"].create_scenario(scenario)

        # Cache scenario
        response = ScenarioResponse(
            scenario=stored_scenario,
            game_state=game_state,
            patterns=patterns
        )
        await services["cache"].set_scenario(
            cache_key,
            response.dict(),
            ttl=3600  # 1 hour cache
        )

        return response

    except Exception as e:
        logger.error(f"Error generating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{scenario_id}/decisions", response_model=DecisionResponse)
async def submit_decision(
    scenario_id: str,
    player_id: str,
    decision: Decision,
    background_tasks: BackgroundTasks,
    services: dict = Depends(get_services)
):
    """Submit and process a player's decision"""
    try:
        # Get scenario and game state
        scenario = await services["db"].get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=404,
                detail="Scenario not found"
            )

        game_state = await services["db"].get_game_state(player_id)
        if not game_state:
            raise HTTPException(
                status_code=404,
                detail="Game state not found"
            )

        # Validate decision
        if not _validate_decision(decision, scenario):
            raise HTTPException(
                status_code=400,
                detail="Invalid decision for scenario"
            )

        # Process decision and get impacts
        updated_state, impacts = await services["game_logic"].process_decision(
            game_state=game_state,
            scenario=scenario,
            decision=decision
        )

        # Store decision in database
        stored_decision = await services["db"].create_decision(
            player_id=player_id,
            scenario_id=scenario_id,
            decision=decision,
            impacts=impacts
        )

        # Update game state
        await services["db"].update_game_state(player_id, updated_state)

        # Invalidate caches
        await services["cache"].delete_game_state(player_id)
        await services["cache"].delete_player(player_id)

        # Schedule background analytics
        background_tasks.add_task(
            process_decision_analytics,
            player_id=player_id,
            decision=stored_decision,
            impacts=impacts,
            services=services
        )

        return DecisionResponse(
            decision=stored_decision,
            impacts=impacts,
            updated_state=updated_state
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scenario_id}/analysis")
async def get_scenario_analysis(
    scenario_id: str,
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get detailed analysis of a scenario and potential outcomes"""
    try:
        # Get scenario
        scenario = await services["db"].get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=404,
                detail="Scenario not found"
            )

        # Get player's game state
        game_state = await services["db"].get_game_state(player_id)
        if not game_state:
            raise HTTPException(
                status_code=404,
                detail="Game state not found"
            )

        # Analyze potential outcomes
        analysis = await services["game_logic"].analyze_scenario_outcomes(
            scenario=scenario,
            game_state=game_state
        )

        return {
            "potential_outcomes": analysis.outcomes,
            "risk_analysis": analysis.risks,
            "stakeholder_analysis": analysis.stakeholder_impacts,
            "opportunity_analysis": analysis.opportunities
        }

    except Exception as e:
        logger.error(f"Error analyzing scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _validate_decision(decision: Decision, scenario: Scenario) -> bool:
    """Validate if decision is valid for the scenario"""
    try:
        # Check if decision approach is valid for scenario
        valid_approaches = [
            approach.id for approach in scenario.possible_approaches
        ]
        if decision.approach_id not in valid_approaches:
            return False

        # Check if decision was made within time constraint
        if scenario.time_constraint:
            decision_time = (
                datetime.utcnow() - scenario.created_at
            ).total_seconds()
            if decision_time > scenario.time_constraint:
                return False

        # Validate decision parameters
        if not all(
            param in scenario.required_parameters
            for param in decision.parameters.keys()
        ):
            return False

        return True

    except Exception:
        return False

async def process_decision_analytics(
    player_id: str,
    decision: Decision,
    impacts: dict,
    services: dict
):
    """Process analytics after decision submission"""
    try:
        # Get player's decision history
        decisions = await services["db"].get_player_decisions(player_id)
        
        # Update player patterns
        patterns = services["pattern_analyzer"].analyze_patterns(decisions)
        await services["db"].update_player_patterns(player_id, patterns)

        # Check for achievements
        achievements = services["game_logic"].check_achievements(
            player_id=player_id,
            decision=decision,
            impacts=impacts,
            patterns=patterns
        )

        # Store new achievements
        if achievements:
            await services["db"].create_achievements(
                player_id=player_id,
                achievements=achievements
            )

        # Update analytics logs
        await services["db"].create_analytics_log(
            player_id=player_id,
            decision_id=decision.id,
            patterns=patterns,
            impacts=impacts
        )

        logger.info(f"Processed analytics for player {player_id}")

    except Exception as e:
        logger.error(f"Error processing decision analytics: {str(e)}")
        # Could implement retry logic or notification system here