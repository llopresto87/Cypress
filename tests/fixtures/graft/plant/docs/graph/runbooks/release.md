# Release

How a release of acme-billing is cut and shipped.

## Steps

1. `git tag v$(cat VERSION)` — tag the release
2. `make dist` — build the artifact
3. `make deploy ENV=prod` — deploy it
