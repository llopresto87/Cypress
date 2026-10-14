# community.routeros — galaxy

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`community.routeros` is the community Ansible collection for MikroTik
RouterOS devices. Galaxy namespace `community`, name `routeros`; licence
GPL-3.0-or-later; it depends on `ansible.netcommon`. It is not part of
ansible-core (`library-corpus/pypi/ansible-core.md`). It reaches a device in
two ways, and every module belongs to one of them:

- **The RouterOS API** (TCP 8728 plain, 8729 with TLS, by default), driven
  from the control node through the Python library `librouteros`: `api` (raw
  add, remove, update, query and commands), `api_info` (read one path, normalized),
  `api_modify` (make a path match a declared list), `api_find_and_modify`
  (change the entries a condition selects) and `api_facts`. They share the
  module defaults group `group/community.routeros.api`.
- **SSH**, through the `ansible.netcommon.network_cli` connection and this
  collection's `routeros` cliconf plugin: `command` (run CLI commands) and
  `facts`.

It also ships filter plugins for RouterOS quoting (`quote_argument_value`,
`quote_argument`, `join`, `split`, `list_to_dict`).

## Install, setup and configuration
- `ansible-galaxy collection install community.routeros`, or an entry with a
  pinned `version:` range in `collections/requirements.yml`. The `ansible`
  community package also bundles a copy, which is not upgraded when the
  collection is installed from Galaxy, and the reverse.
- API modules: `librouteros` must be importable on the host that runs the
  module, which is the control node, because they run under `hosts:
  localhost` or `delegate_to: localhost`. UTF-8 `encoding` needs librouteros
  3.2.1 or newer; modifying a path that has a property called `cmd` (such as
  `container`) needs librouteros 4.0.0 or newer.
- API connection options on every API module: `hostname`, `username`,
  `password`, `port` (default 8728, or 8729 when `tls: true`), `tls`,
  `validate_certs`, `validate_cert_hostname`, `ca_path`, `force_no_cert`,
  `timeout` (default 10 seconds) and `encoding` (default ASCII). Set them once
  per play through `module_defaults: group/community.routeros.api:`; every API
  task in the play then inherits them.
- SSH modules: an inventory host with
  `ansible_connection=ansible.netcommon.network_cli`,
  `ansible_network_os=community.routeros.routeros`, `ansible_user` and the
  password or key. `network_cli` uses paramiko unless its `ssh_type` is
  `libssh` (ansible-pylibssh).
- Device prerequisites for SSH: an identity of letters, digits and dashes
  only, no longer than 19 characters; similar trouble follows unusual
  characters in the user name. Upstream notes that modern MikroTik RouterOS
  refuses password login over SSH for a user that has an SSH key installed.

## Core API / usage shape
- **`api_modify`** makes one path match `data`. Entries present on the device
  but absent from `data` are kept by default (`handle_absent_entries:
  ignore`) or deleted (`remove`); `ensure_order: true` (which needs `remove`)
  also enforces the order. `handle_entries_content` decides fields an entry
  does not mention (`ignore`, the default; `remove`;
  `remove_as_much_as_possible`). `restrict` (from 2.18.0) limits the
  operation to the entries whose field matches, for example one firewall
  chain, so `remove` acts on that subset only. Write-only fields are
  `create_only` by default (`handle_write_only`); read-only fields make the
  module fail by default (`handle_read_only: error`). It returns `old_data`
  and `new_data`. Dynamic and builtin entries are ignored. The module supports
  a fixed list of paths and is described upstream as still heavily in
  development.
- A field can be unset three ways in `data`: nothing after the colon, a null
  value, or the key prefixed with `!`.
- **`api_info`** reads one path, normalized, in the shape `api_modify` takes,
  so its output is a restorable backup of that path. Dynamic, builtin and
  read-only entries are left out unless `include_dynamic`, `include_builtin`
  or `include_read_only` say otherwise; `hide_defaults` (default true) drops
  default values; `handle_disabled` chooses how unset values appear.
- **`api_find_and_modify`** finds entries by `find` and sets `values` on all
  of them. `require_matches_min` (default 0) and `require_matches_max` make it
  fail instead of modifying when the match count is unexpected.
