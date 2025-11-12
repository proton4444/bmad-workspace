"""
FastAPI Web API for multi-agent workflow system.

Provides REST endpoints for:
- Workflow management (create, list, get, delete)
- Workflow execution (start, monitor, results)
- Agent management (list, details)
- Persistence (save, load, export)
- Health and metrics
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.agents.personality import (
    ARCHITECT_PERSONALITY,
    EXECUTOR_PERSONALITY,
    EXPERIMENTER_PERSONALITY,
)
from src.orchestration.workflow import (
    WorkflowOrchestrator,
    create_workflow_from_tasks,
)
from src.persistence.workflow_storage import WorkflowStorage

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Workflow API",
    description="REST API for managing and executing multi-agent workflows",
    version="1.0.0",
)

# Global state management
workflows: Dict[str, WorkflowOrchestrator] = {}
storage = WorkflowStorage(storage_dir="api_workflows")

# ============================================================================
# Pydantic Models
# ============================================================================


class TaskInput(BaseModel):
    """Task definition for workflow creation."""

    id: str
    name: str
    description: str
    task_type: str = "implementation"
    complexity: str = "moderate"
    dependencies: List[str] = []


class WorkflowCreateRequest(BaseModel):
    """Request to create a new workflow."""

    workflow_id: str
    name: str
    description: str
    task_ids: List[str]
    agent_names: List[str]
    problem_statement: str
    tasks: Optional[List[TaskInput]] = None


class WorkflowResponse(BaseModel):
    """Response containing workflow information."""

    workflow_id: str
    name: str
    description: str
    current_phase: str
    task_count: int
    agent_count: int
    created_at: str
    completed_at: Optional[str]


class TaskResponse(BaseModel):
    """Response containing task information."""

    id: str
    name: str
    description: str
    task_type: str
    complexity: str
    status: str
    dependencies: List[str]
    assigned_agent: Optional[str]
    result: Optional[str]
    execution_time_ms: float


class AgentResponse(BaseModel):
    """Response containing agent information."""

    name: str
    role: str
    traits: List[str]


class ExecutionResult(BaseModel):
    """Result from workflow execution."""

    workflow_id: str
    total_time_ms: float
    tasks_completed: int
    phases_completed: int
    ideas_generated: int
    brainstorm_results: Dict[str, Any]
    synthesis_results: Dict[str, Any]
    evaluation_results: Dict[str, Any]


class WorkflowSaveRequest(BaseModel):
    """Request to save a workflow."""

    filename: Optional[str] = None
    tags: Optional[List[str]] = None


class WorkflowLoadRequest(BaseModel):
    """Request to load a workflow."""

    filepath: str


class WorkflowListResponse(BaseModel):
    """Response for workflow list."""

    total: int
    workflows: List[WorkflowResponse]


class MetricsResponse(BaseModel):
    """System metrics response."""

    timestamp: str
    active_workflows: int
    total_workflows: int
    total_tasks_completed: int
    average_execution_time_ms: float


# ============================================================================
# Health & System Endpoints
# ============================================================================


@app.get("/health", tags=["System"])
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_workflows": len(workflows),
        "version": "1.0.0",
    }


@app.get("/metrics", tags=["System"], response_model=MetricsResponse)
async def get_metrics():
    """Get system metrics."""
    total_time = sum(wf.metrics.get("total_time_ms", 0) for wf in workflows.values())
    tasks_completed = sum(
        len([t for t in wf.tasks.values() if t.status == "completed"])
        for wf in workflows.values()
    )
    avg_time = total_time / len(workflows) if workflows else 0

    return MetricsResponse(
        timestamp=datetime.now().isoformat(),
        active_workflows=len(workflows),
        total_workflows=len(storage.list_workflows()),
        total_tasks_completed=tasks_completed,
        average_execution_time_ms=avg_time,
    )


# ============================================================================
# Workflow Management Endpoints
# ============================================================================


@app.post("/workflows", tags=["Workflows"], response_model=WorkflowResponse)
async def create_workflow(request: WorkflowCreateRequest):
    """Create a new workflow.

    Args:
        request: Workflow creation parameters

    Returns:
        Created workflow details
    """
    if request.workflow_id in workflows:
        raise HTTPException(
            status_code=400, detail=f"Workflow {request.workflow_id} already exists"
        )

    # Create workflow
    orchestrator = create_workflow_from_tasks(
        workflow_id=request.workflow_id,
        task_ids=request.task_ids,
        agent_names=request.agent_names,
        problem_statement=request.problem_statement,
        workflow_name=request.name,
    )

    # Update task details if provided
    if request.tasks:
        for task_input in request.tasks:
            if task_input.id in orchestrator.tasks:
                task = orchestrator.tasks[task_input.id]
                task.name = task_input.name
                task.description = task_input.description
                task.task_type = task_input.task_type
                task.complexity = task_input.complexity
                task.dependencies = task_input.dependencies

    # Store workflow
    workflows[request.workflow_id] = orchestrator

    return WorkflowResponse(
        workflow_id=orchestrator.workflow_id,
        name=orchestrator.name,
        description=orchestrator.description,
        current_phase=orchestrator.current_phase.value,
        task_count=len(orchestrator.tasks),
        agent_count=len(orchestrator.agents),
        created_at=orchestrator.created_at,
        completed_at=orchestrator.completed_at,
    )


@app.get("/workflows", tags=["Workflows"], response_model=WorkflowListResponse)
async def list_workflows(
    skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)
):
    """List all workflows.

    Args:
        skip: Number of workflows to skip
        limit: Maximum number to return

    Returns:
        List of workflow details
    """
    workflow_list = list(workflows.values())[skip : skip + limit]

    return WorkflowListResponse(
        total=len(workflows),
        workflows=[
            WorkflowResponse(
                workflow_id=wf.workflow_id,
                name=wf.name,
                description=wf.description,
                current_phase=wf.current_phase.value,
                task_count=len(wf.tasks),
                agent_count=len(wf.agents),
                created_at=wf.created_at,
                completed_at=wf.completed_at,
            )
            for wf in workflow_list
        ],
    )


@app.get("/workflows/saved", tags=["Workflows"])
async def list_saved_workflows(tags: Optional[List[str]] = Query(None)):
    """List saved workflows on disk.

    Args:
        tags: Optional tags to filter by

    Returns:
        List of saved workflows
    """
    workflows_list = storage.list_workflows(tags=tags)
    return {
        "total": len(workflows_list),
        "workflows": workflows_list,
    }


@app.get(
    "/workflows/{workflow_id}", tags=["Workflows"], response_model=WorkflowResponse
)
async def get_workflow(workflow_id: str):
    """Get workflow details.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Workflow details
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    wf = workflows[workflow_id]
    return WorkflowResponse(
        workflow_id=wf.workflow_id,
        name=wf.name,
        description=wf.description,
        current_phase=wf.current_phase.value,
        task_count=len(wf.tasks),
        agent_count=len(wf.agents),
        created_at=wf.created_at,
        completed_at=wf.completed_at,
    )


