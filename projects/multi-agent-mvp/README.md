# Multi-Agent MVP System

A comprehensive multi-agent workflow system with personality-driven task selection, collaborative creativity, and observable state. Built with radical transparency and emergent behavior.

## Overview

This system implements a complete multi-agent architecture across 4 epics:

- **Epic 1: Task Dependency Engine** - Topological sorting, cycle detection, dependency management
- **Epic 2: Agent Personality System** - 3 distinct archetypes with task affinity scoring
- **Epic 3: Collaborative Creativity** - Brainstorming, synthesis, evaluation, and memory
- **Epic 4: Integration & Validation** - End-to-end workflows, benchmarking, real-world scenarios

### Key Features

✨ **Personality-Driven Agents**: 3 archetypes (Architect, Executor, Experimenter) with distinct traits and task preferences

🔗 **Smart Task Dependencies**: Automatic dependency resolution with topological sorting

🤝 **Collaborative Creativity**: Multi-agent brainstorming, idea synthesis, and evaluation

📊 **Observable State**: All components JSON-serializable for radical transparency

⚡ **High Performance**: <1s for 10 tasks, <5s for 50 tasks

🎯 **Real-World Scenarios**: Software projects, research papers, product launches

## Installation

```bash
# Clone repository
git clone <repository-url>
cd multi-agent-mvp

# Install dependencies (Python 3.11+)
pip install -r requirements.txt

# Run tests
pytest
```

## Quick Start

### Basic Workflow

```python
from src.orchestration.workflow import create_workflow_from_tasks

# Create a workflow with tasks and agents
orchestrator = create_workflow_from_tasks(
    workflow_id="my_project",
    task_ids=["design", "implement", "test"],
    agent_names=["Athena", "Cato", "Zephyr"],
    problem_statement="Build a new feature"
)

# Set task types for personality matching
orchestrator.tasks["design"].task_type = "architecture"
orchestrator.tasks["implement"].task_type = "implementation"
orchestrator.tasks["test"].task_type = "testing"

# Set dependencies
orchestrator.tasks["implement"].dependencies = ["design"]
orchestrator.tasks["test"].dependencies = ["implement"]

# Execute complete workflow
result = orchestrator.complete_workflow()

print(f"Completed {result['tasks_completed']} tasks")
print(f"Generated {result['brainstorm_results']['total_ideas']} ideas")
```

### Run Real-World Scenarios

```python
from src.scenarios.real_world import run_all_scenarios

# Run all 3 scenarios (Software, Research, Product Launch)
results = run_all_scenarios()

for result in results:
    print(f"{result.scenario_name}: {result.tasks_completed}/{result.total_tasks} tasks")
    print(f"  Quality: {result.quality_score:.2f}")
    print(f"  Emergent behaviors: {len(result.emergent_behaviors)}")
```

### Performance Benchmarking

```python
from src.benchmarks.performance import run_full_benchmark_suite

# Run complete benchmark suite
suite = run_full_benchmark_suite()

# Export results
suite.export_report("benchmark_results.json")
```

## Architecture

### System Components

```
multi-agent-mvp/
├── src/
│   ├── core/              # Epic 1: Task Dependency Engine
│   │   ├── topological_sort.py
│   │   ├── ready_tasks.py
│   │   └── conditional_branching.py
│   ├── agents/            # Epic 2: Agent Personality System
│   │   ├── personality.py
│   │   ├── affinity.py
│   │   ├── state.py
│   │   └── agency.py
│   ├── collaboration/     # Epic 3: Collaborative Creativity
│   │   ├── context.py
│   │   ├── brainstorming.py
│   │   ├── synthesis.py
│   │   ├── evaluation.py
│   │   └── memory.py
│   ├── orchestration/     # Epic 4: Workflow Orchestration
│   │   └── workflow.py
│   ├── benchmarks/        # Performance Testing
│   │   └── performance.py
│   └── scenarios/         # Real-World Validation
│       └── real_world.py
└── tests/                 # 397 comprehensive tests
```

### Agent Archetypes

**Athena (Architect)**
- Strategic thinker and systems designer
- Excels at: Architecture (0.95), Design (0.90), Planning (0.85)
- Decision pattern: Analyzes from first principles

