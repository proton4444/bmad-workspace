# Git Workflow and Routine

## Purpose
This document defines the git workflow and daily routines for the BMAD workspace. Following these practices ensures code quality, traceability, and prevents structural decay.

---

## Quick Reference

### Daily Workflow
```bash
# Start of session
cd C:\knosso\Bmad
git status                          # Check current state
git pull                            # Get latest changes (if remote exists)

# During work
git add [files]                     # Stage changes
git commit -m "[AREA] Description"  # Commit with proper format

# End of session
git status                          # Verify nothing uncommitted
git log --oneline -5                # Review recent commits
```

### Commit Message Format
```
[AREA] Description

Valid areas: CORE, API, EXEC, DOCS, TEST, FIX, CLEAN, STRUCT, EMERGENCY
```

---

## Git Philosophy

### Sacred Rule #1: Git Commit Discipline
**"No session ends without committing work or explicitly documenting why not."**

**Why:**
- Preserves progress
- Creates audit trail
- Enables rollback
- Communicates changes

**Implementation:**
- Commit at logical checkpoints (feature complete, tests passing)
- Never commit broken code unless marked `[EMERGENCY]`
- Use descriptive messages that future-you will understand

---

## Commit Areas Explained

### [CORE] - Core System Changes
**Use for:** Changes to fundamental system components

**Examples:**
```bash
git commit -m "[CORE] Add file locking to task queue"
git commit -m "[CORE] Implement coordinator retry logic"
git commit -m "[CORE] Refactor agent state management"
```

**Guidelines:**
- Changes to coordinator, queue management, file locking
- State management modifications
- Core algorithm changes

### [API] - API Client Changes
**Use for:** Changes to external API integrations

**Examples:**
```bash
git commit -m "[API] Add rate limiting to Gemini client"
git commit -m "[API] Implement OpenRouter client"
git commit -m "[API] Fix API error handling"
```

**Guidelines:**
- New API client implementations
- Changes to existing API wrappers
- Authentication and credential handling

### [EXEC] - Executor Changes
**Use for:** Changes to agent executor implementations

**Examples:**
```bash
git commit -m "[EXEC] Add Gemini executor with retry logic"
git commit -m "[EXEC] Implement creative writing executor"
git commit -m "[EXEC] Fix executor timeout handling"
```

**Guidelines:**
- New executor types
- Executor-specific logic
- Task execution changes

### [DOCS] - Documentation
**Use for:** Documentation updates (no code changes)

**Examples:**
```bash
git commit -m "[DOCS] Update workspace organization guide"
git commit -m "[DOCS] Add API rate limiting documentation"
git commit -m "[DOCS] Fix typos in CONVENTIONS.md"
```

**Guidelines:**
- README updates
- Documentation file changes
- Comment improvements (if standalone commit)

### [TEST] - Tests
**Use for:** Test additions or modifications

**Examples:**
```bash
git commit -m "[TEST] Add unit tests for file locking"
git commit -m "[TEST] Create stress test for 20 concurrent agents"
git commit -m "[TEST] Fix flaky API test"
```

**Guidelines:**
- New test files
- Test updates
- Test infrastructure changes

### [FIX] - Bug Fixes
**Use for:** Fixing broken functionality

**Examples:**
```bash
git commit -m "[FIX] Resolve Unicode encoding in Windows terminal"
git commit -m "[FIX] Correct file path after reorganization"
git commit -m "[FIX] Handle edge case in task assignment"
```

**Guidelines:**
- Fixes that don't change architecture
- Error handling improvements
- Edge case corrections

### [CLEAN] - Code Cleanup
**Use for:** Refactoring without functional changes

**Examples:**
```bash
git commit -m "[CLEAN] Remove debug print statements"
git commit -m "[CLEAN] Rename variables for clarity"
git commit -m "[CLEAN] Extract helper function"
```

**Guidelines:**
- Refactoring
- Code style improvements
- Dead code removal

### [STRUCT] - Structure Changes
**Use for:** Project structure and organization changes

**Examples:**
```bash
git commit -m "[STRUCT] Reorganize into src/config/tests/ layout"
git commit -m "[STRUCT] Move docs to project subdirectories"
git commit -m "[STRUCT] Initialize new project structure"
```

**Guidelines:**
- File/directory moves
- Project reorganization
- Structure template changes

### [EMERGENCY] - Hotfixes
**Use for:** Breaking build fixes, critical issues

**Examples:**
```bash
git commit -m "[EMERGENCY] Fix broken imports after reorganization"
git commit -m "[EMERGENCY] Restore accidentally deleted config file"
```

**Guidelines:**
- Only for builds that won't run
- Critical data loss prevention
- Should be rare (indicates process breakdown)

---

## Daily Workflow Detailed

### Morning Routine (Start of Session)

```bash
# 1. Navigate to workspace
cd C:\knosso\Bmad

# 2. Check status
git status
# Expected: Clean working tree or known uncommitted work

# 3. Review recent history
git log --oneline --decorate -10
# Review what was done last session

# 4. If remote exists (future)
# git pull
# Get latest changes from team
```

