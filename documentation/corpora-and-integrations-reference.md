# CYPRESS — Corpora and Integrations Reference

This reference documents two parts of the CYPRESS seed:

- **Part A — the corpora.** The five seed-side knowledge stores that
  `harvest` deposits into and that `grow` / `graft` draw from.
- **Part B — the integrations.** The five per-tool adapters under
  `integrations/` that project the shared seed onto each host harness.

The repository root is `<seed-root>`. Every fact below comes from source files
on disk; each major section cites its source path.

---

# Part A — The Corpora

CYPRESS keeps five corpora at the seed root. Each corpus is a
project-agnostic, durable store of reusable knowledge. `harvest`
(`protocols/harvest.md`, `HARVEST_PROMPT.md`) folds a mature plant's
generalizable lessons *into* a corpus; `grow` / `graft` / `toolcraft` /
commission withdraw *from* a corpus when a new project needs the same thing.

The five corpora and their mirror relationship (source:
`protocols/harvest.md`, each corpus `README.md`):

| Corpus | Root path | Holds | Mirror of |
|---|---|---|---|
| Library corpus | `library-corpus/` | Third-party library / language / runtime surface notes | a plant's `docs/graph/libraries/` |
| Legal corpus | `legal-corpus/` | External law, regulation, standards citations | a plant's `docs/graph/legal/` |
| Tool corpus | `tool-corpus/` | Reusable, stack-neutral tools | a plant's `docs/graph/tools/` |
| Agent corpus | `agent-corpus/` | Optional expert roles (candidates) | a plant's roster / `docs/graph/agents/` |
| Skill corpus | `skill-corpus/` | Optional procedures (candidates) | a plant's `docs/graph/skills/` |

The library and legal corpora are reference corpora (external facts to cite).
The tool, agent, and skill corpora are artifact / role / procedure corpora
(reusable seed material to instantiate).

## A.0 The gates every corpus clears

Every corpus entry clears harvest's three gates (agnosticism, durability,
non-redundancy) and the withdraw-ready bar. Their one home is
`protocols/harvest.md` (§The agnosticism gate to §The third gate, §The
corpora); each corpus `README.md` applies them to its own pages.

One more principle governs *reading* a corpus: orientation, not gospel. A
corpus page seeds a project's own leaf as an orientation layer; the project
then confirms current facts against the real source (the lockfile, the
publisher, the stack) and authors its own application beside the citation.

## A.1 Why corpora sit outside the kernel and roster

