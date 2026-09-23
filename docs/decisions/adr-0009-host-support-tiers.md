# ADR-0009: hosts sit in three support tiers, and `install.sh all` installs only the two that are maintained

## Status

`proposed`. Recorded 2026-09-23 from an owner decision given in chat that day,
which this record transcribes and does not re-open. It becomes `accepted` when
the 7.27.0 increment planned in
[`../plans/grill-7.27.0-host-support-tiers.md`](../plans/grill-7.27.0-host-support-tiers.md)
lands with its tests green. It supersedes no earlier ADR.

Amended 2026-09-23, before ratification (review F1): `install.sh all --check`
also checks the Copilot views when the plant's `.cypress/seed.json` records
`github-copilot`. Checking writes nothing, so it adds no feature to a frozen
host. The consequence below about `all --check` having nothing in scope holds
only for a plant whose record lacks `github-copilot`.

## Date

2026-09-23

## Context

The seed ships five host adapters under `integrations/` and treats them as
equals in three places: `install.sh all` installs every one of them
(`install.sh:1721`), the usage text says so (`install.sh:21`), and
`INSTALL.md:63` repeats it. Feature work has not treated them as equals for
some time. `README.md:158` already calls Claude Code and Prime Agent
"first-class citizens at full parity", and `documentation/host-capability-matrix.md`
shows Codex CLI and GitHub Copilot as `unsupported` for delegation, recursion
bounds and model selection, the three rows the method leans on hardest.

Every host costs something on each change to the shared sources. The eager
surface of each harness is modelled and held to `EAGER_BUDGET` in
`tests/seed-lint.py` (`check_eager_surface`, `:2275`), and GitHub Copilot's is
the largest because each projected skill carries pointer boilerplate
(`COPILOT_POINTER_OVERHEAD`, `:209`). The install suites run every adapter.
A harvest that brings a feature back from a plant has had no rule for which
hosts it owes the feature to, so the default reading has been "all five".

A host research pass on 2026-09-23 made the question concrete. It found that
upstream Codex CLI documents stable, on-by-default hooks (`SessionStart` with a
`source` enum, `UserPromptSubmit` with `session_id`, `PreCompact`), which
contradicts the matrix's "no hook surface" evidence line for Codex. That line
is true of what the seed ships and false as a statement about the host. The
same pass confirmed that VS Code's Copilot agent hooks read
`.claude/settings.json`, so the Claude Code hooks already reach Copilot users
whenever both are present, with `session_id` optional and `source` fixed at
`"new"` on that host.

Doing nothing leaves every future feature owing work to two hosts the owner
does not intend to develop, and leaves the Codex contradiction as an open
invitation to wire hooks for a host nobody is maintaining.

## Decision

**The seed recognises three host support tiers, and `install.sh all` expands
to the first two only.**

| Tier | Hosts | What the seed commits to |
|---|---|---|
| `first-class` | `claude-code`, `prime-agent` | Feature parity is the target. A feature that ships on one is owed to the other, or its absence is recorded as a defect to close. |
| `supported` | `opencode` | Installed by `all`, with its current install surfaces unchanged. A feature reaches opencode only where the host carries it natively. Where it cannot, the gap is recorded in the host matrix and no workaround is built. |
| `frozen` | `codex`, `github-copilot` | Legacy and deprecated. Still installable by name, each such install prints a `DEPRECATED` notice and exits as it does today. Adapter files stay byte-identical apart from a deprecation notice in each README. Existing tests keep running as regression. No new features. |

`install.sh all` becomes `claude-code opencode prime-agent`, in that order,
which is today's order with the two frozen hosts removed.

The tier assignment has one home: three arrays in `install.sh`. The
deprecation notice reads the frozen array. The `all` expansion is a separate
literal, written out to keep install order, and `tests/seed-lint.py`
(`check_host_tiers`) holds it to the first-class and supported arrays. The host
matrix publishes the tier table, and the same check holds that table to the
arrays.

## Consequences

### Installer

- `all` writes fewer destinations into a fresh target: no `.codex/`, no
  `.github/`, no `.github/copilot-instructions.md`. A plant that wants a frozen
  host names it, as in `install.sh all codex`, which the parser already accepts.
- `install.sh codex` and `install.sh github-copilot` print one `DEPRECATED`
  line each on stderr, naming this ADR, and change nothing else. The notice
  goes to stderr so that `codex --print-config` keeps a clean stdout.
- A plant whose `.cypress/seed.json` records a frozen host and is re-run with
  `all` would have its frozen projections silently left at the old seed
  version. The installer names the skipped hosts and the command that
  refreshes them. The stamp's `tools` union is unchanged
  (SPEC-0001 `ADAPTERS_ACCUMULATE`).
- `install.sh all --check` used to verify the Copilot views and will now have
  nothing in scope. It must say so, so that a CI job relying on it does not
  turn into a silent green.

### SPEC-0001

The `all` expansion and the notice are behaviour of the one component that
writes into another repository, so they are new contracts in
`docs/specs/SPEC-0001-install-placement.md` §4, with §10 rows and a §12
changelog entry. The plan names them.

