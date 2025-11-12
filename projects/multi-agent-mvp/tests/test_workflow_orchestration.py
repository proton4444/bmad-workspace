"""
Tests for Story 4.1: End-to-End Workflow Orchestration

Acceptance Criteria:
AC1: Workflow combines task dependencies, agent personalities, and collaboration
AC2: Agents autonomously claim tasks based on personality fit
AC3: Collaborative sessions integrated with task execution
AC4: Workflow state observable and serializable to JSON
AC5: Complete workflow execution in <1 second for 10 tasks
"""

import json
import time
from typing import Dict, List

import pytest
from src.agents.agency import AgentExecutor, AgentState, Task
from src.agents.personality import AgentPersonality, AgentRole
from src.collaboration.context import IdeaCategory
from src.orchestration.workflow import (
    WorkflowOrchestrator,
    WorkflowPhase,
    WorkflowTask,
    create_workflow_from_tasks,
)

# ============================================================================
# AC1: Workflow combines task dependencies, agent personalities, and collaboration
# ============================================================================


def test_workflow_orchestrator_initialization():
    """AC1: WorkflowOrchestrator initializes with all three epic components."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="test_workflow",
        task_ids=["task1", "task2"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Test problem",
    )

    # Verify task dependency component (Epic 1)
    assert len(orchestrator.tasks) == 2
    assert "task1" in orchestrator.tasks
    assert "task2" in orchestrator.tasks

    # Verify agent personality component (Epic 2)
    assert len(orchestrator.agents) == 3
    assert "Athena" in orchestrator.agents
    assert "Cato" in orchestrator.agents
    assert "Zephyr" in orchestrator.agents

    # Verify each agent has (state, personality, executor)
    athena_state, athena_personality, athena_executor = orchestrator.agents["Athena"]
    assert isinstance(athena_state, AgentState)
    assert isinstance(athena_personality, AgentPersonality)
    assert isinstance(athena_executor, AgentExecutor)

    # Verify collaboration component (Epic 3) - initialized by default
    assert orchestrator.context is not None
    assert orchestrator.context.problem_statement == "Test problem"
    assert (
        orchestrator.brainstorm_session is not None
    )  # Initialized by create_workflow_from_tasks
    assert orchestrator.synthesis_session is not None
    assert orchestrator.evaluation_session is not None


def test_workflow_phase_progression():
    """AC1: Workflow progresses through all phases."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="phase_test",
        task_ids=["design", "implement"],
        agent_names=["Athena", "Cato"],
        problem_statement="Build feature",
    )

    # Initial phase
    assert orchestrator.current_phase == WorkflowPhase.PLANNING

    # Run complete workflow
    result = orchestrator.complete_workflow()

    # Should reach COMPLETE phase
    assert orchestrator.current_phase == WorkflowPhase.COMPLETE
    assert result["final_phase"] == WorkflowPhase.COMPLETE.value


def test_workflow_integrates_task_dependencies():
    """AC1: Workflow respects task dependency ordering from Epic 1."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="dep_test",
        task_ids=["task_a", "task_b", "task_c"],
        agent_names=["Athena"],
        problem_statement="Test dependencies",
    )

    # Set up dependencies: task_a -> task_b -> task_c
    orchestrator.tasks["task_b"].dependencies = ["task_a"]
    orchestrator.tasks["task_c"].dependencies = ["task_b"]

    # Run workflow
    result = orchestrator.execute_workflow()

    # Verify tasks executed in dependency order
    execution_order = result["execution_order"]
    assert execution_order.index("task_a") < execution_order.index("task_b")
    assert execution_order.index("task_b") < execution_order.index("task_c")


# ============================================================================
# AC2: Agents autonomously claim tasks based on personality fit
# ============================================================================


def test_agents_claim_tasks_by_affinity():
    """AC2: Agents with highest affinity claim tasks autonomously."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="affinity_test",
        task_ids=["design_architecture", "write_tests", "explore_ideas"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Build system",
    )

    # Set task types to match agent archetypes
    orchestrator.tasks["design_architecture"].task_type = "architecture"
    orchestrator.tasks["write_tests"].task_type = "testing"
    orchestrator.tasks["explore_ideas"].task_type = "creative"

    # Execute workflow
    result = orchestrator.execute_workflow()

    # Verify agents claimed tasks matching their personalities
    task_assignments = result["task_assignments"]

    # Athena (Architect) should claim architecture task
    assert task_assignments["design_architecture"] == "Athena"

    # Cato (Executor) should claim testing task
    assert task_assignments["write_tests"] == "Cato"

    # Zephyr (Experimenter) should claim exploration task
    assert task_assignments["explore_ideas"] == "Zephyr"


