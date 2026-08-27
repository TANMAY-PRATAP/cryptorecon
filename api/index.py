"""Vercel Serverless Entrypoint for CryptoRecon FastAPI Backend."""

from app.main import app

# Vercel ASGI handler export
app = app
