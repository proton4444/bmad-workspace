"""
Tests for Story 3.2: Multi-Agent Brainstorming Session

Tests verify that:
- AC1: Agents take turns contributing ideas based on personality fit
- AC2: Ideas reference previous ideas (conversation threading)
- AC3: Brainstorm tracks turn order and participation metrics
- AC4: Session generates diverse ideas leveraging different personalities
- AC5: Brainstorm state observable and serializable to JSON
"""

import pytest
from src.collaboration.brainstorming import (
    BrainstormingFacilitator,
    BrainstormPhase,
    BrainstormSession,
    BrainstormTurn,
    run_brainstorm_round,
)
from src.collaboration.context import IdeaCategory, SharedContext


class TestBrainstormTurn:
    """Tests for BrainstormTurn."""

    def test_turn_creation(self):
        """Turn can be created with agent and idea."""
        turn = BrainstormTurn(
            turn_number=1,
            agent_name="Athena",
            phase=BrainstormPhase.IDEATION,
            idea_content="Use microservices",
            category=IdeaCategory.APPROACH,
        )
        assert turn.turn_number == 1
        assert turn.agent_name == "Athena"
        assert turn.idea_content == "Use microservices"

    def test_turn_has_timestamp(self):
        """Turn records when it occurred."""
        turn = BrainstormTurn(
            turn_number=1,
            agent_name="Athena",
            phase=BrainstormPhase.IDEATION,
        )
        assert turn.timestamp is not None

    def test_turn_references_previous_ideas(self):
        """AC2: Turn can reference previous ideas."""
        turn = BrainstormTurn(
            turn_number=2,
            agent_name="Cato",
            phase=BrainstormPhase.BUILDING,
            idea_content="Add caching layer",
            references_ideas=["idea-1", "idea-2"],
        )
        assert "idea-1" in turn.references_ideas
        assert "idea-2" in turn.references_ideas

    def test_turn_to_dict(self):
        """AC5: Turn serializable to dict."""
        turn = BrainstormTurn(
            turn_number=1,
            agent_name="Athena",
            phase=BrainstormPhase.IDEATION,
            idea_content="Test idea",
        )
        turn_dict = turn.to_dict()
        assert turn_dict["turn_number"] == 1
        assert turn_dict["agent_name"] == "Athena"
        assert turn_dict["phase"] == "ideation"


