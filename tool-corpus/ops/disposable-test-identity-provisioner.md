# Tool: disposable-test-identity-provisioner

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool — the fail-closed guard, the
> coupled-records model, and the lifecycle contract are portable; adopt them
> verbatim. Only the two store adapters are project-specific.

## 0. Identity

- **Category:** ops
- **Name:** disposable-test-identity-provisioner
- **Language / runtime:** bash + a CSPRNG (`openssl rand`) + whatever client the
  identity stores expose
- **Stability:** **portable** — the guard, lifecycle, and credential rules are
  stack-neutral; the two writes (auth store, authorization/profile store) are
  the adapter surface

## 1. What it does

Provisions and tears down a **fixed set of throwaway test identities** against a
**disposable target only**, minting a **fresh CSPRNG credential on every run** —
never derived from a seed, a name, or a date, and never recoverable after
creation.

It exists because test identities are otherwise created by hand, once, with a
guessable password, and then live forever: nobody remembers which environment
they are on, whether they were ever rotated, or whether the "test" account in
front of them is the disposable one or the real one. This tool makes the set
**reproducible, rotated by construction, and safe to delete**, and makes writing
to a non-disposable target **impossible rather than discouraged**.

## 2. Interface & invocation

```sh
provision.sh create --target <t> --yes-disposable [--ttl <hours>]
provision.sh status [--json]
provision.sh delete --target <t> --yes-disposable
provision.sh selftest --target <t> --yes-disposable
```

- **Inputs:** the target identifier; the explicit `--yes-disposable`
  affirmation on **every write path**; optionally `--ttl <hours>`.
- **Outputs:** on `create`, the minted credential printed **once**, and
  optionally written to an **owner-only-permissioned** file; on `status`,
  presence and metadata **only**; a non-zero exit on any refusal or failure.
- **Preconditions:** the target matches the disposable-target allowlist/pattern;
  write access to **both** identity stores.

## 3. Approach / algorithm

### Fail-closed target guard (checked before any write)

Every write path requires **both**:

1. an explicit `--yes-disposable` affirmation from the caller — the operator
   states, at the call site, that this target is throwaway; and
2. a target identifier that matches the **disposable-target allowlist/pattern**.

A target that fails either check is **refused before a single write is
attempted** — not rolled back after, not warned about. The default answer is no;
the affirmation and the allowlist are two independent keys, so a typo'd target
with the flag present, or the right target with the flag absent, both stop.
`status` is read-only and needs neither.

### The coupled-records model (the core fact this tool encodes)

An identity is very often **two coupled records**, not one:

