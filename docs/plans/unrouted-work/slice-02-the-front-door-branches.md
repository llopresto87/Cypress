# Slice 2 — the front door branches

**Status:** implemented 2026-09-14, gate green. **Depends on:** slice 1.

## Why

`from-scratch` is complete and unreachable (evidence E4). Every entry surface
sends every repository — empty or not — into `grow`, the protocol built for the
opposite case. The single link is one conditional clause at `grow.md:555` that
**misdescribes** the target as a sub-step "for intent discovery" when it is a
nine-phase workflow ending in `deliver`.

`initialize` is the node positioned to fix this: it is the adapter the installer
names, and today it forwards unconditionally. The U-40 evaluation recommended
retiring it as an alias. That was wrong — the front door needs a branch, and a
branch is what an adapter belongs as.

## What changes

| File | Change |
|---|---|
| `protocols/initialize.md` | from pass-through to **fork**. Adds `initialize.entry-fork` to `owns:`. Keeps `initialize.adapter-edges` (the prohibitions apply to both arms). `peers:` gains `protocol.from-scratch` |
| `install.sh` | line 770's unconditional "run /initialize to discover the project and grow the graph" becomes shape-aware: it already knows whether the target is empty |
| `core/AGENTS.md` | line ~151 `EXPERT_SEED_INSTALL_PROMPT.md + protocol.grow` gains `protocol.from-scratch`; line 16's "no `docs/graph/` yet" pointer likewise. **Budget: 436 bytes of headroom, shared with slice 4** |
| `protocols/grow.md` | `:555` stops calling `from-scratch` a sub-step "for intent discovery". Grow **hands off**; it does not resume |
| `protocols/from-scratch.md` | entry section (slice 1) names the fork as its primary route |
| `documentation/protocols-reference.md` | both sections follow |

## The fork, precisely

```
/initialize (or INSTALL_PROMPT.md)
  │
  ├── executable project evidence present ──► protocol.grow
  │       (source to scout, ledgers to write, a graph to author from evidence)
  │
  └── empty or near-empty repository ───────► protocol.from-scratch
          (nothing to scout; the nine-phase bootstrap authors the project
           AND its graph, and ends at deliver)
```

The test for "empty" is the one `grow` Phase 1 already applies — no executable
project evidence — so the fork adopts an existing judgement rather than adding a
second, divergent one.

## Contract

- `AN_EMPTY_REPOSITORY_REACHES_FROM_SCRATCH` — the documented entry path, given
  a repository with no executable project evidence, routes to
  `protocol.from-scratch` and not to `protocol.grow`.
- `THE_KERNEL_NAMES_EVERY_ENTRY_PROTOCOL` — every protocol reachable as a first
  move on a fresh repository is named in `core/AGENTS.md`.

## Regression, observed RED first

Extends `tests/test-entry-paths.sh`:

4. `core/AGENTS.md` names `from-scratch` — **RED today**, it never has;
5. `initialize.md` names both arms and the test that chooses between them —
   **RED today**, it names only `grow`;
6. `install.sh`'s post-install line does not tell an empty target to "discover
   the project" — **RED today**;
7. `grow.md` hands off to `from-scratch` rather than calling it a sub-step —
   **RED today**;
8. kernel stays under `KERNEL_BUDGET`.

## Risk

**The kernel edit is the tight one.** 436 bytes of headroom, shared with slice 4,
and the kernel is read on every session of every plant — the rent argument in
CLAUDE.md applies. Budget: ~40 bytes here, ~15 in slice 4. If it does not fit,
the slice is wrong, not the budget (ADR-0007's rule).

**`/initialize` has live host surface** — `install.sh` names it, and the
`claude-code` and `prime-agent` route hooks both carry "/initialize is only a
tool adapter". Those strings stay true: it is still only an adapter. It now
adapts to two protocols instead of one.
