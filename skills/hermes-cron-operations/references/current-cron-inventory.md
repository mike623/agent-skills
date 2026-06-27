# Current Hermes Cron Inventory

Audited from `hermes cron list --all` on 2026-06-27.

> Public-safety note: this repo stores reusable procedures and safe templates. Runtime scripts with private local paths/state may remain in `~/.hermes/scripts` or project workdirs; mirror sanitized templates here before publishing.

| Job | Status | Schedule | Script / Mode | Skills | Workdir | Current source of truth |
|---|---|---:|---|---|---|---|
| Daily UK senior/lead engineer job search | paused | `0 9 * * *` | agent job | `career-operations` | `<career-ops-workspace>` | `skills/career-operations/`; external Career-Ops workspace |
| Daily Second Brain intake + learning digest webpage | active | `0 20 * * *` | agent job | `obsidian`, `raindrop-bookmark-curator`, `second-brain-knowledge-search` | `<user-home-or-vault-workdir>` | `skills/raindrop-bookmark-curator/`; local Obsidian/Hermes skills |
| Hourly Raindrop AI idea-capture engine | active | every 60m | agent job, local delivery | `obsidian`, `mcporter`, `raindrop-bookmark-curator`, `second-brain-knowledge-search` | `<user-home-or-vault-workdir>` | `skills/raindrop-bookmark-curator/`; local Obsidian/Hermes skills |
| Raindrop AI digest pipeline watchdog | active | every 360m | `raindrop_ai_digest_watchdog.py`, `no_agent: true` | none attached | n/a | runtime: `~/.hermes/scripts/raindrop_ai_digest_watchdog.py`; should have sanitized template/reference here |
| Daily Gmail job-alert digest into Career-Ops | active | `15 8 * * *` | `career_ops_job_email_digest.sh` | `career-operations`, `himalaya` | `<career-ops-workspace>` | `skills/career-operations/`; runtime wrapper in `~/.hermes/scripts/` |
| Daily DCLT badminton availability | active | `0 7 * * *` | `dclt_badminton.py`, `no_agent: true` | none attached | n/a | runtime: `~/.hermes/scripts/dclt_badminton.py`; needs dedicated public-safe skill/template if kept long-term |

## Runtime scripts currently in `~/.hermes/scripts`

- `build_daily_bite_html.py`
- `build_second_brain_search.py`
- `career_ops_job_email_digest.sh`
- `cc_codex_health_degraded.py`
- `cc_codex_quota_report.py`
- `daily_bite_static_server.py`
- `dclt_badminton.py`
- `dclt_badminton_check.py`
- `open_dclt_browser.sh`
- `openusage_visual_report.py`
- `raindrop_ai_digest_watchdog.py`

## Follow-up normalization needed

- [ ] Add sanitized script templates for script-only watchdogs.
- [ ] Add a DCLT/GladstoneGo public-safe automation skill or template if this remains a recurring workflow.
- [ ] Document OpenUsage quota scripts under this skill or a dedicated usage-watchdog skill.
- [ ] Keep default/main profile as cron owner; secondary bot profiles should have cron disabled unless explicitly assigned.
