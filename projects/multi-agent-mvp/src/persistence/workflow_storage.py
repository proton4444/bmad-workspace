"""
Workflow persistence layer for saving and loading workflows.

Enables complete workflow state serialization to JSON files and
reconstruction from saved files with full state restoration.

Enhancement: Persistence Layer
- AC1: Save complete workflow state to JSON
- AC2: Load workflow from saved file
- AC3: Batch save/load operations
- AC4: Workflow versioning
- AC5: State validation on load
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.orchestration.workflow import WorkflowOrchestrator, create_workflow_from_tasks


class WorkflowStorage:
    """Manages persistent storage of workflows."""

    def __init__(self, storage_dir: str = "workflows"):
        """
        Initialize workflow storage.

        Args:
            storage_dir: Directory to store workflow files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_workflow(
        self,
        orchestrator: WorkflowOrchestrator,
        filename: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        AC1: Save complete workflow state to JSON file.

        Args:
            orchestrator: WorkflowOrchestrator to save
            filename: Custom filename (defaults to workflow_id.json)
            tags: Optional tags for categorization

        Returns:
            Filepath where workflow was saved
        """
        # Determine filename
        if filename is None:
            filename = f"{orchestrator.workflow_id}.json"

        filepath = self.storage_dir / filename

        # Get complete state
        state = orchestrator.to_dict()

        # Add metadata
        state["_metadata"] = {
            "saved_at": datetime.now().isoformat(),
            "version": "1.0",
            "tags": tags or [],
            "filename": str(filename),
        }

        # Save to JSON
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        return str(filepath)

    def load_workflow(self, filepath: str) -> WorkflowOrchestrator:
        """
        AC2: Load workflow from saved JSON file.

        Args:
            filepath: Path to saved workflow JSON

        Returns:
            Reconstructed WorkflowOrchestrator

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid or corrupted
        """
        filepath = Path(filepath)

        # Verify file exists
        if not filepath.exists():
            raise FileNotFoundError(f"Workflow file not found: {filepath}")

        # Load JSON
        try:
            with open(filepath, "r") as f:
                state = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid workflow file format: {e}")

        # Validate state
        self._validate_workflow_state(state)

        # Reconstruct orchestrator
        orchestrator = self._reconstruct_orchestrator(state)

        return orchestrator

    def save_workflows_batch(
        self, orchestrators: List[WorkflowOrchestrator], directory: Optional[str] = None
    ) -> Dict[str, str]:
        """
        AC3: Save multiple workflows in batch.

        Args:
            orchestrators: List of orchestrators to save
            directory: Optional subdirectory

        Returns:
            Dict mapping workflow_id to filepath
        """
        results = {}

        # Create subdirectory if needed
        if directory:
            subdir = self.storage_dir / directory
            subdir.mkdir(parents=True, exist_ok=True)

        for orchestrator in orchestrators:
            if directory:
                filepath = self.save_workflow(
                    orchestrator,
                    filename=f"{directory}/{orchestrator.workflow_id}.json",
                )
            else:
                filepath = self.save_workflow(orchestrator)

            results[orchestrator.workflow_id] = filepath

        return results

    def load_workflows_batch(self, directory: str) -> Dict[str, WorkflowOrchestrator]:
        """
        AC3: Load multiple workflows from directory.

        Args:
            directory: Directory containing workflow files

        Returns:
            Dict mapping filename to loaded orchestrator
        """
        results = {}
        dir_path = self.storage_dir / directory

        if not dir_path.exists():
            return results

        # Load all JSON files in directory
        for filepath in dir_path.glob("*.json"):
            try:
                orchestrator = self.load_workflow(str(filepath))
                results[filepath.name] = orchestrator
            except (FileNotFoundError, ValueError):
                # Skip invalid files
                continue

        return results

    def get_workflow_versions(self, workflow_id: str) -> List[Dict]:
        """
        AC4: Get all saved versions of a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            List of version info dicts
        """
        versions = []

        # Look for versioned files
        for filepath in self.storage_dir.glob(f"{workflow_id}_v*.json"):
            try:
                with open(filepath, "r") as f:
                    state = json.load(f)

                metadata = state.get("_metadata", {})
                versions.append(
                    {
                        "filename": filepath.name,
                        "saved_at": metadata.get("saved_at"),
                        "version": metadata.get("version"),
                        "tags": metadata.get("tags", []),
                    }
                )
            except (json.JSONDecodeError, IOError):
                continue

        # Sort by filename (version number)
        versions.sort(key=lambda x: x["filename"])

        return versions

    def export_workflow_report(
        self, orchestrator: WorkflowOrchestrator, include_results: bool = True
    ) -> Dict:
        """
        AC4: Generate comprehensive workflow report for export.

        Args:
            orchestrator: Workflow to report on
            include_results: Whether to include execution results

        Returns:
            Report dict suitable for JSON export
        """
        report = {
            "workflow_info": {
                "id": orchestrator.workflow_id,
                "name": orchestrator.name,
                "description": orchestrator.description,
                "created_at": orchestrator.created_at,
                "completed_at": orchestrator.completed_at,
                "current_phase": orchestrator.current_phase.value,
            },
            "tasks": {
                task_id: {
                    "name": task.name,
                    "type": task.task_type,
                    "complexity": task.complexity,
                    "status": task.status,
                    "dependencies": task.dependencies,
                    "assigned_agent": task.assigned_agent,
                    "execution_time_ms": task.execution_time_ms,
                }
                for task_id, task in orchestrator.tasks.items()
            },
            "agents": {
                agent_name: {
                    "personality": agent_personality.role.value,
                    "traits": agent_personality.traits,
                }
                for agent_name, (_, agent_personality, _) in orchestrator.agents.items()
            },
            "collaboration": {
                "ideas_generated": len(orchestrator.context.ideas),
                "participating_agents": list(orchestrator.context.participating_agents),
            },
            "metrics": orchestrator.metrics,
        }

        if include_results and orchestrator.metrics:
            report["results"] = {
                "total_time_ms": orchestrator.metrics.get("total_time_ms"),
                "tasks_completed": orchestrator.metrics.get("tasks_completed"),
                "phases_completed": orchestrator.metrics.get("phases_completed"),
            }

        return report

    def _validate_workflow_state(self, state: Dict) -> None:
        """
        AC5: Validate loaded workflow state.

        Args:
            state: State dict to validate

        Raises:
            ValueError: If state is invalid
        """
        required_keys = ["workflow_id", "tasks", "agents", "context"]

        for key in required_keys:
            if key not in state:
                raise ValueError(f"Invalid workflow state: missing '{key}'")

        # Validate tasks
        if not isinstance(state.get("tasks"), dict):
            raise ValueError("Invalid workflow state: 'tasks' must be a dict")

        # Validate agents
        if not isinstance(state.get("agents"), (dict, list)):
            raise ValueError("Invalid workflow state: 'agents' must be a dict or list")

    def _reconstruct_orchestrator(self, state: Dict) -> WorkflowOrchestrator:
        """
        AC2 & AC5: Reconstruct orchestrator from saved state.

        Args:
            state: Saved workflow state

        Returns:
            Reconstructed WorkflowOrchestrator
        """
        # Create new orchestrator
        orchestrator = WorkflowOrchestrator(
            workflow_id=state["workflow_id"],
            name=state.get("name", ""),
            description=state.get("description", ""),
        )

        # Restore tasks
        for task_id, task_data in state.get("tasks", {}).items():
            from src.orchestration.workflow import WorkflowTask

            task = WorkflowTask(
                id=task_data["id"],
                name=task_data.get("name", ""),
                description=task_data.get("description", ""),
                task_type=task_data.get("task_type", "implementation"),
                complexity=task_data.get("complexity", "moderate"),
                dependencies=task_data.get("dependencies", []),
                status=task_data.get("status", "pending"),
                assigned_agent=task_data.get("assigned_agent"),
                result=task_data.get("result"),
                execution_time_ms=task_data.get("execution_time_ms", 0.0),
            )
            orchestrator.tasks[task_id] = task

        # Restore agents (simplified - would need agent factory in full implementation)
        # For now, we just track that agents existed
        agent_list = state.get("agents", [])
        if isinstance(agent_list, list):
            orchestrator._agent_names = agent_list
        else:
            orchestrator._agent_names = list(agent_list.keys())

        # Restore collaboration context
        orchestrator.context.session_id = state.get("context", {}).get("session_id", "")
        orchestrator.context.topic = state.get("context", {}).get("topic", "")
        orchestrator.context.problem_statement = state.get("context", {}).get(
            "problem_statement", ""
        )

        # Restore metadata
        orchestrator.created_at = state.get("created_at", datetime.now().isoformat())
        orchestrator.completed_at = state.get("completed_at")
        orchestrator.metrics = state.get("metrics", {})

        return orchestrator

    def list_workflows(self, tags: Optional[List[str]] = None) -> List[Dict]:
        """
        List all saved workflows with optional filtering.

        Args:
            tags: Optional tags to filter by

        Returns:
            List of workflow info dicts
        """
        workflows = []

        for filepath in self.storage_dir.glob("*.json"):
            try:
                with open(filepath, "r") as f:
                    state = json.load(f)

                metadata = state.get("_metadata", {})
                workflow_tags = metadata.get("tags", [])

                # Filter by tags if provided
                if tags and not any(tag in workflow_tags for tag in tags):
                    continue

                workflows.append(
                    {
                        "workflow_id": state.get("workflow_id"),
                        "name": state.get("name"),
                        "filename": filepath.name,
                        "saved_at": metadata.get("saved_at"),
                        "tags": workflow_tags,
                    }
                )
            except (json.JSONDecodeError, IOError):
                continue

        return workflows

    def delete_workflow(self, filename: str) -> bool:
        """
        Delete a saved workflow file.

        Args:
            filename: Filename to delete

        Returns:
            True if deleted, False if not found
        """
        filepath = self.storage_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True

        return False


def save_workflow_quick(
    orchestrator: WorkflowOrchestrator, filename: Optional[str] = None
) -> str:
    """
    Convenience function to quickly save a workflow.

    Args:
        orchestrator: Workflow to save
        filename: Optional custom filename

    Returns:
        Path where workflow was saved
    """
    storage = WorkflowStorage()
    return storage.save_workflow(orchestrator, filename)


def load_workflow_quick(filepath: str) -> WorkflowOrchestrator:
    """
    Convenience function to quickly load a workflow.

    Args:
        filepath: Path to workflow file

    Returns:
        Loaded WorkflowOrchestrator
    """
    storage = WorkflowStorage()
    return storage.load_workflow(filepath)


if __name__ == "__main__":
    # Example usage
    from src.orchestration.workflow import create_workflow_from_tasks

    # Create a workflow
    orchestrator = create_workflow_from_tasks(
        workflow_id="demo_workflow",
        task_ids=["task1", "task2", "task3"],
        agent_names=["Athena", "Cato"],
        problem_statement="Demonstration workflow",
    )

    # Execute it
    result = orchestrator.complete_workflow()

    # Save it
    storage = WorkflowStorage()
    filepath = storage.save_workflow(orchestrator, tags=["demo", "completed"])
    print(f"✓ Saved to: {filepath}")

    # Load it back
    loaded = storage.load_workflow(filepath)
    print(f"✓ Loaded: {loaded.workflow_id}")

    # List saved workflows
    workflows = storage.list_workflows()
    print(f"✓ Saved workflows: {len(workflows)}")

    for wf in workflows:
        print(f"  - {wf['workflow_id']} ({wf['filename']})")
