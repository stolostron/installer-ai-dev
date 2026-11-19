# Operator persona — Installer squad (ACM/MCE)

Applies to `multiclusterhub-operator` and `backplane-operator`. Both are Go
Kubernetes operators built with controller-runtime and kubebuilder.

## Verify before opening a PR

Run in this order; a red step means fix it, do not open the PR.

```
make manifests generate fmt vet
make test
```

`make test` runs envtest. The envtest binaries (etcd, kube-apiserver, kubectl)
are pre-populated in the image, and each Makefile sets `KUBEBUILDER_ASSETS`
itself — do not export it yourself. If `make test` fails with a missing
assets error, report it on the Jira ticket instead of downloading binaries.

## Repo conventions

- Never hand-edit generated files: CRDs under `config/crd/bases/`, RBAC under
  `config/rbac/`, and `zz_generated.*.go`. Change the marker or type and re-run
  `make manifests generate`.
- API changes require the corresponding deepcopy regeneration plus a CRD diff
  in the PR. Call out defaulted or newly required fields in the ticket comment.
- New behaviour gets a unit or envtest case in the same PR. No test, no PR.
- Preserve existing log formats and condition/reason strings; other components
  and QE assert on them.
- Version or image bumps: change only what the ticket names. Do not opportunistically
  bump unrelated dependencies.

## Out of scope

- Do not edit `go.mod` Go directive or toolchain version unless the ticket is
  explicitly a Go upgrade.
- Do not push to release branches. Branch from `upstream` default branch only.
- Do not create tags, releases, or bundles.
