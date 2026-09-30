# Suggested skill: live-patch-stopgap

> Optional procedure — **a template**. Deploying an already-committed,
> already-verified fix straight into a running instance by replacing one
> artifact and reloading the process: no push, no pipeline, no rebuild. A
> stopgap to stop active harm on a fix that has passed everything except the
> pipeline. **High blast radius.** **Composes**
> `core/method/incident-posture.md` (the status rule) and
> `core/method/vcs-posture.md` (the authorization boundary) by reference. What
> it adds is the one thing neither owns: the mechanics and the honest
> accounting of a change that exists in exactly one running instance.

**Instantiate by supplying:** `<ARTIFACT_TYPE>`, `<RUNTIME_TARGET>`,
`<COPY_MECHANISM>`, `<RELOAD_MECHANISM>` (an in-place reload; Phase 3 step 6),
`<VERIFICATION_SIGNATURE>`.

## When to apply

- A fix exists, is committed, and is verified locally, and the pipeline that
  would normally deploy it is unavailable, backed up, or hours away.
- The harm the fix removes is **active** — happening now, to someone.
- The owner has authorized this specific patch, having been told its cost.

This mechanism ONLY deploys a fix that is already proven, in the situation
above; a working pipeline, and authoring or first-testing a fix, take the
ordinary path.

## Phase 1 — Authorization

**Gate: an explicit, per-invocation owner authorization naming this patch,
given after the drift debt below was stated in full.**

- Per invocation, never standing. A patch authorized last week does not
  authorize this one; "go ahead with the fix" authorized the fix, not this
  deployment of it. `core/method/vcs-posture.md`
  (`vcs-posture.publish-authorization`) owns the boundary; reloading a running
  service sits inside it.
- **Disambiguate an ambiguous instruction with the owner.** The blast radius
  here is a live instance; a guess is not a reading.
- **Answer a blocked permission by stopping and reporting it**: on a live
  target a denial is the owner's access decision, and a retry or a route around
  it overrides that decision.
- **Disclose the drift debt before the patch, every time, in the same breath as
  the offer.** An offer that withholds it until after acceptance is not an
  offer. The debt, in full:
  - The change exists **nowhere but this one instance's ephemeral layer**. It
    is in no artifact registry, no deployed revision, and no pipeline record.
  - The next ordinary deploy, restart-with-recreate, or scale event **silently
    reverts it**, with no warning, and the symptom returns looking like a new
    incident — to people who were not in this conversation.
  - What the source of truth says is running and what is actually running have
    now **diverged**. Every later reader of the deployment record is reading a
    false statement until the fix lands properly.
  - It buys time to land the fix through the real pipeline, and time is the
    only thing it buys.

## Phase 2 — Preconditions

**Gate: every precondition confirmed, none assumed.**

- **The fix is already committed and verified locally.**
- **Confirm what the deployable unit actually is.** One swappable artifact, or
  an artifact plus a dependency set that must move with it? The difference
  decides whether this procedure applies at all. Confirm it against the
  running target (Phase 3 step 1 says why).
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

1. **Inspect the live target's actual current layout first**: what is running
   is the ground truth; what is committed is a claim about it, and may already
   be stale against what is deployed.
2. **Build `<ARTIFACT_TYPE>` locally in the exact configuration that ships.**
   A debug or development build that happens to contain the fix is a different
   artifact with different behaviour.
3. **Transfer it with `<COPY_MECHANISM>`, using ONLY the owner's own access**:
   the authorization is the owner's, and so is the credential path it travels
   on (`core/method/secrets-posture.md` owns how a credential is handled once
   it is in play).
4. **Write into the target's writable or ephemeral layer only**, leaving the
   durable image untouched. The durable image is what the pipeline owns; a
   patch that mutates it creates a second, undocumented source of truth that
   outlives the incident.
5. **Check the copied file's ownership and permissions match what the running
   process expects.** A correct artifact the process cannot read fails as
   though the fix were wrong.
6. **Reload the process in place with `<RELOAD_MECHANISM>`.** Recreating the
   instance discards the writable layer and the patch with it, so the
   instantiated page names the reload at the point of use.
7. **Verify, then report, in the same message.** A report of a patch whose
   effect has not yet been observed is a claim about the future.

## Phase 4 — Verification

**Gate: a live functional signal, not a static check.**

The obvious static check — searching the deployed artifact for a string the
fix introduced — **lies in both directions** for a compiled or packaged
`<ARTIFACT_TYPE>`. Such formats store literals and identifiers in different
sections, and may store neither as plain text: the string can be absent from
an artifact that carries the fix, and present in one that does not. Treat any
such check as evidence ONLY that a file got copied.

The only check that counts is `<VERIFICATION_SIGNATURE>` — a live functional
signal:

- a specific error stopping;
- a specific new behaviour appearing;
- no crash-restart loop after the reload.

The claim made from that signal is exactly **"the harm stopped"**; the
incident's status follows `incident-posture.containment` and
`incident-posture.closure`.

## Reference files

- `core/method/incident-posture.md` (containment, evidence, and the status
  rule this page defers to)
- `core/method/vcs-posture.md` (`vcs-posture.publish-authorization` — the
  authorization boundary that covers reloading a running service)
- `core/method/secrets-posture.md` (how the transfer credential is handled)
- `core/method/release-posture.md` (the pipeline path this stopgap owes a
  return to, and the artifact identity it temporarily breaks)
- `protocols/recover.md` (classify the failure before reaching for this)
