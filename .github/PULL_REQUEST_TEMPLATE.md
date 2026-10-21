## What changed

<!-- Config, persona, deploy template, setup.sh, or submodule bump. One or two sentences. -->

## Type

- [ ] Instance config (`instance.yaml`, `project-repos.json`, `mcp.json`)
- [ ] Persona prompt (`instance/installer/agent/personas/`)
- [ ] Build hook (`setup.sh`)
- [ ] Deploy template (`deploy/template.yaml`)
- [ ] dev-bot submodule bump
- [ ] Repo plumbing (CI, docs, templates)

## Validation

- [ ] `uv run dev-bot --label ai-installer --dry-run` loads the config and merges cleanly
- [ ] Every repo touched in `project-repos.json` has a fork under the bot account
- [ ] Persona changes name the verification command the bot will run (`make test`, `make verify`, etc.)
- [ ] Deploy template changes cover NetworkPolicy egress, DNS on port 5353, and the `devbot-proxy` label
- [ ] `docker build -f dev-bot/Dockerfile.runner -t installer-ai-dev:local .` succeeds (build-hook changes)
- [ ] `setup.sh` changes verified in a built image, not on the host

## Risk

<!-- What breaks if this is wrong: bot picks wrong repo, cannot run tests, cannot reach proxy, or burns cycles. -->

- Blast radius:
- Rollback: revert this commit / repin the submodule

## Related

- Jira:
- app-interface ref / image digest (if deployed):
