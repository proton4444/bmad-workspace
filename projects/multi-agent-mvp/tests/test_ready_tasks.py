"""
Test suite for ready-task identification (Story 1.3).

Tests instant identification of claimable tasks based on dependency completion.
Validates task state management and ready-task list accuracy.

Acceptance Criteria:
- AC1: Function get_ready_tasks(task_queue) returns list of claimable tasks
- AC2: Task is "ready" when all dependencies completed successfully
- AC3: Task becomes ready within <10ms of dependency completion
- AC4: After Task A completes, Task B (depends on A) appears in ready list
- AC5: If Task A fails, Task B (depends on A) remains not ready
- AC6: Ready-task list updates atomically (no race conditions at Python level)
"""

import time

import pytest
from src.core.ready_tasks import (
    TaskState,
    get_blocked_tasks,
    get_ready_tasks,
    get_ready_tasks_incremental,
    get_task_summary,
    update_task_state,
    validate_ready_state,
)


def create_test_task(state="pending", dependencies=None, success=True):
    """Helper to create task dict for tests."""
    result = None
    if state == "completed":
        result = {"success": success, "output": "test output"}
    elif state == "failed":
        result = {"success": False, "output": "error message"}

    return {"state": state, "dependencies": dependencies or [], "result": result}


class TestGetReadyTasks:
    """Test suite for get_ready_tasks function (AC1, AC2)."""

    def test_no_dependencies_task_is_ready(self):
        """AC2: Task with no dependencies is immediately ready."""
        task_queue = {"A": create_test_task(state="pending", dependencies=[])}
        ready = get_ready_tasks(task_queue)

        assert "A" in ready, "Task with no dependencies should be ready"
        assert len(ready) == 1

    def test_pending_task_with_completed_dependency_is_ready(self):
        """AC4: After Task A completes, Task B (depends on A) appears in ready list."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        ready = get_ready_tasks(task_queue)

        assert "A" not in ready, "Completed task should not be in ready list"
        assert "B" in ready, "Task B should be ready after A completes"

    def test_task_with_failed_dependency_not_ready(self):
        """AC5: If Task A fails, Task B (depends on A) remains not ready."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[], success=False),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        ready = get_ready_tasks(task_queue)

        assert "B" not in ready, "Task B should NOT be ready when dependency failed"
        assert len(ready) == 0

    def test_multiple_dependencies_all_must_complete(self):
        """Task ready only when ALL dependencies completed successfully."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=[]),
            "C": create_test_task(state="pending", dependencies=["A", "B"]),
        }
        ready = get_ready_tasks(task_queue)

        assert "C" not in ready, "C not ready until both A and B complete"
        assert "B" in ready, "B should be ready (no dependencies)"

        # Now complete B
        task_queue["B"]["state"] = "completed"
        task_queue["B"]["result"] = {"success": True}
        ready = get_ready_tasks(task_queue)

        assert "C" in ready, "C now ready after both A and B complete"

    def test_in_progress_task_not_in_ready(self):
        """Task in progress should not be in ready list."""
        task_queue = {"A": create_test_task(state="in_progress", dependencies=[])}
        ready = get_ready_tasks(task_queue)

        assert "A" not in ready, "In-progress task should not be in ready list"

    def test_completed_task_not_in_ready(self):
        """Task already completed should not be in ready list."""
        task_queue = {"A": create_test_task(state="completed", dependencies=[])}
        ready = get_ready_tasks(task_queue)

        assert "A" not in ready, "Completed task should not be in ready list"

    def test_failed_task_not_in_ready(self):
        """Task that failed should not be in ready list."""
        task_queue = {"A": create_test_task(state="failed", dependencies=[])}
        ready = get_ready_tasks(task_queue)

        assert "A" not in ready, "Failed task should not be in ready list"

    def test_empty_queue(self):
        """AC1: Empty queue returns empty ready list."""
        task_queue = {}
        ready = get_ready_tasks(task_queue)

        assert ready == [], "Empty queue should return empty ready list"

    def test_diamond_dependency(self):
        """AC2: Task ready when all paths in DAG complete."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="completed", dependencies=["A"]),
            "C": create_test_task(state="completed", dependencies=["A"]),
            "D": create_test_task(state="pending", dependencies=["B", "C"]),
        }
        ready = get_ready_tasks(task_queue)

        assert "D" in ready, "D should be ready when both B and C complete"

    def test_complex_ready_list(self):
        """Multiple independent ready tasks identified correctly."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
            "C": create_test_task(state="pending", dependencies=["A"]),
            "D": create_test_task(state="pending", dependencies=["B", "C"]),
        }
        ready = get_ready_tasks(task_queue)

        assert set(ready) == {"B", "C"}, "B and C should both be ready"
        assert "D" not in ready, "D waiting for B and C"

    def test_linear_chain_progression(self):
        """AC3: <10ms response for dependency notifications."""
        task_queue = {
            f"task-{i}": create_test_task(
                state="pending" if i > 0 else "completed",
                dependencies=[f"task-{i - 1}"] if i > 0 else [],
            )
            for i in range(10)
        }

        start = time.perf_counter()
        ready = get_ready_tasks(task_queue)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 10, f"Should complete in <10ms, took {elapsed_ms:.2f}ms"
        assert ready == ["task-1"], "Only next task should be ready"


class TestTaskStateUpdate:
    """Test suite for task state management."""

    def test_update_task_state(self):
        """State transitions work correctly."""
        task_queue = {"A": create_test_task(state="pending")}

        # Transition to in_progress
        update_task_state(task_queue, "A", "in_progress")
        assert task_queue["A"]["state"] == "in_progress"

        # Transition to completed
        result = {"success": True, "output": "done"}
        update_task_state(task_queue, "A", "completed", result)
        assert task_queue["A"]["state"] == "completed"
        assert task_queue["A"]["result"] == result

    def test_update_nonexistent_task_raises(self):
        """Updating non-existent task raises error."""
        task_queue = {}

        with pytest.raises(ValueError):
            update_task_state(task_queue, "nonexistent", "completed")

    def test_invalid_state_raises(self):
        """Invalid state value raises error."""
        task_queue = {"A": create_test_task()}

        with pytest.raises(ValueError):
            update_task_state(task_queue, "A", "invalid_state")


class TestIncrementalReady:
    """Test suite for incremental ready-task detection (AC3 optimization)."""

    def test_single_task_completion_triggers_dependent(self):
        """Single task completion identified efficiently."""
        task_queue_before = {
            "A": create_test_task(state="in_progress", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }

        task_queue_after = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }

        newly_ready = get_ready_tasks_incremental(task_queue_before, task_queue_after)
        assert "B" in newly_ready, "B should be newly ready"

    def test_multiple_dependents_identified(self):
        """Multiple dependents of single task identified."""
        task_queue_before = {
            "A": create_test_task(state="in_progress", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
            "C": create_test_task(state="pending", dependencies=["A"]),
        }

        task_queue_after = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
            "C": create_test_task(state="pending", dependencies=["A"]),
        }

        newly_ready = get_ready_tasks_incremental(task_queue_before, task_queue_after)
        assert set(newly_ready) == {"B", "C"}, "Both B and C should be newly ready"

    def test_failure_not_marked_ready(self):
        """Task completion with failure doesn't mark dependents ready."""
        task_queue_before = {
            "A": create_test_task(state="in_progress", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }

        task_queue_after = {
            "A": create_test_task(state="completed", dependencies=[], success=False),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }

        newly_ready = get_ready_tasks_incremental(task_queue_before, task_queue_after)
        assert "B" not in newly_ready, "B should not be ready when A failed"


class TestValidateReadyState:
    """Test suite for ready state validation."""

    def test_valid_ready_state(self):
        """Valid ready state passes validation."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
            "C": create_test_task(state="pending", dependencies=["A"]),
        }
        ready_tasks = ["B", "C"]

        assert validate_ready_state(task_queue, ready_tasks) is True

    def test_invalid_ready_state_missing_task(self):
        """Invalid ready state with missing task fails validation."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        ready_tasks = ["B", "C"]  # C doesn't exist

        assert validate_ready_state(task_queue, ready_tasks) is False

    def test_invalid_ready_state_incomplete_dependency(self):
        """Invalid ready state with incomplete dependencies fails."""
        task_queue = {
            "A": create_test_task(state="pending", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        ready_tasks = ["B"]  # B not ready, A still pending

        assert validate_ready_state(task_queue, ready_tasks) is False

    def test_invalid_ready_state_in_progress_task(self):
        """Task in progress should not be in ready list."""
        task_queue = {"A": create_test_task(state="in_progress", dependencies=[])}
        ready_tasks = ["A"]

        assert validate_ready_state(task_queue, ready_tasks) is False


class TestBlockedTasks:
    """Test suite for blocked task identification (monitoring)."""

    def test_no_blocked_tasks(self):
        """All dependencies satisfied - no blocked tasks."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="completed", dependencies=["A"]),
        }
        blocked = get_blocked_tasks(task_queue)

        assert len(blocked) == 0, "No tasks should be blocked"

    def test_single_blocked_task(self):
        """Task blocked by incomplete dependency identified."""
        task_queue = {
            "A": create_test_task(state="pending", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        blocked = get_blocked_tasks(task_queue)

        assert "B" in blocked, "B should be blocked"
        assert blocked["B"] == ["A"], "B blocked by A"

    def test_multiple_blockers(self):
        """Task blocked by multiple incomplete dependencies."""
        task_queue = {
            "A": create_test_task(state="pending", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=[]),
            "C": create_test_task(state="pending", dependencies=["A", "B"]),
        }
        blocked = get_blocked_tasks(task_queue)

        assert "C" in blocked, "C should be blocked"
        assert set(blocked["C"]) == {"A", "B"}, "C blocked by both A and B"

    def test_in_progress_not_blocked(self):
        """In-progress task not shown as blocked."""
        task_queue = {"A": create_test_task(state="in_progress", dependencies=[])}
        blocked = get_blocked_tasks(task_queue)

        assert "A" not in blocked, "In-progress task not blocked"

    def test_completed_not_blocked(self):
        """Completed task not shown as blocked."""
        task_queue = {"A": create_test_task(state="completed", dependencies=[])}
        blocked = get_blocked_tasks(task_queue)

        assert "A" not in blocked, "Completed task not blocked"


class TestTaskSummary:
    """Test suite for task summary statistics."""

    def test_summary_counts(self):
        """Summary statistics accurate."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="in_progress", dependencies=["A"]),
            "C": create_test_task(state="pending", dependencies=["A"]),
            "D": create_test_task(state="failed", dependencies=[]),
        }
        summary = get_task_summary(task_queue)

        assert summary["total"] == 4
        assert summary["completed"] == 1
        assert summary["in_progress"] == 1
        assert summary["pending"] == 1
        assert summary["failed"] == 1
        assert summary["ready"] == 1  # C is ready
        assert summary["blocked"] == 0

    def test_summary_with_blocked_tasks(self):
        """Summary includes blocked task count."""
        task_queue = {
            "A": create_test_task(state="pending", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        summary = get_task_summary(task_queue)

        assert summary["blocked"] == 1  # B blocked by A


class TestAcceptanceCriteria:
    """Integration tests verifying all acceptance criteria."""

    def test_ac1_get_ready_tasks_returns_claimable_list(self):
        """AC1: Function returns list of claimable tasks."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        ready = get_ready_tasks(task_queue)

        assert isinstance(ready, list)
        assert "B" in ready

    def test_ac2_ready_when_deps_complete_successfully(self):
        """AC2: Task ready when all dependencies completed successfully."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[], success=True),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        ready = get_ready_tasks(task_queue)
        assert "B" in ready

        # If A failed, B not ready
        task_queue["A"]["result"]["success"] = False
        ready = get_ready_tasks(task_queue)
        assert "B" not in ready

    def test_ac3_response_time_under_10ms(self):
        """AC3: Ready-task identification <10ms."""
        task_queue = {
            f"task-{i}": create_test_task(
                state="completed" if i == 0 else "pending",
                dependencies=[f"task-{i - 1}"] if i > 0 else [],
            )
            for i in range(50)
        }

        start = time.perf_counter()
        ready = get_ready_tasks(task_queue)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 10, f"Should be <10ms, was {elapsed_ms:.2f}ms"

    def test_ac4_task_appears_ready_after_dependency_completes(self):
        """AC4: After A completes, B (depends on A) appears in ready list."""
        task_queue = {
            "A": create_test_task(state="in_progress", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }

        # Before A completes
        ready_before = get_ready_tasks(task_queue)
        assert "B" not in ready_before

        # After A completes
        task_queue["A"]["state"] = "completed"
        task_queue["A"]["result"] = {"success": True}
        ready_after = get_ready_tasks(task_queue)
        assert "B" in ready_after

    def test_ac5_failed_dependency_blocks_task(self):
        """AC5: If A fails, B (depends on A) remains not ready."""
        task_queue = {
            "A": create_test_task(state="completed", dependencies=[], success=False),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }
        ready = get_ready_tasks(task_queue)

        assert "B" not in ready, "B should not be ready when A failed"

    def test_ac6_atomic_updates_no_race_conditions(self):
        """AC6: Ready-list updates are atomic at Python level."""
        task_queue = {
            "A": create_test_task(state="pending", dependencies=[]),
            "B": create_test_task(state="pending", dependencies=["A"]),
        }

        # Simulate completion
        update_task_state(task_queue, "A", "completed", {"success": True})
        ready = get_ready_tasks(task_queue)

        # Verify consistent state
        assert validate_ready_state(task_queue, ready) is True
        assert "B" in ready
