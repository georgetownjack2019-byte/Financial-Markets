"""Render the Morning Entry Briefing page body from the fetched JSON."""
import json
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))  # US Eastern, Sep = EDT

W = json.load(open("out/watchlist.json"))
B = json.load(open("out/backdrop.json"))
CAL = json.load(open("out/calendar.json"))
SENT = {r["ticker"]: r for r in json.load(open("out/sentiment.json"))["rows"]}
ROWS = W["rows"]

as_of = datetime.fromisoformat(W["as_of"]).astimezone(ET)
STAMP = as_of.strftime("%H:%M ET, %d %b %Y")

SYM = {"USD": "\\$", "EUR": "€"}


def cur(r):
    return SYM.get(r.get("currency"), "\\$")


def mark(r):
    s = r.get("source") or ""
    return "†" if "yfinance" in s else "‡" if "ADR proxy" in s else ""


def num(v, dp=2, pre="", suf=""):
    return "—" if v is None else f"{pre}{v:,.{dp}f}{suf}"


def pct(v, dp=1):
    return "—" if v is None else f"{v:+.{dp}f}%"


def money(r, v, dp=2):
    return "—" if v is None else f"{cur(r)}{v:,.{dp}f}"


def hitrate(r):
    if r.get("hit_pct") is None:
        return "n/a"
    star = "*" if (r.get("sample") or 0) < 5 else ""
    return f"{r['hit_pct']:.0f}%{star} ({r.get('sample')})"


def light(r):
    p, ma20, ma50, ma200 = r["price"], r.get("ma20"), r.get("ma50"), r.get("ma200")
    rsi, vol = r.get("rsi14"), r.get("vol_ratio")
    if ma200 is None:
        return "NONE"
    if p < ma200:
        return "RED"
    uptrend = ma50 and p > ma50 > ma200
    near = (ma20 and abs(p - ma20) / ma20 <= 0.04) or (ma50 and abs(p - ma50) / ma50 <= 0.04)
    if uptrend and near and rsi and 40 <= rsi <= 55:
        r["setup"] = "PULLBACK"
        return "GREEN"
    if uptrend and vol and vol > 1.2 and (r.get("vs20ma") or 0) > 0 and rsi and rsi < 75:
        r["setup"] = "BREAKOUT"
        return "GREEN"
    return "YELLOW"


for r in ROWS:
    r["light"] = light(r)

ORDER = {"GREEN": 0, "YELLOW": 1, "RED": 2, "NONE": 3}
ROWS.sort(key=lambda r: (ORDER[r["light"]], -(r["price"] or 0)))
GREEN = [r for r in ROWS if r["light"] == "GREEN"]
YELLOW = [r for r in ROWS if r["light"] == "YELLOW"]
RED = [r for r in ROWS if r["light"] == "RED"]
NONE = [r for r in ROWS if r["light"] == "NONE"]

EMOJI = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴", "NONE": "—"}
out = []
w = out.append


