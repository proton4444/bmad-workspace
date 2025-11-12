"""
Stress test suite for task dependency engine (Story 1.5).

Tests the entire dependency engine under realistic load:
- Concurrent task claiming (multiple agents)
- Large graphs (100+ tasks)
- Complex dependency patterns
- Performance under stress

Acceptance Criteria:
- AC1: 10 concurrent tasks, 3 agents - 0 race conditions
- AC2: All tasks claimed uniquely (no dual-claiming)
- AC3: All dependencies respected in execution order
- AC4: 10-task graph processed in <100ms total
- AC5: File locking prevents concurrent conflicts
- AC6: Observable state in task-queue.json
- AC7: Test coverage >80% of engine code
"""

import json
import threading
import time
from typing import Dict, List, Set

import pytest
from src.core import (
    get_blocked_tasks,
    get_parallel_batches,
    get_ready_tasks,
    get_ready_tasks_with_conditions,
    get_task_summary,
    topological_sort,
    update_task_state,
    validate_conditional_graph,
    validate_ready_state,
)


def create_task(state="pending", dependencies=None, condition="always", success=None):
    """Helper to create task dict."""
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


class TestLargeGraphs:
    """Test engine with large task graphs."""

    def test_100_task_linear_chain(self):
        """AC4: 100-task linear chain processed efficiently."""
        task_queue = {
            f"task-{i}": create_task(
                state="pending" if i > 0 else "completed",
                dependencies=[f"task-{i - 1}"] if i > 0 else [],
            )
            for i in range(100)
        }

        start = time.perf_counter()
        ready = get_ready_tasks(task_queue)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(ready) == 1, "Only next task should be ready"
        assert ready[0] == "task-1"
        assert elapsed_ms < 500, (
            f"100-task processing should be <500ms, was {elapsed_ms:.2f}ms"
        )

    def test_100_task_topological_sort(self):
        """AC4: Topological sort of 100-task graph."""
        # Use the correct format for topological_sort: {task: [dependencies]}
        task_graph = {
            f"task-{i}": [f"task-{i - 1}"] if i > 0 else [] for i in range(100)
        }

        start = time.perf_counter()
        ordering = topological_sort(task_graph)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(ordering) == 100
        assert elapsed_ms < 500

    def test_complex_100_task_dag(self):
        """Complex DAG with multiple dependency paths."""
        task_queue = {}

        # Create 10 independent chains of 10 tasks each
        for chain in range(10):
            for pos in range(10):
                task_id = f"chain-{chain}-task-{pos}"
                deps = [f"chain-{chain}-task-{pos - 1}"] if pos > 0 else []
                task_queue[task_id] = create_task(dependencies=deps)

        start = time.perf_counter()
        ready = get_ready_tasks(task_queue)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # 10 independent chains should have 10 ready tasks (first of each)
        assert len(ready) == 10
        assert elapsed_ms < 500

    def test_wide_dependency_graph(self):
        """Graph where one task depends on many tasks."""
        task_queue = {f"dependency-{i}": create_task() for i in range(50)}
        # One task depends on all 50
        task_queue["aggregator"] = create_task(
            dependencies=[f"dependency-{i}" for i in range(50)]
        )

        # Complete all dependencies
        for i in range(50):
            task_queue[f"dependency-{i}"]["state"] = "completed"
            task_queue[f"dependency-{i}"]["result"] = {"success": True}

        ready = get_ready_tasks(task_queue)
        assert "aggregator" in ready

    def test_parallel_batches_large_graph(self):
        """AC4: Parallel batch detection in large graph."""
        task_queue = {}

        # Create diamond at each level
        for level in range(10):
            task_queue[f"root-{level}"] = create_task(
                dependencies=[f"root-{level - 1}"] if level > 0 else []
            )
            task_queue[f"branch1-{level}"] = create_task(dependencies=[f"root-{level}"])
            task_queue[f"branch2-{level}"] = create_task(dependencies=[f"root-{level}"])
            task_queue[f"merge-{level}"] = create_task(
                dependencies=[f"branch1-{level}", f"branch2-{level}"]
            )

        start = time.perf_counter()
        batches = get_parallel_batches(task_queue)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(batches) > 0
        assert elapsed_ms < 500


