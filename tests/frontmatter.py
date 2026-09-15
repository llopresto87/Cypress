#!/usr/bin/env python3
"""The one reader for node frontmatter. Promoted, not written.

Every machinery node, corpus page and template begins with a `---` block of
YAML-ish settings. Seven different programs each grew their own reader for it —
agent-lint, graph-lint, seed-lint, roster-justification, status-register,
growth-audit, status-migrate — and they agreed on the ordinary cases and
disagreed on the rest. A description spilling onto a second line was REJECTED by
two of them and SILENTLY TRUNCATED by three, losing the continuation with no
error, no warning and no finding. Nobody decided that; it is what the same small
job written seven times produces.

This is `agent-lint.py`'s reader, promoted verbatim, plus one addition: a single
level of nesting, because `docs/graph/index.md` carries a `plant:` block of
owner-stated facts and the strict readers refused it. Measured before promoting:
of 108 frontmatter blocks in the seed, the strict reader accepted 107 and
rejected exactly that one — so nothing in the tree relied on a permissive reader
letting it through.

Deliberately NOT a YAML library. It parses the subset the frontmatter actually
uses — measured: 941 list items, 621 `key: scalar`, 291 keys introducing a
block, 20 inline lists, 7 quoted scalars, 4 nested keys, 4 comments — and raises
on everything else. No anchors, no `|`/`>` folding, no multiple documents, no
typed values. A shape it does not recognise is an ERROR rather than a guess,
which is the whole point: the truncation it replaces was a guess.

Dependency-free, like every other tool here: a plant installs into somebody
else's repository and the seed does not add a pip dependency to read its own
headers.
"""

import re
from pathlib import Path

_INT = re.compile(r"-?\d+")


class FrontmatterError(Exception):
    """A frontmatter block that cannot be read as written."""


def scalar(v: str):
    """A bare scalar, an inline list, or a quoted string — nothing else.

    Integer coercion is here because the promoted reader had it and things
    depend on it: `max_spawn_depth: 2` is checked as an int in [1,3], and
    without coercion that check fails on the STRING '2'. Caught by the roster
    lint within a minute of consolidating, which is the argument for doing this
    consolidation against a running gate rather than on paper.

    The trailing `  # comment` strip is likewise inherited, and likewise only on
    unquoted non-list values — a `#` inside a quoted string is content.
    """
    v = v.strip()
    if v[:1] not in "\"'[" and "  #" in v:
        v = v.split("  #", 1)[0].strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [scalar(x) for x in inner.split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if _INT.fullmatch(v):
        return int(v)
    return v


def parse(text: str, where="<frontmatter>"):
    """(meta, body). Raises FrontmatterError on any shape it does not know.

    `where` names the file in errors; callers pass a Path or a name.
    """
    name = Path(where).name if not isinstance(where, str) or "/" in str(where) else str(where)
    if not text.startswith("---\n"):
        raise FrontmatterError(f"{name}: missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise FrontmatterError(f"{name}: unterminated frontmatter")
    raw, body = text[4:end], text[end + 5:]

    meta: dict = {}
    current = None          # a key awaiting its block list
    nest = None             # a key awaiting its nested mapping
    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            item = line.strip()
            if item.startswith("- "):
                if current is None:
                    raise FrontmatterError(
                        f"{name}:{lineno}: list item before any key")
                meta.setdefault(current, []).append(scalar(item[2:]))
                continue
            # one level of nesting: `plant:` and its owner-stated facts. The
            # key was opened as a list because a block list is the common case;
            # the first indented `key: value` is what decides it is a mapping.
            if nest is not None and ":" in item:
                if not isinstance(meta.get(nest), dict):
                    if meta.get(nest):
                        raise FrontmatterError(
                            f"{name}:{lineno}: {nest!r} already holds list items; "
                            f"a key cannot be both a list and a mapping")
                    meta[nest] = {}
                k, _, v = item.partition(":")
                meta[nest][k.strip()] = scalar(v)
                current = None
                continue
            raise FrontmatterError(
                f"{name}:{lineno}: expected '- item' or a nested 'key: value', "
                f"got {line!r}. A continuation line is not supported — put the "
                f"value on one line. (Three readers used to drop it silently.)")
        if ":" not in line:
            raise FrontmatterError(
                f"{name}:{lineno}: expected 'key: value', got {line!r}")
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value:
            meta[key] = scalar(value)
            current = nest = None
        else:
            # a key with no value introduces EITHER a block list or a nested
            # mapping; which one is decided by the first indented line.
            meta[key] = []
            current = key
            nest = key
    return meta, body


def parse_file(path):
    p = Path(path)
    return parse(p.read_text(encoding="utf-8", errors="replace"), p)
