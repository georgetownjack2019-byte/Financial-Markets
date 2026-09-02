#!/usr/bin/env python3
"""Connectivity test for the two market-data sources: yfinance and FMP.

Usage:
    python scripts/test_data_sources.py [SYMBOL ...]

Requires FMP_API_KEY in the environment (or in a .env file next to the repo root).
Exits non-zero if either source fails.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import requests

FMP_BASE = "https://financialmodelingprep.com/stable"

# Yahoo throttles bursts from datacenter IPs with HTTP 429. A browser-like
# User-Agent plus spacing between calls keeps it happy; yfinance's default
# curl_cffi transport is TLS-fingerprint-impersonated and gets reset by an
# intercepting proxy, so we hand it a plain requests session instead.
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
THROTTLE_SECONDS = 1.5


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def yahoo_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    return session


def with_retries(fn, attempts: int = 8, base_delay: float = 6.0, max_delay: float = 45.0):
    """Retry through Yahoo's throttle with capped exponential backoff.

    Yahoo 429s most requests from datacenter IPs; measured success rate from this
    environment is roughly 1 in 5, so a few attempts is not enough to get through.
    """
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller below
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(min(base_delay * (2**attempt), max_delay))
    raise last_error  # type: ignore[misc]


def test_yfinance(symbols: list[str]) -> bool:
    print("=" * 60)
    print("1. yfinance (Yahoo Finance — no API key)")
    print("=" * 60)
    try:
        import yfinance as yf
    except ImportError:
        print("  FAIL: yfinance not installed (pip install yfinance)")
        return False

    session = yahoo_session()
    ok = True
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol, session=session)
            history = with_retries(lambda: ticker.history(period="5d", auto_adjust=True))
            if history.empty:
                print(f"  {symbol:9} FAIL: empty history")
                ok = False
                continue
            last = history.iloc[-1]
            date = history.index[-1].date()
            print(
                f"  {symbol:9} OK  {date}  close={last['Close']:.2f}  "
                f"volume={int(last['Volume']):,}  rows={len(history)}"
            )
        except Exception as exc:  # noqa: BLE001 - diagnostic output
            print(f"  {symbol:9} FAIL: {type(exc).__name__}: {str(exc)[:120]}")
            ok = False
        time.sleep(THROTTLE_SECONDS)
    return ok


def test_fmp(symbols: list[str]) -> bool:
    print()
    print("=" * 60)
    print("2. Financial Modeling Prep (API key)")
    print("=" * 60)
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        print("  FAIL: FMP_API_KEY is not set (copy .env.example to .env)")
        return False
    print(f"  key: {api_key[:4]}...{api_key[-4:]} ({len(api_key)} chars)")

    ok = True
    for symbol in symbols:
        try:
            response = requests.get(
                f"{FMP_BASE}/quote",
                params={"symbol": symbol, "apikey": api_key},
                timeout=25,
            )
            if response.status_code != 200:
                print(f"  {symbol:9} FAIL: HTTP {response.status_code} {response.text[:160]}")
                ok = False
                continue
            payload = response.json()
            if not payload:
                print(f"  {symbol:9} FAIL: empty payload (unknown symbol or plan limit)")
                ok = False
                continue
            quote = payload[0]
            print(
                f"  {symbol:9} OK  price={quote.get('price')}  "
                f"change={quote.get('changePercentage'):+.2f}%  "
                f"volume={quote.get('volume'):,}  ({quote.get('name')})"
            )
        except Exception as exc:  # noqa: BLE001 - diagnostic output
            print(f"  {symbol:9} FAIL: {type(exc).__name__}: {str(exc)[:120]}")
            ok = False

    # Confirm which endpoint families this key can reach.
    print("\n  endpoint check:")
    endpoints = {
        "quote": {"symbol": "AAPL"},
        "quote-short": {"symbol": "AAPL"},
        "profile": {"symbol": "AAPL"},
        "search-symbol": {"query": "AAPL"},
        "historical-price-eod/light": {"symbol": "AAPL"},
        "historical-price-eod/full": {"symbol": "AAPL"},
        "historical-chart/1hour": {"symbol": "AAPL"},
        "income-statement": {"symbol": "AAPL", "limit": 1},
        "key-metrics-ttm": {"symbol": "AAPL"},
        "ratios-ttm": {"symbol": "AAPL"},
        "price-target-consensus": {"symbol": "AAPL"},
        "grades-consensus": {"symbol": "AAPL"},
        "analyst-estimates": {"symbol": "AAPL", "period": "annual", "limit": 1},
        "earnings-calendar": {"symbol": "AAPL"},
        "dividends": {"symbol": "AAPL", "limit": 1},
        "treasury-rates": {},
        "economic-indicators": {"name": "GDP"},
        "news/stock-latest": {"page": 0, "limit": 1},
        # Known to be outside the current plan — reported, not counted as failure.
        "batch-quote-short": {"symbols": "AAPL,MSFT"},
    }
    for endpoint, params in endpoints.items():
        try:
            response = requests.get(
                f"{FMP_BASE}/{endpoint}",
                params={**params, "apikey": api_key},
                timeout=30,
            )
        except Exception as exc:  # noqa: BLE001 - diagnostic output
            print(f"    FAIL {endpoint:28} {type(exc).__name__}: {str(exc)[:80]}")
            continue
        if response.status_code == 200:
            label = "OK  "
            note = ""
        elif response.status_code == 402:
            label = "PLAN"  # restricted by subscription tier, not a broken key
            note = "  restricted by subscription tier"
        else:
            label = "FAIL"
            note = f"  {response.text[:100]}"
        print(f"    {label} {endpoint:28} HTTP {response.status_code}{note}")
    return ok


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    symbols = sys.argv[1:] or ["AAPL", "SPY", "^VIX"]

    yf_ok = test_yfinance(symbols)
    fmp_symbols = [s for s in symbols if not s.startswith("^")]
    fmp_ok = test_fmp(fmp_symbols or ["AAPL"])

    print()
    print("=" * 60)
    print(f"  yfinance: {'PASS' if yf_ok else 'FAIL'}")
    print(f"  FMP:      {'PASS' if fmp_ok else 'FAIL'}")
    print("=" * 60)
    return 0 if (yf_ok and fmp_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
