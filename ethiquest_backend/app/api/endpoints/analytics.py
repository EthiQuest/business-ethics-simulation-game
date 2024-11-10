from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
import logging
from datetime import datetime, timedelta

from ...core.analytics.pattern_analyzer import PatternAnalyzer
from ...services.db_service import DBService
from ...core.cache.cache_service import CacheService
from ...models.analytics import (
    PlayerAnalytics,
    LearningProgress,
    SkillProgress,
    StakeholderAnalytics,
    DecisionPattern
)
from ...config import Settings, get_settings

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)

# Dependency injection
async def get_services(
    settings: Settings = Depends(get_settings),
    db: DBService = Depends(DBService.get_instance),
    cache: CacheService = Depends(CacheService.get_instance),
    pattern_analyzer: PatternAnalyzer = Depends(PatternAnalyzer.get_instance)
):
    return {
        "db": db,
        "cache": cache,
        "pattern_analyzer": pattern_analyzer,
        "settings": settings
    }

@router.get("/players/{player_id}", response_model=PlayerAnalytics)
async def get_player_analytics(
    player_id: str,
    time_range: Optional[int] = Query(30, description="Days of history to analyze"),
    services: dict = Depends(get_services)
):
    """Get comprehensive analytics for a player"""
    try:
        # Check cache first
        cache_key = f"analytics:{player_id}:{time_range}"
        cached_analytics = await services["cache"].get(cache_key)
        if cached_analytics:
            return PlayerAnalytics(**cached_analytics)

        # Get player decisions within time range
        start_date = datetime.utcnow() - timedelta(days=time_range)
        decisions = await services["db"].get_player_decisions(
            player_id,
            start_date=start_date
        )

        # Get game state for current metrics
        game_state = await services["db"].get_game_state(player_id)
        if not game_state:
            raise HTTPException(
                status_code=404,
                detail="Player game state not found"
            )

        # Analyze patterns and progress
        patterns = services["pattern_analyzer"].analyze_patterns(decisions)
        learning_progress = await analyze_learning_progress(
            player_id,
            decisions,
            services
        )
        skill_progress = await analyze_skill_progress(
            player_id,
            decisions,
            services
        )
        stakeholder_analytics = analyze_stakeholder_relations(
            decisions,
            game_state
        )

        # Compile analytics
        analytics = PlayerAnalytics(
            player_id=player_id,
            analyzed_at=datetime.utcnow(),
            time_range=time_range,
            decision_patterns=patterns,
            learning_progress=learning_progress,
            skill_progress=skill_progress,
            stakeholder_analytics=stakeholder_analytics,
            total_decisions=len(decisions),
            current_level=game_state.current_level,
            experience_points=game_state.experience_points
        )

        # Cache results
        await services["cache"].set(
            cache_key,
            analytics.dict(),
            ttl=3600  # 1 hour cache
        )

        return analytics

    except Exception as e:
        logger.error(f"Error getting player analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/{player_id}/learning", response_model=LearningProgress)
