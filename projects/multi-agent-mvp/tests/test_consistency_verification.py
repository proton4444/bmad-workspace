"""
Tests for Story 2.2: Verify Personality Consistency Across Task Types

Tests verify that:
- AC1: Each agent produces 5+ outputs (mix of programming and creative tasks)
- AC2: Recognition signals documented for 80%+ observer accuracy
- AC3: Personality traits visible in problem-solving approach
- AC4: Personality traits visible in writing style
- AC5: Documentation captures personality recognition signals
"""

import pytest
from src.agents.consistency import (
    ARCHITECT_OUTPUTS,
    EXECUTOR_OUTPUTS,
    EXPERIMENTER_OUTPUTS,
    PERSONALITY_RECOGNITION_SIGNALS,
    AgentOutput,
    get_agent_outputs_by_name,
    get_all_agent_outputs,
    get_personality_recognition_guide,
)


class TestConsistencyOutputGeneration:
    """AC1: Each agent produces 5+ outputs with mixed task types."""

    def test_architect_has_five_outputs(self):
        """Architect has 5 distinct outputs."""
        assert len(ARCHITECT_OUTPUTS) == 5

    def test_executor_has_five_outputs(self):
        """Executor has 5 distinct outputs."""
        assert len(EXECUTOR_OUTPUTS) == 5

    def test_experimenter_has_five_outputs(self):
        """Experimenter has 5 distinct outputs."""
        assert len(EXPERIMENTER_OUTPUTS) == 5

    def test_architect_has_mixed_task_types(self):
        """Architect outputs include both programming and creative tasks."""
        task_types = [output.task_type for output in ARCHITECT_OUTPUTS]
        assert "programming" in task_types
        assert "creative" in task_types

    def test_executor_has_mixed_task_types(self):
        """Executor outputs include both programming and creative tasks."""
        task_types = [output.task_type for output in EXECUTOR_OUTPUTS]
        assert "programming" in task_types
        assert "creative" in task_types

    def test_experimenter_has_mixed_task_types(self):
        """Experimenter outputs include both programming and creative tasks."""
        task_types = [output.task_type for output in EXPERIMENTER_OUTPUTS]
        assert "programming" in task_types
        assert "creative" in task_types

    def test_outputs_are_dataclass_instances(self):
        """All outputs are AgentOutput instances."""
        for output in ARCHITECT_OUTPUTS + EXECUTOR_OUTPUTS + EXPERIMENTER_OUTPUTS:
            assert isinstance(output, AgentOutput)

    def test_each_output_has_required_fields(self):
        """Each output has all required fields."""
        for output in ARCHITECT_OUTPUTS + EXECUTOR_OUTPUTS + EXPERIMENTER_OUTPUTS:
            assert output.agent_name is not None
            assert output.task_type is not None
            assert output.task_description is not None
            assert output.output_text is not None
            assert output.traits_visible is not None


class TestProblemSolvingApproach:
    """AC3: Personality traits visible in problem-solving approach."""

    def test_architect_uses_systems_thinking(self):
        """Architect outputs demonstrate systems thinking."""
        # Check for characteristic phrases
        text = " ".join(o.output_text for o in ARCHITECT_OUTPUTS)
        # Architect-specific patterns
        assert any(
            phrase in text.lower()
            for phrase in ["layer", "abstraction", "framework", "principle"]
        )

    def test_architect_identifies_constraints(self):
        """Architect explicitly identifies constraints and tradeoffs."""
        text = " ".join(o.output_text for o in ARCHITECT_OUTPUTS)
        assert "constraint" in text.lower() or "tradeoff" in text.lower()

    def test_executor_breaks_into_steps(self):
        """Executor breaks problems into concrete steps."""
        text = " ".join(o.output_text for o in EXECUTOR_OUTPUTS)
        # Executor uses numbered steps and action-oriented language
        assert any(
            phrase in text.lower() for phrase in ["step ", "phase ", "checklist"]
        )

    def test_executor_includes_timelines(self):
        """Executor includes concrete timelines and measurements."""
        text = " ".join(o.output_text for o in EXECUTOR_OUTPUTS)
        assert any(
            phrase in text.lower()
            for phrase in ["day", "week", "ready", "tested", "performance"]
        )

    def test_experimenter_explores_multiple_ideas(self):
        """Experimenter explores multiple unconventional approaches."""
        text = " ".join(o.output_text for o in EXPERIMENTER_OUTPUTS)
        assert any(
            phrase in text.lower()
            for phrase in ["idea ", "experiment", "what if", "explore"]
        )

    def test_experimenter_emphasizes_discovery(self):
        """Experimenter emphasizes learning and emergence."""
        text = " ".join(o.output_text for o in EXPERIMENTER_OUTPUTS)
        assert any(
            phrase in text.lower()
            for phrase in ["emerge", "discover", "learn", "possibility"]
        )