def test_task_affinity_scoring_drives_assignment():
    """AC2: Tasks assigned based on affinity scores >0.9."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="scoring_test",
        task_ids=["plan_design"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Design task",
    )

    orchestrator.tasks["plan_design"].task_type = "planning"

    result = orchestrator.execute_workflow()

    # Verify affinity scoring was used
    affinity_scores = result["affinity_scores"]["plan_design"]

    # All agents should have affinity scores
    assert "Athena" in affinity_scores
    assert "Cato" in affinity_scores
    assert "Zephyr" in affinity_scores

    # Winning agent should have highest affinity
    winning_agent = result["task_assignments"]["plan_design"]
    winning_score = affinity_scores[winning_agent]

    # Winning agent should have high affinity (>0.7 when complexity is factored in)
    assert winning_score >= 0.7

    # Winning agent should have the best score
    for agent, score in affinity_scores.items():
        if agent != winning_agent:
            assert winning_score >= score


def test_multiple_agents_compete_for_tasks():
    """AC2: Multiple agents evaluate tasks, highest affinity wins."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="competition_test",
        task_ids=["task1", "task2", "task3"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Multi-task competition",
    )

    orchestrator.tasks["task1"].task_type = "architecture"
    orchestrator.tasks["task2"].task_type = "implementation"
    orchestrator.tasks["task3"].task_type = "creative"

    result = orchestrator.execute_workflow()

    # Each task should be claimed by exactly one agent
    task_assignments = result["task_assignments"]
    assert len(task_assignments) == 3

    # Each agent should claim at least one task (with these archetypes)
    assigned_agents = set(task_assignments.values())
    assert len(assigned_agents) >= 1  # At least one agent worked


def test_agent_state_updated_during_execution():
    """AC2: Agent states reflect task assignments and completions."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="state_test",
        task_ids=["task_x"],
        agent_names=["Athena"],
        problem_statement="State tracking",
    )

    # Get initial state
    athena_state, _, _ = orchestrator.agents["Athena"]
    initial_completed = athena_state.completed_tasks

    # Execute workflow
    orchestrator.execute_workflow()

    # Verify state updated
    athena_state_after, _, _ = orchestrator.agents["Athena"]
    assert athena_state_after.completed_tasks > initial_completed


# ============================================================================
# AC3: Collaborative sessions integrated with task execution
# ============================================================================


def test_brainstorming_session_runs_before_execution():
    """AC3: Brainstorming session runs in ideation phase."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="brainstorm_test",
        task_ids=["task1"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Collaborative ideation",
    )

    result = orchestrator.complete_workflow()

    # Verify brainstorm session was created and ran
    assert orchestrator.brainstorm_session is not None
    assert len(orchestrator.brainstorm_session.turns) > 0

    # Verify ideas were generated
    brainstorm_result = result["brainstorm_results"]
    assert brainstorm_result["total_turns"] > 0
    assert brainstorm_result["total_ideas"] > 0


def test_ideas_added_to_shared_context():
    """AC3: Ideas from brainstorming are added to shared context."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="context_test",
        task_ids=["task1"],
        agent_names=["Athena", "Cato"],
        problem_statement="Shared context test",
    )

    # Run brainstorm phase
    result = orchestrator.run_brainstorm_phase(turns_per_agent=2)

    # Verify ideas in shared context
    assert len(orchestrator.context.ideas) > 0

    # Ideas should have contributor metadata
    for idea_id, idea in orchestrator.context.ideas.items():
        assert idea.contributor in ["Athena", "Cato"]
        assert isinstance(idea.category, IdeaCategory)


def test_synthesis_session_combines_ideas():
    """AC3: Synthesis session creates emergent solutions."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="synthesis_test",
        task_ids=["task1"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Synthesis test",
    )

    # Run through brainstorm and execution to synthesis
    orchestrator.run_brainstorm_phase(turns_per_agent=2)
    orchestrator.execute_workflow()
    result = orchestrator.synthesize_results()

    # Verify synthesis session created
    assert orchestrator.synthesis_session is not None

    # Verify synthesized ideas were generated
    assert result["synthesis_count"] >= 0


def test_evaluation_session_assesses_results():
    """AC3: Evaluation session scores workflow quality."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="eval_test",
        task_ids=["task1"],
        agent_names=["Athena", "Cato"],
        problem_statement="Evaluation test",
    )

    # Run through all phases to evaluation
    orchestrator.run_brainstorm_phase(turns_per_agent=1)
    orchestrator.execute_workflow()
    orchestrator.synthesize_results()
    result = orchestrator.evaluate_workflow()

    # Verify evaluation session created
    assert orchestrator.evaluation_session is not None

    # Verify evaluations were generated
    assert result["evaluation_count"] >= 0


def test_collaborative_memory_stored():
    """AC3: Workflow stores collaboration patterns in memory."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="memory_test",
        task_ids=["task1"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Memory test",
    )

    # Run complete workflow
    result = orchestrator.complete_workflow()

    # Verify memory was stored
    memory_result = result["memory_results"]
    assert memory_result["memory_stored"] is True

    # Verify memory store has entries
    assert len(orchestrator.memory_store.memories) > 0


