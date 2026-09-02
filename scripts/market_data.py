#!/usr/bin/env python3
"""Shared real-time market data layer for the daily report commands.

Primary source is Financial Modeling Prep (real-time quotes, keyed by
FMP_API_KEY). Where FMP's plan does not cover a listing, the fetcher falls
back — in this order — to yfinance on the native listing (~15-min delayed),
then to the US-listed ADR on FMP. Every row carries the source that produced
it so a report can label delayed or proxied numbers honestly, and any field
that resolves to nothing stays None so the report can print an em dash rather
than a guess.

Subcommands:
    watchlist [--group G] [--symbols A,B] [--out FILE]
    backdrop  [--out FILE]
    crypto    [--symbols BTCUSD,ETHUSD] [--out FILE]
    calendar  [--days 90] [--out FILE]
    selftest
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

FMP_BASE = "https://financialmodelingprep.com/stable"
REPO_ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_FILE = REPO_ROOT / ".claude" / "watchlist.md"

SOURCE_REALTIME = "FMP real-time"
SOURCE_DELAYED = "yfinance (~15-min delayed)"
SOURCE_PROXY = "FMP real-time (ADR proxy)"

# Listings FMP's plan refuses (HTTP 402). Native listing is tried first; the
# ADR is the last resort and is reported in USD, flagged as a proxy.
ADR_PROXY = {
    "MC.PA": "LVMUY",
    "RMS.PA": "HESAY",
    "SHELL.AS": "SHEL",
}
CURRENCY = {"MC.PA": "EUR", "RMS.PA": "EUR", "SHELL.AS": "EUR"}

MAX_WORKERS = 6
HTTP_RETRIES = 5

# FMP meters by requests per minute. Spacing every call keeps a 67-name pull
# under the cap instead of tripping 429 a third of the way through and losing
# the whole run. Override with FMP_RATE_LIMIT when the plan allows more.
RATE_LIMIT_PER_MIN = int(os.environ.get("FMP_RATE_LIMIT", "240"))
_rate_lock = threading.Lock()
_next_slot = 0.0

# Yahoo is unreachable from some environments (the web sandbox blocks it). One
# failure is enough to know it — skip the fallback for the rest of the run
# rather than paying the timeout on every name.
_YF_UNREACHABLE = False


class DataError(RuntimeError):
    pass


def api_key() -> str:
    key = os.environ.get("FMP_API_KEY", "").strip()
    if not key:
        raise DataError(
            "FMP_API_KEY is not set. See .claude/README.md — put it in .env, "
            "in .claude/settings.local.json, or on the web environment."
        )
    return key


def _throttle() -> None:
    """Space requests so concurrent workers share one rate budget."""
    global _next_slot
    interval = 60.0 / max(RATE_LIMIT_PER_MIN, 1)
    with _rate_lock:
        now = time.monotonic()
        wait = max(0.0, _next_slot - now)
        _next_slot = max(now, _next_slot) + interval
    if wait:
        time.sleep(wait)


def fmp(path: str, **params) -> list | dict | None:
    """GET an FMP endpoint. Returns None when the plan does not cover it."""
    params["apikey"] = api_key()
    url = f"{FMP_BASE}/{path}?" + urllib.parse.urlencode(params)
    delay = 2.0
    for attempt in range(HTTP_RETRIES):
        _throttle()
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 402:  # not on this subscription
                return None
            if exc.code == 429 and attempt < HTTP_RETRIES - 1:
                time.sleep(delay)
                delay = min(delay * 2, 60.0)
                continue
            if attempt == HTTP_RETRIES - 1:
                raise DataError(f"{path}: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt == HTTP_RETRIES - 1:
                raise DataError(f"{path}: {exc}") from exc
            time.sleep(delay)
            delay *= 2
    return None


def redact(text: str) -> str:
    """Strip the API key from anything that might reach a page or a log."""
    key = os.environ.get("FMP_API_KEY", "")
    return text.replace(key, "***") if key else text


# ---------------------------------------------------------------- watchlist

def parse_watchlist(path: Path = WATCHLIST_FILE) -> dict[str, list[str]]:
    """Return {group heading: [tickers]} in the order the file lists them."""
    groups: dict[str, list[str]] = {}
    current = None
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            current = None if heading == "Notes" else heading
            if current:
                groups[current] = []
            continue
        if current is None or not line.strip():
            continue
        for token in line.replace("·", " ").split():
            token = token.strip()
            if re.fullmatch(r"[A-Z0-9.\-]{1,12}", token):
                if token not in groups[current]:
                    groups[current].append(token)
    return groups


def equity_symbols(groups: dict[str, list[str]]) -> list[str]:
    """Every equity ticker, de-duplicated, spot crypto excluded."""
    out: list[str] = []
    for heading, tickers in groups.items():
        if "spot" in heading:
            continue
        for t in tickers:
            if t not in out:
                out.append(t)
    return out


# ------------------------------------------------------------------- quotes

def _fmp_quote(symbol: str) -> dict | None:
    data = fmp("quote", symbol=symbol)
    if not data or not isinstance(data, list):
        return None
    q = data[0]
    return q if q.get("price") is not None else None


def _yahoo_reachable() -> bool:
    """One cheap probe per run. yfinance swallows its own network errors and
    just returns an empty frame, which is indistinguishable from a delisting."""
    global _YF_UNREACHABLE
    if _YF_UNREACHABLE:
        return False
    try:
        req = urllib.request.Request(
            "https://query1.finance.yahoo.com/v1/test/getcrumb",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        urllib.request.urlopen(req, timeout=8).read(1)
        return True
    except Exception:
        _YF_UNREACHABLE = True
        return False


def _yf_quote(symbol: str) -> dict | None:
    """Native listing via yfinance. Unavailable when Yahoo is not reachable."""
    global _YF_UNREACHABLE
    if not _yahoo_reachable():
        return None
    try:
        import logging
        import yfinance as yf
        logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    except ImportError:
        return None
    try:
        hist = yf.Ticker(symbol).history(period="5d")
        if hist.empty:
            return None
        last, prev = hist.iloc[-1], hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
        return {
            "symbol": symbol,
            "price": float(last["Close"]),
            "open": float(last["Open"]),
            "dayHigh": float(last["High"]),
            "dayLow": float(last["Low"]),
            "previousClose": float(prev["Close"]),
            "volume": float(last["Volume"]),
            "timestamp": int(last.name.timestamp()),
        }
    except Exception as exc:
        if "curl" in str(exc) or "SSL" in str(exc) or "Connection" in str(exc):
            _YF_UNREACHABLE = True
        return None


def get_quote(symbol: str) -> dict:
    """Live quote with an explicit source. price is None when nothing resolved."""
    base = {
        "symbol": symbol,
        "currency": CURRENCY.get(symbol, "USD"),
        "source": None,
        "proxy_symbol": None,
        "delayed": False,
    }

    q = _fmp_quote(symbol)
    if q:
        return {**base, **_normalise_quote(q), "source": SOURCE_REALTIME}

    q = _yf_quote(symbol)
    if q:
        return {**base, **_normalise_quote(q), "source": SOURCE_DELAYED, "delayed": True}

    proxy = ADR_PROXY.get(symbol)
    if proxy:
        q = _fmp_quote(proxy)
        if q:
            return {
                **base,
                **_normalise_quote(q),
                "currency": "USD",
                "source": SOURCE_PROXY,
                "proxy_symbol": proxy,
                "symbol": symbol,
            }

    return {**base, "price": None, "name": None}


def _normalise_quote(q: dict) -> dict:
    return {
        "name": q.get("name"),
        "price": q.get("price"),
        "open": q.get("open"),
        "previous_close": q.get("previousClose"),
        "day_high": q.get("dayHigh"),
        "day_low": q.get("dayLow"),
        "change_pct": q.get("changePercentage"),
        "volume": q.get("volume"),
        "exchange": q.get("exchange"),
        "year_high": q.get("yearHigh"),
        "year_low": q.get("yearLow"),
        "market_cap": q.get("marketCap"),
        "timestamp": q.get("timestamp"),
    }


# ------------------------------------------------------------------ history

def get_history(symbol: str, years: int = 3) -> list[dict]:
    """Daily bars, oldest first. Empty list when the listing is not covered."""
    start = (datetime.now(timezone.utc) - timedelta(days=int(365.25 * years))).date()
    data = fmp("historical-price-eod/full", symbol=symbol,
               **{"from": start.isoformat()})
    if not data or not isinstance(data, list):
        return []
    bars = [b for b in data if b.get("close") is not None]
    bars.sort(key=lambda b: b["date"])
    return bars


def splice_live_bar(bars: list[dict], quote: dict) -> list[dict]:
    """Append today's in-progress bar so indicators reflect the live price."""
    if not bars or not quote.get("price"):
        return bars
    ts = quote.get("timestamp")
    if not ts:
        return bars
    quote_date = datetime.fromtimestamp(ts, timezone.utc).date().isoformat()
    if quote_date <= bars[-1]["date"]:
        # Same session already in the EOD series — refresh it with the live print.
        if quote_date == bars[-1]["date"]:
            bars = bars[:-1] + [{**bars[-1], "close": quote["price"]}]
        return bars
    return bars + [{
        "date": quote_date,
        "open": quote.get("open") or quote["price"],
        "high": quote.get("day_high") or quote["price"],
        "low": quote.get("day_low") or quote["price"],
        "close": quote["price"],
        "volume": quote.get("volume") or 0,
    }]


