# API Reference

Complete API documentation for the Multi-Agent MVP System.

## Table of Contents

- [Core Module](#core-module)
- [Agents Module](#agents-module)
- [Collaboration Module](#collaboration-module)
- [Orchestration Module](#orchestration-module)
- [Benchmarks Module](#benchmarks-module)
- [Scenarios Module](#scenarios-module)

---

## Core Module

Task dependency management and execution ordering.

### `topological_sort(task_graph: Dict[str, List[str]]) -> List[str]`

Compute topological ordering using Kahn's algorithm.

**Parameters:**
- `task_graph`: Dict mapping task IDs to their dependencies

**Returns:**
- List of task IDs in execution order

**Raises:**
- `ValueError`: If cycle detected

**Example:**
```python
graph = {"A": [], "B": ["A"], "C": ["A", "B"]}
order = topological_sort(graph)  # ["A", "B", "C"]
```

### `get_ready_tasks(task_queue: Dict) -> List[str]`

Get tasks whose dependencies are satisfied.

**Parameters:**
- `task_queue`: Dict of task states with dependencies

**Returns:**
- List of task IDs ready to execute

---

## Agents Module

Personality-driven agent system with task affinity.

### `AgentPersonality`

Complete agent personality definition.

**Attributes:**
- `name` (str): Agent name
- `role` (AgentRole): Archetype (ARCHITECT, EXECUTOR, EXPERIMENTER)
- `description` (str): One-sentence description
- `system_prompt` (str): Core system instructions (500+ chars)
- `traits` (List[str]): 5-7 personality traits
- `task_preferences` (Dict[str, float]): Task type affinities (0.0-1.0)
- `communication_style` (str): How agent communicates
- `strength_areas` (List[str]): 3-4 areas of expertise
- `weakness_areas` (List[str]): 2-3 areas of limitation
- `decision_pattern` (str): How agent makes decisions

**Methods:**
- `to_dict() -> Dict`: Serialize to dictionary

**Example:**
```python
from src.agents.personality import ARCHITECT_PERSONALITY

print(ARCHITECT_PERSONALITY.name)  # "Athena"
print(ARCHITECT_PERSONALITY.task_preferences["architecture"])  # 0.95
```

### `get_personality_by_name(name: str) -> AgentPersonality`

Get agent personality by name.

**Parameters:**
- `name`: Agent name (case-insensitive)

**Returns:**
- AgentPersonality object

**Raises:**
- `ValueError`: If agent not found

### `score_task_affinity(agent_personality: AgentPersonality, task_profile: TaskProfile) -> float`

Calculate agent's affinity for a task.

**Parameters:**
- `agent_personality`: Agent's personality profile
- `task_profile`: Task characteristics

**Returns:**
- Affinity score (0.0-1.0)

**Formula:**
```
affinity = (type_preference × 0.6) + (complexity_match × 0.3) + (novelty_bonus × 0.1)
```

### `AgentExecutor`

Executes tasks with personality-driven selection.

**Attributes:**
- `agent_state` (AgentState): Current agent state
- `personality` (AgentPersonality): Agent personality

**Methods:**
- `score_task_affinity(task: Task) -> float`: Calculate affinity for task
- `execute_task(task: Task) -> bool`: Execute task if ready
- `select_task(available_tasks: List[Task]) -> Optional[Task]`: Choose best task

---

## Collaboration Module

Multi-agent brainstorming, synthesis, and evaluation.

### `SharedContext`

Shared workspace for multi-agent collaboration.

**Attributes:**
- `session_id` (str): Unique session ID
- `topic` (str): Collaboration topic
- `problem_statement` (str): Problem being solved
- `ideas` (Dict[str, Idea]): All generated ideas
- `participating_agents` (Set[str]): Agent names

**Methods:**
- `add_idea(content, contributor, category) -> Idea`: Add new idea
- `get_ideas_by_category(category) -> List[Idea]`: Filter by category
- `get_ideas_by_contributor(contributor) -> List[Idea]`: Filter by agent
- `to_dict() -> Dict`: Serialize state

### `BrainstormSession`

Turn-based brainstorming session.

**Attributes:**
- `session_id` (str): Session ID
- `context` (SharedContext): Shared context
- `agent_names` (List[str]): Participating agents
- `turns` (List[BrainstormTurn]): All turns taken

**Methods:**
- `add_agents(agent_names: List[str])`: Register agents
- `add_turn(agent_name, idea_content, category) -> Tuple[BrainstormTurn, Idea]`: Add turn
- `get_agent_turns(agent_name) -> List[BrainstormTurn]`: Get agent's turns
- `to_dict() -> Dict`: Serialize session

### `SynthesisSession`

Combines ideas into emergent solutions.

**Attributes:**
- `session_id` (str): Session ID
- `context` (SharedContext): Shared context
- `synthesized_ideas` (Dict[str, SynthesizedIdea]): Combined ideas

**Methods:**
- `synthesize_ideas(source_idea_ids, synthesis_content, emergent_properties, coherence, novelty) -> SynthesizedIdea`: Combine ideas
- `synthesize_high_quality_ideas(min_contributors, category) -> List[SynthesizedIdea]`: Auto-synthesize quality ideas

### `EvaluationSession`

Multi-dimensional quality assessment.

**Attributes:**
- `session_id` (str): Session ID
- `context` (SharedContext): Shared context
- `evaluations` (Dict[str, List[Evaluation]]): All evaluations

**Methods:**
- `evaluate_idea(idea_id, evaluator, quality, novelty, feasibility, impact, justification) -> Evaluation`: Evaluate idea
- `get_idea_evaluations(idea_id) -> List[Evaluation]`: Get all evaluations
- `aggregate_evaluations(idea_id) -> Dict`: Compute aggregate scores

### `CollaborativeMemoryStore`

Stores collaboration patterns and learning.

**Attributes:**
- `store_id` (str): Store ID
- `memories` (List[CollaborationMemory]): Stored memories
- `agent_performance` (Dict): Performance tracking

**Methods:**
- `store_memory(session_type, topic, agents, quality, ideas, success_indicators, lessons) -> CollaborationMemory`: Store memory
- `retrieve_memories(filters) -> List[CollaborationMemory]`: Query memories
- `analyze_patterns() -> Dict`: Analyze collaboration patterns

---

## Orchestration Module

End-to-end workflow orchestration.

### `WorkflowOrchestrator`

Main orchestration class integrating all epics.

**Attributes:**
- `workflow_id` (str): Unique workflow ID
- `name` (str): Workflow name
- `description` (str): Problem description
- `tasks` (Dict[str, WorkflowTask]): All workflow tasks
- `agents` (Dict[str, Tuple]): Agents (state, personality, executor)
- `context` (SharedContext): Shared collaboration context
- `brainstorm_session` (BrainstormSession): Brainstorming session
- `synthesis_session` (SynthesisSession): Synthesis session
- `evaluation_session` (EvaluationSession): Evaluation session
- `memory_store` (CollaborativeMemoryStore): Memory storage
- `current_phase` (WorkflowPhase): Current execution phase
- `metrics` (Dict): Performance metrics

**Methods:**

#### `add_task(task_id, name, description, task_type, complexity='moderate', dependencies=None) -> WorkflowTask`

Add task to workflow.

**Parameters:**
- `task_id`: Unique task identifier
- `name`: Human-readable name
- `description`: Task description
- `task_type`: Type (architecture, implementation, testing, creative, etc.)
- `complexity`: simple, moderate, complex, difficult
- `dependencies`: List of task IDs this depends on

**Returns:**
- WorkflowTask object

#### `add_agent(personality: AgentPersonality) -> str`

Add agent with personality to workflow.

**Parameters:**
- `personality`: AgentPersonality to add

**Returns:**
- Agent name

#### `initialize_collaboration(topic: str, problem_statement: str)`

Initialize collaborative sessions.

**Parameters:**
- `topic`: Collaboration topic
- `problem_statement`: Problem to solve

#### `run_brainstorm_phase(turns_per_agent: int = 2) -> Dict`

Run collaborative brainstorming.

**Parameters:**
- `turns_per_agent`: Number of turns each agent takes

**Returns:**
- Dict with brainstorm results

#### `execute_workflow() -> Dict`

Execute tasks with dependency resolution.

**Returns:**
- Dict with execution results including:
  - `tasks_completed`: Number completed
  - `task_assignments`: Agent assignments
  - `affinity_scores`: Affinity for each task
  - `execution_order`: Order of execution

#### `synthesize_results() -> Dict`

Combine agent outputs into emergent solutions.

**Returns:**
- Dict with synthesis results

#### `evaluate_workflow() -> Dict`

Assess workflow quality and outcomes.

**Returns:**
- Dict with evaluation results

#### `complete_workflow() -> Dict`

Run complete 5-phase workflow: planning → ideation → execution → synthesis → evaluation.

**Returns:**
- Dict with complete results including all phase outputs

#### `to_dict() -> Dict`

Serialize complete workflow state to JSON-compatible dict.

**Returns:**
- Dict with workflow state

### `create_workflow_from_tasks(workflow_id, task_ids, agent_names, problem_statement, workflow_name='', initialize_collab=True) -> WorkflowOrchestrator`

Helper to quickly create configured workflow.

**Parameters:**
- `workflow_id`: Unique identifier
- `task_ids`: List of task IDs to create
- `agent_names`: List of agent names (Athena, Cato, Zephyr)
- `problem_statement`: Problem description
- `workflow_name`: Optional name (defaults to workflow_id)
- `initialize_collab`: Whether to initialize collaboration

**Returns:**
- Configured WorkflowOrchestrator

**Example:**
```python
orchestrator = create_workflow_from_tasks(
    workflow_id="my_project",
    task_ids=["task1", "task2", "task3"],
    agent_names=["Athena", "Cato"],
    problem_statement="Build feature"
)
```

---

## Benchmarks Module

Performance measurement and validation.

### `BenchmarkSuite`

Suite of performance benchmarks.

**Attributes:**
- `suite_name` (str): Suite name
- `results` (List[BenchmarkResult]): All benchmark results
- `performance_targets` (Dict): Target thresholds

**Methods:**

#### `run_benchmark(benchmark_name, task_count, agent_names, workflow_config='default', metadata=None) -> BenchmarkResult`

Run single benchmark and collect metrics.

**Parameters:**
- `benchmark_name`: Benchmark identifier
- `task_count`: Number of tasks
- `agent_names`: Agents to use
- `workflow_config`: Configuration description
- `metadata`: Optional metadata dict

**Returns:**
- BenchmarkResult with metrics

#### `run_scale_benchmarks(task_counts=None) -> List[BenchmarkResult]`

Run benchmarks across different scales.

**Parameters:**
- `task_counts`: List of task counts (default: [10, 25, 50, 100])

**Returns:**
- List of BenchmarkResult objects

#### `run_agent_count_benchmarks(agent_configs=None) -> List[BenchmarkResult]`

Compare performance across agent counts.

**Parameters:**
- `agent_configs`: List of agent name lists

**Returns:**
- List of BenchmarkResult objects

#### `validate_performance_targets() -> Dict`

Validate system meets performance targets.

**Returns:**
- Dict with validation results including:
  - `all_passed`: Boolean
  - `targets`: Results for each target
  - `violations`: List of failures

#### `generate_report() -> Dict`

Generate comprehensive performance report.

**Returns:**
- Dict with:
  - Summary statistics
  - Validation results
  - All benchmark results
  - Visualization data

#### `export_report(filename: str = 'benchmark_report.json') -> str`

Export report to JSON file.

**Parameters:**
- `filename`: Output filename

**Returns:**
- Filename

### `run_full_benchmark_suite() -> BenchmarkSuite`

Run complete benchmark suite with all tests.

**Returns:**
- BenchmarkSuite with results

---

## Scenarios Module

Real-world scenario validation.

### `ScenarioResult`

Results from executing a real-world scenario.

**Attributes:**
- `scenario_name` (str): Scenario name
- `description` (str): Scenario description
- `tasks_completed` (int): Tasks completed
- `total_tasks` (int): Total tasks
- `agents_participated` (List[str]): Agents that worked
- `ideas_generated` (int): Ideas from brainstorming
- `synthesis_count` (int): Synthesized ideas
- `evaluation_average` (float): Average evaluation score
- `execution_time_ms` (float): Execution time
- `quality_score` (float): Overall quality (0.0-1.0)
- `coherence_score` (float): Output coherence (0.0-1.0)
- `emergent_behaviors` (List[str]): Observed emergent behaviors
- `metadata` (Dict): Additional metadata

**Methods:**
- `to_dict() -> Dict`: Serialize result

### `run_software_project_scenario() -> ScenarioResult`

Execute realistic software development scenario.

**Scenario:**
- 9 tasks: Design → Implement → Test → Document
- Exercises all 3 epics
- Demonstrates personality-driven specialization

**Returns:**
- ScenarioResult

### `run_research_paper_scenario() -> ScenarioResult`

Execute academic research collaboration scenario.

**Scenario:**
- 13 tasks: Literature review → Methodology → Experiments → Writing
- Complex dependencies
- Deep collaborative creativity

**Returns:**
- ScenarioResult

### `run_product_launch_scenario() -> ScenarioResult`

Execute business strategy and launch scenario.

**Scenario:**
- 10 tasks: Market research → Positioning → Campaign → Launch
- Parallel execution
- Creative and strategic synthesis

**Returns:**
- ScenarioResult

### `run_all_scenarios() -> List[ScenarioResult]`

Run all 3 real-world scenarios.

**Returns:**
- List of ScenarioResult objects

**Example:**
```python
from src.scenarios.real_world import run_all_scenarios

results = run_all_scenarios()
for result in results:
    print(f"{result.scenario_name}: {result.quality_score:.2f}")
```

---

## Type Definitions

### `WorkflowPhase` (Enum)

Workflow execution phases.

- `PLANNING`: Define tasks and dependencies
- `IDEATION`: Collaborative brainstorming
- `EXECUTION`: Task execution
- `SYNTHESIS`: Combine results
- `EVALUATION`: Assess outcomes
- `COMPLETE`: Finished

### `IdeaCategory` (Enum)

Categories for ideas.

- `CORE_CONCEPT`: Fundamental concepts
- `APPROACH`: Solution approaches
- `DETAIL`: Implementation details
- `CONSTRAINT`: Constraints and limitations
- `CRITIQUE`: Critical analysis
- `SYNTHESIS`: Combined ideas
- `QUESTION`: Questions raised
- `INSIGHT`: Key insights

### `AgentRole` (Enum)

Agent archetype roles.

- `ARCHITECT`: Strategic design and planning
- `EXECUTOR`: Implementation and execution
- `EXPERIMENTER`: Innovation and exploration

---

## Constants

### Agent Personalities

```python
from src.agents.personality import (
    ARCHITECT_PERSONALITY,    # Athena
    EXECUTOR_PERSONALITY,     # Cato
    EXPERIMENTER_PERSONALITY  # Zephyr
)
```

### Performance Targets

```python
{
    "10_tasks_max_ms": 1000,      # <1s for 10 tasks
    "50_tasks_max_ms": 5000,      # <5s for 50 tasks
    "100_tasks_max_ms": 10000,    # <10s for 100 tasks
    "min_throughput_tasks_per_sec": 50  # 50+ tasks/sec
}
```

---

## Error Handling

### Common Exceptions

- `ValueError`: Invalid input (e.g., unknown agent, cycle in dependencies)
- `KeyError`: Missing required data (e.g., task not found)
- `AssertionError`: Validation failure in tests

### Example Error Handling

```python
from src.orchestration.workflow import create_workflow_from_tasks

try:
    orchestrator = create_workflow_from_tasks(
        workflow_id="test",
        task_ids=["task1"],
        agent_names=["UnknownAgent"],  # Invalid agent
        problem_statement="Test"
    )
except ValueError as e:
    print(f"Error: {e}")
```

---

## Best Practices

1. **Task Types**: Use standard types (architecture, implementation, testing, creative, analysis, review, planning, design)

2. **Dependencies**: Keep dependency depth reasonable (<10 levels)

3. **Agent Selection**: Use all 3 archetypes for balanced workflows

4. **Performance**: For >100 tasks, consider batching or parallel execution

5. **Observability**: Use `to_dict()` to inspect state at any point

6. **Testing**: Validate custom workflows with benchmarks

---

## Version

API Version: 1.0  
Last Updated: 2025-11-11  
Tested with Python: 3.11+
