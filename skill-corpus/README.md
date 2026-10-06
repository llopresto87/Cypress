# Skill corpus: suggested skills

**Project-agnostic, durable, optional procedures**, the procedure mirror of
`agent-corpus/` (roles) and `tool-corpus/` (artifacts), and of the reference
corpora `library-corpus/` and `legal-corpus/`. A procedure here is withdrawn by `grow` and
`toolcraft` when a project needs it; a stack-keyed page can also be placed with
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
`docs/graph/skills/<name>.md`. Each page opens with an optional-procedure
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
    `triage-unresolved-required-variable`, `third-party-handover`.
  - Declarative infrastructure and devices: `add-infrastructure-object-safely`,
    `provision-records-from-unstructured-input`,
    `characterize-undocumented-device-protocol`,
    `genericize-config-to-examples`.
  - Security: `fleet-security-review`, `adversarial-pentest-passes`,
    `vulnerability-reduction-by-version-bumps`,
    `residual-finding-exploitability-judgment`, `discardme` (the throwaway
    review packet for a substantial security or compliance fix).
  - Data for review: `seed-demo-world-for-manual-ui-review`.
  - Agents and process: `evolve-agent-charter`, `unit-of-work-retrospective`.
- Stack-keyed:
  - `maven`: `spring-boot-major-line-upgrade`, `offline-legacy-build-harness`.
  - `npm`: `angular-major-upgrade`.
  - `nuget`: `dotnet-integration-test-harness`.
  - `pub`: `local-android-demo-build`.
  - `pypi`: `converge-records-over-http-api`.
  - `platform`: `drive-azure-pipelines-cli`.

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
- **It carries node frontmatter**, so the selective placement (SPEC-0001 §6)
  can place it as a routable skill node at `docs/graph/skills/<name>.md`:

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
stack:
  - library-corpus/<key>/<library>
est_tokens: <honest estimate>
---
```

The page carries no `origin:`; the installer writes `origin: corpus@<seed
version>` when it places the page. `stack:` lists one or more library-corpus
ids, and the presence of any of them in a plant's inventory is what makes the
page a candidate to withdraw. `python3 tests/seed-lint.py` fails a keyed page
whose key the library corpus does not define, a keyed page with no `stack:`, a
flat page with one, and a `stack:` entry that names no library-corpus page.

## The withdraw contract (consumed by `grow`, `toolcraft` and commission)

`protocols/harvest.md` ("The suggested-skill corpus") owns this contract: when
a project hits a repeatable procedure the core `skills/` don't cover, check
this corpus first, and instantiate a match into the project's
`docs/graph/skills/<name>.md` (its home) from
`docs/graph/templates/skill.template.md`. A stack-keyed page is a match only
when the plant's inventory declares a library its `stack:` names. If none
matches, author it fresh as a project skill; its durable, agnostic form becomes
a harvest candidate.
