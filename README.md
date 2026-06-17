# Agent Skills

Reusable, public-safe [agent skills](https://www.skills.sh) and templates for software projects and personal workflows.

Each skill is a self-contained `SKILL.md` directory that any compatible agent — Claude Code, Codex, Cursor, GitHub Copilot — can load by name. The repository is intentionally named generically so non-Claude skill formats can live alongside the current ones later.

## Skills

| Skill | What it does |
| --- | --- |
| [`flutter-release-flow`](skills/flutter-release-flow) | Reusable Flutter release standard: `mise`, Bundler, CocoaPods, Fastlane, Apple `match` signing, TestFlight/App Store, Android Play internal release, plus new-project setup templates. |
| [`career-operations`](skills/career-operations) | Job-search operations co-pilot: role scanning, UK job-board sweeps, fit/salary/location evaluation, CV tailoring, application tracking, and `ctx7`/Context7 doc lookups. |
| [`deep-rock-galactic-board-game`](skills/deep-rock-galactic-board-game) | Public-safe *Deep Rock Galactic: The Board Game* rules assistant backed by a user-built local index of legally obtained notes. |

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
└── deep-rock-galactic-board-game/ # SKILL.md + local-index build/lookup scripts
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
