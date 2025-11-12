"""
Test suite for agent personality system (Story 2.1, 2.3).

Tests personality definitions, task affinity scoring, and agent state management.

Acceptance Criteria:
- AC1: Three agent personalities fully specified
- AC2: Each personality has distinct traits and system prompts
- AC3: Architect scores high on system design (>0.9)
- AC4: Executor scores high on implementation (>0.9)
- AC5: Experimenter scores high on novel tasks (>0.9)
- AC6: 80%+ match between automated and human judgment
"""

import pytest
from src.agents.affinity import (
    TaskComplexity,
    TaskProfile,
    TaskType,
    describe_task_affinity,
    get_best_agent_for_task,
    rank_agents_by_affinity,
    score_task_affinity,
)
from src.agents.personality import (
    ARCHITECT_PERSONALITY,
    EXECUTOR_PERSONALITY,
    EXPERIMENTER_PERSONALITY,
    AgentPersonality,
    AgentRole,
    describe_personality,
    get_personality_by_name,
)
from src.agents.state import (
    AgentState,
    claim_task,
    complete_task,
    create_agent_state,
    fail_task,
    get_agent_stats,
    update_agent_history,
)


class TestPersonalityDefinitions:
    """Test suite for personality definitions (AC1, AC2)."""

    def test_architect_personality_defined(self):
        """AC1: Architect personality fully specified."""
        assert ARCHITECT_PERSONALITY.name == "Athena"
        assert ARCHITECT_PERSONALITY.role == AgentRole.ARCHITECT
        assert len(ARCHITECT_PERSONALITY.system_prompt) > 500
        assert len(ARCHITECT_PERSONALITY.traits) >= 5
        assert ARCHITECT_PERSONALITY.task_preferences is not None

    def test_executor_personality_defined(self):
        """AC1: Executor personality fully specified."""
        assert EXECUTOR_PERSONALITY.name == "Cato"
        assert EXECUTOR_PERSONALITY.role == AgentRole.EXECUTOR
        assert len(EXECUTOR_PERSONALITY.system_prompt) > 500
        assert len(EXECUTOR_PERSONALITY.traits) >= 5
        assert EXECUTOR_PERSONALITY.task_preferences is not None

    def test_experimenter_personality_defined(self):
        """AC1: Experimenter personality fully specified."""
        assert EXPERIMENTER_PERSONALITY.name == "Zephyr"
        assert EXPERIMENTER_PERSONALITY.role == AgentRole.EXPERIMENTER
        assert len(EXPERIMENTER_PERSONALITY.system_prompt) > 500
        assert len(EXPERIMENTER_PERSONALITY.traits) >= 5
        assert EXPERIMENTER_PERSONALITY.task_preferences is not None

    def test_personalities_distinct(self):
        """AC2: Personalities are distinct."""
        # System prompts should be different
        prompts = [
            ARCHITECT_PERSONALITY.system_prompt,
            EXECUTOR_PERSONALITY.system_prompt,
            EXPERIMENTER_PERSONALITY.system_prompt,
        ]
        assert len(set(prompts)) == 3, "All system prompts should be unique"

        # All prompts over 500 characters
        assert all(len(p) > 500 for p in prompts)

    def test_personality_to_dict(self):
        """AC1: Personality serializable to dict."""
        personality_dict = ARCHITECT_PERSONALITY.to_dict()

        assert "name" in personality_dict
        assert "role" in personality_dict
        assert "system_prompt" in personality_dict
        assert "traits" in personality_dict
        assert "task_preferences" in personality_dict

    def test_get_personality_by_name(self):
        """AC1: Can retrieve personalities by name."""
        assert get_personality_by_name("athena") == ARCHITECT_PERSONALITY
        assert get_personality_by_name("cato") == EXECUTOR_PERSONALITY
        assert get_personality_by_name("zephyr") == EXPERIMENTER_PERSONALITY

        # Case insensitive
        assert get_personality_by_name("ATHENA") == ARCHITECT_PERSONALITY

    def test_invalid_personality_name_raises(self):
        """Unknown personality name raises error."""
        with pytest.raises(ValueError):
            get_personality_by_name("unknown")

    def test_personality_narrative_roles(self):
        """AC2: Each personality has distinct narrative role."""
        roles = {
            ARCHITECT_PERSONALITY.narrative_role,
            EXECUTOR_PERSONALITY.narrative_role,
            EXPERIMENTER_PERSONALITY.narrative_role,
        }
        assert len(roles) == 3