- **`api`** is the raw interface: `path` plus one of `add`, `remove`,
  `update`, `cmd`, `query` or `extended_query` (attributes plus `where`
  conditions). It does not support check mode.
- **`command`** sends CLI commands over SSH and returns their output;
  `wait_for` with `retries` and `interval` polls until conditions on the
  output hold. Each command starts with `/` and is complete: nesting (`/ip`
  then `print`) is an error.
- **Quoting**: `community.routeros.quote_argument_value`, `quote_argument` and
  `join` build CLI-safe arguments (a comment with spaces or quotes, say);
  `split` and `list_to_dict` parse them.

## Idioms & best practices
- Prefer the API modules to `command`: they return structured data, support
  check mode and diff, and `api_modify` is idempotent. Keep `command` for what
  the API path list does not cover.
- **Reconcile a set in one call.** `api_modify` with `handle_absent_entries:
  remove` makes the whole path (or the `restrict`ed subset) equal to `data`.
  Pass the full list in one task; never loop it per item (General pitfalls).
- Back up a path with `api_info` before changing it with `api_modify`; the
  output is the restore input.
- Use `restrict` to own one slice of a shared path (a chain, a list name)
  without touching entries another role owns.
- Give `api_find_and_modify` a `require_matches_min` and `require_matches_max`
  that encode what you expect, so a wrong `find` fails instead of editing
  nothing or everything.
- Enable TLS on the API service, install a certificate whose subject
  alternative names include the address you connect to, and keep
  `validate_certs` and `validate_cert_hostname` on (Security defaults).
- Pass CLI arguments through the quoting filters rather than hand-quoting. A
  multi-word value that reaches a playbook through `-e` needs JSON or inner
  quotes (`library-corpus/pypi/ansible-core.md`, the extra-vars pitfall).

