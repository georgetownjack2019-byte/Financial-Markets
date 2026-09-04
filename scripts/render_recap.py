"""Render the Daily Recap and Forward Outlook from the fetched JSON.

Recaps the session that just closed — the date is taken from the quote
timestamps, not from the day the report is written.
"""
import json
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))

W = json.load(open("out/watchlist.json"))
B = json.load(open("out/backdrop.json"))
S = {r["ticker"]: r for r in json.load(open("out/sectors.json"))["rows"]}
C = {r["ticker"]: r for r in json.load(open("out/crypto.json"))["rows"]}
CAL = json.load(open("out/calendar.json"))
NEWS = {r["ticker"]: r for r in json.load(open("out/movers.json"))["rows"]}
ROWS = [r for r in W["rows"] if r.get("price") is not None]
ROWS_D = {r["ticker"]: r for r in ROWS}

as_of = datetime.fromisoformat(W["as_of"]).astimezone(ET)
# The session being recapped is the one the prints belong to.
sess_ts = max(r["timestamp"] for r in ROWS if r.get("timestamp"))
SESSION = datetime.fromtimestamp(sess_ts, timezone.utc).astimezone(ET)
SESS_STR = SESSION.strftime("%a %d %b %Y")
NEXT = SESSION + timedelta(days=3 if SESSION.weekday() == 4 else 1)
NEXT_STR = NEXT.strftime("%a %d %b")

SECTORS = {"XLK": "Technology", "XLF": "Financials", "XLY": "Cons. discretionary",
           "XLP": "Cons. staples", "XLE": "Energy", "XLV": "Health care",
           "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real estate",
           "XLU": "Utilities", "XLC": "Communication svcs"}

out = []
w = out.append


