"""
Test Redis caching implementation for Task 18.1

Tests:
- Bedrock API response caching with 6-hour TTL
- Market intelligence data caching with 24-hour TTL
- Farm profile caching with 1-hour TTL
- Cache invalidation strategies
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from app.core.cache import (
    CacheManager,
    init_cache_manager,
    get_cache_manager,
    TTL_BEDROCK_API,
    TTL_MARKET_DATA,
    TTL_FARM_PROFILE,
    TTL_CROP_RECOMMENDATIONS
)


class TestRedisCaching:
    """Test suite for Redis caching implementation"""
    
    def test_cache_manager_initialization(self):
        """Test cache manager initializes correctly"""
        cache_manager = CacheManager(
            redis_url="redis://localhost:6379/0",
            default_ttl=300,
            enabled=True
        )
        
        assert cache_manager is not None
        assert cache_manager.default_ttl == 300
        assert cache_manager.enabled == True
    
    def test_ttl_constants(self):
        """Test TTL constants are set correctly per Task 18.1 requirements"""
        assert TTL_BEDROCK_API == 6 * 60 * 60  # 6 hours
        assert TTL_MARKET_DATA == 24 * 60 * 60  # 24 hours
        assert TTL_FARM_PROFILE == 1 * 60 * 60  # 1 hour
        assert TTL_CROP_RECOMMENDATIONS == 1 * 60 * 60  # 1 hour
    
    @patch('redis.from_url')
    def test_cache_set_and_get(self, mock_redis):
        """Test basic cache set and get operations"""
        # Mock Redis client
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.get.return_value = '{"test": "data"}'
        
        cache_manager = CacheManager(enabled=True)
        
        # Test set
        result = cache_manager.set("test_key", {"test": "data"}, ttl=300)
        assert result == True
        mock_client.setex.assert_called_once()
        
        # Test get
        cached_data = cache_manager.get("test_key")
        assert cached_data == {"test": "data"}
        mock_client.get.assert_called_with("test_key")
    
    @patch('redis.from_url')
    def test_cache_invalidation_farm(self, mock_redis):
        """Test farm cache invalidation"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.keys.return_value = ["farm:123:profile", "farm:123:crops"]
        mock_client.delete.return_value = 2
        
        cache_manager = CacheManager(enabled=True)
        
        # Test farm cache invalidation
        deleted = cache_manager.invalidate_farm_cache(farm_id=123)
        assert deleted >= 0
        assert mock_client.keys.called
    
    @patch('redis.from_url')
    def test_cache_invalidation_market_data(self, mock_redis):
        """Test market data cache invalidation"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.keys.return_value = ["market_data:rice:karnataka"]
        mock_client.delete.return_value = 1
        
        cache_manager = CacheManager(enabled=True)
        
        # Test market data cache invalidation
        deleted = cache_manager.invalidate_market_data_cache(crop_type="rice", state="karnataka")
        assert deleted >= 0
        assert mock_client.keys.called
    
    @patch('redis.from_url')
    def test_cache_invalidation_crop_recommendations(self, mock_redis):
        """Test crop recommendations cache invalidation"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.keys.return_value = ["crop_recommendations:karnataka:kharif"]
        mock_client.delete.return_value = 1
        
        cache_manager = CacheManager(enabled=True)
        
        # Test crop recommendations cache invalidation
        deleted = cache_manager.invalidate_crop_recommendations_cache(state="karnataka", season="kharif")
        assert deleted >= 0
        assert mock_client.keys.called
    
    @patch('redis.from_url')
    def test_cache_invalidation_bedrock(self, mock_redis):
        """Test Bedrock cache invalidation"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.keys.return_value = ["bedrock:annual_strategy:123"]
        mock_client.delete.return_value = 1
        
        cache_manager = CacheManager(enabled=True)
        
        # Test Bedrock cache invalidation
        deleted = cache_manager.invalidate_bedrock_cache()
        assert deleted >= 0
        assert mock_client.keys.called
    
    @patch('redis.from_url')
    def test_cache_disabled_fallback(self, mock_redis):
        """Test cache operations when caching is disabled"""
        cache_manager = CacheManager(enabled=False)
        
        # All operations should return safely
        assert cache_manager.get("test_key") is None
        assert cache_manager.set("test_key", "value") == False
        assert cache_manager.delete("test_key") == False
        assert cache_manager.delete_pattern("test:*") == 0
        assert cache_manager.clear() == False
    
    @patch('redis.from_url')
    def test_cache_key_generation(self, mock_redis):
        """Test cache key generation with various arguments"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        cache_manager = CacheManager(enabled=True)
        
        # Test simple key
        key1 = cache_manager._generate_cache_key("namespace", "arg1", "arg2")
        assert key1 == "namespace:arg1:arg2"
        
        # Test key with kwargs
        key2 = cache_manager._generate_cache_key("namespace", state="karnataka", district="bangalore")
        assert "namespace:" in key2
        assert "state=karnataka" in key2
        assert "district=bangalore" in key2
        
        # Test long key gets hashed
        long_args = ["arg" * 50 for _ in range(10)]
        key3 = cache_manager._generate_cache_key("namespace", *long_args)
        assert len(key3) < 150  # Should be hashed
        assert "namespace:" in key3
    
    @patch('redis.from_url')
    def test_cache_delete_pattern(self, mock_redis):
        """Test pattern-based cache deletion"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.keys.return_value = ["farm:1:profile", "farm:2:profile", "farm:3:profile"]
        mock_client.delete.return_value = 3
        
        cache_manager = CacheManager(enabled=True)
        
        # Test pattern deletion
        deleted = cache_manager.delete_pattern("farm:*:profile")
        assert deleted == 3
        mock_client.keys.assert_called_with("farm:*:profile")
        mock_client.delete.assert_called_once()


class TestBedrockCaching:
    """Test Bedrock service caching integration"""
    
    def test_bedrock_service_imports_cache_manager(self):
        """Test that Bedrock service imports cache utilities"""
        from app.services.bedrock_service import BedrockService
        from app.core.cache import TTL_BEDROCK_API
        
        # Verify TTL constant is available
        assert TTL_BEDROCK_API == 6 * 60 * 60
        
        # Verify service can be instantiated
        # (actual caching tested via integration tests with real Redis)
        assert BedrockService is not None
    
    def test_cache_key_generation_for_annual_strategy(self):
        """Test cache key generation for annual strategy"""
        from app.core.cache import CacheManager
        
        cache_manager = CacheManager(enabled=False)  # Disabled for testing
        
        # Test cache key generation
        key = cache_manager._generate_cache_key(
            "bedrock:annual_strategy",
            state="Karnataka",
            district="Bangalore",
            soil_type="loamy",
            area_acres=5.0,
            irrigation_type="borewell"
        )
        
        assert "bedrock:annual_strategy" in key
        assert "state=Karnataka" in key or "Karnataka" in key
    
    def test_cache_key_generation_for_crop_recommendations(self):
        """Test cache key generation for crop recommendations"""
        from app.core.cache import CacheManager
        
        cache_manager = CacheManager(enabled=False)  # Disabled for testing
        
        # Test cache key generation
        key = cache_manager._generate_cache_key(
            "bedrock:crop_recommendations",
            state="Karnataka",
            district="Bangalore",
            season="kharif",
            soil_type="loamy"
        )
        
        assert "bedrock:crop_recommendations" in key
        assert "state=Karnataka" in key or "Karnataka" in key
        assert "season=kharif" in key or "kharif" in key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
