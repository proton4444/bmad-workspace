"""
Tests for Story 3.1: Shared Context & Knowledge Exchange

Tests verify that:
- AC1: Agents can contribute ideas to shared context
- AC2: Context accessible to all agents in collaboration
- AC3: Ideas include metadata (contributor, timestamp, affinity score)
- AC4: Context maintains idea relationships (references, builds_on)
- AC5: Observable context serializable to JSON
"""

import pytest
from src.collaboration.context import (
    ContextManager,
    Idea,
    IdeaCategory,
    SharedContext,
)


class TestIdea:
    """Tests for Idea dataclass."""

    def test_idea_creation(self):
        """Idea can be created with content and contributor."""
        idea = Idea(
            content="Use machine learning for classification",
            contributor="Athena",
            category=IdeaCategory.APPROACH,
        )
        assert idea.content == "Use machine learning for classification"
        assert idea.contributor == "Athena"
        assert idea.category == IdeaCategory.APPROACH

    def test_idea_has_unique_id(self):
        """Each idea gets unique ID."""
        idea1 = Idea(content="Idea 1", contributor="Athena")
        idea2 = Idea(content="Idea 2", contributor="Cato")
        assert idea1.id != idea2.id

    def test_idea_has_timestamp(self):
        """Idea records creation timestamp."""
        idea = Idea(content="Test idea", contributor="Athena")
        assert idea.timestamp is not None
        assert "T" in idea.timestamp  # ISO format includes T

    def test_idea_metadata(self):
        """Idea includes all metadata: contributor, timestamp, affinity."""
        idea = Idea(
            content="Test",
            contributor="Zephyr",
            affinity_fit=0.85,
        )
        assert idea.contributor == "Zephyr"
        assert idea.affinity_fit == 0.85
        assert idea.timestamp is not None

    def test_idea_relationships(self):
        """Idea can reference other ideas (builds_on)."""
        idea1 = Idea(content="First idea", contributor="Athena")
        idea2 = Idea(
            content="Builds on first",
            contributor="Cato",
            builds_on=[idea1.id],
        )
        assert idea1.id in idea2.builds_on

    def test_idea_add_reference(self):
        """Idea can add reference to another idea."""
        idea1 = Idea(content="First", contributor="Athena")
        idea2 = Idea(content="Second", contributor="Cato")

        idea2.add_reference(idea1.id)
        assert idea1.id in idea2.builds_on

    def test_idea_add_referrer(self):
        """Idea can track who references it."""
        idea1 = Idea(content="First", contributor="Athena")
        idea2 = Idea(content="Second", contributor="Cato")

        idea1.add_referrer(idea2.id)
        assert idea2.id in idea1.referenced_by

    def test_idea_quality_score(self):
        """Idea tracks quality assessment."""
        idea = Idea(content="Test", contributor="Athena")
        idea.quality_score = 0.85
        assert idea.quality_score == 0.85

    def test_idea_novelty_score(self):
        """Idea tracks creative novelty assessment."""
        idea = Idea(content="Test", contributor="Athena")
        idea.creative_novelty = 0.92
        assert idea.creative_novelty == 0.92

    def test_idea_to_dict(self):
        """AC5: Idea serializable to dict for JSON."""
        idea = Idea(
            content="Test idea",
            contributor="Athena",
            category=IdeaCategory.APPROACH,
            affinity_fit=0.8,
        )
        idea_dict = idea.to_dict()

        assert idea_dict["content"] == "Test idea"
        assert idea_dict["contributor"] == "Athena"
        assert idea_dict["category"] == "approach"
        assert idea_dict["affinity_fit"] == 0.8