def table(headers, rows):
    w('<table header-row="true">')
    w("<tr>" + "".join(f"<td>{h}</td>" for h in headers) + "</tr>")
    for row in rows:
        w("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
    w("</table>")
    w("")


# ---------------------------------------------------------------- backdrop
def bd(key, dp=2):
    q = B[key]
    if q["price"] is None:
        return "—"
    label = f"({q['symbol']} proxy) " if q.get("proxy") else ""
    return f"{label}{q['price']:,.{dp}f} ({q['change_pct']:+.2f}%)"


vix = B["vix"]["price"]
vix_band = "low" if vix < 15 else "moderate" if vix < 22 else "elevated"
risk = sum(1 for k in ("sp500", "nasdaq", "dow", "nikkei") if (B[k]["change_pct"] or 0) < 0)
tone = "risk-off" if risk >= 3 else "risk-on" if risk <= 1 else "mixed / neutral"

# Caption the US index line by the session its print belongs to, so a run
# after the close does not present today's close as yesterday's.
sp_ts = B["sp500"].get("timestamp")
if sp_ts:
    sp_when = datetime.fromtimestamp(sp_ts, timezone.utc).astimezone(ET)
    # The print's own hour is the last tick the feed stamped, which can sit a
    # minute or two before the bell — whether that session has closed is a
    # question about now, not about the tick.
    if sp_when.date() < as_of.date():
        us_label = "US prior close"
    elif as_of.hour >= 16:
        us_label = f"US close {sp_when.strftime('%a %d %b')}"
    else:
        us_label = f"US session (live {sp_when.strftime('%H:%M ET')})"
else:
    us_label = "US last print"

w(f"> **Backdrop: {tone}.**")
w(f"> {us_label} — S&P 500 {bd('sp500')} · Nasdaq {bd('nasdaq')} · Dow {bd('dow')}.")
w(f"> Asia overnight — Nikkei {bd('nikkei')} · Hang Seng {bd('hang_seng')} · Shanghai {bd('shanghai')}.")
w(f"> US futures — S&P fut {bd('sp_futures')} · Nasdaq fut —.")
w(f"> Rates & risk — 10Y {B['ust10y']['value']:.2f}% ({B['ust10y']['change_bp']:+.0f}bp) · "
  f"DXY {bd('dxy')} · VIX {vix:.2f} ({vix_band}).")
w("> **Sentiment backdrop:** HY credit spread — bps.")
w("")
w(f"_Prices real-time via Financial Modeling Prep, as of {STAMP}._")
w("")
w("_Nasdaq futures and the high-yield OAS spread have no series on this data plan — "
  "printed as `—` rather than estimated. Shanghai and the dollar index are shown "
  "through the labelled ETF proxies ASHR and UUP._")
w("")

# ------------------------------------------------------------ master table
w("## 🚦 Master table — all 67 names")
w("")
headers = ["Ticker", "Price", "Dip-buy", "MoS (−30%)", "Tgt Low", "Consensus", "Tgt High",
           "Tgt hit%", "vs20MA", "vs50MA", "vs200MA", "RSI", "ATR% (14d)", "Candle",
           "Stack", "Vol/20d", "Light"]
body = []
for r in ROWS:
    body.append([
        f"**{r['ticker']}**{mark(r)}",
        money(r, r["price"]),
        money(r, r.get("dip_buy")),
        money(r, r.get("mos_30")),
        money(r, r.get("target_low")),
        money(r, r.get("target_consensus")),
        money(r, r.get("target_high")),
        hitrate(r),
        pct(r.get("vs20ma")), pct(r.get("vs50ma")), pct(r.get("vs200ma")),
        num(r.get("rsi14"), 1),
        num(r.get("atr_pct"), 2, suf="%"),
        r.get("candle") or "—",
        r.get("stack") or "—",
        "—" if r.get("vol_ratio") is None else f"{r['vol_ratio']:.2f}x",
        EMOJI[r["light"]],
    ])
table(headers, body)
w("_Sorted 🟢 then 🟡 then 🔴, by price descending inside each light. "
  "‡ = US ADR proxy quoted in USD (MC.PA → LVMUY, RMS.PA → HESAY, SHELL.AS → SHEL): "
  "this data plan does not quote the Paris and Amsterdam lines, and the figures are "
  "not currency-converted._")
w("")

# ------------------------------------------------------------ light sections
def nearest_ma(r):
    """Which MA the price is sitting on, its level, and the signed % against it."""
    best = None
    for label, key, vs in (("20-day MA", "ma20", "vs20ma"), ("50-day MA", "ma50", "vs50ma")):
        ma = r.get(key)
        if ma and (best is None or abs(r[vs]) < abs(best[2])):
            best = (label, ma, r[vs])
    return best


def rsi_read(rsi):
    if rsi is None:
        return "no RSI"
    if rsi < 35:
        return f"RSI {rsi:.1f} is oversold"
    if rsi < 45:
        return f"RSI {rsi:.1f} sits in the lower half of neutral — sold down, not yet washed out"
    if rsi <= 58:
        return f"RSI {rsi:.1f} is mid-range, which is where a pullback entry wants it"
    if rsi <= 70:
        return f"RSI {rsi:.1f} is firm without being stretched"
    return f"RSI {rsi:.1f} is overbought"


w("## 🚦 Traffic light")
w("")
w("### 🟢 GREEN")
w("")
for r in GREEN:
    c, t = cur(r), r["ticker"]
    ma_label, ma_level, ma_vs = nearest_ma(r)
    setup = r.get("setup", "PULLBACK")
    stack = {"bull": "price > 50-MA > 200-MA, a clean bull stack",
             "mixed": "the MA stack is mixed",
             "bear": "the MA stack is bearish"}[r.get("stack") or "mixed"]
    atr_line = (f"ATR(14) runs {r['atr_pct']:.2f}% of price ({c}{r['atr14']:,.2f}), "
                f"so a stop at {c}{r['stop']:,.2f} sits half an ATR under the 20-day low "
                f"and gives the position room to breathe")
    if setup == "PULLBACK":
        s1 = (f"Sitting {abs(ma_vs):.1f}% {'below' if ma_vs < 0 else 'above'} its "
              f"{ma_label} at {c}{ma_level:,.2f} and {r['vs200ma']:+.1f}% against the "
              f"200-MA at {c}{r['ma200']:,.2f}.")
    else:
        s1 = (f"Pushing {r['vs20ma']:+.1f}% through its 20-day MA at {c}{r['ma20']:,.2f} on "
              f"{r['vol_ratio']:.2f}x average volume, {r['vs200ma']:+.1f}% over the "
              f"200-MA at {c}{r['ma200']:,.2f}.")
    warn = ""
    if r.get("hit_pct") is not None and r["hit_pct"] < 50:
        warn = (f" ⚠️ Analyst targets have historically overshot — discount them "
                f"({r['hit_pct']:.0f}%, n={r['sample']}).")
    w(f"- **{t}{mark(r)} {c}{r['price']:,.2f}** — **{setup} setup** — {s1} "
      f"{rsi_read(r.get('rsi14'))}. {atr_line}; {stack}.{warn}")
    w(f"- **Dip-buy zone \\~{c}{r['dip_buy']:,.2f}** · buy zone {c}{r['dip_buy']:,.2f}–"
      f"{c}{r['dip_buy'] + 0.5 * r['atr14']:,.2f} · stop below {c}{r['stop']:,.2f}")
    sn = SENT.get(t, {})
    up_pct = r.get("consensus_upside")
    bias = ("Bullish" if (up_pct or 0) > 10 else "Bearish" if (up_pct or 0) < -5 else "Neutral")
    w(f"- _Sentiment: {bias} · {r.get('rating') or '—'} · "
      f"{'—' if up_pct is None else f'{up_pct:+.1f}%'} PT · "
      f"rev +{sn.get('ratings_revised_up', '—')}/−{sn.get('ratings_revised_down', '—')} · "
      f"insider B{sn.get('insider_buys_90d', '—')}/S{sn.get('insider_sells_90d', '—')} · "
      f"P/C — · IV —_")
    news = sn.get("news") or []
    headlines = " ; ".join(f"{n['title']} ({n['publisher']})" for n in news[:2]) or "no headlines returned"
    w(f"- _data: FMP real-time {as_of.strftime('%H:%M ET')} · news: {headlines}_")
    w("")

w("### 🟡 YELLOW")
w("")
for r in YELLOW:
    c = cur(r)
    if (r.get("vs20ma") or 0) > 5:
        why = f"extended {r['vs20ma']:+.1f}% over the 20-day MA — don't chase"
    elif r.get("stack") == "mixed":
        why = "above the 200-MA but the 50-MA has rolled under it — trend unconfirmed"
    else:
        why = "in the uptrend but with no trigger yet"
    trig = (f"needs a pullback into {c}{r['dip_buy']:,.2f} or a close over "
            f"{c}{r['high20']:,.2f} on above-average volume"
            if r.get("dip_buy") and r.get("high20") else "needs a defined level to form")
    w(f"- **{r['ticker']}{mark(r)} {c}{r['price']:,.2f}** — {why}. "
      f"{rsi_read(r.get('rsi14'))}, {r['vs200ma']:+.1f}% vs the 200-MA. Trigger: {trig}.")
w("")

w("### 🔴 RED")
w("")
for r in RED:
    c = cur(r)
    w(f"- **{r['ticker']}{mark(r)} {c}{r['price']:,.2f}** — {abs(r['vs200ma']):.1f}% below the "
      f"200-MA at {c}{r['ma200']:,.2f}; stand aside. Back in play on a reclaim of "
      f"{c}{r['ma200']:,.2f} that holds, with the 50-MA at {c}{r['ma50']:,.2f} turning up.")
w("")

if NONE:
    w("### ⚪ Not scored")
    w("")
    for r in NONE:
        w(f"- **{r['ticker']} {cur(r)}{r['price']:,.2f}** — only {r['sessions']} sessions of "
          f"history, so there is no 200-day MA and the decision rule cannot be applied. "
          f"Light printed as `—` rather than guessed.")
    w("")

# ------------------------------------------------------- valuation snapshot
w("## 📊 Valuation snapshot (sorted by analyst-target reliability)")
w("")
val = sorted(ROWS, key=lambda r: (r.get("hit_pct") is None, -(r.get("hit_pct") or 0)))
body = []
for r in val:
    up = r.get("consensus_upside")
    hi = r.get("high_upside")
    body.append([
        f"**{r['ticker']}**{mark(r)}",
        money(r, r["price"]),
        money(r, r.get("dip_buy")),
        money(r, r.get("mos_30")),
        "—" if r.get("target_consensus") is None else f"{money(r, r['target_consensus'])} ({up:+.1f}%)",
        "—" if r.get("target_high") is None else f"{money(r, r['target_high'])} ({hi:+.1f}%)",
        hitrate(r),
    ])
table(["Ticker", "Price", "Dip-buy", "MoS", "Consensus (upside)", "High tgt (upside)", "Tgt hit%"], body)
w("_Hit% is the share of individual analyst targets actually reached inside a 365-day window, "
  "scored only on targets whose horizon has fully elapsed. `*` marks a sample under 5. "
  "`n/a` means no target with an elapsed horizon — usually a recent listing._")
w("")

# ---------------------------------------------------------- event calendar
w("## 📅 Major Event Calendar (next 90 days · all IBKR names)")
w("")
NAMES = {r["ticker"]: (r.get("name") or r["ticker"]) for r in ROWS}
body = []
for e in CAL["events"]:
    d = datetime.fromisoformat(e["date"]).date()
    kind = "📊 Earnings" if e["type"] == "earnings" else "💵 Ex-dividend"
    if e["type"] == "ex_dividend" and e.get("amount"):
        kind += f" ({e['amount']})"
    body.append([d.strftime("%a %d %b"), f"+{e['days_out']}d", f"**{e['ticker']}**",
                 NAMES.get(e["ticker"], e["ticker"]), kind])
table(["Date", "In", "Ticker", "Name", "Event"], body)
w(f"_{len(CAL['events'])} scheduled company events across the watchlist in the next 90 days. "
  "Macro releases are not in this feed — see the map below and confirm times on the day's calendar._")
w("")


# -------------------------------------------------------------- macro map
w("## 🌐 Macro Event → Stock Impact (how each release moves the watchlist)")
w("")
MACRO = [
    ("CPI / PCE inflation",
     "Long-duration tech first — NVDA, MSFT, META, PLTR, CRM, TSLA; then rate-sensitive MA, V, FIS",
     "Hot print → yields up, multiples compress, high-multiple growth sells off hardest; cool print → the same names lead the bounce"),
    ("Fed decision / FOMC minutes / Powell",
     "Whole book, but banking and payments (V, MA, FIS, CTAS) and the crypto complex (COIN, MSTR, CRCL, miners) move most",
     "Dovish → risk-on, miners and crypto equities beta up 2–3x the index; hawkish → dollar up, gold and crypto down, growth de-rates"),
    ("Jobs — NFP, weekly claims, ADP",
     "Cyclicals and consumer — DIS, NFLX, TSLA, HSY, RACE; industrials CTAS, DELL",
     "Strong payrolls with cool wages → risk-on; strong wages → yields up and growth down; weak print reads as recession, not relief"),
    ("Retail sales / UMich sentiment",
     "Consumer confidence names — NFLX, TSLA, DIS, HSY, RACE, MC.PA, RMS.PA",
     "Beat → discretionary and luxury lead; miss → staples over discretionary, luxury sold on China read-through"),
    ("GDP · ISM / PMI",
     "Semis and industrials — NVDA, AVGO, ASML, TSM, MU, LITE, CTAS, DELL, MP, USAR",
     "ISM back over 50 → semis and industrial cyclicals lead; sub-48 → defensives (ABT, UNH, XLP-type) outperform"),
    ("Oil — EIA inventories, OPEC+",
     "Energy — XOM, CVX, SHELL.AS, TTE, LNG, EPD; utilities VST, CEG second-order",
     "Draw or supply cut → crude up, integrateds and LNG lead; build or quota rise → energy lags and the CPI read cools"),
    ("10Y yield · Treasury auctions · DXY",
     "Everything, but longest-duration first — IONQ, PLTR, CRWV, APLD, IREN and the miners; gold-adjacent MP, USAR",
     "10Y through recent highs → high-beta and unprofitable growth hit hardest; a soft auction with a weaker dollar → the same names rebound fastest"),
]
table(["Release", "Names it moves", "Typical first-order reaction"],
      [[a, b, c] for a, b, c in MACRO])
w("_Reference map — the typical first-order reaction, not a forecast; confirm the day's release times on the calendar._")
w("")

# ----------------------------------------------------------- decision rule
w("## Decision rule (Part 4)")
w("")
w("- 🟢 **GREEN** — uptrend *and* a trigger: PULLBACK to the 20/50-MA with RSI ~40–55, "
  "or BREAKOUT above a base on above-average volume.")
w("- 🟡 **YELLOW** — wanted, but extended (don't chase) or no trigger yet.")
w("- 🔴 **RED** — below the 200-MA. Stand aside until it bases.")
w("")
w(f"**Verdict: {len(GREEN)} actionable · {len(YELLOW)} on alert · {len(RED)} stand-aside.**"
  + (f" {len(NONE)} unscored ({', '.join(r['ticker'] for r in NONE)}) — too little history for a 200-MA." if NONE else ""))
w("")
w(f"_Data: Financial Modeling Prep, real-time, as of {STAMP}. "
  f"{W['resolved']}/{W['requested']} watchlist names resolved. "
  "Indicators computed from three years of daily bars with the live print spliced in as "
  "today's bar; entry = 20-day low + 0.3×ATR(14), stop = 20-day low − 0.5×ATR(14). "
  "‡ = US ADR proxy quoted in USD._")
w("")
w("_Research and mechanical levels only — not personalized investment advice._")

print("\n".join(out))


