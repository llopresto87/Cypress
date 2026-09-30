# Incident response

The first things to do when something is wrong in production, in order.

## First checks (the first five things)

1. `<dashboard / signal to look at first>`
2. `<the health surface / smoke command>`
3. `<recent deploys or config changes>`
4. `<the dependency most likely implicated>`
5. `<the queue / broker / dead-letter state>`

## Who / where

- On-call / owner: `<who>`
- Dashboards: `<links>`
- Escalation path: `<who, when>`

## What shapes an incident here

The loop below is generic; these facts decide how it is actually run
here. Record each, or mark it `not recorded`, so every fact the loop
depends on is explicit.

- What tells you an incident has started: the signal, or its absence.
  Where nothing alerts, the first step of the loop is a person noticing,
  and the clock starts late by an unknown amount.
- How long the evidence lives: the retention window of the logs,
  metrics and traces the loop asks you to preserve. A short window makes
  "capture before you contain" an ordering constraint rather than good
  practice.
- Which containment actions also destroy evidence. Where a restart, a
  redeploy or a rebuild clears the record that explains the fault,
  capture is a precondition of containment and not a parallel task.
  Name them here.
- What the failure domains actually are. Where one component sits
  underneath several unrelated failure paths, or where containing one
  unit and containing everything are the same act, the smallest
  reversible containment is larger than it looks and the loop must say
  so.
- Who may authorize the destructive path, and how they are reached, with
  the reaching itself recorded: an escalation path nobody has walked is
  an assumption.
- Which failures of the build and deploy machinery look like failures of
  the thing being built. A runner that fills its disk or loses its
  connection mid-job presents as a failed build; name the log line that
  tells the two apart. Say too whether a run's overall status aggregates
  jobs that do not matter equally. Where it does, read the per-stage
  result before concluding that a deploy did or did not happen.

Keep this section to what changes the loop's execution.

## The loop

1. **Contain and keep the evidence.** Stop the unsafe process and leave in
   place the state that explains what happened.
2. **Capture identifiers, not secrets.** Record environment, build/artifact
   ref, and correlation ids; credentials and sensitive fields stay out of the
   record.
3. **Classify the boundary** the failure crosses (which service, which trust
   boundary, which data class).
4. **Preserve sanitized evidence** — logs with redaction, queue/dead-letter
   snapshot.
5. **Contain with the smallest reversible action** (see `rollback.md` — fix-
   forward first; reversal is human-gated; destructive is a separate gate).
6. **Verify recovery against the owning gate** (`verification.md` / the smoke
   suite) — not by eyeballing.
7. **Close the loop:** file the follow-up as a spec/`grill.md` §12 item, add a
   regression test and (if a gate would have caught it) a new gate via
   `verify`, and record the durable prevention rule via `canonize`; the
   narrative stays in Records below.

## Records

### Incident <date> — <one-line title>
- Impact: `<who/what was affected>`
- Root cause / boundary: `<...>`
- Contained by: `<action>` — Recovery verified by: `<gate>`
- Follow-up: `<spec/grill row + regression test + gate added>`

<!-- Append per incident. The follow-up items are the point, not the story. -->
