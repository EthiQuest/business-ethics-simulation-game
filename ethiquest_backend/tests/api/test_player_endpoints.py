import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid
from datetime import datetime

from app.main import app
from app.services.db_service import DBService
from app.models.database import Player

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
class TestPlayerEndpoints:
    """Test suite for player-related API endpoints"""

    async def test_create_player(self, test_client: TestClient):
        """Test player creation endpoint"""
        # Arrange
        player_data = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "TestPassword123!",
            "company_name": "Test Company"
        }

        # Act
        response = test_client.post("/api/v1/players/", json=player_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == player_data["username"]
        assert data["email"] == player_data["email"]
        assert "id" in data
        assert "password" not in data  # Password should not be in response

    async def test_create_player_duplicate_username(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test creating player with duplicate username"""
        # Arrange
        player_data = {
            "username": sample_player.username,
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "TestPassword123!"
        }

        # Act
        response = test_client.post("/api/v1/players/", json=player_data)

        # Assert
        assert response.status_code == 400
        assert "username already registered" in response.json()["detail"].lower()

    async def test_get_player(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test getting player details"""
        # Act
        response = test_client.get(f"/api/v1/players/{sample_player.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_player.id)
        assert data["username"] == sample_player.username

    async def test_get_nonexistent_player(self, test_client: TestClient):
        """Test getting non-existent player"""
        # Act
        response = test_client.get(f"/api/v1/players/{uuid.uuid4()}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_player(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test updating player details"""
        # Arrange
        update_data = {
            "company_name": "Updated Company",
            "industry": "Technology"
        }

        # Act
        response = test_client.put(
            f"/api/v1/players/{sample_player.id}",
            json=update_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == update_data["company_name"]
        assert data["industry"] == update_data["industry"]

    async def test_get_player_state(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_game_state
    ):
        """Test getting player's game state"""
        # Act
        response = test_client.get(f"/api/v1/players/{sample_player.id}/state")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == str(sample_player.id)
        assert "financial_resources" in data
        assert "stakeholder_satisfaction" in data

    async def test_get_player_statistics(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision,
        sample_achievement
    ):
        """Test getting player statistics"""
        # Act
        response = test_client.get(
            f"/api/v1/players/{sample_player.id}/statistics"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data
        assert "total_decisions" in data
        assert "achievements" in data
        assert "stakeholder_relations" in data

    async def test_validate_player_data(self, test_client: TestClient):
        """Test player data validation"""
        # Arrange
        invalid_data = {
            "username": "u",  # Too short
            "email": "invalid_email",
            "password": "weak"
        }

        # Act
        response = test_client.post("/api/v1/players/", json=invalid_data)

        # Assert
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("username" in e["loc"] for e in errors)
        assert any("email" in e["loc"] for e in errors)
        assert any("password" in e["loc"] for e in errors)

    async def test_player_authentication(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test player authentication"""
        # Arrange
        auth_data = {
            "username": sample_player.username,
            "password": "TestPassword123!"
        }

        # Act
        response = test_client.post("/api/v1/auth/login", data=auth_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.parametrize(
        "field,value,expected_status",
        [
            ("username", "", 422),
            ("email", "not_an_email", 422),
            ("password", "short", 422),
            ("company_name", "a" * 101, 422),  # Too long
            ("industry", "", 422)
        ]
    )
    async def test_player_validation_cases(
        self,
        test_client: TestClient,
        field: str,
        value: str,
        expected_status: int
    ):
        """Test various validation cases for player data"""
        # Arrange
        player_data = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "TestPassword123!",
            "company_name": "Test Company",
            "industry": "Technology"
        }
        player_data[field] = value

        # Act
        response = test_client.post("/api/v1/players/", json=player_data)

        # Assert
        assert response.status_code == expected_status
        if expected_status == 422:
            errors = response.json()["detail"]
            assert any(field in e["loc"] for e in errors)

    async def test_concurrent_player_creation(
        self,
        test_client: TestClient
    ):
        """Test concurrent player creation with same username"""
        # Arrange
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        player_data = {
            "username": username,
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "TestPassword123!"
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Send multiple concurrent requests
            responses = await asyncio.gather(
                *[
                    ac.post("/api/v1/players/", json=player_data)
                    for _ in range(3)
                ],
                return_exceptions=True
            )

        # Assert
        success_count = sum(
            1 for r in responses
            if not isinstance(r, Exception) and r.status_code == 200
        )
        assert success_count == 1  # Only one should succeed

    async def test_rate_limiting(
        self,
        test_client: TestClient
    ):
        """Test rate limiting on player endpoints"""
        # Arrange
        player_data = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "TestPassword123!"
        }

        # Act
        responses = []
        for _ in range(61):  # Exceed rate limit (60 per minute)
            response = test_client.post("/api/v1/players/", json=player_data)
            responses.append(response)

        # Assert
        assert any(r.status_code == 429 for r in responses)  # Some should be rate limited

    async def test_player_deletion_cascade(
        self,
        test_client: TestClient,
        test_db_service: DBService,
        sample_player: Player
    ):
        """Test cascading deletion of player data"""
        # Act
        response = test_client.delete(f"/api/v1/players/{sample_player.id}")

        # Assert
        assert response.status_code == 200
        
        # Verify cascading deletion
        async with test_db_service.session() as session:
            # Check related records
            game_states = await session.execute(
                f"SELECT COUNT(*) FROM game_states WHERE player_id = '{sample_player.id}'"
            )
            decisions = await session.execute(
                f"SELECT COUNT(*) FROM decisions WHERE player_id = '{sample_player.id}'"
            )
            achievements = await session.execute(
                f"SELECT COUNT(*) FROM achievements WHERE player_id = '{sample_player.id}'"
            )

            assert game_states.scalar() == 0
            assert decisions.scalar() == 0
            assert achievements.scalar() == 0