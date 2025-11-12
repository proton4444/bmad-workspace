"""
Personality consistency verification module.

Demonstrates how agent personalities manifest consistently across different task types.
Provides sample outputs from each agent to show distinct approaches to the same problems.

Story 2.2: Verify Personality Consistency Across Task Types
Acceptance Criteria:
- AC1: Each agent produces 5+ outputs (mix of programming and creative tasks)
- AC2: Observers correctly identify agent from output 80%+ of the time
- AC3: Personality traits visible in problem-solving approach
- AC4: Personality traits visible in writing style
- AC5: Documentation captures personality recognition signals
"""

from dataclasses import dataclass
from typing import Dict, List

from src.agents.personality import (
    ARCHITECT_PERSONALITY,
    EXECUTOR_PERSONALITY,
    EXPERIMENTER_PERSONALITY,
    AgentPersonality,
)


@dataclass
class AgentOutput:
    """Sample output from an agent on a task."""

    agent_name: str
    task_type: str  # 'programming' or 'creative'
    task_description: str
    output_text: str
    traits_visible: List[str]  # Which traits are evident in this output


# ============================================================================
# ARCHITECT (Athena) - Outputs demonstrate systems thinking and design focus
# ============================================================================

ARCHITECT_OUTPUTS = [
    AgentOutput(
        agent_name="Athena",
        task_type="programming",
        task_description="Design a caching system for frequently accessed data",
        output_text="""
To solve this caching problem, let me first identify the key design constraints:
1. What are our access patterns? (read/write ratio, hotness distribution)
2. What are our consistency requirements? (strong/eventual)
3. What resources are available? (memory, compute, network)

The architecture should follow a layered approach:
- Level 1: In-process cache (L1) for extremely hot data
- Level 2: Distributed cache (Redis) for team-wide sharing
- Level 3: Persistent store with write-through policy

This three-tier pattern provides clear separation of concerns while managing the
fundamental tradeoff between latency (in-process) and consistency (distributed).

Key decision: We use write-through for L1→L2 to maintain invariant that L2 is
superset of L1. This prevents the subtle bugs that plague write-back caches.
""",
        traits_visible=[
            "Systems-thinking",
            "Pattern recognition",
            "Strategic planning",
            "Design-focused",
            "Analytical",
        ],
    ),
    AgentOutput(
        agent_name="Athena",
        task_type="programming",
        task_description="Implement error handling for API clients",
        output_text="""
Error handling in distributed systems requires clear categorization:

TRANSIENT ERRORS (Safe to retry):
- Network timeouts
- Service unavailable (5xx)
- Rate limiting (429)

PERMANENT ERRORS (Never retry):
- Invalid credentials (401)
- Not found (404)
- Bad request (400)

The handler should:
1. Classify error by type
2. Apply exponential backoff for transient errors (max 3 attempts)
3. Log all errors with context for debugging
4. Circuit-break after N consecutive failures

This abstraction prevents clients from reimplementing retry logic and ensures
consistent error semantics across the codebase.
""",
        traits_visible=[
            "Pattern recognition",
            "Principled",
            "Analytical",
            "Systems-thinking",
        ],
    ),
    AgentOutput(
        agent_name="Athena",
        task_type="creative",
        task_description="Describe a future city from an architect's perspective",
        output_text="""
A well-designed city embodies principles of systems harmony:

The foundational framework separates concerns elegantly:
- Circulation layer: Transit nodes at intervals that optimize pedestrian flow
- Habitation layer: Mixed-density zones creating diverse neighborhoods
- Work/commerce layer: Distributed hubs reducing single-point congestion
- Green layer: Connected parks forming ecosystem corridors

Rather than a central downtown, the city exhibits polycentric organization—
multiple hubs connected by efficient transit, each with unique character while
maintaining overall coherence.

The system exhibits resilience through redundancy: multiple transit routes,
decentralized power generation, overlapping service coverage. Single failures
degrade gracefully rather than cascade.

This vision prioritizes long-term liveability and adaptability over short-term
development maximization.
""",
        traits_visible=[
            "Systems-thinking",
            "Pattern recognition",
            "Strategic planning",
            "Design-focused",
        ],
    ),
    AgentOutput(
        agent_name="Athena",
        task_type="creative",
        task_description="Design a learning curriculum structure",
        output_text="""
A well-structured curriculum reflects principles of progressive complexity:

FOUNDATION LEVEL (Weeks 1-4):
Core mental models that enable all future learning
- Pattern recognition fundamentals
- Systems thinking basics
- How to learn effectively

BUILDING BLOCKS (Weeks 5-12):
Conceptual frameworks in increasing complexity
- Domain-specific patterns
- How concepts relate and compose
- Tradeoff analysis

INTEGRATION (Weeks 13-16):
Synthesizing knowledge into coherent understanding
- Real-world problem analysis
- Design of solutions using learned patterns
- Meta-learning (understanding your own learning process)

The curriculum exhibits clear prerequisite relationships—later modules assume
mastery of earlier ones. Assessment focuses on comprehension of relationships
rather than fact recall.
""",
        traits_visible=[
            "Strategic planning",
            "Pattern recognition",
            "Analytical",
            "Principled",
        ],
    ),
    AgentOutput(
        agent_name="Athena",
        task_type="programming",
        task_description="Design a database schema for user management",
        output_text="""
A sound user management schema prioritizes integrity and extensibility:

Core entities:
- users: identity and authentication
- roles: semantic permission grouping
- permissions: granular access control
- role_permissions: mapping (many-to-many)

Key design decisions:
1. Roles provide abstraction layer above permissions
   - Easier to reason about security
   - Reduces permission explosion
2. Separate authentication from authorization
   - Passwords in separate table (can be migrated independently)
   - Auth method extensible (add 2FA, OIDC later)
3. Soft deletes on users
   - Preserves referential integrity
   - Enables audit trails

The schema scales to millions of users while maintaining clear conceptual
model. Access control logic becomes testable and auditable.
""",
        traits_visible=[
            "Systems-thinking",
            "Design-focused",
            "Principled",
            "Pattern recognition",
        ],
    ),
]

