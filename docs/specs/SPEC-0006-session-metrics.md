---
status: implemented
status_date: 2026-10-05
owner: architect
status_evidence: tests/test-session-metrics.sh (the consolidated suite, 14 cases: X399, X400, X404, X406 to X410, X412 to X414, X416, X417, X423), tests/test-lint-audibility.sh (X415) and tests/test-full-install.sh (E14), all wired into tests/run.sh, every §10 row green over the 24 contracts; one sanity check after the cut (an empty value never reported, caught by X400); a read-only `--all --json` query over eight plant changelogs that finds their one delivery entry, filled
---

# SPEC-0006: the session-metrics reader

## 0. Metadata

- **Identifier:** SPEC-0006-session-metrics
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-10-05
- **Last reviewed:** 2026-10-05
- **Related grill section:** docs/plans/grill-8.0.0-wave-a.md §9, the
  increment that carries this spec's RED (to be added by the session)
- **Related ADRs:** adr-0003-enforcement-layering-honesty (the class this
  reader has: detective, §5); adr-0004-pure-graph-architecture (one home per
  fact: the reader takes its line list from the deliver node, §6); adr-0021
  (the tools `install.sh` places are held against `manifest.json`)
- **Related specs:** SPEC-0001-install-placement (its placement contracts and
  its destination sweep hold every file `install.sh` writes, this reader's
  copy included; §2)
- **Related wiki pages:** none (stdlib Python and POSIX shell only)
- **Design latitude:** balanced. The owner decided on 2026-10-05 the
  direction: a reader enforces the
  session-metrics block for Tier 2 and Tier 3 deliveries
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [x] · architect [x] · tester [x] · security [ ]
  Architect 2026-10-05: §0 to §2, §4 to §8, §10 draft, §11; amended at the
  promotion to `active`, after each product review, and after the code review
  (§12). Product and tester signed the 22-contract spec on 2026-10-05; both
  boxes were cleared when the code review widened the contract and were
  ticked again after a re-look: tester 2026-10-05, re-signed over the 29
  contracts, each with its case in §10; product 2026-10-05, re-ticked over the
  widened §6 rules and AC-1, AC-3, AC-4 and AC-10.

## 1. Summary

`protocols/deliver.md` defines a Session metrics block that every full-form
(Tier 2 and Tier 3) delivery must carry, and `protocols/harvest.md` names it
the seed's only quantitative donor surface. Nothing reads it. Deliveries
were found with no block at all, and blocks written under a heading form the
template does not name. A block that nothing reads stays
empty, so harvest has nothing to aggregate.

This spec makes the block readable and enforced. The block lives in one file a
reader can open: the plant's `docs/graph/changelog.md`, where deliver already
appends the full form. A new stdlib tool, `tools/session-metrics.py`, placed
into every plant at `docs/graph/session-metrics.py`, has two roles. The lint
role judges every delivery entry dated on or after a date the caller gives
and exits 1 when a Tier 2 or Tier 3 entry has no block, a missing line, an
empty line, or a `not recorded` with no reason. The query role lists every
entry with its raw line values, for harvest. The tool takes the list of lines
from the deliver node's own template, so the block keeps one home.

## 2. Scope

- **In scope:**
  - where a delivery's metrics are persisted, and the line format the reader
    parses (§6)
  - how a changelog entry declares itself a delivery, and its tier (§6)
  - the lint role: what is judged, what is a violation, the messages and exit
    codes (§4, §6)
  - the query role that `harvest` reads (§4, §6)
  - the reader running inside a fresh plant, against the plant's own deliver
    node (§4)
- **Out of scope:**
  - the block's wording and its list of lines. `protocols/deliver.md` owns
    them, and §11 lists the wording changes this design asks of it
  - the placement mechanics: `install.sh` places the tool with `place_file`,
    the way it places `docs/graph/status-register.py`, and SPEC-0001's
    destination sweep, `manifest.json`'s `tools` map and seed-lint's
    seed-only check hold that placement. This spec holds only that the placed
    tool runs
  - whether a filled value is true. The reader checks that a line is filled,
    not that its number is right (§7 `VALUE_FILLED_BUT_FALSE`)
  - parsing numbers out of a line's value. The query role returns each value
    as written; turning `HIGH×3 MEDIUM×1` into counts is a later harvest tool
  - the intermediate blocks a long session appends to grill.md §15 after each
    increment. The reader reads the changelog only
  - grow's growth metrics and graft's provenance entry, which carry their own
    headings (`# Graft — …`) and are not delivery entries (§11)
  - a hook that refuses a delivery that skipped the run (§7
    `DELIVERY_SKIPPED_THE_RUN`)

## 3. User-facing behavior

(Drafted by `architect` for `product` to review.)

There are three users.

**The orchestrating session at deliver.** It writes the full-form summary,
appends it to `docs/graph/changelog.md`, then runs one command,
`python3 docs/graph/session-metrics.py --since <the date in its heading> --entry <the line of its heading>`.
On a pass it prints one line and the delivery is complete. On a failure it
prints one line per defect of its own entry, each with the file, the line and
the label to fix, and the session fixes that entry before it ends. A defect in
an entry another session wrote that day is printed on a `note:` line and never
fails the run, so a session can always reach a pass by fixing only its own
entry. An older entry from before the rule is never judged, because the
session names the date it starts from.

**A harvest session.** It runs the seed's copy against a plant:
`python3 <seed>/tools/session-metrics.py --root <plant>/docs/graph --all --json`.
It gets one record per delivery entry, with each metrics line as written and a
status of `filled`, `exempt` or `incomplete`. An entry without a block is data
(`incomplete`, no lines), never a failure of the run.

**A plant steward who changed the block.** A plant that adds a line to its
deliver node's block (for example, a tokens line) is checked against its own
block, because the reader takes the lines from the node it finds in that plant.

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

Every contract runs `tools/session-metrics.py` on a changelog its case writes
in a scratch directory, with the shipped `protocols/deliver.md` as the deliver
node, unless it names another file or node. "Delivery entry", "full form",
"compact form", "declared tier", "filled", "label" and the finding codes are
defined in §6.

### Lint role

### Contract: METRICS_FILLED_ENTRY_PASSES
- **Given:** a changelog whose one delivery entry, dated on or after `--since`,
  is full form with a Session metrics block carrying every label with a filled
  value
- **When:** the lint role runs with `--since`
- **Then:** it exits 0 and prints one line that starts `session metrics: PASS`
  and counts one filled entry

### Contract: METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED
- **Given:** a judged entry, every line filled, one of them
  `not recorded: the host exposes no spawn ids` (the canonical form deliver
  teaches)
- **When:** the lint role runs
- **Then:** that line is a filled value: no finding names it
- **Note:** narrowed 2026-10-05 (consolidation): the `not recorded (<reason>)`
  and `not recorded — <reason>` forms are reading rules no contract holds (§6)

### Contract: METRICS_BLOCK_MISSING_FAILS
- **Given:** a full-form delivery entry, dated on or after `--since`, whose
  heading declares no tier and which has no Session metrics heading
- **When:** the lint role runs
- **Then:** it exits 1, and one finding line names the changelog, the line of
  the entry's heading and the code `METRICS_BLOCK_MISSING`

### Contract: METRICS_LINE_MISSING_FAILS
- **Given:** a judged entry whose block carries every label except `Serial waits`
- **When:** the lint role runs
- **Then:** it exits 1, and one finding with the code `METRICS_LINE_MISSING`
  names the label `Serial waits` and the line of the block's heading

### Contract: METRICS_LINE_EMPTY_FAILS
- **Given:** a judged entry whose block carries every label, where `Retries:`
  has nothing after the colon, `Gates:` still holds the template slot
  `<run/failed-then-fixed counts>`
- **When:** the lint role runs
- **Then:** it exits 1 with exactly two `METRICS_LINE_EMPTY` findings, each
  naming its label and its own line number
- **Note:** narrowed 2026-10-05 (consolidation): the empty words (`TBD`, `?`,
  dashes and the rest of the §6 set) are a reading rule no contract holds

### Contract: METRICS_NOT_RECORDED_WITHOUT_REASON_FAILS
- **Given:** a judged entry whose `Spawns:` value is `not recorded` and whose
  `Overflow notes:` value is `not recorded:` with nothing after it
