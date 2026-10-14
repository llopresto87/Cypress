---
stack:
  - library-corpus/galaxy/community.routeros
---
# Tool: config-export-structure-reducer

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable tool, a blueprint keyed
> to the network-device stack its `stack:` entry names: the reduce-in-memory
> contract and the sentinel test are stack-neutral; the line grammar of the
> export is the device family's.

## 0. Identity

- **Category:** ops
- **Name:** config-export-structure-reducer
- **Language / runtime:** python3, **stdlib** for the reducer; fetching the
  export from a live device needs an SSH client (a library or the system
  client), which is the only dependency.
- **Stability:** **blueprint**: proven in practice by a sentinel test over the
  reducer; the parser is per device family, so the page is stack-keyed

## 1. What it does

Reduces a **secret-bearing configuration export** of a network device (the
text a device prints as its full running configuration) to its **skeleton**:
the menu or section paths present and, per path, how many of each command verb
appear. Arguments, comments, names, addresses and values never reach the
output.

It exists to answer a coverage question safely: *which configuration surfaces
does the device carry that the declared configuration does not model yet?* The
raw export answers it, but the raw export holds credentials, keys, addresses
and identities, and must not enter a model's context or a log. The skeleton
answers the coverage question and nothing else.

It is **coverage discovery, not a backup**: the output cannot restore anything
and must never be treated as a configuration snapshot.

## 2. Interface & invocation

```
reducer < export.txt                       # export on stdin
reducer --ssh-host <host> [--ssh-port N] [--timeout S]   # pull in-process
```

- **Input:** the export on stdin, or fetched in-process over SSH with
  credentials taken from the environment (never arguments, which land in the
  process table and shell history). Strict host-key checking stays on.
- **Never writes the export to disk:** no temporary file, no cache, no log of
  the raw text.
- **Output (JSON):** schema version; `sections` as a sorted list of
  `{path, commands: {verb: count}, total}`; section count; command count; a
  count of lines that were neither a path nor a known verb; input line and
  character counts (so a truncated fetch is visible).
- **On failure:** a JSON object with `status: error` and a **coarse error
  code** (host key mismatch, authentication failed, timeout, connection
  refused, transport failure, a dependency missing). Never echo the device's
  error text: it can quote configuration.

## 3. Approach / algorithm

The usual export grammar is a path line (`/section subsection`) that sets the
current section, optionally followed inline by a verb, and verb lines (`add`,
`set`, `remove`, `enable`, `disable`) that belong to the current section:

```
current = ""
for line in export:
    line = strip(line); skip blank and comment lines
    if line starts with "/":
        path, inline_verb = split_path(line)   # path tokens until the first verb
        if path: current = path                 # or the first non-path token
        if current and inline_verb: count[current][inline_verb] += 1
    elif current and first_word(line) in VERBS:
        count[current][first_word(line)] += 1
    elif current:
        unknown += 1                            # counted, never echoed
```

- **Ask the device to hide sensitive values at the source** when its export
  command can, and still reduce: hiding at source is defence in depth, the
  reduction is the guarantee. Some firmware rejects the explicit "hide" option
  in a non-interactive session while hiding by default; retry once without the
  option only when that default is documented for the version in use.
- **Only verbs and path tokens survive**, and path tokens only when they match
  a plain-identifier shape. Everything after the verb is discarded unread.

## 4. Portable vs blueprint

- **Portable (carry over):** stdin-or-in-process input, nothing on disk;
  the skeleton output shape; coarse error codes; unknown lines counted, never
  shown; input size reported; the sentinel test (§6).
- **Fill in per device family (the stack key):** the path and verb grammar;
  the export command and its hide-sensitive option; the identifier shape a path
  token must match; how the SSH session is opened.

## 5. Pitfalls and sharp edges

- **A path-token shape check is not an allow-list.** A grammar that accepts
  any identifier-shaped token as a path component will copy a bare value that
  happens to look like an identifier (a name without `=`) into the path. Where
  the device family's section names are enumerable, check path tokens against
  that vocabulary instead, and treat anything else as the end of the path.
- **Exit status must carry the error.** Reporting a fetch failure as a JSON
  `status: error` with exit 0 lets a wrapper read an empty skeleton as "nothing
  unmodeled". Exit non-zero on error, or have every caller check `status`.
- **A short export looks like a small device.** Report input line and
  character counts, and have the caller compare them with a floor; a cut
  connection otherwise produces a clean, wrong skeleton.
- **Do not print the device's stderr.** Map it to a code; a parse error message
  can quote the offending configuration line.

## 6. Tests that cover it

The **sentinel test** is the contract: build an export containing distinctive
sentinel strings in every value position (a name, a comment, an address-shaped
value, an identity), reduce it, serialize the result, and assert **no sentinel
appears** while the expected section paths and verb counts do. Add one sentinel
in a bare-token position (no `=`) to prove the pitfall above is closed. Also
cover: an inline verb on a path line is counted under that path; an unknown
line is counted and not echoed; an empty input yields zero sections with input
counts of zero; each transport failure maps to its coarse code with no device
text in the output.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Library:** `library-corpus/galaxy/community.routeros.md` (the device
  family this page is keyed to).
- **Related tools:** `tool-corpus/ops/live-state-to-declared-config-probe.md`
  (the next step once a surface is found: bring it into declared config);
  `tool-corpus/ops/structured-secret-field-detector.md` (asserts keys absent,
  where this one reduces); `tool-corpus/ops/bounded-context-packet-router.md`
  (where a skeleton can be routed to a model).
- **Doctrine:** `core/method/secrets-posture.md` (a configuration dump is
  secret-bearing by field).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14: created as a stack-keyed blueprint from a reducer proven by a
  sentinel test; the device grammar and fetch command stay per family.
