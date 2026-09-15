---
name: harvest
description: The inverse of grow — fold a mature plant's GENERALIZABLE lessons back into the seed (tooling fixes, skill and protocol gaps, agent and template improvements, and the five corpus contracts) so the next plant starts ahead of where this one did. Manual trigger only, never automatic; harvest proposes and the steward ratifies. Holds the three admission gates — agnosticism, durability, non-redundancy — and the seed integrity gate table every fold-back clears before it may land.
id: protocol.harvest
tier: 2
kind: protocol
origin: seed
title: harvest — folding a mature plant's project-agnostic lessons back into the seed, user-triggered only
owns:
  - harvest.fold-back-flow
  - harvest.agnosticism-gate
  - harvest.availability-gate
  - harvest.corpus-contracts
requires:
  - method.delegation
peers:
  - method.engineering-posture
  - skill.humanizer
  - protocol.canonize
  - protocol.graft
  - protocol.grow
  - protocol.ingest-library
  - skill.toolcraft
load_when:
  - "harvest lessons back into the seed"
  - "fold generalizable improvements upstream"
  - "the plant is mature, propose a harvest"
  - "seed improvement from project experience"
  - "should this library, tool, skill, or expert page go into the seed's corpus"
  - "is this lesson project-agnostic enough to land in the seed"
  - "wire a harvested artifact so install, grow, or graft actually delivers it"
  - "propose promoting a plant-commissioned expert into the base roster"
  - "a harvested page is in the seed but no plant can reach it"
prevents: A lesson learned in one plant and re-learned in every other, because fixes stay project-local and the next plant starts exactly where the last one did.
est_tokens: 12555
---

# Protocol: harvest

`grow` runs the seed into a project and grows it. `harvest` runs the other
direction: a mature project back into the seed, so the next project starts ahead
of where this one did. A seed that only ever seeds, and never harvests, cannot
improve; a seed that harvests carelessly rots into a pile of one project's
specifics. This protocol is the disciplined gate that lets the seed compound
**without** losing its agnosticism.

The metaphor is load-bearing. The seed grows a plant; the plant lives its own
life and learns things; harvest takes only the seed-worthy essence of what it
learned, never the plant's flesh, and folds it back so the next seed is richer.
What goes back in must be true for *any* future plant, not this one.

## Trigger — manual only, never automatic

Harvest is **user-sovereign**. Unlike `canonize`, which runs at the end of
every task, harvest is **never** triggered automatically, on a schedule, by a
hook, or as a "while I'm here" step at the end of another protocol. The seed is
the inheritance of every future plant; changing it is the user's call, not the
system's.

- **The user starts it**, by invoking this protocol or pasting `HARVEST_PROMPT.md`.
- **The system may, at most, PROPOSE it.** When a mature plant clearly holds
  generalizable lessons, an agent may *suggest* "this looks worth harvesting into
  the seed" and stop. It does not begin. The suggestion is a doorbell, not an
  entry.
- **Nothing reaches the seed until the user is satisfied with the growth.** Every
  fold-back is a proposal the user ratifies, and an unratified harvest is a draft
  rather than a change. If the user is not satisfied, the proposal is revised or
  dropped and the seed stays as it was.

## When to invoke

- The **user** has asked to harvest, or ratified a proposal to. (Maturity below
  is a precondition for *proposing*, never an automatic trigger.)
- A plant is **fully grown**: delivered, its verification gates green, its
  plan-of-record closed or steady. Harvest a living, still-churning project
  and you will backport half-baked lessons.
- The plant's life produced **generalizable** artifacts worth compounding:
  a shared-tooling bug fixed, a new hard rule a skill should have carried, a
  protocol gap discovered, a new reusable expert authored, a template that
  grew a better section, a class of failure whose *prevention* is universal.
- You are the seed's **steward** (the user acting as the seed's owner; the two
  words name the same person), working with the seed as the target scope. The
  plant is a read-only donor, and the seed is the only thing this protocol
  writes.

## The agnosticism gate — the heart of this protocol

Every candidate improvement passes one hard test before it may touch the
seed:

> **Would this help an arbitrary next project, in a different language,
> framework, and domain, that has never heard of this plant?**

- **YES, verbatim.** Harvest as-is (rare; usually only tool-neutral rules).
- **YES, once generalized.** Rewrite it stripping every plant-specific
  name, domain term, stack pin, path, and example, until only the universal
  kernel remains, *then* harvest the generalized form. State the
  before→after generalization explicitly.
- **NO.** Reject it. It is the plant's life, not the seed's. Record why, leave
  it in the plant.

Fail-closed corollary: **if you cannot state the lesson without naming the
plant, it is not ready to harvest.** Generalize it or drop it. A single
leaked project name, domain noun, credential, dataset shape, or
version-pinned specific in the seed is a failed harvest, and it is worse than a
missed lesson, because it silently narrows the seed for everyone downstream.

### What counts as a project reference (all forbidden in the seed)

"Project-agnostic" is stricter than "unnamed": a reference need not name the
plant to identify it. **Every one of these six classes is a project reference and
must not survive into the seed anywhere, including the CHANGELOG entry, the
harvest-log row, provenance notes, and any illustrative example:**

1. a **name**: the plant, its product, company, service, or an internal tool or
   library of its own;
