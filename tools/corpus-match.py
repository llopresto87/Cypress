#!/usr/bin/env python3
"""corpus-match: propose the corpus pages a project's manifests match.

`install.sh <host> --expertise propose` runs this from the seed and prints its
output; it writes nothing (SPEC-0001 EXPERTISE_PROPOSAL_WRITES_NOTHING). It is
not placed in a plant.

It reads the direct dependencies each manifest under the project declares,
normalizes each one to candidate corpus ids by the per-ecosystem rule of
SPEC-0001 §6, and prints one line per matching page, sorted by id:

    <corpus id>  <manifest path>: <entry>        a library-corpus page
    <corpus id>  stack: <library corpus id>      a skill or tool page

A library page matches when its `<key>/<name>` equals a candidate, compared
without regard to case, or when the candidate is a package its own-package list
names: a list item in its `## What it is` section that opens with the package's
registry name in backticks and a colon, read with the key's normalization. Any
other mention of a package on a page is a citation and proposes nothing. A
maven page also matches an entry whose coordinates its `## What it is` section
names in backticks (the own-coordinate form). One entry proposes every page it
matches, the specific page and its umbrella both. A language page is proposed
by the declaration that says the project is written in it (a Java level, a Dart
SDK constraint) where a manifest serves several languages, and a page with no
package (a platform, a CLI tool) by the triggers SPEC-0001 §6 names for it: a
file it reads, an official image, a GitHub Action, a pre-commit hook id, or a
package whose only use is to drive it. The walk reads the project's own
manifests only: it skips scratch and copy directories, the agent hosts' own
directories, a nested plant and a symlinked directory. A stack-keyed `skill-corpus/<key>/<name>` page, and a
`tool-corpus/<category>/<name>` page, match when their `stack:` frontmatter
names a library page that matched. A lockfile's transitive entries are not
read. A manifest that does not parse is named on stderr with the reason and
skipped (SPEC-0001 EXPERTISE_MANIFEST_UNREADABLE); the run still exits 0.

Usage:
  corpus-match.py <project-dir> [--seed <seed-root>]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import importlib.util
import xml.etree.ElementTree as ET
from fnmatch import fnmatchcase
from pathlib import Path

# the plant's edge (a nested plant, a symlinked directory) is plant_walk's rule,
# shared with graft-audit.py and growth-audit.py; loaded from beside this file
_pw_spec = importlib.util.spec_from_file_location(
    "cypress_plant_walk", Path(__file__).resolve().parent / "plant_walk.py")
plant_walk = importlib.util.module_from_spec(_pw_spec)
_pw_spec.loader.exec_module(plant_walk)

try:
    import tomllib
except ImportError:  # Python before 3.11: the pyproject reader falls back
    tomllib = None

# Directories no manifest the plant declares lives in: dependency stores,
# build output, virtual environments, version control, the plant's graph, and
# the scratch and copy directories a session or a graft leaves behind (a
# `.tmp/` verify copy, a graft backup or snapshot, a `.bak-` copy), and the
# agent hosts' own directories, whose manifests are the host's plugins. A copy
# repeats the plant's manifests, so reading it first puts a scratch path in
# every evidence line, and reading a stale copy proposes what the plant dropped.
PRUNE = {"node_modules", ".git", ".hg", ".svn", "target", "build", "dist",
         "vendor", "venv", "env", "__pycache__", "bin", "obj",
         ".dart_tool", ".gradle", ".idea", ".cypress", ".next", ".nuxt",
         "coverage", ".tox", ".mypy_cache", ".pytest_cache", ".tmp",
         ".claude", ".opencode", ".codex", ".prime"}
PRUNE_GLOBS = (".venv*", ".graft-backup-*", ".graft-snapshot-*", "*.bak-*")
DOCKERFILE = re.compile(r"^((Docker|Container)file([.-][^/]*)?|[^/]+\.[Dd]ockerfile)$")
AZURE_PIPELINES = re.compile(r"^azure-pipelines([.-][^/]*)?\.ya?ml$")
COMPOSE = re.compile(r"^(docker-)?compose([.-][^/]*)?\.ya?ml$")
REQUIREMENTS_TXT = re.compile(r"^requirements[^/]*\.txt$")
PEP503 = re.compile(r"[-_.]+")
GRADLE_BUILD = ("build.gradle", "build.gradle.kts")
BITBUCKET_PIPELINES = "bitbucket-pipelines.yml"
PRE_COMMIT = ".pre-commit-config.yaml"
WORKFLOW = re.compile(r"^[^/]+\.ya?ml$")
# A file a tool reads by default names the tool's page by its presence.
PRESENCE = {"trivy.yaml": ("cli", "trivy"), ".trivyignore": ("cli", "trivy"),
            ".gitleaks.toml": ("cli", "gitleaks")}
# The GitHub Action a tool's page names as its own channel, at any ref.
ACTIONS = {"aquasecurity/trivy-action": ("cli", "trivy"),
           "gitleaks/gitleaks-action": ("cli", "gitleaks")}
# The pre-commit hook ids a tool's page names.
HOOKS = {"gitleaks": ("cli", "gitleaks"), "gitleaks-docker": ("cli", "gitleaks"),
         "gitleaks-system": ("cli", "gitleaks")}
# An entry whose only use is to drive a platform names the platform's page too.
DRIVES = {("galaxy", "community.proxmox"): ("platform", "proxmox-ve"),
          ("pypi", "proxmoxer"): ("platform", "proxmox-ve")}
# The Java language level in a POM: a property, or the compiler plugin's setting.
JAVA_LEVEL_PROPERTIES = ("java.version", "maven.compiler.release",
                         "maven.compiler.source", "maven.compiler.target")
JAVA_LEVEL_PLUGIN = ("release", "source", "target")


class Unreadable(Exception):
    """A manifest that cannot be read; the message says why."""


def read_text(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Unreadable(f"not UTF-8 (byte {exc.start})") from None
    except OSError as exc:
        raise Unreadable(f"cannot be read ({exc.strerror})") from None


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def maven(path: Path):
    """(key, candidate, entry) for each <dependency> and <plugin> of a POM."""
    try:
        root = ET.fromstring(read_text(path))
    except ET.ParseError as exc:
        raise Unreadable(f"not well-formed XML ({exc})") from None
    yield "cli", "maven", "(present)"
    level = java_level(root)
    if level:
        yield "language", "java", level
    for el in root.iter():
        if local(el.tag) not in ("dependency", "plugin"):
            continue
        fields = {local(c.tag): (c.text or "").strip() for c in el}
        art, group = fields.get("artifactId", ""), fields.get("groupId", "")
        if not art:
            continue
        entry = f"{group}:{art}" if group else art
        names = artifact_names(art)
        segs = [s for s in group.split(".") if s]
        if segs:
            names.add(segs[-1])
        if len(segs) >= 2:
            names.add("-".join(segs[-2:]))
        for n in names:
            yield "maven", n, entry
        for n in reduced_artifacts(art):
            yield "maven-coordinate", f"{group}:{n}", entry


def java_level(root) -> str:
    """The first Java language level a POM declares, as evidence: a level
    property, or the maven-compiler-plugin's `<release>`, `<source>` or
    `<target>`. An empty string when the POM sets none (an aggregator, or a
    build that inherits its level from a parent outside the project)."""
    for el in root.iter():
        if local(el.tag) != "properties":
            continue
        for prop in el:
            name = local(prop.tag)
            if name in JAVA_LEVEL_PROPERTIES and (prop.text or "").strip():
                return f"{name}={prop.text.strip()}"
    for el in root.iter():
        if local(el.tag) != "plugin":
            continue
        art = next((c for c in el if local(c.tag) == "artifactId"), None)
        if art is None or (art.text or "").strip() != "maven-compiler-plugin":
            continue
        for conf in el.iter():
            if local(conf.tag) != "configuration":
                continue
            for setting in conf:
                name = local(setting.tag)
                if name in JAVA_LEVEL_PLUGIN and (setting.text or "").strip():
                    return f"maven-compiler-plugin {name}={setting.text.strip()}"
    return ""


def gradle(path: Path):
    """A Gradle build is read for its Java language level only: a Java
    toolchain's `languageVersion`, or a `sourceCompatibility` or
    `targetCompatibility`. Its dependencies match no page yet."""
    text = read_text(path)
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if (re.search(r"\blanguageVersion\b.*\bJavaLanguageVersion\b", line)
                or re.match(r"(java\.)?(source|target)Compatibility\b\s*(=|\.set\s*\(|\s)", line)):
            yield "language", "java", line
            return


def reduced_artifacts(artifact: str) -> list:
    """An artifactId read three ways, its tokens split at `-` and `.`: as
    written; with the `starter` token dropped; and with it and the token
    before it dropped. A starter is named after the module it brings in, so
    `<family>-starter-<module>` reads as `<family>-<module>`, and
    `<base>-<flavour>-starter-<area>` as `<base>-<area>`."""
    parts = [t for t in re.split(r"[-.]", artifact.lower()) if t]
    out = [parts]
    if "starter" in parts[1:]:
        i = parts.index("starter", 1)
        out.append(parts[:i] + parts[i + 1:])
        out.append(parts[:i - 1] + parts[i + 1:])
    return ["-".join(p) for p in out if p]


def artifact_names(artifact: str) -> set:
    """Every run of consecutive tokens of each reading of the artifactId: the
    umbrella a prefix names, the module a later run names, a starter's page."""
    names = set()
    for reduced in reduced_artifacts(artifact):
        parts = reduced.split("-")
        for i in range(len(parts)):
            for j in range(i + 1, len(parts) + 1):
                names.add("-".join(parts[i:j]))
    return names


