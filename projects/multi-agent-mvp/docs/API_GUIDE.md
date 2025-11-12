# Multi-Agent Workflow API Guide

## Overview

The Multi-Agent Workflow API provides REST endpoints for managing and executing multi-agent workflows. Built with FastAPI, it offers:

- ✅ Complete workflow lifecycle management
- ✅ Real-time execution monitoring
- ✅ Persistence and versioning
- ✅ Agent information and configuration
- ✅ Health checks and metrics

## Getting Started

### Installation

```bash
pip install fastapi uvicorn pydantic python-multipart httpx
```

### Starting the Server

```bash
python -m src.api.app
# or
uvicorn src.api.app:app --reload
```

Server runs at `http://localhost:8000`

API docs available at `http://localhost:8000/docs`

## API Endpoints

### Health & System

#### Health Check
```
GET /health
```

Returns API health status and version.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "active_workflows": 2,
  "version": "1.0.0"
}
```

#### System Metrics
```
GET /metrics
```

Returns system performance metrics.

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "active_workflows": 2,
  "total_workflows": 5,
  "total_tasks_completed": 15,
  "average_execution_time_ms": 250.5
}
```

### Workflow Management

#### Create Workflow
```
POST /workflows
```

Create a new workflow.

**Request Body:**
```json
{
  "workflow_id": "my_project",
  "name": "My Project",
  "description": "Project description",
  "task_ids": ["task1", "task2", "task3"],
  "agent_names": ["Athena", "Cato", "Zephyr"],
  "problem_statement": "What should we build?",
  "tasks": [
    {
      "id": "task1",
      "name": "Design",
      "description": "Architecture design",
      "task_type": "architecture",
      "complexity": "complex",
      "dependencies": []
    }
  ]
}
```

**Response:**
```json
{
  "workflow_id": "my_project",
  "name": "My Project",
  "description": "Project description",
  "current_phase": "planning",
  "task_count": 3,
  "agent_count": 3,
  "created_at": "2024-01-15T10:30:00.000Z",
  "completed_at": null
}
```

#### List Workflows
```
GET /workflows?skip=0&limit=10
```

List all workflows with pagination.

**Query Parameters:**
- `skip` (int, default=0): Number to skip
- `limit` (int, default=10): Max results (1-100)

**Response:**
```json
{
  "total": 5,
  "workflows": [
    {
      "workflow_id": "project1",
      "name": "Project 1",
      "description": "...",
      "current_phase": "complete",
      "task_count": 5,
      "agent_count": 2,
      "created_at": "2024-01-15T10:30:00.000Z",
      "completed_at": "2024-01-15T10:35:00.000Z"
    }
  ]
}
```

#### Get Workflow
```
GET /workflows/{workflow_id}
```

Get details for a specific workflow.

**Response:**
```json
{
  "workflow_id": "my_project",
  "name": "My Project",
  "description": "Project description",
  "current_phase": "planning",
  "task_count": 3,
  "agent_count": 3,
  "created_at": "2024-01-15T10:30:00.000Z",
  "completed_at": null
}
```

#### Get Workflow Tasks
```
GET /workflows/{workflow_id}/tasks
```

Get all tasks in a workflow.

**Response:**
```json
[
  {
    "id": "task1",
    "name": "Design",
    "description": "Architecture design",
    "task_type": "architecture",
    "complexity": "complex",
    "status": "pending",
    "dependencies": [],
    "assigned_agent": null,
    "result": null,
    "execution_time_ms": 0
  }
]
```

#### Get Workflow Agents
```
GET /workflows/{workflow_id}/agents
```

Get all agents in a workflow.

**Response:**
```json
[
  {
    "name": "Athena",
    "role": "Architect",
    "traits": ["strategic", "analytical", "creative"]
  },
  {
    "name": "Cato",
    "role": "Executor",
    "traits": ["pragmatic", "focused", "disciplined"]
  }
]
```

#### Delete Workflow
```
DELETE /workflows/{workflow_id}
```

Delete a workflow from memory.

**Response:**
```json
{
  "message": "Workflow my_project deleted"
}
```

### Workflow Execution

#### Run Brainstorming
```
POST /workflows/{workflow_id}/brainstorm?turns_per_agent=2
```

Run collaborative brainstorming phase.

**Query Parameters:**
- `turns_per_agent` (int, default=2): Turns per agent

**Response:**
```json
{
  "workflow_id": "my_project",
  "ideas_generated": 12,
  "turn_count": 6,
  "agents_participated": ["Athena", "Cato", "Zephyr"]
}
```

#### Execute Tasks
```
POST /workflows/{workflow_id}/execute-tasks
```

Execute task assignment and execution phase.

