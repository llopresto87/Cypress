# Swashbuckle.AspNetCore — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`Swashbuckle.AspNetCore` generates OpenAPI (Swagger) documents from an
ASP.NET Core application's endpoints and serves them as JSON, together with an
embedded swagger-ui. The packages:

- `Swashbuckle.AspNetCore`: the NuGet package id, a metapackage over the three
  core packages that follow.
- `Swashbuckle.AspNetCore.Swagger`: serves the documents through an
  `ISwaggerProvider`.
- `Swashbuckle.AspNetCore.SwaggerGen`: the generator, which implements
  `ISwaggerProvider`.
- `Swashbuckle.AspNetCore.SwaggerUI`: the embedded swagger-ui.
- `Swashbuckle.AspNetCore.Annotations`: an add-on.
- `Swashbuckle.AspNetCore.Newtonsoft`: an add-on.
- `Swashbuckle.AspNetCore.ReDoc`: an add-on.
- `Swashbuckle.AspNetCore.Cli`: an add-on tool.

The object model comes from `Microsoft.OpenApi`. Source:
`domaindrivendev/Swashbuckle.AspNetCore`. Licence: MIT.

## Install, setup and configuration
- `dotnet add package Swashbuckle.AspNetCore`, or only the core packages you
  need.
- Register the generator with `builder.Services.AddSwaggerGen(o => o.SwaggerDoc("v1", new OpenApiInfo { Title = ..., Version = "v1" }))`.
  The generator reads ASP.NET Core's `ApiExplorer`. `AddMvc()` registers it;
  `AddMvcCore()` needs `.AddApiExplorer()`, and Minimal APIs need
  `AddEndpointsApiExplorer()`.
- Expose the document with `app.MapSwagger()` (endpoint routing) or
  `app.UseSwagger()` (middleware). The default route is
  `/swagger/{documentName}/swagger.json`; `RouteTemplate` changes it.
- Add the UI with `app.UseSwaggerUI(o => o.SwaggerEndpoint("v1/swagger.json", "My API V1"))`.
  It is served under `/swagger` by default; `RoutePrefix` changes it.
- The document format is set on the Swagger middleware through
  `OpenApiVersion` (`OpenApi2_0`, `OpenApi3_0`, and on the 10.x line
  `OpenApi3_1`). OpenAPI 3.0 is the default.
- Schemas follow `System.Text.Json` by default. A Newtonsoft.Json application
  adds `Swashbuckle.AspNetCore.Newtonsoft` and calls
  `AddSwaggerGenNewtonsoftSupport()`.
- XML comments: set `<GenerateDocumentationFile>true</GenerateDocumentationFile>`
  in the project and call `o.IncludeXmlComments(assembly)` once per assembly
  that carries comments. Add `1591` to `NoWarn` if the missing-comment
  warnings are unwanted.

## Core API / usage shape
- `SwaggerGenOptions`: `SwaggerDoc(name, info)` per document,
  `DocInclusionPredicate(...)` to choose which actions go into which document,
  `CustomSchemaIds(type => ...)`, `CustomOperationIds(...)`,
  `MapType<T>(() => schema)`, `IgnoreObsoleteActions()`,
  `AddSecurityDefinition(...)`, `AddSecurityRequirement(...)`.
- Filters extend the generator: `ISchemaFilter`, `IOperationFilter`,
  `IDocumentFilter`, and request-body filters (with async variants such as
  `IRequestBodyAsyncFilter`), registered with `o.SchemaFilter<T>()`,
  `o.OperationFilter<T>()` and the matching methods for the other kinds.
- `SwaggerOptions.PreSerializeFilters` change the document per request (a
  server URL from the request, for example).
- `SwaggerUIOptions`: `SwaggerEndpoint` per document, `RoutePrefix`,
  `DocumentTitle`, `DisplayOperationId()`, and the `OAuth*` settings for
  swagger-ui's OAuth 2.0 flows (`OAuthClientId`, `OAuthScopes`,
  `OAuthUsePkce`, ...).
- CLI: `swagger tofile --output <file> <startup assembly> <doc name>` writes a
  document without running a server. It loads your startup assembly, so the
  .NET SDK must match the app's target framework. A class
  `SwaggerHostFactory` with `public static IHost CreateHost()` lets the tool use
  your own host setup.

## Idioms & best practices
- Use attribute routing and explicit `[From*]` bindings. A parameter with no
  binding attribute is described as a query parameter, and conventionally
  routed controllers do not appear at all.
- Set `operationId`s on purpose (route names or `CustomOperationIds`) when
  clients are generated from the document; Swashbuckle omits them by default.
- When two types share a name in different namespaces, set
  `CustomSchemaIds(t => t.FullName)` or another unique strategy.
- Keep swagger-ui URLs relative to its `RoutePrefix`, so the UI works behind a
  reverse proxy or a virtual directory. Use the Forwarded Headers middleware
  for proxy headers; Swashbuckle does not read `X-Forwarded-*` itself.
- Generate the document in CI with the CLI tool, pinned in a local tool
  manifest, and publish or diff the file there.
- Before you add Swashbuckle to a new project, decide between it and the
  built-in `Microsoft.AspNetCore.OpenApi` (`AddOpenApi` / `MapOpenApi`). The
  web API templates from .NET 9 on use the built-in package.

## General pitfalls
- "Conflicting schemaIds": two types with the same short name throw at
  generation time, often only when the document is first requested.
