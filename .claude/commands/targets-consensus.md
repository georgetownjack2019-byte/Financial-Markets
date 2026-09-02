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
- Intro line: `Analyst price targets, consensus upside, fair-value estimate, dip-buy level, target hit-rate and ATR for the <n>-name **complete watchlists <DDMM>**. Prices and targets real-time via Financial Modeling Prep, <HH:MM ET, DD Mon YYYY>. Not advice.`

## 1 · Data

```bash
python3 scripts/market_data.py watchlist --out out/watchlist.json
```

`pip install -q matplotlib` for the charts if the import fails; the data layer
itself needs nothing beyond the standard library.

Per name, straight off the row:
- `Price` — `price`, live, in `currency` (€ for MC.PA / RMS.PA / SHELL.AS when
  the native line resolved; a `‡` ADR row is USD — mark it, do not convert).
- `Consensus` — `target_consensus`.
- `Upside` — `consensus_upside`, signed.
- `Tgt High` — `target_high` (`high_upside` for its upside).
- `Fair val` — not on this FMP plan → `—` for every name. Do not substitute
  consensus for it.
- `Dip-buy` — `dip_buy`. Above the current price → `—`.
- `Hit%` — `hit_pct` with `sample`; `null` → `—`.
- `ATR%` — `atr_pct`.
- `#An` — `analysts`.

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
