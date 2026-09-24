# Reader test: the baseline run (AC-18)

The "before" run of SPEC-0004 AC-18, the detective reader test for the front
door. It records what the "after" run must repeat and what it is compared
against. It is evidence, never a gate. Plan: [grill-7.29.0-front-door](../grill-7.29.0-front-door.md).

- **Date:** 2026-09-24
- **Seed revision:** `ee4cd95` (7.28.0)
- **Figure:** FAIL against the pass criterion. The median reader answered 1
  of 7 questions fully correct. Six errors were traced to the README itself.

## Method

**What the readers saw.** The first screen of `README.md` at `ee4cd95`: lines
1 to 413, from the first line up to the sixth `## ` heading. Readers opened no
linked file.

**Readers.** Three fresh model sessions, each with no prior context: two
mid-tier (Sonnet class) and one small-tier (Haiku class). AC-18 requires the
same mix for the "after" run. The exact wording of the reader prompt, beyond
the seven questions, is not recorded. Each reader also named the hardest part
to understand; that answer was not graded.

**The seven questions.**

1. What does this project do?
2. Who is it for?
3. What files does installing it add to my repository?
4. What does it cost per session, and how confident is that number?
5. Which rules are enforced by the tool, and which are requests to the model?
6. What is an "agent" here, and how does it differ from a "skill"?
7. Would I need to learn new vocabulary to try it?

**The answer key.** A tester wrote it from the implementation, not from the
README, before reading any response. Where README and implementation
disagreed, the implementation won. Each question has a list of MUST points and
a list of disqualifying errors (below). AC-18 requires the key to be
re-checked against the implementation at the post-rewrite revision before the
"after" run. Points 1 and 3 of Q4 name the figures the README printed at
`ee4cd95` and are the likeliest to need that re-check.

**Scoring.** C (correct): every MUST point present and no disqualifier. P
(partial): at least half the MUST points, rounded up, and no disqualifier. W
(wrong): fewer, or any disqualifier. An "I can't tell" counts as absent and
never as a disqualifier. A point counts when its substance is present in any
wording. A hedged claim counts as present if true, and as a disqualifier if it
matches one. Each answer is graded on its own text, with no credit carried
across answers. A correct answer lifted from the screen scores full marks,
since the test measures what the screen conveys.

**Grader.** A reviewer who did not write the README and did not write the key.

**Pass criterion.** The median session, by count of fully correct answers,
is correct on all seven, and no README-caused error appears in the grades.

## The key's MUST points and disqualifiers

**Q1** (4). It installs files into an existing repository for an AI coding
agent and is not a library, SDK or service. It gives the agent a method (any
one of spec-first or test-first, risk tiers, specialist delegation). It builds
a knowledge graph of the project in `docs/graph/` to limit what the agent
loads. Installing only places files, and building the graph is a separate
agent-driven step. *Disqualifiers:* calls it a runtime framework, SDK, hosted
service or model; says the installer analyzes code or builds the graph; says
it modifies application source.

**Q2** (3). Users of AI coding agents working in a repository. Names at least
one supported harness correctly; a deprecated harness counts only if marked
deprecated. Not tied to one language or stack. *Disqualifiers:* for end users
or non-programmers; requires a specific language, framework or cloud; calls a
deprecated harness first-class.

**Q3** (4). The kernel instruction file at the top of the repository (`CLAUDE.md` or
`AGENTS.md`). The harness directory (`.claude/` for Claude Code), with any two
of agents, skills, commands, hooks or settings. `docs/graph/`. A file that
differs is replaced with a timestamped backup beside it, not merged and not
skipped. *Disqualifiers:* merges into or appends to an existing kernel file;
skips existing files; overwrites with no backup; modifies source or adds CI;
installs a package.

**Q4** (4). The always-loaded figure for Claude Code, within 5% in either unit.
That figure covers only up-front context, and on-demand nodes, subagents and
growth cost extra. The overhead figure rests on a single measurement. No money
figure is given. *Disqualifiers:* states a money cost; presents the overhead as
a general or averaged benchmark; calls the always-loaded figure the total cost;
says it is free.

**Q5** (4). Uses the classes of ADR-0003. At least one genuinely hard control
named correctly: the per-agent tool allowlist (only some agents can spawn) or
the pre-tool Bash guard. The process rules (any two of tiers, spec-first,
test-first, routing) are requests to the model. Linters refuse only when run,
and the install wires no CI or commit gate. The `produced_by` check is
detective and not automated; saying instead that the routing hook injects
guidance but cannot block counts the same. *Disqualifiers:* tiers, test-first
or spec-first enforced by the tool; depth caps enforced at run time; the
routing hook blocks prompts; nothing enforced at all.

**Q6** (3). An agent is a separately spawned subagent with its own context and
role. A skill is instructions loaded into the current agent's context, not a
worker. One mechanical difference: the agent's own tool allowlist, model or
spawn rights, or the two install directories. *Disqualifiers:* agents as
background processes or daemons; a skill as code, a tool or a model; the two
equated or reversed; agents as separate AI products.

**Q7** (3). Running the try-it commands needs no new vocabulary.
Understanding the README or the method does. Names at least three coined
terms from the first screen. *Disqualifiers:* vocabulary must be learned before
installing or trying; lists only standard terms as coined; invents a term the
screen does not use.

## Result

| Q | R1 (Sonnet) | R2 (Sonnet) | R3 (Haiku) | Median |
|---|---|---|---|---|
| Q1 | P | P | P | P |
| Q2 | C | P | W | P |
| Q3 | P | P | W | P |
| Q4 | P | P | W | P |
| Q5 | P | P | W | P |
| Q6 | P | P | W | P |
| Q7 | W | C | W | W |

| Reader | Correct | Partial | Wrong |
|---|---|---|---|
| R1 | 1 | 5 | 1 |
| R2 | 2 | 5 | 0 |
| R3 | 0 | 1 | 6 |

No reader answered all seven correctly, and no per-question median is C.

## The six README-caused errors

The "after" run passes only if none of these recurs. Line numbers are README
lines at `ee4cd95`.

1. The always-loaded figure called "measured" (all three readers, Q4). Line
   46 said "measured rather than estimated"; the figure is computed from
   source by the seed's gate, a model and a lower bound.
2. A four-digit kernel figure that disagreed with the gated one (one reader,
   Q4; not penalized). Lines 51 and 342.
3. The kernel budget read as a control in the adopter's repository (two
   readers). Lines 51 and 81 to 83; only the seed's own gate enforces it.
4. The seed's source tree read as what install adds (all three, Q3). The
   `## What you get` heading at line 67, then seed-repository paths at lines
   75, 84, 114 and 155. The screen never named the top-level kernel files or
   `.claude/`.
5. Graph invariants read as mechanically enforced (one reader, Q5). Line 231;
   they are soft, since a linter refuses only when run.
6. The overhead read as a "10 to 20%" range (all three, Q4; not penalized).
   Line 53; the record behind it is one run of 11%.

Not README-caused: Q1 point 4 and Q7 point 1 were stated on the screen (lines
40 to 44 and 65), so those misses are the readers' own.

## Grading ambiguities, resolved conservatively

None changes a median or the verdict.

- Q7: a flat "yes" was read as the disqualifier. Reading it otherwise moves R1
  and R3 from W to P.
- Q3 point 1: the kernel's seed path was not accepted for its installed
  location. Accepting it moves R3 to P.
- Q5 point 2: generic wording that names no process rule counted as absent.
- Q2 point 2 and Q6 point 1: no credit carried from another answer.
  Carrying it moves R2's Q2 to C.
