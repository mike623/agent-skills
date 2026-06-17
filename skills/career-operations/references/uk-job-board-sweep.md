# UK job-board sweep pattern

Use when the user asks whether broader UK boards (Indeed, JobDB, Reed, CV-Library, Totaljobs, JobServe, Adzuna, LinkedIn) were included, or when company/ATS scans over-index on London and miss regional/remote roles.

## Search strategy

1. Start from the user's real commute geography, not just national tech hubs.
   - For a Doncaster-based user: Remote UK first, then Sheffield / Leeds / Manchester / Yorkshire / Northern England hybrid, then remote Europe/EMEA, then London only if exceptional.
2. Search both strict site-specific queries and broader board-name queries.
   - Strict queries may return zero results due to indexing/anti-scraping quirks.
   - Broader queries often surface the same posting through CV-Library, Reed, Totaljobs, JobServe, Adzuna, LinkedIn snippets, and recruiter mirrors.
3. Query examples:
   - `uk indeed technical lead manchester react node typescript aws 70000`
   - `reed senior software engineer manchester node.js typescript aws 70000`
   - `cv library technical lead manchester react node aws 70000`
   - `totaljobs lead fullstack engineer leeds node typescript aws 75000`
   - `jobserve senior software engineer manchester node.js typescript aws 70000`
   - `senior software engineer sheffield typescript node aws 75000 remote`
4. Deduplicate aggressively: one role may appear on CV-Library, Reed, Adzuna, JobServe, LinkedIn, and the recruiter site.
5. Separate result classes:
   - direct employer/JD page (best);
   - recruiter page with salary/location snippet (usable, verify client/scope);
   - aggregator/search page (weak evidence; use only to discover original posting);
   - generic Indeed/board search page (not a JD; do not rank as a role).

## Evidence and scoring

Capture for each promising lead:

- role title;
- company/recruiter/source;
- direct URL and alternate mirrors;
- salary evidence and whether it is disclosed, snippet-only, or estimated;
- location evidence and cadence (remote, remote-first, visits/month, hybrid days/week);
- liveness confidence;
- fit risks (salary ceiling, IC vs lead, language mismatch, recruiter-fronted, contract vs permanent).

Rank by practical apply value, not brand prestige:

1. Remote UK / fully remote.
2. Nearby hybrid (Sheffield, Leeds, Manchester, Yorkshire/Northern England for Doncaster).
3. Remote Europe/EMEA with UK payroll/timezone compatibility.
4. London hybrid only if salary/scope clearly offsets commute/relocation.
5. London 3+ days/week is a significant negative.

## Indeed and JobDB notes

- Indeed UK often surfaces generic search result pages via search engines rather than stable specific JDs. Treat these as leads for manual/browser follow-up, not as evaluated roles.
- JobDB may be low-yield for UK senior/lead software searches compared with Reed/CV-Library/Totaljobs/JobServe/Adzuna/LinkedIn. Still try it when the user explicitly asks, but report honestly if no relevant results surface.
- Do not claim a board was covered unless you actually searched it.

## Report shape

Produce a report such as `reports/uk-jobboards-70k-remote-north.md` with:

- coverage result by board;
- `Apply first` section;
- `Worth checking` section;
- explicit Indeed/JobDB conclusion;
- best next action: which full JDs to capture first;
- statement that no applications were submitted.

Keep raw evidence separately, e.g. `reports/uk-jobboards-70k-remote-north-raw.json`, so the user-facing report stays readable.
