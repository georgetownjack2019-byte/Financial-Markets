---
description: Generate and push mechanical BTC/ETH Crypto Levels to Notion
argument-hint: [optional — extra tickers, e.g. "SOL-USD"]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ₿ Crypto Levels

Mechanical level sheet for BTC and ETH. Purely rule-driven — no narrative, no
news, no opinion. Push to Notion.

Read `.claude/notion-push-rules.md` for destination, formatting and
data-integrity rules. Binding.

Extra assets (if given): `$ARGUMENTS` — default is `BTC-USD` and `ETH-USD`.

## Title & icon

- Title: `₿ Crypto Levels — <Ddd DD Mon YYYY>`
- Icon: `₿`
- Sub-line, first thing on the page:
  `_Generated <HH:MM> · mechanical levels only, not a recommendation._`

## 1 · Data

Real-time spot and 3 years of daily bars from the shared layer:

```bash
python3 scripts/market_data.py crypto --symbols BTC-USD,ETH-USD --out out/crypto.json
```

Crypto quotes come straight from FMP (`BTC-USD` → `BTCUSD`), so spot is live,
not a delayed close, and `source` on every row reads `FMP real-time`. The rows
carry `price`, `ma20` / `ma50` / `ma200`, `atr14`, `atr_pct`, `dip_buy` and
`sessions`. The 20-week MA and the 7/20-day range are not in the payload —
derive them in the same script run from the daily bars
(`market_data.get_history("BTCUSD")`): the 20-week MA is the mean of the last
100 daily closes' weekly resample, and the range rows are plain min/max over
the trailing 7 and 20 bars.

State the `as_of` timestamp (Eastern) on the page. Crypto trades continuously,
so a level sheet is only meaningful next to the minute it was cut.

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

Per `.claude/notion-push-rules.md`. Report the title and URL.
