# Ardalis.GuardClauses — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
An input-validation ("fail fast") library for .NET. Guard clauses check for
invalid state at the beginning of a method and throw immediately, simplifying
downstream logic.

## Core API / usage shape
- The canonical entry point is the fluent `Guard.Against.*` surface. Common
  guards include `Guard.Against.Null(...)`, `Guard.Against.NullOrEmpty(...)`,
  `Guard.Against.NullOrWhiteSpace(...)`, `Guard.Against.NegativeOrZero(...)`,
  `Guard.Against.NotFound(...)`, and `Guard.Against.Expression(...)`.
- Guards throw on invalid input and otherwise return the validated value, so
  they can be used inline (e.g. `_name = Guard.Against.NullOrEmpty(name)`).
- Most validations throw `ArgumentException`-family exceptions;
  `Guard.Against.NotFound` throws `NotFoundException`.

## Idioms & best practices
- Put guards at the top of a method/constructor to establish invariants before
  any real work runs.
- Prefer the validated return value over re-referencing the raw argument.

## General pitfalls
- `Guard.Against.Expression` has a semantics that can read as reversed from what
  the name suggests — check its behavior before relying on it.

## Upstream docs
- https://github.com/ardalis/GuardClauses
- https://github.com/ardalis/GuardClauses/blob/main/README.md
- https://www.nuget.org/packages/Ardalis.GuardClauses
