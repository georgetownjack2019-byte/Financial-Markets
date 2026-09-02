---
description: Generate and push the Morning Entry Briefing (traffic-light watchlist) to Notion
argument-hint: [optional — watchlist subset, or "intraday" for a mid-session refresh]
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ☀️ Morning Entry Briefing

Generate today's pre-open entry briefing over the full watchlist, then push it
to Notion.

Read `.claude/watchlist.md` for the names and `.claude/notion-push-rules.md`
for the destination, formatting and data-integrity rules. Both are binding.

Scope override (if given): `$ARGUMENTS`

## Title & icon

- Title: `☀️ Morning Entry Briefing — <Ddd DD Mon YYYY>` (e.g. `Wed 02 Sep 2026`)
- Icon: `☀️`
- Intraday refresh → append `(real-time)` to the title.

## 1 · Data

All numbers come from the shared real-time layer, `scripts/market_data.py`
(Financial Modeling Prep, keyed by `FMP_API_KEY`). No stdlib-external
dependency is required; `yfinance` is optional and only used as a fallback.

```bash
python3 scripts/market_data.py watchlist --out out/watchlist.json
python3 scripts/market_data.py backdrop  --out out/backdrop.json
python3 scripts/market_data.py calendar --days 90 --out out/calendar.json
```

Each watchlist row already carries, computed off 3 years of daily bars with the
live print spliced in as today's in-progress bar:

- `price`, `open`, `previous_close`, `day_high`, `day_low`, `change_pct`, `volume`.
- `ma20` / `ma50` / `ma200` and `vs20ma` / `vs50ma` / `vs200ma` as signed % of
  price against each.
- `rsi14` (Wilder), `atr14` and `atr_pct`.
- `vol_ratio` → render as `1.16x`.
- `candle` (`up` / `down`), `stack` (`bull` / `bear` / `mixed`).
- `target_low` / `target_consensus` / `target_high`, `rating`, `analysts`.
- `dip_buy` — 20-day low lifted by 0.3×ATR.
- `mos_30` — consensus × 0.70, the margin-of-safety price.
- `hit_pct` / `sample` — the share of analyst targets actually reached inside a
  365-day horizon, scored only on targets whose horizon has fully elapsed.
  Render as `31% (13)`; fewer than 5 observations gets a `*` (`100%* (2)`) so a
  thin sample is never read as a strong signal; `hit_pct: null` renders `n/a`.
- `source` — the provenance of that row (see below).
- `currency` — `USD` or `EUR`. Print the native symbol; never convert.

### Sourcing and honesty

`source` is one of three values and the page must reflect which one it was:

| `source` | Meaning | How to label the row |
|---|---|---|
| `FMP real-time` | live quote | no marker |
| `yfinance (~15-min delayed)` | native listing, delayed | mark the row `†` |
| `FMP real-time (ADR proxy)` | US ADR standing in for a listing FMP's plan does not cover — `proxy_symbol` names it, price is USD | mark the row `‡` and name the proxy in the footnote |

Footnote whichever markers appear, e.g.
`_† ~15-min delayed. ‡ US ADR proxy in USD (MC.PA → LVMUY) — FMP's plan does not quote the Paris/Amsterdam lines._`

A field that resolved to nothing arrives as `null` — print `—`. Never
substitute, extrapolate or carry a value over from a previous day's page. If
`unresolved` in the JSON exceeds 20% of the watchlist, stop and report the
failure instead of publishing.

## 2 · Backdrop block

Open the page with a `>` quote block, exactly these five lines:

```
> **Backdrop: <mixed / neutral | risk-on | risk-off>.**
> US prior close — S&P 500 <lvl> (<±%>) · Nasdaq <lvl> (<±%>) · Dow <lvl> (<±%>).
> Asia overnight — Nikkei <lvl> (<±%>) · Hang Seng <lvl> (<±%>) · Shanghai <lvl> (<±%>).
> US futures — S&P fut <lvl> (<±%>) · Nasdaq fut <lvl> (<±%>).
> Rates & risk — 10Y <x.xx%> · DXY <lvl> · VIX <lvl> (<low|moderate|elevated>).
> **Sentiment backdrop:** HY credit spread <n> bps.
```

