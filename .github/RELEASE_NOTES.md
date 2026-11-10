## 8.4.0 — opencode is a first-class host, on OpenCode 2 (2026-11-10)

The owner decided on 2026-11-10 that opencode becomes a first-class host at
parity with Claude Code, and that the seed supports OpenCode 2 only
([ADR-0033](docs/decisions/adr-0033-opencode-first-class-on-opencode-2.md)). The
adapter keeps its name; the documents say which generation it means. Measured on
OpenCode 2.2.6 before any change, the 8.3.2 projection registered none of the
seed's specialists: a `tools:` list in an agent file makes the host drop the
file without a diagnostic, and every seed agent has one. This round makes the
adapter work there, in the host's own format, and records what is still
different from Claude Code. The kernel is 7049 bytes. By the owner's decision
of 2026-11-10 (below) opencode's always-loaded surface is now 67131 bytes,
recorded as a second `EAGER_EXEMPTIONS` entry; it was 24207. The budget itself
did not move.

### The round in brief

- **opencode is first-class.** The tier arrays, the lint, the host matrix and
  every document that states the tiers agree. `install.sh all` installs the
  same hosts in the same order. The `supported` tier stays defined and empty.
- **Specialists register in the host's native form.** Each agent is rendered
  as `.opencode/agents/<callable name>.md` with `description`, `mode`, `model`
  from the plant's model map and `permissions`; the seed's own frontmatter does
  not reach the host. The tool bound is deny-all followed by an allow per tool,
  from one table (`integrations/opencode/tool-permissions.json`) that stops the
  render on a tool name it does not know. `delegates_to` becomes the host's
  `subagent` rules. A map cell may end in `#<variant>`, which is how a plant
  expresses an effort on a model that has one. The composed agents carry their
  always-loaded nodes through the same function Claude Code's use
  (`tools/agent_compose.py`).
- **The config is OpenCode 2's.** `experimental.subagent_depth: 3` replaces the
  top-level key, which the host reports as an unsupported legacy setting and
  omits. The installer prints one line saying it targets OpenCode 2.
- **Route, status and bounded execution reach opencode.** One plugin,
  `.opencode/plugins/cypress.ts`, runs the same three Python cores Claude Code
  runs, placed under `.opencode/hooks/`. The route and status text arrive as
  synthetic messages ahead of the prompt, byte-identical to the cores' text; a
  child session gets none; a shell command the bound core refuses is denied with
  the core's reason. The plugin composes no text, writes no file and fails open.
  It loads with no install step and no network.
- **`--check` and `--recompose-agents` cover opencode.** `--check` names a
  drifted agent or skill, an `opencode.json` still in the earlier shape, a
  missing plugin and a missing core, each with a remedy and a non-zero exit.
  `--recompose-agents` takes `opencode` and rewrites only projections.
- **The lead plays the orchestrator.** The owner decided on 2026-11-10 that
  the orchestrator is opencode's default agent and that its surface is exempt
  from the budget. `opencode.json` sets `default_agent` to `orchestrator`; a
  new session starts in that `primary` agent, whose instructions are the
  charter and its always-loaded nodes. The host's built-in coding prompt does
  not apply to that agent, and the user can switch to `build`. OpenCode 2.2.6
  accepted the key with no warning and a new session started in the
  orchestrator.
- **`brief.py --charter` is refused on an opencode plant**, whose agent type
  carries the charter, as on Claude Code.

### Behaviour change for existing opencode plants

A re-install over a plant installed by an earlier seed succeeds. It moves each
numbered agent file (`02-implementer.md` and the rest) and the old
`opencode.json` to timestamped backups beside them, so a plant's edit is kept,
and writes the OpenCode 2 files. The plant then loads on OpenCode 2 with no
warning and passes `--check`. Nothing is promised for OpenCode 1 afterwards, and
the installer neither detects nor branches on it. Two placed tools change in every plant: `docs/graph/brief.py`
(its behaviour changes only on an opencode plant) and `docs/graph/source_paths.py`
(the source index leaves out the installer's opencode files).

### Verified live, and what is not

Observed on OpenCode 2.2.6: the agents list with their models, variants and
rules; an agent with neither edit nor shell loses its write tool; a launch
outside a coordinator's list is refused by the host and one inside it runs; three
nested launches run and a fourth is refused at the configured depth; the plugin
loads with no install; the route and status text reach the model once, ahead of
the prompt; a child gets nothing; a refused command's reason reaches the model.
Not verified live: the second-prompt reminder in one host process (held by fixtures; the owner closed it without a live check on 2026-11-10), slash commands, and whether the provider applies a model variant, which stays the user's choice through the model map. The procedure is
`docs/skills/opencode-live-verification.md`; the version it records is in
`integrations/opencode/verified-version`.

### Not landed: parity defects

There is no worker-continuation guard (the shared core reads Claude Code's
transcript layout), a compose-mode plant's opencode session does not see the
kernel, and there is no compaction reset; the owner accepted these on
2026-11-10 and asked for none to be built now. Prime Agent has no pre-tool
guard, which the owner set aside for this round. The host matrix records each with what
would close it; the decision notes are in
`docs/plans/owner-decisions-8.4.0-opencode-2.md`.
