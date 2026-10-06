# @microsoft/signalr — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
SignalR JavaScript/TypeScript client (`HubConnectionBuilder`, `HubConnection`, `LogLevel`, etc.) for real-time hub connections against an ASP.NET Core SignalR server.

The page covers the npm package `@microsoft/signalr`. The client calls hub methods on the server and receives the server's calls to client methods, over WebSockets, Server-Sent Events or long polling. Upstream home: the ASP.NET Core SignalR docs on Microsoft Learn, with the source in the `dotnet/aspnetcore` repository. The server side belongs to [`../language/dotnet.md`](../language/dotnet.md) and, for authentication, [`../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md`](../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md).

## Install, setup and configuration
Install it with `npm install @microsoft/signalr`. With a bundler, import the builder from the package. Without one, the browser build sits in `node_modules/@microsoft/signalr/dist/browser/signalr.js` and exposes a global `signalR`; upstream also lists CDN copies.

Build a connection with `new HubConnectionBuilder()`, chain its options, and finish with `.build()`. The hub name in the URL is not case-sensitive. A hub on another origin needs an absolute URL, and the server must allow that origin through CORS.

Options passed as the second argument of `withUrl(url, options)`:

- `accessTokenFactory` (default none): returns the access token, or a promise of it. The client calls it before every HTTP request it makes.
- `transport` (default: all enabled): restrict with a bitwise OR of `HttpTransportType.WebSockets`, `ServerSentEvents` and `LongPolling`.
- `headers` (default none): extra headers on every HTTP request. In a browser they are not sent on WebSocket or Server-Sent Events requests.
- `skipNegotiation` (default `false`): skips the negotiate request. It works only when WebSockets is the only enabled transport, and not with Azure SignalR Service.
- `withCredentials` (default `true`): sends credentials on the cross-origin request. Cookie-based sticky sessions need it.
- `timeout` (default 100000 ms): applies to plain HTTP requests, not to long-poll polls, Server-Sent Events or WebSockets.
- `logMessageContent` (default off): logs message bodies.

Builder and connection settings:

- `configureLogging(LogLevel.X)`: `Error`, `Warning`, `Information` or `Trace`; `Trace` logs message data too. Output goes to the browser console.
- `withAutomaticReconnect()`: off unless called. With no argument, it waits 0, 2, 10 and 30 seconds before four attempts. An array of millisecond delays sets a custom schedule, and an object with `nextRetryDelayInMilliseconds(retryContext)` sets a policy. That method returns the next delay, or `null` to stop. `retryContext` carries `previousRetryCount`, `elapsedMilliseconds` and `retryReason`.
- `withStatefulReconnect({ bufferSize })`: buffers and replays messages across a short network drop (default buffer 100000 bytes). The server hub endpoint must also enable it.
- `connection.serverTimeoutInMilliseconds` (default 30000): with no message from the server in this window, the client closes the connection with an error. Upstream recommends at least double the server's keep-alive interval.
- `connection.keepAliveIntervalInMilliseconds` (default 15000): how often the client pings the server.

## Core API / usage shape
- Typical connection setup: `new HubConnectionBuilder().withUrl(url, { accessTokenFactory }).withAutomaticReconnect().configureLogging(LogLevel.Information).build()`.
- Core connection API: `.on(eventName, callback)`, `.off(eventName, callback?)`, `.onreconnected(callback)`, `.onclose(callback)`, `.start(): Promise<void>`, `.invoke(methodName, ...args): Promise<any>`.
- `invoke` resolves with the hub method's return value once the server finishes, and rejects when the hub method throws. `send(methodName, ...args)` resolves once the message is sent; it returns no data and no server error.
- `stream(methodName, ...args)` calls a streaming hub method.
- `off(name, handler)` needs the same function instance that was passed to `on`. `off(name)` removes every handler for that name.
- `onreconnecting(error => ...)` fires when automatic reconnect starts. `onreconnected(connectionId => ...)` fires when it succeeds. `onclose(error => ...)` fires when the connection ends for good.
- `stop()` closes the connection. `state` reports a `HubConnectionState` (`Connected`, `Reconnecting`, `Disconnected` and the transitions between). `connectionId` is `null` while disconnected and when negotiation was skipped.

