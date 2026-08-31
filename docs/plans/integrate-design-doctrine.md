# Implementation plan — integrate the SOLID / separation-of-responsibilities doctrine into the seed

**Status:** EXECUTED (shipped in 5.7.0), then **SUPERSEDED by 6.0.0**. The
design doctrine this plan installed now lives as the routable posture node
`core/method/design-posture.md` (`method.design-posture`, kernel §3-adjacent),
and the minimum-sufficiency doctrine as `method.engineering-posture` — reached
on demand through the router, not through agent prompts. **This plan's §0
Context is pre-6.0 and no longer describes the seed:** the kernel is a ~7 KB
bootstrap (not 20,940 bytes), and `core/operating-principles.md` is a tombstone,
not the doctrine's home. Kept as a historical record of the 5.7 work; do not
execute it against the current seed. See CHANGELOG 5.7.0 and 6.0.0.

**For:** a clean-context executing agent.
**Goal:** install a distilled SOLID + separation-of-responsibilities design
posture into CYPRESS as an on-demand reference that always guides code and
content authoring — **without** adding a file, spending kernel bytes, or
duplicating any fact that already has a home.

This plan is self-contained. Do not consult chat history; everything you
need is below. Execute the steps in order, then run the verification gate.

---

## 0. Context you need (read once)

This repository **is** the CYPRESS seed — the product shipped to target
projects, not a grown project. Its own working rules are in `CLAUDE.md`.

Relevant homes:

- `core/AGENTS.md` — the **kernel**, loaded on every session of every plant.
  It is at **20,940 / 21,000 bytes** (`tests/seed-lint.py` fails past
  budget). **You will not touch it.** The doctrine is reference-tier and
  reaches agents the same way the existing posture file does — via the
  agent prompts and the manifest, never via kernel bytes.
