"""
Multi-agent brainstorming session implementation.

Facilitates collaborative brainstorming where agents generate ideas,
build on each other's contributions, and explore solution space together.

Story 3.2: Multi-Agent Brainstorming Session
Acceptance Criteria:
- AC1: Agents take turns contributing ideas based on personality fit
- AC2: Ideas reference previous ideas (conversation threading)
- AC3: Brainstorm tracks turn order and participation metrics
- AC4: Session generates diverse ideas leveraging different personalities
- AC5: Brainstorm state observable and serializable to JSON
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from .context import Idea, IdeaCategory, SharedContext


class BrainstormPhase(Enum):
    """Phases of brainstorming session."""

    OPENING = "opening"  # Introduce problem, set context
    IDEATION = "ideation"  # Generate ideas
    BUILDING = "building"  # Build on ideas
    EVALUATION = "evaluation"  # Assess ideas
    SYNTHESIS = "synthesis"  # Combine ideas
    CLOSING = "closing"  # Wrap up, prepare for next phase


@dataclass
class BrainstormTurn:
    """Single turn in brainstorming session."""

    turn_number: int
    agent_name: str
    phase: BrainstormPhase
    idea_contributed: Optional[str] = None  # Idea ID if contributed
    idea_content: str = ""
    category: IdeaCategory = IdeaCategory.CORE_CONCEPT
    references_ideas: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reflection: str = ""  # Agent's reflection on the idea

    def to_dict(self) -> Dict:
        """Serialize turn to dict."""
        return {
            "turn_number": self.turn_number,
            "agent_name": self.agent_name,
            "phase": self.phase.value,
            "idea_contributed": self.idea_contributed,
            "idea_content": self.idea_content,
            "category": self.category.value,
            "references_ideas": self.references_ideas,
            "timestamp": self.timestamp,
            "reflection": self.reflection,
        }


@dataclass
class BrainstormSession:
    """Multi-agent brainstorming session."""

    session_id: str = field(default_factory=lambda: str(uuid4())[:8])
    context: SharedContext = field(
        default_factory=lambda: SharedContext(topic="", problem_statement="")
    )
    agent_names: List[str] = field(default_factory=list)
    current_agent_index: int = 0
    current_turn: int = 0
    current_phase: BrainstormPhase = BrainstormPhase.OPENING
    turns: List[BrainstormTurn] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True

    def __post_init__(self):
        """Initialize session."""
        if not self.context.topic:
            self.context = SharedContext(
                topic="Collaborative Brainstorm",
                problem_statement="Multi-agent creative session",
            )

    def add_agents(self, agents: List[str]):
        """Add agents to brainstorming session."""
        self.agent_names = agents
        for agent in agents:
            self.context.participating_agents.add(agent)

    def get_current_agent(self) -> str:
        """Get agent whose turn it is."""
        if not self.agent_names:
            return ""
        return self.agent_names[self.current_agent_index % len(self.agent_names)]

    def next_agent(self):
        """Move to next agent in rotation."""
        self.current_agent_index = (self.current_agent_index + 1) % len(
            self.agent_names
        )

    def add_turn(
        self,
        agent_name: str,
        idea_content: str,
        category: IdeaCategory = IdeaCategory.CORE_CONCEPT,
        references_ideas: Optional[List[str]] = None,
        reflection: str = "",
    ) -> Tuple[BrainstormTurn, Idea]:
        """
        Add agent contribution to brainstorming.

        AC1: Agents take turns contributing ideas

        Args:
            agent_name: Agent making contribution
            idea_content: The idea
            category: Type of idea
            references_ideas: Ideas this builds on
            reflection: Agent's reflection on idea

        Returns:
            Tuple of (turn, added_idea)
        """
        self.current_turn += 1

        # Add idea to shared context
        idea = self.context.add_idea(
            content=idea_content,
            contributor=agent_name,
            category=category,
            builds_on=references_ideas or [],
        )

        # Record turn
        turn = BrainstormTurn(
            turn_number=self.current_turn,
            agent_name=agent_name,
            phase=self.current_phase,
            idea_contributed=idea.id,
            idea_content=idea_content,
            category=category,
            references_ideas=references_ideas or [],
            reflection=reflection,
        )

        self.turns.append(turn)
        self.updated_at = datetime.now().isoformat()

        return turn, idea

    def get_turn_history(self) -> List[BrainstormTurn]:
        """AC3: Get brainstorm turn order and participation."""
        return self.turns

    def get_participation_metrics(self) -> Dict[str, int]:
        """AC3: Track participation by agent."""
        metrics = {}
        for agent in self.agent_names:
            count = sum(1 for turn in self.turns if turn.agent_name == agent)
            metrics[agent] = count
        return metrics

    def get_diversity_metrics(self) -> Dict:
        """AC4: Measure diversity of ideas across personalities."""
        diversity = {
            "total_ideas": len(self.turns),
            "ideas_by_agent": self.get_participation_metrics(),
            "ideas_by_category": {},
            "total_references": 0,
        }

        # Count by category
        for turn in self.turns:
            category = turn.category.value
            if category not in diversity["ideas_by_category"]:
                diversity["ideas_by_category"][category] = 0
            diversity["ideas_by_category"][category] += 1

            # Count references (conversation threading)
            diversity["total_references"] += len(turn.references_ideas)

        return diversity

    def set_phase(self, phase: BrainstormPhase):
        """Transition to next brainstorming phase."""
        self.current_phase = phase
        self.updated_at = datetime.now().isoformat()

    def conclude_session(self):
        """End brainstorming session."""
        self.is_active = False
        self.context.set_phase("closed")
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """AC5: Observable brainstorm state serializable to JSON."""
        return {
            "session_id": self.session_id,
            "context": self.context.to_dict(),
            "agent_names": self.agent_names,
            "current_agent_index": self.current_agent_index,
            "current_turn": self.current_turn,
            "current_phase": self.current_phase.value,
            "turn_count": len(self.turns),
            "participation": self.get_participation_metrics(),
            "diversity": self.get_diversity_metrics(),
            "turns": [turn.to_dict() for turn in self.turns],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
        }

    def get_summary(self) -> str:
        """Get human-readable brainstorm summary."""
        summary = f"""
