"""
Task affinity scoring for personality-driven task assignment.

Calculates how well-suited each agent is for specific tasks based on
personality traits and task characteristics.

Story 2.3: Implement Task Affinity Scoring
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

from .personality import (
    ARCHITECT_PERSONALITY,
    EXECUTOR_PERSONALITY,
    EXPERIMENTER_PERSONALITY,
    AgentPersonality,
)


class TaskType(Enum):
    """Task classification types."""

    ARCHITECTURE = "architecture"  # System design, planning
    IMPLEMENTATION = "implementation"  # Coding, building
    TESTING = "testing"  # Test writing, validation
    CREATIVE = "creative"  # Creative writing, design
    ANALYSIS = "analysis"  # Research, evaluation
    REVIEW = "review"  # Code review, critique
    PLANNING = "planning"  # Task planning, organization
    DESIGN = "design"  # UX/UI design


class TaskComplexity(Enum):
    """Task difficulty assessment."""

    SIMPLE = 1.0  # Straightforward, low cognitive load
    MODERATE = 2.0  # Requires attention to detail
    COMPLEX = 3.0  # Multiple moving parts, tradeoffs
    DIFFICULT = 4.0  # Requires deep expertise, novel approach


@dataclass
class TaskProfile:
    """Complete task profile for affinity calculation."""

    task_type: TaskType
    complexity: TaskComplexity
    description: str
    requires_creativity: bool = False
    requires_precision: bool = False
    novel_problem: bool = False
    time_critical: bool = False

    def get_affinity_weights(self) -> Dict[str, float]:
        """
        Calculate weights for task characteristics.

        Returns weights between 0.0 and 1.0 for each personality type.
        """
        weights = {"architect": 0.3, "executor": 0.3, "experimenter": 0.3}

        # Adjust based on task type
        type_weights = {
            TaskType.ARCHITECTURE: {
                "architect": 0.9,
                "executor": 0.3,
                "experimenter": 0.5,
            },
            TaskType.IMPLEMENTATION: {
                "architect": 0.4,
                "executor": 0.9,
                "experimenter": 0.3,
            },
            TaskType.TESTING: {"architect": 0.5, "executor": 0.8, "experimenter": 0.4},
            TaskType.CREATIVE: {"architect": 0.6, "executor": 0.2, "experimenter": 0.9},
            TaskType.ANALYSIS: {"architect": 0.8, "executor": 0.4, "experimenter": 0.6},
            TaskType.REVIEW: {"architect": 0.7, "executor": 0.6, "experimenter": 0.4},
            TaskType.PLANNING: {"architect": 0.8, "executor": 0.6, "experimenter": 0.3},
            TaskType.DESIGN: {"architect": 0.7, "executor": 0.3, "experimenter": 0.8},
        }

        if self.task_type in type_weights:
            for agent, weight in type_weights[self.task_type].items():
                weights[agent] = weight

        # Adjust based on complexity
        complexity_adjustment = {
            TaskComplexity.SIMPLE: {
                "architect": 0.7,
                "executor": 1.0,
                "experimenter": 0.8,
            },
            TaskComplexity.MODERATE: {
                "architect": 0.9,
                "executor": 0.9,
                "experimenter": 0.8,
            },
            TaskComplexity.COMPLEX: {
                "architect": 1.0,
                "executor": 0.8,
                "experimenter": 0.9,
            },
            TaskComplexity.DIFFICULT: {
                "architect": 1.0,
                "executor": 0.7,
                "experimenter": 1.0,
            },
        }

        if self.complexity in complexity_adjustment:
            for agent in weights:
                weights[agent] *= complexity_adjustment[self.complexity].get(agent, 1.0)

        # Adjust based on special characteristics
        if self.requires_creativity:
            weights["experimenter"] *= 1.3
            weights["architect"] *= 1.1
            weights["executor"] *= 0.8

        if self.requires_precision:
            weights["executor"] *= 1.2
            weights["architect"] *= 1.1
            weights["experimenter"] *= 0.7

        if self.novel_problem:
            weights["experimenter"] *= 1.4
            weights["architect"] *= 1.1
            weights["executor"] *= 0.7

        if self.time_critical:
            weights["executor"] *= 1.2
            weights["architect"] *= 0.9
            weights["experimenter"] *= 0.8

        # Normalize to 0.0-1.0 range
        max_weight = max(weights.values())
        if max_weight > 1.0:
            weights = {agent: w / max_weight for agent, w in weights.items()}

        return weights


def score_task_affinity(
    task_profile: TaskProfile, personality: AgentPersonality
) -> float:
    """
    Calculate affinity score between task and agent personality.

    Args:
        task_profile: Task characteristics
        personality: Agent personality

    Returns:
        Score between 0.0 and 1.0, where 1.0 is perfect match

    AC3: Architect scores high on system design tasks (>0.9)
    AC3: Executor scores high on implementation tasks (>0.9)
    AC3: Experimenter scores high on novel/edge case tasks (>0.9)
    """
    # Get base weight from task profile
    weights = task_profile.get_affinity_weights()
    agent_name = personality.name.lower()

    if agent_name == "athena":
        base_weight = weights.get("architect", 0.5)
    elif agent_name == "cato":
        base_weight = weights.get("executor", 0.5)
    elif agent_name == "zephyr":
        base_weight = weights.get("experimenter", 0.5)
    else:
        base_weight = 0.5

    # Get personality task preference
    task_type_str = task_profile.task_type.value
    personality_preference = personality.task_preferences.get(task_type_str, 0.5)

    # Combine factors: 50% task profile weight, 50% personality preference
    # This ensures personality-matched tasks consistently score >0.9
    combined_score = (base_weight * 0.5) + (personality_preference * 0.5)

    # Clamp to 0.0-1.0
    return min(1.0, max(0.0, combined_score))


def get_best_agent_for_task(
    task_profile: TaskProfile, available_agents: List[AgentPersonality]
) -> Tuple[AgentPersonality, float]:
    """
    Find best agent for a task based on affinity.

    Args:
        task_profile: Task to assign
        available_agents: List of available agents

    Returns:
        Tuple of (best_agent, affinity_score)

    AC4: Different agents selected for personality-matching tasks
    """
    if not available_agents:
        raise ValueError("No agents available")

    scores = [
        (agent, score_task_affinity(task_profile, agent)) for agent in available_agents
    ]

    best_agent, best_score = max(scores, key=lambda x: x[1])
    return best_agent, best_score


def rank_agents_by_affinity(
    task_profile: TaskProfile, available_agents: List[AgentPersonality]
) -> List[Tuple[AgentPersonality, float]]:
    """
    Rank all agents by affinity for a task.

    Returns list of (agent, score) tuples sorted by score descending.
    """
    scores = [
        (agent, score_task_affinity(task_profile, agent)) for agent in available_agents
    ]
    return sorted(scores, key=lambda x: x[1], reverse=True)


def describe_task_affinity(task_profile: TaskProfile) -> str:
    """Generate human-readable task affinity analysis."""
    all_agents = [ARCHITECT_PERSONALITY, EXECUTOR_PERSONALITY, EXPERIMENTER_PERSONALITY]
    ranks = rank_agents_by_affinity(task_profile, all_agents)

    output = f"""
Task: {task_profile.description}
Type: {task_profile.task_type.value}
Complexity: {task_profile.complexity.name}

Agent Affinity Scores:
"""
    for agent, score in ranks:
        bar_length = int(score * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)
        output += f"  {agent.name:12} [{bar}] {score:.2f}\n"

    best_agent, best_score = ranks[0]
    output += f"\nBest Agent: {best_agent.name} ({best_score:.2f})\n"

    return output
