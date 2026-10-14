"""plant_walk: the files that belong to one plant, and nothing reached through it.

A recursive glob from a plant's root does not stop at the plant's edge. Three
kinds of directory sit under that root and are not part of it:

  * a directory holding its own `.cypress/seed.json` is another plant: a
    scratch copy, a nested seed workspace. It has its own backups and its own
    knowledge, and a walk that counts them audits the wrong plant. A graft's
    backup audit once reported a large UNMAPPED total, every entry from a copy.
  * a directory holding a seed checkout (the seed's manifest, its installer
    and its kernel source, and no stamp) is the seed, vendored or cloned
    inside the plant. Its agents, protocols and graph-shaped files are the
    seed's, and a walk that reads them as plant content counts seed prose as
    the plant's own.
  * a symlinked directory is another tree. A walk that follows it collects
    that tree's leaves as this plant's. This includes the directory being
    walked, when it is itself a link. The walk does not decide whether a cited
    path is DANGLING: source_paths.py's cite_problem still refuses a citation
    that resolves outside the plant through a symlink.

Symlinked FILES are still walked: a `--symlink` plant is made of them, because
install.sh places one link per file and never links a directory.

The root is the caller's to name and is always walked, stamp and all. Every
directory below it, including the ones on the way to `sub`, is judged by the
three rules above. Walking `sub` from the root, rather than walking `sub`
itself, is what lets a collection directory that is a symlink be skipped
while a plant root reached through a symlink is not.

Library module, no CLI. graft-audit.py and growth-audit.py load it from beside
themselves. Dependency-free.
"""
import os
from fnmatch import fnmatchcase
from pathlib import Path

STAMP_REL = ".cypress/seed.json"
# A seed checkout is recognised by its shape, every one of these files at its
# root; no single one is enough, since a plant may well hold a manifest.json
# or an install.sh of its own.
SEED_CHECKOUT_MARKERS = ("manifest.json", "install.sh", "core/AGENTS.md")


def is_seed_checkout(d: Path) -> bool:
    """True for the root of a seed checkout: it holds the seed's manifest,
    installer and kernel source together."""
    return all((d / m).is_file() for m in SEED_CHECKOUT_MARKERS)


def is_foreign(d: Path) -> bool:
    """True for a directory that is not this plant's to walk: a symlink, the
    root of another plant (it holds its own seed stamp), or a seed checkout."""
    return d.is_symlink() or (d / STAMP_REL).is_file() or is_seed_checkout(d)


def files(root, sub="", pattern="*"):
    """Every file under `root/sub` whose name matches `pattern` (case
    sensitive, as a POSIX glob is), in a stable order, skipping each foreign
    directory and everything below it. Yields nothing when `root/sub` is not a
    directory or is itself foreign."""
    top = Path(root)
    for part in Path(sub).parts:
        top = top / part
        if is_foreign(top):
            return
    if not top.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(top):
        here = Path(dirpath)
        # os.walk lists a symlinked directory among the directories; pruning
        # it here is what keeps the walk from ever entering it
        dirnames[:] = sorted(d for d in dirnames if not is_foreign(here / d))
        for name in sorted(filenames):
            if fnmatchcase(name, pattern):
                yield here / name
