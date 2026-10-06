# Tool: orphaned-scoped-config-auditor

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A portable tool: the script below runs as-is, and a
> plant supplies the scope list from its own resolver and the directory to
> audit.

## 0. Identity

- **Category:** ops
- **Name:** orphaned-scoped-config-auditor
- **Language / runtime:** python3, **stdlib only** (`json`, `fnmatch`,
  `difflib`, `argparse`)
- **Stability:** **portable**. The scope-list reader, the stem rule, the
  exclusions, the refusals and the fail/warn toggle are complete. A plant
  supplies two inputs and, where its consumer differs from the defaults, the
  extensions it loads.

## 1. What it does

Many configuration systems load a file **by its name**: the file named after a
scope (a host group, an environment, a workspace, a profile) is read when that
scope exists. When no scope of that name is declared, the file is **never
loaded**, and nothing says so. Edits to it have no effect. A typo in a file
name, a scope that was renamed or removed, and a file copied from another
repository all produce such orphans. They look like configuration and they do
nothing.

This tool lists the entries in one scope-keyed directory, takes the list of
declared scopes, and reports every entry whose name matches no scope. It
suggests the nearest scope name when there is one, so a typo is fixed in one
step.

Examples of scope-keyed directories: a configuration-management tool's
per-group variable directory next to its inventory; per-environment overlay
directories; per-workspace variable files in an infrastructure-as-code tool;
per-profile property files in an application framework.

**Boundary with its neighbours.** `declared-variable-existence-auditor` asks a
live store whether declared **names exist in the store**.
`declared-consumer-link-generator` checks that each **consumer's links** match
one declaration. This tool asks whether each **file on disk** has a declared
scope to be loaded for. The three point the same check (declaration versus
reality) at three different places.

**When not to use it.** It does not check what is *inside* a file, and it does
not prove that a matched file is loaded (§5). It audits one directory per run;
run it once per directory.

## 2. Interface & invocation

```sh
python3 orphaned-scope-config.py --config-dir <dir> --scopes <file|-> \
  [--reserved <name>]... [--ext <.ext>]... [--exclude <glob>]... \
  [--mode fail|warn] [--hosts]
python3 orphaned-scope-config.py --self-test
```

- **Inputs:**
  - `--config-dir`: the scope-keyed directory. Required, no default.
  - `--scopes`: the declared scopes, from a file or stdin (`-`). Required, no
    default. Two formats are read. A JSON object, as a resolver dumps it: every
    key that does not start with `_` is a scope, and so is every name in any
    `children` list. Or plain text, one scope per line, with `#` comments.
    A list that starts with `[` (a JSON array) is refused, because read as
    plain text it would become one scope named `["a"]`.
  - `--reserved`: a scope name the consumer always defines, such as an
    implicit "all" scope. Needed only when the scope list leaves it out.
  - `--ext`: an extension the consumer loads, repeatable. The default is
    `.yml`, `.yaml`, `.json` and no extension. Pass `--ext ''` to admit files
    with no extension when you set the list yourself.
  - `--exclude`: a glob for entries that are not configuration, such as
    reference examples (`*.example.*`). Excluded entries are listed in the
    summary, so an exclusion stays visible.
  - `--mode`: `fail` (the default) or `warn`.
  - `--hosts`: read the hosts of the resolver's JSON dump as the scopes, for
    a per-host directory: every name in any `hosts` list, plus the keys of
    `_meta.hostvars`. Both are read because the dump lists under
    `_meta.hostvars` only the hosts that have variables.
- **Outputs:** one line per orphan (`ORPHAN:` or `WARN:`, the path, why it is
  never loaded, and a nearest-name hint), then one summary line with the
  counts and the excluded names.
- **Exit codes:** 0 no orphan, or `--mode warn`; 1 an orphan in `fail` mode;
  2 usage error or refusal (a missing directory, an unreadable, empty or
  invalid scope list).
- **Preconditions:** the scope list comes from the system that will load the
  files (§3, "Ask the resolver").

## 3. Approach / algorithm

### Ask the resolver for the scopes

Take the scope list from the configuration system's own resolver whenever it
has one, not from a hand parse of its registry file. The resolver applies the
system's real naming rules, and a hand parse gets them wrong in quiet ways.

The worked case is an INI-style group inventory. In that format a group is
declared by a `[name]` section **or** by a `[name:children]` section; a
`[name:vars]` section alone does not declare one. The group named in a
`:children` section is a real group with real variables. A hand parse that
skips every section with a colon in it (the obvious first version) reports
that group's variable file as orphaned: a false positive on a valid file.
The resolver's JSON dump avoids this. Two details of that dump matter, both
read from the resolver's source:

- a group with no hosts and no children is left out of the top-level keys,
  but still appears in its parent's `children` list. That is why the tool
  collects `children` names too;
- the dump includes the implicit groups (an "all" group and an "ungrouped"
  group), so `--reserved` is not needed with it.

When the system has no resolver, write the scope list by hand or by a small
script, and treat that script as part of the audit's own test surface.

### The stem rule

For each entry in the directory (hidden entries skipped):

1. An entry that matches an `--exclude` glob is set aside and named in the
   summary.
2. A directory is a scope entry by its name. (Many systems read a
   directory named after a scope file by file.)
3. A file whose name ends in a loaded extension has that extension removed;
   the rest is the scope name. A file with no extension, where that is
   admitted, is its own scope name.
4. A file with any other extension (`web.yml.bak`, `db.yml.orig`) is reported
   as never read: the consumer does not load it. The same holds for an
   editor backup such as `web.yml~`, which the consumer skips on purpose:
   delete such a file, do not rename it, because its content is an older
   copy of a file that is loaded.
5. Every scope name not in the declared set (plus `--reserved`) is an orphan.
   `difflib.get_close_matches` supplies the hint.

### Refuse rather than guess

- **A missing directory is a refusal, not a pass.** The first version of
  this check returned success when the directory was absent, so a mistyped
  path made the gate permanently green.
- **An empty scope list is a refusal.** Against no scopes, every file is an
  orphan; with a guard that skips the comparison when the list is empty, none
  is. Neither answer is honest.

### One toggle, failing closed

`--mode fail` is the default. A pipeline that wants a softer start sets
`--mode warn` explicitly, for example from one CI variable, and the variable's
absence means `fail`. This keeps a single switch between "report" and "gate",
and a forgotten switch gates.

