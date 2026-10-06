# Tool: live-state-to-declared-config-probe

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the read-only probe
> discipline, the separate generated root, the guard defaults and the promotion
> step are portable; the probe itself is written in whatever
> configuration-management or inventory tool the adopting project already uses.

## 0. Identity

- **Category:** ops
- **Name:** live-state-to-declared-config-probe
- **Language / runtime:** any. The project's configuration-management tool
  (for its connection handling and fact gathering) and a serializer for the
  declaration format are the whole requirement.
- **Stability:** **blueprint**. No portable implementation ships here,
  because the probe runs through the project's own remote-execution tool and
  writes the project's own declaration format. Everything around those two
  (the guard defaults, the output layout, the status manifest, the
  promotion rule) is portable and is the value of the page.

## 1. What it does

Brings an existing fleet ("brownfield") under declarative configuration
without guessing its current state. It probes live hosts **read-only**,
renders what it found as **proposed** declarative configuration into a
separate generated directory, and stops. An operator reviews the proposal,
promotes the parts that should be declared into the real configuration tree,
and commits them.

It exists because the two obvious alternatives both go wrong. Writing the
declared configuration by hand from memory misses what is really on the
hosts, so the first converge run "fixes" things that were deliberate. Letting
a probe write straight into the declared tree turns whatever was on the host,
mistakes and secrets included, into the declared truth with nobody reading
it.

**When not to use it.** It is not a drift detector for a fleet that is
already declared: use the configuration tool's check or diff mode for that.
It is not a backup: the generated root holds a selection, by design. And it
is not for hosts the project may not read: the probe still logs in.

## 2. Interface & invocation

```sh
live-state-probe \
  --targets <host list or inventory> [--limit <subset>] \
  --out <generated root, outside the declared tree> \
  [--mode facts-only|full-scan] [--allow-escalation] \
  [--max-files <n per host>] [--max-file-bytes <n>]
```

- **Inputs:**
  - `--targets`: the hosts to probe, through the project's own inventory.
    Required.
  - `--out`: the generated root. Required; refused when it resolves inside
    the declared tree or inside a directory the configuration tool searches
    (§3, "The generated root").
  - `--mode`: `facts-only` (the default) gathers system facts and the output
    of a fixed list of read-only commands. `full-scan` also fetches
    configuration files, under the caps and the deny list. §3 gives the
    default command list and the default file search.
  - `--allow-escalation`: run the reads with privilege escalation. Off unless
    given on this run.
  - `--max-files` and `--max-file-bytes`: per-host caps for `full-scan`. Both
    have finite defaults (for example 200 files and 1 MiB) and both are
    enforced.
- **Outputs**, all under `--out`:
  - one proposal file per host, in the declaration format, in a **host-scoped**
    layout (`<out>/hosts/<host>.<ext>`);
  - for `full-scan`, the fetched files under `<out>/files/<host>/<original
    path>`;
  - one manifest (`<out>/manifest.json`): per host, per probe step, the status
    (`ok`, `failed` with the error line, `skipped` with the reason), the mode,
    whether escalation was used, the caps, and every file refused by the deny
    list or a cap.
- **Exit codes:** 0 every host probed and every step `ok` or `skipped`; 1 at
  least one step `failed` (the proposals are still written, and the manifest
  says which parts are missing); 2 usage error or refusal (`--out` inside the
  declared tree, missing required input).
- **Preconditions:** read access to the hosts through the project's normal
  connection; a generated root that is ignored by version control.

## 3. Approach / algorithm

### Read-only, by construction

Every probe step is a read: fact gathering, a fixed list of commands with no
side effects, a file search and a fetch. Each command step is marked as not
changing anything, so the run report shows zero changes. A probe step that
needs a write is not a probe step.