2. a **stack fingerprint**, the specific language/framework/datastore combination
   that identifies the plant (e.g. "a `<language>/<framework>` microservices
   plant"). Name a library only where the seed genuinely documents that library
   for *any* project (the library corpus), never as "the stack this plant ran";
3. an **identifying count or metric**: "authored N library pages", "an N-observer
   registry", a figure that describes this plant's scale rather than a universal
   rule;
4. a **description of the plant's internals**: its file names, config keys, plugin
   names, module wiring, or a security finding on its own code;
5. a **path, host, port, credential, or absolute install location** (`/root/…`);
6. an **illustrative example framed as the plant's own**, such as "this project's
   fleet does X". Recast every example in the generic ("a fleet may do X"); an
   example is admissible only once it no longer belongs to any specific project.

Plant-identifying provenance (which plant it was, its stack, the exact
before-text that was stripped) belongs in the **ratification proposal you show
the steward**, never in the seed's committed files. The seed records *that* a
harvest happened and *what* generalized lesson landed; it never records *whose*
plant it came from.

This list is the one home of the rule. Phase 2 applies it, **G1** and **G2**
enforce it, and both point here by number rather than re-listing the classes.

### The second gate — durability (surface, not pin)

Agnosticism asks *"true for another project?"* Durability asks a second,
independent question of every fact:

> **Will this still be true a version from now — is it about the library,
> or about one pinned release of it?**

The seed's inheritance is **surface-level, version-durable** knowledge: what
a library is for, its stable API shape, its enduring idioms and conceptual
pitfalls. That is what compounds. Anything keyed to an exact release is the
*plant's* concern, discovered fresh by `ingest-library` against the plant's
own lockfile, and it rots the moment the pin moves.

- **KEEP (surface, durable):** the capability the library provides; its core
  API shape and canonical usage; idioms and best practices that hold across
  minor/major lines; conceptual gotchas inherent to the tool; the upstream
  doc/repo home.
- **REJECT (pinned, ephemeral):** CVEs and advisories tied to an exact
  version; "version X.Y.Z is a breaking-change marker"; deprecations
  introduced in a specific release; upgrade/migration diffs between two
  pins; a resolved-version number itself. These belong in the plant's
  `docs/graph/libraries/<name>.md`, never in the seed.

When in doubt, a fact is pinned, so drop it. A corpus page that reads like a
security bulletin for one release has failed this gate; one that reads like
the opening orientation of the library's own docs has passed.

Of the two classes above, only the CVE identifier has a detector
(`tools/agnosticism-lint.py`'s `CVE_RE`). A resolved version number has none,
and 4.8.0 recorded one reaching the seed. Durability is read by a person.

### The third gate — non-redundancy (does the seed already own this?)

Agnosticism asks *"true for another project?"*; durability asks *"true a
version from now?"*. The third gate asks the question this protocol most
often forgets:

> **Does the seed ALREADY say this — in a kernel rule, an agent, a skill, a
> protocol, or a template?**

A plant grew *from* the seed, so its ADRs, plan-of-record, best-practices,
and runbooks are saturated with the seed's own doctrine filled in with local
facts. A survey that reads only the plant will keep "discovering" rules the
seed already ships (reversibility-with-trigger, a risk paired with its
verifying check, fail-closed defaults, released-bits-are-tested-bits,
resolve-in-place, two-axis severity) and proposing them back is not a
harvest, it is an echo. Before any candidate is proposed, **open its would-be
seed home and read it**: if the rule already lives there, the candidate is
**rejected as redundant**, and only the genuinely net-new residue survives.
Corroboration across several plants raises confidence that a *net-new* rule is
universal; it never converts a seed duplicate into a fold-back. A candidate
that bolts a second home onto a fact the seed already owns fails the seed's
one-home-per-fact rule (`seed-lint`), and that is worse than a missed lesson,
because it splits a fact across two homes that will drift.

## The flow

Orchestrated like `grow`: the session plans, briefs, and ratifies, while
clean-context workers survey, triage, and author. Model policy is strict, with
Sonnet-class for read-only survey and Opus-class for every generalization and
authoring call.

### Phase 1 — Survey the mature plant (Sonnet scouts, read-only)

Inventory how the plant diverged from the seed it grew from, and what it
accumulated. A prior `graft`'s customization-audit ledger and its KEEP-PLANT list
(`tools/graft-audit.py` output, the graft record's "kept as the plant's" section)
is a ready-made divergence inventory: a machinery file the plant customized that
the graft preserved is already a flagged harvest candidate, so start from it
rather than rediscovering the divergence. Candidate donor surfaces:
- shared scripts/tooling the plant fixed or added;
- skills whose rules the plant sharpened, or gaps it hit that a core skill
  should close, and any **project skill** the plant authored (a repeatable
  procedure) whose steps generalize, mined for the agnostic procedure only;
- protocols the plant found insufficient or missing a step;
- agent/expert definitions authored to fill a roster gap;
- templates that gained a better section or default;
- the plant's accumulated sharp-edges / case library / ADRs, mined for the
  *generalizable prevention rule* only, never the incident narrative;
- the plant's **plan-of-record** (`grill.md` §6 Decisions, §7 Options, §11
  Risks, §12 Open Questions) and its **ADRs**, mined for *decision and
  planning discipline* a plan should always carry (a decision's evidence and
  reversibility-with-trigger, a risk paired with the check that verifies it,
  an open question's pinned-by and do-not-guess marker, "do nothing" recorded
  as a decision), never this plant's actual decisions or their content;
- the plant's **best-practices pages** (`docs/graph/best-practices/`), mined
  for a durable engineering/security/testing *principle*, never a
  stack-specific rule, a framework API, or a pinned advisory;
- the plant's **runbooks** (`release`, `rollback`, `incident-response`,
  `verification`), mined for operational *discipline* (a release-readiness
  gate, a reversal that is non-autonomous and reversible-before-destructive,
  an incident loop that closes by adding a gate), never its hosts, commands,
  or ports;
- the library & language wiki pages the plant built during `ingest-library`,
  mined for their **version-durable surface** only (see the corpora below):
  what the library is and how it is idiomatically used, never the plant's
  pinned CVEs, per-release deprecations, or migration diffs;
- the plant's reusable-tool catalog (`docs/graph/tools/`) built during
  `toolcraft`, mined for **project-agnostic, durable tools**: the capability
  and interface, and the portable implementation when it is stack-neutral,
  never the plant's paths, credentials, or stack-pinned wiring;
- the plant's **legal / regulatory leaves**, where the plant reasoned against
  externally-authored rules, mined for the **citation only** (instrument,
  provision, `text_form` and text, publisher URL, verification grade, status),
  never the plant's application of the rule, its own determination, or any
  finding drawn from it. A citation is portable; a determination never is;
- the plant's **session metrics**, aggregated from delivery summaries
  (grill.md §15 / `docs/graph/changelog.md`, the block defined in
  `docs/graph/protocols/deliver.md`). This is the seed's only *quantitative*
  donor surface: recurring routing overrides or LOW-band spawns of the same
  kind mean a specialist's `routing_triggers` need sharpening; frequent
  tier reclassifications in one direction mean the kernel §0 tier edges
  need tuning; repeated retries of one failure class
  (`docs/graph/protocols/recover.md`) mean a protocol is missing a step, a gate,
  or a sharp-edge rule. Mine the *pattern*, propose the seed change; the
  plant's raw numbers stay in the plant;
- a **capability the seed ships that stays inert**: a surface (a suggested
  skill, a runbook template, a corpus withdrawal) present as machinery on many
  plants yet grown on none. Inertness across plants is a design signal, not a
  plant fact. The withdraw contract may be missing, the capability may be
  mis-placed, or `graft`/`grow` may lack a step that actualizes it. Harvest the
  *fix to the seed's own machinery* (a clearer withdraw contract, a grow step),
  never any plant's would-be content.

Output: a **candidate ledger**, each row a candidate with provenance (where
in the plant, what triggered it) and a first guess at its class. Claims cite
plant paths/symbols; centralized prose is an untrusted clue until corroborated.

### Phase 2 — Triage against all three gates (Opus authors)

For each candidate, apply **all three** gates (agnosticism, durability,
non-redundancy) and decide KEEP-AS-IS / GENERALIZE / REJECT. For anything kept,
write its **generalized restatement**: the tool-neutral, version-durable form
that will land in the seed, with the before→after shown (what plant-specifics
*and* what pinned specifics were stripped). Reject rows carry a one-line reason,
including "redundant — the seed already owns this at `<home>`". This phase is
where the seed's purity is defended, so be conservative: when in doubt, reject or
generalize harder.

### Phase 3 — Backport authoring (Opus authors)

Apply each surviving generalized improvement to the SEED artifact it belongs
in (`skills/`, `protocols/`, `agents/`, shared scripts, `templates/`,
`library-corpus/`, `legal-corpus/`, `tool-corpus/`, `agent-corpus/`,
`skill-corpus/`, kernel), each as a **holistic edit**, integrated into the
artifact as if it had always been there and never bolted on. Every fold-back
records provenance: which plant lineage it came from, the generalization
applied, and the seed files touched. The seed evolves spec/test-first too, so a
harvested tooling fix arrives with its regression test generalized alongside it.

Three things are part of *authoring*, not of verifying, because a reader who
leaves them to Phase 4 has already written the defect:

- **Wire it in the same edit that lands it.** The delivery path an artifact
  needs (a `place_*` call, a line in the consuming node, a roster row) is
  written with the artifact, not after **G4** complains. Deposit-then-wire is how
  the legal corpus sat in the seed from 6.12.0 until 7.11.0 while `install.sh`
  placed none of it, and how a tool the seed built was found only because someone
  applied this protocol's own availability gate to an unrelated release.
- **Run the prose pass on imported prose.** A harvested page, charter, or
  section is text a person will read in the seed's voice, and it arrived in
  the plant's. `skill.humanizer` names harvest as one of its execution sites
  for exactly this. Apply the skill, then floor the result, then prove the pass
  dropped nothing. **G8** holds the commands.
- **Never widen a limit to make a fold-back fit.** Every budget, ceiling and
  debt ledger in the seed is recorded in `tools/ratchet-lint.py` and may only
  move toward stricter. If a fold-back does not fit a kernel budget, a body
  ceiling, or an eager-surface exemption, then the fold-back is the wrong size:
  land it in a cheaper surface (**G9**). Raising the number is an owner
  decision taken in the open, and `ratchet-lint.py --bless` is the owner's
  signature, never the harvester's (**G11**).

### Phase 4 — Seed integrity gate

The seed must leave harvest **more capable and no less agnostic**. The table
below is the **single home** of every gate this protocol runs: the record in
§Output format is its result column, and the quality bar and "what you do not
do" point at it rather than restating it. Adding a gate is one edit here.

A gate that runs but asserts nothing is a green lie. So every row names its
command, **or** names the judgment and who owns it, in the same cell. There is
no third state and no blank.

`Class` is the ADR-0003 vocabulary, as its 2026-09-14 amendment settles it:
`hard` (the **harness** refuses, so the wrong thing is impossible), `soft` (a
contract **or a tool** refuses), `detective` (asserted post-hoc from named
evidence that a person reads and acts on), `judgment` (a named agent or person
decides, and no tool can). **Nothing here is `hard`**, because no harness
prevents a steward committing a harvest, and saying so is the point of the
column. The cell holds exactly that one word, which `seed-lint.py`'s
`check_gate_single_home()` enforces; the judge's name lives in the command cell.

| # | Gate | What it asserts | Command, or the judge | On failure | Class |
|---|---|---|---|---|---|
| G1 | `harvest.gate.agnosticism-floor` | No host-IP literal, pinned CVE, or supplied plant token survives in any changed file, and every changed file was actually opened | `python3 tools/agnosticism-lint.py --forbid <plant token> …` with one `--file` per changed file, the set enumerated from `git diff --name-only --diff-filter=d <pre-harvest rev>` (the literal invocation is in §G1 in detail). Exits 0, with no `unreadable` finding. Drive the file list from git, never from an extension list: a `--file` is scanned whatever the globs say, so nothing a hand-kept list forgot can slip past. `--root` plus `--glob` is for a directory added whole, and there the glob list **is** the coverage boundary: an extension nobody listed is not opened and yields no finding at all, because the tool models `unreadable` for a file it failed to read and has no concept of a file it never matched | BLOCK | soft |
| G2 | `harvest.gate.agnosticism-judgment` | The classes no regex sees: every class in §What counts as a project reference that G1's `--forbid` list did not cover | No command exists. Read `git diff` whole against that section, class by class. Judge: the Phase-2 generalizer, re-read by the steward at ratification | BLOCK | judgment |
| G3 | `harvest.gate.faithful-import` | Each imported artifact carries the whole of its donor's generalizable discipline, with only plant-specifics stripped and never substance | No command exists. Section-by-section donor→import comparison, one per artifact. Judge: an Opus reviewer who did **not** author the import | BLOCK | judgment |
| G4 | `harvest.gate.availability` | Every import is reachable by the flow that delivers it, proven against `install.sh` and the consuming node | The five-step resolution below; record the resolved path per artifact | BLOCK as INERT | detective |
| G5 | `harvest.gate.plant-untouched` | The donor plant's working tree is byte-unchanged, because harvest is inbound-only | `git -C <plant> status --porcelain` is empty, and `git -C <plant> rev-parse HEAD` matches the pre-harvest value. Both exit 0 either way, so the output is evidence a person reads, never a refusal | BLOCK | detective |
| G6 | `harvest.gate.self-consistency` | The seed's own FULL gate is green and every registry is in sync | `bash tests/run.sh`, every lint and suite, never a hand-picked subset | BLOCK | soft |
| G7 | `harvest.gate.clean-install` | A by-hand install of the working tree into a fresh directory succeeds, and its owner-facing output says what this harvest expects | `bash install.sh claude-code --project-dir "$(mktemp -d)"` (the harness is POSITIONAL; there is no `--harness` flag and the parser dies on one). Read the warnings, the re-created-node notices and the NEXT STEP lines. The install suites are G6's and are not re-run here | BLOCK | soft |
| G8 | `harvest.gate.prose` | Imported prose reads as the seed's own writing and lost no fact in the rewrite | `python3 tools/prose-lint.py --file <changed .md>` and `--against <pre-harvest rev>`; the judgment above it is `skill.humanizer` | BLOCK, or record the genre exception in the proposal | soft |
| G9 | `harvest.gate.minimum-sufficient` | The fold-back is the smallest edit that reaches its audience, in the cheapest surface that reaches it | No command exists. Weighed against `method.engineering-posture` §5 and the surface ladder below. Judge: the steward at ratification | RETURNED as a smaller edit, not blocked | judgment |
| G10 | `harvest.gate.provenance` | The version is bumped, the CHANGELOG entry and harvest-log row exist, and every seed change carries a test or lint proof | `git diff --stat` shows `manifest.json` and `CHANGELOG.md`, read by a person; `python3 tests/seed-lint.py` holds the manifest, the kernel roster line and README to the agent frontmatter | NOT RELEASABLE | detective |
| G11 | `harvest.gate.no-loosened-limit` | No budget, ceiling, or debt ledger was widened to make a fold-back fit | `python3 tools/ratchet-lint.py`, the bare invocation `tests/run.sh` runs and G6 therefore covers. It is the only form that can fail, and it names each widened limit (`was LOOSENED`, `GREW by`). `--show` prints `recorded=… current=…` for every ratchet, says of none of them that it moved, and always exits 0: a reading aid, never a check. A loosening is an owner decision stated in the proposal | BLOCK pending the owner | soft |

**Only G9 returns rather than blocks.** A fold-back that could have been a
one-line sharpening of an existing home comes back in that form. Three more rows
name an outcome that is not a flat BLOCK, each in its own cell: G8 admits a
recorded genre exception, G10 is not releasable rather than un-landable, and G11
blocks pending an owner decision nobody else may take. The remaining seven are
absolute.

**The surface ladder G9 weighs against.** Land the lesson in the cheapest
surface that still reaches its audience: a reference or corpus page before a
skill, a skill before a protocol, a protocol before the kernel. A new rule,
file, or section is the last resort, and kernel bytes cost every session of
every plant. `method.engineering-posture` §5 owns *minimum sufficient work*;
this ladder is harvest's own ordering of the seed's surfaces, and the seed has
no other home for it.

**G6 is a green run, not a compliance certificate.** `tests/run.sh` exits 0 and
a reader hears "the seed obeys everything it checks", which is a different
claim: a large share of its steps read only `tests/fixtures/`, so they prove a
linter works and say nothing about the tree the seed ships.
`python3 tools/gate-registry.py --summary` prints how many of each, and
`--table` prints the false green each step can still produce. Read it before
writing G6's result line, and cite the class when a fold-back's only proof is a
fixture suite. If this harvest adds a step to `tests/run.sh`, the registry's
`--lint` (itself a step in `run.sh`) refuses it until the step is classified:
adding a gate without saying what it can miss is a defect the seed treats as
one.

#### G1 in detail — what the mechanical floor actually covers

`tools/agnosticism-lint.py` is the floor under G1 and G2, and the floor is
narrower than the definition it floors. State its real reach, because a clean
run reads like a verdict and is not one.

- It detects **host-IP literals** (loopback, unspecified, broadcast and the
  RFC 5737 documentation ranges excepted), **pinned CVE identifiers**, and any
  term passed as `--forbid`. That is all three of its rules.
- It detects **none** of the six classes in §What counts as a project reference
  unless the run supplies them as `--forbid`. Supplying them is the harvester's
  job: the seed cannot hardcode a plant's vocabulary without leaking it, which
  is why the tool takes it as an argument. Whatever is not supplied is G2, and
  G2 has no tool.
- **Its default glob is `*.md` alone, and a glob list is a coverage boundary.**
  A directory contributes only its glob matches, so a changed `.py`, `.sh`,
  `.json`, `.tsv`, `.yml`, `.toml` or extensionless script under a changed
  `--root` is never opened and produces no finding of any kind. There is no
  silent-skip signal to read: the tool models `unreadable` for a file it failed
  to read and has no concept of a file it never matched, so an unlisted
  extension is indistinguishable from a clean tree. This is why **G1 names its
  files instead of its extensions.** A `--file` is scanned whatever the globs
  say, and the changed set comes from git with no hand-kept list in it:

  ```bash
  args=()
  while IFS= read -r -d '' f; do args+=(--file="$f"); done \
      < <(git diff -z --name-only --diff-filter=d <pre-harvest rev>)
  if [ ${#args[@]} -eq 0 ]; then
      echo "no changed files: G1 has nothing to scan"   # a PASS here is a lie
  else
      python3 tools/agnosticism-lint.py "${args[@]}" \
          --forbid <plant token> --forbid <plant domain>
  fi
  ```

  The loop is not ceremony, and the obvious one-liner
  (`$(git diff --name-only … | sed 's|^|--file |')`) fails two ways that were
  reproduced before this was written. A changed path containing a **space**
  word-splits under the unquoted `$(...)`, and the tool exits 2 on
  `unrecognized arguments` — the gate does not skip that file, it dies. And with
  **no changed files** the substitution contributes no arguments at all, so
  `roots` falls back to its default of `.`: the run scans an unrelated superset
  of the tree and prints `PASS`, which reads as "the changed set is clean" and
  is not. `-z` with `read -d ''` also survives a newline in a path, and is bash
  3.2 (no `mapfile`, which this repo avoids for macOS).

  `--diff-filter=d` drops deletions, which would otherwise exit 2 as `no such
  path`. A changed binary comes back as `unreadable`, which is a BLOCK to judge,
  not noise to wave. Reach for `--root`/`--glob` only for a directory added
  whole, and then state in the proposal which extensions the run could see.
- Since 7.16.0 a file it cannot decode is reported as `unreadable` instead of
  skipped. For its whole life before that, a file the tool failed to open was
  indistinguishable from a clean one, and the skip even carried a rationale
  ("binary or unreadable: carries no prose") while its only glob was `*.md`.
  **Treat an `unreadable` finding as a BLOCK.** An unread input is UNKNOWN,
  and unknown is not green. It also exits 2 on a run that matched no file, so
  a mistyped `--root` cannot print the verdict a real scan earns.
- **The seed's own committed gate covers less than this run does.**
  `tests/seed-lint.py` runs the same detector over `core/ agents/ protocols/
  skills/ templates/` and the five corpora, with **no `--forbid` set** and the
  default `*.md` glob, plus `manifest.json`, `README.md` and `CHANGELOG.md`
  passed as **named files**, which are scanned whatever the glob says. So
  `docs/`, `tools/`, `tests/`, `integrations/`, `documentation/`, `install.sh`
  and the root prompt files sit outside the roots entirely, and inside the roots
  a `*.py`, `*.sh` or `*.tsv` file is never opened. A harvest that writes into
  any of them gets a green seed-lint that scanned none of it, and must scan them
  itself with `--root`/`--file`/`--glob`.

#### G4 in detail — reach is proven against `install.sh`, never against this file

6.12.0 asserted *"no change needed — the machinery was present"* for the legal
corpus. `install.sh` did not place it until 7.11.0, and the truth in between was
that it had **never placed it: not partially, not at all**. Every plant grown in
that window received an empty legal collection and an analyst whose only
available act was refusal, and a plant recorded that emptiness as a careful
deferral. The gate had satisfied itself by reading the withdraw contract further
down *this file*, which is this protocol's own prose. A withdraw contract is a
**claim about the installer**, and only the installer settles it.

So for every artifact a harvest adds, resolve its delivery path:

1. **Decide which arm it uses.** There are two, and which one applies is a fact
   about the consumer, not a style choice.
   - **Placed**: the installer copies it into the plant. Today exactly one
     corpus is placed, `legal-corpus/` → `docs/graph/legal/corpus/`, by
     `place_legal_corpus`, whole or not at all. It runs on the owner's explicit
     `--legal-corpus yes`, **and also with no flag at all** on a re-install:
     when the flag is absent and the plant already exists, the installer
     re-derives the decision from `legal_corpus` in `.cypress/seed.json` and
     restores the corpus to match the record. Placement can therefore happen on
     a run where nobody typed anything. The consumer has no filesystem reach to
     the seed, so an unplaced page is unreachable law.
   - **Read seed-side**: the corpus stays in the seed and the consuming node
     names its path formula. `library-corpus/`, `tool-corpus/`, `agent-corpus/`
     and `skill-corpus/` are all of this kind. `ingest-library.corpus-first`
     states the condition in the open: the corpus check is a **no-op** unless
     the session is working in the seed repo or the plant has harvested that
     corpus. A page added to one of these four reaches a plant only through a
     session that has the seed.
2. **Prove the placed arm against the installer, by discovery.** Run
   `bash tests/test-install-placement.sh`: it discovers the destination set from
   a real install rather than from a list, and reading what it discovers is the
   move. That test exists *because* a hardcoded list is how this defect class
   survived, as the installer grew bare `cp`s, a `cat >`, a `sed >` and
   embedded-Python writes that no list was ever updated to cover. Every
   destination a withdraw contract names must appear in the discovered set. A
   contract naming a path no placer produces is the 6.12.0 failure verbatim.

   A grep is the **weaker fallback**, for when no install can be run, and it is
   weaker in a way that matters: it sees only the writers someone thought to
   name. If you must, walk the composite placers (`place_docs_skeleton`,
   `place_graph_machinery`, `place_graph_scaffold`) into the single-file writers
   they call, and remember the writers that are not named `place_*` at all, such
   as `record_instruction_migration`, which writes a plant's
   `docs/graph/plans/adopted-instructions.md` with a bare `cat >`. Any list
   written here is out of date the next time a writer is added, which is why it
   is the fallback and not the step.
3. **Prove the seed-side arm against the consumer, and require a path formula.**
   A node that mentions a corpus without saying where a page lives establishes
   no reach. Two consumers meet that bar today:
   - `library-corpus/<ecosystem>/<library>.md` → `ingest-library.corpus-first`,
     which states the formula and the no-op condition;
   - `tool-corpus/<category>/<name>.md` and `skill-corpus/<name>.md` →
     `protocols/grow.md`, which states both formulas where it authors.

   The other mentions are pointers, not reach, and the gate records them as
   such: `skills/toolcraft/SKILL.md` names the two corpora in the harvest direction
   (folding IN, not withdrawing) and gives no path; `protocols/canonize.md`
   tells the librarian to check both first and gives no path;
   `core/method/delegation.md` and the orchestrator's charter name
   `agent-corpus/` and give no path. Where the consumer names the corpus but no
   formula, the only reach is a seed-side session's own filesystem. Say that in
   the proposal instead of claiming a contract, and treat the gap as exactly the
   inert-capability candidate Phase 1 tells you to harvest. A README that states
   the formula is documentation, not reach: a file nobody is instructed to open
   is not a path.

   **Where a page must also be in an index, and where an index is forbidden.**
   A consumer that can enumerate the directory is reached by the path formula
   alone, and a second listing would be a copy of the filesystem that drifts
   against it, so an enumerable corpus must **not** keep one. A consumer that
   **cannot** enumerate needs a routed `index.md`, because for that reader a
   missing row and a missing instrument are the same thing. Exactly one corpus
   is of the second kind: the legal corpus, read by an analyst with no
   filesystem reach whose whole discipline is that a gap produces a refusal. So
   a harvested legal page is in `legal-corpus/index.md` (and a decision in
   `legal-corpus/case-law/index.md`) or it is not reachable law, while a
   library, tool, expert or skill page is reached by its formula and gets no
   index at all. Nothing checks index membership; this one is the harvester's
   own read.
4. **Trace a harness-visible artifact to the harness.** An `agent-corpus` or
   `skill-corpus` entry is withdrawn by instantiating it into the project's
   `docs/graph/agents/` or `docs/graph/skills/<name>.md`; `install.sh`'s
   `project_agents` / `project_skills` then project the graph's **top level**
   into every harness roster on the next run. A withdraw path that terminates
   at `docs/graph/` and never reaches a harness is the hole four documents, this
   file among them, quietly wrote down as if it were the design, from 6.0.0
   until 7.15.0 closed it. Trace the last hop every time.
5. **A base-roster promotion must be present in every ground-truth surface**,
   and only some of them are held together by a tool. The surfaces are the agent
   file's frontmatter, `manifest.json`, the kernel roster line, the
   `method.delegation` specialist table, and `agents/_routes.golden.tsv`.
   `python3 tests/seed-lint.py` holds **three** of the five: frontmatter against
   `manifest.json`, and frontmatter against the kernel's §1 roster line. It never
   compares `agents/` to the delegation table, and it never opens the golden
   corpus, which `grep -c golden tests/seed-lint.py` confirms by returning 0.
   **A promoted agent missing from the delegation table or from
   `_routes.golden.tsv` passes this step green.** Open both by hand, name them
   in the proposal as hand-checked, and read the green as covering only the
   three it covers. Nothing at all checks that you *meant* to promote, which is
   the other half that is yours.

Record the resolved path per artifact in the proposal. "Reachable" with no path
named is the 6.12.0 sentence again. A harvested artifact no `install`/`grow`/
`graft` path can reach is an **INERT** import: it compounds nothing, and it is
the mirror of grow's *"grown, not just installed"* and graft's *"grown, not just
grafted"*. Material imported but not made available has not been harvested, only
stored.

#### G3 in detail — who judges a faithful import, and why it is not the author

The most recent harvest recorded *"Faithful import: PASS after correction — an
independent review found four passages thinned out of their donors and one page
that had inverted its donor's contract outright."* Five defects, none caught by
the gate as it was written, all caught by a reviewer who had not done the
import. That is the whole finding: an author comparing their own summary against
its source reads the summary and recognises it.

So G3's judge is a second Opus reviewer with the donor open, working
section by section, whose output is a per-artifact comparison and not a verdict
word. Reducing a full expert charter to a short blueprint, or a procedure to its
step titles, loses exactly the hard-won discipline the harvest exists to
compound, and reads like a clean summary while doing it.

### Phase 5 — Deliver (propose, do not impose)

Harvest **proposes**; the human steward **ratifies**. Emit the fold-back as a
reviewable patch/proposal against the seed with the harvest summary below,
never a silent mutation of the seed. The seed is deliberate, and its evolution
is too.

## The corpora — five withdraw contracts

Five corpora carry knowledge forward between plants: library, legal, tool,
suggested-expert, suggested-skill. They are what `grow`, `graft`,
`ingest-library`, `toolcraft` and `canonize` actually consume from the seed, and
each is defined by the same four questions: where it lives, what is portable,
what stays out, and the withdraw contract that delivers it.

**All three gates apply to every page of every corpus**: agnosticism (§the
agnosticism gate), durability (§the second gate) and non-redundancy (§the
third gate). Two carry an additional economy, stated in their own section: the
suggested-expert corpus is a catalog rather than a roster, and the legal corpus
is placed whole or not at all. No corpus is exempt from any of the three, and a
corpus section that names fewer than three is wrong. Three sections here said
"both gates" and a fourth named none, and they went on saying it long after
Phase 2 was corrected to "all three".

Every page also clears **G4**: each withdraw contract below is a claim about
what `install.sh` and the consuming node do, and G4 is where that claim is
checked against them rather than believed.

### The library & language documentation corpus

Ingesting a dependency is expensive: a scout downloads upstream docs, an author
normalizes and wikifies them into a version-pinned page. Most of that cost is
paid rediscovering the same **surface** every time, meaning what the library is,
its core API, how it is idiomatically used. That surface barely moves between
versions; only the pins, CVEs, and per-release quirks do. Harvest folds the
durable surface into a shared corpus in the seed so the next plant starts from
an orientation instead of a blank page, then ingests the version-specific
delta fresh.

- **Where it lives.** A seed-side corpus keyed by ecosystem + library,
  **not by version**: `library-corpus/<ecosystem>/<library>.md`. One page per
  library, describing the library in general, carrying its upstream doc/repo
  home as provenance. It is a cache of *library-surface* knowledge, never a
  second home for a plant's facts and never a version-pinned bulletin.
- **What is portable (surface, durable).** Only the version-durable surface:
  the capability the library provides, its core API shape and canonical usage,
  idioms and best practices that hold across releases, and conceptual pitfalls
  inherent to the tool. Strip every plant-specific usage example, path, and
  domain reference **and** every version-pinned specific before it lands. The
  page must read like the opening orientation of the library's own docs,
  usable by any project on any recent version.
- **What stays out (pinned, ephemeral).** Exact-version CVEs and advisories,
  "version X.Y.Z is a breaking marker" notes, deprecations introduced in a
  specific release, upgrade/migration diffs between two pins, and resolved
  version numbers. These live in the *plant's* `docs/graph/libraries/<name>.md`
  and are rediscovered per project, because they are wrong the moment the pin
  moves.
- **The withdraw contract (consumed by `ingest-library`, and by `grow` through
  it).** Read seed-side. `ingest-library.corpus-first` checks the corpus when
  the session is in the seed repo or the plant has harvested it, and is a no-op
  otherwise; `grow` reaches this corpus only by invoking `ingest-library`, and
  has no second path of its own. If a surface page exists, **seed the plant's
  `docs/graph/libraries/<name>.md` from it as the orientation layer**, then
  ingest from upstream only the version-specific facts the plant actually needs
  (the exact pin, its advisories, its deprecations) against the plant's real
  lockfile. If no surface page exists, ingest from upstream as usual, and the
  durable surface of that work becomes a harvest candidate for the next cycle.
  Never re-derive the surface the corpus already holds, and never trust the
  corpus for a pinned fact.
- **Currency.** A surface page ages slowly but not never, since an API redesign
  across a major line can outdate it. Treat it as orientation to confirm, not
  gospel to copy. Pinned facts are never read from here at all, so a stale pin
  cannot leak: the corpus simply has none to be stale.

### The legal & regulatory documentation corpus

Verifying a legal citation is expensive: a scout must find the official
publisher, get past whatever blocks a non-browser client, read the provision,
and correctly date the edition it actually read. Most of that cost is paid
rediscovering the same **primary text** every time, and that text is durable
far longer than any one plant's application of it, since a statute outlives
several codebases. Harvest folds the durable **citation** into a shared corpus
in the seed so the next plant that must comply with or reason about the same
body of law starts from a sourced orientation instead of a blank page, then
confirms currency and derives its own application fresh.

- **Where it lives.** A seed-side corpus keyed by jurisdiction scope +
  instrument, **not by the plant reading it**:
  `legal-corpus/<scope>/<instrument-slug>.md`, where `<scope>` is `eu`,
  `national` (country-code-prefixed filename), `international` (global standards
  bodies), or `case-law` (judicial and regulator decisions, which span
  jurisdictions and so get their own scope). One page per instrument, its entry
  shape fixed by `legal-corpus/_schema.md` and routed by `legal-corpus/index.md`.
  It is a cache of *citation* knowledge, never a second home for a plant's
  compliance findings.
- **What is portable (citation, durable).** The citable entry itself: the
  instrument in full official form, the provision, its text graded by
  `text_form`, the official publisher URL, the `verification_grade` and
  verification date, and the `legal_status` on that date, plus the blockage that
  stopped a primary fetch, and any *verified absence* (a searched-for decision
  found not to exist). Inside its own scope a citation is as reusable as a
  library's API surface, because the law says the same thing to every project
  subject to it. Strip every plant-specific application and every
  unstated-edition citation before it lands.
- **What stays out (application, plant-bound).** Any application of the law to a
  system, meaning how a plant's architecture does or does not trigger a
  provision, and every finding, risk posture, gap, remediation status,
  source-file or component reference used to ground one, and every
  in-scope/compliant/exposed determination. These live in the *plant's* own
  `docs/graph/legal/` (or equivalent), generated fresh per project **against**
  the corpus as its orientation layer. The corpus states what the law says; the
  plant states what that means for one system. Legal analysis feels portable and
  is not, which makes this the sharpest agnosticism boundary of the five
  corpora.
- **The withdraw contract (consumed by `grow` / `graft`).** This is the one
  corpus the installer **places**: `place_legal_corpus` copies it WHOLE into
  the plant's `docs/graph/legal/corpus/`, and refuses a partial copy, because
  the consuming analyst turns a corpus gap into a refusal and a subset therefore
  reads as a smaller body of law instead of a missing one. It runs on the
  owner's explicit `--legal-corpus yes`, and on a re-install it also runs with
  no flag, from the `legal_corpus` decision the plant recorded in
  `.cypress/seed.json` (G4 step 1). The installer also reports which national
  jurisdictions the corpus carries against `--legal-jurisdiction`, so a country
  the corpus does not hold is recorded as absent instead of inferred. With the
  corpus in hand, a plant seeds its legal leaf from the matching entries as the
  orientation layer, re-confirms each entry's `verified` + `legal_status` before
  relying on it, then authors its own application against it. If no page exists,
  ingest from the official publisher as usual, and the durable, graded citation
  from that work becomes a harvest candidate for the next cycle. Never re-derive
  a citation the corpus already holds, and never read a plant's determination
  out of it, because there are none in it to read.
- **Currency.** A citation ages more slowly than a library API, but law amends,
  transposes, is annulled, and comes under appeal. Treat an entry as orientation
  to confirm, not gospel to copy. Two disciplines are non-negotiable and are why
  a stale entry cannot quietly pass as current. An entry must state whether its
  text is the **original** or the **consolidated/as-amended** edition, the
  *amendment trap*, where an unamended reading of an amended instrument reads
  exactly like a correct one. And a `verification_grade` is **never upgraded
  without a new fetch**: downgrading on new evidence is expected, while
  upgrading without re-reading the source is falsification.

### The reusable-tool corpus

A plant builds durable tools during its life (`toolcraft`, kernel §3.8) and
catalogs them in `docs/graph/tools/`. Most of a tool's value is not the one
project's wiring but the **capability and approach**: what it does, its
interface, the algorithm behind it. When that is genuinely stack-neutral,
harvest folds it into a shared corpus in the seed so the next plant starts from
a working tool or a clear blueprint instead of reinventing the wheel.

- **Where it lives.** A seed-side corpus keyed by category + tool, **not by
  project**: `tool-corpus/<category>/<name>.md`. One page per tool, describing
  the tool in general. It is a cache of *reusable-tool* knowledge, never a second
  home for a plant's operations.
- **What is portable (durable).** The capability and the recurring operation it
  serves; the interface shape (invocation, inputs, outputs) in the general; the
  approach/algorithm and enduring idioms; the portable implementation **when the
  tool is genuinely stack-neutral** (a self-contained script with no third-party
  or project dependencies, like the seed's own `graph-lint.py` /
  `agent-lint.py`). Strip every plant path, credential and domain reference
  **and** every stack-pinned specific before it lands.
- **What stays out (project-bound, ephemeral).** Project names, paths,
  credentials, dataset shapes, a call-site tied to one repo's layout, a
  version-locked dependency, an environment only this project has. These live in
  the *plant's* `docs/graph/tools/<name>.md` and never in the seed.
- **The withdraw contract (consumed by `grow`; pointed at by `toolcraft` /
  `canonize`).** Read seed-side. The node that states the path formula is
  `protocols/grow.md`, where growth seeds `docs/graph/tools/<name>.md` from
  `tool-corpus/<category>/<name>.md` when the plant's real stack matches a
  portable tool the corpus carries. `toolcraft` names this corpus in the harvest
  direction and `canonize` tells the librarian to check it first; neither states
  where a page lives, so neither is reach on its own (G4 step 3). When a new
  plant needs a capability, it checks the corpus FIRST: if a matching tool
  exists, **seed `docs/graph/tools/<name>.md` from it as the orientation
  layer**, adopting the portable implementation when the stack matches, or
  re-authoring against the plant's own stack (test-first) when it does not. If
  no tool exists, build it fresh, and the durable, agnostic surface of that work
  becomes a harvest candidate for the next cycle.
- **Currency.** A tool page ages slowly but not never, since an approach can be
  superseded. Treat it as orientation to confirm and adapt, not gospel to copy.

### The suggested-expert corpus

The roster mirror of the library and tool corpora. A plant sometimes needs a
specialist the base roster lacks and commissions one, not because a stack was
unfamiliar (a plant closes a *knowledge* gap with an expertise node of its own,
which the router composes into the roster it already has) but because some work
needs its own tools, model class, stance, or isolation. Most of that role's
value sits in its **mandate**: what it owns, when to
select it, how it bounds against the base roster. Its stack wiring is the part
that does not travel. When that mandate is
genuinely stack-neutral, harvest folds it into a seed-side catalog so the next
plant selects a ready role instead of reinventing it.

The roster's own economy applies on top of the three gates: the base team is
paid on every session of every plant, so a harvested role lands in the
**catalog** by default, never straight into the always-loaded roster.

**Promotion to the base roster is a separate, steward-only decision**, and the
bar is higher than "useful". The role's mandate must be **universal**, meaning
every project produces the thing it addresses rather than merely many of them,
and no base-roster agent may already cover it. A role that serves a domain some
projects simply do not have (a regulatory analyst, a stack specialist) stays in
the catalog however good it is, because the catalog costs nothing until
selected. Harvest may *propose* a promotion; it never performs one, and a
promotion that is ratified clears G4 step 5 before it is real.

- **Where it lives.** `agent-corpus/<name>.md`, one page per suggested role,
  keyed by role, not project. A catalog of *candidate* experts, never the
  active roster.
- **What is portable (durable).** The role's mandate, its when-to-select, its
  boundary against the base roster, and its `routing_triggers` exemplars, all
  statable with zero framework names.
- **What stays out.** A stack-specific expert (a framework/language/library
  specialist), and any role that duplicates a base-roster mandate. The first
  is the plant's own knowledge, which belongs in its expertise nodes against
  its own pins rather than in any roster; the second breaks one-home-per-fact.
- **The withdraw contract (consumed by `grow` / `graft` / commission).** Read
  seed-side. `core/method/delegation.md` and the orchestrator's charter both
  send a commissioning session here, and neither states the path formula, so
  the reach is a seed-side session's filesystem and G4 step 3 records it that
  way. When a project needs a role the base roster lacks, check the corpus
  FIRST: if a match exists, instantiate it into the project's
  `docs/graph/agents/` from `docs/graph/templates/agent.template.md`, grounded
  in the project's version-pinned facts and the role's mandate + triggers; the
  harness projections (`.claude/agents/` and kin) are regenerated **from that
  graph home** by the next `install.sh` run, which is the hop that makes the
  role spawnable. Else commission fresh, and its durable, agnostic mandate
  becomes a harvest candidate. A selected role joins the *project's* roster
  (and its kernel table), never the seed's.

### The suggested-skill corpus

The procedure mirror of the corpora above. A plant sometimes authors a
project **skill**, a repeatable procedure such as a migration recipe or a
release choreography, that is not stack-bound and would serve any project.
Harvest folds its agnostic form into a seed-side catalog so the next plant
instantiates a ready procedure instead of rediscovering the sequence.

- **Where it lives.** `skill-corpus/<name>.md`, one page per suggested
  procedure, keyed by procedure, not project. The core `skills/` stay the fixed
  shared methodology; this corpus holds *optional* procedures a project selects.
- **What is portable (durable).** The procedure's steps and the gate each one
  clears, stated by **composing** existing protocols/skills by reference,
  never a stack-bound recipe and never a restatement of a discipline the seed
  already owns (one home per procedure).
- **What stays out.** A procedure bound to one stack or repo layout (the
  plant's own), and anything duplicating a core skill.
- **The withdraw contract (consumed by `grow`; pointed at by `toolcraft` /
  `canonize` / commission).** Read seed-side. `protocols/grow.md` is the node
  that states the formula, seeding `docs/graph/skills/<name>.md` from
  `skill-corpus/<name>.md` where a repeatable procedure the source actually
  performs matches an entry; `canonize` tells the librarian to check the corpus
  first without saying where it lives (G4 step 3). Check the corpus first; if a
  match exists, instantiate it into the project's `docs/graph/skills/<name>.md`
  from `docs/graph/templates/skill.template.md`, grounding its steps in the
  project's real gates and tools. `install.sh` then projects that graph home
  into `.claude/skills/<name>/SKILL.md` and kin on the next run, the same as any
  seed skill. Else author it fresh, and its durable form becomes a harvest
  candidate. This contract was edited to match broken installer behaviour once
  and stood wrong from 6.0.0 until 7.15.0; its last hop is the one G4 step 4
  exists to re-verify on every harvest, not to take on this file's word.

## Output format

Harvest produces **two distinct records, and they do not carry the same
content**:

1. **The ratification proposal**, stated in chat or the PR for the steward to
   review. It *may* name the plant and show every before→after generalization,
   because it is the evidence the steward weighs. It is **never committed to the
   seed.**
2. **The seed-committed record**, the CHANGELOG entry and harvest-log row that
   land *inside* the seed. Bound by the agnosticism gate exactly like any other
   seed artifact: no plant name, stack fingerprint, identifying count,
   internal-component name, path, or "from <this stack> plant" line. It records
   *that* a harvest happened and *what* generalized lesson landed, never *whose*
   plant it came from.

**Proposal — to the steward, may reference the plant, NOT committed:**

```markdown
# Harvest proposal — from <plant lineage id> — YYYY-MM-DD

## Harvested (generalized fold-backs)
- <seed file touched> — lesson: <universal statement> — generalized-from:
  <plant surface> — before→after: <what was stripped to make it agnostic>
- ...

## Rejected (stayed in the plant)
- <candidate> — reason it is not project-agnostic

## Provenance ledger
- <one row per fold-back: plant lineage, source surface, seed target, test added>

## Seed integrity gate (the result column; the plant may be named here)
- <one line per row of the Phase 4 gate table, in its order, no row omitted.
  A row that names a command reports `<id>: PASS — <command> → <result>` or
  `BLOCK (<what>)`. A `judgment` row reports `<id>: PASS — judged by <who>,
  evidence: <where it can be read>`. A row with no result is a blank cell, and
  a blank cell is the green lie the table exists to prevent.
  G4's line expands to one row per artifact: arm (placed / seed-side),
  resolved path (the `place_*` call the discovery found, or the consuming node
  and its path formula), last hop (harness projection, roster surface, or n/a).>

## Recommended next step
<single highest-leverage action — usually "ratify and merge" or "one more
candidate to generalize">
```

**Seed-committed harvest-log — agnostic, no plant identity — this is what
enters the CHANGELOG (and `HARVEST_LOG.md` if the seed keeps one):**

```markdown
# Harvest — from a grown plant — YYYY-MM-DD

Harvested:   <count + kind of generalized fold-backs, e.g. "3 corpus pages;
             6 doctrine/template rules"> — no plant identity.
Generalized: every plant name/domain/path/credential/host/port, every stack
             fingerprint and identifying count, and every version pin stripped.
Rejected:    <generic categories only, e.g. "internal/proprietary pages;
             kernel/agent duplicates">.

## Seed integrity gate (verdicts only; no command, no output, no path)
- <id>: PASS
- <id>: BLOCK (<seed-side reason, e.g. "a rule the seed already owned">)
- <one such line per row of the Phase 4 gate table, in its order, no row
  omitted. The id and the verdict, nothing else: the evidence that produced
  the verdict is the proposal's. A row with no verdict is a blank cell, and a
  blank cell is the green lie the gate table exists to prevent.>
- Version bump: <old> → <new>
```

**Why the committed record carries no evidence.** It is bound by the
agnosticism gate, and a gate's own result string is made of plant identity:
G1's command is the plant's forbidden-token list spelled out, G5's result is
`git -C <plant> status` output, G4's is resolved paths. Printing
`<command> → <result>` into the seed would route every class in §What counts as
a project reference through this protocol's own output template, which is the
4.8.0 contamination class arriving by the door built to stop it. The evidence
lives in the proposal, where naming the plant is the point; the seed keeps the
roll-call.

The gate table is the single home of the rows. The proposal's block is their
result column, and the committed record is their verdict column. Adding a gate
means adding a row to that table, and nothing in either record here.

## Quality bar

Everything the Phase 4 table asserts is asserted *there*, and the discipline of
each phase is stated in that phase. What is left is the judgment neither one
carries: what a *good* harvest looks like once every row of that table is green.

- **It leaves the seed more capable, and that is not the same as landing
  something.** A harvest that lands nothing because nothing generalized is a
  correct and complete outcome, and says so in the proposal. A harvest that
  lands a rule the seed already owned is a failure with every row green.
- **The steward weighs evidence, not a verdict.** Every fold-back reaches
  ratification with its before→after (Phase 2) and its resolved delivery path
  (G4) legible, because a proposal the steward cannot check is a request for
  trust, and the one recorded seed contamination was landed by a harvest
  everyone trusted.
- **The seed reads as one author afterwards.** An import that is agnostic,
  faithful and reachable but audibly written by somebody else has been stored
  rather than integrated (Phase 3, G8).

## What you do not do

Prohibitions with a gate are not restated here. Copying plant identity is
**G1**/**G2**, thinning an import is **G3**, leaving an import inert is **G4**,
writing to the donor plant is **G5**, reporting green from a partial run is
**G6**, breaking a clean install is **G7**, bumping the version without
provenance is **G10**, and widening a limit to make a fold-back fit is **G11**.
What remains:

- You do not start a harvest on your own. It is user-triggered, and the most an
  agent does unprompted is *propose* one and stop. Never automatic, never a
  hook, never a tail-end step of another protocol.
- You do not merge a fold-back the user has not ratified; an unratified harvest
  is a draft. The user must be satisfied with the seed's growth first, and the
  seed is never silently mutated.
- You do not harvest a plant that is still churning; wait for maturity.
- You do not harvest a self-healing / diagnostic case **narrative**; you
  harvest only its generalized prevention rule, recast tool-neutrally.
- You do not harvest the plant's `docs/graph/` content. That is the plant's
  life, not the seed's.
- You do not bolt a special case onto a seed artifact. A fold-back is
  integrated as if it had always been there, or it is not landed.
- You do not trade a gate for a lesson. A candidate that cannot clear G1 through
  G11 stays in the plant, with the reason recorded. The gates are not the price
  of a fold-back, they are its definition.
