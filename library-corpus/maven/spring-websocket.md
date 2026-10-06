# spring-websocket — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Spring Framework's WebSocket support (`spring-websocket`), its SockJS fallback,
and STOMP messaging over WebSocket (`spring-messaging`). This page covers the
server side and the Java STOMP client; the browser client is
[`stomp-sockjs`](../npm/stomp-sockjs.md). Coordinates:
`org.springframework:spring-websocket`, `org.springframework:spring-messaging`,
and with Spring Boot `org.springframework.boot:spring-boot-starter-websocket`.
Reference: https://docs.spring.io/spring-framework/reference/web/websocket.html.

## Install, setup and configuration
- **Spring Boot** auto-configures WebSocket support for embedded Tomcat and
  Jetty; a war on a standalone container gets it from the container. The
  servlet stack uses `spring-boot-starter-websocket`; the reactive stack needs
  the Jakarta WebSocket API beside the WebFlux starter.
- **Raw WebSocket.** Implement `WebSocketHandler` (usually by extending
  `TextWebSocketHandler` or `BinaryWebSocketHandler`), enable with
  `@EnableWebSocket`, and register through
  `WebSocketConfigurer.registerWebSocketHandlers`; `.withSockJS()` adds the
  fallback; a custom `HandshakeHandler` or `RequestUpgradeStrategy` can be set.
- **STOMP.** `@EnableWebSocketMessageBroker` plus a
  `WebSocketMessageBrokerConfigurer`:
  - `registerStompEndpoints`: the endpoint URL, optional `.withSockJS()`, and
    the allowed origins;
  - `configureMessageBroker`: `setApplicationDestinationPrefixes("/app")` and
    either `enableSimpleBroker("/topic", "/queue")` or
    `enableStompBrokerRelay(...)` for an external broker.
  Messages under the application prefix go to `@MessageMapping` methods;
  `/topic` and `/queue` go to the broker.
- **Channels.** `clientInboundChannel` carries messages from clients,
  `clientOutboundChannel` messages to clients, and `brokerChannel` messages from
  application code to the broker. With an external broker the relay sits between
  the channels and the broker.
- **Transport limits.** `configureWebSocketTransport` sets
  `setMessageSizeLimit`, `setTimeToFirstMessage`, `sendTimeLimit` and
  `sendBufferSizeLimit`; on a Jakarta WebSocket server a
  `ServletServerContainerFactoryBean` sets the container's text and binary
  buffer sizes and idle timeout.
- **Relay credentials** default to `guest` for both the client and the system
  login and passcode (`StompBrokerRelayRegistration`: `setClientLogin`,
  `setClientPasscode`, `setSystemLogin`, `setSystemPasscode`).
- **Thread pools.** Keep `clientInboundChannel` near the processor count for
  CPU-bound handlers and grow it when handlers block on I/O. With the default
  queue capacity (`Integer.MAX_VALUE`) the executor never grows past its core
  size, because extra tasks queue; set a bounded queue capacity if the maximum
  pool size should matter. The outbound pool's needs follow client network
  speed.

## Core API / usage shape
- `@Controller` classes handle client messages with `@MessageMapping` (type and
  method level, Ant-style patterns), `@SubscribeMapping` and
  `@MessageExceptionHandler`.
- **Server push.** Inject `SimpMessagingTemplate` and call
  `convertAndSend(destination, payload)`; it sends through `brokerChannel`.
- **User destinations.** A destination prefixed `/user/` is rewritten by
  `UserDestinationMessageHandler` into one unique to the user's session, so a
  client subscribes to a generic name without collisions.
- **Events and interceptors.** `SessionConnectEvent`, `SessionConnectedEvent`
  (STOMP session established), `SessionSubscribeEvent`,
  `SessionUnsubscribeEvent`, `SessionDisconnectEvent`; a `ChannelInterceptor`
  sees every message at any point of the chain.
- **Session attributes.** Each WebSocket session has an attribute map, attached
  as a header to inbound client messages and available to controller methods;
  a `websocket` bean scope exists.
- **Ordering.** Broker messages go out through `clientOutboundChannel`, which is
  backed by a thread pool, so a client can see them out of publication order;
  `setPreservePublishOrder(true)` keeps the order.
- **Java STOMP client.** `WebSocketStompClient` over a `WebSocketClient`
  (`StandardWebSocketClient`, or `SockJsClient`, which can fall back to HTTP
  transports), with a `MessageConverter` and, for heartbeats, a
  `TaskScheduler`. A STOMP-over-TCP client also exists.

## Idioms & best practices
- Register `ChannelInterceptor`s in `configureClientInboundChannel` for
  authentication and logging.
- Use the broker relay to an external STOMP broker whenever more than one
  application instance serves clients: every instance connects to the broker, so
  a broadcast from one instance reaches clients on all of them.
- Register the endpoint with SockJS when browsers may need the fallback; list
  explicit allowed origins.
- Never expose the relay's default `guest` account.

## General pitfalls
- **The simple broker does not cluster.** It supports a subset of STOMP (no
  acks, no receipts, other features absent), uses a simple send loop, and
  cannot serve several application instances.
