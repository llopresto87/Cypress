# Working on the CYPRESS seed (this repo)

This repository is the seed, not a grown plant. `core/AGENTS.md` here is
the product shipped to target projects; this repo's own instructions are
these notes. There is no `docs/graph/` here; these notes replace it.

## Gates (run before claiming anything works)

```
bash tests/run.sh        # the full gate; tools/gate-registry.py --summary describes it
```

A count in prose is a fact with two homes. Where one is unavoidable, derive it.
`tools/gate-registry.py` derives the gate: it parses `tests/run.sh` and refuses
a step nobody has classified. `--summary` prints how many gates there are and
what each reads; `--table` prints the false green each can still produce. The
same classification keeps the gate honest about the steps that read only
`tests/fixtures/`: they prove a linter works and say nothing about the tree the
seed ships, and `--summary` prints how many there currently are.

`tests/seed-lint.py` is one-home-per-fact for the seed's own meta-facts:
roster/frontmatter/manifest/README consistency, the delegator invariant,
numeric claims, the kernel size budget (`KERNEL_BUDGET`), stable §3.1–§3.8
anchors, machinery-node frontmatter (every protocol/skill/agent/method
file is a graph node: id, kind, origin: seed, owns, load_when,
est_tokens, prevents; owns globally unique; the eight `rule.*` keys in
exactly their mapped homes), canonical-block byte-identity in the brief
templates, and the per-session instruction budget of the integrations.

## Release

The release, with its one documentation pass, is `docs/skills/seed-release.md`.
It ends in `tools/prepare-release.py` and a `vX.Y.Z` tag push. Both files are
seed-only: `install.sh` places neither into a plant. Pushing the tag is a publish: it waits for
the owner's explicit go-ahead (`vcs-posture.publish-authorization`).
`.github/workflows/release.yml` publishes the staged notes unedited and writes
no prose of its own, because CI has no access to the judgment
`skills/humanizer` requires.

## Canonical homes (edit the home; copies follow it)

- The seed is a graph: every protocol, skill, agent, and
  `core/method/` file is a routable node installed into a plant's
  `docs/graph/{protocols,skills,agents,method}/`; the kernel is a
  bootstrap of anchors and pointers.
- Each of the eight rules → its owning node's `rule.*` fact
  (3.1 specify, 3.2 context-router, 3.3 grill, 3.4 test-first,
  3.5 verify, 3.6 deliver, 3.7 canonize, 3.8 toolcraft); the kernel
  keeps only the one-line §3.x anchors.
- Tier depth → `core/method/tiers.md`; roster/routing →
  `core/method/delegation.md`; brief depth →
  `core/method/delegation-briefs.md`; engineering/design/stewardship posture →
  `core/method/{engineering,design,stewardship}-posture.md`
  (`core/operating-principles.md` is a tombstone).
- Graph-session discipline → `templates/prompts/graph-session-bootstrap.md`
  (brief templates embed it byte-identical; lint enforces sync).
- Handback contract → `templates/prompts/handback-payload.md`
  (agent files carry a short pointer to it).
- Close-out flow → `protocols/canonize.md` (single librarian spawn;
  `skills/toolcraft/` owns only the durable-tool doctrine: `agent.tool-smith` builds, `canonize` catalogs).
- Failure discipline → `protocols/recover.md` (classify, one move per
  class, three attempts, escalate).
- Seed release and the seed docs' one-home rule → `docs/skills/seed-release.md`
  (`seed-release.flow`, `seed-release.dedupe-rule`).
- The seed's own specs → `docs/specs/`, one file per specced surface, each
  titled by its surface. Kernel §3.1 says code without a spec is in remediation
  mode, and a seed surface where the seed writes into somebody else's repository
  or makes a quantitative claim about itself carries a spec. Each spec names
  its contracts in words rather than by letter-number label; read §4
  of each, and `seed-lint`'s `check_spec_test_mapping` for which test holds
  which. A new spec is owed the moment a new surface starts writing into a plant
  or reporting a number about itself.
  **Recorded exemption: the corpora are deliberately unspecced.** A
  `library-corpus/`, `legal-corpus/` or `tool-corpus/` page is transcribed
  knowledge, not behavior: its contract is its `_schema.md` plus
  `legal-lint.py` / the page-shape checks, and a §4 Given/When/Then over a
  statute would restate the statute. The exemption is bounded to the corpora and
  does not extend to any code path.
