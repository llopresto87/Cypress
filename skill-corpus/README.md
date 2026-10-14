# Skill corpus: suggested skills

**Project-agnostic, durable, optional procedures**, the procedure mirror of
`agent-corpus/` (roles) and `tool-corpus/` (artifacts), and of the reference
corpora `library-corpus/` and `legal-corpus/`. A procedure here is withdrawn by `grow` and
`toolcraft` when a project needs it, and every page carries node frontmatter
(below), so any of them can also be placed with
`install.sh <host> --expertise <id>`. New pages enter through the **harvest**
protocol (`protocols/harvest.md`).

## Purpose

A skill is a **procedure**: the disciplined sequence for doing a recurring kind
of work well. An *agent* is a role (who does the work) and a *tool* is an
artifact (code that runs). The seed's `skills/` holds the fixed **core
methodology** every plant inherits (planning, spec-authoring, test-first,
ADR-writing, and the rest). This corpus holds the **optional** procedures a
project may or may not need (a migration recipe, a data-reset dance, a release
choreography), so the next plant instantiates a ready sequence instead of
rediscovering it.

## What belongs here (procedure, durable)

- A procedure statable with **no plant identity** (no project name, domain
  noun, path, host, or credential) whose steps each name the gate they clear.
  Naming a widely portable substrate is fine when that substrate *is* the
  procedure's subject (a container runtime, an SSH transport); what disqualifies
  a page is binding to one repo's layout or one project's pins. (A *role* is
  held to the stricter bar of `agent-corpus/README.md`.)
- A **stack-bound** procedure, at a stack key (below): one that only makes
  sense on a given library, framework or platform, such as an upgrade across a
  framework's major lines, provided it still holds no plant identity.
- Stated by **composing** the protocols, skills and agents it runs under, by
  reference, so each discipline, and the rules of the agent a procedure runs
  under, keep their one home. A page names what it composes and states only its
  own steps.
