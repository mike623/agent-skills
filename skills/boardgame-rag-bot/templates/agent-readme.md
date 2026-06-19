# <Game Title> Rules Agent

Private local board-game rules assistant generated from:

```text
<BGG URL>
```

## Ask a question

```bash
scripts/lookup.py "<rules question>" --limit 5
```

## Contents

```text
sources/      private PDFs/extracted text/metadata
rag/          generated local RAG index
scripts/      lookup helper
SKILL.md      generated agent instructions
```

## Public safety

Do not commit this generated package unless you remove private rulebooks, extracted rulebook text, generated chunks, embeddings, and private paths.
