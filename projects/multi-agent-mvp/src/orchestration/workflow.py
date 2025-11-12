"""
End-to-end workflow orchestration integrating all system components.

Combines task dependency engine, agent personalities, and collaborative
creativity into complete workflows that solve real problems.

Story 4.1: End-to-End Workflow Orchestration
Acceptance Criteria:
- AC1: Workflow combines all 3 epics (dependencies, agents, collaboration)
- AC2: Agents autonomously claim tasks based on personality
- AC3: Collaborative sessions integrated with task execution
- AC4: Workflow state observable and serializable to JSON
- AC5: Complete workflow execution in <1 second for 10 tasks
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from src.agents.agency import AgentExecutor, Task

# Epic 2: Agent personalities & agency
from src.agents.personality import (
    ARCHITECT_PERSONALITY,
    EXECUTOR_PERSONALITY,
    EXPERIMENTER_PERSONALITY,
    AgentPersonality,
)
from src.agents.state import create_agent_state
from src.collaboration.brainstorming import BrainstormSession

# Epic 3: Collaboration
from src.collaboration.context import IdeaCategory, SharedContext
from src.collaboration.evaluation import EvaluationSession
from src.collaboration.memory import CollaborativeMemoryStore
from src.collaboration.synthesis import SynthesisSession

# Epic 1: Task dependency
from src.core.ready_tasks import get_ready_tasks, update_task_state
from src.core.topological_sort import topological_sort


class WorkflowPhase(Enum):
    """Phases of workflow execution."""

    PLANNING = "planning"  # Define tasks and dependencies
    IDEATION = "ideation"  # Collaborative brainstorming
    EXECUTION = "execution"  # Task execution by agents
    SYNTHESIS = "synthesis"  # Combine results
    EVALUATION = "evaluation"  # Assess outcomes
    COMPLETE = "complete"  # Workflow finished


@dataclass
class WorkflowTask:
    """Task in workflow with dependency info."""

    id: str
    name: str
    description: str
    task_type: str  # architecture, implementation, creative, etc.
    complexity: str  # simple, moderate, complex, difficult
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, ready, in_progress, completed, failed
    assigned_agent: Optional[str] = None
    result: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        """Serialize task."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "complexity": self.complexity,
            "dependencies": self.dependencies,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "result": self.result,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }


