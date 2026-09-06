---
name: humanizer
description: Draft or revise prose a person will read (documentation, README text, ADR and spec bodies, runbooks, pull-request descriptions, commit messages, delivery summaries, briefs and reports for the owner) so it reads as deliberate writing by a competent author, without changing what it says. Use when a draft came out of a model and shows the tells (empty contrasts, staged openers, one-line closers, forced triads, dash dependence, inflated significance, bold labels on every item, chatbot residue), when drafting finished prose from notes, or as the last pass before such text is handed off. Preserves facts, numbers, conditions, requirement levels, citations and voice; adds no fact; never fakes a human author or chases a detector score. The doctrine is method.prose-posture; docs/graph/prose-lint.py is the mechanical floor and the fact-preservation check.
id: skill.humanizer
tier: 2
kind: skill
origin: seed
title: humanizer — prose a person will read is drafted or revised by judgment, with every fact intact
owns:
  - humanizer.method
  - humanizer.document-contract
  - humanizer.progressive-execution
  - humanizer.fact-preservation
  - humanizer.modes
  - humanizer.scope
requires:
  - method.prose-posture
peers:
  - skill.holistic-editing
  - skill.adr-writer
  - skill.spec-author
  - agent.docs-librarian
  - protocol.deliver
load_when:
  - "this reads like it was written by an AI, remove the AI tells, humanize this text, it sounds like a chatbot"
  - "rewrite the documentation so it reads naturally, plain-language pass on the docs, make the README sound human"
  - "draft the report, brief, or memo from these notes; turn the bullets into finished prose"
  - "not X but Y, one-line closer, forced triad, too many em dashes, bold labels on every bullet, decorative headings"
  - "polish the pull-request description, commit message, or delivery summary before hand-off"
  - "did the rewrite drop a fact, prose-lint --against, fact preservation after a prose edit"
  - "audit this document for prose quality without rewriting it"
est_tokens: 3300
---

# humanizer

This skill drafts or revises expository prose whose value depends on the
reader understanding and trusting it. Its doctrine is
`docs/graph/method/prose-posture.md`: meaning governs style, the information
contract is preserved, structure carries emphasis, genre outranks generic
advice, voice is a constraint, and editing stops when the prose does its
job. This node holds the procedure that applies the doctrine and the tool
that floors it.

Two halves do the work. The skill is the judgment: what the document must
cause the reader to understand or do, which claims must survive, which
diagnostics apply, what the voice is. The tool `docs/graph/prose-lint.py`
(seed home `tools/prose-lint.py`) is the floor under that judgment: it
reports the tells a pattern can catch, and with `--against <rev>` it proves
that a rewrite added and dropped nothing.

## When to apply this skill

- A document, README, runbook, or node body is being written or refreshed
  for people, and the draft came out of a model or from notes.
- An ADR or spec body is about to flip to `accepted` or `active`
  (`docs/graph/skills/adr-writer.md`, `docs/graph/skills/spec-author.md`).
  The record is prose someone reads in a year.
- The `deliver` protocol's full-form summary, a pull-request description, or
  a commit message is being prepared. Other people read these most and edit
  them least.
- A reviewer or the owner says the text "sounds like an AI".
- Text imported from outside the project (a harvest import, a vendored
  guide) will be read as the project's own voice.

Out of scope: code, commands, frontmatter, `owns:` and `load_when:` lists,
generated tables, the kernel, and the seed's own machinery prompts. The
machinery is edited by `grill` and `holistic-editing`, never by a prose
pass. Fiction is out of scope; invented detail is its task.

## The document contract

Before drafting or revising substantial prose, settle a compact contract.
For a short edit, infer it in a moment and proceed; for long, high-stakes,
or multi-source work, let it govern every section. It is internal unless
the owner asks for the reasoning or an audit.

- Purpose: what must this document cause the reader to understand, decide,
  approve, do, or remember?
- Audience: what does the reader know, what terminology can they handle,
  what do they care about, what is their likely next action?
- Genre: which profile in `prose-posture.genre-outranks` applies?
- Substance: which claims, evidence, instructions, and caveats must survive?
- Priority: which one to three ideas matter most?
- Authority: which statements are facts, attributed claims, inferences,
  assumptions, recommendations, unknowns, or contested
  (`prose-posture.claim-classes`)?
