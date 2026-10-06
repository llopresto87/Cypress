## 8.0.0 — corpus pages placed on request, a deeper corpus, and sharper doctrine across the lifecycle (2026-10-05)

A plant can now ask the seed for the corpus pages that match its own stack,
one by one, and get version-aware library, skill and tool pages it can work
from without a research pass. The corpora are much larger. Planning,
delegation, the postures and the lifecycle protocols carry new rules. A
placed tool reads the session-metrics block of every full delivery. This
release is a major version because it adds a placed tool, a stamp key and
stricter checks that an existing plant meets on upgrade (see Upgrade notes).

### Install and selective placement

- `install.sh <host> --expertise propose` prints the library, tool and
  stack-keyed skill pages that the project's manifests match, one line per
  page with the manifest entry that matched, and writes nothing.
  `tools/corpus-match.py` does the matching; it runs from the seed and is
  never placed.
- `install.sh <host> --expertise <id>[,<id>...]` places exactly the pages
  named: library pages at `docs/graph/libraries/<name>.md` and tool pages at
  `docs/graph/tools/<name>.md` under a provenance line, and a stack-keyed
  skill page as the node `docs/graph/skills/<name>.md` with
  `origin: corpus@<seed version>`. The list is recorded in `.cypress/seed.json`
  under `expertise`, with the SHA-256 of each page written.
- Each later install refreshes the recorded pages nobody edited and names
  each edited page for graft. `--check` names a recorded page that is
  missing or stale.
- `grow` proposes the list, `graft` refreshes it, and `ingest-library` skips
  the scout for a placed page and pins only the version delta
  (`ingest-library.corpus-first`).

### Seed defects fixed

- The graft ledger takes an honest lineage base and accepts `--base-dir`.
  `graft-run` infers the adapters of an old stamp. graft re-checks at the end
  every file its record says it merged or kept.
- `status-migrate` keeps multi-line statuses and invents no dates.
  `growth-audit` declares grounding it could not check.
- graph-lint's artifact escape check is lexical, so a symlink install no
  longer reports false escapes. spec-lint and grill-lint refuse a misnamed
  spec instead of passing over it.
- A missing hook script prints one `cypress: hook script missing` line
  instead of nothing, and `install.sh --check` runs each wired context hook
  once. A harness agent or skill with no graph home is named RETIRED or
  ORPHAN; nothing is deleted.
- The hooks detect deeply nested input on any Python version. The installer
  resolves the legal jurisdiction once per run.
- Router triggers are sharper, and the adversarial ratchet is 2.

### Corpora

- The library corpus grows from 91 to 131 pages, with new `galaxy` and `pub`
  ecosystems. Pages state the version facts the library's own docs document
  (a minimum version, a version where behaviour changed) next to their
  subject, and a section per major line where the surface differs.
- The skill corpus grows from 12 to 33 pages. Stack-keyed pages live at
  `skill-corpus/<key>/<name>.md`, carry node frontmatter and a `stack:` field,
  and can be placed as routable skill nodes.
- The tool corpus grows from 24 to 40 pages, each with a self-test where the
  page claims portability. A tool page may carry the same `stack:` field.
- The agent corpus grows from 6 to 8 roles, including discipline roles on a
  stack-shaped surface.
- The legal corpus grows from 13 to 16 instrument pages: PSD2, the SCA
  technical standards and EDPB Guidelines 2/2023, plus two more provisions of
  the national data-protection code.
- Every corpus admits a page only at the withdraw-ready bar: a new plant
  could adopt it instead of running a research scout. Pitfalls, steps and
  rules from problems met in practice are written into the pages that own
  their subject.

### Doctrine

- Planning: a scoped standing grant for repeated non-production acts, asked
  for once at plan approval (`vcs-posture.publish-authorization`); a walking
  skeleton first for a new pipeline or deploy path, with a spec that grows one
  signed slice ahead of each RED; an environment-parity read for a plan that
  changes a deploy chain; an operational act that closes on evidence of the
  act, not of the tool that performs it.