@dataclass
class WorkflowOrchestrator:
    """
    Orchestrates complete workflow integrating all epics.

    AC1: Combines task dependencies, agent personalities, and collaboration.
    """

    workflow_id: str = field(
        default_factory=lambda: str(__import__("uuid").uuid4())[:8]
    )
    name: str = ""
    description: str = ""
    tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
    agents: Dict[str, Tuple] = field(
        default_factory=dict
    )  # name -> (state, personality, executor)
    context: SharedContext = field(default_factory=SharedContext)
    brainstorm_session: Optional[BrainstormSession] = None
    synthesis_session: Optional[SynthesisSession] = None
    evaluation_session: Optional[EvaluationSession] = None
    memory_store: CollaborativeMemoryStore = field(
        default_factory=CollaborativeMemoryStore
    )
    current_phase: WorkflowPhase = WorkflowPhase.PLANNING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    metrics: Dict = field(default_factory=dict)

    def add_task(
        self,
        task_id: str,
        name: str,
        description: str,
        task_type: str,
        complexity: str = "moderate",
        dependencies: Optional[List[str]] = None,
    ) -> WorkflowTask:
        """Add task to workflow."""
        task = WorkflowTask(
            id=task_id,
            name=name,
            description=description,
            task_type=task_type,
            complexity=complexity,
            dependencies=dependencies or [],
        )
        self.tasks[task_id] = task
        return task

    def add_agent(self, personality: AgentPersonality) -> str:
        """AC2: Add agent with personality to workflow."""
        agent_state = create_agent_state(personality)
        executor = AgentExecutor(agent_state, personality)
        self.agents[personality.name] = (agent_state, personality, executor)
        return personality.name

    def initialize_collaboration(self, topic: str, problem_statement: str):
        """Initialize collaborative sessions."""
        self.context = SharedContext(topic=topic, problem_statement=problem_statement)
        self.brainstorm_session = BrainstormSession(context=self.context)
        self.brainstorm_session.add_agents(list(self.agents.keys()))
        self.synthesis_session = SynthesisSession(context=self.context)
        self.evaluation_session = EvaluationSession(context=self.context)

    def run_brainstorm_phase(self, turns_per_agent: int = 2) -> Dict:
        """AC3: Run collaborative brainstorming before task execution."""
        if not self.brainstorm_session:
            return {}

        self.current_phase = WorkflowPhase.IDEATION
        brainstorm_results = {
            "ideas_generated": 0,
            "total_ideas": 0,
            "total_turns": 0,
            "participants": list(self.agents.keys()),
            "turns": [],
        }

        # Each agent contributes ideas about the workflow
        for _ in range(turns_per_agent):
            for agent_name in self.agents.keys():
                # Agent contributes idea based on personality
                _, personality, _ = self.agents[agent_name]

                # Generate idea content based on personality
                if "Architect" in personality.name or "Athena" in personality.name:
                    idea_content = f"Systematic approach to {self.name}"
                    category = IdeaCategory.APPROACH
                elif "Executor" in personality.name or "Cato" in personality.name:
                    idea_content = f"Practical implementation for {self.name}"
                    category = IdeaCategory.DETAIL
                else:
                    idea_content = f"Creative solution for {self.name}"
                    category = IdeaCategory.INSIGHT

                turn, idea = self.brainstorm_session.add_turn(
                    agent_name=agent_name,
                    idea_content=idea_content,
                    category=category,
                )
                brainstorm_results["ideas_generated"] += 1
                brainstorm_results["total_ideas"] += 1
                brainstorm_results["turns"].append(turn.turn_number)

        brainstorm_results["total_turns"] = len(brainstorm_results["turns"])
        return brainstorm_results

    def execute_workflow(self) -> Dict:
        """
        AC1 & AC5: Execute complete workflow integrating all components.

        Returns:
            Workflow execution results
        """
        start_time = datetime.now()
        self.current_phase = WorkflowPhase.EXECUTION

        execution_results = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "task_assignments": {},
            "agent_assignments": {},
            "affinity_scores": {},
            "execution_order": [],
        }

        # Convert WorkflowTasks to dependency graph format for topological sort
        task_graph = {
            task_id: task.dependencies for task_id, task in self.tasks.items()
        }

        # Use topological sort to get execution order
        sorted_tasks = topological_sort(task_graph)

        # Track task status for ready_tasks
        task_queue = {
            task_id: {
                "id": task.id,
                "dependencies": task.dependencies,
                "status": task.status,
            }
            for task_id, task in self.tasks.items()
        }

        # Execute tasks in dependency order
        for task_id in sorted_tasks:
            task = self.tasks[task_id]

            # Skip if already completed
            if task.status == "completed":
                continue

            # Convert to Task for agent execution
            agent_task = Task(
                id=task.id,
                name=task.name,
                task_type=task.task_type,
                complexity=task.complexity,
                description=task.description,
                is_ready=True,
            )

            # Find best agent for task (AC2: based on personality)
            best_agent = None
            best_affinity = 0.0
            task_affinity_scores = {}

            for agent_name, (state, personality, executor) in self.agents.items():
                affinity = executor.score_task_affinity(agent_task)
                task_affinity_scores[agent_name] = affinity
                if affinity > best_affinity:
                    best_affinity = affinity
                    best_agent = agent_name

            # Store affinity scores
            execution_results["affinity_scores"][task_id] = task_affinity_scores

            # Assign and execute
            if best_agent:
                _, _, executor = self.agents[best_agent]
                task_start = datetime.now()

                if executor.execute_task(agent_task):
                    task_end = datetime.now()
                    task.status = "completed"
                    task.assigned_agent = best_agent
                    task.execution_time_ms = (
                        task_end - task_start
                    ).total_seconds() * 1000
                    task.result = f"Completed by {best_agent}"

                    execution_results["tasks_completed"] += 1
                    execution_results["execution_order"].append(task_id)
                    execution_results["task_assignments"][task_id] = best_agent

                    if best_agent not in execution_results["agent_assignments"]:
                        execution_results["agent_assignments"][best_agent] = 0
                    execution_results["agent_assignments"][best_agent] += 1

                    # Update task queue
                    task_queue = update_task_state(task_queue, task_id, "completed")
                else:
                    task.status = "failed"
                    execution_results["tasks_failed"] += 1

        end_time = datetime.now()
        execution_results["total_time_ms"] = (
            end_time - start_time
        ).total_seconds() * 1000

        return execution_results

    def synthesize_results(self) -> Dict:
        """AC3: Synthesize results from executed tasks."""
        if not self.synthesis_session:
            return {"synthesis_count": 0}

        self.current_phase = WorkflowPhase.SYNTHESIS

        # Get completed task results as ideas
        completed_tasks = [t for t in self.tasks.values() if t.status == "completed"]

        if len(completed_tasks) >= 2:
            # Add task results as ideas to context
            for task in completed_tasks:
                if task.assigned_agent:
                    self.context.add_idea(
                        content=f"{task.name}: {task.result}",
                        contributor=task.assigned_agent,
                        category=IdeaCategory.SYNTHESIS,
                    )

            # Synthesize
            idea_ids = list(self.context.ideas.keys())
            if len(idea_ids) >= 2:
                synthesis = self.synthesis_session.synthesize_ideas(
                    source_idea_ids=idea_ids[:2],  # Synthesize first 2
                    synthesis_content=f"Integrated solution for {self.name}",
                    emergent_properties=[
                        "Cross-agent collaboration",
                        "Personality diversity",
                    ],
                    coherence=0.85,
                    novelty=0.75,
                )
                return {
                    "synthesis_id": synthesis.id,
                    "source_count": len(synthesis.source_ideas),
                    "coherence": synthesis.coherence_score,
                    "synthesis_count": 1,
                }

        return {"synthesis_count": 0}

    def evaluate_workflow(self) -> Dict:
        """AC3: Evaluate workflow outcomes."""
        if not self.evaluation_session:
            return {"evaluation_count": 0}

        self.current_phase = WorkflowPhase.EVALUATION

        # Calculate overall quality
        completed = len([t for t in self.tasks.values() if t.status == "completed"])
        total = len(self.tasks)
        quality_score = completed / total if total > 0 else 0.0

        # Have each agent evaluate the workflow
        evaluation_count = 0
        for agent_name, (_, personality, _) in self.agents.items():
            self.evaluation_session.evaluate_idea(
                idea_id=self.workflow_id,
                evaluator=agent_name,
                quality=quality_score,
                novelty=0.7,
                feasibility=0.85,
                impact=0.75,
                justification=f"Workflow evaluation by {agent_name}",
            )
            evaluation_count += 1

        aggregated = self.evaluation_session.aggregate_evaluations(self.workflow_id)
        aggregated["evaluation_count"] = evaluation_count
        return aggregated

    def store_memory(self) -> Dict:
        """Store workflow execution in collaborative memory."""
        completed = len([t for t in self.tasks.values() if t.status == "completed"])
        total = len(self.tasks)
        quality = completed / total if total > 0 else 0.0

        self.memory_store.store_memory(
            session_type="workflow",
            topic=self.name,
            agents=list(self.agents.keys()),
            quality=quality,
            ideas=len(self.context.ideas),
            success_indicators=[f"{completed}/{total} tasks completed"],
            lessons=[f"Workflow {self.workflow_id} execution pattern"],
        )

        return {"memory_stored": True}

    def complete_workflow(self) -> Dict:
        """
        Complete full workflow: brainstorm → execute → synthesize → evaluate → remember.

        AC1: Integrates all 3 epics in end-to-end flow.
        AC5: Performance measured.
        """
        start_time = datetime.now()

        # Phase 1: Ideation
        brainstorm_results = self.run_brainstorm_phase(turns_per_agent=1)

        # Phase 2: Execution
        execution_results = self.execute_workflow()

        # Phase 3: Synthesis
        synthesis_results = self.synthesize_results()

        # Phase 4: Evaluation
        evaluation_results = self.evaluate_workflow()

        # Phase 5: Memory
        memory_results = self.store_memory()

        end_time = datetime.now()
        total_time_ms = (end_time - start_time).total_seconds() * 1000

        self.current_phase = WorkflowPhase.COMPLETE
        self.completed_at = end_time.isoformat()

        self.metrics = {
            "workflow_id": self.workflow_id,
            "total_time_ms": round(total_time_ms, 2),
            "tasks_completed": execution_results["tasks_completed"],
            "final_phase": self.current_phase.value,
            "brainstorm_results": brainstorm_results,
            "execution_results": execution_results,
            "synthesis_results": synthesis_results,
            "evaluation_results": evaluation_results,
            "memory_results": memory_results,
            "phases_completed": 5,
        }

        return self.metrics

    def to_dict(self) -> Dict:
        """AC4: Serialize workflow state to JSON."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "current_phase": self.current_phase.value,
            "tasks": {tid: task.to_dict() for tid, task in self.tasks.items()},
            "agents": {
                agent_name: {
                    "state": state.to_dict(),
                    "personality": {
                        "name": personality.name,
                        "role": personality.role.value,
                        "traits": personality.traits,
                    },
                }
                for agent_name, (state, personality, _) in self.agents.items()
            },
            "context": {
                "session_id": self.context.session_id,
                "topic": self.context.topic,
                "problem_statement": self.context.problem_statement,
                "ideas": {
                    idea_id: {
                        "content": idea.content,
                        "contributor": idea.contributor,
                        "category": idea.category.value,
                    }
                    for idea_id, idea in self.context.ideas.items()
                },
            },
            "brainstorm_session": (
                {
                    "session_id": self.brainstorm_session.session_id,
                    "total_turns": len(self.brainstorm_session.turns),
                }
                if self.brainstorm_session
                else None
            ),
            "synthesis_session": (
                {
                    "session_id": self.synthesis_session.session_id,
                    "synthesis_count": len(self.synthesis_session.synthesized_ideas),
                }
                if self.synthesis_session
                else None
            ),
            "evaluation_session": (
                {
                    "session_id": self.evaluation_session.session_id,
                    "evaluation_count": len(self.evaluation_session.evaluations),
                }
                if self.evaluation_session
                else None
            ),
            "metrics": self.metrics,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


def create_workflow_from_tasks(
    workflow_id: str,
    task_ids: List[str],
    agent_names: List[str],
    problem_statement: str,
    workflow_name: str = "",
    initialize_collab: bool = True,
) -> WorkflowOrchestrator:
    """
    Helper function to create a workflow with tasks and agents.

    Args:
        workflow_id: Unique workflow identifier
        task_ids: List of task IDs to create
        agent_names: List of agent names (Athena, Cato, Zephyr)
        problem_statement: Problem statement for collaboration
        workflow_name: Optional workflow name
        initialize_collab: Whether to initialize collaboration (default True)

    Returns:
        Configured WorkflowOrchestrator
    """
    orchestrator = WorkflowOrchestrator(
        workflow_id=workflow_id,
        name=workflow_name or workflow_id,
        description=problem_statement,
    )

    # Add tasks
    for task_id in task_ids:
        orchestrator.add_task(
            task_id=task_id,
            name=task_id.replace("_", " ").title(),
            description=f"Task: {task_id}",
            task_type="implementation",  # Default type
            complexity="moderate",
        )

    # Add agents
    agent_map = {
        "Athena": ARCHITECT_PERSONALITY,
        "Cato": EXECUTOR_PERSONALITY,
        "Zephyr": EXPERIMENTER_PERSONALITY,
    }

    for agent_name in agent_names:
        if agent_name in agent_map:
            orchestrator.add_agent(agent_map[agent_name])

    # Initialize collaboration if requested
    if initialize_collab:
        orchestrator.initialize_collaboration(
            topic=workflow_name or workflow_id, problem_statement=problem_statement
        )

    return orchestrator
