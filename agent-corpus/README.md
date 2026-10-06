# Agent corpus: suggested experts

**Project-agnostic, durable, optional expert roles**, the roster mirror of
`skill-corpus/` (procedures) and `tool-corpus/` (artifacts), and of the
reference corpora `library-corpus/` and `legal-corpus/`. A role here is
withdrawn by `grow` and `graft` (or the orchestrator's commission step) when a specific project
needs a role, and not the expertise node a knowledge gap closes as. New pages
enter through the **harvest** protocol (`protocols/harvest.md`).

## Purpose

The always-loaded team lives in `agents/`, is named in the kernel §1 table, and
**every plant pays its per-session cost**. That economy is why an optional role
lands here instead: this corpus is a **catalog of candidates**, roles a project
*may* select, none loaded by default, none named in the kernel. It gives the
same role one stable home so it is not reinvented per project, and gives harvest
somewhere to deposit a generic foreign role without touching the kernel budget
or the one-home-per-fact roster. Each page is instantiated through the withdraw
contract below; a page states only its role.

## What belongs here (role, durable)

- A **role**: its mandate, when to select it, and how it bounds against the base
  roster, statable with **zero framework names**.
- A role that owns a **discipline on a stack-shaped surface**: destroy-safety
  on declarative infrastructure, say, or build-and-delivery from a commit to a
  running platform. The surface has the shape of a stack, but what the role
  owns is a discipline (what it refuses, what it checks, what it hands to whom),
  and the mandate names the surface by its shape, never by a product. Such a
  role is catalog only, like every page here, and its page names the **base
  agent it narrows**: the agent in `agents/` whose mandate it takes a slice of,
  and what stays with that agent.
- Its `routing_triggers` exemplars (intent-phrased task cues) so a project's
  router can match it once selected.

The page shape follows from these: an optional-role blockquote, `Mandate`,
`When to select`, `Boundary (does not duplicate the base roster)` (for a
discipline role, it opens by naming the base agent it narrows),
`routing_triggers (exemplars)`.

## What stays OUT

- **Pure stack experts**: a framework, language or library specialist whose
  mandate is knowing the stack. Those are the plant's own, and usually not an
  agent at all: knowing a stack is knowledge, so it closes as an `expertise.*`
  node authored against the plant's own pins, which the router composes into the
  roster the plant already has. The test: if the mandate needs a language or
  framework name to be stated, it is a stack expert. Stack knowledge a harvest
  finds in such a charter is not lost: it goes to the library corpus, and the
  discipline, if any, to a role page here.
- **Roles that duplicate the base roster's mandate** ("a security role", "a
  testing role"): one home per role; extend the existing agent instead.

## Layout

```
agent-corpus/<name>.md
```

One page per suggested role, kebab-case id. Categories may be introduced as
subdirectories when the catalog grows. Currently populated:

- Discipline roles on a stack-shaped surface, each naming the base agent it
  narrows: `build-and-delivery-engineer` (a commit to a running platform),
  `iac-change-author` (destroy-capable declarative infrastructure).
- Owners of a surface between parts: `integration-topologist` (the call and
  event graph between services), `client-frontend-specialist` (the client
  application and its client → edge contract), `env-contract-manager` (the
  configuration and secret contract across source and deploy manifests),
  `legacy-runtime-reconstructor` (a runtime world that is gone, rebuilt
  from evidence).
- Evidence and reporting: `claim-verifier` (re-tests recorded claims),
  `report-editor` (re-cuts a finished report for another reader).

## The withdraw contract (consumed by `grow`, `graft` and commission)

`protocols/harvest.md` ("The suggested-expert corpus") owns this contract:
check this corpus first when a project needs a specialist the base roster
lacks, and instantiate a match into the project's `docs/graph/agents/` from
`docs/graph/templates/agent.template.md`. The selected role joins the project's
roster (and its kernel table and manifest); this catalog keeps only candidates.