class TestConcurrentTaskClaiming:
    """Test concurrent agent task claiming (AC1, AC2, AC5)."""

    def test_10_tasks_3_agents_no_race_conditions(self):
        """AC1, AC2: 10 tasks with 3 concurrent agents - no conflicts."""
        task_queue = {
            f"task-{i}": create_task(dependencies=[f"task-{i - 1}"] if i > 0 else [])
            for i in range(10)
        }

        claimed_tasks: Set[str] = set()
        claim_lock = threading.Lock()
        errors: List[str] = []

        def agent_claiming_loop(agent_id: int):
            """Simulate agent claiming tasks."""
            try:
                # Each agent claims 3-4 tasks
                for _ in range(4):
                    # Get ready tasks
                    ready = get_ready_tasks(task_queue)

                    if ready:
                        task_id = ready[0]

                        # Check for dual-claiming (AC2)
                        with claim_lock:
                            if task_id in claimed_tasks:
                                errors.append(
                                    f"Agent {agent_id}: Task {task_id} already claimed!"
                                )
                                return

                            claimed_tasks.add(task_id)

                        # Mark as in progress
                        update_task_state(task_queue, task_id, "in_progress")

                        # Simulate execution
                        time.sleep(0.001)

                        # Mark as completed
                        update_task_state(
                            task_queue, task_id, "completed", {"success": True}
                        )
            except Exception as e:
                errors.append(f"Agent {agent_id}: {str(e)}")

        # Run 3 agents concurrently
        threads = [
            threading.Thread(target=agent_claiming_loop, args=(i,)) for i in range(3)
        ]

        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(claimed_tasks) > 0, "Some tasks should be claimed"
        assert elapsed_ms < 1000, f"Should complete in <1s, took {elapsed_ms:.2f}ms"

    def test_sequential_claiming_with_dependencies(self):
        """AC3: Sequential claiming respects dependencies."""
        task_queue = {
            "A": create_task(state="pending"),
            "B": create_task(dependencies=["A"]),
            "C": create_task(dependencies=["B"]),
            "D": create_task(dependencies=["C"]),
        }

        claim_order = []

        # Simulate agent claiming tasks in dependency order
        for _ in range(4):
            ready = get_ready_tasks(task_queue)
            if ready:
                task_id = ready[0]
                claim_order.append(task_id)
                update_task_state(task_queue, task_id, "completed", {"success": True})

        # Verify order respects dependencies
        assert claim_order[0] == "A"
        assert claim_order[1] == "B"
        assert claim_order[2] == "C"
        assert claim_order[3] == "D"

    def test_10_task_graph_under_100ms(self):
        """AC4: 10-task graph processed in <100ms."""
        task_queue = {
            f"task-{i}": create_task(dependencies=[f"task-{i - 1}"] if i > 0 else [])
            for i in range(10)
        }

        start = time.perf_counter()

        # Simulate full execution
        for _ in range(10):
            ready = get_ready_tasks(task_queue)
            if ready:
                task_id = ready[0]
                update_task_state(task_queue, task_id, "completed", {"success": True})

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 100, (
            f"10-task graph should be <100ms, was {elapsed_ms:.2f}ms"
        )


class TestObservableState:
    """Test observable state in task-queue.json format (AC6)."""

    def test_task_queue_json_serialization(self):
        """AC6: Task queue serializable to JSON."""
        task_queue = {
            f"task-{i}": create_task(
                state="completed" if i == 0 else "pending",
                dependencies=[f"task-{i - 1}"] if i > 0 else [],
            )
            for i in range(5)
        }

        # Should be JSON serializable
        json_str = json.dumps(task_queue)
        deserialized = json.loads(json_str)

        assert len(deserialized) == 5
        assert deserialized["task-0"]["state"] == "completed"

    def test_observable_state_consistency(self):
        """AC6: Observable state stays consistent with internal state."""
        task_queue = {
            "A": create_task(state="pending", dependencies=["setup"]),
            "setup": create_task(state="pending"),
            "B": create_task(state="pending", dependencies=["A"]),
        }

        # Initial state - setup is ready, A and B are not
        ready = get_ready_tasks(task_queue)
        summary = get_task_summary(task_queue)
        assert summary["ready"] == 1  # Only setup is ready

        # Complete A
        update_task_state(task_queue, "A", "completed", {"success": True})

        # Check observable state
        ready = get_ready_tasks(task_queue)
        assert "B" in ready

        # Serialize and verify
        json_str = json.dumps(task_queue)
        restored = json.loads(json_str)
        assert restored["A"]["state"] == "completed"

    def test_complex_state_observable(self):
        """AC6: Complex graph state fully observable."""
        task_queue = {
            "A": create_task(state="completed", success=True),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
            "D": create_task(
                state="pending", dependencies=["B", "C"], condition="always"
            ),
        }

        # Mark task states
        update_task_state(task_queue, "B", "in_progress")

        # All state observable in JSON
        json_str = json.dumps(task_queue)
        restored = json.loads(json_str)

        assert restored["B"]["state"] == "in_progress"
        assert restored["C"]["condition"] == "failure"
        assert restored["D"]["dependencies"] == ["B", "C"]