class TestSharedContext:
    """Tests for SharedContext - collaborative context."""

    def test_context_creation(self):
        """SharedContext can be created with topic and problem statement."""
        context = SharedContext(
            topic="API Design",
            problem_statement="Design a scalable REST API for user management",
        )
        assert context.topic == "API Design"
        assert (
            context.problem_statement
            == "Design a scalable REST API for user management"
        )

    def test_context_has_session_id(self):
        """Context gets unique session ID."""
        context1 = SharedContext(topic="Topic 1", problem_statement="Problem 1")
        context2 = SharedContext(topic="Topic 2", problem_statement="Problem 2")
        assert context1.session_id != context2.session_id

    def test_context_tracks_timestamp(self):
        """Context records creation timestamp."""
        context = SharedContext(topic="Test", problem_statement="Test problem")
        assert context.created_at is not None
        assert context.updated_at is not None

    def test_add_idea_to_context(self):
        """AC1: Agents can contribute ideas to shared context."""
        context = SharedContext(topic="Design", problem_statement="Design something")

        idea = context.add_idea(
            content="Use microservices architecture",
            contributor="Athena",
            category=IdeaCategory.APPROACH,
            affinity_fit=0.95,
        )

        assert idea.id in context.ideas
        assert idea.content == "Use microservices architecture"

    def test_context_accessible_to_agents(self):
        """AC2: Context accessible to all agents in collaboration."""
        context = SharedContext(topic="Brainstorm", problem_statement="Problem")

        # Multiple agents contribute
        idea1 = context.add_idea("Idea from Athena", "Athena", affinity_fit=0.9)
        idea2 = context.add_idea("Idea from Cato", "Cato", affinity_fit=0.85)
        idea3 = context.add_idea("Idea from Zephyr", "Zephyr", affinity_fit=0.88)

        # All agents can access all ideas
        assert len(context.ideas) == 3
        assert idea1.id in context.ideas
        assert idea2.id in context.ideas
        assert idea3.id in context.ideas

    def test_idea_metadata_preserved(self):
        """AC3: Ideas include metadata (contributor, timestamp, affinity)."""
        context = SharedContext(topic="Test", problem_statement="Test")

        idea = context.add_idea(
            content="Test idea",
            contributor="Athena",
            affinity_fit=0.87,
        )

        retrieved = context.ideas[idea.id]
        assert retrieved.contributor == "Athena"
        assert retrieved.affinity_fit == 0.87
        assert retrieved.timestamp is not None

    def test_idea_relationships_in_context(self):
        """AC4: Context maintains idea relationships (references, builds_on)."""
        context = SharedContext(topic="Design", problem_statement="Problem")

        idea1 = context.add_idea(
            "Core approach",
            "Athena",
            category=IdeaCategory.APPROACH,
        )
        idea2 = context.add_idea(
            "Detail for approach",
            "Cato",
            category=IdeaCategory.DETAIL,
            builds_on=[idea1.id],
        )

        # Relationship recorded
        assert idea1.id in idea2.builds_on
        assert idea2.id in idea1.referenced_by

    def test_participating_agents_tracked(self):
        """Context tracks which agents are participating."""
        context = SharedContext(topic="Test", problem_statement="Test")

        context.add_idea("Idea 1", "Athena")
        context.add_idea("Idea 2", "Cato")
        context.add_idea("Idea 3", "Zephyr")

        assert "Athena" in context.participating_agents
        assert "Cato" in context.participating_agents
        assert "Zephyr" in context.participating_agents
        assert len(context.participating_agents) == 3

    def test_get_ideas_by_category(self):
        """Context can retrieve ideas by category."""
        context = SharedContext(topic="Test", problem_statement="Test")

        context.add_idea("Approach 1", "Athena", category=IdeaCategory.APPROACH)
        context.add_idea("Approach 2", "Cato", category=IdeaCategory.APPROACH)
        context.add_idea("Detail 1", "Zephyr", category=IdeaCategory.DETAIL)

        approaches = context.get_ideas_by_category(IdeaCategory.APPROACH)
        details = context.get_ideas_by_category(IdeaCategory.DETAIL)

        assert len(approaches) == 2
        assert len(details) == 1

    def test_get_ideas_by_contributor(self):
        """Context can retrieve ideas by specific agent."""
        context = SharedContext(topic="Test", problem_statement="Test")

        context.add_idea("Athena idea 1", "Athena")
        context.add_idea("Athena idea 2", "Athena")
        context.add_idea("Cato idea", "Cato")

        athena_ideas = context.get_ideas_by_contributor("Athena")
        assert len(athena_ideas) == 2
        assert all(i.contributor == "Athena" for i in athena_ideas)

    def test_get_related_ideas(self):
        """Context can retrieve ideas related to a given idea."""
        context = SharedContext(topic="Test", problem_statement="Test")

        idea1 = context.add_idea("Core idea", "Athena")
        idea2 = context.add_idea("Building on core", "Cato", builds_on=[idea1.id])
        idea3 = context.add_idea("Another on core", "Zephyr", builds_on=[idea1.id])

        related = context.get_related_ideas(idea1.id)
        assert len(related["referencing_ideas"]) == 2

    def test_quality_assessment(self):
        """Context can update and retrieve quality scores."""
        context = SharedContext(topic="Test", problem_statement="Test")

        idea = context.add_idea("Test idea", "Athena")
        context.update_idea_quality(idea.id, 0.92)

        retrieved = context.ideas[idea.id]
        assert retrieved.quality_score == 0.92

    def test_novelty_assessment(self):
        """Context can update and retrieve novelty scores."""
        context = SharedContext(topic="Test", problem_statement="Test")

        idea = context.add_idea("Creative idea", "Zephyr")
        context.update_idea_novelty(idea.id, 0.88)

        retrieved = context.ideas[idea.id]
        assert retrieved.creative_novelty == 0.88

    def test_get_ideas_for_synthesis(self):
        """Context can retrieve high-quality ideas for synthesis."""
        context = SharedContext(topic="Test", problem_statement="Test")

        idea1 = context.add_idea("Low quality", "Athena")
        idea1.quality_score = 0.3

        idea2 = context.add_idea("Good idea", "Cato")
        idea2.quality_score = 0.75

        idea3 = context.add_idea("Excellent idea", "Zephyr")
        idea3.quality_score = 0.92

        high_quality = context.get_ideas_for_synthesis(min_quality=0.7)
        assert len(high_quality) == 2
        assert idea2.id in [i.id for i in high_quality]
        assert idea3.id in [i.id for i in high_quality]

    def test_context_phase_management(self):
        """Context can transition between collaboration phases."""
        context = SharedContext(topic="Test", problem_statement="Test")
        assert context.phase == "exploration"

        context.set_phase("synthesis")
        assert context.phase == "synthesis"

        context.set_phase("evaluation")
        assert context.phase == "evaluation"

    def test_context_to_dict(self):
        """AC5: Observable context serializable to JSON."""
        context = SharedContext(topic="Test", problem_statement="Test problem")
        context.add_idea("Idea 1", "Athena", affinity_fit=0.9)
        context.add_idea("Idea 2", "Cato", affinity_fit=0.85)

        context_dict = context.to_dict()

        assert context_dict["topic"] == "Test"
        assert context_dict["problem_statement"] == "Test problem"
        assert context_dict["idea_count"] == 2
        assert context_dict["agent_count"] == 2
        assert "session_id" in context_dict
        assert isinstance(context_dict["ideas"], dict)

    def test_context_summary(self):
        """Context provides human-readable summary."""
        context = SharedContext(topic="API Design", problem_statement="Design API")
        context.add_idea("Use REST", "Athena", category=IdeaCategory.APPROACH)
        context.add_idea("Add caching", "Cato", category=IdeaCategory.DETAIL)

        summary = context.get_summary()
        assert "API Design" in summary
        assert "Athena" in summary or "REST" in summary
        assert len(summary) > 0


