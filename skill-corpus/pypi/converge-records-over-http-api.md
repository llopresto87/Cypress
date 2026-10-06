---
name: converge-records-over-http-api
description: Converge a set of records (users, credentials, schedules, settings) on an appliance that is managed only through an HTTP API, using Ansible roles that run on the control node. Use when a plant drives a device or service with no agent and no SSH through ansible.builtin.uri, and needs logins, offline contract checks, guarded writes and read-back proof.
id: skill.converge-records-over-http-api
tier: 2
kind: skill
title: converge-records-over-http-api, Ansible against an HTTP-managed appliance, gate role to read-back
owns:
  - converge-records-over-http-api.layout
  - converge-records-over-http-api.session-gate
  - converge-records-over-http-api.converge-loop
  - converge-records-over-http-api.pitfalls
requires:
load_when:
  - "manage an appliance over its http api with ansible"
  - "ansible uri login token then write records to a device"
  - "playbook reports changed=0 but the device changed"
  - "converge users on a device that has no ssh"
stack:
  - library-corpus/pypi/ansible-core
est_tokens: 3387
---

# Suggested skill: converge-records-over-http-api

> Optional procedure, stack-keyed to Ansible (`library-corpus/pypi/ansible-core`).
> The target is an appliance or service that offers no SSH and no agent, only
> an HTTP API, and Ansible drives it from the control node with
> `ansible.builtin.uri`. When the records come from photos or pasted lists,
> run `skill-corpus/provision-records-from-unstructured-input.md` first: it
> owns the generic rules this page shares (the offline-check list, the
> automation's own account, read-back), and this page is its Ansible apply
> surface. **Composes** `library-corpus/pypi/ansible-core.md` (the `uri` module's
> `changed` behaviour, `form-multipart` file parts, `encrypt_string`, variable
> precedence and `group_vars` loading: read those facts there),
> `core/method/design-posture.md` (§11, `design-posture.converge-on-drift`),
> `core/method/restrictive-policy.md` (report-only defaults for destructive
> writes), `core/method/secrets-posture.md`, and `protocols/recover.md`
> (classify a failure before retrying) by reference.

**Instantiate by supplying:** `<APPLIANCE_GROUP>` (the inventory group whose
hosts are the appliances; each host's vars hold its base URL), `<LOGIN>` (the
login endpoint, its body format and fields, and where the session token sits
in the response), `<TOKEN_HEADER>` (how later calls present the token),
`<LOGOUT>` (the logout endpoint), `<LIST>`, `<READ_ONE>`, `<CREATE>`,
`<UPDATE>` and `<DELETE>` (the record endpoints), `<SUCCESS_CODES>` (the
response codes or body values that mean the appliance accepted a write),
`<STABLE_KEY>` (the record field that identifies it across runs),
`<PAGE_CAP>` (the largest page size the list endpoint accepts, as measured),
`<FIELD_LIMITS>` (each field's limits, as measured), and `<RECORDS_VAR>` (the
host variable that declares the desired records).

## When to apply

- A plant manages a device or a hosted service whose only management surface
  is HTTP (a web UI's own backend, a REST or form endpoint set), and Ansible
  is the plant's automation.
- Records on that target (people, credentials, schedules, network settings)
  must match a declared state, and a person or a later run must be able to
  prove that they do.
- A run reported success and the target did not change, or the reverse.

Not for targets Ansible can reach over SSH or WinRM with a native module: use
the module. Not for a target with a maintained collection that wraps its API:
read that collection's library page first.

## 1. Lay the repository out as roles, and playbooks as composition

One role per concern:

| role | does | calls the target? |
|---|---|---|
| gate | logs in, stores the token as a host fact; a separate `logout` tasks file ends the session | yes |
| contract check | validates `<RECORDS_VAR>` alone | **no** |
| one role per record family | reads, compares, writes on drift, reports | yes |
| guarded-setting roles | settings whose wrong value strands the operator (addressing, identity) | yes, behind `apply` |

Every playbook has the same shape and holds no inline procedure:

```yaml
- name: records
  hosts: <APPLIANCE_GROUP>
  connection: local          # uri runs on the control node
  gather_facts: false        # the appliance has no Python to gather with
  serial: 1                  # one appliance at a time; a fault stops at the first
  pre_tasks:
    - name: Validate the declared records (no HTTP)
      ansible.builtin.import_role: { name: records_check }
      tags: [always]
    - name: Open a session
      ansible.builtin.import_role: { name: gate }
      tags: [always]
  roles:
    - role: records
  post_tasks:
    - name: Close the session
      ansible.builtin.import_role: { name: gate, tasks_from: logout.yml }
      tags: [always]
```

The check runs before the gate on purpose: a fault in the declared records
fails in seconds, with no session opened and no retry backoff spent. Tag it
`always` so a `--tags` run still validates.

New work is a new small role plus a playbook line, never a task pasted into a
playbook. A read-only "show" playbook (gate, list, print by `<STABLE_KEY>`,
logout) is the read-back surface for step 7.

## 2. The gate role owns the session

```yaml
# roles/gate/tasks/main.yml
- name: gate | log in
  ansible.builtin.uri:
    url: "{{ base_url }}<LOGIN>"
    method: POST
    body_format: form-urlencoded     # or json: whatever the target's own UI sends
    body: { user: "{{ api_user }}", password: "{{ api_password }}" }
    return_content: true
  # token_from_login: the token extractor of the plant's one response-parsing
  # filter plugin (see "Parse responses in one place" below)
  register: login
  no_log: true
  changed_when: false

- name: gate | the login produced a token
  ansible.builtin.assert:
    that:
      - login.status == 200
      - login.content | token_from_login | length > 0
    fail_msg: "Login failed for {{ api_user }} at {{ inventory_hostname }}: check the credential and the account's role"

- name: gate | store the token
  ansible.builtin.set_fact:
    api_token: "{{ login.content | token_from_login }}"
```

`logout.yml` calls `<LOGOUT>` with `changed_when: false` and
`ignore_errors: true`: logout is best effort, and a failed logout must not
turn a good run red.

Know what `post_tasks` does not cover. By default Ansible stops running tasks
on a host after a task on that host fails (upstream "Error handling in
playbooks"), so a failed run never reaches the logout in `post_tasks`. That is
fine when the target expires tokens. When it caps concurrent sessions, wrap
the roles in a `block:` with the logout in its `always:` section, which runs
whatever the block's outcome; upstream notes that `always` does not run for an
unreachable host or an invalid task definition.

Parse responses in one place. Parse every target response through one filter
plugin that wraps `tool-corpus/ops/lenient-json-response-parser.md` (its script runs as-is; the plugin is only the call
site), and never call `from_json` on a target response inside a role. The
tool page holds the parsing rules and the token-claim decoder, and its
warning that a decoded claim is never an authorization input.

## 3. The contract-check role asserts everything knowable offline

```yaml
- name: check | each managed record fits the target's limits
  ansible.builtin.assert:
    that:
      - item.name | length <= <FIELD_LIMITS: name length>
      - item.key | string is match('<FIELD_LIMITS: key pattern>')
    fail_msg: "Record {{ item.key }} ('{{ item.name }}'): <the limit, and the fix>"
    quiet: true
  loop: "{{ records }}"
  loop_control: { label: "{{ item.key }}" }
  when: item.manage | default(true) | bool
```

Write each check that step 6 of
`skill-corpus/provision-records-from-unstructured-input.md` lists as an
`assert` like the one above, and add one that every required field is
present. Put `no_log: true` on the secret assertions only, so the others
still print which record failed. Each `fail_msg` names
the record and the fix.

`<STABLE_KEY>` uniqueness covers every declared record, managed or not: a
managed record that shares a key with an audit-only record still shares a
card. The field, privilege and secret checks cover managed records only
(step 5), because a record imported for audit may legitimately break a rule
the plant applies to its own records.

## 4. The record role reads, compares, and writes only on drift

1. **Read the full list.** Page through `<LIST>` with a page size at or below
   `<PAGE_CAP>` until the count the target reports. Over the cap, a target
   may answer with an unrelated error, such as an authentication failure.
   Why the cap is a measurement and never one page is on
   `skill-corpus/characterize-undocumented-device-protocol.md` (Pitfalls).
   When `<READ_ONE>`, `<UPDATE>` or `<DELETE>` address a record by the
   target's own id, build the key-to-id map from this list on every run.
2. **Normalize the desired list once**, so every later step can read the
   `manage` flag without repeating its default:
   ```yaml
   - name: records | apply defaults once
     ansible.builtin.set_fact:
       desired: "{{ desired | default([]) + [{'manage': true} | combine(item)] }}"
     loop: "{{ records }}"
   ```
   The defaults mapping comes first in `combine`, so a value declared in the
   inventory always wins.
3. **Create what is missing.** Select managed records whose `<STABLE_KEY>` is
   not on the target, and `include_tasks` a create file per record. When the
   target is known to refuse the first write of a fresh session, open a fresh
   session inside the create file, retry the write with `until:` on
   `<SUCCESS_CODES>` with explicit `retries:` and `delay:`, set
   `ignore_errors: true` on that task, and follow it with an `assert` whose
   `fail_msg` carries the target's raw response. A record that never got
   created must fail the run, never pass as converged. When the target needs
   the id on create, take the next-free value it reports. An "already exists"
   answer is not a refusal: handle it the way the target's own UI does (a
   forced save, or an update).
4. **Compare and update on drift.** Read each managed record with
   `<READ_ONE>`, compare each declared field, and call `<UPDATE>` only where a
   field differs. Build the update body from the declared fields over the
   live record just read (`declared | default(live)` per field), so a field
   the inventory does not declare is sent back unchanged. An update endpoint
   that takes the whole record resets any field the body leaves out.
   Combine the per-field differences with `or`. A list of
   conditions under `when:` is a logical **and** (upstream "Conditionals"), so
   writing one condition per field there updates a record only when every
   field differs at once.
5. **Delete only what is listed as absent**, and only when it is present.
   Never delete a record merely because it is undeclared.
6. **Report the unmanaged.** List records on the target that the inventory
   does not declare, and print them. Do not write them.

Give every write task a `changed_when` taken from the response (status code,
or a body value in `<SUCCESS_CODES>`). Without it the play recap reports
`changed=0` over real writes: `uri` reports `changed` only when it writes a
`dest` file (`library-corpus/pypi/ansible-core.md`, General pitfalls).
A write the target refuses fails the run with an actionable `fail_msg` that
carries the raw response, so the next operator can tell a refusal from a
validation error.

Put `no_log: true` on every write task whose body carries a secret. In
verbose mode Ansible shows what a task was given (upstream FAQ, "How do I
keep secret data in my playbook?"), so a create or update that posts a
secret would print it. The registered result
still holds the response for the following `assert`.

Gate a follow-up check on whether the write ran, not on whether it reported
a change. A re-verify step guarded by `when: write_result is changed`
silently never runs when the write task has no `changed_when`; use
`write_result is not skipped`, or give the write its `changed_when` first.

## 5. Two records are never converged by default

- **The automation's own login account.** The rule is step 5 of
  `skill-corpus/provision-records-from-unstructured-input.md`; here it can
  lock the control node out of every appliance at once. Declare the account
  with `manage: "{{ manage_operator_account | default(false) }}"`; the
  override is the extra var `-e manage_operator_account=true`. The verify
  playbook still asserts that the account exists and has the role the
  automation needs.
- **Records found on the target when the plant first adopts it.** Import them
  into the inventory as `manage: false`: declared, read and reported, never
  written. Promote a record to managed one at a time, by owner decision.
  Day-one convergence then never rewrites state nobody has reviewed.

## 6. Settings that can strand the operator sit behind `apply`

A role that changes how the control node reaches the target (its address,
mask, gateway, management port, or the account roles) reads and reports
drift by default and writes only when a role variable `apply` is true; the
default in `defaults/main.yml` is `false` (`restrictive-policy`). After a
write, it re-reads the setting from the address the inventory expects and
fails loudly when the target no longer answers there.

## 7. Secrets, and proof

- Write each per-record secret with
  `ansible-vault encrypt_string --stdin-name <var_name>`, fed by a writer that
  emits no trailing newline (`library-corpus/pypi/ansible-core.md` shows the
  command and the newline trap). Put the vaulted values where the play loads
  them: a `host_vars/<host>/` or `group_vars/<group>/` file, or `vars_files`.
  The loading rule is on the library page.
- Treat each appliance's login credential as its own until one live login
  per host proves a shared one: identical devices on one site still need not
  share an account. Scaffold a new site's credential variables as references
  to vault entries that do not exist yet, so a run against it fails closed on
  an undefined variable instead of falling back to another site's account.
- Prove the run by read-back, as step 8 of
  `skill-corpus/provision-records-from-unstructured-input.md` says: run the
  "show" playbook and match each declared record on `<STABLE_KEY>`. A clean recap or
  `changed=0` is not that proof.

## 8. Pitfalls specific to this shape

- **One error code, two causes.** A target can return the same error code for
  a permanent validation failure (a field too long) and for a transient (the
  first write after login). Classify by varying the input, not by reading the
  code: when the message names a field, test that field first. A retry loop
  that ran out of attempts is not proof that the operation is impossible, and
  an "impossible" verdict stays open until a request is shown to have reached
  the target and been refused for the stated reason. `protocols/recover.md`
  owns failure classification; this rule has no seed doctrine home yet, so
  it is stated here.
- **A multipart "refusal" that never left the control node.** A
  `body_format: form-multipart` part given a `filename:` and no `content:` is
  read from a local file. When that file does not exist the task fails before
  any request is sent, so the failure says nothing about the target
  (`library-corpus/pypi/ansible-core.md`).
- **A stale role comment.** When the role's behaviour changes (a create path
  that once failed now works), rewrite its header comment in the same change.
  A header that still says "this does not work" sends the next reader back to
  the manual workaround.
- **Limits are firmware behaviour.** Field limits, page caps and refusal codes
  belong to the target's firmware or release; re-measure them after an
  upgrade (`skill-corpus/characterize-undocumented-device-protocol.md`,
  step 8). Record each with the release it was measured on, in the plant's
  own notes for the target.

## Reference files

- `skill-corpus/provision-records-from-unstructured-input.md` (the generic
  procedure and the rules this page applies)
- `tool-corpus/ops/lenient-json-response-parser.md` (the one parsing home
  for target responses)
- `skill-corpus/characterize-undocumented-device-protocol.md` (limits are
  measurements; re-verify after a firmware change)
- `library-corpus/pypi/ansible-core.md` (the module and CLI facts this page
  relies on)
- `core/method/design-posture.md` (§11, read, compare, write only on drift)
- `core/method/restrictive-policy.md` (report-only defaults, explicit flags)
- `core/method/secrets-posture.md` (one channel in, names not values)
- `protocols/recover.md` (classify a failure before retrying it)
- Upstream: docs.ansible.com, "Error handling in playbooks", "Blocks" and
  "Conditionals" in the Playbook Guide; the `ansible.builtin.uri` module page
