# Claude Code integration

This page says where an install puts the seed's files for Claude Code and how
Claude Code picks them up. Claude Code reads these on every session:
1. `CLAUDE.md` (project memory, at repo root).
2. `.claude/agents/*.md` (subagent definitions, YAML frontmatter).
3. `.claude/skills/*/SKILL.md` (loadable skills, progressive disclosure).
4. `.claude/commands/*.md` (custom slash commands).

"On every session" is also the sharp edge. Agent files can be written while a
session is running, by an install, a graft or a freshly commissioned expert,
and when the host picks them up is host-dependent; the
[host capability matrix](../../documentation/host-capability-matrix.md) records
it per host. A session rooted at the seed does not carry a plant's roster (the
agents installed in your project) at all.
`docs/graph/method/delegation-bounds.md` (`delegation.harness-registration`) owns the
preflight, the remedy, and the recorded fallback.

Project-scoped config in `.claude/` overrides user-scoped config in
`~/.claude/`. Both check into git when team-shared.

This seed system maps to Claude Code as follows:

| Seed file                    | Claude Code path                              |
|------------------------------|-----------------------------------------------|
| `core/AGENTS.md`             | `CLAUDE.md` (copy by default, or symlink with `--symlink`), with `AGENTS.md` beside it as a symlink to it |
| `agents/*.md`                | `.claude/agents/*.md`                         |
| `skills/*/SKILL.md`          | `.claude/skills/*/SKILL.md`                   |
| protocols → slash commands   | `.claude/commands/*.md` (see below)           |
| `templates/`                 | `docs/graph/templates/` (graph nodes)   |
| `templates/docs/` (graph leaves) | `docs/graph/` (missing leaves added on install) |

> **The projection is taken from the graph, not from the seed.** The rows
> above are `seed → harness` for brevity; the real path is
> `seed → docs/graph/{agents,skills}/ → harness`, and `install.sh`'s own
> log lines say so ("harness projection of docs/graph/skills/"). The
> distinction is not cosmetic: it is why a plant-commissioned expert that
> a grow run writes into `docs/graph/agents/` gets projected here too, and
> why `tools/growth-audit.py` reports one that reached the graph but not
> the harness as `UNGROWN` — on disk and unspawnable.

The agent frontmatter format used by this seed (`name`, `description`,
`tools`, `model`) is exactly what Claude Code expects, so the files
work unchanged.

## Slash commands

Every protocol whose node declares `command: true` in its frontmatter is
exposed as a slash command; `install.sh` **generates** one command file per
such node into `.claude/commands/`. Each generated file is a short pointer
that opens the corresponding `docs/graph/protocols/<name>.md` node as the
working context — the node is the single home, the command a generated
projection, so no per-harness copy can drift. The user-sovereign meta-loop
protocols (`graft`, `grow`, `harvest`)
carry no `command:` field, so they are commands on no harness; the command
surface is identical everywhere.

## Subagent invocation

In Claude Code, the orchestrator delegates to specialists through the
host's spawn tool (the [host capability matrix](../../documentation/host-capability-matrix.md#delegation-mechanism)
names it), calling them by their `name` field. The `description`
field is what Claude Code reads when deciding which subagent to
delegate to, so descriptions in `agents/*.md` are written to be
"pushy": they say when to use the agent as well as what it does.

## Effort

How Claude Code reads the `effort` key in subagent frontmatter, the values
it accepts, the override and inherit behaviour, the source and the seed's
closed set are recorded once, in `core/method/delegation-model-classes.md`
(`delegation.effort`). A plant has it as
`docs/graph/method/delegation-model-classes.md`, so a plant session reaches
those facts from its own graph.

## Prompt cache lifetime

Claude Code caches each request's prompt so a later call reads it at the
cached rate instead of paying for it again. The facts below come from the
Claude Code documentation (prompt caching, settings, subagents and
environment variables), read on 2026-11-10.

- **Defaults.** The main conversation, the lead, gets one hour on a
  subscription within its included usage and five minutes on usage credits,
  an API key or a cloud provider. Everything else, subagents above all, gets five minutes, except the helper
  requests the server controls, which get one hour on a subscription.
