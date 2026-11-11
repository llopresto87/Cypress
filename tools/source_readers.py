"""Stack readers of the source index (SPEC-0007 §6 "Stack readers").

`source-index.py` reads Python, shell and TS/JS itself; each other stack's
reader lives here, and the index mixes `StackReaders` into its extractor. A
reader is a stack-keyed module added on its own: Java, Thymeleaf templates,
YAML (with Compose), SQL, Dockerfile and nginx today. A reader reads a line at
a time from comment- and string-blanked text where the language has them, adds
`link`, `define` and `opaque_at` records through the extractor's own methods,
and records nothing for a reference that names no inventory file (a JDK or
library import, a container path, an image file, an uncommitted secret).

`source-index.py` loads this file by path from beside itself (the installer
places the two together) and hands it the helpers it shares through `bind`.
Standard library only.
"""
import json
import posixpath
import re
from types import SimpleNamespace

_host = SimpleNamespace()       # the shared helpers `bind` receives from source-index.py


def bind(**helpers):
    """Receive `joined`, `inside`, `glob_regex`, `scheme_led`, `literal_max`
    and `dir_link_max` from the index, which is their one home."""
    _host.__dict__.update(helpers)


# Extensions the readers add to the index's LANGUAGES; `thymeleaf`, `dockerfile`
# and `nginx` are decided by name and place (`named_language`).
LANGUAGES = {".java": "java", ".yml": "yaml", ".yaml": "yaml", ".sql": "sql"}
LINK_BEARING = ("java", "thymeleaf", "yaml", "sql", "dockerfile", "nginx")
# The languages a test file is run in besides the index's own: a YAML or SQL
# test fixture is data, never run.
RUNNABLE = ("java",)
ENUM_LANGUAGES = {"java", "thymeleaf", "yaml", "sql", "dockerfile", "nginx"}
ENUM_FOUND = {"same-package", "view-name"}     # a Java type a body names; a Java string naming a template
TEMPLATES_DIR = ("resources", "templates")     # a classpath `templates/` root (Spring Boot's)
RESOURCES_DIR = ("src", None, "resources")     # a classpath root: src/<set>/resources
DOCKERFILE = "Dockerfile"
NGINX_DIR = "nginx"
NGINX_SUFFIXES = (".conf", ".conf.template")
COMPOSE_NAME = re.compile(r"(?:docker-)?compose(?:\.[\w-]+)*\.ya?ml")

_JNAME = r"[A-Za-z_$][\w$]*"
JAVA_PACKAGE = re.compile(rf"[ \t]*package[ \t]+({_JNAME}(?:\.{_JNAME})*)[ \t]*;")
JAVA_IMPORT = re.compile(rf"[ \t]*import[ \t]+(static[ \t]+)?({_JNAME}(?:\.{_JNAME})*)(\.\*)?[ \t]*;")
JAVA_DEF = re.compile(rf"[ \t]*(?:@{_JNAME}(?:\.{_JNAME})*(?:\([^()]*\))?[ \t]+)*"
                      r"(?:(?:public|protected|private|static|final|abstract|sealed|non-sealed|strictfp)[ \t]+)*"
                      rf"(class|interface|enum|@[ \t]*interface|record(?=[ \t]+{_JNAME}[ \t]*[(<]))[ \t]+({_JNAME})")
JAVA_DEF_KIND = {"class": "class", "record": "class", "interface": "type", "enum": "type", "@interface": "type"}
JAVA_TYPE_REF = re.compile(r"(?<![\w$.])[A-Z][\w$]*")          # a capitalised name not after a `.`
JAVA_VIEW = re.compile(r"[A-Za-z0-9_][\w.-]*(?:/[\w.-]+)*")     # a view name: `orders/list`
TH_ATTR = re.compile(r"\bth:(?:replace|insert|include)\s*=\s*(['\"])(.*?)\1", re.S)
TH_FRAGMENT = re.compile(r"~\{\s*([A-Za-z0-9_][\w./-]*)\s*(?:::|\})")   # `~{name :: frag}`, `~{name}`
# YAML, read a line at a time: a `key: value` line or a `- item` line, by indentation.
YAML_LINE = re.compile(r"(?P<indent>[ \t]*)(?:(?P<dash>-)[ \t]+)?"
                       r"(?:(?P<key>[A-Za-z_][\w.-]*|\"[^\"]*\"|'[^']*')[ \t]*:(?:[ \t]+|$))?(?P<value>.*)")
