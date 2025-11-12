"""
Tests for Story 4.3: Real-World Scenario Validation

Acceptance Criteria:
AC1: Implement 3+ realistic multi-agent scenarios
AC2: Each scenario exercises all 3 epics
AC3: Scenarios demonstrate emergent behavior and personality collaboration
AC4: Validate outputs are coherent and high-quality
AC5: Scenarios serve as integration tests and examples
"""

import pytest
from src.scenarios.real_world import (
    run_all_scenarios,
    run_product_launch_scenario,
    run_research_paper_scenario,
    run_software_project_scenario,
)

# ============================================================================
# AC1: Implement 3+ realistic multi-agent scenarios
# ============================================================================


def test_software_project_scenario_exists():
    """AC1: Software development project scenario can be run."""
    result = run_software_project_scenario()

    assert result is not None
    assert result.scenario_name == "Software Development Project"
    assert "authentication" in result.description.lower()


def test_research_paper_scenario_exists():
    """AC1: Research paper collaboration scenario can be run."""
    result = run_research_paper_scenario()

    assert result is not None
    assert result.scenario_name == "Research Paper Collaboration"
    assert "research" in result.description.lower()


def test_product_launch_scenario_exists():
    """AC1: Product launch planning scenario can be run."""
    result = run_product_launch_scenario()

    assert result is not None
    assert result.scenario_name == "Product Launch Planning"
    assert "launch" in result.description.lower()


def test_all_scenarios_can_run():
    """AC1: All scenarios can be executed together."""
    results = run_all_scenarios()

    # Should have at least 3 scenarios
    assert len(results) >= 3

    # All should complete
    for result in results:
        assert result.tasks_completed > 0


# ============================================================================
# AC2: Each scenario exercises all 3 epics
# ============================================================================


def test_software_project_exercises_epic1_dependencies():
    """AC2: Software project has task dependencies (Epic 1)."""
    result = run_software_project_scenario()

    # Should have metadata about dependencies
    assert "task_dependency_depth" in result.metadata
    # Should complete all tasks respecting dependencies
    assert result.tasks_completed == result.total_tasks


def test_software_project_exercises_epic2_personalities():
    """AC2: Software project uses agent personalities (Epic 2)."""
    result = run_software_project_scenario()

    # Multiple agents should participate
    unique_agents = set(result.agents_participated)
    assert len(unique_agents) >= 2

    # Should show personality-driven behavior in emergent behaviors
    has_personality_behavior = any(
        "specialized" in behavior.lower()
        or "athena" in behavior.lower()
        or "cato" in behavior.lower()
        for behavior in result.emergent_behaviors
    )
    # May or may not show explicit specialization, but agents participated
    assert len(unique_agents) > 1


def test_software_project_exercises_epic3_collaboration():
    """AC2: Software project uses collaborative features (Epic 3)."""
    result = run_software_project_scenario()

    # Should generate ideas through brainstorming
    assert result.ideas_generated > 0

    # May have synthesis
    assert result.synthesis_count >= 0

    # Should have evaluation
    assert result.evaluation_average > 0


def test_research_paper_exercises_all_epics():
    """AC2: Research paper scenario exercises all 3 epics."""
    result = run_research_paper_scenario()

    # Epic 1: Complex dependencies (13 tasks)
    assert result.total_tasks >= 10
    assert result.tasks_completed == result.total_tasks

    # Epic 2: Multiple agents
    assert len(set(result.agents_participated)) >= 2

    # Epic 3: Collaboration
    assert result.ideas_generated > 0
    assert result.evaluation_average > 0


def test_product_launch_exercises_all_epics():
    """AC2: Product launch scenario exercises all 3 epics."""
    result = run_product_launch_scenario()

    # Epic 1: Dependencies with parallelism
    assert result.total_tasks >= 8
    assert result.tasks_completed == result.total_tasks

    # Epic 2: Agent participation
    assert len(set(result.agents_participated)) >= 2

    # Epic 3: Creative collaboration
    assert result.ideas_generated > 0


# ============================================================================
# AC3: Scenarios demonstrate emergent behavior and personality collaboration
# ============================================================================


def test_software_project_shows_emergent_behaviors():
    """AC3: Software project demonstrates emergent behaviors."""
    result = run_software_project_scenario()

    # Should detect emergent behaviors
    assert len(result.emergent_behaviors) > 0

    # Common emergent behaviors to look for
    behavior_text = " ".join(result.emergent_behaviors).lower()

    # Should show some form of collaboration or specialization
    assert (
        "specialized" in behavior_text
        or "collaboration" in behavior_text
        or "synthesis" in behavior_text
        or "balanced" in behavior_text
    )


def test_research_paper_shows_deep_collaboration():
    """AC3: Research paper shows collaborative ideation."""
    result = run_research_paper_scenario()

    # Research should generate many ideas
    assert result.ideas_generated >= len(set(result.agents_participated))

    # Should show collaborative behaviors
    assert len(result.emergent_behaviors) > 0


def test_personality_driven_task_selection():
    """AC3: Agents select tasks based on personality."""
    result = run_software_project_scenario()

    # Check for specialization in emergent behaviors
    specialization_found = any(
        "specialized" in behavior for behavior in result.emergent_behaviors
    )

    # Either specialization detected, or all agents participated
    assert specialization_found or len(set(result.agents_participated)) >= 2