**Response:**
```json
{
  "workflow_id": "my_project",
  "tasks_completed": 3,
  "total_time_ms": 150.25,
  "execution_results": {
    "task_assignments": {
      "task1": "Athena",
      "task2": "Cato",
      "task3": "Zephyr"
    },
    "completion_order": ["task1", "task2", "task3"]
  }
}
```

#### Full Workflow Execution
```
POST /workflows/{workflow_id}/execute
```

Execute complete 5-phase workflow.

**Response:**
```json
{
  "workflow_id": "my_project",
  "total_time_ms": 500.50,
  "tasks_completed": 3,
  "phases_completed": 6,
  "ideas_generated": 18,
  "brainstorm_results": {
    "total_ideas": 18,
    "turn_count": 6
  },
  "synthesis_results": {
    "synthesized_ideas": 3,
    "lineage_paths": [...]
  },
  "evaluation_results": {
    "quality_scores": {...},
    "coherence_score": 0.85
  }
}
```

#### Get Execution Results
```
GET /workflows/{workflow_id}/results
```

Get complete workflow state and results.

**Response:**
```json
{
  "workflow_id": "my_project",
  "name": "My Project",
  "tasks": {...},
  "agents": {...},
  "context": {...},
  "metrics": {...}
}
```

### Persistence

#### Save Workflow
```
POST /workflows/{workflow_id}/save
```

Save workflow to disk.

**Request Body:**
```json
{
  "filename": "my_workflow.json",
  "tags": ["completed", "production"]
}
```

**Response:**
```json
{
  "workflow_id": "my_project",
  "filepath": "/path/to/api_workflows/my_workflow.json",
  "message": "Workflow saved to /path/to/api_workflows/my_workflow.json"
}
```

#### Load Workflow
```
POST /workflows/load
```

Load workflow from disk.

**Request Body:**
```json
{
  "filepath": "/path/to/api_workflows/my_workflow.json"
}
```

**Response:**
```json
{
  "workflow_id": "my_project",
  "name": "My Project",
  "description": "Project description",
  "current_phase": "complete",
  "task_count": 3,
  "agent_count": 3,
  "created_at": "2024-01-15T10:30:00.000Z",
  "completed_at": "2024-01-15T10:35:00.000Z"
}
```

#### List Saved Workflows
```
GET /workflows/saved?tags=completed
```

List workflows saved to disk.

**Query Parameters:**
- `tags` (list[str]): Filter by tags

**Response:**
```json
{
  "total": 3,
  "workflows": [
    {
      "workflow_id": "my_project",
      "name": "My Project",
      "filename": "my_project.json",
      "saved_at": "2024-01-15T10:35:01.000Z",
      "tags": ["completed", "production"]
    }
  ]
}
```

#### Get Workflow Versions
```
GET /workflows/{workflow_id}/versions
```

Get version history of a workflow.

**Response:**
```json
{
  "workflow_id": "my_project",
  "total_versions": 2,
  "versions": [
    {
      "filename": "my_project_v1.json",
      "saved_at": "2024-01-15T10:30:00.000Z",
      "version": "1.0",
      "tags": ["draft"]
    },
    {
      "filename": "my_project_v2.json",
      "saved_at": "2024-01-15T10:35:00.000Z",
      "version": "1.0",
      "tags": ["completed"]
    }
  ]
}
```

#### Export Workflow Report
```
POST /workflows/{workflow_id}/export
```

Export comprehensive workflow report.

**Response:**
```json
{
  "workflow_info": {
    "id": "my_project",
    "name": "My Project",
    "description": "...",
    "created_at": "2024-01-15T10:30:00.000Z",
    "completed_at": "2024-01-15T10:35:00.000Z",
    "current_phase": "complete"
  },
  "tasks": {
    "task1": {
      "name": "Design",
      "type": "architecture",
      "complexity": "complex",
      "status": "completed",
      "dependencies": [],
      "assigned_agent": "Athena",
      "execution_time_ms": 150
    }
  },
  "agents": {
    "Athena": {
      "personality": "Architect",
      "traits": ["strategic", "analytical"]
    }
  },
  "collaboration": {
    "ideas_generated": 18,
    "participating_agents": ["Athena", "Cato", "Zephyr"]
  },
  "metrics": {
    "total_time_ms": 500.50,
    "tasks_completed": 3,
    "phases_completed": 6
  },
  "results": {
    "total_time_ms": 500.50,
    "tasks_completed": 3,
    "phases_completed": 6
  }
}
```

### Agent Information

#### List Agents
```
GET /agents
```

List all available agents.

