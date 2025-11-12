"""
Web API for multi-agent workflow system.

Provides FastAPI-based REST endpoints for:
- Workflow management (create, list, get, delete)
- Workflow execution (start, monitor, results)
- Agent management (list, details)
- Persistence (save, load, export)
- Health and metrics
"""

from src.api.app import app

__all__ = ["app"]
