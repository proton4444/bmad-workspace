"""
Test suite for conditional branching (Story 1.4).

Tests success/failure path routing based on task outcomes.
Validates condition evaluation and execution flow management.

Acceptance Criteria:
- AC1: Task definition supports condition: "success" | "failure" | "always"
- AC2: Task with condition "success" executes if parent completed successfully
- AC3: Task with condition "failure" executes if parent failed
- AC4: Task with condition "always" executes regardless
- AC5: Task A fails → Task B (success) not ready → Task C (failure) becomes ready
- AC6: Conditional logic transparent in task-queue.json
"""

import pytest
from src.core.conditional_branching import (
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


def create_task(state="pending", dependencies=None, condition="always", success=None):
    """Helper to create task dict for tests."""
    result = None
    if state == "completed":
        result = {"success": success if success is not None else True, "output": "done"}
    elif state == "failed":
        result = {"success": False, "output": "error"}

    return {
        "state": state,
        "dependencies": dependencies or [],
        "condition": condition,
        "result": result,
    }


class TestConditionType:
    """Test suite for ConditionType enum."""

    def test_condition_type_values(self):
        """ConditionType enum has correct values."""
        assert ConditionType.SUCCESS.value == "success"
        assert ConditionType.FAILURE.value == "failure"
        assert ConditionType.ALWAYS.value == "always"


class TestAddConditionToTask:
    """Test suite for add_condition_to_task function (AC1)."""

    def test_add_condition_success(self):
        """AC1: Add success condition to task."""
        task = create_task()
        add_condition_to_task(task, "success")

        assert task["condition"] == "success"

    def test_add_condition_failure(self):
        """AC1: Add failure condition to task."""
        task = create_task()
        add_condition_to_task(task, "failure")

        assert task["condition"] == "failure"

    def test_add_condition_always(self):
        """AC1: Add always condition to task."""
        task = create_task()
        add_condition_to_task(task, "always")

        assert task["condition"] == "always"

    def test_invalid_condition_raises(self):
        """AC1: Invalid condition raises ValueError."""
        task = create_task()

        with pytest.raises(ValueError):
            add_condition_to_task(task, "invalid")

    def test_add_condition_returns_task(self):
        """add_condition_to_task returns modified task."""
        task = create_task()
        result = add_condition_to_task(task, "success")

        assert result is task
        assert result["condition"] == "success"


class TestEvaluateCondition:
    """Test suite for evaluate_condition function (AC2, AC3, AC4)."""

    def test_success_condition_parent_succeeded(self):
        """AC2: Success condition true when parent completed successfully."""
        result = evaluate_condition(
            "success", "completed", {"success": True, "output": "ok"}
        )

        assert result is True

    def test_success_condition_parent_failed(self):
        """AC2: Success condition false when parent failed."""
        result = evaluate_condition("success", "completed", {"success": False})

        assert result is False

    def test_success_condition_parent_still_pending(self):
        """AC2: Success condition false when parent still pending."""
        result = evaluate_condition("success", "pending", None)

        assert result is False

    def test_success_condition_parent_in_progress(self):
        """AC2: Success condition false when parent in progress."""
        result = evaluate_condition("success", "in_progress", None)

        assert result is False

    def test_failure_condition_parent_failed(self):
        """AC3: Failure condition true when parent failed."""
        result = evaluate_condition("failure", "failed", {"success": False})

        assert result is True

    def test_failure_condition_parent_completed_unsuccessfully(self):
        """AC3: Failure condition true when parent completed with failure."""
        result = evaluate_condition("failure", "completed", {"success": False})

        assert result is True

    def test_failure_condition_parent_succeeded(self):
        """AC3: Failure condition false when parent succeeded."""
        result = evaluate_condition("failure", "completed", {"success": True})

        assert result is False

    def test_failure_condition_parent_in_progress(self):
        """AC3: Failure condition false when parent still in progress."""
        result = evaluate_condition("failure", "in_progress", None)

        assert result is False

    def test_always_condition_parent_completed(self):
        """AC4: Always condition true when parent completed successfully."""
        result = evaluate_condition("always", "completed", {"success": True})

        assert result is True

    def test_always_condition_parent_failed(self):
        """AC4: Always condition true when parent failed."""
        result = evaluate_condition("always", "failed", {"success": False})

        assert result is True

    def test_always_condition_parent_in_progress(self):
        """AC4: Always condition false when parent still in progress."""
        result = evaluate_condition("always", "in_progress", None)

        assert result is False

    def test_always_condition_parent_pending(self):
        """AC4: Always condition false when parent still pending."""
        result = evaluate_condition("always", "pending", None)

        assert result is False


class TestCheckConditionalDependencies:
    """Test suite for conditional dependency checking."""

    def test_no_dependencies_satisfied(self):
        """Task with no dependencies has satisfied dependencies."""
        task_queue = {}
        result = check_conditional_dependencies_satisfied("A", task_queue, [])

        assert result is True

    def test_single_success_dependency_satisfied(self):
        """Single dependency with success condition satisfied."""
        task_queue = {
            "A": create_task(state="completed", condition="success", success=True)
        }
        result = check_conditional_dependencies_satisfied("B", task_queue, ["A"])

        assert result is True

    def test_single_success_dependency_failed(self):
        """Single dependency with success condition not satisfied when parent failed."""
        task_queue = {
            "A": create_task(state="completed", condition="success", success=False),
            "B": create_task(state="pending", condition="success"),
        }
        result = check_conditional_dependencies_satisfied("B", task_queue, ["A"])

        assert result is False

    def test_single_failure_dependency_satisfied(self):
        """Single dependency with failure condition satisfied."""
        task_queue = {"A": create_task(state="failed", condition="failure")}
        result = check_conditional_dependencies_satisfied("B", task_queue, ["A"])

        assert result is True

    def test_single_failure_dependency_not_satisfied(self):
        """Single dependency with failure condition not satisfied when parent succeeded."""
        task_queue = {
            "A": create_task(state="completed", condition="failure", success=True),
            "B": create_task(state="pending", condition="failure"),
        }
        result = check_conditional_dependencies_satisfied("B", task_queue, ["A"])

        assert result is False

    def test_multiple_dependencies_all_satisfied(self):
        """Multiple dependencies all satisfied."""
        task_queue = {
            "A": create_task(state="completed", condition="success", success=True),
            "B": create_task(state="completed", condition="success", success=True),
        }
        result = check_conditional_dependencies_satisfied("C", task_queue, ["A", "B"])

        assert result is True

    def test_multiple_dependencies_one_unsatisfied(self):
        """Multiple dependencies with one not satisfied."""
        task_queue = {
            "A": create_task(state="completed", condition="success", success=True),
            "B": create_task(state="pending", condition="success"),
        }
        result = check_conditional_dependencies_satisfied("C", task_queue, ["A", "B"])

        assert result is False

    def test_missing_dependency(self):
        """Missing dependency returns False."""
        task_queue = {"A": create_task(state="completed", success=True)}
        result = check_conditional_dependencies_satisfied("B", task_queue, ["missing"])

        assert result is False


class TestGetReadyTasksWithConditions:
    """Test suite for get_ready_tasks_with_conditions function (AC5, AC6)."""

    def test_no_dependencies_ready(self):
        """Tasks with no dependencies are ready."""
        task_queue = {"A": create_task(state="pending")}
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "A" in ready

    def test_success_condition_success_path(self):
        """AC5: Success condition task ready when parent succeeds."""
        task_queue = {
            "A": create_task(state="completed", success=True),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "B" in ready

    def test_success_condition_failure_path(self):
        """AC5: Success condition task NOT ready when parent fails."""
        task_queue = {
            "A": create_task(state="completed", success=False),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "B" not in ready

    def test_failure_condition_becomes_ready(self):
        """AC5: Failure condition task becomes ready when parent fails."""
        task_queue = {
            "A": create_task(state="completed", success=False),
            "B": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "B" in ready

    def test_failure_condition_not_ready_on_success(self):
        """Failure condition task NOT ready when parent succeeds."""
        task_queue = {
            "A": create_task(state="completed", success=True),
            "B": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "B" not in ready

    def test_always_condition_success_and_failure(self):
        """AC4: Always condition task ready after success or failure."""
        # Success case
        task_queue = {
            "A": create_task(state="completed", success=True),
            "B": create_task(state="pending", dependencies=["A"], condition="always"),
        }
        ready = get_ready_tasks_with_conditions(task_queue)
        assert "B" in ready

        # Failure case
        task_queue["A"]["state"] = "failed"
        task_queue["A"]["result"] = {"success": False}
        ready = get_ready_tasks_with_conditions(task_queue)
        assert "B" in ready

    def test_complete_scenario_ac5(self):
        """AC5: Task A fails → Task B (success) not ready → Task C (failure) becomes ready."""
        task_queue = {
            "A": create_task(state="completed", success=False),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "B" not in ready, "Success task not ready when parent failed"
        assert "C" in ready, "Failure task ready when parent failed"


class TestGetConditionalSuccessors:
    """Test suite for get_conditional_successors function."""

    def test_success_path_successors(self):
        """Identify successors on success path."""
        task_queue = {
            "A": create_task(state="completed", success=True),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        successors = get_conditional_successors("A", task_queue, {"success": True})

        assert "B" in successors["success_path"]
        assert "C" not in successors["success_path"]
        assert "C" in successors["failure_path"] or len(successors["failure_path"]) == 0

    def test_failure_path_successors(self):
        """Identify successors on failure path."""
        task_queue = {
            "A": create_task(state="failed"),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        successors = get_conditional_successors("A", task_queue, {"success": False})

        assert "C" in successors["failure_path"]
        assert "B" not in successors["failure_path"]

    def test_always_path_successors(self):
        """Identify successors on always path."""
        task_queue = {
            "A": create_task(state="completed", success=True),
            "B": create_task(state="pending", dependencies=["A"], condition="always"),
        }
        successors = get_conditional_successors("A", task_queue, {"success": True})

        assert "B" in successors["always_path"]


class TestValidateConditionalGraph:
    """Test suite for validate_conditional_graph function (AC6)."""

    def test_valid_graph(self):
        """Valid conditional graph passes validation."""
        task_queue = {
            "A": create_task(state="pending"),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        validation = validate_conditional_graph(task_queue)

        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    def test_invalid_condition(self):
        """Invalid condition detected."""
        task_queue = {
            "A": {
                "state": "pending",
                "dependencies": [],
                "condition": "invalid_condition",
                "result": None,
            }
        }
        validation = validate_conditional_graph(task_queue)

        assert validation["valid"] is False
        assert len(validation["errors"]) > 0

    def test_missing_dependency(self):
        """Missing dependency detected."""
        task_queue = {"A": create_task(state="pending", dependencies=["missing"])}
        validation = validate_conditional_graph(task_queue)

        assert validation["valid"] is False
        assert any("missing" in err for err in validation["errors"])

    def test_complex_valid_graph(self):
        """Complex graph with multiple branches validates."""
        task_queue = {
            "A": create_task(state="pending"),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
            "D": create_task(state="pending", dependencies=["B"], condition="success"),
            "E": create_task(state="pending", dependencies=["C"], condition="always"),
        }
        validation = validate_conditional_graph(task_queue)

        assert validation["valid"] is True


class TestExecutionPaths:
    """Test suite for get_execution_paths function."""

    def test_linear_success_path(self):
        """Linear task chain forms success path."""
        task_queue = {
            "A": create_task(state="pending"),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["B"], condition="success"),
        }
        paths = get_execution_paths(task_queue)

        assert "A" in paths["success_path"]
        assert "B" in paths["success_path"]
        assert "C" in paths["success_path"]

    def test_branching_paths(self):
        """Branching creates alternative paths."""
        task_queue = {
            "A": create_task(state="pending"),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        paths = get_execution_paths(task_queue)

        assert "A" in paths["success_path"]
        assert "B" in paths["success_path"]
        # C is on failure path, not success path
        assert "C" not in paths["success_path"]


class TestSimulateExecution:
    """Test suite for simulate_execution function."""

    def test_simulate_all_success(self):
        """Simulate when all tasks succeed."""
        task_queue = {
            "A": create_task(state="pending"),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        sim = simulate_execution(task_queue, failure_task=None)

        assert "A" in sim["executed"]
        assert "B" in sim["executed"]
        assert "C" not in sim["executed"]

    def test_simulate_task_failure(self):
        """Simulate when task A fails."""
        task_queue = {
            "A": create_task(state="pending"),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
            "D": create_task(state="pending", dependencies=["A"], condition="always"),
        }
        sim = simulate_execution(task_queue, failure_task="A")

        assert "B" in sim["skipped"] or "B" not in sim["executed"]
        assert "C" in sim["error_handlers"]
        # Always path should execute
        assert "D" in sim["executed"] or "D" in sim["always_path"]


class TestAcceptanceCriteria:
    """Integration tests for all acceptance criteria."""

    def test_ac1_condition_types_in_schema(self):
        """AC1: Task definition supports condition field."""
        task = create_task()
        add_condition_to_task(task, "success")

        assert "condition" in task
        assert task["condition"] == "success"

    def test_ac2_success_condition_logic(self):
        """AC2: Success condition executes if parent completed successfully."""
        task_queue = {
            "parent": create_task(state="completed", success=True),
            "child": create_task(
                state="pending", dependencies=["parent"], condition="success"
            ),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "child" in ready

    def test_ac3_failure_condition_logic(self):
        """AC3: Failure condition executes if parent failed."""
        task_queue = {
            "parent": create_task(state="completed", success=False),
            "error_handler": create_task(
                state="pending", dependencies=["parent"], condition="failure"
            ),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "error_handler" in ready

    def test_ac4_always_condition_logic(self):
        """AC4: Always condition executes regardless of parent outcome."""
        # Success case
        task_queue = {
            "parent": create_task(state="completed", success=True),
            "follow_up": create_task(
                state="pending", dependencies=["parent"], condition="always"
            ),
        }
        ready = get_ready_tasks_with_conditions(task_queue)
        assert "follow_up" in ready

        # Failure case
        task_queue["parent"]["state"] = "completed"
        task_queue["parent"]["result"]["success"] = False
        ready = get_ready_tasks_with_conditions(task_queue)
        assert "follow_up" in ready

    def test_ac5_complete_failure_scenario(self):
        """AC5: Task A fails → B (success) not ready → C (failure) becomes ready."""
        task_queue = {
            "A": create_task(state="completed", success=False),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
        }
        ready = get_ready_tasks_with_conditions(task_queue)

        assert "B" not in ready
        assert "C" in ready

    def test_ac6_conditions_transparent_in_task_queue(self):
        """AC6: Conditional logic transparent in task-queue.json format."""
        # Task queue should show condition field
        task_queue = {
            "A": create_task(state="completed", success=True),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
            "D": create_task(state="pending", dependencies=["A"], condition="always"),
        }

        # Validate all conditions present and evaluable
        validation = validate_conditional_graph(task_queue)
        assert validation["valid"] is True

        # Get ready tasks accounting for conditions
        ready = get_ready_tasks_with_conditions(task_queue)
        assert isinstance(ready, list)


class TestErrorHandlingScenarios:
    """Real-world error handling scenarios."""

    def test_error_recovery_workflow(self):
        """Error recovery: Main task fails, recovery task executes."""
        task_queue = {
            "fetch_data": create_task(state="completed", success=False),
            "process_data": create_task(
                state="pending", dependencies=["fetch_data"], condition="success"
            ),
            "retry_fetch": create_task(
                state="pending", dependencies=["fetch_data"], condition="failure"
            ),
            "fallback_data": create_task(
                state="pending", dependencies=["retry_fetch"], condition="failure"
            ),
        }

        ready = get_ready_tasks_with_conditions(task_queue)
        assert "process_data" not in ready
        assert "retry_fetch" in ready

    def test_parallel_branches(self):
        """Parallel branches with different conditions."""
        task_queue = {
            "build": create_task(state="completed", success=True),
            "test": create_task(
                state="pending", dependencies=["build"], condition="success"
            ),
            "build_debug": create_task(
                state="pending", dependencies=["build"], condition="failure"
            ),
            "notify_success": create_task(
                state="pending", dependencies=["test"], condition="success"
            ),
            "notify_failure": create_task(
                state="pending", dependencies=["build_debug"], condition="always"
            ),
        }

        ready = get_ready_tasks_with_conditions(task_queue)
        assert "test" in ready
        assert "build_debug" not in ready
        assert "notify_success" not in ready  # test not done yet
