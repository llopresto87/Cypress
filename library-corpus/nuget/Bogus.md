# Bogus — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A fake/test-data generator for .NET, used to produce realistic randomized data
for tests, seeding, and demos.

## Core API / usage shape
- `new Faker()` exposes categorized generators such as `Random`, `Company`,
  `Lorem`, `Internet`, etc. — e.g. `Faker.Random.Int(min, max)`,
  `Faker.Random.Bool(weight)`, `Faker.Random.Guid()`,
  `Faker.Company.CompanyName()`, `Faker.Lorem.Sentence()`, `Faker.Lorem.Word()`.
- `Faker.PickRandom<T>(...)` selects from a set; `Faker.Make<T>(count, () => ...)`
  produces a list.
- `Faker<T>` builds strongly-typed object generators with fluent rules
  (`RuleFor(...)`), and can be seeded locally via `Faker<T>.UseSeed(int)`.

## Idioms & best practices
- Prefer a local seed (`Faker<T>.UseSeed`) over the global `Randomizer.Seed`.
- Append new generation rules last, so adding rules doesn't shift the random
  sequence for existing ones.

## General pitfalls
- Setting `Randomizer.Seed` globally couples determinism across every generator
  in the process for the whole program run — easy to make one test's seeding
  perturb another.

## Upstream docs
- https://github.com/bchavez/Bogus
- https://github.com/bchavez/Bogus/blob/master/README.md
- https://www.nuget.org/packages/Bogus
