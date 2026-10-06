# Suggested skill: provision-records-from-unstructured-input

> Optional procedure: a person hands over unstructured input (photos of ID
> cards or badges, a pasted list, a forwarded chat log) and asks for the
> people or items in it to become records on a system the project manages as
> desired state. **Composes** `core/method/design-posture.md` (§11,
> `design-posture.converge-on-drift`: read, compare, write only on drift),
> `core/method/secrets-posture.md` (`secrets-posture.channel` and
> `secrets-posture.recording`: a secret enters by one channel and is recorded
> by name only), `core/method/restrictive-policy.md` (a destructive or
> stranding write sits behind an explicit flag), `core/method/stewardship-posture.md`
> (§3, `stewardship-posture.synthetic-data-only`), `protocols/verify.md`
> (a gate asserts something, and an exit code is not state), and
> `protocols/deliver.md` (`deliver.numbered-decisions`: a question put to the
> owner is numbered) by reference. What it adds is the order of the steps
> between "here is a photo" and "the record exists and nothing else moved",
> and the pitfalls that turn a misread input into a wrong physical credential.

**Instantiate by supplying:** `<TARGET_SYSTEM>` (the system that holds the
records), `<RECORD_CONTRACT>` (the desired-state file or store where each
record is declared, and its fields), `<STABLE_KEY>` (the field that
identifies a record across runs and is printed on the input, for example a
card or badge number; never a position or an id the target assigns),
`<FIELD_LIMITS>` (each field's length, character set and value range, as
measured on the target), `<SECRET_STORE>` (where per-record secrets live, and
the command that writes one), `<OFFLINE_CHECK>` (the validation that reads
only `<RECORD_CONTRACT>` and makes no call to the target), `<APPLY_SURFACE>`
(the one durable command that converges the target to the contract), and
`<READ_BACK>` (the command that lists what the target holds).

## When to apply

- Someone pastes or attaches photos of cards, badges or labels and says "add
  these people", "enrol them", "put these on the system".
- Someone pastes a list ("name, number" per line), or forwards a chat log
  that contains one.
- A record has to be created on a target whose state is declared in a file
  and converged by automation, and the input exists only as a picture or as
  free text.

The procedure does not apply when the target exposes no read-back. Without
one, step 8 cannot run. Build the read surface first.

## 1. Read the input where it already is

Pasted text and attached images are already in the session's context. Read
them there. Searching the disk for a file the person already pasted wastes
turns and can open unrelated personal files.

