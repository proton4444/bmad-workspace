"""
Agent agency module - autonomous task selection based on affinity.

Implements agent execution loop where agents autonomously select and claim
tasks based on their personality preferences and task affinity scores.

Story 2.4: Implement Agent Agency in Task Selection
Acceptance Criteria:
- AC1: Agent execution loop includes: get ready tasks → score affinity → claim highest-affinity
- AC2: Executor preferentially claims implementation tasks
- AC3: Architect preferentially claims design tasks
- AC4: Emergent behavior validates personality preferences
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.agents.affinity import TaskProfile, score_task_affinity
from src.agents.personality import AgentPersonality
from src.agents.state import AgentState, claim_task, complete_task, update_agent_history


@dataclass
class Task:
    """Simple task representation with core properties."""

    id: str
    name: str
    task_type: str  # e.g., 'architecture', 'implementation', 'creative', etc.
    complexity: str  # 'simple', 'moderate', 'complex', 'difficult'
    description: str
    is_ready: bool = False
    claimed_by: Optional[str] = None
    completed: bool = False

    def to_task_profile(self) -> TaskProfile:
        """Convert Task to TaskProfile for affinity scoring."""
        from .affinity import TaskComplexity, TaskType

        # Map string task_type to TaskType enum
        task_type_map = {
            "architecture": TaskType.ARCHITECTURE,
            "implementation": TaskType.IMPLEMENTATION,
            "testing": TaskType.TESTING,
            "creative": TaskType.CREATIVE,
            "analysis": TaskType.ANALYSIS,
            "review": TaskType.REVIEW,
            "planning": TaskType.PLANNING,
            "design": TaskType.DESIGN,
        }

        # Map string complexity to TaskComplexity enum
        complexity_map = {
            "simple": TaskComplexity.SIMPLE,
            "moderate": TaskComplexity.MODERATE,
            "complex": TaskComplexity.COMPLEX,
            "difficult": TaskComplexity.DIFFICULT,
        }

        task_type_enum = task_type_map.get(self.task_type, TaskType.ANALYSIS)
        complexity_enum = complexity_map.get(self.complexity, TaskComplexity.MODERATE)

        return TaskProfile(
            task_type=task_type_enum,
            complexity=complexity_enum,
            description=self.description,
            requires_creativity=self.task_type in ["creative", "design"],
            requires_precision=self.task_type in ["implementation", "testing"],
            novel_problem=self.task_type in ["creative", "architecture"],
            time_critical=self.task_type in ["implementation", "testing"],
        )


@dataclass
class AgencyMetrics:
    """Metrics tracking agent agency and task selection behavior."""

    agent_name: str
    total_tasks_claimed: int = 0
    tasks_by_type: Dict[str, int] = field(default_factory=dict)
    average_affinity_score: float = 0.0
    preference_match_percentage: float = 0.0
    execution_count: int = 0

    def update_from_claim(
        self, task: Task, affinity_score: float, personality: AgentPersonality
    ):
        """Update metrics after claiming a task."""
        self.total_tasks_claimed += 1

        # Track task type distribution
        if task.task_type not in self.tasks_by_type:
            self.tasks_by_type[task.task_type] = 0
        self.tasks_by_type[task.task_type] += 1

        # Update average affinity score
        self.average_affinity_score = (
            self.average_affinity_score * (self.total_tasks_claimed - 1)
            + affinity_score
        ) / self.total_tasks_claimed

        # Calculate preference match (does claimed task match personality?)
        preference = personality.task_preferences.get(task.task_type, 0.0)
        is_high_preference = preference > 0.75
        is_match = affinity_score > 0.75

        if is_match and is_high_preference:
            # Strong match to preferences
            self.preference_match_percentage = (
                self.preference_match_percentage * (self.total_tasks_claimed - 1) + 1.0
            ) / self.total_tasks_claimed
        else:
            self.preference_match_percentage = (
                self.preference_match_percentage * (self.total_tasks_claimed - 1) + 0.0
            ) / self.total_tasks_claimed

    def to_dict(self) -> Dict:
        """Convert metrics to dict for JSON serialization."""
        return {
            "agent_name": self.agent_name,
            "total_tasks_claimed": self.total_tasks_claimed,
            "tasks_by_type": self.tasks_by_type,
            "average_affinity_score": round(self.average_affinity_score, 3),
            "preference_match_percentage": round(self.preference_match_percentage, 3),
            "execution_count": self.execution_count,
        }


class AgentExecutor:
    """Manages agent execution loop with autonomous task selection."""

    def __init__(self, agent_state: AgentState, personality: AgentPersonality):
        """Initialize executor with agent state and personality."""
        self.agent_state = agent_state
        self.personality = personality
        self.metrics = AgencyMetrics(agent_name=personality.name)

    def score_task_affinity(self, task: Task) -> float:
        """Score task affinity based on personality."""
        profile = task.to_task_profile()
        return score_task_affinity(profile, self.personality)

    def get_best_available_task(self, ready_tasks: List[Task]) -> Optional[Task]:
        """
        Select best available task based on affinity scoring.

        Algorithm:
        1. Score all ready tasks by affinity
        2. Return task with highest affinity score
        3. Return None if no ready tasks available

        Args:
            ready_tasks: List of tasks ready to be claimed

        Returns:
            Best task for this agent, or None if no tasks available
        """
        if not ready_tasks:
            return None

        # Score all ready tasks
        scored_tasks = [(task, self.score_task_affinity(task)) for task in ready_tasks]

        # Find best task (highest affinity)
        best_task, best_score = max(scored_tasks, key=lambda x: x[1])
        return best_task

    def claim_task(self, task: Task) -> bool:
        """
        Claim a task for execution.

        Args:
            task: Task to claim

        Returns:
            True if claim successful, False if task already claimed
        """
        if task.claimed_by is not None:
            return False

        task.claimed_by = self.personality.name
        affinity_score = self.score_task_affinity(task)
        self.metrics.update_from_claim(task, affinity_score, self.personality)

        # Update agent state using module-level function
        self.agent_state = update_agent_history(
            self.agent_state,
            task_id=task.id,
            task_type=task.task_type,
            complexity=task.complexity,
            affinity_score=affinity_score,
        )
        self.agent_state = claim_task(
            self.agent_state,
            task_id=task.id,
            task_type=task.task_type,
            complexity=task.complexity,
            affinity_score=affinity_score,
        )

        return True

    def complete_task(self, task: Task):
        """Mark task as completed."""
        task.completed = True
        # Update agent state using module-level function
        if self.agent_state.current_task == task.id:
            self.agent_state = complete_task(
                self.agent_state,
                task_id=task.id,
                execution_time_ms=0.0,  # Could be calculated from task start time
                notes="Task completed by agent",
            )

    def execute_task(self, task: Task) -> bool:
        """
        Execute one task and update state.

        Args:
            task: Task to execute

        Returns:
            True if execution successful
        """
        if self.claim_task(task):
            self.complete_task(task)
            self.metrics.execution_count += 1
            return True
        return False

    def execution_loop(self, ready_tasks: List[Task], iterations: int = 1) -> int:
        """
        Execute agent's task selection loop multiple times.

        Loop:
        1. Get ready tasks
        2. Score affinity for each
        3. Claim highest-affinity task
        4. Complete task
        5. Repeat

        Args:
            ready_tasks: Available tasks to claim
            iterations: Number of task claims to attempt

        Returns:
            Number of tasks successfully claimed and completed
        """
        executed = 0
        for _ in range(iterations):
            best_task = self.get_best_available_task(ready_tasks)
            if best_task is None:
                break  # No more ready tasks

            if self.execute_task(best_task):
                executed += 1

        return executed

    def get_metrics(self) -> AgencyMetrics:
        """Get current execution metrics."""
        return self.metrics

    def get_metrics_dict(self) -> Dict:
        """Get metrics as dict for JSON serialization."""
        return self.metrics.to_dict()


def demonstrate_agent_agency(
    agents: Dict[str, Tuple[AgentState, AgentPersonality]],
    tasks: List[Task],
) -> Dict[str, AgencyMetrics]:
    """
    Demonstrate agent agency by running execution loop for all agents.

    Simulates multiple agents autonomously selecting and executing tasks
    based on their personality preferences.

    Args:
        agents: Dict mapping agent names to (state, personality) tuples
        tasks: List of available tasks

    Returns:
        Dict mapping agent names to their execution metrics
    """
    # Create executors
    executors = {
        name: AgentExecutor(state, personality)
        for name, (state, personality) in agents.items()
    }

    # Mark all tasks ready initially
    for task in tasks:
        task.is_ready = True

    # Execute round-robin: each agent gets a turn claiming a task
    executed = {name: 0 for name in agents}
    max_rounds = len(tasks)

    for round_num in range(max_rounds):
        # Each agent gets to claim one task
        for agent_name in executors:
            unclaimed_tasks = [t for t in tasks if t.claimed_by is None]
            if not unclaimed_tasks:
                break

            executor = executors[agent_name]
            best_task = executor.get_best_available_task(unclaimed_tasks)

            if best_task is not None:
                executor.execute_task(best_task)
                executed[agent_name] += 1

    # Return metrics for each agent
    return {name: executor.get_metrics() for name, executor in executors.items()}


def analyze_agency_outcomes(metrics_dict: Dict[str, AgencyMetrics]) -> Dict:
    """
    Analyze outcomes of agent agency execution.

    Checks whether agents actually preferred their personality-matched tasks.

    Args:
        metrics_dict: Dict of agent metrics

    Returns:
        Analysis showing preference match and behavior validation
    """
    analysis = {
        "summary": {},
        "agent_behaviors": {},
        "emergent_patterns": {},
    }

    for agent_name, metrics in metrics_dict.items():
        analysis["summary"][agent_name] = {
            "tasks_claimed": metrics.total_tasks_claimed,
            "average_affinity": round(metrics.average_affinity_score, 3),
            "preference_match": round(metrics.preference_match_percentage, 3),
        }

        # Track which task types agent chose
        analysis["agent_behaviors"][agent_name] = {
            "task_distribution": metrics.tasks_by_type,
            "specialization": (
                "High"
                if max(
                    (
                        metrics.tasks_by_type.get(task_type, 0)
                        for task_type in metrics.tasks_by_type
                    ),
                    default=0,
                )
                / max(metrics.total_tasks_claimed, 1)
                > 0.6
                else "Balanced"
            ),
        }

    # Identify emergent patterns
    # Pattern 1: Do agents specialize by task type?
    task_type_specialists = {}
    for agent_name, behavior in analysis["agent_behaviors"].items():
        if behavior["specialization"] == "High":
            main_type = max(
                behavior["task_distribution"],
                key=behavior["task_distribution"].get,
            )
            if main_type not in task_type_specialists:
                task_type_specialists[main_type] = []
            task_type_specialists[main_type].append(agent_name)

    analysis["emergent_patterns"]["task_specialization"] = task_type_specialists
    analysis["emergent_patterns"]["has_specialization"] = len(task_type_specialists) > 0

    return analysis


def validate_agent_preferences(
    metrics_dict: Dict[str, AgencyMetrics],
    personality_dict: Dict[str, AgentPersonality],
) -> Dict[str, bool]:
    """
    Validate that agents actually preferred personality-matched tasks.

    Args:
        metrics_dict: Metrics from agent execution
        personality_dict: Personality definitions for reference

    Returns:
        Dict of validation results
    """
    validation = {}

    for agent_name, metrics in metrics_dict.items():
        personality = personality_dict.get(agent_name)
        if not personality:
            continue

        # Get agent's preferred task types (>0.75 affinity)
        preferred_types = {
            task_type
            for task_type, affinity in personality.task_preferences.items()
            if affinity > 0.75
        }

        # Get actual task types claimed
        claimed_types = set(metrics.tasks_by_type.keys())

        # Calculate match: what % of claimed tasks were preferred?
        if claimed_types:
            preference_match = len(preferred_types & claimed_types) / len(claimed_types)
        else:
            preference_match = 0.0

        validation[agent_name] = {
            "preferred_task_types": list(preferred_types),
            "claimed_task_types": list(claimed_types),
            "preference_match_ratio": round(preference_match, 2),
            "validates": preference_match > 0.5,  # >50% match is validation
        }

    return validation
