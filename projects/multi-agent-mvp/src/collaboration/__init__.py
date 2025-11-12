"""
Collaboration module for multi-agent cooperative work.

Provides shared context, brainstorming sessions, and collaborative
idea development features.
"""

from .context import (
    ContextManager,
    Idea,
    IdeaCategory,
    SharedContext,
)

__all__ = [
    "SharedContext",
    "Idea",
    "IdeaCategory",
    "ContextManager",
]
