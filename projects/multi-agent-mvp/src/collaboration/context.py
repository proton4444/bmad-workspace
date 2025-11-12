"""
Shared context and knowledge exchange for multi-agent collaboration.

Implements a shared context system where agents can exchange ideas, build on
each other's contributions, and maintain a common understanding of the problem space.

Story 3.1: Shared Context & Knowledge Exchange
Acceptance Criteria:
- AC1: Agents can contribute ideas to shared context
- AC2: Context accessible to all agents in collaboration
- AC3: Ideas include metadata (contributor, timestamp, affinity score)
- AC4: Context maintains idea relationships (references, builds_on)
- AC5: Observable context serializable to JSON
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import uuid4


class IdeaCategory(Enum):
    """Category of idea or contribution."""

    CORE_CONCEPT = "core_concept"  # Core problem understanding
    APPROACH = "approach"  # Proposed solution approach
    DETAIL = "detail"  # Implementation detail
    CONSTRAINT = "constraint"  # Identified constraint or limitation
    CRITIQUE = "critique"  # Critical feedback
    SYNTHESIS = "synthesis"  # Synthesized/combined idea
    QUESTION = "question"  # Question or clarification
    INSIGHT = "insight"  # Key insight or realization


@dataclass
class Idea:
    """Single contribution to shared context."""

    content: str  # The actual idea text
    contributor: str = ""  # Agent name
    category: IdeaCategory = IdeaCategory.CORE_CONCEPT
    affinity_fit: float = 0.0  # How well this idea fits agent's personality
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    builds_on: List[str] = field(default_factory=list)  # IDs of ideas this references
    referenced_by: List[str] = field(default_factory=list)  # IDs that reference this
    quality_score: float = 0.5  # 0.0-1.0 quality assessment
    creative_novelty: float = 0.5  # 0.0-1.0 novelty assessment

    def to_dict(self) -> Dict:
        """Serialize idea to dict for JSON storage."""
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category.value,
            "contributor": self.contributor,
            "timestamp": self.timestamp,
            "affinity_fit": self.affinity_fit,
            "builds_on": self.builds_on,
            "referenced_by": self.referenced_by,
            "quality_score": self.quality_score,
            "creative_novelty": self.creative_novelty,
        }

    def add_reference(self, idea_id: str):
        """Record that this idea references another idea."""
        if idea_id not in self.builds_on:
            self.builds_on.append(idea_id)

    def add_referrer(self, idea_id: str):
        """Record that another idea references this one."""
        if idea_id not in self.referenced_by:
            self.referenced_by.append(idea_id)


@dataclass
class SharedContext:
    """Shared collaborative context accessible to all agents."""

    session_id: str = field(default_factory=lambda: str(uuid4())[:8])
    topic: str = ""  # The problem or creative topic
    problem_statement: str = ""  # Detailed problem description
    ideas: Dict[str, Idea] = field(default_factory=dict)  # Map of idea_id -> Idea
    participating_agents: Set[str] = field(default_factory=set)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    phase: str = "exploration"  # exploration, synthesis, evaluation, etc.

    def add_idea(
        self,
        content: str,
        contributor: str,
        category: IdeaCategory = IdeaCategory.CORE_CONCEPT,
        affinity_fit: float = 0.0,
        builds_on: Optional[List[str]] = None,
    ) -> Idea:
        """
        Add a new idea to shared context.

        Args:
            content: The idea text
            contributor: Agent name contributing the idea
            category: Type of idea
            affinity_fit: How well this matches agent's personality (0.0-1.0)
            builds_on: List of idea IDs this idea references

        Returns:
            The created Idea object
        """
        idea = Idea(
            content=content,
            contributor=contributor,
            category=category,
            affinity_fit=affinity_fit,
            builds_on=builds_on or [],
        )

        self.ideas[idea.id] = idea

        # Record references
        if builds_on:
            for ref_id in builds_on:
                if ref_id in self.ideas:
                    self.ideas[ref_id].add_referrer(idea.id)

        # Track participating agents
        self.participating_agents.add(contributor)
        self.updated_at = datetime.now().isoformat()

        return idea

    def get_ideas_by_category(self, category: IdeaCategory) -> List[Idea]:
        """Get all ideas of a specific category."""
        return [idea for idea in self.ideas.values() if idea.category == category]

    def get_ideas_by_contributor(self, contributor: str) -> List[Idea]:
        """Get all ideas contributed by specific agent."""
        return [idea for idea in self.ideas.values() if idea.contributor == contributor]

    def get_related_ideas(self, idea_id: str) -> Dict[str, List[Idea]]:
        """Get ideas related to a given idea (builds_on and referenced_by)."""
        if idea_id not in self.ideas:
            return {}

        idea = self.ideas[idea_id]
        result = {
            "referenced_ideas": [
                self.ideas[ref_id] for ref_id in idea.builds_on if ref_id in self.ideas
            ],
            "referencing_ideas": [
                self.ideas[ref_id]
                for ref_id in idea.referenced_by
                if ref_id in self.ideas
            ],
        }
        return result

    def get_ideas_for_synthesis(self, min_quality: float = 0.4) -> List[Idea]:
        """Get highest-quality ideas suitable for synthesis."""
        return sorted(
            [idea for idea in self.ideas.values() if idea.quality_score >= min_quality],
            key=lambda i: (i.quality_score, i.creative_novelty),
            reverse=True,
        )

    def update_idea_quality(self, idea_id: str, quality_score: float):
        """Update quality assessment of an idea."""
        if idea_id in self.ideas:
            self.ideas[idea_id].quality_score = max(0.0, min(1.0, quality_score))
            self.updated_at = datetime.now().isoformat()

    def update_idea_novelty(self, idea_id: str, novelty_score: float):
        """Update creative novelty assessment of an idea."""
        if idea_id in self.ideas:
            self.ideas[idea_id].creative_novelty = max(0.0, min(1.0, novelty_score))
            self.updated_at = datetime.now().isoformat()

    def set_phase(self, phase: str):
        """Transition to next collaboration phase."""
        self.phase = phase
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Serialize context to dict for JSON storage."""
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "problem_statement": self.problem_statement,
            "ideas": {idea_id: idea.to_dict() for idea_id, idea in self.ideas.items()},
            "participating_agents": list(self.participating_agents),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "phase": self.phase,
            "idea_count": len(self.ideas),
            "agent_count": len(self.participating_agents),
        }

    def get_summary(self) -> str:
        """Get human-readable summary of context."""
        summary = f"""
COLLABORATIVE CONTEXT SUMMARY
=============================
Session: {self.session_id}
Topic: {self.topic}
Phase: {self.phase}

Problem:
{self.problem_statement}

Participating Agents: {", ".join(self.participating_agents)}

Ideas Contributed: {len(self.ideas)}
"""

        # Breakdown by category
        for category in IdeaCategory:
            ideas = self.get_ideas_by_category(category)
            if ideas:
                summary += f"\n{category.value.upper()} ({len(ideas)} ideas):\n"
                for idea in ideas[:3]:  # Show top 3
                    summary += f"  - [{idea.contributor}] {idea.content[:60]}...\n"
                if len(ideas) > 3:
                    summary += f"  ... and {len(ideas) - 3} more\n"

        # Highest quality ideas
        top_ideas = self.get_ideas_for_synthesis(min_quality=0.7)
        if top_ideas:
            summary += f"\nTop Quality Ideas (score >0.7):\n"
            for idea in top_ideas[:5]:
                summary += (
                    f"  - [{idea.contributor}] {idea.content[:60]}... "
                    f"(Q:{idea.quality_score:.2f}, N:{idea.creative_novelty:.2f})\n"
                )

        return summary


