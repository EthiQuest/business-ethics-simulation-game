import pytest
from fastapi.testclient import TestClient
import time
from datetime import datetime, timedelta
from unittest.mock import patch
import psutil
import json

from app.main import app
from app.services.db_service import DBService
from app.core.cache.cache_service import CacheService
from app.monitoring.metrics_collector import MetricsCollector
from app.monitoring.health_checker import HealthChecker
from app.monitoring.system_stats import SystemStats

@pytest.fixture
def test_client():
    return TestClient(app)

class TestMonitoringEndpoints:
    """Test suite for monitoring endpoints"""

    async def test_health_check(self, test_client: TestClient):
        """Test basic health check endpoint"""
        # Act
        response = test_client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data

        # Check service statuses
        services = data["services"]
        assert "database" in services
        assert "cache" in services
        assert "ai_service" in services

    async def test_detailed_health_check(self, test_client: TestClient):
        """Test detailed health check endpoint"""
        # Act
        response = test_client.get("/health/detailed")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check detailed service information
        assert "database" in data
        assert "connection_pool" in data["database"]
        assert "response_time" in data["database"]
        
        assert "cache" in data
        assert "memory_usage" in data["cache"]
        assert "hit_rate" in data["cache"]
        
        assert "ai_service" in data
        assert "response_time" in data["ai_service"]
        assert "success_rate" in data["ai_service"]

    async def test_system_metrics(self, test_client: TestClient):
        """Test system metrics endpoint"""
        # Act
        response = test_client.get("/metrics/system")

        # Assert
        assert response.status_code == 200
        metrics = response.json()
        
        # Check system metrics
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
        assert "network_stats" in metrics
        assert "process_stats" in metrics

    async def test_application_metrics(self, test_client: TestClient):
        """Test application metrics endpoint"""
        # Act
        response = test_client.get("/metrics/application")

        # Assert
        assert response.status_code == 200
        metrics = response.json()
        
        # Check application metrics
        assert "request_count" in metrics
        assert "error_rate" in metrics
        assert "response_times" in metrics
        assert "active_users" in metrics
        assert "db_connection_pool" in metrics

    async def test_prometheus_metrics(self, test_client: TestClient):
        """Test Prometheus metrics endpoint"""
        # Act
        response = test_client.get("/metrics/prometheus")

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; version=0.0.4"
        
        # Check for expected Prometheus metric types
        metrics_text = response.text
        assert "# HELP" in metrics_text
        assert "# TYPE" in metrics_text
        assert "ethiquest_requests_total" in metrics_text
        assert "ethiquest_response_time_seconds" in metrics_text

    async def test_service_dependencies(self, test_client: TestClient):
        """Test service dependencies endpoint"""
        # Act
        response = test_client.get("/health/dependencies")

        # Assert
        assert response.status_code == 200
        deps = response.json()
        
        # Check service dependencies
        assert "database" in deps
        assert "cache" in deps
        assert "ai_service" in deps
        
        # Check dependency details
        for service in deps.values():
            assert "status" in service
            assert "last_check" in service
            assert "latency" in service

    @pytest.mark.asyncio
    async def test_metrics_collection(
        self,
        test_client: TestClient,
        test_db_service: DBService
    ):
        """Test metrics collection over time"""
        # Arrange
        collector = MetricsCollector()
        start_time = datetime.utcnow()
        
        # Generate some activity
        for _ in range(3):
            test_client.get("/health")
            await test_db_service.check_health()
            time.sleep(0.1)
        
        # Act
        metrics = await collector.collect_metrics(
            start_time=start_time,
            end_time=datetime.utcnow()
        )

        # Assert
        assert metrics["total_requests"] >= 3
        assert metrics["database_queries"] >= 3
        assert "average_response_time" in metrics
        assert "error_count" in metrics

    async def test_error_rate_monitoring(self, test_client: TestClient):
        """Test error rate monitoring"""
        # Act
        # Generate some errors
        for _ in range(3):
            test_client.get("/non-existent-endpoint")
        
        response = test_client.get("/metrics/errors")

        # Assert
        assert response.status_code == 200
        error_metrics = response.json()
        
        assert error_metrics["error_count"] >= 3
        assert "error_rate" in error_metrics
        assert "error_types" in error_metrics
        assert "404" in error_metrics["error_types"]

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, test_client: TestClient):
        """Test performance monitoring endpoints"""
        # Act
        response = test_client.get("/metrics/performance")

        # Assert
        assert response.status_code == 200
        perf_metrics = response.json()
        
        # Check performance metrics
        assert "response_time_p95" in perf_metrics
        assert "response_time_p99" in perf_metrics
        assert "throughput" in perf_metrics
        assert "concurrent_users" in perf_metrics

    async def test_resource_usage_monitoring(self, test_client: TestClient):
        """Test resource usage monitoring"""
        # Act
        response = test_client.get("/metrics/resources")

        # Assert
        assert response.status_code == 200
        resources = response.json()
        
        # Check resource metrics
        assert "cpu" in resources
        assert resources["cpu"]["usage_percent"] >= 0
        
        assert "memory" in resources
        assert resources["memory"]["used_percent"] >= 0
        
        assert "disk" in resources
        assert resources["disk"]["used_percent"] >= 0

    @pytest.mark.asyncio
    async def test_cache_monitoring(
        self,
        test_client: TestClient,
        test_db_service: DBService
    ):
        """Test cache monitoring"""
        # Arrange - Generate some cache activity
        cache_key = "test_key"
        await CacheService.set(cache_key, "test_value", ttl=60)
        await CacheService.get(cache_key)
        
        # Act
        response = test_client.get("/metrics/cache")

        # Assert
        assert response.status_code == 200
        cache_metrics = response.json()
        
        assert cache_metrics["hit_count"] > 0
        assert "miss_count" in cache_metrics
        assert "hit_rate" in cache_metrics
        assert "memory_usage" in cache_metrics

    async def test_alerts(self, test_client: TestClient):
        """Test alerts endpoint"""
        # Act
        response = test_client.get("/monitoring/alerts")

        # Assert
        assert response.status_code == 200
        alerts = response.json()
        
        assert "active_alerts" in alerts
        assert "alert_history" in alerts
        for alert in alerts["alert_history"]:
            assert "type" in alert
            assert "severity" in alert
            assert "timestamp" in alert
            assert "description" in alert

    @pytest.mark.asyncio
    async def test_system_health_threshold(
        self,
        test_client: TestClient
    ):
        """Test system health thresholds"""
        # Mock high CPU usage
        with patch('psutil.cpu_percent', return_value=95.0):
            response = test_client.get("/health/system")
            data = response.json()
            
            assert data["status"] == "warning"
            assert "high_cpu_usage" in data["warnings"]

    async def test_metrics_export(self, test_client: TestClient):
        """Test metrics export functionality"""
        # Act
        response = test_client.get(
            "/metrics/export",
            params={"format": "json"}
        )

        # Assert
        assert response.status_code == 200
        exported_metrics = response.json()
        
        assert "system_metrics" in exported_metrics
        assert "application_metrics" in exported_metrics
        assert "timestamp" in exported_metrics
        assert "version" in exported_metrics

    @pytest.mark.asyncio
    async def test_monitoring_dashboard_data(
        self,
        test_client: TestClient
    ):
        """Test monitoring dashboard data endpoint"""
        # Act
        response = test_client.get("/monitoring/dashboard")

        # Assert
        assert response.status_code == 200
        dashboard_data = response.json()
        
        assert "system_health" in dashboard_data
        assert "application_metrics" in dashboard_data
        assert "recent_alerts" in dashboard_data
        assert "service_status" in dashboard_data