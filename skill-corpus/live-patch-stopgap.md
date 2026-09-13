# Suggested skill: live-patch-stopgap

> Optional procedure — **a template**. Deploying an already-committed,
> already-verified fix straight into a running instance by replacing one
> artifact and reloading the process: no push, no pipeline, no rebuild. A
> stopgap to stop active harm on a fix that has passed everything except the
> pipeline. **High blast radius.** Not a core skill; instantiate into
> `docs/graph/skills/<name>.md` (its home, projected into the harness dirs the
> plant uses) from `templates/skill.template.md` if selected. **Composes**
> `core/method/incident-posture.md` (the status rule) and
> `core/method/vcs-posture.md` (the authorization boundary) **by reference and
> restates neither**. What it adds is the one thing neither owns: the
> mechanics and the honest accounting of a change that exists in exactly one
> running instance.

**Instantiate by supplying:** `<ARTIFACT_TYPE>`, `<RUNTIME_TARGET>`,
`<COPY_MECHANISM>`, `<RELOAD_MECHANISM>` (never a recreate call),
`<VERIFICATION_SIGNATURE>`.

## When to apply

- A fix exists, is committed, and is verified locally, and the pipeline that
  would normally deploy it is unavailable, backed up, or hours away.
- The harm the fix removes is **active** — happening now, to someone.
- The owner has authorized this specific patch, having been told its cost.

Never as a way to skip a pipeline that works. Never to author or first-test a
fix. If the fix is not already proven, this is not the procedure — this
mechanism only ever **deploys** a proven fix.

## Phase 1 — Authorization

**Gate: an explicit, per-invocation owner authorization naming this patch.**

- Per invocation, never standing. A patch authorized last week does not
  authorize this one; "go ahead with the fix" authorized the fix, not this
  deployment of it. `core/method/vcs-posture.md`
  (`vcs-posture.publish-authorization`) owns the boundary — reloading a
  running service sits inside it — and this page does not restate it.
- **An ambiguous instruction is disambiguated with the owner, never
  inferred.** The blast radius here is a live instance; a guess is not a
  reading.
- **A blocked permission is answered by stopping and reporting**, never
  retried and never routed around. A denied access on a live target is
  information, not an obstacle.
- **The full cost (phase 5) is disclosed before the patch, in the same breath
  as the offer.** An offer that withholds the drift debt until after
  acceptance is not an offer.

## Phase 2 — Preconditions

**Gate: every precondition confirmed, none assumed.**

- **The fix is already committed and verified locally.** This mechanism
  deploys; it never authors and never first-tests.
- **Confirm what the deployable unit actually is.** One swappable artifact, or
  an artifact plus a dependency set that must move with it? The difference
  decides whether this procedure applies at all. Confirm it against the
  running target; do not reason it from the build definition.
- **Confirm the running target's environment genuinely matches what was
  built.** A build produced for a different runtime generation, architecture,
  or configuration will load and then misbehave, or not load and take the
  process down with it.
- **Confirm what tooling exists inside the running target.** A minimal or
  hardened runtime may offer no interactive shell, no package manager, and no
  text editor at all. Discovering that after the artifact is half-copied is
  the failure this step prevents.

## Phase 3 — Procedure

**Gate: each step's result observed before the next begins.**

1. **Inspect the live target's actual current layout first** — never the
   source-controlled definition, which may already be stale against what is
   deployed. What is running is the ground truth; what is committed is a
   claim about it.
2. **Build `<ARTIFACT_TYPE>` locally in the exact configuration that ships.**
   A debug or development build that happens to contain the fix is a different
   artifact with different behaviour.
3. **Transfer it with `<COPY_MECHANISM>`, using the owner's own access, never
   the agent's.** The authorization is the owner's; so is the credential path
   it travels on (`core/method/secrets-posture.md` owns how a credential is
   handled once it is in play).
4. **Write into the target's writable or ephemeral layer only**, leaving the
   durable image untouched. The durable image is what the pipeline owns; a
   patch that mutates it creates a second, undocumented source of truth that
   outlives the incident.
5. **Check the copied file's ownership and permissions match what the running
   process expects.** A correct artifact the process cannot read fails as
   though the fix were wrong.
6. **Reload the process with `<RELOAD_MECHANISM>`, without recreating the
   instance.** Recreating is the one action that discards the patch — the
   writable layer goes with it. Whatever `<RELOAD_MECHANISM>` is, it is not a
   recreate call, and the instantiated page says so at the point of use.
7. **Verify, then report, in the same message.** A report of a patch whose
   effect has not yet been observed is a claim about the future.

## Phase 4 — Verification

**Gate: a live functional signal, not a static check.**

The obvious static check — searching the deployed artifact for a string the
fix introduced — **lies in both directions** for a compiled or packaged
`<ARTIFACT_TYPE>`. Such formats store literals and identifiers in different
sections, and may store neither as plain text: the string can be absent from
an artifact that carries the fix, and present in one that does not. Treat any
such check as evidence that **a file got copied**, never as evidence that
**it works**.

The only check that counts is `<VERIFICATION_SIGNATURE>` — a live functional
signal:

- a specific error stopping;
- a specific new behaviour appearing;
- no crash-restart loop after the reload.

The claim made from that signal is exactly what it supports: **"the harm
stopped."** Never "the incident is closed."
`core/method/incident-posture.md` (`incident-posture.containment`,
`incident-posture.closure`) owns the status rule — a containment that leaves
the improper state standing is not `closed` — and this page defers to it
rather than restating it.

## Phase 5 — Drift-debt disclosure

**Gate: stated every time, before acting, in full.**

- The change exists **nowhere but this one instance's ephemeral layer**. It is
  in no artifact registry, no deployed revision, and no pipeline record.
- The next ordinary deploy, restart-with-recreate, or scale event **silently
  reverts it**, with no warning, and the symptom returns looking like a new
  incident — to people who were not in this conversation.
- What the source of truth says is running and what is actually running have
  now **diverged**. Every later reader of the deployment record is reading a
  false statement until the fix lands properly.
- This is **never a substitute** for landing the fix through the real
  pipeline. It buys time for that, and the time it buys is the only thing it
  buys.

## Anti-patterns

- Patching a fix that has not been verified locally, or authoring the fix in
  the live target.
- Reading the committed deployment definition instead of the live layout.
- Recreating the instance to "make sure the reload took".
- Reporting a string match in the artifact as proof the fix is live.
- Saying "incident closed" on the strength of a stopped error.
- Disclosing the drift debt after the owner has already accepted.
- Retrying or routing around a blocked permission on a live target.
- Using the agent's own access because the owner's was slower to arrange.
- Writing into the durable image because the writable layer was inconvenient.

## Reference files

- `core/method/incident-posture.md` (containment, evidence, and the status
  rule this page defers to — a containment that leaves the improper state
  standing is never `closed`)
- `core/method/vcs-posture.md` (`vcs-posture.publish-authorization` — the
  authorization boundary that covers reloading a running service)
- `core/method/secrets-posture.md` (how the transfer credential is handled)
- `core/method/release-posture.md` (the pipeline path this stopgap owes a
  return to, and the artifact identity it temporarily breaks)
- `protocols/recover.md` (classify the failure before reaching for this)