**Cato (Executor)**
- Pragmatic implementer focused on delivery
- Excels at: Implementation (1.0), Testing (0.85), Review (0.70)
- Decision pattern: Gathers requirements, validates through testing

**Zephyr (Experimenter)**
- Creative innovator and boundary-pusher
- Excels at: Creative (0.95), Design (0.75), Architecture (0.60)
- Decision pattern: Explores possibilities, learns through experimentation

### Workflow Phases

1. **Planning**: Define tasks and dependencies
2. **Ideation**: Collaborative brainstorming
3. **Execution**: Task execution by agents
4. **Synthesis**: Combine results
5. **Evaluation**: Assess outcomes
6. **Complete**: Store memory and finish

## Examples

### Example 1: Software Development Project

```python
from src.orchestration.workflow import create_workflow_from_tasks

# Create realistic software project
orchestrator = create_workflow_from_tasks(
    workflow_id="auth_feature",
    task_ids=[
        "design_architecture",
        "implement_backend",
        "implement_frontend",
        "write_tests",
        "documentation"
    ],
    agent_names=["Athena", "Cato", "Zephyr"],
    problem_statement="Build user authentication feature"
)

# Configure task types
orchestrator.tasks["design_architecture"].task_type = "architecture"
orchestrator.tasks["implement_backend"].task_type = "implementation"
orchestrator.tasks["implement_frontend"].task_type = "implementation"
orchestrator.tasks["write_tests"].task_type = "testing"
orchestrator.tasks["documentation"].task_type = "planning"

# Set dependencies
orchestrator.tasks["implement_backend"].dependencies = ["design_architecture"]
orchestrator.tasks["implement_frontend"].dependencies = ["design_architecture"]
orchestrator.tasks["write_tests"].dependencies = ["implement_backend", "implement_frontend"]
orchestrator.tasks["documentation"].dependencies = ["write_tests"]

# Execute and analyze
result = orchestrator.complete_workflow()

print(f"✓ {result['tasks_completed']} tasks completed")
print(f"✓ Agents: {list(result['execution_results']['task_assignments'].values())}")
print(f"✓ Time: {result['total_time_ms']:.2f}ms")
```

### Example 2: Custom Agent Workflow

```python
from src.orchestration.workflow import WorkflowOrchestrator
from src.agents.personality import ARCHITECT_PERSONALITY, EXECUTOR_PERSONALITY

# Create orchestrator manually
orchestrator = WorkflowOrchestrator(
    workflow_id="custom_workflow",
    name="Custom Project",
    description="Custom multi-agent workflow"
)

# Add tasks
orchestrator.add_task(
    task_id="task1",
    name="Design System",
    description="System architecture design",
    task_type="architecture",
    complexity="complex"
)

orchestrator.add_task(
    task_id="task2",
    name="Implement",
    description="Build the system",
    task_type="implementation",
    complexity="moderate",
    dependencies=["task1"]
)

# Add agents
orchestrator.add_agent(ARCHITECT_PERSONALITY)
orchestrator.add_agent(EXECUTOR_PERSONALITY)

# Initialize collaboration
orchestrator.initialize_collaboration(
    topic="Custom Project",
    problem_statement="Build custom system"
)

# Execute
result = orchestrator.complete_workflow()
```

### Example 3: Benchmarking Performance

```python
from src.benchmarks.performance import BenchmarkSuite

# Create benchmark suite
suite = BenchmarkSuite(suite_name="My Benchmarks")

# Run scale tests
suite.run_scale_benchmarks(task_counts=[10, 25, 50])

# Run agent count comparison
suite.run_agent_count_benchmarks(
    agent_configs=[
        ["Athena"],
        ["Athena", "Cato"],
        ["Athena", "Cato", "Zephyr"]
    ]
)

# Generate report
report = suite.generate_report()

print(f"Benchmarks: {report['total_benchmarks']}")
print(f"Avg time: {report['summary']['avg_execution_time_ms']:.2f}ms")
print(f"Max throughput: {report['summary']['max_throughput_tasks_per_sec']:.2f} tasks/sec")

# Validate targets
validation = report['validation']
print(f"All targets passed: {validation['all_passed']}")
```