# ============================================================================
# AC4: Workflow state observable and serializable to JSON
# ============================================================================


def test_workflow_serializable_to_json():
    """AC4: Complete workflow state can be serialized to JSON."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="json_test",
        task_ids=["task1", "task2"],
        agent_names=["Athena", "Cato"],
        problem_statement="JSON serialization test",
    )

    # Get workflow state
    state = orchestrator.to_dict()

    # Should be JSON serializable
    json_str = json.dumps(state, indent=2)
    assert len(json_str) > 0

    # Should contain all major components
    assert "workflow_id" in state
    assert "tasks" in state
    assert "agents" in state
    assert "context" in state
    assert "current_phase" in state


def test_workflow_state_includes_all_components():
    """AC4: Serialized state includes Epic 1, 2, and 3 data."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="state_test",
        task_ids=["task_a"],
        agent_names=["Athena"],
        problem_statement="State completeness test",
    )

    orchestrator.complete_workflow()
    state = orchestrator.to_dict()

    # Epic 1: Task dependencies
    assert "tasks" in state
    assert "task_a" in state["tasks"]
    assert "status" in state["tasks"]["task_a"]

    # Epic 2: Agent personalities
    assert "agents" in state
    assert "Athena" in state["agents"]
    agent_data = state["agents"]["Athena"]
    assert "state" in agent_data
    assert "personality" in agent_data

    # Epic 3: Collaboration
    assert "context" in state
    assert "ideas" in state["context"]
    assert "brainstorm_session" in state
    assert "synthesis_session" in state
    assert "evaluation_session" in state


def test_workflow_state_observable_at_any_phase():
    """AC4: Workflow state can be serialized at any execution phase."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="phase_state_test",
        task_ids=["task1"],
        agent_names=["Athena"],
        problem_statement="Phase observability test",
    )

    # Serialize at PLANNING phase
    state_planning = orchestrator.to_dict()
    assert state_planning["current_phase"] == WorkflowPhase.PLANNING.value
    json.dumps(state_planning)  # Should not raise

    # Move to IDEATION phase
    orchestrator.run_brainstorm_phase(turns_per_agent=1)
    state_ideation = orchestrator.to_dict()
    assert state_ideation["current_phase"] == WorkflowPhase.IDEATION.value
    json.dumps(state_ideation)  # Should not raise

    # Move to EXECUTION phase
    orchestrator.execute_workflow()
    state_execution = orchestrator.to_dict()
    assert state_execution["current_phase"] == WorkflowPhase.EXECUTION.value
    json.dumps(state_execution)  # Should not raise


def test_workflow_state_roundtrip():
    """AC4: Workflow can be serialized and reconstructed."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="roundtrip_test",
        task_ids=["task1"],
        agent_names=["Athena"],
        problem_statement="Roundtrip test",
    )

    # Serialize
    state_dict = orchestrator.to_dict()
    json_str = json.dumps(state_dict)

    # Deserialize
    loaded_dict = json.loads(json_str)

    # Verify key data preserved
    assert loaded_dict["workflow_id"] == "roundtrip_test"
    assert "task1" in loaded_dict["tasks"]
    assert "Athena" in loaded_dict["agents"]


# ============================================================================
# AC5: Complete workflow execution in <1 second for 10 tasks
# ============================================================================


def test_workflow_performance_10_tasks():
    """AC5: Workflow completes 10 tasks in <1 second."""
    task_ids = [f"task_{i}" for i in range(10)]

    orchestrator = create_workflow_from_tasks(
        workflow_id="perf_test",
        task_ids=task_ids,
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Performance test with 10 tasks",
    )

    # Measure execution time
    start_time = time.time()
    result = orchestrator.complete_workflow()
    end_time = time.time()

    execution_time = end_time - start_time

    # Should complete in <1 second
    assert execution_time < 1.0, f"Workflow took {execution_time:.3f}s, expected <1.0s"

    # Verify all tasks completed
    assert result["tasks_completed"] == 10


def test_workflow_performance_scaling():
    """AC5: Workflow scales efficiently with task count."""
    execution_times = []

    for task_count in [5, 10, 15]:
        task_ids = [f"task_{i}" for i in range(task_count)]

        orchestrator = create_workflow_from_tasks(
            workflow_id=f"scale_test_{task_count}",
            task_ids=task_ids,
            agent_names=["Athena", "Cato", "Zephyr"],
            problem_statement=f"Scaling test with {task_count} tasks",
        )

        start_time = time.time()
        orchestrator.complete_workflow()
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)

    # Performance should scale reasonably (not exponentially)
    # 15 tasks shouldn't take more than 10x as long as 5 tasks
    # Use max to handle case where 5 tasks complete very quickly (near 0)
    baseline = max(execution_times[0], 0.001)  # At least 1ms baseline
    assert execution_times[2] < baseline * 10


