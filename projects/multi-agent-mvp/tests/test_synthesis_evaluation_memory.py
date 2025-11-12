"""
Tests for Stories 3.3, 3.4, 3.5:
- Story 3.3: Emergent Solution Synthesis
- Story 3.4: Creative Output Evaluation
- Story 3.5: Collaborative Memory & Learning
"""

import pytest
from src.collaboration.context import IdeaCategory, SharedContext
from src.collaboration.evaluation import Evaluation, EvaluationSession
from src.collaboration.memory import CollaborationMemory, CollaborativeMemoryStore
from src.collaboration.synthesis import SynthesisEngine, SynthesisSession


class TestSynthesis:
    """Tests for Story 3.3: Emergent Solution Synthesis."""

    def test_synthesize_ideas(self):
        """AC1 & AC2: Synthesize multiple ideas."""
        context = SharedContext(topic="Design", problem_statement="Problem")
        context.add_idea("Idea 1", "Athena", category=IdeaCategory.APPROACH)
        context.add_idea("Idea 2", "Cato", category=IdeaCategory.DETAIL)

        session = SynthesisSession(context=context)
        idea_ids = list(context.ideas.keys())

        synthesis = session.synthesize_ideas(
            source_idea_ids=idea_ids,
            synthesis_content="Combined approach",
            emergent_properties=["Novel combination", "Emergent property"],
            coherence=0.85,
            novelty=0.75,
        )

        assert synthesis.id in session.synthesized_ideas
        assert len(synthesis.source_ideas) == 2
        assert synthesis.coherence_score == 0.85

    def test_find_related_ideas(self):
        """AC1: Find ideas related for synthesis."""
        context = SharedContext(topic="Design", problem_statement="Problem")
        idea1 = context.add_idea("Core idea", "Athena", category=IdeaCategory.APPROACH)
        idea2 = context.add_idea(
            "Another approach", "Cato", category=IdeaCategory.APPROACH
        )
        idea3 = context.add_idea("Detail", "Zephyr", category=IdeaCategory.DETAIL)

        session = SynthesisSession(context=context)
        related = session.find_related_ideas(idea1.id)

        assert idea2.id in related
        assert idea3.id not in related

    def test_synthesis_lineage(self):
        """AC4: Track synthesis lineage."""
        context = SharedContext(topic="Test", problem_statement="Problem")
        idea1 = context.add_idea("First", "Athena")
        idea2 = context.add_idea("Second", "Cato")

        session = SynthesisSession(context=context)
        synthesis = session.synthesize_ideas(
            source_idea_ids=[idea1.id, idea2.id],
            synthesis_content="Synthesis",
        )

        lineage = session.get_synthesis_lineage(synthesis.id)
        assert lineage["synthesis_id"] == synthesis.id
        assert len(lineage["source_ideas"]) == 2

    def test_synthesis_to_dict(self):
        """AC5: Serialize synthesis state to JSON."""
        context = SharedContext(topic="Test", problem_statement="Problem")
        idea = context.add_idea("Idea", "Athena")

        session = SynthesisSession(context=context)
        synthesis = session.synthesize_ideas(
            source_idea_ids=[idea.id],
            synthesis_content="Synthesis",
        )

        session_dict = session.to_dict()
        assert session_dict["synthesized_count"] == 1
        assert isinstance(session_dict["synthesized_ideas"], dict)

    def test_synthesis_engine(self):
        """AC3: Show emergent properties in synthesis."""
        context = SharedContext(topic="Test", problem_statement="Problem")
        # Add multiple ideas in same category so they can be synthesized together
        idea1 = context.add_idea("Approach 1", "Athena", category=IdeaCategory.APPROACH)
        idea2 = context.add_idea("Approach 2", "Cato", category=IdeaCategory.APPROACH)

        # Set high quality scores so they're included in synthesis
        idea1.quality_score = 0.85
        idea2.quality_score = 0.80

        engine = SynthesisEngine()
        session = engine.create_synthesis_session(context)

        synthesized = engine.synthesize_high_quality_ideas(
            session.session_id, min_quality=0.7
        )
        assert len(synthesized) > 0


