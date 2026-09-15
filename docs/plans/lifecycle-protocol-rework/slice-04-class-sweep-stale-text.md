# Slice 4 — class sweep: stale and self-contradicting text

**Depends on:** nothing. Can run parallel to slices 1–3 **only if a single writer
owns all three files** — these edits touch the same regions slice 1 rewrites.

## Why a sweep and not a fix list

The seed wrote `holistic-editing.class-sweep` in 6.14.0 specifically against this
failure: *"Where a defect has siblings, the unit of work is the defect class… New
forbidden move (fixing the handed instance while known siblings keep the
defect)."* The rule exists. It has never been applied to these three files, and
the evidence below is what that costs.

## The instances

### `harvest.md` — "both gates", three surviving siblings

6.1.0 fixed an internal contradiction: *"Phase 2 said 'apply both gates' while
the protocol defines three — now 'all three'."* The sweep was not done. Three
survive, untouched since the initial import:

- `:415` legal corpus — *"both gates apply"*
- `:471` tool corpus — *"both gates apply"*
- `:508` expert corpus — *"Both gates apply, plus the roster's own economy"*

And the skill-corpus section `:539-562` names **no** gates at all — a fourth
sibling of the same defect, in the contract that was *also* demonstrably wrong for
fourteen versions.

### `grow.md` — the contract's exit condition names an abolished artifact

7.3.0 replaced the completeness ledger with the coverage record. It rewrote
`:184-186` and `:286-287`, and missed the one inside a paragraph nobody had
reason to open. `:250-252`, byte-identical since the initial import:

> "It ends when **the ledger** shows every collection is covered-to-evidence or
> absent-with-reason…"

`.cypress/growth/completeness-ledger.md` was superseded by `.cypress/coverage.json`.
So the word "ledger" now means two different things in this file: the abolished
completeness ledger (`:251`) and the live per-scout evidence ledger (`:47`, `:268`,
`:363`). **The exit condition of the completeness contract points at nothing.**

### `grow.md` — Boundaries contradicted by Phase 1, never amended

`:129` (original): *"Preserve target-owned files. Knowledge writes stay under
`docs/graph/`."* Phase 1 since 7.3.0 requires writes to `.cypress/growth/` and
`.cypress/coverage.json`, outside `docs/graph/`. The exception lives only in
Phase 1; the absolute statement was left standing.

### `grow.md` — Phase 3 is byte-identical to the initial import and stale

The only section with zero edits in ten commits. It still says *"Configure
`ROOT_ID` and `KINDS` in `graph-lint.py`"* with no mention of `KIND_PREFIX`
(documented since 6.9.2) and no mention of the `expertise` kind 7.5.0 added to
`KINDS`. 7.5.0 introduced an entire new node kind and wired it into **Phase 4**,
because Phase 4 was where the `libraries/` sentence already sat — a placement
made by inertia, not ownership. Node authoring is Phase 3's job.

### `graft.md` — two passages describe an installer that no longer exists

`graft.md` went untouched through four releases including 7.15.0, whose fix was
that *"every adapter copied `agents/*.md` **out of the seed**, so the projection
was a projection of the seed's roster."* `:312-315` and `:578-582` instruct
regenerating the `.claude/` projection from the reconciled home — text authored
in 7.5.0 against the old hand-rolled behaviour. The installer now projects from
the graph. **The instruction is currently wrong.**

### `graft.md` — an absolute rule narrowed 240 lines later

`:126` — a fast-forward *"never advances, closes, or re-opens a plant's lifecycle
state"*. `:369-372` then carves out *"the one sanctioned exception to the rootstock
rule on `status:`"*. The exception is not referenced from `:126`. Same shape at
`:131-134` (absolute blockquote) narrowed at `:136-142` and again at `:681-684`.

### `harvest.md` — the description restates four sections

The frontmatter `description:` (`:3`) is a ~250-word prose restatement of
§agnosticism-gate, §what-counts-as-a-project-reference, §trigger and §what-you-do-
not-do. It is also the **eagerly loaded** surface — 7.16.0 measures `description:`
as always-on context — which makes it the most expensive duplicate in the file.

## The change

One pass per class, all siblings in the same edit:

1. "both gates" → "all three gates", ×3, **and** the skill-corpus section gains
   its gate statement — the fourth sibling.
2. `grow.md:250-252` exit condition renamed to the coverage record. Sweep every
   remaining occurrence of "ledger" in the file and disambiguate the two senses;
   if the evidence ledger is the only survivor, say so once.
3. `grow.md:129` amended in place to name where growth legitimately writes
   outside `docs/graph/`, with Phase 1 keeping the detail.
4. `grow.md` Phase 3 updated for `KIND_PREFIX` and `expertise`, and the expertise
   node-authoring rules moved from Phase 4 to Phase 3 where ownership says they
   belong. **This is a move, not a copy** — Phase 4 keeps the `libraries/`
   sentence that needs it and points.
5. `graft.md:312-315` and `:578-582` rewritten against the current installer.
6. `graft.md:126` and `:131-134` gain the forward reference to their exceptions.
   An absolute rule with an unreferenced exception is a trap for the reader who
   stops at the absolute.
7. `harvest.md:3` cut to what a router needs to select the node. The four
   sections it restates are the home; the description is not a summary of the
   file, it is a routing key.

## The guard

Item 5's class — *protocol text describing tool behaviour that has since
changed* — has no detector and is the reason `graft.md` shipped a wrong
instruction for four releases. A cheap partial: `seed-lint` already greps spec
§10 cells against the test suite (`check_spec_test_mapping`). The same shape
applies here — every `install.sh` flag a lifecycle protocol names must exist in
`install.sh`'s option parser, and every flag the protocol *should* name (those
that change what is written or backed up) must appear. Red first: `--force` and
`--symlink` appear in neither, which is slice 3 item 4 and 5.
