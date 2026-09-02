"""Render the Crypto Levels page body from live FMP data."""
import sys, json
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "scripts")
import market_data as m

ET = timezone(timedelta(hours=-4))
now = datetime.now(timezone.utc).astimezone(ET)
STAMP = now.strftime("%H:%M ET, %d %b %Y")

out = []
w = out.append
w(f"_Generated {now.strftime('%H:%M')} ET · mechanical levels only, not a recommendation._")
w("")
w(f"_Spot and bars real-time via Financial Modeling Prep, as of {STAMP}. Crypto trades "
  "continuously, so these levels are only meaningful next to the minute they were cut._")
w("")

summary = []
for label, sym in (("BTC-USD", "BTCUSD"), ("ETH-USD", "ETHUSD")):
    q = m.get_quote(sym)
    bars = m.splice_live_bar(m.get_history(sym), q)
    ind = m.indicators(bars)
    spot = q["price"]
    atr = ind["atr14"]

    # 20-week MA: last close of each ISO week, mean of the trailing 20 weeks.
    weekly = {}
    for b in bars:
        d = datetime.fromisoformat(b["date"]).date()
        weekly[d.isocalendar()[:2]] = b["close"]
    wk = list(weekly.values())
    ma20w = sum(wk[-20:]) / 20 if len(wk) >= 20 else None

    lo7, hi7, lo20, hi20 = ind["low7"], ind["high7"], ind["low20"], ind["high20"]
    rng_pos = (spot - lo7) / (hi7 - lo7) * 100 if hi7 > lo7 else None

    entry = lo7 + 0.3 * atr
    zone_lo = lo7 + 0.20 * (hi7 - lo7)
    zone_hi = lo7 + 0.25 * (hi7 - lo7)
    stop = lo7 - 0.5 * atr
    target = entry + 2 * atr

    close180 = bars[-181]["close"] if len(bars) > 181 else None
    gates = [
        ("above 20-week MA", ma20w is not None and spot > ma20w,
         f"20-week MA {ma20w:,.0f}" if ma20w else "20-week MA —"),
        ("above MA200", ind["ma200"] is not None and spot > ind["ma200"],
         f"MA200 {ind['ma200']:,.0f}" if ind["ma200"] else "MA200 —"),
        ("180-day momentum positive", close180 is not None and spot > close180,
         f"close 180 sessions ago {close180:,.0f}" if close180 else "no 180-session history"),
    ]
    all_gates = all(g[1] for g in gates)
    in_zone = zone_lo <= spot <= zone_hi
    status = ("**Status: 🟢 ENTRY ZONE LIVE**" if all_gates and in_zone
              else "**Status: 🟡 WAIT**" if all_gates
              else "**Status: 🔴 STAND ASIDE**")
    summary.append((label, status))

    def vs(level):
        """Spot measured against the level — the indicator table's convention."""
        return f"{(spot - level) / level * 100:+.2f}%"

    def off(level):
        """The level measured against spot — how far the plan sits from here."""
        return f"{(level - spot) / spot * 100:+.2f}%"

    w(f"## {label} — {spot:,.0f}")
    w("")
    w(f"ATR {atr:,.0f} ({ind['atr_pct']:.2f}%) · sits at **{rng_pos:.0f}%** of the 7-day range")
    w("")
    w('<table header-row="true">')
    w("<tr><td>Indicator</td><td>Level</td><td>Spot vs it</td></tr>")
    rows = [("MA 20 (daily)", ind["ma20"]), ("MA 50 (daily)", ind["ma50"]),
            ("MA 200 (daily)", ind["ma200"]), ("MA 20 (weekly)", ma20w),
            ("7-day low", lo7), ("7-day high", hi7),
            ("20-day low", lo20), ("20-day high", hi20)]
    for name, level in rows:
        w(f"<tr><td>{name}</td><td>{'—' if level is None else f'{level:,.0f}'}</td>"
          f"<td>{'—' if level is None else vs(level)}</td></tr>")
    w("</table>")
    w("")
    w("**Gates**")
    w("")
    for name, ok, detail in gates:
        w(f"- {'✅' if ok else '❌'} {name} — {detail}")
    w("")
    w("**Trade plan**")
    w("")
    w('<table header-row="true">')
    w("<tr><td> </td><td>Level</td><td>vs spot</td></tr>")
    w(f"<tr><td>Entry (7d low + 0.3×ATR)</td><td>**{entry:,.0f}**</td><td>{off(entry)}</td></tr>")
    w(f"<tr><td>Entry zone (lower 20–25%)</td><td>{zone_lo:,.0f}–{zone_hi:,.0f}</td>"
      f"<td>{off(zone_lo)} / {off(zone_hi)}</td></tr>")
    w(f"<tr><td>Stop (7d low − 0.5×ATR)</td><td>{stop:,.0f}</td><td>{off(stop)}</td></tr>")
    w(f"<tr><td>Target (entry + 2×ATR)</td><td>{target:,.0f}</td><td>{off(target)}</td></tr>")
    w("</table>")
    w("")
    w(status)
    w("")

w("---")
w("")
w(f"_Data: Financial Modeling Prep, real-time, as of {STAMP}. ATR is 14-period on daily bars; "
  "every level is recomputed each run and never carried over from a previous page._")
w("")
w("_Research and mechanical levels only — not personalized investment advice._")
print("\n".join(out))
