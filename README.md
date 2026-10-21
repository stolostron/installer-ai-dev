# installer-ai-dev

Rehor runner instance for the Installer squad (RHACM / MCE). Built on
[OpenShift-Fleet/rehor](https://github.com/OpenShift-Fleet/rehor) as a pinned
git submodule; this repo contains only instance configuration, the build hook,
and the deployment template.

Bot label: `ai-installer`

## Layout

```
setup.sh                       # build hook: envtest assets, instance id
instance/installer/agent/
  instance.yaml                # workflow + env presets + runtime/provider
  project-repos.json           # squad repos and their bot forks
  mcp.json                     # Jira MCP (via shared proxy)
  personas/{operator,backend,config,tooling}/prompt.md
deploy/template.yaml           # OpenShell SandboxTemplate + WarmPool + KEDA
```

`BOT_CONFIG_REPO` points at this repo with `BOT_CONFIG_PATH=instance/installer`,
so the resolved config lives at `instance/installer/agent/instance.yaml`.

## Build

```bash
git submodule update --init --recursive
docker build -f dev-bot/Dockerfile.runner -t installer-ai-dev:local .
```

Konflux builds the same way: `dockerfile: dev-bot/Dockerfile.runner`,
`path-context: .`.

## Updating dev-bot

```bash
cd dev-bot && git pull origin master && cd ..
git add dev-bot
git commit -s -m "chore: bump dev-bot submodule"
```

## Tickets

Tickets are picked up when they carry the `ai-installer` label plus a
`repo:<name>` label matching a key in `project-repos.json`, for example:

```
ai-installer repo:backplane-operator
```

## Not yet done

- [ ] Fork each repo under the bot GitHub account (`platex-rehor-bot`)
- [ ] Konflux onboarding + ReleasePlan + public Quay repo
- [ ] app-interface app/namespace, Vault secret, and resource template
- [ ] Deploy shared or per-instance proxy + memory server
- [ ] Replace placeholder `BOT_IMAGE`, `GCP_PROJECT_ID`, and KEDA window in `deploy/template.yaml`
