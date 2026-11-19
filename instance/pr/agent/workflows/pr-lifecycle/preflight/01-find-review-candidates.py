#!/usr/bin/env python3
"""Preflight: discover tickets this instance owns (label ai-review).

Tasks are instance-scoped, so this instance cannot see the implement
instance's task rows. Discovery happens through the Jira label, then the
agent creates its own task record and `02-gh-pr-status.py` monitors it for
free on subsequent cycles.
"""

import sys

from common import build_repo_lookup, load_project_repos, output_result
from jira_sprint_preflight import _format_candidates, _jira_search

MAX_CANDIDATES = 10


def main():
    repo_lookup = build_repo_lookup(load_project_repos())
    issues = _jira_search(
        "labels = ai-review AND statusCategory != Done "
        "ORDER BY updated DESC",
        limit=MAX_CANDIDATES,
    )
    if not issues:
        output_result("skip", "No ai-review tickets.")
        return

    candidates = _format_candidates(issues, repo_lookup)
    lines = [f"{len(candidates)} ai-review candidate(s):", ""]
    for candidate in candidates:
        lines.append(f"{candidate['key']} [{candidate['status']}] priority={candidate['priority']}")
        lines.append(f"  title: {candidate['summary']}")
        lines.append(f"  repos: {','.join(candidate['repos']) or 'none'}")
        lines.append("")
    lines.append("Handle exactly one PR issue per cycle, in this order:")
    lines.append("failing CI > merge conflict > unaddressed review feedback > Jira comment > QE handoff due > merged.")
    output_result("start", "\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