**Questions to ask yourself:**
- Is there uncommitted work from last session?
- Did I leave a note about why?
- Are there conflicts to resolve?

### During Work

#### Checkpoint Commits
**Pattern:** Commit at logical breakpoints

```bash
# Complete a feature
git add src/new_feature.py
git commit -m "[CORE] Add task dependency validation"

# Add tests
git add tests/test_task_deps.py
git commit -m "[TEST] Add tests for task dependencies"

# Update docs
git add docs/STRUCTURE.md
git commit -m "[DOCS] Document task dependency system"
```

**Frequency:** Every 30-60 minutes of productive work, or when feature is complete

#### Viewing Changes Before Commit
```bash
# See what changed
git diff

# See what's staged
git diff --cached

# See specific file changes
git diff src/coordinator.py
```

#### Staging Strategies

**Option 1: Stage all changes**
```bash
git add .
git commit -m "[AREA] Description"
```

**Option 2: Stage specific files**
```bash
git add src/coordinator.py src/executor.py
git commit -m "[CORE] Update coordinator and executor"
```

**Option 3: Interactive staging** (for partial file commits)
```bash
git add -p src/coordinator.py
# Interactively choose which changes to stage
git commit -m "[CORE] Update task assignment logic"
```

### Evening Routine (End of Session)

```bash
# 1. Check for uncommitted changes
git status

# 2. Review what changed today
git log --oneline --since="1 day ago"

# 3. If work is complete, commit it
git add [files]
git commit -m "[AREA] Description"

# 4. If work is incomplete, create a note
echo "WIP: Implementing task dependencies - 60% complete" > .temp/session_notes.txt
# Don't commit broken code

# 5. If remote exists (future)
# git push
```

**Checklist:**
- [ ] All completed work committed
- [ ] No debug print statements left in code
- [ ] Tests pass (if applicable)
- [ ] Documentation updated if needed
- [ ] Session notes created if work incomplete

---

## Git Hooks Integration

### Pre-Commit Hook
**Location:** `.git/hooks/pre-commit`

**What it checks:**
1. No debug print statements
2. Python files use snake_case naming
3. No files >1MB
4. No hardcoded API keys (warns)
5. JSON files are valid
6. No trailing whitespace (warns)

**If hook blocks commit:**
```bash
# Fix the issues
[Fix the problems indicated]

# Try again
git add [files]
git commit -m "[AREA] Description"
```

**Emergency bypass (use rarely):**
```bash
git commit --no-verify -m "[EMERGENCY] Description"
# Only use when hook is wrong or urgent fix needed
```

### Commit-Msg Hook
**Location:** `.git/hooks/commit-msg`

**What it checks:**
- Commit message follows `[AREA] Description` format
- AREA is one of the valid values
- Description is not empty

**If hook blocks commit:**
```bash
# Rewrite commit message
git commit -m "[FIX] Correct task assignment logic"
# Not: git commit -m "fixed bug"
```

---

## Advanced Workflows

### Feature Branch Pattern (Future)
When working on large features:

```bash
# Create feature branch
git checkout -b feature/task-dependencies

# Work on feature with regular commits
git commit -m "[CORE] Add dependency graph structure"
git commit -m "[CORE] Implement cycle detection"
git commit -m "[TEST] Add dependency tests"

# Merge back to main when complete
git checkout main
git merge feature/task-dependencies
git branch -d feature/task-dependencies
```

### Fixing a Mistake

#### Wrong commit message
```bash
# Fix most recent commit message
git commit --amend -m "[CORRECT] New message"
```

#### Forgot to add file
```bash
# Add file to previous commit
git add forgotten_file.py
git commit --amend --no-edit
```

#### Committed to wrong branch
```bash
# Create new branch with current commits
git branch correct-branch

# Reset current branch to before commits
git reset --hard HEAD~2  # Go back 2 commits

# Switch to new branch
git checkout correct-branch
```

#### Need to undo last commit (keep changes)
```bash
git reset --soft HEAD~1
# Changes still staged, commit is gone
```

#### Need to undo last commit (discard changes)
```bash
git reset --hard HEAD~1
# WARNING: Changes are lost forever
```

---

## Makefile Integration

### Using Make for Git Operations

```bash
# Check workspace status (includes git status)
make status

# View commit history
make history

# Run pre-commit checks manually
make check

# Clean outputs before committing
make clean
```

---

## Best Practices

### 1. Atomic Commits
**Rule:** One logical change per commit

```bash
# GOOD - Separate commits
git commit -m "[CORE] Add task dependencies"
git commit -m "[TEST] Add tests for dependencies"
git commit -m "[DOCS] Document dependency system"

# BAD - Mixed concerns
git commit -m "[CORE] Add dependencies and fix bugs and update docs"
```

### 2. Descriptive Messages
**Rule:** Message should explain WHY, not just WHAT

