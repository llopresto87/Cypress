"""source_paths: the seed's rules for what counts as source and how a path is named.

One home for the path rules the seed's tools share, so no two of them can
disagree about a path:

  * the code-path rule: paths under `docs/graph/` and `.cypress/` are the
    graph and its state, not code, and neither are build and backup files
    (`__pycache__/`, `*.pyc`, `*.bak`, `*.bak-*`), which no fact describes
    (SPEC-0003, "Code anchor");
  * the governed repositories: the plant root when it is a Git work tree,
    plus each `repo:` value in node frontmatter that resolves inside the root
    to a directory holding `.git`;
  * the Git boundary: every Git call, with the variables that would point it
    at another repository removed and optional locks off;
  * the uncommitted paths of a repository, and the content state of a path,
    as its Git blob hash, read through the one regular-file opener that never
    follows a symlink or blocks on a FIFO;
  * the descriptor-relative directory opener and atomic write under
    `.cypress/`, which never follow a symlink;
  * the citation grammar and its one resolution function,
    `resolve_citation`: strict, the plant-relative reading `cite_problem`
    gives; lenient, the text match `source-index.py anchors` reads
    (SPEC-0007 §6 "Helper").

A scratch directory under `.cypress/` that the atomic write fills ignores
itself with an inner `.gitignore` of `*`; the other home of that self-ignore
rule is route-hook.py's `.cypress/session/` writer.

Library module, no CLI. code-anchor.py, growth-audit.py and source-index.py
load it by file path from beside themselves, like frontmatter.py; it loads the one
frontmatter reader, `frontmatter.py`, from beside itself. install.sh places it
in a plant's `docs/graph/`, beside code-anchor.py. No function reads a
module-global root: each takes the root, or the repository, as a parameter.
"""

import hashlib
import os
import posixpath
import re
import secrets
import stat
import subprocess
from pathlib import Path
import importlib.util as _ilu
_fm_spec = _ilu.spec_from_file_location(
    "cypress_frontmatter", Path(__file__).resolve().parent / "frontmatter.py")
_frontmatter = _ilu.module_from_spec(_fm_spec)
_fm_spec.loader.exec_module(_frontmatter)

GIT_TIMEOUT = 10            # seconds per Git call
NOT_CODE = ("docs/graph/", ".cypress/")
NOISE_DIR = "__pycache__"                       # build and backup files: never code
NOISE_NAME = re.compile(r"\.(pyc|bak)$|\.bak-\d")   # *.bak-<digit>*: the installer's stamp
DELETED = "deleted"

# Variables that would point Git at some other repository or index than the
# work tree it runs in.
GIT_LOCATORS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                "GIT_OBJECT_DIRECTORY")

# Every file call of the atomic write, and the creation of a scratch directory,
# is relative to a directory descriptor. A platform without these has no safe
# way to refuse a symlink, so it gets no write, never a path-string fallback.
# os.replace rides on renameat, listed as `rename`.
DIR_FD_CALLS = {"open", "stat", "unlink", "rename", "mkdir"}

MISSING_CITATION = "does not exist in the plant"
MALFORMED_CITATION = "is not a path citation"

# The shape a citation may take: a relative path, an optional `:line` (or
# `:line:col`, or `:line-line`) suffix, and — stripped before this is ever
# asked — a `#anchor`. A segment may hold a space, because a repository path
# may; what it may not hold is the punctuation prose arrives with, which is
# what makes a trailing note detectable as one.
_CITE_SEG = r"[^\s/:'\"()\[\]{}<>|*?=,;]+(?: [^\s/:'\"()\[\]{}<>|*?=,;]+)*"
CITATION_RE = re.compile(
    rf"{_CITE_SEG}(?:/{_CITE_SEG})*/?(?::\d+(?::\d+)?(?:-\d+)?)?")
_LINE_SUFFIX = re.compile(r":(\d+)(?::\d+)?(-\d+)?$")


class Refused(Exception):
    """A write that must not happen. The message is the line the caller shows."""


class GitMissing(Exception):
    pass


class GitFailed(Exception):
    pass


# --- Git: the one boundary to the repositories ------------------------------
def git(repo: Path, *args: str, input: bytes = None, ok=(0,)) -> bytes:
    """One Git call in `repo`, as an argument list, bounded by GIT_TIMEOUT.
    Optional locks and the fsmonitor are off, so no call rewrites the index
    or leaves a file behind; a partial clone never fetches a missing object.
    `input` is the call's stdin (none when None); `ok` holds the exit codes
    that are answers (`check-ignore` exits 1 when nothing is ignored), and any
    other exit is GitFailed."""
    env = {k: v for k, v in os.environ.items() if k not in GIT_LOCATORS}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    try:
        r = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args],
                           cwd=str(repo), env=env, input=input,
                           stdin=subprocess.DEVNULL if input is None else None,
                           capture_output=True, timeout=GIT_TIMEOUT)
    except FileNotFoundError:
        raise GitMissing() from None
    except (OSError, subprocess.SubprocessError) as e:
        raise GitFailed(f"git {args[0]}: {type(e).__name__}") from None
    if r.returncode not in ok:
        raise GitFailed(f"git {args[0]} exited {r.returncode}")
    return r.stdout


