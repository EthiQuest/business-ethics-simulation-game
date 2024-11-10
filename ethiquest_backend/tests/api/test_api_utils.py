import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
import json
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.api.utils.pagination import paginate_results
from app.api.utils.filtering import apply_filters
from app.api.utils.sorting import apply_sorting
from app.api.utils.caching import cache_response, clear_cache
from app.api.utils.rate_limiting import check_rate_limit
from app.api.utils.validation import validate_uuid, validate_date_range
from app.api.utils.response_formatting import format_response

@pytest.fixture
def test_client():
    return TestClient(app)

class TestAPIUtils:
    """Test suite for API utility functions"""

    @pytest.mark.asyncio
    async def test_pagination(self):
        """Test pagination utility"""
        # Arrange
        items = [{"id": i, "value": f"item_{i}"} for i in range(100)]
        
        # Act
        page1 = await paginate_results(items, page=1, page_size=10)
        page2 = await paginate_results(items, page=2, page_size=10)
        
        # Assert
        assert len(page1["items"]) == 10
        assert page1["total"] == 100
        assert page1["page"] == 1
        assert page1["items"][0]["id"] == 0
        
        assert len(page2["items"]) == 10
        assert page2["items"][0]["id"] == 10

    @pytest.mark.asyncio
    async def test_filtering(self):
        """Test filtering utility"""
        # Arrange
        items = [
            {"type": "A", "value": 10},
            {"type": "B", "value": 20},
            {"type": "A", "value": 30}
        ]
        
        filters = {
            "type": "A",
            "value_gt": 15
        }
        
        # Act
        filtered = await apply_filters(items, filters)
        
        # Assert
        assert len(filtered) == 1
        assert filtered[0]["value"] == 30

    @pytest.mark.asyncio
    async def test_sorting(self):
        """Test sorting utility"""
        # Arrange
        items = [
            {"name": "C", "value": 1},
            {"name": "A", "value": 3},
            {"name": "B", "value": 2}
        ]
        
        # Act
        sorted_asc = await apply_sorting(items, sort_by="name", order="asc")
        sorted_desc = await apply_sorting(items, sort_by="name", order="desc")
        
        # Assert
        assert sorted_asc[0]["name"] == "A"
        assert sorted_desc[0]["name"] == "C"

    @pytest.mark.asyncio
    async def test_caching(self):
        """Test caching utility"""
        # Arrange
        cache_key = f"test_key_{uuid.uuid4()}"
        test_data = {"value": "test"}
        
        # Act
        # Cache data
        await cache_response(cache_key, test_data, ttl=60)
        
        # Get cached data
        cached = await cache_response.get(cache_key)
        
        # Clear cache
        await clear_cache(cache_key)
        cleared = await cache_response.get(cache_key)
        
        # Assert
        assert cached == test_data
        assert cleared is None

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting utility"""
        # Arrange
        client_id = str(uuid.uuid4())
        limit = 5
        window = 60
        
        # Act & Assert
        # Should allow initial requests
        for _ in range(limit):
            allowed = await check_rate_limit(client_id, limit, window)
            assert allowed is True
        
        # Should block additional requests
        blocked = await check_rate_limit(client_id, limit, window)
        assert blocked is False

    def test_uuid_validation(self):
        """Test UUID validation utility"""
        # Arrange
        valid_uuid = str(uuid.uuid4())
        invalid_uuid = "not-a-uuid"
        
        # Act & Assert
        assert validate_uuid(valid_uuid) is True
        assert validate_uuid(invalid_uuid) is False

    def test_date_range_validation(self):
        """Test date range validation utility"""
        # Arrange
        now = datetime.utcnow()
        valid_start = now - timedelta(days=7)
        valid_end = now
        invalid_start = now + timedelta(days=1)
        
        # Act & Assert
        assert validate_date_range(valid_start, valid_end) is True
        
        with pytest.raises(HTTPException) as exc_info:
            validate_date_range(invalid_start, valid_end)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    def test_response_formatting(self):
        """Test response formatting utility"""
        # Arrange
        data = {
            "nested": {
                "value": datetime.utcnow(),
                "list": [1, 2, 3]
            }
        }
        
        # Act
        formatted = format_response(data)
        
        # Assert
        assert isinstance(formatted["nested"]["value"], str)
        assert json.dumps(formatted)  # Should be JSON serializable

    @pytest.mark.asyncio
    async def test_pagination_edge_cases(self):
        """Test pagination with edge cases"""
        # Arrange
        items = [{"id": i} for i in range(5)]
        
        # Act & Assert
        # Empty page
        empty_page = await paginate_results(items, page=99, page_size=10)
        assert len(empty_page["items"]) == 0
        
        # Negative page
        with pytest.raises(HTTPException) as exc_info:
            await paginate_results(items, page=-1, page_size=10)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        
        # Zero page size
        with pytest.raises(HTTPException) as exc_info:
            await paginate_results(items, page=1, page_size=0)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_filtering_complex(self):
        """Test complex filtering scenarios"""
        # Arrange
        items = [
            {"type": "A", "value": 10, "tags": ["x", "y"]},
            {"type": "B", "value": 20, "tags": ["y", "z"]},
            {"type": "C", "value": 30, "tags": ["x", "z"]}
        ]
        
        # Act
        # Multiple conditions
        multi_filter = await apply_filters(
            items,
            {
                "value_gt": 15,
                "tags_contains": "z"
            }
        )
        
        # OR conditions
        or_filter = await apply_filters(
            items,
            {
                "type_in": ["A", "B"],
                "_operator": "or"
            }
        )
        
        # Assert
        assert len(multi_filter) == 2  # B and C items
        assert len(or_filter) == 2     # A and B items

    @pytest.mark.asyncio
    async def test_sorting_complex(self):
        """Test complex sorting scenarios"""
        # Arrange
        items = [
            {"name": "A", "value": 3, "priority": 1},
            {"name": "B", "value": 2, "priority": 2},
            {"name": "C", "value": 1, "priority": 1}
        ]
        
        # Act
        # Multiple field sorting
        multi_sorted = await apply_sorting(
            items,
            sort_by=["priority", "value"],
            order=["asc", "desc"]
        )
        
        # Custom sorting
        custom_sorted = await apply_sorting(
            items,
            sort_by="value",
            order="asc",
            custom_order={"name": ["C", "B", "A"]}
        )
        
        # Assert
        assert multi_sorted[0]["name"] == "A"  # Priority 1, Value 3
        assert custom_sorted[0]["name"] == "C"

    @pytest.mark.asyncio
    async def test_caching_complex(self):
        """Test complex caching scenarios"""
        # Arrange
        base_key = f"test_key_{uuid.uuid4()}"
        
        # Act & Assert
        # Test pattern-based cache clearing
        await cache_response(f"{base_key}_1", "data1", ttl=60)
        await cache_response(f"{base_key}_2", "data2", ttl=60)
        
        # Clear by pattern
        await clear_cache(f"{base_key}_*")
        
        cached1 = await cache_response.get(f"{base_key}_1")
        cached2 = await cache_response.get(f"{base_key}_2")
        
        assert cached1 is None
        assert cached2 is None

    @pytest.mark.asyncio
    async def test_rate_limiting_dynamic(self):
        """Test dynamic rate limiting"""
        # Arrange
        client_id = str(uuid.uuid4())
        
        # Different limits for different actions
        limits = {
            "read": {"limit": 100, "window": 60},
            "write": {"limit": 20, "window": 60},
            "delete": {"limit": 5, "window": 60}
        }
        
        # Act & Assert
        for action, config in limits.items():
            # Should allow up to limit
            for _ in range(config["limit"]):
                allowed = await check_rate_limit(
                    f"{client_id}_{action}",
                    config["limit"],
                    config["window"]
                )
                assert allowed is True
            
            # Should block after limit
            blocked = await check_rate_limit(
                f"{client_id}_{action}",
                config["limit"],
                config["window"]
            )
            assert blocked is False

    def test_response_formatting_complex(self):
        """Test complex response formatting scenarios"""
        # Arrange
        now = datetime.utcnow()
        complex_data = {
            "datetime": now,
            "date_only": now.date(),
            "nested": {
                "datetime": now,
                "list": [
                    {"datetime": now},
                    {"date": now.date()}
                ]
            },
            "bytes": b"binary data",
            "custom_obj": type("CustomObj", (), {"__str__": lambda x: "custom"})()
        }
        
        # Act
        formatted = format_response(complex_data)
        
        # Assert
        assert isinstance(formatted["datetime"], str)
        assert isinstance(formatted["date_only"], str)
        assert isinstance(formatted["nested"]["datetime"], str)
        assert isinstance(formatted["nested"]["list"][0]["datetime"], str)
        assert isinstance(formatted["nested"]["list"][1]["date"], str)
        assert isinstance(formatted["bytes"], str)
        assert formatted["custom_obj"] == "custom"
        assert json.dumps(formatted)  # Should be JSON serializable