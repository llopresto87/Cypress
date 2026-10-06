# stomp-sockjs — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The client side of STOMP over WebSocket in a browser or Node.js app. The page
covers the packages that are usually installed together:

- `@stomp/stompjs`: the STOMP protocol client (STOMP 1.0, 1.1 and 1.2) for
  JavaScript and TypeScript. It publishes and subscribes through a message
  broker that speaks STOMP over WebSocket.
- `@stomp/rx-stomp`: the same client exposed as RxJS observables. It runs
  `@stomp/stompjs` underneath.
- `sockjs-client`: a WebSocket emulation with HTTP fallback transports. It is
  needed only when a raw WebSocket cannot reach the broker end to end, and it
  needs a SockJS server counterpart.
- `stompjs`: the legacy unscoped client (`Stomp.over(socket)`), unmaintained
  for years. It appears here only so that a project still on it can find its
  migration path.

Upstream home: the StompJS Family site (guides, FAQ, API docs) and the
`stomp-js/stompjs` and `stomp-js/rx-stomp` repositories; SockJS lives in
`sockjs/sockjs-client`. The client-side JWT decoder that these apps often carry
has its own page, [jwt-decode](jwt-decode.md).

## Install, setup and configuration
- Browser: `npm install @stomp/stompjs` (add `@stomp/rx-stomp` for the RxJS
  API, and `sockjs-client` only if SockJS is really needed). Browsers
  typically need no polyfills.
- `@stomp/rx-stomp` declares `@stomp/stompjs`, `rxjs` and `uuid` as peer
  dependencies, so all three must be installed by the app.
- Node.js: install a WebSocket implementation beside the client
  (`npm install @stomp/stompjs ws`) and expose it as the global `WebSocket`
  before creating the client. `TextEncoder`/`TextDecoder` must exist too.
- The current `@stomp/stompjs` lines ship ES modules (plus a UMD bundle for a
  `<script>` tag). Its guide states that CommonJS `require` is not supported.
- `@stomp/rx-stomp` is ESM-only too: its package `exports` points at the ES
  module build. A CommonJS export was added during the 2 line and reverted in
  a later 2 release, so a project that relied on it breaks on upgrade.

The client is configured through one object, passed to the constructor, to
`configure()` or to `activate()`. The settings that matter most, with their
defaults:

| Setting | Default | Meaning |
|---|---|---|
| `brokerURL` | none | The `ws://` or `wss://` URL of the broker's STOMP-over-WebSocket endpoint. |
| `webSocketFactory` | none | A function returning a WebSocket-like object (a `SockJS`, say). If both are set, the factory wins. |
| `connectHeaders` | `{}` | Headers sent in the STOMP `CONNECT` frame: `login`, `passcode`, `host`, or a custom `Authorization`. |
| `beforeConnect` | none | Called before every connect and reconnect. It may be `async`. |
| `reconnectDelay` | 5000 ms | Wait between reconnect attempts. `0` turns automatic reconnect off. |
| `reconnectTimeMode` | linear | The exponential mode doubles the delay after each attempt, capped by `maxReconnectDelay` (15 minutes by default). |
| `heartbeatIncoming` / `heartbeatOutgoing` | 10000 ms each | STOMP heartbeats. `0` turns that direction off. |
| `connectionTimeout` | 0 (none) | If set, a connection not established in time is closed and a reconnect is scheduled. |
| `discardWebsocketOnCommFailure` | `false` | Drop the socket at once on a communication failure instead of waiting for a delayed close. |
| `debug` | ignored | A logger for connection and frame traffic. |

Exponential back-off, the `beforeConnect(client)` argument and heartbeat
tolerance arrived inside the 7 line, so an early 7.x install has only the
linear reconnect.

## Core API / usage shape
Plain client:

```ts
import { Client } from '@stomp/stompjs';

const client = new Client({
  brokerURL: 'wss://example.org/ws',
  beforeConnect: async () => { client.connectHeaders = { Authorization: `Bearer ${await getToken()}` }; },
  onConnect: () => {
    client.subscribe('/topic/updates', (message) => render(JSON.parse(message.body)));
  },
  onStompError: (frame) => report(frame.headers['message']),
  onWebSocketClose: () => markDisconnected(),
});
client.activate();
client.publish({ destination: '/app/command', body: JSON.stringify(cmd) });
await client.deactivate();
```

- `activate()` connects and keeps reconnecting. `await deactivate()`
  disconnects and stops the reconnect loop; `deactivate({ force: true })`
  skips the shutdown sequence for a stale socket.
- Subscribe inside `onConnect`. It runs after the first connect and after
  every reconnect, and the plain client does not restore subscriptions on its
  own. `subscribe()` returns an object with an `id` and `unsubscribe()`.
- Bodies are strings or `Uint8Array` (`binaryBody`). JSON goes through
  `JSON.stringify` and `JSON.parse`.
