"""
Tests for persistence layer - save/load workflows to disk.

Coverage:
- AC1: Save complete workflow state to JSON
- AC2: Load workflow from saved file
- AC3: Batch save/load operations
- AC4: Workflow versioning
- AC5: State validation on load
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from src.orchestration.workflow import (
    WorkflowOrchestrator,
    create_workflow_from_tasks,
)
from src.persistence.workflow_storage import (
    WorkflowStorage,
    load_workflow_quick,
    save_workflow_quick,
)


class TestWorkflowStorageBasics:
    """Test basic save/load functionality (AC1, AC2)."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_workflow(self):
        """Create a sample workflow for testing."""
        return create_workflow_from_tasks(
            workflow_id="test_workflow_001",
            task_ids=["task1", "task2", "task3"],
            agent_names=["Athena", "Cato"],
            problem_statement="Test workflow for persistence testing",
            workflow_name="Test Workflow",
        )

    def test_workflow_storage_initialization(self, temp_storage_dir):
        """AC1: Initialize workflow storage with custom directory."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        assert storage.storage_dir == Path(temp_storage_dir)
        assert storage.storage_dir.exists()

    def test_save_workflow_creates_file(self, sample_workflow, temp_storage_dir):
        """AC1: Saving workflow creates JSON file."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = storage.save_workflow(sample_workflow)

        assert Path(filepath).exists()
        assert filepath.endswith(".json")

    def test_save_workflow_with_custom_filename(
        self, sample_workflow, temp_storage_dir
    ):
        """AC1: Save workflow with custom filename."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        custom_filename = "custom_workflow.json"
        filepath = storage.save_workflow(sample_workflow, filename=custom_filename)

        assert Path(filepath).exists()
        assert custom_filename in filepath

    def test_save_workflow_includes_metadata(self, sample_workflow, temp_storage_dir):
        """AC1: Saved workflow includes metadata."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = storage.save_workflow(sample_workflow, tags=["test", "persistence"])

        with open(filepath, "r") as f:
            state = json.load(f)

        assert "_metadata" in state
        assert "saved_at" in state["_metadata"]
        assert "version" in state["_metadata"]
        assert "tags" in state["_metadata"]
        assert set(state["_metadata"]["tags"]) == {"test", "persistence"}

    def test_save_workflow_preserves_state(self, sample_workflow, temp_storage_dir):
        """AC1: Saved workflow preserves complete state."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = storage.save_workflow(sample_workflow)

        with open(filepath, "r") as f:
            state = json.load(f)

        assert state["workflow_id"] == sample_workflow.workflow_id
        assert "tasks" in state
        assert "agents" in state
        assert "context" in state

    def test_load_workflow_from_file(self, sample_workflow, temp_storage_dir):
        """AC2: Load workflow from saved file."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = storage.save_workflow(sample_workflow)

        loaded = storage.load_workflow(filepath)

        assert isinstance(loaded, WorkflowOrchestrator)
        assert loaded.workflow_id == sample_workflow.workflow_id

    def test_load_workflow_restores_tasks(self, sample_workflow, temp_storage_dir):
        """AC2: Loading workflow restores tasks."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = storage.save_workflow(sample_workflow)

        loaded = storage.load_workflow(filepath)

        assert len(loaded.tasks) == len(sample_workflow.tasks)
        for task_id in sample_workflow.tasks:
            assert task_id in loaded.tasks

    def test_load_workflow_file_not_found(self, temp_storage_dir):
        """AC2: Loading non-existent file raises error."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        with pytest.raises(FileNotFoundError):
            storage.load_workflow(os.path.join(temp_storage_dir, "nonexistent.json"))

    def test_load_invalid_json(self, temp_storage_dir):
        """AC2: Loading invalid JSON raises error."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = Path(temp_storage_dir) / "invalid.json"

        with open(filepath, "w") as f:
            f.write("{ invalid json }")

        with pytest.raises(ValueError):
            storage.load_workflow(str(filepath))

    def test_load_workflow_with_missing_required_fields(self, temp_storage_dir):
        """AC5: Validation catches missing required fields."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = Path(temp_storage_dir) / "invalid_state.json"

        with open(filepath, "w") as f:
            json.dump({"workflow_id": "test"}, f)

        with pytest.raises(ValueError):
            storage.load_workflow(str(filepath))


