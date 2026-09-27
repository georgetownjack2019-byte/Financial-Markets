---
description: Generate and push the Book Catalysts note — every live bullish and bearish development, each sized in dollars against the actual position book
argument-hint: [optional — a horizon, e.g. "next week", "10 days", or a single driver like "rates" / "oil"]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ⚖️ Book Catalysts — bullish vs bearish, priced

Every live catalyst for the held book, translated into **dollars against the
real positions**. Not a news digest: the point is that "bullish for LNG" and
"bullish for the book" are different claims, and only arithmetic separates them.

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

## 2 · Measure the channels before naming any catalyst

This ordering is the whole method. Establish how the book transmits *first*,
then every catalyst gets routed through a measured channel instead of a guess.

Regress each held name's daily % return on each driver, over the full sample:

| Channel | Driver series | Note |
|---|---|---|
| Equity beta | `^IXIC` daily % | The headline exposure |
| **Rates** | `treasury-rates` `year10`, **daily change in bp** | Filter to days with `abs(dY) > 0.5bp` — flat days add noise and flatten the slope |
| Oil | `BZUSD` daily % | Only for energy names |
| Crypto | `BTCUSD` daily % | Only for crypto-linked names |

Report **beta and correlation together, always.** A beta without its correlation
is a number pretending to be a forecast. Where `abs(corr) < 0.3`, say in the
text that the relationship is weak and the dollar figures are central tendencies
with wide scatter.

Then compute and publish:

- **Weighted book beta** per channel — the sum of (weight × beta). This is the
  single most useful number on the page.
- **The split**: what share of the book wants each driver to go up vs down.
  A book that is 72% long-duration and 28% energy is a rates bet whatever the
  ticker list looks like.
- **Cost per unit**: "the book loses X% per +1bp on the 10-year, i.e. $Y per
  +25bp". Quote it in dollars, not just percent.

## 3 · Sections, in this order

### `## 1 · What the book is, in exposure terms`

The position table (shares, basis, price, P&L, weight) followed by the channel
matrix: per name and for the book, each beta with its correlation.

### `## 2 · 🟢 Bullish, sized`

One row per catalyst. Columns:

`Catalyst · Channel and assumed magnitude · Book $ · then one column per name`

### `## 3 · 🔴 Bearish, sized`

Same shape. Also include the **break-support arithmetic**: for each name, the
dollar cost of walking to its next support, and to the one after that, plus the
cumulative P&L against cost basis at each level. Then state what it costs if
every name breaks its first support in the same session — a correlated risk-off
day is the scenario a low correlation matrix does *not* protect against.

### `## 4 · The inversion check`

**Mandatory section — never skip it, even to say nothing inverted.**

For every catalyst, ask whether it reaches the book through more than one
channel, and whether the channels disagree. Oil is the standing example: a
crude spike pays the energy position through its Brent beta and charges the
rate-sensitive majority through the inflation-and-yields channel, usually
several times over. Publish the netting arithmetic line by line.

Any catalyst whose **net book effect has the opposite sign to its obvious
read** goes in this section with the full derivation. These are the findings
that justify the page existing.

### `## 5 · Combined scenarios`

Three to six mixed paths (full bull, dovish data, term-premium leg, full
risk-off …), each stated as a combination of channel moves, with the book
figure and the per-name split. Say plainly whether the tails are symmetric —
if the full-bear number is larger than the full-bull number, that is the
headline, not a footnote.

### `## 6 · What I cannot size`

List the catalysts with no measurable channel — diffuse Fed-speaker risk, a
first-time read-through from another company's earnings, an unscheduled
political outcome. **Name them and say why, rather than inventing a number.**
Where a rough bound exists from an observed analogue, give it and label it as
judgement, not measurement.

### `## 7 · News classification`

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

### `## 8 · Standing levels`

Per name: spot, basis, next support, line to reclaim, hard invalidation, and
ATR(14) as % of price. For any name whose ATR exceeds ~5%, state that stops
must be **closing** stops — an intraday touch will be noise.

## 4 · Rules that keep this honest

- **Measured vs assumed.** Betas are measured from data; scenario magnitudes
  ("Brent +5%", "10Y +20bp") are chosen for illustration. Label which is which
  in the footer of every page. Never present an assumed input as a forecast.
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
