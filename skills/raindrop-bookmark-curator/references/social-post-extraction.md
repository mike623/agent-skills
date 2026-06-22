# Social post extraction notes

Social bookmarks often contain sparse metadata. Use a layered extraction strategy and stay honest about what is public.

## Order of preference

1. Raindrop bookmark metadata and cached content.
2. Standard web extraction for normal pages, repos, docs, articles, PDFs, and product sites.
3. Browser inspection for public social pages only when needed.
4. Manual uncertainty labels when content is gated or media-only.

## Safety boundaries

- Do not log in.
- Do not bypass cookie walls, account gates, CAPTCHAs, rate limits, or paywalls.
- Do not scrape private comments or follower-only content.
- Do not infer video overlay text unless it is actually visible or available in public metadata.
- Do not invent external links mentioned by a post.

## Useful public metadata sources

In browser context, social pages may expose useful metadata in:

```js
Array.from(document.querySelectorAll('meta[property="og:title"], meta[property="og:description"], meta[property="og:url"], meta[name="description"]'))
  .map(m => ({
    name: m.getAttribute('name') || m.getAttribute('property'),
    content: m.content
  }))
```

Some public pages expose post text in `document.title` even when the visible UI is gated. Treat this as public metadata, but still label uncertainty if the full post/comments were not accessible.

## Good uncertainty wording

- `Comments were not publicly visible / not extracted.`
- `The public caption was visible, but the reel/video overlay content could not be verified.`
- `The post references a tool name, but no explicit external URL was visible.`
- `Engagement counts are omitted because they were not reliably visible during extraction.`

## External links

If a social post names a GitHub repo, product domain, or paper, verify the target with web extraction before summarizing. If only a name is visible and no URL can be confirmed, say so.
