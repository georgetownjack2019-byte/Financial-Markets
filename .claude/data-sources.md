# Market data sources — access test

Run `python scripts/test_data_sources.py [SYMBOL ...]` to re-test both sources.
Last run: 2 Sep 2026, from a Claude Code on the web remote environment.

| Source | Key needed | Status from the web environment |
|---|---|---|
| Financial Modeling Prep | `FMP_API_KEY` | **Working** — all report endpoints reachable |
| yfinance / Yahoo Finance | none | **Blocked** — Yahoo returns HTTP 429 to this egress IP |

## 1 · Financial Modeling Prep — working

The key in `FMP_API_KEY` authenticates and returns live data. Both
`financialmodelingprep.com` and `api.financialmodelingprep.com` work.

**Use the `/stable/` base path.** The old `/api/v3/` path is retired and returns
HTTP 403 for this key:

> Legacy Endpoint: Due to Legacy endpoints being no longer supported — this
> endpoint is only available for legacy users who have valid subscriptions prior
> August 31, 2025.

Base URL: `https://financialmodelingprep.com/stable`

Endpoints confirmed reachable (HTTP 200):

| Endpoint | Params | Covers |
|---|---|---|
| `quote`, `quote-short` | `symbol` | last price, change %, volume, day/52w range, market cap |
| `profile` | `symbol` | company, sector, beta, dividend |
| `search-symbol` | `query` | symbol lookup |
| `historical-price-eod/light` | `symbol`, `from`, `to` | close + volume series |
| `historical-price-eod/full` | `symbol`, `from`, `to` | OHLCV — use for MA / RSI / ATR |
| `historical-chart/1hour` | `symbol` | intraday bars |
| `income-statement` | `symbol`, `limit` | fundamentals |
| `key-metrics-ttm`, `ratios-ttm` | `symbol` | valuation ratios |
| `price-target-consensus` | `symbol` | consensus target, high/low |
| `grades-consensus` | `symbol` | analyst buy/hold/sell spread |
| `analyst-estimates` | `symbol`, **`period`** (`annual`/`quarter`) | forward estimates |
| `earnings-calendar` | `symbol` | earnings dates |
| `dividends` | `symbol` | dividend history |
| `treasury-rates` | — | yield curve |
| `economic-indicators` | `name` (e.g. `GDP`) | macro series |
| `news/stock-latest` | `page`, `limit` | headlines |

Index, crypto and FX symbols resolve through `quote`: `^GSPC`, `^VIX`,
`BTCUSD`, `EURUSD`.

Not available on the current plan (HTTP 402 `Restricted Endpoint`):

- `batch-quote-short` — request symbols one at a time instead.

`analyst-estimates` returns HTTP 400 without a `period` parameter.

## 2 · yfinance — blocked from the web environment

yfinance imports and installs fine (`pip install yfinance`), but Yahoo rejects
this environment's shared egress IP with HTTP 429. Measured over a 7-minute
probe at 20-second intervals: **4 of 20 requests succeeded (20%)**; a later
6-request probe returned 0 of 6. This is Yahoo IP-throttling a datacenter
range, not a code or credential problem — there is no key to fix.

`yfinance.Ticker.history()` needs three sequential Yahoo calls (cookie/crumb,
timezone, chart) and raises `YFRateLimitError` if any one 429s, so at a ~20%
per-request success rate it effectively never completes, even with eight
retries and capped backoff.

Two further environment-specific notes, both already handled in the test script:

- yfinance ≥ 1.7 defaults to a `curl_cffi` session with TLS fingerprint
  impersonation, which the environment's intercepting proxy resets
  (`SSLError: Recv failure: Connection reset by peer`). Passing a plain
  `requests.Session` to `yf.Ticker(..., session=...)` avoids this and is the
  only reason the 429 is visible at all.
- Yahoo needs a browser-like `User-Agent`; the default `curl` UA is refused.

### What this means for the report commands

`/morning-briefing`, `/daily-recap`, `/crypto-levels` and `/targets-consensus`
all specify yfinance for price history. **They cannot get prices from yfinance
in a web session.** Either run those commands from local Claude Code, where the
residential IP is not throttled, or port them to the FMP endpoints above —
`historical-price-eod/full` supplies the OHLCV that the MA / RSI / ATR
calculations need, and `price-target-consensus` plus `grades-consensus` supply
the analyst data.
