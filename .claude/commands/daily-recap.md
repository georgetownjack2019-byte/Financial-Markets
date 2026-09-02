---
description: Generate and push the Daily Recap and Forward Outlook to Notion
argument-hint: [optional — the session date to recap, defaults to the last close]
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# 🗓️ Daily Recap and Forward Outlook

Recap the session that just closed, then project the next trading day and the
week ahead. Push to Notion.

Read `.claude/watchlist.md` for the names and `.claude/notion-push-rules.md`
for the destination, formatting and data-integrity rules. Both are binding.

Session override (if given): `$ARGUMENTS`

## Title & icon

- Title: `🗓️ Daily Recap and Forward Outlook — <Ddd DD Mon YYYY>` — the date of
  the session being recapped, not the date you are writing.
- Icon: `🗓️`

## 1 · Data

From the shared real-time layer (`scripts/market_data.py`, FMP-backed):

```bash
python3 scripts/market_data.py watchlist --out out/watchlist.json
python3 scripts/market_data.py backdrop  --out out/backdrop.json
python3 scripts/market_data.py crypto    --out out/crypto.json
python3 scripts/market_data.py calendar --days 10 --out out/calendar.json
python3 scripts/market_data.py watchlist --no-targets \
  --symbols XLE,XLK,XLF,XLV,XLY,XLP,XLI,XLB,XLRE,XLU,XLC,IWM,GLD,USO,BNO \
  --out out/sectors.json
```

- Index board: S&P 500, Nasdaq, Dow (`backdrop.json`), Russell 2000 (`IWM`).
- All 11 S&P sectors — `change_pct` from `sectors.json`, ranked.
- Cross-asset: 10Y and 2Y from `backdrop.json` (`ust10y`, `ust2y` — these are
  Treasury constant-maturity rates, dated; take the bp change against the prior
  session's row), DXY (`UUP` proxy — say so), VIX, gold (`GLD`), oil
  (`USO` / `BNO`), BTC and ETH from `crypto.json`.
- Every watchlist name: `price`, `change_pct`, `vol_ratio` from `watchlist.json`.
- Watchlist earnings and ex-dividends from `calendar.json`.

This is a post-close report, so the live print and the session close are the
same number — but still state the `as_of` timestamp and the source, and carry
through the `†` / `‡` source markers described in `/morning-briefing` §1 for any
row that is delayed or ADR-proxied.

Yields move in **basis points** — report `+80bp to 4.80%`, never `+0.80%`.

## 2 · Sections, in this order

- `## TL;DR` — one paragraph. What happened and the single reason why.
- `## Executive summary` — 4–6 bold-led bullets (`**Broad equities weakness**: …`)
  each carrying its numbers.
- `## Yesterday's tape` — index board narrative, breadth.
- `## Sector rotation` — which sectors led/lagged and the rotation it implies.
- `## Cross-asset & macro` — rates, dollar, commodities, crypto, and the link
  back to equities.
- `## Watchlist movers & why` with `### Top gainers` and `### Top losers` —
  5 each, every mover paired with the actual catalyst. No catalyst found →
  say "no company-specific news; moved with <sector/factor>."
- `## Next trading day — projection`
  - `### Bias: **<RISK-ON | RISK-OFF | NEUTRAL> with <overlay>**`
  - `### Watchlist to monitor <Ddd D Mon>`
  - `### Bull / Base / Bear scenarios for <Ddd D Mon>` — each with a trigger
    level and the index/watchlist consequence.
  - `### Key catalysts (<Ddd D Mon> & near-term)`
- `## The week ahead — projection`
  - `### Dominant themes (Week of <D–D Mon YYYY>)`
  - `### Scheduled catalysts (Week of <D–D Mon>)`
  - `### Sector positioning into week`
  - `### Watchlist sector allocation for week`
- `## 7 · Per-stock brief — why it moved · next day · this week` — every
  watchlist name, three short clauses each.
- `## 📎 Data appendix (raw tables)` with:
  - `## 1 · Index board` + `### Cross-asset`
  - `## 2 · Sector rotation (11 S&P sectors)`
  - `## 3 · Watchlist — every name` + `### Group averages`
  - `## 4 · Biggest movers`
  - `## 5 · News → watchlist (by size of move)`
  - `## 6 · Scheduled events — U.S. calendar (next ~week)` +
    `### Watchlist earnings due (~1 week)` — event table columns:
    `Date · Event · Impact · Forecast · Previous`, missing values as `None`.

Scenarios are conditional on levels, never predictions: "above X → Y". Say
what would falsify the bias.

## 3 · Push

Per `.claude/notion-push-rules.md`. Report the title and URL.
