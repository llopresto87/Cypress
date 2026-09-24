# Host capability matrix

"Tool agnostic" describes the *method*: the same kernel, protocols, skills,
and agent charters apply on every adapter. It does not describe
*enforcement*: five adapters read the same source files through five very
different mechanisms, and some of those mechanisms silently drop a
guarantee the source frontmatter claims. This document keeps three things
distinct that a single "supported / not supported" table would blur:

- **Method parity**: does the adapter carry the same protocols, skills,
  and agent charters? (Yes, on all five, two of them frozen, see Support
  tiers. `install.sh`'s five `install_*` functions place or project the
  identical seed sources.)
- **Artifact parity**: does the adapter's *projection* of a source file
  preserve every field (frontmatter included)? (No. Codex and GitHub
  Copilot both drop fields the source carries; see "model selection" and
  "tool allowlists" below.)
- **Enforcement parity**: when a frontmatter field claims a bound (a tool
  allowlist, a recursion depth, a model class), does the *harness itself*
  hold the line, or does holding it depend on the model reading and obeying
  prose? This is the honesty distinction `docs/decisions/adr-0003-enforcement-layering-honesty.md`
  draws for Claude Code alone (**hard** = the harness refuses, **soft** = a
  contract or a tool refuses (lint plus prose plus the brief), **detective** =
  asserted post-hoc from named evidence a person reads, **judgment** = a named
  agent or person decides and no tool can, the fourth label its 2026-09-14
  amendment added), extended here across all five hosts.

Every cell below is one of exactly six classes. They are not a second
vocabulary: they are ADR-0003's labels split by *why* a host lands where it
does, because one "supported / not supported" column would blur a missing
feature, a lossy transform, and a field the harness never reads. The
right-hand column says which ADR-0003 label each class is.

| Class | Meaning | ADR-0003 |
|---|---|---|
| **mechanically enforced** | The harness itself reads this and holds the bound at runtime, or automatically fires the mechanism (a wired hook). A hook that only injects text fires on its event and holds nothing. | `hard` where the harness holds a bound; `not a control` where a wired hook only fires and injects text (the Session-start, Routing and Status hook rows) |
| **observed** | Works as described, verified against the source/docs cited, but through a different mechanism than the reference case: not weaker, just not the same shape (e.g. Prime Agent's roster). | `hard` where the host's own primitive holds it, `soft` where the agent does; the row below says which |
| **projected** | The seed generates a host-native artifact from the universal source (a transform), and the *projection step* is what to trust, not the source file directly. | `hard` over the generated artifact where the host honors it; each row names what the transform drops and any condition on it being installed at all |
| **brief-enforced** | Nothing in the harness reads this field; it holds only if the spawned worker's brief carries it and the model follows it. | `soft` |
| **degraded** | The capability exists but delivers materially less than the reference case, on the same host, because of a field mismatch or a projection choice, not because the host lacks the feature outright. | `soft` |
| **unsupported** | No equivalent ships for this host at all. | none: the bound is not held on this host |

No cell is `detective` or `judgment`, because this table asks one question only:
does the harness hold the bound at runtime. The seed's `detective` and
`judgment` controls (the `produced_by` assertion, the gate tables in `graft`,
`grow` and `harvest`) are host-independent, and each is classed in its own
node.

Source for every `install_*` function: `install.sh`. Source for every hook
wiring: each adapter's `integrations/<name>/settings.json` (or `.ts`
extension, or `.toml` example) and its `README.md`. Version measured:
manifest.json's current version at the time of this pass (see the
Measurements section).

## Support tiers (ADR-0009)

A tier is a maintenance commitment, set by
[ADR-0009](../docs/decisions/adr-0009-host-support-tiers.md). It says what the
seed owes each host on the next change; the matrix below says what each harness
holds today, so the two do not replace each other and no cell below moved when
the tiers were set. The assignment's one home is the three tier arrays in
`install.sh`, and `tests/seed-lint.py` (`check_host_tiers`) holds this table to
them. `install.sh all` installs the first-class and supported hosts; a frozen
host installs only when it is named, as in `install.sh all codex`, and prints a
`DEPRECATED` notice.