- Spec shape and contract coverage → `templates/knowledge-graph/spec-lint.py`
  (tested by `tests/test-spec-lint.sh`); plan-of-record shape →
  `templates/knowledge-graph/grill-lint.py` (tested by
  `tests/test-grill-lint.sh`).
- Front-door word definitions → `DOCUMENTATION.md` §15, the glossary (one
  anchored entry per term; README, the manual and the references link an
  entry instead of restating it). What each mechanism holds and misses, with its
  ADR-0003 class → `DOCUMENTATION.md` §17, the enforcement section (one row per
  mechanism kind; a front-door claim of enforcement links its row).
  `SPEC-0004-front-door` holds both through `tests/seed-lint.py`.
- Spawn order of a pass → its protocol's phase table (`grill.flow`,
  `specify.flow`, `test-first.cycle`, `ingest-library.flow`,
  `from-scratch.phases`); the generic sequencing rule →
  `core/method/delegation-sequencing.md` (`delegation.sequencing`). Skills, agents
  and the orchestrator point to it.
- Source ranking, retrieval steps, conflict rule → `skills/research-and-ingest`;
  page-section discipline → `skills/library-wiki`; the scout charter points.
- The spec's `active` moment → `verify.status-evidence` (promotion lands
  with the RED); specify, spec-author, and the template point at it.
- Roster ground truth → `agents/*.md` frontmatter (manifest, kernel
  roster line, and the agents reference follow it; lint checks). Why a component is on
  the roster → the node's own `prevents:` (the failure its absence
  produces), never a summary page; `tools/roster-justification.py`
  derives the table and prints evidence-of-use and class as absent
  rather than guessing them ([ADR-0008](docs/decisions/adr-0008-roster-justification-lives-in-the-node.md)).
- Unknown-row disclosure → `tools/growth-audit.py` (`SILENT`): every
  UNKNOWN row is named in the plant's `changelog.md` entry and put to the
  owner as a numbered decision; grow's delivery and graft's Phase 8 point.
  Raw-snapshot provenance → the `raw:` line of a normalized source
  (`skills/research-and-ingest`).

## Conventions

- A round with a behavior change ends in a version bump (`manifest.json`) and a
  `CHANGELOG.md` entry (append-only; a later entry supersedes an earlier one,
  which stays as written), through `docs/skills/seed-release.md`.
- The kernel is loaded on every session of every plant: every addition there
  is paid by every session, and lint enforces the budget. Depth belongs in a
  machinery node.
- Append-only artifacts: CHANGELOG.md, docs/decisions/. Everything else is
  integrated in place (`skills/holistic-editing`).
  - The one exception ([ADR-0011](docs/decisions/adr-0011-donor-token-redaction.md)):
    a token that identifies a project the seed was harvested from may be
    replaced in an append-only record, by owner decision only, never in an
    ADR body, and always disclosed. The records it has reached are a plan of
    record, append-only by the grill rule, and a spec's changelog,
    append-only by the spec rule. Four limits: (a) each token span becomes
    the one fixed placeholder `[redacted]`, and no sentence is reworded or
    deleted; (b) the release's CHANGELOG entry names each edited record and
    the class of token removed, never the token, and says the original text
    remains at the prior tag and in history, that history was not rewritten,
    and that published tags and Releases keep it; (c) the same statement is
    a dated line in each edited plan's or spec's changelog; (d) no
    force-push and no tag move.
- `harvest`/`graft` are user-sovereign: they start only from the owner, and
  seed machinery may propose one and stop there.
- Seed text (specs, plans, ADRs, doctrine) states an owner decision in words
  with its date, for example "the owner decided on 2026-10-04 that ...", and
  names no ruling id and no private record, because ruling ids, session
  identifiers (a spawn id, a worker label) and paths to a round's working
  records do not resolve for a later reader. Records of earlier releases keep
  the form they were written in.