def npm(path: Path):
    try:
        data = json.loads(read_text(path))
    except ValueError as exc:
        raise Unreadable(f"not valid JSON ({exc})") from None
    if not isinstance(data, dict):
        raise Unreadable("not a JSON object")
    yield "language", "nodejs", "(present)"
    for section in ("dependencies", "devDependencies"):
        deps = data.get(section)
        if not isinstance(deps, dict):
            continue
        for name in deps:
            cand = name.lower().lstrip("@").replace("/", "-")
            yield "npm", cand, name
            if name == "typescript":
                yield "language", "typescript", name
            if name == "@angular/core":
                yield "language", "angular", name


def pep503(name: str) -> str:
    return PEP503.sub("-", name).lower()


def requirement_name(spec: str) -> str:
    m = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", spec)
    return m.group(1) if m else ""


def requirements_txt(path: Path):
    text = read_text(path)
    yield "language", "python", "(present)"
    for raw in text.splitlines():
        line = raw.split(" #", 1)[0].strip()
        if not line or line.startswith(("#", "-")) or "://" in line:
            continue
        name = requirement_name(line)
        if name:
            yield "pypi", pep503(name), line


def pyproject(path: Path):
    text = read_text(path)
    if tomllib is not None:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise Unreadable(f"not valid TOML ({exc})") from None
    else:
        data = {"project": {"dependencies": re.findall(r'^\s*"([^"]+)",?\s*$', text, re.M)}}
    yield "language", "python", "(present)"
    project = data.get("project") or {}
    specs = list(project.get("dependencies") or [])
    for group in (project.get("optional-dependencies") or {}).values():
        specs.extend(group or [])
    for spec in specs:
        if isinstance(spec, str) and requirement_name(spec):
            yield "pypi", pep503(requirement_name(spec)), spec
    poetry = ((data.get("tool") or {}).get("poetry") or {})
    for section in ("dependencies", "dev-dependencies"):
        for name in (poetry.get(section) or {}):
            if name.lower() != "python":
                yield "pypi", pep503(name), name


