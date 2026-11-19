# Backend persona — Installer squad (ACM/MCE)

Applies to `discovery`. Go service with controller-runtime, plus e2e tests that
need a live cluster.

## Verify before opening a PR

```
make manifests generate fmt vet
make test
```

Do not run `make deploy-and-test` or any e2e target — those need a cluster and
will hang or dirty the workspace. If a change is only provable by e2e, leave
the PR in draft, state the untested path on the Jira ticket, and let a human
run it.

## Repo conventions

- `make verify` runs test + deploy-and-test + manifests. Do not run it in the
  bot workspace for the reason above.
- Regenerate manifests/deepcopy after API changes; never hand-edit generated
  files.
- Keep handlers idempotent and requeue-safe. If you add a reconciliation branch,
  add the envtest case that drives it.
- Respect existing error wrapping and logging conventions.

## Out of scope

- Cluster-scoped side effects, installations, or upgrades on live clusters.
- Dependency sweeps unrelated to the ticket.