### Example 4: Persistence - Save and Load Workflows

```python
from src.persistence.workflow_storage import WorkflowStorage
from src.orchestration.workflow import create_workflow_from_tasks

# Create and execute a workflow
orchestrator = create_workflow_from_tasks(
    workflow_id="my_project_v1",
    task_ids=["task1", "task2", "task3"],
    agent_names=["Athena", "Cato"],
    problem_statement="Complete project implementation"
)

result = orchestrator.complete_workflow()

# Save workflow to disk
storage = WorkflowStorage(storage_dir="saved_workflows")
filepath = storage.save_workflow(orchestrator, tags=["completed", "production"])

print(f"✓ Saved to: {filepath}")

# Load workflow back from disk
loaded = storage.load_workflow(filepath)
print(f"✓ Loaded: {loaded.workflow_id} with {len(loaded.tasks)} tasks")

# List all saved workflows
workflows = storage.list_workflows()
for wf in workflows:
    print(f"  - {wf['workflow_id']} ({wf['saved_at']})")

# Filter by tags
completed = storage.list_workflows(tags=["completed"])
print(f"✓ Completed workflows: {len(completed)}")
```

### Example 5: Batch Persistence - Multiple Workflows

```python
from src.persistence.workflow_storage import WorkflowStorage
from src.orchestration.workflow import create_workflow_from_tasks

# Create multiple workflows
workflows = [
    create_workflow_from_tasks(
        workflow_id=f"project_{i}",
        task_ids=[f"t{i}_1", f"t{i}_2"],
        agent_names=["Athena", "Cato"],
        problem_statement=f"Project {i}"
    )
    for i in range(3)
]

# Execute all
for wf in workflows:
    wf.complete_workflow()

# Save all in batch
storage = WorkflowStorage(storage_dir="saved_workflows")
results = storage.save_workflows_batch(workflows, directory="projects")

print(f"✓ Saved {len(results)} workflows to 'projects' directory")

# Load all from directory
loaded_workflows = storage.load_workflows_batch("projects")
print(f"✓ Loaded {len(loaded_workflows)} workflows back")

# Export comprehensive report
for name, orchestrator in loaded_workflows.items():
    report = storage.export_workflow_report(orchestrator)
    print(f"  - {report['workflow_info']['id']}: {report['metrics']}")
```

### Example 6: Workflow Versioning and Management

```python
from src.persistence.workflow_storage import WorkflowStorage, save_workflow_quick, load_workflow_quick
from src.orchestration.workflow import create_workflow_from_tasks

# Quick save using convenience function
orchestrator = create_workflow_from_tasks(
    workflow_id="versioned_project",
    task_ids=["task1", "task2"],
    agent_names=["Athena"],
    problem_statement="Version control demo"
)

# Save version 1
filepath_v1 = save_workflow_quick(orchestrator, filename="versioned_project_v1.json")
print(f"✓ Saved v1: {filepath_v1}")

# Modify and save version 2
orchestrator.metrics = {"iterations": 2, "quality": 0.95}
filepath_v2 = save_workflow_quick(orchestrator, filename="versioned_project_v2.json")
print(f"✓ Saved v2: {filepath_v2}")

# Load specific version
storage = WorkflowStorage()
v1 = load_workflow_quick(filepath_v1)
v2 = load_workflow_quick(filepath_v2)

# Get version history
versions = storage.get_workflow_versions("versioned_project")
for v in versions:
    print(f"  - {v['filename']} ({v['saved_at']})")

# Delete old version
storage.delete_workflow("versioned_project_v1.json")
print("✓ Deleted v1")
```

## API Reference

### Core Classes

#### `WorkflowOrchestrator`
Main orchestration class integrating all system components.

**Methods:**
- `add_task(task_id, name, description, task_type, complexity, dependencies)` - Add task to workflow
- `add_agent(personality)` - Add agent with personality
- `initialize_collaboration(topic, problem_statement)` - Set up collaboration
- `run_brainstorm_phase(turns_per_agent)` - Run collaborative ideation
- `execute_workflow()` - Execute tasks with dependency resolution
- `synthesize_results()` - Combine agent outputs
- `evaluate_workflow()` - Assess quality
- `complete_workflow()` - Run full 5-phase workflow
- `to_dict()` - Serialize state to JSON

