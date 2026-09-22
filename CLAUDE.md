# Working on the CYPRESS seed (this repo)

This repository IS the seed — not a grown plant. `core/AGENTS.md` here is
the product shipped to target projects, not this repo's instructions.
There is no `docs/graph/` here; these notes replace it.

## Gates (run before claiming anything works)

```
bash tests/run.sh        # the full gate. The roster is deliberately not
                         # restated here: it drifted twice during one session
                         # of editing it, which is what a count in prose does.
                         # Ask the thing that derives it:
                         #   python3 tools/gate-registry.py --summary
                         # for how many gates there are and what each READS,
                         # --table for the false green each can still produce.
```

A count in prose is a fact with two homes. Where one is unavoidable, derive it:
`tools/gate-registry.py` parses `tests/run.sh` and refuses a step nobody has
classified — which is also what keeps the gate honest about the gates that read
only `tests/fixtures/`, and therefore prove a linter works while saying nothing
about the tree the seed ships. `--summary` prints how many that currently is.

`tests/seed-lint.py` is one-home-per-fact for the seed's own meta-facts:
roster/frontmatter/manifest/README consistency, the delegator invariant,
numeric claims, the kernel size budget (8 000 bytes), stable §3.1–§3.8
anchors, machinery-node frontmatter (every protocol/skill/agent/method
file is a graph node: id, kind, origin: seed, owns, load_when,
est_tokens, prevents; owns globally unique; the eight `rule.*` keys in
exactly their mapped homes), canonical-block byte-identity in the brief
templates, and the per-session instruction budget of the integrations.

## Release (GitHub, tag-triggered)

`tools/prepare-release.py` is seed-only — absent from `manifest.json`'s
`tools` map, so it never ships to a plant. It stages
`.github/RELEASE_NOTES.md` from the `CHANGELOG.md` entry for the current
`manifest.json` version, taken verbatim rather than re-drafted: the entry
already passed canonize's `skills/humanizer` prose pass, so re-authoring it
here would be a second home for the same release, in the same voice, for
the same reader. The staged file is `skill-corpus/discardme.md`-shaped
scaffolding — produced this session, consumed by the pipeline below,
superseded (not explicitly deleted) the next time the script runs for the
following version, since a same-turn cleanup commit back to the default
branch would race whatever lands on it next for no benefit a release reader
gets.

Flow, once the version bump and its `CHANGELOG.md` entry are committed:

1. `python3 tools/prepare-release.py` — writes `.github/RELEASE_NOTES.md`
   and prints the exact commands for the next step.
2. `bash tests/run.sh` green, then commit the staged file with the rest of
   the change.
3. `git tag -a vX.Y.Z -m vX.Y.Z && git push && git push origin vX.Y.Z` —
   pushing the tag is a publish and needs the same explicit go-ahead as any
   other push (`core/method/vcs-posture.md`'s `vcs-posture.publish-authorization`).

`.github/workflows/release.yml` triggers on that `vX.Y.Z` tag push, checks
it against `manifest.json`, and runs `gh release create` with the staged
file as the body, unedited. It writes no prose of its own: CI has no access
to the judgment `skills/humanizer` and `skill-corpus/discardme.md` both
require. `tests/seed-lint.py`'s `check_release_workflow` holds the
workflow's shape; `tests/test_prepare_release.py` holds the script's
extraction and CLI behavior.

## Canonical homes (edit the home, never a copy)

- The seed IS a graph (6.0.0): every protocol, skill, agent, and
  `core/method/` file is a routable node installed into a plant's
  `docs/graph/{protocols,skills,agents,method}/`; the kernel is a
  bootstrap of anchors and pointers.
- Each of the eight rules → its owning node's `rule.*` fact
  (3.1 specify, 3.2 context-router, 3.3 grill, 3.4 test-first,
  3.5 verify, 3.6 deliver, 3.7 canonize, 3.8 toolcraft); the kernel
  keeps only the one-line §3.x anchors.
- Tier depth → `core/method/tiers.md`; roster/routing/brief depth →
  `core/method/delegation.md`; engineering/design/stewardship posture →
  `core/method/{engineering,design,stewardship}-posture.md`
  (`core/operating-principles.md` is a tombstone).
- Graph-session discipline → `templates/prompts/graph-session-bootstrap.md`
  (brief templates embed it byte-identical; lint enforces sync).
- Handback contract → `templates/prompts/handback-payload.md`
  (agent files carry a 3-sentence pointer, never the full spec).
- Close-out flow → `protocols/canonize.md` (single librarian spawn;
  `skills/toolcraft/` owns only the durable-tool doctrine — `agent.tool-smith` builds, `canonize` catalogs).
- Failure discipline → `protocols/recover.md` (classify, one move per
  class, three attempts, escalate).
- The seed's own specs → `docs/specs/`. Kernel §3.1 says code without a spec is
  in remediation mode, and the seed had none of its own. Two exist, covering the
  two surfaces where the seed writes into somebody else's repository or makes a
  quantitative claim about itself: `SPEC-0001-install-placement` (what
  `install.sh` may do to a target) and
  `SPEC-0002-routing-contract` (what `--route` and `--eval` may claim). Both
  name their contracts in words rather than by letter-number label; read §4 of
  each, and `seed-lint`'s `check_spec_test_mapping` for which test holds which.
  **Recorded exemption — the corpora are deliberately unspecced.** A
  `library-corpus/`, `legal-corpus/` or `tool-corpus/` page is transcribed
  knowledge, not behavior: its contract is its `_schema.md` plus
  `legal-lint.py` / the page-shape checks, and a §4 Given/When/Then over a
  statute would restate the statute. The exemption is bounded to the corpora and
  does not extend to any code path. A third spec is owed the moment a new
  surface starts writing into a plant or reporting a number about itself.
- Spec shape and contract coverage → `templates/knowledge-graph/spec-lint.py`
  (tested by `tests/test-spec-lint.sh`); plan-of-record shape →
  `templates/knowledge-graph/grill-lint.py` (tested by
  `tests/test-grill-lint.sh`).
- Spawn order of a pass → its protocol's phase table (`grill.flow`,
  `specify.flow`, `test-first.cycle`, `ingest-library.flow`,
  `from-scratch.phases`); the generic sequencing rule →
  `core/method/delegation.md` (`delegation.sequencing`). Skills, agents,
  and the orchestrator point, never re-list.
- Source ranking, retrieval steps, conflict rule → `skills/research-and-ingest`;
  page-section discipline → `skills/library-wiki`; the scout charter points.
- The spec's `active` moment → `verify.status-evidence` (promotion lands
  with the RED); specify, spec-author, and the template point at it.
- Roster ground truth → `agents/*.md` frontmatter (manifest, kernel
  roster line, and README follow it; lint checks). Why a component is on
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

- Behavior change ⇒ bump `manifest.json` version + `CHANGELOG.md` entry
  (append-only; supersede, don't rewrite).
- The kernel is loaded on every session of every plant: additions there
  need to earn ~2k-token-per-session rent, and lint fails past budget.
  Depth belongs in a machinery node, never the kernel.
- Append-only artifacts: CHANGELOG.md, docs/decisions/. Everything else:
  integrate, don't bolt on.
- `harvest`/`graft` are user-sovereign; nothing in the seed may trigger
  them automatically.
