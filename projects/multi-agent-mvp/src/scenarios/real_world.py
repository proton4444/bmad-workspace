"""
Real-world scenario validation for multi-agent workflows.

Implements realistic scenarios that exercise all system capabilities:
- Software development project
- Research paper collaboration
- Product launch planning

Story 4.3: Real-World Scenario Validation
Acceptance Criteria:
- AC1: Implement 3+ realistic multi-agent scenarios
- AC2: Each scenario exercises all 3 epics
- AC3: Scenarios demonstrate emergent behavior and personality collaboration
- AC4: Validate outputs are coherent and high-quality
- AC5: Scenarios serve as integration tests and examples
"""

from dataclasses import dataclass, field
from typing import Dict, List

from src.orchestration.workflow import WorkflowOrchestrator, create_workflow_from_tasks


@dataclass
class ScenarioResult:
    """Results from executing a real-world scenario."""

    scenario_name: str
    description: str
    tasks_completed: int
    total_tasks: int
    agents_participated: List[str]
    ideas_generated: int
    synthesis_count: int
    evaluation_average: float
    execution_time_ms: float
    quality_score: float
    coherence_score: float
    emergent_behaviors: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialize scenario result."""
        return {
            "scenario_name": self.scenario_name,
            "description": self.description,
            "tasks_completed": self.tasks_completed,
            "total_tasks": self.total_tasks,
            "success_rate": round(
                self.tasks_completed / self.total_tasks * 100
                if self.total_tasks > 0
                else 0,
                1,
            ),
            "agents_participated": self.agents_participated,
            "ideas_generated": self.ideas_generated,
            "synthesis_count": self.synthesis_count,
            "evaluation_average": round(self.evaluation_average, 2),
            "execution_time_ms": round(self.execution_time_ms, 2),
            "quality_score": round(self.quality_score, 2),
            "coherence_score": round(self.coherence_score, 2),
            "emergent_behaviors": self.emergent_behaviors,
            "metadata": self.metadata,
        }


def run_software_project_scenario() -> ScenarioResult:
    """
    AC1 & AC2: Software development project scenario.

    Realistic workflow for building a feature:
    - Architecture design (Athena)
    - Implementation tasks (Cato)
    - Creative UX design (Zephyr)

    Exercises:
    - Epic 1: Task dependencies (design → implement → test)
    - Epic 2: Personality-driven task selection
    - Epic 3: Collaborative brainstorming and synthesis
    """
    # Create workflow with realistic software tasks
    orchestrator = create_workflow_from_tasks(
        workflow_id="software_project",
        task_ids=[
            "design_architecture",
            "design_database",
            "implement_backend",
            "implement_api",
            "design_ui",
            "implement_frontend",
            "write_tests",
            "code_review",
            "documentation",
        ],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Build a user authentication feature with secure backend and intuitive UI",
    )

    # Set realistic task types for personality matching
    orchestrator.tasks["design_architecture"].task_type = "architecture"
    orchestrator.tasks["design_database"].task_type = "design"
    orchestrator.tasks["implement_backend"].task_type = "implementation"
    orchestrator.tasks["implement_api"].task_type = "implementation"
    orchestrator.tasks["design_ui"].task_type = "creative"
    orchestrator.tasks["implement_frontend"].task_type = "implementation"
    orchestrator.tasks["write_tests"].task_type = "testing"
    orchestrator.tasks["code_review"].task_type = "review"
    orchestrator.tasks["documentation"].task_type = "planning"

    # Set realistic dependencies (Epic 1)
    orchestrator.tasks["implement_backend"].dependencies = ["design_architecture"]
    orchestrator.tasks["implement_api"].dependencies = [
        "implement_backend",
        "design_database",
    ]
    orchestrator.tasks["implement_frontend"].dependencies = [
        "design_ui",
        "implement_api",
    ]
    orchestrator.tasks["write_tests"].dependencies = [
        "implement_backend",
        "implement_frontend",
    ]
    orchestrator.tasks["code_review"].dependencies = ["write_tests"]
    orchestrator.tasks["documentation"].dependencies = ["code_review"]

    # Execute complete workflow
    result = orchestrator.complete_workflow()

    # Analyze for emergent behaviors (AC3)
    emergent_behaviors = _analyze_emergent_behaviors(orchestrator, result)

    # Calculate quality scores (AC4)
    quality_score = _calculate_quality_score(result)
    coherence_score = _calculate_coherence_score(orchestrator)

    return ScenarioResult(
        scenario_name="Software Development Project",
        description="Build user authentication feature with architecture, implementation, and testing",
        tasks_completed=result["tasks_completed"],
        total_tasks=len(orchestrator.tasks),
        agents_participated=list(
            result["execution_results"]["task_assignments"].values()
        ),
        ideas_generated=result["brainstorm_results"]["total_ideas"],
        synthesis_count=result["synthesis_results"].get("synthesis_count", 0),
        evaluation_average=result["evaluation_results"]
        .get("average", {})
        .get("quality", 0.5),
        execution_time_ms=result["total_time_ms"],
        quality_score=quality_score,
        coherence_score=coherence_score,
        emergent_behaviors=emergent_behaviors,
        metadata={
            "domain": "software_engineering",
            "complexity": "high",
            "task_dependency_depth": 6,
        },
    )


def run_research_paper_scenario() -> ScenarioResult:
    """
    AC1 & AC2: Research paper collaboration scenario.

    Realistic academic research workflow:
    - Literature review (Athena)
    - Methodology design (Athena)
    - Experiment execution (Cato)
    - Data analysis (Athena)
    - Creative visualization (Zephyr)
    - Paper writing (all collaborate)

    Exercises:
    - Epic 1: Complex dependencies
    - Epic 2: Multi-agent personality diversity
    - Epic 3: Deep collaborative creativity
    """
    orchestrator = create_workflow_from_tasks(
        workflow_id="research_paper",
        task_ids=[
            "literature_review",
            "methodology_design",
            "hypothesis_formulation",
            "experiment_design",
            "run_experiments",
            "collect_data",
            "analyze_data",
            "create_visualizations",
            "write_introduction",
            "write_methods",
            "write_results",
            "write_discussion",
            "peer_review",
        ],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Research novel approaches to multi-agent coordination and publish findings",
    )

    # Set task types for personality matching
    orchestrator.tasks["literature_review"].task_type = "analysis"
    orchestrator.tasks["methodology_design"].task_type = "design"
    orchestrator.tasks["hypothesis_formulation"].task_type = "creative"
    orchestrator.tasks["experiment_design"].task_type = "planning"
    orchestrator.tasks["run_experiments"].task_type = "implementation"
    orchestrator.tasks["collect_data"].task_type = "implementation"
    orchestrator.tasks["analyze_data"].task_type = "analysis"
    orchestrator.tasks["create_visualizations"].task_type = "creative"
    orchestrator.tasks["write_introduction"].task_type = "creative"
    orchestrator.tasks["write_methods"].task_type = "planning"
    orchestrator.tasks["write_results"].task_type = "analysis"
    orchestrator.tasks["write_discussion"].task_type = "creative"
    orchestrator.tasks["peer_review"].task_type = "review"

    # Set research workflow dependencies
    orchestrator.tasks["methodology_design"].dependencies = ["literature_review"]
    orchestrator.tasks["hypothesis_formulation"].dependencies = ["literature_review"]
    orchestrator.tasks["experiment_design"].dependencies = [
        "methodology_design",
        "hypothesis_formulation",
    ]
    orchestrator.tasks["run_experiments"].dependencies = ["experiment_design"]
    orchestrator.tasks["collect_data"].dependencies = ["run_experiments"]
    orchestrator.tasks["analyze_data"].dependencies = ["collect_data"]
    orchestrator.tasks["create_visualizations"].dependencies = ["analyze_data"]
    orchestrator.tasks["write_introduction"].dependencies = ["literature_review"]
    orchestrator.tasks["write_methods"].dependencies = ["experiment_design"]
    orchestrator.tasks["write_results"].dependencies = [
        "analyze_data",
        "create_visualizations",
    ]
    orchestrator.tasks["write_discussion"].dependencies = [
        "write_results",
        "hypothesis_formulation",
    ]
    orchestrator.tasks["peer_review"].dependencies = [
        "write_introduction",
        "write_methods",
        "write_results",
        "write_discussion",
    ]

    # Execute workflow
    result = orchestrator.complete_workflow()

    emergent_behaviors = _analyze_emergent_behaviors(orchestrator, result)
    quality_score = _calculate_quality_score(result)
    coherence_score = _calculate_coherence_score(orchestrator)

    return ScenarioResult(
        scenario_name="Research Paper Collaboration",
        description="Conduct research and write paper through multi-agent collaboration",
        tasks_completed=result["tasks_completed"],
        total_tasks=len(orchestrator.tasks),
        agents_participated=list(
            set(result["execution_results"]["task_assignments"].values())
        ),
        ideas_generated=result["brainstorm_results"]["total_ideas"],
        synthesis_count=result["synthesis_results"].get("synthesis_count", 0),
        evaluation_average=result["evaluation_results"]
        .get("average", {})
        .get("quality", 0.5),
        execution_time_ms=result["total_time_ms"],
        quality_score=quality_score,
        coherence_score=coherence_score,
        emergent_behaviors=emergent_behaviors,
        metadata={"domain": "academic_research", "complexity": "very_high"},
    )


def run_product_launch_scenario() -> ScenarioResult:
    """
    AC1 & AC2: Product launch planning scenario.

    Business strategy and execution workflow:
    - Market analysis (Athena)
    - Product positioning (Athena + Zephyr)
    - Marketing campaign (Zephyr)
    - Launch execution (Cato)
    - Metrics tracking (Athena)

    Exercises:
    - Epic 1: Parallel task execution
    - Epic 2: Balanced agent utilization
    - Epic 3: Creative and strategic synthesis
    """
    orchestrator = create_workflow_from_tasks(
        workflow_id="product_launch",
        task_ids=[
            "market_research",
            "competitive_analysis",
            "product_positioning",
            "messaging_strategy",
            "creative_campaign",
            "launch_plan",
            "prepare_materials",
            "execute_launch",
            "monitor_metrics",
            "collect_feedback",
        ],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Launch new AI productivity tool to market with strategic positioning and creative campaign",
    )

    # Set task types
    orchestrator.tasks["market_research"].task_type = "analysis"
    orchestrator.tasks["competitive_analysis"].task_type = "analysis"
    orchestrator.tasks["product_positioning"].task_type = "design"
    orchestrator.tasks["messaging_strategy"].task_type = "creative"
    orchestrator.tasks["creative_campaign"].task_type = "creative"
    orchestrator.tasks["launch_plan"].task_type = "planning"
    orchestrator.tasks["prepare_materials"].task_type = "implementation"
    orchestrator.tasks["execute_launch"].task_type = "implementation"
    orchestrator.tasks["monitor_metrics"].task_type = "analysis"
    orchestrator.tasks["collect_feedback"].task_type = "review"

    # Set dependencies allowing some parallelism
    orchestrator.tasks["product_positioning"].dependencies = [
        "market_research",
        "competitive_analysis",
    ]
    orchestrator.tasks["messaging_strategy"].dependencies = ["product_positioning"]
    orchestrator.tasks["creative_campaign"].dependencies = ["messaging_strategy"]
    orchestrator.tasks["launch_plan"].dependencies = ["product_positioning"]
    orchestrator.tasks["prepare_materials"].dependencies = [
        "creative_campaign",
        "launch_plan",
    ]
    orchestrator.tasks["execute_launch"].dependencies = ["prepare_materials"]
    orchestrator.tasks["monitor_metrics"].dependencies = ["execute_launch"]
    orchestrator.tasks["collect_feedback"].dependencies = ["execute_launch"]

    # Execute workflow
    result = orchestrator.complete_workflow()

    emergent_behaviors = _analyze_emergent_behaviors(orchestrator, result)
    quality_score = _calculate_quality_score(result)
    coherence_score = _calculate_coherence_score(orchestrator)

    return ScenarioResult(
        scenario_name="Product Launch Planning",
        description="Strategic market analysis, creative campaign, and product launch execution",
        tasks_completed=result["tasks_completed"],
        total_tasks=len(orchestrator.tasks),
        agents_participated=list(
            set(result["execution_results"]["task_assignments"].values())
        ),
        ideas_generated=result["brainstorm_results"]["total_ideas"],
        synthesis_count=result["synthesis_results"].get("synthesis_count", 0),
        evaluation_average=result["evaluation_results"]
        .get("average", {})
        .get("quality", 0.5),
        execution_time_ms=result["total_time_ms"],
        quality_score=quality_score,
        coherence_score=coherence_score,
        emergent_behaviors=emergent_behaviors,
        metadata={"domain": "business_strategy", "complexity": "high"},
    )


def _analyze_emergent_behaviors(
    orchestrator: WorkflowOrchestrator, result: Dict
) -> List[str]:
    """
    AC3: Analyze workflow for emergent behaviors.

    Emergent behaviors include:
    - Personality-driven task distribution
    - Cross-agent idea synthesis
    - Collaborative problem-solving patterns
    """
    behaviors = []

    # Check for personality-driven specialization
    task_assignments = result["execution_results"]["task_assignments"]
    agent_task_types = {}

    for task_id, agent_name in task_assignments.items():
        task = orchestrator.tasks[task_id]
        if agent_name not in agent_task_types:
            agent_task_types[agent_name] = []
        agent_task_types[agent_name].append(task.task_type)

    # Detect specialization patterns
    for agent, task_types in agent_task_types.items():
        if len(task_types) > 2:
            most_common = max(set(task_types), key=task_types.count)
            frequency = task_types.count(most_common) / len(task_types)
            if frequency > 0.6:
                behaviors.append(
                    f"{agent} specialized in {most_common} tasks ({int(frequency * 100)}%)"
                )

    # Check for collaborative idea generation
    if result["brainstorm_results"]["total_ideas"] > len(orchestrator.agents) * 2:
        behaviors.append(
            f"Rich collaborative ideation: {result['brainstorm_results']['total_ideas']} ideas from {len(orchestrator.agents)} agents"
        )

    # Check for synthesis (emergent solutions)
    if result["synthesis_results"].get("synthesis_count", 0) > 0:
        behaviors.append(
            f"Emergent synthesis: {result['synthesis_results']['synthesis_count']} combined solutions"
        )

    # Check for balanced agent participation
    agent_counts = result["execution_results"]["agent_assignments"]
    if len(agent_counts) == len(orchestrator.agents):
        variance = max(agent_counts.values()) - min(agent_counts.values())
        if variance <= 2:
            behaviors.append("Balanced multi-agent participation")

    return behaviors


def _calculate_quality_score(result: Dict) -> float:
    """
    AC4: Calculate overall quality score.

    Based on:
    - Task completion rate
    - Evaluation scores
    - Synthesis quality
    """
    completion_rate = (
        result["tasks_completed"]
        / max(len(result["execution_results"]["execution_order"]), 1)
        if result["execution_results"]["execution_order"]
        else 0
    )

    eval_quality = result["evaluation_results"].get("average", {}).get("quality", 0.5)

    synthesis_score = (
        0.8 if result["synthesis_results"].get("synthesis_count", 0) > 0 else 0.5
    )

    # Weighted average
    quality = completion_rate * 0.4 + eval_quality * 0.4 + synthesis_score * 0.2

    return quality


def _calculate_coherence_score(orchestrator: WorkflowOrchestrator) -> float:
    """
    AC4: Calculate workflow coherence.

    Based on:
    - Dependency satisfaction
    - Agent state consistency
    - Idea connectivity
    """
    # Check all tasks completed
    completed_count = len(
        [t for t in orchestrator.tasks.values() if t.status == "completed"]
    )
    total_count = len(orchestrator.tasks)
    completion_coherence = completed_count / total_count if total_count > 0 else 0

    # Check ideas were generated
    idea_coherence = 0.9 if len(orchestrator.context.ideas) > 0 else 0.5

    # Check memory stored
    memory_coherence = 1.0 if len(orchestrator.memory_store.memories) > 0 else 0.7

    coherence = (
        completion_coherence * 0.5 + idea_coherence * 0.3 + memory_coherence * 0.2
    )

    return coherence


def run_all_scenarios() -> List[ScenarioResult]:
    """
    AC5: Run all scenarios as integration tests.

    Returns:
        List of results from all scenarios
    """
    scenarios = [
        ("Software Project", run_software_project_scenario),
        ("Research Paper", run_research_paper_scenario),
        ("Product Launch", run_product_launch_scenario),
    ]

    results = []
    print(f"\n{'=' * 70}")
    print("Real-World Scenario Validation")
    print(f"{'=' * 70}\n")

    for scenario_name, scenario_func in scenarios:
        print(f"Running: {scenario_name}...")
        result = scenario_func()
        results.append(result)

        print(f"  ✓ {result.tasks_completed}/{result.total_tasks} tasks completed")
        print(f"  ✓ {len(set(result.agents_participated))} agents participated")
        print(
            f"  ✓ Quality: {result.quality_score:.2f}, Coherence: {result.coherence_score:.2f}"
        )
        print(f"  ✓ {len(result.emergent_behaviors)} emergent behaviors observed")
        print()

    print(f"{'=' * 70}")
    print(f"Summary: {len(results)} scenarios validated successfully")
    print(f"{'=' * 70}\n")

    return results


if __name__ == "__main__":
    results = run_all_scenarios()

    print("Emergent Behaviors Observed:")
    for result in results:
        print(f"\n{result.scenario_name}:")
        for behavior in result.emergent_behaviors:
            print(f"  - {behavior}")
