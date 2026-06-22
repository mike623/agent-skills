---
name: raindrop-bookmark-curator
description: Curate Raindrop.io bookmarks by scanning recent or state-tracked items, extracting public content, renaming titles, updating bookmark notes/descriptions, adding tags, sorting into collections, optionally writing Markdown/Obsidian notes, and maintaining a safe state file.
---

# Raindrop Bookmark Curator

Use this skill when the user wants an agent to organize Raindrop.io bookmarks, especially saved social posts, research links, AI/tool discoveries, reading lists, or inbox-style collections.

The core job is to turn messy saved bookmarks into useful library entries:

- content-based title;
- concise bookmark note/description;
- useful tags;
- appropriate collection;
- optional Markdown/Obsidian note;
- durable state so future runs process only deltas.

## Public-safe constraints

- Do **not** commit OAuth tokens, API keys, cookies, real Raindrop export/state files, generated private notes, personal collection IDs, or private filesystem paths.
- Use placeholders such as `<vault>`, `<state-file>`, `<collection-id>`, and `<bookmark-id>` in reusable templates.
- Never delete bookmarks or collections unless the user explicitly asks and confirms the exact IDs.
- Never bypass login walls, paywalls, CAPTCHAs, private posts, or account-only comments.
- For social posts, extract only publicly visible metadata/content. Mark inaccessible comments/media as `not publicly visible / not extracted`.
- Do not invent post text, comments, links, engagement counts, claims, or summaries.
- Verify every mutation by reading the bookmark back from Raindrop.

## Prerequisites

Preferred interface: Raindrop's Streamable HTTP MCP endpoint via `mcporter`:

```bash
npx -y mcporter list \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop \
  --schema --json
```

On first use, the tool may require OAuth in the user's browser. Do not ask the user for passwords or tokens.

## Standard workflow

1. **Establish scope**
   - Recent/delta scan: usually `find_bookmarks` with `has_tags`, `collection_ids`, recency, or limit.
   - Historical reprocess: read bookmark IDs from the state file and fetch exactly those IDs.
   - Single item: fetch the provided bookmark ID or URL.

2. **Load or create state**
   - Use `templates/raindrop-state.example.json` as the shape.
   - If missing/invalid, initialize safely with empty arrays/objects.
   - Preserve existing state keys; add new metadata rather than overwriting unrelated state.

3. **Fetch Raindrop data**
   - Use `find_bookmarks` for lists and current title/tags/collection.
   - Use `fetch_bookmark_content` for the full bookmark payload, including note/description when available.

4. **Extract public content**
   - Use Raindrop metadata first.
   - Use normal web extraction for accessible articles, docs, GitHub repos, product pages, PDFs, etc.
   - For Threads/Instagram/X/TikTok-like pages, use browser extraction only when needed and only for public visible content.
   - If the page is gated, summarize only metadata that is actually visible.

5. **Generate curation metadata**
   - `title`: concise, searchable, content-based. Avoid raw URLs and social shortcodes.
   - `note`: 1–2 sentence bookmark description explaining what it is and why it matters.
   - `tags`: add helpful tags; do not remove existing user tags unless explicitly asked.
   - `collection`: choose the best match from the configured taxonomy. Create collections only when the user asked for sorting and the needed collection does not already exist.

6. **Optional note output**
   - If requested, write one Markdown note per bookmark.
   - Include source metadata, original visible text/excerpt, external links found, external link summaries, useful public comments if available, TL;DR, key ideas, why it matters, and follow-up actions.

7. **Mutate Raindrop**
   - Use `update_bookmarks` for title, note/description, collection, and tags.
   - Never perform delete/merge operations as part of normal curation.

8. **Verify**
   - Read back with `find_bookmarks` for title, tags, and collection.
   - Read back with `fetch_bookmark_content` for note/description.
   - Report any mismatch or API limitation honestly.

9. **Update state**
   - Add successfully processed IDs only after all required outputs/mutations are verified.
   - Store applied title, description, collection name/id, tags, timestamps, and note path if applicable.
   - Do not mark failed or partially processed bookmarks as fully processed.

## Useful mcporter calls

List tools/schema:

```bash
npx -y mcporter list \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop \
  --schema --json
```

Find newest bookmarks with a tag:

```bash
npx -y mcporter call \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop find_bookmarks \
  --args '{"has_tags":["ai"],"limit":50,"sort":"created_desc"}' \
  --output json
```

Find specific historical bookmarks by ID:

```bash
npx -y mcporter call \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop find_bookmarks \
  --args '{"bookmark_ids":[123,456],"limit":150}' \
  --output json
```

Fetch full bookmark content/metadata:

```bash
npx -y mcporter call \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop fetch_bookmark_content \
  --args '{"bookmark_id":123}' \
  --output json
```

