---
name: career-operations
description: "Use when helping with job search operations: setting up Career-Ops or similar job-search automation, scanning roles, configuring candidate profile/compensation/location filters, evaluating job fit, tailoring CV/application materials, and using documentation lookup tools such as Context7/ctx7 to move faster."
---

# Career Operations

Use this skill for job-search workflows where the user wants active help discovering, filtering, evaluating, and applying to roles.

## Trigger phrases

- "looking for a new job"
- "explore career-ops"
- "scan roles/jobs"
- "senior engineer / technical lead roles"
- "update salary target"
- "remote or hybrid roles"
- "tailor my CV / application"
- "use ctx7 / Context7 for faster job explore"

## Operating principles

1. **Actively set up and verify the workspace.** Do not only summarize a tool from GitHub; clone/install/configure it when the user asks to explore or use it, then run its health checks.
2. **Keep candidate preferences machine-readable.** Put durable preferences in the tool's config files, not just in chat. For Career-Ops this usually means `config/profile.yml`, `modes/_profile.md`, and sometimes scanner config such as `portals.yml`.
3. **Separate discovery from evaluation.** First tune role/location filters and scan/save candidate jobs. Then run a second pass that evaluates fit, salary, remote/hybrid compatibility, and application priority.
4. **Verify after edits.** After changing Career-Ops config, run the project's built-in checks such as `npm run sync-check`, `npm run verify`, and `npm run doctor` when relevant.
5. **Report concise operational status.** Include exact project path, files changed, counts found/saved, commands run, and next command/prompt the user can use.

## Career-Ops setup/checklist

When using `santifer/career-ops`:

1. Clone/install into the user's workspace if needed.
2. Check prerequisites: Node/npm, Claude Code, Go if required, Playwright browser install.
3. Create/update candidate profile from CV/LinkedIn/user input.
4. Tune `portals.yml`:
   - title positives for target roles;
   - title negatives for obvious bad fits;
   - location allow/block lists;
   - tracked companies and search queries.
5. Run scan and save pending jobs into `data/pipeline.md`.
6. Run verification checks.
7. Present top matches and next evaluation prompt.
8. If the first shortlist over-indexes on prestige hubs (e.g. London), run a separate practical-location pass before recommending applications.

## Regional UK job-board sweeps

Company/ATS scans miss many UK recruiter and aggregator postings. When the user asks about boards like Indeed, JobDB, Reed, CV-Library, Totaljobs, JobServe, or Adzuna — or challenges whether nearby locations were searched — run a dedicated job-board sweep instead of relying on the Career-Ops company list.

Use the pattern in `references/uk-job-board-sweep.md`:

- search both strict site-specific queries and broader board-name queries;
- dedupe recruiter mirrors across Reed/CV-Library/Adzuna/JobServe/LinkedIn;
- treat generic Indeed result pages as leads, not evaluated JDs;
- report honestly when JobDB/Indeed produce no high-confidence specific postings;
- rank by practical apply value: remote UK, nearby hybrid, remote Europe/EMEA, then London only if exceptional.

## Preference encoding pattern

For salary/location preferences, update all relevant layers:

- `config/profile.yml`:
  - `compensation.target_range`
  - `compensation.minimum`
  - `compensation.currency`
  - `compensation.location_flexibility`
  - `location.onsite_availability`
- `modes/_profile.md`:
  - comp target narrative;
  - salary expectation script;
  - location policy/scoring notes.
- Persistent user memory only for stable preferences that should survive across sessions.

Example preference interpretation:

- "Salary targets 70k pounds per year" → target and minimum `£70,000` base/year unless the user says it is only a preference.
- "Prefer remote but hybrid is acceptable" → remote should score highest; UK hybrid is acceptable for strong-fit roles meeting scope/comp expectations.
- For a UK user outside London, do not let London dominate merely because many high-signal AI/SaaS companies are London-based. Ask or infer nearby hybrid geographies from the user's base, then explicitly encode them in scanner location filters and ranking. For this user in Doncaster, prioritize remote first, then Manchester/Leeds/Sheffield/Yorkshire/Northern England hybrid, and treat London hybrid as secondary unless salary/scope is exceptional.

## Application submission co-pilot

When the user asks to apply or "submit" shortlisted jobs, treat submission as a co-pilot workflow unless all required non-secret form fields are already known and no login is needed.

Follow `references/application-submission-co-pilot.md`:

- collect common blockers up front: current salary/expectation, notice period, UK work status/visa sponsorship, own transport/driving where relevant, recruiter consent preferences, phone/email, and CV path;
- never type, create, store, or ask the user to reveal passwords; have the user complete login, magic-link, CAPTCHA, permission, and personal-attestation steps themselves;
- prefer direct employer/ATS pages, then recruiter mirrors/direct recruiter email, then prepared application packs for login-gated aggregators;
- if automation is blocked by login or account creation, say clearly what was prepared and what the user must do manually.

Do not wait until after failed form attempts to explain this boundary. State early what can be automated versus what needs the user present.

## Application tracking corrections

When the user reports applications after the fact (e.g. "No2 applied", "Done Zorba", "we applied Adria, Tiro and Faculty"), prioritize the explicit company/role names they give over any inferred shortlist numbering. If numbers are ambiguous across multiple shortlists/reports, inspect the tracker/pipeline and either map only high-confidence entries or ask a short clarification before writing. If the user corrects an applied list, immediately rewrite `data/applications.md` to the corrected set, remove wrongly inferred entries, preserve useful follow-up questions, then run `npm run verify` before reporting success.

## Application status tracking

When the user says a ranked item was applied (for example, "No2 applied"), update Career-Ops immediately rather than asking again if the ranking context is available:

