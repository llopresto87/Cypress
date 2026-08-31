# FluentValidation.DependencyInjectionExtensions — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The DI-container wiring for FluentValidation. It discovers `AbstractValidator<T>`
classes by scanning assemblies and registers them in
`Microsoft.Extensions.DependencyInjection` so they can be constructor-injected.
Validators registered this way are typically **consumed by a pipeline or
decorator step** that runs them before a handler, rather than being called
directly from the code being validated.

## Core API / usage shape
- Registration: `services.AddValidatorsFromAssembly(assembly, includeInternalTypes: true)`
  — one call per assembly that contains validators; the internal-types flag is
  needed when validators are not public.
- Author validators as ordinary classes:
  `class XValidator : AbstractValidator<X> { public XValidator() { RuleFor(x => x.Prop)...; } }`.
  The rule chain is the whole surface — the class carries no framework plumbing.
- `RuleForEach` validates each element of a collection property; `ChildRules`
  (and dedicated child validators) handle nested objects, so a composite request
  is validated by composing validators rather than by flattening the rules.
- Consumption point: a pipeline behavior, decorator, or action filter resolves
  `IEnumerable<IValidator<T>>` from the container and runs them before the
  handler, turning failures into a single uniform error response.
- Resolving `IEnumerable<IValidator<T>>` (not a single `IValidator<T>`) is the
  robust shape — it tolerates zero validators and multiple validators for the
  same type without a resolution error.

## Idioms & best practices
- Keep validation in one composition point (the pipeline step) so every request
  is validated the same way and no handler can forget to call it.
- Let the validator own the shape rules and leave business-invariant checks to
  the domain; a validator that needs to query state is a sign the check belongs
  deeper.

## General pitfalls
- **Registration is by exact declared generic type:** a validator is registered
  as `IValidator<X>` for the `X` it literally declares. A request that flows
  through the pipeline under a base class or interface type resolves
  `IValidator<TBase>` — which nothing registered — so the concrete type's
  validator never runs. Nothing throws; validation is simply skipped, and the
  request reaches the handler looking validated. Polymorphic dispatch and
  scan-based validator registration do not compose for free.

## Upstream docs
- https://docs.fluentvalidation.net/en/latest/
- https://github.com/FluentValidation/FluentValidation
- https://www.nuget.org/packages/FluentValidation.DependencyInjectionExtensions
