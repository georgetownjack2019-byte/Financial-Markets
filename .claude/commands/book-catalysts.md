---
description: Generate and push the Book Catalysts note — every live bullish and bearish development, each sized in dollars against the actual position book
argument-hint: [optional — a horizon, e.g. "next week", "10 days", or a single driver like "rates" / "oil"]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ⚖️ Book Catalysts — bullish vs bearish, priced

Two questions, in this order:

1. **Why did each name move?** — split today's move into the part the market
   explains and the part that is the company's own story.
2. **What can it do next?** — forward ranges from each name's own volatility,
   plus the catalysts that could push it outside them.

Not a news digest. The organising fact is that for a concentrated book the
market usually explains a *minority* of any given day, so an explanation that
stops at "the Nasdaq was down" has explained almost nothing.

Read `.claude/portfolio.md` for names, tiers and cost basis, and
`.claude/notion-push-rules.md` for destination, formatting and data-integrity
rules. Both are binding. Held names only — candidates get a one-line mention at
most. `.claude/watchlist.md` is **not** used here.

Horizon or driver override (if given): `$ARGUMENTS` — default is the next five
trading sessions.

## Title & icon

- Title: `⚖️ Book Catalysts — <Ddd DD Mon YYYY>`
- Icon: `⚖️`
- Existing page for the day → append `(update 2)` / `(intraday)` per the push
  rules. Never overwrite.

## 1 · Data

FMP `/stable`, key from `FMP_API_KEY`. Fetch per held name: `quote`,
`historical-price-eod/full` (≥ 13 months, for a 200d SMA and a stable beta),
`price-target-consensus`, `price-target-summary`, `grades-consensus`,
`news/stock`. Plus `treasury-rates`, `economic-calendar` (forward window **and**
the trailing 12 months for reaction measurement), `earnings-calendar`,
`news/general-latest` and `news/crypto-latest` for the driver sweep.

Day-over-day change comes from **consecutive closes**. The provider's EOD
`change` field is open-to-close and must not be used.

State the as-of timestamp and whether the market was open at read time.

## 2 · Fit one multi-factor model per name — never separate single-factor ones

**Run a single multivariate OLS per name**, regressing its daily % return on all
drivers *together*:

| Factor | Series | Applies to |
|---|---|---|
| Equity | `^IXIC` daily % | every name |
| Rates | `treasury-rates` `year10`, daily change in **bp** | every name |
| Oil | `BZUSD` daily % | energy names only |
| Crypto | `BTCUSD` daily % | crypto-linked names only |

**Fitting the factors separately and adding the results double-counts and is
wrong.** Rate moves already drive much of what the equity index does, so a
univariate rates beta silently re-charges the book for the equity selloff those
rates caused. On this book that error overstated the rates sensitivity by
roughly 13x (−$1,118 per 25bp against a true −$84). Always quote the rates
coefficient as "holding the index constant".

From the fitted model, compute and publish:

- **R² per name** — the share of daily variance the factors explain. This is the
  headline number of the whole report, not a diagnostic. Publish `1 − R²` beside
  it and label it **company-specific**.
- **Residual standard deviation** — the 1-sigma daily move with the market
  stripped out, in % and in dollars on the position.
- **Weighted book beta** per factor, and the book's dollar cost per 25bp.
- **The split**: what share of the book wants each driver up vs down.

Report **every coefficient with its R² or correlation.** A beta without its fit
is a number pretending to be a forecast. Where the market explains under ~30%,
say so in the text at the point of use: for that name, macro reasoning explains
a minority of the move and the news section carries the weight.

## 3 · Sections, in this order

### `## 1 · Why it moved — attribution`

The position table (shares, basis, price, P&L, weight), then the attribution
table for the session: for each name, the actual move decomposed into

`market · rates · commodity/crypto · RESIDUAL (= company-specific)`

Flag any residual above roughly 1.5x the name's residual SD — that is a
company-story day, and the news section must name the cause or state plainly
that none was found.

Then the standing explanatory table: per name, **R² (market) vs 1 − R²
(company-specific)**, with the daily 1-sigma split into its market and company
parts in dollars.

Rank the names by R². The lowest-R² name is the one where macro commentary is
least useful and company news matters most — say which it is.

### `## 2 · What it can do next — ranges`

