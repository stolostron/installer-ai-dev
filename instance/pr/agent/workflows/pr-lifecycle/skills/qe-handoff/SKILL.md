---
name: qe-handoff
description: Post a QE-ready handoff for an open PR — what changed, how to verify, expected results, setup notes. Invoked once per ticket when the PR is green.
---

# QE Handoff

Args: `<JIRA-KEY>`.

Run when the PR is green, conflicts are resolved, and no review feedback is outstanding. Posts one Jira comment and reports back. Never posts code internals.

## Gather

- `jira_get_issue` — summary, type, labels, description, existing comments.
- Task record — `task_get(<KEY>)` → `metadata.prs` for the PR URL and repo.
- `gh pr view <n> --json title,body,files,headRefName` (or `gh pr diff <n> --stat`) — files touched, PR title, linked issue.
- Repo `CLAUDE.md` / `AGENTS.md` and `Makefile` — build, deploy, and test prerequisites.
- The ticket's acceptance criteria / expected behaviour, if present.

## Compose

Show the draft first if the caller asked for approval; otherwise post directly. Keep it tester-facing, high level. No SHAs, no file paths unless the tester needs them, no function names.

```
### QE Handoff

**Change:** one or two sentences on what the user or operator now sees differently.

**Affected components:** ACM / MCE / both, component names, upgrade or fresh install.

**Prerequisites:**

- cluster type and version
- images, catalogs, or bundles to install
- feature flags or CRDs to enable

**Verification steps:**

1. concrete step
2. concrete step

**Expected results:** what a passing run looks like, including log or status lines to check.

**Negative cases:** what must NOT happen.

**Known limitations:** scope boundaries, follow-up tickets.
```

## Post

1. `jira_add_comment(issue_key=KEY, body=<composed>)`.
2. If `BOT_QA_CONTACT_FIELD` is set (e.g. `customfield_10001`, single user picker), set it via `jira_update_issue` with the QA contact value. If unset, skip silently — do not guess a field id.
3. Do not transition the ticket yourself unless `BOT_QE_TRANSITION` names the target status; otherwise leave the status to the reviewer.
4. `task_update(external_key=KEY, metadata={"last_step": "qe_handoff_posted"})`.
5. Report the comment URL back to the caller.

## Rules

- One handoff comment per ticket. If one already exists, edit it in place instead of adding a duplicate.
- No source code, no diffs, no internal identifiers.
- If prerequisites are unknown, say so explicitly rather than omitting the section.