**Response:**
```json
{
  "total": 3,
  "agents": [
    {
      "name": "Athena",
      "role": "Architect",
      "description": "Strategic thinker and systems designer",
      "traits": ["strategic", "analytical", "creative"],
      "affinities": {
        "architecture": 0.95,
        "design": 0.90,
        "planning": 0.85
      }
    },
    {
      "name": "Cato",
      "role": "Executor",
      "description": "Pragmatic implementer focused on delivery",
      "traits": ["pragmatic", "focused", "disciplined"],
      "affinities": {
        "implementation": 1.0,
        "testing": 0.85,
        "review": 0.70
      }
    },
    {
      "name": "Zephyr",
      "role": "Experimenter",
      "description": "Creative innovator and boundary-pusher",
      "traits": ["creative", "curious", "bold"],
      "affinities": {
        "creative": 0.95,
        "design": 0.75,
        "architecture": 0.60
      }
    }
  ]
}
```

#### Get Agent Details
```
GET /agents/{agent_name}
```

Get details for a specific agent.

**Response:**
```json
{
  "name": "Athena",
  "role": "Architect",
  "traits": ["strategic", "analytical", "creative"]
}
```

## Error Handling

All errors follow standard HTTP status codes:

- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

**Error Response Format:**
```json
{
  "detail": "Workflow not found"
}
```

## Examples

### Example 1: Complete Workflow Lifecycle

```bash
# 1. Create workflow
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "project_001",
    "name": "Web App",
    "description": "Build a web app",
    "task_ids": ["design", "implement", "test"],
    "agent_names": ["Athena", "Cato"],
    "problem_statement": "Create a new web application"
  }'

# 2. Execute workflow
curl -X POST http://localhost:8000/workflows/project_001/execute

# 3. Get results
curl http://localhost:8000/workflows/project_001/results

# 4. Save workflow
curl -X POST http://localhost:8000/workflows/project_001/save \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["completed", "production"]
  }'

# 5. List saved workflows
curl "http://localhost:8000/workflows/saved?tags=completed"
```

### Example 2: Custom Task Configuration

```bash
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "complex_project",
    "name": "Complex Project",
    "description": "Project with dependencies",
    "task_ids": ["design", "backend", "frontend", "test"],
    "agent_names": ["Athena", "Cato", "Zephyr"],
    "problem_statement": "Build complex system",
    "tasks": [
      {
        "id": "design",
        "name": "System Design",
        "description": "Design the architecture",
        "task_type": "architecture",
        "complexity": "complex",
        "dependencies": []
      },
      {
        "id": "backend",
        "name": "Backend Implementation",
        "description": "Implement backend",
        "task_type": "implementation",
        "complexity": "moderate",
        "dependencies": ["design"]
      },
      {
        "id": "frontend",
        "name": "Frontend Implementation",
        "description": "Implement frontend",
        "task_type": "implementation",
        "complexity": "moderate",
        "dependencies": ["design"]
      },
      {
        "id": "test",
        "name": "Testing",
        "description": "Write tests",
        "task_type": "testing",
        "complexity": "complex",
        "dependencies": ["backend", "frontend"]
      }
    ]
  }'
```

### Example 3: Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Create workflow
response = requests.post(
    f"{BASE_URL}/workflows",
    json={
        "workflow_id": "api_test",
        "name": "API Test",
        "description": "Testing API",
        "task_ids": ["t1", "t2"],
        "agent_names": ["Athena", "Cato"],
        "problem_statement": "Test"
    }
)
workflow = response.json()
print(f"Created: {workflow['workflow_id']}")

# Execute
response = requests.post(
    f"{BASE_URL}/workflows/{workflow['workflow_id']}/execute"
)
result = response.json()
print(f"Completed {result['tasks_completed']} tasks")

# Save
response = requests.post(
    f"{BASE_URL}/workflows/{workflow['workflow_id']}/save",
    json={"tags": ["api_test"]}
)
save_info = response.json()
print(f"Saved to: {save_info['filepath']}")

# List agents
response = requests.get(f"{BASE_URL}/agents")
agents = response.json()
for agent in agents["agents"]:
    print(f"- {agent['name']}: {agent['role']}")
```

## Performance

- **Create Workflow**: ~10ms
- **Execute Workflow** (3 tasks): ~200-500ms
- **Save Workflow**: ~5-10ms
- **Load Workflow**: ~3-5ms
- **List Workflows**: <5ms

## Testing

Run API tests:

```bash
pytest tests/test_api.py -v
```

36 comprehensive API tests covering:
- Health checks and metrics
- Workflow management
- Execution phases
- Persistence operations
- Agent information
- Error handling
- Integration scenarios

## Limitations & Future Enhancements

### Current Limitations
- In-memory workflow storage (lost on restart)
- Single-process execution
- No authentication/authorization
- No rate limiting

### Planned Enhancements
- Distributed execution
- WebSocket for real-time updates
- Authentication (OAuth2, API keys)
- Rate limiting and quotas
- Workflow scheduling
- Batch job monitoring
- Advanced filtering and search

## Support

For issues or questions:
1. Check the API docs at `/docs`
2. Review the examples above
3. Check test cases in `tests/test_api.py`
