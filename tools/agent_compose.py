#!/usr/bin/env python3
"""The one composer of an agent's always-loaded nodes (SPEC-0001
ROLE_AGENT_COMPOSES_ITS_ALWAYS_LOADED_NODES).

A charter whose frontmatter names `always_loads:` is rendered by a host as the
charter followed, in that order, by each named node's body under
"## Always loaded: <id>", its frontmatter stripped, so the role's system prompt
carries those nodes and is the same bytes on every spawn (a cache-friendly
prefix). Claude Code's projection and opencode's both call `sections`, so the
two hosts cannot diverge in which nodes ride along or how a node is cut.
The nodes stay the only home: a composed file is generated, and `--check`
compares it with a fresh composition.

Library module, no CLI; install.sh puts this directory on the path when it
renders. Dependency-free like every tool here.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "templates", "knowledge-graph"))
from frontmatter import parse, FrontmatterError  # noqa: E402


class ComposeError(Exception):
    """A charter that cannot be composed; the message names it and why."""


def node_bodies(graph):
    """id -> body for every node under docs/graph/{method,skills,protocols}/."""
    home = {}
    for sub in ("method", "skills", "protocols"):
        d = os.path.join(graph, sub)
        for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            f = os.path.join(d, name)
            if not (name.endswith(".md") and os.path.isfile(f)):
                continue
            try:
                meta, body = parse(open(f, encoding="utf-8").read(), f)
            except (FrontmatterError, UnicodeDecodeError):
                continue
            if isinstance(meta.get("id"), str):
                home.setdefault(meta["id"], body)
    return home


def composed(body, wanted):
    """A node body as a role composes it: the text before its first `## `
    section, then each section except `## Neighbours` and one whose next line
    is `<!-- reference-only -->`; with `wanted`, only the `## <n>.` sections
    it names. Returns (text, the wanted numbers no section carries)."""
    chunks = re.split(r"(?m)^(?=## )", body.strip("\n"))
    pre = [] if chunks[0].startswith("## ") else [chunks.pop(0)]
    keep, seen = [], set()
    for c in chunks:
        num = re.match(r"## (\d+)\.", c)
        seen.add(num.group(1) if num else None)
        lines = c.split("\n")
        if lines[0].strip() == "## Neighbours" or (len(lines) > 1 and lines[1].strip() == "<!-- reference-only -->"):
            # the heading and its list go; text after the list (a plant's own line) stays
            n = 1
            while n < len(lines) and (not lines[n].strip() or lines[n].startswith(("- ", "  "))
                                      or lines[n].strip() == "<!-- reference-only -->"):
                n += 1
            rest = "\n".join(lines[n:])
            if rest.strip():
                keep.append("\n" + rest)
            continue
        if wanted and not (num and num.group(1) in wanted):
            continue
        keep.append(c)
    text = "".join(pre + keep).strip("\n")
    return text, [n for n in wanted if n not in seen]


def sections(meta, name, home):
    """The "## Always loaded: <id>" sections a charter's `always_loads:` names,
    in order; [] for a charter that names none. `name` is the charter's file
    name, for the error. Raises ComposeError for an id no node carries or a
    selector no section answers."""
    ids = meta.get("always_loads") or []
    if not isinstance(ids, list) or not ids:
        return []
    out = []
    for entry in ids:
        i, _, sel = str(entry).partition("#")
        if i not in home:
            raise ComposeError(
                f"docs/graph/agents/{name}: always_loads names {i!r}, which no node in "
                f"docs/graph/{{method,skills,protocols}}/ carries.")
        part, missing = composed(home[i], [n.strip() for n in sel.split(",") if n.strip()])
        if missing:
            raise ComposeError(
                f"docs/graph/agents/{name}: always_loads entry {entry!r}: {i} has no "
                f"section {', '.join(missing)}.")
        head = f"## Always loaded: {i}" + (f" (sections {', '.join(sel.split(','))})" if sel else "")
        out.append(head + "\n\n" + part)
    return out
