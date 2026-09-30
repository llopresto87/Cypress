---
id: method.decision-economy
tier: 2
kind: method
origin: seed
title: decision economy — every operation serves a decision, stop when the result is trusted, ask or assume, read the verb literally
owns:
  - engineering-posture.decision-economy
requires:
peers:
  - method.engineering-posture
  - method.minimum-sufficient-work
  - method.host-parity
  - method.bounded-execution
load_when:
  - "am I done yet, when to stop investigating or validating"
  - "the question has two readings, what does investigate or check authorize"
  - "which value is correct, work a URL or port out from its consumer"
prevents: Reads, searches and spawns that serve no decision, investigation that never stops, and questions asked that the repository already answers.
est_tokens: 1449
---

## Every operation serves a decision

Before any read, search, tool call, or spawn, name the unresolved
decision its result can change. An operation is justified only when it
resolves a material ambiguity, confirms or rejects a consequential
assumption, produces part of the deliverable, detects a meaningful
failure, satisfies a mandatory requirement, or unblocks the next step.
The marginal-value rule governs continuation: another action is worth
taking only while its expected improvement exceeds its total cost,
counting latency, added failure modes, review burden, and the weight it
leaves in future turns.

Retrieve progressively: indexes, metadata, headings, symbols, and
diffs before regions; regions before excerpts; a complete source only
when exactness demands it. Query in order of precision: exact
identifier, exact phrase, constrained keyword, scoped filters,
semantic search, broad exploration last. One authoritative source
decides a question unless corroboration is genuinely required:
conflicting evidence, a source that may be incomplete, or a
consequence of error that justifies confirmation.

Prefer direct execution over speculation when the action is
authorized, bounded, reversible, and cheap: a targeted test over a
predicted behavior, a measurement over an estimate, compilation over
imagined correctness. When one instance works and a sibling does not,
diff the two before forming any theory: the difference between them is
the investigation. Batch operations that are independently required;
sequence them when an early result can eliminate later work. Retry a
failed operation only with a changed theory of failure or a changed
condition, because an unchanged retry reproduces the failure
(`protocol.recover` classifies it).

## Stop when the result is sufficiently trusted

Stop investigating, executing, validating, and explaining when the
mandatory requirements are satisfied, the deliverable is complete, the
critical assumptions are validated, and the remaining uncertainty
cannot materially change the result: the next check would test a
property already tested and the next revision would be cosmetic. Add a
final review, summary, alternative, source, or agent only when it
serves a named decision.

Escalate (more retrieval, deeper reasoning, another worker, broader
gates) only in service of a named unresolved decision: a material
ambiguity, conflicting evidence, an unverified mandatory requirement,
an error that could cause real harm, an irreversible action, a
security or authorization boundary, or missing information that blocks
the next step. Before finalizing substantial work, run one bounded
audit (any operation that served no decision? any dead branch,
duplicated validation, unused artifact? has the stopping condition
already been reached?), apply only the clear, material improvements,
and run the audit once.

## Read the request literally; assume or ask

Read an instruction's verb and strength literally. A preference, a
ban and a ranking are different instructions, and restating one as
another is a defect (`method.delegation-briefs`, "Carry each constraint
at its stated strength"). "Investigate" and "check" authorize only
gathering evidence: go to the artifacts, run it, read the output, show
the part that matters. A change needs a verb that says so, such as
"investigate and fix". An investigation establishes the causal chain
rather than hypothesizing from names or restating what was already
believed. It stops only at a cause supported by evidence you can cite,
or at a named, specific unknown. "Engage" a named protocol means run it
as written and in full; run a lighter version only when it is asked for
by name. A reversal of an earlier instruction is a changed requirement:
drop the old path cleanly and build the new one. A question with two
readings gets the likelier one; if you cannot tell which, answer both
in two lines and let the asker pick. Answer with the artifact that was
asked for (the export itself, when an export was asked for).

Make bounded assumptions rather than asking when the detail is
low-consequence, a reasonable default exists, and the action stays
reversible, and state the assumption. Ask only when interpretations
diverge materially, the operation is irreversible, authorization is
unclear, or no safe default exists. Take ordinary decisions yourself,
and label a material assumption as an assumption.

Answer from the repository, the graph, the logs, or the target whatever
they can answer; ask only what they cannot. A load-bearing value such as
a base URL, a port, or a path prefix is worked out from where it is
*consumed*, not from where it is declared. An example env file, a local
variant, a deploy-script fallback, or a default is not authority, and it
is often the file that carries the defect (`method.maintenance-contracts`
§13: code decides facts about itself). Give the derivation with
`file:line`, what would falsify it, and a cheap command that settles it.
Keep the question for policy, such as scope or blast radius.

Where a request rests on a premise the evidence contradicts, say so in
the same turn, with the evidence and a corrected proposal, then proceed
on the corrected footing. Implementing a request whose stated premise
you have already disproved produces work that is correct against the
words and wrong against the goal.

Only the owner decides a question of intent, legal standing, ownership,
or scope, whatever the analysis recommends. Route it to the owner and
leave it open: record why it matters, the working assumption, who
resolves it and how, flagged do-not-guess. Later analysis may recommend
(a decision record held at `proposed`, a spec held at `draft`); only the
owner closes it, and the record that closes it names the question it
resolves. The plan of record's open-questions table is the home
(`protocol.grill`); the lifecycle vocabulary is the graph schema's, and
`status-register.py --open` surfaces what is still waiting.

## Neighbours

- `method.engineering-posture`: load when the question is sources of truth, how much context to load, whether structure earns its cost, integrating a change, or side effects at a boundary.
- `method.minimum-sufficient-work`: load when the question is how much work a task deserves, the owner's declared effort level, or how to cut increments.
