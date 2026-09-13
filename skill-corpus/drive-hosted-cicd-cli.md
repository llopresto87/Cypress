# Suggested skill: drive-hosted-cicd-cli

> Optional procedure — **a template, vendor-neutral**. Driving a hosted CI/CD
> platform from its command-line client: authenticating once, queueing a run
> against the right refs, proving what the run actually built, and registering
> a pipeline that so far exists only as a committed definition. Not a core
> skill; instantiate into `docs/graph/skills/<name>.md` (its home, projected
> into the harness dirs the plant uses) from `templates/skill.template.md` if
> selected. **Composes** `core/method/release-posture.md` (artifact identity,
> rollout ordering), `core/method/secrets-posture.md` (credential handling),
> and `core/method/vcs-posture.md` (the publishing boundary) **by reference and
> restates none of them**. What it adds is the two-branch trap and the way to
> prove which ref a run actually operated on.

**Instantiate by supplying:** `<CLI>`, `<ORG>`/`<PROJECT>` or the platform
equivalent, `<CREDENTIAL_ENV_VAR>`, the pipeline/workflow id table, the
per-target override parameter name(s), and the preview/dry-run call if the
platform has one.

## When to apply

- A pipeline must be queued, inspected, or registered from a terminal rather
  than from the platform's web interface.
- A run must be proven to have built a specific ref of a specific subject
  repository, not merely to have been asked to.
- A workflow definition has been committed but no runnable object exists for
  it yet on the platform.

## 1. One session login

Authenticate **once per shell session**, from a credential already in the
environment (`<CREDENTIAL_ENV_VAR>`). The credential is never echoed, never
placed in a URL, and never passed on a command line where a process list or a
shell trace would capture it — `core/method/secrets-posture.md`
(`secrets-posture.channel`, `secrets-posture.recording`) owns how it enters
and how it is written about, and this page adds nothing to that.

**Pin the target organization/project explicitly on every command.** An
omitted target does not fail: it resolves against whatever the client's
configured default happens to be, and the call succeeds against the wrong
scope. Explicit pinning converts a silent wrong-scope success into a loud
failure.

## 2. The two-branch trap — the reason this page exists

A triggered run resolves **two independent branch questions** from **two
different inputs**:

| question | set by |
|---|---|
| which ref the **pipeline definition** is read from | the queue call's definition-ref input |
| which ref(s) of the **subject repositories** the run builds | the run's own parameters, with possible per-target overrides |

**Matching one proves nothing about the other.** A run can compile a
definition from the intended branch and check out an entirely different ref of
the code it builds, and every summary field will look correct.

**Omitting the definition-ref does not mean "the branch I am on".** It means
the *definition's own configured default*, which is usually the trunk. If the
definition file you are trying to run exists only on a feature branch, the run
never starts at all — and that is the lucky case, because the error names the
file, the repository and the ref, so the mistake is visible. The unlucky case
is a definition that *does* exist on the default branch in an older form: it
compiles, it runs, and it is not the pipeline you edited.

Read the flag's own help with suspicion. The wording platforms use for this
input — "the branch on which the run is to be queued", or similar — reads
exactly like the branch that gets built. It is not; it is the branch the
definition is read from. Naming the ref explicitly on every call costs one
flag and removes the whole class.

The expensive part: **the platform's own displayed step name and log for the
initial checkout are generated from the compile-time input and are blind to
any later per-target override.** The display is therefore a faithful rendering
of what was requested at compile time and a false statement about what landed
on the executing agent. Trusting that display is the single most expensive
mistake this procedure exists to prevent.

**This trap is not one vendor's.** It recurs on every hosted CI/CD platform
that separates the ref a workflow definition is read from from the ref it
operates on. An instantiated copy of this page names its own platform's two
inputs; the trap survives the renaming.

## 3. Per-pipeline parameter surfaces differ

**Read each pipeline's own declared parameter set before composing a call.**
Two pipelines in the same project rarely take the same parameters, and a
parameter name that means one thing in one pipeline can mean another
elsewhere.

**Never "simplify" an unusual-looking default without reading why it is set
that way.** A default can be maximal by design — a list that names everything
precisely so that the pipeline's exclusion logic has something to subtract
from. Blanking it silently re-includes what was deliberately excluded, and the
run succeeds while building more than anyone asked for.

## 4. The dry run that costs nothing

Use the platform's **free, non-mutating preview/validate call before every
consequential queue**. It compiles the definition and validates every
parameter without creating a run, and — the reason it belongs here — it
**checks both branch questions at once**, before anything executes.

A preview call that a platform does not offer is recorded as absent in the
instantiated page, not silently skipped: the instantiation says what
compensates for it.

## 5. Proving what a run actually built

A run's summary fields answer only **"what was asked for"**. They are the
request, echoed back.

To prove **what landed on the executing agent**, open the execution log of the
specific step that performs the **real per-target checkout** — not the summary
step, and not the initial checkout display from fact 2. That log is the only
place the resolved ref appears as an observed fact rather than as a restated
input.

The identity discipline this feeds is `core/method/release-posture.md`'s
(`release-posture.artifact-identity`): what shipped is the artifact that was
verified, addressed immutably. A run whose built ref was never proven cannot
support that claim.

## 6. Registering a pipeline that exists only as a committed definition

A definition file in source control is **not yet a runnable object** on the
platform. Committing it changes nothing about what can be queued.

When one must be created:

- **Re-derive its identifier and scope from the platform's own live listing**,
  never copy one from an unrelated project or from documentation.
- **Identical names resolve to different objects in different scopes.** A name
  that is unique in one project is not a unique reference across the platform,
  and a copied identifier silently addresses a stranger's object.
- Record the resulting id in the instantiated page's pipeline/workflow id
  table, so the next session reads it instead of re-deriving it.

## 7. Opening a change request from the same client

Opening a change request (pull/merge request) from `<CLI>` **publishes the
branch**. It carries the same publishing authorization boundary as any other
push — `core/method/vcs-posture.md` (`vcs-posture.publish-authorization`) owns
it, and this page does not restate it. Convenience of the client is not a
grant.

## Anti-patterns

- Authenticating per command, or interpolating the credential into a URL.
- Omitting the organization/project pin and trusting the client's default.
- Reading the initial-checkout step's displayed name as proof of what was
  built.
- Treating the run summary as evidence of the ref that landed.
- Blanking an unusual default to "simplify the call".
- Queueing a consequential run without the free preview.
- Copying a pipeline identifier from another project because the name matched.
- Opening a change request from the client without the push authorization it
  implies.

## Reference files

- `core/method/release-posture.md` (artifact identity and rollout ordering —
  what fact 5's proof is in service of)
- `core/method/secrets-posture.md` (how `<CREDENTIAL_ENV_VAR>` enters, and why
  it never reaches a log, a URL, or a command line)
- `core/method/vcs-posture.md` (`vcs-posture.publish-authorization` — fact 7)
- `protocols/verify.md` (the gate results a run's output is read as, and the
  null-result control a green run owes)
