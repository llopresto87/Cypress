# Tool: structured-secret-field-detector

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool — the recursive walk and the
> exact-key rule are portable; the key list and the subtree it starts from are
> the two things each project fills in.

## 0. Identity

- **Category:** ops
- **Name:** structured-secret-field-detector
- **Language / runtime:** any. The reference walk is python3 **stdlib** over an
  already-parsed document; only reading a non-JSON serialization needs a parser
  for that format.
- **Stability:** **portable at the algorithm level**, pattern-level in scope —
  the traversal, the exact-key match, and the failure semantics are stack-neutral
  and adoptable as written; the **key list and the entry subtree are
  project-supplied by definition**, because a detector with a universal key list
  would be the generic scanner it is designed to complement

## 1. What it does

Recurses into a **specific, known substructure** of a seed, fixture, or
configuration artifact and asserts that a **fixed, named set of
credential-shaped keys is absent by exact key name** anywhere beneath it.

It **complements** a generic pattern/entropy secret scanner — it does not
replace one, and a project that has this and not the generic scanner has made a
mistake.

It exists because generic scanners miss credential material that is well-formed
**data** rather than a string that merely looks like a secret. A password hash, a
salt, a derived verifier, a key-derivation parameter block, a wrapped key: these
are structured fields with ordinary-looking values, and they do not trip an
entropy heuristic or a provider-token regex. The failure mode is specific and
quiet — a scanner reports "no leaks found" over a large artifact while a password
verifier sits inside it as a named field, in plain view of anyone who opens the
file.

The narrow scope is the point. It answers one question — *is any of these exact
keys anywhere under this node?* — and answers it completely.

## 2. Interface & invocation

```sh
structured-secret-field-detector \
  --artifact <file> \
  --under <path to the subtree that must be clean> \
  --forbid <key> [--forbid <key> ...]
```

- **Inputs:** the artifact; the **entry path** naming the subtree to search
  (everything beneath it is in scope, at any depth); the forbidden key set.
- **Outputs:** one line per hit — the **full path to the offending key** and
  nothing about its value beyond the fact that it is present. A detector that
  prints the value to prove the finding has published the secret it found.
- **Exit codes:** non-zero on any hit; non-zero when the entry path does not
  exist (see §5 — a missing subtree is a failure, not a pass); zero only when the
  subtree was found and contained no forbidden key.
- **Preconditions:** the artifact parses; the entry path is a real location in
  the document at the time of the run.

## 3. Approach / algorithm

A depth-first walk from the entry node, comparing **each mapping key** to the
forbidden set by **exact equality**, and recursing through every mapping and
every sequence beneath it.

**Exact key name, never substring.** This is what keeps the detector usable. A
substring match on a short credential word flags every legitimate field whose
name happens to contain it, and the resulting noise gets the check disabled or
its list truncated — the two ways a security check dies. Exact matching also
means the same word appearing as a **different** field elsewhere in the document
is correctly not flagged; the entry path plus exact names is the whole precision
mechanism.

```python
"""structured-secret-field-detector — assert that a fixed set of
credential-shaped keys is absent, by EXACT key name, anywhere under one node.

Complements a generic pattern/entropy scanner; it does not replace one.
"""
from __future__ import annotations


def walk_keys(node, path=""):
    """Yield (dotted-path, key, value) for every mapping key beneath `node`."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            yield here, str(key), value
            yield from walk_keys(value, here)
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            yield from walk_keys(value, f"{path}[{i}]")


def resolve(doc, entry: str):
    """Follow a dotted entry path. Returns a sentinel, never a silent None."""
    node = doc
    for part in entry.split("."):
        if not isinstance(node, dict) or part not in node:
            return KeyError(entry)          # returned, so callers must handle it
        node = node[part]
    return node


def find_forbidden(doc, entry: str, forbidden: set[str]) -> list[str]:
    """Paths of every EXACT forbidden key beneath `entry`. Raises if the entry
    subtree is missing: a subtree that is not there was not searched, and an
    unsearched subtree must never report clean."""
    node = resolve(doc, entry)
    if isinstance(node, KeyError):
        raise node
    return [path for path, key, _ in walk_keys(node, entry) if key in forbidden]
```

The caller supplies `doc` already parsed — from stdlib JSON, from the project's
existing parser, or from whatever produced the artifact — which keeps the
detector itself dependency-free and equally usable over JSON, over a YAML
document, and over an in-memory structure a test just built.

## 4. Portable vs blueprint

- **Portable (use as-is):** the recursive walk through mappings **and**
  sequences; the exact-key comparison; path-only reporting; the
  missing-entry-is-a-failure rule; taking a parsed document rather than a file
  format.
- **Project-supplied (by design):** the forbidden key list, and the entry path.
  These are the domain knowledge — the whole reason this check can see what a
  generic scanner cannot — and they cannot be shipped.
- **Say this out loud in the adopting project:** the **general** form of this
  check is a **custom rule added to the generic scanner**. If the scanner in use
  supports project rules, put the key list there and get it applied everywhere,
  on every artifact, by the tool already wired into the pipeline. Build this as a
  standalone detector when the scanner cannot express "this exact key, anywhere
  under this node" — or when the artifact is produced by a build step the scanner
  never sees.

## 5. Pitfalls and sharp edges

- **It is narrow, and the narrowness must be declared where the result is
  read.** A green result means *these named keys are not under that node*. It
  does not mean the artifact is free of secrets, and it does not mean a
  credential-shaped field under a **different** name or a **different** subtree
  would have been caught. Write that sentence into the check's own output.
- **A missing entry path must fail, not pass.** When the artifact is
  restructured and the node moves or is renamed, a detector that treats "nothing
  found at that path" as "nothing forbidden found" goes permanently green on the
  day the artifact changes shape — which is exactly the day it most needs to run.
- **Key lists go stale silently.** A new credential-shaped field is not covered
  until someone adds its name. Pair the list with a review trigger on the schema
  or generator that produces the artifact, and keep the list next to that
  generator rather than in a distant configuration file.
- **Never print the value.** The finding is the path. A detector that quotes the
  offending field to make the report convincing has copied the secret into logs,
  into a CI artifact, and into whatever aggregates them.
- **Do not let it substitute for the generic scanner.** The two see disjoint
  classes: the generic scanner catches things that look like secrets under
  unpredictable names; this catches things that do not look like secrets under
  predictable names. Removing either leaves a whole class uncovered.
- **Sequences are part of the walk.** A forbidden key nested inside a list of
  objects is the common real-world placement, and a walk that recurses only
  through mappings misses it entirely while appearing to work.

## 6. Tests that cover it

Cover: a forbidden key nested several levels beneath the entry node is found and
reported with its full path; the same key placed **outside** the entry subtree is
**not** reported; a forbidden key inside a list of objects is found; a key whose
name merely **contains** a forbidden word is not reported (the exact-match
regression); the value is absent from every line of output, including on the
failure path; a missing entry path exits non-zero rather than reporting clean; an
artifact with none of the keys exits zero.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/declared-variable-existence-auditor.md`
  (names in a live store, the outward direction of the same concern);
  `tool-corpus/ops/env-secret-rotation.md` (the values this must never print);
  `tool-corpus/ops/layered-config-merge-verifier.md` (the same "walk the parsed
  document, report by path" traversal, applied to resolved configuration).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-09-13 — created from harvested, generalized capability, by docs-librarian.
