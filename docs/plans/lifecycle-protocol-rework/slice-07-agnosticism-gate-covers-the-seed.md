# Slice 7 — the agnosticism gate covers the seed

**Depends on:** nothing. **Owner decision required** on one item (the leak).
**Files:** `tests/seed-lint.py`, `tools/agnosticism-lint.py`,
`docs/plans/grill-7.5.0-composable-expertise.md`, `protocols/harvest.md`.

## The defect

`harvest`'s agnosticism gate is the seed's defence against project identity
reaching it. 4.8.0 found it had already failed once: *"a full sweep found
project-identifying content that had reached the seed from the projects it was
authored and grown inside — a host application's name and absolute install path,
an authoring fleet's internal component names, stack fingerprints and an
identifying count in the harvest logs, and one concrete dependency version pin."*

The root cause then was harvest's own output template, and that was fixed. The
**gate** was not, and it has four holes.

### Hole 1 — the scan roots exclude the directories where two of the four 4.8.0 leaks were found

`tests/seed-lint.py:1066-1068` fixes the roots at `core, agents, protocols,
skills, templates, library-corpus, legal-corpus, tool-corpus, agent-corpus,
skill-corpus` plus three files.

**Excluded:** `docs/` (plans *and* decisions), `tools/`, `tests/`,
`integrations/`, `documentation/`, `install.sh`, `DOCUMENTATION.md`,
`HARVEST_PROMPT.md`, `GRAFT_PROMPT.md`, `INSTALL_PROMPT.md`.

Two of the four sites 4.8.0 cleaned — `docs/plans/` and `tests/` — sit in that
blind spot today.

### Hole 2 — a live instance of exactly that, in the current tree

`docs/plans/grill-7.5.0-composable-expertise.md` carries, committed:

- `:41` — an absolute operator home path
- `:60` — a path to a local assistant-memory file, including a surname
- `:62` — a private handoff path outside the repository

This is the class `harvest.md:113` forbids — *"a path, host, port, credential, or
absolute install location"* — and precisely what 4.8.0 purged from
`docs/plans/agent-routing-and-delegation.md`. The precedent is explicit: 7.2.0
recorded *"A host path in the documentation named a user's home directory;
replaced with a placeholder. **The agnosticism lint that guards the diff would
have refused it as a new line**"* — a statement that is only true inside a
scanned root.

The `Copyright (c) 2026 Luigi Lopresto` lines in `README.md`, `DOCUMENTATION.md`
and `documentation/README.md` are **authorship, not contamination.** They stay.
The rule is about a *plant's* identity reaching the seed, not the seed's own
author.

### Hole 3 — only `*.md` is scanned

`tools/agnosticism-lint.py:65` — `DEFAULT_GLOBS = ("*.md",)`. So `install.sh`,
`tools/*.py`, `tests/*.sh`, `agents/_routes.golden.tsv` and the integration
configs are never scanned even inside scanned roots. 4.8.0's `tests/test_agent_lint.py`
leak — a hardcoded absolute repo path — was this class.

### Hole 4 — the forbidden-term arm never runs on the seed

`tests/seed-lint.py:1072` calls `agn.scan(...)` with **no `forbid=`**. What
actually gates the committed seed is host-IP, CVE, and (since 7.16.0) unreadable.
The plant-name, domain-noun, component-name and stack-fingerprint classes —
which `harvest.md:95-122` spends 28 lines defining — are enforced only if a human
remembers to type `--forbid` at harvest time. `--forbid` appears in exactly one
place in the tree: `tests/test-agnosticism-lint.sh:75`, against synthetic
fixtures. The ledger already classifies that suite: *"they prove the linter works
and say nothing about whether the seed complies."*

Version pins have no detector at all — the durability gate rejects *"a resolved
version number itself"* and the lint has only `CVE_RE`. 4.8.0 recorded one pin
having reached the seed.

## The change

1. **Widen the scan roots** to every directory the seed commits, with named
   exclusions rather than a named inclusion list — a list is what failed three
   times in the 7.16.0 remediation. Exclusions: `.git`, `__pycache__`, and
   `CHANGELOG.md`'s historical entries **only if** a reason is recorded here.
2. **Scan more than `*.md`** in those roots: `*.py`, `*.sh`, `*.json`, `*.toml`,
   `*.tsv`. Binary and unreadable already report as findings since 7.16.0.
3. **Decide the leak** — owner decision, below.
4. **Wire a default `forbid` set** for the seed's own gate, or record explicitly
   in `harvest.md` that the four judgment classes are human-only and that the
   gate's PASS does not cover them. One or the other; the current state claims a
   floor it does not have.
5. **A version-pin detector** for the durability gate, since that gate already
   forbids what nothing checks.

Expect step 1 to go **red immediately** — that is the point, and it is how every
other check in this remediation was established.

## The owner decision

**What it is.** Whether to redact three lines from
`docs/plans/grill-7.5.0-composable-expertise.md`, a committed historical plan.

**Why it matters.** The repository is public
(`github.com/llopresto87/Cypress`). The lines expose an operator's home directory
layout and a local assistant-memory path. Separately, leaving them makes step 1
impossible to land green without an exemption, and an exemption on the first file
the widened gate catches is how a gate becomes decorative.

**TAKEN, 2026-09-14 — the owner approved the redaction.** The three lines are
replaced with placeholders and a `> **Redacted**` note at the head of §0.0 says
what was removed, why, and that history was deliberately not rewritten. Same
treatment 4.8.0 gave `docs/plans/agent-routing-and-delegation.md`. Plans are not
append-only; only `CHANGELOG.md` and `docs/decisions/` are.

Nothing was lost: each line named *where* a thing sat on one machine, never
*what* it said, so no instruction changed meaning. What stays, and is not
contamination: the `Copyright (c) 2026` lines, which are authorship, and the
project's own clone URL, which `README.md` already publishes — the SSH form at
`grill-7.5.0-composable-expertise.md:73` exposes nothing the repository does not.

Step 1 below can now land green rather than needing an exemption on the first
file the widened gate catches.

**What NOT to do.** Rewrite git history. The lines are in published commits; a
force-push would break every clone and graft base for a cosmetic gain, and the
stamp `graft` reads for provenance is a commit sha.
