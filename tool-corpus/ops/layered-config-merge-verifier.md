# Tool: layered-config-merge-verifier

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool — the native-oracle idiom,
> both guard checks, and the false-green guard are portable and adoptable as-is.
>
> **Read §5 first.** This tool's ancestor shipped a defect of exactly the kind
> the tool exists to catch: it keyed guard strength on the wrong token and
> published a measurement that was mostly false. The correction is why the page
> is worth reading before the code.

## 0. Identity

- **Category:** ops
- **Name:** layered-config-merge-verifier
- **Language / runtime:** python3. The two guard checks and the false-green
  guard are **stdlib only**. The optional resolved-document walk needs a parser
  for whatever the resolver prints: stdlib `json` when the resolver can emit
  JSON, otherwise **one third-party YAML parser** — that parser is the single
  non-stdlib requirement anywhere in the tool, and only for that one block.
- **Stability:** **portable** — the implementation below runs as written against
  any layered declarative configuration with `${VAR}`-style substitution; the
  resolver command, the layer labels, and the sensitive-token list are all
  caller-supplied, with no defaults

## 1. What it does

Answers what a **layered** declarative configuration **actually resolves to**,
as opposed to what any one of its source files appears to say.

The recurring situation: a configuration is assembled from several files —
a base layer plus per-environment overlays, includes, or profile files — and the
system that consumes it performs a real merge with real precedence rules.
Reading one file therefore answers nothing, and reading all of them by eye
answers it wrongly, because the merge is not textual.

On top of the resolved truth it adds two checks the configuration system itself
does not have, both about **variable-substitution guards** — the syntax that
makes an unset or empty value abort the load instead of silently resolving to
nothing:

- **Check A — cross-environment drift.** A reference guarded in one layer must
  be guarded **at least as strongly** in every other layer that uses it.
- **Check B — within-file consistency.** A reference guarded somewhere in a file
  must be guarded **everywhere** in that file.

It applies to any system that resolves a layered declarative config with
variable-substitution guards — container orchestration manifests, infrastructure
definitions, application config with an overlay chain, any format whose loader
supports a fail-on-unset substitution form.

## 2. Interface & invocation

```sh
layered-config-merge-verifier.py \
  --layer base=<path> --layer overlay=<path> [--layer <label>=<path> ...] \
  [--resolver '<cmd> -f {target} resolve'] [--target <file> ...] \
  [--cwd <dir>] [--resolver-format json|yaml] \
  [--sensitive <token> ...] [--sensitive-label '<what a hit means>']
```

- **Inputs:**
  - `--layer LABEL=PATH` — **required, at least twice, no defaults.** The layers
    whose guard strength is compared. The label is the caller's, and appears
    verbatim in every finding. Baking a project's own file paths in as defaults
    is exactly what makes a tool unshareable; this tool has none.
  - `--resolver` — the command that performs the **real** merge, with `{target}`
    substituted per target. Optional: with no resolver the tool runs the guard
    checks alone.
  - `--target` — repeatable; each is resolved by `--resolver` separately.
  - `--sensitive` / `--sensitive-label` — **caller-supplied.** A list of service
    names, ports, or other tokens that must not appear in the resolved document,
    and the one line to print when one does. The tool ships **no** opinion about
    which names or ports are dangerous; that judgment belongs to the caller's
    domain and is passed in at the call site.
- **Outputs:** stdout only. One `=== resolved: <target> ===` block per target,
  then a Check A block that opens with a **per-layer variable census**, then a
  Check B block, then `problems: <n>`. Every guard finding carries **line
  numbers**. No files written, no network.
- **Exit codes:** `0` only when `problems == 0`; `1` when any problem is counted,
  **or** when any layer yielded zero variable references (§3, false-green guard).
- **Preconditions:** the layer files exist and are readable; if `--resolver` is
  used, the resolver binary is on disk and needs no daemon or service to run.

## 3. Approach / algorithm

### Native oracle over reimplementation

The merge is performed by **shelling out to the configuration system's own
resolver** and reading its resolved output. The tool never re-derives merge
semantics itself.

This is the load-bearing decision. A reimplementation of merge semantics is a
**second, unvalidated implementation of the thing under test** — it has its own
precedence bugs, its own list-versus-map merge quirks, its own include handling,
and nothing checks it against the real one. When the two disagree, the tool is
wrong and says the configuration is. Prefer a resolver that runs without a
daemon or live service, so the oracle is available in a check, in CI, and on a
developer machine with nothing installed.