class TestBrainstormSession:
    """Tests for BrainstormSession."""

    def test_session_creation(self):
        """Session can be created."""
        context = SharedContext(topic="Design", problem_statement="Design API")
        session = BrainstormSession(context=context)
        assert session.context.topic == "Design"
        assert session.is_active

    def test_add_agents_to_session(self):
        """AC1: Agents added to session."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])
        assert len(session.agent_names) == 3
        assert "Athena" in session.agent_names

    def test_get_current_agent(self):
        """AC1: Can identify current agent for turn."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])
        assert session.get_current_agent() == "Athena"

    def test_agent_rotation(self):
        """AC1: Agents take turns in rotation."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])

        agents_order = []
        for _ in range(6):
            agents_order.append(session.get_current_agent())
            session.next_agent()

        # Should cycle through all agents twice
        assert agents_order == [
            "Athena",
            "Cato",
            "Zephyr",
            "Athena",
            "Cato",
            "Zephyr",
        ]

    def test_add_turn_contributes_idea(self):
        """AC1: Adding turn contributes idea to context."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])

        turn, idea = session.add_turn(
            agent_name="Athena",
            idea_content="Use REST API",
            category=IdeaCategory.APPROACH,
        )

        assert turn.turn_number == 1
        assert turn.agent_name == "Athena"
        assert idea.content == "Use REST API"
        assert idea.id in session.context.ideas

    def test_turn_references_previous_ideas(self):
        """AC2: Turns can reference previous ideas (threading)."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])

        turn1, idea1 = session.add_turn(
            "Athena", "Core idea", category=IdeaCategory.CORE_CONCEPT
        )
        turn2, idea2 = session.add_turn(
            "Cato",
            "Build on core",
            category=IdeaCategory.DETAIL,
            references_ideas=[idea1.id],
        )

        assert idea1.id in turn2.references_ideas
        assert idea1.id in idea2.builds_on

    def test_get_turn_history(self):
        """AC3: Track turn order."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])

        session.add_turn("Athena", "Idea 1", category=IdeaCategory.CORE_CONCEPT)
        session.add_turn("Cato", "Idea 2", category=IdeaCategory.APPROACH)
        session.add_turn("Athena", "Idea 3", category=IdeaCategory.DETAIL)

        history = session.get_turn_history()
        assert len(history) == 3
        assert history[0].turn_number == 1
        assert history[1].turn_number == 2
        assert history[2].turn_number == 3

    def test_participation_metrics(self):
        """AC3: Track participation by agent."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])

        session.add_turn("Athena", "Idea 1", category=IdeaCategory.CORE_CONCEPT)
        session.add_turn("Cato", "Idea 2", category=IdeaCategory.APPROACH)
        session.add_turn("Athena", "Idea 3", category=IdeaCategory.DETAIL)
        session.add_turn("Zephyr", "Idea 4", category=IdeaCategory.INSIGHT)

        metrics = session.get_participation_metrics()
        assert metrics["Athena"] == 2
        assert metrics["Cato"] == 1
        assert metrics["Zephyr"] == 1

    def test_diversity_metrics(self):
        """AC4: Measure diversity of ideas."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])

        session.add_turn("Athena", "Core idea", category=IdeaCategory.CORE_CONCEPT)
        session.add_turn("Cato", "Approach", category=IdeaCategory.APPROACH)
        session.add_turn("Athena", "Detail", category=IdeaCategory.DETAIL)

        diversity = session.get_diversity_metrics()
        assert diversity["total_ideas"] == 3
        assert diversity["ideas_by_category"]["core_concept"] == 1
        assert diversity["ideas_by_category"]["approach"] == 1
        assert diversity["ideas_by_category"]["detail"] == 1

    def test_diversity_counts_references(self):
        """AC4: Diversity counts conversation threading."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])

        turn1, idea1 = session.add_turn(
            "Athena", "Core", category=IdeaCategory.CORE_CONCEPT
        )
        turn2, idea2 = session.add_turn(
            "Cato",
            "Build on core",
            category=IdeaCategory.DETAIL,
            references_ideas=[idea1.id],
        )

        diversity = session.get_diversity_metrics()
        assert diversity["total_references"] >= 1

    def test_phase_transitions(self):
        """Session can transition through brainstorm phases."""
        session = BrainstormSession()
        assert session.current_phase == BrainstormPhase.OPENING

        session.set_phase(BrainstormPhase.IDEATION)
        assert session.current_phase == BrainstormPhase.IDEATION

        session.set_phase(BrainstormPhase.SYNTHESIS)
        assert session.current_phase == BrainstormPhase.SYNTHESIS

    def test_conclude_session(self):
        """AC1: Session can be concluded."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])
        session.add_turn("Athena", "Idea 1", category=IdeaCategory.CORE_CONCEPT)

        assert session.is_active
        session.conclude_session()
        assert not session.is_active

    def test_session_to_dict(self):
        """AC5: Session state serializable to JSON."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])
        session.add_turn("Athena", "Idea 1", category=IdeaCategory.CORE_CONCEPT)

        session_dict = session.to_dict()
        assert session_dict["agent_names"] == ["Athena", "Cato"]
        assert session_dict["current_turn"] == 1
        assert session_dict["is_active"] is True
        assert isinstance(session_dict["turns"], list)
        assert isinstance(session_dict["participation"], dict)

    def test_session_summary(self):
        """Session provides human-readable summary."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])
        session.add_turn("Athena", "Idea 1", category=IdeaCategory.CORE_CONCEPT)
        session.add_turn("Cato", "Idea 2", category=IdeaCategory.APPROACH)

        summary = session.get_summary()
        assert "BRAINSTORMING" in summary
        assert "Athena" in summary
        assert "Cato" in summary


class TestBrainstormingFacilitator:
    """Tests for BrainstormingFacilitator."""

    def test_create_session(self):
        """AC1: Facilitator creates brainstorming session."""
        facilitator = BrainstormingFacilitator()
        session = facilitator.create_session(
            topic="API Design",
            problem_statement="Design a REST API",
            agents=["Athena", "Cato"],
        )

        assert session is not None
        assert session.context.topic == "API Design"
        assert "Athena" in session.agent_names

    def test_get_session(self):
        """Facilitator can retrieve session by ID."""
        facilitator = BrainstormingFacilitator()
        session = facilitator.create_session("Test", "Problem", ["Athena"])

        retrieved = facilitator.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    def test_list_active_sessions(self):
        """Facilitator lists active sessions."""
        facilitator = BrainstormingFacilitator()
        session1 = facilitator.create_session("Topic 1", "Problem 1", ["Athena"])
        session2 = facilitator.create_session("Topic 2", "Problem 2", ["Cato"])

        active = facilitator.list_active_sessions()
        assert session1.session_id in active
        assert session2.session_id in active

    def test_get_session_stats(self):
        """Facilitator provides session statistics."""
        facilitator = BrainstormingFacilitator()
        session = facilitator.create_session("Design", "Problem", ["Athena", "Cato"])
        session.add_turn("Athena", "Idea 1", category=IdeaCategory.CORE_CONCEPT)
        session.add_turn("Cato", "Idea 2", category=IdeaCategory.APPROACH)

        stats = facilitator.get_session_stats(session.session_id)
        assert stats["topic"] == "Design"
        assert stats["total_turns"] == 2
        assert stats["total_ideas"] == 2