- Acknowledgement defaults to the broker's automatic mode. `ack: 'client'` or
  `'client-individual'` on the subscription makes the app call `message.ack()`
  or `message.nack()`.
- Callbacks: `onConnect`, `onDisconnect` (fires only on a graceful
  disconnect), `onStompError` (a broker `ERROR` frame; a compliant broker then
  closes the connection), `onWebSocketClose` (upstream calls it the most
  reliable sign that the connection ended), `onWebSocketError`,
  `onChangeState`.

RxJS client:

```ts
import { RxStomp } from '@stomp/rx-stomp';

const rxStomp = new RxStomp();
rxStomp.configure({ brokerURL: 'wss://example.org/ws' });
rxStomp.activate();
const sub = rxStomp.watch({ destination: '/topic/updates' }).subscribe((m) => render(m.body));
rxStomp.publish({ destination: '/app/command', body: 'hello' });
```

- `watch()` returns an Observable of messages. The subscription is sent once
  the broker is connected, and it is restored after every reconnect.
- Connection state is observable too: `connected$`, `connectionState$`,
  `stompErrors$`, `webSocketErrors$`, `serverHeaders$`, and `connected()` for
  a synchronous check. Every stompjs callback except `beforeConnect` is
  exposed as an observable.
- `asyncReceipt` waits for a broker `RECEIPT` frame.

## Idioms & best practices
- Prefer a raw WebSocket (`brokerURL`). The upstream FAQ calls SockJS
  optional and reserves it for environments without WebSocket or for
  deployments that allow only HTTP transport.
- When SockJS is needed, set `webSocketFactory: () => new SockJS(url)` so each
  attempt gets a new instance. A reused SockJS object breaks automatic
  reconnect. Never configure both transports for one client.
- In an RxJS app (Angular in particular) prefer `@stomp/rx-stomp`: the FAQ
  recommends it there, because subscriptions survive reconnects without
  bookkeeping and the client can be used outside the connect lifecycle.
- The Angular guide wires the RxJS client through a DI factory that creates,
  configures and activates it, then provides it under a service token. Inject
  that token everywhere; a component that constructs its own client skips the
  shared configuration.
- Own the lifecycle. Call `deactivate()` when the owning service or component
  is destroyed, and end each `watch()` subscription (`unsubscribe()` in
  `ngOnDestroy`, or `takeUntil`). Otherwise the socket and its reconnect timer
  outlive the view.
- Keep the broker URL in configuration, not in a per-environment `if` in code.
  Derive it from the page origin where possible, so `ws`/`wss` follows the page
  scheme ([angular](../language/angular.md) owns the same-origin idiom).
- Choose heartbeat values on purpose and agree them with the broker. Very
  short intervals add server load. The Angular guide suggests starting from
  incoming `0`, outgoing `20000` when a proxy or broker needs tuning.
- Use `debug` during development only.

## General pitfalls
- A browser WebSocket handshake cannot carry custom HTTP headers. A token set
  as a request header never reaches the broker; it belongs in `connectHeaders`.
- A token read once at startup goes stale across reconnects. Refresh it in
  `beforeConnect`, which runs before each attempt.
- With the plain client, publishing or subscribing outside `onConnect` races
  the connection. After a reconnect the subscriptions are gone unless
  `onConnect` creates them again.
- Heartbeats set to `0` remove STOMP-level liveness. Observed in practice: a
  half-dead connection was then noticed only by the transport, sometimes
  minutes later. Upstream says heartbeats detect stale connections sooner at
  the cost of idle traffic.
- Setting `reconnectDelay` to `0` turns automatic reconnect off entirely.
- SockJS allows one connection per domain at a time. A second session blocks,
  and both can time out. Share one client across the app's components.
- A SockJS URL is `http(s)://`, not `ws(s)://`. The client first requests
  `<url>/info`, then uses transport sub-paths. Observed in practice: a reverse
  proxy or gateway route that forwards only the bare endpoint breaks the
  handshake. The whole sub-tree must be forwarded, with the `Upgrade` headers
  for the websocket transport.
- SockJS may not support heartbeats with every broker (FAQ).
- Observed in practice: a broker URL built from a base that already holds the
  scheme, with a hard-coded `ws://` prefix added, yields a double scheme. Keep
  the scheme in one place or out of the configuration.
- Observed in practice: an environment switch in code whose last branch
  returns `undefined` produces no socket and no error.
- Observed in practice: after a package rescope, the legacy `stompjs` can stay
  installed beside `@stomp/stompjs` while only one is imported. Check which one
  the code calls before assuming an API.
- Observed in practice: a wrapper service over the client can become dead code
  once components call the client directly. Confirm a wrapper is on the call
  path before treating it as the integration point.