- Recurring across **independent** project lineages.
- Complete: a page lands only when a plant can run the procedure from the page
  alone, the procedure form of the withdraw-ready bar (`tool-corpus/README.md`,
  "The withdraw-ready bar for a procedure or a tool"; the bar itself is
  `library-corpus/README.md`'s).

## What stays OUT

- A procedure bound to one repo's layout or one project's pins: the plant's
  own, authored fresh.
- A security fact (a CVE id, an advisory, an exposure warning), a calendar date,
  or a project's own version. A version fact the library's release notes or docs
  state, written with the step it qualifies (the minimum version a step needs,
  the line an upgrade page carries its subject across, a version where a step's
  behaviour changes), is admissible, as in the library corpus
  (`library-corpus/README.md`, "What stays OUT" and "A major line is not a
  pin").

## Layout

```
skill-corpus/<name>.md          a generic procedure
skill-corpus/<key>/<name>.md    a stack-keyed procedure
```

One page per suggested procedure, kebab-case id, describing the skill in
general (orientation to instantiate, not the plant's copy). `<name>` is unique
across the whole corpus, keys included, because a placed page lands at
`docs/graph/skills/<name>.md`, whichever form its id takes: `skill-corpus/<name>`
for a generic page, `skill-corpus/<key>/<name>` for a stack-keyed one. Each page
opens with its node frontmatter (below), then an optional-procedure
blockquote naming what it composes and its parameters, then `When to apply`,
the procedure itself, and `Reference files`. Each step names the move it
replaces, and a hard boundary sits, paired with its right move, in the step
that owns it.

Currently populated:

- Flat, by the kind of work:
  - Test-first and verification: `deploy-gated-red-green`,
    `mutation-verify`, `prove-red-after-green`.
  - Migration and legacy recovery: `framework-version-migration`,
    `vendor-dependency-from-dead-registry`.
  - Delivery and hosts: `deploy-fleet-on-remote-docker-host`,
    `harden-docker-host`, `same-origin-web-edge`, `drive-hosted-cicd-cli`,
    `live-patch-stopgap`, `release`, `operator-compressed-fix-path`,
    `triage-unresolved-required-variable`, `dead-hostname-audit`,
    `third-party-handover`.
  - Declarative infrastructure and devices: `add-infrastructure-object-safely`,
    `provision-records-from-unstructured-input`,
    `characterize-undocumented-device-protocol`,
    `genericize-config-to-examples`.
  - Security: `fleet-security-review`, `adversarial-pentest-passes`,
    `vulnerability-reduction-by-version-bumps`,
    `residual-finding-exploitability-judgment`.
  - Review reports: `change-review-report` (the self-contained report a
    reviewer accepts or rejects a substantial change from without reading the
    diff, discarded on acceptance unless the plant must keep review evidence).
  - Data for review and rendering: `seed-demo-world-for-manual-ui-review`,
    `review-rendered-ui`.
  - Agents and process: `evolve-agent-charter`, `unit-of-work-retrospective`.
- Stack-keyed:
  - `maven`: `spring-boot-major-line-upgrade`, `offline-legacy-build-harness`.
  - `npm`: `angular-major-upgrade`.
  - `nuget`: `dotnet-integration-test-harness`.
  - `pub`: `local-android-demo-build`.
  - `pypi`: `converge-records-over-http-api`.
  - `platform`: `drive-azure-pipelines-cli`.
  - `galaxy`: `managed-edge-read-only-triage`, `shared-line-qos-design`.

## Node frontmatter

Every page, generic or stack-keyed, opens with this block, so the selective
placement (SPEC-0001 §6) can place it as a routable skill node at
`docs/graph/skills/<name>.md`. The installer refuses a page without it by
name, before it writes anything:

```yaml
---
name: <name>
description: <one line: the procedure, and the exact triggers that invoke it>
id: skill.<name>
tier: 2
kind: skill
title: <name>, <one-line description>
owns:
  - <name>.<fact>
requires:
load_when:
  - "<the phrase a developer would type>"
prevents: <the failure a plant meets without the procedure>
stack:
  - library-corpus/<key>/<library>
est_tokens: <measured: the file's bytes over four>
---
```

- `owns:` keys are unique across the seed and every corpus, so a placed page
  never contests a fact another node owns.
- `load_when:` holds the phrases a plant session types when it needs the
  procedure, with no plant name in them; the plant's router matches a task
  against them.
- `prevents:` names the failure its absence produces, not the title again.
- `est_tokens:` is measured, not guessed: a placed node whose figure is not
  within twice the plant's own word count measure fails its `graph-lint.py`.
- `stack:` is a stack-keyed page's alone (below); a generic page omits it.
- A page the owner must start by name, because a router that selected it
  would start a gated change from a passing phrase, says so in its
  `description`, holds its own name in every `load_when:` phrase, and adds
  `disable-model-invocation: true`, the manual-only flag Claude Code reads.

The page carries no `origin:`; the installer writes `origin: corpus@<seed
version>` when it places the page, generic or keyed.

## Stack-keyed pages

A stack-keyed page lives at `skill-corpus/<key>/<name>.md`, where `<key>` is a
`library-corpus/` key (`maven`, `npm`, `pub`, `galaxy`, `platform`, and the rest
that README lists). Three things hold for it:

- **It specializes by reference.** When a generic page covers the procedure in
  general (`framework-version-migration.md` for an upgrade), the keyed page
  names it and adds only the steps the stack needs; it never restates the
  generic page.
- **It holds no plant identity.** The stack is its subject; a project, a host,
  a path or a pin is not.
- **It names its stack.** Its node frontmatter adds `stack:`, one or more
  library-corpus ids, and the presence of any of them in a plant's inventory
  is what makes the page a candidate to withdraw. `python3 tests/seed-lint.py`
  fails a keyed page whose key the library corpus does not define, a keyed
  page with no `stack:`, a flat page with one, and a `stack:` entry that names
  no library-corpus page.

## The withdraw contract (consumed by `grow`, `toolcraft` and commission)

`protocols/harvest.md` ("The suggested-skill corpus") owns this contract: when
a project hits a repeatable procedure the core `skills/` don't cover, check
this corpus first, and instantiate a match into the project's
`docs/graph/skills/<name>.md` (its home) from
`docs/graph/templates/skill.template.md`. A stack-keyed page is a match only
when the plant's inventory declares a library its `stack:` names. If none
matches, author it fresh as a project skill; its durable, agnostic form becomes
a harvest candidate. No manifest proposes a generic page: grow and graft place
one when the plant's work needs the procedure, by listing its id
(`--expertise skill-corpus/<name>`), and the stamp's `expertise` record then
keeps it refreshed like a keyed page.
