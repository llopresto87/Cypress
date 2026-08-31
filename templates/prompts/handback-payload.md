<!--
Template: prompts/handback-payload.md
Used: ONCE per spawn, at the moment a worker returns control to its caller —
delegating or leaf, and on all three endings (complete, blocked-out-of-domain,
failed). Not per tool call. "Turn" is defined in docs/graph/method/delegation.md
(delegation.turn). This hands control back across the subagent boundary — where hooks do not reach, so
this block is the only reliable carrier.
A LEAF worker (no Task tool) that hits an out-of-domain boundary returns
this instead of doing the work itself: it names the specialist, it does
not spawn one. A DELEGATOR returns it when it STOPs rather than spawning.
Fill the {{PLACEHOLDERS}} and return the body verbatim to the caller.
Discipline: .agents/00-orchestrator.md (delegation), kernel §3.6.
-->

# Handback — {{unit of work}}

```
HANDBACK
- produced_by: {{this agent name}}
- status: complete | blocked-out-of-domain | failed
- failure_class: {{only when failed: transient | deterministic | capability |
                   ambiguity | systemic | unregistered — see
                   docs/graph/protocols/recover.md; what survives goes in
                   in_domain_work_done}}
- in_domain_work_done: {{what this agent legitimately did, with paths}}
- out_of_domain_needed: {{work this agent must NOT do itself, or "none"}}
- route_evidence: {{the agent-lint --route line that selected THIS agent,
                    or the caller's recorded override rationale — echoed
                    from the brief}}
- harness_override: {{omit unless this worker is a ROLE EMULATION of a
                      specialist the host had no registered type for:
                      "role-emulated (<reason>)" — see
                      docs/graph/method/delegation.md,
                      delegation.harness-registration}}
- recommended_next: {{agent name}} + {{protocol/step}}, or "none — session
                    ends here"
- next_route_evidence: {{only when recommending: the agent-lint --route line
                         that supports recommended_next, or "not run"}}
- gates: {{commands run + results, or "none"}}
- tools_built: {{durable reusable tools this task produced — name + path +
                 invocation, one per line — or "none"}}
- skills_built: {{repeatable multi-step procedures this task followed that a
                  future session will likely walk again — name + step gist, one
                  per line — or "none"}}
```

## Rules (why this block exists)

- **`route_evidence` is about YOU, `next_route_evidence` about the next
  hop.** `route_evidence` echoes the routing line from your brief that
  selected you — the deliver-time attribution assertion reads it beside
  `produced_by` to confirm the right specialist did the work. Never put
  the next agent's routing (or graph-lint `--plan` output — that is
  graph-route evidence and belongs in your report body) in this field.
- **`produced_by` is load-bearing.** A unit of work with no `produced_by`
  is a deliver-time BLOCK, not a pass (fail-closed).
- **Every field is its shortest sufficient form.** Paths and identifiers,
  not narration — the payload is a routing header the caller re-reads
  each time a worker returns, not a report; findings go in the report body.
- **Name an addressable agent, never only a protocol.** When you
  recommend, `recommended_next` points at a specialist the orchestrator
  can spawn, plus the protocol/step. A protocol name alone is not a
  routable target. On a final turn with nothing left, "none — session
  ends here" is the defined value.
- **A leaf worker recommends; it does not spawn.** Leaf agents carry no
  `Task` tool by design (the recursion cap the harness enforces for a
  registered specialist). At an out-of-domain boundary you STOP and
  return this payload — you do not do the work. Under role emulation the
  same cap holds by brief instead of by frontmatter, and
  `harness_override` is what makes that visible at `deliver`.
- **A delegator that stops still fills this in.** The caller needs the
  same attribution either way.
- **`failure_class` feeds `recover` (§ the failure discipline).** Classify
  before handing back; preserve what survived in `in_domain_work_done` so
  the next attempt starts from the frontier, not zero.
- **`tools_built` feeds the close-out (§3.8).** A durable, reusable tool —
  stable interface, covering test, plausibly run again in a later
  session — is named here so the orchestrator forwards it in the single
  canonize close-out brief. A throwaway prototype or genuine one-off is
  `none`. Leaving a reusable tool out is a silent capability leak.
- **`skills_built` feeds the same close-out (§3.8) — the procedure sibling.**
  A repeatable multi-step *procedure* a future session will walk again (a
  migration recipe, a release choreography) is named here so the close-out
  crystallizes it into a project skill (`.claude/skills/`). A one-off sequence
  is `none`. Leaving a recurring procedure out is a silent capability leak,
  exactly as an uncatalogued tool is.