def csproj(path: Path):
    try:
        root = ET.fromstring(read_text(path))
    except ET.ParseError as exc:
        raise Unreadable(f"not well-formed XML ({exc})") from None
    yield "language", "dotnet", "(present)"
    for el in root.iter():
        if local(el.tag) == "PackageReference" and el.get("Include"):
            yield "nuget", el.get("Include"), el.get("Include")


def dotnet_tools(path: Path):
    """The local tool manifest: each tool's package id, as `dotnet tool` reads it."""
    try:
        data = json.loads(read_text(path))
    except ValueError as exc:
        raise Unreadable(f"not valid JSON ({exc})") from None
    tools = data.get("tools") if isinstance(data, dict) else None
    if not isinstance(tools, dict):
        raise Unreadable("no tools object")
    for name in tools:
        yield "nuget", name, name


def yaml_block(text: str, key: str) -> dict:
    """The child keys of a top-level YAML mapping `key`, each with the lines of
    its own block: enough of YAML for a pubspec, stdlib only."""
    out, current, inside = {}, None, False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            inside = line.split(":", 1)[0].strip() == key
            current = None
            continue
        if not inside:
            continue
        if current is None or indent <= out[current][0]:
            name = line.strip().split(":", 1)[0].strip()
            out[name] = (indent, [])
            current = name
        else:
            out[current][1].append(line.strip())
    return {k: v[1] for k, v in out.items()}