class TestTaskAffinityScoring:
    """Test suite for task affinity scoring (AC3, AC4, AC5)."""

    def test_architect_affinity_system_design(self):
        """AC3: Architect scores high on system design (>0.9)."""
        task = TaskProfile(
            task_type=TaskType.ARCHITECTURE,
            complexity=TaskComplexity.COMPLEX,
            description="Design a new microservice architecture",
        )

        score = score_task_affinity(task, ARCHITECT_PERSONALITY)
        assert score > 0.9, (
            f"Architect affinity for architecture should be >0.9, got {score}"
        )

    def test_executor_affinity_implementation(self):
        """AC4: Executor scores high on implementation (>0.9)."""
        task = TaskProfile(
            task_type=TaskType.IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            description="Implement the REST API endpoints",
        )

        score = score_task_affinity(task, EXECUTOR_PERSONALITY)
        assert score > 0.9, (
            f"Executor affinity for implementation should be >0.9, got {score}"
        )

    def test_experimenter_affinity_novel_tasks(self):
        """AC5: Experimenter scores high on novel tasks (>0.9)."""
        task = TaskProfile(
            task_type=TaskType.CREATIVE,
            complexity=TaskComplexity.DIFFICULT,
            description="Explore novel visualization approaches",
            requires_creativity=True,
            novel_problem=True,
        )

        score = score_task_affinity(task, EXPERIMENTER_PERSONALITY)
        assert score > 0.9, (
            f"Experimenter affinity for novel creative tasks should be >0.9, got {score}"
        )

    def test_task_affinity_personality_preference(self):
        """AC2: Affinity considers personality task preferences."""
        task = TaskProfile(
            task_type=TaskType.ANALYSIS,
            complexity=TaskComplexity.COMPLEX,
            description="Analyze system bottlenecks",
        )

        # Architect should have high affinity (analysis in preferences)
        arch_score = score_task_affinity(task, ARCHITECT_PERSONALITY)
        exec_score = score_task_affinity(task, EXECUTOR_PERSONALITY)

        assert arch_score > exec_score

    def test_complexity_affects_affinity(self):
        """Complex tasks favor Architect and Experimenter."""
        task = TaskProfile(
            task_type=TaskType.IMPLEMENTATION,
            complexity=TaskComplexity.DIFFICULT,
            description="Implement complex algorithm",
        )

        arch_score = score_task_affinity(task, ARCHITECT_PERSONALITY)
        exec_score = score_task_affinity(task, EXECUTOR_PERSONALITY)

        # Executor high on implementation, Architect gets boosted for complexity
        assert exec_score > 0.7
        assert arch_score > 0.35

    def test_creativity_boost(self):
        """Creative tasks boost Experimenter affinity."""
        task_basic = TaskProfile(
            task_type=TaskType.DESIGN,
            complexity=TaskComplexity.MODERATE,
            description="Design UI",
        )

        task_creative = TaskProfile(
            task_type=TaskType.DESIGN,
            complexity=TaskComplexity.MODERATE,
            description="Design UI",
            requires_creativity=True,
        )

        basic_score = score_task_affinity(task_basic, EXPERIMENTER_PERSONALITY)
        creative_score = score_task_affinity(task_creative, EXPERIMENTER_PERSONALITY)

        assert creative_score > basic_score

    def test_precision_boost(self):
        """Precise tasks boost Executor affinity."""
        task_basic = TaskProfile(
            task_type=TaskType.TESTING,
            complexity=TaskComplexity.MODERATE,
            description="Test code",
        )

        task_precise = TaskProfile(
            task_type=TaskType.TESTING,
            complexity=TaskComplexity.MODERATE,
            description="Test code",
            requires_precision=True,
        )

        basic_score = score_task_affinity(task_basic, EXECUTOR_PERSONALITY)
        precise_score = score_task_affinity(task_precise, EXECUTOR_PERSONALITY)

        assert precise_score > basic_score

    def test_get_best_agent_for_task(self):
        """AC6: Best agent selection matches personality."""
        task = TaskProfile(
            task_type=TaskType.ARCHITECTURE,
            complexity=TaskComplexity.COMPLEX,
            description="Design system architecture",
        )

        agents = [ARCHITECT_PERSONALITY, EXECUTOR_PERSONALITY, EXPERIMENTER_PERSONALITY]
        best_agent, score = get_best_agent_for_task(task, agents)

        assert best_agent == ARCHITECT_PERSONALITY
        assert score > 0.9

    def test_rank_agents_by_affinity(self):
        """AC6: Agent ranking matches personality fit."""
        task = TaskProfile(
            task_type=TaskType.IMPLEMENTATION,
            complexity=TaskComplexity.SIMPLE,
            description="Code implementation",
        )

        agents = [ARCHITECT_PERSONALITY, EXECUTOR_PERSONALITY, EXPERIMENTER_PERSONALITY]
        ranking = rank_agents_by_affinity(task, agents)

        # Executor should be first
        assert ranking[0][0] == EXECUTOR_PERSONALITY
        assert ranking[0][1] > ranking[1][1]  # Score decreases down ranking
        assert ranking[1][1] > ranking[2][1]