#### `BenchmarkSuite`
Performance measurement and validation.

**Methods:**
- `run_benchmark(benchmark_name, task_count, agent_names, workflow_config)` - Run single benchmark
- `run_scale_benchmarks(task_counts)` - Test across scales
- `run_agent_count_benchmarks(agent_configs)` - Compare configurations
- `validate_performance_targets()` - Check against targets
- `generate_report()` - Create comprehensive report
- `export_report(filename)` - Save to JSON

#### `WorkflowStorage`
Persistent storage for workflows with versioning and batch operations.

**Methods:**
- `save_workflow(orchestrator, filename, tags)` - Save workflow to JSON file
- `load_workflow(filepath)` - Load workflow from saved file
- `save_workflows_batch(orchestrators, directory)` - Save multiple workflows
- `load_workflows_batch(directory)` - Load multiple workflows from directory
- `get_workflow_versions(workflow_id)` - Get version history
- `export_workflow_report(orchestrator, include_results)` - Generate comprehensive report
- `list_workflows(tags)` - List saved workflows with optional tag filtering
- `delete_workflow(filename)` - Delete saved workflow file

### Utility Functions

#### Workflow Creation
- `create_workflow_from_tasks(workflow_id, task_ids, agent_names, problem_statement)` - Helper to quickly create configured workflow

#### Scenarios
- `run_software_project_scenario()` - Execute realistic software development scenario
- `run_research_paper_scenario()` - Execute academic research collaboration scenario
- `run_product_launch_scenario()` - Execute business strategy and launch scenario
- `run_all_scenarios()` - Run all 3 real-world scenarios

#### Persistence (Convenience Functions)
- `save_workflow_quick(orchestrator, filename)` - Quick save workflow without creating storage object
- `load_workflow_quick(filepath)` - Quick load workflow without creating storage object

## Testing

The system includes 429 comprehensive tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test suites
pytest tests/test_workflow_orchestration.py -v      # Workflow integration
pytest tests/test_persistence.py -v                 # Persistence layer
pytest tests/test_performance_benchmarks.py -v      # Performance
pytest tests/test_scenarios.py -v                   # Real-world scenarios
pytest tests/test_agents.py -v                      # Agent system

# Run benchmarks
python -m src.benchmarks.performance

# Run scenarios
python -m src.scenarios.real_world
```

### Test Coverage

- **Epic 1**: 133 tests (topological sort, ready tasks, branching)
- **Epic 2**: 109 tests (personality, affinity, state, agency)
- **Epic 3**: 86 tests (context, brainstorming, synthesis, evaluation, memory)
- **Epic 4**: 69 tests (orchestration, benchmarks, scenarios)
- **Persistence**: 32 tests (save/load, batch operations, versioning, validation)

## Performance Targets

✅ **10 tasks**: <1 second  
✅ **50 tasks**: <5 seconds  
✅ **100 tasks**: <10 seconds  
✅ **Throughput**: >50 tasks/second

## Design Principles

1. **Observable State**: All components JSON-serializable for transparency
2. **Personality-Driven**: Agents autonomously select tasks by affinity
3. **Emergent Behavior**: System demonstrates collaborative problem-solving
4. **Test-Driven**: 100% test coverage with acceptance criteria validation
5. **Real-World Ready**: Validated with realistic scenarios
6. **Persistent**: Complete workflow state saved/restored with versioning

## Contributing

This is a demonstration project showcasing multi-agent system design patterns.

## License

MIT License - see LICENSE file for details.

## Authors

Built as a comprehensive multi-agent MVP demonstrating:
- Task dependency management
- Personality-driven agent systems
- Collaborative creativity
- End-to-end workflow orchestration
- Performance benchmarking
- Real-world scenario validation
- Persistent storage and versioning

---

**Total:** 429 passing tests | 3 agent archetypes | 4 epics + persistence | 3 real-world scenarios | 32 persistence tests
