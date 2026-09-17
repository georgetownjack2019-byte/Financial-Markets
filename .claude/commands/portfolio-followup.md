---
description: Generate and push the Portfolio Follow-up — recap, sentiment and target consensus for held and candidate names only
argument-hint: [optional — a ticker subset, e.g. "CRCL ORCL", or "held" / "candidates"]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# 💼 Portfolio Follow-up

One page covering the whole position book: what moved, what the sell side
thinks, and where consensus sits — for held names and declared candidates only,
not the full watchlist.

Read `.claude/portfolio.md` for the names, tiers and cost basis, and
`.claude/notion-push-rules.md` for destination, formatting and data-integrity
rules. Both are binding. `.claude/watchlist.md` is **not** used here.

Scope override (if given): `$ARGUMENTS`

## Title & icon

- Title: `💼 Portfolio Follow-up — <Ddd DD Mon YYYY>`
- Icon: `💼`
- If a page with that title already exists for the day, append `(update 2)`,
  `(intraday)` etc. per the push rules — do not overwrite.

## 1 · Data

FMP `/stable`, key from `FMP_API_KEY`. Per name fetch: `quote`,
`historical-price-eod/full`, `price-target-consensus`, `price-target-summary`,
`grades-consensus`, `grades`, `news/stock`.

Day-over-day change is computed from **consecutive closes**. The provider's EOD
`change` field measures open-to-close and must not be used.

State the as-of timestamp, and whether the market was open or closed at read
time, in the footer.

## 2 · Sections, in this order

### `## 1 · Position ledger`

Held names only. Columns:

`Ticker · Shares · Avg cost · Price · Chg % · P&L $ · vs breakeven % · Breakeven price`

Then a **TOTAL** row: cost, market value, unrealised P&L, and P&L as % of cost.
Candidates appear in a second short table with `—` in every P&L cell.

Report the loss as it is. Never net a loss against an unrealised gain elsewhere
to soften the total, and never omit a losing row.

### `## 2 · Daily recap`

One table for all names: `Price · Day % · Vol vs 20d · 5d · ~1m · ~3m · 52w range`.

Then one short paragraph per name: what moved it, the level it closed against
(20d / 50d / 100d SMA), and its ATR(14) as % of price. Name the catalyst or say
"no company-specific news; moved with <sector/factor>".

### `## 3 · Sentiment`

Table: `Strong Buy · Buy · Hold · Sell · n · Bullish %`, sorted by bullish share.

Then **recent rating actions** per name — date, firm, previous → new, action.
Call out explicitly when every recent action is `maintain`: a frozen sell side
through a live catalyst is itself the signal, and should be stated rather than
passed over as "no change".

Flag any name where a major house sits on the opposite side of consensus
(an Underweight/Underperform against a Buy consensus) — that split is what
drives the daily range.

### `## 4 · Target consensus`

Table: `Spot · Consensus · Median · Low · High · Upside to consensus`.

Then the **revision-momentum** table, which is the part that carries the signal:

`Last month avg · Last quarter avg · Last year avg · All-time avg · Direction`

Rules for reading it:
- A consensus **above** the last-month average is **stale** — it is averaging in
  older, higher targets. Say so, and quote the recent figure as the live one.
- A last-month average **below spot** means the sell side now marks the name
  above fair value. State that plainly even when the headline upside is positive.
- A target **low** above spot means every contributing analyst is above the
  price. Worth naming when it happens; note that unanimity is its own risk.

### `## 5 · Levels to watch`

Per name: the nearest support and resistance from 20d/50d/100d/200d SMAs and
recent swing highs/lows, plus ATR(14). For held names add the breakeven price
and where it sits relative to those levels.

Levels only — conditional statements ("above X → Y"), never predictions.

### `## 6 · Since last run`

Fetch the previous `💼 Portfolio Follow-up` page from the parent and diff:
price, P&L, consensus, bullish share, and any rating action since. First ever
run → state that no prior page was found and skip the section.

## 3 · Push

Per `.claude/notion-push-rules.md`. Report the title and URL. Nothing else.