class TestAgentStateManagement:
    """Test suite for agent state management (AC1)."""

    def test_create_agent_state(self):
        """AC1: Agent state creation from personality."""
        state = create_agent_state(ARCHITECT_PERSONALITY)

        assert state.agent_name == "Athena"
        assert state.current_task is None
        assert state.completed_tasks == 0
        assert len(state.task_history) == 0

    def test_claim_task(self):
        """Agent can claim a task."""
        state = create_agent_state(ARCHITECT_PERSONALITY)
        state = update_agent_history(state, "task-1", "architecture", "complex", 0.95)
        state = claim_task(state, "task-1", "architecture", "complex", 0.95)

        assert state.current_task == "task-1"
        assert state.current_task_start is not None

    def test_complete_task(self):
        """Agent can complete a task."""
        state = create_agent_state(ARCHITECT_PERSONALITY)
        state = update_agent_history(state, "task-1", "architecture", "complex", 0.95)
        state = claim_task(state, "task-1", "architecture", "complex", 0.95)
        state = complete_task(state, "task-1", 1000.0)

        assert state.current_task is None
        assert state.completed_tasks == 1
        assert state.total_execution_time_ms == 1000.0

    def test_fail_task(self):
        """Agent can fail a task."""
        state = create_agent_state(ARCHITECT_PERSONALITY)
        state = update_agent_history(state, "task-1", "architecture", "complex", 0.95)
        state = claim_task(state, "task-1", "architecture", "complex", 0.95)
        state = fail_task(state, "task-1", "Out of memory")

        assert state.current_task is None
        assert state.failed_tasks == 1

    def test_agent_stats(self):
        """AC6: Agent statistics calculated correctly."""
        state = create_agent_state(ARCHITECT_PERSONALITY)

        # Complete some tasks
        for i in range(5):
            state = update_agent_history(
                state, f"task-{i}", "architecture", "complex", 0.9
            )
            state = claim_task(state, f"task-{i}", "architecture", "complex", 0.9)
            state = complete_task(state, f"task-{i}", 1000.0)

        # Fail one task
        state = update_agent_history(state, "task-fail", "architecture", "complex", 0.5)
        state = claim_task(state, "task-fail", "architecture", "complex", 0.5)
        state = fail_task(state, "task-fail")

        stats = get_agent_stats(state)

        assert stats["total_tasks_executed"] == 6
        assert stats["completed_tasks"] == 5
        assert stats["failed_tasks"] == 1
        assert stats["success_rate"] > 0.8
        assert stats["avg_execution_time_per_task_ms"] == 1000.0

    def test_agent_state_to_dict(self):
        """AC1: Agent state serializable to dict."""
        state = create_agent_state(ARCHITECT_PERSONALITY)
        state = update_agent_history(state, "task-1", "architecture", "complex", 0.95)

        state_dict = state.to_dict()

        assert "agent_name" in state_dict
        assert "personality" in state_dict
        assert "task_history" in state_dict
        assert "completed_tasks" in state_dict


