## 7.30.0 — a harvest: cheaper cycles in the open, sharper doctrine, and new corpus pages (2026-09-26)

A grown plant was harvested back into the seed. What follows is the generalized
residue: no plant identity, no stack, no counts that belong to any project.
The seed owner then decided the proposed rule changes. The adopted ones ship
here under SPEC-0005 (`docs/specs/SPEC-0005-cycle-economy.md`), built with
the rules they introduce. The ones the owner declined (a thin spec grown by
slice, a walking skeleton, a candidate implementation counted as GREEN,
standing grants, among others) are not in this release.

**The humanizer is rebuilt on the owner's evolved catalogue.** The skill's
substance is now a 36-pattern diagnostic catalogue with context exceptions, a
contract of invariants, a diagnose-before-rewrite procedure, a language and
grammar check, a worked audit and separate pattern, meaning and reader checks.
The prose-posture links, the prose-lint floor and the execution sites are kept.
Its description is unchanged.

**Delegation carries lanes, briefs by file and light variants.** One writer per
file set, measured on files; a worker outside a shared artifact's lane lists
the rows to change and the lane holder applies them. Handbacks and shared rules
travel by file path. A prohibition names its alternative. No concurrency cap is
invented. Spawn ids are never minted after the fact. A light variant for small,
mechanical work is adopted, and never runs on a security surface.
Effort refines a model class and is kept apart from the owner's effort level.

**A cheaper development cycle (SPEC-0005).** A batch of increments is sized
from its effort label and dependencies, never fixed: a tester writes five to
seven or more REDs per spawn, an implementer takes one to five GREENs, and
security or concurrency code is always a batch of one. The implementer runs
the tests itself and never edits them; the orchestrator records a hash of
each RED and refuses a commit that changed one. Each increment runs its
targeted tests and the gates its files touch, and the full suite runs once at
the batch tip. A worker that meets an ambiguity writes it to the batch's
question file and keeps working; when the batch lands, the architect rules on
every question in one pass, and a ruling that relaxes a contract, or amends
one on a security, data-integrity or money surface, goes to the owner first.
Mutation runs once at the end of a spec, mandatory for security,
data-integrity and money contracts and sampled elsewhere. Specify and grill
run as one joint pass, which first asks how much design latitude the work
has, from creative to as simple as possible.

**Spawn effort is regulated.** Every agent definition declares a default
`effort:` (low, medium or high), and agent-lint refuses a missing or unknown
value. A spawn's effort is derived from its step kind and its batch's hardest
effort label, forced to high for security, contracts and rulings; the brief
names it and the handback echoes it. Claude Code reads the key from agent
frontmatter; whether other hosts do is not recorded.

**Expertise reaches the worker that needs it.** `--plan` now loads an
expertise node whose whole trigger phrase the task names, even past the
scored cut, and infers expertise from the file paths a task names, matched
against file patterns in `load_when` by string alone, capped and never
raising. The stack-expertise step is mandatory in every code brief, and a
worker that finds it needs expertise mid-work looks it up, or names the gap
in a new `expertise_gap:` handback field so the caller can request
`research-scout` to build the node.
Reachability now follows the edges of nodes the index lists.

**Nodes are menus; leaves stay small.** The leaves, children and neighbours a
node lists are a menu: a session opens only the items whose one-line "load
when" serves the task. A branch node is that menu plus only the doctrine every
leaf needs. The delegation node is split verbatim into six sibling leaves,
engineering posture into five, design posture into four and verify into
three, so a typical task loads a fraction of each. A leaf ceiling of 170 body
lines holds new leaves, with a ledger of the existing oversized ones that can
only shrink.

**Four boundaries.** Inspecting a shared host never writes; a claim that a
change works cites the execution target or real CI; the graph outranks a
harness's default working style; no test is added only to turn a lint green.