- `core/operating-principles.md` — the manifest calls this *"the deep
  version of the engineering posture sketched in AGENTS.md — an on-demand
  reference, never always-loaded."* It is a numbered list of 16 principles.
  **This is the canonical home for the new doctrine.** Software-structure
  discipline (SOLID, cohesion, coupling) is engineering posture; it belongs
  here, integrated, not in a new parallel file. Adding a file would commit
  the exact anti-pattern the doctrine names ("more files mistaken for more
  separation").
- Authoring agents that must be guided by it: `agents/01-architect.md`,
  `agents/02-implementer.md`, `agents/03-reviewer.md`.
- `manifest.json` — carries a top-level `principles[]` array and the
  `version`.
- `CHANGELOG.md` — append-only; supersede, never rewrite.

## 1. Invariants you must hold (these are the point of the exercise)

You are installing a doctrine about good structure; obey it while you do.

1. **One home per fact.** State each principle once. Where the doctrine
   overlaps a principle that already exists, **fold a sentence into the
   existing principle and link it** — do not restate it. The three
   overlaps and their existing homes:
   - *side effects at a named boundary* → already `operating-principles.md`
     §8 (and applied in the architect/implementer/reviewer prompts).
   - *integrate, do not patch / delete-and-consolidate* → already §5 (and
     `skills/holistic-editing/SKILL.md`).
   - *minimum behavior, nothing speculative* → already the implementer
     prompt (lines 21–24) and kernel §3.4 / op-principles §2.
2. **Integrate, don't bolt on.** The new principles go in a coherent
   cluster placed with their kin (right after §8), and the tail is
   renumbered so the file reads as if they had always been there. Appending
   after §16 is a bolt-on — do not.
3. **Smallest structure that fits.** No new file, no new skill, no new lint
   check, no new manifest kernel entry. The footprint below is deliberate
   and complete.
4. **Kernel is untouched.** Zero bytes added to `core/AGENTS.md`.

## 2. Pre-flight (confirm the renumber is safe)

The cluster is inserted after §8 and the current §9–§16 shift down by 7
(to §16–§23). §1–§8 keep their numbers, so any cross-reference to §1–§8 is
unaffected. Before editing, confirm nothing outside the file pins a section
number of this file:

```
grep -rn "operating-principles" --include='*.md' --include='*.json' \
  --include='*.py' . | grep -v CHANGELOG | grep -v '.git'
```

Expected: only `README.md` (names the file, no section number) and
`manifest.json` (describes the file, no section number). If any hit cites a
specific `§N` of `operating-principles.md`, stop and report it — the
renumber would break it and this plan must be revised.

Also note the **internal** cross-references inside `operating-principles.md`
that point at sections that will move:
- §2 cites "(see §5)" — §5 does not move. No change.
- §16 (Build tools to last) cites "(§5)", "(§6)", and **"(§14)"**. §5 and §6
  do not move; **§14 → §21**, so that one reference must be updated in
  Step 4.

---

## 3. Step 1 — fold the two overlaps into their existing homes

### 3a. `core/operating-principles.md` §5 (Integrate; do not patch)

Find this sentence in §5:

> Deleting and consolidating are first-class outcomes. Stay within the file and the direct consequences of the request; unrelated issues are their own increment.

Replace it with:

> Deleting and consolidating are first-class outcomes — remove duplicated *policy* and second sources of truth as you go, though code that merely looks alike while meaning something different is left alone (§10). Stay within the file and the direct consequences of the request; unrelated issues are their own increment.

### 3b. `core/operating-principles.md` §8 (Make side effects visible and testable)

The section body currently ends:

> …Tests run without the boundaries by substituting fakes that honor the same contract as the real adapter.

Append one sentence so it ends:

> …Tests run without the boundaries by substituting fakes that honor the same contract as the real adapter. This is dependency inversion made concrete (§12): the boundary is the stable contract; the adapter is the volatile detail the domain refuses to import.

---

## 4. Step 2 — insert the design cluster and renumber the tail

In `core/operating-principles.md`, **insert the seven principles below
immediately after the end of §8 and before the current `## 9. Record
decisions; do not editorialize`**. Then **renumber the current §9–§16 to
§16–§23** (headings only; +7 to each), and in the renumbered tools
principle (was §16, now §23) change its "(§14)" citation to **"(§21)"**.

Insert verbatim:

```markdown
## 9. Design for the smallest structure that fits

Separation is a tool, not a quota. Give each part one coherent
responsibility, keep cohesive things together, and point dependencies at
stable contracts — but the goal is *correct* separation, never *maximum*.
A design is not better for holding more classes, interfaces, layers, or
files; more files is not more separation. When these principles conflict
with the project's specs, idioms, ADRs, or a framework's conventions, those
win. Apply the rest of this section where it earns its keep and nowhere it
does not.

## 10. Responsibilities are reasons to change

A responsibility is a coherent obligation — a policy, a capability, an owned
piece of state, a reason the code changes. Give a component one, keep
together what changes together, and split apart what changes for different
reasons, has different owners, or has different failure or security
semantics. Judge this by what forces the code to change, not by its size: a
large cohesive module is fine; a small one mixing unrelated policies is not.
Do not split when splitting would scatter one invariant across components,
obscure the main flow, or trade visible coupling for hidden coupling.

## 11. Cohesion and coupling are the real metrics

Weak cohesion shows up as unrelated field groups, methods that share no
state, and consumers that use disjoint slices — signals to investigate, not
automatic verdicts. For coupling, the *count* of dependencies matters less
than their **direction** and **stability**: a few hidden dependencies are
worse than many explicit ones. Keep coupling explicit, avoid shared mutable
state and needless temporal ordering, and never let a dependency cycle
stand. Prefer a direct call to indirection that only relocates the same
coupling.

## 12. Depend on stable contracts, not volatile detail

High-level policy does not depend on volatile implementation detail; both
depend on a stable contract at a meaningful boundary. Invert the dependency
when the detail is external, nondeterministic, or likely to have more than
one implementation — using the smallest mechanism that does it: a
parameter, a function, an interface, an adapter. This is §8 seen from the
design side — the named side-effect boundary *is* the inverted dependency.
Passing a collaborator through a constructor is not inversion; dependency
injection is not dependency inversion. A stable, local, explicit direct
dependency needs no ceremony.

## 13. Honor contracts at type boundaries

Define an interface around what a consumer actually needs: no consumer
should depend on operations it does not use, and no implementor should have
to fake behavior it cannot provide. A subtype must keep the whole promise of
its base — no strengthened preconditions, no weakened guarantees, no
unsupported-operation holes, no forcing callers to check its concrete type.
Use inheritance only where that substitutability genuinely holds; otherwise
compose. Do not split an interface whose operations form one capability, and
do not mint one-method interfaces without a real substitution, testing, or
domain boundary behind them.

## 14. Own state; separate deciding from sequencing

Give every piece of stateful behavior one owner that guards its invariants,
and expose behavior rather than raw mutation where that keeps the invariant
true. Keep *policy* — what is allowed, how an outcome is computed, which
invariant must hold — separate from *orchestration* — sequence, retries,
transaction scope, error translation — so infrastructure mechanics do not
entangle domain decisions. Put validation and error handling where the
decision lives: validate a rule next to the rule, handle a failure at the
layer that can actually decide, and neither dilute one rule across every
layer nor funnel every error into one generic type. Do not split
coordination from policy when they are one simple, cohesive act.

## 15. Abstract only where variation is real

Design an extension point where variation already exists and recurs, not for
a future you are guessing at. Before adding a plugin seam, base class,
factory, or strategy, ask whether the variation is here yet and whether
direct modification would simply be clearer — often it is. An abstraction
earns its place by *reducing* meaningful coupling; one that mirrors a single
implementation, forwards every call unchanged, or exists only to satisfy a
principle by name adds indirection without subtracting anything. Remove such
structure when you find it — over-abstraction is a defect, exactly as
under-abstraction is.

**Applying this to a change.** Before adding structure, ask: what
responsibility is this, and who owns it? Does anything here change for a
different reason than its neighbors? Is a dependency pointing at a volatile
detail it should not know? Does this abstraction remove coupling, or only
move it? Would the smallest version — a function, a parameter, deleting a
duplication — do? If a smaller change solves the real problem, it is the
better change. This posture governs *knowledge* as much as code: one home
per fact (kernel §3.2) is the single-responsibility rule for the graph, and
a node that owns unrelated facts has the same weak cohesion a class would.

**Anti-patterns.** One class per method; one interface per class;
pass-through layers; dependency injection without inversion; generic
managers, helpers, or processors with no owned responsibility; factories for
trivial construction; strategies for variation that does not exist;
inheritance for code reuse alone; an event bus replacing a clear direct
call; duplicated policy across layers; more files mistaken for more
separation.
```

After the edit, the file's principle order is: §1–§8 (unchanged), §9–§15
(new cluster above), §16 Record decisions, §17 Treat model output as
untrusted, §18 Never source test/demo data from production, §19 Convert
ambiguity into artifacts, §20 Verify at the level where failure is most
informative, §21 The knowledge graph and the spec catalog compound, §22 End
every session in a known state, §23 Build tools to last.

---

## 5. Step 3 — the one-line canonical statement in `manifest.json`

`principles[]` currently has 10 strings; the last is the toolcraft one
(begins "Toolcraft:"). **Append** this 11th entry after it (mind the comma
on the previous line):

```json
    "Design for responsibility: give each part one coherent responsibility, keep cohesive things together, and point dependencies at stable contracts rather than volatile detail — but prefer the smallest structure that fits; correct separation is the goal, never maximum. Depth in core/operating-principles.md."
```

In the same file, bump the version:

```
"version": "5.5.0"   ->   "version": "5.6.0"
```

Do **not** add anything to the `kernel` object (no new file exists) and do
**not** change the `README.md` core line (it already names
`operating-principles`).

---

## 6. Step 4 — wire the three authoring agents (thin pointers, folded into kin)

These are links to the home, not restatements. Keep them minimal.

### 6a. `agents/03-reviewer.md` — extend the existing checklist block

Find the block:

```markdown
**Architecture adherence**
- Are the boundaries from the architect's design respected?
- Are domain modules free of transport/storage/vendor imports?
- Are side effects at named adapters?
```

Replace it with:

```markdown
**Architecture & responsibilities** (the design posture: `core/operating-principles.md`)
- Are the boundaries from the architect's design respected?
- Are domain modules free of transport/storage/vendor imports? Are side
  effects at named adapters?
- Does each changed unit still hold one coherent responsibility, or did the
  change pile a second reason-to-change onto it? Is new logic placed with
  the kin it shares state and change-cadence with?
- Does a new dependency point at a stable contract, or did the diff make
  high-level policy import a volatile detail?
- **Over-abstraction is a finding too.** Flag speculative extension points,
  pass-through layers, one-method interfaces with no real boundary, and
  dependency injection that is not dependency inversion — structure that
  adds indirection without removing coupling. The smallest change that
  satisfies the spec is the correct one.
```

### 6b. `agents/01-architect.md` — one sentence after the non-negotiable boundary rule

Find:

> Domain logic does not import transport, storage, or vendor SDKs.
> Adapters do. This is non-negotiable on the production path.

Append, in the same paragraph:

> That rule is dependency inversion applied (`core/operating-principles.md`): design each boundary as the stable contract, give each module one responsibility — separating what changes for different reasons — and add an abstraction only where variation is already real, never on speculation.

### 6c. `agents/02-implementer.md` — one sentence in the "Minimum" paragraph

Find the paragraph (lines ~21–24) ending:

> …The code that delivers the behavior is woven into the file, not stapled to its edge. See "Integrate, don't bolt on" below.

Append one sentence:

> Introducing an abstraction the spec's variation does not yet demand is the same violation as bolting on — see "Abstract only where variation is real" (`core/operating-principles.md`).

---

## 7. Step 5 — CHANGELOG entry

Append a new entry to `CHANGELOG.md` following the file's existing
newest-first format (match the structure of the current top entry). Content:

- **Version:** 5.6.0
- **Summary:** Integrated a distilled SOLID / separation-of-responsibilities
  design posture into `core/operating-principles.md` (new §9–§15) as an
  on-demand reference; folded the side-effect and duplication overlaps into
  the existing §8 and §5 rather than duplicating them; added a one-line
  canonical principle to `manifest.json`; and wired thin pointers into the
  architect, implementer, and reviewer prompts (the reviewer gains an
  over-abstraction check). No kernel bytes, no new files, no new lint.

---

## 8. Verification gate (must pass before claiming done)

1. Renumber sanity — no stale internal references remain:
   ```
   grep -nE "§(9|1[0-6])\b" core/operating-principles.md
   ```
   Inspect each hit: every `§9`–`§15` must be a *new-cluster* reference, and
   there must be **no** surviving `§14` inside the tools principle (it should
   now read `§21`). Confirm §2 still reads "(see §5)".
2. `grep -c "^## " core/operating-principles.md` returns **23**.
3. `python3 -c "import json; json.load(open('manifest.json'))"` succeeds, and
   `principles[]` has 11 entries with `version` = `5.6.0`.
4. Full gate:
   ```
   bash tests/run.sh
   ```
   All 5 shell suites and `tests/seed-lint.py` pass. In particular the
   kernel budget check passes (it must — `core/AGENTS.md` was not touched).

## 9. Done criteria

- `core/operating-principles.md` reads as one coherent posture, 23
  principles, the design cluster sitting naturally after §8; §5 and §8 carry
  their folded sentences; no fact is stated twice.
- `manifest.json`: +1 principle, version 5.6.0.
- Architect, implementer, reviewer each carry one thin pointer to the home;
  the reviewer's block covers over-abstraction.
- `CHANGELOG.md`: one appended 5.6.0 entry.
- `bash tests/run.sh` is green.
- No new files, no kernel edit, no README edit, no lint edit.

## 10. This plan's own footprint (for the reviewer)

Files touched: `core/operating-principles.md`, `manifest.json`,
`agents/01-architect.md`, `agents/02-implementer.md`,
`agents/03-reviewer.md`, `CHANGELOG.md`. Deletions of this planning file
itself are at the user's discretion; it is a working artifact, not a seed
organ.