1. Resolve the number against the latest shortlist/report, commonly `reports/top5-job-links.md` or the current evaluation report.
2. Add/update a row in `data/applications.md` with status `Applied`, the current date, company, role, score, CV/report paths, and concise follow-up notes.
3. Use Career-Ops score format exactly as `4.4/5` (not `4.4`) or `npm run verify` fails.
4. Include a follow-up date in notes when possible (typically about 5 working days / one week after applying).
5. Run `npm run verify` and fix any tracker formatting errors before reporting success.

If the user reports several applications in sequence, keep the reply concise: role recorded, file updated, verification status, and follow-up suggestion.

## Dedicated job-search Hermes profile

When the user asks for a new/dedicated agent for job search, create or configure a separate Hermes profile rather than only describing the idea:

1. Use a class-level profile name such as `jobsearch` and set the profile description around UK senior/lead engineering career operations.
2. Clone useful baseline config/skills from the active profile, then customize the profile `SOUL.md` with job-search defaults: target compensation, remote/hybrid location policy, Career-Ops workspace, concise operating style, and application-submission boundaries.
3. Point the profile at the Career-Ops workspace in config and verify with a real one-shot `pwd`/health-check run before reporting success. If cwd routing does not take effect immediately, tell the user exactly what was verified and use explicit workspace paths in prompts/cron jobs until a fresh session/gateway restart confirms it.
4. Be careful with gateways: do not start a cloned Telegram gateway if it would reuse the default bot token and conflict with the main agent. Leave it stopped and explain that a separate Telegram bot token is needed before `jobsearch gateway setup/start`.
5. Report concise operational status: profile name, profile path, alias, workspace, gateway status, verification command/result, and next command.

## Daily job-search automation

When the user asks for a regular/daily job-search routine, schedule a self-contained recurring job that:

- uses the Career-Ops workspace and loads this skill;
- inspects existing `data/pipeline.md`, `data/applications.md`, `reports/`, config, and prior daily reports before searching;
- searches company/ATS sources plus UK boards/recruiters (Reed, CV-Library, Totaljobs, JobServe, Adzuna, Indeed UK, LinkedIn snippets, IT Jobs Watch, recruiter/direct pages);
- dedupes against existing records and recruiter mirrors by canonical URL, company, title, location, salary, and role details;
- evaluates only live/high-confidence roles and labels snippet-only/blocked pages clearly;
- writes a dated report under `reports/daily-job-search-YYYY-MM-DD.md` with coverage, new roles, deduped/rejected roles, ranked shortlist, recruiter questions, CV angle, and next actions;
- updates pipeline records where appropriate without duplicating existing entries;
- runs `npm run verify` at minimum, plus `sync-check`/`doctor` after config changes;
- delivers a concise Telegram summary with counts, top 3–5 roles, files updated, verification result, and recommended action.

## Context7 / ctx7 acceleration

If the user asks about `ctx7` or `Context7`, first disambiguate by lookup if needed. In this session, `ctx7` referred to Upstash Context7: a docs server / MCP tool that gives current library docs and examples to coding agents.

Use it for faster job-search tooling work by:

- pulling current docs for Career-Ops dependencies, ATS APIs, Playwright, GitHub APIs, scraping libraries, or CV/document-generation libraries;
- avoiding stale API assumptions during scanner/parser customization;
- installing or linking Context7 docs access into agent workflows such as Claude Code when the user wants autonomous coding support.

Do not describe Context7 as a job board. It accelerates building/customizing the job-search system; it does not itself discover jobs.

## Pitfalls

- Do not make a mass-apply bot positioning claim for Career-Ops; frame it as a pipeline/evaluation/tailoring assistant unless upstream docs say otherwise.
- Avoid US-only remote matches when the user is UK-based unless the posting explicitly supports UK/Europe/EMEA time zones.
- When the pipeline has many matches, do not dump all URLs; shortlist by fit and save the full list in the repo.
- Do not rely on chat-only preferences. Write them into config and verify.
- Do not assume a company/ATS scan covers the broader job-board market. If the user asks about specific boards, search those boards explicitly and say which yielded useful JDs versus only generic search pages.
- Avoid presenting search snippets as confirmed live postings. Label snippet-only salary/location/liveness clearly and make full-JD capture the next step.
- Before telling the user “apply to this today,” verify the recommended links are still live/extractable, especially recruiter/aggregator links such as Haystack, Totaljobs, Reed, CV-Library, BeBee, LinkedIn snippets, and other mirrors. If the user reports a link is expired or invalid, immediately mark that pipeline item completed/invalid with the date and user-supplied reason, run `npm run verify`, then re-rank from verified/live candidates only.
- Prefer direct employer/ATS apply links over aggregator mirrors in final recommendations. If only a mirror is available, say so and label it as “verify first” rather than presenting it as a clean application target.
- Do not imply autonomous submission is guaranteed. Many recruiter/job-board forms require login, passwords, magic links, CAPTCHA, consent, or personal declarations. Prepare the application pack and co-pilot, but make user-needed steps explicit early.

## References

- `references/career-ops-context7-session-2026-06-10.md` — session-specific notes from setting up Career-Ops for a UK senior/lead engineer profile and interpreting Context7/ctx7.
- `references/uk-job-board-sweep.md` — durable workflow for UK remote/Northern job-board sweeps across Indeed, JobDB, Reed, CV-Library, Totaljobs, JobServe, Adzuna, LinkedIn, and recruiter mirrors.
- `references/application-submission-co-pilot.md` — workflow for moving shortlisted roles into applications while handling login/password/magic-link blockers, direct recruiter email fallbacks, and prepared application packs.