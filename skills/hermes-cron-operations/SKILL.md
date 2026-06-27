---
name: hermes-cron-operations
description: Maintain Hermes cron jobs with explicit skill/script ownership, public-safe script templates, profile delivery checks, and reproducible cron inventories.
version: 0.1.0
author: Mike Wong + Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, cron, scheduled-jobs, watchdogs, automation]
    related_skills: [raindrop-bookmark-curator, career-operations]
---

# Hermes Cron Operations

Use this skill when creating, fixing, auditing, or migrating Hermes cron jobs.

## Ownership rules

1. Keep cron execution owned by the intended Hermes profile, usually the default/main profile.
2. Secondary Telegram bots/profiles should not claim shared cron jobs unless explicitly intended.
3. For each cron job, maintain:
   - schedule and delivery target,
   - script path or agent prompt,
   - required skills,
   - workdir,
   - verification command,
   - healthy/silent output behaviour if `no_agent: true`.
4. Public reusable procedures and safe templates belong in this repo.
5. Private local runtime scripts may live in `~/.hermes/scripts`; mirror only public-safe versions/templates here. Do not commit secrets, tokens, private state files, real cookie stores, raw logs, or hardcoded private paths.

## Script-only cron contract

For `no_agent: true` jobs:

- stdout is delivered verbatim;
- healthy/watchdog jobs should print nothing;
- alerting jobs should print concise Telegram-ready text;
- scripts must cap output and avoid raw JSON/log dumps;
- run the script manually before attaching it to cron.

## Audit checklist

1. List jobs: `hermes cron list --all`.
2. Verify each job has a matching skill/procedure in this repo or an existing installed skill.
3. Verify referenced scripts exist under the profile that will execute the job, or under shared `~/.hermes/scripts` when run by the default profile.
4. Verify secondary profiles have `cron.provider: disabled` if they should not deliver scheduled jobs.
5. Run script manually or force-run cron once.
6. Record the inventory in `references/current-cron-inventory.md`.

## Current local cron families

See `references/current-cron-inventory.md` for the latest audited local jobs and where their implementation lives.
