# Suggested skill: seed-demo-world-for-manual-ui-review

> Optional procedure: seed one coherent synthetic "demo world" into a running,
> deployed instance, so that a person can log in and click through every
> screen of every client surface with no setup, the broken paths included.
> The seed is owner-scoped, idempotent and verified through the real API.
> Composes `tool-corpus/ops/disposable-test-identity-provisioner.md` (its
> fail-closed guard against a non-disposable target is the model for step 0's
> target check), `protocols/canonize.md` (step 5) and
> `skill-corpus/mutation-verify.md` (to prove the verify script bites).
> Parameterized by `<TARGET>` (the deployed instance and how its datastore and
> API are reached), `<DEMO_MARKER>` (the owner value or id prefix that marks
> every seeded row), `<DEMO_PASSWORD>` (one synthetic password every demo user
> shares, supplied by the owner) and `<SURFACES>` (every client the product
> exposes: web front end, operator or device app, kiosk, mobile, admin).

## When to apply

- A person must review the UI or UX of a deployed instance by hand, and the
  instance is empty, or holds only data nobody may show.
- Demo data already seeded must be refreshed after a schema change or a
  redeploy, or removed.
- The team is about to inject rows by hand "just to see a screen". That is
  the ad hoc path this procedure replaces. Each step below exists because
  skipping it cost hours once: foreign-key order, enum storage, login modes,
  rows that vanish overnight, and screens that crash on a missing related row.

Do not use it to build test fixtures for an automated suite. Fixtures belong
to the suite and its own setup. A demo world serves a human reviewer.

## Hard rules

- **Synthetic data only.** Never copy a real or production record. What
  makes generated data good (valid against every constraint, identifiers
  issued to nobody, consistent with itself, plausible for the product's
  locale) is the data role's list in `agents/07-data-ml.md`, "Synthetic and
  example data"; the seed meets all of it.
- **The owner authorizes the target.** Seeding writes to a datastore. Name
  the instance, get the owner's go-ahead for it, and stop if the target
  cannot be identified as the one the owner named.
- **Never touch a non-demo row** except to unlink and re-link it (step 2).
- **No secrets in the artifacts.** `<DEMO_PASSWORD>` is a synthetic
  credential for a demo world and may be recorded. Datastore credentials are
  read from where the deployment keeps them, at run time, and never written
  into the seed or the verify script.

## The procedure

### 0. Recon the live system before writing anything

This step replaces "write the inserts from memory or from the docs". The
schema in the docs and the schema in the database disagree more often than
anyone expects, and the database is the one the seed must satisfy.

1. Record how `<TARGET>` is reached: the datastore (container or host,
   database name, where the credentials live), the published API base, and
   every surface in `<SURFACES>`.
2. Read the **live** schema for every table you will touch: its columns, the
   foreign-key graph, and each key's delete rule (cascade, restrict, set
   null), from the engine's catalog. In MySQL the graph is in
   `information_schema.KEY_COLUMN_USAGE` (the `REFERENCED_*` columns) and the
   delete rule is in `information_schema.REFERENTIAL_CONSTRAINTS`
   (`DELETE_RULE`); join the two on the constraint name.
3. Find how each enum is stored. A column that holds an ordinal integer, not
   a label, is mapped through the source code's enum declaration, so read
   that declaration and write the mapping down. Never guess an ordinal.
4. Read the authentication path in source: how passwords are hashed, which
   roles exist, how a login identifier resolves to a user, and **every**
   login endpoint. Products often have a main login plus machine, device,
   kiosk or operator logins, each with its own preconditions (a user linked
   to a site, a device identifier in the path).
5. Hunt for data-lifecycle landmines in source:
   - scheduled jobs that purge or archive old rows;
   - queries keyed on "today" (available today, due today);
   - exact-string matches the UI depends on (a status label, an issue type);
   - columns or tables that are dead code, which the seed should leave empty.
6. Take a full backup of the datastore before the first apply, and record
   where it is.

Gate: a written recon note with the schema facts, the enum mappings, the
login modes and the landmines. The seed is not authored before this note
exists.

### 1. Design one coherent world

This step replaces "a few rows per table". Map the entities parent to child,
then design one world that covers:

- every enum value and every role;
- every state kind a workflow can be in, including the terminal and the
  blocked ones;
- at least one **broken** entity per domain (a failed machine, an overdue or
  blocked task, a rejected request), so the error screens can be reviewed;
- empty cases (a user, a site or a list with nothing in it);
- at least two organizational units (sites, tenants, teams) where the
  product has them, so switching between them can be reviewed.

Keep it readable: dozens of rows, not thousands, held to the data role's
list in `agents/07-data-ml.md` (story, locale, dates that follow each row's
lifecycle, stored derived values that agree with their inputs).