- **Controls.** `promptCacheTtl` (the lead) and `subagentPromptCacheTtl`
  (workers) in any settings file, `5m` or `1h`; the matching variables
  `CLAUDE_CODE_PROMPT_CACHE_TTL` and `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`;
  all four need Claude Code v2.1.242 or later. A subagent definition can set
  `cacheTtl` nested under `experimental:` in its frontmatter (v2.1.248 or
  later); Claude Code ignores a frontmatter `1h` while a subscription draws on
  usage credits. `FORCE_PROMPT_CACHING_5M`, set to `1`, forces five minutes
  over every other control, and `ENABLE_PROMPT_CACHING_1H`, set to `1`,
  requests an hour for both (environment variables and prompt caching pages).
- **Precedence**, first match wins: the force-five-minutes variable; the
  bucket's variable; the bucket's setting; the subagent's frontmatter; the
  enable-one-hour variable; the default.
- **Cost.** A cache write costs more than an uncached input token, a one-hour
  write more than a five-minute one, and a read costs less. The documentation
  read gives no multipliers; the API pricing page is their source, not
  checked here, and the seed stores no price.
- **Rule of thumb.** The lead gains from an hour when it waits on workers for
  more than five minutes at a time on metered billing. Workers stay on five
  minutes while new work goes to fresh workers (`delegation.continuation`).

The default install writes no cache setting. `install.sh claude-code
--prompt-cache-ttl 1h` writes `"promptCacheTtl": "1h"` into
`.claude/settings.json` and records the choice in `.cypress/seed.json`, so a
later install keeps it; `--prompt-cache-ttl default` removes it. The resume
guard below reads the worker lifetime by the same precedence.

## Install

Run `install.sh claude-code` from the seed root in the target project:

```sh
/path/to/cypress/install.sh claude-code
```

This creates (copies by default; pass `--symlink` for live seed links):
- `CLAUDE.md` → copy of `core/AGENTS.md`, and `AGENTS.md` → a symlink to `CLAUDE.md`
- `.claude/agents/*.md` → copies of `agents/*.md`; a charter that names
  `always_loads:` is composed with those nodes' bodies (a whole node, numbered
  sections, or one section named by its slug, as
  `skill.test-first#test-first.proportionate-checks`), and `--check` names
  one that drifted, and one whose loaded prompt lacks a rule that must reach
  its role (`tools/delivery_rules.py`, run from the seed). `install.sh claude-code --recompose-agents` rewrites
  `.claude/agents/` and `.claude/skills/` from the nodes on disk and writes no
  node (SPEC-0005 ROLE_AGENT_COMPOSES_ITS_ALWAYS_LOADED_NODES; `--check` also
  names a skill projection that differs from its node,
  SPEC-0001 CHECK_FLAGS_A_DRIFTED_SKILL_PROJECTION)
- `.claude/output-styles/orchestrator.md` → the orchestrator's composition,
  selected by `"outputStyle": "orchestrator"` in `settings.json`: the main
  session is no subagent, and an output style with `keep-coding-instructions:
  true` adds to Claude Code's prompt where an `agent` setting replaces it
  (SPEC-0005 MAIN_SESSION_PLAYS_THE_ORCHESTRATOR)
- `.claude/skills/<name>/SKILL.md` → copies of `skills/<name>/SKILL.md`
- `.claude/commands/*.md` → generated by install.sh, one per protocol node with `command: true`
- `docs/graph/` → scaffold + missing leaves from `templates/docs/`

With `--kernel-mode compose`, a team's own `AGENTS.md` stays canonical and is
never written: `CLAUDE.md` imports it on its first line and carries the
kernel after it (INSTALL.md, "An instruction hub your team already keeps").
A generic skill-corpus page placed with `--expertise skill-corpus/<name>`
lands as `docs/graph/skills/<name>.md` and is projected to
`.claude/skills/<name>/SKILL.md` like any skill node.

Every hook command names the Python the installer found at the seed's floor,
3.14 (SPEC-0005 §5): `python3`
when it is at the floor, else the `python3.<n>` it found on `PATH`. With no
Python at the floor the installer refuses before writing anything.

If a target file already exists with different content, the installer
backs it up to `<path>.bak-<timestamp>` and warns (byte-identical
files are left untouched). `--force` drops the warning but still makes
the backup; see INSTALL.md "What gets backed up". For an edited
`.claude/settings.json` the warning names each key path your file had and
the new one lacks; edited host settings upgrade by graft, which keeps the
file.

## Hooks

