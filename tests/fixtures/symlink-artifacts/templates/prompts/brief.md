# Brief

This directory stands for the seed's `templates/` under a `--symlink` install.
`tests/test_graph_lint.py` links a temp graph's `templates/` here, so an
artifact edge into it resolves outside the graph on disk while its path stays
inside the graph.
