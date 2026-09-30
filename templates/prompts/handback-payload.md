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
- produced_by: {{this agent name}}
- spawn_id: {{echoed verbatim from the brief — the caller-minted
             dot-chain, e.g. orchestrator.3.architect.1; see
             docs/graph/method/delegation-bounds.md, delegation.tracing}}
- status: complete | blocked-out-of-domain | failed
- failure_class: {{only when failed: transient | deterministic | capability |
                   ambiguity | systemic | unregistered — see
                   docs/graph/protocols/recover.md; what survives goes in
                   in_domain_work_done}}
- in_domain_work_done: {{what this agent legitimately did, with paths}}
- out_of_domain_needed: {{work outside this agent's domain, for the caller
                          to route, or "none"}}
- route_evidence: {{the agent-lint --route line that selected this agent,
                    or the caller's recorded override rationale — echoed
                    from the brief}}
- effort: {{echoed from the brief: <low|medium|high> (row <n>: <reason>),
            plus "host applies: definition default <value>" where it differs}}
- expertise_gap: {{each stack element met mid-work with no expertise.* node,
                   with the path that shows it, one per line, or "none"}}
- harness_override: {{only when this worker is a role emulation of a
                      specialist the host had no registered type for:
                      "role-emulated (<reason>)" — see
                      docs/graph/method/delegation-bounds.md,
                      delegation.harness-registration}}
- recommended_next: {{agent name}} + {{protocol/step}}, or "none — session
                    ends here"
- next_route_evidence: {{only when recommending: the agent-lint --route line
                         that supports recommended_next, or "not run"}}
- gates: {{commands run + results, or "none"; when this spawn added
          tests, also the test cases and the runtime it added, as a
          delta, not the suite's total}}
- tools_built: {{durable reusable tools this task produced — name + path +
                 invocation, one per line — or "none"}}
- skills_built: {{repeatable multi-step procedures this task followed that a
                  future session will likely walk again — name + step gist, one
                  per line — or "none"}}
```

## Rules (why this block exists)

- **`route_evidence` is about you, `next_route_evidence` about the next
  hop.** `route_evidence` echoes the routing line from your brief that
  selected you — the deliver-time attribution assertion reads it beside
  `produced_by` to confirm the right specialist did the work. This field
  holds only your own routing line: the next hop's goes in
  `next_route_evidence`, and graph-lint `--plan` output (graph-route
  evidence) goes in your report body.
- **`produced_by` is load-bearing.** A unit of work with no `produced_by`
  is a deliver-time BLOCK, not a pass (fail-closed).
- **Every field is its shortest sufficient form.** Paths and identifiers,
  not narration — the payload is a routing header the caller re-reads
  each time a worker returns, not a report; findings go in the report body.
- **The report body carries decisions, in a fixed order, and has an
  overflow note.** The order is: the verdict; the paths delivered; the
  gates, with their numbers; the blockers; then this payload. Point at
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
- **`gates:` also reports what the spawn added to the suite.** A spawn
  that adds tests states the cases and the runtime it added, as a delta.
  It lets the caller weigh the suite's growth against the contracts it
  covers before the cost compounds across increments.
- **`effort` is echoed, not chosen.** Copy the effort label, row and
  reason from your brief. When the host cannot apply a per-spawn setting
  and runs your definition's default instead, add "host applies:
  definition default <value>", so the caller sees what really ran
  (`delegation.effort`, `docs/graph/method/delegation-model-classes.md`).
- **`expertise_gap` follows the stack rule.** What goes in the field,
  and the evidence it cites, is set by "Stack expertise found mid-work"
  in `docs/graph/templates/prompts/graph-session-bootstrap.md`, the one
  home of the stack rule.
- **`recommended_next` names a spawnable specialist.** When you
  recommend, it points at a specialist the orchestrator can spawn, plus
  the protocol/step, because a protocol name alone is not a routable
  target. On a final turn with nothing left, "none — session ends here"
  is the defined value.
- **A leaf worker ONLY recommends.** At an out-of-domain boundary it
  names the specialist in `recommended_next` and returns this payload;
  the work is the specialist's. Leaf agents carry no spawn tool by
  design: for a registered specialist that is one of the harness's two
  recursion caps, the host's nesting limit being the other. Under role
  emulation the same cap holds by brief instead of by frontmatter, and
  `harness_override` is what makes that visible at `deliver`.
- **A delegator that stops instead of spawning still fills this in.**
  The caller needs the same attribution either way.
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
