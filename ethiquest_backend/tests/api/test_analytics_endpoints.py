import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid
import json

from app.main import app
from app.services.db_service import DBService
from app.models.database import Player, Decision, GameState
from app.core.analytics.pattern_analyzer import PatternAnalyzer

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
class TestAnalyticsEndpoints:
    """Test suite for analytics-related API endpoints"""

    async def test_get_player_analytics(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test retrieving comprehensive player analytics"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "learning_progress" in data
        assert "skill_progress" in data
        assert "stakeholder_analytics" in data
        assert "decision_patterns" in data
        assert "ethical_profile" in data

    async def test_get_learning_progress(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test retrieving learning progress analytics"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/learning"
        )

        # Assert
        assert response.status_code == 200
        progress = response.json()
        assert "mastered_concepts" in progress
        assert "current_challenges" in progress
        assert "improvement_rate" in progress
        assert "avg_success_rate" in progress
        assert "learning_path_progress" in progress

    async def test_get_skill_progress(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test retrieving skill progress analytics"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/skills"
        )

        # Assert
        assert response.status_code == 200
        skills = response.json()
        assert "skill_levels" in skills
        assert "recent_improvements" in skills
        assert "recommended_focus" in skills
        assert "skill_trajectory" in skills

    async def test_get_stakeholder_analytics(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test retrieving stakeholder relationship analytics"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/stakeholders"
        )

        # Assert
        assert response.status_code == 200
        analytics = response.json()
        assert "stakeholder_impacts" in analytics
        assert "balanced_score" in analytics
        assert "critical_relationships" in analytics
        assert "improvement_opportunities" in analytics

    async def test_get_decision_patterns(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test retrieving decision pattern analysis"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/patterns"
        )

        # Assert
        assert response.status_code == 200
        patterns = response.json()
        assert len(patterns) > 0
        assert all(
            key in patterns[0] for key in [
                "pattern_type",
                "frequency",
                "impact",
                "context"
            ]
        )

    async def test_get_performance_metrics(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_game_state: GameState
    ):
        """Test retrieving performance metrics"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/performance"
        )

        # Assert
        assert response.status_code == 200
        metrics = response.json()
        assert "financial_metrics" in metrics
        assert "reputation_metrics" in metrics
        assert "efficiency_metrics" in metrics
        assert "growth_metrics" in metrics

    async def test_get_comparative_analytics(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test retrieving comparative analytics"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/comparative"
        )

        # Assert
        assert response.status_code == 200
        analytics = response.json()
        assert "peer_comparison" in analytics
        assert "industry_benchmarks" in analytics
        assert "percentile_rankings" in analytics

    async def test_get_trend_analysis(
        self,
        test_client: TestClient,
        sample_player: Player,
        test_db_service: DBService
    ):
        """Test retrieving trend analysis"""
        # Arrange - Create historical data points
        timestamps = [
            datetime.utcnow() - timedelta(days=i)
            for i in range(5)
        ]
        
        for ts in timestamps:
            await test_db_service.create_analytics_log(
                player_id=sample_player.id,
                log_type="performance",
                data={
                    "timestamp": ts.isoformat(),
                    "metrics": {
                        "financial": 100 + (5 * timestamps.index(ts)),
                        "reputation": 75 + (3 * timestamps.index(ts))
                    }
                }
            )

        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/trends",
            params={"days": 5}
        )

        # Assert
        assert response.status_code == 200
        trends = response.json()
        assert "financial_trend" in trends
        assert "reputation_trend" in trends
        assert len(trends["financial_trend"]) == 5

    async def test_get_ethical_profile(
        self,
        test_client: TestClient,
        sample_player: Player,
        sample_decision: Decision
    ):
        """Test retrieving ethical profile analytics"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/ethical-profile"
        )

        # Assert
        assert response.status_code == 200
        profile = response.json()
        assert "ethical_alignment" in profile
        assert "value_priorities" in profile
        assert "decision_consistency" in profile
        assert "stakeholder_consideration" in profile

    async def test_export_analytics(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test analytics export functionality"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/export",
            params={"format": "json"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "analytics_data" in data
        assert "export_metadata" in data
        assert "timestamp" in data["export_metadata"]

    @pytest.mark.parametrize(
        "date_range,expected_count",
        [
            (7, 7),   # Last week
            (30, 30), # Last month
            (90, 90)  # Last quarter
        ]
    )
    async def test_analytics_date_range(
        self,
        test_client: TestClient,
        sample_player: Player,
        date_range: int,
        expected_count: int
    ):
        """Test analytics with different date ranges"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/trends",
            params={"days": date_range}
        )

        # Assert
        assert response.status_code == 200
        trends = response.json()
        assert all(
            len(trend) <= expected_count
            for trend in trends.values()
            if isinstance(trend, list)
        )

    async def test_get_recommendation_analytics(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test retrieving personalized recommendations"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/recommendations"
        )

        # Assert
        assert response.status_code == 200
        recommendations = response.json()
        assert "skill_recommendations" in recommendations
        assert "focus_areas" in recommendations
        assert "learning_paths" in recommendations
        assert "improvement_strategies" in recommendations

    async def test_analytics_caching(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test analytics caching behavior"""
        # Make two quick requests
        response1 = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}"
        )
        response2 = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}"
        )

        # Assert responses are identical (cached)
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()

    async def test_bulk_analytics_retrieval(
        self,
        test_client: TestClient,
        test_db_service: DBService
    ):
        """Test bulk analytics retrieval"""
        # Arrange - Create multiple players
        player_ids = []
        for _ in range(3):
            player = await test_db_service.create_player({
                "username": f"test_user_{uuid.uuid4().hex[:8]}",
                "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
                "created_at": datetime.utcnow(),
                "status": "active"
            })
            player_ids.append(str(player.id))

        # Act
        response = test_client.post(
            "/api/v1/analytics/bulk",
            json={"player_ids": player_ids}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(player_ids)
        assert all(pid in data for pid in player_ids)

    async def test_analytics_webhook(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test analytics webhook functionality"""
        # Arrange
        webhook_url = "https://test.webhook.com/analytics"
        webhook_config = {
            "url": webhook_url,
            "events": ["milestone_reached", "pattern_detected"]
        }

        # Act - Configure webhook
        config_response = test_client.post(
            f"/api/v1/analytics/webhook/configure",
            json=webhook_config
        )

        # Assert
        assert config_response.status_code == 200
        assert config_response.json()["status"] == "configured"

    async def test_realtime_analytics(
        self,
        test_client: TestClient,
        sample_player: Player
    ):
        """Test real-time analytics updates"""
        # Act
        response = test_client.get(
            f"/api/v1/analytics/players/{sample_player.id}/realtime"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "current_session" in data
        assert "active_metrics" in data
        assert "recent_events" in data