```python
#!/usr/bin/env python3
"""orphaned-scope-config: find config entries keyed by a scope name (a group,
an environment, a workspace) for which no scope is declared. Such an entry is
never loaded, so every edit to it has no effect.

  orphaned-scope-config.py --config-dir DIR --scopes FILE|- [--reserved NAME]...
                           [--ext .EXT]... [--exclude GLOB]... [--mode fail|warn]
  orphaned-scope-config.py --self-test

--scopes reads either a JSON object (a resolver's dump: every key not starting
with '_' is a scope, and so is every name in any "children" list) or plain
text (one scope per line, '#' starts a comment).

Exit 0 no orphan (or --mode warn); 1 orphan found in fail mode;
2 usage error or refusal (missing dir, unreadable or empty scope list).
Stdlib only.
"""
from __future__ import annotations

import argparse
import difflib
import fnmatch
import json
import sys
from pathlib import Path

DEFAULT_EXTS = (".yml", ".yaml", ".json")


class Refusal(Exception):
    """The audit cannot give an honest answer; exit 2."""


def load_scopes(text: str, hosts: bool = False) -> set[str]:
    """Scope names from a resolver's JSON dump or a plain list. With hosts=True
    the names are the hosts of the dump (every "hosts" list and the keys of
    _meta.hostvars), for a per-host directory."""
    text = text.strip()
    if not text:
        raise Refusal("the scope list is empty: an audit against no scopes "
                      "would call every entry orphaned, or with a guard, none")
    if text.startswith("["):
        raise Refusal("the scope list starts with '[': a JSON array is neither "
                      "a resolver object nor a line list")
    if hosts:
        if not text.startswith("{"):
            raise Refusal("--hosts reads a resolver's JSON dump, not a line list")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise Refusal(f"the scope dump is not valid JSON: {exc.msg}") from None
        names = set((data.get("_meta") or {}).get("hostvars") or {})
        for val in data.values():
            if isinstance(val, dict):
                names.update(h for h in val.get("hosts", []) or [] if isinstance(h, str))
        if not names:
            raise Refusal("the scope dump names no host")
        return names
    if text.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise Refusal(f"the scope dump is not valid JSON: {exc.msg}") from None
        scopes = set()
        for key, val in data.items():
            if key.startswith("_"):
                continue
            scopes.add(key)
            if isinstance(val, dict):
                scopes.update(c for c in val.get("children", []) or [] if isinstance(c, str))
    else:
        scopes = {ln.split("#", 1)[0].strip() for ln in text.splitlines()}
        scopes.discard("")
    if not scopes:
        raise Refusal("the scope list names no scope")
    return scopes


def entries(config_dir: Path, exts, excludes):
    """(name, stem or None, kind) for each entry. stem is None when a file's
    extension is not one the consumer loads."""
    for p in sorted(config_dir.iterdir()):
        if p.name.startswith("."):
            continue
        if any(fnmatch.fnmatch(p.name, g) for g in excludes):
            yield p.name, None, "excluded"
            continue
        if p.is_dir():
            yield p.name, p.name, "dir"
            continue
        if "." not in p.name and "" in exts:
            yield p.name, p.name, "file"
            continue
        for e in exts:
            if e and p.name.endswith(e):
                yield p.name, p.name[: -len(e)], "file"
                break
        else:
            yield p.name, None, "ignored-extension"


def audit(config_dir: Path, scopes: set[str], reserved=(), exts=DEFAULT_EXTS + ("",),
          excludes=()):
    """(checked, findings, excluded). Each finding is (entry, message)."""
    if not config_dir.is_dir():
        raise Refusal(f"config dir {config_dir} does not exist: a missing dir "
                      "is not a clean one")
    known = set(scopes) | set(reserved)
    checked, findings, excluded = 0, [], []
    for name, stem, kind in entries(config_dir, exts, excludes):
        if kind == "excluded":
            excluded.append(name)
            continue
        checked += 1
        if stem is None:
            findings.append((name, "extension the consumer does not load: never read"))
        elif stem not in known:
            near = difflib.get_close_matches(stem, sorted(known), n=1)
            hint = f" (did you mean '{near[0]}'?)" if near else ""
            findings.append((name, f"no declared scope '{stem}': never loaded{hint}"))
    return checked, findings, excluded


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="orphaned-scope-config.py")
    ap.add_argument("--config-dir", type=Path)
    ap.add_argument("--scopes")
    ap.add_argument("--reserved", action="append", default=[])
    ap.add_argument("--ext", action="append", default=None,
                    help="loaded extension, repeatable; '' admits files with none")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--mode", choices=("fail", "warn"), default="fail")
    ap.add_argument("--hosts", action="store_true",
                    help="the scopes are the dump's hosts (a per-host directory)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        self_test()
        return 0
    if a.config_dir is None or a.scopes is None:
        ap.print_usage(sys.stderr)
        print("error: --config-dir and --scopes are required", file=sys.stderr)
        return 2
    exts = tuple(a.ext) if a.ext is not None else DEFAULT_EXTS + ("",)
    try:
        text = sys.stdin.read() if a.scopes == "-" else Path(a.scopes).read_text()
        scopes = load_scopes(text, hosts=a.hosts)
        checked, findings, excluded = audit(a.config_dir, scopes, a.reserved, exts, a.exclude)
    except (Refusal, OSError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    for name, msg in findings:
        print(f"{'ORPHAN' if a.mode == 'fail' else 'WARN'}: {a.config_dir / name}: {msg}")
    print(f"checked {checked} entr{'y' if checked == 1 else 'ies'} against "
          f"{len(scopes)} scope(s); {len(findings)} orphaned; "
          f"{len(excluded)} excluded{': ' + ', '.join(excluded) if excluded else ''}")
    return 1 if findings and a.mode == "fail" else 0


def self_test() -> None:
    import tempfile
    root = Path(tempfile.mkdtemp())
    cfg = root / "scope_vars"
    cfg.mkdir()
    for n in ("web.yml", "db.yaml", "all.yml", "parent.yml", "child.json", "webb.yml",
              "old.yml.bak", "example.yml", "noext"):
        (cfg / n).write_text("k: v\n")
    (cfg / "cache").mkdir()
    (cfg / ".gitkeep").write_text("")
    dump = {"_meta": {"hostvars": {}}, "all": {"children": ["ungrouped", "parent", "web", "db", "cache"]},
            "parent": {"children": ["child"]}, "web": {"hosts": ["h1"]}, "db": {"hosts": ["h2"]}}
    scopes = load_scopes(json.dumps(dump))
    # empty groups appear only as children in a resolver dump; they still count
    assert {"child", "cache", "ungrouped", "parent"} <= scopes and "_meta" not in scopes, scopes
    checked, f, ex = audit(cfg, scopes, excludes=["example*"])
    got = {n: m for n, m in f}
    assert set(got) == {"webb.yml", "old.yml.bak", "noext"}, got
    assert "did you mean 'web'" in got["webb.yml"], got
    assert "never read" in got["old.yml.bak"]
    assert ex == ["example.yml"] and checked == 9, (checked, ex)
    # plain list registry, reserved scope, no-extension files not loaded
    lst = load_scopes("web\ndb # databases\n\nparent\nchild\ncache\nnoext\n")
    _, f, _ = audit(cfg, lst, reserved=["all"], exts=DEFAULT_EXTS, excludes=["example*"])
    assert {n for n, _ in f} == {"webb.yml", "old.yml.bak", "noext"}, f
    # --hosts: the dump's hosts, from every "hosts" list and _meta.hostvars
    hdump = dict(dump, _meta={"hostvars": {"h1": {}, "h3": {}}})
    assert load_scopes(json.dumps(hdump), hosts=True) == {"h1", "h2", "h3"}
    # refusals: missing dir, empty list, list with only comments, broken JSON
    for bad in (lambda: audit(root / "absent", scopes),
                lambda: load_scopes(""), lambda: load_scopes("# none\n"),
                lambda: load_scopes("{oops"), lambda: load_scopes('["web"]'),
                lambda: load_scopes("h1\n", hosts=True),
                lambda: load_scopes('{"web": {"children": []}}', hosts=True)):
        try:
            bad()
        except Refusal:
            pass
        else:
            raise AssertionError("a refusal case returned a result")
    # exit codes
    sf = root / "scopes.json"
    sf.write_text(json.dumps(dump))
    import contextlib, io
    quiet = contextlib.redirect_stdout(io.StringIO())
    quiet_err = contextlib.redirect_stderr(io.StringIO())
    with quiet, quiet_err:
        _exit_codes(cfg, sf, root)
    print("self-test: PASS (resolver dump with children, orphan with hint, unloaded extension, "
          "exclusion, plain list, reserved, host list, refusals, exit codes)")


def _exit_codes(cfg, sf, root) -> None:
    assert main(["--config-dir", str(cfg), "--scopes", str(sf), "--exclude", "example*"]) == 1
    assert main(["--config-dir", str(cfg), "--scopes", str(sf), "--exclude", "example*",
                 "--mode", "warn"]) == 0
    assert main(["--config-dir", str(root / "absent"), "--scopes", str(sf)]) == 2
    assert main(["--scopes", str(sf)]) == 2


if __name__ == "__main__":
    sys.exit(main())
```