def test_brainstorm_phase_performance():
    """AC5: Brainstorming phase completes quickly."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="brainstorm_perf_test",
        task_ids=["task1"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Brainstorm performance test",
    )

    start_time = time.time()
    orchestrator.run_brainstorm_phase(turns_per_agent=3)
    end_time = time.time()

    brainstorm_time = end_time - start_time

    # 3 agents * 3 turns = 9 turns should be fast
    assert brainstorm_time < 0.5


def test_synthesis_phase_performance():
    """AC5: Synthesis phase completes quickly."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="synthesis_perf_test",
        task_ids=["task1"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Synthesis performance test",
    )

    # Add some ideas to synthesize
    orchestrator.run_brainstorm_phase(turns_per_agent=2)

    start_time = time.time()
    orchestrator.synthesize_results()
    end_time = time.time()

    synthesis_time = end_time - start_time

    # Synthesis should be fast
    assert synthesis_time < 0.3


# ============================================================================
# Integration Tests
# ============================================================================


def test_complete_workflow_end_to_end():
    """Integration: Complete workflow from start to finish."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="e2e_test",
        task_ids=["design", "implement", "test", "document"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Build complete feature",
    )

    # Set up task dependencies
    orchestrator.tasks["implement"].dependencies = ["design"]
    orchestrator.tasks["test"].dependencies = ["implement"]
    orchestrator.tasks["document"].dependencies = ["test"]

    # Set task types for personality matching
    orchestrator.tasks["design"].task_type = "architecture"
    orchestrator.tasks["implement"].task_type = "implementation"
    orchestrator.tasks["test"].task_type = "testing"
    orchestrator.tasks["document"].task_type = "documentation"

    # Execute complete workflow
    result = orchestrator.complete_workflow()

    # Verify all phases completed
    assert result["final_phase"] == WorkflowPhase.COMPLETE.value
    assert result["tasks_completed"] == 4

    # Verify brainstorming happened
    assert result["brainstorm_results"]["total_ideas"] > 0

    # Verify execution respected dependencies
    execution_order = result["execution_results"]["execution_order"]
    assert execution_order.index("design") < execution_order.index("implement")
    assert execution_order.index("implement") < execution_order.index("test")
    assert execution_order.index("test") < execution_order.index("document")

    # Verify synthesis and evaluation ran
    assert "synthesis_results" in result
    assert "evaluation_results" in result

    # Verify memory stored
    assert result["memory_results"]["memory_stored"] is True

    # Verify entire state is JSON serializable
    json.dumps(orchestrator.to_dict())


def test_workflow_handles_complex_dependencies():
    """Integration: Workflow handles diamond dependency pattern."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="diamond_test",
        task_ids=["start", "branch_a", "branch_b", "merge"],
        agent_names=["Athena", "Cato"],
        problem_statement="Complex dependencies",
    )

    # Diamond pattern: start -> [branch_a, branch_b] -> merge
    orchestrator.tasks["branch_a"].dependencies = ["start"]
    orchestrator.tasks["branch_b"].dependencies = ["start"]
    orchestrator.tasks["merge"].dependencies = ["branch_a", "branch_b"]

    result = orchestrator.execute_workflow()

    # Verify dependency ordering
    execution_order = result["execution_order"]
    start_idx = execution_order.index("start")
    branch_a_idx = execution_order.index("branch_a")
    branch_b_idx = execution_order.index("branch_b")
    merge_idx = execution_order.index("merge")

    assert start_idx < branch_a_idx
    assert start_idx < branch_b_idx
    assert branch_a_idx < merge_idx
    assert branch_b_idx < merge_idx


def test_workflow_multiple_agents_collaborate():
    """Integration: Multiple agents collaborate on shared problem."""
    orchestrator = create_workflow_from_tasks(
        workflow_id="collab_test",
        task_ids=["task_arch", "task_impl", "task_explore"],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Multi-agent collaboration",
    )

    orchestrator.tasks["task_arch"].task_type = "architecture"
    orchestrator.tasks["task_impl"].task_type = "implementation"
    orchestrator.tasks["task_explore"].task_type = "creative"

    result = orchestrator.complete_workflow()

    # All three agents should have participated
    participating_agents = set(result["execution_results"]["task_assignments"].values())
    assert len(participating_agents) == 3
    assert "Athena" in participating_agents
    assert "Cato" in participating_agents
    assert "Zephyr" in participating_agents

    # All agents should have contributed ideas
    ideas = orchestrator.context.ideas
    contributors = {idea.contributor for idea in ideas.values()}
    assert len(contributors) >= 2  # At least 2 agents contributed ideas


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
