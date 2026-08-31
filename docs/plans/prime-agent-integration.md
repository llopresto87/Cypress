# Plan-of-record — first-class `prime-agent` integration (CYPRESS)

**Directive (user, verbatim intent):** "Engage grill protocol, tier-3; i
want you to add complete and full, first citizen support for prime-agent
to this project."

**Protocol:** `grill` (docs/graph/protocols/grill.md) — plan-of-record
before code. **Tier:** T3 (new behavior + new installer path + new gated
surface). This file is the seed's plan-of-record home (`docs/plans/`,
the seed's replacement for `docs/graph/plans/`).

**Status:** EXECUTED (shipped as 6.7.0 — see CHANGELOG.md). All gates green: `bash tests/run.sh` (five-tool install contract + CC/PA coexistence, seed-lint, agent-lint parity gate on `.prime/agent/agents/`, graph/spec/legal lints). Delivered beyond the original plan: an RLM-native `APPEND_SYSTEM.md` execution overlay (exploits rlm()/continual-harness/agent_message/in-kernel gates), a shared-kernel `place_kernel` for interchangeable CC/PA plants, and cross-organ enumeration parity (kernel, delegation, seed-installer, initialize, from-scratch, graft, bootstrap skill). The `skills/test-first/SKILL.md` strict-YAML bug was fixed.

---

## §1 — Artifact discovery (what already exists; read, not guessed)

- `integrations/{claude-code,codex,github-copilot,opencode}/` — four
  supported harnesses. Each ships a `README.md`; claude-code also ships
  `settings.json`, `route-hook.py`, `agent-lint.py`; codex ships
  `config.toml.example`; github-copilot ships `hooks/route.json`;
  opencode ships `opencode.json`.
- `install.sh` — per-tool installers (`install_claude_code`,
  `install_opencode`, `install_codex`, `install_github_copilot`),
  shared helpers (`place_file`, `place_tree`, `place_docs_skeleton`,
  `generate_slash_commands`, `command_protocols`,
  `log_registration_notice`), arg parser (`claude-code|opencode|codex|
  github-copilot|all`), and `all` expansion.
- `manifest.json` — `integrations` array (4 entries) + `version` (6.6.0).
- `tests/seed-lint.py` — `REGISTRATION_REFERRERS` (every dispatch/install
  surface must contain the literal `delegation.harness-registration`);
  prose numeric scan over `integrations/*/README.md`; opencode config
  validity + session budget.
- `tests/test-full-install.sh` — the "four-tool install contract";
  `assert_cmd_roster` pins each harness's command set to the
  `command:true` protocol roster.
- `README.md`, `INSTALL.md`, `integrations/claude-code/README.md` —
  prose that enumerates "four" tools / lists the four integrations.

## §5 — Research summary (prime-agent conventions, verified vs
prime-agent 0.8.1 `README.md` + `docs/`)

| Capability | Prime Agent home (verified) | Notes |
|---|---|---|
| Project instructions (kernel) | auto-loads `AGENTS.md` **or** `CLAUDE.md` from cwd + parents + `~/.prime/agent/`; concatenated | same repo-root `AGENTS.md` opencode/codex already produce |
| Slash commands | prompt templates `.prime/agent/prompts/<name>.md`, `/name`; frontmatter `description`; auto-discovered | 1:1 with the `command:true` roster |
| Skills | `.prime/agent/skills/<name>/SKILL.md`, auto-discovered, `/skill:name`; same Agent-Skills `SKILL.md` shape the seed already ships | copy/symlink, no transform |
| Delegation / roster | **no static roster dir**; delegation is runtime `await rlm("brief")` + continual-harness subagent specs (`rlm.harness`) | see D4 |
| Route enforcement (hook) | TypeScript extension `.prime/agent/extensions/*.ts`, event `before_agent_start` → returns `{message, systemPrompt}` = inject context/mandate | exact analog of Claude Code `UserPromptSubmit` route-hook.py |
| Settings | `.prime/agent/settings.json` (project); resource keys `extensions`/`skills`/`prompts` arrays; **no** `instructions` key, **no** `subagent_depth` analog | no double-load risk, no depth-cap knob needed (unlike opencode) |

## §6 — Decisions

- **D1 (reversible):** kernel → repo-root `AGENTS.md` (reuse existing
  target; Prime Agent auto-loads it).
