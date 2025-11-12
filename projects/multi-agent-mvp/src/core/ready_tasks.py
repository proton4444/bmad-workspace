"""
Ready-task identification for task dependency graphs.

Implements instant identification of which tasks agents can claim based on
completion status of their dependencies. Story 1.3 implementation.

Key Function: get_ready_tasks(task_queue)
- Returns list of tasks whose all dependencies have completed successfully
- Task states: pending → ready → in_progress → completed/failed
- Ready-task identification happens within <10ms of dependency completion

Data Structures:
- task_queue: {task_id: {state, dependencies, result}}
- task_states: {pending, ready, in_progress, completed, failed}
"""

from enum import Enum
from typing import Dict, List, Set


class TaskState(Enum):
    """Task execution state machine."""

    PENDING = "pending"  # Not yet ready (dependencies incomplete)
    READY = "ready"  # All dependencies met, can be claimed
    IN_PROGRESS = "in_progress"  # Agent is executing
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Failed execution


def get_ready_tasks(task_queue: Dict[str, Dict]) -> List[str]:
    """
    Return list of tasks currently ready to be claimed by agents.

    A task is "ready" when:
    1. All its dependencies have completed successfully
    2. Its current state is not already in_progress/completed/failed

    Task state format in task_queue:
    {
        "task_id": {
            "state": "pending|ready|in_progress|completed|failed",
            "dependencies": ["task_id_1", "task_id_2"],  # List of task IDs this depends on
            "result": None or {"success": bool, "output": str}
        }
    }

    Args:
        task_queue: Task queue with complete task definitions and states

    Returns:
        List of task IDs that are ready to be claimed. Empty list if no tasks ready.

    Performance:
        AC: <10ms response time for task completion notification

    Example:
        >>> task_queue = {
        ...     "A": {"state": "completed", "dependencies": [], "result": {"success": True}},
        ...     "B": {"state": "pending", "dependencies": ["A"], "result": None},
        ...     "C": {"state": "pending", "dependencies": ["A"], "result": None}
        ... }
        >>> get_ready_tasks(task_queue)
        ["B", "C"]
    """
    if not task_queue:
        return []

    ready = []

    for task_id, task_info in task_queue.items():
        # Skip tasks already in progress or completed
        state = task_info.get("state", "pending")
        if state in [
            TaskState.IN_PROGRESS.value,
            TaskState.COMPLETED.value,
            TaskState.FAILED.value,
        ]:
            continue

        # Check if all dependencies are satisfied
        dependencies = task_info.get("dependencies", [])
        all_deps_ready = _check_dependencies_satisfied(
            task_id, task_queue, dependencies
        )

        if all_deps_ready:
            ready.append(task_id)

    return ready


def _check_dependencies_satisfied(
    task_id: str, task_queue: Dict, dependencies: List[str]
) -> bool:
    """
    Check if all dependencies for a task have completed successfully.

    Args:
        task_id: Task being checked (for debugging)
        task_queue: Full task queue for lookup
        dependencies: List of task IDs this task depends on

    Returns:
        True if all dependencies completed successfully, False otherwise
    """
    if not dependencies:
        # No dependencies means task is ready
        return True

    for dep_id in dependencies:
        if dep_id not in task_queue:
            # Missing dependency - cannot proceed
            return False

        dep_task = task_queue[dep_id]
        dep_state = dep_task.get("state", "pending")

        # Dependency must be completed
        if dep_state != TaskState.COMPLETED.value:
            return False

        # And it must have succeeded
        dep_result = dep_task.get("result")
        if dep_result is None:
            return False

        # Check success flag (could be missing in some cases, treat as failure)
        if not dep_result.get("success", False):
            return False

    return True


def update_task_state(
    task_queue: Dict[str, Dict], task_id: str, new_state: str, result: Dict = None
) -> Dict[str, Dict]:
    """
    Update a task's state and return updated task queue.

    Updates are atomic at the Python level (not thread-safe without external locking).
    For concurrent access, use file locking as implemented in Story 1.5.

    Args:
        task_queue: Current task queue
        task_id: Task to update
        new_state: New state value (pending|ready|in_progress|completed|failed)
        result: Optional result dict with {success: bool, output: str, ...}

    Returns:
        Updated task queue (modified in place, also returned)
    """
    if task_id not in task_queue:
        raise ValueError(f"Task {task_id} not found in queue")

    # Validate state
    valid_states = {state.value for state in TaskState}
    if new_state not in valid_states:
        raise ValueError(f"Invalid state: {new_state}. Must be one of {valid_states}")

    # Update task
    task_queue[task_id]["state"] = new_state
    if result is not None:
        task_queue[task_id]["result"] = result

    return task_queue


