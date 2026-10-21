# Tooling persona — Installer squad (ACM/MCE)

Applies to `installer-dev-tools`, `stolostron-release-tools`, and `release`.
Build and release automation: shell, Python, Makefiles, and CI config rather
than shipped product code.

## Verify before opening a PR

Static checks first, then the repo's own documented target if one exists:

```
bash -n <changed-script>
shellcheck <changed-script>            # if the repo uses it
python3 -m py_compile <changed-file>   # for Python changes
make help                              # discover available targets
```

Run a target only if it works without cluster or registry credentials. If the
only validation needs credentials or a live cluster, say so on the ticket and
leave the PR in draft.

## Repo conventions

- `release` and `stolostron-release-tools` touch shipped artifacts. Change the
  minimum number of lines the ticket requires and never trigger a pipeline,
  release, tag, or image promotion.
- Scripts must stay POSIX/bash portable to the images they run in; do not
  assume tools that are not already used in the repo.
- Preserve exit-code behaviour and output format; other automation parses it.
- Add a dry-run flag rather than a destructive default. Any script that mutates
  state must be runnable with `--dry-run` or equivalent.

## Out of scope

- Publishing releases, bundles, or catalogs.
- Changing CI credentials, secrets, or webhook targets.
- Deleting or rewriting release history.
