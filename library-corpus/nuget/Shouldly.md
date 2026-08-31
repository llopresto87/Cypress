# Shouldly — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A fluent assertion library for .NET tests, used in place of a framework's
native `Assert` API. Assertions are extension methods read left-to-right off
the value under test, and failure messages echo the asserting expression along
with the actual value — so a failure names what was being checked, not just
that two values differed.

## Core API / usage shape
- `ShouldBe` for equality (with collection and tolerance overloads);
  `ShouldNotBeNull` for presence.
- `ShouldContain` for membership, including a predicate overload that asserts
  at least one element satisfies a condition.
- `ShouldAllBe(predicate)` asserts every element of a collection satisfies a
  condition; `ShouldHaveSingleItem()` asserts exactly one element and returns
  it for further assertions.
- `ShouldThrow<T>()` asserts that a delegate throws a given exception type and
  returns the exception for follow-up assertions.

## Idioms & best practices
- Assert the narrowest true statement: one behavior per assertion, so a
  failure message localizes the defect.
- Chain off the value returned by `ShouldThrow<T>()` or
  `ShouldHaveSingleItem()` instead of re-fetching and re-asserting.

## General pitfalls
- `ShouldHaveSingleItem()` asserts the *whole* collection has exactly one
  element, not that exactly one element is relevant. On a collection that can
  carry incidental extra entries — stray log lines mixed into results,
  diagnostics appended alongside the real output — it fails for a reason
  unrelated to what the test meant to check. Prefer a predicate-based
  `ShouldContain` when the collection is not guaranteed to hold exactly one
  relevant entry.

## Upstream docs
- https://docs.shouldly.org/
- https://github.com/shouldly/shouldly
- https://www.nuget.org/packages/Shouldly