def get_ready_tasks_incremental(
    prev_task_queue: Dict, updated_task_queue: Dict
) -> List[str]:
    """
    Identify newly ready tasks after a task state update (optimization).

    This is faster than scanning entire queue when only one task changed.
    Used to implement <10ms response time for ready-task identification.

    Args:
        prev_task_queue: Task queue state before update
        updated_task_queue: Task queue state after update

    Returns:
        List of task IDs that became ready due to the update
    """
    newly_ready = []

    # Find which task was updated
    for task_id, task_info in updated_task_queue.items():
        prev_state = prev_task_queue.get(task_id, {}).get("state", "pending")
        new_state = task_info.get("state", "pending")

        # Skip if state didn't change to completed
        if prev_state == new_state or new_state != TaskState.COMPLETED.value:
            continue

        # This task just completed - find all tasks that depend on it
        for dependent_id, dependent_info in updated_task_queue.items():
            if dependent_id == task_id:
                continue

            # Check if this task depends on the just-completed task
            dependencies = dependent_info.get("dependencies", [])
            if task_id in dependencies:
                # Check if dependent is now ready
                dep_state = dependent_info.get("state", "pending")
                if dep_state == TaskState.PENDING.value:
                    if _check_dependencies_satisfied(
                        dependent_id, updated_task_queue, dependencies
                    ):
                        newly_ready.append(dependent_id)

    return newly_ready


def validate_ready_state(task_queue: Dict[str, Dict], ready_tasks: List[str]) -> bool:
    """
    Validate that a ready-task list is consistent with task queue state.

    Used for testing and debugging to ensure no race conditions or state corruption.

    Args:
        task_queue: Current task queue
        ready_tasks: List of tasks claimed to be ready

    Returns:
        True if ready list is valid and consistent, False otherwise
    """
    # Recompute ready tasks
    computed_ready = set(get_ready_tasks(task_queue))
    given_ready = set(ready_tasks)

    if computed_ready != given_ready:
        return False

    # Validate each ready task
    for task_id in ready_tasks:
        if task_id not in task_queue:
            return False

        task_info = task_queue[task_id]
        state = task_info.get("state", "pending")

        # Ready tasks should be in pending state (not already claimed)
        if state != TaskState.PENDING.value:
            return False

        # All dependencies should be completed
        dependencies = task_info.get("dependencies", [])
        if not _check_dependencies_satisfied(task_id, task_queue, dependencies):
            return False

    return True


def get_blocked_tasks(task_queue: Dict[str, Dict]) -> Dict[str, List[str]]:
    """
    Identify tasks that are blocked and the tasks blocking them.

    Useful for debugging and monitoring system health.
    Returns map of blocked task -> list of incomplete dependencies.

    Args:
        task_queue: Current task queue

    Returns:
        Dict mapping task IDs to list of incomplete dependency task IDs
    """
    blocked = {}

    for task_id, task_info in task_queue.items():
        state = task_info.get("state", "pending")

        # Skip tasks that are completed, failed, or already in progress
        if state in [
            TaskState.IN_PROGRESS.value,
            TaskState.COMPLETED.value,
            TaskState.FAILED.value,
        ]:
            continue

        dependencies = task_info.get("dependencies", [])
        incomplete_deps = []

        for dep_id in dependencies:
            if dep_id not in task_queue:
                incomplete_deps.append(dep_id)  # Missing dependency
                continue

            dep_state = task_queue[dep_id].get("state", "pending")
            dep_result = task_queue[dep_id].get("result")

            # Dependency is incomplete if not completed or not successful
            if dep_state != TaskState.COMPLETED.value or not dep_result.get(
                "success", False
            ):
                incomplete_deps.append(dep_id)

        if incomplete_deps:
            blocked[task_id] = incomplete_deps

    return blocked


def get_task_summary(task_queue: Dict[str, Dict]) -> Dict:
    """
    Generate summary statistics about task queue state.

    Useful for monitoring and debugging.

    Args:
        task_queue: Current task queue

    Returns:
        Dict with counts: {pending, ready, in_progress, completed, failed, blocked}
    """
    summary = {
        "pending": 0,
        "ready": 0,
        "in_progress": 0,
        "completed": 0,
        "failed": 0,
        "total": len(task_queue),
    }

    ready_count = len(get_ready_tasks(task_queue))
    blocked = get_blocked_tasks(task_queue)

    for task_id, task_info in task_queue.items():
        state = task_info.get("state", "pending")
        if state in summary:
            summary[state] += 1

    summary["ready"] = ready_count
    summary["blocked"] = len(blocked)

    return summary