- **D2 (reversible):** commands → generated projections in
  `.prime/agent/prompts/` via the existing `generate_slash_commands`
  (same roster, same single home = the protocol node).
- **D3 (reversible):** skills → `.prime/agent/skills/<name>/SKILL.md`
  projections (no transform — SKILL.md format matches).
- **D4 (reversible):** roster → `.prime/agent/agents/*.md` projections
  as **brief sources**. Prime Agent has no session-start roster
  enumeration and spawns children with an inline brief, so the
  "installed but not spawnable" registration lag *does not exist here*:
  a brief on disk is usable by the very next `rlm()` call. The kernel's
  `delegation.harness-registration` role-emulation path already covers
  "harness without native roster registration"; prime-agent is its
  cleanest case. README states this explicitly.
- **D5 (reversible):** route enforcement → ship
  `integrations/prime-agent/route-extension.ts`, installed to
  `.prime/agent/extensions/route-extension.ts`. On `before_agent_start`
  it runs `python3 docs/graph/graph-lint.py --plan "<prompt>"` (identical
  to route-hook.py) and injects the route-first mandate + suggested
  nodes. Fail-open, never blocks.
- **D6 (reversible):** ship `integrations/prime-agent/settings.json`,
  copied to `.prime/agent/settings.json` — minimal, valid, pins the
  three resource dirs explicitly (robust even if a project disables
  auto-discovery); no `instructions` key (kernel already auto-loaded,
  so no double-load).
- **D7 (reversible):** manifest `method: "symlink"`; bump manifest
  version + append CHANGELOG entry (behavior change).

## §8 — Architecture

```
seed source                      prime-agent target (in a plant)
core/AGENTS.md            ->      AGENTS.md                      (kernel, auto-loaded)
docs/graph/ (machinery)  ->      docs/graph/                    (the one knowledge system)
skills/<n>/SKILL.md       ->      .prime/agent/skills/<n>/SKILL.md
agents/*.md               ->      .prime/agent/agents/*.md       (brief sources for rlm())
protocols[command:true]   ->      .prime/agent/prompts/<n>.md    (generated /commands)
route-extension.ts        ->      .prime/agent/extensions/route-extension.ts
settings.json             ->      .prime/agent/settings.json     (copied, editable)
```

## §9 — Implementation increments (each maps to a gate = its contract)

- **INC1 — payload authored.** Files: `integrations/prime-agent/README.md`,
  `settings.json`, `route-extension.ts`. Contract: README contains the
  literal `delegation.harness-registration`; README numeric prose
  consistent. Gate: `seed-lint` referrer + prose scan. Rollback: rm dir.
- **INC2 — installer.** Files: `install.sh` (`install_prime_agent`, arg
  case, `all` expansion, help header). Contract: `install.sh prime-agent
  --project-dir T` places `AGENTS.md`, `.prime/agent/{prompts,skills,
  agents,extensions,settings.json}`, `docs/graph/`. Gate: new block in
  `test-full-install.sh`. Rollback: revert install.sh.
- **INC3 — lint recognizes the fifth harness.** Files: `tests/seed-lint.py`
  (add prime-agent README to `REGISTRATION_REFERRERS`). Contract:
  seed-lint PASS. Gate: `seed-lint`. Rollback: revert.
- **INC4 — five-tool contract + docs.** Files: `tests/test-full-install.sh`
  (prime-agent block + "five-tool"), `manifest.json` (integrations +
  version), `CHANGELOG.md` (append), `README.md`, `INSTALL.md`,
  `integrations/claude-code/README.md` (four→five). Contract:
  test-full-install PASS; prose numeric PASS. Rollback: revert.
- **INC5 — verify.** `bash tests/run.sh` all green + a manual
  `install.sh prime-agent` scratch install inspection.

## §10 — Verification plan

`bash tests/run.sh` (9 shell suites + agent-lint + graph regressions +
seed-lint + legal-lint) after each increment; the five-tool block in
`test-full-install.sh` is the load-bearing new gate.

## §11 — Risks

- **R1 (med/med): extension API drift.** `before_agent_start` shape is
  from prime-agent 0.8.1 docs. Mitigation: the extension is fail-open
  (any error → no injection, never blocks); the kernel's own FIRST-MOVE
  mandate is the non-hook floor. README pins the verified version.
