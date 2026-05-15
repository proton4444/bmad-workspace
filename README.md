# bmad-workspace

Operational workspace for the Mac Mini home lab. Tracks the BMAD framework installation, nightly health snapshots, tool version history, and release notes.

## Purpose

This repository is the durable record for:

- **BMAD framework** — installed skill manifests and module configuration (`_bmad/`)
- **Nightly health snapshots** — daily automated reports of service state, repo sync status, and system inventory (`snapshots/`)
- **Release notes** — version change records for major tool upgrades (`releases/`)
- **Installed versions** — current tool version table (`versions.md`)

This is not a source code repository. It is an operational log and configuration store.

## Structure

```
bmad-workspace/
├── _bmad/                  # BMAD framework installation — do not edit manually
│   ├── _config/            # Agent manifests, file manifests, skill manifest
│   ├── core/               # Core module config and help index
│   └── bmm/                # BMM module config and help index
├── snapshots/              # Nightly health reports (one file per day)
├── releases/               # Version release notes (one file per event)
├── docs/                   # Reference documentation (sparse by design)
├── versions.md             # Current installed tool versions
└── AGENT_CLEANUP_OPTIMIZATION_PLAN.md  # Cleanup plan for this repo
```

## Snapshot Retention Policy

Snapshots in `snapshots/` are audit evidence for the nightly health check automation. All snapshots are retained. The automation runs via launchd at 3am PT (job: `ai.claude.nightly-health`) and commits directly to this repo.

If snapshot accumulation becomes a storage concern, archive snapshots older than 90 days to a separate branch rather than deleting them.

## Daily Operations

The nightly health check runs automatically. No manual steps required during normal operation.

To run the health check manually:

```bash
stack-health    # Check service status
inventory       # Check repo/agent/structure state
```

These commands are defined in `~/repos/macmini-infra/`.

## Maintenance

```bash
make status     # git status + folder sizes
make audit      # secret scan + diff check
make docs       # verify required root docs exist
```

## Related Repos

- `~/repos/macmini-infra/` — canonical source for launchd jobs, service config, and operational runbooks
- `~/dev/SimOne9000` — primary application stack