When the person gives a path or a vague location ("the photos in my
downloads"), list the candidate files by type and date, then confirm which
ones are the input before opening any of them. A folder of photos holds more
than the cards you were asked about.

Convert formats the reader cannot open. A model's image input accepts a fixed
set of formats (one vendor documents JPEG, PNG, GIF and WebP), and a phone's
default photo format is often not in that set. Convert to one that is, in a
scratch folder. When the converter can apply the stored orientation flag (one
widely used tool calls the step auto-orient), apply it while converting, so
the converted pixels match what a viewer shows.

**Render the whole image once, at a legible size. Do not crop.** Observed in
practice: a command-line image tool that crops by stored pixel coordinates
ignores the EXIF orientation flag that a viewer applies, so crop boxes chosen
from the rotated view land on the wrong region. One full render, scaled so the
longest side is a couple of thousand pixels, was enough to read a printed
number of seven digits. If the number is still not legible, ask for a retake or for
the number typed out. Never guess a digit.

## 2. Transcribe verbatim, then ask once

Write down exactly what the input says, per record, before interpreting any
of it: every name as printed and every number as printed.

Then collect every ambiguity and ask about all of them in one numbered
message, with a recommendation for each (`deliver.numbered-decisions`). Do not
drip one question per turn. Ambiguities that recur:

- **Name order.** Lists mix "given name, family name" and "family name, given
  name". A compound family name may be split or joined.
- **The sender is not a subject.** In a forwarded chat log, the name before
  the colon on every line is whoever sent the message. It is not a person to
  enrol.
- **A field the target cannot hold.** A name longer than `<FIELD_LIMITS>`
  allows needs a shortening rule. Propose one (initial plus family name, then
  the bare family name, then truncation) and show the result.
- **A collision.** The number is already on another declared record, or two
  inputs carry the same number.
- **An altered credential.** A photographed card is not proof of who owns it.
  Cards get relabelled, and a sticker over the printed name shows someone
  else's card number. When a card looks altered, or its number already
  exists, ask.

A default that is safe and reversible (for example, joining a two-word family
name to fit a length limit) may be applied and stated instead of asked.

## 3. Confirm the identity-to-key table before any write

Show the person the final table: one row per record, with the name as it will
be stored and `<STABLE_KEY>`. Wait for an explicit confirmation.

This gate exists because the most expensive error here is invisible later. A
misread digit provisions the wrong physical credential, the read-back then
agrees with the contract, and nothing downstream can tell.

## 4. Write each record's secret straight into the store

When a record needs a secret (a PIN, an initial password), generate it with a
cryptographic generator and pipe it straight into `<SECRET_STORE>`. Never
write it as a literal in the contract, never print it, and never let a
default value stand (`secrets-posture.channel`).

Watch the trailing newline. A generator piped through `echo` or a
`printf '%s\n'` adds a newline, and some secret-store commands encrypt it as
part of the value, so the target receives one character too many. Use a
writer that emits no newline (`printf '%s'`, or a language call that writes
the bare string). `<OFFLINE_CHECK>` should assert each secret's exact length,
so this fault fails before any session opens.

## 5. Declare the records in the contract

Add one entry per confirmed row to `<RECORD_CONTRACT>`, with the secret as a
reference to its store entry. Match on `<STABLE_KEY>`, not on a position or
on an id the target assigns, because ids can shift when someone else adds a
record on the target at the same time. When the target needs a record id
supplied on create, take it from the next-free value the target reports at
the time of the run, never from the contract's last row, and match on
`<STABLE_KEY>` again after the apply.

Give the lowest privilege by default. A field that grants administrative
rights on the target stays at its non-privileged value unless the owner
approves otherwise, by name, for that record.

The identity the automation itself logs in with is not one of these records.
Leave it out of convergence by default: converging it can lock the control
plane out of the target. Overriding that takes an explicit, named flag that nobody sets on
their own initiative.

## 6. Validate offline

Run `<OFFLINE_CHECK>` before opening any session to the target. It asserts,
from the contract alone:

- every field is within `<FIELD_LIMITS>`, as measured on the target;
- `<STABLE_KEY>` is unique across all declared records;
- every secret resolves, has the exact expected length, and is not a default;
- no ordinary record carries a privileged role.

A fault caught here costs seconds. The same fault caught by the target often
arrives as a generic error after retries and backoff, and reads like a
transient or a permission problem.

Derive each limit from the domain, or measure it, rather than from the sample
in hand. A rule inferred from the first few inputs (a number is always seven
digits) encodes the sample, and the first real input outside it fails or,
worse, passes a wrong check. When a real input contradicts the rule, widen the
rule.

## 7. Apply through the one durable surface

Run `<APPLY_SURFACE>`. Do not write an ad-hoc script, and do not call the
target's endpoint by hand. When the surface cannot do something the task
needs, add the capability to it, so the next run has it and the change is
reviewed like any other.

The apply surface converges every managed record, not only the new ones
(`design-posture.converge-on-drift`). That is the point: a rerun is safe, and
drift on existing records is repaired in the same pass.

## 8. Prove it by read-back, including what did not change

Run `<READ_BACK>` and compare it with the contract, matched on
`<STABLE_KEY>`:

- each new record is present, with the declared field values and a non-empty
  secret (checked for presence, never printed);
- **every other record is unchanged**. Compare against a read-back taken
  before the apply, or against the contract.

An exit code of zero, or a run summary that reports nothing changed, is not
this proof. Some automation tools report "unchanged" for writes that did
change the target (`protocols/verify.md`; the tool's own library page says
which). Report the table, by name and key, never with secrets.

## Privacy

The input is personal data.

- Images and pasted lists stay in the session's scratch area. They are never
  committed, attached to a ticket, or copied into the knowledge graph.
- A field the target has no slot for (a birth date, a birth place, a tax
  number printed on a card) is never stored anywhere, not even "for later".
- The contract legitimately holds names and keys. Secrets live only in
  `<SECRET_STORE>`.
- Examples, fixtures and tests use synthetic people and numbers
  (`stewardship-posture.synthetic-data-only`).

## Reference files

- `core/method/design-posture.md` (§11, convergence by read, compare, write)
- `core/method/secrets-posture.md` (one channel in, recorded by name)
- `core/method/restrictive-policy.md` (report-only defaults for destructive
  writes)
- `core/method/stewardship-posture.md` (§3, synthetic data only)
- `protocols/verify.md` (read-back as evidence; an exit code is not state)
- `protocols/deliver.md` (numbered questions to the owner)
- `skill-corpus/pypi/converge-records-over-http-api.md` (the same procedure's
  stack-specific steps when the target is an appliance managed over HTTP with
  Ansible)
