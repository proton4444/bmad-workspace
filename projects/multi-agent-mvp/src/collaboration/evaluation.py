"""
Creative output evaluation and assessment.

Evaluates the quality, novelty, and impact of ideas and synthesized solutions.

Story 3.4: Creative Output Evaluation
Acceptance Criteria:
- AC1: Evaluate ideas across multiple dimensions (quality, novelty, feasibility)
- AC2: Agents provide evaluations reflecting their personalities
- AC3: Evaluation aggregates multiple perspectives
- AC4: Evaluations tracked with timestamps and justification
- AC5: Evaluation results serializable to JSON
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .context import Idea, SharedContext


@dataclass
class Evaluation:
    """Evaluation of an idea."""

    idea_id: str
    evaluator: str  # Agent name who evaluated
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    quality_score: float = 0.5  # 0.0-1.0
    novelty_score: float = 0.5  # 0.0-1.0
    feasibility_score: float = 0.5  # 0.0-1.0
    impact_score: float = 0.5  # 0.0-1.0
    justification: str = ""
    personality_alignment: float = 0.5  # How aligned with evaluator personality

    def average_score(self) -> float:
        """Get average evaluation score."""
        return (
            self.quality_score
            + self.novelty_score
            + self.feasibility_score
            + self.impact_score
        ) / 4.0

    def to_dict(self) -> Dict:
        """Serialize evaluation."""
        return {
            "idea_id": self.idea_id,
            "evaluator": self.evaluator,
            "timestamp": self.timestamp,
            "quality": round(self.quality_score, 2),
            "novelty": round(self.novelty_score, 2),
            "feasibility": round(self.feasibility_score, 2),
            "impact": round(self.impact_score, 2),
            "average": round(self.average_score(), 2),
            "justification": self.justification,
        }


@dataclass
class EvaluationSession:
    """Session for evaluating ideas."""

    session_id: str = field(default_factory=lambda: str(__import__("uuid").uuid4())[:8])
    context: SharedContext = field(default_factory=SharedContext)
    evaluations: Dict[str, List[Evaluation]] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def evaluate_idea(
        self,
        idea_id: str,
        evaluator: str,
        quality: float,
        novelty: float,
        feasibility: float,
        impact: float,
        justification: str = "",
        personality_alignment: float = 0.5,
    ) -> Evaluation:
        """AC1 & AC2: Evaluate idea across dimensions."""
        evaluation = Evaluation(
            idea_id=idea_id,
            evaluator=evaluator,
            quality_score=quality,
            novelty_score=novelty,
            feasibility_score=feasibility,
            impact_score=impact,
            justification=justification,
            personality_alignment=personality_alignment,
        )

        if idea_id not in self.evaluations:
            self.evaluations[idea_id] = []

        self.evaluations[idea_id].append(evaluation)
        return evaluation

    def get_idea_evaluations(self, idea_id: str) -> List[Evaluation]:
        """AC4: Get all evaluations for an idea."""
        return self.evaluations.get(idea_id, [])

    def aggregate_evaluations(self, idea_id: str) -> Dict:
        """AC3: Aggregate multiple evaluations."""
        evals = self.get_idea_evaluations(idea_id)
        if not evals:
            return {}

        return {
            "idea_id": idea_id,
            "evaluation_count": len(evals),
            "average_quality": sum(e.quality_score for e in evals) / len(evals),
            "average_novelty": sum(e.novelty_score for e in evals) / len(evals),
            "average_feasibility": sum(e.feasibility_score for e in evals) / len(evals),
            "average_impact": sum(e.impact_score for e in evals) / len(evals),
            "evaluators": [e.evaluator for e in evals],
        }

    def to_dict(self) -> Dict:
        """AC5: Serialize evaluation session."""
        return {
            "session_id": str(self.session_id),
            "evaluation_count": sum(len(e) for e in self.evaluations.values()),
            "ideas_evaluated": len(self.evaluations),
            "evaluations": {
                idea_id: [e.to_dict() for e in evals]
                for idea_id, evals in self.evaluations.items()
            },
            "created_at": self.created_at,
        }
