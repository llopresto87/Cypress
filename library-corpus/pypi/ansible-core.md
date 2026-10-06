# ansible-core — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
ansible-core is the Ansible engine: the command-line tools (`ansible`,
`ansible-playbook`, `ansible-galaxy`, `ansible-vault`, `ansible-config`,
`ansible-doc`, `ansible-inventory`), the playbook language and runtime, and the
`ansible.builtin` collection. It is agentless: a control node drives managed
nodes over SSH (or PowerShell remoting and other connection plugins), shipping
each module to the target and running it there, with no daemon and no
database. Licence GPL-3.0-or-later. Two PyPI distributions install it:

- `ansible-core`: the engine itself.
- `ansible`: a different distribution, the community package, which depends on
  ansible-core and bundles a curated set of Galaxy collections. The two have
  separate version numbers and maintenance.

Collections used with ansible-core have their own pages under
`library-corpus/galaxy/`.

## Install, setup and configuration
- Control node: a UNIX-like machine with Python (Windows only through WSL).
  Install into a virtual environment, `pip install ansible-core`, and pin it in
  the project's requirements like any other Python dependency. Each release
  line sets its own minimum control-node Python; check it before choosing a
  line.
- Managed nodes need a Python interpreter for Python modules. The interpreter
  is discovered per host on first use (`interpreter_python = auto` is the
  default); override it per host or group with `ansible_python_interpreter`.
- Configuration file lookup: the file named by `ANSIBLE_CONFIG`, then
  `./ansible.cfg` in the current directory, then `~/.ansible.cfg`, then
  `/etc/ansible/ansible.cfg`. The first file found wins and the others are
  ignored entirely; nothing merges. An `ansible.cfg` in a world-writable
  current directory is not loaded.
- Collections: `ansible-galaxy collection install -r collections/requirements.yml`.
  Each entry has `name:` and `version:` (and optionally signature URLs). With
  no `version:` the newest release is installed, so a name-only list drifts at
  every fresh install. Pin with a range such as `">=1.0.0,<2.0.0"`; quote
  operators on the command line.

## Core API / usage shape
- Project layout: an inventory (static INI or YAML, or an inventory plugin);
  `group_vars/` and `host_vars/` beside the inventory or the playbook; plays
  (`hosts`, `pre_tasks`, `roles`, `tasks`, `post_tasks`, `handlers`); roles
  with the standard directories `tasks/ handlers/ defaults/ vars/ files/
  templates/ meta/`.
- `group_vars/<group>` and `host_vars/<host>` (a file with an optional
  `.yml`, `.yaml` or `.json` extension, or a directory) load for the group or
  host of exactly that name. A directory is read file by file in lexical order.
- Call every module, role and plugin by its fully qualified collection name:
  `ansible.builtin.copy`, `community.docker.docker_container`. A short name
  resolves through the collection search order and redirects, and that
  resolution changes when collections move modules.
- Control-node work: `connection: local` or `delegate_to: localhost` runs a
  task on the control node, and `ansible.builtin.uri` is the module for HTTP
  calls. Together they drive HTTP APIs and agentless appliances.
- Hosts without Python: `gather_facts: false` and `ansible.builtin.raw` (which
  needs no interpreter on the target) to install Python or talk to the device;
  normal modules after that.
- Role inputs: `meta/argument_specs.yml` makes Ansible insert a validation task
  at the start of the role. The alternative is an `ansible.builtin.assert`
  (`that:`, `fail_msg:`) at the top of `tasks/main.yml`.
- Reuse: `import_*` is static, pre-processed at parse time, and keywords on the
  import (`when`, `tags`, `become`, `delegate_to`) apply to every imported
  task. `include_*` is dynamic, processed at run time once per loop item, and
  its keywords apply to the include statement only; pass keywords to the
  included tasks with `apply:`. The docs advise one approach per playbook.

## Idioms & best practices
- Variable precedence, lowest to highest: role `defaults/`; inventory
  file or script group vars; inventory `group_vars/all`; playbook
  `group_vars/all`; inventory `group_vars/*`; playbook `group_vars/*`;
  inventory file or script host vars; inventory `host_vars/*`; playbook
  `host_vars/*`; host facts and cached `set_fact`; play `vars`, `vars_prompt`,
  `vars_files`; role `vars/`; block vars; task vars; `include_vars`;
  registered vars and `set_fact`; role and `include_role` params; include
  params; extra vars (`-e`), which always win. Role defaults are the lowest by
  design: they exist to be overridden. Some notes in circulation put role
  defaults above inventory and play vars; that ordering is wrong.
