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

- **Finding.** The check reads what the plant's code index reads: Python, shell invocations, and TypeScript or JavaScript. Every other file is reported as not checked.
- **Options.** (a) those three. (b) add a named language.
- **Decided.** The owner decided on 2026-11-10 on (a). A language is added when a plant needs it and the owner names it.

## D5. The baseline of a grafted plant

- **Finding.** Graft records the tests the worth check flags that day as the plant's baseline; the baseline only shrinks; graft and grow remove nothing.
- **Options.** (a) decide per plant, after seeing its baseline. (b) never clean up. (c) a standing cleanup at the next release.
- **Decided.** The owner decided on 2026-11-10 on (a), and added clean-as-you-touch: when a spec is reopened, the baseline tests that belong to it are listed for the owner's confirmation within that work, and removed only on a confirmation that names them.

## The lead's trim (Phase 1)

- **Finding.** Delivering the rule to the lead in full needed bytes the lead's ratcheted prompt did not have, and the first delivery removed routing examples and condensed two paragraphs of `agents/00-orchestrator.md` to make room.
- **Decided.** The owner decided on 2026-11-10 not to keep the trim: the routing hints and examples are restored, the lead carries a two-line pointer to the rule instead of the rule (the architect slices the plan and sets kinds at specify), and the remaining bytes came from the superseded "Code to write → test-first" example. The eager surface is 67,071 bytes against the base's 67,131.