- **When:** the lint role runs
- **Then:** it exits 1 with two `METRICS_REASON_MISSING` findings, one per line

### Retired: METRICS_TIER_UNREADABLE_FAILS
Retired 2026-10-05 (consolidation, `test-first.proportionate-checks`): no named blast radius. The behaviour stays the reader's; §6 "Reading rules no contract holds" states it and its coverage loss.

### Retired: METRICS_TIER_IN_MARKUP_READ
Retired 2026-10-05 (consolidation, `test-first.proportionate-checks`): no named blast radius. The behaviour stays the reader's; §6 "Reading rules no contract holds" states it and its coverage loss.

### Retired: METRICS_TIER_NOT_RECORDED_DECLARES_NONE
Retired 2026-10-05 (consolidation, `test-first.proportionate-checks`): no named blast radius. The behaviour stays the reader's; §6 "Reading rules no contract holds" states it and its coverage loss.

### Contract: METRICS_LOW_TIER_EXEMPT
- **Given:** two judged full-form entries, one whose block holds only
  `- Tier: T1 (reclassified: none)`, and one whose heading reads
  `## T0 delivery — answered a question — <date>` with no block
- **When:** the lint role runs
- **Then:** it exits 0, and the PASS line counts two exempt entries

### Contract: METRICS_COMPACT_ENTRY_EXEMPT
- **Given:** a judged entry with a compact-form heading,
  `# Delivery (compact) — <what> — <date>`, and no block
- **When:** the lint role runs
- **Then:** it exits 0, and the PASS line counts one exempt entry

### Contract: METRICS_ENTRIES_BEFORE_SINCE_NOT_JUDGED
- **Given:** a changelog with a full-form entry dated the day before `--since`
  that has no block, and a filled entry dated on `--since`
- **When:** the lint role runs
- **Then:** it exits 0, and the PASS line counts one entry judged

