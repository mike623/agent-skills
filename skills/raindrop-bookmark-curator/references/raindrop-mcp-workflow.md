# Raindrop MCP workflow

Use Raindrop's official Streamable HTTP MCP endpoint with `mcporter` for bookmark curation.

Endpoint:

```text
https://api.raindrop.io/rest/v2/ai/mcp
```

## Discover available tools

```bash
npx -y mcporter list \
  --http-url https://api.raindrop.io/rest/v2/ai/mcp \
  --name raindrop \
  --schema --json
```

Expected useful tools include:

- `find_bookmarks`
- `fetch_bookmark_content`
- `find_collections`
- `create_collections`
- `update_bookmarks`
- `find_tags`
- `update_tags`

## Mutation discipline

Before writing:

1. Resolve bookmark IDs and collection IDs.
2. Fetch current bookmark state.
3. Generate proposed title/note/tags/collection.
4. Mutate with `update_bookmarks`.
5. Read back with `find_bookmarks` and `fetch_bookmark_content`.
6. Update local state only after verification.

## Batch update shape

```json
{
  "updates": [
    {
      "bookmark_ids": [123],
      "update": {
        "title": "Clean content-based title",
        "note": "Concise description grounded in extracted content.",
        "collection_id": 456,
        "add_tags": ["ai-coding", "repo-analysis"]
      }
    }
  ]
}
```

Keep batch writes small enough to inspect and recover. For high-risk runs, do a dry-run table first.

## Verification

`find_bookmarks` usually returns title/tags/collection/link. `fetch_bookmark_content` is better for confirming the bookmark note/description.

If either verification step fails, report the bookmark as partial and do not mark it as fully processed in state.
