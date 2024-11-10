from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete, and_, or_, desc
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from ..models.database import (
    Base,
    Player,
    GameState,
    Decision,
    Scenario,
    Achievement,
    AnalyticsLog
)
from ..config import Settings, get_settings

logger = logging.getLogger(__name__)

class DBService:
    """Database service for handling all database operations"""
    
    _instance = None
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = None
        self.session_factory = None
        self._setup_task = None
        
    @classmethod
    async def get_instance(cls) -> 'DBService':
        """Get singleton instance of DBService"""
        if cls._instance is None:
            settings = get_settings()
            cls._instance = cls(settings)
            await cls._instance.setup()
        return cls._instance

    async def setup(self):
        """Initialize database connection"""
        if self._setup_task is not None:
            await self._setup_task
            return

        self._setup_task = asyncio.create_task(self._setup())
        await self._setup_task

    async def _setup(self):
        """Setup database connection and session factory"""
        try:
            # Create engine
            self.engine = create_async_engine(
                self.settings.DATABASE_URL,
                echo=self.settings.DB_ECHO,
                pool_size=self.settings.DB_POOL_SIZE,
                max_overflow=self.settings.DB_MAX_OVERFLOW,
                pool_timeout=self.settings.DB_POOL_TIMEOUT
            )

            # Create session factory
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Create tables (if they don't exist)
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Database connection established successfully")

        except Exception as e:
            logger.error(f"Database setup error: {str(e)}")
            raise

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Get database session"""
        if self.session_factory is None:
            await self.setup()

        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def check_health(self) -> bool:
        """Check database health"""
        try:
            async with self.session() as session:
                await session.execute(select(1))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    # Player Operations
    async def create_player(self, player: Player) -> Player:
        """Create new player"""
        async with self.session() as session:
            session.add(player)
            await session.flush()
            return player

    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        async with self.session() as session:
            result = await session.execute(
                select(Player).where(Player.id == player_id)
            )
            return result.scalars().first()

    async def update_player(
        self,
        player_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Player]:
        """Update player"""
        async with self.session() as session:
            result = await session.execute(
                update(Player)
                .where(Player.id == player_id)
                .values(**updates)
                .returning(Player)
            )
            await session.commit()
            return result.scalars().first()

    # Game State Operations
    async def create_game_state(self, game_state: GameState) -> GameState:
        """Create new game state"""
        async with self.session() as session:
            session.add(game_state)
            await session.flush()
            return game_state

    async def get_game_state(
        self,
        player_id: str
    ) -> Optional[GameState]:
        """Get player's game state"""
        async with self.session() as session:
            result = await session.execute(
                select(GameState)
                .where(GameState.player_id == player_id)
                .order_by(desc(GameState.timestamp))
                .limit(1)
            )
            return result.scalars().first()

    async def update_game_state(
        self,
        player_id: str,
        updates: Dict[str, Any]
    ) -> Optional[GameState]:
        """Update game state"""
        async with self.session() as session:
            result = await session.execute(
                update(GameState)
                .where(GameState.player_id == player_id)
                .values(**updates)
                .returning(GameState)
            )
            await session.commit()
            return result.scalars().first()

    # Decision Operations
    async def create_decision(
        self,
        player_id: str,
        scenario_id: str,
        decision: Dict[str, Any]
    ) -> Decision:
        """Record player decision"""
        async with self.session() as session:
            db_decision = Decision(
                player_id=player_id,
                scenario_id=scenario_id,
                **decision
            )
            session.add(db_decision)
            await session.flush()
            return db_decision

    async def get_player_decisions(
        self,
        player_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Decision]:
        """Get player's decisions"""
        async with self.session() as session:
            query = select(Decision).where(
                Decision.player_id == player_id
            ).order_by(desc(Decision.timestamp))
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            result = await session.execute(query)
            return result.scalars().all()

    # Scenario Operations
    async def create_scenario(self, scenario: Scenario) -> Scenario:
        """Create new scenario"""
        async with self.session() as session:
            session.add(scenario)
            await session.flush()
            return scenario

    async def get_scenario(
        self,
        scenario_id: str
    ) -> Optional[Scenario]:
        """Get scenario by ID"""
        async with self.session() as session:
            result = await session.execute(
                select(Scenario).where(Scenario.id == scenario_id)
            )
            return result.scalars().first()

    async def get_player_scenarios(
        self,
        player_id: str,
        limit: Optional[int] = None
    ) -> List[Scenario]:
        """Get scenarios player has encountered"""
        async with self.session() as session:
            query = (
                select(Scenario)
                .join(Decision)
                .where(Decision.player_id == player_id)
                .order_by(desc(Decision.timestamp))
            )
            
            if limit:
                query = query.limit(limit)
                
            result = await session.execute(query)
            return result.scalars().all()

    # Achievement Operations
    async def create_achievement(
        self,
        player_id: str,
        achievement_type: str,
        data: Dict[str, Any]
    ) -> Achievement:
        """Create new achievement"""
        async with self.session() as session:
            achievement = Achievement(
                player_id=player_id,
                achievement_type=achievement_type,
                **data
            )
            session.add(achievement)
            await session.flush()
            return achievement

    async def get_player_achievements(
        self,
        player_id: str
    ) -> List[Achievement]:
        """Get player's achievements"""
        async with self.session() as session:
            result = await session.execute(
                select(Achievement)
                .where(Achievement.player_id == player_id)
                .order_by(desc(Achievement.date_earned))
            )
            return result.scalars().all()

    # Analytics Operations
    async def create_analytics_log(
        self,
        player_id: str,
        log_type: str,
        data: Dict[str, Any]
    ) -> AnalyticsLog:
        """Create analytics log entry"""
        async with self.session() as session:
            log = AnalyticsLog(
                player_id=player_id,
                log_type=log_type,
                data=data,
                timestamp=datetime.utcnow()
            )
            session.add(log)
            await session.flush()
            return log

    async def get_player_analytics(
        self,
        player_id: str,
        log_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AnalyticsLog]:
        """Get player's analytics logs"""
        async with self.session() as session:
            query = select(AnalyticsLog).where(
                AnalyticsLog.player_id == player_id
            )
            
            if log_type:
                query = query.where(AnalyticsLog.log_type == log_type)
            if start_date:
                query = query.where(AnalyticsLog.timestamp >= start_date)
            if end_date:
                query = query.where(AnalyticsLog.timestamp <= end_date)
                
            query = query.order_by(desc(AnalyticsLog.timestamp))
            
            result = await session.execute(query)
            return result.scalars().all()

    # Batch Operations
    async def bulk_create_scenarios(
        self,
        scenarios: List[Scenario]
    ) -> List[Scenario]:
        """Bulk create scenarios"""
        async with self.session() as session:
            session.add_all(scenarios)
            await session.flush()
            return scenarios

    async def bulk_update_game_states(
        self,
        updates: List[Dict[str, Any]]
    ) -> List[GameState]:
        """Bulk update game states"""
        async with self.session() as session:
            results = []
            for update in updates:
                result = await session.execute(
                    update(GameState)
                    .where(GameState.player_id == update['player_id'])
                    .values(**update['updates'])
                    .returning(GameState)
                )
                results.append(result.scalars().first())
            await session.commit()
            return results

    # Cleanup Operations
    async def cleanup_old_data(
        self,
        days_old: int = 30
    ) -> Dict[str, int]:
        """Clean up old data"""
        async with self.session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old analytics logs
            analytics_result = await session.execute(
                delete(AnalyticsLog)
                .where(AnalyticsLog.timestamp < cutoff_date)
            )
            
            # Delete old scenarios
            scenarios_result = await session.execute(
                delete(Scenario)
                .where(and_(
                    Scenario.created_at < cutoff_date,
                    Scenario.is_active == False
                ))
            )
            
            await session.commit()
            
            return {
                "analytics_deleted": analytics_result.rowcount,
                "scenarios_deleted": scenarios_result.rowcount
            }

    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()

# Initialize global database service
db_service = None

async def get_db() -> DBService:
    """Get database service instance"""
    global db_service
    if db_service is None:
        db_service = await DBService.get_instance()
    return db_service