# Suggested skill: genericize-config-to-examples

> Optional procedure: a repository holds real per-instance configuration
> (one variable file per host, service or environment, with real names,
> addresses and encrypted secrets), and the owner wants it replaced by
> reference examples, for a public or shared copy, a template repository, or
> a clean start. **Composes** `core/method/secrets-posture.md`
> (`secrets-posture.compromise`: a secret that reached version control is
> compromised, and a history rewrite is the owner's decision, never the
> remedy), `core/method/contract-posture.md` (§3: one document per contract,
> with one worked example per distinct shape, derived from the consuming
> code), `core/method/stewardship-posture.md` (§3: examples hold synthetic
> data), `protocols/grill.md` (the increment and its open questions), and
> `protocols/verify.md` by reference. What it adds is how to apply that
> example rule to a config tree that is being deleted, the three places the
> real instances survive the deletion, and the gate that proves what is
> left.

**Instantiate by supplying:** `<CONFIG_DIRS>` (the directories that hold
per-instance files), `<CONSUMERS>` (the code that reads those files: roles,
templates, entry points, validators), `<REGISTRIES>` (inventories, service
lists, DNS or proxy tables that name instances), `<VALIDATORS>` (every check
that reads the config tree, including drift checks keyed on file names),
`<LINTERS>` (the linters for the file types), `<EXAMPLE_SUFFIX>` (the naming
mark for an example, such as `.example.yaml`), and `<PRE_IMAGE>` (the commit
that holds the real files before the change).

## When to apply

- The owner asks to "genericize", "turn this into examples", or "remove the
  real config but keep it usable".
- A repository is about to be shared or published, and its config tree names
  real hosts, addresses or secrets.

## 1. Agree the scope, and where the real config goes

Agree with the owner which directories are in scope; a subsystem the owner
excludes stays out of `<CONFIG_DIRS>`. Then ask where the real instances live
after the change (a private copy, an ignored overlay, or nowhere), before
anything is deleted. Without an answer, an owner who still deploys from this
repository is left with nothing to run the automation against the real fleet.
Record the answer with the increment.

## 2. Group the instances by contract shape

Read every per-instance file in `<CONFIG_DIRS>` and group them by the shape
of the contract they fill: the set of keys and the structure of their values.
Many instance files usually fall into a few shapes (for example: a bare host,
a host running one composed application, a non-container service).

Write **one example per distinct shape**, not one per instance, and not one
for the whole tree (`contract-posture` §3). Name each by its shape, with
`<EXAMPLE_SUFFIX>`.

## 3. Write each example from its consumer, not from the old file

For each shape, open the consumer in `<CONSUMERS>` that reads it and derive
the example from what the consumer reads, asserts and defaults:

- every key the consumer reads appears, with a comment saying what it does
  and which values are valid;
- a key no consumer reads is left out. A real file is the place where dead
  keys accumulate, and copying it carries them forward;
- a value the consumer rejects is not in the example. Real files can hold a
  value an assertion added later now refuses, and an example that fails its
  own consumer teaches the failure;
- when two consumers read two forms of the same contract (a mapping and a
  list, say), show the form the main consumer reads, and the other as a
  commented variant naming its consumer.

Every value is synthetic: documentation address ranges, example domains,
placeholder names, and a vault or store reference in place of every secret
(`stewardship-posture.synthetic-data-only`).

Shared files that hold defaults for every instance (an `all` scope) are
edited in place, comments improved, not replaced by examples.

## 4. Delete the real files, and keep the rollback

Delete the per-instance files. The rollback is `<PRE_IMAGE>`: restoring the
directories from that commit brings every real file back. Record the commit in
the increment, so the rollback does not depend on someone remembering it.

## 5. The three places the real instances survive

Deleting the files does not remove the instances from the repository. Check
each place, and either fix it in this increment or record it as an open
question for the owner:

1. **History.** Every secret in a deleted file is still in the version
   history. Treat it as compromised and remedy it in the order
   `secrets-posture.compromise` gives (neutralize, externalize, rotate). A
   history rewrite is extra hygiene the owner may decide on, never a
   substitute for rotation. Encrypted values count: the ciphertext and its
   key may both be reachable.
2. **Registries.** `<REGISTRIES>` still name the deleted instances: inventory
   groups, host lists, DNS records, proxy routes. Either genericize them in
   the same way, or decide with the owner that they stay for the owner's
   private use, and record that decision.
3. **Validators.** A check in `<VALIDATORS>` that compares file names with
   registry entries now reports every example as drift (an example's name
   matches no real group). Give it an explicit exclusion for
   `<EXAMPLE_SUFFIX>`, or the check stays red and people learn to ignore it.
   `tool-corpus/ops/orphaned-scoped-config-auditor.md` is a ready check with
   that exclusion, and it says not to widen the exclusion to make the gate
   pass.

## 6. Gate

- `<LINTERS>` clean over every changed directory.
- Each example parses, and its keys match what its consumer reads (re-read the
  consumer against the example, key by key).
- `<VALIDATORS>` give the expected result, with the example exclusion in
  place or its absence recorded.
- A search of the tree for each real hostname, address and domain that was in
  the deleted files returns only the places step 5 recorded as kept. The
  plant's `docs/graph/agnosticism-lint.py` does this:
  `python3 docs/graph/agnosticism-lint.py --root <dir> --glob <file pattern>
  --forbid <each real name>`. It also flags any host address outside the
  documentation ranges, so it catches an address nobody listed. The list of
  real identifiers is itself sensitive: do not commit it.

Record what the cross-check against consumers found. It can find real
defects the old files carried (in the one run this page comes from, a value
the consumer rejects and a dead key). File each through `canonize` into the
node that owns that consumer.

## Reference files

- `core/method/secrets-posture.md` (§3, a committed secret is compromised)
- `core/method/contract-posture.md` (§3, one document per contract, one
  example per shape, derived from the consumer)
- `core/method/stewardship-posture.md` (§3, synthetic data)
- `protocols/grill.md` (the increment, its rollback and open questions)
- `protocols/verify.md` (what a passing gate proves)
- `tool-corpus/ops/orphaned-scoped-config-auditor.md` (a name-keyed drift
  check with an example exclusion)
- `docs/graph/agnosticism-lint.py` in a plant, `tools/agnosticism-lint.py`
  in the seed (the search for real identifiers)
