#!/usr/bin/env python3
"""Preflight: gather ai-triage candidates and score their readiness.

Read-only. Emits `skip` when there is nothing to triage, otherwise `start`
with the candidate list plus a deterministic completeness verdict per
candidate. No model call happens on a `skip`.
"""

import re
import sys

from common import build_repo_lookup, load_project_repos, output_result
from jira_sprint_preflight import _get_candidates

MIN_DESCRIPTION_CHARS = 200
MIN_SUMMARY_CHARS = 15
ACCEPTANCE_PATTERN = re.compile(
    r"acceptance\s+criteria|definition\s+of\s+done|expected\s+behaviou?r|"
    r"steps\s+to\s+reproduce|how\s+to\s+verify|test\s+plan",
    re.IGNORECASE,
)


def triage_candidate(candidate):
    """Return a list of gaps. Empty list means ready for a plan."""
    gaps = []
    description = (candidate.get("description") or "").strip()
    summary = (candidate.get("summary") or "").strip()

    if len(summary) < MIN_SUMMARY_CHARS:
        gaps.append(f"summary too short ({len(summary)} chars)")
    if len(description) < MIN_DESCRIPTION_CHARS:
        gaps.append(f"description too short ({len(description)} chars)")
    if not ACCEPTANCE_PATTERN.search(description):
        gaps.append("no acceptance criteria / expected behaviour / verification section")
    if not candidate.get("repos"):
        gaps.append("no repo:<name> label matching project-repos.json")
    if candidate.get("type", "").lower() not in ("bug", "task", "story", "sub-task", "subtask", "epic"):
        gaps.append(f"unexpected issue type: {candidate.get('type')}")

    return gaps


def main():
    repo_lookup = build_repo_lookup(load_project_repos())
    candidates = _get_candidates(repo_lookup)
    if not candidates:
        output_result("skip", "No ai-triage candidates.")
        return

    lines = [f"{len(candidates)} ai-triage candidate(s):", ""]
    ready = 0
    for candidate in candidates:
        gaps = triage_candidate(candidate)
        verdict = "READY" if not gaps else "INCOMPLETE"
        if not gaps:
            ready += 1
        lines.append(f"{candidate['key']} [{verdict}] priority={candidate['priority']} type={candidate['type']}")
        lines.append(f"  title: {candidate['summary']}")
        lines.append(f"  status: {candidate['status']}")
        lines.append(f"  repos: {','.join(candidate['repos']) or 'none'}")
        lines.append(f"  labels: {','.join(candidate['labels'])}")
        if gaps:
            lines.append(f"  gaps: {'; '.join(gaps)}")
        lines.append("")

    lines.append(f"Ready for planning: {ready}/{len(candidates)}")
    lines.append("Triage exactly one candidate per cycle, highest priority first.")
    output_result("start", "\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
