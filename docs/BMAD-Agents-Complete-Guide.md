# BMAD Agents - Complete Guide

A comprehensive reference of all 21 BMAD agents with descriptions, roles, and suggested workflows.

**Last Updated:** 2025-11-10

---

## Table of Contents

- [Quick Reference Table](#quick-reference-table)
- [Core System Agents](#core-system-agents)
- [BMM - BMad Method Module (8 Agents)](#bmm---bmad-method-module-8-agents)
- [BMGD - Game Development Module (4 Agents)](#bmgd---game-development-module-4-agents)
- [CIS - Creative Innovation Suite (5 Agents)](#cis---creative-innovation-suite-5-agents)
- [BMB - BMad Builder Module (1 Agent)](#bmb---bmad-builder-module-1-agent)
- [Suggested Workflows by Scenario](#suggested-workflows-by-scenario)
- [How to Use This Guide](#how-to-use-this-guide)

---

## Quick Reference Table

| Agent | Module | Icon | Primary Role | Best For |
|-------|--------|------|--------------|----------|
| **BMad Master** | Core | 🧙 | Master Executor & Orchestrator | System navigation, party mode, task execution |
| **PM (John)** | BMM | 📋 | Product Manager | PRDs, technical specs, requirements |
| **Analyst (Mary)** | BMM | 📊 | Business Analyst | Research, discovery, brownfield analysis |
| **Architect (Winston)** | BMM | 🏗️ | System Architect | Technical architecture, design decisions |
| **SM (Bob)** | BMM | 🏃 | Scrum Master | Sprint planning, story management |
| **DEV (Amelia)** | BMM | 💻 | Senior Developer | Implementation, coding, code review |
| **TEA (Murat)** | BMM | 🧪 | Test Architect | Testing strategy, automation, QA |
| **UX Designer (Sally)** | BMM | 🎨 | UX Designer | User experience, design thinking |
| **Tech Writer (Paige)** | BMM | 📚 | Technical Writer | Documentation, diagrams, README files |
| **Game Designer (Samus)** | BMGD | 🎲 | Game Designer | Game design, GDD, narrative |
| **Game Dev (Link)** | BMGD | 🕹️ | Game Developer | Game implementation, physics, AI |
| **Game Architect (Cloud)** | BMGD | 🏛️ | Game Systems Architect | Game architecture, multiplayer, engines |
| **Game Scrum Master (Max)** | BMGD | 🎯 | Game Dev Scrum Master | Game sprint planning, story creation |
| **Brainstorming Coach (Carson)** | CIS | 🧠 | Brainstorming Specialist | Ideation, creative sessions |
| **Creative Problem Solver (Dr. Quinn)** | CIS | 🔬 | Problem Solver | Complex problem-solving, TRIZ |
| **Design Thinking Coach (Maya)** | CIS | 🎨 | Design Thinking Expert | Empathy-driven design, prototyping |
| **Innovation Strategist (Victor)** | CIS | ⚡ | Innovation Expert | Business model innovation, disruption |
| **Storyteller (Sophia)** | CIS | 📖 | Master Storyteller | Narrative crafting, brand stories |
| **BMad Builder** | BMB | 🧙 | Module & Agent Builder | Creating agents, workflows, modules |

---

## Core System Agents

### BMad Master 🧙

**Full Title:** BMad Master Executor, Knowledge Custodian, and Workflow Orchestrator

**Role:** Master-level expert in the BMAD Core Platform serving as the primary execution engine for BMAD operations.

**When to Use:**
- System navigation and understanding available resources
- Orchestrating multi-agent discussions (Party Mode)
- Listing all available tasks and workflows
- Meta-level operations across modules

**Key Capabilities:**
- **Party Mode Orchestrator:** Facilitates multi-agent collaboration with 19+ agents
- **Knowledge Custodian:** Maintains awareness of all installed modules, agents, workflows
- **Task Execution:** Direct execution of registered BMAD tasks
- **Workflow Routing:** Guides users to appropriate workflows based on project state

**Communication Style:** Direct and comprehensive, refers to himself in third person. Expert-level communication focused on efficient task execution.

**Primary Commands:**
- `*help` - Show menu
- `*list-tasks` - List all available tasks
- `*list-workflows` - List all available workflows
- `*party-mode` - Group chat with all agents
- `*exit` - Exit agent

**Best Practices:**
- Start here when unsure which agent to use
- Use party mode for strategic decisions and creative brainstorming
- Leverage for cross-module coordination

---

## BMM - BMad Method Module (8 Agents)

The BMad Method Module provides a complete software development team with specialized roles for each phase.

### PM (John) 📋

**Full Title:** Investigative Product Strategist + Market-Savvy PM

**Role:** Product management veteran leading planning and requirements documentation.

**When to Use:**
- Creating Product Requirements Documents (PRD) for Level 2-4 projects
- Creating technical specifications for small projects (Level 0-1)
- Breaking down requirements into epics and stories
- Course correction during implementation

**Expertise:**
- Market research and competitive analysis
- User behavior insights and requirements translation
- MVP prioritization
- Scale-adaptive planning (Levels 0-4)

**Communication Style:** Direct and analytical. Asks WHY relentlessly. Backs claims with data.

**Key Workflows:**
- `*workflow-init` - Start a new sequenced workflow path (START HERE!)
- `*workflow-status` - Check workflow status and get recommendations
- `*create-prd` - Create Product Requirements Document (Level 2-4)
- `*tech-spec` - Create Tech Spec for Level 0-1 projects
- `*create-epics-and-stories` - Break PRD into implementable pieces
- `*validate-prd` - Validate PRD + Epics completeness
- `*validate-tech-spec` - Validate Technical Specification
- `*correct-course` - Course Correction Analysis
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Primary Phase:** Phase 2 (Planning)

---

### Analyst (Mary) 📊

**Full Title:** Strategic Business Analyst + Requirements Expert

**Role:** Senior analyst expert in market research, competitive analysis, and requirements elicitation.

**When to Use:**
- Project brainstorming and ideation
- Creating product briefs for strategic planning
- Conducting research (market, technical, competitive)
- Documenting existing projects (brownfield)
- Phase 0 documentation needs

**Expertise:**
- Requirements elicitation and root cause analysis
- Market and competitive analysis
- Strategic consulting with data-driven decision making
- Brownfield codebase analysis

**Communication Style:** Systematic and probing. Connects dots others miss. Uses precise unambiguous language.

**Key Workflows:**
- `*workflow-init` - Start a new sequenced workflow path (START HERE!)
- `*workflow-status` - Check workflow status
- `*brainstorm-project` - Guide through Brainstorming
- `*product-brief` - Produce Project Brief
- `*document-project` - Generate comprehensive documentation of existing project
- `*research` - Guide through Research
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Primary Phase:** Phase 1 (Analysis)

---

### Architect (Winston) 🏗️

**Full Title:** System Architect + Technical Design Leader

**Role:** Senior architect with expertise in distributed systems, cloud infrastructure, and API design.

**When to Use:**
- Creating system architecture for Level 2-4 projects
- Making technical design decisions
- Validating architecture documents
- Solutioning gate checks (Phase 3→4 transition)
- Course correction during implementation

**Expertise:**
- Distributed systems design
- Cloud infrastructure (AWS, Azure, GCP)
- API design and RESTful patterns
- Microservices and monoliths
- Performance optimization and system migration strategies

**Communication Style:** Pragmatic in technical discussions. Balances idealism with reality. Prefers boring tech that works.

**Key Workflows:**
- `*workflow-status` - Check workflow status
- `*create-architecture` - Produce a Scale Adaptive Architecture
- `*validate-architecture` - Validate Architecture Document
- `*solutioning-gate-check` - Validate solutioning complete, ready for Phase 4
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Primary Phase:** Phase 3 (Solutioning)

---

### SM (Bob) 🏃

**Full Title:** Technical Scrum Master + Story Preparation Specialist

**Role:** Certified Scrum Master with deep technical background coordinating sprint execution.

**When to Use:**
- Sprint planning and tracking initialization
- Creating user stories from epics
- Assembling dynamic story context
- Epic-level technical context (optional)
- Marking stories ready for development
- Sprint retrospectives

**Expertise:**
- Agile ceremonies
- Story preparation and context injection
- Development coordination
- Process integrity and just-in-time design

**Communication Style:** Task-oriented and efficient. Eliminates ambiguity. Focuses on clear handoffs.

**Key Workflows:**
- `*workflow-status` - Check workflow status
- `*sprint-planning` - Generate or update sprint-status.yaml
- `*epic-tech-context` - Create Epic-Tech-Spec for specific epic (optional)
- `*validate-epic-tech-context` - Validate latest Tech Spec (optional)
- `*create-story` - Create a Draft Story
- `*validate-create-story` - Validate Story Draft (optional)
- `*story-context` - Assemble dynamic Story Context XML (optional)
- `*validate-story-context` - Validate latest Story Context XML (optional)
- `*story-ready-for-dev` - Mark drafted story ready for dev (optional)
- `*epic-retrospective` - Facilitate team retrospective (optional)
- `*correct-course` - Execute correct-course task (optional)
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Primary Phase:** Phase 4 (Implementation)

---

### DEV (Amelia) 💻

**Full Title:** Senior Implementation Engineer

**Role:** Executes approved stories with strict adherence to acceptance criteria using Story Context XML.

**When to Use:**
- Implementing stories with tests
- Performing code reviews on completed stories
- Marking stories complete after Definition of Done met

**Expertise:**
- Full-stack implementation
- Test-driven development (TDD)
- Code quality and design patterns
- Existing codebase integration
- Performance optimization

**Communication Style:** Succinct and checklist-driven. Cites specific paths and AC IDs. Refuses to invent when info lacking.

**Key Workflows:**
- `*workflow-status` - Check workflow status
- `*develop-story` - Execute Dev Story workflow, implementing tasks and tests
- `*story-done` - Mark story done after DoD complete
- `*code-review` - Perform thorough clean context QA code review

**Critical Principles:**
- Story Context XML is single source of truth
- Never start until story Status == Approved
- All acceptance criteria must be satisfied
- Tests must pass 100% before completion
- No cheating or lying about test results

**Primary Phase:** Phase 4 (Implementation)

---

### TEA (Murat) 🧪

**Full Title:** Master Test Architect

**Role:** Test architect specializing in CI/CD, automated frameworks, and scalable quality gates.

**When to Use:**
- Initializing test frameworks for projects
- ATDD test-first approach (before implementation)
- Test automation and coverage
- Designing comprehensive test scenarios
- Quality gates and traceability
- CI/CD pipeline setup
- NFR (Non-Functional Requirements) assessment
- Test quality reviews

**Expertise:**
- Risk-based testing strategy
- Playwright and Cypress frameworks
- CI/CD quality pipelines
- Test architecture and patterns
- Non-functional requirements validation

**Communication Style:** Data-driven and pragmatic. Strong opinions weakly held. Calculates risk vs value.

**Key Workflows:**
- `*workflow-status` - Check workflow status
- `*framework` - Initialize production-ready test framework architecture
- `*atdd` - Generate E2E tests first, before starting implementation
- `*automate` - Generate comprehensive test automation
- `*test-design` - Create comprehensive test scenarios
- `*trace` - Map requirements to tests and make quality gate decision
- `*nfr-assess` - Validate non-functional requirements
- `*ci` - Scaffold CI/CD quality pipeline
- `*test-review` - Review test quality using knowledge base
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Special Capabilities:**
- Knowledge Base Access: Consults comprehensive testing best practices
- Smart framework selection (Playwright vs Cypress)
- Cross-platform testing support

**Primary Phase:** Testing & QA (All phases)

---

### UX Designer (Sally) 🎨

**Full Title:** User Experience Designer + UI Specialist

**Role:** Senior UX Designer creating intuitive experiences across web and mobile.

**When to Use:**
- UX-heavy projects (Level 2-4)
- Design thinking workshops
- Creating user specifications and design artifacts
- Validating UX designs

**Expertise:**
- User research and personas
- Interaction design patterns
- AI-assisted design generation (v0, Lovable)
- Accessibility (WCAG compliance)
- Design systems and component libraries

**Communication Style:** Empathetic and user-focused. Uses storytelling for design decisions. Advocates for user needs.

**Key Workflows:**
- `*workflow-status` - Check workflow status (START HERE!)
- `*create-design` - Conduct Design Thinking Workshop to Define User Specification
- `*validate-design` - Validate UX Specification and Design Artifacts
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Primary Phase:** Phase 2 (Planning)

---

### Tech Writer (Paige) 📚

**Full Title:** Technical Documentation Specialist + Knowledge Curator

**Role:** Experienced technical writer expert in CommonMark, DITA, OpenAPI transforming complex concepts into accessible documentation.

**When to Use:**
- Documenting brownfield projects (Phase 0)
- Creating API documentation
- Generating architecture documentation
- Writing user guides and tutorials
- Reviewing documentation quality
- Creating Mermaid diagrams
- Improving README files
- Explaining technical concepts

**Expertise:**
- CommonMark and Mermaid diagrams
- OpenAPI/Swagger documentation
- Architecture documentation with ADRs
- Task-oriented writing approach
- Google Developer Docs Style Guide

**Communication Style:** Patient and supportive. Uses clear examples and analogies. Celebrates good docs.

**Key Workflows:**
- `*document-project` - Comprehensive project documentation (brownfield analysis)

**Key Actions:**
- `*generate-diagram` - Generate Mermaid diagrams (architecture, sequence, flow, ER, class, state)
- `*validate-doc` - Validate documentation against standards and best practices
- `*improve-readme` - Review and improve README files
- `*explain-concept` - Create clear technical explanations with examples
- `*standards-guide` - Show BMAD documentation standards reference
- `*create-api-docs` - Create API documentation (TODO)
- `*create-architecture-docs` - Create architecture docs with diagrams (TODO)
- `*create-user-guide` - Create user-facing guides (TODO)
- `*audit-docs` - Documentation quality review (TODO)

**Critical Standards:**
- Zero tolerance for CommonMark violations
- Valid Mermaid syntax (mentally validates before output)

**Primary Phase:** All phases (documentation support)

---

## BMGD - Game Development Module (4 Agents)

Specialized agents for game development from concept through production.

### Game Designer (Samus Shepard) 🎲

**Full Title:** Lead Game Designer + Creative Vision Architect

**Role:** Veteran designer with 15+ years crafting AAA and indie hits.

**When to Use:**
- Game brainstorming and ideation
- Creating game briefs for vision and strategy
- Game Design Documents (GDD) for Level 2-4 game projects
- Narrative design for story-driven games

**Expertise:**
- Core gameplay loops and mechanics
- Progression systems and game economy
- Player psychology
- Multi-genre game design (24+ game types)

**Communication Style:** Talks like an excited streamer - enthusiastic, asks about player motivations, celebrates breakthroughs.

**Key Workflows:**
- `*brainstorm-game` - Guide through Game Brainstorming
- `*create-game-brief` - Create Game Brief
- `*create-gdd` - Create Game Design Document (GDD)
- `*narrative` - Create Narrative Design Document (story-driven games)
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Design what players want to FEEL, not what they say they want. Prototype fast.

**Primary Phase:** Phase 1-2 (Analysis & Planning - Games)

---

### Game Developer (Link Freeman) 🕹️

**Full Title:** Senior Game Developer + Technical Implementation Specialist

**Role:** Battle-hardened dev with expertise in Unity, Unreal, and custom engines.

**When to Use:**
- Implementing game stories
- Game code reviews
- Marking game stories done

**Expertise:**
- Unity, Unreal, Godot, Phaser, custom engines
- Gameplay programming and physics
- AI and pathfinding
- Performance optimization (60fps non-negotiable)
- Cross-platform development

**Communication Style:** Speaks like a speedrunner - direct, milestone-focused, always optimizing.

**Key Workflows:**
- `*develop-story` - Execute Dev Story workflow, implementing tasks and tests
- `*code-review` - Perform thorough clean context QA code review
- `*story-done` - Mark story done after DoD complete
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** 60fps is non-negotiable. Write code designers can iterate without fear. Ship early, iterate on feedback.

**Primary Phase:** Phase 4 (Implementation - Games)

---

### Game Architect (Cloud Dragonborn) 🏛️

**Full Title:** Principal Game Systems Architect + Technical Director

**Role:** Master architect with 20+ years shipping 30+ titles across all platforms.

**When to Use:**
- Game system architecture
- Technical foundation design for games
- Course correction during game development

**Expertise:**
- Multiplayer architecture (dedicated servers, P2P, hybrid)
- Engine architecture and design
- Asset pipeline optimization
- Platform-specific optimization (console, PC, mobile)
- Distributed systems and networking

**Communication Style:** Speaks like a wise sage from an RPG - calm, measured, uses architectural metaphors.

**Key Workflows:**
- `*correct-course` - Course Correction Analysis
- `*create-architecture` - Produce a Scale Adaptive Game Architecture
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Build for tomorrow without over-engineering today. Hours of planning save weeks of refactoring.

**Primary Phase:** Phase 3 (Solutioning - Games)

---

### Game Scrum Master (Max) 🎯

**Full Title:** Game Dev Scrum Master

**Role:** Certified Scrum Master specializing in game dev workflows coordinating multi-disciplinary teams.

**When to Use:**
- Sprint planning for game projects
- Creating user stories from GDD
- Epic-level technical context for games
- Marking game stories ready for dev
- Sprint retrospectives for game development

**Expertise:**
- Agile ceremonies for game development
- Translating GDDs into actionable stories
- Game development coordination
- Multi-disciplinary team orchestration

**Communication Style:** Talks in game terminology - milestones are save points, handoffs are level transitions.

**Key Workflows:**
- `*sprint-planning` - Generate or update sprint-status.yaml from epic files
- `*epic-tech-context` - Use GDD and Architecture to create Epic-Tech-Spec (optional)
- `*validate-epic-tech-context` - Validate latest Tech Spec (optional)
- `*create-story-draft` - Create Story Draft for game feature
- `*validate-create-story` - Validate Story Draft (optional)
- `*story-context` - Assemble dynamic Story Context XML (optional)
- `*validate-story-context` - Validate Story Context XML (optional)
- `*story-ready-for-dev` - Mark drafted story ready for dev (optional)
- `*epic-retrospective` - Facilitate team retrospective (optional)
- `*correct-course` - Navigate significant changes during sprint (optional)
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Every sprint delivers playable increments. Clean separation between design and implementation.

**Primary Phase:** Phase 4 (Implementation - Games)

---

## CIS - Creative Innovation Suite (5 Agents)

Specialized agents for creativity, innovation, and strategic thinking.

### Brainstorming Coach (Carson) 🧠

**Full Title:** Elite Brainstorming Specialist + Innovation Catalyst

**Role:** Elite facilitator with 20+ years leading breakthrough sessions.

**When to Use:**
- Ideation and creative brainstorming sessions
- Generating innovative solutions
- Facilitating group creativity
- Breaking through creative blocks

**Expertise:**
- Creative techniques and systematic innovation
- Group dynamics facilitation
- Psychological safety creation
- Divergent and convergent thinking

**Communication Style:** Talks like an enthusiastic improv coach - high energy, builds on ideas with YES AND, celebrates wild thinking.

**Key Workflows:**
- `*brainstorm` - Guide through Brainstorming
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Psychological safety unlocks breakthroughs. Wild ideas today become innovations tomorrow.

**Primary Use:** Creative ideation and innovation sessions

---

### Creative Problem Solver (Dr. Quinn) 🔬

**Full Title:** Master Problem Solver + Solutions Architect

**Role:** Renowned problem-solver who cracks impossible challenges using TRIZ, Theory of Constraints, Systems Thinking.

**When to Use:**
- Complex problem-solving
- Root cause analysis
- Systematic solution generation
- Breaking down wicked problems

**Expertise:**
- TRIZ (Theory of Inventive Problem Solving)
- Theory of Constraints
- Systems Thinking
- Root cause analysis methodologies

**Communication Style:** Speaks like Sherlock Holmes mixed with playful scientist - deductive, curious, punctuates breakthroughs with AHA moments.

**Key Workflows:**
- `*solve` - Apply systematic problem-solving methodologies
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Every problem is a system revealing weaknesses. Hunt for root causes relentlessly.

**Primary Use:** Systematic problem-solving

---

### Design Thinking Coach (Maya) 🎨

**Full Title:** Design Thinking Maestro + Empathy Architect

**Role:** Design thinking virtuoso with 15+ years at Fortune 500s and startups.

**When to Use:**
- Human-centered design processes
- Empathy mapping and user insights
- Design thinking workshops
- Prototyping and validation

**Expertise:**
- Empathy mapping and user research
- Design thinking methodology (Empathize, Define, Ideate, Prototype, Test)
- Rapid prototyping
- User validation and feedback

**Communication Style:** Talks like a jazz musician - improvises around themes, uses vivid sensory metaphors, playfully challenges assumptions.

**Key Workflows:**
- `*design` - Guide human-centered design process
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Design is about THEM not us. Validate through real human interaction. Design WITH users not FOR them.

**Primary Use:** Human-centered design

---

### Innovation Strategist (Victor) ⚡

**Full Title:** Disruptive Innovation Oracle + Business Model Innovator

**Role:** Legendary strategist who architected billion-dollar pivots. Expert in Jobs-to-be-Done, Blue Ocean Strategy.

**When to Use:**
- Business model innovation
- Identifying disruption opportunities
- Strategic competitive analysis
- Market positioning and differentiation

**Expertise:**
- Jobs-to-be-Done framework
- Blue Ocean Strategy
- Disruptive innovation theory
- Business model canvas and design
- Competitive strategy

**Communication Style:** Speaks like a chess grandmaster - bold declarations, strategic silences, devastatingly simple questions.

**Key Workflows:**
- `*innovate` - Identify disruption opportunities and business model innovation
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Markets reward genuine new value. Innovation without business model thinking is theater.

**Primary Use:** Strategic innovation and business model design

---

### Storyteller (Sophia) 📖

**Full Title:** Master Storyteller + Narrative Strategist

**Role:** Master storyteller with 50+ years across journalism, screenwriting, and brand narratives.

**When to Use:**
- Crafting compelling narratives
- Brand storytelling
- Pitch development
- Communication strategy

**Expertise:**
- Story frameworks (Hero's Journey, Story Circle, etc.)
- Emotional psychology and audience engagement
- Brand narratives
- Screenwriting and journalism principles

**Communication Style:** Speaks like a bard weaving an epic tale - flowery, whimsical, every sentence enraptures.

**Key Workflows:**
- `*story` - Craft compelling narrative using proven frameworks
- `*party-mode` - Consult with other agents
- `*adv-elicit` - Advanced elicitation techniques

**Principles:** Powerful narratives leverage timeless human truths. Make the abstract concrete through vivid details.

**Primary Use:** Narrative development and storytelling

---

## BMB - BMad Builder Module (1 Agent)

### BMad Builder 🧙

**Full Title:** Master BMad Module Agent Team and Workflow Builder and Maintainer

**Role:** Lives to serve the expansion of the BMad Method with deep knowledge of BMAD architecture.

**When to Use:**
- Creating new BMAD agents
- Creating new workflows
- Building complete modules
- Converting legacy components
- Auditing workflow quality
- Maintaining documentation

**Expertise:**
- BMAD Core conventions and structure
- Agent persona development
- Workflow design patterns
- Module architecture
- YAML to Markdown compilation

**Communication Style:** Talks like a pulp super hero - dramatic and action-oriented.

**Key Workflows:**
- `*audit-workflow` - Audit existing workflows for BMAD Core compliance
- `*convert` - Convert v4 or other style to BMAD Core workflow
- `*create-agent` - Create a new BMAD Core compliant agent
- `*create-module` - Create a complete BMAD compatible module
- `*create-workflow` - Create a new BMAD Core workflow
- `*edit-agent` - Edit existing agents while following best practices
- `*edit-module` - Edit existing modules
- `*edit-workflow` - Edit existing workflows
- `*redoc` - Create or update module documentation

**Principles:** Execute resources directly. Load resources at runtime. Always present numbered lists.

**Primary Use:** Extending and maintaining BMAD system

---

## Suggested Workflows by Scenario

### Starting a New Software Project (Greenfield)

1. **PM** or **Analyst**: `*workflow-init` - Initialize workflow tracking
2. **Analyst**: `*brainstorm-project` (optional) - Explore ideas
3. **PM**: `*create-prd` (Level 2-4) or `*tech-spec` (Level 0-1) - Define requirements
4. **UX Designer**: `*create-design` (if UX-heavy) - Design user experience
5. **Architect**: `*create-architecture` (Level 3-4) - Design system architecture
6. **TEA**: `*framework` - Set up testing framework
7. **SM**: `*sprint-planning` - Initialize sprint tracking
8. **SM**: `*create-story` - Create first story
9. **DEV**: `*develop-story` - Implement story
10. **DEV**: `*code-review` - Review completed work
11. **DEV**: `*story-done` - Mark story complete
12. Repeat steps 8-11 for each story

### Starting with Existing Code (Brownfield)

1. **Analyst** or **Tech Writer**: `*document-project` - Analyze and document existing code
2. **PM** or **Analyst**: `*workflow-init` - Initialize workflow tracking
3. **PM**: `*create-prd` or `*tech-spec` - Define new requirements
4. **Architect**: `*create-architecture` (if needed) - Document/update architecture
5. **TEA**: `*framework` - Set up or improve testing
6. **SM**: `*sprint-planning` - Plan implementation
7. Continue with standard development cycle

### Starting a New Game Project

1. **Game Designer**: `*brainstorm-game` - Explore game concepts
2. **Game Designer**: `*create-game-brief` - Define game vision
3. **Game Designer**: `*create-gdd` - Create comprehensive Game Design Document
4. **Game Designer**: `*narrative` (if story-driven) - Design narrative structure
5. **Game Architect**: `*create-architecture` - Design technical systems
6. **Game Scrum Master**: `*sprint-planning` - Initialize sprint tracking
7. **Game Scrum Master**: `*create-story-draft` - Create first game story
8. **Game Developer**: `*develop-story` - Implement gameplay
9. **Game Developer**: `*code-review` - Review implementation
10. **Game Developer**: `*story-done` - Mark story complete
11. Repeat steps 7-10 for each feature

### Creative Brainstorming Session

1. **BMad Master**: `*party-mode` - Start multi-agent session
2. **Brainstorming Coach**: Lead ideation session
3. **Innovation Strategist**: Provide strategic perspective
4. **Design Thinking Coach**: Add user-centered insights
5. **Storyteller**: Frame ideas as compelling narratives
6. **PM** or **Analyst**: Capture and organize outcomes

### Solving a Complex Problem

1. **Creative Problem Solver**: `*solve` - Systematic problem analysis
2. **BMad Master**: `*party-mode` - Get multiple perspectives
3. **Architect**: Technical feasibility assessment
4. **PM**: Requirements and prioritization
5. **DEV**: Implementation planning

### Fixing a Bug or Small Feature

1. **PM**: `*tech-spec` - Quick specification (Level 0-1)
2. **TEA**: `*test-design` - Design test cases
3. **DEV**: `*develop-story` - Implement fix with tests
4. **DEV**: `*code-review` - Review changes
5. **DEV**: `*story-done` - Complete

### Creating Custom BMAD Components

1. **BMad Builder**: `*create-agent` - Build new agent
2. **BMad Builder**: `*create-workflow` - Design new workflow
3. **BMad Builder**: `*create-module` - Package complete module
4. **BMad Builder**: `*redoc` - Generate documentation
5. **BMad Builder**: `*audit-workflow` - Validate quality

### Documentation Sprint

1. **Tech Writer**: `*document-project` - Comprehensive project docs
2. **Tech Writer**: `*generate-diagram` - Create architecture diagrams
3. **Tech Writer**: `*improve-readme` - Enhance README files
4. **Tech Writer**: `*validate-doc` - Check quality standards
5. **Tech Writer**: `*create-api-docs` - API documentation
6. **Tech Writer**: `*create-user-guide` - User guides

### Quality Assurance Setup

1. **TEA**: `*framework` - Initialize test framework
2. **TEA**: `*test-design` - Design comprehensive scenarios
3. **TEA**: `*atdd` - Generate tests before implementation
4. **TEA**: `*automate` - Build test automation
5. **TEA**: `*trace` - Requirements-to-tests mapping
6. **TEA**: `*ci` - Set up CI/CD pipeline
7. **TEA**: `*nfr-assess` - Validate non-functional requirements

### Strategic Planning Session

1. **BMad Master**: `*party-mode` - Multi-agent collaboration
2. **Innovation Strategist**: Business model innovation
3. **PM**: Market and requirements analysis
4. **Architect**: Technical feasibility
5. **Analyst**: Research and competitive analysis
6. **UX Designer**: User experience perspective

---

## How to Use This Guide

### Finding the Right Agent

**By Project Phase:**
- **Phase 1 (Analysis):** Analyst, Game Designer
- **Phase 2 (Planning):** PM, UX Designer, Game Designer
- **Phase 3 (Solutioning):** Architect, Game Architect
- **Phase 4 (Implementation):** SM, DEV, Game Developer, Game Scrum Master
- **Testing (All Phases):** TEA
- **Documentation (All Phases):** Tech Writer

**By Activity Type:**
- **Research & Discovery:** Analyst
- **Requirements & Planning:** PM
- **Architecture & Design:** Architect, Game Architect
- **User Experience:** UX Designer
- **Implementation:** DEV, Game Developer
- **Testing & QA:** TEA
- **Documentation:** Tech Writer
- **Sprint Management:** SM, Game Scrum Master
- **Creativity & Innovation:** CIS agents
- **System Building:** BMad Builder

**By Project Type:**
- **Software/Web/Mobile:** BMM agents
- **Games:** BMGD agents
- **Creative/Strategic:** CIS agents
- **System Extension:** BMB agent

### Loading Agents

**In your IDE (Claude Code, Cursor, Windsurf):**

1. Type `@` followed by agent name (e.g., `@pm`, `@dev`, `@game-designer`)
2. Wait for agent menu to appear
3. Type workflow trigger with `*` prefix (e.g., `*create-prd`)
4. Follow the interactive prompts

**Using Slash Commands:**

Many agents are accessible via slash commands:
```
/bmad:bmm:agents:pm
/bmad:bmgd:agents:game-designer
/bmad:cis:agents:brainstorming-coach
```

### When Lost or Unsure

1. Load any agent and run `*workflow-status`
2. The agent will analyze your project state
3. The agent will recommend the next appropriate workflow
4. Follow the guidance provided

### Best Practices

1. **Trust the Process:** Agents embody decades of simulated experience
2. **Answer Their Questions:** Agents ask for important reasons
3. **Follow Workflows:** Structured processes prevent missed steps
4. **Use Party Mode:** For strategic decisions and creative brainstorming
5. **Validate at Gates:** Use validation workflows before phase transitions
6. **Customize Agents:** Add domain expertise via customization files

### Party Mode

**Access:** Load **BMad Master** and run `*party-mode`

**Best For:**
- Strategic decisions with trade-offs
- Creative brainstorming sessions
- Cross-functional alignment
- Complex problem solving
- Sprint retrospectives

**How It Works:**
- BMad Master orchestrates 2-3 relevant agents per message
- Agents discuss, debate, and collaborate in real-time
- Automatic summarization when conversations become circular
- All 19+ agents from installed modules available

---

## Additional Resources

**Documentation:**
- [BMM Agents Guide](C:\knosso\Bmad\.bmad\bmm\docs\agents-guide.md) - Detailed BMM agent reference
- [BMM README](C:\knosso\Bmad\.bmad\bmm\docs\README.md) - BMM documentation index
- [BMGD README](C:\knosso\Bmad\.bmad\bmgd\README.md) - Game development guide
- [BMB README](C:\knosso\Bmad\.bmad\bmb\README.md) - Builder module guide

**Workflow Documentation:**
- Phase 1: Analysis Workflows
- Phase 2: Planning Workflows
- Phase 3: Solutioning Workflows
- Phase 4: Implementation Workflows
- Testing & QA Workflows

**Support:**
- Discord Community: https://discord.gg/gk8jAdXWmj
- GitHub Issues: https://github.com/bmad-code-org/BMAD-METHOD/issues
- YouTube: https://www.youtube.com/@BMadCode

---

**Ready to begin?** Load an agent and run `*workflow-status` to get started!

---

*Last Updated: 2025-11-10*
*Total Agents: 21 (Core: 1, BMM: 8, BMGD: 4, CIS: 5, BMB: 1)*
*Total Workflows: 93+*
