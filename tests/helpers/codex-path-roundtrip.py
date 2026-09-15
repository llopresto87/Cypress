#!/usr/bin/env python3
"""Does the Codex snippet carry --project-dir back out, byte for byte?

Split out of tests/test-seed-budgets.sh because the assertion has to PARSE the
TOML, and a heredoc inside the loop that generates it is a quoting problem
nobody should have to read. `EXPECT` is the target path; argv[1] the snippet.

The test is round-trip, not substring: a TOML basic string escapes a newline or
a tab, so grepping the file for the literal path asserted the absence of correct
escaping, and passed only because no fixture had ever contained one.
"""
import os
import sys
import tomllib

with open(sys.argv[1], "rb") as fh:
    doc = tomllib.load(fh)

want = os.environ["EXPECT"]
paths = [entry["path"] for entry in doc.get("skills", {}).get("config", [])]
if not paths:
    sys.exit("no skills.config entries in the snippet")
bad = [p for p in paths if not p.startswith(want + "/")]
if bad:
    sys.exit(f"path does not round-trip: {bad[0]!r} does not start with {want!r}")