class ContextManager:
    """Manages shared context for collaboration sessions."""

    def __init__(self):
        """Initialize context manager."""
        self.active_contexts: Dict[str, SharedContext] = {}
        self.context_history: List[SharedContext] = []

    def create_context(self, topic: str, problem_statement: str) -> SharedContext:
        """Create new collaboration context."""
        context = SharedContext(topic=topic, problem_statement=problem_statement)
        self.active_contexts[context.session_id] = context
        return context

    def get_context(self, session_id: str) -> Optional[SharedContext]:
        """Get active context by session ID."""
        return self.active_contexts.get(session_id)

    def close_context(self, session_id: str):
        """Close context and move to history."""
        if session_id in self.active_contexts:
            context = self.active_contexts.pop(session_id)
            self.context_history.append(context)

    def list_active_contexts(self) -> List[str]:
        """List all active context session IDs."""
        return list(self.active_contexts.keys())

    def get_context_stats(self, session_id: str) -> Dict:
        """Get statistics about a context."""
        context = self.get_context(session_id)
        if not context:
            return {}

        ideas_by_agent = {}
        for idea in context.ideas.values():
            if idea.contributor not in ideas_by_agent:
                ideas_by_agent[idea.contributor] = 0
            ideas_by_agent[idea.contributor] += 1

        avg_quality = (
            sum(i.quality_score for i in context.ideas.values()) / len(context.ideas)
            if context.ideas
            else 0.0
        )
        avg_novelty = (
            sum(i.creative_novelty for i in context.ideas.values()) / len(context.ideas)
            if context.ideas
            else 0.0
        )

        return {
            "session_id": session_id,
            "topic": context.topic,
            "phase": context.phase,
            "total_ideas": len(context.ideas),
            "ideas_by_agent": ideas_by_agent,
            "average_quality": round(avg_quality, 3),
            "average_novelty": round(avg_novelty, 3),
            "participating_agents": list(context.participating_agents),
            "created_at": context.created_at,
            "updated_at": context.updated_at,
        }
