# Shared data sources (referenced by the daily report commands)

Two providers. **FMP is the source of record; yfinance is the fallback and the
history backstop.** Every report command follows this file — do not pick a
provider ad hoc.

## The key

`FMP_API_KEY` comes from the environment. Read it from `os.environ` /
`$FMP_API_KEY` at the moment of the call.

- Never echo it, never `print()` it, never paste it into a shell line that gets
  reported back, never write it into a report or a commit.
- Never pass it as a command argument. If a fetch fails, report the HTTP status
  and the symbol — never the URL with the key in it.

## Base URL and endpoints

`https://financialmodelingprep.com/stable/<endpoint>?<params>&apikey=<key>`

| Need | Endpoint | Fields used |
|---|---|---|
| Quote, prev close, open, volume, 50/200-MA | `quote?symbol=X` | `price`, `previousClose`, `open`, `dayLow`, `dayHigh`, `volume`, `priceAvg50`, `priceAvg200`, `yearHigh`, `yearLow`, `marketCap`, `timestamp` |
| Daily bars for MA20 / RSI / ATR / vol avg | `historical-price-eod/full?symbol=X&from=&to=` | `date`, `open`, `high`, `low`, `close`, `volume`, `vwap` |
| Analyst targets | `price-target-consensus?symbol=X` | `targetHigh`, `targetLow`, `targetConsensus`, `targetMedian` |
| Target history / recency | `price-target-summary?symbol=X` | `lastMonthAvgPriceTarget`, `lastQuarterAvgPriceTarget`, `lastYearAvgPriceTarget`, `allTimeAvgPriceTarget`, and their `*Count` |
| Rating | `ratings-snapshot?symbol=X` | `rating`, `overallScore` |
| Analyst spread (rev +/−) | `grades-consensus?symbol=X` | `strongBuy`, `buy`, `hold`, `sell`, `strongSell`, `consensus` |
| Earnings calendar | `earnings-calendar?from=&to=` | `symbol`, `date`, `epsEstimated` |
| Ex-dividend calendar | `dividends-calendar?from=&to=` | `symbol`, `date`, `dividend`, `yield` |
| Macro calendar | `economic-calendar?from=&to=` | `date`, `country`, `event`, `estimate`, `previous`, `impact` |

The three calendar endpoints return the whole market for the window (1k–2k
rows). Fetch each **once** per report and filter to the watchlist in memory —
do not call them per ticker.

For `historical-price-eod/full`, request ~18 months so at least 250 sessions
survive holidays; a 12-month window returns ~253 rows and leaves no margin.

## Provider split

**FMP for:** last price, previous close, open, volume, 50/200-MA, daily bars,
analyst targets, ratings, grades, and all three calendars.

**yfinance for:**

1. **The three European names FMP will not serve on this plan** — `MC.PA`,
   `RMS.PA`, `SHELL.AS`. FMP returns HTTP 402 (`Premium Query Parameter`) for
   these; that is a plan limit, not a transient error, so do not retry them
   against FMP.
2. **Any FMP call that fails** — non-200, empty array, or a null in a field the
   report needs.
3. **Anything FMP has no endpoint for on this plan** — options-derived IV and
   put/call, index futures, Treasury yields, DXY and WTI. See the table below.

Confirmed available on FMP: the other 65 watchlist symbols, spot crypto
included.

## Indices and cross-asset (verified against this plan)

**On FMP** — use these: `^GSPC`, `^IXIC`, `^DJI`, `^RUT`, `^VIX`; every S&P
sector ETF (`XLE`, `XLK`, `XLF`, `XLV`, `XLY`, `XLP`, `XLI`, `XLB`, `XLRE`,
`XLU`, `XLC`); gold `GCUSD`; Brent `BZUSD`; FX pairs such as `EURUSD`.

Also on FMP, for the morning backdrop block: `^N225` (Nikkei), `^HSI` (Hang
Seng) and `ESUSD` (E-mini S&P future).

**Not on FMP — always yfinance:** Treasury yields (`^TNX`, `^FVX`, `^TYX`), the
dollar index (`DX-Y.NYB`), WTI (`CL=F`), Shanghai (`000001.SS`) and the Nasdaq
future. Do not substitute the ETF proxies (`USO`, `UUP`) for these: they track
the exposure, not the quoted level, and the reports print the level.

## Symbol mapping

| Report ticker | FMP | yfinance |
|---|---|---|
| Bitcoin | `BTCUSD` | `BTC-USD` |
| Ethereum | `ETHUSD` | `ETH-USD` |
| LVMH / Hermès / Shell | *(not served)* | `MC.PA` / `RMS.PA` / `SHELL.AS` |

Everything else uses the same symbol on both. Keep reporting the watchlist's
spelling (`BTC-USD`) in the report itself whatever the fetch used.

## Reconciliation

When both providers return a price for the same name:

- **FMP wins.** Use it for every displayed number and every derived level.
- If the two differ by **more than 2%**, mark that row's price with `‡` and
  footnote it: `‡ FMP and Yahoo disagree by >2% — FMP shown.` A gap that size
  usually means a stale feed or a corporate action, and it should be visible
  rather than silently resolved.
- Never average the two, and never mix them inside one derived figure: an MA,
  an RSI or an ATR is computed from one provider's bar series end to end.

## Labelling — every report

The per-provider timeliness is different, so a page can no longer carry one
blanket Yahoo disclaimer.

- Name the source in the footer of every page, with the as-of timestamp:
  `_Quotes and fundamentals via Financial Modeling Prep, as of <HH:MM TZ>. <n> name(s) via Yahoo Finance (~15-min delayed): <tickers>. Not real-time._`
- If **every** name on a page fell back to yfinance, say so plainly instead and
  keep the old ~15-min-delayed wording.
- Mark yfinance-sourced rows in the master table with `†` after the ticker, and
  define `†` under the table.

## Failure handling

- Retry an FMP call **once** on a 429 or a 5xx, after ~2s. A 402 is a plan
  limit — fall back immediately, no retry.
- Fall back per name, not per report: one dead ticker must not push the whole
  watchlist onto yfinance.
- The existing rule in `notion-push-rules.md` still governs: if more than ~20%
  of the watchlist has no usable data **after** fallback, stop and report the
  failure instead of publishing a half-empty page.
- Report the fallback count in the run summary so a silent provider outage is
  visible: `FMP 63 · yfinance 5 (3 EU + 2 fallback) · failed 0`.

**The fallback is not guaranteed.** Yahoo rate-limits cloud egress: from a Claude
Code environment `yfinance` intermittently returns HTTP 429 on its cookie/crumb
fetch and raises rather than returning bars. Treat that as a data failure, not a
reason to retry in a loop — print `—` for the affected fields, count the name as
failed in the tally, and let the >20% rule stop the run if it spreads. Never
carry yesterday's number forward to paper over it. This is the main reason FMP
is the source of record: the names that *only* yfinance can serve (the three
European ones, yields, DXY, WTI) are the ones at risk on any given morning.
