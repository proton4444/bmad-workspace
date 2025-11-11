# BMAD Workspace Organization Guide

## Purpose
This guide defines the organizational structure and best practices for the C:\knosso\Bmad\ workspace. Following these rules ensures consistency, prevents chaos as the workspace grows, and maintains BMAD methodology compliance.

---

## Directory Structure

```
C:\knosso\Bmad/
├── .bmad/                  # BMAD system files (auto-managed)
├── .claude/                # Claude Code configuration
│   └── commands/           # Custom slash commands
├── .git/                   # Git repository (workspace-level)
│   └── hooks/              # Git hooks for convention enforcement
├── docs/                   # Workspace-level documentation
│   ├── CONVENTIONS.md      # Naming and coding standards
│   ├── BMAD_COMPLIANCE.md  # BMAD methodology checklist
│   └── WORKSPACE_GUIDE.md  # This file
├── projects/               # All individual projects live here
│   ├── multi-agent-mvp/    # Example: Multi-agent system
│   │   ├── src/            # Source code
│   │   ├── config/         # Configuration files
│   │   ├── tests/          # Test files
│   │   ├── outputs/        # Generated outputs (git ignored)
│   │   ├── logs/           # Log files (git ignored)
│   │   └── docs/           # Project-specific docs
│   └── [other-projects]/   # Future projects
├── output/                 # Workspace-level temporary output
├── .temp/                  # Temporary files (git ignored)
└── Makefile                # Common workspace operations
```

---

## Core Principles

### 1. Project Isolation
**Rule:** Each project is self-contained in `projects/[project-name]/`

**Why:** Prevents cross-project contamination, makes projects portable, enables independent git repositories per project if needed.

**Example:**
```
✅ projects/multi-agent-mvp/src/coordinator.py
❌ src/multi-agent-mvp/coordinator.py
❌ multi-agent-mvp/coordinator.py (at root)
```

### 2. Hierarchical Documentation
**Rule:** Documentation exists at both workspace and project levels

**Workspace-level (`docs/`):**
- CONVENTIONS.md - Standards for ALL projects
- BMAD_COMPLIANCE.md - Methodology checklist
- WORKSPACE_GUIDE.md - This file
- Architecture decisions affecting multiple projects

**Project-level (`projects/[name]/docs/`):**
- README.md - Project overview
- SETUP.md - Installation/setup instructions
- STRUCTURE.md - Project architecture
- Project-specific technical docs

### 3. Git Strategy
**Rule:** Single git repository at workspace root, project-level .gitignore files

**Why:** Unified version control for all projects, shared conventions, atomic commits across projects when needed.

**Structure:**
```
C:\knosso\Bmad/.git           # Main repository
projects/multi-agent-mvp/.gitignore  # Project-specific ignores
```

### 4. No Root-Level Clutter
**Rule:** Only configuration and organizational files at root

**Allowed at root:**
- WORKSPACE_GUIDE.md, CONVENTIONS.md, BMAD_COMPLIANCE.md
- Makefile, .gitignore, .git/
- .bmad/, .claude/, .temp/
- README.md (workspace overview only)

**NOT allowed at root:**
- Source code files (.py, .js, etc.)
- Data files
- Output files
- Project-specific documentation

---

## Project Naming Conventions

### Format
`lowercase-with-dashes`

### Examples
```
✅ multi-agent-mvp
✅ creative-writing-engine
✅ task-dependency-system
❌ MultiAgentMVP
❌ multi_agent_mvp
❌ multiAgentMVP
```

### Project Directory Structure Template
Every project should follow this structure:

```
projects/[project-name]/
├── src/                    # Source code
│   ├── __init__.py        # Makes it a package
│   └── [modules].py       # snake_case modules
├── config/                 # Configuration files
│   └── [configs].json     # JSON configs
├── tests/                  # Test files
│   └── test_[module].py   # Test naming: test_*
├── docs/                   # Project documentation
│   ├── README.md          # Project overview
│   ├── SETUP.md           # Setup instructions
│   └── STRUCTURE.md       # Architecture docs
├── outputs/                # Generated outputs (git ignored)
├── logs/                   # Log files (git ignored)
├── .gitignore             # Project-specific ignores
├── run.py                 # Entry point (if applicable)
└── requirements.txt       # Dependencies (if not stdlib-only)
```

---

## File Management Rules

### 1. Output Files
**Rule:** All generated outputs go in `outputs/` or `logs/`, never committed to git

**Examples:**
```
projects/multi-agent-mvp/outputs/story_001.txt  ✅
projects/multi-agent-mvp/logs/agent_001.log     ✅
projects/multi-agent-mvp/src/generated.txt      ❌
```

### 2. Configuration Files
**Rule:** Config files go in `config/`, environment-specific configs use different files

**Examples:**
```
config/task-queue.json           # Runtime state
config/settings.json             # User settings
config/settings.dev.json         # Dev overrides
config/settings.prod.json        # Prod overrides (git ignored)
```

### 3. Temporary Files
**Rule:** Use workspace-level `.temp/` or project-level `outputs/` for temporary files

**Never:**
- Create temp files in `src/`
- Leave temp files uncommitted in tracked directories
- Use generic names like `test.py`, `temp.json` at root

### 4. Large Files
**Rule:** Files >1MB must be in `outputs/` or `logs/` (git ignored)

