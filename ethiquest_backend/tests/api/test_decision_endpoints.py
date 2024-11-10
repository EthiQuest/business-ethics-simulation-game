import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid
from datetime import datetime, timedelta

from app.main import app
from app.services.db_service import DBService
from app.models.database import Player, Scenario, Decision, GameState

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
class TestDecisionEndpoints:
    """Test suite for decision-related API endpoints"""

    async def test_submit_basic_decision(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test basic decision submission"""
        # Arrange
        decision_data = {
            "choice_made": sample_scenario.possible_approaches[0]["id"],
            "rationale": "Test decision rationale",
            "time_spent": 45,
            "stakeholder_focus": ["employees", "community"],
            "ethical_considerations": ["fairness", "transparency"]
        }

        # Act
        response = test_client.post(
            f"/api/v1/decisions/",
            params={
                "player_id": sample_player.id,
                "scenario_id": sample_scenario.id
            },
            json=decision_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "impacts" in data
        assert "state_changes" in data
        assert data["choice_made"] == decision_data["choice_made"]

    async def test_get_decision_history(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test retrieving decision history"""
        # Act
        response = test_client.get(
            f"/api/v1/decisions/history/{sample_player.id}"
        )

        # Assert
        assert response.status_code == 200
        decisions = response.json()
        assert len(decisions) > 0
        assert all(
            required_field in decisions[0]
            for required_field in [
                "id", "timestamp", "choice_made", "impacts"
            ]
        )

    async def test_get_decision_details(
        self,
        test_client: TestClient,
        sample_decision: Decision
    ):
        """Test retrieving detailed decision information"""
        # Act
        response = test_client.get(
            f"/api/v1/decisions/{sample_decision.id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_decision.id)
        assert "immediate_impacts" in data
        assert "long_term_impacts" in data
        assert "stakeholder_reactions" in data

    async def test_decision_impact_calculation(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario,
        sample_game_state: GameState
    ):
        """Test decision impact calculation endpoint"""
        # Arrange
        decision_data = {
            "choice_made": sample_scenario.possible_approaches[0]["id"],
            "stakeholder_focus": ["employees"],
            "ethical_considerations": ["fairness"]
        }

        # Act
        response = test_client.post(
            f"/api/v1/decisions/calculate-impact",
            params={
                "player_id": sample_player.id,
                "scenario_id": sample_scenario.id
            },
            json=decision_data
        )

        # Assert
        assert response.status_code == 200
        impacts = response.json()
        assert "financial_impact" in impacts
        assert "stakeholder_impacts" in impacts
        assert "reputation_impact" in impacts
        assert "risk_assessment" in impacts

    async def test_decision_validation(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_scenario: Scenario
    ):
        """Test decision validation"""
        # Arrange - Invalid decision data
        invalid_decisions = [
            {
                # Missing required field
                "rationale": "Test rationale",
                "time_spent": 45
            },
            {
                # Invalid choice
                "choice_made": "invalid_choice",
                "rationale": "Test rationale",
                "time_spent": 45
            },
            {
                # Negative time spent
                "choice_made": sample_scenario.possible_approaches[0]["id"],
                "rationale": "Test rationale",
                "time_spent": -10
            }
        ]

        # Act & Assert
        for invalid_data in invalid_decisions:
            response = test_client.post(
                f"/api/v1/decisions/",
                params={
                    "player_id": sample_player.id,
                    "scenario_id": sample_scenario.id
                },
                json=invalid_data
            )
            assert response.status_code == 422

    async def test_decision_analytics(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test decision analytics endpoint"""
        # Act
        response = test_client.get(
            f"/api/v1/decisions/analytics/{sample_player.id}"
        )

        # Assert
        assert response.status_code == 200
        analytics = response.json()
        assert "decision_patterns" in analytics
        assert "stakeholder_preferences" in analytics
        assert "ethical_alignment" in analytics
        assert "risk_profile" in analytics

    async def test_batch_decision_retrieval(
        self,
        test_client: TestClient,
        sample_player: Player,
        test_db_service: DBService
    ):
        """Test batch retrieval of decisions"""
        # Arrange - Create multiple decisions
        decision_ids = []
        for _ in range(3):
            decision = await test_db_service.create_decision(
                player_id=sample_player.id,
                scenario_id=str(uuid.uuid4()),
                decision={
                    "choice_made": "test_choice",
                    "rationale": "batch test",
                    "time_spent": 30
                }
            )
            decision_ids.append(str(decision.id))

        # Act
        response = test_client.post(
            f"/api/v1/decisions/batch",
            json={"decision_ids": decision_ids}
        )

        # Assert
        assert response.status_code == 200
        decisions = response.json()
        assert len(decisions) == len(decision_ids)
        assert all(d["id"] in decision_ids for d in decisions)

    async def test_decision_undo(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision,
        sample_game_state: GameState
    ):
        """Test decision undo functionality"""
        # Act
        response = test_client.post(
            f"/api/v1/decisions/{sample_decision.id}/undo",
            params={"player_id": sample_player.id}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "reverted_state" in data
        assert "undo_impacts" in data

        # Verify game state reverted
        state_response = test_client.get(
            f"/api/v1/players/{sample_player.id}/state"
        )
        current_state = state_response.json()
        assert current_state == data["reverted_state"]

    async def test_decision_export(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test decision export functionality"""
        # Act
        response = test_client.get(
            f"/api/v1/decisions/export/{sample_player.id}",
            params={"format": "json"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "decisions" in data
        assert "metadata" in data
        assert "export_date" in data["metadata"]

    async def test_concurrent_decision_submission(
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
                        "/api/v1/decisions/",
                        params={
                            "player_id": sample_player.id,
                            "scenario_id": sample_scenario.id
                        },
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
        assert success_count == 1  # Only one decision should succeed

    @pytest.mark.parametrize(
        "filter_params,expected_count",
        [
            ({"stakeholder_focus": "employees"}, 1),
            ({"ethical_rating_min": 0.8}, 2),
            ({"date_from": datetime.utcnow().date()}, 3),
            ({"impact_type": "positive"}, 2)
        ]
    )
    async def test_decision_filtering(
        self,
        test_client: TestClient,
        sample_player: Player,
        filter_params: dict,
        expected_count: int
    ):
        """Test decision filtering with various parameters"""
        # Act
        response = test_client.get(
            f"/api/v1/decisions/history/{sample_player.id}",
            params=filter_params
        )

        # Assert
        assert response.status_code == 200
        decisions = response.json()
        assert len(decisions) == expected_count

    async def test_decision_metrics(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test decision metrics calculation"""
        # Act
        response = test_client.get(
            f"/api/v1/decisions/metrics/{sample_player.id}"
        )

        # Assert
        assert response.status_code == 200
        metrics = response.json()
        assert "average_time_spent" in metrics
        assert "ethical_rating_distribution" in metrics
        assert "stakeholder_impact_summary" in metrics
        assert "decision_outcome_distribution" in metrics