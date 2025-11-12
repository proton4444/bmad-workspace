# Tutorial: Building Multi-Agent Workflows

Step-by-step guide to creating multi-agent workflows from scratch.

## Table of Contents

1. [Hello World](#hello-world)
2. [Understanding Agent Personalities](#understanding-agent-personalities)
3. [Working with Dependencies](#working-with-dependencies)
4. [Collaborative Creativity](#collaborative-creativity)
5. [Complete Project Example](#complete-project-example)
6. [Performance Optimization](#performance-optimization)
7. [Best Practices](#best-practices)

---

## Hello World

Let's create your first multi-agent workflow.

### Step 1: Create a Simple Workflow

```python
from src.orchestration.workflow import create_workflow_from_tasks

# Create workflow with 3 tasks and 2 agents
orchestrator = create_workflow_from_tasks(
    workflow_id="hello_world",
    task_ids=["task1", "task2", "task3"],
    agent_names=["Athena", "Cato"],
    problem_statement="My first multi-agent workflow"
)

# Execute the workflow
result = orchestrator.complete_workflow()

# View results
print(f"✓ Completed {result['tasks_completed']} tasks")
print(f"✓ Generated {result['brainstorm_results']['total_ideas']} ideas")
print(f"✓ Time: {result['total_time_ms']:.2f}ms")
```

**Output:**
```
✓ Completed 3 tasks
✓ Generated 2 ideas
✓ Time: 15.43ms
```

### Step 2: Inspect the Results

```python
# See which agent did what
assignments = result['execution_results']['task_assignments']
for task_id, agent_name in assignments.items():
    print(f"{task_id} → {agent_name}")

# Check execution order
print(f"Order: {result['execution_results']['execution_order']}")
```

**Output:**
```
task1 → Cato
task2 → Cato
task3 → Cato
Order: ['task1', 'task2', 'task3']
```

### Step 3: Serialize the State

```python
import json

# Get complete workflow state
state = orchestrator.to_dict()

# Save to file
with open('workflow_state.json', 'w') as f:
    json.dump(state, f, indent=2)

print("✓ State saved to workflow_state.json")
```

---

## Understanding Agent Personalities

Each agent has distinct preferences and behaviors.

### The Three Archetypes

**Athena (Architect)**: Strategic designer
```python
from src.agents.personality import ARCHITECT_PERSONALITY

print(ARCHITECT_PERSONALITY.name)  # "Athena"
print(ARCHITECT_PERSONALITY.role)  # AgentRole.ARCHITECT

# Check task preferences
prefs = ARCHITECT_PERSONALITY.task_preferences
print(f"Architecture: {prefs['architecture']}")  # 0.95
print(f"Implementation: {prefs['implementation']}")  # 0.40
```

**Cato (Executor)**: Pragmatic implementer
```python
from src.agents.personality import EXECUTOR_PERSONALITY

prefs = EXECUTOR_PERSONALITY.task_preferences
print(f"Implementation: {prefs['implementation']}")  # 1.0
print(f"Testing: {prefs['testing']}")  # 0.85
```

**Zephyr (Experimenter)**: Creative innovator
```python
from src.agents.personality import EXPERIMENTER_PERSONALITY

prefs = EXPERIMENTER_PERSONALITY.task_preferences
print(f"Creative: {prefs['creative']}")  # 0.95
print(f"Testing: {prefs['testing']}")  # 0.40
```

### Matching Tasks to Personalities

```python
orchestrator = create_workflow_from_tasks(
    workflow_id="personality_demo",
    task_ids=["design", "build", "experiment"],
    agent_names=["Athena", "Cato", "Zephyr"],
    problem_statement="Demonstrate personality matching"
)

# Set task types to match agent preferences
orchestrator.tasks["design"].task_type = "architecture"  # Athena likes this
orchestrator.tasks["build"].task_type = "implementation"  # Cato likes this
orchestrator.tasks["experiment"].task_type = "creative"  # Zephyr likes this

result = orchestrator.execute_workflow()

# Check who claimed what
assignments = result['task_assignments']
print(f"design → {assignments['design']}")  # Should be Athena
print(f"build → {assignments['build']}")  # Should be Cato
print(f"experiment → {assignments['experiment']}")  # Should be Zephyr
```

### Viewing Affinity Scores

```python
# See how much each agent wanted each task
for task_id, scores in result['affinity_scores'].items():
    print(f"\n{task_id}:")
    for agent, score in scores.items():
        print(f"  {agent}: {score:.3f}")
```

**Output:**
```
design:
  Athena: 0.855
  Cato: 0.450
  Zephyr: 0.540

build:
  Athena: 0.360
  Cato: 0.900
  Zephyr: 0.450
```

---

## Working with Dependencies

Create complex workflows with task dependencies.

### Linear Dependencies

```python
orchestrator = create_workflow_from_tasks(
    workflow_id="linear_workflow",
    task_ids=["step1", "step2", "step3"],
    agent_names=["Athena", "Cato"],
    problem_statement="Linear pipeline"
)

# Create chain: step1 → step2 → step3
orchestrator.tasks["step2"].dependencies = ["step1"]
orchestrator.tasks["step3"].dependencies = ["step2"]

result = orchestrator.execute_workflow()

# Verify execution order
order = result['execution_order']
assert order.index("step1") < order.index("step2")
assert order.index("step2") < order.index("step3")
print(f"✓ Executed in order: {order}")
```

### Parallel Dependencies

```python
orchestrator = create_workflow_from_tasks(
    workflow_id="parallel_workflow",
    task_ids=["start", "parallel_a", "parallel_b", "merge"],
    agent_names=["Athena", "Cato", "Zephyr"],
    problem_statement="Parallel execution"
)

# Diamond pattern: start → [parallel_a, parallel_b] → merge
orchestrator.tasks["parallel_a"].dependencies = ["start"]
orchestrator.tasks["parallel_b"].dependencies = ["start"]
orchestrator.tasks["merge"].dependencies = ["parallel_a", "parallel_b"]

result = orchestrator.execute_workflow()

# Verify start executed first, merge executed last
order = result['execution_order']
assert order[0] == "start"
assert order[-1] == "merge"
print(f"✓ Parallel execution: {order}")
```

### Complex Dependencies

```python
# Real-world example: Software feature development
orchestrator = create_workflow_from_tasks(
    workflow_id="feature_dev",
    task_ids=[
        "design_api",
        "design_ui",
        "implement_backend",
        "implement_frontend",
        "integration_test",
        "deploy"
    ],
    agent_names=["Athena", "Cato", "Zephyr"],
    problem_statement="Build complete feature"
)

# Set dependencies
orchestrator.tasks["implement_backend"].dependencies = ["design_api"]
orchestrator.tasks["implement_frontend"].dependencies = ["design_ui"]
orchestrator.tasks["integration_test"].dependencies = [
    "implement_backend",
    "implement_frontend"
]
orchestrator.tasks["deploy"].dependencies = ["integration_test"]

# Set task types
task_types = {
    "design_api": "architecture",
    "design_ui": "creative",
    "implement_backend": "implementation",
    "implement_frontend": "implementation",
    "integration_test": "testing",
    "deploy": "implementation"
}

for task_id, task_type in task_types.items():
    orchestrator.tasks[task_id].task_type = task_type

result = orchestrator.complete_workflow()
print(f"✓ {result['tasks_completed']}/{len(orchestrator.tasks)} tasks completed")
```

---

## Collaborative Creativity

Enable multi-agent brainstorming and synthesis.

### Basic Brainstorming

```python
orchestrator = create_workflow_from_tasks(
    workflow_id="brainstorm_demo",
    task_ids=["task1"],
    agent_names=["Athena", "Cato", "Zephyr"],
    problem_statement="How can we improve user onboarding?"
)

# Run brainstorming with 3 turns per agent
brainstorm_result = orchestrator.run_brainstorm_phase(turns_per_agent=3)

print(f"✓ Generated {brainstorm_result['total_ideas']} ideas")
print(f"✓ Total turns: {brainstorm_result['total_turns']}")

# View the ideas
for idea_id, idea in orchestrator.context.ideas.items():
    print(f"\n{idea.contributor}: {idea.content}")
    print(f"  Category: {idea.category.value}")
```

### Idea Synthesis

```python
# After brainstorming, synthesize ideas
result = orchestrator.complete_workflow()

synthesis_result = result['synthesis_results']
if synthesis_result.get('synthesis_count', 0) > 0:
    print(f"✓ Created {synthesis_result['synthesis_count']} synthesized solutions")
    print(f"  Coherence: {synthesis_result.get('coherence', 0):.2f}")
```

### Multi-Agent Evaluation

```python
# Each agent evaluates the workflow
eval_result = result['evaluation_results']

print(f"\nAverage Scores:")
avg = eval_result.get('average', {})
print(f"  Quality: {avg.get('quality', 0):.2f}")
print(f"  Novelty: {avg.get('novelty', 0):.2f}")
print(f"  Feasibility: {avg.get('feasibility', 0):.2f}")
print(f"  Impact: {avg.get('impact', 0):.2f}")
```

---

## Complete Project Example

Build a full software project from start to finish.

```python
from src.orchestration.workflow import create_workflow_from_tasks

def build_authentication_feature():
    """Complete example: Build user authentication feature."""
    
    # 1. Define the workflow
    orchestrator = create_workflow_from_tasks(
        workflow_id="auth_feature_v1",
        task_ids=[
            # Design phase
            "architecture_design",
            "database_schema",
            "api_design",
            "ui_mockups",
            
            # Implementation phase
            "implement_auth_service",
            "implement_user_model",
            "implement_api_endpoints",
            "implement_login_ui",
            "implement_signup_ui",
            
            # Testing phase
            "unit_tests",
            "integration_tests",
            "security_audit",
            
            # Documentation phase
            "api_documentation",
            "user_guide"
        ],
        agent_names=["Athena", "Cato", "Zephyr"],
        problem_statement="Build secure user authentication with intuitive UI"
    )
    
    # 2. Set task types for personality matching
    task_types = {
        # Design - Athena excels here
        "architecture_design": "architecture",
        "database_schema": "design",
        "api_design": "design",
        "ui_mockups": "creative",  # Zephyr can help
        
        # Implementation - Cato's domain
        "implement_auth_service": "implementation",
        "implement_user_model": "implementation",
        "implement_api_endpoints": "implementation",
        "implement_login_ui": "implementation",
        "implement_signup_ui": "implementation",
        
        # Testing - Cato excels
        "unit_tests": "testing",
        "integration_tests": "testing",
        "security_audit": "review",
        
        # Documentation - Athena's planning strength
        "api_documentation": "planning",
        "user_guide": "creative"
    }
    
    for task_id, task_type in task_types.items():
        orchestrator.tasks[task_id].task_type = task_type
    
    # 3. Set realistic dependencies
    # Implementation depends on design
    orchestrator.tasks["implement_auth_service"].dependencies = ["architecture_design"]
    orchestrator.tasks["implement_user_model"].dependencies = ["database_schema"]
    orchestrator.tasks["implement_api_endpoints"].dependencies = [
        "api_design",
        "implement_auth_service",
        "implement_user_model"
    ]
    orchestrator.tasks["implement_login_ui"].dependencies = [
        "ui_mockups",
        "implement_api_endpoints"
    ]
    orchestrator.tasks["implement_signup_ui"].dependencies = [
        "ui_mockups",
        "implement_api_endpoints"
    ]
    
    # Testing depends on implementation
    orchestrator.tasks["unit_tests"].dependencies = [
        "implement_auth_service",
        "implement_user_model"
    ]
    orchestrator.tasks["integration_tests"].dependencies = [
        "implement_api_endpoints",
        "implement_login_ui",
        "implement_signup_ui"
    ]
    orchestrator.tasks["security_audit"].dependencies = ["integration_tests"]
    
    # Documentation depends on completion
    orchestrator.tasks["api_documentation"].dependencies = ["implement_api_endpoints"]
    orchestrator.tasks["user_guide"].dependencies = [
        "implement_login_ui",
        "implement_signup_ui"
    ]
    
    # 4. Execute complete workflow
    print("Starting authentication feature development...")
    result = orchestrator.complete_workflow()
    
    # 5. Analyze results
    print(f"\n{'='*60}")
    print("Authentication Feature - Complete!")
    print(f"{'='*60}")
    
    print(f"\nExecution Summary:")
    print(f"  ✓ Tasks completed: {result['tasks_completed']}/{len(orchestrator.tasks)}")
    print(f"  ✓ Execution time: {result['total_time_ms']:.2f}ms")
    
    print(f"\nAgent Contributions:")
    for agent, count in result['execution_results']['agent_assignments'].items():
        print(f"  {agent}: {count} tasks")
    
    print(f"\nCollaboration Metrics:")
    print(f"  Ideas generated: {result['brainstorm_results']['total_ideas']}")
    print(f"  Synthesis count: {result['synthesis_results'].get('synthesis_count', 0)}")
    
    print(f"\nQuality Metrics:")
    avg = result['evaluation_results'].get('average', {})
    print(f"  Quality: {avg.get('quality', 0):.2f}")
    print(f"  Feasibility: {avg.get('feasibility', 0):.2f}")
    
    # 6. Save state for later analysis
    import json
    state = orchestrator.to_dict()
    with open('auth_feature_state.json', 'w') as f:
        json.dump(state, f, indent=2)
    print(f"\n✓ Workflow state saved to auth_feature_state.json")
    
    return orchestrator, result

# Run the example
if __name__ == "__main__":
    orchestrator, result = build_authentication_feature()
```

**Expected Output:**
```
Starting authentication feature development...

============================================================
Authentication Feature - Complete!
============================================================

Execution Summary:
  ✓ Tasks completed: 14/14
  ✓ Execution time: 45.23ms

Agent Contributions:
  Athena: 4 tasks
  Cato: 8 tasks
  Zephyr: 2 tasks

Collaboration Metrics:
  Ideas generated: 3
  Synthesis count: 1

Quality Metrics:
  Quality: 0.76
  Feasibility: 0.85

✓ Workflow state saved to auth_feature_state.json
```

---

## Performance Optimization

Tips for building high-performance workflows.

### Benchmark Your Workflow

```python
from src.benchmarks.performance import BenchmarkSuite
import time

suite = BenchmarkSuite()

# Benchmark your workflow at different scales
start = time.time()
result = suite.run_benchmark(
    benchmark_name="my_workflow",
    task_count=20,
    agent_names=["Athena", "Cato", "Zephyr"]
)
end = time.time()

print(f"Execution time: {result.execution_time_ms:.2f}ms")
print(f"Throughput: {result.tasks_per_second:.2f} tasks/sec")
print(f"Memory: {result.memory_usage_mb:.2f}MB")
```

### Optimize Task Structure

**Good**: Balanced dependency tree
```python
# This is efficient
orchestrator.tasks["task2"].dependencies = ["task1"]
orchestrator.tasks["task3"].dependencies = ["task1"]
orchestrator.tasks["task4"].dependencies = ["task2", "task3"]
```

**Bad**: Deep linear chain
```python
# This is slower
orchestrator.tasks["task2"].dependencies = ["task1"]
orchestrator.tasks["task3"].dependencies = ["task2"]
orchestrator.tasks["task4"].dependencies = ["task3"]
# ... 50 more levels
```

### Use Appropriate Agent Count

```python
# For 10-30 tasks: 2-3 agents is optimal
# For 50+ tasks: 3-5 agents recommended

# Don't over-provision
create_workflow_from_tasks(
    task_ids=list(range(10)),
    agent_names=["Athena", "Cato"],  # ✓ Good for 10 tasks
    # agent_names=["Athena", "Cato", "Zephyr", "Agent4", "Agent5"],  # ✗ Overkill
    problem_statement="..."
)
```

---

## Best Practices

### 1. Use Descriptive Task IDs

```python
# Good
task_ids = [
    "design_database_schema",
    "implement_user_authentication",
    "write_integration_tests"
]

# Bad
task_ids = ["task1", "task2", "task3"]
```

### 2. Set Appropriate Task Types

```python
# Match task types to agent strengths
type_mapping = {
    "architecture": "Athena will love this",
    "implementation": "Perfect for Cato",
    "creative": "Zephyr excels here",
    "testing": "Cato's specialty",
    "planning": "Athena's strength"
}
```

### 3. Use All Three Archetypes

```python
# Balanced team
agent_names = ["Athena", "Cato", "Zephyr"]  # ✓ Good variety

# Imbalanced
agent_names = ["Athena", "Athena"]  # ✗ Lacks diversity
```

### 4. Validate Dependencies

```python
# Check for cycles before executing
from src.core.topological_sort import topological_sort

try:
    task_graph = {
        task_id: task.dependencies
        for task_id, task in orchestrator.tasks.items()
    }
    order = topological_sort(task_graph)
    print(f"✓ Valid dependency graph: {len(order)} tasks")
except ValueError as e:
    print(f"✗ Cycle detected: {e}")
```

### 5. Use Brainstorming for Complex Problems

```python
# For complex, creative problems
orchestrator.run_brainstorm_phase(turns_per_agent=5)  # More ideas

# For simple, well-defined problems
orchestrator.run_brainstorm_phase(turns_per_agent=1)  # Quick ideation
```

### 6. Monitor Performance

```python
result = orchestrator.complete_workflow()

# Check if meeting targets
if result['total_time_ms'] > 1000:  # 1 second target
    print(f"⚠ Slow execution: {result['total_time_ms']:.2f}ms")
    print(f"Consider: reducing brainstorm turns, simplifying dependencies")
```

### 7. Save Important States

```python
import json

# Save workflow state at key points
state = orchestrator.to_dict()
with open(f"workflow_{orchestrator.workflow_id}_state.json", 'w') as f:
    json.dump(state, f, indent=2)
```

---

## Next Steps

1. **Explore Real-World Scenarios**: See `src/scenarios/real_world.py` for complete examples
2. **Run Benchmarks**: Use `src/benchmarks/performance.py` to measure your workflows
3. **Read API Reference**: Check `docs/API_REFERENCE.md` for complete API documentation
4. **Study Architecture**: Review `docs/ARCHITECTURE.md` for system design
5. **Run Tests**: Execute `pytest` to see 397 tests demonstrating all features

---

**Happy Multi-Agent Workflow Building!** 🎉
