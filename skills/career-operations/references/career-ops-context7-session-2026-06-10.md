# Career-Ops + Context7 session notes — 2026-06-10

## User/job-search context captured

- User is UK-based in Doncaster and is targeting senior engineering / technical lead / AI-product/platform roles.
- Salary preference captured during the session: target/minimum £70,000 base salary per year.
- Location preference captured during the session: remote preferred; UK hybrid acceptable for strong-fit roles.
- Important correction: do not equate "UK hybrid" with London-first. For this Doncaster-based user, nearby hybrid should prioritize Manchester, Leeds, Sheffield, Yorkshire, and Northern England before London.

## Career-Ops workflow that worked

1. Install/setup `santifer/career-ops` in the user's workspace.
2. Verify prerequisites and run Career-Ops health checks.
3. Configure candidate profile from LinkedIn/CV material.
4. Tune scanner filters for senior/lead/full-stack/platform/AI/FDE/solutions-architecture roles.
5. Scan tracked companies and save pending roles to `data/pipeline.md`.
6. Run verification commands after config edits:
   - `npm run doctor`
   - `npm run sync-check`
   - `npm run verify`

## Files edited for preference updates

When user later said: "Salary targets 70k pounds per year. Refer remote but hybrid is acceptable" the right action was to update config, not only acknowledge it.

Career-Ops files changed:

- `config/profile.yml`
  - `compensation.target_range: "£70,000+ base salary per year"`
  - `compensation.minimum: "£70,000 base salary per year"`
  - `compensation.location_flexibility: "Remote preferred; UK-based hybrid acceptable for strong-fit roles"`
  - `location.onsite_availability: "Remote preferred; UK hybrid acceptable for strong-fit roles"`
- `modes/_profile.md`
  - comp target narrative;
  - salary expectation script;
  - location policy: remote preferred, UK hybrid acceptable for strong-fit roles meeting £70k+ scope/comp.

The update was verified with `npm run sync-check` and `npm run verify`.

## Location ranking correction

A later evaluation pass over-weighted London because the initial Career-Ops scan targeted high-signal AI/SaaS/FDE/platform companies, many of which list UK roles in London. The user challenged this: "Why also London? Did u look for nearby location like Leeds, Sheffield and Manchester?"

Future workflow:

1. For Doncaster/Northern England users, explicitly search and rank nearby hybrid markets: Manchester, Leeds, Sheffield, Yorkshire, North West, North East, Northern England.
2. Keep London roles, but label them as secondary unless the role is remote-flexible or exceptional on salary/scope.
3. Update `portals.yml` `location_filter.always_allow` and `location_filter.allow` with nearby regions, not just `United Kingdom`/`London`/`Europe`.
4. If producing a shortlist, include a separate nearby-location pass or evidence file, e.g. search terms combining role + city + salary + stack (`Senior Software Engineer Manchester £70000 remote TypeScript AWS`).
5. Re-rank recommendations as: remote UK/EMEA first; Manchester/Leeds/Sheffield hybrid second; London hybrid third.

## Context7 / ctx7 interpretation

The user asked to "look up ctx7" in the context of faster job exploration. The relevant interpretation was Upstash Context7, a current-docs/MCP workflow for coding agents.

Practical framing:

- Context7 is not a job board or job-search data source.
- It is useful when customizing Career-Ops because it can provide current docs/examples for APIs and libraries that job-search automation depends on.
- Good use cases:
  - ATS APIs/parsers and board formats;
  - Playwright/current browser automation APIs;
  - GitHub/API docs;
  - document/CV generation libraries;
  - wiring docs lookup into Claude Code sessions.

## Reporting pattern that matched the user's preference

Keep output concise and operational:

- exact repo path;
- files changed;
- counts scanned/saved;
- checks run and pass/fail status;
- next command or next prompt.

Avoid dumping every job URL into chat when the pipeline file already stores them.