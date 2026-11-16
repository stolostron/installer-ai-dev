# Agent Pipeline — staged Rehor instances

Three Rehor instances share the installer squad's repos, each owning one stage of
the ticket lifecycle. Jira labels are the handoff bus; memory-server tasks stay
instance-scoped, so no stage can act on another stage's work queue.

```
human files ticket
      │  adds ai-triage
      ▼
[triage]   read-only reconnaissance, posts plan
      │  ai-triage → ai-planned
      ▼
human reviews plan
      │  adds ai-installer
      ▼
[impl]     claim, branch, implement, test, open PR
      │  ai-installer → ai-review
      ▼
[pr]       CI, conflicts, review feedback, QE handoff
      │  ai-review → ai-qe
      ▼
human QE   executes the handoff plan
      │  PR merges
      ▼
[pr]       wrap-up: Release Pending, learnings, branch cleanup
```

## Label contract

| Label | Meaning | Owner | Set by |
|---|---|---|---|
| `ai-triage` | Needs triage | triage | human |
| `ai-planned` | Plan posted, awaiting approval | — | triage |
| `ai-needs-info` | Sent back to reporter | — | triage |
| `ai-installer` | Approved for implementation | impl | **human** |
| `ai-review` | PR open | pr | impl |
| `ai-qe` | QE handoff posted | pr | pr |

Rules that keep the state machine safe:

1. **Exactly one stage label at a time.** Each stage removes its predecessor's label in the same Jira update that adds its own. Two labels = ambiguous ownership.
2. **`repo:<name>` label is required** at triage time and must resolve in that instance's `project-repos.json`. Instances keep their own copy of the file.
3. **Assignee stays empty until impl claims the ticket.** Every preflight JQL keeps `assignee is EMPTY` as a second guard against double claiming.
4. **`ai-installer` is only ever added by a human.** It is the approval gate for the plan, and the only label that authorises code changes.
5. **Tasks are per-instance.** `GET /api/tasks?instance_id=…` filters to `instance_id = $1 OR instance_id IS NULL`, so the triage instance cannot see impl's rows. Never rely on a shared task record for handoff — use the label plus a Jira comment.
6. **RAG memory is shared.** `memory_store` learnings from any stage are visible to all stages via `memory_search`. Use this for cross-stage context (repo conventions, recurring CI failures), not for task state.

## Instances

| Instance dir | `BOT_LABEL` | Workflow | Purpose |
|---|---|---|---|
| `instance/triage` | `ai-triage` | `./workflows/ticket-triage` | Completeness gate + implementation plan. Read-only. |
| `instance/installer` | `ai-installer` | `jira-sprint` **→ `./workflows/jira-impl`** | Implement and open PR. |
| `instance/pr` | `ai-review` | `./workflows/pr-lifecycle` | PR maintenance, QE handoff, wrap-up. |

Each instance needs its own deployment of `deploy/template.yaml` with distinct
`BOT_LABEL`, `BOT_INSTANCE_ID`, and `BOT_CONFIG_PATH`. All three point at the
same proxy and memory server.

## Rollout

### Phase 1 — triage only (safe, no changes to the existing bot)

1. Deploy `instance/triage` as a second pod.
2. Humans add `ai-triage` when filing or grooming a ticket. It must also carry `repo:<name>`.
3. Triage either posts a plan (`ai-planned`) or reports gaps (`ai-needs-info`).
4. Approving a plan = adding `ai-installer`. The existing bot picks the ticket up exactly as it does today.

One-way benefit, zero risk to the current flow: incomplete tickets never reach
the implement stage, and every implementation starts from a written plan.

### Phase 2 — split PR maintenance out of impl

The built-in `jira-sprint` workflow runs Priority 1 (PR maintenance) and
Priority 2 (new tickets) in one instance. To hand PRs to the `pr` instance
without duplicate work, fork the workflow:

```bash
mkdir -p instance/installer/agent/workflows
cp -R dev-bot/presets/workflows/jira-sprint instance/installer/agent/workflows/jira-impl
```

Then edit `instance/installer/agent/workflows/jira-impl/`:

1. `CLAUDE.md` — delete the **Priority 1: Maintain Existing PRs** section. Keep
   Priority 0 items that apply before a PR exists (interrupted work,
   investigations) and Priority 2 (new work).
2. `CLAUDE.md` — after step 12 (`/post-pr`, transition to Code Review), replace
   the task tracking step with: add `ai-review`, remove `ai-installer`,
   `task_update(status="done", metadata={"last_step": "handed_off"})`, then stop.
3. `manifest.yaml` — remove `wrap-up` from `provides.skills`; the `pr` instance
   owns it.
4. `instance/installer/agent/instance.yaml` — set `workflow: ./workflows/jira-impl`.
5. Deploy `instance/pr` with `BOT_LABEL=ai-review`.

Validate before flipping: run both instances in dry-run style by labelling a
single low-risk ticket and watching one full cycle of each.

## Cost and capacity notes

- **Idle cost is near zero.** Preflight `skip` starts no agent session, so an
  idle triage or PR instance only costs one Jira search per poll.
- **Model per stage.** Both new instances set `model: claude-sonnet-4-6` in
  `instance.yaml`. Drop triage to `claude-haiku-4-5` only if plan quality holds
  up; the triage stage reads code, so start on Sonnet.
- **Capacity is per instance** (max 10 active tasks each). Triage tasks are
  written as `status="done"`, so they do not consume impl or PR capacity.
- **Memory server** is shared and sized for "a few API calls per cycle" per bot.
  Three instances is still well inside that envelope.

## Failure modes to watch

| Symptom | Cause | Fix |
|---|---|---|
| Ticket pulled by both impl and pr | Overlap during Phase 2 rollout | Finish the impl workflow fork before deploying `instance/pr` |
| Ticket ping-pongs between `ai-planned` and `ai-needs-info` | Triage threshold too strict for the team's writing style | Lower `MIN_DESCRIPTION_CHARS` / relax `ACCEPTANCE_PATTERN` in the preflight |
| PR instance rejects a handoff with no PR | Implement stage died after labelling | Preflight JQL catches it; the workflow comments and returns `ai-installer` |
| Duplicate PR comments | Both instances read the same thread | Confirms Phase 2 prerequisite was skipped |
| Triage comments on the same ticket repeatedly | Label swap failed (Jira write error) | Check the Jira MCP path, then `ai-triage` removal; preflight re-queues until the label is gone |

## Rollback

- Phase 1: delete the triage deployment. Remove `ai-triage` labels; nothing else changes.
- Phase 2: revert `instance/installer/agent/instance.yaml` to `workflow: jira-sprint`, delete the `pr` deployment, re-add `ai-installer` to any ticket sitting in `ai-review`.