# --------------------------------------------------------------- indicators

def _sma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def rsi_wilder(closes: list[float], period: int = 14) -> float | None:
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for prev, cur in zip(closes[:-1], closes[1:]):
        diff = cur - prev
        gains.append(max(diff, 0.0))
        losses.append(max(-diff, 0.0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for g, l in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + l) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def atr_wilder(bars: list[dict], period: int = 14) -> float | None:
    if len(bars) < period + 1:
        return None
    trs = []
    for prev, cur in zip(bars[:-1], bars[1:]):
        trs.append(max(
            cur["high"] - cur["low"],
            abs(cur["high"] - prev["close"]),
            abs(cur["low"] - prev["close"]),
        ))
    atr = sum(trs[:period]) / period
    for tr in trs[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def indicators(bars: list[dict]) -> dict:
    if not bars:
        return {}
    closes = [b["close"] for b in bars]
    price = closes[-1]
    ma20, ma50, ma200 = (_sma(closes, w) for w in (20, 50, 200))
    atr = atr_wilder(bars)
    vols = [b.get("volume") or 0 for b in bars]
    avg_vol20 = sum(vols[-21:-1]) / 20 if len(vols) >= 21 else None

    def vs(ma):
        return None if not ma else (price - ma) / ma * 100

    if ma50 and ma200:
        stack = "bull" if price > ma50 > ma200 else "bear" if price < ma50 < ma200 else "mixed"
    else:
        stack = None

    last = bars[-1]

    def window(n, key, fn):
        return fn(b[key] for b in bars[-n:]) if len(bars) >= n else None

    low20, high20 = window(20, "low", min), window(20, "high", max)
    low7, high7 = window(7, "low", min), window(7, "high", max)

    return {
        "ma20": ma20, "ma50": ma50, "ma200": ma200,
        "vs20ma": vs(ma20), "vs50ma": vs(ma50), "vs200ma": vs(ma200),
        "rsi14": rsi_wilder(closes),
        "atr14": atr,
        "atr_pct": (atr / price * 100) if atr and price else None,
        "vol_ratio": (vols[-1] / avg_vol20) if avg_vol20 else None,
        "candle": ("up" if last["close"] > last["open"] else "down")
                  if last.get("open") else None,
        "stack": stack,
        "low7": low7, "high7": high7, "low20": low20, "high20": high20,
        # Entry, stop and target are one mechanical family across the reports:
        # entry off the 20-day low lifted by 0.3xATR, stop half an ATR below
        # that low, target two ATR above entry.
        "dip_buy": (low20 + 0.3 * atr) if (low20 is not None and atr) else None,
        "stop": (low20 - 0.5 * atr) if (low20 is not None and atr) else None,
        "target": (low20 + 2.3 * atr) if (low20 is not None and atr) else None,
        "sessions": len(bars),
    }


# ------------------------------------------------------------------ targets

def get_targets(symbol: str) -> dict:
    consensus = fmp("price-target-consensus", symbol=symbol) or []
    grades = fmp("grades-consensus", symbol=symbol) or []
    c = consensus[0] if consensus else {}
    g = grades[0] if grades else {}
    analysts = sum(v for k, v in g.items()
                   if k in ("strongBuy", "buy", "hold", "sell", "strongSell")
                   and isinstance(v, (int, float))) or None
    return {
        "target_low": c.get("targetLow"),
        "target_consensus": c.get("targetConsensus"),
        "target_high": c.get("targetHigh"),
        "target_median": c.get("targetMedian"),
        "rating": g.get("consensus"),
        "analysts": analysts,
        "ratings_up": (g.get("strongBuy") or 0) + (g.get("buy") or 0) or None,
        "ratings_down": (g.get("sell") or 0) + (g.get("strongSell") or 0) or None,
    }


def target_hit_rate(symbol: str, bars: list[dict], horizon_days: int = 365) -> dict:
    """Share of published targets whose price was actually reached in horizon.

    Only targets whose horizon has fully elapsed are scored, so an unreached
    target still inside its window never counts as a miss.
    """
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=horizon_days)
    # Heavily covered names publish 100+ targets a year, so the first page can
    # be entirely inside the open horizon. Page back until the feed predates
    # the cutoff, or three pages, whichever comes first.
    news: list[dict] = []
    for page in range(3):
        batch = fmp("price-target-news", symbol=symbol, page=page, limit=100)
        if not batch:
            break
        news.extend(batch)
        oldest = (batch[-1].get("publishedDate") or "")[:10]
        if oldest and oldest < cutoff.isoformat():
            break
    if not news or not bars:
        return {"hit_pct": None, "sample": 0}
    highs = [(b["date"], b["high"]) for b in bars]
    hits = total = 0
    for item in news:
        target = item.get("adjPriceTarget") or item.get("priceTarget")
        published = (item.get("publishedDate") or "")[:10]
        if not target or not published:
            continue
        try:
            pub_date = datetime.fromisoformat(published).date()
        except ValueError:
            continue
        if pub_date > cutoff:
            continue  # horizon has not elapsed yet
        window_end = (pub_date + timedelta(days=horizon_days)).isoformat()
        window = [h for d, h in highs if published <= d <= window_end]
        if not window:
            continue
        total += 1
        if max(window) >= target:
            hits += 1
    if total == 0:
        return {"hit_pct": None, "sample": 0}
    return {"hit_pct": hits / total * 100, "sample": total}


# --------------------------------------------------------------- news, flow

def get_news(symbol: str, limit: int = 3) -> list[dict]:
    """Recent headlines for the per-name news line. Empty list, never a guess."""
    items = fmp("news/stock", symbols=ADR_PROXY.get(symbol, symbol), limit=limit) or []
    return [{
        "date": (i.get("publishedDate") or "")[:16],
        "publisher": i.get("publisher") or i.get("site"),
        "title": i.get("title"),
        "url": i.get("url"),
    } for i in items if i.get("title")]


def get_sentiment(symbol: str) -> dict:
    """Rating, one-month ratings drift and insider flow.

    Put/call ratio and implied volatility have no series on this FMP plan, so
    they come back None and the report prints an em dash for them.
    """
    target = ADR_PROXY.get(symbol, symbol)
    hist = fmp("grades-historical", symbol=target, limit=2) or []
    up = down = None
    if len(hist) >= 2:
        cur, prev = hist[0], hist[1]

        def bulls(g):
            return (g.get("analystRatingsStrongBuy") or 0) + (g.get("analystRatingsBuy") or 0)

        def bears(g):
            return (g.get("analystRatingsSell") or 0) + (g.get("analystRatingsStrongSell") or 0)

        up, down = max(bulls(cur) - bulls(prev), 0), max(bears(cur) - bears(prev), 0)

    trades = fmp("insider-trading/search", symbol=target, limit=100) or []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).date().isoformat()
    buys = sells = 0
    for t in trades:
        if (t.get("transactionDate") or "") < cutoff:
            continue
        kind = (t.get("acquisitionOrDisposition") or "").upper()
        if kind == "A":
            buys += 1
        elif kind == "D":
            sells += 1

    return {
        "ratings_revised_up": up,
        "ratings_revised_down": down,
        "insider_buys_90d": buys,
        "insider_sells_90d": sells,
        "put_call": None,   # not on this plan
        "implied_vol": None,  # not on this plan
    }