- a record in the **authentication store** (the thing that verifies the
  credential and owns the identity's id), and
- a record in the **authorization / profile store**, keyed on the first
  record's id (roles, entitlements, tenant, profile).

The tool **always writes both**, and treats the pair as the unit of existence.
Writing only the auth record yields an identity that **authenticates
successfully but authorizes against nothing** — logins work, then every
subsequent action fails in a way that looks like a permissions bug, a data bug,
or a broken environment. It is a partial-provisioning failure, and it is
genuinely hard to diagnose from the symptom. The same coupling holds in reverse
for delete: remove both, or the orphan half is a landmine for the next run.

### Lifecycle

- **`create` is convergent.** It first removes any existing set for these
  identities, then creates them fresh. A second run therefore always leaves
  **exactly one known-good, freshly-rotated set** — never a second copy, never a
  half-updated one. "Run it again" is always a valid recovery move.
- **`delete` is idempotent.** Absent records are not an error; deleting twice, or
  deleting a set that never existed, exits zero.
- **TTL is optional and DEFAULT OFF.** `--ttl <hours>` may arm auto-expiry, but
  it is off unless asked for. An armed timer that fires **mid-engagement**
  presents as mysteriously broken credentials — the most expensive failure this
  tool can produce, and worse than a test identity that simply never expires on
  a target that is disposable anyway.
- **`selftest` exercises the full lifecycle as a gate:** create →
  verify-usable → re-create-and-confirm-the-credential-rotated → delete →
  verify-absent. It is the check that the tool still works against the current
  state of both stores, run before relying on it.

### Credential handling

- Minted from a **CSPRNG** at every `create`. Never derived from the identity
  name, the target, a date, or a shared seed — derived credentials are
  reproducible by anyone who knows the recipe.
- **Printed once**, at creation, and optionally written to an
  **owner-only-permissioned** file if the caller asks for one.
- The auth store **never returns the plaintext again**. A lost credential is
  therefore **not recoverable** — the remedy is to `create` again (a rotation),
  which is cheap precisely because `create` is convergent.
- **`status` never displays a credential** — only presence and metadata. A
  status command that prints secrets ends up in logs, screenshots, and CI
  output.

## 4. Portable vs blueprint

- **Portable (use as-is):** the two-key fail-closed guard; the
  write-both-records rule; convergent `create` / idempotent `delete`; TTL
  default-off; the `selftest` sequence; CSPRNG minting, print-once, owner-only
  file, and secret-free `status`.
- **Project-specific (fill in):** the two store adapters (how an auth record and
  an authorization/profile record are created, read, and deleted), the
  disposable-target pattern, and the fixed list of identities in the set.

Portable skeleton (the guard and lifecycle are complete; the adapters are stubs):

```bash
#!/usr/bin/env bash
set -euo pipefail
case "$-" in *x*) echo "refusing: set -x leaks credentials" >&2; exit 3;; esac

DISPOSABLE_PATTERN="${DISPOSABLE_PATTERN:?pattern matching throwaway targets}"
IDENTITIES=( "<id-1>" "<id-2>" )          # the fixed set

require_disposable() {                     # fail CLOSED, before any write
  [ "${AFFIRMED:-}" = "yes" ] || {
    echo "refusing: --yes-disposable not given" >&2; exit 2; }
  case "$TARGET" in
    $DISPOSABLE_PATTERN) ;;
    *) echo "refusing: '$TARGET' is not a disposable target" >&2; exit 2;;
  esac
}

# adapters — PROJECT-SPECIFIC; both stores, always both.
auth_create()  { :; }   # -> prints the new record's id
auth_delete()  { :; }
authz_create() { :; }   # keyed on the auth record's id
authz_delete() { :; }
auth_verify()  { :; }   # credential actually usable?
records_exist(){ :; }

create_one() {
  local name="$1" secret id
  secret="$(openssl rand -base64 24)"      # CSPRNG, fresh every run
  delete_one "$name"                       # convergent: never accumulate
  id="$(auth_create "$name" "$secret")"
  authz_create "$id" "$name"               # BOTH records or the identity is broken
  printf '%s\t%s\n' "$name" "$secret"      # printed ONCE; never retrievable again
}

delete_one() {                             # idempotent: absent is not an error
  local name="$1"; authz_delete "$name" || true; auth_delete "$name" || true
}

case "${1:-}" in
  create)  require_disposable; for n in "${IDENTITIES[@]}"; do create_one "$n"; done;;
  delete)  require_disposable; for n in "${IDENTITIES[@]}"; do delete_one "$n"; done;;
  status)  for n in "${IDENTITIES[@]}"; do                    # metadata only
             records_exist "$n" && echo "$n present" || echo "$n absent"; done;;
  selftest) require_disposable                                # full lifecycle gate
            create_one "<probe>" >/dev/null; auth_verify "<probe>"
            first="$(create_one "<probe>")"; second="$(create_one "<probe>")"
            [ "$first" != "$second" ] || { echo "credential did not rotate" >&2; exit 1; }
            delete_one "<probe>"; ! records_exist "<probe>";;
  *) echo "usage: provision.sh {create|status|delete|selftest} --target <t> --yes-disposable [--ttl <hours>]" >&2; exit 1;;
esac
```

## 5. Pitfalls and sharp edges

- **Writing one record of a coupled pair** is the signature failure of this
  capability: the identity logs in and then authorizes against nothing, and the
  symptom points everywhere except at provisioning. Write both, delete both,
  and have `status` report the pair, not just the auth half.
- **Guarding after the first write is not guarding.** The disposable check must
  run before any store is touched; a "we'll roll back if the target was wrong"
  design has already written to production by the time it notices.
- **A single guard is one typo from a real target.** The explicit affirmation
  and the allowlist/pattern are deliberately redundant; do not collapse them.
- **Non-convergent `create` accumulates duplicates** — a second run leaves two
  sets, and the next debugging session is about which one is live. Remove first,
  then create.
- **TTL on by default is a self-inflicted outage.** Credentials that vanish
  mid-engagement look like an environment failure and cost far more than a
  lingering identity on a disposable target.
- **Expecting to recover a lost credential.** The auth store will not return it.
  Re-`create` (rotate) is the answer, and the tool is built so that is safe.
- **`status --json` that includes the credential** turns the safe read-only
  command into the leak; emit presence and metadata only.
- **A derived or fixed credential** ("test target, who cares") makes every
  provisioned identity predictable to anyone who has read the script. CSPRNG,
  every run, no exceptions.

## 6. Tests that cover it

Cover: a target outside the allowlist is refused with **zero writes** attempted;
a missing affirmation is refused likewise; `create` writes **both** records and
`status` reports the pair; a second `create` leaves exactly one set and a
**different** credential; `delete` on an absent set exits zero; TTL is off
unless requested; `status` output contains no credential material under any
flag; `selftest` passes end to end and fails loudly if the credential does not
rotate.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/env-secret-rotation.md` (same CSPRNG,
  print-once, owner-only-permission discipline for secrets at rest);
  `tool-corpus/testing/http-smoke-suite.md` (a natural consumer — the identities
  this mints are what an auth-enforcement assertion authenticates with).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-08-05 — created from harvested, generalized capability, by docs-librarian.
