# Bogus — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Bogus is a fake-data generator for .NET, a port of faker.js. It produces
realistic random data (names, addresses, companies, text, dates, numbers,
internet values) for tests, database seeding and demos, in many locales.
Licence: MIT. A separate, paid Bogus Premium package adds extra data sets;
the open-source package does not need it.

## Install, setup and configuration
- `dotnet add package Bogus`. It targets .NET Standard 2.0 (and older .NET
  Standard and .NET Framework versions), so it runs on any current .NET.
- Locale: `new Faker("de")`, `new Faker<T>("fr")`, or a data set with
  `new Bogus.DataSets.Lorem(locale: "ko")`. The default locale is `en`.
- `Faker.DefaultStrictMode` sets the strict-mode default for every
  `Faker<T>`; it is `false` unless set.
- Global seed: `Randomizer.Seed = new Random(n)`. Local seed:
  `Faker<T>.UseSeed(n)`, or `Random = new Randomizer(n)` on a `Faker` or a
  data set. A local seed makes the instance ignore the global one.
- Time reference: `Faker<T>.UseDateTimeReference(dateTime)` or
  `DateTimeReference` on a `Faker` anchors `Date.Past`, `Date.Soon` and the
  other relative date methods. Without it they are relative to the current
  clock.

## Core API / usage shape
- `new Faker()` is a facade over categorized data sets: `Random`, `Name`,
  `Person`, `Address`, `Company`, `Commerce`, `Internet`, `Lorem`, `Date`,
  `Finance`, `Phone`, `Image`, `System`, `Vehicle`, `Database` and more.
  For example `Random.Int(min, max)`, `Random.Bool(weight)`,
  `Random.Guid()`, `Company.CompanyName()`, `Lorem.Word()`,
  `Lorem.Words(n)`, `Lorem.Sentence(wordCount)`, `Lorem.Paragraph()`.
- `faker.PickRandom<T>(...)` selects from a set or an enum;
  `faker.Make<T>(count, () => ...)` produces a list; `MakeLazy` produces a
  deferred sequence.
- `Faker<T>` builds strongly typed object generators with fluent rules:
  `RuleFor(x => x.Prop, f => ...)`, or `(f, x) => ...` to use properties set
  by earlier rules. `CustomInstantiator(f => new T(...))` builds objects that
  need constructor arguments, `FinishWith((f, x) => ...)` runs after all rules,
  and `Rules((f, x) => { ... })` sets several properties in one action.
- `Generate()` returns one object, `Generate(n)` a list, `GenerateLazy(n)`
  and `GenerateForever()` deferred sequences.
- `RuleSet("name", set => ...)` defines named variants;
  `Generate("name,default")` picks them.
- `StrictMode(true)` demands a rule for every property and public field;
  `AssertConfigurationIsValid()` checks that on demand, which suits a unit
  test of the faker itself.
- Extension methods in `Bogus.Extensions` add `OrNull(f, probability)`, which
  makes a value null with the given probability, plus country-specific
  identifiers in namespaces such as `Bogus.Extensions.Brazil`.
- A subclass of `Faker<T>` that calls `RuleFor` in its constructor packages a
  reusable generator.

## Idioms & best practices
- Prefer a local seed (`Faker<T>.UseSeed`) over the global `Randomizer.Seed`.
  The README rates the global seed "not so good for unit tests".
- Append new generation rules last, and avoid changing existing ones, so
  adding a rule does not shift the random sequence for the existing ones.
- Assert that a generated value exists or has a shape, not that it equals a
  literal (`NotBeNullOrWhiteSpace`, not `Be("Bike")`, in the README's
  FluentAssertions examples). Literal values change
  when locales or the library change.
- Set both a seed and a date-time reference when the test needs dates to
  repeat.
- Use `StrictMode(true)` on fakers for types that grow, so a new property
  without a rule fails loudly.

## General pitfalls
- Setting `Randomizer.Seed` globally couples determinism across every generator
  in the process for the whole program run, so one test's seeding can perturb
  another's.
- A `Randomizer` captures the global seed when it is constructed. Setting
  `Randomizer.Seed` after a `Faker` exists does not change that faker; set it
  first, or use local seeds.
- `UseSeed` changes the `Faker<T>` instance it is called on. A `Faker<T>`
  shared between parallel tests and re-seeded per test is shared mutable
  state; `Clone()` gives each test its own copy.
- `Rules(...)` cannot be combined with `StrictMode(true)`, because the
  library cannot tell which properties a bulk action sets.
- Generators that emit third-party URLs (`Internet.Avatar()`, the `Image`
  placeholder methods) point at hosts that upstream changes between releases,
  when a service shuts down. Never assert on the host or shape of a generated
  URL, and do not let tests fetch them.
- `MakeLazy`, `GenerateLazy` and `GenerateForever` are deferred: values are
  only repeatable once materialized, for example with `ToList()`.

## Testing
- Unit-test a `Faker<T>` with `AssertConfigurationIsValid()` under strict
  mode, so a model change that leaves a property without a rule fails one
  focused test.
- For repeatable fixtures, seed locally and fix the date-time reference; for
  broad coverage, leave the seed off and assert only shape.

## Security defaults
- Values come from `System.Random`, which is not cryptographically secure.
  Never use Bogus output as a password, token, key or other secret.
- Generated personal-looking data (names, emails, national identifiers) is
  synthetic. Generated emails (`Internet.Email()`) use real mail domains and
  can be real addresses. Use `Internet.ExampleEmail()` (`@example.com`) where
  a test system could send mail.

## Operational behaviour
- Everything runs in process with bundled locale data; no network calls are
  made, apart from what consuming code does with generated URLs.
- Every `Randomizer` call takes one process-wide lock around the random
  source. Bogus is safe to call from many threads, but heavy parallel
  generation serializes on that lock.
- A `Faker<T>` reads the members of `T` through its binder once, in its
  constructor, and reuses them, so create a faker once and call `Generate`
  many times.

## Interop
- EF Core seeding: generate entities with `Faker<T>` and add them to the
  context (upstream ships an EF Core seeding example;
  `Microsoft.EntityFrameworkCore.md`).
- Test frameworks: build fakers in fixtures or test-class fields
  (`xunit.md`); assertions on shape fit any assertion library
  (`Shouldly.md`).
- Many locales come from faker.js data, so locale coverage matches faker.js.

## Major lines
Bogus treats a change to deterministic outputs as a breaking change. A new
major version may change the values a seed produces (locale data refreshed
from faker.js, bug fixes), while patch releases keep them. Stay within one
major line where tests compare seeded values, and expect to refresh such
expectations on a major upgrade. Upstream publishes no other per-line
surface difference that a page could list here.

## Upstream docs
- https://github.com/bchavez/Bogus
- https://github.com/bchavez/Bogus/blob/master/README.md
- https://github.com/bchavez/Bogus/blob/master/HISTORY.md
- https://www.nuget.org/packages/Bogus
