---
description: Generate and push the Targets & Consensus sheet for the full watchlist to Notion
argument-hint: [optional — a single group, e.g. "Semi", or a ticker subset]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page, mcp__Notion__notion-create-file-upload, mcp__Notion__notion-create-attachment
---

# 📊 Targets & Consensus

Analyst price targets and valuation anchors across the whole watchlist, grouped
by theme, with two summary charts. Push to Notion.

Read `.claude/watchlist.md` for the names and groups, and
`.claude/notion-push-rules.md` for destination, formatting and data-integrity
rules. Both are binding.

Scope override (if given): `$ARGUMENTS`

## Title & icon

- Title: `📊 Targets & Consensus — complete watchlists <DDMM> — <Ddd DD Mon YYYY>`
  (the `<DDMM>` tag matches the watchlist snapshot, e.g. `3108`)
- Icon: `📊`
- Intro line: `Analyst price targets, consensus upside, fair-value estimate, dip-buy level, target hit-rate and ATR for the <n>-name **complete watchlists <DDMM>**. Prices/targets via yfinance, <DD Mon YYYY>. Not advice.`

## 1 · Data

Bootstrap: `pip install -q yfinance pandas numpy matplotlib` if imports fail.

Per name:
- `Price` — last close, native currency (€ for MC.PA / RMS.PA / SHELL.AS).
- `Consensus` — mean analyst target.
- `Upside` — signed % from price to consensus.
- `Tgt High` — highest analyst target.
- `Fair val` — DCF/analyst fair-value estimate. Unavailable → `—`.
- `Dip-buy` — 20-day low lifted by ~0.3×ATR. Above the current price → `—`.
- `Hit%` — historical target hit-rate; thin/no history → `—`.
- `ATR%` — ATR(14) as % of price.
- `#An` — number of contributing analysts.

Keep a negative upside negative (`-24.0%`) — a consensus below spot is a
signal, not an error to correct. A nonsensical fair value (e.g. negative)
prints as computed; do not silently suppress it.

## 2 · Charts

Two matplotlib PNGs, uploaded and embedded at the top of the page, in order:

1. `Upside to consensus target, all <n> names` — horizontal bar, sorted
   descending by upside, name labels legible, zero line marked.
2. `Average upside to consensus by group` — bar chart, one bar per watchlist
   group, sorted descending.

Both: no chartjunk, direct value labels, colourblind-safe palette, readable at
Notion's inline width. Upload with `notion-create-file-upload` +
`notion-create-attachment`, then reference them as image blocks with those
captions.

## 3 · Tables

One `##` section per watchlist group, in the order they appear in
`.claude/watchlist.md`, each with the same 10 columns:

`Ticker · Price · Consensus · Upside · Tgt High · Fair val · Dip-buy · Hit% · ATR% · #An`

Bold the ticker (`**MC**`). Sort each group by upside descending. A name in two
groups appears in both with identical figures.

## 4 · Push

Per `.claude/notion-push-rules.md`. Report the title and URL.
