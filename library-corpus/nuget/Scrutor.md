# Scrutor — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
An extension of `Microsoft.Extensions.DependencyInjection` that adds two things
the built-in container lacks: **assembly-scanning auto-registration** and
**decorator wrapping**. It removes the one-`AddScoped`-line-per-type boilerplate
of a conventional service layer, and lets cross-cutting concerns be layered
around a service without introducing a mediator library.

## Core API / usage shape
- Scanning registration:
  `services.Scan(scan => scan.FromAssemblies(...).AddClasses(c => c.AssignableTo(typeof(IX<,>))).AsImplementedInterfaces().WithScopedLifetime())`.
  The chain reads as: which assemblies, which classes, registered as what, with
  which lifetime.
- `AssignableTo(typeof(IX<,>))` matches open generic interfaces, which is what
  makes convention-based handler/service families registrable in one statement.
- `AsImplementedInterfaces()` / `AsSelf()` choose the service key(s) the
  implementation is resolvable under; the lifetime clause is separate and
  explicit.
- `services.Decorate<TService, TDecorator>()` wraps an already-registered
  service, which is the idiomatic way to build a cross-cutting pipeline — for
  example validation-then-logging around a handler — without a mediator.
- `TryDecorate<TService, TDecorator>()` is the safe variant of the same call: it
  no-ops when the target service is not registered instead of throwing, which
  matters when decorators live in an optional composition module.

## Idioms & best practices
- Keep scanning rules narrow and convention-backed (a marker interface, an open
  generic), so registration is explainable from the type's shape.
- Register the base service first, then apply decorators in a single, ordered,
  commented block — the order is behavior, not formatting.

## General pitfalls
- **Silent non-registration and order-sensitive decoration:** scanning matches by
  exact interface plus assembly, so a type placed in an unscanned assembly, or
  named/shaped so it no longer matches the predicate, is simply not registered —
  there is no error at startup, only a resolution failure (or a wrong default)
  later, far from the cause. Separately, decorator registration **order is
  significant**: each `Decorate` call wraps whatever is currently registered, so
  the sequence determines which concern sits outermost and therefore which one
  sees the call first and the exceptions last. Pin the nesting direction with a
  test that asserts the observed order rather than assuming it.

## Upstream docs
- https://github.com/khellang/Scrutor
- https://www.nuget.org/packages/Scrutor
