# Aspire.Hosting.AppHost — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The .NET Aspire distributed-application orchestrator. An AppHost project
declares the whole composition of a distributed app — services, containers,
and their dependencies — as a single resource graph, and drives local/dev
composition from it (starting resources, wiring them together, and surfacing
them in the Aspire dashboard). It is a composition host, not a runtime
library the services themselves reference.

## Core API / usage shape
- `DistributedApplication.CreateBuilder(args)` is the entrypoint; the AppHost
  is an ordinary executable whose `Program` builds and runs the application.
- `AddProject<T>()` adds a .NET project in the solution as a resource;
  `AddContainer()` adds a container image as a resource. Together they compose
  the resource graph.
- Resource references wire by name: declaring that one resource references
  another injects the dependency's connection information into the dependent
  as environment variables, so consuming code reads configuration rather than
  hard-coded addresses.
- `builder.ExecutionContext.IsPublishMode` distinguishes publish-mode (emitting
  a deployment manifest) from run-mode (local composition), so the graph can
  branch — e.g. run a real container locally but reference a managed service
  when publishing.
- A companion package, `Aspire.Hosting.Testing`, can boot the whole resource
  graph in-process, letting integration tests exercise real wired-up resources
  instead of stubs.

## Idioms & best practices
- Keep the AppHost declarative: it describes what exists and what depends on
  what, and leaves per-service behavior to the services themselves.
- Prefer resource references over hand-written connection strings so the
  injected environment stays the single source of wiring truth.

## General pitfalls
- The Aspire dashboard exposes a per-resource environment-variable view. Since
  references are injected as environment variables, that view can reveal
  downstream secrets (connection strings, keys) to anyone who can reach the
  dashboard. Treat dashboard access as sensitive and scope it accordingly.

## Upstream docs
- https://learn.microsoft.com/en-us/dotnet/aspire/
- https://github.com/dotnet/aspire
- https://www.nuget.org/packages/Aspire.Hosting.AppHost
