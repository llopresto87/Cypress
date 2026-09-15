# Evidence — `protocols/grow.md`

Mined from `CHANGELOG.md`, the plans, and the diff of every one of the 10 commits
that touched the file. **Untouched since 7.12.0 (`5b46114`)** — 7.13.0, 7.13.1,
7.14.0, 7.15.0 and the 7.16.0 working tree all leave it byte-identical.

## Size and structure

388 → 743 total lines, **+91% over 10 commits, monotonic. The file has never
shrunk.** The largest single deletion in its history is 42 lines, and that was a
rewrite-in-place.

| sha | release | total | Δ | cause |
|---|---|---|---|---|
| `6dde434` | import | 388 | — | |
| `c8706d7` | 6.9.1/2 | 388 | 0 | router repathed; bootstrap block became a pointer |
| `5c33f03` | **6.11.0** | 482 | **+94** | the live install that read only the project's own files |
| `b4de261` | 6.13.0 | 497 | +15 | tool/skill corpus path |
| `53f845a` | **7.0.0** | 557 | **+60** | plant facts; scaffold pruning; `grown: true` |
| `713d32a` | **7.3.0** | 635 | **+78** | the coverage gate; the intake list; the stack inventory |
| `e9c1896` | **7.5.0** | 689 | **+54** | expertise as nodes; "staff the project" |
| `7ff4b55` | 7.10.0 | 705 | +16 | `raw:`; the verdict list; `UNKNOWN` disclosure |
| `bb90f8d` | 7.11.0 | 728 | +23 | the legal-corpus decision |
| `5b46114` | 7.12.0 | 743 | +15 | jurisdiction |

**All eleven `##` headings date to the initial import.** No section has ever been
added or removed at that level; every increment arrived as a `**Bold-lead**`
paragraph bolted inside an existing section.

Section growth is wildly uneven: Phase 1 ×3.6, Phase 4 ×2.9, Phase 2 ×2.9,
Phase 5 ×3.5, the completeness contract +43 — and **Phase 3 is byte-identical to
the import**, the only section with zero edits in ten commits.

## The worst recorded outcome

*"The roster grew and grow's intake did not."* `ui-ux-designer` joined at 6.9.0
and `legal` at 6.12.0, but grow's scout assignment, shape diagram, Phase 4
authoring list and evidence-ledger schema were never extended. **Every plant
grown between 6.9.0 and 7.3.0 carries an empty `design/` and `legal/`, and the
seed reported those growths as complete.**

The scar is now in the text at `:349-355`. But the actual guard is
`tests/seed-lint.py:846-948` — a seed-side CI arm a plant-side growth run never
executes, and which `grow.md` never names.

## The sentence that was itself the defect

7.11.0, under the heading *"The sentence that taught this"*: grow's Phase 4 said
to *"seed each page from it"*, which read as licence to assemble a per-project
legal subset, and **a session following it faithfully began building exactly the
filtered corpus** — one page at a time, from an applicability judgment it made
itself. *"The instruction was wrong, not the reading."* Why it matters: the
analyst has no web access, so a missing page *"produces no visible gap; it
produces a silent false negative wearing the shape of a correct refusal."*

## The eight false greens, all tool-only

An adversarial review of 7.3.0 *"found the audit passing the exact plants it was
written to catch"*: a one-character append marked a collection COVERED; agent
coverage was any-of not all-of; a bare `UNKNOWN` with no blocker passed;
grounding was satisfied by the seed's own untouched README; a planned artifact
with no `path` was skipped; `resolves()` accepted directories and escapes;
`${{ github.ref }}` read as an unfilled placeholder; a record naming no
`seed_version` disabled the `STALE` check.

**Not one became protocol text.** The most consequential is documented as a code
comment at `tools/growth-audit.py:175-182`.

## False-green paths still open

1. **The `inventory` row set is self-declared.** Three of four row sets derive
   from the seed; the fourth drives every artifact and is written by the run about
   its own findings. `grow.md:398-399` says so — *"a project item that never
   reaches it is an item no gate can miss the absence of"* — with no mitigation.
2. **Nothing verifies a scout ever ran.** The ledgers are the evidentiary basis of
   Phases 3–4, are mandated gitignored (`:267-273`), and no tool reads them. A run
   that authored everything from model memory produces the same green audit.
3. **`UNGROUNDED` proves a file exists under `sources/`**, not that anything was
   retrieved; `raw_retained` accepts a stated reason in place of a snapshot.
4. **`UNKNOWN` is uncapped.** A growth marking `design/`, `legal/`, `api/`, `data/`
   and every dependency `UNKNOWN` exits 0 and prints *"coverage complete"*.
5. **`SILENT` is satisfied by a word match** in `changelog.md`, not by an ask.
6. **`grown: true` is set by the same party that decides validation passed**, and
   `graph-lint` reads it to decide how strictly to judge the plant.

## Steps with no verification

Topology 1, 2, 3, 6; the routing-band citation; the spawnability preflight;
Phase 1 provenance and gitignore; Phase 2's ledgers; **Phase 3 in its entirety**;
Phase 4's agnosticism run; Phase 5 (mandatory, emphatic, and verified only by the
orchestrator's own self-report — *"'No rebalance needed' is a legitimate result
only when the librarian pass actually ran and says so"*); the canonize close-out;
the maturity test.

## Accretion

- `"template files existing at their paths is never coverage"` at `:191-192` and
  again at `:232-233`, 41 lines apart, **inside the one section whose subject is
  one-home-per-fact**.
- **The contract's exit condition names an abolished artifact.** `:250-252`,
  byte-identical since import, still says *"It ends when **the ledger** shows…"*
  — 7.3.0 replaced the ledger with the coverage record and edited the two other
  references.
- `research-scout` mandated in three places, each with its own wording.
- `.cypress/growth/` gitignore stated twice; the record's location three times.
- Boundaries `:129` — *"Knowledge writes stay under `docs/graph/`"* — contradicted
  by Phase 1 since 7.3.0, never amended.
- 21 bold lead-ins and 18 ALL-CAPS emphasis words, clustering on exactly the rules
  with the worst incident history: eight restatements of the completeness idea,
  six of external evidence, four of the librarian pass (which has zero mechanical
  verification).
- 19 body lines over the 79-column margin; six sit exactly at the seams where
  later blocks were spliced in and the tail was never re-wrapped.

## Frontmatter

Six `owns:` facts, none ever removed. `grow.completeness-contract` holds 19% of
the body across five separate places; `grow.stack-inventory` gets 12 lines (2%)
despite driving every inventory-derived artifact and containing the file's
largest acknowledged false green. `load_when:` has not changed since 7.3.0, so
`grow.legal-corpus` added 38 lines and no routing trigger. `est_tokens` frozen at
7726 since 7.5.0 while the body grew — passing only because the honesty check is
2×-loose.