### Host matrix

`documentation/host-capability-matrix.md` gains a support-tier section ahead
of the matrix. The six-class cells stay as they are, since a tier is a
maintenance commitment and the cells describe what the harness holds. The
opencode statement is written there: native only, gaps recorded, no
workarounds.

The Codex hooks contradiction is recorded and **not acted on**. The cell stays
`unsupported`, which is correct under the matrix's own definition ("no
equivalent ships for this host"), and the evidence line gains one sentence
saying that upstream documents hooks, that the seed wires none, and that this
ADR is why. Wiring them would be a new feature on a frozen host.

### Claude Code hooks and Copilot

Freezing Copilot means the seed stops designing for it. It does not stop
Copilot from reading `.claude/settings.json`. Every change to
`integrations/claude-code/{route,status}-hook.py` must therefore keep failing
open on a Copilot-shaped envelope: no `session_id`, `source: "new"`, unknown
fields. A regression test pins that, so the constraint does not live only in
this paragraph. The pre-tool guard is out of scope here; the matrix records
it as `unsupported` on Copilot and it stays so.

### Eager budget in `tests/seed-lint.py`

All five harnesses stay in `check_eager_surface`'s `surfaces` map and all five
stay under `EAGER_BUDGET`. A frozen host still installs, so a plant that
names it still pays that surface on every session. If a change to the shared
sources would push a frozen host alone over the budget while every
`first-class` and `supported` host stays under it, that breach is taken to the
owner as a removal trigger (below). It is never answered by an
`EAGER_EXEMPTIONS` entry or a budget raise; the existing comment at `:184`
already forbids both and this ADR does not relax it. The Codex `≤` footnote in
the matrix stays as written, since correcting that model is work on a frozen
host.

### Harvests and new features

A harvest generalises a feature for the `first-class` hosts. It carries the
feature to opencode where opencode can hold it natively, and otherwise records
the gap in the matrix. It targets no frozen host. A shared-source change that
happens to reach a frozen host through the common kernel, graph or roster is
fine, and the regression suites are what show it did no harm.

### Documentation

`README.md`, `INSTALL.md`, `DOCUMENTATION.md`,
`documentation/corpora-and-integrations-reference.md` and
`integrations/claude-code/README.md` stop describing `all` as five hosts.
`core/AGENTS.md` names the five hosts only as the files each one reads, which
stays true, so the kernel is left alone.

## Alternatives rejected

### Remove the two adapters now

This would delete `integrations/codex/`, `integrations/github-copilot/`, two
`install_*` functions, the Copilot transform and `--check`, and the suites that
cover them. It is the cheapest end state and the one the owner has explicitly
deferred. Plants installed with either host would lose their upgrade path in
the same release that announced the deprecation, with no notice period. The
removal criteria below say when to revisit it.

### Keep `all` at five and add an opt-in `--legacy` flag

The flag would have to mean something for `all` and nothing for a named host,
which is a second vocabulary for a choice the positional argument already
expresses. `install.sh all codex` says the same thing with no new option to
document, test and later remove. Keeping five in `all` also keeps every new
user installing the two hosts the seed has stopped developing.

### Cut opencode's surfaces to what it holds natively

opencode's `model:` and `tools:` projections are read differently by the host
and are recorded as degraded in the matrix. Trimming them would change what
existing opencode plants receive, and the owner's decision was that opencode
keeps its current install surfaces unchanged. What changes for opencode is the
forward rule only: no new workaround.

## Reversibility

`reversible`. Adding `codex` and `github-copilot` back to the `all` array and
deleting the notice restores 7.26.0 behaviour in one session. No plant data is
migrated, because a stamp that records a frozen host is left intact and a
re-run with the host named refreshes it. The only cost of reversing is the
documentation and SPEC-0001 rows written for 7.27.0.

## Removal criteria

Removing a frozen adapter is a separate owner decision and a new ADR that
supersedes the frozen row of this one. Any one of these is reason to put it
to the owner:

1. A shared-source change would push a frozen host alone over `EAGER_BUDGET`
   (see the eager budget consequence above).
2. A frozen host's regression suite fails for a reason rooted in the host's
   own format or discovery rules, where the fix would be new work on that
   adapter.
3. The host's upstream breaks or withdraws a surface the adapter depends on,
   such as Copilot's custom-agent or instruction file formats, or Codex's
   `AGENTS.md` loading.
4. Two consecutive minor releases pass with no harvest, issue or owner report
   showing a plant in use on that host. The seed cannot observe plants, so
   this one depends on the owner saying so.
5. A security finding in a frozen adapter, such as a privilege leak in the
   Copilot `tools:` transform, whose fix is more than restoring its previous
   behaviour.

## Related

- Owner decision: 2026-09-23, recorded in chat and transcribed into
  `docs/plans/grill-7.27.0-host-support-tiers.md` §1.
- [ADR-0003](adr-0003-enforcement-layering-honesty.md), whose labels the host
  matrix's six classes extend.
- `docs/specs/SPEC-0001-install-placement.md`, which gains the tier contracts.