class TestBrainstormRound:
    """Tests for brainstorm round execution."""

    def test_run_brainstorm_round(self):
        """AC1: Run full brainstorm round with all agents."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])

        agent_ideas = {
            "Athena": ("Systematic approach", IdeaCategory.APPROACH, []),
            "Cato": ("Practical solution", IdeaCategory.DETAIL, []),
            "Zephyr": ("Creative idea", IdeaCategory.INSIGHT, []),
        }

        turns = run_brainstorm_round(session, agent_ideas)

        assert len(turns) == 3
        assert turns[0].agent_name == "Athena"
        assert turns[1].agent_name == "Cato"
        assert turns[2].agent_name == "Zephyr"

    def test_brainstorm_round_with_references(self):
        """AC2: Round supports idea threading."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])

        # First round: just initial ideas
        agent_ideas_1 = {
            "Athena": ("Core idea", IdeaCategory.CORE_CONCEPT, []),
        }
        turns1 = run_brainstorm_round(session, agent_ideas_1)
        core_id = turns1[0].idea_contributed

        # Second round: build on first
        agent_ideas_2 = {
            "Cato": ("Build on core", IdeaCategory.DETAIL, [core_id]),
        }
        turns2 = run_brainstorm_round(session, agent_ideas_2)

        assert core_id in turns2[0].references_ideas


class TestAcceptanceCriteria:
    """Comprehensive acceptance criteria tests."""

    def test_ac1_agents_take_turns(self):
        """AC1: Agents take turns contributing ideas."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])

        # Each agent takes a turn
        session.add_turn("Athena", "Idea A", category=IdeaCategory.APPROACH)
        session.add_turn("Cato", "Idea C", category=IdeaCategory.CORE_CONCEPT)
        session.add_turn("Zephyr", "Idea Z", category=IdeaCategory.INSIGHT)

        assert len(session.turns) == 3
        assert session.turns[0].agent_name == "Athena"
        assert session.turns[1].agent_name == "Cato"
        assert session.turns[2].agent_name == "Zephyr"

    def test_ac2_ideas_reference_previous(self):
        """AC2: Ideas reference previous ideas (conversation threading)."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])

        turn1, idea1 = session.add_turn(
            "Athena", "First idea", category=IdeaCategory.CORE_CONCEPT
        )
        turn2, idea2 = session.add_turn(
            "Cato",
            "Second idea",
            category=IdeaCategory.DETAIL,
            references_ideas=[idea1.id],
        )
        turn3, idea3 = session.add_turn(
            "Athena",
            "Third idea",
            category=IdeaCategory.APPROACH,
            references_ideas=[idea2.id],
        )

        # Check threading
        assert idea1.id in idea2.builds_on
        assert idea2.id in idea3.builds_on

    def test_ac3_tracks_turns_and_participation(self):
        """AC3: Brainstorm tracks turn order and participation metrics."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])

        session.add_turn("Athena", "Idea 1", category=IdeaCategory.CORE_CONCEPT)
        session.add_turn("Cato", "Idea 2", category=IdeaCategory.APPROACH)
        session.add_turn("Athena", "Idea 3", category=IdeaCategory.DETAIL)
        session.add_turn("Zephyr", "Idea 4", category=IdeaCategory.INSIGHT)

        # Check turn history
        history = session.get_turn_history()
        assert len(history) == 4
        assert history[0].turn_number == 1
        assert history[3].turn_number == 4

        # Check participation
        metrics = session.get_participation_metrics()
        assert metrics["Athena"] == 2
        assert metrics["Cato"] == 1
        assert metrics["Zephyr"] == 1

    def test_ac4_generates_diverse_ideas(self):
        """AC4: Session generates diverse ideas from different personalities."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato", "Zephyr"])

        # Each agent contributes different idea types
        session.add_turn(
            "Athena", "Architectural approach", category=IdeaCategory.APPROACH
        )
        session.add_turn("Cato", "Implementation detail", category=IdeaCategory.DETAIL)
        session.add_turn("Zephyr", "Creative solution", category=IdeaCategory.INSIGHT)

        diversity = session.get_diversity_metrics()
        assert diversity["ideas_by_category"]["approach"] == 1
        assert diversity["ideas_by_category"]["detail"] == 1
        assert diversity["ideas_by_category"]["insight"] == 1

    def test_ac5_state_json_serializable(self):
        """AC5: Observable brainstorm state serializable to JSON."""
        session = BrainstormSession()
        session.add_agents(["Athena", "Cato"])
        session.add_turn("Athena", "Idea 1", category=IdeaCategory.APPROACH)
        session.add_turn("Cato", "Idea 2", category=IdeaCategory.DETAIL)

        session_dict = session.to_dict()

        # Verify all fields are JSON-serializable types
        assert isinstance(session_dict["session_id"], str)
        assert isinstance(session_dict["agent_names"], list)
        assert isinstance(session_dict["current_turn"], int)
        assert isinstance(session_dict["is_active"], bool)
        assert isinstance(session_dict["turns"], list)
        assert isinstance(session_dict["context"], dict)

        # Verify turns are dicts (not objects)
        for turn in session_dict["turns"]:
            assert isinstance(turn, dict)
            assert "turn_number" in turn
            assert "agent_name" in turn
