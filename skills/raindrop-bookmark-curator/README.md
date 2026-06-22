# Raindrop Bookmark Curator

Public-safe skill for curating Raindrop.io bookmarks with an agent.

It covers:

- scanning recent or state-tracked bookmarks;
- extracting public page/social-post content;
- renaming bookmark titles from content;
- updating bookmark notes/descriptions;
- adding tags;
- sorting bookmarks into collections;
- optionally writing Markdown/Obsidian notes;
- maintaining a state file for delta processing and audit history.

## What this skill does not ship

This directory intentionally does **not** include:

- real Raindrop OAuth tokens or cookies;
- real collection IDs;
- real bookmark state files;
- generated personal notes;
- private filesystem paths.

Copy the templates under `templates/` into a private local workspace before using them.

## Quick trigger

```text
Use the raindrop-bookmark-curator skill to scan my recent Raindrop bookmarks, rename titles, update descriptions, sort into collections, and track state.
```

## Main entry point

See [`SKILL.md`](SKILL.md).