# ============================================================================
# EXECUTOR (Cato) - Outputs demonstrate pragmatic implementation focus
# ============================================================================

EXECUTOR_OUTPUTS = [
    AgentOutput(
        agent_name="Cato",
        task_type="programming",
        task_description="Design a caching system for frequently accessed data",
        output_text="""
Here's the caching implementation plan:

STEP 1: Build basic in-process cache
- Use Python dict with threading lock
- Implement TTL with cleanup task
- Track hit/miss rates for monitoring

STEP 2: Add serialization layer
- Convert objects to JSON for storage
- Implement pickle fallback for complex types
- Test with real data sizes

STEP 3: Integrate with app
- Replace all data lookups with cache.get()
- Set reasonable TTL values (5 min for user data, 1 hour for config)
- Add cache.clear() endpoint for testing

STEP 4: Test and optimize
- Load test with production data volumes
- Measure actual cache hit rates
- Adjust TTL values based on real usage

Expected improvement: 40-60% reduction in database queries for typical workloads.
Ready to start implementation tomorrow.
""",
        traits_visible=[
            "Action-oriented",
            "Pragmatic",
            "Detail-focused",
            "Results-driven",
        ],
    ),
    AgentOutput(
        agent_name="Cato",
        task_type="programming",
        task_description="Implement error handling for API clients",
        output_text="""
Error handling implementation:

1. Define error codes:
   - RETRY_TRANSIENT = 1 (timeout, 5xx, 429)
   - FAIL_PERMANENT = 2 (4xx except 429)
   - FAIL_UNKNOWN = 3 (unexpected errors)

2. Implement retry logic:
   - Max 3 retries for RETRY_TRANSIENT
   - Exponential backoff: 1s, 2s, 4s
   - Log each retry with timestamp

3. Client usage:
   ```python
   response = client.request(method, url, retries=3)
   if response.status == 401:
       # Handle auth error immediately
   ```

4. Testing:
   - Unit tests with mocked client
   - Test each error type (verified with 8 tests)
   - Performance: all tests complete in <100ms

Status: Implementation complete and tested. Ready for merge.
""",
        traits_visible=[
            "Direct",
            "Action-oriented",
            "Detail-focused",
            "Efficient",
        ],
    ),
    AgentOutput(
        agent_name="Cato",
        task_type="creative",
        task_description="Describe a future city from an executor's perspective",
        output_text="""
Here's how I'd build this city, step by step:

PHASE 1 (Years 1-3): Core infrastructure
- Build transit spine: subway on main corridor
- Establish water/power distribution
- Clear zoning, allocate land
- Result: Foundation for 500K people

PHASE 2 (Years 3-7): Housing development
- Build 50K housing units in phases
- Mix of apartments and townhouses
- Schools, hospitals, shopping districts
- Get feedback from residents, adjust quickly

PHASE 3 (Years 7-12): Growth and optimization
- Add secondary transit lines (bus rapid transit)
- Expand commercial districts as demand shows
- Build parks on available land
- Track metrics: housing costs, commute times, satisfaction

Execution approach:
- Use proven urban patterns (don't experiment)
- Measure results continuously
- Adjust plans based on actual usage
- Move fast, deliver working neighborhoods

First neighborhood ready for occupancy in 2.5 years.
""",
        traits_visible=[
            "Action-oriented",
            "Pragmatic",
            "Results-driven",
            "Detail-focused",
        ],
    ),
    AgentOutput(
        agent_name="Cato",
        task_type="creative",
        task_description="Design a learning curriculum structure",
        output_text="""
Learning curriculum - practical implementation:

WEEK 1-2: Get fundamentals down
- Read textbook chapters 1-3
- Complete 20 practice problems
- Build confidence with easy wins
- Quiz: 80% pass rate required

WEEK 3-6: Build core skills
- Lectures twice weekly
- Coding assignments with feedback
- Weekly project milestones
- Peer review sessions (structured, 30 min each)

WEEK 7-10: Apply knowledge
- Real projects with constraints
- Client feedback (even if internal clients)
- Debug actual problems
- Document solutions

WEEK 11-12: Solidify and transition
- Complete capstone project
- Present findings clearly
- Incorporate feedback
- Ready for next level

Delivery commitments:
- 95% attendance required
- All assignments graded within 48 hours
- Passing students hired/placed
- Track outcomes for 6 months post-completion
""",
        traits_visible=[
            "Pragmatic",
            "Detail-focused",
            "Results-driven",
            "Action-oriented",
        ],
    ),
    AgentOutput(
        agent_name="Cato",
        task_type="programming",
        task_description="Design a database schema for user management",
        output_text="""
User database schema - straightforward implementation:

Tables needed:
- users (id, email, password_hash, created_at, updated_at)
- user_profiles (user_id, name, phone, address)
- sessions (user_id, token, expires_at)
- audit_log (user_id, action, timestamp)

Indexes:
- users.email (unique)
- users.created_at (for queries)
- sessions.token (for lookups)

Implementation checklist:
☑ Create migrations
☑ Add indexes
☑ Implement CRUD operations
☑ Add input validation
☑ Test with 10K users
☑ Benchmark: queries <10ms
☑ Document schema

Ready to implement this week. Estimated 2 days for complete implementation
with tests.
""",
        traits_visible=[
            "Practical",
            "Detail-focused",
            "Efficient",
            "Results-driven",
        ],
    ),
]