| Tier | Hosts | What the seed commits to |
|---|---|---|
| `first-class` | `claude-code`, `prime-agent` | Feature parity is the target. A feature that ships on one is owed to the other, or its absence is recorded as a defect to close. |
| `supported` | `opencode` | Installed by `all`, with its install surfaces unchanged. |
| `frozen` | `codex`, `github-copilot` | Still installable by name, with a `DEPRECATED` notice. No new features; the existing tests run as regression. |

A feature reaches opencode only where the host carries it natively; where it
cannot, the gap is recorded in this matrix and no workaround is built. A
harvest generalises a feature for the first-class hosts, carries it to
opencode under that rule, and targets no frozen host.

## The matrix

| Capability | Claude Code | opencode | Codex CLI | GitHub Copilot | Prime Agent |
|---|---|---|---|---|---|
| Root kernel loading | mechanically enforced | mechanically enforced | mechanically enforced | mechanically enforced | mechanically enforced |
| Specialist discovery/registration | mechanically enforced | degraded | unsupported | projected | observed |
| Delegation mechanism | mechanically enforced | mechanically enforced | unsupported | unsupported | mechanically enforced |
| Recursion bound | brief-enforced¹ | mechanically enforced | unsupported | unsupported | mechanically enforced² |
| Tool allowlists | mechanically enforced | degraded | unsupported | projected | brief-enforced |
| Model selection | mechanically enforced | degraded | unsupported | unsupported | brief-enforced |
| Session-start hook | mechanically enforced | unsupported | unsupported | projected³ | mechanically enforced |
| Routing hook | mechanically enforced | unsupported | unsupported | projected³ | mechanically enforced |
| Status hook | mechanically enforced | unsupported | unsupported | projected³ | mechanically enforced |
| Per-session injection dedup | mechanically enforced | unsupported | unsupported | degraded³ | unsupported⁵ |
| Pre-tool guard | mechanically enforced | unsupported | unsupported | unsupported | unsupported |
| Slash commands | mechanically enforced | mechanically enforced | unsupported | mechanically enforced | mechanically enforced |
| Always-applied instructions | mechanically enforced (26 261 B) | mechanically enforced (26 261 B) | mechanically enforced (≤ 26 261 B)⁴ | mechanically enforced (31 905 B) | mechanically enforced (24 444 B) |

