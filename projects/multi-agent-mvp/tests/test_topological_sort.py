"""
Test suite for topological sort functionality (Story 1.2).

Tests Kahn's algorithm implementation for task dependency ordering,
parallel batch detection, and ordering validation.

Acceptance Criteria:
- AC1: Function topological_sort(task_graph) implements Kahn's algorithm
- AC2: Returns ordered list of task IDs where dependencies satisfied in order
- AC3: 10-task DAG produces valid ordering in <100ms
- AC4: Test case {A: [], B: [A], C: [A, B]} produces [A, B, C]
- AC5: Test case {A: [], B: [A], C: [A]} produces valid ordering with B and C interchangeable
- AC6: Enables parallel execution detection (identifies tasks that can run concurrently)
"""

import time
from typing import Dict, List

import pytest
from src.core.topological_sort import (
    get_parallel_batches,
    topological_sort,
    validate_ordering,
)


class TestTopologicalSort:
    """Test suite for topological_sort function using Kahn's algorithm."""

    def test_simple_linear_chain(self):
        """AC4: Test case {A: [], B: [A], C: [A, B]} produces [A, B, C]"""
        graph = {"A": [], "B": ["A"], "C": ["A", "B"]}
        result = topological_sort(graph)

        # Verify exact ordering for this specific case
        assert result == ["A", "B", "C"], f"Expected [A, B, C], got {result}"

        # Verify dependencies are satisfied
        assert validate_ordering(graph, result) is True, (
            "Ordering should satisfy all dependencies"
        )

    def test_parallel_tasks(self):
        """AC5: Test case {A: [], B: [A], C: [A]} allows B and C interchangeable"""
        graph = {"A": [], "B": ["A"], "C": ["A"]}
        result = topological_sort(graph)

        # Verify A comes first
        assert result[0] == "A", "A must be first (no dependencies)"

        # Verify B and C come after A (order between them doesn't matter)
        assert set(result[1:]) == {"B", "C"}, "B and C should be in positions 1 and 2"

        # Verify dependencies are satisfied
        assert validate_ordering(graph, result) is True, (
            "Ordering should satisfy all dependencies"
        )

    def test_empty_graph(self):
        """Test topological sort of empty graph"""
        graph = {}
        result = topological_sort(graph)

        assert result == [], "Empty graph should produce empty ordering"

    def test_single_node(self):
        """Test topological sort of single node with no dependencies"""
        graph = {"A": []}
        result = topological_sort(graph)

        assert result == ["A"], "Single node should produce single-element ordering"

    def test_multiple_roots(self):
        """Test graph with multiple nodes that have no dependencies"""
        graph = {"A": [], "B": [], "C": ["A", "B"]}
        result = topological_sort(graph)

        # A and B can be in any order, but both must come before C
        assert len(result) == 3, "Should have 3 nodes"
        assert result[2] == "C", "C must be last (depends on A and B)"
        assert set(result[:2]) == {"A", "B"}, "A and B should be first (in any order)"
        assert validate_ordering(graph, result) is True

    def test_diamond_dependency(self):
        """Test diamond-shaped dependency graph"""
        graph = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        result = topological_sort(graph)

        # Verify A is first
        assert result[0] == "A", "A must be first"

        # Verify D is last
        assert result[3] == "D", "D must be last"

        # Verify B and C are in middle (any order)
        assert set(result[1:3]) == {"B", "C"}, "B and C should be in middle positions"

        assert validate_ordering(graph, result) is True

    def test_ten_task_dag_performance(self):
        """AC3: 10-task DAG produces valid ordering in <100ms"""
        # Create 10-task linear chain
        graph = {f"task-{i}": [f"task-{i - 1}"] if i > 0 else [] for i in range(10)}

        start_time = time.perf_counter()
        result = topological_sort(graph)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert len(result) == 10, "Should return all 10 tasks"
        assert elapsed_ms < 100, f"Should complete in <100ms, took {elapsed_ms:.2f}ms"
        assert validate_ordering(graph, result) is True

    def test_large_graph_performance(self):
        """Test performance with 100-task graph"""
        # Create 100-task linear chain
        graph = {f"task-{i}": [f"task-{i - 1}"] if i > 0 else [] for i in range(100)}

        start_time = time.perf_counter()
        result = topological_sort(graph)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert len(result) == 100, "Should return all 100 tasks"
        assert elapsed_ms < 500, (
            f"Should complete reasonably fast, took {elapsed_ms:.2f}ms"
        )
        assert validate_ordering(graph, result) is True

    def test_disconnected_components(self):
        """Test graph with multiple disconnected components"""
        graph = {"A": [], "B": ["A"], "X": [], "Y": ["X"]}
        result = topological_sort(graph)

        assert len(result) == 4, "Should include all nodes"

        # Verify A comes before B
        assert result.index("A") < result.index("B"), "A must come before B"

        # Verify X comes before Y
        assert result.index("X") < result.index("Y"), "X must come before Y"

        assert validate_ordering(graph, result) is True

    def test_complex_dag(self):
        """Test more complex DAG structure"""
        graph = {
            "build": [],
            "test": ["build"],
            "lint": ["build"],
            "deploy": ["test", "lint"],
            "verify": ["deploy"],
        }
        result = topological_sort(graph)

        assert len(result) == 5, "Should include all 5 tasks"

        # Verify build is first
        assert result[0] == "build", "build must be first"

        # Verify verify is last
        assert result[4] == "verify", "verify must be last"

        # Verify deploy comes before verify
        assert result.index("deploy") < result.index("verify"), (
            "deploy must come before verify"
        )

        # Verify test and lint come before deploy
        assert result.index("test") < result.index("deploy"), (
            "test must come before deploy"
        )
        assert result.index("lint") < result.index("deploy"), (
            "lint must come before deploy"
        )

        assert validate_ordering(graph, result) is True