The division of labour follows from this: **any question about the merge goes to
the binary; only the guard questions are parsed here**, and they are parsed from
the source text because guards are a property of the text, not of the resolution.

### Check A — cross-environment drift, strongest wins

Per **variable reference**, take the strongest occurrence in each layer, and
report any layer whose strongest occurrence is weaker than the strongest seen
across all layers.

Two rules make this correct:

- **Key on the variable reference inside the value, never on the configuration
  key's name.** The guard belongs to the reference; a key and the reference under
  it differ the moment a key's value is composed from a variable, or the same
  variable appears under several keys. See §5 — this is the corrected defect.
- **Strongest occurrence wins**, because that matches real substitution
  semantics: one fail-closed reference **anywhere** aborts the whole load, even
  when a bare use of the same variable sits in an unrelated block.

### Check B — within-file consistency

Within one file, a variable guarded in one place and bare in another is covered
**by accident**: the coverage survives only while the guarded block stays in the
document. Deleting that block, or merging the layers, tears it. Check B reports
every variable that is fail-closed somewhere in a file and bare somewhere else in
the same file.

### False-green guard

**Analysing zero variables is a hard failure, never a pass.** A mistyped path, a
renamed file, a moved directory, or a resolver that printed nothing all produce
an empty census, and an empty census satisfies every check vacuously. The tool
prints the per-layer census before any finding and exits non-zero if any layer is
empty, so "no findings" can never be read as "nothing was looked at".

### Portable implementation