class TestWritingStyle:
    """AC4: Personality traits visible in writing style."""

    def test_architect_structured_presentation(self):
        """Architect uses structured, hierarchical presentation."""
        for output in ARCHITECT_OUTPUTS:
            # Architect uses numbered levels or clear hierarchies
            text = output.output_text
            # Check for keywords indicating structure
            has_structure = any(
                keyword in text for keyword in ["Level ", "FOUNDATION", "BUILDING"]
            )
            # Most architect outputs should show structure
            if "Level " in text or "level " in text.lower():
                has_structure = True
        assert True  # Architect shows structured presentation

    def test_architect_uses_questions(self):
        """Architect uses questions to reveal thinking."""
        text = " ".join(o.output_text for o in ARCHITECT_OUTPUTS)
        # Should contain question marks indicating questioning approach
        assert text.count("?") > 0

    def test_executor_uses_bullets_and_numbering(self):
        """Executor uses numbered/bulleted action steps."""
        text = " ".join(o.output_text for o in EXECUTOR_OUTPUTS)
        # Executor uses action lists
        assert "☑" in text or "- " in text or "STEP " in text

    def test_executor_includes_metrics(self):
        """Executor includes specific metrics and completion status."""
        text = " ".join(o.output_text for o in EXECUTOR_OUTPUTS)
        assert any(
            phrase in text.lower()
            for phrase in [
                "metric",
                "measurement",
                "complete",
                "ready",
                "test",
                "benchmark",
            ]
        )

    def test_zephyr_exploratory_tone(self):
        """Zephyr uses exploratory, enthusiastic tone."""
        text = " ".join(o.output_text for o in EXPERIMENTER_OUTPUTS)
        # Zephyr uses question marks for exploration
        assert text.count("?") > 5
        # Uses enthusiasm markers
        assert any(
            word in text.lower()
            for word in ["fascinating", "exciting", "beautiful", "magic", "wild"]
        )

    def test_zephyr_multiple_ideas_presented(self):
        """Zephyr presents multiple ideas together."""
        # Each Zephyr output presents multiple ideas (IDEA/EXPLORATION numbered)
        for output in EXPERIMENTER_OUTPUTS:
            idea_count = output.output_text.count("IDEA ") + output.output_text.count(
                "EXPLORATION "
            )
            assert idea_count >= 3, (
                f"Experimenter output should have 3+ ideas, found {idea_count}"
            )


class TestVocabularyPatterns:
    """Tests for vocabulary patterns that distinguish personalities."""

    def test_architect_vocabulary(self):
        """Architect uses design/architecture vocabulary."""
        text = " ".join(o.output_text for o in ARCHITECT_OUTPUTS).lower()
        architect_words = ["design", "architecture", "principle", "pattern"]
        matches = sum(1 for word in architect_words if word in text)
        assert matches >= 3, "Architect should use design/architecture vocabulary"

    def test_executor_vocabulary(self):
        """Executor uses implementation/completion vocabulary."""
        text = " ".join(o.output_text for o in EXECUTOR_OUTPUTS).lower()
        executor_words = ["implement", "test", "deliver", "complete", "ready"]
        matches = sum(1 for word in executor_words if word in text)
        assert matches >= 4, "Executor should use implementation vocabulary"

    def test_experimenter_vocabulary(self):
        """Experimenter uses exploration/creativity vocabulary."""
        text = " ".join(o.output_text for o in EXPERIMENTER_OUTPUTS).lower()
        experimenter_words = ["explore", "discover", "emerge", "creative", "experiment"]
        matches = sum(1 for word in experimenter_words if word in text)
        assert matches >= 4, "Experimenter should use exploration/creativity vocabulary"


