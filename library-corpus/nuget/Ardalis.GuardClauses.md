# Ardalis.GuardClauses — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
An input-validation ("fail fast") library for .NET. Guard clauses check for
invalid state at the beginning of a method and throw immediately, simplifying
downstream logic. The package id is `Ardalis.GuardClauses` and the namespace
`Ardalis.GuardClauses`. Licence: MIT. It targets .NET Standard 2.0 and 2.1 and
current .NET, and declares no runtime package dependencies.

## Install, setup and configuration
- `dotnet add package Ardalis.GuardClauses`, then
  `using Ardalis.GuardClauses;`.
- There is no configuration and no registration. `Guard.Against` is a static
  singleton `IGuardClause`, and every guard is an extension method on it.

## Core API / usage shape
- The canonical entry point is the fluent `Guard.Against.*` surface:
  - `Null` (throws `ArgumentNullException`);
  - `NullOrEmpty` (string, `Guid`, or `IEnumerable<T>`), `NullOrWhiteSpace`,
    and `Empty` / `WhiteSpace` for `ReadOnlySpan<char>`;
  - `Default` (the type's default value);
  - `Zero`, `Negative`, `NegativeOrZero` (int, long, decimal, float, double,
    `TimeSpan`);
  - `OutOfRange`, `NullOrOutOfRange`, `EnumOutOfRange`, `OutOfSQLDateRange`,
    `LengthOutOfRange`, `StringTooShort`, `StringTooLong`;
  - `InvalidFormat` (regular expression), `InvalidInput` and
    `NullOrInvalidInput` (predicate), `Expression` / `ExpressionAsync`;
  - `NotFound(key, value)` (throws `NotFoundException`).
- Guards throw on invalid input and otherwise return the validated value, so
  they can be used inline (e.g. `_name = Guard.Against.NullOrEmpty(name)`).
- Most overloads take an optional parameter name and an optional custom
  message (`Guard.Against.Null(v, nameof(v), "msg")`). The parameter name
  defaults to the argument expression through `[CallerArgumentExpression]`,
  so `Guard.Against.Null(order)` reports `order` without `nameof`. The
  exceptions: `Expression` and `ExpressionAsync` require the message;
  `InvalidInput`, `NullOrInvalidInput`, `Empty` and `WhiteSpace` require the
  parameter name and do not capture it from the argument expression; `NotFound`
  takes no custom message.
- Every current guard also takes an optional `exceptionCreator: () => new
  MyException(...)`. When given, the guard throws that exception instead of
  the default one.
- Null guards carry `[NotNull]`, so after `Guard.Against.Null(x)` the compiler's
  nullable analysis treats `x` as non-null.
- Most validations throw `ArgumentException`-family exceptions
  (`ArgumentNullException` for null, `ArgumentOutOfRangeException` for ranges);
  `Guard.Against.NotFound` throws `NotFoundException`, which derives directly
  from `Exception`.
- Custom guards: write an extension method on `IGuardClause` in the
  `Ardalis.GuardClauses` namespace and it appears on `Guard.Against` wherever
  the package is imported.

## Idioms & best practices
- Put guards at the top of a method/constructor to establish invariants before
  any real work runs.
- Prefer the validated return value over re-referencing the raw argument.
- Assign constructor arguments through guards
  (`_quantity = Guard.Against.NegativeOrZero(quantity)`), so an object cannot be
  built in an invalid state.
- Use `NotFound` for a lookup result that came back null. The distinct
  exception type lets an error-handling layer map it to "not found" instead of
  "bad request". The mapping itself is yours: the library ships no handler.
- Keep domain-specific guards as extension methods in the
  `Ardalis.GuardClauses` namespace, not in a parallel helper class.

## General pitfalls
- Opposite polarity: `Guard.Against.Expression(func, input, message)` throws
  when `func` returns **true** (the function describes the invalid state).
  `InvalidInput(input, name, predicate)` throws when `predicate` returns
  **false** (the predicate describes the valid state). The older
  `AgainstExpression` was the reverse of `Expression`: it threw when the
  function returned false. It is obsolete, and its obsolete message warns about
  the reversed logic. Read which one you are calling.
- `NullOrEmpty` on a lazy `IEnumerable<T>` calls `Any()`, which starts the
  enumeration. The guard returns the same sequence, so the caller's own pass
  runs the query again. Materialize first when that matters.
- Upgrading only some projects in a solution can fail at run time with
  `MissingMethodException`. The cause is a binary break between the 4.x and
  5.x lines (see Major lines). It compiles cleanly and fails only when the guard
  runs.
- `NotFoundException` is not an `ArgumentException`. A handler that maps only
  `ArgumentException` to a client error turns it into a server error.

## Testing
- Test that a method rejects bad input by asserting the exception type and
  `ParamName` (for example with `Assert.Throws<ArgumentNullException>` in
  xunit). The parameter name comes from the argument expression unless you pass
  one.
- Upstream documents no test helpers. The repository's unit tests cover each
  guard and are the reference for edge cases.
- When you supply a custom message, tests that assert on message text change.
  Upstream noted this for the 4.x line, where custom messages became
  consistent.

## Security defaults
- Upstream documents no security surface. The library runs no I/O and holds no
  state. Default exception messages name the parameter, and
  `NotFoundException` also includes the key it was looked up by, so do not
  return raw exception messages to untrusted clients.

## Operational behaviour
- Guards are static checks with no startup, shutdown or resources. The only runtime effect is the exception thrown on invalid input.

## Interop
- Works with any .NET code and has no framework coupling. Mapping its
  exceptions to HTTP responses belongs in the host's exception handling (see
  the `NotFound` idiom above).
- Its `[NotNull]` annotations feed the C# nullable analysis, so guarded values
  need no `!` afterwards.

## Major lines

### 4.x line
- `OutOfRange` for enums is renamed `EnumOutOfRange`.
- `[CallerArgumentExpression]` support arrives, so the parameter name becomes
  optional.
- Custom error messages apply consistently, which can break tests that assert
  on message text.
- `AgainstExpression` is replaced by `Expression` with reversed logic.

### 5.x line
- Exists to mark a binary break that first shipped late in the 4.x line: the
  optional `exceptionCreator` parameter changed the method signatures. Code
  compiled against an earlier 4.x release fails with `MissingMethodException`
  when it runs against the new signatures, typically when a library
  references an old 4.x release and the application references 5.x. Upstream
  advice: keep every project in the solution on the same side of the break.

## Upstream docs
- https://github.com/ardalis/GuardClauses
- https://github.com/ardalis/GuardClauses/blob/main/README.md
- https://github.com/ardalis/GuardClauses/releases
- https://github.com/ardalis/GuardClauses/issues/354 (the binary break between
  the 4.x and 5.x lines)
- https://www.nuget.org/packages/Ardalis.GuardClauses