- **STOMP CONNECT credentials are ignored by default.** Spring ignores the
  `login` and `passcode` headers of a CONNECT frame and expects the user to be
  authenticated at the HTTP handshake, carried on the WebSocket or SockJS
  session. To authenticate from a CONNECT header (a token), register a
  `ChannelInterceptor` on `clientInboundChannel` that authenticates the CONNECT
  frame and calls `setUser` on the accessor; Spring then keeps that user for the
  session. Without it, a client that sends `Authorization` as a STOMP header
  subscribes unauthenticated (the rule is upstream; the symptom is observed in
  practice).
- **Handshake tokens.** Observed in practice, and stated in the 5 line's
  reference (the current reference no longer says it): browsers and SockJS
  cannot add custom headers to the handshake, and a token in the query string
  may be logged.
- **Origins.** Allowed origins default to same-origin. The check protects
  browser clients only; other clients can send any `Origin`. With SockJS in
  same-origin mode the iframe response carries `X-Frame-Options: SAMEORIGIN`
  and the JSONP transport is off. Opening every origin removes the protection;
  list explicit origins. `setAllowedOrigins` and `setAllowedOriginPatterns`
  both exist on the endpoint registration.
- **Heartbeats.** SockJS heartbeats default to 25 seconds and turn off when
  STOMP heartbeats are negotiated; the SockJS scheduler is sized by processor
  count.
- **SockJS and CORS.** Cross-origin SockJS XHR streaming and polling use CORS,
  and Spring adds the headers unless the response already has them (from a
  filter, for example).
- **Start-up scan.** JSR-356 containers run a ServletContainerInitializer scan
  that can slow start-up noticeably after an upgrade to such a container.
- **Mixed client estates** (observed in practice, weak evidence: inferred on
  one project). SockJS clients and raw WebSocket clients need both endpoint forms
  registered, or one kind cannot connect. The docs say `.withSockJS()` adds
  fallback endpoints and do not cover the mixed case.
- Which broker Spring starts when `configureMessageBroker` is not overridden is
  not stated in the reference or javadoc (the method is a default no-op);
  configure it explicitly.

## Testing
- Upstream names two approaches, not exclusive: server-side tests of
  controllers and annotated message handlers (focused and easier to write), and
  end-to-end tests that run a client against a running server. The reference
  shows no code for them; the Java STOMP client above is the usual end-to-end
  driver.

## Security defaults
- Same-origin only for WebSocket and SockJS; STOMP credential headers ignored
  unless an interceptor handles them; relay logins default to `guest`.
- **Spring Security message authorization:** `@EnableWebSocketSecurity` with an
  `AuthorizationManager<Message<?>>` bean. Any inbound CONNECT then needs a
  valid CSRF token (same-origin enforcement), and the `SecurityContextHolder` is
  filled from the `simpUser` header. See
  [`spring-security`](./spring-security.md).
- Spring Session keeps the HTTP session alive while a WebSocket is open.

## Operational behaviour
- Proxies in front of the application may refuse the `Upgrade` header or close
  idle long-lived connections; heartbeats keep intermediaries from judging a
  connection dead. Proxy configuration belongs to the proxy's page (see
  [`nginx`](../container/nginx.md)).
- The simple broker sends STOMP heartbeats only when given a task scheduler;
  the Java client needs a `TaskScheduler` for heartbeats.
- SockJS HTTP streaming and long-polling hold connections open; client
  disconnects are logged at a low level (the `org.springframework.web.socket`
  category at TRACE shows more).

## Interop
- **Spring Security** for message-level authorization; **Spring Session** for
  session keep-alive.
- **External STOMP brokers** (RabbitMQ, ActiveMQ and others) through the relay;
  the broker's own STOMP documentation covers its side. See
  [`rabbitmq`](./rabbitmq.md).
- **Message converters.** JSON payloads go through the configured
  `MessageConverter`; on Framework 7 Jackson 3 is tried first, then Jackson 2.
  See [`jackson`](./jackson.md).
- **Browser client:** [`stomp-sockjs`](../npm/stomp-sockjs.md).

## Major lines
### Framework 5
`javax.websocket`. Message security through Spring Security's
`AbstractSecurityWebSocketMessageBrokerConfigurer` and
`MessageSecurityMetadataSourceRegistry`; the late Spring Security 5 line added
the authorization-manager style.

### Framework 6
The Jakarta namespace (`jakarta.websocket`). Spring Security 6 offers
`@EnableWebSocketSecurity` with `AuthorizationManager<Message<?>>`.

### Framework 7
Servlet 6.1 baseline; the Undertow-specific WebSocket classes are removed
(Undertow lacks Servlet 6.1). Spring Security 7 removes the legacy configurer
and `MessageSecurityMetadataSourceRegistry`.

## Upstream docs
- https://docs.spring.io/spring-framework/reference/web/websocket.html
- https://docs.spring.io/spring-framework/reference/web/websocket/stomp.html
- https://docs.spring.io/spring-framework/reference/web/websocket/fallback.html
- https://docs.spring.io/spring-boot/reference/messaging/websockets.html
- https://docs.spring.io/spring-security/reference/servlet/integrations/websocket.html
- https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/messaging/simp/config/StompBrokerRelayRegistration.html
