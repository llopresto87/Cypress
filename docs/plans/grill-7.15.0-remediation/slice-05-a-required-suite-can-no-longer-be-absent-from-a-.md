### Slice 5 — A required suite can no longer be absent from a green gate (U-26)

**Tier:** T2. **Invariant:** V1, V2.

`tests/test_agent_lint.py` needed third-party `pytest`. Since 7.15.0 `run.sh`
probed for it and announced loudly when missing — but announcing is not failing,
and the gate still exited 0 with a mandatory suite unexecuted. Ported to stdlib
`unittest`, matching `tests/test_graph_lint.py` beside it, which was already
stdlib for this exact reason. 45 tests before, 45 after, the one conditional skip
preserved. Verified to run with no `pytest` on `PATH`.

This removed the question rather than answering it: the alternative — requiring
CI to install `pytest` — would have added an environment dependency to satisfy a
rule the seed already has ("no third-party import in any shipped script").
