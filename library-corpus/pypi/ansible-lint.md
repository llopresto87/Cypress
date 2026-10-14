# ansible-lint — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`ansible-lint` checks Ansible playbooks, roles and collections for practices
and behaviour that could be improved. It loads the content the way Ansible
does: it runs `ansible-playbook --syntax-check` on every playbook, and on
every role through a temporary playbook that only includes that role. It then
applies its own rules plus yamllint, grouped into profiles of increasing
strictness. PyPI package `ansible-lint`; licence GPL-3.0-or-later; maintained
by the Ansible project. Installing it installs ansible-core
(`library-corpus/pypi/ansible-core.md`) when it is not already present, and
upstream supports only the last two major versions of Ansible. It is often
installed with pipx or as part of `ansible-dev-tools` rather than listed in a
project's requirements file.

## Install, setup and configuration
- `pip3 install ansible-lint` or `pipx install ansible-lint` (pipx isolates it
  from the project's environment); upstream's recommended route is
  `pip3 install ansible-dev-tools`, which bundles it. The `lock` extra
  (`ansible-lint[lock]`) installs the exact dependency versions a release was
  tested with, inside a virtual environment only. Windows is not supported.
  Upstream also ships a GitHub Action and a pre-commit hook.
- **Configuration file**: `.ansible-lint`, `.ansible-lint.yml`,
  `.ansible-lint.yaml`, `.config/ansible-lint.yml` or
  `.config/ansible-lint.yaml` in the working directory, or one named with
  `-c`. If none is there, parent directories are searched, but never outside
  the git repository. A scalar given on the command line overrides the file;
  list options (`skip_list`, `warn_list`, `exclude_paths`) are extended, not
  replaced.
- **The file is schema-validated.** A key the schema does not know aborts the
  run before any file is linted, with "Additional properties are not allowed"
  and exit code 3 (reproduced). `yamllint_config_file` is such a key: the
  yamllint configuration is found on its own (`.yamllint`, `.yamllint.yaml`,
  `.yamllint.yml`, the user config, or `YAMLLINT_CONFIG_FILE`) or named with
  `--yamllint-file`.
- Settings that matter most:
  - `profile`: `min`, `basic`, `moderate`, `safety`, `shared`, `production`,
    each extending the one before (Core API).
  - `skip_list` hides a rule entirely; `warn_list` reports it without failing;
    `enable_list` turns on opt-in rules (`args`, `no-log-password`,
    `no-same-owner`, `name[prefix]`, and others). The default warn list is
    `experimental`, `jinja[spacing]` and `fqcn[deep]`; a custom `warn_list`
    replaces it, so restate the defaults you want to keep.
  - `offline: true` (or `--offline`) disables installing `requirements.yml`
    and refreshing schemas. Collections must then already be installed.
  - `strict: true` makes warnings fail the run as well.
  - `exclude_paths` entries in the file are relative to the file's location;
    `--exclude` on the command line is relative to the working directory.
  - `mock_modules` and `mock_roles` stand in for content that cannot be
    installed, so the syntax check passes; `extra_vars` supplies variables the
    syntax check needs.
  - `var_naming_pattern` (default `^[a-z_][a-z0-9_]*$`), `loop_var_prefix`,
    `task_name_prefix` tune the naming rules.
- **Ignore file**: `.ansible-lint-ignore` (or
  `.config/ansible-lint-ignore.txt`) beside the config file, one
  `<file> <rule>` per line; such a violation still shows as a warning unless
  the line adds `skip`. `--generate-ignore` writes the file from the current
  findings and overwrites it.

## Core API / usage shape
```
ansible-lint                         # auto-detect content from the project root
ansible-lint site.yml roles/web      # lint the named playbooks and roles
ansible-lint --profile=production    # lint against one profile
ansible-lint -L / -T / -P            # list rules / tags / profiles
ansible-lint -f pep8|sarif|codeclimate|md|brief|full|quiet
ansible-lint --sarif-file out.sarif  # SARIF to a file, stdout unchanged
ansible-lint --fix[=all|none|<rules>] # reformat YAML and apply rule transforms
ansible-lint -t <tags> / -x <tags>   # only / all-but these rules or tags
```
- **Exit codes**: 0 success, 2 violations found, 3 invalid configuration, 4
  lock timeout, 5 no files matched, 8 violations fixed by `--fix` (the `RC`
  constants in the source).
- **Profiles**: `min` holds only what stops Ansible loading the content
  (`internal-error`, `load-failure`, `parser-error`, `syntax-check`); `basic`
  adds style and common coding issues (`no-free-form`, `var-naming`, `yaml`,
  `name`, `schema` and more); `moderate` adds naming polish; `safety` adds
  non-deterministic and risky calls (`latest`, `package-latest`,
  `risky-file-permissions`, `risky-octal`, `risky-shell-pipe`); `shared` adds
  packaging rules for published content (`no-changed-when`, `meta-*`,
  `galaxy`); `production` adds `fqcn` and the rules for certified content. A
  rule in the chosen profile applies even if it is tagged opt-in or
  experimental.
- **Inline suppression**: `# noqa: <rule_id>` at the end of a line in a task
  (several ids space-separated); a line-based rule needs it on that exact
  line. The `skip_ansible_lint` tag skips the task-based rules of a task, not
  the line-based ones, and cannot silence `yaml`.
- Output: violations go to stdout, logging and statistics to stderr.

## Idioms & best practices
- Run it from the project root, always. Upstream states that from 25.7.0,
  running from a subdirectory (inside `roles/` or `tasks/`) is not supported
  and may report zero errors while violations exist.
- Adopt it gradually: start at `min` or `basic`, generate an ignore file for
  the existing findings, and fail only on new ones; raise the profile as the
  content matures. Prefer the ignore file to `skip_list`, because ignored
  findings stay visible.
- Every `# noqa` carries a short comment saying why.
- Pin ansible-lint like any other tool, and the collections it resolves too:
  a new release adds rules and changes defaults.
- In CI, install the declared collections first and lint `offline: true`, so
  the run neither reaches Galaxy nor lints against collections the project
  never declared.
- Keep a project `.yamllint` compatible with ansible-lint's requirements
  (General pitfalls), or leave it out and take ansible-lint's yamllint
  defaults.

## General pitfalls
- **A key a release no longer knows stops everything.** An old configuration
  file that still carries a removed key exits 3 before linting a single file
  (Install, setup and configuration). Read the schema error, not the absence
  of findings.
- **An unresolved module hides the rest of the file.** A module from a
  collection that is not installed is reported as
  `syntax-check[unknown-module]` (observed in practice; an older run reported
  the same cause as `load-failure`), and that file's other findings are not
  reported. Install the collections before judging a run. ansible-lint
  installs what `requirements.yml` (and the other recognised requirement
  files) lists when a listed collection is missing and the run is not
  offline, so declare every collection there.
- **`args[module]` does not see `module_defaults`.** The rule validates each
  task's arguments against the module's argument spec, task by task. Required
  arguments supplied by a play-level `module_defaults` group (a connection's
  host and credentials, typically) are reported as "missing required
  arguments" on every task (reproduced). `ansible-playbook --syntax-check`,
  which ansible-lint also runs, evaluates the tasks with the defaults in
  scope, so it is the authority there: skip `args[module]` for such content or
  mark the tasks with `# noqa: args[module]`, with a comment. Upstream
  documents other `args` false positives around Jinja-templated arguments.
- **`var-naming[no-role-prefix]` covers more than `vars:`.** Inside a role,
  variables created by `set_fact` and by `register` must carry the role's
  prefix too (`<role>_`, with leading underscores accepted), or the rule
  fires (reproduced). Variables passed to `include_role` or `import_role`
  through `vars` should carry the included role's prefix; other task-level
  `vars` are task-scoped and exempt. A shared, cross-role variable contract
  conflicts with the rule by design, so either skip the sub-rule with a
  written reason or rename. A rename driven by this rule must sweep templates
  as well as YAML (`library-corpus/pypi/ansible-core.md`, the template
  pitfall).
- **A custom yamllint file can switch off `--fix`.** ansible-lint requires
  some yamllint settings so its reformatter and the YAML loaders agree
  (`comments.min-spaces-from-content: 1`, `comments-indentation: false`,
  `braces.max-spaces-inside: 1`, `octal-values.forbid-implicit-octal` and
  `forbid-explicit-octal: true`). A `.yamllint` that differs gets a warning
  and fix mode becomes unavailable (reproduced).
- **A custom `warn_list` drops the defaults** (Install, setup and
  configuration), so experimental rules can start failing the build.
- **`-f json` is ambiguous.** The usage page says `-f json`, which used to
  produce Code Climate JSON, was switched to mean SARIF; the CLI's own help
  still calls `json` "an alias for codeclimate", and a recent release run with
  `-f json` emitted Code Climate issues, not SARIF (reproduced). Name
  `-f codeclimate` or `-f sarif` explicitly, and upstream recommends SARIF,
  the more complete format.
- **pre-commit cannot see the community bundle's collections.** The hook runs
  in its own virtual environment, so collections that come with the `ansible`
  package are missing there (collections under `~/.ansible` are found). Add
  `ansible` to the hook's `additional_dependencies`, or install the
  collections where the hook looks. Upstream supports only the latest
  ansible-core as a pre-commit hook.

## Testing
- Lint is a gate, not a test of behaviour: a clean run says the content
  loads and follows the rules, never that it does what it should. Check mode
  and a scoped real run remain the behavioural tests
  (`library-corpus/pypi/ansible-core.md`, Testing).
- In CI, use `--strict` when warnings must fail, a machine format (`-f pep8`
  or SARIF via `--sarif-file`), and the exit code, not the text, as the
  verdict. The GitHub Action annotates findings when it detects GitHub's
  environment variables.
- `ansible-lint -t <rule>` reruns one rule while fixing its findings.

## Security defaults
- **Linting untrusted content runs code.** ansible-lint honours the same vault
  sources as `ansible-playbook` (`ANSIBLE_VAULT_PASSWORD_FILE`,
  `vault_password_file` in `ansible.cfg`, `vault_identity_list`), and Ansible
  reads `ansible.cfg` from the working directory, where a
  `vault_password_file` can name an executable. Lint a fork's pull request
  only in an isolated environment, or point `ANSIBLE_CONFIG` and the vault
  variables at configuration you control. Interactive vault prompts are not
  supported.
- Without vault access, lint with dummy fallbacks
  (`{{ var | default('dummy') }}`) or exclude the vault files; a role should
  pass the syntax check with no variables supplied.
- Not offline, a run installs collections and roles from `requirements.yml`
  and refreshes schemas over the network. `offline: true` keeps a CI run off
  the network.
- `no-log-password` (opt-in) flags tasks that may print a password; it is not
  in any profile by default.

## Operational behaviour
- Caches live under the runtime cache directory: typically `.ansible/` in the
  project when not offline, and `~/.ansible` (or `ANSIBLE_HOME`) when
  `offline: true`. Nothing cleans them automatically. Add project-local
  `.ansible/` and `.cache/` to `.gitignore`.
- Mocked modules and roles are written under
  `{cache_dir}/ansible-lint-mocks/` and used only when the real plugin is
  missing. Upstream notes that older releases wrote mocks into
  `{cache_dir}/collections/`, which could overwrite real modules under
  `~/.ansible`; a module there that starts with the lint mock marker is a
  clobbered one, and `ansible-galaxy collection install <name> --force`
  restores it.
- One run executes `ansible-playbook --syntax-check` per playbook and per
  role, so its time grows with the number of entry points; `exclude_paths`
  narrows the scope.

## Interop
- **ansible-core** (`library-corpus/pypi/ansible-core.md`): its syntax check
  is the `syntax-check` rule, its collections are what `args` validates
  against, and its configuration and vault sources are read the same way.
- **yamllint**: the `yaml` rule runs yamllint with ansible-lint's defaults;
  `yaml[<rule>]` ids skip or warn on single yamllint rules.
- **pre-commit**: upstream publishes a hook; see the pitfall above.
- **Molecule** and the other ansible-dev-tools members are separate tools,
  not covered here.

## Major lines
ansible-lint's numbering moved from the 6 line straight to 24.x; releases
since are numbered 24.x, 25.x, 26.x and on (the PyPI release list).

### 6.x line
- The `--progressive` mode was removed in 6.16.0; the ignore file replaces it
  for gradual adoption.

### 24.x and later
- From 25.7.0, running from a subdirectory of the project is not supported
  (Idioms).
- The configuration file is schema-validated, so a key removed in a release
  fails the run (General pitfalls).

## Upstream docs
- Docs: https://docs.ansible.com/projects/lint/
- Configuration: https://docs.ansible.com/projects/lint/configuring/
- Usage (CLI, profiles, noqa, vaults, caching):
  https://docs.ansible.com/projects/lint/usage/
- Installing: https://docs.ansible.com/projects/lint/installing/
- Profiles: https://docs.ansible.com/projects/lint/profiles/
- Rules: https://docs.ansible.com/projects/lint/rules/ (`args`,
  `var-naming`, `yaml` pages)
- Repo and releases: https://github.com/ansible/ansible-lint