## General pitfalls
- **A loop around a reconciling call keeps only the last item.** With
  `handle_absent_entries: remove`, each `api_modify` call makes the path equal
  to the `data` it was given. Called once per `loop:` item, every call deletes
  the entries the previous calls added, the task reports `changed` on every
  run, and only the last item survives on the device (observed in practice;
  the option's documented meaning implies it). Tell: `loop:` or `with_*` on an
  `api_modify` that carries `remove`.
- **On a path without a key, a changed entry is added, not updated.** For a
  list path whose entries have no identifying field, `api_modify` with
  `handle_absent_entries: ignore` matches an existing entry only when every
  field in `data` equals the device's value. Changing any field therefore
  adds a second entry beside the old one instead of modifying it (the
  matching code, `essentially_same_weight`, in the module source; observed in
  practice). Paths with primary keys match by those keys instead. To change
  such an entry in place, use `remove` with the full list, or
  `api_find_and_modify`. On these paths `remove` cannot be combined with
  `handle_entries_content: ignore`; the module fails.
- **Check mode does not ask the device.** `api_modify` in check mode computes
  the diff against what it read and sends nothing, so a parameter the device
  rejects still passes the check. Observed in practice: a field the device's
  RouterOS release did not accept on that row was shown as a clean diff in
  check mode, and the real apply failed with "unknown parameter". Upstream
  documents check mode as a prediction without modifying the target and says
  nothing about device-side validation. Tell: the diff adds a field to an
  entry whose device copy lacks it, often on disabled entries. Read such
  lines before applying, and after a failed multi-step apply, confirm the
  device state before retrying.
- **`command` has no check mode and always reports changed.** Since 3.0.0 it
  declares no check-mode support, so under `--check` it is skipped (earlier
  releases claimed support and ran the command anyway). Since 2.0.0 it always
  reports `changed`; give it `changed_when`. A task that reads its registered
  output gets nothing in check mode.
- **Long-running prints hit the SSH command timeout.** `network_cli` waits
  `persistent_command_timeout` seconds for a command to return (default 30,
  also `[persistent_connection] command_timeout` or `ansible_command_timeout`)
  and then raises and closes the connection. Raise it for commands that print
  a lot, and keep commands short: RouterOS wraps long lines unless the login
  user carries a `+cet512w`-style suffix.
- **Write-only fields break strict idempotence.** A path with write-only
  fields cannot compare their current value; with `handle_write_only:
  always_update` the task reports `changed` every run, and with the default
  `create_only` a later change to such a field is not applied.
- **Type matters in `restrict`.** A string `"0"` does not match a value
  librouteros returned as the integer `0`; list both forms when unsure.
- **`api` fails on errors since 2.0.0.** Earlier releases never failed, so
  old roles may rely on that; accept specific failures with `failed_when`.

## Testing
- `--check --diff` on the API modules shows the per-entry change (`old_data`
  against `new_data`) without writing; it does not prove the device accepts
  it (General pitfalls).
- Run an `api_modify` task twice: the second run must report `changed: false`.
  A second run that still changes points at a write-only field, a value the
  device normalizes, or a reconciling call inside a loop.
- `api_info` before and after an apply gives a diffable record of what
  changed on the device.
- Upstream documents no simulator or mock device; a disposable lab device
  stands in for production when an apply must be proved before it runs.

## Security defaults
- `tls` defaults to false: without it the API carries credentials and
  configuration in clear text. Upstream recommends `tls: true` even on a
  trusted network.
- `validate_certs` defaults to true, but `validate_cert_hostname` defaults to
  false (kept for backwards compatibility), so a valid certificate for any
  host is accepted. Set it to true with a certificate that names the device
  (its IP address included) and `ca_path` for a private CA.
- `force_no_cert: true` uses anonymous Diffie-Hellman, open to a
  man-in-the-middle; it exists for first setup only.
- Credentials set in `module_defaults` belong in vault-encrypted variables;
  tasks that print device configuration can print secrets, so review diff
  output before it lands in a log.

## Operational behaviour
- API modules open a connection per task from the control node; SSH modules
  hold a persistent `network_cli` connection per host for the play, bounded
  by its connect and command timeouts.
- A reconciling `api_modify` reads the whole path, computes creates,
  modifies, removes and moves, and then applies them one by one. The source
  has no rollback step, so a failure partway leaves the earlier changes on
  the device; take an `api_info` backup first.
- New RouterOS releases add paths and fields; a key the collection does not
  know for a path fails the task ("Unknown key") before anything is sent, and
  the collection's changelog records each addition.

## Interop
- **ansible-core** (`library-corpus/pypi/ansible-core.md`): module defaults
  groups, check mode, `delegate_to: localhost`, and the extra-vars pitfall.
- **ansible.netcommon**: the `network_cli` connection and its timeouts, used
  by `command` and `facts`.
- **librouteros** (PyPI): the API transport, a requirement on the control
  node.
- **community.crypto** (`library-corpus/galaxy/community.crypto.md`): upstream
  points to its CA guide to build the device certificates.
- **ansible-lint** (`library-corpus/pypi/ansible-lint.md`): `args[module]`
  reports the API connection options set in `module_defaults` as missing.

## Major lines

### 1.x line
- The original `api` and `command` modules; certificate validation options
  arrived in 1.2.0.

### 2.x line
- 2.0.0 changed behaviour: `api` fails on errors (it never did before),
  splits commands the way the RouterOS CLI does rather than on whitespace,
  and `command` always reports `changed`. The quoting filters arrived here.
- `api_facts` and `api_find_and_modify` arrived in 2.1.0, `api_info` and
  `api_modify` in 2.2.0, `restrict` in 2.18.0, and the
  write-only and read-only handling options in 2.10.0.

### 3.x line
- 3.0.0 dropped support for Ansible 2.9, ansible-base 2.10 and ansible-core
  before 2.15, and `command` stopped declaring check-mode support. Stay on
  2.x for older controllers.

## Upstream docs
- Collection docs: https://docs.ansible.com/ansible/latest/collections/community/routeros/
  (the `latest` tree documents the copy bundled in the `ansible` package;
  `devel` documents the newest Galaxy release)
- API guide: https://docs.ansible.com/ansible/latest/collections/community/routeros/docsite/api-guide.html
- SSH guide: https://docs.ansible.com/ansible/latest/collections/community/routeros/docsite/ssh-guide.html
- Quoting guide: https://docs.ansible.com/ansible/latest/collections/community/routeros/docsite/quoting.html
- `network_cli` timeouts: https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/network_cli_connection.html
- Repo and changelog: https://github.com/ansible-collections/community.routeros