**New checks.** agent-lint gains the effort rule. seed-lint gains the leaf
ceiling, the delegation split, the adopted rule homes (one owner per key, no
pointer to a moved key's old home), the two handback fields, the exact
bootstrap step 2 and a refusal of adopted rules still worded as pending.

**Protocols gain evidence rules, not new gates.** Grill gains a conditional
plan-approval ask (the cost levers the plant's doctrine defines and every
owner-only prerequisite, asked once) and a planned test-consolidation
increment. Verify gains the value-or-spelling question, the chronic-red mirror
of the vacuous green, and "a passed configuration is not an applied one".
Recover probes cheaply before theorizing and treats a permission refusal of an
owner-directed action as systemic. Deliver takes the metrics block after each
landed increment, with class, full-suite runs, serial waits and a quality line,
and stops a loop when only the owner can act. Canonize reads every handback
overflow note. New obligations are written as "before claiming X, show Y".

**Posture sharpened.** Failures leave their logs; a log is also a command
channel; merging to test is publishing; an override-only fix is borrowed, not
deployed; durable owner rules live in the graph, not in harness memory; a
load-bearing value is derived from its consumer; a run is identified by the id
its tool returned; every artifact carries one of three maintenance contracts.

**Linters fixed, with regression tests.** grill-lint ignores fenced examples,
reads a fenced field value as a value and fails an increment heading outside
section 9. spec-lint names the draft specs it did not check, warns when a
tested draft missed its promotion, and gains a print-only `--slice` reader
that uses the same fence rule. Two install tests no longer abort on a findings
exit that they meant to tolerate. The migration-date install test pins its clock, so
it no longer fails between local and UTC midnight.

**New corpus pages.** A portable, tested parallel suite runner that compares
failures by test id and fails closed on an empty or unreadable run. Tool
blueprints for a static config contract gate, N-way parity, test hygiene,
consumer link generation, a chained pipeline-run driver, a session cost
profiler, a registry digest resolver and a hashed-lock closure check. Library
surface pages for Node.js, PostgreSQL, Qdrant, Redis, Bandit, CycloneDX and a
hosted CI REST API, a new `cli` ecosystem for curl and git (ingest-library now
says where host-supplied tools live), and version-durable sharpenings across
the language, container, PyPI, NuGet and npm pages. A skill-corpus procedure
for triaging an unresolved required variable. Templates for a findings report
and an operator working-style node (an existing node kind), and a best-practices
shelf contract.

**Reach.** graph-lint, spec-lint, grill-lint and the docs scaffold are placed
only when missing, so existing plants receive their changes through graft.
agent-lint is different: the installer fast-forwards it on any re-install, so
after either a graft or a re-install it requires an `effort:` line on every
agent, the plant's own commissioned experts and light variants included.
Through graft, a plant also receives:
- `--plan` promotes an expertise node whose whole trigger phrase the task
  names, uncapped, on the per-prompt route hook too;
- a `load_when` piece with no whitespace that contains `/` or `*` now reads as
  a file pattern (a plant piece such as `CI/CD` becomes one);
- reachability follows the edges of nodes the index lists, so a plant's own
  `index.md`, which graft leaves untouched, reaches the new delegation leaves
  through its existing delegation row;
- the grill template's `Effort:` field is now a label, with a `Phase:` field
  and a `Design latitude:` row;
- a batch's questions go to a shared question file,
  `docs/graph/plans/<unit of work>/questions/batch-<N>.md`.

### Harvest log

```
# Harvest — from a grown plant — 2026-09-26
Harvested:   a rebuilt prose skill; doctrine sharpenings across delegation,
             five protocols and eleven method nodes; two linter fixes and two
             install-test fixes, each with regression tests; one tested
             portable tool and eight tool blueprints; nine new library
             surface pages and a new ecosystem, plus sharpenings across the
             library corpus; one skill-corpus procedure; three templates.
             No plant identity.
Generalized: every plant name, domain term, path, host, credential, finding,
             identifying count, stack fingerprint and version pin stripped;
             before->after held per candidate in triage.
Rejected:    candidates the seed already owned (the donor carried older
             copies of several seed files); per-stack expert agents (a stack
             gap closes as an expertise node); pinned version bulletins; the
             plant's application-specific rules.
Decided:     the owner decided the proposed rule changes; the adopted ones
             ship under SPEC-0005, built with the rules they introduce.
Held:        items listed for the owner's review (lifecycle-protocol splits,
             one template contract clarification, a minimum Python version,
             the wording of the real-CI rule) and the round's rulings the
             owner may still change (no kernel menu rule, the withdrawn
             leaf-list lint, the mutation scope reading, plant `effort:`).
