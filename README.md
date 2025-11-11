# BMAD Workspace

**Business-Analyst-driven Multi-Agent Development** workspace with foundation hardening, automated quality enforcement, and organizational standards.

## 🎯 Overview

This workspace implements a structured development environment for building multi-agent systems. Phase 2.5 Foundation Hardening is complete, establishing the organizational foundation before scaling to complex features.

## ✨ Key Features

- **Automated Quality Enforcement** - Git hooks validate code before commits
- **Project Isolation** - Each project self-contained in `projects/` directory
- **Comprehensive Documentation** - Standards, workflows, and guides
- **Streamlined Operations** - Makefile for common tasks
- **BMAD Methodology** - Business analyst-driven development workflow

## 📁 Structure

```
bmad-workspace/
├── .git/hooks/          # Pre-commit & commit-msg validation
├── docs/                # Workspace-level documentation
│   ├── BMAD_COMPLIANCE.md      # Methodology checklist
│   ├── GIT_WORKFLOW.md         # Git workflow guide
│   └── BMAD-Agents-Complete-Guide.md
├── projects/            # All projects live here
│   └── multi-agent-mvp/ # Multi-agent system MVP
├── Makefile            # Common operations
└── WORKSPACE_GUIDE.md  # Organization standards
```

## 🚀 Quick Start

### Check Workspace Status
```bash
make status
```

### Create a New Project
```bash
make init PROJECT=my-project
```

### Run Tests
```bash
make test PROJECT=multi-agent-mvp
```

### Clean Outputs
```bash
make clean PROJECT=multi-agent-mvp
```

## 📋 Git Workflow

### Commit Message Format
All commits must follow: `[AREA] Description`

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

**Example:**
```bash
git commit -m "[CORE] Add task dependency validation"
```

### Automated Checks
Pre-commit hooks validate:
- ✅ Python naming conventions (snake_case)
- ✅ No debug print statements
- ✅ JSON file validity
- ✅ File size limits (<1MB)
- ⚠️ API keys warning
- ⚠️ Trailing whitespace warning

## 📚 Documentation

- **[WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md)** - Complete workspace organization guide
- **[docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md)** - Daily git routines and best practices
- **[docs/BMAD_COMPLIANCE.md](docs/BMAD_COMPLIANCE.md)** - BMAD methodology checklist

## 🎓 BMAD Methodology

This workspace follows the BMAD approach:

1. **Analysis Phase** - Business requirements and user stories
2. **Architecture Phase** - System design and technical decisions
3. **Development Phase** - Implementation with quality gates
4. **Review Phase** - Code review and validation

## 🏗️ Current Status

### Phase 2.5: Foundation Hardening - ✅ COMPLETE

All deliverables implemented:
- [x] Git repository initialized
- [x] Pre-commit and commit-msg hooks
- [x] Workspace organization guide
- [x] Makefile for common operations
- [x] Git workflow documentation
- [x] BMAD compliance framework
- [x] Coding conventions

### Phase 3: Task Dependencies - 🔜 NEXT

Planned features:
- Task dependency system with cycle detection
- OpenRouter API integration (free models)
- Resource management and storage
- Creative writing task types

## 🛠️ Projects

### Multi-Agent MVP
**Status:** Week 1-2 complete, 3 concurrent agents operational

A multi-agent system with:
- File-locked JSON task queue (msvcrt on Windows)
- 3 concurrent Gemini agents
- Stress tested: 20 tasks, 0 conflicts
- Stdlib-only implementation
- Rate limiting (4s between requests)

**Location:** `projects/multi-agent-mvp/`

## 📖 Common Operations

### Working with Projects
```bash
# Navigate to project
cd projects/multi-agent-mvp

# Run project
make run PROJECT=multi-agent-mvp

# Run tests
make test PROJECT=multi-agent-mvp

# Clean outputs
make clean PROJECT=multi-agent-mvp
```

### Git Operations
```bash
# Check status (includes git status)
make status

# View commit history
make history

# Run pre-commit checks manually
make check
```

### Workspace Maintenance
```bash
# Generate documentation index
make docs

# Count lines of code
make loc

# Create backup
make backup
```

## 🔒 Security

- API keys managed via environment variables (never committed)
- Pre-commit hook warns about potential secrets
- `.gitignore` configured to exclude sensitive files
- Outputs and logs never committed to version control

## 🤝 Contributing

When adding new features:

1. Follow naming conventions (see WORKSPACE_GUIDE.md)
2. Use proper commit message format
3. Let git hooks validate your work
4. Update documentation when needed
5. Test before committing

## 📊 Metrics

**Phase 2.5 Achievements:**
- 7/7 deliverables complete (100%)
- 4 documentation files (54KB total)
- 2 git hooks with 10+ validation checks
- 1 Makefile with 15+ operations
- 1 initial commit with validated format

## 🎯 Next Steps

1. Run `/bmad:bmm:agents:architect` for Phase 3 design
2. Implement task dependency system
3. Add OpenRouter API client
4. Extend to creative writing tasks
5. Add resource management

## 📄 License

This workspace and all projects within are currently unlicensed. Add appropriate license files as needed.

## 🔗 Links

- **Repository:** https://github.com/proton4444/bmad-workspace
- **BMAD Documentation:** See `docs/` directory
- **Issues & Feedback:** Use GitHub Issues

---

**Last Updated:** 2025-11-11  
**Version:** 1.0 (Phase 2.5 Complete)  
**Status:** Foundation hardening complete, ready for Phase 3
