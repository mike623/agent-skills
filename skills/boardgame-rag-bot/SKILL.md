---
name: boardgame-rag-bot
description: Create public-safe board-game rules agents from a BGG link plus user-provided rulebooks, using private semantic RAG, lexical fallback, and page citations.
---

# Boardgame RAG Bot

Use this skill when the user wants to turn a board game into a rules assistant from a BoardGameGeek link, PDF rulebook, FAQ, errata, or local notes.

The skill is intentionally **frontend-agnostic**: it creates a local RAG-backed agent package that Claude Code, Codex, Cursor, Hermes, or another agent can use. Telegram/Discord bots are optional wrappers, not part of the core workflow.

## Public-safe constraints

- Do **not** commit official rulebook PDFs, extracted full text, generated chunks, embeddings, indexes, or private filesystem paths.
- Keep source documents and generated RAG indexes in a user-local output directory.
- Quote only short snippets returned by lookup; prefer paraphrased rulings with citations.
- If a BGG file needs login or an expiring signed URL, ask the user to download/upload/provide a fresh direct link. Never ask for BGG passwords.
- Treat BGG metadata as useful context, not rules authority. Official rulebook/FAQ/errata sources are authoritative.

## Practical user flow

User provides:

```text
Make a rules agent from https://boardgamegeek.com/boardgame/<id>/<slug>
```

Best MVP command:

```bash
python3 skills/boardgame-rag-bot/scripts/boardgame_agent_from_bgg.py \
  "https://boardgamegeek.com/boardgame/<id>/<slug>" \
  --pdf /path/to/rulebook.pdf \
  --out /path/to/private/boardgame-agents/<game-slug>
```

Output package:

```text
<out>/
├── README.md
├── SKILL.md                         # generated game-specific agent skill
├── sources/
│   ├── bgg-metadata.json
│   ├── source-links.json
│   ├── rulebook.pdf                 # private, gitignored by default
│   ├── rulebook.raw.txt             # private extraction
│   └── rulebook.md                  # private cleaned Markdown with page anchors
├── rag/
│   ├── chunks.jsonl                 # generated, private
│   ├── manifest.json
│   ├── embeddings.npy               # if semantic deps available
│   └── vectorizer.pkl               # if sklearn available
└── scripts/
    └── lookup.py
```

## Retrieval policy

Always do retrieval before answering rules questions:

```bash
<out>/scripts/lookup.py "<question>" --limit 5
```

Use the returned `source`, `page`, `heading`, `match_type`, and short `excerpt` fields to answer.

Answer format:

```text
Ruling: <direct answer>

Do this:
- <step>
- <step>

Source: <source>, p. <page> / <heading>
Confidence: high|medium|low
```

If retrieval is weak or conflicting:

```text
I could not find a clear official rule in the indexed sources. Table ruling: ...
```

## Build workflow

1. **Fetch BGG metadata** with XML API from the provided BGG URL.
2. **Create a private output package** under `--out`.
3. **Collect rules sources**:
   - use `--pdf` or `--pdf-url` when provided;
   - otherwise save candidate links and ask the user for a rulebook PDF/direct URL.
4. **Extract PDF** to text/Markdown with page anchors.
5. **Build hybrid RAG**:
   - semantic embeddings when `sentence-transformers` + `numpy` are installed;
   - TF-IDF when `scikit-learn` is installed;
   - stdlib BM25-style lexical fallback always.
6. **Generate game-specific `SKILL.md`** that tells future agents to run `scripts/lookup.py` first.
7. **Verify** with 5-10 generic test queries such as setup, turn order, line of sight, end of round, victory, and common game-specific terms.

## Dependencies

The scripts run with Python 3. Optional semantic dependencies:

```bash
python3 -m pip install --user sentence-transformers numpy scikit-learn pymupdf
```

Fallback behavior:

- Without `sentence-transformers`/`numpy`, semantic embeddings are skipped and clearly recorded in `manifest.json`.
- Without `scikit-learn`, TF-IDF is skipped.
- Stdlib lexical BM25-style search still works.

## BGG limitations

BGG metadata is usually accessible through:

```text
https://boardgamegeek.com/xmlapi2/thing?id=<id>&stats=1
```

BGG file downloads are less reliable:

- may require login;
- may use short-lived Geekdo/S3 signed URLs;
- may include fan uploads with unclear authority.

Practical rule: bootstrap metadata automatically, but treat rulebook discovery as best-effort. If the PDF is not publicly accessible, ask the user to provide it.

## Source precedence

When multiple sources disagree:

1. Official errata/FAQ.
2. Current edition rulebook.
3. Expansion rulebook for expansion-specific rules.
4. Publisher player aid/reference.
5. Fan summaries/teaching aids, clearly labeled as non-authoritative.

## Verification checklist

- [ ] Output package exists outside the public skill repo.
- [ ] `sources/bgg-metadata.json` exists.
- [ ] Rulebook PDF/text/Markdown are private and not committed.
- [ ] `sources/rulebook.md` has `## Page N {#page-n}` anchors.
- [ ] `rag/manifest.json` and `rag/chunks.jsonl` exist.
- [ ] Semantic status is recorded in `manifest.json`.
- [ ] `scripts/lookup.py "setup"` returns cited results.
- [ ] Generated game `SKILL.md` requires lookup before rules answers.