BRAINSTORMING SESSION SUMMARY
=============================
Session ID: {self.session_id}
Phase: {self.current_phase.value.upper()}
Status: {"Active" if self.is_active else "Concluded"}

Agents: {", ".join(self.agent_names)}
Total Turns: {self.current_turn}

Participation:
"""
        for agent, count in self.get_participation_metrics().items():
            summary += f"  {agent}: {count} turns\n"

        diversity = self.get_diversity_metrics()
        summary += f"\nIdea Categories:\n"
        for category, count in diversity["ideas_by_category"].items():
            summary += f"  {category}: {count} ideas\n"

        summary += f"\nTotal References (Threading): {diversity['total_references']}\n"
        summary += f"\nCreated: {self.created_at}\n"
        summary += f"Updated: {self.updated_at}\n"

        return summary


class BrainstormingFacilitator:
    """Facilitates brainstorming sessions between agents."""

    def __init__(self):
        """Initialize facilitator."""
        self.sessions: Dict[str, BrainstormSession] = {}

    def create_session(
        self,
        topic: str,
        problem_statement: str,
        agents: List[str],
    ) -> BrainstormSession:
        """
        Create new brainstorming session.

        AC1: Session set up with agents ready to contribute

        Args:
            topic: Session topic
            problem_statement: Detailed problem description
            agents: List of agent names participating

        Returns:
            New BrainstormSession
        """
        context = SharedContext(topic=topic, problem_statement=problem_statement)
        session = BrainstormSession(context=context)
        session.add_agents(agents)

        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[BrainstormSession]:
        """Get brainstorming session by ID."""
        return self.sessions.get(session_id)

    def list_active_sessions(self) -> List[str]:
        """List all active session IDs."""
        return [sid for sid, session in self.sessions.items() if session.is_active]

    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics about session."""
        session = self.get_session(session_id)
        if not session:
            return {}

        return {
            "session_id": session_id,
            "topic": session.context.topic,
            "agents": session.agent_names,
            "total_turns": session.current_turn,
            "total_ideas": len(session.context.ideas),
            "participation": session.get_participation_metrics(),
            "diversity": session.get_diversity_metrics(),
            "is_active": session.is_active,
            "created_at": session.created_at,
        }


def run_brainstorm_round(
    session: BrainstormSession,
    agent_ideas: Dict[str, Tuple[str, IdeaCategory, List[str]]],
    reflections: Dict[str, str] = None,
) -> List[BrainstormTurn]:
    """
    Run one round of brainstorming with all agents.

    AC1: Agents contribute in turn
    AC2: Ideas can reference previous ideas

    Args:
        session: BrainstormSession
        agent_ideas: Dict mapping agent to (content, category, references)
        reflections: Optional dict of agent reflections

    Returns:
        List of turns executed
    """
    turns = []
    reflections = reflections or {}

    for agent, (content, category, refs) in agent_ideas.items():
        turn, _ = session.add_turn(
            agent_name=agent,
            idea_content=content,
            category=category,
            references_ideas=refs,
            reflection=reflections.get(agent, ""),
        )
        turns.append(turn)

    return turns