- Vault layout: `group_vars/all/vars.yml` holds plain values that refer to
  `vault_*` names, and `group_vars/all/vault.yml` holds the encrypted values.
  Both load automatically through the directory form, so no `vars_files` is
  needed. The `vault_` prefix is a convention observed in practice, not an
  upstream rule.
- Dispatch per OS family with
  `include_tasks: "{{ ansible_facts['os_family'] | lower }}.yml"`.
- Confirm the target set before an apply: `ansible-playbook site.yml
  --list-hosts --list-tasks`, and `--syntax-check`. `--limit` / `-l` matches
  inventory names and patterns. Observed in practice: it does not match DNS
  names, so target by `inventory_hostname` and keep DNS or display names in
  explicit variables.
- `meta: reset_connection` drops the persistent connection (SSH
  ControlPersist). Observed in practice: after adding the connecting user to a
  group (for example `docker`), later tasks see the new membership only after
  this reset.
- Encrypt one value with
  `printf '%s' "$SECRET" | ansible-vault encrypt_string --vault-id prod@prompt --stdin-name db_password`.
  Use `echo -n` or `printf '%s'`: plain `echo` encrypts a trailing newline into
  the secret. A secret typed as an argument lands in shell history.
- Several vault passwords: label each with `--vault-id label@source`. For
  non-interactive runs supply `--vault-password-file` or
  `ANSIBLE_VAULT_PASSWORD_FILE`. Observed in practice: fail fast when the vault
  context is missing rather than retrying.
- Quote file modes: `mode: "0644"`. The `file` module docs say modes are octal
  and should be quoted. Observed in practice: an unquoted `644` is read as
  decimal and sets wrong permissions, and an unquoted `0644` works only through
  YAML 1.1 octal parsing. yamllint's `octal-values` and ansible-lint's
  `risky-octal` rule catch it.

## General pitfalls
- `ansible.builtin.uri` reports `changed: false` on every request unless it
  writes a `dest` file (or changes file attributes). A POST, PUT or DELETE
  that changes a remote system still shows `ok`. Give write tasks a
  `changed_when` on the status or response body, and read the state back
  afterwards: a play recap is not evidence of state.
- `uri` with `body_format: form-multipart`: a part given as a mapping with
  `filename:` and no (or empty) `content:` is read from a file on the host where
  the module runs, which is the control node under `connection: local`. A
  missing file fails the task before any request leaves, so a "refusal"
  gathered that way says nothing about the server. With non-empty `content:`
  the content is sent and `filename:` is only the part's name. One of the two
  is required, and `Content-Type` cannot be overridden for form-multipart.
- `command` and `shell` report `changed: true` every time they run; `creates`
  or `removes` skip the run when the file condition decides. Give every command
  task a `changed_when` (and a `failed_when` where the exit code lies);
  ansible-lint's `no-changed-when` rule enforces it.
- Observed in practice: a `changed_when` that matches English text in a tool's
  output (`"Creating" in result.stdout`) breaks silently when the tool rewords
  its output. Prefer a module that reports `changed` itself, or compare
  structured state before and after.
- `when: x is defined` skips a task silently when a host lacks the variable.
  Use `assert`, role argument specs or the `mandatory` filter for required
  inputs, and keep `is defined` / `default` for optional ones. A non-boolean
  string in `when` needs `| bool`.
- A `group_vars` file whose name matches no inventory group (and is not
  `all`) is never loaded; `group_vars/vault.yml` with no `vault` group is
  silently ignored unless a play names it in `vars_files`.
- `include_role` keywords such as `delegate_to` do not reach the tasks inside
  the role; use `apply:` or `import_role`. Observed in practice:
  `--syntax-check` rejects `delegate_to` written directly on `include_role` as
  "not a valid attribute"; the docs only say the keyword applies to the include
  statement.
- `loop` is not a `block` keyword ("'loop' is not a valid attribute for a
  Block"); the blocks guide names loops as the exception. To repeat a group of tasks,
  put the body in a tasks file and loop an `include_tasks` of it.
- A delegated task runs the module on the delegate but evaluates variables for
  the original `inventory_hostname`, and facts it gathers land on the original
  host unless `delegate_facts: true`.
- Observed in practice: under `delegate_to: localhost` or `connection: local`,
  modules run with the interpreter discovered for localhost, which can differ
  from the Python running `ansible-playbook`. A module's Python dependencies
  (an SDK, `cryptography`, `requests`) must import in that interpreter. Set
  `ansible_python_interpreter: "{{ ansible_playbook_python }}"` for localhost
  so modules run in the same virtual environment. The docs describe discovery
  and the override, not this drift.
- Observed in practice: `no_log: true` hides the failure reason along with the
  secret. Drive it from a variable and lift it only for a bounded debug run
  (one task, one host, one run), then restore it.

## Testing
- `ansible-playbook --syntax-check` parses without connecting to anything. It
  takes a playbook. Observed in practice: run on a role's `tasks/main.yml`, it
  parses the task list as plays and reports false errors such as "not a valid
  attribute for a Play". Check a role through a small wrapper playbook (`hosts: localhost`,
  local connection) that includes it.
