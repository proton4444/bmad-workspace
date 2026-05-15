# AGENTS.md — bmad-workspace

Instructions for agents operating in this repository.

## What This Repo Is

Operational log and configuration store for the Mac Mini home lab. Not a source code repo. No build steps, no tests, no deployments originating here.

## What Agents Should Know

### `_bmad/` is managed by the BMAD installer

Do not manually edit files in `_bmad/`. This directory is written by the BMAD CLI during installs and upgrades. If BMAD config needs to change, use the BMAD installer commands — do not patch files directly.

### Snapshots are append-only

`snapshots/` contains one file per day written by the nightly health check automation (`ai.claude.nightly-health` launchd job). Do not delete or modify snapshot files. Do not add snapshots manually. If you need to inspect recent health state, read the latest file in `snapshots/`.

### The authoritative operational source is macmini-infra

This repo tracks outputs and artifacts. The canonical source for how the stack works — launchd plists, service config, runbooks — lives in `~/repos/macmini-infra/`. If this repo conflicts with macmini-infra docs, macmini-infra wins.

### Nightly commit noise is expected

Git history will show daily `chore: nightly health check` commits. This is expected behavior from the automation. Do not try to squash, rebase, or clean this history.

## Allowed Agent Actions

- Read any file in this repo
- Update `README.md`, `AGENTS.md`, `docs/`, `.gitignore`, `Makefile`
- Add `versions.md` entries when tool versions change
- Add files to `releases/` when a meaningful upgrade is documented
- Run `make audit` or `make status`

## Prohibited Agent Actions

- Do not edit `_bmad/` directly
- Do not delete or modify `snapshots/` files
- Do not push to main without user confirmation if changes are non-trivial
- Do not add secrets, credentials, or local absolute paths to tracked files

## Commit Convention

```
docs: ...       # README, AGENTS, docs/
chore: ...      # gitignore, Makefile, automation-related
release: ...    # releases/ entries
```

Nightly automation uses: `chore: nightly health check YYYY-MM-DD`
