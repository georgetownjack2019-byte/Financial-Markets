---
description: Push the day's briefing/report to the DAILY BRIEFINGS page in Notion
argument-hint: [what to push — defaults to the briefing produced in this session]
allowed-tools: mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page, mcp__Notion__notion-search
---

# Push Daily

Publish today's briefing to Notion as a new sub-page of **DAILY BRIEFINGS**.

## Target

- **Parent page:** `DAILY BRIEFINGS`
- **Page ID:** `3cf9de12-4ade-8005-8cd6-d023cb6fa071`
- **URL:** https://www.notion.so/3cf9de124ade80058cd6d023cb6fa071
- **Location:** `Investment Research 投研报告 / DAILY BRIEFINGS`

Always create a **new child page** under this parent. Never overwrite the parent
page itself, and never overwrite an existing child unless I explicitly say to
update a specific dated briefing.

## What to push

`$ARGUMENTS`

If no arguments are given, push the briefing / research note / recap that was
produced in this session. If nothing like that exists yet, say so and stop —
do not invent content.

## Steps

1. Determine today's date (use the real current date, not a cached one).
2. Build the page title in this format, matching the existing convention:
   - Morning briefing → `☀️ Morning Entry Briefing — <Ddd DD Mon YYYY>`
   - End-of-day recap → `🗓️ Daily Recap and Forward Outlook — <Ddd DD Mon YYYY>`
   - Crypto levels → `₿ Crypto Levels — <Ddd DD Mon YYYY>`
   - Anything else → `<emoji> <Topic> — <Ddd DD Mon YYYY>`

   Example: `☀️ Morning Entry Briefing — Wed 02 Sep 2026`
3. Call `notion-fetch` on the parent page id above to confirm it exists and to
   check whether a page with that exact title already exists for today.
   - If it exists and I asked for an update → update that page.
   - If it exists and I did not → append a short qualifier to the new title
     (e.g. `(update 2)`, `(real-time)`) rather than clobbering it.
4. Create the page with `notion-create-pages`, using
   `parent: { type: "page_id", page_id: "3cf9de124ade80058cd6d023cb6fa071" }`.
5. Set a matching page icon (☀️ / 🗓️ / ₿ / 📊).

## Content rules

- Write the body in Notion-flavored Markdown: `##` section headings, tables for
  levels/targets, bullets for theses. No H1 — the title is the page title.
- Keep every number that was in the source material; do not round or re-derive.
- Preserve ticker symbols, price levels, and dates exactly as produced.
- End the page with a one-line source/timestamp footer, e.g.
  `_Generated <date/time>, data as of <as-of>._`
- Add the standard disclaimer when the content contains price levels or
  entry plans: this is research, not personalized investment advice.

## After pushing

Report back the created page title and its Notion URL. Nothing else.