Recorded run of the self-test, then of the script on a synthetic fixture: an
INI inventory with groups `web` and `db`, a parent group declared only by
`[cluster:children]`, and an empty group `spare`; a variable directory holding
files for those groups and `all`, plus `staging.yml` (no such group),
`dbs.yml` (a typo) and `web.example.yml` (a reference example). The scope list
comes from the resolver.

```text
$ python3 orphaned-scope-config.py --self-test
self-test: PASS (resolver dump with children, orphan with hint, unloaded extension, exclusion, plain list, reserved, host list, refusals, exit codes)
$ ansible-inventory -i inventory.ini --list > scopes.json
$ python3 orphaned-scope-config.py --config-dir group_vars --scopes scopes.json --exclude "*.example.*"
ORPHAN: group_vars/dbs.yml: no declared scope 'dbs': never loaded (did you mean 'db'?)
ORPHAN: group_vars/staging.yml: no declared scope 'staging': never loaded
checked 7 entries against 6 scope(s); 2 orphaned; 1 excluded: web.example.yml
exit 1
$ python3 orphaned-scope-config.py --config-dir group_var --scopes scopes.json
REFUSED: config dir group_var does not exist: a missing dir is not a clean one
exit 2
```

A second fixture for `--hosts`: host `h1` in `web`, `h2` in `db`, `h3` in no
group, and a per-host directory with `h1.yml`, `h2.yml` and `h4.yml`. The
dump lists `h3` only under `ungrouped.hosts`, because it has no variables.

```text
$ ansible-inventory -i inventory.ini --list > scopes.json
$ python3 orphaned-scope-config.py --config-dir host_vars --scopes scopes.json --hosts
ORPHAN: host_vars/h4.yml: no declared scope 'h4': never loaded
checked 3 entries against 3 scope(s); 1 orphaned; 0 excluded
exit 1
```

On the same fixture, the hand-parsing first version reported `cluster.yml`
(declared by `[cluster:children]`) and `web.example.yml` as orphans, and
returned success for the missing directory.

## 4. Portable vs blueprint