# --------------------------------------------------------------------- rows

def build_row(symbol: str, with_targets: bool = True) -> dict:
    quote = get_quote(symbol)
    row: dict = {"ticker": symbol, **quote}

    if quote.get("price") is None:
        row.update({"error": "no quote from FMP, yfinance or ADR proxy"})
        return row

    hist_symbol = quote.get("proxy_symbol") or symbol
    bars = splice_live_bar(get_history(hist_symbol), quote)
    row.update(indicators(bars))

    if with_targets:
        tgt = get_targets(hist_symbol)
        row.update(tgt)
        row.update(target_hit_rate(hist_symbol, bars))
        consensus = tgt.get("target_consensus")
        row["mos_30"] = consensus * 0.70 if consensus else None
        row["consensus_upside"] = (
            (consensus - quote["price"]) / quote["price"] * 100 if consensus else None
        )
        high = tgt.get("target_high")
        row["high_upside"] = (
            (high - quote["price"]) / quote["price"] * 100 if high else None
        )
    return row


def build_rows(symbols: list[str], with_targets: bool = True) -> list[dict]:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        return list(pool.map(lambda s: build_row(s, with_targets), symbols))


# ----------------------------------------------------------------- backdrop

# (label, primary symbol, proxy symbol or None). A proxy is reported as a proxy.
BACKDROP_SYMBOLS = [
    ("sp500", "^GSPC", None),
    ("nasdaq", "^IXIC", None),
    ("dow", "^DJI", None),
    ("nikkei", "^N225", None),
    ("hang_seng", "^HSI", None),
    ("shanghai", "000001.SS", "ASHR"),
    ("sp_futures", "ESUSD", None),
    ("nasdaq_futures", "NQUSD", None),
    ("vix", "^VIX", None),
    ("dxy", "DX-Y.NYB", "UUP"),
]