class TestEvaluation:
    """Tests for Story 3.4: Creative Output Evaluation."""

    def test_evaluate_idea(self):
        """AC1: Evaluate ideas across dimensions."""
        session = EvaluationSession()
        idea_id = "test-idea"

        eval1 = session.evaluate_idea(
            idea_id=idea_id,
            evaluator="Athena",
            quality=0.85,
            novelty=0.90,
            feasibility=0.75,
            impact=0.80,
            justification="Strong approach",
        )

        assert eval1.idea_id == idea_id
        assert eval1.quality_score == 0.85
        assert eval1.evaluator == "Athena"

    def test_personality_aligned_evaluation(self):
        """AC2: Agents evaluate reflecting their personalities."""
        session = EvaluationSession()
        idea_id = "test-idea"

        # Architect evaluation (focuses on design)
        arch_eval = session.evaluate_idea(
            idea_id=idea_id,
            evaluator="Athena",
            quality=0.9,
            novelty=0.7,
            feasibility=0.8,
            impact=0.75,
            personality_alignment=0.95,  # High alignment
        )

        # Executor evaluation (focuses on feasibility)
        exec_eval = session.evaluate_idea(
            idea_id=idea_id,
            evaluator="Cato",
            quality=0.8,
            novelty=0.6,
            feasibility=0.95,
            impact=0.85,
            personality_alignment=0.90,
        )

        assert arch_eval.personality_alignment > exec_eval.novelty_score
        assert exec_eval.feasibility_score > arch_eval.novelty_score

    def test_aggregate_evaluations(self):
        """AC3: Aggregate multiple evaluations."""
        session = EvaluationSession()
        idea_id = "test-idea"

        session.evaluate_idea(idea_id, "Athena", 0.9, 0.8, 0.7, 0.8)
        session.evaluate_idea(idea_id, "Cato", 0.8, 0.7, 0.9, 0.85)
        session.evaluate_idea(idea_id, "Zephyr", 0.85, 0.95, 0.6, 0.75)

        aggregated = session.aggregate_evaluations(idea_id)
        assert aggregated["evaluation_count"] == 3
        assert len(aggregated["evaluators"]) == 3
        assert aggregated["average_quality"] > 0.8

    def test_evaluation_to_dict(self):
        """AC5: Serialize evaluation to JSON."""
        session = EvaluationSession()
        session.evaluate_idea(
            "idea-1", "Athena", 0.85, 0.90, 0.75, 0.80, justification="Good"
        )

        session_dict = session.to_dict()
        assert session_dict["evaluation_count"] == 1
        assert "idea-1" in session_dict["evaluations"]
        assert isinstance(session_dict["evaluations"]["idea-1"], list)


class TestMemory:
    """Tests for Story 3.5: Collaborative Memory & Learning."""

    def test_store_memory(self):
        """AC1: Store collaboration session memory."""
        store = CollaborativeMemoryStore()

        memory = store.store_memory(
            session_type="brainstorm",
            topic="Design",
            agents=["Athena", "Cato"],
            quality=0.85,
            ideas=8,
            success_indicators=["High participation", "Diverse ideas"],
            lessons=["Architect-Executor combo works well"],
        )

        assert memory.memory_id is not None
        assert memory.session_type == "brainstorm"
        assert len(store.memories) == 1

    def test_agent_history(self):
        """AC1: Retrieve agent collaboration history."""
        store = CollaborativeMemoryStore()

        store.store_memory("brainstorm", "Topic 1", ["Athena", "Cato"], 0.85, 5)
        store.store_memory("synthesis", "Topic 2", ["Athena", "Zephyr"], 0.80, 3)
        store.store_memory("evaluation", "Topic 1", ["Cato", "Zephyr"], 0.75, 2)

        athena_history = store.get_agent_history("Athena")
        assert athena_history["collaboration_count"] == 2
        assert athena_history["average_outcome_quality"] > 0.75

    def test_analyze_patterns(self):
        """AC2: Analyze patterns in collaboration data."""
        store = CollaborativeMemoryStore()

        store.store_memory("brainstorm", "Topic 1", ["Athena"], 0.85, 10)
        store.store_memory("brainstorm", "Topic 2", ["Cato"], 0.80, 8)
        store.store_memory("synthesis", "Topic 3", ["Zephyr"], 0.75, 3)

        patterns = store.analyze_patterns()
        assert patterns["total_sessions"] == 3
        assert patterns["session_types"]["brainstorm"]["count"] == 2
        assert "synthesis" in patterns["session_types"]

    def test_successful_patterns(self):
        """AC3: Identify successful collaboration approaches."""
        store = CollaborativeMemoryStore()

        # High quality
        store.store_memory(
            "brainstorm",
            "Success",
            ["Athena", "Cato"],
            0.90,
            15,
            success_indicators=["Great participation", "Novel ideas"],
        )
        # Low quality
        store.store_memory(
            "brainstorm",
            "Failure",
            ["Athena"],
            0.50,
            3,
            success_indicators=["Limited engagement"],
        )

        successful = store.get_successful_patterns(min_quality=0.75)
        assert len(successful) == 1
        assert successful[0]["agents"] == ["Athena", "Cato"]

    def test_extract_lessons(self):
        """AC4: Extract lessons learned."""
        store = CollaborativeMemoryStore()

        store.store_memory(
            "brainstorm",
            "Topic",
            ["Athena", "Cato"],
            0.85,
            10,
            lessons=[
                "Mixed personalities improve diversity",
                "Improve time management",
            ],
        )

        lessons = store.extract_lessons()
        assert len(lessons) == 2
        assert any("diversity" in l["lesson"].lower() for l in lessons)

    def test_memory_to_dict(self):
        """AC5: Serialize memory store to JSON."""
        store = CollaborativeMemoryStore()

        store.store_memory("brainstorm", "Topic", ["Athena", "Cato"], 0.85, 8)

        store_dict = store.to_dict()
        assert store_dict["total_memories"] == 1
        assert isinstance(store_dict["memories"], list)
        assert isinstance(store_dict["agent_stats"], dict)
        assert isinstance(store_dict["patterns"], dict)


