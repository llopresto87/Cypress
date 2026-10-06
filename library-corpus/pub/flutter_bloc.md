# flutter_bloc — pub

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). A plant can adopt this page instead of scouting
> the BLoC library's surface; it still runs `ingest-library` against its own
> `pubspec.lock` for the exact versions of `bloc`, `flutter_bloc` and
> `bloc_test`.

## What it is
`flutter_bloc` is the Flutter half of the BLoC state-management library, a
family of packages in one monorepo under the MIT licence:
- `bloc`: the pure-Dart core (`Cubit`, `Bloc`, `BlocObserver`);
- `flutter_bloc`: the widgets that provide blocs to a widget tree and rebuild
  or react on state changes;
- `bloc_test`: the test harness (`blocTest`, `MockBloc`, `MockCubit`);
- `bloc_concurrency`: event transformers.

Upstream home: the docs at https://bloclibrary.dev , the source at
https://github.com/felangel/bloc , and the packages on pub.dev under their own
names. The docs describe the current major line only.

## Install, setup and configuration
- Add `flutter_bloc` (which brings `bloc`) to `dependencies`, and `bloc_test`
  plus `test` to `dev_dependencies`. A pure-Dart package uses `bloc` alone.
- Keep the family on matching major lines: `flutter_bloc` 9 and `bloc_test` 10
  both build on `bloc` 9.
- Global hooks: set `Bloc.observer = MyObserver()` (a `BlocObserver` subclass)
  once at startup for `onCreate`, `onEvent`, `onChange`, `onTransition`,
  `onError` and `onClose` across every bloc. `Bloc.transformer` sets the
  default event transformer.
- Defaults: a bloc ignores a state equal to the current one (`==`); events
  without a custom transformer are processed concurrently;
  `BlocProvider(create:)` creates its bloc lazily.

## Core API / usage shape
- `Cubit<State>`: public methods compute a new state and call `emit(state)`.
  `emit` is protected; the initial state goes to `super(...)`. A `Change`
  (current and next state) is observable through `onChange`.
- `Bloc<Event, State>`: events go in through `add(event)`, and handlers
  registered with `on<Event>((event, emit) async {...})` emit zero or more
  states. A bloc never emits outside a handler. A `Transition` (current state,
  event, next state) is observable through `onTransition`, which runs before
  `onChange`; `onEvent` and `onTransition` exist on `Bloc` only.
- Both expose `state`, `stream` and `close()`. `stream.listen` sees only
  states emitted after it subscribes.
- Errors: `addError` reports from anywhere; the bloc's own `onError` runs
  first, then `BlocObserver.onError`. An exception that escapes an event
  handler is reported to `onError` as well.
- Event transformers (`bloc_concurrency`): `concurrent()`, `sequential()`,
  `droppable()` and `restartable()`, passed as
  `on<E>(handler, transformer: sequential())`. Debounce and throttle come from
  `stream_transform` or `rxdart` in a custom transformer.
- `emit.forEach(stream, onData: ...)` inside a handler maps an external stream
  to states without a manual subscription (but with no pause, resume or custom
  transformer).
- Widgets (`flutter_bloc`): `BlocProvider`, `MultiBlocProvider`,
  `BlocBuilder` (`buildWhen`), `BlocListener` (`listenWhen`),
  `MultiBlocListener`, `BlocConsumer`, `BlocSelector`, `RepositoryProvider`
  and `MultiRepositoryProvider`, plus the context extensions `context.read`,
  `context.watch` and `context.select`.

## Idioms & best practices
- Start with a `Cubit`. Move to a `Bloc` when you need traceability (which
  event caused a change, as in authentication) or event transformers
  (debounce, throttle, drop, restart). Upstream gives this advice.
- Layers: presentation, business logic, then data (a repository over data
  providers such as an HTTP client). A bloc receives its repositories through
  its constructor.
- No bloc depends on another bloc. Connect them through the presentation layer
  (a `BlocListener` on one adds an event to the other) or through the domain
  (both listen to a repository `Stream`).
- `BlocProvider(create:)` creates and closes its bloc. `BlocProvider.value`
  re-provides an existing bloc and never closes it, so never construct a bloc
  inline inside `.value`.
- `BlocBuilder`'s `builder` must be a pure function; it may run many times. Use
  `BlocListener` for one-shot effects (navigation, dialogs, snack bars); it is
  not called for the initial state. Use `BlocConsumer` only when one widget
  needs both.
- Use `context.read` to add events in callbacks, never to read state inside
  `build` (the widget would not rebuild). Use `context.watch` or `BlocBuilder`
  in `build`, and `context.select` for one part of the state.
- Model state as immutable values with value equality (extend `Equatable`, mark
  `@immutable`, use `const` constructors). When data must survive an error,
  keep a single state class with `copyWith`.
