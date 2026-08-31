# rxjs — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Reactive Extensions library for JavaScript: Observables, operators, and schedulers for composing asynchronous and event-based programs.

## Core API / usage shape
- Operators and creation functions (`map`, `tap`, `catchError`, `finalize`, `switchMap`, `forkJoin`, `of`, `Observable`, etc.) import from the top-level `'rxjs'` package. The older `'rxjs/operators'` path remains valid.
- `firstValueFrom` (and `lastValueFrom`) bridge a one-shot Observable to a Promise for async/await.

## Idioms & best practices
- Import operators from `'rxjs'` rather than `'rxjs/operators'` in current code.
- Prefer `firstValueFrom`/`lastValueFrom` over the deprecated `toPromise()` when converting an Observable to a Promise.

## General pitfalls
- **`firstValueFrom`/`lastValueFrom` on empty streams:** an Observable that completes without emitting rejects (unless a default value is supplied); handle that path.
- **Subscription management:** long-lived subscriptions leak if not unsubscribed (or completed via operators like `takeUntil`).

## Upstream docs
- Official docs: https://rxjs.dev/
- Source: https://github.com/ReactiveX/rxjs
- npm: https://www.npmjs.com/package/rxjs
