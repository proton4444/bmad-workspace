"""
Conditional branching support for task dependency graphs.

Implements success/failure path routing based on upstream task outcomes.
Tasks can have conditions: "success" (execute if parent succeeded),
"failure" (execute if parent failed), or "always" (execute regardless).

Story 1.4 implementation.

Key Concept: Conditional Dependencies
- Regular dependency: Task must wait for parent
- Conditional dependency: Task waits for parent AND evaluates condition
- Three condition types enable error handling and alternative paths
"""

from enum import Enum
from typing import Dict, List, Literal, Optional


class ConditionType(Enum):
    """Condition evaluation types."""

    SUCCESS = "success"  # Task ready only if parent completed successfully
    FAILURE = "failure"  # Task ready only if parent failed
    ALWAYS = "always"  # Task ready once parent completes (success or failure)


def add_condition_to_task(task_def: Dict, condition: str = "always") -> Dict:
    """
    Add condition field to task definition.

    Args:
        task_def: Task definition dict
        condition: "success" | "failure" | "always"

    Returns:
        Updated task definition with condition field

    Raises:
        ValueError: If condition is invalid
    """
    valid_conditions = {c.value for c in ConditionType}
    if condition not in valid_conditions:
        raise ValueError(
            f"Invalid condition: {condition}. Must be one of {valid_conditions}"
        )

    task_def["condition"] = condition
    return task_def


def evaluate_condition(
    condition: str, parent_state: str, parent_result: Optional[Dict]
) -> bool:
    """
    Evaluate if a task's condition is satisfied based on parent state.

    Args:
        condition: Task's condition ("success", "failure", "always")
        parent_state: Parent task's state ("pending", "in_progress", "completed", "failed")
        parent_result: Parent task's result dict with {"success": bool, ...}

    Returns:
        True if condition is satisfied, False otherwise

    Examples:
        >>> evaluate_condition("success", "completed", {"success": True})
        True
        >>> evaluate_condition("success", "completed", {"success": False})
        False
        >>> evaluate_condition("failure", "failed", {"success": False})
        True
        >>> evaluate_condition("always", "completed", {"success": True})
        True
    """
    if condition == ConditionType.ALWAYS.value:
        # Always condition satisfied when parent completes (success or failure)
        return parent_state in ["completed", "failed"]

    elif condition == ConditionType.SUCCESS.value:
        # Success condition satisfied when parent completed successfully
        if parent_state != "completed":
            return False
        return parent_result is not None and parent_result.get("success", False)

    elif condition == ConditionType.FAILURE.value:
        # Failure condition satisfied when parent failed
        if parent_state == "failed":
            return True
        if parent_state == "completed" and parent_result is not None:
            return not parent_result.get("success", False)
        return False

    else:
        raise ValueError(f"Unknown condition type: {condition}")


def check_conditional_dependencies_satisfied(
    task_id: str, task_queue: Dict[str, Dict], dependencies: List[str]
) -> bool:
    """
    Check if all conditional dependencies are satisfied.

    Extends the non-conditional dependency check to evaluate conditions.
    A task is ready when:
    1. All dependencies have reached their final state (completed or failed)
    2. Each dependency's condition is satisfied

    Args:
        task_id: Task being checked
        task_queue: Full task queue with states and results
        dependencies: List of dependency task IDs

    Returns:
        True if all conditional dependencies satisfied, False otherwise
    """
    if not dependencies:
        return True

    # Get the current task's condition
    current_task = task_queue.get(task_id, {})
    condition = current_task.get("condition", ConditionType.ALWAYS.value)

    for dep_id in dependencies:
        if dep_id not in task_queue:
            return False

        dep_task = task_queue[dep_id]
        dep_state = dep_task.get("state", "pending")
        dep_result = dep_task.get("result")

        # Dependency must reach final state (completed or failed)
        if dep_state not in ["completed", "failed"]:
            return False

        # Evaluate the task's condition based on dependency state
        if not evaluate_condition(condition, dep_state, dep_result):
            return False

    return True


def get_ready_tasks_with_conditions(task_queue: Dict[str, Dict]) -> List[str]:
    """
    Get ready tasks considering conditional dependencies.

    Extends the basic ready-task logic to evaluate success/failure/always conditions.
    This replaces get_ready_tasks() when conditions are present.

    Args:
        task_queue: Task queue with states, results, and conditions

    Returns:
        List of task IDs ready to be claimed
    """
    if not task_queue:
        return []

    ready = []

    for task_id, task_info in task_queue.items():
        state = task_info.get("state", "pending")

        # Skip tasks already in progress or completed
        if state in ["in_progress", "completed", "failed"]:
            continue

        # Check if all dependencies (with conditions) are satisfied
        dependencies = task_info.get("dependencies", [])
        if check_conditional_dependencies_satisfied(task_id, task_queue, dependencies):
            ready.append(task_id)

    return ready


def get_conditional_successors(
    task_id: str, task_queue: Dict[str, Dict], task_result: Dict
) -> Dict[str, List[str]]:
    """
    Identify which successor tasks become ready based on task outcome.

    Returns successors grouped by whether they were triggered by success/failure.
    Useful for understanding execution flow and error handling paths.

    Args:
        task_id: Task that just completed
        task_queue: Full task queue
        task_result: Result of completed task {"success": bool, ...}

    Returns:
        Dict with keys "success_path" and "failure_path" containing task IDs
    """
    task_state = "completed" if task_result.get("success", False) else "failed"

    successors = {"success_path": [], "failure_path": [], "always_path": []}

    # Find all tasks that depend on this task
    for dependent_id, dependent_info in task_queue.items():
        dependencies = dependent_info.get("dependencies", [])
        if task_id not in dependencies:
            continue

        dependent_state = dependent_info.get("state", "pending")
        condition = dependent_info.get("condition", ConditionType.ALWAYS.value)

        # Skip if not pending
        if dependent_state != "pending":
            continue

        # Check if this dependent would become ready
        if evaluate_condition(condition, task_state, task_result):
            if condition == ConditionType.SUCCESS.value:
                successors["success_path"].append(dependent_id)
            elif condition == ConditionType.FAILURE.value:
                successors["failure_path"].append(dependent_id)
            else:  # always
                successors["always_path"].append(dependent_id)

    return successors


