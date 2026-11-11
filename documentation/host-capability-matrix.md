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
  agent or person decides and no tool can), extended here across all five
  hosts.

Every cell below is one of exactly six classes, with one deliberate
exception: the Effort override row uses `not recorded` where whether the host
reads the field at all has never been confirmed either way (footnote 6). The
six classes are not a second vocabulary: they are ADR-0003's labels split by
*why* a host lands where it does, because one "supported / not supported"
column would blur a missing feature, a lossy transform, and a field the
harness never reads. The right-hand column says which ADR-0003 label each
class is.

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
`judgment` controls (the deliver-time attribution assertion, the gate tables in `graft`,
`grow` and `harvest`) are host-independent, and each is classed in its own
node.

Source for every `install_*` function: `install.sh`. Source for every hook
wiring: each adapter's `integrations/<name>/settings.json` (or `.ts`
extension, or `.toml` example) and its `README.md`. Version measured:
manifest.json's current version at the time of this pass (see the
Measurements section). An opencode cell rises only on an observation made on a
running OpenCode 2 release by the live procedure
(`docs/skills/opencode-live-verification.md`), and its evidence line names
that release; documentation and fixture runs hold or lower a cell. The cells
below were last observed on OpenCode 2.2.6
(`integrations/opencode/verified-version`).

## Support tiers (ADR-0009)

A tier is a maintenance commitment, set by
[ADR-0009](../docs/decisions/adr-0009-host-support-tiers.md) and, for opencode,
by [ADR-0033](../docs/decisions/adr-0033-opencode-first-class-on-opencode-2.md). It says what the
seed owes each host on the next change; the matrix below says what each harness
holds today, so the two do not replace each other. The assignment's one home is the three tier arrays in
`install.sh`, and `tests/seed-lint.py` (`check_host_tiers`) holds this table to
them. `install.sh all` installs the first-class and supported hosts; a frozen
host installs only when it is named, as in `install.sh all codex`, and prints a
`DEPRECATED` notice.

| Tier | Hosts | What the seed commits to |
|---|---|---|
| `first-class` | `claude-code`, `opencode`, `prime-agent` | Feature parity is the target. A feature that ships on one is owed to the others, or its absence is recorded as a defect to close. opencode means OpenCode 2 only. |
| `supported` | none | The tier stays defined; no host sits in it. |
| `frozen` | `codex`, `github-copilot` | Still installable by name, with a `DEPRECATED` notice. No new features; the existing tests run as regression. |

A feature that ships on one first-class host is owed to opencode: through the
host's own mechanism where OpenCode 2 holds it, through a thin envelope over
the shared hook core where only its plugin API does, and otherwise recorded here
as a defect to close. A harvest generalises a feature for the first-class
hosts and targets no frozen host.

## The matrix

| Capability | Claude Code | opencode | Codex CLI | GitHub Copilot | Prime Agent |
|---|---|---|---|---|---|
| Root kernel loading | mechanically enforced | mechanically enforced | mechanically enforced | mechanically enforced | mechanically enforced |
| Specialist discovery/registration | mechanically enforced | projected | unsupported | projected | observed |
| Delegation mechanism | mechanically enforced | mechanically enforced | unsupported | unsupported | mechanically enforced |
| Recursion bound | brief-enforced¹ | mechanically enforced | unsupported | unsupported | mechanically enforced² |
| Tool allowlists | mechanically enforced | projected | unsupported | projected | brief-enforced |
| Model selection | mechanically enforced | mechanically enforced⁷ | unsupported | unsupported | brief-enforced |
| Effort override (agent-frontmatter `effort:` key) | mechanically enforced | not recorded⁶ | not recorded⁶ | not recorded⁶ | brief-enforced⁶ |
| Session-start hook | mechanically enforced | observed | unsupported | projected³ | mechanically enforced |
| Routing hook | mechanically enforced | mechanically enforced | unsupported | projected³ | mechanically enforced |
| Status hook | mechanically enforced | mechanically enforced | unsupported | projected³ | mechanically enforced |
| Per-session injection dedup | mechanically enforced | unsupported⁸ | unsupported | degraded³ | mechanically enforced⁵ |
| Pre-tool guard | mechanically enforced | mechanically enforced | unsupported | unsupported | unsupported |
| Slash commands | mechanically enforced | mechanically enforced | unsupported | mechanically enforced | mechanically enforced |
| Always-applied instructions | mechanically enforced (67 065 B, recorded exemption) | mechanically enforced (67 065 B, recorded exemption) | mechanically enforced (≤ 24 125 B)⁴ | mechanically enforced (29 769 B) | mechanically enforced (18 388 B) |