class TestParallelBatches:
    """Test suite for parallel batch detection (AC6)."""

    def test_linear_chain_batches(self):
        """Linear chain should produce batches of size 1"""
        graph = {"A": [], "B": ["A"], "C": ["B"]}
        batches = get_parallel_batches(graph)

        assert len(batches) == 3, "Linear chain should have 3 batches"
        assert batches[0] == ["A"], "First batch should be [A]"
        assert batches[1] == ["B"], "Second batch should be [B]"
        assert batches[2] == ["C"], "Third batch should be [C]"

    def test_parallel_tasks_batches(self):
        """AC6: Parallel tasks should be grouped in same batch"""
        graph = {"A": [], "B": ["A"], "C": ["A"]}
        batches = get_parallel_batches(graph)

        assert len(batches) == 2, "Should have 2 batches"
        assert batches[0] == ["A"], "First batch should be [A]"
        assert set(batches[1]) == {"B", "C"}, (
            "Second batch should contain B and C (parallel)"
        )

    def test_diamond_batches(self):
        """Diamond graph should show parallel middle layer"""
        graph = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        batches = get_parallel_batches(graph)

        assert len(batches) == 3, "Should have 3 batches"
        assert batches[0] == ["A"], "First batch: [A]"
        assert set(batches[1]) == {"B", "C"}, "Second batch: B and C (parallel)"
        assert batches[2] == ["D"], "Third batch: [D]"

    def test_complex_parallel_structure(self):
        """Test complex graph with multiple parallel opportunities"""
        graph = {
            "build": [],
            "test": ["build"],
            "lint": ["build"],
            "deploy": ["test", "lint"],
            "verify": ["deploy"],
        }
        batches = get_parallel_batches(graph)

        # Build first
        assert batches[0] == ["build"]

        # Test and lint can run in parallel
        assert set(batches[1]) == {"test", "lint"}

        # Deploy after test and lint
        assert batches[2] == ["deploy"]

        # Verify last
        assert batches[3] == ["verify"]

    def test_empty_graph_batches(self):
        """Empty graph should produce empty batches"""
        graph = {}
        batches = get_parallel_batches(graph)

        assert batches == [], "Empty graph should produce empty batches"

    def test_all_independent_tasks(self):
        """All independent tasks should be in single batch"""
        graph = {"A": [], "B": [], "C": [], "D": []}
        batches = get_parallel_batches(graph)

        assert len(batches) == 1, "All independent tasks should be in one batch"
        assert set(batches[0]) == {"A", "B", "C", "D"}, "Batch should contain all tasks"