```bash
# GOOD
git commit -m "[FIX] Add rate limiting to prevent 429 errors from Gemini API"

# BAD
git commit -m "[FIX] Fixed API"
```

### 3. Commit Complete Work
**Rule:** Don't commit half-implemented features

```bash
# GOOD
git commit -m "[CORE] Implement task dependency validation with cycle detection"

# BAD
git commit -m "[CORE] WIP task dependencies"
```

**Exception:** End of day with incomplete work - create session notes instead

### 4. Test Before Commit
**Rule:** Ensure code works before committing

```bash
# Run tests
make test PROJECT=multi-agent-mvp

# If tests pass
git commit -m "[CORE] Add new feature"

# If tests fail
# Fix issues first, then commit
```

### 5. Keep Commits Small
**Rule:** Smaller commits are easier to review and revert

```bash
# GOOD - Can revert color change without losing validation
git commit -m "[CLEAN] Standardize error message colors"
git commit -m "[CORE] Add input validation to task queue"

# BAD - Reverting would lose both changes
git commit -m "[CORE] Add validation and change colors and fix bug"
```

---

## Common Scenarios

### Scenario 1: Fixed a bug during feature work
```bash
# Commit the bugfix separately
git add src/coordinator.py  # Bug fix
git commit -m "[FIX] Correct race condition in task assignment"

# Then commit feature work
git add src/task_deps.py
git commit -m "[CORE] Add task dependency graph"
```

### Scenario 2: Made changes across multiple projects
```bash
# Commit each project separately
git add projects/multi-agent-mvp/
git commit -m "[CORE] Update multi-agent task queue"

git add projects/creative-writing/
git commit -m "[CORE] Update creative-writing task queue"
```

### Scenario 3: Updated conventions that affect code
```bash
# Commit convention change first
git add docs/CONVENTIONS.md
git commit -m "[DOCS] Add new naming convention for executors"

# Then commit code conforming to new convention
git add projects/multi-agent-mvp/src/executor_*.py
git commit -m "[CLEAN] Rename executors per updated conventions"
```

### Scenario 4: Emergency fix during feature work
```bash
# Stash current work
git stash

# Fix the emergency
git add src/broken_file.py
git commit -m "[EMERGENCY] Fix broken imports"

# Resume feature work
git stash pop
```

---

## Git Ignore Strategy

### Workspace-Level .gitignore
**Location:** `C:\knosso\Bmad\.gitignore`

```
# Temporary files
.temp/
output/
*.tmp

# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
```

### Project-Level .gitignore
**Location:** `projects/[name]/.gitignore`

```
# Project outputs
outputs/
logs/

# Environment
.env
.env.local

# Dependencies (if not stdlib-only)
venv/
node_modules/

# Build artifacts
dist/
build/
*.egg-info
```

---

## Troubleshooting

### Hook is blocking valid commit
```bash
# Check what's wrong
git status
git diff --cached

# If hook is wrong, bypass once
git commit --no-verify -m "[AREA] Description"

# Then fix the hook
nano .git/hooks/pre-commit
```

### Accidentally committed sensitive data
```bash
# Remove from last commit
git reset --soft HEAD~1
# Edit files to remove sensitive data
git add .
git commit -m "[FIX] Remove sensitive data"
```

### Merge conflict (future, with remote)
```bash
# Pull latest
git pull

# Git will mark conflicts in files
# Edit files to resolve

# Mark as resolved
git add [resolved files]
git commit -m "[FIX] Resolve merge conflicts"
```

---

## Integration with BMAD Phases

### Analysis Phase
```bash
git commit -m "[DOCS] Add product requirements document"
git commit -m "[DOCS] Create user stories"
```

### Architecture Phase
```bash
git commit -m "[DOCS] Add system architecture document"
git commit -m "[DOCS] Define API contracts"
```

### Development Phase
```bash
git commit -m "[CORE] Implement feature per architecture"
git commit -m "[TEST] Add tests per requirements"
```

### Review Phase
```bash
git commit -m "[DOCS] Add code review notes"
git commit -m "[FIX] Address review feedback"
```

---

## Summary

### The Five Commandments

1. **Commit at logical checkpoints** - Not too often, not too rare
2. **Use correct [AREA] tags** - Let hooks enforce format
3. **Write descriptive messages** - Future-you will thank you
4. **Test before committing** - Don't break the build
5. **Review before pushing** - Check `git log` and `git status`

### Daily Checklist

**Morning:**
- [ ] `git status` to check state
- [ ] `git log` to review history

**During:**
- [ ] Commit every 30-60 min of productive work
- [ ] Use proper `[AREA]` tags
- [ ] Write descriptive messages

**Evening:**
- [ ] `git status` to check uncommitted work
- [ ] Commit completed work
- [ ] Create session notes if work incomplete
- [ ] `git log --since="1 day ago"` to review day

---

*Last Updated: 2025-11-11*
*Version: 1.0*