def pubspec(path: Path):
    text = read_text(path)
    if not re.search(r"^name\s*:", text, re.M):
        raise Unreadable("not a pubspec (no top-level name:)")
    sdk = environment_sdk(text)
    if sdk:
        yield "language", "dart", f"sdk: {sdk}"
    for section in ("dependencies", "dev_dependencies"):
        for name, body in yaml_block(text, section).items():
            if any(re.match(r"sdk\s*:\s*flutter\b", b) for b in body):
                if section == "dependencies" and name == "flutter":
                    yield "language", "flutter", "flutter"
                continue
            yield "pub", name, name


def environment_sdk(text: str) -> str:
    """The `sdk:` constraint of a pubspec's top-level `environment:` block,
    the Dart SDK's; an empty string when there is none."""
    inside = False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            inside = line.split(":", 1)[0].strip() == "environment"
            continue
        m = re.match(r"\s+sdk\s*:\s*(.*?)\s*$", line)
        if inside and m and m.group(1).split(" #", 1)[0].strip():
            return m.group(1).split(" #", 1)[0].strip()
    return ""


# A runtime image names a language or a build tool as well as itself, and
# a tool that arrives as an official image names its cli page.
IMAGE_ALSO = {"node": ("language", "nodejs"), "python": ("language", "python"),
              "maven": ("cli", "maven"), "trivy": ("cli", "trivy"),
              "gitleaks": ("cli", "gitleaks")}


def image_matches(image: str):
    """(key, candidate) for one image reference: its last path segment, tag
    and digest dropped, as a container; a runtime image's language or build
    tool; nothing when the name itself is a variable. A variable registry or
    tag does not hide the name."""
    path = image.split("@", 1)[0]
    last = path.rsplit("/", 1)[-1].split(":", 1)[0].lower()
    if not last or "$" in last or "{" in last:
        return
    yield "container", last
    if last in IMAGE_ALSO:
        yield IMAGE_ALSO[last]
    if "/dotnet/" in path.lower():
        yield "language", "dotnet"


def compose(path: Path):
    text = read_text(path)
    yield "container", "docker-compose", "(present)"
    for raw in text.splitlines():
        m = re.match(r"\s*image\s*:\s*['\"]?([^'\"#\s]+)", raw)
        if not m:
            continue
        for key, cand in image_matches(m.group(1)):
            yield key, cand, m.group(1)


def dockerfile(path: Path):
    """Every stage's FROM image. A stage alias, `scratch` and an image an ARG
    names propose nothing."""
    text = read_text(path)
    yield "container", "docker", "(present)"
    stages = set()
    for raw in text.splitlines():
        words = raw.split()
        if len(words) < 2 or words[0].upper() != "FROM":
            continue
        words = [w for w in words[1:] if not w.startswith("--")]
        if not words:
            continue
        image = words[0]
        if len(words) >= 3 and words[1].upper() == "AS":
            stages.add(words[2].lower())
        if image.lower() in stages or image.lower() == "scratch":
            continue
        for key, cand in image_matches(image):
            yield key, cand, image


def azure_pipelines(path: Path):
    """A pipeline definition names its schema's platform page by its presence."""
    read_text(path)
    yield "platform", "azure-pipelines-yaml", "(present)"


def bitbucket_pipelines(path: Path):
    """A Bitbucket pipeline names its platform page by its presence, and each
    `image:` given as a string, at file level or on a step, is read as an image.
    An image given as a mapping (`name:` beside credentials) is not read."""
    text = read_text(path)
    yield "platform", "bitbucket-pipelines", "(present)"
    for raw in text.splitlines():
        m = re.match(r"\s*(?:-\s*)?image\s*:\s*['\"]?([^'\"#\s]+)", raw)
        if not m:
            continue
        for key, cand in image_matches(m.group(1)):
            yield key, cand, m.group(1)


def workflow(path: Path):
    """A GitHub workflow's `uses:` lines: an Action a tool's page names as its
    own channel proposes that page; the evidence is the action as written."""
    text = read_text(path)
    for raw in text.splitlines():
        m = re.match(r"\s*(?:-\s*)?uses\s*:\s*['\"]?([^'\"#\s]+)", raw)
        if m and m.group(1).split("@", 1)[0].lower() in ACTIONS:
            yield (*ACTIONS[m.group(1).split("@", 1)[0].lower()], m.group(1))


