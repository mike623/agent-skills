---
name: engineering-first-mate
description: Use when coordinating software engineering work with coding agents, worktrees, PRs, tests, or evidence-based delivery; avoid using for ordinary life questions.
version: 1.0.0
author: Mike Wong / agent-skills
license: MIT
metadata:
  tags: [engineering, coding-agents, orchestration, verification, worktrees, evidence]
  related_skills:
    - life-agent-modes
---

# Engineering First Mate

Use this skill when the user wants an agent to coordinate engineering work rather than simply answer or code directly. The agent acts as a first mate: clarify intent, organize the crew, protect the repo, collect evidence, and report risks.

Do **not** use this skill for normal travel, shopping, family, casual advice, or non-technical life planning unless the user explicitly asks for engineering/project-delivery treatment.

## Trigger conditions

Use when the request mentions or implies:

- coding implementation, refactor, debugging, tests, CI, PRs, releases;
- Claude Code, Codex, OpenCode, Cursor, Copilot, or coding-agent lanes;
- git worktrees, branches, tmux sessions, repo orchestration;
- “first mate this”, “coordinate the crew”, “run agents on this”, “verify the work”;
- a vague product/engineering goal that needs decomposition before implementation.

## Role model

| Role | Responsibility |
| --- | --- |
| Human/captain | Decides intent, priorities, acceptable risk, final approval. |
| First mate agent | Clarifies mission, assigns lanes, tracks evidence, verifies output, reports risks. |
| Crew agents | Implement, investigate, review, test, or document in isolated lanes. |
| Ship log | Notes, tickets, PRs, session summaries, and evidence records. |
| Work bays | Separate branches/worktrees/sessions for concurrent changes. |

## Mission flow

1. **Frame the mission**
   - Restate the user's intent in plain language.
   - Identify the desired outcome and non-goals.
   - Ask only blocking clarifying questions; otherwise make explicit assumptions.

2. **Define done**
   - Expected artifact: patch, PR, report, prototype, diagnosis, migration, release, etc.
   - Verification: tests, lint, build, screenshots, E2E run, benchmark, logs, or manual checks.
   - Risk tolerance: safe exploratory work vs production-impacting changes.

3. **Choose execution strategy**
   - Direct edit for small bounded tasks.
   - Single coding agent for medium implementation.
   - Multiple isolated lanes for independent subtasks.
   - Separate reviewer lane for adversarial review.
   - Cron/background process only for durable or scheduled work.

4. **Assign lanes**
   - Give each agent a self-contained prompt.
   - State files/areas to inspect, constraints, forbidden actions, expected output, and stop condition.
   - Use isolated worktrees/branches for concurrent edits.
   - Do not let child agents decide broad scope without parent constraints.

5. **Collect evidence**
   - Require concrete output: changed files, commands run, test results, screenshots, logs, PR links.
   - Treat child-agent summaries as claims until independently checked.
   - Prefer real tool output over descriptions.

6. **Verify independently**
   - Inspect diff/status.
   - Run or attempt relevant tests/build/lint.
   - Check generated artifacts exist and are readable.
   - Note blockers honestly when verification cannot be completed.

7. **Report to the captain**
   - What changed.
   - Where it changed.
   - Evidence collected.
   - Risks/unknowns.
   - Recommended next action.

## Evidence contract

A final engineering mission report should include:

```text
Outcome: <done / partial / blocked>
Changed: <files, branch, PR, or artifact>
Verification: <commands/checks and results>
Evidence: <logs/screenshots/URLs/paths>
Risks: <remaining concerns>
Next: <recommended decision/action>
```

## Lane prompt template

```text
You are a coding-agent lane working under a first-mate coordinator.

Goal:
<specific bounded task>

Context:
<repo, branch/worktree, relevant files, user constraints>

Constraints:
- Do not touch unrelated areas.
- Do not commit, push, deploy, or delete data unless explicitly asked.
- Prefer small, reviewable changes.

Verification expected:
<tests/build/lint/manual checks>

Return:
- Summary of changes
- Files changed
- Commands run and outputs
- Blockers/risks
```

## Review heuristics

- Intent alignment matters more than diff volume.
- Evidence matters more than agent confidence.
- Parallel work needs isolation.
- A failed or skipped verification step is a risk, not a success.
- Human attention should focus on intent, evidence, and residual risk.

## Anti-patterns

- Starting implementation from a vague request without defining done.
- Running multiple agents in the same worktree.
- Trusting “tests passed” without real output.
- Hiding blockers behind optimistic summaries.
- Applying this engineering mode to ordinary life-agent questions.
