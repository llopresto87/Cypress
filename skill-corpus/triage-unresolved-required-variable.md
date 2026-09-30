# Suggested skill: triage-unresolved-required-variable

> Optional procedure: a deployment stops because one or more required
> configuration variables resolved to nothing, and each one must be sorted into
> the bucket that decides its fix before anyone touches the pipeline. It runs
> under the role `agent-corpus/env-contract-manager.md` when
> a plant has selected that role, and under `reliability` otherwise.
> **Composes** `core/method/secrets-posture.md` (names and locations, never
> values), `protocols/test-first.md` (the test that pins a deliberate empty
> mode), `protocols/verify.md` (a gate not run is recorded as not run), and
> `tool-corpus/ops/declared-variable-existence-auditor.md` (the names-only
> store probe) by reference. What it adds is the
> three-bucket classification, the one sanctioned exception to it, and the
> diagnostic order that finds a missing value before a wiring bug.

**Instantiate by supplying:** `<RESOLVE_ERROR>` (the exact message the
fail-closed check prints), `<CONSUMER_SOURCES>` (where each component reads its
configuration: settings classes, entrypoint scripts, framework config
binders), `<DEPLOY_MANIFESTS>` (the files that reference the variables at
deploy time, and which of them are local-only), `<VARIABLE_STORE>` (where
values live, and whether it is bound when a run is queued or when a step
reads it), `<ALIAS_MECHANISM>` (how the deploy layer maps one name onto
another, if it has one), `<TARGET_EXEC>` (how to run a command inside the
deployed target), and `<GOLDEN_TEST>` (the test that pins the generated
variable set, if there is one).

## When to apply

- A deploy or start-up fails closed with `<RESOLVE_ERROR>` naming one or more
  variables.
- A variable is set in the store, yet arrives empty in the running target.
- A deploy still fails after someone saved the missing value.
- Someone proposes a default for a required variable "to get the deploy
  through".

## 1. Classify each variable into exactly one bucket

Start from the **consumer**: for each variable the error names, read the
application code and container entrypoint that read it, and the deploy
manifests that reference it, split into the local and the non-local side. The
bucket decides the fix, and every variable goes into exactly one.

| bucket | how you know | the fix |
|---|---|---|
| **Dead config** | no reader anywhere in the consumer | remove the stale reference from the deploy manifest and unwire it from the contract; do not supply a value |
| **Blank-safe** | the consumer supplies its own fallback (a settings default, an entrypoint `${X:-N}`) | give the deploy reference a default that equals the consumer's own fallback **exactly**; keep the required check everywhere else |
| **Real secret** | a reader rejects or breaks on empty (throws, refuses to start, signs with nothing) | leave the reference bare so the fail-closed check keeps guarding it, and supply the value; a default or an optional flag would disarm that check (§2 is the one exception) |

A blank-safe default that differs from the consumer's fallback is a second
home for that value, and the two will drift. When the consumer renames the
variable between the host and the container, the default goes on the name the
deploy layer actually resolves.

## 2. The one exception, and what it costs

A variable a reader would otherwise break on may be made optional only when
all three of these exist, and each is named in the change:

1. **An owner-accepted risk id**: the owner has accepted, in the plant's risk
   record, that this capability runs without the secret.
2. **A reader that tolerates empty by design**: the consumer reads the value
   with an explicit empty fallback that its authors wrote on purpose, not a
   null that happens to pass.
3. **A test that pins the empty mode**: the consumer's own suite runs the
   configured and the unconfigured deployment and asserts what each does
   (`protocols/test-first.md`).

The exception is scoped to that one name. A sibling secret read by the same
component keeps its bucket, and every later request to optionalize something
else must bring its own three artifacts. Without all three, the variable is a
real secret.

## 3. A name mismatch is bridged, never defaulted

When the value exists under one name (the form the store or the operator
uses) and the deploy reference asks for another (the form the framework binds),
the reference resolves empty and the check fails, correctly. Bridge the two
names with an **alias that has no default**, through `<ALIAS_MECHANISM>`: the
target name is filled from the source name, and an absent or empty source
writes nothing, so the target stays empty and the check still fires. Inject
the source name wherever the component's variable list is declared, so it
reaches the step. Leave the bare reference untouched.

Declare only inputs. A variable produced by a derivation step at deploy time
is an output, and it is correctly absent from the declared set; check that a
variable is not derived before adding it there, because a declared copy is a
second source for one value.

Check the other side too. Local and non-local manifests often spell the same
setting in two forms, and a local example file may omit it entirely. Confirm
the name on the side you are resolving before concluding it is missing.

## 4. Diagnose in this order

**First, is the value there?** The name contract can be correct at every layer
and the variable still arrive empty because the value is absent or empty in
the store. Check the value before re-reading the wiring. The
names-only probe (`tool-corpus/ops/declared-variable-existence-auditor.md`)
reads names and the secret flag, never values, so it can prove a name
**absent**. It can never prove a value **present**: a store that masks secrets
does not say whether a masked value is empty.

**Second, when was the run queued?** On a platform that binds the variable
store when a run is queued, a run in flight never sees a later edit. A failure
reported after the value was saved may come from a run queued before the save.
Compare the queue time against the save, then queue a fresh run. A green
re-run is evidence only for values that existed at its own queue time. Whether
`<VARIABLE_STORE>` behaves this way is a platform fact, owned by the
platform's library-corpus page (for one example,
`library-corpus/platform/azure-pipelines-yaml.md`).

**Third, what does the target hold?** Probe the deployed target so it reports
ONLY one of three states, never the value:

```sh
<TARGET_EXEC> sh -c 'if ! printenv NAME >/dev/null; then echo unset;
  elif [ -z "$(printenv NAME)" ]; then echo set-empty;
  else echo set-non-empty; fi'
```

The value never reaches the terminal, and neither does its length
(`core/method/secrets-posture.md`, `secrets-posture.recording`).

**Fourth, which code wrote it?** When the symptom is "empty in the target"
rather than "deploy failed", suspect deploy code older than the fail-closed
check. A deploy agent still running that code writes the empty value silently,
while the current branch fails loudly on the same input.

## 5. Record, and keep the golden test honest

Record variable **names and locations**, never values, in the fix and in every
note about it. Record each gate command and its real output where the plant
keeps verification results; a gate that did not run is written as not run
(`protocols/verify.md`).

When the fix legitimately changes the generated variable set (a new alias
output, a removed dead reference), update `<GOLDEN_TEST>`'s list of intended
deltas on purpose, with the reason. Change `<GOLDEN_TEST>` only through that
list, because loosening or deleting its assertion hides real drift behind a
passing gate.

## Reference files

- `agent-corpus/env-contract-manager.md` (the role that selects and applies
  this procedure)
- `core/method/secrets-posture.md` (`secrets-posture.recording`: names and
  locations only; `secrets-posture.channel`: how a value enters)
- `tool-corpus/ops/declared-variable-existence-auditor.md` (the names-only
  store probe used in step 4)
- `tool-corpus/ops/renamed-config-key-auditor.md` (when the mismatch is a key
  the framework renamed, not a naming difference between layers)
- `protocols/test-first.md` (the test that pins an accepted empty mode)
- `protocols/verify.md` (recording gate results, and absences, honestly)