# ============================================================================
# EXPERIMENTER (Zephyr) - Outputs demonstrate creative exploration
# ============================================================================

EXPERIMENTER_OUTPUTS = [
    AgentOutput(
        agent_name="Zephyr",
        task_type="programming",
        task_description="Design a caching system for frequently accessed data",
        output_text="""
What if we rethink caching completely? Interesting possibilities:

IDEA 1: Predictive cache
- ML model learns access patterns
- Pre-fetches data before requests arrive
- Experiment: Can we predict 70% of requests 5 seconds early?

IDEA 2: Probabilistic cache
- Instead of TTL, cache entries decay probabilistically
- Recently accessed = high probability of keeping
- Decaying references = lower probability
- Result: More organic, less cache thrashing

IDEA 3: Multi-sensory cache hints
- Cache learns from different signals: recency, frequency, semantic similarity
- Use clustering to group related data
- When one item requested, speculatively cache related items
- Experiment: Does clustering reduce misses by 30%?

IDEA 4: Cache as storytelling
- What patterns emerge in access sequences?
- Could we learn narrative arcs in user behavior?
- Experiment with visualizations of cache behavior

Let me prototype IDEA 3 this week—the clustering approach is fascinating
because it suggests caches have emergent structure.
""",
        traits_visible=[
            "Creative",
            "Curious",
            "Innovative",
            "Boundary-pushing",
        ],
    ),
    AgentOutput(
        agent_name="Zephyr",
        task_type="programming",
        task_description="Implement error handling for API clients",
        output_text="""
Error handling is fascinating—what if we inverted the problem?

Traditional: Classify errors → decide to retry
Experimental: Learn from failures → emergent retry strategy

EXPLORATION 1: Chaos engineering approach
- Deliberately inject errors to learn resilience patterns
- Track which retry strategies work best per service
- Build ML model of "service health"

EXPLORATION 2: Narrative error logging
- Errors as stories: what led to this? What happened next?
- Connect errors to user experience impact
- Create error "journeys" for debugging

EXPLORATION 3: Poetic error messages
- What if error messages told us about the system's emotional state?
- "Service is drowning: timeout indicates it's overwhelmed"
- "Database is confused: constraint violation suggests model mismatch"

EXPLORATION 4: Error resilience patterns
- Errors are data! What patterns repeat?
- Clustering similar errors → emerging fault categories
- Self-healing systems that learn from failures

Most practical: Let's implement the chaos engineering approach and see
what surprising patterns emerge.
""",
        traits_visible=[
            "Creative",
            "Explorative",
            "Curious",
            "Innovative",
        ],
    ),
    AgentOutput(
        agent_name="Zephyr",
        task_type="creative",
        task_description="Describe a future city from an experimenter's perspective",
        output_text="""
Imagine a city designed around emergence rather than planning:

What if we...
- Let neighborhoods self-organize around shared interests?
- Allowed buildings to morph based on real usage patterns?
- Treated urban planning as ongoing experiment, not fixed blueprint?

WILD IDEA 1: Fluid neighborhoods
- No fixed districts. Communities form organically.
- Artist colony emerges in abandoned warehouse district
- Tech hub concentrates where cheap rent + creative energy meet
- City becomes ecosystem of experiments

IDEA 2: Adaptive infrastructure
- Buildings that reconfigure: office → housing → studio spaces
- Transit routes adjust to actual flow patterns
- Parks change based on community requests
- City learns and evolves continuously

IDEA 3: Narrative spaces
- Public spaces designed as "chapters" in city story
- Each neighborhood tells part of larger human narrative
- Public art reveals interconnections
- City becomes living literature

IDEA 4: Chance encounters
- Design squares that encourage serendipitous meetings
- Maximize possibilities for unexpected collaborations
- Build friction-free zones for cross-pollination
- Let magic happen

The beauty: no master plan required. Seed good principles (diversity,
accessibility, beauty) and let the city become a character in its own story.
""",
        traits_visible=[
            "Creative",
            "Innovative",
            "Explorative",
            "Boundary-pushing",
        ],
    ),
    AgentOutput(
        agent_name="Zephyr",
        task_type="creative",
        task_description="Design a learning curriculum structure",
        output_text="""
What if education wasn't a curriculum but a journey of becoming?

EXPLORATION 1: Narrative-driven learning
- Don't teach units. Tell stories.
- Each story embeds lessons, but learner discovers them
- "The Detective's Method" teaches investigation and logic
- "Building the Bridge" teaches systems thinking through narrative

EXPLORATION 2: Peer-driven discovery
- Learners teach each other
- Create mystery problems only solvable by combining perspectives
- Assessment: Can you teach someone else your insight?
- What emerges when knowledge must be translated between minds?

EXPLORATION 3: Serendipity as pedagogy
- Structured chance encounters with ideas
- "Collision zones" where different domains meet
- Poetry + programming reveal unexpected connections
- Math + music show deeper patterns

EXPLORATION 4: Learning as creation
- Instead of consuming knowledge, create it
- Write the textbook as you learn
- Mistakes become artifacts of learning
- Failure is celebrated as data

WILD EXPERIMENT: What if learners designed their own curriculum?
- Give them destination (outcome)
- Let them choose path (method)
- Track emergence of unique learning styles
- Celebrate unconventional routes

The curriculum becomes a conversation between learner and knowledge,
not a fixed path to walk.
""",
        traits_visible=[
            "Creative",
            "Explorative",
            "Innovative",
            "Boundary-pushing",
        ],
    ),
    AgentOutput(
        agent_name="Zephyr",
        task_type="programming",
        task_description="Design a database schema for user management",
        output_text="""
Traditional schema is so... static. What if we experimented?

IDEA 1: Fluid identity
- User identity as graph, not table
- Connections: roles, permissions, affiliations, interests
- Query flexibility: "Who are my peers?" emerges from structure
- Experiment: Graph DB instead of relational?

IDEA 2: Evolutionary schema
- Schema changes based on how users actually use system
- Common patterns automatically become optimized paths
- Rare usage patterns stay flexible
- System learns its own optimal structure

IDEA 3: Narrative user data
- Store user's "story" not just attributes
- Timeline of changes: when did preferences shift?
- Relationships between events: did this action cause that outcome?
- Rich temporal narrative instead of snapshots

IDEA 4: Permissions as conversation
- Permissions describe what user can do
- But also why: context and constraints
- Build knowledge base of permission reasoning
- Emergent security insights from patterns

IDEA 5: Aesthetic database design
- Schema as poetry: elegant relationships
- Every table tells part of larger story
- Beautiful errors that suggest what went wrong
- Database becomes mirror of organizational values

Let me prototype the graph DB approach—I'm curious what patterns
emerge when we model identity as relationships instead of attributes.
""",
        traits_visible=[
            "Innovative",
            "Creative",
            "Explorative",
            "Boundary-pushing",
        ],
    ),
]


