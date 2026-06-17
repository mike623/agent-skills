# Agent Skills

Reusable, public-safe agent skills and templates for software projects and personal workflows. The repository starts with Claude Code-compatible `SKILL.md` directories under `skills/`, but is intentionally named generically so Codex/OpenCode/other agent skill formats can be added later.

## Skills

- `deep-rock-galactic-board-game` — public-safe Deep Rock Galactic board-game rules assistant workflow using a user-built local index of legally obtained notes/docs.
- `flutter-release-flow` — reusable Flutter release automation standard covering mise, Bundler, CocoaPods, Fastlane, Apple signing, TestFlight/App Store, Android Play internal release, and new-project setup templates.

## Usage

For Claude Code, copy one or more skill directories into your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cp -R skills/flutter-release-flow ~/.claude/skills/
cp -R skills/deep-rock-galactic-board-game ~/.claude/skills/
```

Future Codex/OpenCode-compatible formats can live alongside `skills/` when we add them.

Then ask Claude Code, Codex, or another compatible agent to use the skill by name, for example:

```text
Use the flutter-release-flow skill to set up release automation for this Flutter app.
```

```text
Use the deep-rock-galactic-board-game skill to answer this Space Rig campaign rules question from my local notes.
```

## Public-safety notes

This repository contains templates and generic tooling only. Do not commit real `.env`, `.p8`, certificates, provisioning profiles, passwords, API keys, generated release artifacts, official rulebook PDFs/text, extracted rulebook chunks, generated indexes, or private profile state.
