<!-- The owner decisions D1 to D7 of `docs/plans/grill-8.3.2-review-fixes.md`; its §12 row 1 points here. Kept beside the plan, outside its increment directory, which holds only §9 increments. -->

# Owner decisions D1 to D7: findings of the independent review that change a default

The independent review that produced round 8.3.2 found seven things this round does not land: each changes a default the owner set, or needs evidence the round could not produce. Each note gives the finding, the evidence and how it is classed (verified in this round, or reported by the review and carried as reported), the options with their costs, and what would be verified. Nothing here is implemented, no default changed, and no option is adopted by being written down.

## D1. The bound hook: a guard to extend, or a nudge that advises

- **Finding.** `bound-hook.py` refuses (exit 2) a command from a fixed table (`BLOCKING_PRONE`): service control, process signalling, package managers, installers, builds, log followers. This round closes spelling gaps within that table (R7). Whole classes outside it still pass: other build tools, development servers, container start-up, watchers.
- **Evidence.** Verified: the table's rows and the classes it lacks, by reading `integrations/claude-code/bound-hook.py`. Not verified: how often a session hangs on a class outside the table, because no record of such hangs was available.
- **Options.** (a) Keep the table as a guard and extend it by class when a hang is recorded. Cost: each class adds false-positive risk on commands that are fine, and the table grows by hand. (b) Turn the hook into a nudge: print the two accepted forms on stderr and exit 0. Cost: nothing is refused, so the property "no unbounded foreground command" rests on the model's compliance, and `toolcraft.bounded-execution` is then advice. (c) Keep the guard exactly as it is and measure first.
- **To verify.** Count, over real transcripts, the commands that hung outside the table and the commands the guard refused that were in fact short. Decide the class list from the first count and the false-positive budget from the second.

## D2. The interpreter floor stays at 3.14, or drops

- **Finding.** The owner decided on 2026-10-14 to keep the floor at 3.14 (`PYTHON_FLOOR` in `install.sh`). The review reports that at the commits it reviewed every shipped Python file parsed, and the tools it exercised ran, under 3.12.
- **Evidence.** Reported by the review, not re-run in this round. This round ran its gate on the floor interpreter only.
- **Options.** (a) Keep 3.14: one tested interpreter, and a plant on an older system installs a newer one. Cost: the install fails closed on a machine whose newest Python is 3.12 or 3.13. (b) Lower the floor to the oldest version the whole gate passes on. Cost: every syntax and library feature the code uses must be held to that version by a gate step, or the floor drifts back up unnoticed; the seed has no such step today. (c) Keep 3.14 for the gate and lower it for the placed tools only.
- **To verify.** Run `bash tests/run.sh` under each candidate version, and list the standard-library calls and syntax newer than it. The owner's 2026-10-14 decision stands until then.

## D3. The knowledge rule: trust a graph fact, or open its cited source first

- **Finding.** Kernel §3.2 treats a fact the graph states as settled. The proposal is to keep that and add: before acting on a load-bearing fact, open its cited source.
- **Evidence.** Verified: the rule and its home (`skills/context-router.md`, `rule.knowledge`) and that the code anchor already compares recorded code against the working tree once per session (`code-anchor.py --compare`), which covers facts about the plant's own code and no other class. Not measured: how often a stale graph fact led a session wrong.
- **Options.** (a) Keep the rule as it is. (b) Add the check for facts marked load-bearing. Cost: a source read per such fact in every session, paid against the economy the rule was written for, and a definition of "load-bearing" that someone must keep. (c) Add it only for facts that carry a `source:` older than the last code-anchor move, which a tool can decide.
- **To verify.** Take a sample of graph facts with citations and count how many no longer match their source; if the stale share is small, (a) stands, and if it is not, (c) costs less than (b).

## D4. Token estimates: calibrate `est_tokens` with a tokenizer, or keep the word count