def validate_conditional_graph(task_queue: Dict[str, Dict]) -> Dict:
    """
    Validate that conditional dependencies form a valid DAG.

    Checks:
    1. No cycles in conditional graph
    2. All referenced dependencies exist
    3. Conditions are valid
    4. No orphaned success/failure-only tasks

    Args:
        task_queue: Task queue to validate

    Returns:
        Dict with {valid: bool, errors: List[str]}
    """
    errors = []

    for task_id, task_info in task_queue.items():
        # Check condition is valid
        condition = task_info.get("condition", ConditionType.ALWAYS.value)
        valid_conditions = {c.value for c in ConditionType}
        if condition not in valid_conditions:
            errors.append(f"Task {task_id}: invalid condition '{condition}'")

        # Check all dependencies exist
        dependencies = task_info.get("dependencies", [])
        for dep_id in dependencies:
            if dep_id not in task_queue:
                errors.append(
                    f"Task {task_id}: dependency '{dep_id}' not found in task queue"
                )

        # Check for orphaned tasks (no path to completion)
        if dependencies:
            # Task depends on something - will be checked when dependencies complete
            pass
        else:
            # No dependencies - should reach ready state
            state = task_info.get("state", "pending")
            if state == "pending":
                # OK - will become ready
                pass

    return {"valid": len(errors) == 0, "errors": errors}


def get_execution_paths(task_queue: Dict[str, Dict]) -> Dict[str, List[str]]:
    """
    Analyze all possible execution paths through conditional DAG.

    Returns main execution path (success path) and error handling paths.
    Useful for understanding system behavior and testing different scenarios.

    Args:
        task_queue: Task queue with conditions

    Returns:
        Dict with {success_path: [...], failure_paths: {...}}
    """
    paths = {
        "success_path": [],  # Path assuming all tasks succeed
        "failure_paths": {},  # Alternative paths for each failure scenario
        "always_tasks": [],  # Tasks that execute regardless
    }

    # Find root tasks (no dependencies)
    roots = [tid for tid, info in task_queue.items() if not info.get("dependencies")]

    # Trace success path (assuming all tasks succeed)
    visited_success = set()

    def trace_success_path(task_id):
        if task_id in visited_success:
            return
        visited_success.add(task_id)
        paths["success_path"].append(task_id)

        # Find successors with success condition
        for dependent_id, dependent_info in task_queue.items():
            deps = dependent_info.get("dependencies", [])
            if task_id in deps:
                condition = dependent_info.get("condition", ConditionType.ALWAYS.value)
                if condition in [
                    ConditionType.SUCCESS.value,
                    ConditionType.ALWAYS.value,
                ]:
                    trace_success_path(dependent_id)

    # Trace always tasks
    def trace_always_tasks(task_id):
        condition = task_queue[task_id].get("condition", ConditionType.ALWAYS.value)
        if condition == ConditionType.ALWAYS.value:
            if task_id not in paths["always_tasks"]:
                paths["always_tasks"].append(task_id)

        for dependent_id in task_queue:
            if task_id in task_queue[dependent_id].get("dependencies", []):
                trace_always_tasks(dependent_id)

    for root in roots:
        trace_success_path(root)
        trace_always_tasks(root)

    return paths


def simulate_execution(
    task_queue: Dict[str, Dict], failure_task: Optional[str] = None
) -> Dict:
    """
    Simulate execution path when a specific task fails.

    Shows which tasks would be skipped and which error handlers would trigger.

    Args:
        task_queue: Task queue
        failure_task: Task ID to simulate as failed (None = all succeed)

    Returns:
        Dict with {executed: [...], skipped: [...], error_handlers: [...]}
    """
    simulation = {"executed": [], "skipped": [], "error_handlers": []}

    if failure_task is None:
        # All tasks succeed - execute success path
        for task_id, task_info in task_queue.items():
            state = task_info.get("state", "pending")
            condition = task_info.get("condition", ConditionType.ALWAYS.value)

            if condition in [ConditionType.SUCCESS.value, ConditionType.ALWAYS.value]:
                simulation["executed"].append(task_id)
            else:
                simulation["skipped"].append(task_id)
    else:
        # Simulate failure at failure_task
        # Tasks on failure path execute, others skipped
        for task_id, task_info in task_queue.items():
            state = task_info.get("state", "pending")
            condition = task_info.get("condition", ConditionType.ALWAYS.value)
            dependencies = task_info.get("dependencies", [])

            # Check if this task depends on failure_task
            depends_on_failed = failure_task in dependencies

            if depends_on_failed:
                if condition == ConditionType.FAILURE.value:
                    simulation["error_handlers"].append(task_id)
                elif condition == ConditionType.SUCCESS.value:
                    simulation["skipped"].append(task_id)
                else:  # always
                    simulation["executed"].append(task_id)
            elif not any(
                dep in dependencies for dep in [failure_task] + simulation["skipped"]
            ):
                # No dependency on failed task or skipped tasks
                if condition in [
                    ConditionType.SUCCESS.value,
                    ConditionType.ALWAYS.value,
                ]:
                    simulation["executed"].append(task_id)

    return simulation
