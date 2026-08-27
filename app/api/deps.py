"""FastAPI Dependency Injection Providers."""

from typing import Generator
from fastapi import Depends
from app.config import Settings, get_settings
from app.core.bloom_filter import InvertedBloomFilter, get_bloom_filter
from app.storage.redis_client import RedisManager, get_redis_manager
from app.storage.memory_store import MemoryCaseStore, get_memory_store


def get_app_settings() -> Settings:
    """Provide application configuration settings."""
    return get_settings()


def get_filter() -> InvertedBloomFilter:
    """Provide the initialized Bloom Filter & Tag Attribution instance."""
    return get_bloom_filter()


def get_redis() -> RedisManager:
    """Provide Redis queue and cache manager."""
    return get_redis_manager()


def get_case_store() -> MemoryCaseStore:
    """Provide the memory/state store for investigation cases."""
    return get_memory_store()