¹ The leaf/coordinator split (who holds the spawn tool at all: `Agent` on Claude Code, `Task` accepted) is read by the
harness from each agent's `tools:` line, and ADR-0003 classes that read
`hard` for what the harness reads and nothing wider. What the split leaves
open is recorded in the [leaf spawn row of the enforcement table](../DOCUMENTATION.md#enf-leaf-cannot-spawn).
The *numeric* `max_spawn_depth`
ceiling is not read by the harness at all; only `agent-lint.py --lint`
checks it statically. The host's own nesting limit on subagents spawning
subagents is a separate, harness-held ceiling that the seed does not set
([`delegation.bounds`](../core/method/delegation-bounds.md#delegation-is-bounded)). The cell reflects the
numeric ceiling, since that is what "recursion bound" asks for a coordinator
that does hold the spawn tool.

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

⁵ Through the shared hook core: `route-extension.ts` runs the same
`route-hook.py` Claude Code runs, from `.prime/agent/hooks/`, and passes the
session id the host's session manager gives. When the host gives no id, the
core injects in full on every prompt (see "Per-session injection dedup"
below).

⁶ Whether Codex CLI or GitHub Copilot read an `effort`
key from agent frontmatter at all is not established
(`docs/specs/SPEC-0005-cycle-economy.md` §6, "Effort";
`core/method/delegation-model-classes.md`, `delegation.effort`). On opencode
the installer places no `effort` key; the effort travels as the model map
cell's `#<variant>`, which OpenCode 2.2.6 registers, and whether the provider
applies it is not verified live. "not
recorded" is not one of the six classes above: it names an open question, not
a confirmed capability gap, so no cell here reads "unsupported" on the
strength of a guess. Prime Agent takes the effort per spawn as
`rlm.spawn(..., thinking=<effort>)`, and its overlay tells the parent to pass
the brief's effort there (`integrations/prime-agent/APPEND_SYSTEM.md`), so that
cell is brief-enforced. Whether Claude Code itself offers a per-spawn override on
top of the frontmatter key is likewise not recorded
(`integrations/claude-code/README.md`, "Effort").

⁷ Once the plant's model map row is filled. An unfilled row projects no
`model:` line, and the agent runs on its caller's model.

⁸ The plugin passes the session id to the same `route-hook.py`, and fixtures
hold the ledger, but no live run has yet sent a second prompt in one host
process. A cell rises only on a live observation (ADR-0033), so the class
stays **unsupported**. The owner closed the item on 2026-11-10 and chose not to
run the live check (check 7 of the live procedure); a later release may run it
(see "Per-session injection dedup" below).

## Per-capability evidence

### Root kernel loading

Every adapter auto-loads its kernel file by the host's own convention, no
config key required:

- Claude Code: `CLAUDE.md` at the project root (`install_claude_code`,
  `place_kernel()` in `install.sh`).
- opencode: `AGENTS.md` (`integrations/opencode/README.md`, "What the host
  reads"), as OpenCode 2 documents it; the seed relies on no `CLAUDE.md`
  fallback, and none is verified live. In a compose-kernel plant the seed kernel sits in `CLAUDE.md` only, so
  an opencode session there does not see it (a
  [defect](#defects-to-close)).
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
  native Claude Code convention; the harness registers it and spawns by
  name via `Agent` (`Task` accepted). When a file written mid-session is
  picked up is in
  [`delegation.harness-registration`](../core/method/delegation-bounds.md#a-specialist-is-spawnable-only-once-the-host-registered-it).
- **opencode: projected.** `render_opencode_agents()` in `install.sh`
  transforms every `docs/graph/agents/*.md` into
  `.opencode/agents/<callable name>.md` carrying only OpenCode 2's own fields
  (`description`, `mode`, `model`, `permissions`) and the composed charter
  body (`integrations/opencode/README.md`, "The native agent file"). The
  transform drops `effort`, `can_delegate`, `routing_triggers` and the graph
  fields, which the host does not read; it turns `tools:` and `delegates_to:`
  into host rules (see "Tool allowlists"). Observed on OpenCode 2.2.6:
  `opencode2 debug agents` lists all 20 seed agents under their callable names
  with the mode, the model and variant, and the rules as rendered, and prints
  no configuration warning. The earlier, verbatim projection registered
  nothing on that release, because a frontmatter `tools:` list voids the whole
  agent file there. The orchestrator is the default agent, so a new session
  starts in it (a session started in `orchestrator` on 2.2.6, with no
  configuration warning).
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
  sources**; the orchestrator composes a brief from one with
  `docs/graph/brief.py --charter` and spawns a child with
  `rlm.spawn(brief, name=...)` at the moment it is needed
  (`integrations/prime-agent/APPEND_SYSTEM.md`, "Delegation — recursive
  subagents, not a Task tool"). This is not a weaker version of
  registration: there is no "installed but not yet spawnable" lag the way
  there can be on Claude Code after a first install (opencode: not recorded)
  (`core/method/delegation-bounds.md`, `delegation.harness-registration`). It is
  a different mechanism verified to work, which is exactly what "observed"
  is for.

### Delegation mechanism

- Claude Code: the native spawn tool, `Agent` (`Task` accepted), granted only to 6 coordinator agents
  (`tools:` frontmatter). **mechanically enforced**: ADR-0003 `hard` for the
  grant the harness reads from the `tools:` line, and for nothing wider; what
  it leaves open is in the [leaf spawn row of the enforcement table](../DOCUMENTATION.md#enf-leaf-cannot-spawn).
- opencode: the host's own subagent tool. Which agents an agent may launch
  is its own rules: a charter with `Task` gets a rule denying every
  `subagent` launch and one allow per agent in its `delegates_to:`, and a
  charter without `Task` launches nothing. The lead's list also allows each
  agent the plant authored that passes the agent lint, generated from the
  roster at install (the owner's decision of 2026-11-11), and
  `install.sh opencode --check` reports a list that no longer matches. Observed on OpenCode 2.2.6: a
  coordinator whose rules allow only one agent was refused another by the host
  ("Permission denied: subagent"), and the allowed one ran. **mechanically
  enforced**, and the allowlist is held by the agent's own host rules rather
  than by a brief; Claude Code gets its bound through the agent type.
- Codex CLI: no working spawn-tool equivalent is wired by this integration (see
  discovery, above): **unsupported**.
- GitHub Copilot: `install_github_copilot()` in `install.sh` states it outright in a comment:
  "`Task` (subagent spawning) has no Copilot equivalent and is not
  projected." VS Code's "agent mode" is a user-driven persona switch, not
  one agent programmatically spawning another: **unsupported**.
- Prime Agent: the native `rlm.spawn()` primitive, a real recursive-subagent
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
  checks it statically (`core/method/delegation-bounds.md`,
  `delegation.bounds`). **brief-enforced** for the number that matters.
  The host's own nesting limit on subagents spawning subagents is a
  separate, harness-held ceiling the seed does not set
  ([`delegation.bounds`](../core/method/delegation-bounds.md#delegation-is-bounded)).
- opencode: `experimental.subagent_depth` in `opencode.json` is the
  load-bearing key. The host defaults the depth to 1, at which a subagent
  launches none of its own, and the seed ships 3, the deepest chain;
  `tests/seed-lint.py` asserts the two agree (`integrations/opencode/README.md`,
  "opencode.json"). Observed on OpenCode 2.2.6: the key is accepted with no
  warning, three nested launches ran and a fourth was refused ("Subagent depth
  limit reached (3)"); the top-level
  `subagent_depth` an earlier seed shipped is omitted as an unsupported legacy
  setting. A leaf launches nothing, because its rules deny `subagent`.
  **mechanically enforced**: the host holds one depth for the whole session,
  the seed's deepest, and a coordinator whose own `max_spawn_depth` is lower is
  held to that number by `agent-lint.py --lint` only.
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
- opencode: **projected**. The transform renders each charter's `tools:`
  as the agent's `permissions:`: a rule denying every action, then one allow
  per host action the tools map to in
  `integrations/opencode/tool-permissions.json`, with the host's `.env` guard
  restored after `read`; the host applies the last matching rule. A tool name
  the table lacks stops the install when a seed charter names it, and
  `tests/seed-lint.py` holds the seed's charters to the table. In a plant's own
  agent the tool is denied, a warning names the file and the tool, the rest
  installs, and `install.sh opencode --check` fails until it is fixed (the
  owner's decision of 2026-11-11). Observed on OpenCode 2.2.6: an agent with
  neither edit nor shell had its write tool removed by the host, and no file
  was created; all 20 agents' effective rules, read from the host's own
  listing, equal their charters' tools and `delegates_to:`. As on Claude Code,
  a worker granted the shell can reach through it much of what its list leaves
  out ([tool allow-list row](../DOCUMENTATION.md#enf-tool-allowlist)).
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
  `rlm.spawn()` child's actual capability set is whatever the discipline in
  `APPEND_SYSTEM.md` asks the parent to respect. **brief-enforced**.

### Model selection

- Claude Code: `model: opus` / `model: sonnet` in frontmatter is read
  natively by the spawn tool (`Agent`, `Task` accepted). **mechanically enforced**.
- opencode: opencode expects a `provider/model` selector, so the installer
  writes each projected agent's `model:` line from the plant's model map,
  `docs/graph/models.md`, at the agent's class and effort
  (`render_opencode_agents()` in `install.sh`; `integrations/opencode/README.md`,
  "The native agent file"). Observed on OpenCode 2.2.6: the host lists each
  agent's model, with the variant a `#<variant>` cell names. **mechanically enforced**
  once the map row is filled. An unfilled row projects no `model:` line, and the
  agent runs on its caller's model. `install.sh opencode --check` compares the
  placed projections with a fresh rendering, the `model:` line included.
- Codex CLI: no per-agent model directive appears anywhere in
  `config.toml.example`, and the README doesn't describe one being
  generated: **unsupported**.
- GitHub Copilot: the transform (`install_github_copilot()` in `install.sh`) emits only
  `description:` and `tools:`; there is no `model:` line in the generated
  frontmatter at all; the field is dropped, not mismapped. **unsupported**.
- Prime Agent: the parent reads the class from the brief and the model from
  the plant's model map, `docs/graph/models.md`, resolves it with
  `rlm.find_models(...)` and spawns with `rlm.spawn(..., model=...)`
  (`APPEND_SYSTEM.md`, "Delegation"). A selector that does not resolve stops
  the spawn; an unfilled row inherits the parent's model and is recorded. Real
  mechanism, but it depends on the calling agent following that instruction on
  every spawn. **brief-enforced**.

### Effort override

- Claude Code: reads an `effort` key from subagent frontmatter (`low`,
  `medium`, `high`, `xhigh` and `max`; the level it accepts depends on the
  model), overriding the session's effort level for every spawn of that
  definition; a subagent
  with no `effort` key inherits the session's level. The seed ships only the
  three lower values in `agents/*.md`
  (`integrations/claude-code/README.md`, "Effort";
  `core/method/delegation-model-classes.md`, `delegation.effort`).
  **mechanically enforced**. This cell rests on the vendor page that
  `integrations/claude-code/README.md` cites until the fresh-install gate
  observes it. Whether Claude Code additionally offers a
  per-spawn override on top of the frontmatter key: not recorded.
- Every host: the per-spawn derived effort (`delegation.effort`) is
  **brief-enforced**. The brief records it; no host applies it.
- Prime Agent: the parent passes the brief's effort as
  `rlm.spawn(..., thinking=<effort>)` on each spawn (`APPEND_SYSTEM.md`).
  **brief-enforced**.
- opencode: the installer places no `effort` key. The plant's map carries
  the effort as a cell's `#<variant>`, which OpenCode 2.2.6 registers; whether
  the provider applies it, and any per-launch effort, are **not recorded**
  (the subagent tool's observed input is the agent, a description and the
  prompt; a `model` field is documented and not run).
- Codex CLI, GitHub Copilot: whether the host reads an
  `effort` key from agent frontmatter at all is **not recorded**
  (`docs/specs/SPEC-0005-cycle-economy.md` §6, "Effort"). This sits outside
  the six classes above by design (see footnote 6): an unconfirmed read is
  not the same claim as a confirmed absence, and the matrix does not guess.

### Prompt-cache lifetime

- Claude Code: the lead and worker lifetimes are host settings
  (`promptCacheTtl`, `subagentPromptCacheTtl`, v2.1.242 or later) and a
  subagent frontmatter key (`experimental: cacheTtl`, v2.1.248 or later);
  `FORCE_PROMPT_CACHING_5M=1` and `ENABLE_PROMPT_CACHING_1H=1` override or
  request; the lead defaults to one hour on a subscription within included
  usage, five minutes otherwise; workers default to five minutes. Defaults, precedence and when to change
  them: `integrations/claude-code/README.md`, "Prompt cache lifetime". The
  installer places the lead setting only on `--prompt-cache-ttl 1h`, and
  `resume-hook.py` reads the worker lifetime, counting an hour only when the
  worker's transcript shows a one-hour cache write. **documented**, not observed.
- opencode, Codex CLI, GitHub Copilot, Prime Agent: **not recorded**. On
  opencode the host can continue a finished child (the subagent tool with a
  `sessionID`, documented and not run), so the hazard `resume-hook.py` guards
  exists wherever the provider's cache has a lifetime (a
  [defect](#defects-to-close)).

### Session-start hook / Routing hook / Status hook

These three are grouped because their per-host story is identical: a
harness either has an automatic pre-turn or session-start injection point
or it doesn't, and where it exists the seed wires the *same two* payloads
onto it (the route-first pointer with the router's suggestion, each node
beside its file, and, once per session, the status-register summary followed
by the code-anchor line). The anchor line is what `docs/graph/code-anchor.py
--compare` prints: whether the code moved since canonize recorded the anchor,
and which paths. It fails toward checking: a comparison that does not finish
within 5 s, or does not run, gives a line saying code facts are unverified.
Only the session-start hook runs it, never the per-prompt one.

- **Claude Code**: `UserPromptSubmit` → `route-hook.py` (routing hook,
  fail-open `|| true`); `SessionStart` → `status-hook.py` (status hook,
  fail-open); `.claude/settings.json`. Both are real, harness-invoked hook
  points (**mechanically enforced**), fail-open by design (a broken script
  degrades to no injection, never to a blocked prompt; that asymmetry with
  the pre-tool guard is deliberate, see below). Both are prompt- or
  session-scoped; whether either fires for a subagent's turn is in the
  [delegation node](../core/method/delegation-briefs.md#every-brief-carries-the-graph-discipline).
- **opencode**: `install_opencode()` in `install.sh` places the three cores
  in `.opencode/hooks/` and the plugin `.opencode/plugins/cypress.ts`, which
  the host loads by convention (`integrations/opencode/README.md`, "The plugin
  and the hook core"). On the host's prompt hook the plugin runs
  `route-hook.py` and adds its text as a synthetic message with
  `resume: false`, ahead of the prompt, which it leaves unedited. On the first
  prompt this host process sees for a session it first runs `status-hook.py`
  the same way. The plugin composes no text; a child session (one with a
  `parentID`) gets nothing. Observed on OpenCode 2.2.6: the plugin loads with
  no install step and no network, and both texts arrive byte-identical to the
  cores' text. Routing and Status hook: **mechanically enforced**, and, like
  Claude Code's hooks, they never block. Session-start hook: **observed**,
  because no session-start event runs the status core: the first prompt of a
  session in a host process does, so a new host process runs it again on a
  session it has not seen. OpenCode 2 offers the plugin no compaction event it
  uses, so the reset Prime Agent performs after a compaction does not happen
  here (a [defect](#defects-to-close)).
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
  and runs `route-hook.py`, the core Claude Code runs, from
  `.prime/agent/hooks/`. `status-extension.ts` runs `status-hook.py` on the
  session events that can leave the model without context it was shown
  (`session_start`, `session_compact`, `session_tree`, `refine_complete`)
  and injects the result on the next prompt of that session, once. Neither
  extension composes text. A child session (`rlmDepth` above 0) gets
  nothing, and the route core skips a turn a person did not type. Both are real, natively
  auto-discovered (`.prime/agent/extensions/`, transpiled at runtime, no
  build step): **mechanically enforced**, and, like Claude Code's hooks,
  they never block: "a missing core, a timeout or any error injects
  nothing" (`route-extension.ts` header comment).

### Pre-tool guard

Only Claude Code ships them: `PreToolUse` on `Bash` → `bound-hook.py` and
`PreToolUse` on `SendMessage` → `resume-hook.py` (`.claude/settings.json`,
the cold-resume guard: [row](../DOCUMENTATION.md#enf-cold-resume-guard)).
`bound-hook.py` is wired, like `resume-hook.py`, without the
`|| true` the context hooks carry, so that its exit 2 can turn away a matched
command that may hang the session. Every failure path inside the script exits 0,
so a fault in it lets the command through. It is a reliability guard, not a
control on what a session may do: it matches command words against a fixed
list, a call made by indirection passes, and it holds only on a host that
fires it. Its classes, `hard` for a matched command on this host and
`not a control` otherwise, are in the
[pre-Bash guard row of the enforcement table](../DOCUMENTATION.md#enf-pre-bash-guard).
**mechanically enforced** on Claude Code. Whether it fires on a
subagent's Bash calls is recorded in the
[delegation node](../core/method/delegation-briefs.md#every-brief-carries-the-graph-discipline).

- opencode: the plugin's permission hook runs the same `bound-hook.py` for a
  shell command, and a command the core refuses is denied through the host
  with the core's reason as the message, byte for byte; other actions keep the
  effect the host decided. A missing or slow core lets the command through,
  and `install.sh opencode --check` names it. Observed on OpenCode 2.2.6: a
  refused command was denied and the model reported the core's reason.
  **mechanically enforced** for the bound guard. No continuation guard ships
  (a [defect](#defects-to-close)).
- Codex CLI, GitHub Copilot, Prime Agent: no equivalent shipped for any of
  the three. Copilot's hook set stops at route/status, the seed wires no
  Codex hook at all (see the session-start hook section above), and Prime
  Agent's two extensions cover only routing and status, never a tool-call
  gate. **unsupported** on all three; on Prime Agent, a first-class host, that
  is a [defect](#defects-to-close).

### Slash commands

- Claude Code, opencode, Prime Agent: `generate_slash_commands()` in
  `install.sh`, called from `install_claude_code()`, `install_opencode()` and
  `install_prime_agent()`,
  produces one command file per protocol node declaring `command: true`,
  into `.claude/commands/`, `.opencode/commands/`, and
  `.prime/agent/prompts/` respectively, the identical roster on all
  three. **mechanically enforced**. On opencode the class predates OpenCode 2,
  and that the host lists the generated commands is not yet verified live.
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
- **opencode**: the plugin passes the session id the host gives to the same
  `route-hook.py`, so the session would keep one ledger under
  `.cypress/session/` with Claude Code's rules. The plugin's fixture test and
  the core's ledger tests hold that; no live run has sent a second prompt in
  one host process. Each new host process runs the status core again on a
  session it has not seen, which resets that session's ledger, as a Claude
  Code resume does. Class: **unsupported**⁸, held until a live observation.
- **Codex CLI**: frozen under ADR-0009, and nothing ships. Class:
  **unsupported**.
- **GitHub Copilot**: it runs the same `route-hook.py`, but its envelope
  carries no `session_id`, so every prompt takes the full injection and no
  dedup is delivered. Class: **degraded**, and only where the hook is
  installed at all: the Routing hook row's **projected**³ condition applies.
- **Prime Agent**: `route-extension.ts` passes the session id from the
  host's session manager to the same `route-hook.py`, so the session keeps
  one ledger under `.cypress/session/`, and `status-hook.py` resets it after
  each session start, compaction, tree switch or refine. The rules are
  Claude Code's: a node already suggested is named by id on one `seen:`
  line, with a full injection after each reset, every `REFRESH_EVERY`
  routed prompts, and on any doubt about the record. Without a session id
  the core injects in full. Class: **mechanically enforced**. Over 47
  follow-up prompts in 22 real sessions, the text injected after the first
  prompt fell by 69% (cl100k). The model-kept `_cypress_surfaced` set and the
  overlay section that asked for it are retired.

### Always-applied instructions

What loads into every session or every skill invocation regardless of
routing: the eager surface that `check_eager_surface()` in
`tests/seed-lint.py` bounds. Re-measured for this pass by running that
function's own computation against current sources:

| Harness | Formula | Measured |
|---|---|---|
| Claude Code | kernel + agent descriptions + skill descriptions + orchestrator output style | 67 065 B (recorded exemption) |
| opencode | kernel + agent descriptions + skill descriptions + orchestrator charter (the default agent) | 67 065 B (recorded exemption) |
| Codex CLI | kernel + agent descriptions + skill descriptions⁴ | ≤ 24 125 B |
| Prime Agent | kernel + skill descriptions + `APPEND_SYSTEM.md` overlay | 18 388 B |
| GitHub Copilot | kernel + agent descriptions + skill descriptions + pointer boilerplate | 29 769 B |

The component figures live in `check_eager_surface()` in `tests/seed-lint.py`,
their one home, and `check_published_figures()` beside it holds this table to
that computation: a cell that drifts from what the function computes fails the
gate and names both numbers.

Four harnesses enumerate only `name` + `description` for each of the 15
skills at session start and load a skill's full body only when the model
invokes it: genuine progressive disclosure. Copilot's projections (written by
`install_github_copilot()`, not by `generate_slash_commands()`) are pointers of
the same shape, so GitHub Copilot is modelled like every other harness. `EAGER_EXEMPTIONS`
holds one recorded debt: on Claude Code the main session plays the
orchestrator, so its charter and always-loaded nodes ride in the
`orchestrator` output style on every session. Its extra bytes
are the pointer boilerplate each projected file carries. On opencode
the orchestrator is the default agent, so its charter and always-loaded nodes
are the main session's system prompt on every session, a second recorded debt
(owner decision, 2026-11-10); the host's own coding prompt does not apply to
that agent, and a user can switch to the host's `build` agent.

## Defects to close

Each first-class host is owed what another holds
([ADR-0033](../docs/decisions/adr-0033-opencode-first-class-on-opencode-2.md)),
so each remaining difference is recorded here, its one home, with what would
close it. The adapter README lists them by name.

| Host | Difference | Where it shows | What would close it |
|---|---|---|---|
| opencode | No worker-continuation guard. The host can continue a finished child (the subagent tool with a `sessionID`, documented and not run), so the prompt-cache hazard exists wherever the provider's cache has a lifetime. `resume-hook.py` reads Claude Code's transcript layout and cache settings, so the shared core cannot decide on opencode's input as it stands. | Pre-tool guard; Prompt-cache lifetime | A core input contract carrying the child's last-activity time and the provider's cache lifetime, then a third branch in the plugin |
| opencode | The seed kernel is absent in a compose-kernel plant: the kernel sits in `CLAUDE.md` only, and the host reads `AGENTS.md` (documented, not verified live). | Root kernel loading | The plugin delivers the kernel once per session through its synthetic-message surface without loading it twice, which adds a kernel-delivery duty to the envelope |
| opencode | No compaction reset: OpenCode 2 offers the plugin no compaction event it uses, so the status and ledger reset Prime Agent performs after a compaction does not happen. | Session-start hook | A host compaction event the plugin subscribes to, running `status-hook.py` as Prime Agent's `session_compact` does |
| Prime Agent | No pre-tool guard: Claude Code and opencode refuse a matched shell command through `bound-hook.py`; Prime Agent's extensions cover routing and status only. | Pre-tool guard | Owner decision D4 in [`docs/plans/owner-decisions-8.4.0-opencode-2.md`](../docs/plans/owner-decisions-8.4.0-opencode-2.md): a tool-call hook in Prime Agent's extension API that can refuse, and a third envelope over `bound-hook.py` |

The owner accepted these differences on 2026-11-10 and asked for none of them
to be built now: the worker-continuation guard, the kernel in a compose-kernel
plant, and the compaction reset stay recorded here, and Prime Agent's missing
guard was set aside for this round. Two items are not defects. The per-session
dedup check is closed without a live run. Effort stays the user's choice: the
installer writes a model-map cell's `#<variant>` into the agent, as it writes
Prime Agent's map cell for `thinking`, and neither the seed nor the matrix claims
the provider applies it.

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

# selective placement of library, tool and stack-keyed skill pages
grep -n 'place_expertise' install.sh   # (SPEC-0001 §6)
```

`integrations/codex/config.toml.example` registers all 15 skills, one
`[[skills.config]]` entry per skill the seed ships, as
`integrations/codex/README.md` says.
