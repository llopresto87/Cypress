# Tool: declared-variable-existence-auditor

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: the shape — the three-outcome
> vocabulary, the redirect refusal, the two-step skip predicate — is portable;
> the transport that talks to the variable store is vendor-specific and is
> written against whatever store the adopting project uses.

## 0. Identity

- **Category:** ops
- **Name:** declared-variable-existence-auditor
- **Language / runtime:** any (an HTTP client and a reader for the project's
  declaration file are the whole requirement)
- **Stability:** **blueprint** — no portable implementation, because the
  authenticated call to a configuration-variable store has no stack-neutral
  form. Everything above that call is portable and is the value of the page.

## 1. What it does

Asks a **live, credentialed configuration-variable store** whether the names a
project **declares** it needs actually exist there.

It reads **names and a "this is secret" flag only, never a value.** That is the
whole safety posture, and it is what makes the tool runnable from a pipeline, a
developer machine, or a review without turning the audit itself into a secret
exposure.

It exists because the declaration and the store drift independently, and nothing
notices until a deployment fails at start-up with a message about something else.
A project's declaration file says "these names must be set"; the store holds
whatever the last person to touch it left there. The gap between those two is
invisible from either side alone.

## 2. Interface & invocation

```sh
declared-variable-audit \
  --declared <path to the project's declaration of required names> \
  --scope <the store's addressing of one variable set> \
  [--json]
```

- **Inputs:** the project's own declaration of required names (its single source
  of truth for "what must exist"); the store scope to query; credentials from the
  environment, never from a flag or a file path passed on the command line.
- **Outputs:** one line per declared name — present, absent, or unknown — and a
  summary. The secret flag is reported as a flag; **no value is ever read,
  printed, logged, or returned**, including in the JSON form.
- **Exit codes:** a **closed vocabulary** — see §3. Adding an outcome means
  adding a code, not overloading one.
- **Preconditions:** network reach to the store; a credential with permission to
  **list** names in the scope.
- **Names-only is a property of THIS TOOL, not of the store.** Assume the
  opposite of what is convenient: most stores return a non-secret variable's
  value in plaintext beside a secret's `null`, in the same response, because
  only the secret flag suppresses it. So the response is split at that boundary
  the moment it arrives — a `raw` half that is compared and **never printed**,
  and a `display` half that is printed and has already passed the allow-list.
  A tool that merely *chooses not to look* at values is one careless log line
  from publishing them; the split is what makes the guarantee structural. If a
  store genuinely cannot list names without values, that is a finding about the
  store — it is never a reason to relax the split.

## 3. Approach / algorithm

### Three outcomes, never collapsed

The durable core. Three different things can happen, and a tool that reports two
of them identically is lying about one:

1. **The server said no** — it answered, authoritatively, that the name is not
   there. This is a **finding about the project**: a declared name is missing.
2. **The server refused to answer** — authentication failed, the scope does not
   exist, permission was denied, the request was rejected. This is a **finding
   about access**, and it says nothing at all about whether the name exists.
3. **The tool could not run** — no client, no network, a malformed declaration
   file, an unparseable response. This is a **finding about the tool**.

Give each its own exit code, and keep the vocabulary **closed**: every path
through the program terminates in exactly one of the declared codes, and there is
no catch-all. Collapsing (2) into (1) is the dangerous one: it reports missing
variables that are, in fact, present and merely unreadable, and it does so with
the confident wording of an authoritative answer.

### Hard refusal to follow redirects

The client **must not follow redirects while carrying the credential.** A 3xx
response would otherwise hand a bearer token to a **server-chosen host**: the
tool would reach its configured endpoint, be told to go elsewhere, and obediently
re-send the authorization header to that elsewhere. Disable redirect following
explicitly, and treat any 3xx as outcome (2) — the server refused to answer —
rather than as something to chase. Do not make this configurable.

### Two-step skip predicate

Skipping is where audits quietly die, so the predicate has two steps and they are
not symmetric:

- **No credential and no automation marker** ⇒ **SKIP**, cleanly and loudly. A
  developer running the suite on a laptop has no store credential and should not
  be blocked by one.
- **Running under automation with an empty or missing token** ⇒ **HARD FAILURE**,
  never a skip. Under automation the credential is supposed to be injected; an
  empty one means the injection broke, and a skip there turns a broken audit into
  a green run forever. The most expensive version of this bug is the one where
  the token expires and the gate keeps passing.

Read the automation marker from the environment the runner sets, and check it
**before** deciding to skip, not after.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the read-names-and-flags-only rule; the
  three-outcome model and closed exit-code vocabulary; the redirect refusal; the
  two-step skip predicate; the rule that the project's declaration file is the
  single source of "what must exist".
- **Vendor-specific (write per store):** the endpoint and its pagination; the
  authentication scheme and where the credential comes from; how a scope is
  addressed; the response shape that names and flags are read out of.
- **Adopting note:** where the store's client library follows redirects by
  default, either turn that off explicitly or use a lower-level client. "It
  probably will not redirect" is not the property being relied on.

## 5. Pitfalls and sharp edges

- **The asymmetry, stated plainly: a names-and-flags probe can prove a
  variable's ABSENCE, but never the presence of a usable VALUE.** A name can
  exist and hold an empty string, a stale credential, a value for the wrong
  environment, or a value the consuming service cannot parse. Every one of those
  reads as present. The audit's green means *nothing declared is missing by
  name* — say exactly that, in the tool's own output, so a reader cannot inflate
  it into "the configuration is correct".
- **The snapshot is taken when the run is queued, not when the value is read.**
  Many stores materialize a variable set at the moment a run starts; a value
  changed afterwards is not what the run has, and a value the audit saw may not
  be the value the deployment got. The audit describes the store at query time
  and nothing else. Two runs that disagree about the same variable may both be
  telling the truth about different instants.
- **Collapsing "refused" into "absent" manufactures findings.** A permissions
  change or an expired token turns every declared name into a reported defect,
  and the report looks exactly like a real one. This is why the vocabulary is
  closed and the codes are distinct.
- **A skip that should have been a failure is permanent.** Under automation,
  once an empty credential skips instead of failing, nothing ever raises its
  hand again. Test the predicate in both directions explicitly.
- **Never widen the read to values "just for this check".** The moment the tool
  reads a value, it becomes a thing that must not be logged, cached, printed on
  failure, or included in a diagnostic dump — and one of those will eventually
  happen. Keep the capability it does not have.

## 6. Tests that cover it

Cover: a declared name absent from the store yields the *absent* code and names
it; a rejected credential yields the *refused* code and **no** absent findings; a
malformed declaration file yields the *tool* code; a 3xx response is **not**
followed and is classified as refused, with the credential proven not to have
been re-sent; no code path returns or logs a value, including on the error paths;
no credential and no automation marker exits as a clean skip; the automation
marker set with an empty token is a **hard failure**, not a skip; every
terminating path maps to one of the declared codes and no other.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/layered-config-merge-verifier.md` (answers
  how strongly a variable is **guarded** in the configuration text — a different
  question, and the blind spot each leaves is the other's subject);
  `tool-corpus/ops/env-secret-rotation.md` (writes the values this only ever
  counts by name); `tool-corpus/ops/structured-secret-field-detector.md` (the
  complementary "what is already inside the artifact" direction).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-09-13 — created from harvested, generalized capability, by docs-librarian.
