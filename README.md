# Claude Skills

Reusable Claude Code skills and templates for software projects.

## Skills

- `flutter-release-flow` — reusable Flutter release automation standard covering mise, Bundler, CocoaPods, Fastlane, Apple signing, TestFlight/App Store, Android Play internal release, and new-project setup templates.

## Usage

Copy a skill directory into your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cp -R skills/flutter-release-flow ~/.claude/skills/
```

Then ask Claude Code to use the skill by name, for example:

```text
Use the flutter-release-flow skill to set up release automation for this Flutter app.
```

## Public-safety notes

This repository contains templates only. Do not commit real `.env`, `.p8`, certificates, provisioning profiles, passwords, API keys, or generated release artifacts.