Gate: a coverage table, one row per enum value, role, state and broken case,
naming the demo entity that exercises it.

### 2. Author one owner-scoped, idempotent seed

This step replaces a pile of insert statements run once. Write one seed
script that runs inside **one** transaction, opens with a reset block that
deletes only the rows carrying `<DEMO_MARKER>`, and then inserts the world
again, so a second run gives the same world and never touches anything else.
The method and its traps are on `tool-corpus/ops/owner-scoped-idempotent-seed.md`:
the marker, the reset order read from step 0.2's foreign keys, the unlink and
re-link of a real row that points at a demo parent, parent-first inserts with
generated keys chained through variables, and dates relative to the day of
the apply (§3.1); the per-engine idioms, such as MySQL's unquoted user
variable (§3.2); the pitfalls (§5). This procedure adds three decisions:

1. **The marker.** Choose it from what step 0 found (an owner or "created
   by" column, a prefix on a natural key, or a side table), and write the
   choice into the recon note.
2. **One shared demo password.** Store every demo user with
   `<DEMO_PASSWORD>`, hashed with the product's own algorithm and cost
   (step 0.4), so the reviewer logs in as anyone with one value.
3. **Inline content where the product expects content in the row.** When an
   attachment or reference is stored as content (a data URI with a small
   valid PNG or PDF, say), keep each statement on one physical line, and keep
   the payloads tiny.

Gate: the script parses, and it runs inside one transaction from its first
statement to its last.

### 3. Apply

Ship the script to the host and feed it to the datastore's own client, inside
the datastore's container where it runs in one, with the character set made
explicit. Pass the datastore credential through the client's option file
(for MySQL, `--defaults-extra-file` naming a file only the operator can read)
or a scoped environment variable, never as a command-line argument such as
`-p<password>` (`core/method/secrets-posture.md`). A non-zero exit means the
transaction rolled back and the datastore is unchanged: fix the script and
apply again. Never apply part of a script by
hand to get past an error.

Gate: exit 0, and a second apply also exits 0 and leaves the same world
(idempotency proved, not assumed).

### 4. Verify through the real API, as each screen does

This step replaces row counts. A count proves the rows exist; it does not
prove that any screen can show them. Drive the API with the seeded-world
verifier on `tool-corpus/ops/owner-scoped-idempotent-seed.md` (§3.3: its
plan format, ids resolved at run time, a non-zero exit on any failure, its
self-test), or with a script built to the same contract, run where the API is
reached. Its plan covers, by this page's gate:

1. **every** demo user in **every** login mode from step 0.4;
2. every endpoint each screen in `<SURFACES>` uses: lists per organizational
   unit, detail views, wizards step by step, device and operator flows;
3. the broken paths and the empty cases of step 1: a blocked list that is not
   empty, a failed status that is reported as failed, an empty list that
   renders as empty.

Instructions written for the human reviewer name entities, not ids, because
ids move on every re-apply.

Prove the verify script bites before trusting a green run: remove one
required related row from a copy of the seed, re-apply it, and watch the
matching check fail (`skill-corpus/mutation-verify.md`), then restore.

**When an endpoint fails on seeded data**, find the cause in source before
changing anything. A product defect (for example, an unconditional
dereference of a related row the schema allows to be missing) is worked
around in the data and recorded as a bug, never fixed inside the data task
(the tool page's §5). Record it with the file, the line and a recommended fix
in the project's plan or bug log, and explain the workaround there.

Gate: every login and every screen endpoint passes, and every defect found is
recorded.

### 5. Leave it durable

Deliver three artifacts and one record:

- the idempotent seed script, committed to the repository;
- the verify script, committed beside it;
- a record of the run: what the world contains, every landmine and defect
  found, and the caveats of a re-seed (ids move; a schema change means
  re-running step 0);
- the procedure itself as a project skill and a tool card for each script,
  handed to the close-out (`protocols/canonize.md`), so the next session
  re-seeds with one command instead of rediscovering the method.

Removing the world is the reset block alone, run in its own transaction.

## Reference files

- `tool-corpus/ops/disposable-test-identity-provisioner.md` (throwaway
  identities against a disposable target; this page seeds a whole data world
  for a human reviewer)
- `tool-corpus/ops/owner-scoped-idempotent-seed.md` (the reset-then-insert
  method, the engine idioms and the seeded-world API verifier of steps 2
  and 4)
- `skill-corpus/mutation-verify.md` (proving the verify script bites)
- `protocols/canonize.md` (the close-out that catalogs the seed and the
  verify script)
- `agents/07-data-ml.md` (the role that owns synthetic and example data, and
  its list of what good synthetic data is)
