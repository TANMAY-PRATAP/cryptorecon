"""API v1 Router aggregation."""

from fastapi import APIRouter
from app.api.v1.endpoints import cases, entities, health, traversal, ml, legal

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(cases.router)
api_v1_router.include_router(entities.router)
api_v1_router.include_router(traversal.router)
api_v1_router.include_router(ml.router)
api_v1_router.include_router(legal.router)