The defaults below leave out a `*key*` search pattern (see "Guards that are
enforced, not declared" below). They are a starting point for a Linux fleet. A plant
changes them per host family, and each change is a reviewed edit.

- **Fact subsets:** network, hardware and virtual. The full fact set is
  larger and mostly noise for a declaration.
- **Fixed command list:** `ip -br addr` (addresses per interface),
  `lsblk -J` (block devices, as JSON), `hostnamectl` (host identity, OS and
  kernel). Each runs without escalation unless the run asks for it.
- **`full-scan` file search:** root `/etc`, which also holds the container
  engines' configuration directories (`/etc/docker`, `/etc/containers`);
  depth 3 below the root; files only; patterns `*.conf`, `*.json`, `*.yaml`,
  `*.yml`, `*.service` and `*daemon*`. The default leaves out `*.env`:
  those files hold secrets by convention. A
  plant that needs them adds the pattern, and a person checks every fetched
  `*.env` file for secrets before any value from it is promoted.

### Least access by default

- **`facts-only` is the default mode.** File fetching is the step that can
  copy secrets off a host, so it is opt-in.
- **Escalation is off unless this run asks for it.** The flag sets it for one
  run; no default file turns it on. A probe that documents escalation as
  opt-in while its role default is `true`, and whose wrapper only ever sets
  it to `true`, escalates on every run. Test the default (§6).

### Guards that are enforced, not declared

A guard that is defined in a defaults file and read by nothing is worse than
none, because a reviewer sees it and trusts it. An exclude-path list, a
per-host file cap and a sensitive-name pattern that are declared and used
by nothing protect nothing. Each guard below must be applied in the step it protects
and covered by a test:

1. **Deny list, applied before the fetch.** Never fetch key material or
   credential stores: private key directories, the SSH host keys and the
   user key directories, TLS private key directories, password and shadow
   databases, and any file whose name matches the sensitive-name pattern.
   Search patterns such as `*key*` must not override the deny list. Under
   `/etc` that pattern selects the SSH host private keys.
2. **Pseudo filesystems and runtime state excluded:** `/proc`, `/sys`,
   `/dev`, `/run`, container and VM storage.
3. **Caps enforced:** at most `--max-files` per host and `--max-file-bytes`
   per file. Every file refused by a cap or by the deny list is listed in the
   manifest, so a missing file is never a silent absence.
4. **Values redacted in the proposal.** A key whose name matches the
   sensitive-name pattern (`pass`, `secret`, `token`, `private`, `key`) is
   written as a placeholder that names the secret store entry to create,
   never with the value.

The sensitive-name pattern is matched without regard to case, as a
substring. For redaction it is matched against the key name. For the deny
list it is matched against the file's base name, not against the directory
path. The pattern has `key`, not `ssh`. `key` makes
the name rule catch key files wherever they are, so the deny list does not
depend on a search pattern. `ssh` is dropped because the path entries in
rule 1 already cover the SSH key directories, and `ssh` as a file-name
substring would also refuse `sshd_config`, which is configuration. A
substring match also redacts harmless keys such as `keyboard_layout`. That
error is the safe one: the reviewer sees a placeholder and reads the value
on the host.

### The generated root

- It is **outside every directory the configuration tool searches**. If
  `--out` resolves inside the declared tree, the tool refuses. A proposal the
  configuration tool can load is no longer a proposal.
- It is ignored by version control. Probe output stays local until a person
  promotes part of it.
- **Host data goes to a host-scoped layout.** A host's facts written to the
  group-scoped variables directory, under the host's name, go wrong: with no
  group of that name the file is never loaded
  (`tool-corpus/ops/orphaned-scoped-config-auditor.md`), and with one it is
  loaded for the wrong scope. Write per host; deciding which values are
  shared by a group is a promotion decision.
- Each run replaces the generated root for the hosts it probed and leaves the
  rest alone, so a partial re-run is safe.

### Status, not empty strings

A probe step that fails is recorded as `failed` with its error line in the
manifest, and its field in the proposal is absent, not empty. A probe that runs
each step with errors ignored renders a failed command as an empty string. An empty value then reads as "this host has no addresses", which is
a false fact a reviewer may promote.

### Render with a serializer

Build the proposal as a data structure and write it with the format's
serializer, never with a text template. A hand template leaves values
unquoted, so a version string like `22.10` comes back as the number `22.1`,
and an empty list renders as a list holding an empty list. A serializer
quotes and nests correctly by construction.

### Promotion

1. Read the manifest first: every `failed` step and every refused file is a
   gap in the proposal.
2. Compare each host's proposal with what is declared today, using the
   configuration tool's own diff or check mode where it has one.
3. By owner decision, move the values that should be declared into the
   declared tree, at the scope where they belong (per host, or per group
   when several hosts share them). Move secrets into the secret store, never
   into the tree. When the configuration tool converges live systems, a
   promoted value may first land as an unmanaged audit baseline and become
   managed one at a time (`skills/adopt-existing/SKILL.md`, the `plans/`
   row).
4. Run the configuration tool in check mode against the promoted tree. It
   must report no change on the probed hosts; a change means the
   declaration does not yet match reality.
5. Commit the promoted files with a message naming the probe run. The
   generated root is not committed.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** read-only steps; `facts-only` and no
  escalation by default; the deny list before the fetch, the caps, the
  redaction; the generated root outside the search path, with a refusal; the
  host-scoped layout; the status manifest; serializer rendering; the
  five-step promotion with the check-mode proof.
- **Write per project:** the probe itself in the project's configuration
  tool (fact gathering, the fixed command list, the file search and fetch),
  the mapping from facts to the declaration format, and the deny list
  additions for the project's own secret locations.
- **Adopting note:** most configuration tools fetch files through a module
  that copies to the control machine. Apply the deny list and the caps to the
  **search result** before that module runs; a filter on the fetch's
  condition line is easy to get subtly wrong, and a fetched secret is already
  on disk.

## 5. Pitfalls and sharp edges

- **Probe output contains secrets even with a deny list.** Configuration
  files embed passwords inline. Keep the generated root out of version
  control, out of shared drives and out of chat, and delete it after
  promotion.
- **A probe is still a login.** It appears in the hosts' audit logs, and
  escalation appears there too. Agree the run with the hosts' owners when
  that matters.
- **What is on a host is not what should be declared.** The proposal shows
  current state, including mistakes and leftovers. Promotion is a review,
  not a copy.
- **Facts drift between probe and promotion.** Promote soon after the probe,
  or probe again; the check-mode run in step 4 shows drift that appeared in
  between.
- **A proposal for an unreachable host is empty, not absent.** Read the
  manifest for hosts with no successful step before promoting anything for
  them.

## 6. Tests that cover it

Cover with a fake host (a local container or a temporary directory standing
in for the remote filesystem): the default run uses `facts-only` and no
escalation, asserted from the run's own record; `--allow-escalation` turns
escalation on for that run only; a denied path (an SSH host private key, a
file named like a secret) is never fetched even when the search pattern
selects it, and is listed as refused in the manifest; the file cap and the
size cap stop the fetch and list the rest as refused; a failing command is
`failed` in the manifest and absent from the proposal; a value whose key
looks sensitive is redacted; a version-like string round-trips as a string;
`--out` inside the declared tree refuses with exit 2; the proposal is in the
host-scoped layout; the run reports zero changes on the host.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/orphaned-scoped-config-auditor.md`
  (catches a proposal written under the wrong scope, and orphaned files
  after promotion); `tool-corpus/ops/structured-secret-field-detector.md`
  (a gate that a promoted file holds no credential-shaped field);
  `tool-corpus/ops/env-secret-rotation.md` (for a secret that the probe did
  copy off a host).
- **Related skills:** `skills/adopt-existing/SKILL.md` (the same promotion
  rule from the adoption side: an unmanaged audit baseline, promoted to
  managed one at a time by owner decision).
- **Library notes:** `library-corpus/pypi/ansible-core.md` (one
  configuration tool's layout for per-group and per-host variables).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-05: created as a
  blueprint. Escalation and full scan are opt-in, not default; the declared
  guards are enforced; host data goes to a host-scoped layout; failed probes
  are recorded, not rendered empty; rendering uses a serializer.
- 2026-10-05: review fixes. The default fact subsets, command list and
  `full-scan` search are stated; the sensitive-name pattern says what it
  matches and why it holds `key`, not `ssh`; promotion names the owner
  decision and links the adoption skill.