Three hooks ship in `settings.json`. `route-hook.py` (UserPromptSubmit) and
`status-hook.py` (SessionStart) inject context and are wired fail-open with
`|| true`, so a context hook always lets the prompt through
([routing pointer](../../DOCUMENTATION.md#enf-route-hook),
[status summary](../../DOCUMENTATION.md#enf-status-hook)).
The route hook names the router's nodes for the prompt, each id beside its
node file. Later in the session it names a node already shown by id on one
`seen:` line, and it does not route a turn a person did not type, such as a
task notification. Prime Agent runs the same two scripts through its extensions. The status hook runs once per session: it injects the status
register's summary and ends with the line `docs/graph/code-anchor.py
--compare` prints, which says whether the code moved since canonize last
recorded the anchor. When the comparison does not finish within 5 s, that
line says the code was not checked. No other hook runs the anchor.

Fail-open does not mean silent. When the script a context-hook command names
is missing, the command prints one line, `cypress: hook script missing:
<path>; continuing without it. Re-run install.sh to restore it.`, and the
prompt still goes through. When the router itself crashes, the route hook
prints one line, `No route: graph-lint.py exit <status>: <its last stderr
line>`, and the prompt still goes through
(SPEC-0003).
`install.sh claude-code --check` runs each wired
context hook once, from the plant, on an envelope with no session id, and
fails naming any hook whose script is missing, exits non-zero or prints
nothing. A sound hook always prints on that envelope, because the status hook
ends with its anchor line even when the register is absent. The check writes
nothing in the plant, and graft runs it under `graft.gate.routes`.

`bound-hook.py` (PreToolUse, matcher `Bash`) is a guard and is wired without
`|| true`. It exits 2, and the host then does not run the command, when a shell
command that can hang (service control, process signalling, package managers,
installers, builds, log followers) carries neither an explicit bound nor a
detached launch. It prints both accepted forms for the offending command on
stderr ([pre-Bash check](../../DOCUMENTATION.md#enf-pre-bash-guard)):

- bounded: `timeout 30 systemctl --user daemon-reload`
- detached: `setsid nohup ./job.sh > job.log 2>&1 & echo $! > job.pid`

Kill by a recorded pid (`kill -TERM $(cat job.pid)`) passes; `pkill`,
`killall` and `kill … $(pgrep …)` do not, because no bound repairs signalling
the wrong process. The script itself can only exit 0 or 2, and every failure
path inside it (not Bash, no command, unparseable stdin, internal error)
exits 0 with one line on stderr, so a bug in the guard degrades to no guard
and can never block every call. A script that is missing is the wiring's
case: both guard commands test that the file exists and, when it does not,
allow the call with one stderr line, `cypress: hook script missing: <path>;
the guard is off. Re-run install.sh to restore it.` `install.sh claude-code
--check` fails naming the event, matcher and path of a missing guard script,
and does not run the guard. A plant still wired by an earlier seed runs the
guard with no existence test, so a missing script makes the interpreter exit 2
and the host blocks every call of that tool; `--check` says so plainly and
names the remedy, a re-install that restores the script and the guarded
wiring. The pattern list is a commented constant at
the top of the file; extending it is a one-line change. The doctrine behind
the guard is `core/method/bounded-execution.md` (`toolcraft.bounded-execution`); the test is
`tests/test-bound-hook.sh`. What the pattern match can miss is listed in the
[pre-Bash check row](../../DOCUMENTATION.md#enf-pre-bash-guard).

`resume-hook.py` (PreToolUse, matcher `SendMessage`) is the second guard, wired
the same way. It acts only on a worker whose transcript has been idle longer
than the worker's prompt cache lives (the lifetime resolved as above; five
minutes when it cannot tell, `COLD_AFTER`), because a message to it
re-reads its whole context uncached. A worker whose last record is the host's
API error (usage or rate limit, network or server error) was cut off and its
resume is allowed. Any other cold worker, one that handed back above all, is
refused (exit 2): the message is new work for an old context, or a nudge to a
worker with nothing left to do. A message whose first line starts
`continuation:` passes: the caller declares a small follow-up that needs that
context, or a worker stopped with no error record (`delegation.continuation`).
Every failure path allows. The test is
`tests/test-resume-hook.sh`. Each brief `brief.py` composes is logged to
`docs/graph/plans/spawns.jsonl` (`delegation.tracing`), the spawn log the
delivery's attribution reads.

A hook or loop you add yourself exits when every open step is the owner's;
`docs/graph/protocols/deliver.md` ("When every open step is the owner's") owns
that rule.

## Works unchanged

The agents and skills work in Claude Code as written: they follow its
conventions and the other tools' at once. The kernel and team are the
same across every host the seed installs.
