from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
import logging
from datetime import datetime

from ...core.game.game_logic import GameLogic
from ...models.player import Player, PlayerCreate, PlayerUpdate
from ...models.game_state import GameState
from ...services.db_service import DBService
from ...core.cache.cache_service import CacheService
from ...core.analytics.pattern_analyzer import PatternAnalyzer
from ...core.ai.ai_service import AIService
from ...config import Settings, get_settings

router = APIRouter(prefix="/players", tags=["players"])
logger = logging.getLogger(__name__)

# Dependency injection
async def get_services(
    settings: Settings = Depends(get_settings),
    db: DBService = Depends(DBService.get_instance),
    cache: CacheService = Depends(CacheService.get_instance),
    pattern_analyzer: PatternAnalyzer = Depends(PatternAnalyzer.get_instance),
    ai_service: AIService = Depends(AIService.get_instance),
):
    game_logic = GameLogic(settings, pattern_analyzer)
    return {
        "db": db,
        "cache": cache,
        "game_logic": game_logic,
        "pattern_analyzer": pattern_analyzer,
        "ai_service": ai_service
    }

@router.post("/", response_model=Player)
async def create_player(
    player_data: PlayerCreate,
    background_tasks: BackgroundTasks,
    services: dict = Depends(get_services)
):
    """Create a new player and initialize their game state"""
    try:
        # Check if username is already taken
        existing_player = await services["db"].get_player_by_username(
            player_data.username
        )
        if existing_player:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

        # Create player
        player = Player(
            username=player_data.username,
            email=player_data.email,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        # Save to database
        created_player = await services["db"].create_player(player)
        
        # Initialize game state in background
        background_tasks.add_task(
            initialize_player_game_state,
            created_player,
            services
        )
        
        # Cache player data
        await services["cache"].set_player(
            created_player.id,
            created_player.dict()
        )
        
        return created_player
        
    except Exception as e:
        logger.error(f"Error creating player: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{player_id}", response_model=Player)
async def get_player(
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get player details"""
    try:
        # Check cache first
        cached_player = await services["cache"].get_player(player_id)
        if cached_player:
            return Player(**cached_player)
        
        # Get from database
        player = await services["db"].get_player(player_id)
        if not player:
            raise HTTPException(
                status_code=404,
                detail="Player not found"
            )
        
        # Update cache
        await services["cache"].set_player(player_id, player.dict())
        
        return player
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving player: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{player_id}", response_model=Player)
async def update_player(
    player_id: str,
    player_update: PlayerUpdate,
    services: dict = Depends(get_services)
):
    """Update player details"""
    try:
        # Get existing player
        player = await services["db"].get_player(player_id)
        if not player:
            raise HTTPException(
                status_code=404,
                detail="Player not found"
            )
        
        # Update player data
        updated_player = await services["db"].update_player(
            player_id,
            player_update
        )
        
        # Invalidate cache
        await services["cache"].delete_player(player_id)
        
        return updated_player
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating player: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{player_id}/state", response_model=GameState)
async def get_player_state(
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get player's current game state"""
    try:
        # Check cache first
        cached_state = await services["cache"].get_game_state(player_id)
        if cached_state:
            return GameState(**cached_state)
        
        # Get from database
        state = await services["db"].get_game_state(player_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail="Game state not found"
            )
        
        # Update cache
        await services["cache"].set_game_state(player_id, state.dict())
        
        return state
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving game state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{player_id}/statistics")
async def get_player_statistics(
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get player's game statistics and analytics"""
    try:
        # Get player decisions
        decisions = await services["db"].get_player_decisions(player_id)
        
        # Analyze patterns
        patterns = services["pattern_analyzer"].analyze_patterns(decisions)
        
        # Get game state
        state = await services["db"].get_game_state(player_id)
        
        return {
            "patterns": patterns,
            "total_decisions": len(decisions),
            "current_level": state.current_level,
            "experience_points": state.experience_points,
            "achievements": await services["db"].get_player_achievements(player_id),
            "stakeholder_relations": state.stakeholder_satisfaction
        }
        
    except Exception as e:
        logger.error(f"Error retrieving player statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def initialize_player_game_state(
    player: Player,
    services: dict
):
    """Initialize new player's game state"""
    try:
        # Create initial game state
        initial_state = await services["game_logic"].initialize_game_state(player)
        
        # Save to database
        await services["db"].create_game_state(initial_state)
        
        # Cache game state
        await services["cache"].set_game_state(
            player.id,
            initial_state.dict()
        )
        
        logger.info(f"Initialized game state for player {player.id}")
        
    except Exception as e:
        logger.error(f"Error initializing game state: {str(e)}")
        # Could implement retry logic or notification system here