def pre_commit(path: Path):
    """A pre-commit config's hook ids: a hook id a tool's page names proposes it."""
    text = read_text(path)
    for raw in text.splitlines():
        m = re.match(r"\s*(?:-\s*)?id\s*:\s*['\"]?([A-Za-z0-9_.-]+)", raw)
        if m and m.group(1) in HOOKS:
            yield (*HOOKS[m.group(1)], m.group(1))


def presence(path: Path):
    """A config file a tool reads by default names the tool's page."""
    read_text(path)
    yield (*PRESENCE[path.name], "(present)")


def galaxy(path: Path):
    text = read_text(path)
    inside = False
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith((" ", "-")):
            inside = raw.split(":", 1)[0].strip() == "collections"
            continue
        if not inside:
            continue
        m = re.match(r"\s*-\s*(?:name\s*:\s*)?['\"]?([A-Za-z0-9_]+\.[A-Za-z0-9_]+)", raw)
        if m:
            yield "galaxy", m.group(1), m.group(1)


def reader_for(name: str, rel_base: Path = Path(".")):
    if rel_base.parts[-2:] == (".github", "workflows") and WORKFLOW.match(name):
        return workflow
    if name in GRADLE_BUILD:
        return gradle
    if name == BITBUCKET_PIPELINES:
        return bitbucket_pipelines
    if name == PRE_COMMIT:
        return pre_commit
    if name in PRESENCE:
        return presence
    if name == "pom.xml":
        return maven
    if name == "package.json":
        return npm
    if REQUIREMENTS_TXT.match(name):
        return requirements_txt
    if name == "pyproject.toml":
        return pyproject
    if name.endswith(".csproj"):
        return csproj
    if name == "dotnet-tools.json":
        return dotnet_tools
    if name == "pubspec.yaml":
        return pubspec
    if COMPOSE.match(name):
        return compose
    if name in ("requirements.yml", "requirements.yaml"):
        return galaxy
    if DOCKERFILE.match(name):
        return dockerfile
    if AZURE_PIPELINES.match(name):
        return azure_pipelines
    return None


def pruned(name: str) -> bool:
    return name in PRUNE or any(fnmatchcase(name, g) for g in PRUNE_GLOBS)


def manifests(project: Path):
    for base, dirs, files in os.walk(project):
        rel_base = Path(base).relative_to(project)
        if rel_base.parts[:2] == ("docs", "graph"):
            dirs[:] = []           # the plant's graph holds no manifest
            continue
        dirs[:] = sorted(d for d in dirs if not pruned(d)
                         and not plant_walk.is_foreign(Path(base) / d))
        for name in sorted(files):
            reader = reader_for(name, rel_base)
            if reader is not None:
                yield (rel_base / name).as_posix(), project / rel_base / name, reader


def frontmatter_stack(path: Path) -> list:
    """The `stack:` list of a page's leading frontmatter block."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return []
    out, inside = [], False
    for line in m.group(1).splitlines():
        if re.match(r"^stack\s*:", line):
            inside = True
            rest = line.split(":", 1)[1].strip()
            if rest.startswith("[") and rest.endswith("]"):
                out.extend(x.strip().strip("'\"") for x in rest[1:-1].split(",") if x.strip())
                inside = False
            continue
        if inside:
            item = re.match(r"^\s+-\s*(.+?)\s*$", line)
            if item:
                out.append(item.group(1).strip("'\""))
            elif line.strip():
                inside = False
    return out


def own_coordinates(page: Path) -> set:
    """The `groupId:artifactId` coordinates a maven page names in backticks in
    its `## What it is` section, its own artifacts, each read as an entry's
    artifactId is (reduced_artifacts). A coordinate cited in a later section,
    the interop a page describes, is not the page's own and proposes nothing."""
    out = set()
    for group, art in re.findall(r"`([A-Za-z0-9_.-]+):([A-Za-z0-9_.-]+)`", what_it_is(page)):
        out.update(f"{group}:{n}".lower() for n in reduced_artifacts(art))
    return out