class TestBatchOperations:
    """Test batch save/load operations (AC3)."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_workflows(self):
        """Create multiple sample workflows."""
        return [
            create_workflow_from_tasks(
                workflow_id=f"batch_workflow_{i}",
                task_ids=[f"t{i}_1", f"t{i}_2"],
                agent_names=["Athena"],
                problem_statement=f"Batch workflow {i}",
            )
            for i in range(3)
        ]

    def test_save_workflows_batch(self, sample_workflows, temp_storage_dir):
        """AC3: Save multiple workflows in batch."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        results = storage.save_workflows_batch(sample_workflows)

        assert len(results) == 3
        for workflow in sample_workflows:
            assert workflow.workflow_id in results
            assert Path(results[workflow.workflow_id]).exists()

    def test_save_workflows_batch_with_subdirectory(
        self, sample_workflows, temp_storage_dir
    ):
        """AC3: Save batch workflows in subdirectory."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        results = storage.save_workflows_batch(sample_workflows, directory="batch")

        assert len(results) == 3
        for filepath in results.values():
            assert "batch" in filepath

    def test_load_workflows_batch(self, sample_workflows, temp_storage_dir):
        """AC3: Load multiple workflows from directory."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Save workflows first
        storage.save_workflows_batch(sample_workflows, directory="test_batch")

        # Load them back
        loaded = storage.load_workflows_batch("test_batch")

        assert len(loaded) == 3
        for filename, orchestrator in loaded.items():
            assert isinstance(orchestrator, WorkflowOrchestrator)

    def test_load_workflows_batch_empty_directory(self, temp_storage_dir):
        """AC3: Load from non-existent directory returns empty."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        loaded = storage.load_workflows_batch("nonexistent")

        assert loaded == {}

    def test_load_workflows_batch_skips_invalid(
        self, sample_workflows, temp_storage_dir
    ):
        """AC3: Batch load skips invalid files."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Create batch directory with mix of valid and invalid files
        batch_dir = Path(temp_storage_dir) / "mixed_batch"
        batch_dir.mkdir()

        # Save one valid workflow
        valid_workflow = sample_workflows[0]
        with open(batch_dir / "valid.json", "w") as f:
            json.dump(valid_workflow.to_dict(), f)

        # Create invalid file
        with open(batch_dir / "invalid.json", "w") as f:
            f.write("invalid json")

        # Load should skip invalid
        loaded = storage.load_workflows_batch("mixed_batch")
        assert len(loaded) == 1


class TestVersioning:
    """Test workflow versioning (AC4)."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_workflow(self):
        """Create a sample workflow."""
        return create_workflow_from_tasks(
            workflow_id="versioned_workflow",
            task_ids=["task1", "task2"],
            agent_names=["Athena"],
            problem_statement="Versioning test",
        )

    def test_get_workflow_versions_multiple_saves(
        self, sample_workflow, temp_storage_dir
    ):
        """AC4: Track multiple versions of a workflow."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Save same workflow multiple times with version suffix
        for version in range(1, 4):
            filename = f"versioned_workflow_v{version}.json"
            storage.save_workflow(sample_workflow, filename=filename)

        # Get versions
        versions = storage.get_workflow_versions("versioned_workflow")

        assert len(versions) == 3
        assert all("saved_at" in v for v in versions)
        assert all("version" in v for v in versions)

    def test_export_workflow_report(self, sample_workflow, temp_storage_dir):
        """AC4: Export comprehensive workflow report."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Save and load to populate some metrics
        filepath = storage.save_workflow(sample_workflow)
        loaded = storage.load_workflow(filepath)

        report = storage.export_workflow_report(loaded)

        assert "workflow_info" in report
        assert "tasks" in report
        assert "agents" in report
        assert "collaboration" in report
        assert "metrics" in report

        # Validate workflow info
        assert report["workflow_info"]["id"] == loaded.workflow_id
        assert report["workflow_info"]["name"] == loaded.name
        assert "current_phase" in report["workflow_info"]

    def test_export_report_includes_results(self, sample_workflow, temp_storage_dir):
        """AC4: Export report can include execution results."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Add some metrics to the workflow
        sample_workflow.metrics = {"total_time_ms": 1000, "tasks_completed": 3}

        report = storage.export_workflow_report(sample_workflow, include_results=True)

        assert "results" in report
        assert report["results"]["total_time_ms"] == 1000
        assert report["results"]["tasks_completed"] == 3


