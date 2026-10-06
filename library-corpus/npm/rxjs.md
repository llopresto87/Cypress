# rxjs — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Reactive Extensions for JavaScript: Observables, operators and schedulers for
composing asynchronous and event-based programs. The npm package is `rxjs`; it
also serves the subpath entry points `rxjs/operators`, `rxjs/ajax`,
`rxjs/fetch`, `rxjs/webSocket` and `rxjs/testing`. It has one runtime
dependency (`tslib`). Licence: Apache-2.0. Angular's `HttpClient`, router and
reactive forms return Observables, so most Angular apps carry it as a peer of
the framework.

## Install, setup and configuration
- `npm install rxjs`. In an Angular app the framework declares the accepted
  RxJS range per major; install inside that range (see
  [angular](../language/angular.md)).
- There is no setup step. The one global setting is the `config` object
  exported from `'rxjs'`:
  - `config.onUnhandledError`: called for an error that reaches a subscriber
    with no error handler. Unset by default, so the error is rethrown on a
    separate call stack (see Operational behaviour).
  - `config.onStoppedNotification`: called when a notification arrives after
    a subscriber has already errored or completed. Mostly for logging.
  - `config.useDeprecatedNextContext`: restores the old `this`-is-the-subscriber
    behaviour inside `next` handlers. Off by default; turning it on costs
    performance on every subscription.

## Core API / usage shape
- An `Observable` is lazy: nothing runs until `subscribe()`. Each subscription
  starts its own execution (unicast).
- `subscribe()` takes either one `next` function or an observer object
  `{ next, error, complete }`, where any callback may be omitted. It returns a
  `Subscription`, the disposable for that execution: `unsubscribe()` cancels it,
  `add(child)` attaches a child subscription or teardown function so one
  `unsubscribe()` ends the group, and `remove(child)` detaches it.
- Operators and creation functions (`map`, `tap`, `catchError`, `finalize`,
  `switchMap`, `forkJoin`, `of`, `Observable`, etc.) import from the top-level
  `'rxjs'` package. The older `'rxjs/operators'` path still works but is
  deprecated upstream, which says it will go in a later major.
- Subjects are Observables that are also observers and multicast to every
  subscriber. `Subject` has no current value. `BehaviorSubject` holds one and
  replays it to each new subscriber. `ReplaySubject` replays a buffer, and
  `AsyncSubject` emits only its last value on completion.
- Multicasting in the 7 line goes through `share`, `shareReplay`, `connect`
  and `connectable`. `multicast`, `publish*`, `refCount` and
  `ConnectableObservable` are deprecated, and upstream says they break in the
  next major.
- `firstValueFrom` (and `lastValueFrom`) bridge a one-shot Observable to a
  Promise for async/await. Both take an optional `{ defaultValue }`.

## Idioms & best practices
- Import operators from `'rxjs'` rather than `'rxjs/operators'` in current code.
  Use the `...With` operators (`mergeWith`, `concatWith`, `zipWith`,
  `combineLatestWith`, `raceWith`) or the static creation functions in place
  of the deprecated pipeable `merge`/`concat`/`zip`/`combineLatest`/`race`.
- Pass `subscribe` (and `tap`) a single `next` function or an observer object.
  Every signature with more than one callback argument has been deprecated
  since the 6 line.
- Prefer `firstValueFrom`/`lastValueFrom` over the deprecated `toPromise()` when converting an Observable to a Promise. The swap changes behavior on an empty
  completion (see the pitfall below).
- Give every manual long-lived subscription an owner that ends it:
  `takeUntil(destroy$)`, `Subscription.add` under a parent that is
  unsubscribed, or the Angular `async` pipe (on Angular, also
  `takeUntilDestroyed` from `@angular/core/rxjs-interop`). Observed in
  practice: projects put `takeUntil` last in the pipe; the rxjs docs state no
  ordering rule.
- Hold shared state in a service as a private `BehaviorSubject` (or `Subject`
  when there is no current value) and expose it read-only through
  `.asObservable()`. Projects use this as the store when there is no store
  library; upstream documents the Subject types but not this pattern.
- To share one HTTP result across several subscribers, use `shareReplay` (or
  cache the value in a `BehaviorSubject`). For a source that holds a resource,
  use `shareReplay({ bufferSize: 1, refCount: true })`.
- Bound every `retry()` with a count or a `{ count, delay }` config.

## General pitfalls
- **`firstValueFrom`/`lastValueFrom` on empty streams:** an Observable that completes without emitting rejects with `EmptyError` (unless a default value is supplied), where `toPromise()` resolved `undefined`; handle that path.
- `lastValueFrom` on a stream that never completes never settles, and
  `firstValueFrom` on one that never emits hangs the same way, keeping the
  async function's state in memory. Add `take`, `takeUntil` or `timeout`
  first.