SQL_DEF = re.compile(r"[ \t]*CREATE[ \t]+(?:OR[ \t]+REPLACE[ \t]+)?(?:UNIQUE[ \t]+)?(?:CONSTRAINT[ \t]+)?"
                     r"(SCHEMA|TABLE|FUNCTION|INDEX|TRIGGER)[ \t]+(?:IF[ \t]+NOT[ \t]+EXISTS[ \t]+)?"
                     r"([A-Za-z_][\w$]*(?:\.[A-Za-z_][\w$]*)?)", re.I)
SQL_DEF_KIND = {"schema": "type", "table": "type", "function": "function", "trigger": "function",
                "index": "variable"}
NGINX_INCLUDE = re.compile(r"[ \t]*include[ \t]+([^;\s]+)[ \t]*;")


# --- where a stack's files are found ------------------------------------------
def root_of(path: str, shape: tuple):
    """The directories of `path` up to the first run that matches `shape`
    (a segment, or None for any one), or None when no run does."""
    dirs = path.split("/")[:-1]
    for k in range(len(shape), len(dirs) + 1):
        if all(want is None or want == got for want, got in zip(shape, dirs[k - len(shape):k])):
            return "/".join(dirs[:k])
    return None


def template_root(path: str):
    """The Thymeleaf templates root of an `.html` path, the first
    `*/resources/templates` directory above it, or None."""
    return root_of(path, TEMPLATES_DIR) if path.endswith(".html") else None



def named_language(name: str):
    """`nginx` for a NGINX_SUFFIXES file under an `nginx/` directory,
    `thymeleaf` for an `.html` file under a templates root, `dockerfile` for a
    file named DOCKERFILE; None for every other path."""
    base = name.rsplit("/", 1)[-1]
    if base.endswith(NGINX_SUFFIXES) and NGINX_DIR in name.split("/")[:-1]:
        return "nginx"
    if template_root(name):
        return "thymeleaf"
    return "dockerfile" if base == DOCKERFILE else None