Source: `agent-corpus/README.md`, `protocols/harvest.md` (§ "The
suggested-expert corpus").

The always-loaded team lives in `agents/`, is named in the kernel §1 table, and
every plant pays its per-session cost. That economy is the reason a harvested
role, procedure, or reference does not land in the kernel or the always-loaded
roster. Instead:

- A corpus is a catalog of candidates: none loaded by default, none named in
  the kernel. It costs nothing until a project selects an entry.
- Depositing into a corpus gives harvest a home for a generic foreign role,
  tool, procedure, or citation without touching the kernel budget or the
  seed's one-home-per-fact roster.
- The kernel is loaded on every session of every plant, so depth belongs in
  a machinery node or a corpus; the kernel's byte budget is
  [enforced](../DOCUMENTATION.md#enf-kernel-budget).

## A.2 The steward-only promotion rule

Source: `protocols/harvest.md`, §"Promotion to the base roster".

> **Promotion to the base roster is a separate, steward-only decision**, and
> the bar is higher than "useful": the role's mandate must be **universal** —
> every project produces the thing it addresses, not merely many of them — and
> no base-roster agent may already cover it.

Key points:

- A role that serves a domain some projects simply do not have (a regulatory
  analyst, a stack specialist) stays in the catalog however good it is,
  because the catalog costs nothing until selected.
- Harvest may *propose* a promotion; the steward (the seed owner) makes it.
- `harvest` and `graft` are user-sovereign: only the user starts them, and
  the method may propose one and then stops (source: `CLAUDE.md`,
  `HARVEST_PROMPT.md`, `protocols/harvest.md` § "Trigger: user-started; the
  system proposes, the steward starts").

## A.3 How harvest deposits and grow/graft withdraw

Source: `protocols/harvest.md`, each corpus `README.md` § "The withdraw
contract".

**Deposit (harvest, inbound).** Harvest runs only when the user starts it.
What it mines from a mature plant, the gates each candidate clears and the bar
a page meets have one home, `protocols/harvest.md` (§Phase 1, §The agnosticism
gate to §The third gate, §The corpora). Plant-identifying provenance lives only
in the ratification proposal shown to the steward.

**Withdraw (grow / graft / toolcraft / commission, outbound).** When a new
project needs a capability, role, procedure, or citation, it checks the
matching corpus first:

| Consumer | Corpus checked first | What it seeds | Template used |
|---|---|---|---|
| `ingest-library` (grow) | `library-corpus/` | `docs/graph/libraries/<name>.md` orientation layer | — |
| `grow` (Phase 4) / `graft` | `legal-corpus/` | `docs/graph/legal/<instrument>.md` orientation layer | — |
| `toolcraft` / `grow` | `tool-corpus/` | `docs/graph/tools/<name>.md` orientation layer | — |
| `grow` / `graft` / commission | `agent-corpus/` | `docs/graph/agents/<name>.md` | `docs/graph/templates/agent.template.md` |
| `grow` / `toolcraft` / commission | `skill-corpus/` | `docs/graph/skills/<name>.md` | `docs/graph/templates/skill.template.md` |

If a match exists, the project seeds its own leaf from the corpus page as the
orientation layer, then fetches or authors the version-specific / project-
specific delta fresh. If no match exists, the project ingests / commissions /
authors fresh, and that durable, agnostic work becomes a harvest candidate
for the next cycle. Nothing project-specific ever flows back.

## A.4 Inventory

The inventory of each corpus is its directory listing, and each corpus README's
`## Layout` names what every folder holds. The tables below name the folders
and give examples; they carry no page counts, because a count restated here is
a second home that goes stale with the next page added.

### A.4.1 Library corpus — `library-corpus/`

Keyed by `library-corpus/<ecosystem>/<library>.md`, one page per library, not
per version. `<library>` is the canonical id, lowercased, scope slash removed
(`@microsoft/signalr` -> `microsoft-signalr`). Source:
`library-corpus/README.md`.

| Ecosystem (subfolder) | Examples |
|---|---|
| `cli` | `curl.md`, `git.md`, `trivy.md`, `gitleaks.md` |
| `container` | `docker.md`, `docker-compose.md`, `nginx.md`, `docker-host-hardening.md`, `postgres.md` |
| `galaxy` | `ansible.posix.md`, `community.docker.md` |
| `language` | `python.md`, `typescript.md`, `dotnet.md`, `nodejs.md`, `angular.md`, `flutter.md` |
| `maven` | `spring-boot.md`, `hibernate-orm.md`, `resilience4j.md`, `stripe-java.md` |
| `npm` | `rxjs.md`, `playwright-test.md`, `primeng.md`, `keycloak-js.md` |
| `nuget` | `Microsoft.EntityFrameworkCore.md`, `Dapper.md`, `xunit.md`, `Npgsql.md` |
| `platform` | `azure-cli.md`, `azure-devops-rest.md`, `azure-pipelines-yaml.md` |
| `pub` | `dio.md`, `flutter_bloc.md`, `flutter_secure_storage.md` |
| `pypi` | `fastapi.md`, `pydantic.md`, `numpy.md`, `openai.md`, `qdrant-client.md` |

`maven` and `nuget` hold the largest share of the pages; see §A.4.1a for
what that means for an adopter on a different stack.

- **Belongs here and stays out:** one home, `library-corpus/README.md` ("The
  admission bar", "What belongs here", "What stays OUT").
- **Note on hosted-platform DSLs:** a hosted platform's declarative
  pipeline/config DSL (e.g. a CI platform's YAML schema) may earn a page with
  no installable package, pinned by retrieval-date instead of a version.
- New ecosystems (`cargo`, `go`, `gem`, …) are added as they are harvested.

Example entry shape (`library-corpus/pypi/fastapi.md`): a title
`# fastapi — pypi`, an agnostic blockquote, then `## What it is`,
`## Core API / usage shape`, `## Idioms & best practices`, `## Upstream docs`.

### A.4.1a Agnosticism: the machinery is, the shipped corpus is not

The seed's machinery — protocols, skills, agents, `ingest-library`,
`research-and-ingest`, `library-wiki` — makes no assumption about ecosystem;
it ingests any dependency, in any language, the same way. The **shipped
library-corpus content** is a different claim: `maven` and `nuget` hold the
largest share of its pages (the §A.4.1 table). The lean is in the
composition, not the mechanism.

A library page reaches a plant only by selective placement, on the owner's
word: `install.sh <host> --expertise propose` prints the corpus pages the
project's manifests match, and `install.sh <host> --expertise <id>[,<id>...]`
places exactly the pages named and records them in `.cypress/seed.json`
(`expertise`). `grow` proposes the list and `graft` refreshes it. Nothing is
placed by default. A placed page skips the scout in `ingest-library` and gets
only the version delta (`ingest-library.corpus-first`, which owns the rule).

**What this means for an adopter, concretely:**

- On any stack, `install.sh` gives every adopter the identical, fully
  agnostic machinery: the same `ingest-library` phases, the same
  smoke-test-then-finalize pass, over whatever dependency the project
  actually uses.
- A .NET or Java plant finds a page to place for much of its dependency
  surface (EF Core, Dapper, xUnit, Npgsql, Spring Boot, Hibernate,
  Resilience4j, and the rest); the plant still pins and validates the page
  against its own lockfile.
- A Rust, Go, Ruby, or PHP plant finds nothing to place for its ecosystem
  (none of those ecosystems has a subfolder yet) and runs the same
  from-upstream `ingest-library` pass a .NET plant runs for any dependency
  the corpus lacks. The gap is corpus coverage, not capability, and it closes
  the way every corpus entry arrives: `harvest` folding a future plant's
  ingested pages back in.

**Why the corpus exists, and why it is not a version-drift tracker:** one
home, `protocols/harvest.md` ("The library & language documentation corpus"),
with `library-corpus/README.md` ("Purpose"). A plant's own pin, smoke test and
advisories still come from running `ingest-library` against its lockfile.

### A.4.2 Legal corpus — `legal-corpus/`

Keyed by `legal-corpus/<scope>/<instrument-slug>.md`, one page per instrument
(or tightly-coupled family). Entry shape fixed by `_schema.md`; routed by
`index.md`. Source: `legal-corpus/README.md`, `legal-corpus/index.md`,
`legal-corpus/_schema.md`.

| Scope (subfolder) | Examples |
|---|---|
| `eu` | `gdpr.md`, `nis2.md`, `cra.md`, `eprivacy-directive.md`, `psd2.md`, `sca-rts-2018-389.md`, `edpb-guidelines-02-2023.md` |
| `international` | `iso-27001.md` |
| `national` | `it-codice-privacy.md`, `it-workers-statute.md`, `it-accounting-retention.md` |
| `case-law` | `index.md`, a multi-entry router page (see below) |

`legal-corpus/index.md` routes every instrument page; read it, not this table,
for the full list.

The four scopes are: `eu` (Union-level instruments), `national`
(country-code-prefixed statutes, e.g. `it-…`; a second jurisdiction would
file as `de-…` or `fr-…` under the same convention, but today the national
layer carries exactly one country — `it` — across all three of its pages),
`international` (global standards / treaty-level), and `case-law` (judicial
and regulator decisions, which routinely span jurisdictions).

`case-law/index.md` is a single page holding several citable entries, one
per case/decision, each with its own id. Examples present:
`cjeu-c-582-14-breyer`, `gc-latombe-2025-judgment`,
`cjeu-c-703-25-p-latombe-appeal`, `garante-elenco-dpia-2018`,
`lg-muenchen-i-3-o-17493-20`, `garante-9782874-google-analytics`, and
`absent-garante-google-fonts` (a verified absence: a recorded finding that
a decision does not exist, itself a valid citable entry).

**What is special about the legal corpus.** It is the sharpest agnosticism
boundary of the five, because legal analysis *feels* portable and is not. The
corpus states what the law says; the plant states what that means for
one system. Everything that stays out (source: `legal-corpus/README.md`):

- Any application of the law to a system.
- Any project's own finding, risk posture, gap, or remediation status.
- Any source-file, path, component, endpoint, or vendor reference.
- Any determination (in scope, compliant, exposed).

**The citability contract (`_schema.md`).** An entry is citable only if it
carries all eight fields: `id`, `instrument`, `provision`, `text_form` +
`text`, `official_url`, `consulted` (what was actually read, with a
`verification_grade`), `language_version` (edition / consolidation),
`verified` + `legal_status`. Missing any one ⇒ non-citable, treated by a
consumer as `not recorded — requires ingest`.

**Standing hazards (`_schema.md`, `index.md`):**

1. **The amendment trap:** original text and consolidated text sit under the
   same article number and read identically. An entry must state ORIGINAL vs
   CONSOLIDATED (with date), or it is non-citable.
2. **Same number, different subject:** a directive's Article N and its
   transposing act's Article N routinely address unrelated matters.
3. **`in force` ≠ settled:** an instrument can be valid and under appeal.
4. **A number is the highest-risk field:** deadlines, thresholds, fine
   ceilings. Record a deadline that is a *formula* as the formula; a
   *calendar date* in its place is wrong.
5. Guidance is not law, and a standard is not a legal basis.

Grade each entry on its own, never the page: a page may hold a
primary-fetched verbatim article beside a secondary-corroborated summary, and
a page-level "verified" banner over mixed provenance is falsification. `text_form` values: `verbatim`
(quotable), `normalized summary` (not the law's words), `wording withheld —
requires licensed copy` (citable by identifier and title only), `topic only`.

**Roles (`legal-corpus/index.md`):** written by `docs-librarian`, ingested by
`research-scout`, and read by the base-roster legal agent, `agents/14-legal.md`,
which runs without `WebSearch`, `WebFetch`, or `Bash`, so this
corpus plus the project's own legal leaf is its only source of law. A corpus
gap produces an explicit refusal (`not recorded — needs ingest`), never a
reconstructed citation. That refusal-on-gap behaviour is only safe because
`_schema.md` forces the corpus to be honest about what it did and did not read.

**Withdraw contract.** `grow` (Phase 4, the `legal/` collection) seeds the
project's `docs/graph/legal/<instrument>.md` from the matching corpus page as
the orientation layer; the project authors its own application beside it.
`graft` (Phases 2, 4, 5) refreshes an already-grown project's legal leaves the
same way. Currency is never withdrawn, only the citation: re-confirm
`verified` + `legal_status` before any consequential reliance. Nothing flows
back except a citation; a superseded entry is never deleted, only marked and
linked forward.

### A.4.3 Tool corpus — `tool-corpus/`

Keyed by `tool-corpus/<category>/<name>.md`, one page per tool. Source:
`tool-corpus/README.md`.

| Category (subfolder) | Examples |
|---|---|
| `ops` | `container-deploy-pipeline.md`, `env-secret-rotation.md`, `registry-digest-resolver.md`, `resolved-dependency-gate.md`, `destructive-command-guard-hook.md` |
| `testing` | `http-smoke-suite.md`, `behavior-baseline-oracle.md`, `failure-signature-triage.md`, `live-contract-check-harness.md`, `test-hygiene-lint.md` |

`tool-corpus/README.md` (`## Layout`) names every kind of tool each category
holds.

- **Belongs here:** the capability and the recurring operation; the interface
  shape (invocation, inputs, outputs) in the general; the portable
  implementation when the tool is genuinely stack-neutral (a self-contained
  script with no third-party or project dependencies, like the seed's own
  `graph-lint.py` / `agent-lint.py`); the approach/algorithm and idioms;
  conceptual pitfalls.
- **Stays out:** one home, `tool-corpus/README.md` ("What stays OUT").
- Each page carries a `## 0. Identity` block (Category, Name, Language /
  runtime, Stability: `portable`) then `## 1. What it does`, `## 2. Interface &
  invocation`, and so on.
- A page may carry a `stack:` field naming the library-corpus pages it is
  bound to (`tool-corpus/README.md`, "The stack field"); a stack-neutral tool
  carries none.
- Further categories (`scaffolding`, `codegen`, `data`, `analysis`) are added
  as harvested.
- **Withdraw:** adopt the portable implementation only when the stack matches;
  otherwise treat the page as a blueprint and re-author against the project's
  real stack, test-first.

### A.4.4 Agent corpus — `agent-corpus/`

Keyed by `agent-corpus/<name>.md`, kebab-case id, one page per suggested role.
Source: `agent-corpus/README.md`.

`agent-corpus/README.md` (`## Layout`) names every role and what it owns. The
legal page there, `legal.md`, is only a pointer to the base-roster agent,
`agents/14-legal.md`, which owns the legal mandate; the catalog offers no second
legal role (see A.4.2).

- These are OPTIONAL expert roles: none loaded by default, none named in
  the kernel. A project *may* select one.
- **Belongs here:** a role's mandate, when to select it, its boundary against
  the base roster, and its `routing_triggers` exemplars, all statable with
  zero framework names. Every page follows the shape: optional-role
  blockquote, `## Mandate`, `## When to select`, `## Boundary (does not
  duplicate the base roster)`, `## routing_triggers (exemplars)`.
- **Stays out:** one home, `agent-corpus/README.md` ("What stays OUT"); it
  also admits discipline roles on a stack-shaped surface ("What belongs here").
- **Withdraw:** a matching role is instantiated into the project's
  `docs/graph/agents/` (the harness projections, `.claude/agents/` and kin,
  are regenerated from it) from `docs/graph/templates/agent.template.md`,
  grounded in the project's pinned facts. The selected role joins the
  *project's* roster (and its kernel table / manifest), never this catalog.

### A.4.5 Skill corpus — `skill-corpus/`

Keyed by `skill-corpus/<name>.md` for a generic procedure and
`skill-corpus/<key>/<name>.md` for a stack-keyed one, where `<key>` is a
library-corpus key; one page per suggested procedure, kebab-case id. Source:
`skill-corpus/README.md` (`## Layout` names every page; `## Stack-keyed pages`
holds the keyed-page rules).

- A skill is a procedure (the disciplined sequence for a recurring kind of
  work), as opposed to an *agent* (a role) or a *tool* (an artifact). The
  seed's `skills/` holds the fixed core methodology every plant inherits;
  this corpus holds optional procedures a project may or may not need.
- **Belongs here:** a procedure statable with no plant identity, whose steps
  each name the gate they clear, stated by composing existing
  protocols/skills/agents by reference (never restating a discipline the seed
  already owns), recurring across independent project lineages. Naming a
  widely-portable substrate (a container runtime, an SSH transport) is fine when
  that substrate *is* the procedure's subject.
- **Stays out:** one home, `skill-corpus/README.md` ("What stays OUT").
- Each page opens with an optional-procedure blockquote naming what it composes
  and its parameters, then `## When to apply`, the procedure, and
  `Reference files`.
- **Withdraw:** a matching page is instantiated into the project's
  `docs/graph/skills/<name>.md` (projected into `.claude/skills/<name>/SKILL.md`
  and kin by the harness) from `docs/graph/templates/skill.template.md`,
  grounding its steps in the project's real gates and tools.

---

# Part B — The Integrations

CYPRESS ships one kernel, one roster, one skill set, and one protocol set, and
projects them onto five host harnesses, two of them frozen (ADR-0009), through
per-tool adapters under `integrations/`. Source: `integrations/*/README.md`, `README.md`, `INSTALL.md`,
`tests/test-full-install.sh`.

The universal source of truth is:

- `core/AGENTS.md`: the kernel.
- `agents/*.md`: the roster (Claude-Code-shaped frontmatter: `name`,
  `description`, `tools`, `model`).
- `skills/*/SKILL.md`: the skills.
- `protocols/*.md`: the protocols (each node whose frontmatter declares
  `command: true` is projected as a slash command; the user-sovereign
  meta-loop protocols `graft`, `grow` and `harvest` carry no `command:` field
  and are commands on no harness).
- `templates/docs/`: the `docs/graph/` knowledge-graph leaves.

`install.sh <tool> [<tool> …]` drops the seed into a target project for one
tool, or `all` for the three maintained ones, copying by default (`--symlink` opts into live seed
links); machinery re-installs fast-forward: identical files untouched,
changed ones backed up. The install also delivers `docs/graph/prose-lint.py`,
the prose gate under the `humanizer` skill, as fast-forward machinery.

## B.0 Support tiers

Source: [ADR-0009](../docs/decisions/adr-0009-host-support-tiers.md), the
Support tiers table of `documentation/host-capability-matrix.md`,
`integrations/prime-agent/README.md`, `tests/test-full-install.sh`.

- Claude Code and Prime Agent are the two first-class citizens at full
  parity: each ships a progressive-discovery enforcement hook/extension, and
  the same `agent-lint.py` passes against either harness's installed roster.
  What asserts that is `tests/test-full-install.sh`, a gate in the seed's own
  suite; `install.sh` places the linter into a plant but no workflow that runs
  it, so running it on every push is the plant's to wire (§B.8).
- opencode is the one `supported` host; Codex and GitHub Copilot are
  `frozen`: still installable by name, with a `DEPRECATED` notice, and no new
  features. All three install the same kernel, roster, and skills; commands
  reach opencode and Copilot but not Codex, which gets no command surface at
  all (the Slash commands row of `documentation/host-capability-matrix.md`).
  Each has stated gaps, documented per tool below.

## B.1 Per-tool summary table

| Tool | Kernel file (destination) | Overlay directory | Install method | First-class | Enforcement mechanism |
|---|---|---|---|---|---|
| Claude Code | `CLAUDE.md` (copy of `core/AGENTS.md`; `--symlink` opt-in) | `.claude/{agents,skills,commands}` | copy by default; commands generated | **Yes** | `.claude/route-hook.py` on `UserPromptSubmit`; `.claude/status-hook.py` on `SessionStart` |
| Prime Agent | `AGENTS.md` (copy of `core/AGENTS.md`; shared with CLAUDE.md when co-installed) | `.prime/agent/{agents,skills,prompts,extensions,hooks}` | copy by default; prompts generated | **Yes** | `.prime/agent/extensions/route-extension.ts` on `before_agent_start` and `status-extension.ts` on the session events, both running the hook core in `.prime/agent/hooks/` |
| opencode | `AGENTS.md` (or `CLAUDE.md` fallback) | `.opencode/{agents,skills,commands}` | copy by default; agents rendered with their `model:` line from the model map; `opencode.json` copied | No | Kernel FIRST-MOVE mandate (no dedicated hook shipped) |
| Codex | `AGENTS.md` at repo root | `.codex/{agents,skills}` | copy by default; global `~/.codex/config.toml` edits are user-consented | No | Kernel FIRST-MOVE mandate; skills registered in global config |
| GitHub Copilot | `.github/copilot-instructions.md` (copy) + `AGENTS.md` | `.github/{agents,prompts,instructions,hooks}` | **transform** (regenerate, not symlink) | No | `route-hook.py` + `status-hook.py` via VS Code Agent Hooks (Preview), installed only when `.claude/settings.json` is absent — VS Code reads both, and firing both would double-inject (`documentation/host-capability-matrix.md`) |

## B.2 Claude Code

Source: `integrations/claude-code/README.md`, `settings.json`, `route-hook.py`, `status-hook.py`.

Claude Code reads on every session: `CLAUDE.md` (project memory at repo root),
`.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, and `.claude/commands/*.md`.

**Mapping:**

| Seed file | Claude Code path |
|---|---|
| `core/AGENTS.md` | `CLAUDE.md` (copy by default; `--symlink` opt-in) |
| `agents/*.md` | `.claude/agents/*.md` |
| `skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` |
| protocols → slash commands | `.claude/commands/*.md` (generated) |
| `templates/` | `templates/` (kept at repo root, untouched) |
| `templates/docs/` | `docs/graph/` (missing leaves added on install) |

- **Install:** `install.sh claude-code`. `CLAUDE.md` → copy of
  `core/AGENTS.md` (`--symlink` opt-in); agents/skills → copies; commands generated
  one per protocol node with `command: true`; `docs/graph/` scaffolded. If
  `.claude/` already has custom content, the installer prompts, and conflicts
  are reported for you to resolve.
- **Enforcement:** `.claude/route-hook.py` runs on `UserPromptSubmit`, runs the
  graph router (`docs/graph/graph-lint.py --plan-json=<prompt>`) on the actual
  prompt, and injects a one-line pointer at the kernel plus the suggested node
  set in the compact lines `--plan` prints, each id beside its node file, as
  `hookSpecificOutput.additionalContext`. No line echoes the prompt. A child
  session and a turn a person did not type are not routed. A session ledger under `.cypress/session/` lets later prompts name
  already-suggested nodes by id; `status-hook.py` resets it on every
  `SessionStart` (SPEC-0003). It is fail-open (trailing `|| true`; any error
  degrades to the full injection, the pointer line, or silence, so every
  prompt goes through). The frontmatter format (`name`, `description`, `tools`,
  `model`) is exactly what Claude Code expects, so the files work unchanged.
- **Bounded execution before every shell call:** `.claude/bound-hook.py` (`PreToolUse`, matcher `Bash`) refuses a blocking-prone command that carries neither an explicit bound nor a detached launch, printing both accepted forms; it is the one hook wired without `|| true`, because a guard that cannot block is not a guard. Doctrine: `core/method/bounded-execution.md` §14, "A command that may outlive its session is bounded" (`toolcraft.bounded-execution`).
- **Status register at session start:** `.claude/status-hook.py` runs once on
  `SessionStart`, runs `docs/graph/status-register.py --summary` (a frontmatter
  scan that counts `open` / `hotfix` / `deferred` items and the oldest of them)
  and injects it as `additionalContext`, so lifecycle debt is in front of the
  model before it plans without a line in any brief. Fail-open. It ends the
  injection with the line `docs/graph/code-anchor.py --compare` prints: whether
  the code moved since canonize recorded the anchor, and which paths. That
  comparison fails toward checking instead: when it does not run or does not
  finish within 5 s, the line says code facts are unverified. No other hook
  runs the anchor. What any
  hook carries into a subagent's turn is recorded in
  `docs/graph/method/delegation-briefs.md` (`delegation.briefs`).
- **Known gap / sharp edge:** a roster written mid-session (by an install,
  graft, or freshly commissioned expert) can be on disk and not yet
  spawnable, and a session rooted at the seed never carries a plant's
  roster. When the host registers such a file, the preflight, the remedy,
  and the recorded fallback are owned by `docs/graph/method/delegation-bounds.md`
  (`delegation.harness-registration`).

## B.3 Prime Agent

Source: `integrations/prime-agent/README.md`, `settings.json`,
`route-extension.ts`, `status-extension.ts`, `APPEND_SYSTEM.md`.

Prime Agent is an RLM-native harness built around a persistent IPython kernel,
recursive subagents (`rlm.spawn()`), durable sessions, and a continual-harness state
ledger. Discovery (verified against prime-agent 0.8.1): context files
(`AGENTS.md` or `CLAUDE.md`, auto-loaded and concatenated), prompt templates
(`.prime/agent/prompts/<name>.md`), skills (`.prime/agent/skills/<name>/
SKILL.md`), extensions (`.prime/agent/extensions/*.ts`), and settings
(`.prime/agent/settings.json` overriding global).

**Mapping:**

| Seed file | Prime Agent path |
|---|---|
| `core/AGENTS.md` | `AGENTS.md` (copy by default; `--symlink` opt-in) |
| `agents/*.md` | `.prime/agent/agents/*.md` (brief sources) |
| `skills/*/SKILL.md` | `.prime/agent/skills/*/SKILL.md` |
| protocols → slash commands | `.prime/agent/prompts/*.md` (generated projections) |
| route and status enforcement | `.prime/agent/extensions/{route,status}-extension.ts` |
| `integrations/claude-code/{route,status}-hook.py` | `.prime/agent/hooks/` (the hook core the extensions run) |
| `templates/docs/` | `docs/graph/` (missing leaves added on install) |

- **Install:** `install.sh prime-agent`. `AGENTS.md` → `core/AGENTS.md`; roster
  briefs, skills, generated prompts, the two extensions and the hook core they
  run, `settings.json`, and `APPEND_SYSTEM.md` are placed; `docs/graph/` scaffolded. Prime Agent has
  no static roster/protocol/template tool-dirs; it is graph-only (the test
  asserts `.prime/agent/protocols` and `.prime/agent/templates` do not exist).
- **Enforcement:** `route-extension.ts` subscribes to `before_agent_start` and
  runs `route-hook.py`, the core Claude Code runs, from `.prime/agent/hooks/`,
  with the prompt, the session id and the session depth. The core decides
  everything and keeps the session ledger, so a node this session was already
  shown is named by id, not injected again; a child session and a turn a
  person did not type are not routed. `status-extension.ts` runs
  `status-hook.py` on `session_start`, `session_compact`, `session_tree` and
  `refine_complete`, and injects `status-register.py --summary` and the
  code-anchor line on the next prompt of that session, once; that is the parity
  of Claude Code's `SessionStart` hook. Both are fail-open and auto-discovered
  from `.prime/agent/extensions/` (`settings.json` also lists them for
  locked-down configs). Without the extensions, the kernel's FIRST MOVE is the
  floor: the session runs `graph-lint.py --plan` itself.
- **Delegation advantage (no registration lag):** Prime Agent has no
  session-start roster enumeration. Delegation is a runtime primitive
  (`await rlm.spawn("<brief>", name=...)`); the `agents/*.md` install as
  **brief sources** the orchestrator reads and passes into the `rlm.spawn()` call. The "installed but not
  spawnable" trap therefore does not exist here: the recorded
  `delegation.harness-registration` fallback is the normal path.
- **Native-execution overlay:** `.prime/agent/APPEND_SYSTEM.md` is appended to
  the system prompt every session (Claude Code never reads it). It maps the
  kernel's discipline onto Prime Agent primitives (fan-out `rlm.spawn()` delegation,
  a model policy that reads each class's model from the plant's model map,
  `docs/graph/models.md`, kernel-run gates, canonize + continual-harness close-out,
  nonblocking `goal` / `rlm_heartbeat` loops). A project can edit it; a global
  `~/.prime/agent/APPEND_SYSTEM.md` is superseded inside the plant.
- **settings.json:** lists only the seed's own resource dirs with bare
  relative names (`extensions`, `skills`, `prompts`), resolved against
  `.prime/agent/`; a `.prime/agent/...` prefix would double-nest. No
  `instructions` key (the kernel auto-loads via the context-file walk).
- **Known gap (recursion depth):** `RLM_MAX_DEPTH` (default 2) is a
  global/session/env dial and is not settable from project `settings.json`:
  `getRlmMaxDepth()` reads global settings only, so a committed value is
  silently ignored (`rlmMaxDepth` in project settings is rejected by the CI
  test). Default depth-2 work runs unchanged; to reach the seed's deepest chain
  (`max_spawn_depth: 3`: orchestrator → multi-agent-architect → architect →
  leaf) raise it by `/rlm-max-depth 3`, `~/.prime/agent/settings.json`
  `{ "rlmMaxDepth": 3 }`, or `RLM_MAX_DEPTH=3`.

## B.4 opencode

Source: `integrations/opencode/README.md`, `opencode.json`.

opencode reads `AGENTS.md` (its preferred filename) or `CLAUDE.md` as fallback,
`.opencode/agents/*.md`, `.opencode/commands/*.md`,
`.opencode/skills/<name>/SKILL.md` (with `.claude/skills/` fallbacks), and
`opencode.json`. All directory locations are discovered by convention; the
schema rejects unknown keys (`additionalProperties: false`). opencode is
Claude-Code-compatible by default, so a Claude Code project already works in it.

**Mapping:** `core/AGENTS.md` → `AGENTS.md`; `agents/*.md` →
`.opencode/agents/*.md`; `skills/*/SKILL.md` → `.opencode/skills/*/SKILL.md`;
protocols → `.opencode/commands/*.md`; `templates/docs/` → `docs/graph/`.

- **Install:** `install.sh opencode`. Symlinks (copies on Windows); commands
  generated; `opencode.json` copied (not symlinked) so the project can edit
  it; `docs/graph/` scaffolded.
- **Enforcement:** no dedicated hook is shipped. The kernel's FIRST-MOVE
  mandate is the route-first floor.
- **`opencode.json`** is deliberately almost empty:
  `{"$schema": "https://opencode.ai/config.json", "subagent_depth": 3}`.
  `subagent_depth: 3` is the load-bearing key: opencode defaults it to 1
  ("prevents subagents from launching subagents"), which collapses the seed's
  depth-3 delegation chain. The value must equal the highest `max_spawn_depth`
  in `agents/*.md`; `tests/seed-lint.py` enforces that the two agree. Only one
  config file ships (`opencode.json`, never a `.jsonc` twin), because with both
  present the winner is unspecified.
- **Known gap (Claude-Code-shaped frontmatter):** opencode's markdown-agent
  contract is not a superset of Claude Code's. Two seed fields are read
  differently:

  | seed frontmatter | opencode expects | consequence today |
  |---|---|---|
  | `model: opus` / `model: sonnet` | `provider/model` | the installer writes each agent's `provider/model` from the plant's model map, `docs/graph/models.md`; with no map row the projected agent has no `model:` line and runs on its caller's model |
  | `tools: [Read, Glob, Grep, Bash]` (list) | `permission: {edit: deny, bash: deny}` (`tools` object deprecated) | a read-only leaf's tool bound is not enforced by the harness |

  Neither is fixable in `opencode.json`. The `model:` line is a transformed
  projection: `install.sh opencode` renders each agent with it, and
  `install.sh opencode --check` compares the placed projections with a fresh
  rendering ([ADR-0022](../docs/decisions/adr-0022-the-plant-model-map.md);
  `integrations/opencode/README.md`, "Model choice comes from the plant's model
  map"). The leaf tool bound stays brief-enforced on opencode, per
  `delegation.harness-registration`.

## B.5 Codex (OpenAI Codex CLI)

Source: `integrations/codex/README.md`, `config.toml.example`.

Codex reads `AGENTS.md` files (walking up to the project root, merging
top-down), fallback filenames from `~/.codex/config.toml`, skills registered
via `[[skills.config]]`, and subagent config via the `[agents]` section, both
in global `~/.codex/config.toml`. Codex does not support `.claude/`-style
subagent directories out of the box; project-local agents are surfaced by
referencing them from `AGENTS.md`.

**Mapping:** `core/AGENTS.md` → `AGENTS.md` at repo root (sub-agents inlined or
referenced); `agents/*.md` → `.codex/agents/*.md`; protocols install once,
as graph nodes → `docs/graph/protocols/*.md` (no `.codex/` copy);
`skills/*/SKILL.md` → `.codex/skills/*/SKILL.md`
(registered in `~/.codex/config.toml`); `templates/docs/` → `docs/graph/`.

- **Install:** `install.sh codex`. Copies by default; prints a reminder of the
  `~/.codex/config.toml` lines to add for skill registration (the installer
  does not modify global user config without consent). `install.sh codex
  --print-config` prints the snippet with paths substituted.
- **Enforcement:** no dedicated hook. Kernel FIRST-MOVE mandate is the floor.
  Approval modes: `untrusted`, `on-request`, `never`; the `verify` protocol
  needs the agent to run gate commands, so pick `on-request` (interactive) or
  `never` (non-interactive CI with a hardened sandbox).
- **Known gaps:**
  - **AGENTS.md size budget:** Codex truncates `AGENTS.md` at
    `project_doc_max_bytes` (default 32 KiB). The seed's `AGENTS.md` is
    intentionally short; its size is whatever [`core/AGENTS.md`](../core/AGENTS.md)
    measures, and the byte budget it sits under is soft, checked only in the
    seed's own gate ([kernel-budget row](../DOCUMENTATION.md#enf-kernel-budget)).
    Depth lives in referenced files. Do not paste
    agent/protocol bodies into `AGENTS.md`. Raise via
    `project_doc_max_bytes = 65536` if needed.
  - **Skills not auto-discovered:** each must be listed one `[[skills.config]]`
    entry at a time in global config.
  - **Registration lag:** installed agents and the global-config merge both
    land after the current session began, so nothing is addressable until a new
    session (`delegation.harness-registration` owns the rule and fallback).

## B.6 GitHub Copilot (VS Code & GitHub.com)

Source: `integrations/github-copilot/README.md`.

Copilot reads several customization layers, each with its own format:
repository instructions (`.github/copilot-instructions.md` or `AGENTS.md`),
path-scoped instructions (`.github/instructions/<name>.instructions.md` with an
`applyTo:` glob), prompt files (`.github/prompts/<name>.prompt.md`), and custom
agents (`.github/agents/<name>.agent.md`).

**Mapping:**

| Seed file | Copilot destination |
|---|---|
| `core/AGENTS.md` | `.github/copilot-instructions.md` (copy) |
| `core/AGENTS.md` | `AGENTS.md` at repo root (Copilot also reads this) |
| `agents/*.md` | `.github/agents/*.agent.md` (transformed) |
| `skills/*/SKILL.md` | `.github/instructions/*-skill.instructions.md` (transformed) |
| `protocols/*.md` | `.github/prompts/*.prompt.md` (transformed) |
| `templates/docs/` | `docs/graph/` (missing leaves added on install) |

- **Install method:** transform. Copilot's discovery is filename-driven and
  its formats are incompatible (different frontmatter keys, different folder
  expectations), so `install.sh github-copilot` regenerates transformed copies
  instead of symlinking the source files. The source of truth stays the
  universal files; re-run the installer after editing any source. The toolset is derived per agent from
  its own `tools:` allowlist (see integrations/github-copilot/README.md for
  the exact mapping); `model:` and `Task` are not projected, because Copilot
  has no subagent spawning, so coordinator delegation degrades to the single
  session there.
- **Enforcement (Agent Hooks, Preview):** the same cross-tool `route-hook.py`
  runs on `UserPromptSubmit`, emits JSON (`hookSpecificOutput.
  additionalContext`; plain-text stdout is not injected by Copilot), and its
  command uses `${CLAUDE_PROJECT_DIR:-$PWD}`, which Copilot, not setting the
  variable, resolves to `$PWD`, so it resolves in both hosts. VS Code reads `.claude/settings.json` hooks directly,
  so a project with the Claude Code install picks up the same hook with nothing
  extra; a Copilot-only install drops `.github/hooks/route.json` +
  `.github/hooks/route-hook.py` (and `status.json` + `status-hook.py` for the
  session-start status register). Do not keep both configs, or the hook fires
  twice. The generated `.github/copilot-instructions.md` also leads with the
  FIRST-MOVE mandate, so route-first holds even without hooks enabled.
- **Known gaps:** Agent Hooks are Preview (format may change). A regenerated
  `.github/agents/*.agent.md` does not appear in the picker of the session that
  regenerated it (registration lag; `delegation.harness-registration`). If
  `.github/copilot-instructions.md` already exists, the installer backs it up
  (`.bak-<timestamp>`), writes the kernel, and prints a diff to merge back. For
  multi-root workspaces enable `chat.useCustomizationsInParentRepositories`. A
  weak local model may still skip the injected context; the hook guarantees the
  context is present, not that the model reasons over it.

## B.7 The interchangeable Claude-Code + Prime-Agent shared kernel

Source: `integrations/prime-agent/README.md` § "Interchangeable with Claude
Code in one plant", `tests/test-full-install.sh`.

A single plant is meant to run either Claude Code or Prime Agent,
interchangeably, off the same project knowledge. Install both in one command or
two, in any order:

```
/path/to/cypress/install.sh claude-code prime-agent
```

What that gives:

- **One shared kernel, no drift.** Claude Code reads `CLAUDE.md`; Prime Agent
  reads `AGENTS.md` (it wins over `CLAUDE.md` in a directory). The installer
  collapses the two to a single source of truth: the first placed is the
  real file, the second a project-local relative symlink to it (`AGENTS.md
  -> CLAUDE.md` or the reverse, by install order). Editing the kernel updates
  both harnesses at once. On a platform without symlinks the second file
  degrades to an independent copy (identical at install; keep in sync by hand).
- **Parallel harness trees, no collision.** `.claude/{agents,skills,commands}`
  and `.prime/agent/{agents,skills,prompts,extensions}` sit side by side; each
  harness reads only its own. The roster, skills, and command set are the same
  because both are projections of the same `docs/graph/` nodes.
- **One shared knowledge graph.** `docs/graph/` is installed once and read by
  both.
- **Enforcement per session type.** A Claude Code session fires
  `.claude/route-hook.py` (`UserPromptSubmit`) and `.claude/status-hook.py`
  (`SessionStart`); a Prime Agent session fires
  `.prime/agent/extensions/route-extension.ts` and `status-extension.ts`,
  which run the same two scripts from `.prime/agent/hooks/`. They run in
  different session types, so there is no double-firing.

Switching harness is just opening the plant in the other tool, with nothing to
re-install and nothing to reconcile.

## B.8 The parity gate (seed-local)

Source: `tests/test-full-install.sh` (run via `bash tests/run.sh`).

`tests/test-full-install.sh` is the gate that makes Prime Agent a first-class
citizen and not a doc-only integration. It runs in the seed's own suite
(`bash tests/run.sh`), against a throwaway install — it is not a workflow any
plant receives. It asserts:

- **The SAME `agent-lint.py` runs on Prime Agent's installed roster.** The test
  runs `integrations/claude-code/agent-lint.py --lint --dir <T>/.prime/agent/
  agents` and `--eval --dir <T>/.prime/agent/agents`. `--dir` bypasses the
  `.claude/agents` assumption, pointing the *same* linter at the brief-source
  roster. Passing both `--lint` (frontmatter validity) and `--eval` (golden
  routing set) is the parity proof.
- **The golden routing corpus is byte-identical across projections.**
  `.prime/agent/agents/_routes.golden.tsv` must `cmp` equal to the one home
  `agents/_routes.golden.tsv`, with no drift.
- **Prime Agent is graph-only.** `.prime/agent/protocols` and
  `.prime/agent/templates` must not exist (stale-dir check).
- **settings.json hygiene.** Valid JSON; resource entries use bare relative
  names (no `.prime/` prefix, which would double-nest); `rlmMaxDepth` must not
  appear in project settings (it is silently ignored, so shipping it is a bug).
- **Coexistence in both orders.** For `claude-code prime-agent` and
  `prime-agent claude-code`, the test asserts both `CLAUDE.md` and `AGENTS.md`
  exist and are identical, exactly one of them is a symlink (the single
  source of truth), that symlink's target is the project-local sibling basename
  (not into the seed), both harness roster roots exist
  (`.claude/agents/00-orchestrator.md`, `.prime/agent/agents/00-orchestrator.md`),
  both enforcement files exist (`.claude/route-hook.py`,
  `.prime/agent/extensions/route-extension.ts`), and the shared
  `docs/graph/index.md` exists. Both install orders must converge.

The broader gate is `bash tests/run.sh`: every shell suite under `tests/`,
plus agent-lint lint/eval, graph/agent-lint regressions, `seed-lint.py`, and
`legal-lint.py`. The suite count moves as suites are added — read
`tests/run.sh` for the current roster rather than a number restated here.

---

## Source files cited

- Corpora READMEs: `library-corpus/README.md`, `legal-corpus/README.md`,
  `legal-corpus/index.md`, `legal-corpus/_schema.md`,
  `legal-corpus/case-law/index.md`, `tool-corpus/README.md`,
  `agent-corpus/README.md`, `skill-corpus/README.md`.
- The legal agent: `agents/14-legal.md` (the base-roster agent).
- Harvest / withdraw contract: `protocols/harvest.md`, `HARVEST_PROMPT.md`.
- Kernel economy / gates / conventions: `CLAUDE.md`.
- Integrations: `integrations/{claude-code,prime-agent,opencode,codex,
  github-copilot}/README.md` and their config files
  (`settings.json`, `opencode.json`, `config.toml.example`), `route-hook.py`,
  `status-hook.py`, `route-extension.ts`, `status-extension.ts`, `APPEND_SYSTEM.md`.
- Overview and parity: `README.md`, `INSTALL.md`, `tests/test-full-install.sh`.
