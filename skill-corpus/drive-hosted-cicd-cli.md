# Suggested skill: drive-hosted-cicd-cli

> Optional procedure, **a template, vendor-neutral**. Driving a hosted CI/CD
> platform from its command-line client: authenticating once, queueing a run
> against the right refs, proving what the run actually built, and registering
> a pipeline that so far exists only as a committed definition. **Composes**
> `core/method/release-posture.md` (artifact identity, rollout ordering),
> `core/method/secrets-posture.md` (credential handling),
> `core/method/vcs-posture.md` (the publishing boundary), and
> `core/method/bounded-execution.md` (`toolcraft.bounded-execution`: run
> identity and liveness evidence) by reference. What it adds is the two-branch
> trap, testing unmerged work through run parameters, and the way to prove
> which ref a run actually operated on.

**Instantiate by supplying:** `<CLI>`, `<ORG>`/`<PROJECT>` or the platform
equivalent, `<CREDENTIAL_ENV_VAR>`, the pipeline/workflow id table, the
per-target override parameter name(s), the parameter recipe that runs an
unmerged branch, and the preview/dry-run call if the platform has one.

## When to apply

- A pipeline must be queued, inspected, or registered from a terminal rather
  than from the platform's web interface. For a consequential run the terminal
  is the better surface anyway: a command can be read before it is sent and
  re-run after, and a sequence of web-form clicks can be neither.
- Work on a branch that is not merged must be exercised in CI.
- A run must be proven to have built a specific ref of a specific subject
  repository, not merely to have been asked to.
- A workflow definition has been committed but no runnable object exists for
  it yet on the platform.

## 1. One session login

Authenticate **once per shell session**, from a credential already in the
environment (`<CREDENTIAL_ENV_VAR>`). The credential stays in the environment
and off every URL, command line and shell trace, where a process list or a
trace would capture it (`core/method/secrets-posture.md`:
`secrets-posture.channel`, `secrets-posture.recording`).

**Pin the target organization/project explicitly on every command.** An
omitted target does not fail: it resolves against whatever the client's
configured default happens to be, and the call succeeds against the wrong
scope. Explicit pinning converts a silent wrong-scope success into a loud
failure.

**Pin the pipeline the same way.** Two definitions whose names or ids differ by
one suffix or one digit can deploy to different environments. When a request
could mean either ("the production bootstrap"), ask which one is meant,
because the wording cannot settle it.

## 2. The two-branch trap: the reason this page exists

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
never starts at all. That is the lucky case, because the error names the
file, the repository and the ref, so the mistake is visible. The unlucky case
is a definition that *does* exist on the default branch in an older form: it
compiles, it runs, and it is not the pipeline you edited.

Read the flag's own help with suspicion. The wording platforms use for this
input ("the branch on which the run is to be queued", or similar) reads
exactly like the branch that gets built. It is not; it is the branch the
definition is read from. Naming the ref explicitly on every call costs one
flag and removes the whole class.

**The platform's own displayed step name and log for the initial checkout are
generated from the compile-time input and are blind to any later per-target
override.** The display is therefore a faithful rendering of what was requested
at compile time and a false statement about what landed on the executing
agent; §5 says where the landed ref is observed instead.

**This trap is not one vendor's.** It recurs on every hosted CI/CD platform
that separates the ref a workflow definition is read from from the ref it
operates on. An instantiated copy of this page names its own platform's two
inputs; the trap survives the renaming.

**Testing work that is not merged.** The two inputs above are also how an
unmerged branch gets tested, and they are the only sanctioned way. Queue the
run with the definition-ref pointing at the branch that holds the edited
definition, and with the per-target parameters pointing the subject
repositories at the branches under test. The default branch is left alone.
Merging to get code tested, or opening a change request so that a merge-gated
run fires, is publishing; `core/method/vcs-posture.md` ("Sharp edges") owns
that boundary. Both branch questions apply to such a run, so prove it with
§5 before trusting its result. Record the exact parameter recipe in the
instantiated page, so the next session reruns it instead of rediscovering it.

## 3. Per-pipeline parameter surfaces differ

**Read each pipeline's own declared parameter set before composing a call.**
Two pipelines in the same project rarely take the same parameters, and a
parameter name that means one thing in one pipeline can mean another
elsewhere.