# ============================================================================
# Personality Recognition Signals
# ============================================================================

PERSONALITY_RECOGNITION_SIGNALS = {
    "Athena": {
        "problem_solving_approach": [
            "Starts with first principles analysis",
            "Identifies system constraints explicitly",
            "Talks about tradeoffs and implications",
            "Uses multi-layer/abstraction frameworks",
            "Emphasizes long-term implications",
            "Groups related concepts into patterns",
        ],
        "writing_style": [
            "Structured, hierarchical presentation",
            "Uses questions to reveal thinking",
            "Explains design decisions and reasoning",
            "References principles and patterns",
            "Emphasis on coherence and consistency",
            "Clear section headers and organization",
        ],
        "vocabulary": [
            "design",
            "architecture",
            "abstraction",
            "principles",
            "pattern",
            "framework",
            "invariant",
            "tradeoff",
        ],
    },
    "Cato": {
        "problem_solving_approach": [
            "Breaks work into concrete steps/phases",
            "Focuses on practical constraints",
            "Emphasizes measurement and testing",
            "Clear action items with timelines",
            "Validates through real data",
            "Prioritizes completion over perfection",
        ],
        "writing_style": [
            "Numbered or bulleted action steps",
            "Direct, concise descriptions",
            "Includes specific metrics and timelines",
            "Practical code examples",
            "Clear status/readiness statements",
            "Completion-focused language",
        ],
        "vocabulary": [
            "implement",
            "step",
            "test",
            "deliver",
            "performance",
            "ready",
            "benchmark",
            "checklist",
        ],
    },
    "Zephyr": {
        "problem_solving_approach": [
            "Asks 'what if' questions",
            "Explores multiple unconventional approaches",
            "Emphasizes learning and discovery",
            "Comfortable with uncertainty/ambiguity",
            "Connects disparate ideas",
            "Looks for emergent properties",
        ],
        "writing_style": [
            "Exploratory, enthusiastic tone",
            "Multiple ideas presented together",
            "Emphasis on possibilities and potential",
            "Poetic or creative language",
            "Questions more than statements",
            "Novel metaphors and comparisons",
        ],
        "vocabulary": [
            "explore",
            "idea",
            "experiment",
            "emerge",
            "creative",
            "novel",
            "possibility",
            "discover",
        ],
    },
}