class TestIntegration:
    """Integration tests across collaboration features."""

    def test_full_collaboration_workflow(self):
        """Test complete collaboration: brainstorm → synthesis → evaluate → remember."""
        # Start with context
        context = SharedContext(
            topic="Product Design",
            problem_statement="Design new feature",
        )

        # Add ideas from brainstorming
        idea1 = context.add_idea("Mobile-first", "Athena", IdeaCategory.APPROACH)
        idea2 = context.add_idea("API integration", "Cato", IdeaCategory.DETAIL)
        idea3 = context.add_idea("Interactive UX", "Zephyr", IdeaCategory.INSIGHT)

        # Synthesize
        synthesis_session = SynthesisSession(context=context)
        synthesis = synthesis_session.synthesize_ideas(
            source_idea_ids=[idea1.id, idea2.id, idea3.id],
            synthesis_content="Integrated mobile product with rich UX",
            emergent_properties=["Synergistic design", "Cross-domain integration"],
            coherence=0.88,
            novelty=0.85,
        )

        # Evaluate
        eval_session = EvaluationSession()
        eval_session.evaluate_idea(synthesis.id, "Athena", 0.9, 0.85, 0.8, 0.88)
        eval_session.evaluate_idea(synthesis.id, "Cato", 0.85, 0.80, 0.92, 0.87)

        aggregated = eval_session.aggregate_evaluations(synthesis.id)
        avg_quality = aggregated["average_quality"]

        # Remember
        memory_store = CollaborativeMemoryStore()
        memory = memory_store.store_memory(
            session_type="full_workflow",
            topic="Product Design",
            agents=["Athena", "Cato", "Zephyr"],
            quality=avg_quality,
            ideas=3,
            success_indicators=["Strong synthesis", "High quality evaluations"],
            lessons=["Cross-agent collaboration improves outcomes"],
        )

        # Verify complete workflow
        assert synthesis.coherence_score > 0.85
        assert aggregated["evaluation_count"] == 2
        assert memory.outcome_quality >= 0.8
        assert len(memory_store.memories) == 1


class TestAcceptanceCriteria:
    """Comprehensive acceptance criteria tests."""

    def test_story_33_synthesis(self):
        """Story 3.3 ACs: Synthesis works correctly."""
        context = SharedContext(topic="Test", problem_statement="Test")
        idea1 = context.add_idea("Idea 1", "Athena")
        idea2 = context.add_idea("Idea 2", "Cato")

        session = SynthesisSession(context=context)
        synthesis = session.synthesize_ideas(
            [idea1.id, idea2.id],
            "Synthesis",
            emergent_properties=["Property 1", "Property 2"],
        )

        # AC1, AC2: Combined and created
        assert len(synthesis.source_ideas) == 2
        # AC3: Emergent
        assert len(synthesis.emergent_properties) > 0
        # AC4: Lineage
        assert session.get_synthesis_lineage(synthesis.id) is not None
        # AC5: Serializable
        assert isinstance(session.to_dict(), dict)

    def test_story_34_evaluation(self):
        """Story 3.4 ACs: Evaluation works correctly."""
        session = EvaluationSession()

        eval1 = session.evaluate_idea("idea-1", "Athena", 0.9, 0.8, 0.7, 0.8)
        eval2 = session.evaluate_idea("idea-1", "Cato", 0.8, 0.7, 0.95, 0.85)

        # AC1: Multiple dimensions
        assert eval1.quality_score == 0.9
        assert eval1.novelty_score == 0.8
        # AC2: Personality reflected
        assert eval2.feasibility_score > eval1.feasibility_score
        # AC3: Aggregated
        agg = session.aggregate_evaluations("idea-1")
        assert agg["evaluation_count"] == 2
        # AC5: Serializable
        assert isinstance(session.to_dict(), dict)

    def test_story_35_memory(self):
        """Story 3.5 ACs: Memory works correctly."""
        store = CollaborativeMemoryStore()

        store.store_memory(
            "brainstorm",
            "Topic",
            ["Athena", "Cato"],
            0.85,
            10,
            lessons=["Lesson 1"],
        )

        # AC1: Store and retrieve
        memories = store.get_session_memories("brainstorm")
        assert len(memories) == 1
        # AC2: Patterns
        patterns = store.analyze_patterns()
        assert patterns["total_sessions"] == 1
        # AC3: Successful patterns
        successful = store.get_successful_patterns(0.7)
        assert len(successful) == 1
        # AC4: Lessons
        lessons = store.extract_lessons()
        assert len(lessons) == 1
        # AC5: Serializable
        assert isinstance(store.to_dict(), dict)
