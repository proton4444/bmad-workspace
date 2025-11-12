"""
Core dependency engine module for Agent Society multi-agent system.

This module provides task dependency management with cycle detection,
topological sorting, and ready-task identification.
"""

from .conditional_branching import (
    ConditionType,
    add_condition_to_task,
    check_conditional_dependencies_satisfied,
    evaluate_condition,
    get_conditional_successors,
    get_execution_paths,
    get_ready_tasks_with_conditions,
    simulate_execution,
    validate_conditional_graph,
)
from .ready_tasks import (
    TaskState,
    get_blocked_tasks,
    get_ready_tasks,
    get_ready_tasks_incremental,
    get_task_summary,
    update_task_state,
    validate_ready_state,
)
from .topological_sort import get_parallel_batches, topological_sort, validate_ordering

__all__ = [
    "topological_sort",
    "get_parallel_batches",
    "validate_ordering",
    "get_ready_tasks",
    "update_task_state",
    "get_ready_tasks_incremental",
    "validate_ready_state",
    "get_blocked_tasks",
    "get_task_summary",
    "TaskState",
    "add_condition_to_task",
    "evaluate_condition",
    "check_conditional_dependencies_satisfied",
    "get_ready_tasks_with_conditions",
    "get_conditional_successors",
    "validate_conditional_graph",
    "get_execution_paths",
    "simulate_execution",
    "ConditionType",
]