# --- paths and content -------------------------------------------------------
def plant_path(repo: str, path: str) -> str:
    """A repository-relative path made plant-relative ("." is the root)."""
    return path if repo == "." else posixpath.join(repo, path)


def is_code(repo: str, path: str) -> bool:
    """False for the graph and its state, and for build and backup noise
    (SPEC-0003 ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE)."""
    rel = plant_path(repo, path.rstrip("/"))
    *dirs, name = rel.split("/")
    return not ((rel + "/").startswith(NOT_CODE) or NOISE_DIR in dirs or NOISE_NAME.search(name))


def relative(path) -> bool:
    """True for a clean path inside the directory it is relative to."""
    return isinstance(path, str) and (path == "." or (
        not path.startswith("/") and posixpath.normpath(path) == path
        and ".." not in path.split("/")))


def uncommitted(repo: Path) -> list:
    """Every path `git status` shows as changed or untracked, relative to the
    repository, ignored files left out."""
    out = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames")
    return [e[3:].decode("utf-8", "surrogateescape") for e in out.split(b"\0") if len(e) > 3]


def open_regular(path, dir_fd=None):
    """(descriptor, size) of a regular file opened for reading, or None when
    the path is anything else. The open never follows a symlink and never
    blocks on a FIFO, and nothing is read before `fstat` shows a regular file.
    `dir_fd` makes `path` relative to that directory descriptor. FileNotFoundError
    when nothing is there; any other OSError when unusable."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dir_fd)
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode):
        os.close(fd)
        return None
    return fd, st.st_size


def content_state(repo: Path, path: str):
    """The Git blob hash of the path's content now, DELETED when nothing is
    there, or None when it cannot be hashed (a directory, a FIFO, a nested work
    tree, an unreadable file, a file that changed size while read). A symlink
    hashes its link text. A file is hashed as a stream under the blob header of
    its `fstat` size, so no file is held whole."""
    p = repo / path
    try:
        if stat.S_ISLNK(os.lstat(p).st_mode):
            text = os.fsencode(os.readlink(p))
            return hashlib.sha1(b"blob %d\0" % len(text) + text).hexdigest()
        opened = open_regular(p)
    except FileNotFoundError:
        return DELETED
    except OSError:
        return None
    if opened is None:
        return None
    fd, size = opened
    h = hashlib.sha1(b"blob %d\0" % size)
    read = 0
    try:
        while chunk := os.read(fd, 1 << 16):
            h.update(chunk)
            read += len(chunk)
    except OSError:
        return None
    finally:
        os.close(fd)
    return h.hexdigest() if read == size else None


# --- governed repositories ---------------------------------------------------
def repo_values(graph: Path):
    """Each string `repo:` value the one frontmatter reader returns for a node
    under `graph`. A node it refuses, or an unreadable file, is skipped."""
    for dirpath, dirnames, filenames in os.walk(graph):
        for name in filenames:
            if not name.endswith(".md"):
                continue
            try:
                meta, _ = _frontmatter.parse_file(os.path.join(dirpath, name))
            except (OSError, _frontmatter.FrontmatterError):
                continue
            value = meta.get("repo")
            if isinstance(value, str) and value:
                yield value


def governed_repositories(root: Path) -> list:
    """The plant root when it is a Git work tree, then each distinct `repo:`
    value that resolves inside the root to a directory holding `.git`, as
    paths relative to the root ("." is the root)."""
    top = root.resolve()
    nested = set()
    for value in repo_values(root / "docs" / "graph"):
        target = (root / value).resolve()
        try:
            rel = target.relative_to(top).as_posix()
        except ValueError:
            continue
        if rel != "." and target.is_dir() and (target / ".git").exists():
            nested.add(rel)
    return (["."] if (root / ".git").exists() else []) + sorted(nested)


# --- the descriptor-relative atomic write ------------------------------------
def open_dir(root: Path, *parts: str, create: bool = False) -> int:
    """A descriptor on <root>/<parts...>, each part opened relative to the one
    before and never through a symlink. With `create`, the last part is made
    (0755, by `mkdir` relative to its parent's descriptor) when absent; no
    other part is ever created. FileNotFoundError when a part is absent; any
    other OSError when unusable."""
    if not (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")
            and DIR_FD_CALLS <= {f.__name__ for f in os.supports_dir_fd}):
        raise OSError(0, "no descriptor-relative file calls on this platform")
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for i, part in enumerate(parts):
            if create and i == len(parts) - 1:
                try:
                    os.mkdir(part, 0o755, dir_fd=fd)
                except FileExistsError:
                    pass
            inner = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = inner
    except BaseException:
        os.close(fd)
        raise
    return fd


def atomic_write(dir_fd: int, name: str, data: bytes, temp_prefix: str, shown: str) -> None:
    """Replace `name` under `dir_fd` atomically: a 0644 temp file named
    `temp_prefix` plus a random suffix, created exclusively, then os.replace
    onto the name. On any failure the temp file is removed and the old file,
    if any, stays as it was. A name that is anything but a regular file (a
    symlink above all) is Refused, never replaced; `shown` names it there."""
    try:
        st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        if not stat.S_ISREG(st.st_mode):
            raise Refused(f"refusing {shown}: not a regular file "
                          f"(a symlink is never followed); nothing written")
    except FileNotFoundError:
        pass
    tmp = temp_prefix + secrets.token_hex(8)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dir_fd)
    try:
        try:
            os.fchmod(fd, 0o644)
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view):]
        finally:
            os.close(fd)
        os.replace(tmp, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except BaseException:
        try:
            os.unlink(tmp, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        raise


# --- citations ---------------------------------------------------------------
def split_citation(ref):
    """(cited, path, line) of a reference: `cited` with any `#anchor`
    stripped, `path` with the `:line`, `:line:col` or `:line-line` suffix
    stripped too, and the first line it names, or None."""
    cited = str(ref).split("#", 1)[0].strip()
    m = _LINE_SUFFIX.search(cited)
    return cited, _LINE_SUFFIX.sub("", cited).strip(), int(m.group(1)) if m else None


def shape_problem(ref):
    """The part of a reference that never was a path, as a phrase — or None
    when the whole of it parses as a citation.

    Asked only of a reference the filesystem could not answer for, because
    wherever a path resolves its shape is past arguing about. A reference
    carrying a trailing note, a quoted value or a parenthetical named no file
    to begin with, and reporting it as a missing one asserts a fact about the
    filesystem that was never tested: it sends the reader hunting for a file
    that is sitting exactly where the message says it is not."""
    m = CITATION_RE.match(ref)
    rest = (ref[m.end():] if m else ref).strip()
    if not rest:
        return None
    return f"{MALFORMED_CITATION} — {rest!r} is not part of a path"


def resolve_citation(plant, ref, known=None, page=None, nested=()):
    """The one reading of a cited path: (targets, line, found, problem).

    `line` is the first line the citation names, or None. Strict, the
    default (`known` None): the plant-relative reading `cite_problem` gives,
    asked of the filesystem, the line checked; `targets` holds the one path,
    `found` is `exact`, `problem` is None, or `targets` is empty and `problem`
    says why. Lenient (`known` a set of plant-relative paths): the citation
    is text matched against `known`, never opened, its line reported and not
    checked, in order plant-relative, `docs/graph/`-relative, relative to the
    directory of `page`, then under each `nested` repository, each found
    `exact`; then, for a citation holding no `/`, every path of `known` with
    that basename, found `basename` (several are the caller's ambiguity).
    Nothing found is (), line, None and a problem (SPEC-0007 §6 "Query answer")."""
    cited, raw, cited_line = split_citation(ref)
    if not raw:
        return (), cited_line, None, f"{MALFORMED_CITATION} — it names no path"
    if known is not None:
        if not raw.startswith("/"):
            tries = [raw, "docs/graph/" + raw]
            tries += [posixpath.join(posixpath.dirname(page), raw)] if page else []
            tries += [posixpath.join(n, raw) for n in nested]
            for t in tries:
                t = posixpath.normpath(t)
                if relative(t) and t in known:
                    return (t,), cited_line, "exact", None
            if "/" not in raw:
                hits = tuple(sorted(p for p in known if p.rsplit("/", 1)[-1] == raw))
                if hits:
                    return hits, cited_line, "basename", None
        return (), cited_line, None, shape_problem(cited) or MISSING_CITATION
    if Path(raw).is_absolute():
        return (), cited_line, None, MISSING_CITATION
    target = plant / raw
    try:
        target.resolve().relative_to(plant.resolve())
    except (ValueError, OSError):
        return (), cited_line, None, MISSING_CITATION
    if not target.is_file():
        return (), cited_line, None, shape_problem(cited) or MISSING_CITATION
    if cited_line:
        try:
            held = len(target.read_text(encoding="utf-8",
                                        errors="replace").splitlines())
        except OSError:
            return (), cited_line, None, MISSING_CITATION
        if cited_line > held:
            return (), cited_line, None, (f"names line {cited_line} of a file that holds "
                                          f"{held} lines")
    return (raw,), cited_line, "exact", None


def cite_problem(plant, ref):
    """Why a cited path does not resolve, as a phrase — or None when it does:
    the strict mode of `resolve_citation`.

    A citation names a real file INSIDE the plant, and the line it names is in
    that file. Anchor suffixes (`path#section`) are stripped and not checked:
    there is no cheap check for an anchor, and inventing one is a different
    job. A line suffix IS checked, because the line number is the part of a
    citation a reader actually follows — `manifest.json:999999` resolved
    against a file whose last line is 457 for as long as the suffix was
    stripped and forgotten. A directory is not a citation
    (`docs/graph/sources/` names where the evidence would live, not any
    evidence), and an absolute path is not a claim about this plant at all.

    A reference that is not a citation at all is reported as one. "This file
    does not exist" is a claim about the filesystem, and a reference that never
    parsed as a path never reached the filesystem to earn it — every shape the
    grammar did not recognise collapsed into that one phrase, and the reader
    went looking for the wrong defect."""
    return resolve_citation(plant, ref)[3]