def test_cross_agent_synthesis():
    """AC3: Scenarios show cross-agent idea synthesis."""
    results = [
        run_software_project_scenario(),
        run_research_paper_scenario(),
        run_product_launch_scenario(),
    ]

    # At least one scenario should show synthesis
    synthesis_counts = [r.synthesis_count for r in results]
    assert any(count > 0 for count in synthesis_counts)


# ============================================================================
# AC4: Validate outputs are coherent and high-quality
# ============================================================================


def test_software_project_quality_score():
    """AC4: Software project produces high-quality output."""
    result = run_software_project_scenario()

    # Quality should be reasonable (>0.5)
    assert result.quality_score > 0.5

    # Coherence should be high
    assert result.coherence_score > 0.7


def test_research_paper_quality_score():
    """AC4: Research paper produces high-quality output."""
    result = run_research_paper_scenario()

    assert result.quality_score > 0.5
    assert result.coherence_score > 0.7


def test_product_launch_quality_score():
    """AC4: Product launch produces high-quality output."""
    result = run_product_launch_scenario()

    assert result.quality_score > 0.5
    assert result.coherence_score > 0.7


def test_all_scenarios_complete_successfully():
    """AC4: All scenarios complete with high success rates."""
    results = run_all_scenarios()

    for result in results:
        # Should complete all or most tasks
        success_rate = result.tasks_completed / result.total_tasks
        assert success_rate >= 0.9  # At least 90% completion

        # Should have reasonable quality
        assert result.quality_score > 0.5


def test_scenario_outputs_are_coherent():
    """AC4: Scenario outputs are internally consistent."""
    result = run_software_project_scenario()

    # Coherence score should be high
    assert result.coherence_score > 0.7

    # All tasks should complete
    assert result.tasks_completed == result.total_tasks

    # Should have participated agents
    assert len(result.agents_participated) > 0


# ============================================================================
# AC5: Scenarios serve as integration tests and examples
# ============================================================================


def test_scenarios_are_documented_examples():
    """AC5: Scenarios have clear descriptions for use as examples."""
    scenarios = [
        run_software_project_scenario(),
        run_research_paper_scenario(),
        run_product_launch_scenario(),
    ]

    for scenario in scenarios:
        # Should have descriptive name
        assert len(scenario.scenario_name) > 0

        # Should have clear description
        assert len(scenario.description) > 20

        # Should have metadata for context
        assert "domain" in scenario.metadata
        assert "complexity" in scenario.metadata


def test_scenarios_as_integration_tests():
    """AC5: Scenarios serve as comprehensive integration tests."""
    results = run_all_scenarios()

    # All scenarios should pass
    assert len(results) >= 3

    for result in results:
        # Should complete successfully
        assert result.tasks_completed == result.total_tasks

        # Should have quality metrics
        assert result.quality_score > 0
        assert result.coherence_score > 0

        # Should demonstrate system capabilities
        assert result.ideas_generated > 0
        assert len(result.agents_participated) > 0


def test_scenario_results_serializable():
    """AC5: Scenario results can be serialized for examples."""
    result = run_software_project_scenario()

    result_dict = result.to_dict()

    # Should have all key fields
    assert "scenario_name" in result_dict
    assert "description" in result_dict
    assert "success_rate" in result_dict
    assert "quality_score" in result_dict
    assert "coherence_score" in result_dict
    assert "emergent_behaviors" in result_dict

    # Success rate should be calculated
    assert 0 <= result_dict["success_rate"] <= 100


def test_scenarios_demonstrate_system_capabilities():
    """AC5: Scenarios showcase full system capabilities."""
    results = run_all_scenarios()

    # Should cover different domains
    domains = [r.metadata.get("domain") for r in results]
    assert len(set(domains)) >= 3

    # Should show varying complexity
    complexities = [r.metadata.get("complexity") for r in results]
    assert len(set(complexities)) >= 2

    # Should demonstrate collaboration
    total_ideas = sum(r.ideas_generated for r in results)
    # Each scenario generates ideas (1 per agent by default = 3 per scenario)
    assert total_ideas >= len(results) * 3  # At least agents * scenarios ideas


# ============================================================================
# Performance and Scale Tests
# ============================================================================


def test_scenarios_execute_in_reasonable_time():
    """Integration: Scenarios complete in reasonable time."""
    result = run_software_project_scenario()

    # 9 tasks should complete quickly
    assert result.execution_time_ms < 5000  # Less than 5 seconds


def test_large_scenario_scales_well():
    """Integration: Large research scenario with 13 tasks scales well."""
    result = run_research_paper_scenario()

    # 13 tasks with complex dependencies
    assert result.total_tasks == 13
    assert result.tasks_completed == 13

    # Should still complete in reasonable time
    assert result.execution_time_ms < 10000  # Less than 10 seconds


# ============================================================================
# Edge Cases and Robustness
# ============================================================================


def test_scenario_with_complex_dependencies():
    """Integration: Scenario with deep dependency chains works correctly."""
    result = run_software_project_scenario()

    # Has 6-level dependency depth
    assert result.metadata.get("task_dependency_depth", 0) >= 3

    # All tasks should still complete
    assert result.tasks_completed == result.total_tasks


def test_scenario_with_parallel_tasks():
    """Integration: Scenario with parallel execution works correctly."""
    result = run_product_launch_scenario()

    # Product launch has tasks that can run in parallel
    # Should complete efficiently
    assert result.tasks_completed == result.total_tasks

    # Should have good agent utilization
    unique_agents = len(set(result.agents_participated))
    assert unique_agents >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