class TestPersonalityDifferentiation:
    """Test personality differentiation and recognition (AC2)."""

    def test_different_system_prompts(self):
        """AC2: System prompts differ by >500 characters."""
        prompts = [
            ARCHITECT_PERSONALITY.system_prompt,
            EXECUTOR_PERSONALITY.system_prompt,
            EXPERIMENTER_PERSONALITY.system_prompt,
        ]

        for i, p1 in enumerate(prompts):
            for j, p2 in enumerate(prompts):
                if i != j:
                    diff = sum(1 for a, b in zip(p1, p2) if a != b)
                    assert diff > 500, (
                        f"Prompts {i} and {j} should differ by >500 chars"
                    )

    def test_distinct_traits(self):
        """AC2: Each personality has distinct traits."""
        all_traits = {
            frozenset(ARCHITECT_PERSONALITY.traits),
            frozenset(EXECUTOR_PERSONALITY.traits),
            frozenset(EXPERIMENTER_PERSONALITY.traits),
        }

        # All trait sets should be different
        assert len(all_traits) == 3

    def test_distinct_communication_styles(self):
        """AC2: Communication styles are distinct."""
        styles = {
            ARCHITECT_PERSONALITY.communication_style,
            EXECUTOR_PERSONALITY.communication_style,
            EXPERIMENTER_PERSONALITY.communication_style,
        }

        assert len(styles) == 3

    def test_different_strength_areas(self):
        """AC2: Strength areas reflect personality."""
        arch_strengths = ARCHITECT_PERSONALITY.strength_areas
        exec_strengths = EXECUTOR_PERSONALITY.strength_areas
        exp_strengths = EXPERIMENTER_PERSONALITY.strength_areas

        # Should have minimal overlap
        arch_set = set(arch_strengths)
        exec_set = set(exec_strengths)
        exp_set = set(exp_strengths)

        # Check for some uniqueness (not all should overlap)
        overlap_12 = len(arch_set & exec_set)
        overlap_23 = len(exec_set & exp_set)
        overlap_13 = len(arch_set & exp_set)

        total_overlaps = overlap_12 + overlap_23 + overlap_13
        assert total_overlaps <= 3, "Strength areas should be mostly distinct"


class TestAcceptanceCriteria:
    """Integration tests for all acceptance criteria."""

    def test_ac1_three_personalities_specified(self):
        """AC1: Three personalities fully specified."""
        personalities = [
            ARCHITECT_PERSONALITY,
            EXECUTOR_PERSONALITY,
            EXPERIMENTER_PERSONALITY,
        ]

        for personality in personalities:
            assert personality.name
            assert personality.role
            assert len(personality.system_prompt) > 500
            assert personality.traits
            assert personality.narrative_role
            assert personality.task_preferences
            assert personality.communication_style

    def test_ac3_ac4_ac5_affinity_thresholds(self):
        """AC3, AC4, AC5: Agents score high on personality-matched tasks."""
        # Architect on architecture
        arch_task = TaskProfile(
            task_type=TaskType.ARCHITECTURE,
            complexity=TaskComplexity.DIFFICULT,
            description="Design distributed system",
        )
        arch_score = score_task_affinity(arch_task, ARCHITECT_PERSONALITY)
        assert arch_score > 0.9

        # Executor on implementation
        exec_task = TaskProfile(
            task_type=TaskType.IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            description="Code features",
        )
        exec_score = score_task_affinity(exec_task, EXECUTOR_PERSONALITY)
        assert exec_score > 0.9

        # Experimenter on creative/novel
        exp_task = TaskProfile(
            task_type=TaskType.CREATIVE,
            complexity=TaskComplexity.DIFFICULT,
            description="Explore new design directions",
            requires_creativity=True,
            novel_problem=True,
        )
        exp_score = score_task_affinity(exp_task, EXPERIMENTER_PERSONALITY)
        assert exp_score > 0.9

    def test_ac6_automated_human_agreement(self):
        """AC6: Automated assignment matches human judgment."""
        test_scenarios = [
            (TaskType.ARCHITECTURE, "Design system", ARCHITECT_PERSONALITY),
            (TaskType.IMPLEMENTATION, "Code features", EXECUTOR_PERSONALITY),
            (TaskType.CREATIVE, "Design UI", EXPERIMENTER_PERSONALITY),
            (TaskType.TESTING, "Write tests", EXECUTOR_PERSONALITY),
            (TaskType.ANALYSIS, "Analyze patterns", ARCHITECT_PERSONALITY),
        ]

        agents = [ARCHITECT_PERSONALITY, EXECUTOR_PERSONALITY, EXPERIMENTER_PERSONALITY]

        matches = 0
        for task_type, description, expected_agent in test_scenarios:
            task = TaskProfile(
                task_type=task_type,
                complexity=TaskComplexity.MODERATE,
                description=description,
            )
            best_agent, score = get_best_agent_for_task(task, agents)

            if best_agent == expected_agent:
                matches += 1

        match_rate = matches / len(test_scenarios)
        assert match_rate >= 0.8, (
            f"Should match human judgment 80%+ of time, got {match_rate:.0%}"
        )