@app.get("/workflows/{workflow_id}/tasks", tags=["Workflows"])
async def get_workflow_tasks(workflow_id: str) -> List[TaskResponse]:
    """Get all tasks in a workflow.

    Args:
        workflow_id: Workflow identifier

    Returns:
        List of task details
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    wf = workflows[workflow_id]
    return [
        TaskResponse(
            id=task.id,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            complexity=task.complexity,
            status=task.status,
            dependencies=task.dependencies,
            assigned_agent=task.assigned_agent,
            result=task.result,
            execution_time_ms=task.execution_time_ms,
        )
        for task in wf.tasks.values()
    ]


@app.get("/workflows/{workflow_id}/agents", tags=["Workflows"])
async def get_workflow_agents(workflow_id: str) -> List[AgentResponse]:
    """Get all agents in a workflow.

    Args:
        workflow_id: Workflow identifier

    Returns:
        List of agent details
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    wf = workflows[workflow_id]
    return [
        AgentResponse(
            name=name,
            role=personality.role.value,
            traits=personality.traits,
        )
        for name, (_, personality, _) in wf.agents.items()
    ]


@app.delete("/workflows/{workflow_id}", tags=["Workflows"])
async def delete_workflow(workflow_id: str):
    """Delete a workflow.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Success message
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    del workflows[workflow_id]
    return {"message": f"Workflow {workflow_id} deleted"}


# ============================================================================
# Workflow Execution Endpoints
# ============================================================================


@app.post(
    "/workflows/{workflow_id}/execute",
    tags=["Execution"],
    response_model=ExecutionResult,
)
async def execute_workflow(workflow_id: str):
    """Execute a workflow end-to-end.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Execution results
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    orchestrator = workflows[workflow_id]
    result = orchestrator.complete_workflow()

    return ExecutionResult(
        workflow_id=workflow_id,
        total_time_ms=result.get("total_time_ms", 0),
        tasks_completed=result.get("tasks_completed", 0),
        phases_completed=result.get("phases_completed", 0),
        ideas_generated=len(orchestrator.context.ideas),
        brainstorm_results=result.get("brainstorm_results", {}),
        synthesis_results=result.get("synthesis_results", {}),
        evaluation_results=result.get("evaluation_results", {}),
    )


@app.post("/workflows/{workflow_id}/brainstorm", tags=["Execution"])
async def brainstorm_phase(workflow_id: str, turns_per_agent: int = 2):
    """Run brainstorming phase for a workflow.

    Args:
        workflow_id: Workflow identifier
        turns_per_agent: Number of turns per agent

    Returns:
        Brainstorming results
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    orchestrator = workflows[workflow_id]
    result = orchestrator.run_brainstorm_phase(turns_per_agent=turns_per_agent)

    return {
        "workflow_id": workflow_id,
        "ideas_generated": result.get("total_ideas", 0),
        "turn_count": result.get("turn_count", 0),
        "agents_participated": result.get("agents_participated", []),
    }


@app.post("/workflows/{workflow_id}/execute-tasks", tags=["Execution"])
async def execute_tasks(workflow_id: str):
    """Execute task assignment and execution phase.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Execution results
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    orchestrator = workflows[workflow_id]
    result = orchestrator.execute_workflow()

    return {
        "workflow_id": workflow_id,
        "tasks_completed": result.get("tasks_completed", 0),
        "total_time_ms": result.get("total_time_ms", 0),
        "execution_results": result.get("execution_results", {}),
    }


