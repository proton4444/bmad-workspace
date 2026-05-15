# Agent Cleanup and Optimization Plan

Purpose: give an implementation agent a practical, repo-local plan for cleaning, hardening, and optimizing this project without guessing scope or mixing unrelated changes.

Run this from the repository root:

```bash
cd /Users/simone/repos/bmad-workspace
```

## Operating Rules

- Work in small commits. One concern per commit.
- Do not rewrite history or delete tracked content unless the audit step proves it is obsolete.
- Preserve user changes. Start with `git status --short` and stop if unexpected dirty files exist.
- Prefer documentation, ignore rules, validation scripts, and low-risk cleanup before code behavior changes.
- If modifying functions, classes, or methods in an indexed repo, run GitNexus impact analysis first.
- Before any commit, run GitNexus change detection if available.
- Treat secrets, credentials, browser sessions, tokens, and private local paths as high priority.

## Phase 0: Baseline Inventory

Goal: understand exactly what is tracked, stale, generated, or missing.

Commands:

```bash
git status --short
git remote -v
git branch --show-current
git log --oneline -10
find . -maxdepth 3 -type f | sort
du -sh . snapshots _bmad _bmad-output releases docs 2>/dev/null
```

Record:

- Current branch and latest commit.
- Dirty files, if any.
- Large folders and generated-output folders.
- Missing standard files: `README.md`, `LICENSE`, `CONTRIBUTING.md`, `AGENTS.md`, setup docs.
- Whether `docs/` is intentionally empty.

Stop condition: if the worktree is dirty before the agent starts, document the files and ask for direction unless the dirty files are clearly generated and ignored.

## Phase 1: Repository Hygiene

Goal: make the repository understandable and safe to operate.

Tasks:

- Add or update `README.md` with project purpose, setup, daily operations, and maintenance commands.
- Add or update `AGENTS.md` with repo-specific instructions for future agents.
- Decide whether this repository should have a license. If yes, add `LICENSE`; if not, state "private/internal/no license selected" in `README.md`.
- Review `.gitignore` and ensure local/generated files are excluded:

```gitignore
_bmad-output/
*.tmp
.DS_Store
node_modules/
.env
.env.*
*.log
dist/
build/
coverage/
```

- Confirm whether `snapshots/` is intended to be tracked. If it is generated history, document its retention policy.
- Confirm whether `docs/` should remain empty. If not, add an index file.

Verification:

```bash
git status --short
git diff --check
```

Expected result: the repo root explains what this project is, how to work in it, and what should not be committed.

## Phase 2: Secret and Sensitive Data Audit

Goal: remove accidental credential risk before deeper work.

Commands:

```bash
rg -n --hidden --glob '!.git/**' --glob '!node_modules/**' \
  'api[_-]?key|token|secret|password|passwd|bearer|authorization|cookie|session|client_secret|private_key|OPENAI|ANTHROPIC|GEMINI|GITHUB|PATREON'

find . -type f \( -name '.env*' -o -name '*token*' -o -name '*secret*' -o -name '*cookie*' -o -name '*session*' \) \
  -not -path './.git/*'
```

Tasks:

- Move real secrets out of tracked files.
- Replace examples with `.env.example` placeholders.
- Add ignore rules for local credential material.
- If a real secret was committed, mark it as compromised and rotate it outside this repo.

Verification:

```bash
git diff --check
git status --short
```

Stop condition: if real credentials are found, do not continue normal cleanup until the owner confirms rotation or accepts the risk.

## Phase 3: Structure and Documentation Cleanup

Goal: make project structure match actual usage.

Tasks:

- Create a concise root structure section in `README.md`.
- Move orphaned docs into `docs/` if they are project documentation.
- Add `docs/INDEX.md` if `docs/` will contain durable references.
- Document `_bmad/`, `_bmad-output/`, `releases/`, and `snapshots/`.
- Check that dated snapshots have a clear retention rule:
  - keep all snapshots if they are audit evidence;
  - otherwise keep latest N and archive older ones outside the repo.

Verification:

```bash
find . -maxdepth 2 -type f | sort
git diff --stat
```

Expected result: a new agent can tell which files are source, which are generated, and which are historical records.

## Phase 4: Automation and Quality Gates

Goal: make routine checks repeatable.

Tasks:

- Add a `Makefile` or script only if there is not already a local command convention.
- Recommended commands:
  - `make status`: git status plus important folder sizes.
  - `make audit`: secret scan, markdown check if available, and `git diff --check`.
  - `make docs`: verify docs index and required root docs exist.
- Avoid adding heavyweight dependencies unless the repo already uses them.

Suggested minimal checks:

```bash
git diff --check
rg -n --hidden --glob '!.git/**' 'TODO|FIXME|XXX|HACK'
```

Verification:

```bash
make audit
```

Expected result: future cleanup can be verified with one command.

## Phase 5: GitHub Portfolio Review

Goal: prioritize cleanup across the public `proton4444` repositories.

Priority order:

1. `bmad-workspace`: active operational repo; fix docs, license, ignore rules, and validation first.
2. `board-studio`: TypeScript app; review default branch, open issue, build/test/lint, local persistence, and UI workflow.
3. `patreon-mcp`: security-sensitive automation repo; audit secrets, browser sessions, Patreon credentials, Playwright config, and package scripts.
4. `TradingAgents`, `multi-agent-pipeline`, `weavy-gemini-frontend`, `alpha`: audit dependencies, setup docs, and AI/API key handling.
5. Forks and archived repos: only clean if actively used or publicly presented as maintained.

For each repo:

```bash
git clone <repo-url>
cd <repo>
git status --short
find . -maxdepth 2 -type f | sort
rg -n --hidden --glob '!.git/**' 'api[_-]?key|token|secret|password|bearer|cookie|session|client_secret'
```

Then produce one issue list with:

- security risks;
- broken setup or build steps;
- missing docs/license;
- stale generated files;
- dependency problems;
- recommended first commit.

## Phase 6: Optimization Pass

Goal: improve maintainability after hygiene and security are stable.

Tasks:

- Remove duplicate docs or consolidate them behind indexes.
- Standardize naming and dates in release/snapshot files.
- Add lightweight metadata where useful: owner, status, last reviewed date.
- Review recurring nightly health commits and confirm they add signal. If they are noisy, propose changing the automation to update a single status file or open an issue instead of committing every day.
- Keep optimization changes separate from security and docs commits.

Verification:

```bash
git diff --stat
git diff --check
git status --short
```

Expected result: less repository noise, clearer history, and fewer ambiguous files.

## Final Deliverables

The agent should finish with:

- A short audit report committed as Markdown, or a clearly named issue list.
- Root documentation updated enough for a new agent to operate safely.
- `.gitignore` covering generated and sensitive local files.
- A reproducible audit command or `Makefile` target.
- A prioritized backlog for changes that were intentionally not made.

Suggested commit sequence:

```bash
git add README.md AGENTS.md docs .gitignore Makefile AGENT_CLEANUP_OPTIMIZATION_PLAN.md
git commit -m "docs: add repo cleanup and agent operating plan"

git add <security-doc-or-ignore-updates>
git commit -m "chore: harden local secret and generated file handling"

git add <automation-files>
git commit -m "chore: add repository audit checks"
```

Before committing, run:

```bash
git diff --check
git status --short
```

If GitNexus is configured for this repo, also run its change detection before committing.