class StackReaders:
    """The readers, mixed into the index's `Extract`. They use its `files`,
    `by_name`, `under`, `link`, `define`, `opaque_at`, `missing`,
    `path_literal` and `literal_hit`."""

    def init_stack_readers(self):
        """The state the readers keep between files: Java's package directories
        and same-package references (linked once every package is read), the
        Thymeleaf templates roots, the classpath roots, and the Compose bind
        mounts with the container paths nginx files name (linked once every
        Compose file is read)."""
        self.java_dirs = {}                  # directory -> the .java files directly in it
        for path in sorted(self.records):
            if path.endswith(".java"):
                self.java_dirs.setdefault(posixpath.dirname(path), []).append(path)
        self.java_refs = {}                  # holder -> (package, {type name: first line})
        self.template_roots = sorted({r for r in map(template_root, self.records) if r})
        self.resource_roots = sorted({r for r in (root_of(p, RESOURCES_DIR) for p in self.records) if r})
        self.mounts = []                     # (container path, host plant path, holder) of each bind mount
        self.container_refs = []             # (holder, line, container path) an nginx file names

    def stack_readers(self) -> dict:
        """Language -> the method that reads a file of it."""
        return {"java": self.java, "thymeleaf": self.thymeleaf, "yaml": self.yaml, "sql": self.sql,
                "dockerfile": self.dockerfile, "nginx": self.nginx}

    def finish_stack_readers(self):
        """The links that need every file read first."""
        self.java_same_package()
        self.container_links()

    def forget_stack_reads(self, holder):
        """Drop what a file kept for the passes above when it turns out unreadable."""
        self.java_refs.pop(holder, None)
        self.container_refs = [r for r in self.container_refs if r[0] != holder]
        self.mounts = [m for m in self.mounts if m[2] != holder]

    @staticmethod
    def java_text(text: str):
        """(`text` with comments, string, text-block and char literals blanked,
        every newline kept so line numbers stand; each one-line string
        literal's content with its line)."""
        out, strings, i, n, line = [], [], 0, len(text), 1

        def blank(seg):
            return "".join(ch if ch == "\n" else " " for ch in seg)

        while i < n:
            c = text[i]
            if text.startswith('"""', i):
                j = i + 3                          # an escaped `\"""` does not close the block
                while j < n and not text.startswith('"""', j):
                    j += 2 if text[j] == "\\" else 1
                j = min(j + 3, n)
            elif c in "'\"":
                j = i + 1
                while j < n and text[j] != c and text[j] != "\n":
                    j += 2 if text[j] == "\\" else 1
                j = min(j, n)
                if c == '"':
                    strings.append((line, text[i + 1:j]))
                j += j < n and text[j] == c
            elif text.startswith("//", i):
                j = text.find("\n", i)
                j = n if j < 0 else j
            elif text.startswith("/*", i):
                j = text.find("*/", i + 2)
                j = n if j < 0 else j + 2
            else:
                out.append(c)
                line, i = line + (c == "\n"), i + 1
                continue
            out.append(blank(text[i:j]))
            line, i = line + text.count("\n", i, j), j
        return "".join(out), strings

    def java(self, rec, text):
        """A Java file: its package, imports and type definitions (nested ones
        qualified by brace depth), the capitalised names its body uses (linked
        by `java_same_package` once every package is read), and the string
        literals that name a Thymeleaf template (`view-name`, maybe)."""
        holder = rec["path"]
        code, strings = self.java_text(text)
        package, imported, refs = "", set(), {}
        stack, depth = [], 0                       # [name, depth at its declaration, body opened]
        for lineno, line in enumerate(code.split("\n"), 1):
            if (m := JAVA_PACKAGE.match(line)):
                package = m.group(1)
                continue
            if (m := JAVA_IMPORT.match(line)):
                static, name, star = m.groups()
                if not (static or star):
                    imported.add(name.rsplit(".", 1)[-1])   # a single-type import shadows the package's
                self.java_import(holder, name, bool(static), bool(star), lineno)
                continue
            decl = JAVA_DEF.match(line)
            if decl:
                prefix = "".join(s[0] + "." for s in stack if s[2])
                self.define(holder, prefix + decl.group(2), lineno,
                            JAVA_DEF_KIND[re.sub(r"[ \t]", "", decl.group(1))], "line-reading")
                stack.append([decl.group(2), depth, False])
            for m in JAVA_TYPE_REF.finditer(line):
                refs.setdefault(m.group(0), lineno)
            for c in line:
                if c == "{":
                    depth += 1
                    if stack and not stack[-1][2] and depth == stack[-1][1] + 1:
                        stack[-1][2] = True
                elif c == "}":
                    depth -= 1
                    if stack and stack[-1][2] and depth == stack[-1][1]:
                        stack.pop()
        # the default package is one per directory
        key = package or "/" + posixpath.dirname(holder)
        self.java_refs[holder] = (key, {k: v for k, v in refs.items() if k not in imported})
        for lineno, s in strings:
            view = s.split("::", 1)[0].strip().lstrip("/")
            if view and len(view) <= _host.literal_max and JAVA_VIEW.fullmatch(view):
                for root in self.template_roots:
                    if f"{root}/{view}.html" in self.files:
                        self.link(holder, f"{root}/{view}.html", "path-literal", "view-name", lineno)
            # the quoted path-literal rule, then the string as a classpath resource.
            # A leading-`/` string is a route ("/orders") or a classpath name in
            # Java, never holder-relative, so it skips the path-literal rule and
            # keeps the classpath one.
            if not s.startswith("/"):
                self.path_literal(holder, s, lineno)
            self.classpath(holder, s, lineno)

    def classpath(self, holder, text, line):
        """A classpath resource name (`/fixtures/x.yaml`, `db/roles.sql`,
        `classpath:db/migration`): a `maybe` link to the file, or to each file
        of the directory (a name holding a `/`), it names under each
        `src/<set>/resources` root."""
        name = text[len("classpath:"):] if text.startswith("classpath:") else text
        name = _host.inside(name.lstrip("/")) if name.strip("/") and len(name) <= _host.literal_max else None
        if not name or any(c.isspace() for c in name) or "://" in name:
            return
        for root in self.resource_roots:
            cand = f"{root}/{name}"
            if cand in self.files:
                self.literal_hit(holder, ("file", cand, False), line, text)
            elif "/" in name and cand in self.under:
                self.literal_hit(holder, ("dir", self.under[cand]), line, text)

    def java_files(self, suffix):
        """The inventory files whose path is `suffix` or ends in `/<suffix>`."""
        return [p for p in self.by_name.get(suffix.rsplit("/", 1)[-1], [])
                if p == suffix or p.endswith("/" + suffix)]

    def java_import(self, holder, name, static, star, line):
        """One import, by suffix over every source root: a wildcard links each
        `.java` file directly in each directory ending in the package's path
        (`directory`, maybe); a type import the one file ending in its path
        (`resolved`) or each of several (`ambiguous`), a static import's member
        dropped first and a nested type read as its outer file. An import
        naming no inventory file (the JDK, a library) records nothing."""
        segs = name.split(".")
        if star:
            d = "/".join(segs)
            files = [f for k, fs in sorted(self.java_dirs.items()) if k == d or k.endswith("/" + d) for f in fs]
            if len(files) > _host.dir_link_max:
                self.opaque_at(holder, line, name + ".*", "walks-tree")
                return
            for f in files:
                self.link(holder, f, "import", "directory", line)
            if files:
                return                                     # else `a.b.C.*`: the nested types of C
        elif static:
            segs = segs[:-1]                               # the member
        while segs:
            hits = self.java_files("/".join(segs) + ".java")
            for h in hits:
                self.link(holder, h, "import", "resolved" if len(hits) == 1 else "ambiguous", line)
            if hits or len(segs) < 2 or not segs[-2][:1].isupper():
                return
            segs = segs[:-1]                               # `a.b.C.Inner` lives in a/b/C.java

    def java_same_package(self):
        """Each capitalised name a Java file uses that names a `.java` file of
        its package, in any source root (Maven's src/main/java and
        src/test/java share packages): a `maybe` `same-package` link."""
        by_package = {}
        for holder, (key, _) in self.java_refs.items():
            stem = posixpath.splitext(holder.rsplit("/", 1)[-1])[0]
            by_package.setdefault(key, {}).setdefault(stem, []).append(holder)
        for holder, (key, refs) in sorted(self.java_refs.items()):
            types = by_package[key]
            for name, line in refs.items():
                for target in types.get(name, []):
                    self.link(holder, target, "import", "same-package", line)

    def thymeleaf(self, rec, text):
        """A Thymeleaf template: each `~{name :: fragment}` or `~{name}` in a
        `th:replace`, `th:insert` or `th:include` names `<root>/name.html`, an
        `exact` link when the inventory holds it, else unresolved. A
        fragment of the template itself (`~{::x}`, `~{this :: x}`) and a
        fragment passed in as a parameter (`${content}`) name no file."""
        holder = rec["path"]
        root = template_root(holder)
        for m in TH_ATTR.finditer(text):
            lineno = text.count("\n", 0, m.start()) + 1
            for ref in TH_FRAGMENT.finditer(m.group(2)):
                name = ref.group(1).lstrip("/")
                if name == "this":
                    continue
                target = _host.joined(root, name + ".html")
                if target in self.files:
                    self.link(holder, target, "import", "exact", lineno)
                else:
                    self.missing(holder, lineno, "import", ref.group(1), target)

    # -- the config languages (YAML, SQL, the Dockerfile, nginx), a line at a
    # time. A reference naming no inventory file records nothing: a container
    # path, an image file or an uncommitted secret is not the plant's to name.
    @staticmethod
    def hash_comment(line: str) -> str:
        """`line` cut at a `#` that starts it or follows a blank, outside quotes."""
        quote = None
        for i, c in enumerate(line):
            if quote:
                quote = None if c == quote else quote
            elif c in "'\"" and (i == 0 or line[i - 1] in " \t:-[{,"):
                quote = c
            elif c == "#" and (i == 0 or line[i - 1] in " \t"):
                return line[:i]
        return line

    @staticmethod
    def yaml_scalar(value: str):
        """A plain or quoted YAML scalar, its anchor dropped; None for an
        alias, a flow collection, a block scalar indicator or nothing."""
        v = re.sub(r"^&\S+\s*", "", value.strip())
        if not v or v[0] in "*[{|>":
            return None
        if len(v) > 1 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        return v or None

    def exact_or_directory(self, holder, path, line, reference, capped=True):
        """A path the config names exactly: a `certain` link to the file, or a
        `maybe` `directory` link to each file below the directory (with
        `capped`, more than DIR_LINK_MAX of them make the holder opaque).
        Whether it named either."""
        if path in self.files:
            self.link(holder, path, "path-literal", "exact", line)
        elif path in self.under or path == "" and self.files:
            files = self.under[path] if path else sorted(self.files)
            if capped:
                self.literal_hit(holder, ("dir", files), line, reference)
            else:
                for target in files:
                    self.link(holder, target, "path-literal", "directory", line)
        else:
            return False
        return True

    def yaml(self, rec, text):
        """A YAML file, its keys tracked by indentation. In a Compose file:
        `build:` and `build: context:` name `<context>/Dockerfile`; a service
        `volumes:` item `./src:/dst` is a bind mount, linked and kept for
        `container_links`; a top-level `secrets: <name>: file:` names its
        file. A `classpath:` scalar (comma-separated) is read by the classpath
        rule; another scheme-led one (`configtree:/x`, `image:tag`) names no
        file; every other scalar is read by the quoted path-literal rule."""
        holder = rec["path"]
        here = posixpath.dirname(holder)
        compose = bool(COMPOSE_NAME.fullmatch(holder.rsplit("/", 1)[-1]))
        stack = []                                 # (indent, key) of the open mappings
        for lineno, raw in enumerate(text.split("\n"), 1):
            line = self.hash_comment(raw).rstrip()
            if not line.strip() or line.strip() in ("---", "..."):
                continue
            m = YAML_LINE.match(line)
            indent, key = len(m["indent"]), m["key"]
            while stack and (stack[-1][0] > indent or stack[-1][0] == indent and not m["dash"]):
                stack.pop()
            if key:
                key = key.strip("'\"")
                stack.append((m.start("key"), key))
            path = [k for _, k in stack]
            value = self.yaml_scalar(m["value"])
            if value is None:
                continue
            if compose and (path[-1:] == ["build"] and key or path[-2:] == ["build", "context"]):
                self.exact_or_directory(holder, _host.joined(_host.joined(here, value) or ".", DOCKERFILE), lineno, value)
            elif compose and m["dash"] and not key and path[:1] == ["services"] and path[-1:] == ["volumes"]:
                self.bind_mount(holder, value, lineno)
            elif compose and len(path) == 3 and path[0] == "secrets" and key == "file":
                self.exact_or_directory(holder, _host.joined(here, value), lineno, value)
            elif value.startswith("classpath:"):
                for part in value.split(","):
                    self.classpath(holder, part.strip(), lineno)
            elif not _host.scheme_led.match(value):      # `configtree:/run/secrets/`, `image:tag` name no file
                self.path_literal(holder, value, lineno)

    def bind_mount(self, holder, item, line):
        """A Compose short-syntax volume `<source>:<target>[:<mode>]` whose
        source is a host path (`./`, `../`): linked, and kept as a mount. A
        named volume (`data:/var/lib/x`) names no file."""
        parts = item.split(":")
        if len(parts) < 2 or not parts[0].startswith("."):
            return
        host = _host.joined(posixpath.dirname(holder), parts[0].rstrip("/"))
        if host is not None and self.exact_or_directory(holder, host, line, parts[0]):
            self.mounts.append((parts[1].rstrip("/"), host, holder))

    def sql(self, rec, text):
        """A SQL file defines what its `CREATE SCHEMA|TABLE|FUNCTION|INDEX|
        TRIGGER` lines name (`OR REPLACE`, `UNIQUE`, `CONSTRAINT`, `IF NOT
        EXISTS` allowed), the name as written, a schema-qualified one whole.
        It names no file: a migration is inbound-only."""
        for lineno, line in enumerate(text.split("\n"), 1):
            m = SQL_DEF.match(line)
            if m:
                self.define(rec["path"], m.group(2), lineno, SQL_DEF_KIND[m.group(1).lower()], "line-reading")

    def dockerfile(self, rec, text):
        """A Dockerfile: each `COPY`/`ADD` source, relative to the build
        context (the Dockerfile's directory), names a file (`certain`) or a
        directory, whose files are each a `maybe` link. A directory source is
        exempt from DIR_LINK_MAX (a copy pulls in every file below it): the image truly
        holds every file below it, so it never makes the Dockerfile opaque.
        `--from=<stage>` copies from a stage and names no file; a source with
        a glob, a variable or a URL is not read."""
        holder = rec["path"]
        lines, k = text.split("\n"), 0
        while k < len(lines):
            start, line = k + 1, lines[k]
            while line.rstrip().endswith("\\") and k + 1 < len(lines):
                k += 1
                line = line.rstrip()[:-1] + " " + lines[k]
            k += 1
            words = line.split(None, 1)
            if len(words) < 2 or words[0].upper() not in ("COPY", "ADD"):
                continue
            rest = words[1].strip()
            args = [w for w in rest.split() if not w.startswith("--")]
            if any(w.startswith("--from") for w in rest.split()):
                continue
            if args and args[0].startswith("["):
                try:
                    args = json.loads(" ".join(args))
                except ValueError:
                    continue
            for src in args[:-1] if isinstance(args, list) else []:
                if not isinstance(src, str) or any(c in src for c in "*?[$") or "://" in src:
                    continue
                target = _host.joined(posixpath.dirname(holder), src.rstrip("/") or ".")
                if target is not None:
                    self.exact_or_directory(holder, "" if target == "." else target, start, src, capped=False)

    def nginx(self, rec, text):
        """An nginx file: each absolute `include` path is kept for
        `container_links`, which maps it through the Compose bind mounts. A
        path no mount maps (an image file, `conf.d/` the image renders)
        names no file."""
        for lineno, line in enumerate(text.split("\n"), 1):
            m = NGINX_INCLUDE.match(self.hash_comment(line))
            if m and m.group(1).startswith("/"):
                self.container_refs.append((rec["path"], lineno, m.group(1)))

    def container_links(self):
        """Each container path an nginx file names, under a bind mount's
        target, as the host file it mounts: a `maybe` link (a glob each
        matching file directly in its directory)."""
        for holder, line, path in self.container_refs:
            for dst, host, _ in self.mounts:
                if path != dst and not path.startswith(dst + "/"):
                    continue
                hp = host + path[len(dst):]
                if any(c in hp for c in "*?["):
                    rx = _host.glob_regex(hp)
                    targets = [f for f in self.under.get(posixpath.dirname(hp), []) if rx.match(f)]
                else:
                    targets = [hp] if hp in self.files else []
                for t in targets:
                    self.link(holder, t, "path-literal", "path-literal", line)
