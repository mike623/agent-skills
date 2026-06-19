# Boardgame RAG Bot

Create a private, citation-grounded board-game rules agent from a BoardGameGeek link plus legally obtained rulebook PDFs/notes.

This skill ships **generic scripts and templates only**. Do not commit real rulebooks, extracted rulebook text, generated chunks, embeddings, or private paths.

## Quick start

```bash
python3 skills/boardgame-rag-bot/scripts/boardgame_agent_from_bgg.py \
  "https://boardgamegeek.com/boardgame/174430/gloomhaven" \
  --pdf /path/to/rulebook.pdf \
  --out /tmp/boardgame-agents/gloomhaven

/tmp/boardgame-agents/gloomhaven/scripts/lookup.py "line of sight" --limit 5
```

The generated package contains a game-specific `SKILL.md`, private source extraction, a local RAG index, and a lookup script.

## Optional dependencies

```bash
python3 -m pip install --user sentence-transformers numpy scikit-learn pymupdf
```

Without optional dependencies, the package still builds a lexical fallback index.