- From .NET 9 on, the project templates do not bundle Swashbuckle. That is a statement
  about template defaults, not about the package's viability: Microsoft's
  announcement removing it from the templates cited slow maintenance at the
  time, and the package has since shipped new major lines. A project that
  wants Swashbuckle references it explicitly instead of assuming a template
  put it there.
- Observed in practice: NSwag-based stacks (for example a web framework's own
  Swagger integration) expose lookalike names such as `UseSwaggerGen` and
  `AddSwaggerDocument`. A pinned `Swashbuckle.AspNetCore` with no
  `AddSwaggerGen` call anywhere in the code was a dead pin. Search for the
  real Swashbuckle API before assuming the package is in use. Upstream does
  not address this.
- Filters that touch `Microsoft.OpenApi` types break at compile time across
  the 9.x to 10.x boundary (see Major lines). Other libraries that depend on
  `Microsoft.OpenApi` 1.x block that upgrade.
- swagger-ui files are cached by browsers; after an upgrade, a stale cache
  can show a broken UI.

## Testing
- Upstream's own test suite snapshots the generated document as JSON. A
  project can do the same: fetch `/swagger/v1/swagger.json` from a test host,
  or write it with the CLI, and compare it with a committed file so a contract
  change shows up in review.
- Test custom filters against the document they produce, not against
  Swashbuckle internals.

## Security defaults
- Nothing is protected by default: `UseSwagger` and `UseSwaggerUI` serve the
  API description and an interactive client to anyone who can reach the
  route. Microsoft's guidance registers them only in the `Development`
  environment. When they must run elsewhere, put the routes behind
  authorization.
- `OAuthClientSecret` hands a client secret to swagger-ui in the browser.
  swagger-ui's own docs say never to use it in production. Use a public client
  with `OAuthUsePkce()` instead.
- The document can reveal internal endpoints and model fields. Use
  `DocInclusionPredicate`, `[ApiExplorerSettings(IgnoreApi = true)]` or a
  document filter to keep them out.

## Operational behaviour
- Documents are generated in process from `ApiExplorer` metadata when they are
  requested, so generation errors surface on that request, not at startup.
  The UI is static files embedded in the package.
- There is no background work, external connection or persistent state. The
  CLI loads the startup assembly and builds a host from it, so startup code
  that needs a database or secrets must tolerate that, or the app supplies a
  `SwaggerHostFactory`.

## Interop
- `Microsoft.OpenApi` supplies the document model; its major line is bound to
  Swashbuckle's (1.x up to Swashbuckle 9.x, 2.x from 10.x).
- `Microsoft.AspNetCore.OpenApi` is the built-in alternative. On the 10.x line,
  Swashbuckle does not support its `WithOpenApi()` extension.
- NSwag is a separate generator with its own UI middleware and client
  generators; do not mix the two in one pipeline.
- Annotations (`[SwaggerOperation]`, `[SwaggerResponse]`, ...) need the
  `Swashbuckle.AspNetCore.Annotations` package and `o.EnableAnnotations()`.

## Major lines

### 6.x line
- Targets .NET Standard 2.0, so it also runs on older ASP.NET Core. The line
  starts by removing Swashbuckle's own `X-Forwarded-*` handling in favour of the
  Forwarded Headers middleware, and the obsolete `DescribeAllEnumsAsStrings`
  settings.

### 7.x line
- Adds .NET 9 support and drops .NET (Core) versions before 8, except 6.

### 8.x line
- Drops `net6.0`. The .NET Standard 2.0 build moves to ASP.NET Core 2.3.
  `SerializeAsV2` becomes obsolete in favour of `OpenApiVersion`, and the CLI's
  `--serializeasv2` gives way to `--openapiversion`. Needs a newer swagger-ui,
  so clear browser caches after the upgrade.

### 9.x line
- Targets `net8.0` and `net9.0` only; .NET Standard and .NET Framework are
  gone. Removes every member that earlier lines marked `[Obsolete]`, including
  `SerializeAsV2` and the CLI's `--serializeasv2`. Upstream advises moving to
  the last 9.x release before going to 10.x.

### 10.x line
- Depends on `Microsoft.OpenApi` 2.x and can emit OpenAPI 3.1 (opt-in through
  `OpenApiVersion = OpenApiSpecVersion.OpenApi3_1`; 3.0 stays the default).
  Targets `net8.0`, `net9.0` and `net10.0`.
- Breaking for custom filters: `Microsoft.OpenApi.Models` becomes
  `Microsoft.OpenApi`; filters receive interfaces such as `IOpenApiSchema` and
  must cast to the concrete type to mutate; `$ref`s use `*Reference` classes;
  `OpenApiSchema.Type` is the `JsonSchemaType` flags enum and nullability is
  `JsonSchemaType.Null` OR-ed in; `AddSecurityRequirement` takes a
  `Func<OpenApiDocument, OpenApiSecurityRequirement>`.

## Upstream docs
- https://github.com/domaindrivendev/Swashbuckle.AspNetCore (README and `docs/`)
- https://github.com/domaindrivendev/Swashbuckle.AspNetCore/blob/master/docs/migrating-to-v10.md
- https://github.com/domaindrivendev/Swashbuckle.AspNetCore/releases
- https://learn.microsoft.com/aspnet/core/tutorials/getting-started-with-swashbuckle
- https://learn.microsoft.com/aspnet/core/fundamentals/openapi/overview
- https://www.nuget.org/packages/Swashbuckle.AspNetCore