The usual start shape registers handlers first and retries the first start by hand:

```ts
connection.on('ReceiveMessage', handler);
async function start() {
  try { await connection.start(); }
  catch (err) { setTimeout(start, 5000); }
}
connection.onclose(() => start()); // only for manual reconnect
start();
```

## Idioms & best practices
- Rejoin server-side groups from an `onreconnected` handler, since the reconnected connection is new to the server.
- Wire an `onclose` handler so the app can react when automatic reconnect gives up.
- Catch and manually retry `start()` failures.
- Register every `on(...)` handler before `start()`, so no message arrives before its handler. Upstream calls this a best practice.
- Make `accessTokenFactory` async and get a fresh token inside it, for example `await keycloak.updateToken(30)` and then return `keycloak.token`. Do not return a string captured at construction. Upstream says the factory runs before every HTTP request and is the place to renew the token. The token-source side is in [`keycloak-js.md`](keycloak-js.md).
- Use `onreconnecting` to warn the user and disable inputs, and `onreconnected` to enable them again.
- For a manual reconnect, call `start()` from `onclose`, with exponential back-off or a capped number of tries.
- Keep a busy tab from sleeping when the connection matters. Browsers that freeze inactive tabs can close the connection; holding a Web Lock while connected is upstream's example.

## General pitfalls
- **`onreconnected` issues a new connectionId:** the reconnected connection looks entirely new to the server; any server-side group membership from before the disconnect is lost and must be rejoined manually.
- **`withAutomaticReconnect()` does not retry the initial `start()`:** `start()` failures must be caught and retried manually by application code.
- **Automatic reconnect gives up after four attempts:** without parameters, `withAutomaticReconnect()` waits 0, 2, 10, 30 seconds for four attempts, then stops, transitions to Disconnected, and fires `onclose`. An app relying only on automatic reconnect with no `onclose` handler will not resume after the attempts are exhausted without a manual restart.
- Handlers belong to one `HubConnection` instance. Code that builds a new connection, on a manual restart or because the token source was not ready at construction, must register every handler again on the new instance. Observed in practice; a small registry of listeners in the wrapping service, replayed onto each new connection, was the fix. Upstream documents handlers per instance and says nothing about rebuilding.
- During automatic reconnect, the connection reports `Reconnecting`, not `Disconnected`, and `onclose` does not fire. Code that waits for `onclose` to detect a drop sees nothing until the attempts run out.
- `onreconnected` receives `undefined` for the connection id when negotiation is skipped.
- Common connection errors: a 404 on the WebSocket handshake usually means a wrong hub URL, or several servers without sticky sessions; a 400 or a transport error means WebSockets is off on the server; a 307 means HTTPS redirection, so use an `https` URL; status 0 or 405 points at CORS; a 413 usually means an access token over 4 KB.
- Custom `headers` never reach the server on WebSocket or Server-Sent Events requests from a browser. Authentication there goes through `accessTokenFactory`.

## Testing
Upstream documents no testing guidance for the JavaScript client, and none was observed in practice. For connection problems, upstream's advice is to collect client logs (`LogLevel.Trace`) together with the server logs.

