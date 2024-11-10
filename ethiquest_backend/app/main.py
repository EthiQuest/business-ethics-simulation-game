from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import logging
from datetime import datetime

from app.core.ai import AIService, ScenarioGenerator
from app.core.analytics import PatternAnalyzer
from app.core.cache import CacheService
from app.models.scenario import Scenario, ScenarioResponse
from app.models.player import Player, PlayerState
from app.models.game import GameState
from app.db import get_db, Database
from app.config import Settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EthiQuest API",
    description="Backend API for EthiQuest ethical business simulation game",
    version="1.0.0"
)

# Add CORS middleware for Flutter Web support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Customize for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
settings = Settings()
ai_service = AIService(settings.ai_key)
cache_service = CacheService(settings.redis_url)
pattern_analyzer = PatternAnalyzer()
scenario_generator = ScenarioGenerator(ai_service, pattern_analyzer)

# Dependency for database connection
async def get_db_session():
    db = get_db()
    try:
        yield db
    finally:
        await db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting EthiQuest API")
    # Start cache cleanup task
    asyncio.create_task(cache_service.start_cleanup_task())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down EthiQuest API")
    await cache_service.close()

# Player Management Endpoints
@app.post("/players/", response_model=Player)
async def create_player(
    player: Player,
    db: Database = Depends(get_db_session)
):
    """Create new player profile"""
    try:
        return await db.create_player(player)
    except Exception as e:
        logger.error(f"Error creating player: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/players/{player_id}", response_model=Player)
async def get_player(
    player_id: str,
    db: Database = Depends(get_db_session)
):
    """Get player profile"""
    cached = await cache_service.get_player_state(player_id)
    if cached:
        return Player(**cached)
        
    player = await db.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    await cache_service.store_player_state(player_id, player.dict())
    return player

# Game State Endpoints
@app.get("/players/{player_id}/state", response_model=GameState)
async def get_game_state(
    player_id: str,
    db: Database = Depends(get_db_session)
):
    """Get current game state for player"""
    state = await db.get_game_state(player_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game state not found")
    return state

@app.post("/players/{player_id}/decisions")
async def submit_decision(
    player_id: str,
    scenario_id: str,
    decision: dict,
    db: Database = Depends(get_db_session)
):
    """Submit player decision for a scenario"""
    try:
        # Record decision
        await db.record_decision(player_id, scenario_id, decision)
        
        # Update player state
        player = await db.get_player(player_id)
        decisions = await db.get_player_decisions(player_id)
        
        # Analyze new patterns
        patterns = pattern_analyzer.analyze_patterns(
            decisions,
            player.current_level
        )
        
        # Update player profile with new patterns
        await db.update_player_patterns(player_id, patterns)
        
        # Invalidate cache
        await cache_service.invalidate_player_state(player_id)
        
        return {"status": "success", "patterns": patterns}
        
    except Exception as e:
        logger.error(f"Error recording decision: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Scenario Generation Endpoints
@app.get("/scenarios/generate", response_model=ScenarioResponse)
async def generate_scenario(
    player_id: str,
    db: Database = Depends(get_db_session)
):
    """Generate new scenario for player"""
    try:
        # Get player state and history
        player = await db.get_player(player_id)
        game_state = await db.get_game_state(player_id)
        
        if not player or not game_state:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Check cache first
        cache_key = f"scenario:{player_id}:{datetime.now().strftime('%Y%m%d')}"
        cached = await cache_service.get_scenario(cache_key)
        if cached:
            return ScenarioResponse(**cached)
        
        # Generate new scenario
        scenario = await scenario_generator.generate_scenario(
            game_state,
            player
        )
        
        # Store in cache
        await cache_service.store_scenario(cache_key, scenario.dict())
        
        return ScenarioResponse(
            scenario=scenario,
            player_state=game_state
        )
        
    except Exception as e:
        logger.error(f"Error generating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Websocket for real-time features
@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """Websocket connection for real-time updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Handle real-time events (achievements, notifications, etc.)
            response = {"status": "received", "data": data}
            await websocket.send_json(response)
    except Exception as e:
        logger.error(f"Websocket error: {str(e)}")
        await websocket.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "ai": await ai_service.check_health(),
            "cache": await cache_service.check_health(),
            "database": await get_db().check_health()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
