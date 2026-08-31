# Swashbuckle.AspNetCore — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Generates Swagger/OpenAPI documents and serves Swagger UI for ASP.NET Core APIs.

## Core API / usage shape
- Register generation with `AddSwaggerGen(...)` on the service collection and
  define documents via `SwaggerDoc(...)`.
- Customize the emitted OpenAPI through filter interfaces: `ISchemaFilter`,
  `IOperationFilter`, and `IDocumentFilter`.
- Serve the JSON document and UI in the request pipeline with `UseSwagger()` and
  `UseSwaggerUI()`.

## General pitfalls
- .NET ships its own built-in OpenAPI document generation, so the project
  templates do not necessarily bundle Swashbuckle. That is a statement about
  template defaults, not about the package's viability: a project that wants
  Swashbuckle references it explicitly rather than assuming a template put it
  there.

## Upstream docs
- https://github.com/domaindrivendev/Swashbuckle.AspNetCore
- https://www.nuget.org/packages/Swashbuckle.AspNetCore
