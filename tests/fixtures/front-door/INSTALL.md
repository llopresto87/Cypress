# Installing CYPRESS

Run the installer from a clone of this repository, naming a harness and a project path:

```sh
bash install.sh claude-code /path/to/your/project
```

Each harness writes its own directory; the [host capability matrix](documentation/host-capability-matrix.md) lists them. A differing file already in place is kept beside itself as a timestamped copy ([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)).

After the install, start a new session so the harness lists the new workers; `delegation.harness-registration` in `docs/graph/method/delegation.md` explains why.