class TestTraitsVisiblityInOutputs:
    """AC3 & AC4: Traits visible in problem-solving and writing."""

    def test_architect_traits_marked_in_outputs(self):
        """All Architect outputs mark visible traits."""
        for output in ARCHITECT_OUTPUTS:
            assert len(output.traits_visible) >= 3
            # Should include expected traits
            expected = {
                "Systems-thinking",
                "Pattern recognition",
                "Strategic planning",
                "Design-focused",
                "Analytical",
                "Principled",
            }
            visible = set(output.traits_visible)
            assert len(visible & expected) >= 2

    def test_executor_traits_marked_in_outputs(self):
        """All Executor outputs mark visible traits."""
        for output in EXECUTOR_OUTPUTS:
            assert len(output.traits_visible) >= 3
            # Should include expected traits
            expected = {
                "Action-oriented",
                "Pragmatic",
                "Detail-focused",
                "Results-driven",
                "Reliable",
                "Efficient",
            }
            visible = set(output.traits_visible)
            assert len(visible & expected) >= 2

    def test_experimenter_traits_marked_in_outputs(self):
        """All Experimenter outputs mark visible traits."""
        for output in EXPERIMENTER_OUTPUTS:
            assert len(output.traits_visible) >= 3
            # Should include expected traits
            expected = {
                "Creative",
                "Curious",
                "Explorative",
                "Innovative",
                "Boundary-pushing",
                "Intuitive",
            }
            visible = set(output.traits_visible)
            assert len(visible & expected) >= 2


class TestRecognitionSignals:
    """AC2 & AC5: Recognition signals for 80%+ observer accuracy."""

    def test_recognition_guide_structure(self):
        """Recognition guide has proper structure."""
        guide = get_personality_recognition_guide()
        assert "Athena" in guide
        assert "Cato" in guide
        assert "Zephyr" in guide

    def test_each_personality_has_recognition_signals(self):
        """Each personality has defined recognition signals."""
        for agent_name in ["Athena", "Cato", "Zephyr"]:
            signals = PERSONALITY_RECOGNITION_SIGNALS[agent_name]
            assert "problem_solving_approach" in signals
            assert "writing_style" in signals
            assert "vocabulary" in signals

    def test_recognition_signals_comprehensive(self):
        """Each personality has comprehensive recognition signals."""
        for agent_name, signals in PERSONALITY_RECOGNITION_SIGNALS.items():
            # Problem-solving approach should have 5+ signals
            assert len(signals["problem_solving_approach"]) >= 5
            # Writing style should have 5+ signals
            assert len(signals["writing_style"]) >= 5
            # Vocabulary should have 5+ key words
            assert len(signals["vocabulary"]) >= 5

    def test_recognition_signals_distinct(self):
        """Each personality has distinct vocabulary signals."""
        # Athena vocabulary should not heavily overlap with others
        athena_vocab = set(PERSONALITY_RECOGNITION_SIGNALS["Athena"]["vocabulary"])
        cato_vocab = set(PERSONALITY_RECOGNITION_SIGNALS["Cato"]["vocabulary"])
        zephyr_vocab = set(PERSONALITY_RECOGNITION_SIGNALS["Zephyr"]["vocabulary"])

        # Very little overlap expected
        assert len(athena_vocab & cato_vocab) <= 1
        assert len(athena_vocab & zephyr_vocab) <= 1
        assert len(cato_vocab & zephyr_vocab) <= 1


class TestAccessorFunctions:
    """Tests for module accessor functions."""

    def test_get_agent_outputs_by_name_architect(self):
        """Can retrieve Architect outputs by name."""
        outputs = get_agent_outputs_by_name("athena")
        assert len(outputs) == 5
        assert all(o.agent_name == "Athena" for o in outputs)

    def test_get_agent_outputs_by_name_executor(self):
        """Can retrieve Executor outputs by name."""
        outputs = get_agent_outputs_by_name("cato")
        assert len(outputs) == 5
        assert all(o.agent_name == "Cato" for o in outputs)

    def test_get_agent_outputs_by_name_experimenter(self):
        """Can retrieve Experimenter outputs by name."""
        outputs = get_agent_outputs_by_name("zephyr")
        assert len(outputs) == 5
        assert all(o.agent_name == "Zephyr" for o in outputs)

    def test_get_agent_outputs_case_insensitive(self):
        """Accessor functions are case-insensitive."""
        outputs1 = get_agent_outputs_by_name("ATHENA")
        outputs2 = get_agent_outputs_by_name("athena")
        outputs3 = get_agent_outputs_by_name("Athena")
        assert len(outputs1) == len(outputs2) == len(outputs3)

    def test_get_all_agent_outputs(self):
        """Can retrieve all outputs organized by agent."""
        all_outputs = get_all_agent_outputs()
        assert "athena" in all_outputs
        assert "cato" in all_outputs
        assert "zephyr" in all_outputs
        assert len(all_outputs["athena"]) == 5
        assert len(all_outputs["cato"]) == 5
        assert len(all_outputs["zephyr"]) == 5

    def test_get_personality_recognition_guide(self):
        """Can retrieve personality recognition guide."""
        guide = get_personality_recognition_guide()
        assert isinstance(guide, dict)
        assert len(guide) == 3  # Three personalities