¹ The leaf/coordinator split (who holds `Task` at all) is read by the
harness from each agent's `tools:` line, and ADR-0003 classes that read
`hard` for what the harness reads and nothing wider. What the split leaves
open is recorded in the [leaf spawn row of the enforcement table](../DOCUMENTATION.md#enf-leaf-cannot-spawn).
The *numeric* `max_spawn_depth`
ceiling is not read by the harness at all; only `agent-lint.py --lint`
checks it statically. The cell reflects the numeric ceiling, since that is
what "recursion bound" asks for a coordinator that does hold `Task`.

² Real runtime ceiling (`RLM_MAX_DEPTH`), but its **default is 2**, one
short of the seed's deepest chain (3), and it is not settable from a
committed project file; see below.

³ Real hook point, but only installed when `.claude/settings.json` is
absent (both are read by VS Code), and it is a Preview API.

⁴ A ceiling, not a measurement. `check_eager_surface()` models Codex with the
Claude Code formula (kernel + agent descriptions + skill descriptions), but
Codex enumerates no roster (see "Specialist discovery/registration:
unsupported"): the `.codex/agents/*.md` files `install_codex` places are
reference copies the harness never reads, so what a Codex session actually pays
is the kernel plus the skill descriptions its global `config.toml` registers.
The budget therefore holds Codex to a number larger than it spends, which is
the safe direction for a ratchet and the wrong direction for a claim, hence
the `≤`. Correcting the model means editing `check_eager_surface()`, which
would move the one home of these figures.

⁵ No injection dedup ships: `route-extension.ts` keeps no state and injects in
full on every prompt. What Prime Agent has instead is a model-kept set of
surfaced node ids, `_cypress_surfaced`, in the session's IPython kernel, which
the overlay asks the model to keep. Its ADR-0003 label is `soft`, and it is
model-cooperative: no harness reads it, and it holds only while the model
follows the overlay. That is not one of the six classes, so it is recorded
here and not in the cell (see "Per-session injection dedup" below).

## Per-capability evidence

### Root kernel loading

Every adapter auto-loads its kernel file by the host's own convention, no
config key required:

- Claude Code: `CLAUDE.md` at the project root (`install_claude_code`,
  `place_kernel()` in `install.sh`).
- opencode: `AGENTS.md`, falling back to `CLAUDE.md` if opencode-native
  files are absent (`integrations/opencode/README.md`, "opencode is
  Claude-Code-compatible by default").
- Codex CLI: `AGENTS.md`, walking up to the project root, truncated at
  `project_doc_max_bytes` (default 32 KiB; the seed's kernel is ~7.5 KB, so
  it fits, but the shipped `config.toml.example` still raises the budget to
  65536 to leave room for referenced files); see `integrations/codex/README.md`.
- GitHub Copilot: **both** `.github/copilot-instructions.md` (Copilot's own
  convention) **and** `AGENTS.md` (which Copilot also reads) get the same
  kernel body (`install_github_copilot()` in `install.sh`).
- Prime Agent: `AGENTS.md`, auto-loaded through a separate context-file walk
  (`integrations/prime-agent/README.md`). Shares the identical byte-for-byte
  file with a co-installed Claude Code via `place_kernel`'s symlink-or-copy
  logic, so the kernel never forks between the two.

All five: **mechanically enforced**. Method and artifact both stay in
parity here; the differences are budget mechanics, not enforcement.

### Specialist discovery/registration

- **Claude Code: mechanically enforced.** `.claude/agents/*.md` is a
  native Claude Code convention; the harness enumerates it at session
  start and spawns by name via `Task`.
- **opencode: degraded.** `.opencode/agents/*.md` is discovered the same
  way, but opencode's agent-markdown contract is not a superset of the
  seed's frontmatter: it does not recognize the seed's `model:` or `tools:`
  shapes at all (see below). Discovery itself works; what an agent is
  *allowed and modeled as* once discovered does not
  (`integrations/opencode/README.md`, "Known gap: the agent frontmatter is
  Claude-Code-shaped").
- **Codex CLI: unsupported.** `integrations/codex/README.md`: "Codex does
  not support `.claude/`-style directories of subagents out of the box;
  subagents are configured globally in `~/.codex/config.toml`." The seed
  places `.codex/agents/*.md` as reference copies, but the shipped
  `config.toml.example` carries no `[agents]` section. The mapping table
  in the README names one as the destination, but `install.sh` never
  generates it (grep confirms no `[agents]` anywhere in
  `integrations/codex/config.toml.example`). The documented fallback is
  "including their contents in `AGENTS.md`", i.e., prose, not a
  registration mechanism.
- **GitHub Copilot: projected.** `install_github_copilot`
  (`install_github_copilot()` in `install.sh`) transforms every `docs/graph/agents/*.md` into
  `.github/agents/<name>.agent.md` with rewritten frontmatter (a Python
  heredoc strips the universal frontmatter and re-derives `description:` +
  a Copilot-native `tools:` array; `model:` is dropped entirely, and there is
  no field for it in the generated file). VS Code's own custom-agent
  feature then discovers that directory natively. The *discovery* is real
  and host-native; what survives the transform is a subset.
- **Prime Agent: observed.** No static roster is enumerated at session
  start at all, by design. `agents/*.md` land as on-disk **brief
  sources**; the orchestrator reads one and spawns a child with
  `rlm(brief + task)` at the moment it is needed
  (`integrations/prime-agent/APPEND_SYSTEM.md`, "Delegation — recursive
  subagents, not a Task tool"). This is not a weaker version of
  registration: there is no "installed but not yet spawnable" lag the way
  there is on Claude Code/opencode after a fresh install
  (`core/method/delegation.md`, `delegation.harness-registration`). It is
  a different mechanism verified to work, which is exactly what "observed"
  is for.

### Delegation mechanism

- Claude Code: the native `Task` tool, granted only to 6 coordinator agents
  (`tools:` frontmatter). **mechanically enforced**: ADR-0003 `hard` for the
  grant the harness reads from the `tools:` line, and for nothing wider; what
  it leaves open is in the [leaf spawn row of the enforcement table](../DOCUMENTATION.md#enf-leaf-cannot-spawn).
- opencode: has its own subagent-invocation mechanism and reads
  `subagent_depth` from `opencode.json` natively: **mechanically
  enforced** as a mechanism, though which agents may act as coordinators is
  not distinguished by the harness (see "tool allowlists").
- Codex CLI: no working Task-equivalent is wired by this integration (see
  discovery, above): **unsupported**.
- GitHub Copilot: `install_github_copilot()` in `install.sh` states it outright in a comment:
  "`Task` (subagent spawning) has no Copilot equivalent and is not
  projected." VS Code's "agent mode" is a user-driven persona switch, not
  one agent programmatically spawning another: **unsupported**.
- Prime Agent: the native `rlm()` primitive, a real recursive-subagent
  spawn with model selection and message-based handback
  (`integrations/prime-agent/APPEND_SYSTEM.md`): **mechanically
  enforced**.

### Recursion bound

- Claude Code: the harness reads each agent's `tools:` line and withholds
  the spawn tool from a leaf whose line does not list it. ADR-0003 classes
  that `hard` on this host, for the withheld tool and nothing wider; a leaf
  can still start work by other routes, which the
  [leaf spawn row of the enforcement table](../DOCUMENTATION.md#enf-leaf-cannot-spawn)
  records. The *numeric* `max_spawn_depth` on a coordinator is read by
  nothing at runtime; only `agent-lint.py --lint`
  checks it statically (`core/method/delegation.md`,
  `delegation.bounds`). **brief-enforced** for the number that matters.
- opencode: `subagent_depth` in `opencode.json` is "the load-bearing key".
  opencode defaults it to 1 (which "prevents subagents from launching
  subagents"), and the seed ships it set to 3 to reach its deepest chain;
  `tests/seed-lint.py` asserts the two agree
  (`integrations/opencode/README.md`). **mechanically enforced**, and
  numerically real: the one host where the seed's actual delegation depth
  is a harness-checked runtime ceiling rather than a lint-only claim.
- Codex CLI / GitHub Copilot: no delegation mechanism, so no recursion to
  bound: **unsupported**.
- Prime Agent: `RLM_MAX_DEPTH`, default **2**, is a real runtime ceiling,
  but the seed's deepest chain needs 3, and the setting is a
  global/session/env dial, never a committed project file
  (`getRlmMaxDepth()` reads global settings only, per
  `integrations/prime-agent/README.md`). A team must raise it by hand
  (`/rlm-max-depth 3`, a global settings key, or `RLM_MAX_DEPTH=3`) to
  exercise the seed's deepest topology at all. **mechanically enforced**,
  with a caveat no other host has: the shipped default undershoots the
  seed's own requirement.

### Tool allowlists

- Claude Code: the native subagent feature reads the `tools: [...]`
  frontmatter and withholds from a spawned worker each tool its line leaves
  out. ADR-0003 classes that `hard` on this host, for the withheld tool and
  nothing wider: a worker can reach much of what its list leaves out through
  a tool it does hold, such as the shell, as the
  [tool allow-list row of the enforcement table](../DOCUMENTATION.md#enf-tool-allowlist)
  records. **mechanically enforced**.
- opencode: explicitly **degraded**. `integrations/opencode/README.md`'s
  gap table: the seed ships `tools: [Read, Glob, Grep, Bash]` (a list);
  opencode expects `permission: {edit: deny, bash: deny}` (`tools` as a
  list is deprecated). Consequence stated verbatim: "a read-only leaf's
  tool bound is not enforced by the harness." Until `install.sh` emits a
  transformed projection for opencode (as it already does for Copilot),
  this is brief-enforced at best in practice.
- Codex CLI: no evidence of a per-agent tool-restriction surface in this
  integration: **unsupported**.
- GitHub Copilot: **projected**. The transform derives a real VS-Code-native
  `tools:` array per agent from the source allowlist (`install_github_copilot()` in `install.sh`):
  a fixed read-only baseline (`codebase`, `search`, `usages`,
  `findTestFiles`, `runCommands`) plus `editFiles` if the source grants
  `Write`/`Edit`, `runTasks` if it grants `Bash`, `fetch`/`githubRepo` if it
  grants `WebSearch`/`WebFetch`. VS Code does enforce this array. The
  granularity is coarser than the source (e.g. any `Bash` grant becomes the
  same `runTasks`), which is a fidelity loss on top of a real mechanism,
  hence "projected," not "degraded". The enforcement is real, the mapping
  is lossy by design and documented as such.
- Prime Agent: no per-role tool-restriction surface is shipped; a spawned
  `rlm()` child's actual capability set is whatever the discipline in
  `APPEND_SYSTEM.md` asks the parent to respect. **brief-enforced**.

### Model selection

- Claude Code: `model: opus` / `model: sonnet` in frontmatter is read
  natively by the `Task` tool. **mechanically enforced**.
- opencode: explicitly **degraded**. Same gap table: opencode expects
  `provider/model` (e.g. `anthropic/claude-sonnet-4-5`); fed `opus` or
  `sonnet` instead, "the seed's model-class policy is not applied; agents
  run on the session default." The mechanism exists on opencode; the
  seed's unmodified projection just doesn't speak its shape.
- Codex CLI: no per-agent model directive appears anywhere in
  `config.toml.example`, and the README doesn't describe one being
  generated: **unsupported**.
- GitHub Copilot: the transform (`install_github_copilot()` in `install.sh`) emits only
  `description:` and `tools:`; there is no `model:` line in the generated
  frontmatter at all; the field is dropped, not mismapped. **unsupported**.
- Prime Agent: the orchestrator reads the brief's `model:` field itself and
  passes it to `rlm(..., model=...)`, resolving the class via
  `rlm.find_models(...)` (`APPEND_SYSTEM.md`, "Model policy"). Real
  mechanism, but it depends on the calling agent following that
  instruction correctly on every spawn, and nothing forces it.
  **brief-enforced**.

### Session-start hook / Routing hook / Status hook

These three are grouped because their per-host story is identical: a
harness either has an automatic pre-turn or session-start injection point
or it doesn't, and where it exists the seed wires the *same two* payloads
onto it (the route-first pointer with the router's suggestion, and the
status-register summary).

- **Claude Code**: `UserPromptSubmit` → `route-hook.py` (routing hook,
  fail-open `|| true`); `SessionStart` → `status-hook.py` (status hook,
  fail-open); `.claude/settings.json`. Both are real, harness-invoked hook
  points (**mechanically enforced**), fail-open by design (a broken script
  degrades to no injection, never to a blocked prompt; that asymmetry with
  the pre-tool guard is deliberate, see below).
- **opencode**: `install_opencode()` in `install.sh` places no hook
  file of any kind, and no config key exists for one either
  (`integrations/opencode/README.md`: "the config schema rejects unknown
  keys outright"). **unsupported**, all three.
- **Codex CLI**: no hook surface appears in `config.toml.example` or its
  README. **unsupported**, all three. Upstream Codex CLI does document
  `SessionStart`, `UserPromptSubmit` and `PreCompact` hooks, and the seed wires
  none of them, because Codex is a frozen host
  ([ADR-0009](../docs/decisions/adr-0009-host-support-tiers.md)).
- **GitHub Copilot**: VS Code Agent Hooks (Preview) reuses Claude Code's
  own `route-hook.py` / `status-hook.py` scripts under `.github/hooks/`,
  wired via `.github/hooks/route.json` / `status.json`
  (`install_github_copilot()` in `install.sh`), **but only installed
  when `.claude/settings.json` is absent**, since VS Code also reads that
  file, and firing both would double-inject. It is also an explicitly
  Preview VS Code API; `status.json`'s own comment: "If this VS Code build
  does not emit SessionStart, the hook is inert." **projected**: real when
  present, conditional on install order and on a Preview feature being
  available in the editor build.
- **Prime Agent**: `route-extension.ts` subscribes to `before_agent_start`
  for routing; `status-extension.ts` uses the same event plus a
  process-local first-prompt flag to emulate session-start. Both are real,
  natively auto-discovered (`.prime/agent/extensions/`, transpiled at
  runtime, no build step): **mechanically enforced**, and, like Claude
  Code's hooks, explicitly never block: "any error … degrades to the
  pointer line or to silence" (`route-extension.ts` header comment).

### Pre-tool guard

Only Claude Code ships one: `PreToolUse` on `Bash` → `bound-hook.py`
(`.claude/settings.json`). It is the one hook the seed wires without the
`|| true` the other hooks carry, so that its exit 2 can turn away a matched
command that may hang the session. Every failure path inside the script exits 0,
so a fault in it lets the command through. It is a reliability guard, not a
control on what a session may do: it matches command words against a fixed
list, a call made by indirection passes, and it holds only on a host that
fires it. Its classes, `hard` for a matched command on this host and
`not a control` otherwise, are in the
[pre-Bash guard row of the enforcement table](../DOCUMENTATION.md#enf-pre-bash-guard).
**mechanically enforced**, on Claude Code alone.

- opencode: "This harness exposes no pre-tool hook … the bounded-execution
  clauses … are the agent's own discipline rather than an enforced guard"
  (`integrations/opencode/README.md`, "Bounded execution has no hook
  here"). **unsupported**.
- Codex CLI, GitHub Copilot, Prime Agent: no equivalent shipped for any of
  the three. Copilot's hook set stops at route/status, Codex has no hook
  surface at all, and Prime Agent's two extensions cover only routing and
  status, never a tool-call gate. **unsupported** on all three.

### Slash commands

- Claude Code, opencode, Prime Agent: `generate_slash_commands()` in
  `install.sh`, called from `install_claude_code()`, `install_opencode()` and
  `install_prime_agent()`,
  produces one command file per protocol node declaring `command: true`,
  into `.claude/commands/`, `.opencode/commands/`, and
  `.prime/agent/prompts/` respectively, the identical roster on all
  three. **mechanically enforced**.
- GitHub Copilot: a separate but equivalent generator produces
  `.github/prompts/<name>.prompt.md` from the same `command: true` roster
  (`install_github_copilot()` in `install.sh`), discovered natively by
  VS Code Copilot Chat's `/` menu. **mechanically enforced**.
- Codex CLI: `install_codex` never calls `generate_slash_commands` and
  produces no prompt/command directory at all, the only adapter with zero
  command surface. **unsupported**.

### Per-session injection dedup

Whether a later prompt in the same session is spared text an earlier prompt
already injected (SPEC-0003).

- **Claude Code**: `route-hook.py` keeps a session ledger under
  `.cypress/session/`, keyed on the `session_id` the host sends, and
  `status-hook.py` resets it on every `SessionStart`. A node already
  suggested this session is named by id, not repeated in full, with a full
  injection after each reset, every `REFRESH_EVERY` routed prompts, and on
  any doubt about the record. Class: **mechanically enforced**.
- **opencode**: no per-prompt injection ships, so there is nothing to dedup.
  Class: **unsupported**.
- **Codex CLI**: frozen under ADR-0009, and nothing ships. Class:
  **unsupported**.
- **GitHub Copilot**: it runs the same `route-hook.py`, but its envelope
  carries no `session_id`, so every prompt takes the full injection and no
  dedup is delivered. Class: **degraded**, and only where the hook is
  installed at all: the Routing hook row's **projected**³ condition applies.
- **Prime Agent**: `before_agent_start` carries no session id, and
  `route-extension.ts` keeps no state, so every routed prompt is injected in
  full and no saving in injected bytes is claimed. Class: **unsupported**,
  for the injection itself. The overlay's `## Surfaced nodes` section asks the model
  to keep `_cypress_surfaced`, a Python set in its IPython kernel, and not to
  re-open a node whose content is still in view. That set is model-kept and
  unenforced: `soft` under ADR-0003, model-cooperative, with nothing observing
  whether the model complies. Any saving is in node bodies not re-read, and it
  is not measured. What every Prime Agent session pays for the instruction is
  the section itself, at most `OVERLAY_SECTION_MAX_BYTES` (512 B) on the
  eager surface (the always-applied figure below includes it).

### Always-applied instructions

What loads into every session or every skill invocation regardless of
routing: the eager surface that `check_eager_surface()` in
`tests/seed-lint.py` bounds. Re-measured for this pass by running that
function's own computation against current sources:

| Harness | Formula | Measured |
|---|---|---|
| Claude Code | kernel + agent descriptions + skill descriptions | 26 261 B |
| opencode | kernel + agent descriptions + skill descriptions | 26 261 B |
| Codex CLI | kernel + agent descriptions + skill descriptions⁴ | ≤ 26 261 B |
| Prime Agent | kernel + skill descriptions + `APPEND_SYSTEM.md` overlay | 24 444 B |
| GitHub Copilot | kernel + agent descriptions + skill descriptions + pointer boilerplate | 31 905 B |

(Component figures are not restated here. These moved four times in one release
and were wrong three of those times, including once while the correction to the
previous error was being written down, because a ten-byte kernel edit landed in
between. `check_eager_surface()` in `tests/seed-lint.py` is their one home, and
`check_published_eager_figures()` beside it now holds this table against that
computation: a cell that drifts from what the function computes fails the gate
and names both numbers. Chasing them by hand was the wrong repair, and this
paragraph used to claim the gate already did this while it did not.)

Four harnesses enumerate only `name` + `description` for each of the 15
skills at session start and load a skill's full body only when the model
invokes it: genuine progressive disclosure. Copilot's projections (written by
`install_github_copilot()`, not by `generate_slash_commands()`) are pointers of
the same shape since 7.16.0.

GitHub Copilot **was** the outlier. Its skill projections carried
`applyTo: '**'`, so every skill body was always-applied context there:
138 535 bytes against 26 261 everywhere else. 7.16.0 narrowed them to
pointers, `EAGER_EXEMPTIONS` is consequently empty, and the harness is
modelled like every other one at 31 905 B. The residue is the pointer
boilerplate each file carries, not the discipline behind it.

## Measurements

Re-run to reproduce, from the seed root:

```sh
# eager-surface bytes per harness. seed-lint prints a figure only when it
# fails, so force every harness over the line in a throwaway copy and read
# the five numbers out of the failures:
cp -a . /tmp/eager && cd /tmp/eager \
  && sed -i 's/^EAGER_BUDGET = .*/EAGER_BUDGET = 1000/' tests/seed-lint.py \
  && python3 tests/seed-lint.py | grep 'eager surface'
python3 tests/seed-lint.py   # in the seed itself: fails loudly if any harness
                             # exceeds its budget/exemption, silent otherwise

# Codex's skills.config coverage vs. the 15 shipped skills
grep -c 'path = ' integrations/codex/config.toml.example
ls skills/ | wc -l

# no [agents] section ships in the Codex config example
grep -n '\[agents\]' integrations/codex/config.toml.example   # (no output)

# no per-plant install path exists for library-corpus
grep -n 'library.corpus' install.sh   # (no output — legal-corpus is the only corpus install.sh places)
```

A gap surfaced while building this matrix and was closed in 7.16.0:
`integrations/codex/config.toml.example` registered 13 of the seed's 15
skills while `integrations/codex/README.md` claimed the bundled example
"shows the full set — one `[[skills.config]]` entry per skill the seed
ships." It now registers all 15, so the README's claim is true.