def what_it_is(page: Path) -> str:
    """The body of a page's `## What it is` section, or an empty string."""
    try:
        text = page.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    m = re.search(r"^## What it is[ \t]*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


OWN_ITEM = re.compile(r"^[ \t]*[-*+][ \t]+`([^`\s]+)`[ \t]*:", re.M)


def normalized(key: str, name: str) -> tuple:
    """(key, candidate) for one package name a page lists, read the way the
    key's manifest row reads an entry (SPEC-0001 §6)."""
    if key == "npm":
        return key, name.lower().lstrip("@").replace("/", "-")
    if key == "pypi":
        return key, pep503(name)
    if key == "container":
        return key, name.split("@", 1)[0].rsplit("/", 1)[-1].split(":", 1)[0].lower()
    if key == "maven" and ":" in name:
        return "maven-coordinate", name.lower()
    return key, name.lower()


def own_packages(page: Path, key: str) -> set:
    """The (key, candidate) pairs of a page's own-package list: each list item
    in its `## What it is` section that opens with a package's registry name in
    backticks and a colon. Every other mention, in prose, in an item opening
    with something else, or in a later section, is a citation."""
    out = set()
    for name in OWN_ITEM.findall(what_it_is(page)):
        k, cand = normalized(key, name)
        if k == "maven-coordinate":
            group, art = name.lower().split(":", 1)
            out.update((k, f"{group}:{n}") for n in reduced_artifacts(art))
        else:
            out.add((k, cand))
    return out


def corpus_pages(seed: Path, root: str):
    """id -> path of each page at `<root>/<key>/<name>.md`."""
    pages = {}
    base = seed / root
    if not base.is_dir():
        return pages
    for key in sorted(p for p in base.iterdir() if p.is_dir()):
        for page in sorted(key.glob("*.md")):
            pages[f"{root}/{key.name}/{page.stem}"] = page
    return pages


def declared_name(key: str, entry: str) -> str:
    """The package name an entry declares, its version specifier dropped: the
    evidence of a match through a page's own-package list."""
    if key == "pypi":
        return requirement_name(entry) or entry
    return entry


def propose(project: Path, seed: Path):
    library = corpus_pages(seed, "library-corpus")
    by_candidate, by_own = {}, {}
    for cid, page in library.items():
        _, key, name = cid.split("/", 2)
        by_candidate.setdefault((key, name.lower()), set()).add(cid)
        for pair in own_packages(page, key):
            by_own.setdefault(pair, set()).add(cid)
        if key == "maven":
            for coord in own_coordinates(page):
                by_candidate.setdefault(("maven-coordinate", coord), set()).add(cid)
    found, skipped = {}, []
    for rel, path, reader in manifests(project):
        try:
            matches = list(reader(path))
        except Unreadable as exc:
            skipped.append(f"corpus-match: skipped {rel}: {exc}")
            continue
        # within one manifest, an entry that names the page itself is better
        # evidence than one its own-package list names
        named, listed = {}, {}
        for key, cand, entry in matches:
            pair = (key, cand.lower())
            pairs = [pair] + ([DRIVES[pair]] if pair in DRIVES else [])
            for p in pairs:
                for cid in sorted(by_candidate.get(p, ())):
                    named.setdefault(cid, f"{rel}: {entry}")
            for cid in sorted(by_own.get(pair, ())):
                listed.setdefault(cid, f"{rel}: {declared_name(key, entry)}")
        for cid, evidence in {**listed, **named}.items():
            found.setdefault(cid, evidence)
    for root in ("skill-corpus", "tool-corpus"):
        for cid, page in corpus_pages(seed, root).items():
            for lib in frontmatter_stack(page):
                if lib in found and not found[lib].startswith("stack: "):
                    found.setdefault(cid, f"stack: {lib}")
                    break
    return found, skipped


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Propose the library-corpus, skill-corpus and tool-corpus pages a "
                    "project's manifests match (SPEC-0001 §6). Read-only.")
    ap.add_argument("project", help="the project directory whose manifests are read")
    ap.add_argument("--seed", default=str(Path(__file__).resolve().parent.parent),
                    help="the seed root whose corpora are matched (default: this seed)")
    args = ap.parse_args()
    project, seed = Path(args.project).resolve(), Path(args.seed).resolve()
    if not project.is_dir():
        print(f"corpus-match: not a directory: {args.project}", file=sys.stderr)
        return 2
    found, skipped = propose(project, seed)
    for line in skipped:
        print(line, file=sys.stderr)
    if not found:
        print("corpus-match: no corpus page matches this project's manifests")
        return 0
    for cid in sorted(found):
        print(f"{cid}  {found[cid]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
