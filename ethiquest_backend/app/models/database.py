from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, Integer, String, Float, JSON, DateTime, ForeignKey, 
    Boolean, Enum, Text, BigInteger
)
import enum
from datetime import datetime
import uuid

Base = declarative_base()

class CompanySize(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class PlayerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Player(Base):
    """Player model storing user information and progress"""
    __tablename__ = "players"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(PlayerStatus), default=PlayerStatus.ACTIVE)
    
    # Game Progress
    current_level = Column(Integer, default=1)
    experience_points = Column(BigInteger, default=0)
    total_decisions = Column(Integer, default=0)
    
    # Company Information
    company_name = Column(String(100))
    company_size = Column(Enum(CompanySize), default=CompanySize.SMALL)
    industry = Column(String(50))
    
    # Analytics and Patterns
    learning_patterns = Column(JSON, default=dict)
    skill_levels = Column(JSON, default=dict)
    achievement_stats = Column(JSON, default=dict)
    
    # Relationships
    decisions = relationship("Decision", back_populates="player")
    game_states = relationship("GameState", back_populates="player")
    achievements = relationship("Achievement", back_populates="player")

class GameState(Base):
    """Current state of player's game"""
    __tablename__ = "game_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Resources
    financial_resources = Column(BigInteger, default=1000000)  # Starting capital
    human_resources = Column(Integer, default=10)  # Starting employees
    reputation_points = Column(Float, default=50.0)
    sustainability_rating = Column(String(2), default="C")
    
    # Stakeholder Satisfaction (0-100)
    stakeholder_satisfaction = Column(JSON, default=dict)
    
    # Current Challenges and Events
    active_challenges = Column(JSON, default=list)
    ongoing_events = Column(JSON, default=list)
    
    # Market Position
    market_share = Column(Float, default=0.0)
    competitor_relations = Column(JSON, default=dict)
    
    # Operational Metrics
    operational_efficiency = Column(Float, default=50.0)
    innovation_score = Column(Float, default=0.0)
    
    player = relationship("Player", back_populates="game_states")

class Decision(Base):
    """Player decisions and their impacts"""
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    scenario_id = Column(String(36), ForeignKey("scenarios.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Decision Details
    choice_made = Column(String(100), nullable=False)
    rationale = Column(Text)
    time_spent = Column(Integer)  # seconds spent deciding
    
    # Impacts and Outcomes
    immediate_impacts = Column(JSON)
    long_term_impacts = Column(JSON)
    stakeholder_reactions = Column(JSON)
    
    # Analysis
    ethical_alignment = Column(Float)  # -1 to 1
    risk_level = Column(Float)  # 0 to 1
    success_rating = Column(Float)  # 0 to 100
    
    player = relationship("Player", back_populates="decisions")
    scenario = relationship("Scenario", back_populates="decisions")

class Scenario(Base):
    """Business scenarios and their parameters"""
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    difficulty_level = Column(Float, nullable=False)
    
    # Scenario Parameters
    stakeholders_affected = Column(JSON, nullable=False)
    possible_approaches = Column(JSON, nullable=False)
    hidden_factors = Column(JSON)
    time_pressure = Column(Integer)  # turns until decision needed
    
    # Success Criteria
    success_metrics = Column(JSON)
    learning_objectives = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    times_used = Column(Integer, default=0)
    average_success = Column(Float)
    
    decisions = relationship("Decision", back_populates="scenario")

class Achievement(Base):
    """Player achievements and badges"""
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    achievement_type = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Achievement Details
    criteria_met = Column(JSON)
    date_earned = Column(DateTime, default=datetime.utcnow)
    associated_stats = Column(JSON)
    
    player = relationship("Player", back_populates="achievements")

class AnalyticsLog(Base):
    """Log of player analytics for ML training"""
    __tablename__ = "analytics_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Analytics Data
    decision_patterns = Column(JSON)
    learning_progress = Column(JSON)
    skill_development = Column(JSON)
    engagement_metrics = Column(JSON)
    
    # ML Features
    feature_vector = Column(JSON)
    labels = Column(JSON)

# Database initialization function
async def init_db(db_url: str):
    """Initialize database with async support"""
    engine = create_async_engine(
        db_url,
        echo=True,  # SQL logging
        pool_size=20,
        max_overflow=10,
        pool_timeout=30
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    return engine

# Session management
async def get_session(engine) -> AsyncSession:
    """Get async database session"""
    async_session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await async_session.close()