def get_backdrop() -> dict:
    out: dict = {}
    for label, primary, proxy in BACKDROP_SYMBOLS:
        q = _fmp_quote(primary)
        used, is_proxy = primary, False
        if not q and proxy:
            q = _fmp_quote(proxy)
            used, is_proxy = proxy, True
        out[label] = {
            "symbol": used if q else primary,
            "proxy": is_proxy,
            "price": q.get("price") if q else None,
            "change_pct": q.get("changePercentage") if q else None,
            "name": q.get("name") if q else None,
            # The session the print belongs to — a report run after the close
            # must not caption today's close as the prior close.
            "timestamp": q.get("timestamp") if q else None,
        }

    rates = fmp("treasury-rates",
                **{"from": (datetime.now(timezone.utc) - timedelta(days=10)).date().isoformat(),
                   "to": datetime.now(timezone.utc).date().isoformat()}) or []
    rates.sort(key=lambda r: r["date"])
    latest = rates[-1] if rates else {}
    prior = rates[-2] if len(rates) > 1 else {}
    for label, field in (("ust10y", "year10"), ("ust2y", "year2")):
        value, prev = latest.get(field), prior.get(field)
        out[label] = {
            "value": value,
            "date": latest.get("date"),
            "prev": prev,
            "prev_date": prior.get("date"),
            # Yields move in basis points; hand the report the bp change so it
            # never has to derive one from two percentages.
            "change_bp": round((value - prev) * 100, 1)
                         if value is not None and prev is not None else None,
        }
    # No high-yield OAS series on this plan — report it as unavailable, never
    # as an estimate.
    out["hy_spread_bps"] = {"value": None, "note": "no HY OAS series on this FMP plan"}
    out["as_of"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return out


# ------------------------------------------------------------------- crypto

def get_crypto(symbols: list[str]) -> list[dict]:
    rows = []
    for sym in symbols:
        fmp_sym = sym.replace("-", "").upper()  # BTC-USD -> BTCUSD
        quote = get_quote(fmp_sym)
        row = {"ticker": sym, **quote}
        if quote.get("price") is not None:
            bars = splice_live_bar(get_history(fmp_sym), quote)
            row.update(indicators(bars))
        rows.append(row)
    return rows


# ----------------------------------------------------------------- calendar

def get_calendar(symbols: list[str], days: int = 90) -> list[dict]:
    """Earnings and ex-dividend dates inside the window, chronological."""
    today = datetime.now(timezone.utc).date()
    end = today + timedelta(days=days)
    events: list[dict] = []

    def for_symbol(symbol: str) -> list[dict]:
        found = []
        target = ADR_PROXY.get(symbol, symbol)
        for row in (fmp("earnings", symbol=target, limit=8) or []):
            date = row.get("date")
            if date and today.isoformat() <= date <= end.isoformat():
                found.append({"ticker": symbol, "date": date, "type": "earnings"})
        for row in (fmp("dividends", symbol=target, limit=8) or []):
            date = row.get("date")
            if date and today.isoformat() <= date <= end.isoformat():
                found.append({"ticker": symbol, "date": date, "type": "ex_dividend",
                              "amount": row.get("dividend")})
        return found

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for chunk in pool.map(for_symbol, symbols):
            events.extend(chunk)

    for e in events:
        e["days_out"] = (datetime.fromisoformat(e["date"]).date() - today).days
    events.sort(key=lambda e: (e["date"], e["ticker"]))
    return events


# ---------------------------------------------------------------------- CLI

def _emit(payload, out: str | None) -> None:
    text = json.dumps(payload, indent=2, default=str)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text)
        print(f"wrote {out} ({len(text):,} bytes)")
    else:
        print(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_w = sub.add_parser("watchlist", help="full watchlist rows with indicators")
    p_w.add_argument("--group", help="only this watchlist group heading (substring)")
    p_w.add_argument("--symbols", help="comma-separated override")
    p_w.add_argument("--no-targets", action="store_true")
    p_w.add_argument("--out")

    p_b = sub.add_parser("backdrop", help="indices, futures, rates, VIX")
    p_b.add_argument("--out")

    p_c = sub.add_parser("crypto", help="spot crypto rows")
    p_c.add_argument("--symbols", default="BTC-USD,ETH-USD")
    p_c.add_argument("--out")

    p_cal = sub.add_parser("calendar", help="earnings and ex-dividend dates")
    p_cal.add_argument("--days", type=int, default=90)
    p_cal.add_argument("--symbols")
    p_cal.add_argument("--out")

    p_s = sub.add_parser("sentiment", help="headlines, ratings drift, insider flow")
    p_s.add_argument("--symbols", required=True)
    p_s.add_argument("--news", type=int, default=3)
    p_s.add_argument("--out")

    sub.add_parser("selftest", help="check key, connectivity and one full row")

    args = parser.parse_args(argv)
    groups = parse_watchlist()

    try:
        if args.cmd == "watchlist":
            if args.symbols:
                symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
            elif args.group:
                symbols = equity_symbols(
                    {k: v for k, v in groups.items() if args.group.lower() in k.lower()}
                )
            else:
                symbols = equity_symbols(groups)
            rows = build_rows(symbols, with_targets=not args.no_targets)
            missing = [r["ticker"] for r in rows if r.get("price") is None]
            payload = {
                "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "source": SOURCE_REALTIME,
                "requested": len(symbols),
                "resolved": len(symbols) - len(missing),
                "unresolved": missing,
                "rows": rows,
            }
            if missing and len(missing) / max(len(symbols), 1) > 0.20:
                print(f"WARNING: {len(missing)}/{len(symbols)} names unresolved "
                      f"({', '.join(missing)}) — over the 20% publish threshold.",
                      file=sys.stderr)
            _emit(payload, args.out)

        elif args.cmd == "backdrop":
            _emit(get_backdrop(), args.out)

        elif args.cmd == "crypto":
            symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
            _emit({
                "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "rows": get_crypto(symbols),
            }, args.out)

        elif args.cmd == "calendar":
            symbols = ([s.strip() for s in args.symbols.split(",")]
                       if args.symbols else equity_symbols(groups))
            _emit({
                "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "days": args.days,
                "events": get_calendar(symbols, args.days),
            }, args.out)

        elif args.cmd == "sentiment":
            symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
            payload = {"as_of": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                bundles = pool.map(
                    lambda t: {"ticker": t, "news": get_news(t, args.news),
                               **get_sentiment(t)},
                    symbols)
            payload["rows"] = list(bundles)
            _emit(payload, args.out)

        elif args.cmd == "selftest":
            api_key()
            row = build_row("AAPL")
            bd = get_backdrop()
            print(f"AAPL {row['price']} via {row['source']} · RSI "
                  f"{row.get('rsi14') and round(row['rsi14'], 1)} · "
                  f"200MA {row.get('ma200') and round(row['ma200'], 2)} · "
                  f"hit {row.get('hit_pct') and round(row['hit_pct'])}% "
                  f"(n={row.get('sample')})")
            print(f"S&P {bd['sp500']['price']} · VIX {bd['vix']['price']} · "
                  f"10Y {bd['ust10y']['value']}")
            print(f"watchlist groups: {len(parse_watchlist())}, "
                  f"equities: {len(equity_symbols(parse_watchlist()))}")
    except DataError as exc:
        print(f"ERROR: {redact(str(exc))}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
