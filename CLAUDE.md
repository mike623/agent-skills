# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of **agent skills** — not an application. Each skill is a self-contained directory under `skills/<name>/` whose entry point is a `SKILL.md` file. Skills are distributed via the [skills.sh](https://www.skills.sh) `skills` CLI (`npx skills add mike623/agent-skills`) and consumed by agents (Claude Code, Codex, Cursor, Copilot) by name.

There is no app-level build, lint, or test step. Most content is Markdown instructions and copyable templates. The only executable code lives in the `deep-rock-galactic-board-game` skill (stdlib-only Python 3, no dependencies).

## Skill structure contract

Two rules govern how skills are discovered and loaded — preserve both when adding or moving skills:

1. **Flat layout.** The `skills` CLI auto-discovers `skills/<name>/SKILL.md`. Keep one level deep; do not nest skills deeper without reason.
2. **Frontmatter.** Every `SKILL.md` starts with YAML frontmatter containing `name` (lowercase, hyphens) and `description`. The `description` is what an agent matches against to decide when to load the skill — make it a precise trigger statement, not a summary.

A skill directory may also carry `templates/`, `scripts/`, `references/`, and its own `README.md` and `.gitignore`.

## Public-safety invariant

This is a **public repo** holding generic tooling only. This constraint is woven through every skill and must not be violated:

- Ship `*.example` placeholders (`templates/.env.example`, `templates/sources.example.json`), never real values.
- Never commit secrets (`.env`, `.p8`/`.p12`/`.cer`, provisioning profiles), build/release artifacts, copyrighted source material (rulebook PDFs/text, extracted chunks), generated indexes, or private filesystem paths.
- The root `.gitignore` and `skills/deep-rock-galactic-board-game/.gitignore` already block these — extend them rather than relaxing them.

When a skill references real local paths in examples, use placeholders like `<path-to-existing-app>` (see `flutter-release-flow/SKILL.md`).

## The three skills

- **`flutter-release-flow`** — opinionated Flutter release *standard* (not a script). Encodes one repeatable toolchain: `mise` for Ruby, Bundler-pinned Fastlane/CocoaPods, Apple `match` signing from a shared team branch, and a fixed release spine (load API key → sync signing → compliance metadata → bump build → build → archive → TestFlight/App Store). Templates in `templates/` are the canonical starting files for a new app's `ios/fastlane/`.
- **`career-operations`** — job-search co-pilot built around the external `santifer/career-ops` tool. Core principle: durable preferences live in machine-readable config (`config/profile.yml`, `modes/_profile.md`, `portals.yml`), not chat, and edits are verified with `npm run verify` / `sync-check` / `doctor`. Reference workflows in `references/`.
- **`deep-rock-galactic-board-game`** — local rules-lookup pipeline. The only skill with runnable code.

## deep-rock-galactic-board-game scripts

Stdlib-only Python 3. Build a local lexical index from user-supplied docs, then query it:

```bash
# Build index from Markdown/text docs
python3 skills/deep-rock-galactic-board-game/scripts/build_drg_index.py \
  --source-dir /path/to/docs --index-dir /tmp/drg-index

# Query the index (JSON citations/snippets out)
python3 skills/deep-rock-galactic-board-game/scripts/drg_lookup.py \
  --index-dir /tmp/drg-index "line of sight reaction attack"
```

Indexer detects pages from Markdown headings like `## Page 12 {#page-12}`. Excerpts cap at 360 chars (`MAX_EXCERPT_CHARS`). Local paths are hidden in lookup output unless `--include-path` is passed. Indexes and source material are gitignored — keep them local.
