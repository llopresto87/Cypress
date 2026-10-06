# Suggested skill: add-infrastructure-object-safely

> Optional procedure: a person asks to add or change one infrastructure
> object (a virtual machine, a container, a hypervisor host entry, a
> composed application, a DNS or proxy entry) in a repository that declares
> infrastructure as code, and a mistake would break objects that already run.
> Started by the owner by name, never routed to automatically. **Composes**
> `protocols/grill.md` (the plan the owner approves),
> `core/method/restrictive-policy.md` (additive by default, destructive steps
> behind their own approval, report-only first: this page does not restate
> it), `core/method/contract-posture.md` (§1 missing input fails loudly; §3
> one document per contract; §4 step order is an asserted contract),
> `core/method/host-parity.md` (blast radius and
> the self-lockout check), `core/method/secrets-posture.md`, and
> `protocols/verify.md` by reference. What it adds is a five-state machine
> with an intake contract, collision checks over every declaration, and a
> GO/HOLD matrix.

**Instantiate by supplying:** `<DECLARATIONS>` (every file or directory that
declares objects: inventories, variable files, compose files, DNS and proxy
config), `<ID_FIELDS>` (the fields that must be unique across the fleet: a
numeric guest id, a name, an address, a published port, a group key, a
named volume or host mount path),
`<LINTERS>` (the repository's linters for the touched file types),
`<SYNTAX_CHECK>` (the parse-only check of the automation, run per entry
point), `<APPLY>` (the command a person runs to apply; this procedure never
runs it) and `<PLATFORM_PAGES>` (the library-corpus pages of the platforms
in play, which own each platform's preflight facts).

## When to apply

- "Add a container for the monitoring stack", "add this host to the
  inventory", "publish a new app behind the proxy".
- Any change to an object that shares an address space, an id space or a
  port space with objects already running.

It runs only when the owner names it. An automatic router that selects it
would start a gated, multi-step change from a passing phrase. So when you
place the page, write its description as "invoke only when the owner names
it", give it no `load_when:` phrase that a passing request would match, and
set the harness's manual-only flag on each projection that has one (Claude
Code reads `disable-model-invocation: true` in a skill's frontmatter).

## The states

Run the states in order. Each has an entry condition and a STOP condition, and
a STOP holds the change at that state until it is cleared.

| state | entry | STOP when |
|---|---|---|
| 1. INTAKE | the person has described the object | a mandatory field is MISSING; a collision exists |
| 2. PLAN | intake complete, no collision | the plan needs a destructive step; it holds until the owner approves that step on its own, or the step is dropped |
| 3. APPROVAL | plan written | the owner has not approved this plan |
| 4. IMPLEMENT | plan approved | an edit diverges from the plan |
| 5. VALIDATE | edits done | any HOLD row in the matrix below |

The person who asked runs `<APPLY>` after a GO. This procedure edits
declarations and stops.

## 1. INTAKE: fill the contract, then check collisions

Fill this contract and mark each field COMPLETE or MISSING:

```
OBJECT TYPE:     <guest | host entry | composed app | other>
IDENTITY:        <name, numeric id, group key, service name>
INTENT:          <one sentence: what it must do>
DEPENDENCIES:    <existing objects it needs>
NETWORK:         <address/prefix, gateway, bridge or network, published ports>
RESOURCES:       <cpu, memory, disk size, storage pool>
SECURITY:        <credential source (a store or vault entry, never a value), key>
COMPATIBILITY:   <one line per ID_FIELD: unique yes/no, with the evidence>
ROLLBACK:        <filled in at PLAN>
```

**MISSING means ask.** Do not fill a field with a default the person did not
give (`contract-posture` §1). When a value can be proposed, propose it with
its evidence ("id 214 is free: the highest declared is 213, and the
platform's free-id check confirms it") and let the person confirm it.

**Collision checks run over every declaration, and compare values, not
substrings.** For each `<ID_FIELDS>` entry, parse every file in
`<DECLARATIONS>` and collect the existing values, then compare the proposed
value for equality. A text search is a first look only: searching for the
id `11` also matches `110`, and searching for an address ending in `.1`
also matches the one ending in `.12`. Check that the declarations searched are all of them;
a check scoped to one stage's directory misses the same address declared in
another. Also check:

- **network compatibility**: the address is inside the subnet of the bridge
  or network it joins, and the gateway is on that subnet;
- **naming conventions**: a scope-keyed file (a group's variable file) must
  match a declared scope name exactly, or it is never loaded;
- **the platform preflight**, from `<PLATFORM_PAGES>`. For a hypervisor driven
  through an automation collection, for example, it covers the free id across
  the whole cluster, the storage and its content type, the guest name format,
  the bridge, the template and the client-library import. The list and the
  facts behind it are on those pages: for one platform, the "Idioms & best
  practices" section of `library-corpus/platform/proxmox-ve.md` and the
  "Testing" section of `library-corpus/galaxy/community.proxmox.md`;
- **the connection key**: the private key the automation connects with parses
  (`ssh-keygen -y -f <private key>` prints its public half). A key that does
  not parse fails every connection later, with no clear error.

**A missing secret fails fast.** A credential the object needs stops the
change at INTAKE when the store lacks it, or when this run cannot write to
the store (for example, no encryption key is available). The object never
deploys with a default. Where the automation does not already assert each
secret before it deploys, the plan adds that assertion (`contract-posture`
§1), so a later run without the secret fails instead of deploying a default.

Output of INTAKE: the filled contract, the collision report, and PROCEED or
HOLD.

## 2. PLAN: an additive change set with a written rollback

List every file the change touches and the exact edit to each. Prefer a new
file or an appended block to an edit inside an existing one; when an existing
file must change, the edit is the smallest insertion range, in the file's own
order and style.

**Producer and consumer change together.** When the object's contract changes
a field that another declaration consumes (the provisioned login user and the
inventory's connection user; a published port and the proxy entry; an address
and the DNS record), the plan updates every consumer in the same change set,
and VALIDATE compares the two. Find consumers by searching for the field name
across `<DECLARATIONS>` and the roles that read them.

**Order is an assertion** (`contract-posture` §4). When the object needs
another to exist first (a guest before the app on it), the plan names the
order and the automation asserts it (a preflight that fails when the
dependency is absent), rather than relying on the order a person runs things
in.

Write the rollback: the exact steps that reverse each edit and, after an
apply, each created object, and confirm each step leaves every other object
as it was. A destructive step (delete, replace, re-address, resize down) is
not in the default plan. It is listed separately and needs its own approval
(`restrictive-policy`).

State the blast radius in one line: what breaks, and for whom, if this change
is wrong (`host-parity`). Include whether the change can cut the control
node's own access.

## 3. APPROVAL

Present the contract, the collision report, the change set, the rollback and
the blast radius, and ask for an explicit approval of this plan. An approval of
the idea ("yes, add it") is not an approval of the plan.

## 4. IMPLEMENT

Make exactly the planned edits. When an edit turns out to need something the
plan did not list (another file, a changed existing value), stop and go back
to PLAN. Do not delete, rename or replace existing objects, groups, keys,
routes, volumes or network definitions in this state.

## 5. VALIDATE: the GO/HOLD matrix

Run in order:

1. **Diff review**: list every changed file; flag any deletion or replacement
   as non-additive.
2. **Collision re-check**: rerun every INTAKE collision check against the
   edited tree.
3. **Lint**: run `<LINTERS>` on every touched file, including new untracked
   files (a diff-based file list misses them).
   `tool-corpus/testing/touched-file-lint-hook.md` is a ready mechanism.
4. **Syntax check**: run `<SYNTAX_CHECK>` for every entry point the change
   can affect.
5. **Producer-consumer comparison**: each changed producer field equals what
   its consumers read.
6. **Rollback readiness**: every edit has its reverse step, and each reverses
   without touching another object.
7. **Security verdict**: a change that opens a port, adds a credential or
   touches access control goes to the security agent (`agents/05-security.md`)
   for a verdict before GO.

| condition | decision |
|---|---|
| all checks pass, additive only, rollback written | GO |
| a lint or syntax failure | HOLD: fix it |
| a non-additive edit without its own approval | HOLD: get the approval or remove the edit |
| a collision found in the re-check | HOLD: resolve it |
| a producer field changed and a consumer was not | HOLD: update the consumer |
| a rollback step missing or unclear | HOLD: write it |
| a security-relevant change without the security agent's verdict | HOLD: get the verdict |
| all checks pass, but the blast radius is high | GO with a WARNING that names the risk |

A GO hands `<APPLY>` to the person, with the advice to resolve the target set
first (list the hosts the command will touch) and to apply to the new object
only. A green check mode or dry run is structural evidence, not proof that
the apply will work.

## Splitting the work

The states fit a chain of narrow roles: an intake role that only reads, an
implementer per object type that only edits declarations, and a validation
role that only runs checks. Narrow roles keep each step's context small. The
orchestrating role owns PLAN and APPROVAL. None of them runs `<APPLY>`. On a
surface that can destroy running objects, `agent-corpus/iac-change-author.md`
is the role that runs this chain.

## Reference files

- `core/method/restrictive-policy.md` (additive by default; destructive
  steps behind their own gate)
- `core/method/contract-posture.md` (§1 missing input; §3 one contract
  document; §4 step order)
- `core/method/host-parity.md` (blast radius; self-lockout)
- `core/method/secrets-posture.md` (credential sources, never values)
- `protocols/grill.md` (the plan the owner approves)
- `protocols/verify.md` (what a check proves)
- `agent-corpus/iac-change-author.md` (the role that runs this procedure)
- `agents/05-security.md` (the verdict on a security-relevant change)
- `tool-corpus/testing/touched-file-lint-hook.md` (lint that includes
  untracked files)
- `library-corpus/platform/proxmox-ve.md`,
  `library-corpus/galaxy/community.proxmox.md` (one platform's preflight
  list and facts)