- **R2 (low/high): claiming a native roster prime-agent lacks.** Avoided
  by D4 — roster installed as brief sources, not as a fake registered
  team; README states the runtime `rlm()`/continual-harness model.
- **R3 (low/med): prose "four" left stale.** Mitigation: INC4 enumerates
  every user-facing "four supported tools" site (README, INSTALL,
  claude-code README); lint's numeric scan is agent/skill counts only,
  so this is manual and checklisted.

## §12 — Open questions

- OQ1: Should the roster ALSO be seeded as continual-harness subagent
  specs? Resolution: no — those are session/user-local state, not
  committable install artifacts; README documents the runtime path as
  the native mechanism. Owner: this plan. RESOLVED.

## §13 — Done criteria

- `install.sh prime-agent` produces the full target tree; `all` includes
  it. `bash tests/run.sh` green including the five-tool contract.
  manifest lists 5 integrations + bumped version; CHANGELOG appended.
  All user-facing "four tools" prose reads five. prime-agent README is a
  `delegation.harness-registration` referrer.

## §14 — Recommended next step

Enter implementation at INC1 (author `integrations/prime-agent/`).

## §15 — Changelog

- <this session>: grill pass; plan authored through §14.


---

## §16 — PARITY DIRECTIVE (user, follow-up): Claude Code AND prime-agent are BOTH first-class

prime-agent must reach Claude Code's depth, NOT the lighter
opencode/codex/copilot tier. Claude Code's first-class surface, and the
required prime-agent equivalent:

| Claude Code first-class element | prime-agent parity target |
|---|---|
| `route-hook.py` (UserPromptSubmit enforcement) | `route-extension.ts` (`before_agent_start`) — D5 |
| `agent-lint.py` — a REAL gate in `tests/run.sh` (`--lint` frontmatter/delegation + `--eval` routing accuracy over `agents/_routes.golden.tsv`) | **OPEN — see below.** A CI-enforced validation surface for the installed `.prime/agent/agents/*.md` roster briefs, equal to claude-code's, not doc-only |
| `settings.json` | `.prime/agent/settings.json` — D6 |
| manifest `agent_router` block → agent-lint.py | manifest must point prime-agent at its validator too |

**The gate question (blocking design decision, scout is investigating):**
`agent-lint.py` lints a *static roster* and scores routing. prime-agent has
no static roster enumerated at session start. Candidate parity moves:
(a) point the SAME `agent-lint.py` at installed `.prime/agent/agents/*.md`
so the briefs are still frontmatter/delegation-validated + routing-scored in
CI; (b) a prime-agent-specific validator; (c) native. Leaning (a): the
roster briefs carry the same frontmatter, so one linter validates both
harnesses — but confirm agent-lint.py's dir assumptions. Resolve from scout
report before implementing.

**Dogfooding (open):** "this project" may also mean the SEED REPO ITSELF
should be developable first-class in BOTH harnesses. It already carries root
`CLAUDE.md` + `.claude/` for its own dev; it may also warrant a `.prime/agent/`
(route-extension + prompts + settings) so a Prime Agent dev session gets the
same experience — without breaking "the seed is not a plant" (install.sh
refuses self-install). Resolve from scout report.

These raise INC list: add **INC2.5 — prime-agent validation gate parity**
(the agent-lint equivalent + manifest agent_router pointer) and, if adopted,
**INC6 — seed-repo dogfooding scaffolding**.


---

## §17 — PRIORITY DIRECTIVE (user): first-class tier vs back-seat tier

- **First-class citizens (parity, protected):** `prime-agent` and `claude-code`.
- **Back-seat citizens (may regress):** `opencode`, `codex`, `github-copilot`.

If a change required for prime-agent/claude-code parity would make one of the
back-seat harnesses incompatible, proceed and let it regress — do NOT compromise
first-class parity to protect them. Keep them working only where it is free
(the core integration is additive, so all five can stay green now). This
latitude covers, e.g., shared-machinery edits (agents/*.md, skills/*, kernel)
and any lint/gate tension: prime-agent + claude-code win.

Consequence for the two resolved source conflicts:
- Depth: the seed's max_spawn_depth=3 vs prime-agent default RLM_MAX_DEPTH=2 is
  documented (global/session/env remedy), since prime-agent has no committable
  project knob — a prime-agent property, not an opencode concern.
- The `skills/test-first/SKILL.md` YAML-quote fix is harmless to all harnesses,
  so it lands regardless.
