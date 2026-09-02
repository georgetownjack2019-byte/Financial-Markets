---
description: Generate and push the Morning Entry Briefing (traffic-light watchlist) to Notion
argument-hint: [optional — watchlist subset, or "intraday" for a mid-session refresh]
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ☀️ Morning Entry Briefing

Generate today's pre-open entry briefing over the full watchlist, then push it
to Notion.

Read `.claude/watchlist.md` for the names, `.claude/data-sources.md` for which
provider serves which field, and `.claude/notion-push-rules.md` for the
destination, formatting and data-integrity rules. All three are binding.

Scope override (if given): `$ARGUMENTS`

## Title & icon

- Title: `☀️ Morning Entry Briefing — <Ddd DD Mon YYYY>` (e.g. `Wed 02 Sep 2026`)
- Icon: `☀️`
- Intraday refresh → append `(real-time)` to the title.

## 1 · Data

Bootstrap once: `pip install -q yfinance pandas numpy` if the imports fail —
yfinance is the fallback path, not the primary one.

**Primary fetch is FMP** (`.claude/data-sources.md` is binding on which endpoint
serves which field): `quote` for the live line, `historical-price-eod/full` over
~18 months for the bar series (at least 250 sessions so the 200-MA is real),
`price-target-consensus` + `grades-consensus` + `ratings-snapshot` for the
analyst block, and the three calendar endpoints once each for §5. The three
European names (`MC.PA`, `RMS.PA`, `SHELL.AS`) and any failed call fall back to
yfinance per name. Derive, per name:

- Last price, previous close, today's open.
- MA20 / MA50 / MA200 (simple, daily close) → `vs20MA`, `vs50MA`, `vs200MA` as
  signed % of last price against each. FMP's `quote` carries `priceAvg50` and
  `priceAvg200` directly; compute MA20 from the bar series. If a quote average
  and the series disagree by more than 1%, trust the series.
- RSI(14), Wilder smoothing.
- ATR(14) as % of price.
- Volume vs 20-day average volume → `Vol/20d` as `1.16x`.
- Candle direction: `up` if close > open, else `down`.
- Stack: `bull` if price > MA50 > MA200, `bear` if price < MA50 < MA200, else `mixed`.
- Analyst data: consensus target, target low, target high, number of analysts —
  `price-target-consensus` for the three levels, `grades-consensus` for the
  analyst count and the buy/hold/sell split.
- `Dip-buy` = the recent swing-low support level (20-day low lifted by ~0.3×ATR).
- `MoS (−30%)` = consensus target × 0.70 — the margin-of-safety price.
- `Tgt hit%` = share of the trailing analyst targets that were actually reached
  within their horizon, with the sample size in parentheses: `31% (13)`.
  Fewer than 5 observations → mark with `*` (e.g. `100%* (2)`) so a thin sample
  is never read as a strong signal. No history → `n/a`.

Label the sources per `.claude/data-sources.md`: FMP for most names, Yahoo
(~15-min delayed) for the European names and any fallback. Never present the
page as real-time, and never mix providers inside one derived figure — an MA,
an RSI or an ATR comes from one provider's bar series end to end.

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

The backdrop block is mixed-source: FMP serves `^GSPC`, `^IXIC`, `^DJI`,
`^N225`, `^HSI`, `^VIX` and the E-mini S&P (`ESUSD`); yfinance serves Shanghai
(`000001.SS`), the Nasdaq future, the 10Y (`^TNX`) and DXY (`DX-Y.NYB`), none of
which this FMP plan carries. Follow the block with the italic line:
`_Backdrop: US, Japan, HK and S&P futures via FMP; Shanghai, Nasdaq futures, 10Y and DXY via Yahoo Finance (~15-min delayed). NOT real-time._`

## 3 · Master table

One row per watchlist name, these 17 columns in this order:

`Ticker · Price · Dip-buy · MoS (−30%) · Tgt Low · Consensus · Tgt High ·
Tgt hit% · vs20MA · vs50MA · vs200MA · RSI · ATR% (14d) · Candle · Stack ·
Vol/20d · Light`

Sort GREEN first, then YELLOW, then RED; within a light, by price descending.

Mark a yfinance-sourced row with `†` after the ticker, and a price the two
providers disagree on by more than 2% with `‡`, defining both markers under the
table. Both markers are specified in `.claude/data-sources.md`.

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
- _data: <FMP | Yahoo (~15-min delayed)> · news: <headline 1 (source)> ; <headline 2 (source)>_
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

Per `.claude/notion-push-rules.md`. Close the page with the source footer from
`.claude/data-sources.md` (providers, the fallback tickers, and the as-of
timestamp) above the standard disclaimer.

Report the title, the URL, and the one-line provider tally:
`FMP <n> · yfinance <n> (<n> EU + <n> fallback) · failed <n>`.