### Contract: METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE
- **Given:** a changelog with two full-form delivery entries dated on
  `--since`, in either order (the session's own above or below the other):
  another session's entry with no Session metrics block, and the session's own
  entry, filled, whose heading is on line N
- **When:** the lint role runs with `--since` and `--entry N`
- **Then:** it exits 0 with the PASS line counting one filled entry
- **And:** a `note:` line names the other entry's heading line and the code
  `METRICS_BLOCK_MISSING`, and no line starts `  - `

### Contract: METRICS_NO_ENTRY_SINCE_FAILS
- **Given:** a changelog whose delivery entries are all dated before `--since`,
  plus one delivery heading that carries no date
- **When:** the lint role runs
- **Then:** it exits 1 with one `NO_DELIVERY_ENTRY` finding that names the
  changelog, the `--since` date and the heading forms the reader accepts
- **And:** a `note:` line names the undated heading by its line, as not judged

### Contract: METRICS_MISSING_CHANGELOG_FAILS
- **Given:** a graph root with a deliver node and no `changelog.md`
- **When:** the lint role runs
- **Then:** it exits 1 with one `NO_DELIVERY_ENTRY` finding that says the
  changelog does not exist

### Contract: METRICS_SINCE_REQUIRED
- **Given:** any changelog
- **When:** the lint role runs without `--since`, or with a `--since` that is
  not a `YYYY-MM-DD` date
- **Then:** it exits 2 and prints a usage message naming `--since`, and judges
  no entry

### Contract: METRICS_ENTRY_HEADINGS_RECOGNIZED
- **Given:** a changelog with six headings dated on `--since`: the template
  form `# Delivery — <title> — <date>` with a filled block; a level-2
  `## T3 delivery — <title> — <date>` with a filled level-3 block; a
  `# Delivery — <title> — <date>` line inside a fenced code block; a
  `## Standalone delivery — <title> — <date>` heading; a
  `## Delivery-pipeline cache fix — <date>` heading; and a
  `## Delivery: moved assets to a CDN — <date>` heading, none of the last four
  with a block
- **When:** the lint role runs
- **Then:** it exits 0, and the PASS line counts two filled entries: a fenced
  line is not a heading, a heading whose first word is not `Delivery` (after
  an optional tier token) is not a delivery entry, and neither is one whose
  `Delivery` is followed by a hyphen inside a word or by a colon

### Contract: METRICS_DATED_HEADING_ENDS_ENTRY
- **Given:** a changelog whose first line is `# Delivery — new — <date>` with
  no block, followed by `## Older — canonize close-out — <date>` with a filled
  `### Session metrics` block, both dated on `--since`
- **When:** the lint role runs
- **Then:** it exits 1 with one `METRICS_BLOCK_MISSING` finding on line 1: the
  dated `##` heading ends the delivery entry, so its block is not borrowed

### Retired: METRICS_ENTRY_DATE_IS_LAST_IN_HEADING
Retired 2026-10-05 (consolidation, `test-first.proportionate-checks`): no named blast radius. The behaviour stays the reader's; §6 "Reading rules no contract holds" states it and its coverage loss.

### Contract: METRICS_SECTION_HEADINGS_STAY_IN_ENTRY
- **Given:** a judged entry written flat: `## Delivery — <title> — <date>`
  followed by `## Files changed`, `## Gates run` and `## Session metrics` at
  the same level, the block filled
- **When:** the lint role runs
- **Then:** it exits 0, because a same-level heading that the deliver node's
  template names as a full-form section stays inside the entry

### Retired: METRICS_FENCED_LINE_NOT_A_METRICS_LINE
Retired 2026-10-05 (consolidation, `test-first.proportionate-checks`): no named blast radius. The behaviour stays the reader's; §6 "Reading rules no contract holds" states it and its coverage loss.

### Input bytes and lines

### Contract: METRICS_LINES_COUNTED_AS_GREP_DOES
- **Given:** a changelog with a U+2028 character inside a line and a line
  holding only a form feed, both above a filled delivery entry dated on
  `--since`, and N the line `grep -n` gives for that entry's heading
- **When:** the lint role runs with `--since` and `--entry N`
- **Then:** it exits 0, and the PASS line names `(line N)`

### Contract: METRICS_LEADING_BOM_IGNORED
- **Given:** a changelog whose bytes start with a UTF-8 byte-order mark,
  followed at once by `# Delivery — x — <date>` with a filled block
- **When:** the lint role runs with `--since` and `--entry 1`
- **Then:** it exits 0, and the PASS line counts one filled entry

### Deliver node

### Contract: METRICS_LABELS_FROM_DELIVER_NODE
- **Given:** a deliver node built from the shipped `protocols/deliver.md`
  whose template block carries one extra line, `- Tokens: <per spawn>`, and a judged entry that carries every
  `protocols/deliver.md` label but not `Tokens`
- **When:** the lint role runs with `--deliver` naming that node
- **Then:** it exits 1 with one `METRICS_LINE_MISSING` finding naming `Tokens`

### Contract: METRICS_SHIPPED_DELIVER_NODE_PARSES
- **Given:** the seed's own `protocols/deliver.md`, as shipped
- **When:** the tool runs `--labels --deliver protocols/deliver.md` from the
  seed root
- **Then:** it exits 0 and prints one label per line, `Tier` among them, and
  every printed label appears in that file as a list item `- <label>:`
- **And:** the file names `session-metrics.py --since` together with
  `--entry`, the command deliver tells the session to run. This holds the §9
  shipping condition
- **Note:** narrowed 2026-10-05 (consolidation): the check that the file names
  `not recorded: <reason>` is dropped; it read back prose (§10 coverage loss)

### Contract: METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD
- **Given:** a deliver node with no fenced block that holds a
  `## Session metrics` heading
- **When:** the lint role runs against it
- **Then:** it exits 2, and its message names the node's path and says no
  Session metrics template was found, and judges no entry

### Contract: METRICS_UNREADABLE_CHANGELOG_FAILS_LOUD
- **Given:** a `changelog.md` that cannot be read (mode 000, or bytes that are
  not UTF-8 when the run is root)
- **When:** the lint role runs
- **Then:** it exits 2, and its message names the path and says it could not
  be read

### Query role

### Contract: METRICS_ALL_REPORTS_EVERY_ENTRY
- **Given:** a changelog with a filled entry, an entry with no block, a
  compact entry, and a `### Session metrics` block under a heading that is not
  a delivery heading
- **When:** the tool runs `--all --json`, with no `--since`
- **Then:** it exits 0 and prints a JSON array of four records in file order,
  with statuses `filled`, `incomplete`, `exempt` and `filled` and markers
  `delivery`, `delivery`, `compact` and `unmarked`
- **And:** the first record's `lines` maps each label to its value exactly as
  written after the colon, trimmed

### In a plant

### Contract: METRICS_READER_RUNS_IN_A_FRESH_PLANT
- **Given:** a fresh `install.sh all --copy` into an empty directory
- **When:** `python3 docs/graph/session-metrics.py --labels` runs from the
  plant root, with no other argument
- **Then:** it exits 0 and prints the labels of the placed
  `docs/graph/protocols/deliver.md`, `Tier` among them

## 5. Non-functional requirements

- **Dependencies:** Python 3 standard library only, one file, no import of
  another seed file, because it is placed alone beside the plant's graph.
- **Configuration:** none. Every input is a flag or a default path, so the
  installer fast-forwards it like `status-register.py` and graft needs no
  engine reconcile for it (contrast `spec-lint.py`, which carries
  `TEST_GLOBS`).
- **Writes:** none. Both roles only read.
- **Determinism:** the same inputs give byte-identical output. Records keep
  file order.
- **Enforcement class (ADR-0003):** detective. The session runs the lint at
  deliver; no hook runs it and no harness refuses a delivery that skips it.
  Any front-door claim of enforcement cites this class.
- **Cost:** one pass over one file; no measurable cost for a changelog of a few
  thousand lines.

## 6. Data shapes

### Where the metrics are persisted

The full-form delivery entry in the plant's `docs/graph/changelog.md`.
`protocols/deliver.md` already appends the full form there and to grill.md
§15; the reader reads the changelog alone. Two places were rejected:

- the session record (`plans/sessions/<date>-<slug>.md`). It is unrouted
  working state with no frontmatter, one per unit of work and not per
  delivery, and a second copy of the block would be a fact with two homes.
- a new ledger file. It would be a third copy of what the changelog entry
  already holds, and one more file every plant must create.

### The deliver node and the labels

The deliver node is `<root>/protocols/deliver.md` by default, or the path
`--deliver` names. The reader finds the first fenced code block (CommonMark
fence: at most three spaces of indent, then three or more backticks or
tildes, closed by a fence of the same character at least as long) that
contains a line `## Session metrics`. From that block it reads:

- **labels:** every list item between that heading and the next heading or the
  fence's end, of the shape `- <label>: <anything>`. The label is the text
  before the first colon, trimmed. Today they are `Tier`, `Spawns`,
  `Route bands`, `Retries`, `Gates`, `Full-suite runs`, `Serial waits`,
  `Overflow notes` and `Quality`; the reader holds no copy of that list.
- **section names:** the text of every `## ` heading inside the same block
  (`Files changed`, `Routing attribution`, … `Recommended next step`).

No such block, or a block with no label, is exit 2.

### Reading the file

Every input file (the changelog and the deliver node) is read as UTF-8, and a
byte-order mark at its start is ignored, so a heading on line 1 is still a
heading. A line is the text between two `\n` characters, counted from 1, the
way `grep -n` counts: a `\r` before the `\n` is dropped, and no other
character (a lone `\r`, a form feed, U+2028 or U+2029, U+0085) ends a line.
Every line number the reader prints, and the LINE that `--entry` takes, use
this count, because deliver tells the session to find its line with `grep -n`.

### Delivery entry

A heading, at any level, outside a fenced block, whose text matches (case
does not matter):

```text
^(?:T(?P<tier>[0-3])\s+)?delivery(?P<compact>\s*\(compact\))?(?:\s*[—–]|\s+-\s)
```

The separator after `delivery` (or `(compact)`) is an em dash or an en dash,
with or without white space before it, or a hyphen with white space on both
sides. The template form `Delivery — <title> — YYYY-MM-DD` and the observed
form `T3 delivery — <title> — YYYY-MM-DD` both match. These do not:
`Standalone delivery — …` (`delivery` is not the first word),
`Delivery-pipeline cache fix — …` (a hyphen inside a word), and
`Delivery: moved assets to a CDN — …`. The colon form is not accepted: the
template never uses it, no plant was seen using it for a delivery, and it is
the form an ordinary title starting with the word takes.

- **date:** the last `YYYY-MM-DD` in the heading text; none means undated. A
  title may quote an earlier date (`follow-up to the 2026-09-30 release`);
  the template puts the delivery's own date last.
- **form:** `compact` when the `(compact)` group matched, otherwise `full`.
- **span:** from the heading to the first of these, outside a fence: the next
  delivery heading at any level; the next heading, at any level, that carries
  a `YYYY-MM-DD` date and is not one of the section names; the next heading
  whose level is the same or higher (as many `#` or fewer), except a heading
  whose text is one of the section names; the end of the file. So a delivery
  heading nested under another delivery entry starts its own entry and ends
  its parent's span, and a dated entry written one level below a delivery
  heading (a `##` close-out under a `#` delivery) ends it too: neither entry
  can take the other's block.
- **block:** the first heading inside the span whose text, trimmed of a
  trailing colon, is `Session metrics` (case does not matter). Its lines run to
  the next heading or the end of the span.
- **unmarked block (query role only):** a Session metrics heading outside
  every delivery entry's span. Its entry is the nearest heading above it of a
  higher level, reported with the marker `unmarked`. The lint role ignores it.

### A metrics line

```text
^\s*[-*+]\s+(?:\*\*)?(?P<label>[^:*]+?)(?:\*\*)?\s*:\s*(?P<value>.*)$
```

A line inside a fenced block is not a metrics line, the same rule that makes a
fenced line not a heading: a fenced example of the template inside a block is
never read as the entry's values. The label is compared with the deliver
node's labels after trimming, folding case and collapsing inner spaces. The
first line for a label counts; a label the deliver node does not name is kept
in the query output and never judged.

A value is **filled** unless one of these holds:

| Value, trimmed | Finding |
|---|---|
| empty | `METRICS_LINE_EMPTY` |
| starts with a template slot: `<`, then text with no `<` or `>`, then `>` | `METRICS_LINE_EMPTY` |
| exactly one of `TBD`, `TODO`, `?`, `...`, `…`, `-`, `–`, `—` (case does not matter) | `METRICS_LINE_EMPTY` |
| starts with `not recorded` and what follows, after stripping spaces and one of `:`, `—`, `–`, `-`, `(`, holds no letter or digit, or is a template slot | `METRICS_REASON_MISSING` |

So `not recorded: <reason>` is filled, and so are `not recorded (<reason>)` and
`not recorded — <reason>`. The canonical form, for deliver.md's wording, is
`not recorded: <reason>`. `n/a`, `none` and `0` are filled values.

**Reading rules no contract holds.** These rules describe how the reader
reads, and no case holds them, so a change to any of them can pass the gate.
Each one's failure is a readable false FAIL the session fixes, or a branch no
caller uses; none has a named blast radius (`test-first.proportionate-checks`).
The coverage loss is recorded with each.

- A line indented by two or more spaces that does not start a list item
  continues the previous line's value. It needs a hand-made input; the
  template writes none. Loss: a wrapped value could read as empty.
- A block's lines end at the next heading, so a `- <label>:` line under a
  later section is never read as a metrics line. The template puts no such
  line there. Loss: a later section's list item could fill a missing line.
- Leading backticks, asterisks and underscores are stripped from a Tier value
  (retired `METRICS_TIER_IN_MARKUP_READ`). A session that writes `**T2**`
  without it sees `METRICS_TIER_UNREADABLE` and fixes the value. Loss: that
  false FAIL could return.
- A `Tier:` value of `not recorded: <reason>` declares no tier and is not
  unreadable (retired `METRICS_TIER_NOT_RECORDED_DECLARES_NONE`). Its only
  failure is a readable `METRICS_TIER_UNREADABLE`. Loss: that false FAIL could
  return.
- A filled Tier value that names no tier is `METRICS_TIER_UNREADABLE` (retired
  `METRICS_TIER_UNREADABLE_FAILS`). The entry is judged as full form either
  way, so the finding is a hint and not a protection. Loss: the hint could
  vanish.
- The date of an entry is the last date in its heading (retired
  `METRICS_ENTRY_DATE_IS_LAST_IN_HEADING`). A heading quoting an earlier date
  is rare, and the wrong pick gives a readable `NO_DELIVERY_ENTRY`. Loss: that
  false FAIL could return.
- A fenced line inside a block is not a metrics line (retired
  `METRICS_FENCED_LINE_NOT_A_METRICS_LINE`). A pasted template inside a block
  is rare, and the wrong read gives a readable false FAIL. Loss: that false
  FAIL could return.
- The empty words `TBD`, `TODO`, `?`, `...`, `…` and the dashes are not filled
  (narrowed from `METRICS_LINE_EMPTY_FAILS`, which keeps the blank value and
  the template slot). A filler word passing costs one harvest figure, no more
  than a wrong value does (§7 `VALUE_FILLED_BUT_FALSE`). Loss: a filler word
  could read as filled.
- `not recorded (<reason>)` and `not recorded — <reason>` are filled (narrowed
  from `METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED`, which keeps the colon form
  deliver teaches). deliver teaches only the colon form. Loss: either variant
  could become a false FAIL.
- A `--changelog FILE` that does not exist is exit 2, naming the path (the §7
  row `CHANGELOG_PATH_NAMED_MISSING`, now this line). deliver, canonize and
  harvest never pass `--changelog`. Loss: the named-file branch; exit 2 on a
  missing input stays held by `METRICS_SINCE_REQUIRED` and
  `METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD`.

### Declared tier and the rule

The declared tier comes from, in order: the `Tier:` value when it starts with
`T0`…`T3`, after stripping any leading backticks, asterisks and underscores
and an optional `Tier ` (case does not matter), so `` `T2` covered `` and
`**T2** covered` read as T2; else the heading's tier token; else none.

| Entry | Judged as |
|---|---|
| compact form | exempt |
| declared tier T0 or T1 | exempt: no other line is required |
| full form, declared tier T2, T3 or none | every label must be present and filled |
| full form, no block | `METRICS_BLOCK_MISSING` (the full form is the T2/T3 form) |
| `Tier:` present, filled, not `not recorded: <reason>`, and not starting with `T0`…`T3` after the stripping above | `METRICS_TIER_UNREADABLE`, and the other lines are still judged |

A `Tier:` value of `not recorded: <reason>` declares no tier, is filled, and
is not `METRICS_TIER_UNREADABLE`: the entry is judged as full form with no
tier.

### Command line

```text
session-metrics.py --since YYYY-MM-DD [--entry LINE] [--root DIR] [--changelog FILE] [--deliver FILE]
session-metrics.py --all [--json] [--root DIR] [--changelog FILE] [--deliver FILE]
session-metrics.py --labels [--root DIR] [--deliver FILE]
```

- `--root` is the graph root, `docs/graph` relative to the working directory
  by default. The changelog is `<root>/changelog.md` and the deliver node is
  `<root>/protocols/deliver.md`, unless `--changelog` or `--deliver` names
  another file.
- The lint role judges every delivery entry whose date is on or after
  `--since`. `--since` is required, and it is the grandfathering line: an
  entry dated before it is never judged.
- `--entry LINE` names the one entry the run judges: the delivery entry whose
  heading is on that 1-based line of the changelog, whatever its date. Every
  other delivery entry dated on or after `--since` is still read, and each of
  its defects is printed as a `note:` line that never changes the exit code. A
  LINE that is not a delivery heading outside a fence is exit 2, with no
  headline and one line naming the line and the accepted heading forms, in the
  same words as `NO_DELIVERY_ENTRY`:
  `<path>:<N>: ENTRY_LINE_NOT_A_DELIVERY_HEADING: line <N> is not a delivery heading; a delivery entry is a heading `Delivery — <title> — YYYY-MM-DD` or `T<n> delivery — <title> — YYYY-MM-DD``.
  Without `--entry`, every entry on or after `--since` is judged, which
  suits an audit; deliver runs with `--entry`.
- Why `--entry` and not an `--after-line N` the session records before it
  appends: many plants write their changelog newest first, so the new entry
  lands above line N and an after-line rule would judge nothing. `--entry`
  works in either order. Its cost is one lookup, the line of the heading the
  session just wrote (`grep -n`), and the run stays one command.
- `--all` and `--labels` are query roles: they never fail on content.

### Output and exit codes

Lint role, pass, without and with `--entry` (the tool's output is the
observed text; ` (line N)` names the judged entry when `--entry` is given):

```text
session metrics: PASS — 2 delivery entries since 2026-10-05: 1 filled, 1 exempt
session metrics: PASS — 1 delivery entry (line 38) since 2026-10-05: 1 filled, 0 exempt
```

Lint role, fail, one line per finding after the headline. The headline counts
the judged entries the same way; a `NO_DELIVERY_ENTRY` run, which judges none,
has the headline `session metrics: FAIL (1 finding) — <path>, entries since <since>`:

```text
session metrics: FAIL (2 findings) — docs/graph/changelog.md, 1 delivery entry (line 38) since 2026-10-05
  - docs/graph/changelog.md:41: METRICS_LINE_MISSING: Serial waits: the block has no `- Serial waits:` line; fill it, or write `not recorded: <reason>`
  - docs/graph/changelog.md:47: METRICS_REASON_MISSING: Spawns: `not recorded` needs a reason: `not recorded: <reason>`
  note: docs/graph/changelog.md:12: undated delivery heading, not judged
```

With `--entry`, a defect of another entry keeps its finding text after the
word `note:` and gains a closing clause:

```text
  note: docs/graph/changelog.md:9: METRICS_BLOCK_MISSING: the entry has no Session metrics block (not this run's entry; not judged)
```

`NO_DELIVERY_ENTRY` names no line. Its finding line is the path, the code and
one of two fixed messages, where `<path>` is the changelog as given or
resolved and `<since>` is the `--since` value:

```text
  - <path>: NO_DELIVERY_ENTRY: no delivery entry dated on or after <since>; a delivery entry is a heading `Delivery — <title> — YYYY-MM-DD` or `T<n> delivery — <title> — YYYY-MM-DD`
  - <path>: NO_DELIVERY_ENTRY: <path> does not exist; a delivery entry is a heading `Delivery — <title> — YYYY-MM-DD` or `T<n> delivery — <title> — YYYY-MM-DD`
```

| Code | Line it names | Meaning |
|---|---|---|
| `NO_DELIVERY_ENTRY` | none (the path only, in the shape above) | no delivery entry dated on or after `--since`, or no changelog at the default path; the message names the accepted heading forms |
| `METRICS_BLOCK_MISSING` | the entry's heading | a full-form entry with no Session metrics heading in its span |
| `METRICS_LINE_MISSING` | the block's heading | a label of the deliver node has no line in the block |
| `METRICS_LINE_EMPTY` | the line | the value is not filled (table above) |
| `METRICS_REASON_MISSING` | the line | `not recorded` with no reason |
| `METRICS_TIER_UNREADABLE` | the Tier line | a filled Tier value names no tier |

| Exit | When |
|---|---|
| 0 | lint: every judged entry is filled or exempt; query: always, on content |
| 1 | lint: at least one finding |
| 2 | usage error (no role, `--since` missing or not a date); `--entry` naming a line that is not a delivery heading; a missing input other than the one below; a file that cannot be read; a deliver node with no template block |

A missing input is exit 2, with its path named (the rule that an unreadable
input is named and fatal), except one case. In the lint role, when the
changelog is the default `<root>/changelog.md` and that file does not exist,
the run reports `NO_DELIVERY_ENTRY` and exits 1, because a plant with no
changelog has written no delivery. A `--changelog FILE` that does not exist is
exit 2: the caller named an input that resolves to nothing. So are a missing
graph root, a missing deliver node (default or `--deliver`), and, in the query
role, a missing changelog of either kind.

### Query output

`--all` prints one line per entry, in file order:

```text
<status>  <date or ->  <tier or ->  <path>:<line>  <heading text>
```

`--all --json` prints a JSON array, one object per entry, in file order:

```yaml
entry:
  line:     { type: integer }          # the heading's 1-based line
  heading:  { type: string }
  date:     { type: string, format: YYYY-MM-DD, nullable: true }
  marker:   { enum: [delivery, compact, unmarked] }
  tier:     { enum: [T0, T1, T2, T3], nullable: true }
  status:   { enum: [filled, exempt, incomplete] }
  lines:    { type: object, of: string }   # label as written -> value as written, trimmed; {} when the entry has no block
  findings: { type: array, of: { code: string, line: integer, message: string } }
```

`--labels` prints one label per line, in the template's order.

## 7. Failure modes

(Authored by `architect`.)

### Failure: PRE_RULE_ENTRY
- **Trigger:** a plant's changelog holds deliveries written before the reader
  existed, most of them with no block
- **Response:** never judged by the lint role, because `--since` is required
  and the session passes its own heading's date; `--all` reports them as
  `incomplete`, which is data
- **Side effects:** none
- **Recovery:** none needed. The changelog is append-only, so an old entry is
  never edited to pass

### Failure: HEADING_NOT_RECOGNIZED
- **Trigger:** the session titles its entry in a form the reader does not
  accept (forms seen in practice: `<title> — canonize close-out — <date>` and
  `<date> — <title>`)
- **Response:** without `--entry`, exit 1, `NO_DELIVERY_ENTRY`, naming the
  accepted forms. With `--entry`, the path deliver takes, exit 2,
  `ENTRY_LINE_NOT_A_DELIVERY_HEADING`, naming the line and the accepted forms
- **Side effects:** none
- **Recovery:** retitle the entry the session just wrote to the template form
  `Delivery — <title> — YYYY-MM-DD`, and run again

### Failure: UNDATED_DELIVERY_HEADING
- **Trigger:** a delivery heading carries no `YYYY-MM-DD`
- **Response:** not judged; a `note:` line names it. When it is the session's
  only entry, the run also fails with `NO_DELIVERY_ENTRY`
- **Side effects:** none
- **Recovery:** add the date to the heading

### Failure: BLOCK_BORROWED_FROM_NEXT_ENTRY
- **Trigger:** a full-form entry has no block, and the next entry at the same
  level, or a dated entry at any lower level (a graft entry, a close-out
  line), carries one
- **Response:** the entry's span ends at that next heading, so the block is
  not borrowed: `METRICS_BLOCK_MISSING`
- **Side effects:** none
- **Recovery:** add the block to the delivery entry

The price of `METRICS_DATED_HEADING_ENDS_ENTRY` is a known false FAIL, kept as
prose since the consolidation of 2026-10-05 (it was the failure row
`DATED_SUBHEADING_IN_ENTRY`): a delivery entry with a dated sub-heading above
its block (`### Increment 2 — <date>`) ends at that sub-heading, so its block is
not found and the run reports `METRICS_BLOCK_MISSING`. The session puts the
block above the sub-heading or drops the date; the template has no dated
sub-heading. No case holds it, because it asserts a cost, not a protection.

### Failure: NESTED_DELIVERY_HEADING
- **Trigger:** a delivery heading sits below another delivery heading at a
  lower level (`# Delivery — a — <date>` with no block, then
  `## T3 delivery — b — <date>` with a filled block)
- **Response:** the nested heading ends the outer entry's span (§6), so `a`
  reports `METRICS_BLOCK_MISSING` on its heading's line and `b` is judged on
  its own block
- **Side effects:** none
- **Recovery:** give each delivery entry its own block

### Failure: SAME_DAY_EARLIER_ENTRY
- **Trigger:** two sessions deliver on the same day; the earlier one left an
  incomplete entry and the later one runs `--since` that day
- **Response:** with `--entry`, the run judges only the later session's entry;
  the earlier entry's defects print as `note:` lines and do not change the exit
  code (`METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE`). Without `--entry`, both are
  judged, as an audit should
- **Side effects:** none
- **Recovery:** none needed for the later session. It may name the earlier
  entry's defect under Known limitations; the changelog stays append-only

### Failure: ENTRY_LINE_NOT_A_DELIVERY_HEADING
- **Trigger:** `--entry LINE` names a line that is not a delivery heading (a
  body line, a fenced line, a non-delivery heading, or past the end)
- **Response:** exit 2, one fixed line naming the changelog, the line and the
  accepted heading forms in the same words as `NO_DELIVERY_ENTRY` (§6), so a
  mistitled heading gets its recovery text; no entry judged
- **Side effects:** none
- **Recovery:** pass the line of the heading the session wrote

### Failure: DELIVER_NODE_REWORDED
- **Trigger:** an edit to `protocols/deliver.md` removes the fenced template or
  its `## Session metrics` heading, or changes a label
- **Response:** in the seed, `METRICS_SHIPPED_DELIVER_NODE_PARSES` fails the
  gate; in a plant, the lint exits 2 naming the node. A changed label is
  followed, not refused: every later entry is checked against the new list
- **Side effects:** none
- **Recovery:** keep the template fenced, or update the edit

### Failure: PLANT_CUSTOMIZED_BLOCK
- **Trigger:** a plant adds or renames a line in its own deliver node
- **Response:** by design, the plant is checked against its own block
  (`METRICS_LABELS_FROM_DELIVER_NODE`); harvest's `--all` reports the plant's
  labels as written
- **Side effects:** harvest sees label sets that differ between plants
- **Recovery:** none; the query role keeps every label so the difference is
  visible

### Failure: CHANGELOG_UNREADABLE
- **Trigger:** the changelog exists and cannot be read or decoded
- **Response:** exit 2, the path and "could not be read"
- **Side effects:** none
- **Recovery:** fix the file's mode or encoding

### Failure: DELIVERY_SKIPPED_THE_RUN
- **Trigger:** the session never runs the lint at deliver
- **Response:** nothing. The class is detective (§5): no hook runs the reader
- **Side effects:** an incomplete entry lands; the next `--all` shows it as
  `incomplete`
- **Recovery:** the canonize librarian or the next session runs `--all` and
  reports it. A warn-first Stop hook that runs the lint is a later decision,
  once deliveries carry the block (the same rule deliver.md applies to the
  attribution hook)

### Failure: TIER_UNDER_DECLARED
- **Trigger:** a Tier 2 or Tier 3 session writes `Tier: T1` to skip the other
  lines
- **Response:** exempt. The reader cannot tell a declared tier from the true one
- **Side effects:** the entry carries no numbers
- **Recovery:** the reviewer reads the tier against the plan; accepted residual

### Failure: VALUE_FILLED_BUT_FALSE
- **Trigger:** a filled value is wrong, or a reason is a placeholder in words
  (`not recorded: n/a`)
- **Response:** filled. The reader checks presence and shape, not truth
- **Side effects:** harvest aggregates a wrong number
- **Recovery:** deliver.md's rule that the orchestrator fills each line from its
  own trace; accepted residual (ADR-0003 class: semantic)

## 8. Examples

Filled, Tier 3 (passes):

```markdown
## T3 delivery — move the client onto one origin — 2026-10-05

### Session metrics
- Tier: T3 (reclassified: none)
- Spawns: 5 (architect×1 opus/high, tester×2 sonnet/medium, implementer×2 sonnet/medium)
- Route bands: HIGH×4 MEDIUM×1 — overrides: none
- Retries: none
- Gates: 6 run, 1 failed then fixed
- Full-suite runs: 2 (1 red)
- Serial waits: not recorded: the host shows no spawn ids
- Overflow notes: none
- Quality: review 0 Critical / 1 Major; no mutation pass
```

Exempt by tier (passes):

```markdown
# Delivery — fix a typo in the runbook — 2026-10-05

## Session metrics
- Tier: T1 (reclassified: none)
```

Failing:

```markdown
# Delivery — add the export endpoint — 2026-10-05

## Session metrics
- Tier: T2 covered
- Spawns: not recorded
- Route bands:
```

Here the run reports `METRICS_REASON_MISSING` on Spawns, `METRICS_LINE_EMPTY`
on Route bands, and one `METRICS_LINE_MISSING` for each of the six labels that
have no line.

## 9. Acceptance criteria

(Drafted by `architect` for `product`.)

- [ ] AC-1: a T2/T3 delivery entry with a filled block passes (a canonical
  `not recorded: <reason>` counts as filled), and one with no block, a missing
  line, an empty value or template slot, or a reasonless `not recorded` fails
  with a finding naming the file, line and label; maps to
  METRICS_FILLED_ENTRY_PASSES, METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED,
  METRICS_BLOCK_MISSING_FAILS, METRICS_LINE_MISSING_FAILS,
  METRICS_LINE_EMPTY_FAILS, METRICS_NOT_RECORDED_WITHOUT_REASON_FAILS. The
  Tier diagnostics, fenced lines and the empty words are reading rules no
  contract holds (§6)

- [ ] AC-2: T0/T1 and compact entries are exempt; maps to
  METRICS_LOW_TIER_EXEMPT, METRICS_COMPACT_ENTRY_EXEMPT
- [ ] AC-3: entries before the session's date are never judged, and a session
  that wrote no entry fails; maps to METRICS_ENTRIES_BEFORE_SINCE_NOT_JUDGED,
  METRICS_NO_ENTRY_SINCE_FAILS, METRICS_MISSING_CHANGELOG_FAILS,
  METRICS_SINCE_REQUIRED
- [ ] AC-4: the reader judges a heading in the template form
  `Delivery — <title> — YYYY-MM-DD` or the form
  `T<n> delivery — <title> — YYYY-MM-DD`, at any level, and no other heading:
  not a fenced line, not a heading whose first word is not `Delivery` after an
  optional tier token, not one where a hyphen inside a word or a colon follows
  `Delivery`; a same-level section heading the template names stays inside the
  entry, and a dated heading at any level ends it; maps to
  METRICS_ENTRY_HEADINGS_RECOGNIZED, METRICS_SECTION_HEADINGS_STAY_IN_ENTRY,
  METRICS_DATED_HEADING_ENDS_ENTRY
- [ ] AC-5: the block's line list has one home, the deliver node, and the
  shipped node parses; maps to METRICS_LABELS_FROM_DELIVER_NODE,
  METRICS_SHIPPED_DELIVER_NODE_PARSES,
  METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD
- [ ] AC-6: an unreadable input is named and fatal; maps to
  METRICS_UNREADABLE_CHANGELOG_FAILS_LOUD
- [ ] AC-7: harvest can read every entry's raw values, and the query role
  exits 0 whatever the content, an entry with no block reported `incomplete`
  with `lines: {}`; maps to METRICS_ALL_REPORTS_EVERY_ENTRY
- [ ] AC-8: the reader runs in a fresh plant; maps to
  METRICS_READER_RUNS_IN_A_FRESH_PLANT
- [ ] AC-9: a defect in an earlier same-day entry does not fail the run of a
  session whose own entry is filled; it is named on a `note:` line; maps to
  METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE
- [ ] AC-10: every line number the reader prints or takes is the one `grep -n`
  gives, and a byte-order mark does not hide line 1; maps to
  METRICS_LINES_COUNTED_AS_GREP_DOES, METRICS_LEADING_BOM_IGNORED

**Shipping condition.** The reader ships only together with the
`protocols/deliver.md` wording it enforces, in the same increment as its
GREEN: the accepted heading forms, the canonical `not recorded: <reason>`, and
the run at deliver with `--since` and `--entry`. Without that wording a plant
session meets rules its own deliver node does not state. A gate holds part
of it: `METRICS_SHIPPED_DELIVER_NODE_PARSES` reads the shipped
`protocols/deliver.md` for the run (`session-metrics.py --since` with
`--entry`), so the reader's GREEN cannot pass without the command deliver
tells the session to run. No gate holds the heading forms or the canonical
`not recorded: <reason>` wording; since the consolidation of 2026-10-05 that
is a recorded coverage loss (§10).

## 10. Test mapping

(Owned by `tester`; drafted by `architect`.) Each row names the case that
holds it, and one case may hold several rows; each case carries its label and
the slugs it asserts as comments. Since the consolidation of 2026-10-05 the
cases are X399, X400, X404, X406 to X410, X412 to X414, X416, X417 and X423 in
`tests/test-session-metrics.sh`, X415 in `tests/test-lint-audibility.sh`, and
E14 in `tests/test-full-install.sh`. The other labels of `X397` to `X424` are
retired, and the dated paragraphs below them are history.

**RED (2026-10-05).** Every row with a test is `red`: each case was observed
failing on its own assertion for the missing reader, the rc-2 cases (X409,
X414, X415) on their message check. That includes X417, which holds
`METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE`, `SAME_DAY_EARLIER_ENTRY` and
`ENTRY_LINE_NOT_A_DELIVERY_HEADING`, and the arms holding
`NESTED_DELIVERY_HEADING` (X399 arm c) and `CHANGELOG_PATH_NAMED_MISSING`
(X408 arm b). The failure rows marked `none` are accepted residuals with no
test.

**Product re-review (2026-10-05).** Three arms were added for it and each was
observed red, so their rows are `red`: X417 arm (c), a mistitled heading named
by `--entry`; X417 arm (d), the session's entry above the other one; and the
X413 assertion that the shipped deliver node names the run (and then also the
reason form, a check the consolidation cut). Both X413 rows stay `red` after
the reader lands, until the deliver.md wording lands.

**GREEN (2026-10-05).** `tools/session-metrics.py` landed with the deliver.md
and canonize.md wording, and every row with a test is `green`, both X413 rows
included. Ten guard mutations, each reverted, made their own case fail (§12).

**Code review (2026-10-05).** The contract widened after the first GREEN:
seven new contracts (X418 to X424), one new failure (X420 arm b) and two
widened Givens (X401, X410). The tester wrote each case and saw it fail, or
pass on arrival as a guard held by a mutation, and the second GREEN turned
every row `green` (§12).

**Consolidation (2026-10-05).** The owner approved cutting the suite under
`test-first.proportionate-checks`: the reader is detective, so a wrong verdict
costs a readable false FAIL or one harvest figure, and mutation proof is not
owed. Five contracts retired and three Givens narrowed (§4, §6); 29 → 24
contracts. The surviving suite is 14 cases in `tests/test-session-metrics.sh`
(X399, X400, X404, X406, X407, X408, X409, X410, X412, X413, X414, X416, X417,
X423), one row in `tests/test-lint-audibility.sh` (X415) and E14: no more cases
than contracts, and no fixture files. Every row whose case is merged, moved or
rebuilt was `pending` until the tester landed the cut; the cut landed on 2026-10-05 and each of those rows is now `green`. Each deleted case names
its survivor, or records a coverage loss:

| Cut case | Survivor | Coverage loss |
|---|---|---|
| X397 filled entry | X417 arm (a) | none |
| X398 not-recorded forms | X400 (colon form) | the `(reason)` and `— reason` forms (§6) |
| X399 arms (b), (c); X420 arm (a) | X399 span fixture | none |
| X401 empty values | X400 (blank, slot) | the empty words (§6) |
| X402 reason missing | X400 block defects | none |
| X403 unreadable Tier | none | the `METRICS_TIER_UNREADABLE` hint (§6) |
| X405 compact | X404 | none |
| X408 arm (b) named `--changelog` | none | the named-file branch (§6) |
| X411 flat sections | X410 | none |
| X413 `not recorded: <reason>` grep | none | the wording read-back |
| X415 | `tests/test-lint-audibility.sh` row X415 | none |
| X417 arm (b) body line | X417 arm (c) | none |
| X418, X419 Tier rules | none | markup stripping; the not-recorded Tier (§6) |
| X420 arm (b) dated sub-heading | none | none: it asserted a known false FAIL (§7 prose) |
| X421 date is last | none | the last-date rule (§6) |
| X422 fenced line | none | the fenced-line rule (§6) |
| X424 byte-order mark | X417 arm (d) | none |

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| METRICS_FILLED_ENTRY_PASSES | X417 case_other_entry_is_a_note: arm (a), the session's filled entry passes under `--entry` | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED | X400 case_block_defects: one canonical `not recorded: <reason>` line among the defects, not flagged | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_BLOCK_MISSING_FAILS | X399 case_entry_span: the span fixture, a blockless full-form entry | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_LINE_MISSING_FAILS | X400 case_block_defects: a dropped line | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_LINE_EMPTY_FAILS | X400 case_block_defects: a blank value and a template slot | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_NOT_RECORDED_WITHOUT_REASON_FAILS | X400 case_block_defects: a bare `not recorded` | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_LOW_TIER_EXEMPT | X404 case_exemptions: a T1 Tier line and a `T0 delivery` heading | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_COMPACT_ENTRY_EXEMPT | X404 case_exemptions: a compact heading (`3 exempt`) | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_ENTRIES_BEFORE_SINCE_NOT_JUDGED | X406 case_before_since_not_judged | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE | X417 case_other_entry_is_a_note: arms (a) and (d) | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_NO_ENTRY_SINCE_FAILS | X407 case_no_entry_since | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_MISSING_CHANGELOG_FAILS | X408 case_missing_changelog: arm (a) only | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_SINCE_REQUIRED | X409 case_since_required | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_ENTRY_HEADINGS_RECOGNIZED | X410 case_entry_headings | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_DATED_HEADING_ENDS_ENTRY | X399 case_entry_span: a dated `##` close-out below a `#` delivery | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_SECTION_HEADINGS_STAY_IN_ENTRY | X410 case_entry_headings: one entry written flat | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_LINES_COUNTED_AS_GREP_DOES | X423 case_lines_as_grep | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_LEADING_BOM_IGNORED | X417 case_other_entry_is_a_note: arm (d), the file starts with the byte-order mark, `--entry 1` | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_LABELS_FROM_DELIVER_NODE | X412 case_labels_from_node: the Tokens node built in the case from `protocols/deliver.md` | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_SHIPPED_DELIVER_NODE_PARSES | X413 case_shipped_deliver_node: the labels and the `--since … --entry` command line | tests/test-session-metrics.sh | unit (real tree) | green |
| METRICS_DELIVER_NODE_UNPARSEABLE_FAILS_LOUD | X414 case_deliver_node_unparseable: the no-fence node built in the case | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_UNREADABLE_CHANGELOG_FAILS_LOUD | X415, one row of the unreadable-input sweep | tests/test-lint-audibility.sh | unit (fixture) | green |
| METRICS_ALL_REPORTS_EVERY_ENTRY | X416 case_all_json | tests/test-session-metrics.sh | unit (fixture) | green |
| METRICS_READER_RUNS_IN_A_FRESH_PLANT | E14 case_session_metrics_in_plant | tests/test-full-install.sh | integration (temp install) | green |
| PRE_RULE_ENTRY | X406 case_before_since_not_judged | tests/test-session-metrics.sh | unit (fixture) | green |
| HEADING_NOT_RECOGNIZED | X407 case_no_entry_since: the message names the accepted forms | tests/test-session-metrics.sh | unit (fixture) | green |
| HEADING_NOT_RECOGNIZED | X417 case_other_entry_is_a_note: arm (c), `--entry` naming `# mine — canonize close-out — 2026-10-05` | tests/test-session-metrics.sh | unit (fixture) | green |
| UNDATED_DELIVERY_HEADING | X407 case_no_entry_since: the `note:` line | tests/test-session-metrics.sh | unit (fixture) | green |
| BLOCK_BORROWED_FROM_NEXT_ENTRY | X399 case_entry_span: a same-level graft entry carrying a block | tests/test-session-metrics.sh | unit (fixture) | green |
| NESTED_DELIVERY_HEADING | X399 case_entry_span: `## T3 delivery` nested under a blockless `#` delivery | tests/test-session-metrics.sh | unit (fixture) | green |
| SAME_DAY_EARLIER_ENTRY | X417 case_other_entry_is_a_note: arm (a) | tests/test-session-metrics.sh | unit (fixture) | green |
| ENTRY_LINE_NOT_A_DELIVERY_HEADING | X417 case_other_entry_is_a_note: arm (c) | tests/test-session-metrics.sh | unit (fixture) | green |
| DELIVER_NODE_REWORDED | X413 case_shipped_deliver_node | tests/test-session-metrics.sh | unit (real tree) | green |
| PLANT_CUSTOMIZED_BLOCK | X412 case_labels_from_node | tests/test-session-metrics.sh | unit (fixture) | green |
| CHANGELOG_UNREADABLE | X415, the same unreadable-input row | tests/test-lint-audibility.sh | unit (fixture) | green |
| DELIVERY_SKIPPED_THE_RUN | none: detective class, no hook (§5, §7) | — | — | — |
| TIER_UNDER_DECLARED | none: accepted residual (§7) | — | — | — |
| VALUE_FILLED_BUT_FALSE | none: accepted residual (§7) | — | — | — |

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Should grow's delivery and graft's Phase 8 entry carry the block under a delivery heading? | grow.md asks for growth metrics "the delivery block"; graft's `# Graft — …` entry is not read | Out of scope: only delivery headings are judged; harvest's `--all` still reports a block under any heading as `unmarked` | owner | the Phase 4 harvest.md amendment |
| The list of tools placed into plants has three homes: the `place_file` calls in `install.sh`, the `tools` map in `manifest.json`, and `DELIVERED_TOOLS` in `tools/graft-audit.py`. Adding this reader needed all three, and only install-placement's backup check holds them in sync, by behavior | a fact with three homes drifts; the owner's pure-graph decision says derive copies from one home | follow-up, not this increment: derive `DELIVERED_TOOLS` (and, if it can, the installer's list) from the manifest `tools` map | architect | a later increment of the round |

## 12. Changelog

- 2026-10-05 — created in `draft` by `architect` from the owner's decision of
  2026-10-05 that a reader enforces the session-metrics block: §0 to §2, §4 to §8, §11; §3 and §9 drafted for `product`; §10 drafted
  for `tester`. Twenty-one contracts, all pending their RED.
- 2026-10-05 — promoted to `active` by `architect` with the RED of
  `tests/test-session-metrics.sh` (X397 to X416) and `tests/test-full-install.sh`
  (E14), every contract row `red`; tester signed, product not yet. Three gaps the
  tester's review found are closed without changing any design decision. §6: a
  delivery heading at any level ends the previous delivery entry's span, so a
  nested delivery entry neither lends nor borrows a block; `NO_DELIVERY_ENTRY`
  has a fixed line shape and two fixed messages naming the accepted heading
  forms; a missing input is exit 2 except the default changelog in the lint
  role, so an explicit `--changelog` that does not exist is exit 2; an entry
  with no block has `lines: {}`. §7 gains `NESTED_DELIVERY_HEADING` and
  `CHANGELOG_PATH_NAMED_MISSING`, each `pending` in §10 until its case arm
  lands. Contract count unchanged at 21.
- 2026-10-05 — amended by `architect` after the product review, which did not
  sign. Still `active`; product unticked. §6 and §3: the lint role takes an
  optional `--entry LINE` that judges only the session's own entry and prints
  every other since-date defect on a `note:` line that never changes the exit
  code, so a session can always reach a pass by fixing only its own entry.
  `--entry` was chosen over an `--after-line N` the session records before it
  appends, because many changelogs are written newest first, where the new
  entry lands above N. §4 gains `METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE`
  (contracts 21 → 22); §7 `SAME_DAY_EARLIER_ENTRY` is no longer an accepted
  residual, and `ENTRY_LINE_NOT_A_DELIVERY_HEADING` is new; §10 maps all three
  to X417, `pending`. §9: AC-1 names the tier case, AC-4 is reworded to the
  heading rule, AC-7 states the query role's exit 0, AC-9 is new, and a
  shipping condition ties the reader to the deliver.md wording it enforces. §11
  rows 2 and 3 resolve in the same increment as the reader's GREEN.
- 2026-10-05 — X417 observed red by `tester` (its own assertion, no reader),
  and the rows of `METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE`, `SAME_DAY_EARLIER_ENTRY`,
  `ENTRY_LINE_NOT_A_DELIVERY_HEADING`, `NESTED_DELIVERY_HEADING` and
  `CHANGELOG_PATH_NAMED_MISSING` flipped `pending` → `red`; the RED now spans
  X397 to X417 and E14.
- 2026-10-05 — amended by `architect` after the product re-review, which did
  not sign. Still `active`; product unticked; contract count unchanged at 22.
  §6 and §7: `ENTRY_LINE_NOT_A_DELIVERY_HEADING` has one fixed line naming the
  line and the accepted heading forms in the same words as `NO_DELIVERY_ENTRY`,
  and `HEADING_NOT_RECOGNIZED` covers the run with `--entry`; the exit table
  lists it. §4: `METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE` holds in either order;
  `METRICS_SHIPPED_DELIVER_NODE_PARSES` also requires the shipped deliver node
  to name the run and the reason form, so a gate holds the §9 shipping
  condition. §10: three owed arms, `pending` (X417 arms c and d, the X413
  wording assertion).
- 2026-10-05 — the three rows added at the product re-review flipped
  `pending` → `red` once each arm was observed failing on its own assertion:
  `HEADING_NOT_RECOGNIZED` (X417 arm c), `METRICS_OTHER_ENTRY_DEFECT_IS_A_NOTE`
  (X417 arm d) and the X413 shipping-condition row; §10's paragraph now says
  so. No contract changed.
- 2026-10-05 — `implemented`, by `architect`, with the GREEN of
  `tools/session-metrics.py` by `implementer`: every §10 row with a test is
  `green` (`tests/test-session-metrics.sh`, 21 cases; E14 in
  `tests/test-full-install.sh`), and spec-lint counts all 22 contracts covered.
  The deliver.md wording (heading forms, `not recorded: <reason>`, the run with
  `--since` and `--entry`) and canonize.md's reworded Session metrics
  paragraph landed in the same increment, so the §9 shipping condition holds
  and X413 passes on the shipped node; §11's two wording rows are resolved and
  removed. Ten guard mutations of the reader, each reverted, failed their own
  case: a nested delivery heading not ending the span, a bare `not recorded`
  read as filled, fences ignored for headings, other entries' defects made
  findings, section names not kept in the entry, entries before `--since`
  judged, unmarked blocks dropped, labels hard-coded, an unreadable tier not
  reported, T0/T1 not exempt. A read-only `--all --json` query over eight plant
  changelogs exited 0 on seven and found one delivery entry, filled; the eighth
  carries an older deliver node with no fenced template and exited 2 as §6
  says, and exited 0 with the seed's node through `--deliver`. Placement:
  `install.sh` places the reader with `place_file`, `manifest.json` lists it,
  and `tools/graft-audit.py` maps its fast-forward backup. The lint headline
  with `--entry` adds ` (line N)` after the count, which §6 leaves free.
- 2026-10-05 — amended by `architect` after the independent code review of the
  GREEN. Back to `active`: the contract widened, so the evidence is owed
  again (frontmatter), and the product and tester boxes are cleared for a
  re-look. Contracts 22 → 29. Decisions, each the smallest rule that closes the
  finding. §6 gains "Reading the file": a line is counted the way `grep -n`
  counts (only `\n` ends a line, a `\r` before it is dropped), because deliver
  finds `--entry` with `grep -n` and a U+2028 or a form feed shifted every later
  number (`METRICS_LINES_COUNTED_AS_GREP_DOES`); a leading byte-order mark is
  ignored (`METRICS_LEADING_BOM_IGNORED`). A fenced line is not a metrics line
  (`METRICS_FENCED_LINE_NOT_A_METRICS_LINE`). A dated heading at any level ends
  a delivery entry, chosen over a recorded residual because a borrowed block is
  a false pass, the one outcome the lint exists to prevent; its cost, a false
  fail on a dated sub-heading inside an entry, is the new failure
  `DATED_SUBHEADING_IN_ENTRY` (`METRICS_DATED_HEADING_ENDS_ENTRY`). The heading
  separator is an em or en dash, or a hyphen with white space on both sides;
  the colon form is dropped, since the template never uses it and an ordinary
  title takes it (`METRICS_ENTRY_HEADINGS_RECOGNIZED` widened). Leading
  backticks, asterisks and underscores are stripped from a Tier value
  (`METRICS_TIER_IN_MARKUP_READ`). Of the five rules whose mutations survived,
  three gain contracts: the last date in a heading
  (`METRICS_ENTRY_DATE_IS_LAST_IN_HEADING`), `Tier: not recorded: <reason>`
  (`METRICS_TIER_NOT_RECORDED_DECLARES_NONE`) and the empty words
  (`METRICS_LINE_EMPTY_FAILS` widened); continuation lines and the block's end
  at the next heading are stated in §6 as reading rules no contract holds,
  because each needs a hand-made input the template never writes. §6's
  headline examples now match the reader's output, ` (line N)` included. §11
  records the three homes of the placed-tools list as a follow-up.
- 2026-10-05 — `implemented` again, by `architect`, with the second GREEN by
  `implementer`, after the tester's RED of X418 to X424 and the widened X401
  and X410 arms; product and tester re-signed. `tests/test-session-metrics.sh`
  passes its 28 cases and E14 passes; every §10 row with a test is `green`,
  and spec-lint counts all 29 contracts covered, so nothing the code-review
  entry above listed as owed is still owed. The reader now counts lines as
  `grep -n` does, ignores a leading byte-order mark, skips fenced lines in a
  block, ends an entry at a dated heading, takes the dash or spaced-hyphen
  separator only, and strips markup from a Tier value. Nine guard mutations,
  each reverted, failed their own case: line splitting on every separator, a
  kept byte-order mark, the fence mask ignored in a block, a dated heading not
  ending the span, the old separator with the colon and bare hyphen, no markup
  strip, the first date winning, a not-recorded Tier read as unreadable, and
  a reduced set of empty words. A read-only `--all --json` query over the eight
  plant changelogs, with the seed's deliver node through `--deliver`, still
  finds one delivery entry, filled. The plan-of-record bookkeeping for the
  seven new contracts belongs to the plan, not this spec.
- 2026-10-05 — consolidation, by `architect`, on the owner's approval of the
  tester's proposal under `test-first.proportionate-checks`. Contracts
  29 → 24, no contract added: retired `METRICS_TIER_UNREADABLE_FAILS`,
  `METRICS_TIER_IN_MARKUP_READ`, `METRICS_TIER_NOT_RECORDED_DECLARES_NONE`,
  `METRICS_ENTRY_DATE_IS_LAST_IN_HEADING` and
  `METRICS_FENCED_LINE_NOT_A_METRICS_LINE` (each a `### Retired:` stub in §4);
  narrowed `METRICS_NOT_RECORDED_WITH_REASON_IS_FILLED` to the colon form,
  `METRICS_LINE_EMPTY_FAILS` to the blank value and the template slot, and
  `METRICS_SHIPPED_DELIVER_NODE_PARSES` to the command line; the §7 rows
  `CHANGELOG_PATH_NAMED_MISSING` and `DATED_SUBHEADING_IN_ENTRY` became prose.
  Each retired or narrowed rule stays the reader's behaviour and is listed in §6
  "Reading rules no contract holds" with why it has no named blast radius and
  its coverage loss; §10 records each cut case's survivor or loss. AC-1 and
  AC-3 lose their mappings to retired contracts. Status `implemented` →
  `active`, because spec-lint refuses an `implemented` spec with a `pending`
  row, and the merged cases' rows are `pending` until the tester lands the cut.
  Sign-offs untouched.
- 2026-10-05 — `implemented` again, by `architect`, with the consolidation
  landed by `tester`: `tests/test-session-metrics.sh` is 14 cases (X399, X400,
  X404, X406 to X410, X412 to X414, X416, X417, X423), down from 28 plus six arm
  functions, and every deliver node is built from the shipped
  `protocols/deliver.md`, so `tests/fixtures/session-metrics/` is deleted; X415
  is a row of `tests/test-lint-audibility.sh`; E14 is unchanged. The tool is
  unchanged. Every §10 row over the 24 contracts is `green`; the 28-case suite,
  29 contracts and the mutation runs named in earlier entries describe the
  suite before this cut. One sanity check replaced mutation proof: a copy of the
  reader that never reports an empty value fails X400. The donor query of the
  second GREEN stands, since the reader did not change. §4's preamble and
  `METRICS_LABELS_FROM_DELIVER_NODE` now name the shipped node in place of the
  deleted fixtures, and §10's preamble names the surviving cases.
