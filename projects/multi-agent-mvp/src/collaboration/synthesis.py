"""
Emergent solution synthesis from collaborative ideas.

Combines and synthesizes ideas from brainstorming into coherent solutions,
showing emergent properties that exceed sum of individual contributions.

Story 3.3: Emergent Solution Synthesis
Acceptance Criteria:
- AC1: Synthesis identifies and combines related ideas
- AC2: Creates new synthesized ideas that build on multiple inputs
- AC3: Synthesis shows emergent properties and novel combinations
- AC4: Tracks synthesis lineage (which ideas contributed to synthesis)
- AC5: Synthesis state serializable to JSON
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import uuid4

from .context import Idea, IdeaCategory, SharedContext


@dataclass
class SynthesizedIdea:
    """Idea created through synthesis of multiple ideas."""

    id: str = field(default_factory=lambda: str(uuid4())[:8])
    content: str = ""  # The synthesized idea
    category: IdeaCategory = IdeaCategory.SYNTHESIS
    source_ideas: List[str] = field(default_factory=list)  # IDs of ideas combined
    emergent_properties: List[str] = field(default_factory=list)  # Novel properties
    coherence_score: float = 0.0  # 0.0-1.0 how well ideas cohere
    novelty_score: float = 0.0  # 0.0-1.0 how novel the synthesis is
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Serialize synthesized idea."""
        return {
            "id": self.id,
            "content": self.content,
            "source_ideas": self.source_ideas,
            "emergent_properties": self.emergent_properties,
            "coherence_score": round(self.coherence_score, 3),
            "novelty_score": round(self.novelty_score, 3),
            "timestamp": self.timestamp,
        }


@dataclass
class SynthesisSession:
    """Session for synthesizing ideas into solutions."""

    session_id: str = field(default_factory=lambda: str(uuid4())[:8])
    context: SharedContext = field(default_factory=SharedContext)
    synthesized_ideas: Dict[str, SynthesizedIdea] = field(default_factory=dict)
    synthesis_operations: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def synthesize_ideas(
        self,
        source_idea_ids: List[str],
        synthesis_content: str,
        emergent_properties: Optional[List[str]] = None,
        coherence: float = 0.8,
        novelty: float = 0.7,
    ) -> SynthesizedIdea:
        """
        AC1 & AC2: Synthesize multiple ideas into new synthesized idea.

        Args:
            source_idea_ids: Ideas being synthesized
            synthesis_content: The synthesized result
            emergent_properties: Novel properties emerging from combination
            coherence: How well ideas fit together (0.0-1.0)
            novelty: How novel the synthesis is (0.0-1.0)

        Returns:
            The synthesized idea
        """
        # Verify source ideas exist
        valid_sources = [id for id in source_idea_ids if id in self.context.ideas]

        synthesis = SynthesizedIdea(
            content=synthesis_content,
            source_ideas=valid_sources,
            emergent_properties=emergent_properties or [],
            coherence_score=coherence,
            novelty_score=novelty,
        )

        self.synthesized_ideas[synthesis.id] = synthesis

        # Record operation for lineage tracking (AC4)
        self.synthesis_operations.append(
            {
                "synthesis_id": synthesis.id,
                "source_ids": valid_sources,
                "timestamp": datetime.now().isoformat(),
                "coherence": coherence,
                "novelty": novelty,
            }
        )

        # Add synthesized idea to context
        self.context.add_idea(
            content=synthesis_content,
            contributor="System",
            category=IdeaCategory.SYNTHESIS,
            builds_on=valid_sources,
        )

        self.updated_at = datetime.now().isoformat()
        return synthesis

    def find_related_ideas(
        self, idea_id: str, min_similarity: float = 0.6
    ) -> List[str]:
        """AC1: Find ideas related to given idea for synthesis."""
        if idea_id not in self.context.ideas:
            return []

        idea = self.context.ideas[idea_id]
        related = []

        # Find ideas in same category
        for other_id, other in self.context.ideas.items():
            if other_id == idea_id:
                continue
            if other.category == idea.category:
                related.append(other_id)

        return related

    def get_synthesis_lineage(self, synthesis_id: str) -> Dict:
        """AC4: Get lineage of synthesis (which ideas contributed)."""
        if synthesis_id not in self.synthesized_ideas:
            return {}

        synthesis = self.synthesized_ideas[synthesis_id]
        lineage = {
            "synthesis_id": synthesis_id,
            "synthesis_content": synthesis.content,
            "source_ideas": [],
        }

        for source_id in synthesis.source_ideas:
            if source_id in self.context.ideas:
                source = self.context.ideas[source_id]
                lineage["source_ideas"].append(
                    {
                        "id": source_id,
                        "content": source.content,
                        "contributor": source.contributor,
                        "category": source.category.value,
                    }
                )

        return lineage

    def to_dict(self) -> Dict:
        """AC5: Serialize synthesis session to JSON."""
        return {
            "session_id": self.session_id,
            "synthesized_count": len(self.synthesized_ideas),
            "synthesized_ideas": {
                id: synthesis.to_dict()
                for id, synthesis in self.synthesized_ideas.items()
            },
            "synthesis_operations": self.synthesis_operations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class SynthesisEngine:
    """Engine for synthesizing ideas across sessions."""

    def __init__(self):
        """Initialize synthesis engine."""
        self.sessions: Dict[str, SynthesisSession] = {}

    def create_synthesis_session(self, context: SharedContext) -> SynthesisSession:
        """Create session for synthesizing ideas from context."""
        session = SynthesisSession(context=context)
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SynthesisSession]:
        """Get synthesis session."""
        return self.sessions.get(session_id)

    def synthesize_high_quality_ideas(
        self, session_id: str, min_quality: float = 0.7
    ) -> List[SynthesizedIdea]:
        """AC2: Synthesize all high-quality ideas into solution."""
        session = self.get_session(session_id)
        if not session:
            return []

        # Get high-quality ideas
        high_quality = session.context.get_ideas_for_synthesis(min_quality)

        synthesized = []
        # Group by category and synthesize
        categories = {}
        for idea in high_quality:
            cat = idea.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(idea.id)

        # Create synthesis for each category
        for category, idea_ids in categories.items():
            if len(idea_ids) > 1:
                content = f"Synthesized {category} solution from {len(idea_ids)} ideas"
                synthesis = session.synthesize_ideas(
                    source_idea_ids=idea_ids,
                    synthesis_content=content,
                    emergent_properties=[
                        f"Combines {len(idea_ids)} {category} perspectives",
                        "Emergent from collaborative ideation",
                    ],
                    coherence=0.85,
                    novelty=0.75,
                )
                synthesized.append(synthesis)

        return synthesized