List collections:

```bash
npx -y mcporter call \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop find_collections \
  --args '{}' \
  --output json
```

Create missing collections, only when sorting was requested:

```bash
npx -y mcporter call \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop create_collections \
  --args '{"create":[{"title":"AI Coding & Developer Tools","description":"AI tools and workflows for coding, repo analysis, prompting, and developer productivity.","parent_id":null}]}' \
  --output json
```

Update a bookmark:

```bash
npx -y mcporter call \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop update_bookmarks \
  --args '{"updates":[{"bookmark_ids":[123],"update":{"title":"Clean content-based title","note":"One or two useful sentences describing the bookmark.","collection_id":456,"add_tags":["ai-coding","prompt-engineering"]}}]}' \
  --output json
```

## Title rules

Good titles are:

- specific enough to find later;
- short enough to scan;
- based on the content, not the platform slug;
- honest about uncertainty.

Examples:

| Bad original | Better title |
| --- | --- |
| `https://www.instagram.com/reel/...` | `GitReverse — reverse-engineer GitHub repos into prompts` |
| `DZsJpOtgrl` | `Tiny World Builder — browser voxel/isometric world editor` |
| `Post by @user` | `ChatGPT RPG simulator GPT collection` |
| `DYjSMxx a` | `Backend API system-design interview reel` |

## Description/note rules

Bookmark notes should be concise, useful, and grounded:

```text
Open-source browser-based tiny-world builder with terrain painting, object placement, roads, traffic, save/share/remix/export, and shared-world features. Useful as a reference for game tooling and world-building workflows.
```

Avoid:

- hype-only copy;
- invented capabilities;
- private comments/media that were not visible;
- long pasted excerpts better stored in a separate Markdown note.

## Collection taxonomy pattern

Use a user-provided taxonomy when available. Otherwise propose a small, stable taxonomy and create collections only after the user asks for sorting.

See `templates/collection-taxonomy.example.json` for a starter taxonomy. Adapt names to the user's domain.

Common AI/bookmark taxonomy:

| Collection | Use for |
| --- | --- |
| AI Game Development | game agents, simulators, world builders, RPG tools, game-dev workflows |
| AI Coding & Developer Tools | coding agents, repo analysis, prompt engineering, developer productivity |
| Software Engineering & System Design | backend, APIs, architecture, scalability, interviews |
| AI Creative Prompts & Assets | image/video/audio prompts, spritesheets, design assets, creative recipes |
| AI Research & Papers | papers, benchmarks, evals, research threads |
| Product & Startup Ideas | market ideas, product strategy, business references |

## Optional Markdown/Obsidian note format

Suggested filename:

```text
YYYY-MM-DD - raindrop-<bookmark_id> - <slug>.md
```

Suggested frontmatter:

```yaml
---
source: raindrop
raindrop_bookmark_id: <bookmark_id>
platform: <domain-or-platform>
link: "<url>"
saved_date: "<raindrop-created-date>"
processed_at: "<local-iso-timestamp>"
tags:
  - ai
---
```

Suggested sections:

```markdown
# <Clean title>

## Source

- Platform/domain:
- Author/account if public:
- Raindrop bookmark ID:
- Link:
- Saved date:
- Tags:

## Original visible post text / bookmark excerpt

> Only quote text actually extracted or visible.

## External links found

- <url>

## External link summaries

### <site/repo/tool>

Grounded summary.

## Useful comments / replies

Not publicly visible / not extracted.

## TL;DR

## Key ideas

## Why it matters

## Follow-up actions
```

## State tracking

Use the state file to avoid duplicate work and maintain an audit trail. Record applied metadata after verification, not before.

Minimum keys:

- `processed_bookmark_ids`
- `last_checked_at`
- `processed_notes`
- `collections`
- `bookmark_metadata`

For each bookmark, store:

- `last_metadata_reprocessed_at`
- `applied_title`
- `applied_description`
- `applied_collection`
- `applied_collection_id`
- `applied_tags`
- `processed_note` if a note was written

## Batch and delta behavior

- For small batches, process in the current agent session.
- For large batches, split into chunks and use parallel subagents only for extraction/classification. Keep Raindrop mutations in the parent agent so writes are centralized and easier to verify.
- Treat failed extraction, failed mutation, or failed verification as a blocker for that item; leave it out of `processed_bookmark_ids` or mark it as `partial`.

## Final report format

Keep final reports operational and concise:

```text
Processed: <n>
Updated titles/descriptions: <n>
Moved collections: <n>
Collections created: <n>
Notes written: <n>
State file: <path>
Verification: read back <n>/<n> bookmarks successfully
Blockers: <none or list>
```

When reporting public/shared output, do not include private file paths unless the user is operating locally and needs them.
