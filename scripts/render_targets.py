"""Render the Targets & Consensus sheet and its two charts.

Writes the page body to stdout and the charts to out/chart_upside.png and
out/chart_groups.png for upload as Notion attachments.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, "scripts")
import market_data as md

ET = timezone(timedelta(hours=-4))
W = json.load(open("out/watchlist.json"))
ROWS = {r["ticker"]: r for r in W["rows"]}
GROUPS = md.parse_watchlist()
as_of = datetime.fromisoformat(W["as_of"]).astimezone(ET)
STAMP = as_of.strftime("%H:%M ET, %d %b %Y")

# Spot crypto is a different report; the equity sheet leaves it out.
GROUPS = {k: v for k, v in GROUPS.items() if "spot" not in k}
N = len({t for v in GROUPS.values() for t in v})


def sym(r):
    return "€" if r.get("currency") == "EUR" else "\\$"


def money(r, v):
    return "—" if v is None else f"{sym(r)}{v:,.2f}"


def pct(v, dp=1):
    return "—" if v is None else f"{v:+.{dp}f}%"


def mark(r):
    s = r.get("source") or ""
    return "†" if "yfinance" in s else "‡" if "ADR proxy" in s else ""


def hit(r):
    if r.get("hit_pct") is None:
        return "—"
    star = "*" if (r.get("sample") or 0) < 5 else ""
    return f"{r['hit_pct']:.0f}%{star}"


# ------------------------------------------------------------------ charts
def draw_charts():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Colourblind-safe: one hue for positive, one for negative, nothing else.
    POS, NEG, INK, GRID = "#1b6ca8", "#c1553b", "#1a1a1a", "#d8d8d8"

    named = [(t, r) for t, r in ROWS.items() if r.get("consensus_upside") is not None]
    named.sort(key=lambda kv: kv[1]["consensus_upside"])
    labels = [t for t, _ in named]
    vals = [r["consensus_upside"] for _, r in named]

    fig, ax = plt.subplots(figsize=(9, max(8, len(labels) * 0.22)), dpi=160)
    ax.barh(labels, vals, color=[POS if v >= 0 else NEG for v in vals], height=0.72)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("Upside to consensus target (%)", color=INK)
    ax.set_title(f"Upside to consensus target, all {len(labels)} names",
                 color=INK, fontsize=13, pad=12, loc="left")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK, labelsize=7.5, length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    span = max(vals) - min(vals)
    for y, v in enumerate(vals):
        ax.text(v + (span * 0.008 if v >= 0 else -span * 0.008), y, f"{v:+.0f}%",
                va="center", ha="left" if v >= 0 else "right", fontsize=6.5, color=INK)
    ax.margins(x=0.10)
    fig.tight_layout()
    fig.savefig("out/chart_upside.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    means = []
    for g, tickers in GROUPS.items():
        ups = [ROWS[t]["consensus_upside"] for t in tickers
               if t in ROWS and ROWS[t].get("consensus_upside") is not None]
        if ups:
            means.append((g, sum(ups) / len(ups), len(ups)))
    means.sort(key=lambda m: -m[1])

    def plain(g):
        """Group headings carry emoji; DejaVu Sans has none of them and draws
        tofu boxes, so chart labels use the words only."""
        return "".join(c for c in g if c.isascii() or c.isalpha()).strip()

    fig, ax = plt.subplots(figsize=(9, 5), dpi=160)
    names = [f"{plain(g)}  (n={n})" for g, _, n in means]
    vals2 = [v for _, v, _ in means]
    ax.bar(names, vals2, color=[POS if v >= 0 else NEG for v in vals2], width=0.62)
    ax.axhline(0, color=INK, lw=1)
    ax.set_ylabel("Average upside to consensus (%)", color=INK)
    ax.set_title("Average upside to consensus by group", color=INK,
                 fontsize=13, pad=12, loc="left")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK, labelsize=8, length=0)
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    plt.setp(ax.get_xticklabels(), rotation=28, ha="right")
    for x, v in enumerate(vals2):
        ax.text(x, v + (max(vals2) * 0.02), f"{v:+.0f}%", ha="center",
                fontsize=8.5, color=INK)
    fig.tight_layout()
    fig.savefig("out/chart_groups.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return means


means = draw_charts()

out = []
w = out.append
w(f"Analyst price targets, consensus upside, fair-value estimate, dip-buy level, target "
  f"hit-rate and ATR for the {N}-name **complete watchlists 3108**. Prices and targets "
  f"real-time via Financial Modeling Prep, {STAMP}. Not advice.")
w("")

for g, tickers in GROUPS.items():
    rows = [ROWS[t] for t in tickers if t in ROWS]
    rows.sort(key=lambda r: -(r.get("consensus_upside")
                              if r.get("consensus_upside") is not None else -1e9))
    w(f"## {g}")
    w("")
    w('<table header-row="true">')
    w("<tr><td>Ticker</td><td>Price</td><td>Consensus</td><td>Upside</td><td>Tgt High</td>"
      "<td>Fair val</td><td>Dip-buy</td><td>Hit%</td><td>ATR%</td><td>#An</td></tr>")
    for r in rows:
        atr = r.get("atr_pct")
        atr_cell = "—" if atr is None else f"{atr:.2f}%"
        dip = r.get("dip_buy")
        # A dip-buy above spot is not a dip — print an em dash rather than a
        # level nobody would act on.
        dip_cell = money(r, dip) if (dip is not None and dip <= r["price"]) else "—"
        w(f"<tr><td>**{r['ticker']}**{mark(r)}</td><td>{money(r, r['price'])}</td>"
          f"<td>{money(r, r.get('target_consensus'))}</td>"
          f"<td>{pct(r.get('consensus_upside'))}</td>"
          f"<td>{money(r, r.get('target_high'))}</td><td>—</td>"
          f"<td>{dip_cell}</td><td>{hit(r)}</td>"
          f"<td>{atr_cell}</td><td>{r.get('analysts') or '—'}</td></tr>")
    w("</table>")
    w("")

w("## Group averages")
w("")
w('<table header-row="true">')
w("<tr><td>Group</td><td>Names priced</td><td>Average upside</td></tr>")
for g, v, n in means:
    w(f"<tr><td>{g}</td><td>{n}</td><td>{v:+.1f}%</td></tr>")
w("</table>")
w("")
w("_A negative upside is kept negative — a consensus below spot is a signal, not an error "
  "to correct. `Fair val` has no series on this data plan and prints `—` for every name "
  "rather than being substituted with consensus. `Dip-buy` prints `—` where the level sits "
  "above the current price. `Hit%` is the share of individual analyst targets actually "
  "reached inside a 365-day window, scored only on targets whose horizon has fully "
  "elapsed; `*` marks a sample under 5._")
w("")
w(f"_Data: Financial Modeling Prep, real-time, as of {STAMP}. "
  f"{W['resolved']}/{W['requested']} watchlist names resolved. "
  "‡ = US ADR proxy quoted in USD (MC.PA → LVMUY, RMS.PA → HESAY, SHELL.AS → SHEL), "
  "not currency-converted; † = ~15-min delayed native listing._")
w("")
w("_Research and mechanical levels only — not personalized investment advice._")
print("\n".join(out))