class TestValidateOrdering:
    """Test suite for ordering validation."""

    def test_valid_ordering(self):
        """Test validation of correct ordering"""
        graph = {"A": [], "B": ["A"], "C": ["B"]}
        ordering = ["A", "B", "C"]

        assert validate_ordering(graph, ordering) is True, "Valid ordering should pass"

    def test_invalid_ordering(self):
        """Test validation catches incorrect ordering"""
        graph = {"A": [], "B": ["A"], "C": ["B"]}
        ordering = ["B", "A", "C"]  # B before A violates dependency

        assert validate_ordering(graph, ordering) is False, (
            "Invalid ordering should fail"
        )

    def test_valid_parallel_ordering(self):
        """Test validation accepts valid parallel task ordering"""
        graph = {"A": [], "B": ["A"], "C": ["A"]}
        ordering = ["A", "C", "B"]  # C and B can be in any order after A

        assert validate_ordering(graph, ordering) is True, (
            "Valid parallel ordering should pass"
        )

    def test_missing_tasks(self):
        """Test validation fails if tasks are missing"""
        graph = {"A": [], "B": ["A"], "C": ["B"]}
        ordering = ["A", "B"]  # Missing C

        assert validate_ordering(graph, ordering) is False, (
            "Incomplete ordering should fail"
        )

    def test_extra_tasks(self):
        """Test validation fails if ordering has extra tasks"""
        graph = {"A": [], "B": ["A"]}
        ordering = ["A", "B", "C"]  # Extra C

        assert validate_ordering(graph, ordering) is False, (
            "Ordering with extra tasks should fail"
        )

    def test_empty_graph_valid(self):
        """Empty graph with empty ordering is valid"""
        graph = {}
        ordering = []

        assert validate_ordering(graph, ordering) is True, (
            "Empty graph/ordering should be valid"
        )

    def test_complex_valid_ordering(self):
        """Test validation with complex graph"""
        graph = {
            "build": [],
            "test": ["build"],
            "lint": ["build"],
            "deploy": ["test", "lint"],
            "verify": ["deploy"],
        }
        ordering = ["build", "test", "lint", "deploy", "verify"]

        assert validate_ordering(graph, ordering) is True, (
            "Valid complex ordering should pass"
        )

    def test_complex_invalid_ordering(self):
        """Test validation catches errors in complex graph"""
        graph = {
            "build": [],
            "test": ["build"],
            "lint": ["build"],
            "deploy": ["test", "lint"],
            "verify": ["deploy"],
        }
        ordering = [
            "build",
            "deploy",
            "test",
            "lint",
            "verify",
        ]  # deploy before test/lint

        assert validate_ordering(graph, ordering) is False, (
            "Invalid complex ordering should fail"
        )


class TestIntegrationWithTaskQueue:
    """Integration tests with task-queue.json format."""

    def test_task_queue_format_compatibility(self):
        """Test topological sort works with task-queue.json structure"""
        # Simulate task-queue.json dependency graph
        task_graph = {
            "task-1": [],  # First task (no dependencies)
            "task-2": ["task-1"],  # Depends on task-1
            "task-3": ["task-1"],  # Depends on task-1 (parallel with task-2)
            "task-4": ["task-2", "task-3"],  # Depends on both task-2 and task-3
        }

        result = topological_sort(task_graph)

        # Verify task-1 is first
        assert result[0] == "task-1"

        # Verify task-4 is last
        assert result[3] == "task-4"

        # Verify valid ordering
        assert validate_ordering(task_graph, result) is True

    def test_batch_execution_planning(self):
        """Test parallel batch detection for execution planning"""
        task_graph = {
            "setup": [],
            "fetch-data": ["setup"],
            "process-images": ["setup"],
            "process-text": ["setup"],
            "merge": ["fetch-data", "process-images", "process-text"],
            "report": ["merge"],
        }

        batches = get_parallel_batches(task_graph)

        # Verify batch structure for parallel execution
        assert batches[0] == ["setup"]
        assert set(batches[1]) == {"fetch-data", "process-images", "process-text"}
        assert batches[2] == ["merge"]
        assert batches[3] == ["report"]

        # Verify this enables parallel execution
        assert len(batches[1]) == 3, "Should identify 3 tasks that can run in parallel"
