import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid
from datetime import datetime, timedelta

from app.main import app
from app.services.db_service import DBService
from app.models.database import Player, Scenario, GameState
from app.core.game.game_logic import GameLogic

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
class TestScenarioEndpoints:
    """Test suite for scenario-related API endpoints"""

    async def test_generate_scenario(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_game_state: GameState
    ):
        """Test scenario generation endpoint"""
        # Act
        response = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "scenario" in data
        assert "game_state" in data
        assert "patterns" in data
        
        scenario = data["scenario"]
        assert scenario["title"] is not None
        assert len(scenario["possible_approaches"]) > 0
        assert "stakeholders_affected" in scenario

    async def test_generate_scenario_with_difficulty(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test scenario generation with specific difficulty"""
        # Act
        response = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}&difficulty=0.8"
        )

        # Assert
        assert response.status_code == 200
        scenario = response.json()["scenario"]
        assert scenario["difficulty_level"] == 0.8
        assert len(scenario["hidden_factors"]) > 0  # Higher difficulty should include hidden factors

    async def test_scenario_caching(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test scenario caching behavior"""
        # Make two quick requests
        response1 = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}"
        )
        response2 = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}"
        )

        # Assert same scenario returned (cached)
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["scenario"]["id"] == response2.json()["scenario"]["id"]

    async def test_submit_decision(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test decision submission endpoint"""
        # Arrange
        decision_data = {
            "choice_made": sample_scenario.possible_approaches[0]["id"],
            "rationale": "Test decision rationale",
            "time_spent": 45
        }

        # Act
        response = test_client.post(
            f"/api/v1/scenarios/{sample_scenario.id}/decisions",
            params={"player_id": sample_player.id},
            json=decision_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "decision" in data
        assert "impacts" in data
        assert "updated_state" in data

    async def test_invalid_decision_submission(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test submission of invalid decision"""
        # Arrange
        invalid_decision = {
            "choice_made": "invalid_approach_id",
            "rationale": "Test rationale",
            "time_spent": -1  # Invalid time
        }

        # Act
        response = test_client.post(
            f"/api/v1/scenarios/{sample_scenario.id}/decisions",
            params={"player_id": sample_player.id},
            json=invalid_decision
        )

        # Assert
        assert response.status_code == 400
        assert "invalid decision" in response.json()["detail"].lower()

    async def test_scenario_analysis(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test scenario analysis endpoint"""
        # Act
        response = test_client.get(
            f"/api/v1/scenarios/{sample_scenario.id}/analysis",
            params={"player_id": sample_player.id}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "potential_outcomes" in data
        assert "risk_analysis" in data
        assert "stakeholder_analysis" in data
        assert "opportunity_analysis" in data

    async def test_scenario_time_constraint(
        self,
        test_client: TestClient,
        test_db_service: DBService,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test scenario time constraint enforcement"""
        # Arrange - set scenario created time to past time constraint
        async with test_db_service.session() as session:
            await session.execute(
                f"""
                UPDATE scenarios 
                SET created_at = '{datetime.utcnow() - timedelta(hours=2)}'
                WHERE id = '{sample_scenario.id}'
                """
            )
            await session.commit()

        decision_data = {
            "choice_made": sample_scenario.possible_approaches[0]["id"],
            "rationale": "Late decision",
            "time_spent": 30
        }

        # Act
        response = test_client.post(
            f"/api/v1/scenarios/{sample_scenario.id}/decisions",
            params={"player_id": sample_player.id},
            json=decision_data
        )

        # Assert
        assert response.status_code == 400
        assert "time constraint exceeded" in response.json()["detail"].lower()

    async def test_concurrent_decisions(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test handling of concurrent decision submissions"""
        # Arrange
        decision_data = {
            "choice_made": sample_scenario.possible_approaches[0]["id"],
            "rationale": "Concurrent test",
            "time_spent": 30
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as ac:
            responses = await asyncio.gather(
                *[
                    ac.post(
                        f"/api/v1/scenarios/{sample_scenario.id}/decisions",
                        params={"player_id": sample_player.id},
                        json=decision_data
                    )
                    for _ in range(3)
                ],
                return_exceptions=True
            )

        # Assert
        success_count = sum(
            1 for r in responses
            if not isinstance(r, Exception) and r.status_code == 200
        )
        assert success_count == 1  # Only one decision should be accepted

    async def test_scenario_difficulty_progression(
        self,
        test_client: TestClient,
        sample_player: Player,
        test_db_service: DBService
    ):
        """Test scenario difficulty progression based on player performance"""
        # Get initial scenario
        response1 = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}"
        )
        initial_difficulty = response1.json()["scenario"]["difficulty_level"]

        # Submit successful decision
        decision_data = {
            "choice_made": response1.json()["scenario"]["possible_approaches"][0]["id"],
            "rationale": "Good decision",
            "time_spent": 45
        }
        await test_client.post(
            f"/api/v1/scenarios/{response1.json()['scenario']['id']}/decisions",
            params={"player_id": sample_player.id},
            json=decision_data
        )

        # Get next scenario
        response2 = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}"
        )
        new_difficulty = response2.json()["scenario"]["difficulty_level"]

        # Assert difficulty increased
        assert new_difficulty > initial_difficulty

    async def test_scenario_adaptation(
        self,
        test_client: TestClient,
        sample_player: Player,
        test_db_service: DBService
    ):
        """Test scenario adaptation based on player patterns"""
        # Generate initial scenario
        response1 = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}"
        )
        scenario1 = response1.json()["scenario"]

        # Submit decision focusing on employee stakeholders
        decision_data = {
            "choice_made": scenario1["possible_approaches"][0]["id"],
            "rationale": "Prioritizing employees",
            "time_spent": 30,
            "stakeholder_focus": "employees"
        }
        await test_client.post(
            f"/api/v1/scenarios/{scenario1['id']}/decisions",
            params={"player_id": sample_player.id},
            json=decision_data
        )

        # Generate next scenario
        response2 = test_client.get(
            f"/api/v1/scenarios/generate?player_id={sample_player.id}"
        )
        scenario2 = response2.json()["scenario"]

        # Assert scenario adapted to focus more on employee stakeholders
        assert "employees" in scenario2["stakeholders_affected"]
        assert len([
            approach for approach in scenario2["possible_approaches"]
            if "employee" in approach["description"].lower()
        ]) > 0

    @pytest.mark.parametrize(
        "invalid_field,invalid_value",
        [
            ("choice_made", None),
            ("time_spent", -1),
            ("rationale", ""),
            ("stakeholder_focus", "invalid_stakeholder")
        ]
    )
    async def test_decision_validation(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario,
        invalid_field: str,
        invalid_value: any
    ):
        """Test validation of decision data"""
        # Arrange
        decision_data = {
            "choice_made": sample_scenario.possible_approaches[0]["id"],
            "rationale": "Test rationale",
            "time_spent": 30
        }
        decision_data[invalid_field] = invalid_value

        # Act
        response = test_client.post(
            f"/api/v1/scenarios/{sample_scenario.id}/decisions",
            params={"player_id": sample_player.id},
            json=decision_data
        )

        # Assert
        assert response.status_code == 422
        assert invalid_field in str(response.json()["detail"]).lower()