**Enforced by:** Pre-commit hook blocks commits with files >1MB in tracked directories

---

## Git Workflow Integration

### Pre-Commit Hook Checks
The workspace enforces quality standards automatically:

1. **Debug statements** - No `print('DEBUG` in Python
2. **Python naming** - Files must be snake_case
3. **File sizes** - No files >1MB in tracked dirs
4. **Secrets** - Warns on API keys (AIzaSy*)
5. **JSON validity** - All .json files must parse
6. **Whitespace** - Warns on trailing whitespace

### Commit Message Format
**Required:** `[AREA] Description`

**Valid areas:**
- `[CORE]` - Core system changes
- `[API]` - API client changes
- `[EXEC]` - Executor changes
- `[DOCS]` - Documentation
- `[TEST]` - Tests
- `[FIX]` - Bug fixes
- `[CLEAN]` - Refactoring
- `[STRUCT]` - Structure changes
- `[EMERGENCY]` - Hotfixes

**Examples:**
```
✅ [CORE] Add file locking to coordinator
✅ [DOCS] Update workspace organization guide
✅ [FIX] Resolve Unicode encoding in Windows
❌ Fixed bug
❌ Updated files
❌ WIP
```

---

## Common Operations

### Creating a New Project
```bash
cd C:\knosso\Bmad
mkdir -p projects/my-new-project/{src,config,tests,docs,outputs,logs}
touch projects/my-new-project/docs/README.md
touch projects/my-new-project/.gitignore
# Add outputs/ and logs/ to .gitignore
```

### Moving Between Projects
```bash
cd C:\knosso\Bmad/projects/multi-agent-mvp
# Work on multi-agent-mvp

cd C:\knosso\Bmad/projects/creative-writing
# Work on creative-writing
```

### Running Tests
```bash
# From project directory
cd projects/multi-agent-mvp
python -m pytest tests/

# Or use Makefile (when created)
make test PROJECT=multi-agent-mvp
```

### Checking Workspace Status
```bash
cd C:\knosso\Bmad
git status                    # See all changes
make status                   # Workspace overview (when Makefile created)
```

---

## Anti-Patterns to Avoid

### ❌ Root-Level Code
```
# BAD
C:\knosso\Bmad/coordinator.py
C:\knosso\Bmad/test.py

# GOOD
C:\knosso\Bmad/projects/multi-agent-mvp/src/coordinator.py
C:\knosso\Bmad/projects/multi-agent-mvp/tests/test_coordinator.py
```

### ❌ Mixing Project Files
```
# BAD
projects/multi-agent-mvp/src/creative_writer.py  # Belongs in different project

# GOOD
projects/multi-agent-mvp/src/coordinator.py
projects/creative-writing/src/creative_writer.py
```

### ❌ Scattered Documentation
```
# BAD
C:\knosso\Bmad/multi-agent-README.md
projects/multi-agent-mvp/docs.txt

# GOOD
docs/CONVENTIONS.md                           # Workspace-level
projects/multi-agent-mvp/docs/README.md       # Project-level
```

### ❌ Hard-Coded Paths
```python
# BAD
file = open("C:\\knosso\\Bmad\\projects\\multi-agent-mvp\\config\\tasks.json")

# GOOD
import os
config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
file = open(os.path.join(config_dir, 'tasks.json'))
```

### ❌ Committing Generated Files
```
# BAD - in git
projects/multi-agent-mvp/outputs/story_001.txt
projects/multi-agent-mvp/logs/agent.log
projects/multi-agent-mvp/__pycache__/

# GOOD - in .gitignore
outputs/
logs/
__pycache__/
*.pyc
```

---

## Maintenance Checklist

### Daily
- [ ] Run `git status` before ending session
- [ ] Commit work with proper `[AREA]` tags
- [ ] Check no temp files left in tracked directories

### Weekly
- [ ] Review BMAD_COMPLIANCE.md status
- [ ] Clean up `outputs/` and `logs/` directories
- [ ] Update project README.md files with new features

### Monthly
- [ ] Review and update CONVENTIONS.md if new patterns emerge
- [ ] Archive old projects if no longer active
- [ ] Check disk space usage in `outputs/` directories

---

## BMAD Methodology Alignment

This workspace structure supports BMAD phases:

1. **Analysis Phase** - Document requirements in project docs/
2. **Architecture Phase** - Design docs in project docs/STRUCTURE.md
3. **Development Phase** - Code in project src/
4. **Review Phase** - Git hooks enforce quality, code review before merge

**Key Principle:** Structure supports workflow, not hinders it.

---

## Quick Reference

| Task | Location |
|------|----------|
| Create new project | `projects/[name]/` |
| Workspace conventions | `docs/CONVENTIONS.md` |
| Project documentation | `projects/[name]/docs/` |
| Source code | `projects/[name]/src/` |
| Tests | `projects/[name]/tests/` |
| Generated output | `projects/[name]/outputs/` |
| Logs | `projects/[name]/logs/` |
| Git hooks | `.git/hooks/` |

---

## Summary

**Three Rules to Remember:**

1. **Projects in `projects/`** - Everything self-contained
2. **Follow conventions** - Snake_case files, [AREA] commits
3. **Git hooks enforce** - Let automation catch mistakes

Following this guide ensures the workspace remains organized, scalable, and BMAD-compliant as complexity grows.

---

*Last Updated: 2025-11-11*
*Version: 1.0*