- Voice: the owner's sample if one exists; otherwise the restrained default
  for the genre, in the plant's declared `deliverable_language`.
- Constraints: length, format, required sections, terminology, headings
  other documents anchor to.
- End state: what should a competent reader be able to say or do after
  reading?

## Progressive execution

Use the lightest process that reliably fits the task.

**Level 1, local edit** (a paragraph, a commit message, a summary): infer
purpose and voice; preserve the claims; revise the weak sentences or
paragraph; run the fidelity and naturalness checks; return the prose.

**Level 2, document revision** (a README, a runbook, a node body, a
multi-section document): settle the contract; map sections and claims; find
the structural defects; revise section by section; harmonize voice and
terminology; audit repetition across sections; verify facts, citations, and
conditions; return the document.

**Level 3, high-stakes synthesis** (a long technical or legal-adjacent
document, a multi-source report, an owner brief that will drive a
decision): settle the contract; keep a claim and source ledger; classify
authority and uncertainty; design the information architecture; draft or
rewrite bounded sections; verify each against its sources; test coherence
across the document; audit citations and quantities; review genre and
voice; run the adversarial pass; finalize. Level 3 ceremony is never spent
on a short paragraph.

## Rewriting existing prose: the passes

1. **Understand before editing.** Read the whole relevant section. Name
   what the passage is trying to do, which claims are indispensable, where
   the logic changes, whether paragraph boundaries match it, which terms
   must stay stable, and what voice the source has. Run
   `python3 docs/graph/prose-lint.py --file <path>` and add its findings to
   your own; it sees density (dash rate, bold-label runs, intensifier
   clusters) better than a reader does, and it misses voice entirely. Do
   not start with a word-replacement pass.
2. **Rebuild weak structure.** For each weak paragraph: state its job in a
   few words, list its indispensable claims, choose a natural order, delete
   staging and duplicated emphasis, write the paragraph again. Reuse source
   sentences that already work. A paragraph that is clear, exact, and
   genre-appropriate stays unchanged.
3. **Edit sentences.** Inspect actor, verb, referent, qualifier, clause
   order, modifier placement, terminology, punctuation, length, and
   repetition, against the diagnostics in `prose-posture.diagnostics` and
   the decision rules in `prose-posture.decision-rules`.
4. **Check the document's rhythm.** Look across paragraphs for the repeats
   invisible sentence by sentence: the same opener, closer, list length,
   paragraph size, transition, or contrast structure. Change repetition
   only where it is accidental or templated.
5. **Audit fidelity.** Compare the rewrite with the source: every number,
   date, proper noun, technical term, quoted phrase, citation, condition,
   exception, modal verb, causal statement, comparative, ranking, and scope
   phrase. Then run
   `python3 docs/graph/prose-lint.py --file <path> --against HEAD` (or the
   revision the edit started from). An unsupported addition or a material
   omission is an error; the rewrite is wrong until it is restored. Finally
   search for the tells that most often survive a rewrite: an empty
   contrast, a one-line closer, a dash, a triad, a bold label.

### Drafting from notes

Do not turn each bullet into one sentence. Settle the contract; classify
each note as claim, evidence, context, caveat, recommendation, instruction,
example, or open question; detect duplicates and contradictions; choose the
information order; decide which notes deserve paragraphs, lists, tables, or
omission; draft paragraphs around reader questions; add connective
reasoning only where the relationship is supported; keep uncertainty and
unresolved points visible ("The notes do not establish whether..."); revise
for voice and genre; verify every concrete statement against the notes.

## What the fact-preservation check proves

A rewrite is a claim that nothing changed except the words. The tool makes
the claim testable: for each file, the working copy and `git show
<rev>:<path>` must agree on the sorted multiset of numbers, heading texts,
inline code spans, fenced blocks, link targets, and requirement levels
(must, must not, shall, should, may, never, required, prohibited). These
classes are where facts hide in prose: a count, a version, a name in
backticks, a command, a destination, an obligation. A drift is reported as
what was added and what was dropped, and it blocks. The check does not
prove the prose is good; it proves the rewrite is honest. Both halves are
required before the text is handed off.

Counts stated in the seed's own documentation are also cross-checked
against `manifest.json` by `tests/seed-lint.py`; a rewrite that drops "13
skills" from a sentence fails there as well.

## Verification, proportional to consequence

