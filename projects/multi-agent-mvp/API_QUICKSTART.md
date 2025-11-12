# Web API Quick Start

## 1. Start the Server

```bash
cd multi-agent-mvp
python -m src.api.app
```

Server runs at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## 2. Create a Workflow

```bash
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "quickstart",
    "name": "Quick Start Project",
    "description": "Quick start demo",
    "task_ids": ["task1", "task2"],
    "agent_names": ["Athena", "Cato"],
    "problem_statement": "Build something awesome"
  }'
```

Response:
```json
{
  "workflow_id": "quickstart",
  "name": "Quick Start Project",
  "current_phase": "planning",
  "task_count": 2,
  "agent_count": 2,
  "created_at": "2024-01-15T10:30:00"
}
```

## 3. Execute the Workflow

```bash
curl -X POST http://localhost:8000/workflows/quickstart/execute
```

Response:
```json
{
  "workflow_id": "quickstart",
  "total_time_ms": 350.25,
  "tasks_completed": 2,
  "phases_completed": 6,
  "ideas_generated": 12,
  "brainstorm_results": {...},
  "synthesis_results": {...},
  "evaluation_results": {...}
}
```

## 4. Get Results

```bash
curl http://localhost:8000/workflows/quickstart/results
```

## 5. Save the Workflow

```bash
curl -X POST http://localhost:8000/workflows/quickstart/save \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["completed"]
  }'
```

Response:
```json
{
  "workflow_id": "quickstart",
  "filepath": "/path/to/api_workflows/quickstart.json",
  "message": "Workflow saved"
}
```

## 6. List Agents

```bash
curl http://localhost:8000/agents
```

Response shows all 3 agents:
- **Athena**: Architect (strategic thinking)
- **Cato**: Executor (pragmatic delivery)
- **Zephyr**: Experimenter (creative innovation)

## 7. Check Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "active_workflows": 1,
  "version": "1.0.0"
}
```

## Python Example

```python
import requests

api = "http://localhost:8000"

# Create
wf = requests.post(f"{api}/workflows", json={
    "workflow_id": "python_test",
    "name": "Python Test",
    "description": "Testing from Python",
    "task_ids": ["t1", "t2", "t3"],
    "agent_names": ["Athena", "Cato", "Zephyr"],
    "problem_statement": "Test workflow"
}).json()

# Execute
result = requests.post(f"{api}/workflows/{wf['workflow_id']}/execute").json()
print(f"✓ Completed {result['tasks_completed']} tasks")
print(f"✓ Generated {result['ideas_generated']} ideas")
print(f"✓ Total time: {result['total_time_ms']:.1f}ms")

# Save
save = requests.post(
    f"{api}/workflows/{wf['workflow_id']}/save",
    json={"tags": ["python", "demo"]}
).json()
print(f"✓ Saved to: {save['filepath']}")

# List saved
saved = requests.get(f"{api}/workflows/saved").json()
print(f"✓ Total saved workflows: {saved['total']}")
```

## API Structure

```
GET  /health                           # Health check
GET  /metrics                          # System metrics

POST /workflows                        # Create workflow
GET  /workflows                        # List workflows
GET  /workflows/saved                  # List saved
GET  /workflows/{id}                   # Get workflow
GET  /workflows/{id}/tasks             # Get tasks
GET  /workflows/{id}/agents            # Get agents
DELETE /workflows/{id}                 # Delete

POST /workflows/{id}/execute           # Full execution
POST /workflows/{id}/brainstorm        # Brainstorm phase
POST /workflows/{id}/execute-tasks     # Execute tasks
GET  /workflows/{id}/results           # Get results

POST /workflows/{id}/save              # Save to disk
POST /workflows/load                   # Load from disk
GET  /workflows/{id}/versions          # Get versions
POST /workflows/{id}/export            # Export report

GET  /agents                           # List agents
GET  /agents/{name}                    # Get agent
```

## Key Features

✅ **Complete Workflow Management** - Create, execute, and manage workflows  
✅ **3 Agent Archetypes** - Athena (Architect), Cato (Executor), Zephyr (Experimenter)  
✅ **Persistence** - Save/load workflows with versioning  
✅ **Comprehensive Execution** - 5-phase workflow (planning → ideation → execution → synthesis → evaluation)  
✅ **Real-time Monitoring** - Track tasks, ideas, and metrics  
✅ **Error Handling** - Clear error messages and HTTP status codes  

## Next Steps

1. Read the full **[API Guide](docs/API_GUIDE.md)** for detailed documentation
2. Try the **[Interactive API Docs](http://localhost:8000/docs)** for live testing
3. Run the **tests**: `pytest tests/test_api.py -v`
4. Explore the **[Swagger UI](http://localhost:8000/docs)** for all endpoints

## Troubleshooting

**"Cannot connect to localhost:8000"**
- Make sure the server is running: `python -m src.api.app`
- Check if port 8000 is available

**"Module not found" errors**
- Install dependencies: `pip install -r requirements.txt`

**Workflow not found**
- Workflows are stored in memory; they're lost on server restart
- Save workflows to disk before restarting: `POST /workflows/{id}/save`
- Load them back with: `POST /workflows/load`

## API Response Times

- Create workflow: ~10ms
- Execute (3 tasks): ~200-500ms
- Save: ~5-10ms
- Load: ~3-5ms
- List: <5ms

## Support

- Full API docs: `/docs` (Swagger UI)
- Advanced guide: `docs/API_GUIDE.md`
- Source code: `src/api/app.py`
- Tests: `tests/test_api.py`
