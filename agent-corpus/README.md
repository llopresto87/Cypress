# Agent corpus — suggested experts

**Project-agnostic, durable, optional expert roles** — the roster mirror of
`skill-corpus/` (procedures) and `tool-corpus/` (artifacts), and of the
reference corpora `library-corpus/` and `legal-corpus/`. Folded back into the
seed by the **harvest** protocol
(`protocols/harvest.md`, `HARVEST_PROMPT.md`) from roles that grown plants found
generally useful, and withdrawn by `grow` / `graft` (or the orchestrator's
commission step) when a specific project needs a role, rather than the
expertise node a knowledge gap closes as.

## Purpose

The always-loaded team lives in `agents/`, is named in the kernel §1 table, and
**every plant pays its per-session cost**. That economy is why a harvested role
lands here instead: this corpus is a **catalog of candidates** — roles a project
*may* select, none loaded by default, none named in the kernel. It gives the
same role one stable home so it is not reinvented per project, and gives harvest
somewhere to deposit a generic foreign role without touching the kernel budget
or the one-home-per-fact roster. Each page is instantiated through the withdraw
contract below; a page states only its role.

## What belongs here (role, durable)

- A **role**: its mandate, when to select it, and how it bounds against the base
  roster, statable with **zero framework names**.
- Its `routing_triggers` exemplars (intent-phrased task cues) so a project's
  router can match it once selected.

The page shape follows from these: an optional-role blockquote, `Mandate`,
`When to select`, `Boundary (does not duplicate the base roster)`,
`routing_triggers (exemplars)`.

## What stays OUT

- **Stack-specific experts** (a framework/language/library specialist, any
  mandate that needs a language or framework name) — those are the plant's own,
  and are usually not an agent at all: knowing a stack is knowledge, so it
  closes as an `expertise.*` node authored against the plant's own pins, which
  the router composes into the roster the plant already has.
- **Roles that duplicate the base roster's mandate** (e.g. "a security role",
  "a testing role") — one home per role; extend the existing agent instead.

## Layout

```
agent-corpus/<name>.md
```

One page per suggested role, kebab-case id. Categories may be introduced as
subdirectories when the catalog grows.

## The withdraw contract (consumed by `grow` / `graft` / commission)

`protocols/harvest.md` ("The suggested-expert corpus") owns this contract:
check this corpus first when a project needs a specialist the base roster
lacks, and instantiate a match into the project's `docs/graph/agents/` from
`docs/graph/templates/agent.template.md`. The selected role joins the project's
roster (and its kernel table / manifest); this catalog keeps only candidates.