- On a cubit, public methods return `void` or `Future<void>`; on a bloc, avoid
  public methods and use `add`.
- Internal events (reacting to a repository stream) are acceptable when kept
  private.
- Observed in practice: navigation driven by an auth `BlocListener` near the
  root, using a navigator key. The docs say only that listeners handle
  navigation.

## General pitfalls
- A state that does not update usually has one of three causes: an
  `Equatable` field missing from `props`; the same instance mutated and
  emitted again; a `List` or `Map` changed in place (copy it with `List.of` or
  `Map.of`). Without value equality, two equal-looking new instances both emit;
  with it, the second is dropped. Skip `Equatable` only when identical
  consecutive states must each trigger a transition.
- `BlocProvider.of(context)` cannot find a bloc from the same `BuildContext`
  that provides it; read it from a child context (a `Builder`, or a child
  widget).
- `emit` or `add` after `close()` throws a `StateError`.
- `context.watch` at the root of `build` rebuilds the whole widget.
- `Bloc` and `Cubit` are not `Stream`s; listen to `bloc.stream`.
- A `BlocListener` callback could fire for an unmounted widget on the
  `flutter_bloc` 8 line; the 9 line checks `mounted` first.
- Observed in practice: codebases with dozens of blocs and no `bloc_test`
  dependency, tested only by the stub widget test. That is an absence to
  correct, not a pattern.

## Testing
- `blocTest<B, S>('description', build: ..., act: ..., expect: () => [...])`
  asserts the states emitted, in order, and that no extra state was emitted,
  because it closes the bloc before it checks. Other options: `seed` (start
  state), `skip` (default 0), `wait` (for debounce), `verify`, `errors`,
  `setUp`, `tearDown` and `tags`. `build` is synchronous; prefer
  `package:test` `setUp` for setup shared across cases.
- Check the initial state with a plain `expect(bloc.state, ...)`.
- Mock repositories, not blocs, when testing a bloc. When testing widgets, use
  `MockBloc<E, S>` or `MockCubit<S>` (built on `mocktail`) with
  `whenListen(bloc, Stream.fromIterable([...]), initialState: ...)`, which
  stubs the stream and keeps `state` in step.
- With `Equatable` states, `expect` can list state instances; without it, use
  matchers or predicates.

## Security defaults
The library has no security surface of its own, and its changelogs list no
advisories. A `BlocObserver` that logs every change or transition logs the
state, so keep tokens and personal data out of logged states (general
practice, not stated upstream).

## Operational behaviour
- `close()` releases the internal stream controller and stops event
  processing. A bloc created by `BlocProvider(create:)` is closed when that
  provider leaves the tree; one passed through `.value` must be closed by
  whoever created it.
- `RepositoryProvider(dispose: ...)` releases a repository that holds
  resources (from the `flutter_bloc` 9 line).
- `BlocObserver` is the single place to log changes, transitions, events and
  errors across the app.

## Interop
- `flutter_bloc` uses `provider` for lookup; the context extensions are
  `provider`-backed.
- `equatable` for state equality, `bloc_concurrency` for transformers,
  `mocktail` for the `bloc_test` mocks, `stream_transform` or `rxdart` for
  custom transformers.
- Repositories commonly wrap an HTTP client such as `library-corpus/pub/dio`.
- Compared with Redux, bloc spreads state over several blocs and has no
  middleware.

## Major lines
### bloc 7 and flutter_bloc 7
Null safety. `Bloc` and `Cubit` extend `BlocBase` and are no longer `Stream`s
or `Sink`s. In `flutter_bloc`, the `cubit:` parameter became `bloc:` and
`context.repository` was removed.

### bloc 8 and flutter_bloc 8
`mapEventToState` was removed in favour of `on<Event>` handlers; `emit` is
scoped to its handler; `add` and `emit` throw on a closed bloc. `BlocOverrides`
arrived and was later deprecated in favour of `Bloc.observer` and
`Bloc.transformer`.

### bloc 9 and flutter_bloc 9
`BlocOverrides` is removed. `BlocBase` implements
`EmittableStateStreamableSource`. `flutter_bloc` checks that the widget is
mounted before calling a `BlocListener` callback, and `RepositoryProvider`
gained `dispose`.

### bloc_test
From 7, `skip` defaults to 0 and `build` is synchronous. From 8, mocks build on
`mocktail` (`MockCubit` added) and `seed`, `expect` and `errors` take
functions. From 9, `MockBloc` no longer needs `registerFallbackValue` for
events and states. 10 depends on the core interfaces and needs `bloc` 9.

## Upstream docs
- https://bloclibrary.dev/
- https://github.com/felangel/bloc
- https://pub.dev/packages/flutter_bloc
- https://pub.dev/packages/bloc
- https://pub.dev/packages/bloc_test
- https://pub.dev/packages/bloc_concurrency