- Check mode (`--check`) is a simulation. Modules that support it report the
  change they would make; modules that do not support it do nothing and report
  nothing. `command` and `shell` run in check mode only when `creates` or
  `removes` decides, so every task that reads their registered output gets no
  data. `check_mode: false` on a read-only probe forces it to run for real
  during a check run; `check_mode: true` forces simulation.
- Observed in practice: a green `--check` does not predict a green apply.
  Follow it with a scoped real run (`--limit` to one host) and read the
  resulting state back instead of trusting the recap counts.
- Linting with ansible-lint and yamllint, and role testing with Molecule, are
  separate tools; this page does not cover their rule sets. Install the
  declared collections before judging an ansible-lint run: a module it cannot
  resolve is reported as `syntax-check[unknown-module]` (observed in practice,
  an older run reported the same cause as `load-failure`), which hides every
  other finding in that file. ansible-lint installs what `requirements.yml`
  lists when a listed collection is missing, so declare every collection
  there.

## Security defaults
- Secrets belong in vault-encrypted files or values, and the tasks that handle
  them carry `no_log: true`.
- Host-key checking is on by default. Turning it off
  (`host_key_checking = False`, `ANSIBLE_HOST_KEY_CHECKING`, or
  `StrictHostKeyChecking=no` in the SSH arguments) removes
  man-in-the-middle protection. A jump host follows its own ProxyCommand or
  ssh config, not the command-line options, so check each hop. For hosts that
  are rebuilt often, pin a per-fleet `known_hosts`, accept only new keys
  (`StrictHostKeyChecking=accept-new`), and re-pin a rebuilt host's key as a
  step of the rebuild, because a changed key is refused. Write down the trust
  assumption if checking stays off.
- `become` raises privileges per play, block or task; `become_user` alone does
  not imply `become: true`.
- An `ansible.cfg` in a world-writable directory is ignored by design. Observed
  in practice: a wrapper script that walks up the directory tree looking for
  `ansible.cfg` should stop at the repository root, or it can pick up a file
  you did not mean to trust.
- Pin collections by version range in `requirements.yml`; an unpinned list
  installs whatever is newest on the next fresh control node.

## Operational behaviour
- Each play gathers facts from its hosts first unless `gather_facts: false`;
  they live under `ansible_facts`.
- Parallelism: `forks` (`-f`) sets how many hosts run at once, and the play's
  `strategy` sets how tasks advance across hosts.
- Handlers run at the end of the play unless `meta: flush_handlers` runs them
  earlier.
- There is no daemon on either side: each run connects, ships modules, and
  exits. The other `meta` actions (`end_host`, `end_play`) stop work for one
  host or the whole play.

## Interop
- Collections supply every module outside `ansible.builtin`. Install them with
  `ansible-galaxy` and call them by FQCN.
- Observed in practice: a control node built from the `ansible` community
  package has a large set of collections "for free", so a playbook can call a
  collection its `requirements.yml` never declares and work until it first runs
  on an ansible-core-only node. Declare every collection you call, and run CI
  on ansible-core plus the declared collections only.
- A collection module's `requirements:` (shown by `ansible-doc`) apply to the
  host where the module executes, which is the control node for
  `delegate_to: localhost` tasks.

## Major lines
ansible-core numbers its release lines 2.N; each line is maintained for a
limited window (the latest line plus two older ones), and each sets its own
control-node Python minimum.

### Before 2.10 (the monolithic `ansible`)
- Modules shipped inside the engine and were called by short names. Playbooks
  from that era assume modules that now live in collections.

### 2.10 and later (`ansible-core` plus collections)
- The engine and the content split: ansible-core ships the language, runtime
  and builtin plugins; every other module lives in a collection. The `ansible`
  package became the community bundle of ansible-core plus collections, with
  its own semantic version (from its 3 line on) and one maintained version at a time.
- Old short names keep working through redirects in the collections'
  `meta/runtime.yml`, with deprecation warnings, until a collection major drops
  them.

## Upstream docs
- Docs: https://docs.ansible.com/ansible/latest/
- Repo: https://github.com/ansible/ansible
