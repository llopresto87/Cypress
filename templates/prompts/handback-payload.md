<!--
Template: prompts/handback-payload.md
Used: once per spawn, at the moment a worker returns control to its caller —
delegating or leaf, and on all three endings (complete, blocked-out-of-domain,
failed). Not per tool call. "Turn" is defined in docs/graph/method/delegation-bounds.md
(delegation.turn). This hands control back across the subagent boundary. No
hook the seed installs reads a worker's result, so this block is the only
reliable carrier (docs/graph/method/delegation-briefs.md).
Leaf and delegator endings: see Rules.
Fill the {{PLACEHOLDERS}} and return the body verbatim to the caller.
Discipline: docs/graph/agents/00-orchestrator.md (delegation), kernel §3.6.
-->

# Handback — {{unit of work}}

```
HANDBACK
- status: complete | blocked-out-of-domain | failed
- failure_class: {{only if failed: transient | deterministic | capability |
  ambiguity | systemic | unregistered (protocol.recover)}}
- in_domain_work_done: {{what you did, with paths}}
- out_of_domain_needed: {{work for the caller to route, or "none"}}
- graph_route: {{`--plan` task line; LOAD <ids>; skipped <ids>; widened <id> (<reason>)}}
- expertise_gap: {{each stack element with no expertise.* node + the path showing it, or "none"}}
- recommended_next: {{agent + protocol/step, or "none — session ends here"}}
- gates: {{evidence by kind, "none" where empty: compiled; executed (command,
  pass/fail counts: a green gate is what it ran); statically inspected;
  device-tested; deferred (not run, and why); tests added: cases + runtime delta}}
- tools_built: {{durable tool: name, path, invocation, one per line, or "none"}}
- skills_built: {{repeatable procedure: name + step gist, one per line, or "none"}}
```

## Rules (why this block exists)

- **The payload starts at `status:`.** `brief.py` logged your spawn_id,
  role, routing line and effort when it composed your brief
  (`delegation.tracing`); the host pairs this reply with that spawn, and the
  deliver-time attribution assertion reads that log. Your own graph route
  goes in `graph_route:` as ids.
- **Every field is its shortest sufficient form.** Paths and identifiers,
  not narration — the payload is a routing header the caller re-reads
  each time a worker returns, not a report; findings go in the report body.
- **The report body carries decisions, in a fixed order, and has an
  overflow note.** The order is: the verdict; the blockers and caveats;
  the findings the caller must act on; then this payload. The paths and
  the gate numbers live in `in_domain_work_done` and `gates:` and are not
  repeated in the body unless a gate failed or misbehaved. Point at
  the brief, the diffs and the paths instead of restating them or
  telling the story of how you got there, because the caller holds the
  brief and can open the paths. Aim at a few thousand characters.
  That is a soft target, not a cap: a cap trims exactly the caveats the
  caller needs. When the content does not fit, the rest goes in an
  overflow note at `docs/graph/plans/<unit of work>/overflow/<spawn_id>.md`,
  and the report names it. Write the note as you work, so that a spawn
  that stalls or runs out of context still leaves its findings on disk. The close-out librarian reads every overflow note
  the task produced (`protocol.canonize`), so nothing that lives only
  there is lost to the graph.
- **`gates:` files each claim under the evidence that backs it.** A
  claim no executed check reached sits under statically inspected or
  deferred, so the caller reads a green gate as the commands it ran, not
  as "done".
- **A run or review contract returns its own evidence.** An increment
  whose contracts are proved by a declared run carries that command and its
  result under `gates:` executed; one proved by review carries the
  reviewer's confirmation, or what fails it, in the report body. The brief
  names both under `Evidence this hand-back owes` (`grill.increment-shape`).
- **`gates:` also reports what the spawn added to the suite.** A spawn
  that adds tests states the cases and the runtime it added, as a delta.
  It lets the caller weigh the suite's growth against the contracts it
  covers before the cost compounds across increments.
- **`expertise_gap` follows the stack rule.** What goes in the field,
  and the evidence it cites, is set by "Stack expertise the graph lacks"
  in `docs/graph/templates/prompts/graph-session-bootstrap.md`, the one
  home of the stack rule.
- **`recommended_next` names a spawnable specialist.** When you
  recommend, it points at a specialist the orchestrator can spawn, plus
  the protocol/step, because a protocol name alone is not a routable
  target. On a final turn with nothing left, "none — session ends here"
  is the defined value.
- **A leaf worker recommends.** At an out-of-domain boundary it names the
  specialist in `recommended_next` and returns this payload; the work is the
  specialist's. Leaf agents carry no spawn tool by design: for a registered
  specialist that is one of the harness's two recursion caps, the host's
  nesting limit being the other. Under role emulation the same cap holds by
  brief, and the spawn log's emulation record makes it visible at `deliver`
  (`delegation.harness-registration`).
- **A delegator that stops instead of spawning still fills this in.**
- **`failure_class` feeds `protocol.recover`.** Classify before handing
  back; preserve what survived in `in_domain_work_done` so the next
  attempt starts from the frontier, not zero.
- **`tools_built` and `skills_built` feed the close-out (§3.8).** Name a
  durable, reusable tool (stable interface, covering test, plausibly run
  again in a later session) or a repeatable multi-step *procedure* a
  future session will walk again (a migration recipe, a release
  choreography), so the orchestrator forwards it in the single canonize
  close-out brief: the tool is cataloged, and the procedure is
  crystallized into a project skill (home `docs/graph/skills/<name>.md`,
  projected into the harness dirs in use). A throwaway prototype or a
  genuine one-off is `none`; a reusable one left out is a silent
  capability leak.