class TestContextManager:
    """Tests for ContextManager - manages collaboration contexts."""

    def test_create_context(self):
        """Manager can create new context."""
        manager = ContextManager()
        context = manager.create_context(topic="Test", problem_statement="Test problem")
        assert context is not None
        assert context.topic == "Test"

    def test_context_stored_in_manager(self):
        """Created context stored in active contexts."""
        manager = ContextManager()
        context = manager.create_context(topic="Test", problem_statement="Problem")

        retrieved = manager.get_context(context.session_id)
        assert retrieved is not None
        assert retrieved.topic == "Test"

    def test_get_nonexistent_context_returns_none(self):
        """Getting nonexistent context returns None."""
        manager = ContextManager()
        result = manager.get_context("nonexistent-id")
        assert result is None

    def test_list_active_contexts(self):
        """Manager lists all active context IDs."""
        manager = ContextManager()
        context1 = manager.create_context("Topic 1", "Problem 1")
        context2 = manager.create_context("Topic 2", "Problem 2")

        active = manager.list_active_contexts()
        assert context1.session_id in active
        assert context2.session_id in active
        assert len(active) == 2

    def test_close_context(self):
        """Manager can close context and move to history."""
        manager = ContextManager()
        context = manager.create_context("Test", "Problem")

        manager.close_context(context.session_id)

        assert context.session_id not in manager.list_active_contexts()
        assert len(manager.context_history) == 1
        assert manager.context_history[0].session_id == context.session_id

    def test_get_context_stats(self):
        """Manager can get statistics about context."""
        manager = ContextManager()
        context = manager.create_context("Design", "Design something")

        context.add_idea("Idea 1", "Athena")
        context.add_idea("Idea 2", "Athena")
        context.add_idea("Idea 3", "Cato")

        stats = manager.get_context_stats(context.session_id)

        assert stats["total_ideas"] == 3
        assert stats["ideas_by_agent"]["Athena"] == 2
        assert stats["ideas_by_agent"]["Cato"] == 1
        assert len(stats["participating_agents"]) == 2


