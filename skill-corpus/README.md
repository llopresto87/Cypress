# Skill corpus — suggested skills

**Project-agnostic, durable, optional procedures** — the procedure mirror of
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
- Stated by **composing** the protocols, skills and agents it runs under, by
  reference, so each discipline, and the rules of the agent a procedure runs
  under, keep their one home. A page names what it composes and states only its
  own steps.
- Recurring across **independent** project lineages.

## What stays OUT

- A procedure bound to one stack or one repo's layout — the plant's own,
  authored fresh.

## Layout

```
skill-corpus/<name>.md
```

One page per suggested procedure, kebab-case id, describing the skill in
general (orientation to instantiate, not the plant's copy). Each page opens
with an optional-procedure blockquote naming what it composes and its
parameters, then `When to apply`, the procedure itself, and `Reference files`.
Each step names the move it replaces, and a hard boundary sits, paired with its
right move, in the step that owns it.

## The withdraw contract (consumed by `grow` / `toolcraft` / commission)

`protocols/harvest.md` ("The suggested-skill corpus") owns this contract: when
a project hits a repeatable procedure the core `skills/` don't cover, check
this corpus first, and instantiate a match into the project's
`docs/graph/skills/<name>.md` (its home) from
`docs/graph/templates/skill.template.md`. If none matches, author it fresh as a
project skill; its durable, agnostic form becomes a harvest candidate.
