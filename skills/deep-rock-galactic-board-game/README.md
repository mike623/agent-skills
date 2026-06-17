# Deep Rock Galactic Board Game skill pack

This skill pack provides a public-safe local assistant workflow for Deep Rock Galactic board-game rules questions. It includes only generic scripts and templates; it does **not** include official rulebook text, PDFs, extracted chunks, generated indexes, private profile paths, or secrets.

## Files

- `SKILL.md` - agent-facing skill instructions.
- `scripts/build_drg_index.py` - builds a deterministic lexical index from user-provided Markdown/text docs.
- `scripts/drg_lookup.py` - searches the generated index and returns JSON citations/snippets.
- `templates/sources.example.json` - copyable local config template.
- `.gitignore` - prevents generated/private local artifacts from being committed.

## Build an index

```bash
python3 scripts/build_drg_index.py \
  --source-dir /path/to/your/drg-board-game-docs \
  --index-dir /tmp/drg-index
```

Optional environment variables:

```bash
export DRG_SOURCE_DIR=/path/to/your/drg-board-game-docs
export DRG_INDEX_DIR=/tmp/drg-index
python3 scripts/build_drg_index.py
```

Optional config:

```bash
cp templates/sources.example.json sources.local.json
# Edit sources.local.json, then:
python3 scripts/build_drg_index.py --sources-config sources.local.json
```

`source_dir` must point to documents you are allowed to use locally. By default, all `*.md`, `*.markdown`, and `*.txt` files in the directory are indexed. Use repeated `--doc <filename>` flags or `docs` in the config to curate specific files.

## Lookup

```bash
python3 scripts/drg_lookup.py --index-dir /tmp/drg-index "line of sight reaction attack"
python3 scripts/drg_lookup.py --index-dir /tmp/drg-index --source "Space Rig" "brew events"
```

The lookup output includes source name, page (when detected from Markdown headings such as `## Page 12 {#page-12}`), heading, short excerpt, and anchor. Local paths are hidden unless `--include-path` is supplied.

## Public-safe behavior

- Generated indexes are local-only and gitignored.
- Stored excerpts default to 360 characters per chunk.
- Answers should paraphrase and cite; avoid reproducing official rulebook passages.