- **Subscription management:** long-lived subscriptions leak if not unsubscribed (or completed via operators like `takeUntil`).
- Each subscription to a cold Observable runs the producer again. An
  `HttpClient` call subscribed twice "to read the value" sends two requests
  (observed in practice; it follows from the unicast model above).
- `retry()` with no count resubscribes forever. It also re-emits every value
  produced during failed attempts, so downstream sees duplicates. Observed in
  practice: stacking `retry()` over a client that already reconnects on its
  own (a STOMP or SignalR client) multiplies its connections.
- `shareReplay` defaults to `refCount: false`: when the subscriber count drops
  to zero it does not unsubscribe from the source, which can then run forever.
  A source that completed stays cached for good; an errored one can be
  retried.
- In the 7 line `toPromise()` is typed `Promise<T | undefined>`, which can
  break a build that assumed `Promise<T>`.

## Testing
- `TestScheduler` from `'rxjs/testing'` tests time-based code synchronously
  with virtual time. Inside `testScheduler.run(helpers => ...)`, operators
  that use the async scheduler (`delay`, `debounceTime`, `throttleTime`)
  switch to virtual time automatically.
- The helpers `cold()` and `hot()` build source Observables from marble
  strings; `expectObservable(obs).toBe(marbles, values)` and
  `expectSubscriptions(...)` schedule assertions that run when the callback
  returns or at `flush()`. Construct the scheduler with your framework's deep
  equality assertion.
- `TestScheduler` cannot reliably test code that consumes a Promise; test that
  path with ordinary async tests.
- From the 7 line, RxJS errors carry a real `stack`, so a deep-equality check
  between two error instances can fail on the stack text alone.

## Security defaults
- RxJS opens network connections only through its opt-in helpers:
  `rxjs/ajax`, `rxjs/fetch` and `rxjs/webSocket`.
- `ajax` in the 7 line has `xsrfCookieName` and `xsrfHeaderName` options for
  cross-site request forgery protection; they do nothing until set. An Angular
  app normally uses `HttpClient` instead, whose XSRF handling the
  [angular](../language/angular.md) page covers.

## Operational behaviour
- Nothing runs before `subscribe()`. Teardown runs on `unsubscribe()`, on
  `error`, or on `complete`, and `finalize` runs on any of the three.
- An error that reaches a subscriber with no error handler is rethrown on a
  new call stack, so one consumer's failure does not stop the others sharing a
  multicast. In the 7 line an error raised during subscription setup after the
  source has already stopped also throws on its own stack (it was a
  `console.warn` before). A Node.js process configured to exit on uncaught
  exceptions can therefore stop; `config.onUnhandledError` can route these to
  a logger instead.
- An Observable that errors is finished; recovery means resubscribing
  (`retry`, `repeat`) or replacing it (`catchError`).

## Interop
- Angular: `HttpClient`, the router and reactive forms return Observables, and
  `@angular/core/rxjs-interop` bridges them to signals. Each Angular major
  declares the RxJS range it accepts. See [angular](../language/angular.md).
- Promises and async iterables: any `ObservableInput` (Promise, array,
  iterable, async iterable, `ReadableStream`) converts with `from()`; the other
  way goes through `firstValueFrom`/`lastValueFrom`.
- Real-time clients: [stomp-sockjs](stomp-sockjs.md) (with its RxJS wrapper)
  and [microsoft-signalr](microsoft-signalr.md) can reconnect on their own,
  which matters for the `retry()` pitfall above.

## Major lines

### 6 line
- Operators import from `'rxjs/operators'`; `firstValueFrom` and
  `lastValueFrom` do not exist, and `toPromise()` is the only Promise bridge.
- The multi-callback `subscribe` signatures and the `resultSelector`
  arguments are already deprecated here.
- The `rxjs-compat` package and the `rxjs/Rx` import site exist on this line;
  the 7 line drops both.

### 7 line
- Needs a later TypeScript 4.x release (the upstream version-7
  breaking-changes page names the floor), so it cannot land before the
  project's TypeScript bump.
- Adds `firstValueFrom`/`lastValueFrom` and deprecates `toPromise()`; adds the
  `config` handlers listed above; simplifies multicasting to
  `share`/`connect`/`connectable`.
- From a later 7.x release most operators also export from `'rxjs'`, and
  `'rxjs/operators'` becomes deprecated.
- `Subscription.add` no longer returns a Subscription, `rxjs-compat` is not
  published, and `defer` factories must return an `ObservableInput` (return
  `EMPTY` where they used to return nothing).

## Upstream docs
- Official docs: https://rxjs.dev/
- Source: https://github.com/ReactiveX/rxjs
- npm: https://www.npmjs.com/package/rxjs
- Guides used here (rxjs.dev renders client-side; the same text is in the
  repository): subscription, observer, subject, importing, marble testing,
  glossary; deprecations: subscribe arguments, `toPromise`, multicasting;
  the 6-to-7 change summary and the version-7 breaking-changes page.