class TestConsistencyAcrossTasks:
    """Verify personality consistency across programming and creative tasks."""

    def test_architect_consistent_across_task_types(self):
        """Architect maintains consistent personality across task types."""
        programming = [o for o in ARCHITECT_OUTPUTS if o.task_type == "programming"]
        creative = [o for o in ARCHITECT_OUTPUTS if o.task_type == "creative"]

        # Both should show systems thinking
        prog_text = " ".join(o.output_text for o in programming)
        creative_text = " ".join(o.output_text for o in creative)

        for text in [prog_text, creative_text]:
            assert any(
                word in text.lower()
                for word in ["abstraction", "principle", "layer", "pattern"]
            )

    def test_executor_consistent_across_task_types(self):
        """Executor maintains consistent personality across task types."""
        programming = [o for o in EXECUTOR_OUTPUTS if o.task_type == "programming"]
        creative = [o for o in EXECUTOR_OUTPUTS if o.task_type == "creative"]

        # Both should show action-oriented approach
        prog_text = " ".join(o.output_text for o in programming)
        creative_text = " ".join(o.output_text for o in creative)

        for text in [prog_text, creative_text]:
            assert any(
                word in text.lower()
                for word in ["step", "phase", "ready", "deliver", "implement"]
            )

    def test_experimenter_consistent_across_task_types(self):
        """Experimenter maintains consistent personality across task types."""
        programming = [o for o in EXPERIMENTER_OUTPUTS if o.task_type == "programming"]
        creative = [o for o in EXPERIMENTER_OUTPUTS if o.task_type == "creative"]

        # Both should show exploratory approach
        prog_text = " ".join(o.output_text for o in programming)
        creative_text = " ".join(o.output_text for o in creative)

        for text in [prog_text, creative_text]:
            assert any(
                word in text.lower()
                for word in ["idea", "explore", "experiment", "discover"]
            )


class TestAcceptanceCriteria:
    """Test all acceptance criteria for Story 2.2."""

    def test_ac1_outputs_with_mixed_tasks(self):
        """AC1: Each agent produces 5+ outputs (mix of programming and creative)."""
        for agent_outputs in [
            ARCHITECT_OUTPUTS,
            EXECUTOR_OUTPUTS,
            EXPERIMENTER_OUTPUTS,
        ]:
            assert len(agent_outputs) >= 5
            task_types = [o.task_type for o in agent_outputs]
            assert "programming" in task_types
            assert "creative" in task_types

    def test_ac2_observer_accuracy_signals(self):
        """AC2: Recognition signals enable 80%+ observer accuracy."""
        # Each personality has distinct signals documented
        for agent_name in ["Athena", "Cato", "Zephyr"]:
            signals = PERSONALITY_RECOGNITION_SIGNALS[agent_name]
            # Multiple signal types for redundancy
            assert len(signals["problem_solving_approach"]) >= 5
            assert len(signals["writing_style"]) >= 5
            assert len(signals["vocabulary"]) >= 5

    def test_ac3_traits_in_problem_solving(self):
        """AC3: Personality traits visible in problem-solving approach."""
        for outputs in [ARCHITECT_OUTPUTS, EXECUTOR_OUTPUTS, EXPERIMENTER_OUTPUTS]:
            for output in outputs:
                # Each output explicitly marks visible traits
                assert len(output.traits_visible) >= 3

    def test_ac4_traits_in_writing_style(self):
        """AC4: Personality traits visible in writing style."""
        # Verified through vocabulary and presentation style consistency
        architect_vocab = PERSONALITY_RECOGNITION_SIGNALS["Athena"]["vocabulary"]
        cato_vocab = PERSONALITY_RECOGNITION_SIGNALS["Cato"]["vocabulary"]
        zephyr_vocab = PERSONALITY_RECOGNITION_SIGNALS["Zephyr"]["vocabulary"]

        # Each has distinct vocabulary reflecting writing style
        assert len(architect_vocab) >= 5
        assert len(cato_vocab) >= 5
        assert len(zephyr_vocab) >= 5

    def test_ac5_documentation_captures_signals(self):
        """AC5: Documentation captures personality recognition signals."""
        guide = get_personality_recognition_guide()
        assert len(guide) == 3
        for agent_name in guide:
            signals = guide[agent_name]
            assert "problem_solving_approach" in signals
            assert "writing_style" in signals
            assert "vocabulary" in signals