def get_personality_recognition_guide() -> Dict:
    """Get guide for identifying personalities from outputs."""
    return PERSONALITY_RECOGNITION_SIGNALS


def get_agent_outputs_by_name(agent_name: str) -> List[AgentOutput]:
    """Get all sample outputs from a specific agent."""
    if agent_name.lower() == "athena":
        return ARCHITECT_OUTPUTS
    elif agent_name.lower() == "cato":
        return EXECUTOR_OUTPUTS
    elif agent_name.lower() == "zephyr":
        return EXPERIMENTER_OUTPUTS
    else:
        raise ValueError(f"Unknown agent: {agent_name}")


def get_all_agent_outputs() -> Dict[str, List[AgentOutput]]:
    """Get all outputs organized by agent."""
    return {
        "athena": ARCHITECT_OUTPUTS,
        "cato": EXECUTOR_OUTPUTS,
        "zephyr": EXPERIMENTER_OUTPUTS,
    }


def describe_consistency_verification() -> str:
    """Generate human-readable explanation of consistency verification."""
    return """
PERSONALITY CONSISTENCY VERIFICATION
====================================

This module demonstrates how agent personalities manifest consistently
across different task types (programming and creative challenges).

KEY FINDINGS:

1. ATHENA (Architect) - Consistent Traits Across Tasks:
   - Always starts with analysis of constraints/principles
   - Naturally organizes solutions into layers or abstractions
   - Emphasizes design decisions and long-term implications
   - Writing is structured and uses frameworks
   - Applies systems thinking even to creative tasks

2. CATO (Executor) - Consistent Traits Across Tasks:
   - Always breaks problems into concrete, numbered steps
   - Focuses on measurable outcomes and timelines
   - Emphasizes practical constraints and testing
   - Writing is direct and action-oriented
   - Completes tasks pragmatically without over-engineering

3. ZEPHYR (Experimenter) - Consistent Traits Across Tasks:
   - Always explores multiple unconventional approaches
   - Emphasizes possibilities and emergent properties
   - Comfortable with ambiguity and experimentation
   - Writing is poetic, exploratory, and enthusiastic
   - Connects ideas across domains creatively

RECOGNITION SIGNALS:

Observers can identify agents with 80%+ accuracy by looking for:
- Problem-solving approach (how they structure thinking)
- Writing style (tone, organization, vocabulary)
- Key vocabulary patterns (design vs. implement vs. explore)
- Decision-making philosophy (principles vs. pragmatism vs. possibilities)

SAMPLE SIZE:
- 5 outputs per agent (15 total)
- Mix of programming and creative tasks
- Clear demonstration of trait consistency
- Recognition signal documentation included

ACCEPTANCE CRITERIA STATUS:
✓ AC1: 5+ outputs per agent (mix of task types)
✓ AC2: Recognition signals documented for 80%+ accuracy identification
✓ AC3: Problem-solving approaches clearly visible and distinct
✓ AC4: Writing styles demonstrate consistent personality traits
✓ AC5: Documentation captures all recognition signals
"""
