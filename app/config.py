"""CryptoRecon Configuration Module.

Loads configuration from environment variables and provides typed settings
using Pydantic BaseSettings.
"""

from functools import lru_cache
from typing import List, Optional
import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Graceful fallback for pure pydantic / basic environments
    from pydantic import BaseModel as BaseSettings  # type: ignore
    SettingsConfigDict = dict  # type: ignore


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "CryptoRecon"
    VERSION: str = "4.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "true").lower() in ("true", "1") and not bool(os.getenv("VERCEL"))
    REDIS_TIMEOUT_SECONDS: int = 1

    # Multi-Chain RPC Providers
    ETH_RPC_URL: str = os.getenv("ETH_RPC_URL", "https://eth.llamarpc.com")
    BSC_RPC_URL: str = os.getenv("BSC_RPC_URL", "https://binance.llamarpc.com")
    POLYGON_RPC_URL: str = os.getenv("POLYGON_RPC_URL", "https://polygon.llamarpc.com")
    ARBITRUM_RPC_URL: str = os.getenv("ARBITRUM_RPC_URL", "https://arbitrum.llamarpc.com")
    OPTIMISM_RPC_URL: str = os.getenv("OPTIMISM_RPC_URL", "https://optimism.llamarpc.com")
    TRON_GRID_API_URL: str = os.getenv("TRON_GRID_API_URL", "https://api.trongrid.io")
    TRON_GRID_API_KEY: Optional[str] = os.getenv("TRON_GRID_API_KEY", None)
    BITCOIN_RPC_URL: str = os.getenv("BITCOIN_RPC_URL", "https://blockstream.info/api")
    DOGECOIN_RPC_URL: str = os.getenv("DOGECOIN_RPC_URL", "https://api.blockcypher.com/v1/doge/main")
    DOGECOIN_API_KEY: Optional[str] = os.getenv("DOGECOIN_API_KEY", None)
    ETHERSCAN_API_KEY: Optional[str] = os.getenv("ETHERSCAN_API_KEY", None)

    # Multicall3 Smart Contract Address (standard across EVM chains)
    MULTICALL3_ADDRESS: str = "0xcA11bde05977b3631167028862bE2a173976CA11"
    MULTICALL_MAX_BATCH_SIZE: int = 50

    # Bloom Filter & Known Entities
    BLOOM_FILTER_EXPECTED_ELEMENTS: int = 150000
    BLOOM_FILTER_FALSE_POSITIVE_RATE: float = 0.001

    # Forensic Traversal Settings (CFR & Mules)
    CFR_MIN_ABSOLUTE_FLOW_USDT: float = 50.0
    CFR_BRANCH_DILUTION_FACTOR: float = 1.5
    MULE_CLUSTER_THRESHOLD_SPLITS: int = 5

    # Neo4j Graph Database
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    ) if hasattr(BaseSettings, "model_config") else None


@lru_cache()
def get_settings() -> Settings:
    """Singleton getter for application settings."""
    return Settings()