class TestAcceptanceCriteria:
    """Comprehensive acceptance criteria tests."""

    def test_ac1_agents_contribute_ideas(self):
        """AC1: Agents can contribute ideas to shared context."""
        context = SharedContext(topic="Test", problem_statement="Test")

        # Multiple agents contribute
        idea1 = context.add_idea("Athena's approach", "Athena")
        idea2 = context.add_idea("Cato's approach", "Cato")
        idea3 = context.add_idea("Zephyr's approach", "Zephyr")

        assert len(context.ideas) == 3
        assert all(
            i.contributor in ["Athena", "Cato", "Zephyr"]
            for i in context.ideas.values()
        )

    def test_ac2_context_accessible_to_all(self):
        """AC2: Context accessible to all agents in collaboration."""
        context = SharedContext(topic="Test", problem_statement="Test")

        # Agent 1 adds idea
        context.add_idea("Idea 1", "Athena")

        # Agent 2 can see and reference it
        idea2 = context.add_idea(
            "Idea 2 builds on 1", "Cato", builds_on=[list(context.ideas.keys())[0]]
        )

        # Agent 3 can see both
        context.add_idea("Idea 3", "Zephyr")

        # All agents have full context access
        assert len(context.participating_agents) == 3
        assert len(context.ideas) == 3

    def test_ac3_ideas_have_metadata(self):
        """AC3: Ideas include metadata (contributor, timestamp, affinity)."""
        context = SharedContext(topic="Test", problem_statement="Test")

        idea = context.add_idea("Test idea", "Athena", affinity_fit=0.95)

        retrieved = context.ideas[idea.id]
        assert retrieved.contributor == "Athena"
        assert retrieved.timestamp is not None
        assert retrieved.affinity_fit == 0.95
        assert retrieved.id is not None

    def test_ac4_context_maintains_relationships(self):
        """AC4: Context maintains idea relationships (references, builds_on)."""
        context = SharedContext(topic="Test", problem_statement="Test")

        idea1 = context.add_idea("First", "Athena")
        idea2 = context.add_idea("Second", "Cato", builds_on=[idea1.id])
        idea3 = context.add_idea("Third", "Zephyr", builds_on=[idea2.id])

        # Check relationships
        assert idea2.id in idea1.referenced_by
        assert idea3.id in idea2.referenced_by
        assert idea1.id in idea2.builds_on
        assert idea2.id in idea3.builds_on

    def test_ac5_observable_context_json_serializable(self):
        """AC5: Observable context serializable to JSON."""
        context = SharedContext(topic="Test", problem_statement="Problem")
        context.add_idea("Idea 1", "Athena", affinity_fit=0.9)
        context.add_idea("Idea 2", "Cato", affinity_fit=0.85)

        context_dict = context.to_dict()

        # Verify all fields serializable
        assert isinstance(context_dict["session_id"], str)
        assert isinstance(context_dict["topic"], str)
        assert isinstance(context_dict["ideas"], dict)
        assert isinstance(context_dict["participating_agents"], list)

        # Ideas are dicts (serializable)
        for idea_id, idea_data in context_dict["ideas"].items():
            assert isinstance(idea_data, dict)
            assert "content" in idea_data
            assert "contributor" in idea_data
