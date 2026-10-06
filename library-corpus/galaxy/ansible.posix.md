# ansible.posix — galaxy

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`ansible.posix` is the Ansible-maintained collection of modules and plugins for
POSIX and POSIX-like systems. Modules: `acl`, `at`, `authorized_key`,
`firewalld`, `firewalld_info`, `mount`, `patch`, `rhel_facts`,
`rhel_rpm_ostree`, `rpm_ostree_upgrade`, `seboolean`, `selinux`,
`synchronize`, `sysctl`. Callback plugins: `profile_tasks`, `profile_roles`,
`timer`, `json`, `jsonl`, `debug`, `cgroup_perf_recap`. Shell plugins: `csh`,
`fish`. Galaxy namespace `ansible`, name `posix`; licence GPL-3.0-or-later. These
modules left the engine at the collection split, so they are not in
ansible-core (`library-corpus/pypi/ansible-core.md`).

## Install, setup and configuration
- The collection ships in the `ansible` community package. With ansible-core
  alone, `ansible-galaxy collection install ansible.posix`, or a pinned
  `version:` range in `collections/requirements.yml`. It depends on no other
  collection and needs the Python version ansible-core needs.
- Module-specific requirements on the executing host: `synchronize` needs
  `rsync` on both ends; `firewalld` needs `firewalld` and its Python bindings
  (`python-firewall`).
- Configuration is per task; the collection has no settings of its own.

## Core API / usage shape
- `authorized_key`: `user`, `key` (one or more keys in a string, a URL such as
  a `.keys` URL, or a `file://` path searched on the remote host), `state`,
  `exclusive`, `manage_dir`, `path`, `key_options`, `follow`.
  ```yaml
  - ansible.posix.authorized_key:
      user: deploy
      key: "{{ deploy_public_keys | join('\n') }}"
      exclusive: true
  ```
- `synchronize` wraps rsync: `src`, `dest`, `mode` (`push` or `pull`),
  `archive` (default true: recursive, links, perms, times, owner, group,
  devices), `delete` (needs `recursive`), `checksum`. `--delay-updates` is on
  by default, so a failed run does not leave a half-updated destination.
- `sysctl`: `name`, `value`, `state` (default `present`), `sysctl_file`
  (default `/etc/sysctl.conf`), `reload` (default true: runs `sysctl -p` when
  the file changed), `sysctl_set` (default false), `ignoreerrors` (skip unknown
  keys).
- `firewalld`: ports, services, rich rules, interfaces, masquerade and zones.
  `permanent` writes the persistent configuration; `immediate` applies to the
  running one, and defaults to true when `permanent` is false.
- `mount`: active and configured mount points (`fstab` handling, `backup`,
  `boot`, `opts`; states for mounted, unmounted and absent, among others).
- `selinux` changes policy and mode; `seboolean` sets booleans; `acl` sets and
  reads file ACLs.

## Idioms & best practices
- Call every module by its FQCN (`ansible.posix.authorized_key`), so a
  playbook still resolves when modules move between collections.
- For a fixed set of keys, join them into one `key:` value and use
  `exclusive: true` once; never loop an exclusive task.
- When a kernel parameter must take effect now and survive a reboot, set
  `sysctl_set: true` as well as writing the file.
- Use `synchronize` where `ansible.builtin.copy` is too slow for many files;
  use `copy` and `template` for single files.

## General pitfalls
- `authorized_key` with `exclusive: true` is not loop-aware: each iteration
  removes the keys the earlier iterations added, leaving only the last.
- `authorized_key` `manage_dir` (default on) creates the key directory and
  resets the owner and permissions of an existing one. With `path` pointing at
  an alternate location, set `manage_dir: false` so it does not change
  permissions you did not mean to change.
- `sysctl` with its defaults edits the file and runs `sysctl -p` when the file
  changed. It sets the running kernel value with `-w` and verifies it only when
  `sysctl_set: true`.
- `synchronize` runs rsync from the "local host", which is the host the task
  originates on. `delegate_to` moves the local host to the delegate, and with
  it the side that `src` and `dest` refer to. `src` is read with the task
  user's permissions on the local host; `dest` is written as `remote_user` or
  the `become_user`. Hard links survive only when the relative subtrees match.
- `acl` with `default: true` applies to directories only and fails on a file.
- `firewalld` changes with `immediate` but not `permanent` vanish on reload or
  reboot; with `permanent` but not `immediate` they wait for the next reload.

## Testing
- Upstream documents no testing guidance beyond each module's attribute table,
  which states its check-mode and diff support. Read that table before relying
  on `--check` for a module.
- Read state back after a change (`firewalld_info`, the mounted file systems,
  the live `sysctl` value) rather than trusting the task status.

## Security defaults
- `authorized_key` decides who can log in: a mistaken `exclusive: true`, a wrong
  `path`, or `manage_dir` acting on the wrong directory can lock out the
  connecting user.
- `synchronize` with `delete: true` removes every destination file that is not
  in the source.
- `selinux` and `firewalld` changes can cut access if applied before the
  configuration is right.

## Operational behaviour
- `sysctl` persists to `sysctl_file` and reloads it; the live value changes
  only through the reload or `sysctl_set`.
- `mount` edits `fstab` (optionally with a backup) and changes the mount state,
  so the result persists across reboots.
- `synchronize` needs rsync on both ends, and its `--delay-updates` default
  keeps a failed transfer from leaving a half-written destination.

## Interop
- Complements `ansible.builtin` (`copy`, `file`, `template`) for files and
  ansible-core's `delegate_to` for push and pull patterns.
- Windows hosts use `community.windows.win_robocopy` instead of
  `synchronize`.

## Major lines

### 1.x line
- `firewalld`'s `forward`, `masquerade` and `icmp_block_inversion` take
  strings; the `skippy` strategy plugin exists.

### 2.x line
- Those three `firewalld` options become booleans (a breaking change for
  playbooks that pass strings), and `skippy` is removed. `authorized_key`
  accepts an absolute file path as the key source, and the timing callbacks
  gain recap output.

## Upstream docs
- Docs: https://docs.ansible.com/ansible/latest/collections/ansible/posix/
- Repo: https://github.com/ansible-collections/ansible.posix
