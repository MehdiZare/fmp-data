# tests/test_config.py
from unittest.mock import patch

import pytest

from fmp_data.config import ClientConfig, RateLimitConfig


def test_config_validation():
    """Test configuration validation"""
    with pytest.raises(ValueError):
        ClientConfig(api_key="test_key", timeout=-1)  # Invalid timeout


def test_config_from_env():
    """Test configuration from environment variables"""
    with patch.dict(
        "os.environ",
        {"FMP_API_KEY": "env_key", "FMP_TIMEOUT": "60", "FMP_MAX_RETRIES": "5"},
    ):
        config = ClientConfig.from_env()
        assert config.api_key == "env_key"
        assert config.timeout == 60
        assert config.max_retries == 5


def test_rate_limit_config():
    """Test rate limit configuration"""
    config = RateLimitConfig(
        daily_limit=1000, requests_per_second=5, requests_per_minute=100
    )
    assert config.daily_limit == 1000
    assert config.requests_per_second == 5
    assert config.requests_per_minute == 100
