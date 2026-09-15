"""
Vercel Python serverless entry point.

Vercel's zero-config Python runtime turns any file under /api that exports a
WSGI `app` into a function - this file just re-exports the real Flask app
from backend/app.py so there's a single source of truth for the API.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app import app  # noqa: E402