```python
#!/usr/bin/env python3
"""layered-config-merge-verifier — report what a LAYERED declarative config
actually resolves to, using the config system's own resolver as the oracle.

Guard checks and the false-green guard are stdlib-only. The optional
resolved-document walk needs a parser for the resolver's output format: stdlib
`json` when the resolver can emit JSON, otherwise one third-party YAML parser
(the single non-stdlib requirement in this file).
"""
from __future__ import annotations
import argparse, json, re, shlex, subprocess
from pathlib import Path

# ${NAME}  ${NAME:?m}  ${NAME?m}  ${NAME:-d}  ${NAME-d}  ${NAME:+a}  $NAME
VARREF = re.compile(
    r"\$\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)(?P<sep>:\?|:-|:\+|\?|-|\+|\})"
    r"|\$(?P<unbraced>[A-Za-z_][A-Za-z0-9_]*)"
)

# A TOTAL order over the modes this tool knows. There is deliberately NO
# default lookup: an unknown mode must crash, never silently rank as strongest.
STRENGTH = {
    "FAIL-CLOSED": 3,        # errors on unset AND on empty
    "FAIL-CLOSED-UNSET": 2,  # errors on unset only; an empty value passes
    "DEFAULTED": 1,          # substitutes a default
    "BARE": 0,               # no guard at all
}
SEP_MODE = {":?": "FAIL-CLOSED", "?": "FAIL-CLOSED-UNSET",
            ":-": "DEFAULTED", "-": "DEFAULTED",
            ":+": "BARE", "+": "BARE",   # alternate-value form: never a guard
            "}": "BARE"}


def var_refs(path: Path) -> dict[str, dict[str, list[int]]]:
    """variable -> mode -> line numbers, keyed on the REFERENCE in the value,
    never on the configuration key the reference sits under."""
    out: dict[str, dict[str, list[int]]] = {}
    if not path.exists():
        return out
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in VARREF.finditer(line):
            name = m.group("braced") or m.group("unbraced")
            mode = SEP_MODE[m.group("sep")] if m.group("braced") else "BARE"
            out.setdefault(name, {}).setdefault(mode, []).append(n)
    return out


def strongest(modes) -> str:
    return max(modes, key=lambda m: STRENGTH[m])


def check_a(layers):
    """CHECK A — cross-layer drift. Strongest occurrence anywhere is the floor."""
    findings = []
    for name in sorted({n for _, refs in layers for n in refs}):
        here = [(lab, strongest(refs[name]), refs[name])
                for lab, refs in layers if name in refs]
        if len(here) < 2:
            continue
        s_lab, s_mode, _ = max(here, key=lambda t: STRENGTH[t[1]])
        for lab, mode, modes in here:
            if STRENGTH[mode] < STRENGTH[s_mode]:
                findings.append((name, lab, mode, sorted(modes[mode]), s_lab, s_mode))
    return findings


def check_b(refs, label):
    """CHECK B — within-file: guarded somewhere => guarded everywhere."""
    findings = []
    for name, modes in sorted(refs.items()):
        guarded = [m for m in modes if m.startswith("FAIL-CLOSED")]
        bare = sorted(l for m in modes if STRENGTH[m] == 0 for l in modes[m])
        if guarded and bare:
            findings.append((name, label,
                             sorted(l for m in guarded for l in modes[m]), bare))
    return findings


def parse_doc(text: str, fmt: str):
    if fmt == "json":
        return json.loads(text)
    try:
        import yaml                       # the one non-stdlib dependency
    except ImportError:
        return None
    return yaml.safe_load(text)


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, node


def resolve(resolver, target, cwd, fmt, sensitive, label):
    """NATIVE ORACLE: the config system resolves its own merge; we only read."""
    cmd = [p.replace("{target}", target) for p in resolver]
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr.strip() or "(no stderr)").splitlines()
        return 1, [f"  resolver FAILED (exit {proc.returncode})",
                   *(f"    {line}" for line in err)]
    doc = parse_doc(proc.stdout, fmt)
    if doc is None:
        return 1, [f"  resolved output not parseable as {fmt}: no parser available"]
    lines, problems = [], 0
    for where, value in walk(doc):
        for token in sensitive:
            if token in str(value):
                lines.append(f"  {label}: {where} = {value}   <-- matches {token!r}")
                problems += 1
    return problems, lines or ["  no sensitive token in the resolved document"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layer", action="append", required=True, metavar="LABEL=PATH",
                    help="configuration layer to compare; repeat at least twice")
    ap.add_argument("--resolver", help="e.g. '<tool> -f {target} resolve'")
    ap.add_argument("--target", action="append", default=[])
    ap.add_argument("--cwd", type=Path, default=None)
    ap.add_argument("--resolver-format", choices=("json", "yaml"), default="yaml")
    ap.add_argument("--sensitive", action="append", default=[],
                    help="caller-supplied token that must not appear resolved")
    ap.add_argument("--sensitive-label", default="SENSITIVE",
                    help="caller-supplied text printed for a sensitive hit")
    a = ap.parse_args()

    layers = []
    for spec in a.layer:
        if "=" not in spec:
            ap.error(f"--layer expects LABEL=PATH, got {spec!r}")
        lab, _, p = spec.partition("=")
        layers.append((lab, Path(p)))
    if len(layers) < 2:
        ap.error("--layer must be given at least twice")
    if a.target and not a.resolver:
        ap.error("--target requires --resolver")

    problems = 0
    for t in a.target:
        p, lines = resolve(shlex.split(a.resolver), t, a.cwd,
                           a.resolver_format, a.sensitive, a.sensitive_label)
        problems += p
        print(f"\n=== resolved: {t} ===")
        print("\n".join(lines))

    refs = [(lab, var_refs(p)) for lab, p in layers]
    print("\n=== A. cross-layer drift (per VARIABLE REFERENCE, strongest wins) ===")
    print("  variables: " + "  ".join(f"{lab}={len(r)}" for lab, r in refs))
    if any(not r for _, r in refs):          # FALSE-GREEN GUARD
        print("  FAIL: a layer yielded zero variable references "
              "— refusing to report a pass")
        return 1
    drift = check_a(refs)
    problems += len(drift)
    for name, lab, mode, lines_, s_lab, s_mode in drift:
        print(f"  WEAKER  {name}  {lab}={mode}{lines_} < {s_lab}={s_mode}")
    if not drift:
        print("  none")

    print("\n=== B. within-file consistency (guarded somewhere => everywhere) ===")
    bad = [f for lab, r in refs for f in check_b(r, lab)]
    problems += len(bad)
    for name, lab, g, bare in bad:
        print(f"  INCONSISTENT  {name}  {lab}: guarded {g} but BARE {bare}")
    if not bad:
        print("  none")

    print(f"\nproblems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the native-oracle split (resolver answers the merge,
  this file answers the guards); the reference-keyed strength model and its total
  order with no default lookup; Check A's strongest-wins comparison across N
  labelled layers; Check B; the false-green guard and the census line that makes
  it legible; caller-supplied layers, resolver, and sensitive tokens.
- **Fill in per system:** the `--resolver` command and its output format; the
  substitution syntax if the system does not use `${VAR}` forms — that is the one
  regex and the one `SEP_MODE` table, and nothing else in the file moves.
- **Blueprint extension:** a structural report beyond the sensitive-token walk
  (which named units expose which endpoints, which declared attributes the
  resolver ignores for a given unit kind) is inherently format-bound. Build it
  against the resolved document's real schema, in the adopting project.

## 5. Pitfalls and sharp edges

- **THE CORRECTED DEFECT — keying guard strength on the wrong token.** The first
  version of this tool compared guard strength by the **configuration key's
  name** rather than by the **variable reference inside the value**. The two
  differ whenever one variable appears under several keys, or a key's value is
  composed from another variable. The result was a **majority of false
  positives**, and they were not caught: the false measurement reached a decision
  record and a committed gate before anyone read the raw lines. Several
  "independent" recounts re-used the one premise instead of re-deriving it, so
  they agreed with each other and with the bug.
  **The lesson, which outlives this tool: re-derive the premise, not the number,
  and suspect the validator before the artifact.** A recount that starts from the
  validator's own output is not a second measurement.
- **A uniformly unguarded variable is invisible to both checks.** Check A needs a
  difference between layers; Check B needs a guarded occurrence in the same file.
  A variable that is bare **everywhere** satisfies neither and is reported by
  neither. This is structural, not a tuning problem. A green A/B does **not**
  mean "every variable is guarded" — that is a separate guard-inventory question,
  answered by a declared-variable check (§7), not by this tool.
- **Guard strength is a total order, and a downgrade inside the strong band is a
  real weakening.** A fail-on-unset-only form lets an **empty** value through
  where a fail-on-unset-and-empty form would abort. Rank them separately and
  compare on the rank, as the implementation above does. The ancestor collapsed
  them by falling back to "assume strongest" for unrecognized modes, and silently
  passed that downgrade. Never give a strength table a permissive default.
- **The reference regex is the census boundary.** Any substitution form the
  regex does not match is silently outside the analysis — not reported as
  unknown, simply absent. When adopting, plant one reference of **every** form
  the system supports into a fixture and confirm the census counts them all.
- **The sensitive-token walk reports; it does not understand.** It is a
  containment test over resolved scalars. It will match a token inside a longer
  unrelated string, and it cannot see an exposure the resolved document expresses
  some other way. Read the block; do not read the counter alone. A reporting
  block whose findings are not counted as problems is the classic way a real
  defect gets printed and scored clean.
- **Resolved output is not runtime truth.** The resolver reports what the
  document declares after the merge. Where a declaration is overridden by
  something created out of band — a pre-existing resource the config only
  references — the tool can report the declaration and flag the ambiguity, but it
  cannot confirm the live property without the running system.

## 6. Tests that cover it

Cover: a variable guarded in one layer and bare in another produces exactly one
Check A finding, naming both layers and both line sets; the same variable
guarded identically in both produces none; a fail-on-unset-only form in one layer
against fail-on-unset-and-empty in another **is** reported; a variable guarded in
one block of a file and bare in another block of the same file produces exactly
one Check B finding; a variable bare in every layer produces none from either
check (the documented blind spot, pinned as known); one variable appearing under
several different configuration keys produces **one** finding, not one per key
(the regression test for the corrected defect); pointing a layer at a missing
path exits `1` with the zero-variables message and never `0`; a resolver that
exits non-zero counts a problem and prints its full stderr; every substitution
form the target system supports appears in the census fixture.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/declared-variable-existence-auditor.md`
  (answers which variable **names** exist in the store — the guard-inventory
  question this tool structurally cannot see);
  `tool-corpus/ops/structured-secret-field-detector.md` (the same
  "the generic scanner does not see this shape" posture, one level down in the
  document); `tool-corpus/ops/config-driven-server-response-harness.md` (measures
  what a config-driven binary **emits**, where this measures what it **declares**).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-09-13 — created from harvested, generalized capability, by docs-librarian.
  Carries the corrected keying defect as the lead pitfall, replaces the donor's
  baked-in default paths with required labelled layers, and replaces its
  hardcoded port literal and domain judgment with a caller-supplied token list
  and label.
