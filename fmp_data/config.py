# fmp_data/config.py
"""Configuration for FMP client."""
from pydantic_settings import BaseSettings


class FMPSettings(BaseSettings):
    """Configuration settings for FMP client."""

    api_key: str
    base_url: str = "https://financialmodelingprep.com/api/v3"
    timeout: int = 30
    rate_limit_per_minute: int = 300
    cache_ttl: int = 300

    class Config:
        env_prefix = "FMP_"
