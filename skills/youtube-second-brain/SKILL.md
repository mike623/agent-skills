---
name: youtube-second-brain
description: "Use when turning YouTube videos into durable second-brain knowledge: transcripts, summaries, claims, tags, Obsidian notes, Raindrop metadata, and NotebookLM-ready source packs."
version: 1.0.0
author: Mike Wong / agent-skills
license: MIT
metadata:
  tags: [youtube, second-brain, transcripts, obsidian, raindrop, notebooklm, research]
  related_skills:
    - life-agent-modes
---

# YouTube Second Brain

Use this skill when a YouTube video should become reusable knowledge rather than just a saved link. The workflow treats YouTube as a source document: capture, transcript, summary, extraction, linking, and optional deep analysis.

## Core principle

YouTube videos become second-brain material only after they are converted into structured, source-grounded notes.

Do not infer video content from title or thumbnail alone. Fetch a transcript when possible. If only metadata is available, state that clearly.

## Input sources

A video may arrive from:

- a direct YouTube URL;
- a Raindrop bookmark;
- a playlist;
- a browser tab;
- a user note such as “this is worth saving”.

## Processing levels

| Level | Meaning | Action |
| --- | --- | --- |
| L0 | Save only | Keep bookmark, light tags. |
| L1 | Summary | Transcript summary + useful tags. |
| L2 | Knowledge note | Full note with key ideas, claims, actions, links, and transcript. |
| L3 | Deep research | Mark as NotebookLM/deep-analysis candidate. |
| L4 | Operationalize | Convert into checklist, task, project plan, or reusable skill. |

Default to L1/L2 for useful videos. Use L3/L4 only when the video contains reusable strategy, workflows, decisions, or implementation ideas.

## Workflow

1. **Capture metadata**
   - URL, title, channel, date if available, saved date, tags, bookmark ID if present.

2. **Fetch transcript**
   - Prefer official captions or captured transcript text.
   - If transcript unavailable, use public metadata/description only and mark `transcript-unavailable` or `manual-review`.
   - Do not claim to have watched visual content unless actual video analysis was performed.

3. **Extract knowledge objects**
   - TL;DR.
   - Key ideas.
   - Claims and assumptions.
   - Tools/products/people mentioned.
   - Workflows or frameworks.
   - Practical takeaways.
   - Open questions.
   - Follow-up actions.
   - External links from the description/transcript when accessible.

4. **Write a durable note**
   - Use Markdown with YAML/frontmatter.
   - Include source link and transcript provenance.
   - Preserve uncertainty and extraction limits.
   - Add topic links/tags for later retrieval.

5. **Update capture system when available**
   - Rename bookmark to a concise searchable title.
   - Add a short description explaining why it matters.
   - Add tags without removing user tags unless explicitly instructed.
   - Mark state such as `transcript-extracted`, `obsidian-note`, `notebooklm-candidate`, or `manual-review`.

6. **Decide NotebookLM readiness**
   - Good candidates: dense conceptual videos, multi-source research, product/tool comparisons, strategy, workflows, or claims to challenge.
   - Poor candidates: shallow news, entertainment-only clips, duplicate content, or videos with no transcript and little metadata.

## Suggested note schema

```markdown
---
type: youtube-note
source: youtube
url: <url>
channel: <channel-if-known>
saved_date: <date-if-known>
processed_at: <timestamp>
tags:
  - youtube
  - research
status: processed
notebooklm: false
---

# <Searchable video title>

## Source

- Video: <url>
- Channel: <channel>
- Transcript: <official captions / auto captions / captured by bookmark tool / unavailable>

## TL;DR

<short summary>

## Key ideas

- ...

## Claims and assumptions

- Claim: ...
  - Evidence in transcript: ...
  - Verification needed: ...

## Tools / links / people mentioned

- ...

## Practical takeaways

- ...

## Questions for deeper analysis

- ...

## Follow-up actions

- [ ] ...

## Transcript / excerpts

<transcript or relevant excerpts>
```

## NotebookLM source-pack guidance

When preparing for NotebookLM, include:

- original video URL;
- transcript or transcript note;
- summary;
- key questions to ask;
- related articles/videos/notes;
- extraction limitations.

Useful NotebookLM prompts:

```text
Extract the core argument and supporting claims from this source.
```

```text
Compare this video against the other sources in this notebook. Where do they agree or contradict?
```

```text
Turn this into an implementation memo with concrete next actions.
```

## Public-safety rules

- Do not bypass paywalls, login walls, private videos, or gated content.
- Do not fabricate transcript, comments, engagement, or visual details.
- Do not commit private bookmark IDs, local vault paths, or personal notes into public skill repos.
- Use placeholders in examples.