@app.get("/workflows/{workflow_id}/results", tags=["Execution"])
async def get_execution_results(workflow_id: str):
    """Get execution results and state.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Complete workflow state and results
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    orchestrator = workflows[workflow_id]
    return orchestrator.to_dict()


# ============================================================================
# Persistence Endpoints
# ============================================================================


@app.post("/workflows/{workflow_id}/save", tags=["Persistence"])
async def save_workflow(workflow_id: str, request: WorkflowSaveRequest):
    """Save a workflow to disk.

    Args:
        workflow_id: Workflow identifier
        request: Save parameters (filename, tags)

    Returns:
        Save confirmation with filepath
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    orchestrator = workflows[workflow_id]
    filepath = storage.save_workflow(
        orchestrator,
        filename=request.filename,
        tags=request.tags,
    )

    return {
        "workflow_id": workflow_id,
        "filepath": filepath,
        "message": f"Workflow saved to {filepath}",
    }


@app.post("/workflows/load", tags=["Persistence"], response_model=WorkflowResponse)
async def load_workflow(request: WorkflowLoadRequest):
    """Load a workflow from disk.

    Args:
        request: Load parameters (filepath)

    Returns:
        Loaded workflow details
    """
    try:
        orchestrator = storage.load_workflow(request.filepath)
        workflows[orchestrator.workflow_id] = orchestrator

        return WorkflowResponse(
            workflow_id=orchestrator.workflow_id,
            name=orchestrator.name,
            description=orchestrator.description,
            current_phase=orchestrator.current_phase.value,
            task_count=len(orchestrator.tasks),
            agent_count=len(orchestrator.agents),
            created_at=orchestrator.created_at,
            completed_at=orchestrator.completed_at,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Workflow file not found: {request.filepath}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid workflow file: {str(e)}")


@app.get("/workflows/{workflow_id}/versions", tags=["Persistence"])
async def get_workflow_versions(workflow_id: str):
    """Get all saved versions of a workflow.

    Args:
        workflow_id: Workflow identifier

    Returns:
        List of versions with metadata
    """
    versions = storage.get_workflow_versions(workflow_id)
    return {
        "workflow_id": workflow_id,
        "total_versions": len(versions),
        "versions": versions,
    }


@app.post("/workflows/{workflow_id}/export", tags=["Persistence"])
async def export_workflow_report(workflow_id: str):
    """Export comprehensive workflow report.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Complete workflow report
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    orchestrator = workflows[workflow_id]
    report = storage.export_workflow_report(orchestrator, include_results=True)

    return report


# ============================================================================
# Agent Information Endpoints
# ============================================================================


@app.get("/agents", tags=["Agents"])
async def list_agents():
    """List all available agent archetypes.

    Returns:
        Available agents with their characteristics
    """
    return {
        "total": 3,
        "agents": [
            {
                "name": "Athena",
                "role": "Architect",
                "description": "Strategic thinker and systems designer",
                "traits": ARCHITECT_PERSONALITY.traits,
                "affinities": {
                    "architecture": 0.95,
                    "design": 0.90,
                    "planning": 0.85,
                },
            },
            {
                "name": "Cato",
                "role": "Executor",
                "description": "Pragmatic implementer focused on delivery",
                "traits": EXECUTOR_PERSONALITY.traits,
                "affinities": {
                    "implementation": 1.0,
                    "testing": 0.85,
                    "review": 0.70,
                },
            },
            {
                "name": "Zephyr",
                "role": "Experimenter",
                "description": "Creative innovator and boundary-pusher",
                "traits": EXPERIMENTER_PERSONALITY.traits,
                "affinities": {
                    "creative": 0.95,
                    "design": 0.75,
                    "architecture": 0.60,
                },
            },
        ],
    }


@app.get("/agents/{agent_name}", tags=["Agents"])
async def get_agent(agent_name: str):
    """Get details for a specific agent.

    Args:
        agent_name: Agent name (Athena, Cato, or Zephyr)

    Returns:
        Agent details and characteristics
    """
    agents_map = {
        "athena": ("Architect", ARCHITECT_PERSONALITY),
        "cato": ("Executor", EXECUTOR_PERSONALITY),
        "zephyr": ("Experimenter", EXPERIMENTER_PERSONALITY),
    }

    agent_key = agent_name.lower()
    if agent_key not in agents_map:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_name} not found. Available: Athena, Cato, Zephyr",
        )

    role, personality = agents_map[agent_key]
    return {
        "name": agent_name,
        "role": role,
        "traits": personality.traits,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
