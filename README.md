# Agent Skills

Reusable, public-safe [agent skills](https://www.skills.sh) and templates for software projects and personal workflows.

Each skill is a self-contained `SKILL.md` directory that any compatible agent — Claude Code, Codex, Cursor, GitHub Copilot — can load by name. The repository is intentionally named generically so non-Claude skill formats can live alongside the current ones later.

## Skills

| Skill | What it does |
| --- | --- |
| [`flutter-release-flow`](skills/flutter-release-flow) | Reusable Flutter release standard: `mise`, Bundler, CocoaPods, Fastlane, Apple `match` signing, TestFlight/App Store, Android Play internal release, plus new-project setup templates. |
| [`career-operations`](skills/career-operations) | Job-search operations co-pilot: role scanning, UK job-board sweeps, fit/salary/location evaluation, CV tailoring, application tracking, and `ctx7`/Context7 doc lookups. |
| [`deep-rock-galactic-board-game`](skills/deep-rock-galactic-board-game) | Public-safe *Deep Rock Galactic: The Board Game* rules assistant backed by a user-built local index of legally obtained notes. |
| [`boardgame-rag-bot`](skills/boardgame-rag-bot) | Generic board-game rules-agent factory: BGG metadata + user-provided rulebook PDF → private semantic/lexical RAG package with citations. |
| [`raindrop-bookmark-curator`](skills/raindrop-bookmark-curator) | Raindrop.io bookmark curation: scan recent/state-tracked items, extract public content, rename titles, update descriptions, add tags, sort into collections, write optional Markdown notes, and track state. |
| [`life-agent-modes`](skills/life-agent-modes) | Persistent mode-routing rules for a general life agent: concierge, research librarian, engineering first mate, operator, career ops, and creative studio without over-applying one mindset. |
| [`engineering-first-mate`](skills/engineering-first-mate) | Engineering coordination playbook for coding-agent lanes, worktrees, tests, evidence, PRs, verification, and risk reporting. |
| [`youtube-second-brain`](skills/youtube-second-brain) | YouTube-to-second-brain workflow: transcripts, summaries, claims, actions, Obsidian-style notes, Raindrop metadata, and NotebookLM-ready source packs. |

## Install

Install one or more skills into your agent with the [`skills`](https://www.skills.sh) CLI:

```bash
npx skills add mike623/agent-skills
```

Or copy a skill directory manually into your Claude Code skills folder:

```bash
mkdir -p ~/.claude/skills
cp -R skills/flutter-release-flow ~/.claude/skills/
```

## Usage

Ask your agent to use a skill by name:

```text
Use the flutter-release-flow skill to set up release automation for this Flutter app.
```

```text
Use the career-operations skill to scan and shortlist remote senior engineering roles.
```

```text
Use the deep-rock-galactic-board-game skill to answer this Space Rig campaign rules question from my local notes.
```

The agent loads the matching `SKILL.md` and follows its workflow.

## Repository layout

```text
skills/
├── flutter-release-flow/          # SKILL.md + Fastlane/mise/Gemfile templates
├── career-operations/             # SKILL.md + job-search reference workflows
├── deep-rock-galactic-board-game/ # SKILL.md + local-index build/lookup scripts
├── boardgame-rag-bot/             # Generic BGG/PDF → private semantic RAG agent factory
├── raindrop-bookmark-curator/     # Raindrop title/description/tag/collection curation workflow
├── life-agent-modes/              # General-agent mode routing and anti-overengineering rules
├── engineering-first-mate/        # Coding-agent orchestration, evidence, and risk reporting
└── youtube-second-brain/          # YouTube transcript/note/NotebookLM source-pack workflow
```

The flat `skills/<name>/SKILL.md` layout is what the `skills` CLI discovers automatically.

## Public-safety notes

> [!IMPORTANT]
> This repository contains templates and generic tooling only.

Do not commit:

- real `.env`, `.p8` keys, certificates, or provisioning profiles;
- passwords, API keys, or generated release artifacts;
- official rulebook PDFs/text, extracted rulebook chunks, or generated indexes;
- private filesystem paths or personal profile state.

Skill templates ship with placeholders (`templates/.env.example`, `templates/sources.example.json`) — copy them locally and fill in your own values.
