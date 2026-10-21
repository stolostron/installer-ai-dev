# Config persona — Installer squad (ACM/MCE)

Applies to `acm-operator-bundle`, `mce-operator-bundle`, and
`acm-mce-operator-catalogs`. These repos carry manifests, bundles, and catalogs
rather than application code.

## Verify before opening a PR

There is no unit-test suite. Validation is render-and-diff:

```
kustomize build <dir> > /tmp/after.yaml        # or: helm template <chart>
yamllint -c .yamllint . 2>/dev/null || true
```

For bundle and catalog repos, run the repo's documented generation/validation
target if one exists (`make bundle`, `make catalog`, `opm validate`). If no
target exists, say so on the ticket — do not invent one.

Every PR must include a rendered diff in the description for the files that
change behaviour (CSVs, subscriptions, catalogsources, catalogs).

## Repo conventions

- Version and image-tag bumps: change exactly the fields the ticket names, and
  quote the source of the new tag (release note, Jira, or upstream commit).
  Never guess a tag.
- Keep ACM and MCE changes symmetric when the ticket covers both, unless the
  ticket says otherwise.
- Preserve ordering and indentation of generated CSV fields; reordering causes
  unreviewable diffs.

## Out of scope

- Publishing bundles to a registry, triggering releases, or editing pipelines.
- Changing catalog channels other than the one the ticket names.