From each name's own realised daily volatility:

`Spot · daily 1σ · 1-week 1σ band · 1-week 2σ band`

and the same for the book in dollars, at 1σ and 2σ.

State clearly that 1σ is roughly a 68% band — a one-in-three chance of
finishing outside it — and that these are distributions, not forecasts.

**Then cross the bands against the levels**: name every position whose 1σ
one-week downside sits *below* its stated support or stop. That means an
ordinary week breaks the level, which is a materially different risk from a
tail event, and it must be called out explicitly.

### `## 3 · 🟢 Bullish, sized`

One row per catalyst. Columns:

`Catalyst · Channel and assumed magnitude · Book $ · then one column per name`

### `## 4 · 🔴 Bearish, sized`

Same shape. Also include the **break-support arithmetic**: for each name, the
dollar cost of walking to its next support, and to the one after that, plus the
cumulative P&L against cost basis at each level. Then state what it costs if
every name breaks its first support in the same session — a correlated risk-off
day is the scenario a low correlation matrix does *not* protect against.

### `## 5 · The inversion check`

**Mandatory section — never skip it, even to say nothing inverted.**

For every catalyst, ask whether it reaches the book through more than one
channel, and whether the channels disagree. Oil is the standing example: a
crude spike pays the energy position through its Brent beta and charges the
rate-sensitive majority through the inflation-and-yields channel, usually
several times over. Publish the netting arithmetic line by line.

Any catalyst whose **net book effect has the opposite sign to its obvious
read** goes in this section with the full derivation. These are the findings
that justify the page existing.

### `## 6 · Combined scenarios`

Three to six mixed paths (full bull, dovish data, term-premium leg, full
risk-off …), each stated as a combination of channel moves, with the book
figure and the per-name split. Say plainly whether the tails are symmetric —
if the full-bear number is larger than the full-bull number, that is the
headline, not a footnote.

### `## 7 · What I cannot size`

List the catalysts with no measurable channel — diffuse Fed-speaker risk, a
first-time read-through from another company's earnings, an unscheduled
political outcome. **Name them and say why, rather than inventing a number.**
Where a rough bound exists from an observed analogue, give it and label it as
judgement, not measurement.

### `## 8 · News classification`

Sweep the per-name feeds plus `news/stock-latest`, `news/general-latest` and
`news/crypto-latest` for the period since the last run. Sort every item into:

1. **New and material** — a genuine event, dated in the window.
2. **Backward-looking disclosure** — 13F filings, insider sales already
   executed weeks earlier, re-reported prior news. These *look* negative to a
   keyword filter and carry almost no information. Say so explicitly.
3. **Commentary** — opinion pieces, bull/bear think-pieces, ratings roundups.
4. **Unresolved carry-over** — overhangs from before the window that got
   neither better nor worse. List these; silence is not resolution.

A name with **zero** articles is a finding worth stating, especially after a
large move or alongside a thin analyst book. And note in the footer that a
quiet feed is not proof nothing happened — disclosures land pre-market.

### `## 9 · Standing levels`

Per name: spot, basis, next support, line to reclaim, hard invalidation, and
ATR(14) as % of price. For any name whose ATR exceeds ~5%, state that stops
must be **closing** stops — an intraday touch will be noise.

## 4 · Rules that keep this honest

- **Measured vs assumed.** Betas, R² and residual SDs are measured from data;
  scenario magnitudes ("Brent +5%", "10Y +20bp") are chosen for illustration.
  Label which is which in the footer of every page. Never present an assumed
  input as a forecast.
- **Never fit factors separately and add them.** See §2. If a prior page quoted
  a univariate sensitivity, correct it explicitly rather than quietly restating.
- **Every figure is beta-implied and excludes company-specific news** — which
  is frequently what actually moves these names. Say so.
- Report the book's losing scenarios at full size. Never net a bad path against
  a good one to soften it, and never drop a bearish row for balance.
- If a prior `⚖️ Book Catalysts` page exists, score the last one: which called
  catalysts fired, which did not, and where the sizing was wrong. A method that
  never marks itself is not a method.
- Small event samples (n < 10) and weak correlations must be flagged at the
  point of use, not only in the footer.

## 5 · Push

Per `.claude/notion-push-rules.md`. Report the title and URL. Nothing else.
