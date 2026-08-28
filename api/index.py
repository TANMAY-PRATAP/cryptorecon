"""Vercel Serverless Entrypoint for CryptoRecon FastAPI Backend."""

import os
import sys

# Ensure root directory is on Python path in Vercel Serverless environment
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.main import app

# Vercel ASGI handler export
app = app
