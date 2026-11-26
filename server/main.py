"""Vercel FastAPI entrypoint.

The application lives in `app/main.py`; this re-export keeps the framework
preset happy while the package layout stays importable for tests and the CLI.
"""

from app.main import app

__all__ = ["app"]
