## 7.29.0 — a harvest: the front door in reader order, and host facts corrected (2026-09-24)

A grown plant was harvested back into the seed. What follows is the generalized
residue: no plant identity, no stack, no counts belonging to any project.

**README is rewritten in the order a newcomer reads it.** It answers what the
seed is, who it is for, what installing writes, what it costs and how to try
it, all on the first screen, and then how it works, why, what it does not do
and where to go next. The agent, skill and protocol catalogs, the tier prose
and the release narration moved out by link. Two README anchors were removed
with their sections, `#what-you-get` and `#try-it-and-what-it-costs`; a link
from outside the repository to either now lands at the top of the page. The
first-screen ceilings were re-measured and lowered: `FIRST_SCREEN_MAX_LINES`
from 100 to 53, and `FIRST_COMMAND_LINE` from 80 to 46.

**The manual gains a glossary and a table of what each control holds.**
`DOCUMENTATION.md` §15 defines each project term once, with its everyday
sense, and every other page links it on first use. §17 gives each mechanism
one row: what holds it, its ADR-0003 class, and what it misses. README's
limits section and the integration READMEs link those rows instead of
asserting enforcement in their own words. The three references open with
their definitions. Body-size and always-loaded figures have one home each and
are computed, not typed; a line that names one harness must now print that
harness's figure, not any live one.

**`tests/seed-lint.py` holds the front door.** SPEC-0004's 22 contracts are
checks over README, the manual, the references, `INSTALL.md` and the
integration READMEs, with a pending ledger that a release version refuses
unless it is empty. The prose floor runs once per file, and
`tools/gate-registry.py --lint` refuses a prose step that passes two files, or
any `--file=`, `--root` or `--glob` argument.

**Host facts corrected.** Hooks configured in settings run inside a subagent on
Claude Code: its tool calls fire the same `PreToolUse` and `PostToolUse` hooks,
so the seed's pre-Bash guard fires on a worker's Bash calls. What still holds
is narrower: no hook the seed installs carries the graph discipline or the
routing context into a worker's turn, or reads a worker's result, so the brief
and the handback block remain their only carriers, and the templates now say
exactly that. The spawn tool is named `Agent`, with `Task` its accepted alias;
`agent-lint.py` and `seed-lint.py` read either name, bare or parenthesized,
through one predicate, and refuse an agent file with no `tools:` line, which on
the host inherits every tool. The host's own nesting limit is recorded as a
harness-held ceiling separate from the seed's soft `max_spawn_depth`, and a
file written into an agents directory mid-session is picked up without a
restart except in the cases the delegation node names. A new check refuses
"hooks do not reach subagents" in shipped and front-door files. ADR-0003 gains
a dated amendment; its body is unchanged. The shipped agents keep `Task`.

**Disclosed redaction of append-only records.** Two records were edited under
the exception in `CLAUDE.md` Conventions (ADR-0011, proposed):
`docs/specs/SPEC-0003-per-prompt-injection.md` and
`docs/plans/grill-7.28.0-context-residency.md`. The class of token removed is
the node ids of the project the seed was harvested from; each span became
`[redacted]` and no sentence was reworded. The original text remains at tag
v7.28.0 and in git history. History was not rewritten, and published tags and
Releases keep it. This file was not redacted.

**The installer was unusable on macOS's own bash.** `install.sh` failed to
parse at all under bash 3.2 — the system `bash` on every default macOS
install — because `fill_plant_facts` captured a python heredoc's output
through a `$(...)` wrapper, and bash 3.2 misreads a heredoc nested inside a
command substitution once another heredoc follows later in the same script;
`install_github_copilot`'s three loops do. The failure surfaced as a plain
`syntax error near unexpected token '('` pointing at a line of Python regex,
for every adapter, before a single file was written — reproduced under bash
3.2.25 and 3.2.57. The heredoc now writes to a staged log file instead of
through `$(...)`; `tests/seed-lint.py`'s SINGLE_WRITER check gained the one
new write site the change added. A second, unrelated bug the same gate run
surfaced — `test-install-adoption.sh`'s `case_check_broken` passed an
indented first line to `python3 -c`, which Python itself refuses regardless
of host — is fixed alongside it.

```
# Harvest — from a grown plant — 2026-09-24
Harvested:   a front-door rewrite (README order, a glossary, an enforcement
             table, reference openers, one home per figure) with its checks;
             a per-file prose floor; a disclosed legacy-token cleanup; host
             facts corrected in method nodes, templates and both lints — no
             plant identity.
Generalized: every plant name, path, host, user, node id and identifying count
             stripped; the forbid list was derived outside the seed and never
             committed.
Rejected:    plant-local evidence ledgers, survey and triage records, and the
             ratification proposal (they stay outside the seed).

### Seed integrity gate (verdicts only)
- G1 agnosticism-floor: PASS
- G2 agnosticism-judgment: PENDING (steward, at ratification)
- G3 faithful-import: PASS
- G4 availability: PASS
- G5 plant-untouched: PENDING (steward, at ratification)
- G6 self-consistency: PASS
- G7 clean-install: PASS
- G8 prose: PASS
- G9 minimum-sufficient: PENDING (steward, at ratification)
- G10 provenance: PASS
- G11 no-loosened-limit: PASS
- Version bump: 7.28.0 → 7.29.0
```