class TestStateValidation:
    """Test state validation on load (AC5)."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_validate_missing_workflow_id(self, temp_storage_dir):
        """AC5: Validation catches missing workflow_id."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = Path(temp_storage_dir) / "invalid.json"

        with open(filepath, "w") as f:
            json.dump({"tasks": {}, "agents": [], "context": {}}, f)

        with pytest.raises(ValueError, match="workflow_id"):
            storage.load_workflow(str(filepath))

    def test_validate_missing_tasks(self, temp_storage_dir):
        """AC5: Validation catches missing tasks."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = Path(temp_storage_dir) / "invalid.json"

        with open(filepath, "w") as f:
            json.dump({"workflow_id": "test", "agents": [], "context": {}}, f)

        with pytest.raises(ValueError, match="tasks"):
            storage.load_workflow(str(filepath))

    def test_validate_missing_agents(self, temp_storage_dir):
        """AC5: Validation catches missing agents."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = Path(temp_storage_dir) / "invalid.json"

        with open(filepath, "w") as f:
            json.dump({"workflow_id": "test", "tasks": {}, "context": {}}, f)

        with pytest.raises(ValueError, match="agents"):
            storage.load_workflow(str(filepath))

    def test_validate_missing_context(self, temp_storage_dir):
        """AC5: Validation catches missing context."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = Path(temp_storage_dir) / "invalid.json"

        with open(filepath, "w") as f:
            json.dump({"workflow_id": "test", "tasks": {}, "agents": []}, f)

        with pytest.raises(ValueError, match="context"):
            storage.load_workflow(str(filepath))

    def test_validate_tasks_not_dict(self, temp_storage_dir):
        """AC5: Validation requires tasks to be dict."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        filepath = Path(temp_storage_dir) / "invalid.json"

        with open(filepath, "w") as f:
            json.dump(
                {"workflow_id": "test", "tasks": [], "agents": {}, "context": {}},
                f,
            )

        with pytest.raises(ValueError, match="tasks"):
            storage.load_workflow(str(filepath))