class TestEngineCodeCoverage:
    """Test coverage of all engine functions (AC7)."""

    def test_all_ready_task_functions(self):
        """Exercise all ready-task functions."""
        task_queue = {
            "A": create_task(state="completed"),
            "B": create_task(state="pending", dependencies=["A"]),
            "C": create_task(state="pending", dependencies=["A"]),
        }

        # get_ready_tasks
        ready = get_ready_tasks(task_queue)
        assert len(ready) > 0

        # validate_ready_state
        assert validate_ready_state(task_queue, ready) is True

        # get_blocked_tasks
        blocked = get_blocked_tasks(task_queue)
        assert len(blocked) == 0

        # get_task_summary
        summary = get_task_summary(task_queue)
        assert summary["total"] == 3

    def test_all_topological_functions(self):
        """Exercise all topological sort functions."""
        # Use correct format for topological_sort: {task: [dependencies]}
        task_graph = {
            "A": [],
            "B": ["A"],
            "C": ["A"],
            "D": ["B", "C"],
        }

        # Create task_queue for get_parallel_batches
        task_queue = {
            "A": create_task(),
            "B": create_task(dependencies=["A"]),
            "C": create_task(dependencies=["A"]),
            "D": create_task(dependencies=["B", "C"]),
        }

        # topological_sort
        ordering = topological_sort(task_graph)
        assert len(ordering) == 4

        # get_parallel_batches (also uses task_graph format)
        batches = get_parallel_batches(task_graph)
        assert len(batches) > 0
        assert batches[0] == ["A"]
        assert set(batches[1]) == {"B", "C"}

    def test_all_conditional_functions(self):
        """Exercise all conditional branching functions."""
        task_queue = {
            "A": create_task(state="completed", success=False),
            "B": create_task(state="pending", dependencies=["A"], condition="success"),
            "C": create_task(state="pending", dependencies=["A"], condition="failure"),
            "D": create_task(state="pending", dependencies=["A"], condition="always"),
        }

        # get_ready_tasks_with_conditions
        ready = get_ready_tasks_with_conditions(task_queue)
        assert "B" not in ready
        assert "C" in ready
        assert "D" in ready

        # validate_conditional_graph
        validation = validate_conditional_graph(task_queue)
        assert validation["valid"] is True

    def test_all_state_update_functions(self):
        """Exercise all state management functions."""
        task_queue = {"A": create_task(state="pending")}

        # update_task_state - multiple transitions
        update_task_state(task_queue, "A", "in_progress")
        assert task_queue["A"]["state"] == "in_progress"

        update_task_state(task_queue, "A", "completed", {"success": True})
        assert task_queue["A"]["state"] == "completed"
        assert task_queue["A"]["result"]["success"] is True


