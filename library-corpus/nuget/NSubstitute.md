# NSubstitute — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A mocking library for .NET unit tests. It creates substitutes for interfaces
and virtual members and configures them through direct calls on the substitute
itself, rather than through a lambda/expression-tree DSL — a stub reads like
the call it replaces, and a verification reads like an assertion about that
call.

## Core API / usage shape
- `Substitute.For<T>()` creates the substitute; it is used wherever the real
  collaborator would be injected.
- `Arg.Any<T>()` and `Arg.Is<T>(predicate)` express argument matching, both
  when stubbing a call and when verifying one.
- `.Returns(value)` stubs a call's result; overloads accept a factory for
  results computed from the received arguments.
- `.Received()` and `.DidNotReceive()` verify that a call happened (optionally
  a given number of times) or did not.

## Idioms & best practices
- Substitute collaborators at a real seam (an interface the design already
  has), not around incidental internals.
- Verify the arguments a call carried, not merely that it was made.

## General pitfalls
- A bare `Received()` count assertion can pass vacuously: it is satisfied by
  *any* call to the member, whatever its arguments. If the call the test meant
  to pin is replaced by an incidental or wrong one, the count still matches and
  the assertion stays green while the behavior it was written to protect is
  gone — which is why the idiom above asserts the arguments the call carried.
  The general rule against citing a vacuous pass is the
  kernel's §3.5 `verify` (green-lie clause), not this library's to restate.

## Upstream docs
- https://nsubstitute.github.io/
- https://github.com/nsubstitute/NSubstitute
- https://www.nuget.org/packages/NSubstitute