Fill it from `out/backdrop.json`. Three of those fields need care:

- `nasdaq_futures` has no series on this FMP plan — print `—`, do not
  substitute QQQ.
- `shanghai` and `dxy` fall back to a proxy (`ASHR`, `UUP`). When
  `proxy: true`, name it inline: `Shanghai (ASHR proxy) <lvl> (<±%>)`.
- `hy_spread_bps` has no OAS series on this plan — print `—`. Never estimate it.

Then the italic line, with the real timestamp from `as_of` converted to
Eastern: `_Prices real-time via Financial Modeling Prep, as of <HH:MM ET, DD Mon YYYY>._`

## 3 · Master table

One row per watchlist name, these 17 columns in this order:

`Ticker · Price · Dip-buy · MoS (−30%) · Tgt Low · Consensus · Tgt High ·
Tgt hit% · vs20MA · vs50MA · vs200MA · RSI · ATR% (14d) · Candle · Stack ·
Vol/20d · Light`

Sort GREEN first, then YELLOW, then RED; within a light, by price descending.

## 4 · Traffic light

Assign per the decision rule:

- 🟢 **GREEN** — uptrend *and* a trigger: PULLBACK to the 20/50-MA with RSI
  ~40–55, or BREAKOUT above a base on above-average volume.
- 🟡 **YELLOW** — wanted, but extended (don't chase) or no trigger yet.
- 🔴 **RED** — below the 200-MA. Stand aside until it bases.

Then `### 🟢 GREEN`, `### 🟡 YELLOW`, `### 🔴 RED` sections. Every GREEN name
gets four bullets:

```
- **<TICKER> \$<price>** — **<PULLBACK|BREAKOUT> setup** — <2–3 sentences: where it sits
  vs its MAs with the actual level, RSI and what it means, ATR/volatility and stop
  implication, MA stack. Add "⚠️ Analyst targets have historically overshot — discount
  them (<hit%>, n=<N>)." when hit% < 50%.>
- **Dip-buy zone \~\$<x>** · buy zone \$<lo>–\$<hi> · stop below \$<stop>
- _Sentiment: <Bullish|Neutral|Bearish> · <rating> · <±n>% PT · rev +<u>/−<d> · insider B<n>/S<n> · P/C <x.xx> · IV <n>%_
- _data: FMP real-time <HH:MM ET> · news: <headline 1 (source)> ; <headline 2 (source)>_
```

YELLOW gets the first bullet plus the level it needs to trigger. RED gets one
line: why it's out and what would put it back in play.

## 5 · Remaining sections

- `## 📊 Valuation snapshot (sorted by analyst-target reliability)` — table:
  `Ticker · Price · Dip-buy · MoS · Consensus (upside) · High tgt (upside) · Tgt hit%`,
  sorted by `Tgt hit%` descending.
- `## 📅 Major Event Calendar (next 90 days · all IBKR names)` — table:
  `Date · In · Ticker · Name · Event`. `Date` as `Wed 02 Sep`, `In` as `+0d`,
  event as `📊 Earnings` / `💵 Ex-dividend` / `🏛️ Macro`. Chronological.
- `## 🌐 Macro Event → Stock Impact (how each release moves the watchlist)` —
  table: `Release · Names it moves · Typical first-order reaction`. Cover CPI/PCE,
  Fed/FOMC, jobs (NFP, claims, ADP), retail sales/UMich, GDP & ISM/PMI, oil
  (EIA, OPEC+), 10Y/auctions/DXY. Close with
  `_Reference map — the typical first-order reaction, not a forecast; confirm the day's release times on the calendar._`
- `## Decision rule (Part 4)` — the three light definitions verbatim as bullets.
- Final line: `**Verdict: <n> actionable · <n> on alert · <n> stand-aside.**`

## 6 · Push

Per `.claude/notion-push-rules.md`. Report the title and URL.