**Keep an unusual-looking default until you have read why it is set that
way.** A default can be maximal by design: a list that names everything
precisely so that the pipeline's exclusion logic has something to subtract
from. Blanking it silently re-includes what was deliberately excluded, and the
run succeeds while building more than anyone asked for.

## 4. The dry run that costs nothing

Use the platform's **free, non-mutating preview/validate call before every
consequential queue**. It compiles the definition and validates every
parameter without creating a run. The reason it belongs here is that it
**checks both branch questions at once**, before anything executes.

A preview call that a platform does not offer is recorded as absent in the
instantiated page, not silently skipped: the instantiation says what
compensates for it.

## 5. Identifying the run, and proving what it built

**Address the run by the id the queue call returned.** Record that id when the
call returns, and make every later status check, log fetch and cancel go to
that id. A run listing sorted "newest first" is not evidence of which run is
yours: a trigger, a retry or a chained tool can queue another run between your
call and your listing. Reading the top row as "my run" can conclude that a
run never started when it did, and a re-queue on that conclusion makes a
duplicate. On a deploy pipeline a duplicate is a second deploy.
`core/method/bounded-execution.md` (`toolcraft.bounded-execution`, clause 4)
owns the identity rule; this is where it bites on a hosted platform.

**"Stuck" is a claim about that run's own progress output.** Before cancelling
a run, or killing the tool that queued it, read the run's own timeline or its
growing log. A tool that has gone quiet in your terminal may be waiting on a
run that is working normally. Killing it and queueing again turns one run into
two.

**Queued is not delivered.** The queue call returns once the run is accepted,
not when it finishes, and a finished run is still not a release;
`core/method/release-posture.md` owns what delivery means.

**A run's exit status describes the command, not the platform.** A run can
report success after doing something other than what was intended, for
example removing a service it was never asked to touch. After a consequential
run, check the target's own state (the services that should be up, answering
where they should) before calling the platform healthy.

A run's summary fields answer only **"what was asked for"**. They are the
request, echoed back.

To prove **what landed on the executing agent**, open the execution log of the
specific step that performs the **real per-target checkout**, not the summary
step, and not the initial checkout display from §2. That log is the only
place the resolved ref appears as an observed fact rather than as a restated
input. Reach that log through the run's timeline (or job listing), which pairs
each step's record with its log id.

The identity discipline this feeds is `core/method/release-posture.md`'s
(`release-posture.artifact-identity`): what shipped is the artifact that was
verified, addressed immutably. A run whose built ref was never proven cannot
support that claim.

## 6. Registering a pipeline that exists only as a committed definition

A definition file in source control is **not yet a runnable object** on the
platform. Committing it changes nothing about what can be queued.

When one must be created:

- **Re-derive its identifier and scope from the platform's own live listing**,
  because identical names resolve to different objects in different scopes: a
  name that is unique in one project is not a unique reference across the
  platform, and an identifier copied from another project or from
  documentation silently addresses a stranger's object.
- Record the resulting id in the instantiated page's pipeline/workflow id
  table, so the next session reads it instead of re-deriving it.

## 7. Opening a change request from the same client

Opening a change request (pull/merge request) from `<CLI>` **publishes the
branch**. It carries the same publishing authorization boundary as any other
push, owned by `core/method/vcs-posture.md`
(`vcs-posture.publish-authorization`). Convenience of the client is not a
grant. The request's title and description are subject to the plant's
attribution setting exactly as a commit is (`vcs-posture.plant-settings`).

## Reference files

- `core/method/release-posture.md` (artifact identity and rollout ordering:
  what §5's proof is in service of)
- `core/method/secrets-posture.md` (how `<CREDENTIAL_ENV_VAR>` enters, and why
  it never reaches a log, a URL, or a command line)
- `core/method/vcs-posture.md` (`vcs-posture.publish-authorization`, §7;
  "Sharp edges", testing unmerged work without merging, §2)
- `core/method/bounded-execution.md` (`toolcraft.bounded-execution`: run
  identity and liveness evidence, §5)
- `protocols/verify.md` (the gate results a run's output is read as, and the
  null-result control a green run owes)
