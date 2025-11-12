"""
Agent system module for Agent Society multi-agent system.

Provides personality-driven agent definitions, task affinity scoring,
agent state management, and personality consistency verification.
"""

from .affinity import (
    TaskComplexity,
    TaskType,
    get_best_agent_for_task,
    score_task_affinity,
)
from .consistency import (
    AgentOutput,
    get_agent_outputs_by_name,
    get_all_agent_outputs,
    get_personality_recognition_guide,
)
from .personality import (
    ARCHITECT_PERSONALITY,
    EXECUTOR_PERSONALITY,
    EXPERIMENTER_PERSONALITY,
    AgentPersonality,
    AgentRole,
    get_personality_by_name,
)
from .state import AgentState, create_agent_state, get_agent_stats, update_agent_history

__all__ = [
    "AgentPersonality",
    "AgentRole",
    "ARCHITECT_PERSONALITY",
    "EXECUTOR_PERSONALITY",
    "EXPERIMENTER_PERSONALITY",
    "get_personality_by_name",
    "score_task_affinity",
    "get_best_agent_for_task",
    "TaskType",
    "TaskComplexity",
    "AgentState",
    "create_agent_state",
    "update_agent_history",
    "get_agent_stats",
    "AgentOutput",
    "get_agent_outputs_by_name",
    "get_all_agent_outputs",
    "get_personality_recognition_guide",
]
