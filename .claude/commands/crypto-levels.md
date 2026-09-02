---
description: Generate and push mechanical BTC/ETH Crypto Levels to Notion
argument-hint: [optional — extra tickers, e.g. "SOL-USD"]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ₿ Crypto Levels

Mechanical level sheet for BTC and ETH. Purely rule-driven — no narrative, no
news, no opinion. Push to Notion.

Read `.claude/data-sources.md` for which provider serves which field and
`.claude/notion-push-rules.md` for destination, formatting and data-integrity
rules. Both are binding.

Extra assets (if given): `$ARGUMENTS` — default is `BTC-USD` and `ETH-USD`.

## Title & icon

- Title: `₿ Crypto Levels — <Ddd DD Mon YYYY>`
- Icon: `₿`
- Sub-line, first thing on the page:
  `_Generated <HH:MM> · mechanical levels only, not a recommendation._`

## 1 · Data

Bootstrap: `pip install -q yfinance pandas numpy` if imports fail — yfinance is
the fallback path, not the primary one.

**Primary fetch is FMP**: `quote` for spot and
`historical-price-eod/full` over ~18 months for the bar series — daily bars,
≥250 sessions (200-MA), resampled to weekly for the 20-week MA. FMP spells the
pairs **without the dash** (`BTCUSD`, `ETHUSD`) while this command's arguments
and headings use the watchlist spelling (`BTC-USD`); map on the way in and
report the watchlist spelling.

An extra asset passed in `$ARGUMENTS` that FMP will not serve falls back to
yfinance for that asset only. Crypto trades continuously, so state the exact
as-of timestamp — there is no "close" to lean on.

## 2 · Per asset

Section heading: `## <SYMBOL> — <spot>` (BTC/ETH, thousands separators, no
currency symbol — these are USD pairs).

Under it: `ATR <n> (<n.nn>%) · sits at **<n>%** of the 7-day range`
where range position = (spot − 7d low) / (7d high − 7d low) × 100.

**Indicator table** — `Indicator · Level · Spot vs it`, these rows in order:
MA 20 (daily), MA 50 (daily), MA 200 (daily), MA 20 (weekly), 7-day low,
7-day high, 20-day low, 20-day high. `Spot vs it` is signed % of spot against
the level.

**Gates** — three bullets, ✅ or ❌:
- above 20-week MA
- above MA200
- 180-day momentum positive (spot > close 180 days ago)

**Trade plan** table — ` · Level · vs spot`:

| Row | Formula |
|---|---|
| Entry (7d low + 0.3×ATR) | `7d_low + 0.3×ATR`, **bolded** |
| Entry zone (lower 20–25%) | 7d low + 20% and 25% of the 7-day range |
| Stop (7d low − 0.5×ATR) | `7d_low − 0.5×ATR` |
| Target (entry + 2×ATR) | `entry + 2×ATR` |

**Status** line, one of:
- `**Status: 🟢 ENTRY ZONE LIVE**` — spot is inside the entry zone and all
  three gates pass.
- `**Status: 🟡 WAIT**` — gates pass but spot is outside the entry zone.
- `**Status: 🔴 STAND ASIDE**` — any gate fails.

ATR is 14-period on daily bars. Round BTC/ETH levels to whole units, ATR% and
all vs-spot figures to 2 decimals. Every number is computed — never carried
over from yesterday's page.

## 3 · Push

Per `.claude/notion-push-rules.md`. Close the page with the source footer from
`.claude/data-sources.md` (provider per asset and the as-of timestamp) above the
standard disclaimer.

Report the title, the URL, and the provider used per asset.
