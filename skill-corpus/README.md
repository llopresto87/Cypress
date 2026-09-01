# Skill corpus — suggested skills

**Project-agnostic, durable, OPTIONAL procedures** — the procedure mirror of
`agent-corpus/` (roles) and `tool-corpus/` (artifacts), and of the reference
corpora `library-corpus/` and `legal-corpus/`. Folded back into the seed by the
**harvest** protocol (`protocols/harvest.md`, `HARVEST_PROMPT.md`) from
procedures a grown plant authored that generalize, and withdrawn by `grow` /
`toolcraft` when a project needs the same procedure.

## Purpose

A skill is a **procedure** — the disciplined sequence for doing a recurring kind
of work well — as opposed to an *agent* (a role: who does the work) or a *tool*
(an artifact: code that runs). The seed's `skills/` holds the fixed **core
methodology** every plant inherits (planning, spec-authoring, test-first,
ADR-writing, …). This corpus holds the **optional** procedures a project may or
may not need — a migration recipe, a data-reset dance, a release choreography —
so the next plant instantiates a ready sequence instead of rediscovering it.

## What belongs here (procedure, durable)

- A procedure statable with **no plant identity** — no project name, domain
  noun, path, host, or credential — whose steps each name the gate they clear.
  Naming a widely-portable substrate is fine when that substrate *is* the
  procedure's subject (a container runtime, an SSH transport); what disqualifies
  a page is binding to one repo's layout or one project's pins. (A *role* is
  held to the stricter bar — see `agent-corpus/README.md`.)
- Stated by **composing** the existing protocols/skills/agents it runs under,
  by reference — never restating a discipline the seed already owns.
- Recurring across **independent** project lineages.

## What stays OUT

- A procedure bound to one stack or one repo's layout — the plant's own,
  authored fresh.
- Anything duplicating a core `skills/` discipline, or restating the rules of
  the agent it runs under: one home per procedure.

## Layout

```
skill-corpus/<name>.md
```

One page per suggested procedure, kebab-case id, describing the skill in
general (orientation to instantiate, not the plant's copy). Each page opens
with an optional-procedure blockquote naming what it composes and its
parameters, then `When to apply`, the procedure itself, `Anti-patterns`, and
`Reference files`.

## The withdraw contract (consumed by `grow` / `toolcraft` / commission)

`protocols/harvest.md` owns this contract. In short: when a project hits a
repeatable procedure the core `skills/` don't cover, check this corpus
**first**. A matching page is instantiated into the project's
`docs/graph/skills/<name>.md` — its home — from
`docs/graph/templates/skill.template.md`, and the projection is then created
in each harness dir the plant actually uses (`.claude/skills/<name>/SKILL.md`
and kin), because `install.sh` projects only the seed's own skills,
grounding its steps in the project's real gates and tools. If none matches,
author it fresh as a project skill — and its durable, agnostic form becomes a
harvest candidate for the next cycle.