## Security defaults
- On WebSocket and Server-Sent Events transports, the browser client sends the access token as the `access_token` query-string parameter, because browser APIs cannot set an `Authorization` header there. Upstream rates this about as safe as the header over HTTPS. The server must read the token from the query on the hub path, and URL logging can record it. [`../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md`](../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md) owns the server-side reading and the log filtering. A reverse proxy can add the header instead.
- Always use HTTPS. The token in the URL is protected only by the transport.
- Cross-origin connections are refused unless the server's CORS policy allows the origin with credentials. CORS does not protect WebSockets; the server needs its own origin check for them.
- Do not expose the connection id to other users. Upstream treats it as sensitive, because on the ASP.NET Core 2 line and earlier (server or client) it lets a caller impersonate a connection.
- By default the server sends the client a generic error message, not the exception detail, when a hub method throws. Detailed errors are a server option for development only.
- Message size is capped by default (32 KB per message on the server). Raising or removing the cap lets a client make the server allocate large buffers.
- The server checks the user when the connection starts and keeps that principal for the life of the connection. A token that expires mid-connection does not close it unless the server sets `CloseOnAuthenticationExpiration` (the JwtBearer page owns that option), and role changes do not reach an open connection.

## Operational behaviour
- Startup: `start()` runs the negotiate request (unless skipped), connects over an enabled transport, and resolves when connected. It does not retry on its own.
- Keep-alive: the client pings every 15 s by default and closes after 30 s without a server message. The server side has matching settings; change both together.
- Drop with automatic reconnect: `Reconnecting`, then `onreconnected` with a new connection id, or after the last attempt `Disconnected` and `onclose`. Server-side state tied to the old id, such as groups, is gone.
- Stateful reconnect, when both ends enable it, keeps the same connection and replays buffered messages after a short drop.
- Token expiry: `accessTokenFactory` runs again on each HTTP request, including reconnects. Long-polling and Server-Sent Events connections fail on their next request without a fresh token.
- Browser tab sleeping can close connections in inactive tabs.
- Shutdown: `stop()` closes the connection and the client ends in `Disconnected`.

## Interop
- [`keycloak-js.md`](keycloak-js.md): a common source for `accessTokenFactory` tokens.
- [`../language/angular.md`](../language/angular.md): observed in practice, an Angular app wraps the connection in one injectable service that owns start, reconnect, group rejoin and handler registration, and feature code calls only that service.
- [`../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md`](../nuget/Microsoft.AspNetCore.Authentication.JwtBearer.md): server-side token validation, including the query-string token on the hub path.
- [`../language/dotnet.md`](../language/dotnet.md): the ASP.NET Core server that hosts the hubs.

## Major lines
The docs tie client features to ASP.NET Core lines, and a feature that both ends negotiate needs both ends on that line or later.

### ASP.NET Core 3.x and later
Automatic reconnect (`withAutomaticReconnect`) is part of the client; the 3-line docs already describe it. From the 3 line the secret that guards a connection is the connection token, not the connection id. Servers and clients on the 2 line and earlier used the id, and an older client may still connect, which is why the id is still kept private.

### .NET 8 and later
Stateful reconnect (`withStatefulReconnect`) is available. The server hub endpoint must enable it as well.

### .NET 11 and later
Authentication refresh. `withAuthenticationRefresh(options)` refreshes credentials on an open connection before the expiry the server reports, and `refreshAuthentication()` refreshes on demand. Each refresh calls `accessTokenFactory` again. `onAuthenticationRefreshed` and `onAuthenticationRefreshFailed` report the outcome. The server must enable the feature, and it updates the connection's roles and claims in place.

## Upstream docs
- ASP.NET Core SignalR JavaScript client (Microsoft Learn): https://learn.microsoft.com/en-us/aspnet/core/signalr/javascript-client
- Configuration (client and server options): https://learn.microsoft.com/en-us/aspnet/core/signalr/configuration
- Authentication and authorization: https://learn.microsoft.com/en-us/aspnet/core/signalr/authn-and-authz
- Security considerations: https://learn.microsoft.com/en-us/aspnet/core/signalr/security
- Troubleshoot connection errors: https://learn.microsoft.com/en-us/aspnet/core/signalr/troubleshoot
- JavaScript API reference (`HubConnection`): https://learn.microsoft.com/en-us/javascript/api/@microsoft/signalr/hubconnection
- npm: https://www.npmjs.com/package/@microsoft/signalr
- Source: https://github.com/dotnet/aspnetcore/tree/main/src/SignalR