- Observed in practice: a lockfile entry for `sockjs` is the SockJS server
  package (often pulled in by dev tooling), not `sockjs-client`.

## Testing
Upstream documents no testing guidance for consuming apps. Observed in
practice: a smoke check that calls the broker directly cannot see a wrong
baked host, a double scheme or a proxy route that drops the SockJS sub-paths.
Check the realtime path through the same edge the browser uses, from the page
origin.

## Security defaults
- The client sends no credentials unless `connectHeaders` carries them. An
  anonymous session is the default, so the broker's own authorization decides
  what a client may read.
- Observed in practice: committed `login`/`passcode` values such as a
  default guest account are not an auth boundary.
- Upstream's Angular guide: use `wss://` when the page is served over HTTPS.
  Observed in practice: a page served over HTTPS that opens `ws://` is blocked
  as mixed content.
- SockJS: do not connect from an `https://` page to an `http://` SockJS
  server. Cookie-based sticky sessions may fail cross-domain in browsers that
  reject third-party cookies; connect from the same parent domain.
- Observed in practice (upstream is silent): a token placed in the URL query
  string ends up in proxy and access logs. The `CONNECT` frame keeps it out of
  them.

## Operational behaviour
- Startup: `activate()` connects asynchronously. Nothing can be published
  until the connection is open; gate the first publish on `connected$` (RxJS
  client) or do it in `onConnect`.
- Reconnect: automatic, every `reconnectDelay` (linear) or with exponential
  back-off. `onConnect` fires again each time.
- Failure: a broker `ERROR` frame arrives on `onStompError` and the broker
  usually closes the connection. `onWebSocketClose` reports every loss of the
  socket. With heartbeats on, a silent peer is detected after the heartbeat
  interval plus grace.
- Shutdown: `await deactivate()` stops reconnecting. `onDisconnect` fires only
  if the broker confirms the disconnect.
- Background tabs: the `heartbeatStrategy: 'worker'` option sends heartbeats
  from a Web Worker. Upstream says this may be more reliable when the page is
  in a background tab.

## Interop
- Server side: any broker that speaks STOMP over WebSocket. Upstream names
  RabbitMQ and ActiveMQ; Spring's STOMP support is the other common server. SockJS needs a SockJS
  server, and Spring's SockJS support is one. For token auth with Spring,
  upstream points at Spring's token-based STOMP authentication guide.
- RxJS: `@stomp/rx-stomp` follows the RxJS major line; its 2 line needs RxJS 7
  ([rxjs](rxjs.md)).
- Angular: upstream recommends `@stomp/rx-stomp` with Angular and provides an
  Angular tutorial and sample.
- Identity: the token for `connectHeaders` usually comes from the app's
  identity adapter ([keycloak-js](keycloak-js.md)) or its own login flow.

## Major lines

### Legacy `stompjs` and `@stomp/stompjs` 3/4
`Stomp.client(url)` or `Stomp.over(socket)`, then
`client.connect(headers, callback)` and `client.send(destination, headers,
body)`. The original project has long been unmaintained (upstream's FAQ). The
4 line of `@stomp/stompjs` was its maintained, compatible fork.

### `@stomp/stompjs` 5 and later
A TypeScript rewrite with the `Client` object: every option is a property,
`activate()`/`deactivate()` replace `connect`/`disconnect`, and `publish({...})`
replaces `send`. Automatic reconnect is on by default and does not restore
subscriptions. A compatibility mode keeps `Stomp.over` code working with no new
features. Upstream promised to maintain it only for a limited period, so treat
it as a bridge: a move off the legacy client can start as a swap and must
finish as a rewrite onto `Client`. STOMP over TCP in Node.js is no longer built in (a
separate TCP wrapper exists). `beforeConnect` may be `async` from the 6 line.
The 7 line ships ES modules and drops CommonJS.

### `@stomp/rx-stomp` 1 and 2
The 1 line pairs with `@stomp/stompjs` 6. The 2 line needs
`@stomp/stompjs` 7 and RxJS 7, makes its dependencies peers, adds
`deactivate({ force })` and `asyncReceipt`, and deprecates `ng2-stompjs`, the
older Angular wrapper.

## Upstream docs
- https://stomp-js.github.io/: guides, FAQ and API docs
- https://stomp-js.github.io/guide/stompjs/using-stompjs-v5.html: client
  configuration, heartbeats, reconnect, callbacks
- https://stomp-js.github.io/guide/stompjs/upgrading-stompjs.html: from the
  legacy API
- https://stomp-js.github.io/guide/rx-stomp/rx-stomp-with-angular.html: the
  Angular guide
- https://stomp-js.github.io/faqs/faqs.html: SockJS, authentication, Node.js
- https://github.com/stomp-js/stompjs and https://github.com/stomp-js/rx-stomp
- https://github.com/sockjs/sockjs-client