- Delegation: an error signature is not a failure class; a provisional
  reading inside a contract keeps a worker going until the ruling pass; the
  run that gates the goal goes first; work split by area is routed area by
  area; a worker that hits a limit is resumed, not respawned.
- Postures: a control sits where the party it must stop cannot edit it; leak
  triage settles liveness by digest and verifies a rotation at the consumer;
  records a system already holds start unmanaged; a green dry run is
  structural evidence only, and a target selector is resolved to hosts before
  a mutating run; staging-only machinery refuses a production profile; a
  changed producer field updates its consumers in the same change.
- Lifecycle: grow treats an agent-operations system in the source as
  evidence; canonize keeps a harvest-candidate record from
  `docs/graph/plans/_harvest-candidates.template.md` and asks for missing tool
  and library pages at close-out; deliver requires the Session metrics block
  on the full form and records a production fault in the incident runbook; a
  ratified ADR takes an appended, dated Correction.
- The harvest protocol now takes knowledge whole. It generalizes a
  candidate instead of rejecting it, admits a stack-bound procedure as a
  stack-keyed page, and admits the version facts a library documents. It
  never states a plant's own version, and it leaves security warnings and
  CVE ids to scanners. Each fact carries a provenance class, candidates read
  from more than one project are consolidated first, a lesson goes into the surface that
  already owns its subject, and an independent reviewer reads each lane.
  [ADR-0028](docs/decisions/adr-0028-harvest-takes-knowledge-whole.md)
  records the decision.

### Session metrics

- `tools/session-metrics.py` is placed at `docs/graph/session-metrics.py`.
  deliver runs its lint role on the full-form entry it appends to
  `changelog.md`, and harvest reads its query role. It takes the block's
  labels from the plant's deliver node at run time.
  [SPEC-0006](docs/specs/SPEC-0006-session-metrics.md) holds its contracts.

### Checks

- The gate has 50 steps (`python3 tools/gate-registry.py --summary`).
- `tests/test_corpus_match.py` holds the matcher, and
  `tests/test-session-metrics.sh` the session-metrics reader.
- `tests/test-tool-corpus.sh` runs the self-test of every portable tool page
  and a mutated copy.
- The two knowledge-graph templates are held by prose-lint.
- SPEC-0001 carries the selective-placement, hook-check and
  harvest-candidate form contracts, and SPEC-0003 the missing-script
  warning.

### Upgrade notes

- **New placed tool.** Every install now places
  `docs/graph/session-metrics.py`, fast-forwarded like the other seed tools.
  A full-form delivery whose Session metrics block is missing or malformed
  is reported by it.
- **Nothing is placed from the corpora by default.** A plant gets library,
  tool or skill pages only through `--expertise`. Once it has used the flag,
  `.cypress/seed.json` carries an `expertise` key, and later installs refresh
  the recorded pages it has not edited.
- **New blank form in `plans/`.** The docs scaffold adds
  `docs/graph/plans/_harvest-candidates.template.md` where it is missing;
  graft treats it as expected.
- **Stricter spec discovery.** After graft reconciles the graph engines, a
  Markdown file in `docs/graph/specs/` that is not named `SPEC-*.md` (index
  and readme aside) fails spec-lint and grill-lint as a misnamed spec. Rename
  it, or it is never checked.
- **Louder hooks.** A context hook whose script is missing now prints one
  line naming it. `install.sh --check` runs each wired hook once, names each
  recorded expertise page that is missing or stale, and names harness agents
  and skills with no graph home.
- **New rules in the protocols and method nodes**, as listed above, reach an
  existing plant through `graft`. A new plant gets them from `install.sh`.

### Known limits

- The `cli/` library pages keep their documented minimum-version markers.
- The portability gate breaks one property per page with a single mutation;
  a self-test that misses other properties still passes it.
- `skills/adopt-existing/SKILL.md` sits at the 170-line leaf ceiling. Whether
  it moves to the lifecycle class or the ceiling is raised is the owner's
  decision.
- ADR-0028 is proposed and waits for the owner.
