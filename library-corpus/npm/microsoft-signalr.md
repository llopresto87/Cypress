# @microsoft/signalr — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
SignalR JavaScript/TypeScript client (`HubConnectionBuilder`, `HubConnection`, `LogLevel`, etc.) for real-time hub connections against an ASP.NET Core SignalR server.

## Core API / usage shape
- Typical connection setup: `new HubConnectionBuilder().withUrl(url, { accessTokenFactory }).withAutomaticReconnect().configureLogging(LogLevel.Information).build()`.
- Core connection API: `.on(eventName, callback)`, `.off(eventName, callback?)`, `.onreconnected(callback)`, `.onclose(callback)`, `.start(): Promise<void>`, `.invoke(methodName, ...args): Promise<any>`.

## Idioms & best practices
- Rejoin server-side groups from an `onreconnected` handler, since the reconnected connection is new to the server.
- Wire an `onclose` handler so the app can react when automatic reconnect gives up.
- Catch and manually retry `start()` failures.

## General pitfalls
- **`onreconnected` issues a new connectionId:** the reconnected connection looks entirely new to the server; any server-side group membership from before the disconnect is lost and must be rejoined manually.
- **`withAutomaticReconnect()` does not retry the initial `start()`:** `start()` failures must be caught and retried manually by application code.
- **Automatic reconnect gives up after four attempts:** without parameters, `withAutomaticReconnect()` waits 0, 2, 10, 30 seconds for four attempts, then stops, transitions to Disconnected, and fires `onclose`. An app relying only on automatic reconnect with no `onclose` handler will not resume after the attempts are exhausted without a manual restart.

## Upstream docs
- ASP.NET Core SignalR JavaScript client (Microsoft Learn): https://learn.microsoft.com/en-us/aspnet/core/signalr/javascript-client
- npm: https://www.npmjs.com/package/@microsoft/signalr
- Source: https://github.com/dotnet/aspnetcore/tree/main/src/SignalR
