<!-- The owner decisions D1 to D5 of `docs/plans/grill-8.5.0-tester-surfaces.md`, plus the lead's trim. Kept beside the plan, outside its increment directory, which holds only §9 increments. -->

# Owner decisions D1 to D5: what the tester-surfaces round left to the owner

The round that makes a test owed only where it can catch something (ADR-0034) left five things to the owner. The owner answered all five on 2026-11-10; each note keeps its evidence and options and ends in the decision.

## D1. The low-risk band of T9

- **Finding.** OD2 lets one implementer write the test and the code for low-risk logic off trust paths. "Low risk" needs a reading a tool can take; the effort label on each plan increment is the only candidate.
- **Evidence.** `delegation.effort-scale` has five labels: `low`, `medium-low`, `medium`, `medium-hard`, `hard`. "The two lowest" is `low` and `medium-low`, a clean cut. A trust-path, stateful or concurrent increment, or a bug reproduction, keeps a tester whatever its label.
- **Options.** (a) `low` and `medium-low`. (b) add `medium`. (c) `low` alone.
- **Decided.** The owner decided on 2026-11-10 on (a), and that the sentences in `delegation.effort-scale` and `delegation.green-self-test` that require separate RED and GREEN spawns are amended for the two low labels off trust paths. The default is recorded in the node that owns the labels; the owner can move it.

## D2. The link between a test and its contracts

- **Finding.** The spec lint finds a contract's test by the contract's name in test code, which pulls test names toward one test per contract.
- **Options.** (a) keep the name. (b) the §10 `Covers` cell is the link in new-form specs. (c) either satisfies.
- **Decided.** The owner decided on 2026-11-10 on (b), not (c). Legacy-form specs keep the name search. The lint checks that the test each row cites exists.

## D3. The seed's own old-form specs

- **Finding.** The seed's specs are in today's form and keep passing: a contract with no kind is read as `test`.
- **Options.** (a) never convert. (b) convert in a later round. (c) convert now.
- **Decided.** The owner decided on 2026-11-10 on (b). A spec without the `Contract form: kinds` line accepts a `Check:` label on individual contracts and reads the unlabelled ones as `test`; a later round labels single contracts in the seed's old-form specs.

## D4. Languages the worth check reads

- **Finding.** The check reads Python and TypeScript or JavaScript test files. The plant's code index also reads shell invocations, but a shell test's assertions are not something the check can read, so shell tests are reported as not checked along with every other language. (The owner's answer was given against a description that listed the index's three; the build follows the narrower reading above, and the owner can ask for shell.)
- **Options.** (a) those three. (b) add a named language.
- **Decided.** The owner decided on 2026-11-10 on (a). A language is added when a plant needs it and the owner names it.

## D5. The baseline of a grafted plant

- **Finding.** Graft records the tests the worth check flags that day as the plant's baseline; the baseline only shrinks; graft and grow remove nothing.
- **Options.** (a) decide per plant, after seeing its baseline. (b) never clean up. (c) a standing cleanup at the next release.
- **Decided.** The owner decided on 2026-11-10 on (a), and added clean-as-you-touch: when a spec is reopened, the baseline tests that belong to it are listed for the owner's confirmation within that work, and removed only on a confirmation that names them.

## The lead's trim (Phase 1)

- **Finding.** Delivering the rule to the lead in full needed bytes the lead's ratcheted prompt did not have, and the first delivery removed routing examples and condensed two paragraphs of `agents/00-orchestrator.md` to make room.
- **Decided.** The owner decided on 2026-11-10 not to keep the trim: the routing hints and examples are restored, the lead carries a two-line pointer to the rule instead of the rule (the architect slices the plan and sets kinds at specify), and the remaining bytes came from the superseded "Code to write → test-first" example. The eager surface is 67,069 bytes against the base's 67,131.

## D6. A plain re-install and a plant's edits to its host settings (found by F2)