- **Portable (use as-is):** the two scope-list formats, the stem rule,
  directory entries, the unloaded-extension finding, exclusions named in the
  summary, the refusals, the fail/warn toggle, the nearest-name hint.
- **Write per project:** the command that dumps the scopes (the resolver
  call), the directory or directories to audit, the extension list when the
  consumer differs from the default, and the exclusion globs for its example
  files.
- **Adopting notes:**
  - Run it in the same gate that already validates the configuration, once
    per scope-keyed directory (variables per group, variables per host,
    overlays per environment).
  - A per-host directory is audited the same way, with the host list as the
    scopes: pass the same resolver dump with `--hosts`.
  - If the plant keeps reference examples in the same directory, give them a
    naming convention and one exclusion glob, and say so where the examples
    live.

## 5. Pitfalls and sharp edges

- **A matched name is not proof the file loads.** Some systems also need the
  scope to be *selected* in the run (an inventory limit, an active profile, a
  selected workspace). A file that passes here can still be skipped by a run
  that does not select its scope. The tool proves "can be loaded", not "was
  loaded".
- **The resolver may rename scopes.** Some resolvers rewrite names with
  characters they do not accept (a hyphen to an underscore, for example),
  depending on a setting. A hand-written scope list then disagrees with what
  the system really uses. Take the list from the resolver, and the files must
  match the resolver's names.
- **A variables file can be loaded by another route.** A play or job that
  names a file explicitly (a "vars files" list, an include) reads it whatever
  its name. Such a file is not scope-keyed: move it out of the scope-keyed
  directory, or add its name to `--exclude` with a comment that says who
  loads it.
- **Deleting an orphan may delete a secret's only copy, not the secret.** An
  orphaned file can still hold encrypted or plain secrets, and removing it
  from the tree does not remove it from version history. Rotate what it held,
  or rewrite history by owner decision.
- **Do not widen `--exclude` to make the gate pass.** An exclusion is a
  statement that an entry is not configuration. A real orphan hidden behind a
  broad glob is the silent failure this tool exists to catch.

## 6. Tests that cover it

The self-test in the script above (`orphaned-scope-config.py --self-test`)
asserts: a resolver dump yields every top-level key except `_`-prefixed ones,
plus every `children` name (an empty group counts); a misspelled file is an
orphan with a nearest-name hint; a file with an unloaded extension is
reported as never read; an excluded example is named in the summary and not
reported; a directory entry and a file with no extension are checked; a plain
list with comments and a reserved scope gives the same findings; `--hosts`
reads every `hosts` list and the `_meta.hostvars` keys; a missing
directory, an empty list, a comment-only list, invalid JSON, a JSON array,
and `--hosts` given a line list or a dump with no host each refuse;
the exit code is 1 for an orphan in `fail` mode, 0 in `warn` mode, 2 for a
missing directory and for missing arguments.

- **How to run the tests:** `python3 orphaned-scope-config.py --self-test`
  (exit 0 on pass; an `AssertionError` names the case that failed).

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/declared-variable-existence-auditor.md`
  (declared names against a live store);
  `tool-corpus/ops/declared-consumer-link-generator.md` (consumer links
  against one declaration); `tool-corpus/ops/renamed-config-key-auditor.md`
  (keys a framework silently ignores after an upgrade, the same "silently
  inert configuration" class one level down, inside a file).
- **Related skills:** `skill-corpus/genericize-config-to-examples.md` (turning
  real per-instance files into reference examples; its trap that a
  file-name-keyed validator needs an example exclusion is this tool's
  `--exclude`).
- **Library notes:** `library-corpus/pypi/ansible-core.md` (variable files
  load for the group or host of exactly that name; a file whose name matches
  no group is never loaded).
- **Sources:** distilled from practice. The INI inventory
  declaration rules and the dump's treatment of empty groups were read from
  the upstream inventory plugin and CLI source
  (https://github.com/ansible/ansible, `lib/ansible/plugins/inventory/ini.py`
  and `lib/ansible/cli/inventory.py`, retrieved 2026-10-05).

## 8. Changelog

- 2026-10-05: created. Groups declared by a `:children` section count; the scope list
  comes from the resolver; a missing directory refuses instead of passing;
  example exclusion and unloaded extensions are handled explicitly.
- 2026-10-05: review fixes. A JSON-array scope list is refused; `--hosts`
  reads the host list from the same dump for a per-host directory; backup
  files are named as skipped by the consumer; the paired skill is linked.