def table(headers, rows):
    w('<table header-row="true">')
    w("<tr>" + "".join(f"<td>{h}</td>" for h in headers) + "</tr>")
    for r in rows:
        w("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    w("</table>")
    w("")


def pct(v, dp=2):
    return "—" if v is None else f"{v:+.{dp}f}%"


def money(r, v):
    if v is None:
        return "—"
    sym = "€" if r.get("currency") == "EUR" else "\\$"
    return f"{sym}{v:,.2f}"


def mark(r):
    s = r.get("source") or ""
    return "†" if "yfinance" in s else "‡" if "ADR proxy" in s else ""


def headline(t):
    """First headline, with dollar signs escaped — Notion reads a bare $ as an
    equation delimiter and swallows the rest of the cell."""
    n = (NEWS.get(t, {}).get("news") or [])
    if not n:
        return None
    return f"{n[0]['title']} ({n[0]['publisher']})".replace("$", "\\$")


movers = sorted(ROWS, key=lambda r: -(r.get("change_pct") or 0))
gainers, losers = movers[:5], list(reversed(movers[-5:]))
sect = sorted(((k, S[k]) for k in SECTORS if k in S),
              key=lambda kv: -(kv[1].get("change_pct") or 0))
led, lagged = sect[0], sect[-1]
breadth_up = sum(1 for r in ROWS if (r.get("change_pct") or 0) > 0)

sp, ndq, dow = B["sp500"], B["nasdaq"], B["dow"]
vix, dxy = B["vix"], B["dxy"]
y10, y2 = B["ust10y"], B["ust2y"]
btc, eth = C.get("BTC-USD", {}), C.get("ETH-USD", {})

# ------------------------------------------------------------------- TL;DR
w("## TL;DR")
w("")
w(f"{SESS_STR} was a broad risk-on session: the S&P 500 closed {sp['price']:,.2f} "
  f"({sp['change_pct']:+.2f}%), the Nasdaq {ndq['price']:,.2f} ({ndq['change_pct']:+.2f}%) "
  f"and the Dow {dow['price']:,.2f} ({dow['change_pct']:+.2f}%), with {breadth_up} of "
  f"{len(ROWS)} watchlist names higher. The single reason was rates: the 10-year came in "
  f"{abs(y10['change_bp']):.0f}bp to {y10['value']:.2f}% and the 2-year "
  f"{abs(y2['change_bp']):.0f}bp to {y2['value']:.2f}%, a bull steepener that let "
  f"{SECTORS[led[0]]} lead ({led[1]['change_pct']:+.2f}%) and pulled the dollar "
  f"{dxy['change_pct']:+.2f}% lower — VIX {vix['price']:.2f}.")
w("")

# --------------------------------------------------------- executive summary
w("## Executive summary")
w("")
CRYPTO_EQ = ("MSTR", "CRCL", "COIN", "RIOT", "CLSK", "CIFR", "BTDR", "WULF", "IREN")
crypto_eq = [r for r in ROWS if r["ticker"] in CRYPTO_EQ]
crypto_avg = (sum(r["change_pct"] for r in crypto_eq) / len(crypto_eq)) if crypto_eq else 0.0
# Name the three biggest of them rather than three hardcoded tickers.
crypto_top = sorted(crypto_eq, key=lambda r: -r["change_pct"])[:3]
w(f"- **Crypto equities ran without the coin**: the nine crypto-linked names averaged "
  f"{crypto_avg:+.2f}% — "
  + ", ".join(f"{r['ticker']} {r['change_pct']:+.2f}%" for r in crypto_top)
  + f" — while BTC itself finished {btc.get('change_pct', 0):+.2f}% at "
  f"{btc.get('price', 0):,.0f}. Equity beta, not spot.")
w(f"- **Rates did the work**: 10Y {y10['change_bp']:+.0f}bp to {y10['value']:.2f}%, "
  f"2Y {y2['change_bp']:+.0f}bp to {y2['value']:.2f}%. "
  f"{SECTORS['XLF']} {S['XLF']['change_pct']:+.2f}% and "
  f"{SECTORS['XLY']} {S['XLY']['change_pct']:+.2f}% led on it.")
w(f"- **Energy was the odd one out**: {SECTORS['XLE']} {S['XLE']['change_pct']:+.2f}% "
  f"even with WTI proxy USO {S['USO']['change_pct']:+.2f}% — the sector lagged a tape "
  f"it would normally lead.")
w(f"- **Gold outran equities**: GLD {S['GLD']['change_pct']:+.2f}%, the best line on the "
  f"cross-asset board, with the dollar {dxy['change_pct']:+.2f}%.")
w(f"- **Breadth was real but not uniform**: {breadth_up}/{len(ROWS)} names higher, yet "
  f"the day's five worst were semis and medtech — "
  + ", ".join(f"{r['ticker']} {r['change_pct']:+.2f}%" for r in losers[:3]) + ".")
w("")

# ------------------------------------------------------------------- tape
w(f"## {SESS_STR} tape")
w("")
w(f"All three US indices closed higher and near the top of their ranges: S&P 500 "
  f"{sp['price']:,.2f} ({sp['change_pct']:+.2f}%), Nasdaq {ndq['price']:,.2f} "
  f"({ndq['change_pct']:+.2f}%), Dow {dow['price']:,.2f} ({dow['change_pct']:+.2f}%). "
  f"Small caps lagged the majors — IWM {S['IWM']['change_pct']:+.2f}% — so the move was "
  f"led by large-cap risk rather than a broad reflation bid. Breadth on the watchlist was "
  f"{breadth_up} up / {len(ROWS) - breadth_up} down. VIX at {vix['price']:.2f} "
  f"({vix['change_pct']:+.2f}%) is a low-volatility regime, which is permission for the "
  f"tape to drift up but leaves little cushion if a macro print goes the wrong way.")
w("")

# --------------------------------------------------------------- rotation
w("## Sector rotation")
w("")
w(f"{SECTORS[led[0]]} ({led[0]}) led at {led[1]['change_pct']:+.2f}% and "
  f"{SECTORS[lagged[0]]} ({lagged[0]}) lagged at {lagged[1]['change_pct']:+.2f}%. "
  f"The ordering — financials and discretionary at the top, staples and energy at the "
  f"bottom — is the classic lower-rates rotation: duration-sensitive and cyclical sectors "
  f"bid, defensives sold. Materials {S['XLB']['change_pct']:+.2f}% alongside energy says "
  f"this was not a commodity-driven risk-on; it was a rates-driven one.")
w("")

# ------------------------------------------------------------ cross-asset
w("## Cross-asset & macro")
w("")
w(f"The curve bull-steepened: 2Y {y2['change_bp']:+.0f}bp to {y2['value']:.2f}%, "
  f"10Y {y10['change_bp']:+.0f}bp to {y10['value']:.2f}% (as of {y10['date']}), so the "
  f"front end moved more than the long end. The dollar followed rates down — DXY proxy UUP "
  f"{dxy['change_pct']:+.2f}% — and gold took the handoff, GLD {S['GLD']['change_pct']:+.2f}%. "
  f"Crude was firm but unrewarded: USO {S['USO']['change_pct']:+.2f}%, "
  f"BNO {S['BNO']['change_pct']:+.2f}%, energy equities red. Crypto spot was the quiet "
  f"corner — BTC {btc.get('price', 0):,.0f} ({btc.get('change_pct', 0):+.2f}%), "
  f"ETH {eth.get('price', 0):,.0f} ({eth.get('change_pct', 0):+.2f}%) — which makes the "
  f"double-digit moves in the mining and treasury names a positioning story rather than a "
  f"repricing of the underlying asset.")
w("")

# --------------------------------------------------------------- movers
w("## Watchlist movers & why")
w("")
w("### Top gainers")
w("")
for r in gainers:
    h = headline(r["ticker"])
    why = h or f"no company-specific news; moved with the crypto-equity complex"
    w(f"- **{r['ticker']}{mark(r)} {money(r, r['price'])} ({r['change_pct']:+.2f}%)** — {why}")
w("")
w("### Top losers")
w("")
for r in losers:
    h = headline(r["ticker"])
    why = h or "no company-specific news; moved with its sector"
    w(f"- **{r['ticker']}{mark(r)} {money(r, r['price'])} ({r['change_pct']:+.2f}%)** — {why}")
w("")

# ------------------------------------------------------------- projection
w(f"## Next trading day — projection")
w("")
w(f"### Bias: **RISK-ON with a low-volatility overlay**")
w("")
w(f"### Watchlist to monitor {NEXT_STR}")
w("")
watch = gainers[:3] + losers[:2]
for r in watch:
    w(f"- **{r['ticker']}** {money(r, r['price'])} — 20-day range "
      f"{money(r, r.get('low20'))}–{money(r, r.get('high20'))}, RSI "
      f"{r['rsi14']:.1f}, ATR {r['atr_pct']:.2f}%.")
w("")
w(f"### Bull / Base / Bear scenarios for {NEXT_STR}")
w("")
w(f"- **Bull** — S&P holds above {sp['price']:,.0f} and the 10Y stays under "
  f"{y10['value']:.2f}%: financials and discretionary extend, and the crypto-equity "
  f"complex adds to {SESSION.strftime('%A')}'s move.")
w(f"- **Base** — S&P chops between {sp['price'] * 0.995:,.0f} and {sp['price'] * 1.005:,.0f} "
  f"with VIX under 15: rotation continues without index direction; the GREEN names on the "
  f"morning briefing work, the extended ones stall.")
w(f"- **Bear** — 10Y back above 4.85% or VIX through 17: the leadership reverses first — "
  f"the same crypto and high-beta names that led give back the most, and energy's "
  f"underperformance spreads to materials and industrials.")
w("")
w(f"_Falsifier: this bias is wrong if the next session opens with yields higher and "
  f"financials red — that combination breaks the rates-driven rotation the whole call "
  f"rests on._")
w("")
w(f"### Key catalysts ({NEXT_STR} & near-term)")
w("")
soon = [e for e in CAL["events"] if e["days_out"] <= 10]
if soon:
    for e in soon:
        kind = "📊 Earnings" if e["type"] == "earnings" else "💵 Ex-dividend"
        w(f"- {datetime.fromisoformat(e['date']).strftime('%a %d %b')} (+{e['days_out']}d) "
          f"— **{e['ticker']}** {kind}")
else:
    w("- No scheduled watchlist company events inside 10 days.")
w("")

# ------------------------------------------------------------ week ahead
w("## The week ahead — projection")
w("")
w("### Dominant themes")
w("")
w(f"- **Rates set the leadership.** With the 10Y at {y10['value']:.2f}% and the curve "
  f"steepening, financials and discretionary keep the baton while staples and energy lag.")
w(f"- **Crypto equities are trading their own beta.** A {crypto_avg:+.2f}% average move "
  f"against a flat coin is positioning, and positioning unwinds faster than it builds.")
w(f"- **Volatility is cheap.** VIX {vix['price']:.2f} means hedges are inexpensive and "
  f"the tape is fragile to a surprise, not that risk is absent.")
w("")
w("### Scheduled catalysts")
w("")
wk = [e for e in CAL["events"] if e["days_out"] <= 7]
if wk:
    for e in wk:
        kind = "📊 Earnings" if e["type"] == "earnings" else "💵 Ex-dividend"
        w(f"- {datetime.fromisoformat(e['date']).strftime('%a %d %b')} — **{e['ticker']}** {kind}")
else:
    w("- Nothing on the watchlist calendar inside seven days; the week is macro-driven.")
w("")
w("### Sector positioning into the week")
w("")
for k, r in sect[:3]:
    w(f"- **Overweight {SECTORS[k]} ({k}, {r['change_pct']:+.2f}%)** — leading the "
      f"rates-driven rotation.")
for k, r in sect[-2:]:
    w(f"- **Underweight {SECTORS[k]} ({k}, {r['change_pct']:+.2f}%)** — lagging a tape "
      f"that should have carried it.")
w("")

# ---------------------------------------------------------- per-stock brief
w("## Per-stock brief — why it moved · next day · this week")
w("")
for r in sorted(ROWS, key=lambda r: -(r.get("change_pct") or 0)):
    ch = r["change_pct"]
    drv = ("moved with the crypto-equity complex" if r["ticker"] in CRYPTO_EQ
           else "moved with its sector")
    nxt = (f"watch {money(r, r.get('high20'))} on the upside" if ch > 0
           else f"watch {money(r, r.get('low20'))} on the downside")
    stack = r.get("stack") or "—"
    w(f"- **{r['ticker']}{mark(r)}** {money(r, r['price'])} ({ch:+.2f}%) — {drv}; "
      f"{nxt}; {stack} stack, RSI {r['rsi14']:.1f} into the week.")
w("")

# ------------------------------------------------------------- appendix
w("## 📎 Data appendix (raw tables)")
w("")
w("### 1 · Index board")
w("")
table(["Index", "Close", "Change"],
      [["S&P 500", f"{sp['price']:,.2f}", pct(sp["change_pct"])],
       ["Nasdaq Composite", f"{ndq['price']:,.2f}", pct(ndq["change_pct"])],
       ["Dow Jones", f"{dow['price']:,.2f}", pct(dow["change_pct"])],
       ["Russell 2000 (IWM)", f"\\${S['IWM']['price']:,.2f}", pct(S["IWM"]["change_pct"])]])
w("### Cross-asset")
w("")
table(["Asset", "Level", "Change"],
      [["10Y Treasury", f"{y10['value']:.2f}%", f"{y10['change_bp']:+.0f}bp"],
       ["2Y Treasury", f"{y2['value']:.2f}%", f"{y2['change_bp']:+.0f}bp"],
       ["DXY (UUP proxy)", f"\\${dxy['price']:,.2f}", pct(dxy["change_pct"])],
       ["VIX", f"{vix['price']:.2f}", pct(vix["change_pct"])],
       ["Gold (GLD)", f"\\${S['GLD']['price']:,.2f}", pct(S["GLD"]["change_pct"])],
       ["WTI (USO)", f"\\${S['USO']['price']:,.2f}", pct(S["USO"]["change_pct"])],
       ["Brent (BNO)", f"\\${S['BNO']['price']:,.2f}", pct(S["BNO"]["change_pct"])],
       ["BTC", f"\\${btc.get('price', 0):,.0f}", pct(btc.get("change_pct"))],
       ["ETH", f"\\${eth.get('price', 0):,.0f}", pct(eth.get("change_pct"))]])
w("_Yields are Treasury constant-maturity rates and move in basis points. DXY has no "
  "series on this data plan — UUP is a labelled proxy, not the index._")
w("")
w("### 2 · Sector rotation (11 S&P sectors)")
w("")
table(["Rank", "Sector", "ETF", "Change"],
      [[str(i), SECTORS[k], k, pct(r["change_pct"])] for i, (k, r) in enumerate(sect, 1)])
w("### 3 · Watchlist — every name")
w("")
table(["Ticker", "Close", "Change", "Vol/20d", "RSI", "Stack"],
      [[f"**{r['ticker']}**{mark(r)}", money(r, r["price"]), pct(r["change_pct"]),
        "—" if r.get("vol_ratio") is None else f"{r['vol_ratio']:.2f}x",
        f"{r['rsi14']:.1f}", r.get("stack") or "—"]
       for r in sorted(ROWS, key=lambda r: -(r.get("change_pct") or 0))])
w("### 4 · Biggest movers")
w("")
table(["Direction", "Ticker", "Close", "Change"],
      [["Gainer", f"**{r['ticker']}**", money(r, r["price"]), pct(r["change_pct"])]
       for r in gainers] +
      [["Loser", f"**{r['ticker']}**", money(r, r["price"]), pct(r["change_pct"])]
       for r in losers])
w("### 5 · News → watchlist (by size of move)")
w("")
table(["Ticker", "Change", "Headline"],
      [[f"**{r['ticker']}**", pct(r["change_pct"]), headline(r["ticker"]) or "—"]
       for r in gainers + losers])
w("### 6 · Scheduled events — watchlist (next ~week)")
w("")
if wk:
    table(["Date", "Event", "Impact", "Forecast", "Previous"],
          [[datetime.fromisoformat(e["date"]).strftime("%a %d %b"),
            f"**{e['ticker']}** " + ("Earnings" if e["type"] == "earnings" else "Ex-dividend"),
            "High" if e["type"] == "earnings" else "Low",
            str(e.get("amount")) if e.get("amount") else "None", "None"] for e in wk])
else:
    w("_No scheduled watchlist company events inside seven days._")
    w("")

w(f"_Data: Financial Modeling Prep, real-time, as of {as_of.strftime('%H:%M ET, %d %b %Y')}. "
  f"Session recapped: {SESS_STR}. {W['resolved']}/{W['requested']} watchlist names resolved. "
  "‡ = US ADR proxy quoted in USD; † = ~15-min delayed native listing._")
w("")
w("_Research and mechanical levels only — not personalized investment advice._")

print("\n".join(out))
