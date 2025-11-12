"""
Collaborative memory and learning system.

Tracks collaborative sessions, patterns, and learning to improve
future collaboration and inform agent growth.

Story 3.5: Collaborative Memory & Learning
Acceptance Criteria:
- AC1: Store and retrieve collaboration session history
- AC2: Track patterns in collaborative behavior and outcomes
- AC3: Identify successful collaboration approaches
- AC4: Extract lessons learned for agent improvement
- AC5: Memory state serializable to JSON
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from .brainstorming import BrainstormSession
from .context import SharedContext
from .evaluation import EvaluationSession
from .synthesis import SynthesisSession


class LessonType(Enum):
    """Type of lesson learned."""

    AGENT_PREFERENCE = "agent_preference"
    COLLABORATION_PATTERN = "collaboration_pattern"
    SYNTHESIS_APPROACH = "synthesis_approach"
    EVALUATION_INSIGHT = "evaluation_insight"


@dataclass
class CollaborationMemory:
    """Single collaboration session memory."""

    memory_id: str
    session_type: str  # brainstorm, synthesis, evaluation, etc.
    context_topic: str
    participating_agents: List[str]
    outcome_quality: float  # 0.0-1.0 overall quality
    ideas_generated: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success_indicators: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize memory."""
        return {
            "memory_id": self.memory_id,
            "session_type": self.session_type,
            "context_topic": self.context_topic,
            "participating_agents": self.participating_agents,
            "outcome_quality": round(self.outcome_quality, 2),
            "ideas_generated": self.ideas_generated,
            "timestamp": self.timestamp,
            "success_indicators": self.success_indicators,
            "lessons": self.lessons_learned,
        }


@dataclass
class CollaborativeMemoryStore:
    """Store of collaboration memories and learning patterns."""

    store_id: str = field(default_factory=lambda: str(__import__("uuid").uuid4())[:8])
    memories: List[CollaborationMemory] = field(default_factory=list)
    agent_performance: Dict[str, Dict] = field(default_factory=dict)
    patterns: Dict[str, int] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def store_memory(
        self,
        session_type: str,
        topic: str,
        agents: List[str],
        quality: float,
        ideas: int,
        success_indicators: Optional[List[str]] = None,
        lessons: Optional[List[str]] = None,
    ) -> CollaborationMemory:
        """AC1: Store collaboration session memory."""
        memory = CollaborationMemory(
            memory_id=str(__import__("uuid").uuid4())[:8],
            session_type=session_type,
            context_topic=topic,
            participating_agents=agents,
            outcome_quality=quality,
            ideas_generated=ideas,
            success_indicators=success_indicators or [],
            lessons_learned=lessons or [],
        )

        self.memories.append(memory)
        self.updated_at = datetime.now().isoformat()

        # Update agent performance
        for agent in agents:
            if agent not in self.agent_performance:
                self.agent_performance[agent] = {
                    "collaborations": 0,
                    "total_quality": 0.0,
                    "average_quality": 0.0,
                }
            self.agent_performance[agent]["collaborations"] += 1
            self.agent_performance[agent]["total_quality"] += quality
            self.agent_performance[agent]["average_quality"] = (
                self.agent_performance[agent]["total_quality"]
                / self.agent_performance[agent]["collaborations"]
            )

        return memory

    def get_session_memories(self, session_type: str) -> List[CollaborationMemory]:
        """Retrieve memories of specific type."""
        return [m for m in self.memories if m.session_type == session_type]

    def get_agent_history(self, agent_name: str) -> Dict:
        """AC1: Get collaboration history for agent."""
        collaborations = [
            m for m in self.memories if agent_name in m.participating_agents
        ]

        return {
            "agent": agent_name,
            "collaboration_count": len(collaborations),
            "average_outcome_quality": (
                sum(m.outcome_quality for m in collaborations) / len(collaborations)
                if collaborations
                else 0.0
            ),
            "collaborations": [m.memory_id for m in collaborations],
        }

    def analyze_patterns(self) -> Dict:
        """AC2: Analyze patterns in collaboration data."""
        if not self.memories:
            return {}

        patterns = {
            "total_sessions": len(self.memories),
            "average_quality": sum(m.outcome_quality for m in self.memories)
            / len(self.memories),
            "agents_involved": len(self.agent_performance),
            "session_types": {},
        }

        # Analyze by session type
        for session_type in set(m.session_type for m in self.memories):
            sessions = self.get_session_memories(session_type)
            patterns["session_types"][session_type] = {
                "count": len(sessions),
                "avg_quality": sum(s.outcome_quality for s in sessions) / len(sessions),
                "avg_ideas": sum(s.ideas_generated for s in sessions) // len(sessions),
            }

        return patterns

    def get_successful_patterns(self, min_quality: float = 0.7) -> List[Dict]:
        """AC3: Identify successful collaboration approaches."""
        successful = [m for m in self.memories if m.outcome_quality >= min_quality]

        patterns = []
        for memory in successful:
            patterns.append(
                {
                    "session_type": memory.session_type,
                    "agents": memory.participating_agents,
                    "quality": memory.outcome_quality,
                    "ideas": memory.ideas_generated,
                    "success_factors": memory.success_indicators,
                }
            )

        return patterns

    def extract_lessons(self) -> List[Dict]:
        """AC4: Extract lessons learned for agent improvement."""
        lessons = []

        for memory in self.memories:
            for lesson in memory.lessons_learned:
                lessons.append(
                    {
                        "lesson": lesson,
                        "from_session": memory.memory_id,
                        "session_type": memory.session_type,
                        "quality_outcome": memory.outcome_quality,
                        "timestamp": memory.timestamp,
                    }
                )

        return lessons

    def get_agent_recommendations(self, agent_name: str) -> Dict:
        """Provide learning recommendations for agent."""
        history = self.get_agent_history(agent_name)
        all_lessons = self.extract_lessons()

        return {
            "agent": agent_name,
            "collaboration_experience": history["collaboration_count"],
            "current_performance": round(history["average_outcome_quality"], 2),
            "recommended_improvements": [
                l["lesson"] for l in all_lessons if "improve" in l["lesson"].lower()
            ][:3],
        }

    def to_dict(self) -> Dict:
        """AC5: Serialize memory store to JSON."""
        return {
            "store_id": self.store_id,
            "total_memories": len(self.memories),
            "memories": [m.to_dict() for m in self.memories],
            "agent_stats": {
                agent: {
                    "collaborations": stats["collaborations"],
                    "average_quality": round(stats["average_quality"], 2),
                }
                for agent, stats in self.agent_performance.items()
            },
            "patterns": self.analyze_patterns(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