- **Finding.** A plain `install.sh claude-code` (or `opencode`) over a plant that edited `.claude/settings.json` or `opencode.json` backs the file up and replaces it. The plant's keys (permissions, theme) are in the `.bak` file only; the installer prints a generic backup line. Graft keeps the edited file instead, and its `kept-deltas` gate blocks, naming the lines the plant's file is missing.
- **Evidence.** Observed on a plant installed from v8.2.0 with an added `permissions` key, then re-installed from this tree; the investigation report holds the commands and excerpts.
- **Options.** (a) merge: a re-install keeps the plant's keys and adds the seed's. (b) keep the replace-with-backup behaviour and name each dropped key in the installer's output. (c) leave as is.
- **Why it is yours.** (a) changes what a landed mechanism does; (b) changes only what the operator is told. Recommendation: (b) now, (a) as a later round with its own spec.
- **Decided.** The owner decided on 2026-11-11 on (b): a plain re-install keeps replacing a plant-edited `.claude/settings.json` or `opencode.json` with a timestamped backup, and names each key path the plant's file has and the new one lacks, with the backup's path and the note that edited host settings upgrade by graft, which keeps the edited file (SPEC-0001 REINSTALL_NAMES_DROPPED_HOST_SETTINGS_KEYS). Open for a later round: key-level ownership, a merge on re-install that keeps the plant's keys and adds the seed's, with its own spec.

## D7. Experts a plant commissions, on opencode (found by F3)

- **Finding.** A plant's own expert agent is projected into `.opencode/agents/` but is missing from the lead's `subagent` allow list, which names the seed roster only. The list lives in the seed-owned charter, so an edit there is overwritten at the next re-install.
- **Options.** (a) generate the lead's list from the plant's roster at projection time. (b) add a plant-owned extension point (a list the projection appends). (c) leave and document.
- **Why it is yours.** Both (a) and (b) widen what the lead may launch on opencode. Recommendation: (a), since the roster is already the plant's own record of who may work.
- **Decided.** The owner decided on 2026-11-11 on (a), bounded: on opencode the lead's `subagent` allow list is generated from the plant's roster at projection time, and only the lead's list changes. The seed roster stays as the lead's charter names it; each plant agent that passes the agent lint is added, and the installer prints one line naming the added agents; a lint-dirty plant agent is left off with a named warning. `install.sh opencode --check` fails on a list that differs from the roster, with the remedy `--recompose-agents` (SPEC-0001 OPENCODE_LEAD_LAUNCHES_THE_PLANTS_LINT_CLEAN_AGENTS, OPENCODE_CHECK_NAMES_A_STALE_LEAD_LIST).

## D8. An unknown tool name in a plant's agent halts the opencode install (found by F2)

- **Finding.** The opencode transform stops the whole install at one agent whose `tools:` names a tool the seed's permission table lacks. The message names the file but gives no remedy, and the table is not in the plant.
- **Options.** (a) a plant-owned table extension the transform reads. (b) skip that agent with a named warning and install the rest. (c) keep stopping, and make the message say how to fix it.
- **Why it is yours.** (b) installs a roster with a gap; (a) adds a permission surface. Recommendation: (c) now (the safe default: an unknown name never reads as allowed), with the remedy in the message.
- **Decided.** The owner decided on 2026-11-11 on a bounded (b) for plant-authored agents: the unknown tool is denied, the agent and every other agent are installed, a warning names the file and the tool with the remedy (remove it from the charter, or the seed adds it to the table), and `install.sh opencode --check` fails until it is fixed. For a seed charter an unknown tool name still stops the run, and `tests/seed-lint.py` fails on any seed charter that names a tool the table lacks (SPEC-0001 OPENCODE_PLANT_AGENT_UNKNOWN_TOOL_IS_DENIED_AND_NAMED, SEED_CHARTER_TOOLS_ARE_IN_THE_PERMISSION_TABLE).