async def get_learning_progress(
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get detailed learning progress analysis"""
    try:
        # Get all player decisions
        decisions = await services["db"].get_player_decisions(player_id)
        
        return await analyze_learning_progress(player_id, decisions, services)

    except Exception as e:
        logger.error(f"Error analyzing learning progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/{player_id}/skills", response_model=SkillProgress)
async def get_skill_progress(
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get detailed skill progress analysis"""
    try:
        # Get all player decisions
        decisions = await services["db"].get_player_decisions(player_id)
        
        return await analyze_skill_progress(player_id, decisions, services)

    except Exception as e:
        logger.error(f"Error analyzing skill progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/{player_id}/stakeholders", response_model=StakeholderAnalytics)
async def get_stakeholder_analytics(
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get detailed stakeholder relationship analytics"""
    try:
        # Get recent decisions and current game state
        decisions = await services["db"].get_player_decisions(
            player_id,
            start_date=datetime.utcnow() - timedelta(days=30)
        )
        game_state = await services["db"].get_game_state(player_id)
        
        return analyze_stakeholder_relations(decisions, game_state)

    except Exception as e:
        logger.error(f"Error analyzing stakeholder relations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/{player_id}/patterns", response_model=List[DecisionPattern])
async def get_decision_patterns(
    player_id: str,
    services: dict = Depends(get_services)
):
    """Get analysis of player's decision-making patterns"""
    try:
        # Get all decisions for pattern analysis
        decisions = await services["db"].get_player_decisions(player_id)
        
        patterns = services["pattern_analyzer"].analyze_patterns(decisions)
        return patterns.patterns

    except Exception as e:
        logger.error(f"Error analyzing decision patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_learning_progress(
    player_id: str,
    decisions: List[dict],
    services: dict
) -> LearningProgress:
    """Analyze player's learning progress"""
    try:
        # Get achievements and completed scenarios
        achievements = await services["db"].get_player_achievements(player_id)
        completed_scenarios = await services["db"].get_completed_scenarios(player_id)

        # Calculate metrics
        if decisions:
            recent_decisions = sorted(decisions, key=lambda x: x['timestamp'])[-10:]
            avg_score = sum(d['success_rating'] for d in recent_decisions) / len(recent_decisions)
            improvement_rate = calculate_improvement_rate(decisions)
        else:
            avg_score = 0
            improvement_rate = 0

        return LearningProgress(
            mastered_concepts=[ach.concept for ach in achievements if ach.type == 'mastery'],
            current_challenges=identify_current_challenges(decisions),
            improvement_rate=improvement_rate,
            avg_success_rate=avg_score,
            completed_scenarios_count=len(completed_scenarios),
            learning_path_progress=calculate_learning_path_progress(
                completed_scenarios,
                services["settings"]
            )
        )

    except Exception as e:
        logger.error(f"Error in learning progress analysis: {str(e)}")
        raise

async def analyze_skill_progress(
    player_id: str,
    decisions: List[dict],
    services: dict
) -> SkillProgress:
    """Analyze player's skill development"""
    try:
        skill_categories = {
            'ethical_reasoning': analyze_ethical_reasoning(decisions),
            'stakeholder_management': analyze_stakeholder_management(decisions),
            'strategic_thinking': analyze_strategic_thinking(decisions),
            'crisis_management': analyze_crisis_management(decisions)
        }

        return SkillProgress(
            skill_levels=skill_categories,
            recent_improvements=identify_recent_improvements(decisions),
            recommended_focus=identify_skill_gaps(skill_categories),
            skill_trajectory=calculate_skill_trajectory(decisions)
        )

    except Exception as e:
        logger.error(f"Error in skill progress analysis: {str(e)}")
        raise

def analyze_stakeholder_relations(
    decisions: List[dict],
    game_state: dict
) -> StakeholderAnalytics:
    """Analyze stakeholder relationship patterns"""
    try:
        stakeholder_impacts = {}
        for stakeholder in game_state.stakeholder_satisfaction.keys():
            stakeholder_impacts[stakeholder] = {
                'current_satisfaction': game_state.stakeholder_satisfaction[stakeholder],
                'trend': calculate_stakeholder_trend(decisions, stakeholder),
                'critical_events': identify_critical_events(decisions, stakeholder),
                'relationship_strength': calculate_relationship_strength(
                    decisions,
                    stakeholder,
                    game_state
                )
            }

        return StakeholderAnalytics(
            stakeholder_impacts=stakeholder_impacts,
            balanced_score=calculate_stakeholder_balance(stakeholder_impacts),
            critical_relationships=identify_critical_relationships(stakeholder_impacts),
            improvement_opportunities=identify_stakeholder_opportunities(
                stakeholder_impacts,
                game_state
            )
        )

    except Exception as e:
        logger.error(f"Error in stakeholder analysis: {str(e)}")
        raise

# Helper functions for analysis

def calculate_improvement_rate(decisions: List[dict]) -> float:
    """Calculate player's rate of improvement"""
    if len(decisions) < 2:
        return 0.0
        
    sorted_decisions = sorted(decisions, key=lambda x: x['timestamp'])
    window_size = min(10, len(sorted_decisions) // 2)
    
    early_window = sorted_decisions[:window_size]
    recent_window = sorted_decisions[-window_size:]
    
    early_avg = sum(d['success_rating'] for d in early_window) / window_size
    recent_avg = sum(d['success_rating'] for d in recent_window) / window_size
    
    return (recent_avg - early_avg) / early_avg if early_avg > 0 else 0.0

def identify_current_challenges(decisions: List[dict]) -> List[str]:
    """Identify areas where player is currently struggling"""
    if not decisions:
        return ["No decision history available"]
        
    recent_decisions = sorted(decisions, key=lambda x: x['timestamp'])[-5:]
    challenges = []
    
    # Analyze recent performance areas
    for decision in recent_decisions:
        if decision['success_rating'] < 70:
            challenges.append(decision['category'])
            
    return list(set(challenges))

def calculate_learning_path_progress(
    completed_scenarios: List[dict],
    settings: Settings
) -> Dict[str, float]:
    """Calculate progress through different learning paths"""
    learning_paths = {
        'ethical_leadership': 0.0,
        'stakeholder_management': 0.0,
        'sustainable_business': 0.0,
        'crisis_management': 0.0
    }
    
    for scenario in completed_scenarios:
        for path in learning_paths:
            if path in scenario['categories']:
                learning_paths[path] += 1
                
    # Normalize progress (assuming 10 scenarios per path for completion)
    return {
        path: min(1.0, count / 10)
        for path, count in learning_paths.items()
    }

def identify_skill_gaps(skill_levels: Dict[str, float]) -> List[str]:
    """Identify skills that need improvement"""
    return [
        skill for skill, level in skill_levels.items()
        if level < 0.7  # Below 70% proficiency
    ]

def calculate_stakeholder_trend(
    decisions: List[dict],
    stakeholder: str
) -> float:
    """Calculate trend in stakeholder relationship"""
    if not decisions:
        return 0.0
        
    stakeholder_decisions = [
        d for d in decisions
        if stakeholder in d['stakeholders_affected']
    ]
    
    if not stakeholder_decisions:
        return 0.0
        
    recent = stakeholder_decisions[-3:]  # Last 3 decisions
    return sum(d['impacts'][stakeholder] for d in recent) / len(recent)