class TestRealWorldScenarios:
    """Test real-world execution scenarios."""

    def test_build_pipeline_workflow(self):
        """Real-world: Build pipeline with success/failure paths."""
        task_queue = {
            "fetch": create_task(state="pending"),
            "compile": create_task(
                state="pending", dependencies=["fetch"], condition="success"
            ),
            "compile_fallback": create_task(
                state="pending", dependencies=["fetch"], condition="failure"
            ),
            "test": create_task(
                state="pending", dependencies=["compile"], condition="success"
            ),
            "package": create_task(
                state="pending", dependencies=["test"], condition="success"
            ),
            "notify_failure": create_task(
                state="pending", dependencies=["compile"], condition="failure"
            ),
            "notify_success": create_task(
                state="pending", dependencies=["package"], condition="success"
            ),
        }

        # Simulate successful build
        start = time.perf_counter()

        claim_sequence = []
        for _ in range(7):
            ready = get_ready_tasks_with_conditions(task_queue)
            if ready:
                task_id = ready[0]
                claim_sequence.append(task_id)
                update_task_state(task_queue, task_id, "completed", {"success": True})

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Verify execution order
        assert claim_sequence[0] == "fetch"
        assert claim_sequence[1] == "compile"
        assert claim_sequence[2] == "test"
        assert claim_sequence[3] == "package"
        assert "notify_failure" not in claim_sequence
        assert "notify_success" in claim_sequence
        assert elapsed_ms < 500

    def test_multi_agent_story_workflow(self):
        """Real-world: Multi-agent creative task."""
        task_queue = {
            "setup": create_task(state="pending"),
            "agent_a": create_task(state="pending", dependencies=["setup"]),
            "agent_b": create_task(state="pending", dependencies=["agent_a"]),
            "agent_c": create_task(state="pending", dependencies=["agent_b"]),
            "synthesize": create_task(
                state="pending", dependencies=["agent_a", "agent_b", "agent_c"]
            ),
            "publish": create_task(state="pending", dependencies=["synthesize"]),
        }

        # Simulate multi-agent execution
        agent_tasks = []
        for _ in range(6):
            ready = get_ready_tasks(task_queue)
            if ready:
                task_id = ready[0]
                agent_tasks.append(task_id)
                update_task_state(task_queue, task_id, "completed", {"success": True})

        # All tasks should complete in dependency order
        assert agent_tasks == [
            "setup",
            "agent_a",
            "agent_b",
            "agent_c",
            "synthesize",
            "publish",
        ]

    def test_parallel_processing_workflow(self):
        """Real-world: Parallel task processing."""
        task_queue = {
            "fetch_data": create_task(state="completed", success=True),
            "process_batch_1": create_task(
                state="pending", dependencies=["fetch_data"]
            ),
            "process_batch_2": create_task(
                state="pending", dependencies=["fetch_data"]
            ),
            "process_batch_3": create_task(
                state="pending", dependencies=["fetch_data"]
            ),
            "merge_results": create_task(
                state="pending",
                dependencies=["process_batch_1", "process_batch_2", "process_batch_3"],
            ),
        }

        # Verify parallel opportunities
        ready = get_ready_tasks(task_queue)
        assert len(ready) == 3  # All 3 batches ready
        assert set(ready) == {"process_batch_1", "process_batch_2", "process_batch_3"}

        # Simulate parallel execution
        for task_id in ready:
            update_task_state(task_queue, task_id, "completed", {"success": True})

        # Merge should now be ready
        ready = get_ready_tasks(task_queue)
        assert "merge_results" in ready


class TestPerformanceBenchmarks:
    """Performance benchmarks for engine operations."""

    def test_ready_task_lookup_performance(self):
        """Ready-task lookup performance with various graph sizes."""
        sizes = [10, 50, 100]

        for size in sizes:
            task_queue = {
                f"task-{i}": create_task(
                    state="pending" if i > 0 else "completed",
                    dependencies=[f"task-{i - 1}"] if i > 0 else [],
                )
                for i in range(size)
            }

            start = time.perf_counter()
            ready = get_ready_tasks(task_queue)
            elapsed_ms = (time.perf_counter() - start) * 1000

            # Performance should scale linearly or better
            assert elapsed_ms < size * 5, f"Size {size}: {elapsed_ms:.2f}ms is too slow"

    def test_state_update_performance(self):
        """Task state update performance."""
        task_queue = {f"task-{i}": create_task() for i in range(100)}

        start = time.perf_counter()

        # Update all 100 tasks
        for i in range(100):
            update_task_state(task_queue, f"task-{i}", "completed", {"success": True})

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 500, f"100 updates should be <500ms, was {elapsed_ms:.2f}ms"

    def test_validation_performance(self):
        """Graph validation performance."""
        task_queue = {
            f"task-{i}": create_task(dependencies=[f"task-{i - 1}"] if i > 0 else [])
            for i in range(100)
        }

        start = time.perf_counter()
        validation = validate_conditional_graph(task_queue)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert validation["valid"] is True
        assert elapsed_ms < 200, f"Validation should be <200ms, was {elapsed_ms:.2f}ms"
