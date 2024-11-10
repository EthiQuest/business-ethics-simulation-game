import pytest
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any

from app.services.db_service import DBService
from app.models.database import Player, GameState, Scenario, Decision, Achievement

class TestDBService:
    """Test suite for database service operations"""

    @pytest.mark.asyncio
    async def test_create_player(self, test_db_service: DBService):
        """Test player creation"""
        # Arrange
        player_data = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "status": "active",
        }

        # Act
        player = await test_db_service.create_player(player_data)

        # Assert
        assert player.id is not None
        assert player.username == player_data["username"]
        assert player.email == player_data["email"]
        assert player.status == "active"

    @pytest.mark.asyncio
    async def test_get_player(self, test_db_service: DBService, sample_player: Player):
        """Test retrieving player"""
        # Act
        retrieved_player = await test_db_service.get_player(sample_player.id)

        # Assert
        assert retrieved_player is not None
        assert retrieved_player.id == sample_player.id
        assert retrieved_player.username == sample_player.username

    @pytest.mark.asyncio
    async def test_update_player(self, test_db_service: DBService, sample_player: Player):
        """Test updating player"""
        # Arrange
        updates = {
            "current_level": 2,
            "experience_points": 1000,
            "company_size": "medium"
        }

        # Act
        updated_player = await test_db_service.update_player(sample_player.id, updates)

        # Assert
        assert updated_player.current_level == 2
        assert updated_player.experience_points == 1000
        assert updated_player.company_size == "medium"

    @pytest.mark.asyncio
    async def test_create_game_state(
        self,
        test_db_service: DBService,
        sample_player: Player
    ):
        """Test game state creation"""
        # Arrange
        state_data = {
            "player_id": sample_player.id,
            "financial_resources": 1000000,
            "human_resources": 10,
            "reputation_points": 50.0,
            "sustainability_rating": "B",
            "stakeholder_satisfaction": {
                "employees": 75,
                "customers": 80
            }
        }

        # Act
        game_state = await test_db_service.create_game_state(state_data)

        # Assert
        assert game_state.id is not None
        assert game_state.player_id == sample_player.id
        assert game_state.financial_resources == 1000000
        assert game_state.stakeholder_satisfaction["employees"] == 75

    @pytest.mark.asyncio
    async def test_get_game_state(
        self,
        test_db_service: DBService,
        sample_game_state: GameState
    ):
        """Test retrieving game state"""
        # Act
        state = await test_db_service.get_game_state(sample_game_state.player_id)

        # Assert
        assert state is not None
        assert state.player_id == sample_game_state.player_id
        assert state.financial_resources == sample_game_state.financial_resources

    @pytest.mark.asyncio
    async def test_create_scenario(self, test_db_service: DBService):
        """Test scenario creation"""
        # Arrange
        scenario_data = {
            "title": "Test Scenario",
            "description": "Test description",
            "category": "ethics",
            "difficulty_level": 0.7,
            "stakeholders_affected": ["employees", "community"],
            "possible_approaches": [
                {
                    "id": "approach_1",
                    "title": "Approach 1",
                    "description": "Description 1"
                }
            ]
        }

        # Act
        scenario = await test_db_service.create_scenario(scenario_data)

        # Assert
        assert scenario.id is not None
        assert scenario.title == "Test Scenario"
        assert len(scenario.possible_approaches) == 1

    @pytest.mark.asyncio
    async def test_create_decision(
        self,
        test_db_service: DBService,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test decision creation"""
        # Arrange
        decision_data = {
            "player_id": sample_player.id,
            "scenario_id": sample_scenario.id,
            "choice_made": "approach_1",
            "time_spent": 45,
            "immediate_impacts": {
                "financial": -10,
                "reputation": 5
            }
        }

        # Act
        decision = await test_db_service.create_decision(
            player_id=sample_player.id,
            scenario_id=sample_scenario.id,
            decision=decision_data
        )

        # Assert
        assert decision.id is not None
        assert decision.player_id == sample_player.id
        assert decision.choice_made == "approach_1"

    @pytest.mark.asyncio
    async def test_get_player_decisions(
        self,
        test_db_service: DBService,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test retrieving player decisions"""
        # Act
        decisions = await test_db_service.get_player_decisions(sample_player.id)

        # Assert
        assert len(decisions) > 0
        assert decisions[0].player_id == sample_player.id

    @pytest.mark.asyncio
    async def test_create_achievement(
        self,
        test_db_service: DBService,
        sample_player: Player
    ):
        """Test achievement creation"""
        # Arrange
        achievement_data = {
            "achievement_type": "milestone",
            "name": "First Decision",
            "description": "Made first decision",
            "criteria_met": {"decisions": 1}
        }

        # Act
        achievement = await test_db_service.create_achievement(
            player_id=sample_player.id,
            achievement_type="milestone",
            data=achievement_data
        )

        # Assert
        assert achievement.id is not None
        assert achievement.player_id == sample_player.id
        assert achievement.achievement_type == "milestone"

    @pytest.mark.asyncio
    async def test_get_player_achievements(
        self,
        test_db_service: DBService,
        sample_player: Player,
        sample_achievement: Achievement
    ):
        """Test retrieving player achievements"""
        # Act
        achievements = await test_db_service.get_player_achievements(sample_player.id)

        # Assert
        assert len(achievements) > 0
        assert achievements[0].player_id == sample_player.id

    @pytest.mark.asyncio
    async def test_create_analytics_log(
        self,
        test_db_service: DBService,
        sample_player: Player,
        mock_analytics_data: Dict[str, Any]
    ):
        """Test analytics log creation"""
        # Act
        log = await test_db_service.create_analytics_log(
            player_id=sample_player.id,
            log_type="decision_analysis",
            data=mock_analytics_data
        )

        # Assert
        assert log.id is not None
        assert log.player_id == sample_player.id
        assert log.log_type == "decision_analysis"
        assert log.data == mock_analytics_data

    @pytest.mark.asyncio
    async def test_get_player_analytics(
        self,
        test_db_service: DBService,
        sample_player: Player,
        mock_analytics_data: Dict[str, Any]
    ):
        """Test retrieving player analytics"""
        # Arrange
        await test_db_service.create_analytics_log(
            player_id=sample_player.id,
            log_type="decision_analysis",
            data=mock_analytics_data
        )

        # Act
        logs = await test_db_service.get_player_analytics(
            player_id=sample_player.id,
            log_type="decision_analysis"
        )

        # Assert
        assert len(logs) > 0
        assert logs[0].player_id == sample_player.id
        assert logs[0].data == mock_analytics_data

    @pytest.mark.asyncio
    async def test_bulk_operations(
        self,
        test_db_service: DBService
    ):
        """Test bulk operations"""
        # Arrange
        scenarios = [
            {
                "title": f"Bulk Scenario {i}",
                "description": f"Description {i}",
                "category": "ethics",
                "difficulty_level": 0.7,
                "stakeholders_affected": ["employees"],
                "possible_approaches": []
            }
            for i in range(3)
        ]

        # Act
        created_scenarios = await test_db_service.bulk_create_scenarios(scenarios)

        # Assert
        assert len(created_scenarios) == 3
        assert all(s.id is not None for s in created_scenarios)

    @pytest.mark.asyncio
    async def test_cleanup_old_data(
        self,
        test_db_service: DBService,
        sample_player: Player,
        mock_analytics_data: Dict[str, Any]
    ):
        """Test cleaning up old data"""
        # Arrange
        old_date = datetime.utcnow() - timedelta(days=31)
        
        # Create old analytics log
        await test_db_service.create_analytics_log(
            player_id=sample_player.id,
            log_type="old_log",
            data=mock_analytics_data
        )
        
        # Manually update timestamp to make it old
        async with test_db_service.session() as session:
            await session.execute(
                f"UPDATE analytics_logs SET timestamp = '{old_date}' " +
                f"WHERE player_id = '{sample_player.id}'"
            )
            await session.commit()

        # Act
        result = await test_db_service.cleanup_old_data(days_old=30)

        # Assert
        assert result["analytics_deleted"] > 0

    @pytest.mark.asyncio
    async def test_database_health_check(self, test_db_service: DBService):
        """Test database health check"""
        # Act
        is_healthy = await test_db_service.check_health()

        # Assert
        assert is_healthy is True