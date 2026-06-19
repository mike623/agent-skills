---
name: <game-slug>-rules
description: Answer <Game Title> board-game rules questions from a private local RAG index with page/source citations.
---

# <Game Title> Rules Assistant

Use this generated skill for rules questions about **<Game Title>**.

## Source material

Private source directory:

```text
<sources-dir>
```

BGG metadata:

```text
<sources-dir>/bgg-metadata.json
```

RAG index:

```text
<rag-dir>
```

## Required lookup workflow

Before answering rules questions, run:

```bash
<lookup-script> "<question>" --limit 5
```

Use returned `source`, `page`, `heading`, `match_type`, `excerpt`, and `score` fields. If results are weak, retry with alternate keywords. If still weak, say the official rule was not found.

## Answer style

```text
Ruling: <direct answer>

Do this:
- <step>
- <step>

Source: <source>, p. <page> / <heading>
Confidence: high|medium|low
```

## Safety and copyright

- Do not quote long rulebook passages.
- Paraphrase and cite.
- Label unsupported recommendations as `Table ruling`, not official rules.
- Prefer official errata/FAQ over printed rulebook if both are indexed.
