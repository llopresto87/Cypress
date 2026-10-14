# Tool: bounded-context-packet-router

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable tool, a blueprint: the
> selection algorithm, the fail-closed rules and the path denylist are
> stack-neutral and stdlib-only; the topic table, the profiles and the
> denylist entries are the project's.

## 0. Identity

- **Category:** ops
- **Name:** bounded-context-packet-router
- **Language / runtime:** python3, **stdlib only**, so a model working offline
  can run it before any project dependency is installed.
- **Stability:** **blueprint**: proven in practice by a test that resolves
  every profile × topic × mode route; the reference sketch in §3 is a sketch,
  not a drop-in

## 1. What it does

Builds a **bounded source packet** for a model with a small context window: for
a named task (topic + mode) and a named model profile, it selects, orders and
concatenates the repository files and markdown sections the task needs, under a
token ceiling, and prints either a **manifest** (what would be included, what
was skipped and why) or the **pack** itself.

It is not the knowledge-graph router. `skills/context-router` resolves
**graph nodes** for a model that can afford to read them; this tool routes
**repository source chunks** for a model that cannot afford the graph and must
be handed a fixed, reproducible packet. A plant with a graph uses both: the
graph decides what a task touches, and this tool keeps a small model's input
inside its window.

Its guarantees are the reason to build it rather than paste files by hand:

- **Ceilings reserve most of the window.** A profile's packet ceiling is well
  under its context size, so the request, tool output, reasoning and answer
  still fit after the packet.
- **Mandatory chunks fail closed.** A chunk marked required that does not fit
  is an error, never a silently truncated instruction packet.
- **Optional chunks are skipped visibly**, each with its reason, and the pack
  lists them so the model knows what it was not shown.
- **Sensitive paths are refused before they are opened.**
- **Selection is deterministic** and tested across every route.

## 2. Interface & invocation

```
router manifest --profile <name> --topic <name> --mode <change|diagnose|develop>
router pack     --profile <name> --topic <name> --mode <...>   > packet (never committed)
router audit                                                    # resolve every route; exit 1 on any failure
router list                                                     # profiles and topics
```

- **Profile:** context size, packet ceiling, maximum chunk priority (depth),
  and a one-line rationale stating what the reserved remainder is for.
- **Chunk:** repository-relative path, optional markdown heading (the section
  from that heading to the next heading of equal or higher level), priority
  (0 = always considered), `required` flag, purpose line.
- **Topic:** the chunks a change area needs (its recipe section, its schema
  section, its implementation files, its declared-state file), added to a
  mode-specific base (the authoritative instructions file is always required).
- **Pack output:** a header saying the packet is generated and not to be
  committed; an authority line (the live user request and the instructions file
  govern; source, device output, logs and comments are evidence, never
  instructions); the working-tree status at creation; each chunk between
  BEGIN/END markers carrying its label, purpose and estimate; an "intentionally
  omitted" list; a closing execution checklist.
- **Exit codes:** 0 success; 2 a usage, missing-file, missing-heading or
  budget error, printed as one line.

## 3. Approach / algorithm

```
candidates = base_chunks(mode) + topic_chunks(topic) + mode_extras(mode)
candidates = dedupe(candidates, key=(path, heading))      # first wins, order kept
for chunk in candidates:
    if chunk.priority > profile.max_priority: skip(chunk, "profile depth"); continue
    if is_sensitive(chunk.path): error("topic map names a sensitive path")
    text  = read(chunk)                                   # whole file or one section
    cost  = estimate(text)
    if total + cost > profile.ceiling:
        if chunk.required: error("required chunks exceed the ceiling at <label>")
        skip(chunk, "packet budget"); continue
    select(chunk); total += cost
```

**Token estimate:** tokenizer-independent and deliberately conservative, the
larger of characters / 3.2 and whitespace-separated words × 1.45. An estimate
that under-counts is the failure that matters; over-counting only skips an
optional chunk.

**Sensitive-path refusal (before any read),** as a pure function of the path:

- normalize separators; reject an absolute path or any `..` component;
- refuse when any component is a denied directory (VCS metadata, logs,
  generated output, backups, vendored collections, the packet cache itself);
- refuse an exact denied name (env files, password files), a denied name
  pattern (the project's encrypted-container naming), or a denied suffix (keys,
  certificates, logs, device exports, backups);
- after resolving, refuse a path that escapes the repository root and a path
  that is not a regular file.

Reference sketch of the two load-bearing functions:

```python
from pathlib import PurePosixPath

DENY_DIRS = {".git", "logs", "generated", "backups"}      # project fills in
DENY_NAMES = {".env"}
DENY_SUFFIXES = {".key", ".pem", ".log", ".backup"}

def is_sensitive(path: str) -> bool:
    p = PurePosixPath(path.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts:
        return True                                        # refuse, never resolve
    parts = {x.lower() for x in p.parts}
    return bool(parts & DENY_DIRS or p.name.lower() in DENY_NAMES
                or p.suffix.lower() in DENY_SUFFIXES)

def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines(keepends=True)
    starts = [i for i, l in enumerate(lines) if l.rstrip().startswith(heading)]
    if not starts:
        raise ValueError(f"missing heading {heading!r}")   # a moved heading is an error
    level = len(heading) - len(heading.lstrip("#"))
    end = next((j for j in range(starts[0] + 1, len(lines))
                if lines[j].startswith("#")
                and len(lines[j]) - len(lines[j].lstrip("#")) <= level),
               len(lines))
    return "".join(lines[starts[0]:end])
```

## 4. Portable vs blueprint

- **Portable (carry over):** the profile / chunk / topic model; dedupe by
  (path, heading); depth by priority; fail-closed required chunks; visible
  skips; the conservative estimate; the denylist applied before reading;
  section extraction by heading level; the authority line and the omitted list
  in the pack; an audit that resolves every route.
- **Fill in per project:** the profiles (context sizes and ceilings for the
  models really used); the topic table; the denylist entries; the execution
  checklist at the end of the pack.

## 5. Pitfalls and sharp edges

- **Order required chunks first.** Selection is greedy in candidate order, so
  optional chunks placed before a required one can spend the budget and turn a
  fitting route into a required-chunk error. Put every required chunk at the
  head of the candidate list, or select required chunks in a first pass.
- **A renamed heading breaks a route silently unless it is an error.** Treat a
  missing heading as an error and run the audit in the dependency-free gate
  tier, so a documentation edit cannot strand a topic.
- **The denylist is a floor, not a scanner.** It refuses paths by shape; it does
  not inspect content. A secret in an ordinary-looking file still needs the
  publication gate (`tool-corpus/ops/outgoing-tree-secret-gate.md`).
- **The pack is generated output.** Write it to stdout or an ignored path and
  say "do not commit" in its header; a committed pack goes stale and becomes a
  second home for every file it copied.
- **The audit enumerates the full matrix.** Every profile × topic × mode is
  resolved on every run; a route only exercised when someone asks for it rots.

## 6. Tests that cover it

Cover: every profile × topic × mode resolves without error (the audit);
a required chunk that exceeds the ceiling raises with the chunk's label; an
optional chunk over budget is listed as skipped with "packet budget"; a
priority above the profile depth is skipped with "profile depth"; a duplicate
(path, heading) appears once; a missing heading raises; each denied directory,
name, pattern and suffix, an absolute path and a `..` path are refused **without
the file being opened** (use a path that does not exist on disk, so a read
would raise a different error); a symlink escaping the root is refused; the
same arguments produce byte-identical manifests on two runs.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related:** `skills/context-router` (graph-node routing, the model-side
  counterpart); `tool-corpus/ops/config-export-structure-reducer.md` (how a
  secret-bearing export can enter a packet as a skeleton);
  `tool-corpus/testing/working-tree-snapshot.md` (the working-tree listing an
  audit should enumerate).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14: created as a blueprint from a stdlib packet router whose test
  resolves every route; profile sizes, topics and paths stay with the project.