- **Finding.** `est_tokens` is the node's word count times 1.35 (`TOKENS_PER_WORD` in `templates/knowledge-graph/graph-lint.py`; `tests/seed-lint.py` recomputes it), checked within a twofold tolerance. The review reports that it ran below bytes divided by four on the large nodes.
- **Evidence.** Verified: the constant and the tolerance in the two files above. Reported by the review: the comparison against bytes divided by four. No tokenizer was available, so neither figure is known to be right.
- **Options.** (a) Keep the estimate: it is only a router budget, and a twofold tolerance absorbs a model change. (b) Calibrate the constant against a real tokenizer once and record the date and the tokenizer in the lint. Cost: a constant that goes stale with each model family. (c) Use the host's reported usage (the token ledger of 8.3.1 records it per spawn) to calibrate per host.
- **To verify.** Run a tokenizer over the twenty largest nodes and compare with both estimates. If the word-count estimate is more than twofold off on any, change the constant; otherwise stop.

## D5. Copied code held by lint: keep the copies, or make each one module loaded by path

- **Finding.** Three pieces of code exist as byte-identical copies that a lint holds equal: the stemmer block, `source_paths.py` (in `tools/` and in `templates/knowledge-graph/`) and the frontmatter reader. The review proposes one module each, loaded by path.
- **Evidence.** Verified: `source_paths.py` has two copies held by `check_source_paths_is_one_module`, and this round had to edit both for R4. The same happens for the frontmatter reader (`check_frontmatter_reader_is_one_reader`). The stemmer block was not inspected.
- **Options.** (a) Keep the copies: a plant receives each file whole, and a lint catches drift. Cost: every edit is made twice, and a forgotten copy fails the gate, not a session. (b) One module, loaded by path from its one home: sibling tools in a plant already load their helpers this way (`source_paths.py` is loaded by path in `graph-lint.py`). Cost: the installer must place the module wherever a tool loads it from, a write site per placement (`check_install_write_sites`), and a tool run outside a plant loses its helper.
- **To verify.** List where each copy is loaded from and whether the same directory always holds both the tool and the helper; if so, (b) removes the copies at the price of one placement each.

## D6. Undated corpus pages

- **Finding.** Most library-corpus pages carry no date, so a reader cannot tell how old the transcribed knowledge is.
- **Evidence.** Verified for the library corpus: none of 158 pages has a frontmatter key named `retrieved`, `date`, `last_verified`, `as_of`, `updated` or `fetched` (a heuristic over those names, not over the schema). The legal and tool corpora were not counted.
- **Options.** (a) Leave undated; the corpus is transcribed knowledge and its contract is `_schema.md`. (b) Add a required date key to the schema and a lint that fails a page without one. Cost: a backfill of every page with a date nobody knows, which would invent dates; a backfill with the commit date records when it was written, not when the source was read. (c) Require the date on new and edited pages only.
- **To verify.** Read `library-corpus/_schema.md` for the key it already defines, then count pages that carry it in the body or elsewhere before choosing.

## D7. Evidence for 8.3.0's figures

- **Finding.** The 8.3.0 changelog entry reports measurements taken from audited trajectories. The trajectories, the replay scripts and the grading rubric are not in the repository.
- **Evidence.** Verified: the entry reports the figures (`CHANGELOG.md`, the 8.3.0 entry) and the repository holds no file for those records. Not verified: whether the figures are right.
- **Options.** (a) Leave the entry as written: the changelog is append-only and says what the owner saw. (b) Commit the trajectories, scripts and rubric, with the redaction `ADR-0011` and `ADR-0031` require for any token that names a donor project. Cost: review of every file before it enters the history, and a large addition. (c) Add an evidence-record file for the figures, in the shape of `method-overhead-evidence.md`, stating what exists, where, and what was not kept. Cost: small, and it records the gap without closing it.
- **To verify.** Ask where the records live and whether they may be published; the answer decides between (b) and (c).
