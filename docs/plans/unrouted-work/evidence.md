# Evidence — measurements taken 2026-09-14, before any edit

All read-only, against the working tree at 7.16.0. Scripts were throwaway; the
method is recorded here so each figure can be re-derived rather than trusted.

## E1 — `from-scratch` invokes; it does not duplicate `grow`

Body = the text after the frontmatter. Shingle = an 8-word sequence of
lowercase alphabetic tokens (≥3 chars), fenced code stripped.

| | `from-scratch` | `grow` |
|---|---|---|
| non-blank body lines | 153 | 777 |
| lines naming another node | 28 | 16 |
| **pointer density** | **18%** | **2%** |
| substantive sentences (>45 chars, non-table) | 54 | 426 |
| **identical sentences shared** | **0** | **0** |
| **shared 8-word shingles** | **0** of 1 006 | — |

## E2 — the delegation discipline holds against everything it adopts

Shared 8-word shingles between `from-scratch` (1 006 shingles) and each node it
declares it adopts:

| Node | shared | % of from-scratch |
|---|---|---|
| `protocols/grow.md` | 0 | 0.0% |
| `protocols/grill.md` | 3 | 0.3% |
| `protocols/brainstorm.md` | 0 | 0.0% |
| `protocols/specify.md` | 3 | 0.3% |
| `protocols/test-first.md` | 8 | 0.8% |
| `protocols/verify.md` | 0 | 0.0% |
| `protocols/canonize.md` | 0 | 0.0% |
| `protocols/deliver.md` | 0 | 0.0% |
| `protocols/ingest-library.md` | 10 | 1.0% |
| `skills/from-scratch-bootstrap/SKILL.md` | 0 | 0.0% |
| `skills/knowledge-graph/SKILL.md` | 0 | 0.0% |
| **union of all eleven** | **10** | **1.0%** |

**99.0% of `from-scratch`'s prose exists nowhere else**, and its own text says
why: *"Phases 3–5 are `grill.flow`'s phases 0–4 and are not restated here; what
a greenfield adds:"*.

Consequence for slice 1: absorbing `from-scratch-bootstrap` is an **append**,
not a merge. Overlap is 0.0%; there is nothing to reconcile.

## E3 — they delegate to disjoint halves of the method

- `from-scratch` → `brainstorm`, `grill.flow`, `ingest-library.flow`,
  `adr-writer`, `verify`, `specify.flow`, `test-first.cycle`, `canonize`,
  `deliver`, `knowledge-graph`, `install.sh` — the core method protocols.
- `grow` → `research-scout`, `legal`, `ingest-library`, `harvest`, `recover`,
  `initialize`, the postures — the growth machinery.
- Common targets: `canonize`, `deliver`. The close-out, and nothing else.

## E4 — `from-scratch` is unreachable

| Surface | Text | Effect on an empty repo |
|---|---|---|
| `core/AGENTS.md` | names `/initialize` and `protocol.grow`; **never names `from-scratch`** | a session learns there is a growth path, never a new-project path |
| `install.sh:770` | "run /initialize to **discover the project** and grow the graph" — unconditional | discover a project that is not there |
| `protocols/initialize.md` | "delegates unchanged to `grow`" | forwards the empty case to the protocol for the opposite case |
| `protocols/grow.md:555` | "If there is no executable project evidence, route through `from-scratch` **for intent discovery**" | the only link — buried in Phase 1 of an 869-line file, and it **misdescribes** from-scratch as a sub-step returning intent when it is a nine-phase workflow ending in `deliver` |

Counts: `grow.md` names `verify` **0** times, `specify` **0**, `brainstorm`
**0**, `test-first` 1, `grill` 2.

## E5 — the Phase 2 circularity

`from-scratch` Phase 2 ("Project skeleton") runs `install.sh` and owns
`seed-installer`. But the documented route reaches `from-scratch` only *after*
installing. Anyone arriving by the documented path lands on a procedure whose
Phase 2 is already done, with nothing saying so. Phase order assumes an entry
the installer does not create.

## E6 — no two components in the roster are confusable

Jaccard overlap of routing-trigger / `load_when` vocabulary, stopwords removed,
across all pairs within each kind:

| Kind | highest-overlap pair | trigger | `prevents:` |
|---|---|---|---|
| agents | `implementer` / `tester` | 0.13 | 0.12 |
| protocols | `graft` / `grow` | 0.15 | 0.12 |
| skills | `library-wiki` / `research-and-ingest` | 0.18 | 0.00 |

Highest anywhere is 0.18. `prevents:` overlap — do two nodes stop the same
failure — peaks at 0.12 and is near zero across the roster. Every high pair is a
declared collaboration, not a duplication. This is why the plan merges nothing
beyond the two folds the owner named.

## E7 — the brainstorm gap is structural, not stylistic

- `protocols/brainstorm.md` requires **explicit user confirmation before exit**.
  The only brainstorm in the graph cannot complete without a user, so internal
  option generation has no home.
- `skills/brainstorm-socratic/SKILL.md` declares peers `protocol.brainstorm` and
  `skill.spec-author`. **`humanizer` is not among them**, though `humanizer`'s
  charter already covers "briefs and reports for the owner".
- The Socratic machinery — one-to-three questions per turn, reflect every two
  answers, a nine-question hard cap, an eight-point convergence checklist — is
  **wholly inapplicable** with no user to question. The two modes share a name
  and almost nothing else, which is the evidence the seam is real.

## E8 — tool authorship has no owner

- `canonize`'s brief catalogs "any durable tool **it produced**" — *it* being
  some other actor, never named.
- `toolcraft`'s own description: *"EXECUTION lives in the canonize close-out …
  toolcraft never spawns separately."*
- `canonize` forbids a second spawn, and states the reason: *"a second spawn
  with the same bootstrap and lint run would be coordination waste."* That
  rationale is about **cataloging** — writing the page in `docs/graph/tools/`.
  It says nothing about **authoring**, which happens mid-task, and it therefore
  survives slice 4 unamended in substance and narrowed in wording.
- `toolcraft` also owns `toolcraft.bounded-execution` (~18 lines on long-running
  commands, polling, and never re-issuing a command). That is an execution
  discipline, not tool-authoring doctrine; it was filed here because toolcraft
  was the nearest protocol.

## E9 — where a `rule.*` fact may live

The eight kernel rules map to homes in `seed-lint.py`:

| Home kind | count | which |
|---|---|---|
| protocol | 7 | spec, grill, test-first, verify, deliver, canonize, toolcraft |
| skill | 1 | `rule.knowledge` → `skills/context-router/SKILL.md` |
| agent | **0** | — |

A non-protocol home is precedent. An **agent** home would be a first, and slice 4
declines to make it one: a kernel rule binds every session, and a rule whose only
home is a specialist's charter is invisible to any session that never spawns it.
