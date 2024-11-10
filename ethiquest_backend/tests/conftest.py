import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator
import os
import uuid
from datetime import datetime, timedelta

from app.models.database import Base
from app.services.db_service import DBService
from app.config import Settings, get_settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://ethiquest_test:ethiquest_test@localhost:5432/ethiquest_test"

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create a test session factory"""
    return sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

@pytest.fixture
async def test_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Create a test session for each test"""
    async with test_session_factory() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_db_service(test_session_factory) -> AsyncGenerator[DBService, None]:
    """Create a test database service"""
    settings = get_settings()
    settings.DATABASE_URL = TEST_DATABASE_URL
    
    service = DBService(settings)
    service.session_factory = test_session_factory
    
    yield service

@pytest.fixture
async def sample_player(test_db_service):
    """Create a sample player for testing"""
    player_data = {
        "id": str(uuid.uuid4()),
        "username": f"test_user_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow(),
        "status": "active",
        "current_level": 1,
        "experience_points": 0,
        "company_name": "Test Company",
        "company_size": "small",
        "industry": "technology"
    }
    
    player = await test_db_service.create_player(player_data)
    return player

@pytest.fixture
async def sample_game_state(test_db_service, sample_player):
    """Create a sample game state for testing"""
    game_state_data = {
        "player_id": sample_player.id,
        "timestamp": datetime.utcnow(),
        "financial_resources": 1000000,
        "human_resources": 10,
        "reputation_points": 50.0,
        "sustainability_rating": "B",
        "stakeholder_satisfaction": {
            "employees": 75,
            "customers": 80,
            "investors": 70,
            "community": 65,
            "environment": 60
        },
        "market_share": 5.0,
        "operational_efficiency": 70.0
    }
    
    game_state = await test_db_service.create_game_state(game_state_data)
    return game_state

@pytest.fixture
async def sample_scenario(test_db_service):
    """Create a sample scenario for testing"""
    scenario_data = {
        "id": str(uuid.uuid4()),
        "title": "Test Scenario",
        "description": "A test ethical scenario",
        "category": "employee_relations",
        "difficulty_level": 0.7,
        "stakeholders_affected": ["employees", "community"],
        "possible_approaches": [
            {
                "id": "approach_1",
                "title": "Conservative Approach",
                "description": "Safe but slow",
                "impacts": {
                    "financial": -10,
                    "reputation": 5
                }
            },
            {
                "id": "approach_2",
                "title": "Aggressive Approach",
                "description": "Fast but risky",
                "impacts": {
                    "financial": 20,
                    "reputation": -10
                }
            }
        ],
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    scenario = await test_db_service.create_scenario(scenario_data)
    return scenario

@pytest.fixture
async def sample_decision(test_db_service, sample_player, sample_scenario):
    """Create a sample decision for testing"""
    decision_data = {
        "player_id": sample_player.id,
        "scenario_id": sample_scenario.id,
        "timestamp": datetime.utcnow(),
        "choice_made": "approach_1",
        "rationale": "Safer option for long-term stability",
        "time_spent": 45,
        "immediate_impacts": {
            "financial": -10,
            "reputation": 5,
            "employees": 10
        },
        "stakeholder_reactions": {
            "employees": "positive",
            "community": "neutral"
        },
        "ethical_alignment": 0.8,
        "risk_level": 0.3,
        "success_rating": 75.0
    }
    
    decision = await test_db_service.create_decision(decision_data)
    return decision

@pytest.fixture
async def sample_achievement(test_db_service, sample_player):
    """Create a sample achievement for testing"""
    achievement_data = {
        "player_id": sample_player.id,
        "achievement_type": "ethical_decision",
        "name": "Ethical Leader",
        "description": "Made 10 highly ethical decisions",
        "criteria_met": {
            "decisions_count": 10,
            "average_ethical_rating": 0.85
        },
        "date_earned": datetime.utcnow(),
        "associated_stats": {
            "total_decisions": 15,
            "ethical_rating_history": [0.8, 0.9, 0.85]
        }
    }
    
    achievement = await test_db_service.create_achievement(achievement_data)
    return achievement

@pytest.fixture
def mock_analytics_data():
    """Create mock analytics data for testing"""
    return {
        "decision_patterns": {
            "risk_preference": 0.7,
            "ethical_alignment": 0.85,
            "stakeholder_focus": ["employees", "community"]
        },
        "learning_progress": {
            "completed_scenarios": 10,
            "skill_improvements": {
                "ethical_reasoning": 0.2,
                "stakeholder_management": 0.3
            }
        },
        "engagement_metrics": {
            "average_session_length": 45,
            "decisions_per_session": 3,
            "return_frequency": "daily"
        }
    }

# Helper Functions
async def cleanup_test_data(test_db_service):
    """Clean up test data"""
    async with test_db_service.session() as session:
        # Delete all test data
        await session.execute("TRUNCATE TABLE analytics_logs CASCADE")
        await session.execute("TRUNCATE TABLE achievements CASCADE")
        await session.execute("TRUNCATE TABLE decisions CASCADE")
        await session.execute("TRUNCATE TABLE scenarios CASCADE")
        await session.execute("TRUNCATE TABLE game_states CASCADE")
        await session.execute("TRUNCATE TABLE players CASCADE")
        await session.commit()

@pytest.fixture(autouse=True)
async def cleanup(test_db_service):
    """Automatically clean up after each test"""
    yield
    await cleanup_test_data(test_db_service)