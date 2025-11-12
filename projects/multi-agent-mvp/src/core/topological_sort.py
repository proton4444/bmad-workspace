"""
Topological sorting functionality for task dependency graphs.

Implements Kahn's algorithm for topological ordering, parallel batch detection,
and ordering validation per Architecture Decision #5 and Story 1.2.

Key Algorithm: Kahn's Algorithm (BFS-based topological sort)
1. Compute in-degree (number of dependencies) for each node
2. Start with nodes that have in-degree 0 (no dependencies)
3. Process nodes in queue, decrementing in-degree of dependents
4. Add nodes to result when their in-degree reaches 0

Time Complexity: O(V + E) where V = nodes, E = edges
Space Complexity: O(V) for in-degree tracking and queue
"""

from collections import deque
from typing import Dict, List


def topological_sort(task_graph: Dict[str, List[str]]) -> List[str]:
    """
    Compute topological ordering of tasks using Kahn's algorithm.

    Given a task dependency graph where task_graph[task] = [list of dependencies],
    returns an ordered list where all dependencies appear before dependent tasks.

    Args:
        task_graph: Adjacency list where keys are tasks and values are lists
                   of tasks they depend on. Format: {task_id: [dependency_ids]}

    Returns:
        List of task IDs in topological order, where dependencies are satisfied
        in execution order. Returns empty list for empty graph.

    Example:
        >>> graph = {"A": [], "B": ["A"], "C": ["A", "B"]}
        >>> topological_sort(graph)
        ["A", "B", "C"]

    Performance:
        AC3: 10-task DAG produces valid ordering in <100ms
    """
    if not task_graph:
        return []

    # Step 1: Compute in-degree for all nodes
    # in_degree[task] = number of dependencies task has
    in_degree = {node: 0 for node in task_graph}

    for node in task_graph:
        dependencies = task_graph[node]
        in_degree[node] = len(dependencies)

        # Ensure all dependency nodes exist in in_degree map
        for dep in dependencies:
            if dep not in in_degree:
                in_degree[dep] = 0

    # Step 2: Initialize queue with nodes that have no dependencies (in_degree = 0)
    queue = deque([node for node in in_degree if in_degree[node] == 0])
    result = []

    # Step 3: Process queue using BFS
    while queue:
        # Remove node with no dependencies
        node = queue.popleft()
        result.append(node)

        # Find all tasks that depend on this node and decrement their in-degree
        for dependent in task_graph:
            if node in task_graph[dependent]:
                in_degree[dependent] -= 1

                # If all dependencies satisfied, add to queue
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    return result


def get_parallel_batches(task_graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    Identify tasks that can execute in parallel by grouping into batches.

    Each batch contains tasks with no dependencies on each other that can
    run concurrently. Batches are ordered such that all tasks in batch N
    can execute after all tasks in batches 0..N-1 complete.

    This enables parallel execution planning and resource optimization.

    Args:
        task_graph: Adjacency list of task dependencies

    Returns:
        List of batches, where each batch is a list of tasks that can
        execute in parallel. Batches are in execution order.

    Example:
        >>> graph = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        >>> get_parallel_batches(graph)
        [["A"], ["B", "C"], ["D"]]

        Execution: A first, then B and C in parallel, then D

    AC6: Enables parallel execution detection
    """
    if not task_graph:
        return []

    # Compute in-degree for all nodes
    in_degree = {node: 0 for node in task_graph}

    for node in task_graph:
        dependencies = task_graph[node]
        in_degree[node] = len(dependencies)

        for dep in dependencies:
            if dep not in in_degree:
                in_degree[dep] = 0

    # Initialize with nodes that have no dependencies
    current_batch = [node for node in in_degree if in_degree[node] == 0]
    batches = []

    # Process in batches - all nodes at same dependency level
    while current_batch:
        batches.append(current_batch)
        next_batch = []

        # For each node in current batch, decrement in-degree of dependents
        for node in current_batch:
            for dependent in task_graph:
                if node in task_graph[dependent]:
                    in_degree[dependent] -= 1

                    # If this was the last dependency, add to next batch
                    if in_degree[dependent] == 0:
                        next_batch.append(dependent)

        current_batch = next_batch

    return batches


def validate_ordering(task_graph: Dict[str, List[str]], ordering: List[str]) -> bool:
    """
    Validate that a topological ordering respects all dependencies.

    Checks that:
    1. Ordering contains exactly the same tasks as graph
    2. For every task, all its dependencies appear earlier in ordering

    Args:
        task_graph: Adjacency list of task dependencies
        ordering: Proposed topological ordering to validate

    Returns:
        True if ordering is valid, False otherwise

    Example:
        >>> graph = {"A": [], "B": ["A"], "C": ["B"]}
        >>> validate_ordering(graph, ["A", "B", "C"])
        True
        >>> validate_ordering(graph, ["B", "A", "C"])
        False  # B before A violates dependency
    """
    if not task_graph and not ordering:
        return True

    if not task_graph or not ordering:
        return False

    # Get all nodes in graph (including those only appearing as dependencies)
    all_nodes = set(task_graph.keys())
    for dependencies in task_graph.values():
        all_nodes.update(dependencies)

    # Check 1: Ordering must contain exactly the same tasks
    if set(ordering) != all_nodes:
        return False

    # Check 2: Build position map for efficient lookup
    position = {task: idx for idx, task in enumerate(ordering)}

    # Check 3: Verify all dependencies appear before dependent tasks
    for task in task_graph:
        task_position = position[task]

        for dependency in task_graph[task]:
            dependency_position = position[dependency]

            # Dependency must appear before task
            if dependency_position >= task_position:
                return False

    return True
