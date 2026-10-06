# community.docker — galaxy

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`community.docker` is the Ansible collection for Docker: modules for
containers (`docker_container`), images (`docker_image`), networks, volumes,
registry login (`docker_login`), host information, exec and copy into
containers, Swarm, and Docker Compose v2 (`docker_compose_v2` and its
`_pull`, `_exec`, `_run` companions), plus a `docker` connection plugin that
runs tasks inside containers, a `docker_api` connection plugin, and inventory
plugins. Galaxy namespace `community`, name `docker`; maintained by the Ansible
Docker Working Group; licence GPL-3.0-or-later. The engine and Compose
themselves are on `library-corpus/container/docker.md` and
`library-corpus/container/docker-compose.md`.

## Install, setup and configuration
- The collection ships inside the `ansible` community package. With ansible-core
  alone, `ansible-galaxy collection install community.docker`, or list it with
  a pinned `version:` range in `collections/requirements.yml`.
- Requirements are per module and apply to the host that executes the module:
  - the container, image, network and volume modules talk to the Docker daemon
    API and need the Python `requests` library (plus `paramiko` for SSH
    transport without the ssh client, `pyOpenSSL` for some TLS setups,
    `pywin32` for Windows named pipes). From the 3.x line the collection
    vendors the Docker SDK code it needs, so they no longer need the Docker SDK
    for Python (`docker`);
  - `docker_compose_v2` does not use the API at all: it runs the Docker CLI
    with the Compose v2 plugin, which must be installed on the executing host
    (and PyYAML when an inline `definition` is used).
- Daemon connection, per task (`docker_host`, the TLS options) or from the
  environment: `DOCKER_HOST`, `DOCKER_TLS`, `DOCKER_TLS_VERIFY`,
  `DOCKER_CERT_PATH`, `DOCKER_API_VERSION`, `DOCKER_TIMEOUT`,
  `DOCKER_TLS_HOSTNAME`.

## Core API / usage shape
- `docker_container` manages a container's life cycle: `state: present`
  creates or updates, `started`, `stopped`, and `absent` (with `force_kill`,
  `keep_volumes`). `restart_policy` is `no`, `on-failure`, `always` or
  `unless-stopped`. `comparisons` decides, per option, whether a difference
  forces a recreate (`strict`, `ignore`, `allow_more_present`).
- `docker_compose_v2` maps states onto Compose commands: `present` is
  `docker compose up`, `stopped` is `stop`, `restarted` is `restart`, `absent`
  is `down`. Choose the project with `project_src`, `files` or an inline
  `definition`; control `pull` (`always`, `missing`, `never`), `recreate`
  (`auto` by default, `always`, `never`), `build`, `remove_images`, and `wait`
  with `wait_timeout`.
  ```yaml
  - community.docker.docker_compose_v2:
      project_src: /srv/app
      state: present
      pull: missing
      wait: true
      wait_timeout: 120
    register: compose
  ```
- `docker_image` manages images; `docker_login` logs in to a registry.

## Idioms & best practices
- Prefer `docker_compose_v2` over `ansible.builtin.command: docker compose up
  -d` with a `changed_when` that matches its output. The module derives
  `changed` from the events the Compose CLI emits (`ignore_build_events`
  filters build noise), so no output text is parsed in the playbook. Observed
  in practice: the text-matching form broke when Compose reworded its output.
- On each `docker_container` task, state every option you care about. When the
  module recreates a container it uses only the options given (plus the
  image); anything set by hand earlier is lost.
- Keep data in named volumes, so a recreate does not lose it.
- Observed in practice: after adding the SSH user to the `docker` group, run
  `meta: reset_connection` so the persistent connection picks up the new group
  (the connection semantics are on `library-corpus/pypi/ansible-core.md`).

## General pitfalls
- Most configuration changes to a container require destroying and recreating
  it; the docs warn of unexpected data loss and downtime. Use `comparisons` to
  stop cosmetic differences from forcing a recreate.
- The Compose CLI plugin has no stable, machine-friendly output. The module
  adapts to plugin versions and is tested against a range of them, and a new
  Compose release can break it. Pin the Compose plugin with the collection, and
  upgrade them together.
- The old `docker_compose` module (Compose v1, Python-based) is removed on the
  4.x line. Never install the obsolete `docker-py` package; the Docker SDK for
  Python is `docker`, and most modules no longer need even that.
- The Python requirements apply where the module runs. Under
  `delegate_to: localhost` that is the control node's interpreter, which may
  not be the one running `ansible-playbook`.

## Testing
- `docker_container` supports check mode: `--check --diff` shows the
  configuration differences and the action it would take. `docker_compose_v2`
  states its check-mode support in its attribute table.
- Run tests against a throwaway daemon, never a production host.

## Security defaults
- Access to the Docker daemon API is root-equivalent on the host. For a remote
  daemon use TLS (`tls`, `validate_certs`, client certificates).
- Give `docker_login` its credentials from vault and run it with
  `no_log: true`.

## Operational behaviour
- `docker_compose_v2` needs the Compose plugin on the target host, not on the
  control node (unless the task runs locally). `pull` controls when images are
  fetched; `wait` / `wait_timeout` block until the services are running or
  healthy, which turns a slow start into a task failure you can see.

## Interop
- The `docker` connection plugin runs Ansible tasks inside running containers;
  the `docker_api` connection does the same through the API.
- Works with ansible-core's `delegate_to` and `meta: reset_connection`
  (`library-corpus/pypi/ansible-core.md`).

## Major lines

### 2.x line
- `container_default_behavior` defaults to `no_defaults`.

### 3.x line
- `docker_container` is rewritten, and the collection vendors the Docker SDK
  code it needs, so most modules need only `requests`.

### 4.x line
- The Compose v1 module `docker_compose` is removed; use `docker_compose_v2`.
- `image_name_mismatch` defaults to `recreate` (it was `ignore`): a container
  whose image matches by id but not by name is recreated.

### 5.x line
- Python 2.7 and old ansible-core lines are dropped; module utils and doc
  fragments become private to the collection.

## Upstream docs
- Docs: https://docs.ansible.com/ansible/latest/collections/community/docker/
- Repo: https://github.com/ansible-collections/community.docker
