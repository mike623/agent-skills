# Agent Skills

Reusable agent skills and templates for software projects. The repository starts with Claude Code-compatible `SKILL.md` skills, but is intentionally named generically so Codex/OpenCode/other agent skill formats can be added later.

## Skills

- `flutter-release-flow` — reusable Flutter release automation standard covering mise, Bundler, CocoaPods, Fastlane, Apple signing, TestFlight/App Store, Android Play internal release, and new-project setup templates.

## Usage

For Claude Code, copy a skill directory into your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cp -R skills/flutter-release-flow ~/.claude/skills/
```

Future Codex/OpenCode-compatible formats can live alongside `skills/` when we add them.

Then ask Claude Code, Codex, or another compatible agent to use the skill by name, for example:

```text
Use the flutter-release-flow skill to set up release automation for this Flutter app.
```

## Public-safety notes

This repository contains templates only. Do not commit real `.env`, `.p8`, certificates, provisioning profiles, passwords, API keys, or generated release artifacts.
