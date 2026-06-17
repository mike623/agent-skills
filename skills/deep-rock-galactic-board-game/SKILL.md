---
name: deep-rock-galactic-board-game
description: Public-safe DRG board-game rules assistant using a user-built local index for lookups, citations, setup reminders, and expansion questions.
---

# Deep Rock Galactic Board Game Assistant

Use this skill to answer **Deep Rock Galactic: The Board Game** rules and play-aid questions from the user's own local reference documents.

Public-safe constraints:

- Do **not** quote or reproduce official rulebook text beyond short snippets returned by the local lookup tool.
- Do **not** commit PDFs, extracted rulebook chunks, generated indexes, private filesystem paths, tokens, or profile state.
- Treat the scripts as generic tooling: the user must provide `--source-dir`, `DRG_SOURCE_DIR`, or a local config copied from `templates/sources.example.json`.
- Prefer concise answers with source/page/heading citations. If a rule is uncertain, say so and point to the retrieved citation instead of inventing wording.

## Quick setup

```bash
cd skills/deep-rock-galactic-board-game
python3 scripts/build_drg_index.py \
  --source-dir /path/to/your/drg-board-game-notes \
  --index-dir /tmp/drg-index
python3 scripts/drg_lookup.py --index-dir /tmp/drg-index "line of sight reaction attack"
```

You can also set:

```bash
export DRG_SOURCE_DIR=/path/to/your/drg-board-game-notes
export DRG_INDEX_DIR=/tmp/drg-index
```

Or copy `templates/sources.example.json` to a local, gitignored config and pass `--sources-config`.

## Lookup workflow

1. Ensure an index exists. If not, ask for or infer the local source directory and run `scripts/build_drg_index.py`.
2. Run 1-3 focused lookup queries with `scripts/drg_lookup.py --index-dir <dir> "<query>"`.
3. Synthesize the answer using retrieved page/source/heading citations.
4. Keep quotations short. Paraphrase rules and cite the local source.
5. For expansion questions, use `--source` to narrow results when useful (for example `--source "Space Rig"`).

## Script notes

- `build_drg_index.py` indexes Markdown/text files into `chunks.jsonl` and `manifest.json`.
- `drg_lookup.py` performs deterministic BM25-style lexical search and returns JSON.
- Lookup output hides local file paths by default; use `--include-path` only for private debugging.
- Generated `.drg-index/`, `chunks.jsonl`, and `manifest.json` are ignored by this skill pack's `.gitignore`.
