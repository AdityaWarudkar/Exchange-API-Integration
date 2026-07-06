from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "exchange-api-order-execution-sandbox"
    environment: str = "local"
    secret_key: str = Field(default="dev-only-secret-change-me", min_length=16)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql+asyncpg://exchange:exchange@localhost:5432/exchange"
    redis_url: str = "redis://localhost:6379/0"

    binance_base_url: str = "https://api.binance.com"
    bybit_base_url: str = "https://api.bybit.com"

    paper_starting_balance: float = 100_000.0
    fee_rate: float = 0.0004
    rate_limit_per_minute: int = 120
    market_symbols: list[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    enable_background_workers: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
