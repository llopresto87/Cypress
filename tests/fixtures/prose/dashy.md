# Release notes

The parser reads the header first — the body follows once the length is known.

A short read returns an error — the caller retries with a larger buffer.
