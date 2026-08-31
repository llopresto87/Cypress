# Agent corpus — suggested experts

**Project-agnostic, durable, OPTIONAL expert roles** — the roster mirror of
`skill-corpus/` (procedures) and `tool-corpus/` (artifacts), and of the
reference corpora `library-corpus/` and `legal-corpus/`. Folded back into the
seed by the **harvest** protocol
(`protocols/harvest.md`, `HARVEST_PROMPT.md`) from roles that grown plants found
generally useful, and withdrawn by `grow` / `graft` (or the orchestrator's
commission step) when a specific project decides it needs one.

## Purpose

The always-loaded team lives in `agents/`, is named in the kernel §1 table, and
**every plant pays its per-session cost**. That economy is why a harvested role
lands here instead: this corpus is a **catalog of candidates** — roles a project
*may* select, none loaded by default, none named in the kernel. It gives the
same role one stable home so it is not reinvented per project, and gives harvest
somewhere to deposit a generic foreign role without touching the kernel budget
or the one-home-per-fact roster.

## What belongs here (role, durable)

- A **role**: its mandate, when to select it, and how it bounds against the base
  roster — statable with **zero framework names**. If you cannot define the
  mandate without naming a language or framework, it is a stack-specific expert
  (plant flesh) and does not belong here.
- Its `routing_triggers` exemplars (intent-phrased task cues) so a project's
  router can match it once selected.

Those four elements are also the page shape every entry in this catalog
follows: an optional-role blockquote, `Mandate`, `When to select`, `Boundary
(does not duplicate the base roster)`, `routing_triggers (exemplars)`.

## What stays OUT

- **Stack-specific experts** (a framework/language/library specialist) — those
  are the plant's own, commissioned fresh against its pins.
- **Roles that duplicate the base roster's mandate** (e.g. "a security role",
  "a testing role") — one home per role; extend the existing agent instead.

## Layout

```
agent-corpus/<name>.md
```

One page per suggested role, kebab-case id. Categories may be introduced as
subdirectories when the catalog grows.

## The withdraw contract (consumed by `grow` / `graft` / commission)

`protocols/harvest.md` owns this contract. In short: when a project needs a
specialist the base roster lacks, check this corpus **first**. A matching role
is instantiated into the project's `docs/graph/agents/` (the harness
projections — `.claude/agents/` and kin — are regenerated from it) from
`docs/graph/templates/agent.template.md`, grounded in the project's
version-pinned facts (its `stack.*` node, `docs/graph/libraries/`) and the
page's mandate + `routing_triggers`. No match ⇒ commission one fresh, and its
durable, agnostic mandate becomes a harvest candidate for the next cycle.
Either way the selected role joins the *project's* roster (and its kernel table
/ manifest) — never this catalog.