- Fidelity: no unsupported addition; no dropped material claim; no changed
  number, date, unit, name, or term; no altered citation scope; no stronger
  causal language; no lost condition or exception; no changed requirement
  level.
- Logic: each conclusion follows from what precedes it; transitions name
  real relationships; comparisons share a basis; pronouns have clear
  referents; alternatives are real; recommendations separate evidence from
  judgment.
- Structure: each section has a function; order follows reader need;
  headings are useful; repetition is intentional; lists exist because
  scanning helps; important ideas get proportionate space.
- Voice: register matches audience and genre; a supplied sample is
  recognizable without caricature; no random personality was introduced;
  terminology is stable.
- Naturalness: read as a reader, not as a pattern detector. Fix only
  defects that matter. For prose read linearly, simulate a read-aloud pass
  for breathless clause stacks and punctuation that hides the relation
  between clauses.

**The adversarial pass** (Level 2 and 3). Ask: which sentence sounds more
certain than the evidence; which paragraph exists because a template
expected it; which abstract noun hides an actor; which sentence repeats the
one before; which contrast argues with nobody; which transition would
vanish under a better order; which list was forced into a pattern; which
heading promises more than its section delivers; which recommendation hides
a tradeoff; which citation now supports more than it did; which
qualification was lost; which line was written to impress; and which line
is being edited only because it "sounds AI" rather than because it is weak.
The last question prevents overcorrection: revert those edits.

## Output modes

- **File mode** (the default in this system). The text lives in a file
  under version control. Run the passes and write only the finished text
  back. Change prose only; keep code, metadata, commands, paths,
  identifiers, link targets, citations, table data, and anchored heading
  text unchanged. Keep process commentary outside the file; report in one
  short paragraph what changed.
- **Embedded mode.** Another protocol or skill uses this one as its prose
  layer (a pull-request description, a commit message, the delivery
  summary). Return only the finished prose in the structure the caller
  requires. No chat wrapper.
- **Drafting mode.** From notes, sources, or an outline, return the finished
  prose in the requested format without narrating the drafting.
- **Rewrite mode.** For pasted prose, return the complete revised text; keep
  change notes brief and separate.
- **Audit mode.** When asked to review rather than rewrite, report the
  highest-impact issues in order of effect on fidelity, logic, structure,
  audience fit, naturalness, and surface style. Do not list every weak
  phrase.

## Where this skill runs in the system

- `deliver`: the full-form summary and any pull-request description or
  commit message pass through embedded mode before hand-off; the summary's
  quality bar names it.
- `canonize`: the docs-librarian applies file mode to node bodies,
  runbooks, and README prose it writes or refreshes, and runs the tool with
  `--against` before the graph-lint pass.
- `adr-writer` and `spec-author`: the body of a record is prose a person
  reads; file mode applies before the status flips.
- `harvest`: imported prose that will read as the seed's own voice passes
  file mode; the tool runs beside `agnosticism-lint.py` on the changed
  files. The seed's machinery prompts themselves are not humanized; they
  change only through `grill`.

## Reference

- `docs/graph/prose-lint.py` (seed home `tools/prose-lint.py`): findings as
  `path:line: §N|letter strong|weak`, the dash rate per 1,000 words,
  `--strict`, `--sample <file>`, `--against <rev>`, `--changelog-ok`; exit 0
  clean, 1 findings, 2 usage or no file matched. Vocabulary detectors are
  weak by doctrine; a weak cluster (three weak tells in one paragraph)
  fails; strong tells fail on one sighting.
- `docs/graph/method/prose-posture.md`: the doctrine, the genre profiles,
  the diagnostics A to X, the anti-patterns, the decision rules, the stop
  conditions.
- `docs/graph/skills/holistic-editing.md`: a prose rewrite is an
  integration into the whole document, never a patch of flagged phrases.

## Source and license

Adapted from two MIT-licensed skills: the humanizer skill by Siqi Chen
(2025; patterns from Wikipedia's "Signs of AI writing") and the
human-prose doctrine (4.0.0, derived from it). Upstream notices are kept at
`skills/humanizer/LICENSE.upstream`. The adaptation adds the mechanical
fact-preservation check, the plant language facts, the scope and exemptions
of this system, the split between doctrine (`method.prose-posture`) and
procedure (this node), and the wiring into deliver, canonize, and the
writing skills.