class TestConvenienceFunctions:
    """Test convenience functions for quick save/load."""

    @pytest.fixture
    def temp_storage_dir(self, monkeypatch):
        """Create temporary storage directory and set as default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setenv("WORKFLOW_STORAGE_DIR", tmpdir)
            # Also directly patch the default in WorkflowStorage init
            original_init = WorkflowStorage.__init__

            def patched_init(self, storage_dir: str = "workflows"):
                original_init(self, storage_dir=tmpdir)

            monkeypatch.setattr(WorkflowStorage, "__init__", patched_init)
            yield tmpdir

    @pytest.fixture
    def sample_workflow(self):
        """Create a sample workflow."""
        return create_workflow_from_tasks(
            workflow_id="quick_test",
            task_ids=["task1"],
            agent_names=["Athena"],
            problem_statement="Quick test",
        )

    def test_save_workflow_quick(self, sample_workflow, temp_storage_dir):
        """Quick save function works."""
        filepath = save_workflow_quick(sample_workflow)

        assert Path(filepath).exists()
        assert "quick_test" in filepath

    def test_load_workflow_quick(self, sample_workflow, temp_storage_dir):
        """Quick load function works."""
        filepath = save_workflow_quick(sample_workflow)
        loaded = load_workflow_quick(filepath)

        assert isinstance(loaded, WorkflowOrchestrator)
        assert loaded.workflow_id == "quick_test"


class TestWorkflowListing:
    """Test listing and managing workflows."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_list_workflows(self, temp_storage_dir):
        """List all saved workflows."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Save multiple workflows
        for i in range(3):
            workflow = create_workflow_from_tasks(
                workflow_id=f"wf_{i}",
                task_ids=["task1"],
                agent_names=["Athena"],
                problem_statement=f"Test {i}",
            )
            storage.save_workflow(workflow, tags=["test"])

        # List workflows
        workflows = storage.list_workflows()

        assert len(workflows) == 3
        assert all("workflow_id" in w for w in workflows)
        assert all("filename" in w for w in workflows)
        assert all("saved_at" in w for w in workflows)

    def test_list_workflows_filter_by_tags(self, temp_storage_dir):
        """Filter workflow list by tags."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Save workflows with different tags
        for i in range(2):
            workflow = create_workflow_from_tasks(
                workflow_id=f"tagged_{i}",
                task_ids=["task1"],
                agent_names=["Athena"],
                problem_statement=f"Test {i}",
            )
            storage.save_workflow(workflow, tags=["tagged"])

        for i in range(2):
            workflow = create_workflow_from_tasks(
                workflow_id=f"untagged_{i}",
                task_ids=["task1"],
                agent_names=["Athena"],
                problem_statement=f"Test {i}",
            )
            storage.save_workflow(workflow, tags=["other"])

        # List with filter
        tagged = storage.list_workflows(tags=["tagged"])

        assert len(tagged) == 2
        assert all("tagged" in w["tags"] for w in tagged)

    def test_delete_workflow(self, temp_storage_dir):
        """Delete a saved workflow."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        workflow = create_workflow_from_tasks(
            workflow_id="to_delete",
            task_ids=["task1"],
            agent_names=["Athena"],
            problem_statement="Will be deleted",
        )
        filepath = storage.save_workflow(workflow)
        filename = Path(filepath).name

        # Verify it exists
        assert Path(filepath).exists()

        # Delete it
        result = storage.delete_workflow(filename)
        assert result is True
        assert not Path(filepath).exists()

    def test_delete_nonexistent_workflow(self, temp_storage_dir):
        """Deleting non-existent workflow returns False."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)
        result = storage.delete_workflow("nonexistent.json")

        assert result is False


class TestRoundTripIntegration:
    """Integration tests for complete save/load cycles."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_workflow_roundtrip_preserves_properties(self, temp_storage_dir):
        """Save and load preserves workflow properties."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Create workflow with specific properties
        original = create_workflow_from_tasks(
            workflow_id="roundtrip_test",
            task_ids=["task1", "task2", "task3"],
            agent_names=["Athena", "Cato"],
            problem_statement="Test roundtrip",
            workflow_name="Roundtrip Test",
        )

        # Save and load
        filepath = storage.save_workflow(original, tags=["roundtrip"])
        loaded = storage.load_workflow(filepath)

        # Verify properties match
        assert loaded.workflow_id == original.workflow_id
        assert loaded.name == original.name
        assert len(loaded.tasks) == len(original.tasks)

    def test_multiple_save_cycles(self, temp_storage_dir):
        """Multiple save/load cycles maintain integrity."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        original = create_workflow_from_tasks(
            workflow_id="multi_cycle",
            task_ids=["task1"],
            agent_names=["Athena"],
            problem_statement="Multi-cycle test",
        )

        # Multiple save/load cycles
        current = original
        for _ in range(3):
            filepath = storage.save_workflow(current)
            current = storage.load_workflow(filepath)

        # Final state should match original
        assert current.workflow_id == original.workflow_id

    def test_batch_roundtrip(self, temp_storage_dir):
        """Batch save/load maintains all workflows."""
        storage = WorkflowStorage(storage_dir=temp_storage_dir)

        # Create and save batch
        originals = [
            create_workflow_from_tasks(
                workflow_id=f"batch_{i}",
                task_ids=["task1"],
                agent_names=["Athena"],
                problem_statement=f"Batch {i}",
            )
            for i in range(3)
        ]

        storage.save_workflows_batch(originals, directory="batch_test")

        # Load batch
        loaded = storage.load_workflows_batch("batch_test")

        # All should be present
        assert len(loaded) == len(originals)
        for orchestrator in loaded.values():
            assert isinstance(orchestrator, WorkflowOrchestrator)
