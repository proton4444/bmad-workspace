"""
Tests for FastAPI Web API endpoints.

Coverage:
- Health checks and metrics
- Workflow management (create, list, get, delete)
- Workflow execution (brainstorm, execute, results)
- Persistence (save, load, list, export)
- Agent information
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

# Create test client
client = TestClient(app)


class TestHealthAndMetrics:
    """Test health check and metrics endpoints."""

    def test_health_check(self):
        """Health check returns status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "active_workflows" in data
        assert "version" in data

    def test_metrics_endpoint(self):
        """Metrics endpoint returns system metrics."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "active_workflows" in data
        assert "total_workflows" in data
        assert "total_tasks_completed" in data
        assert "average_execution_time_ms" in data


class TestWorkflowManagement:
    """Test workflow management endpoints."""

    @pytest.fixture
    def workflow_data(self):
        """Sample workflow creation data."""
        return {
            "workflow_id": "test_workflow_001",
            "name": "Test Workflow",
            "description": "Test workflow for API",
            "task_ids": ["task1", "task2", "task3"],
            "agent_names": ["Athena", "Cato"],
            "problem_statement": "Test problem",
        }

    def test_create_workflow(self, workflow_data):
        """Create a new workflow."""
        response = client.post("/workflows", json=workflow_data)
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == "test_workflow_001"
        assert data["name"] == "Test Workflow"
        assert data["task_count"] == 3
        assert data["agent_count"] == 2
        assert "current_phase" in data
        assert "created_at" in data

    def test_create_workflow_duplicate(self, workflow_data):
        """Creating duplicate workflow fails."""
        # Create first
        client.post("/workflows", json=workflow_data)

        # Try to create duplicate
        response = client.post("/workflows", json=workflow_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_list_workflows(self, workflow_data):
        """List all workflows."""
        # Create a workflow
        client.post("/workflows", json=workflow_data)

        # List workflows
        response = client.get("/workflows")
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "workflows" in data
        assert len(data["workflows"]) > 0

    def test_list_workflows_pagination(self, workflow_data):
        """List workflows with pagination."""
        # Create multiple workflows
        for i in range(5):
            workflow_data["workflow_id"] = f"workflow_{i}"
            client.post("/workflows", json=workflow_data)

        # List with limit
        response = client.get("/workflows?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) <= 2

    def test_get_workflow(self, workflow_data):
        """Get specific workflow."""
        # Create workflow
        client.post("/workflows", json=workflow_data)

        # Get it
        response = client.get(f"/workflows/{workflow_data['workflow_id']}")
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_data["workflow_id"]
        assert data["name"] == workflow_data["name"]

    def test_get_workflow_not_found(self):
        """Getting non-existent workflow returns 404."""
        response = client.get("/workflows/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_workflow_tasks(self, workflow_data):
        """Get all tasks in a workflow."""
        # Create workflow
        client.post("/workflows", json=workflow_data)

        # Get tasks
        response = client.get(f"/workflows/{workflow_data['workflow_id']}/tasks")
        assert response.status_code == 200
        tasks = response.json()

        assert len(tasks) == 3
        assert all("id" in task for task in tasks)
        assert all("name" in task for task in tasks)
        assert all("status" in task for task in tasks)

    def test_get_workflow_agents(self, workflow_data):
        """Get all agents in a workflow."""
        # Create workflow
        client.post("/workflows", json=workflow_data)

        # Get agents
        response = client.get(f"/workflows/{workflow_data['workflow_id']}/agents")
        assert response.status_code == 200
        agents = response.json()

        assert len(agents) == 2
        assert all("name" in agent for agent in agents)
        assert all("role" in agent for agent in agents)

    def test_delete_workflow(self, workflow_data):
        """Delete a workflow."""
        # Create workflow
        client.post("/workflows", json=workflow_data)

        # Delete it
        response = client.delete(f"/workflows/{workflow_data['workflow_id']}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

        # Verify it's gone
        response = client.get(f"/workflows/{workflow_data['workflow_id']}")
        assert response.status_code == 404


class TestWorkflowExecution:
    """Test workflow execution endpoints."""

    @pytest.fixture
    def workflow_for_execution(self):
        """Create a workflow for execution tests."""
        data = {
            "workflow_id": "exec_workflow",
            "name": "Execution Test",
            "description": "Test execution",
            "task_ids": ["t1", "t2"],
            "agent_names": ["Athena"],
            "problem_statement": "Test",
        }
        client.post("/workflows", json=data)
        return data["workflow_id"]

    def test_brainstorm_phase(self, workflow_for_execution):
        """Run brainstorming phase."""
        response = client.post(
            f"/workflows/{workflow_for_execution}/brainstorm",
            params={"turns_per_agent": 2},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_for_execution
        assert "ideas_generated" in data
        assert "turn_count" in data
        assert "agents_participated" in data

    def test_execute_tasks(self, workflow_for_execution):
        """Execute task phase."""
        response = client.post(f"/workflows/{workflow_for_execution}/execute-tasks")
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_for_execution
        assert "tasks_completed" in data
        assert "total_time_ms" in data
        assert "execution_results" in data

    def test_full_execution(self, workflow_for_execution):
        """Execute complete workflow."""
        response = client.post(f"/workflows/{workflow_for_execution}/execute")
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_for_execution
        assert "total_time_ms" in data
        assert "tasks_completed" in data
        assert "phases_completed" in data
        assert "ideas_generated" in data
        assert "brainstorm_results" in data
        assert "synthesis_results" in data
        assert "evaluation_results" in data

    def test_get_execution_results(self, workflow_for_execution):
        """Get execution results and state."""
        # Execute workflow
        client.post(f"/workflows/{workflow_for_execution}/execute")

        # Get results
        response = client.get(f"/workflows/{workflow_for_execution}/results")
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_for_execution
        assert "tasks" in data
        assert "agents" in data
        assert "context" in data
        assert "metrics" in data


class TestPersistence:
    """Test persistence endpoints."""

    @pytest.fixture
    def workflow_to_save(self):
        """Create a workflow to save."""
        data = {
            "workflow_id": "persist_workflow",
            "name": "Persistence Test",
            "description": "Test saving",
            "task_ids": ["t1"],
            "agent_names": ["Athena"],
            "problem_statement": "Test",
        }
        client.post("/workflows", json=data)
        return data["workflow_id"]

    def test_save_workflow(self, workflow_to_save):
        """Save a workflow."""
        response = client.post(
            f"/workflows/{workflow_to_save}/save", json={"tags": ["test", "api"]}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_to_save
        assert "filepath" in data
        assert data["filepath"].endswith(".json")

    def test_save_workflow_custom_filename(self, workflow_to_save):
        """Save workflow with custom filename."""
        response = client.post(
            f"/workflows/{workflow_to_save}/save",
            json={"filename": "custom.json", "tags": ["custom"]},
        )
        assert response.status_code == 200
        data = response.json()

        assert "custom.json" in data["filepath"]

    def test_get_saved_workflows(self, workflow_to_save):
        """List saved workflows."""
        # Save a workflow
        client.post(f"/workflows/{workflow_to_save}/save", json={"tags": ["test"]})

        # List saved
        response = client.get("/workflows/saved")
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "workflows" in data

    def test_get_saved_workflows_filter(self, workflow_to_save):
        """Filter saved workflows by tag."""
        # Save a workflow
        client.post(
            f"/workflows/{workflow_to_save}/save", json={"tags": ["unique_tag"]}
        )

        # Filter by tag
        response = client.get("/workflows/saved?tags=unique_tag")
        assert response.status_code == 200
        data = response.json()

        # Should find at least our workflow
        assert len(data["workflows"]) >= 1

    def test_load_workflow(self, workflow_to_save):
        """Load a workflow from disk."""
        # Save first
        save_response = client.post(f"/workflows/{workflow_to_save}/save", json={})
        filepath = save_response.json()["filepath"]

        # Delete from memory
        client.delete(f"/workflows/{workflow_to_save}")

        # Load back
        response = client.post("/workflows/load", json={"filepath": filepath})
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_to_save

    def test_get_workflow_versions(self, workflow_to_save):
        """Get version history of a workflow."""
        # Save multiple times
        for i in range(2):
            client.post(
                f"/workflows/{workflow_to_save}/save", json={"filename": f"v{i}.json"}
            )

        # Get versions
        response = client.get(f"/workflows/{workflow_to_save}/versions")
        assert response.status_code == 200
        data = response.json()

        assert data["workflow_id"] == workflow_to_save
        assert "total_versions" in data
        assert "versions" in data

    def test_export_workflow_report(self, workflow_to_save):
        """Export workflow report."""
        # Execute first to get results
        client.post(f"/workflows/{workflow_to_save}/execute")

        # Export report
        response = client.post(f"/workflows/{workflow_to_save}/export")
        assert response.status_code == 200
        data = response.json()

        assert "workflow_info" in data
        assert "tasks" in data
        assert "agents" in data
        assert "collaboration" in data
        assert "metrics" in data


class TestAgentEndpoints:
    """Test agent information endpoints."""

    def test_list_agents(self):
        """List available agents."""
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert "agents" in data
        assert len(data["agents"]) == 3

        # Check agent structure
        for agent in data["agents"]:
            assert "name" in agent
            assert "role" in agent
            assert "description" in agent
            assert "traits" in agent
            assert "affinities" in agent

    def test_list_agents_contains_all(self):
        """All three agents are present."""
        response = client.get("/agents")
        data = response.json()

        agent_names = {agent["name"] for agent in data["agents"]}
        assert agent_names == {"Athena", "Cato", "Zephyr"}

    def test_get_agent_athena(self):
        """Get Athena agent details."""
        response = client.get("/agents/Athena")
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Athena"
        assert data["role"] == "Architect"
        assert "traits" in data

    def test_get_agent_cato(self):
        """Get Cato agent details."""
        response = client.get("/agents/Cato")
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Cato"
        assert data["role"] == "Executor"

    def test_get_agent_zephyr(self):
        """Get Zephyr agent details."""
        response = client.get("/agents/Zephyr")
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Zephyr"
        assert data["role"] == "Experimenter"

    def test_get_agent_case_insensitive(self):
        """Agent lookup is case insensitive."""
        response = client.get("/agents/athena")
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "Architect"

    def test_get_agent_not_found(self):
        """Non-existent agent returns 404."""
        response = client.get("/agents/NonExistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestErrorHandling:
    """Test API error handling."""

    def test_invalid_workflow_on_tasks(self):
        """Getting tasks of non-existent workflow fails."""
        response = client.get("/workflows/nonexistent/tasks")
        assert response.status_code == 404

    def test_invalid_workflow_on_agents(self):
        """Getting agents of non-existent workflow fails."""
        response = client.get("/workflows/nonexistent/agents")
        assert response.status_code == 404

    def test_invalid_workflow_on_execute(self):
        """Executing non-existent workflow fails."""
        response = client.post("/workflows/nonexistent/execute")
        assert response.status_code == 404

    def test_invalid_workflow_on_save(self):
        """Saving non-existent workflow fails."""
        response = client.post("/workflows/nonexistent/save", json={})
        assert response.status_code == 404

    def test_load_invalid_filepath(self):
        """Loading invalid filepath fails."""
        response = client.post(
            "/workflows/load", json={"filepath": "/nonexistent/path.json"}
        )
        assert response.status_code == 404


class TestIntegration:
    """Integration tests combining multiple endpoints."""

    def test_workflow_lifecycle(self):
        """Complete workflow lifecycle."""
        # 1. Create
        create_data = {
            "workflow_id": "lifecycle_test",
            "name": "Lifecycle Test",
            "description": "Full lifecycle test",
            "task_ids": ["t1", "t2"],
            "agent_names": ["Athena", "Cato"],
            "problem_statement": "Test lifecycle",
        }
        create_response = client.post("/workflows", json=create_data)
        assert create_response.status_code == 200

        # 2. Get
        get_response = client.get("/workflows/lifecycle_test")
        assert get_response.status_code == 200

        # 3. Get tasks
        tasks_response = client.get("/workflows/lifecycle_test/tasks")
        assert tasks_response.status_code == 200
        assert len(tasks_response.json()) > 0

        # 4. Execute
        exec_response = client.post("/workflows/lifecycle_test/execute")
        assert exec_response.status_code == 200

        # 5. Get results
        results_response = client.get("/workflows/lifecycle_test/results")
        assert results_response.status_code == 200

        # 6. Save
        save_response = client.post(
            "/workflows/lifecycle_test/save", json={"tags": ["lifecycle"]}
        )
        assert save_response.status_code == 200

        # 7. Delete from memory
        delete_response = client.delete("/workflows/lifecycle_test")
        assert delete_response.status_code == 200

        # 8. Load from disk
        load_response = client.post(
            "/workflows/load", json={"filepath": save_response.json()["filepath"]}
        )
        assert load_response.status_code == 200

    def test_metrics_after_execution(self):
        """Metrics update after execution."""
        # Create and execute workflow
        create_data = {
            "workflow_id": "metrics_test",
            "name": "Metrics Test",
            "description": "Test metrics",
            "task_ids": ["t1"],
            "agent_names": ["Athena"],
            "problem_statement": "Test",
        }
        client.post("/workflows", json=create_data)
        client.post("/workflows/metrics_test/execute")

        # Check metrics
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()

        assert data["active_workflows"] > 0
        assert data["total_tasks_completed"] > 0
