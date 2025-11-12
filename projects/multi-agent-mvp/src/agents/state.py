"""
Agent state management for tracking agent activity and preferences.

Maintains observable state of each agent including current task,
execution history, and preference learning.

Story 2.1: Define Agent Personality Architecture
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .personality import AgentPersonality


@dataclass
class TaskExecution:
    """Record of a single task execution."""

    task_id: str
    task_type: str
    complexity: str
    start_time: str
    end_time: Optional[str]
    status: str  # in_progress, completed, failed
    affinity_score: float
    notes: str = ""


@dataclass
class AgentState:
    """Complete observable state of an agent."""

    agent_name: str
    personality: Dict  # AgentPersonality as dict
    current_task: Optional[str] = None
    current_task_start: Optional[str] = None
    task_history: List[TaskExecution] = field(default_factory=list)
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time_ms: float = 0.0
    task_type_preferences: Dict[str, float] = field(default_factory=dict)
    preferred_agents_to_collaborate_with: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert state to dict for JSON serialization."""
        return {
            "agent_name": self.agent_name,
            "personality": self.personality,
            "current_task": self.current_task,
            "current_task_start": self.current_task_start,
            "task_history": [
                {
                    "task_id": t.task_id,
                    "task_type": t.task_type,
                    "complexity": t.complexity,
                    "start_time": t.start_time,
                    "end_time": t.end_time,
                    "status": t.status,
                    "affinity_score": t.affinity_score,
                    "notes": t.notes,
                }
                for t in self.task_history
            ],
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "total_execution_time_ms": self.total_execution_time_ms,
            "task_type_preferences": self.task_type_preferences,
            "preferred_agents_to_collaborate_with": self.preferred_agents_to_collaborate_with,
        }


def create_agent_state(personality: AgentPersonality) -> AgentState:
    """
    Create initial agent state from personality.

    Args:
        personality: Agent personality definition

    Returns:
        Initial AgentState
    """
    return AgentState(
        agent_name=personality.name,
        personality=personality.to_dict(),
        task_type_preferences=personality.task_preferences.copy(),
    )


def claim_task(
    agent_state: AgentState,
    task_id: str,
    task_type: str,
    complexity: str,
    affinity_score: float,
) -> AgentState:
    """
    Record agent claiming a task.

    Args:
        agent_state: Current agent state
        task_id: Task being claimed
        task_type: Type of task
        complexity: Task complexity level
        affinity_score: Affinity score for this task

    Returns:
        Updated agent state
    """
    agent_state.current_task = task_id
    agent_state.current_task_start = datetime.now().isoformat()
    return agent_state


def complete_task(
    agent_state: AgentState, task_id: str, execution_time_ms: float, notes: str = ""
) -> AgentState:
    """
    Record task completion.

    Args:
        agent_state: Current agent state
        task_id: Completed task
        execution_time_ms: Time taken
        notes: Optional execution notes

    Returns:
        Updated agent state
    """
    if agent_state.current_task != task_id:
        raise ValueError(f"Agent not executing task {task_id}")

    # Find the task in history
    for task in agent_state.task_history:
        if task.task_id == task_id:
            task.status = "completed"
            task.end_time = datetime.now().isoformat()
            break

    agent_state.completed_tasks += 1
    agent_state.total_execution_time_ms += execution_time_ms
    agent_state.current_task = None
    agent_state.current_task_start = None

    return agent_state


def fail_task(
    agent_state: AgentState, task_id: str, error_message: str = ""
) -> AgentState:
    """
    Record task failure.

    Args:
        agent_state: Current agent state
        task_id: Failed task
        error_message: Failure reason

    Returns:
        Updated agent state
    """
    if agent_state.current_task != task_id:
        raise ValueError(f"Agent not executing task {task_id}")

    # Find the task in history
    for task in agent_state.task_history:
        if task.task_id == task_id:
            task.status = "failed"
            task.end_time = datetime.now().isoformat()
            task.notes = error_message
            break

    agent_state.failed_tasks += 1
    agent_state.current_task = None
    agent_state.current_task_start = None

    return agent_state


def update_agent_history(
    agent_state: AgentState,
    task_id: str,
    task_type: str,
    complexity: str,
    affinity_score: float,
) -> AgentState:
    """
    Add task to agent's execution history.

    Args:
        agent_state: Current agent state
        task_id: Task being added
        task_type: Type of task
        complexity: Complexity level
        affinity_score: Affinity score

    Returns:
        Updated agent state with task in history
    """
    execution = TaskExecution(
        task_id=task_id,
        task_type=task_type,
        complexity=complexity,
        start_time=datetime.now().isoformat(),
        end_time=None,
        status="in_progress",
        affinity_score=affinity_score,
    )

    agent_state.task_history.append(execution)
    return agent_state


def get_agent_stats(agent_state: AgentState) -> Dict:
    """
    Calculate agent statistics.

    Args:
        agent_state: Agent to analyze

    Returns:
        Dict with statistics
    """
    total_tasks = agent_state.completed_tasks + agent_state.failed_tasks

    success_rate = 0.0
    if total_tasks > 0:
        success_rate = agent_state.completed_tasks / total_tasks

    avg_execution_time = 0.0
    if agent_state.completed_tasks > 0:
        avg_execution_time = (
            agent_state.total_execution_time_ms / agent_state.completed_tasks
        )

    # Calculate task type affinity from history
    task_type_stats = {}
    for task in agent_state.task_history:
        if task.status == "completed":
            if task.task_type not in task_type_stats:
                task_type_stats[task.task_type] = {"count": 0, "affinity": 0.0}
            task_type_stats[task.task_type]["count"] += 1
            task_type_stats[task.task_type]["affinity"] += task.affinity_score

    # Average affinity per task type
    for task_type in task_type_stats:
        count = task_type_stats[task_type]["count"]
        if count > 0:
            task_type_stats[task_type]["affinity"] /= count

    return {
        "agent_name": agent_state.agent_name,
        "total_tasks_executed": total_tasks,
        "completed_tasks": agent_state.completed_tasks,
        "failed_tasks": agent_state.failed_tasks,
        "success_rate": success_rate,
        "total_execution_time_ms": agent_state.total_execution_time_ms,
        "avg_execution_time_per_task_ms": avg_execution_time,
        "task_type_statistics": task_type_stats,
        "current_task": agent_state.current_task,
        "preferred_collaborators": agent_state.preferred_agents_to_collaborate_with,
    }


def describe_agent_state(agent_state: AgentState) -> str:
    """Generate human-readable agent state summary."""
    stats = get_agent_stats(agent_state)

    output = f"""
Agent: {agent_state.agent_name}
Current Task: {agent_state.current_task or "None"}

Statistics:
  Total Tasks: {stats["total_tasks_executed"]}
  Completed: {stats["completed_tasks"]}
  Failed: {stats["failed_tasks"]}
  Success Rate: {stats["success_rate"]:.1%}

Performance:
  Total Time: {stats["total_execution_time_ms"]:.0f}ms
  Avg Time/Task: {stats["avg_execution_time_per_task_ms"]:.0f}ms

Task Type Performance:
"""
    for task_type, type_stats in stats["task_type_statistics"].items():
        output += f"  {task_type}: {type_stats['count']} completed, avg affinity {type_stats['affinity']:.2f}\n"

    if stats["preferred_collaborators"]:
        output += f"\nPreferred Collaborators: {', '.join(stats['preferred_collaborators'])}\n"

    return output
