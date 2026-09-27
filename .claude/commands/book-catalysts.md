---
description: Today's bullish and bearish news for the held book and the week's upcoming news, each with the mechanism that moves the price and the dollar impact
argument-hint: [optional — "today" for the news only, "week" for the forward half, or a ticker to focus on]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ⚖️ Book Catalysts

**News in, price impact out.** Four questions, in this order:

1. What was **bullish** for my names today, and how much is it worth?
2. What was **bearish** today, and how much did it cost?
3. What **bullish** news is coming this week?
4. What **bearish** news is coming this week?

Every item is a real news story or a dated scheduled event — never an abstract
factor. Every item carries the **mechanism** (one clause on why it moves the
price) and the **size** (percent and dollars on the actual position).

Read `.claude/portfolio.md` for names and cost basis, and
`.claude/notion-push-rules.md` for destination and formatting. Both binding.
Held names only. `.claude/watchlist.md` is not used.

Scope (if given): `$ARGUMENTS`

**Keep it short enough to read in five minutes.** Lead with the biggest dollar
item in each direction. If a section has nothing in it, say "nothing" in one
line rather than padding it.

## Title & icon

- Title: `⚖️ Book Catalysts — <Ddd DD Mon YYYY>`, icon `⚖️`
- Existing page for the day → append `(update 2)` / `(intraday)`. Never
  overwrite.

## 1 · Data

FMP `/stable`, key from `FMP_API_KEY`. Per held name: `quote`,
`historical-price-eod/full` (≥ 13 months), `news/stock`,
`price-target-consensus`, `price-target-summary`, `grades-consensus`. Plus
`economic-calendar` (the week ahead, and 12 months back for reaction sizing),
`earnings-calendar`, `treasury-rates`, `news/general-latest`,
`news/crypto-latest`.

Day-over-day from **consecutive closes**. The provider's EOD `change` field is
open-to-close and must not be used. State the as-of time and whether the market
was open.

## 2 · The sizing model, fitted once and used everywhere

Fit **one multivariate OLS per name** — index, 10-year yield in bp, and oil or
crypto where relevant — in a single regression.

**Never fit the factors separately and add them.** Rate moves already drive much
of what the index does, so a standalone rates beta re-charges the book for the
equity selloff those rates caused. On this book that error overstated rates
sensitivity roughly 13x (−$1,118 per 25bp against a true −$84). Always quote the
rates coefficient as "holding the index constant".

Keep from the fit, for use in the news tables:

- **Factor betas** → sizes macro and sector news.
- **R² and residual SD per name** → sizes company news. A story worth 1σ of that
  name's residual is worth `residual SD × position value`.
- **Event multiples** — median absolute move on past occurrences of each
  scheduled release type, over its baseline → sizes the week's calendar.

R² is also reported to the reader, because it sets how much any macro
explanation is worth: where the market explains under ~30% of a name's daily
variance, say so and lean on the company news instead.

## 3 · The report

### `## Today — 🟢 bullish`

One row per story, biggest dollar impact first:

`News · Name · Mechanism (one clause) · Move % · $ impact`

Mechanism must be concrete and causal — "Berkshire disclosed a \$38bn stake,
which sets a floor under the float", not "positive sentiment".

### `## Today — 🔴 bearish`

Same shape.

### `## Did the price agree?`

One compact table: each name's actual move split into `market · rates ·
residual`. This is a **check on the news sections, not a feature of its own** —
keep it to the table plus at most two lines.

Three outcomes to call out explicitly:

- **Big residual, story found** → the news above explains the day. Good.
- **Big residual, no story** → say so plainly. An unexplained ±1.5σ move means
  there is news the feed missed, or someone is repositioning. Flag it for
  follow-through the next session.
- **Small residual on a day of loud headlines** → the news was already priced.
  Say that rather than implying it moved the stock.

### `## This week — 🟢 bullish`

Dated. Scheduled releases and earnings with a consensus, plus live unscheduled
storylines that could break either way but currently lean positive.

`When · Event or story · Name(s) · Why it helps · Expected move · $ if it lands`

### `## This week — 🔴 bearish`

Same. Include the **ordinary-week risk**: cross each name's 5-day empirical
range against its support, and name any position whose normal weekly downside
already breaks a level. A 75% chance of touching support is a base case, not a
tail, and must be described that way.

### `## How the news reaches the price`

Short. For each channel actually used above, one or two sentences on the
transmission — why a hot inflation print reaches a software company at all, why
oil reaches an energy name only weakly through a fee-based model. **This is the
section that teaches, so write it in plain language and skip the jargon.**

Flag any item that **inverts**: a story that helps one position through one
channel but costs the book more through another. Oil is the standing example —
a crude spike pays the energy name via its Brent beta and charges the
rate-sensitive majority several times over through inflation and yields. Show
the netting.

### `## Levels and what to watch`

Per name: spot, basis, next support, line to reclaim, and the **empirical
probability of touching each within five sessions**, computed from actual
intraday paths rather than a normal assumption. Then three to five lines on
what would change the picture.

## 4 · Rules that keep this honest

- **Measured vs assumed.** Betas, R², residual SDs and touch probabilities are
  measured; scenario sizes ("Brent +5%") are chosen for illustration. Label
  which is which. Never present an assumed input as a forecast.
- **Sort the news, don't just list it.** Separate genuine new events from
  backward-looking disclosures — 13F filings, insider sales executed weeks
  earlier, re-reported prior stories. These trip a keyword filter and carry
  almost no information. Say so explicitly rather than reporting them as news.
- A name with **zero** articles is a finding, especially after a large move or
  alongside thin analyst coverage. State it.
- **Unresolved carry-over**: overhangs from earlier that got neither better nor
  worse still belong in the bearish section. Silence is not resolution.
- Name what you **cannot** size — diffuse Fed-speaker risk, a first-time
  read-through from another company's earnings — rather than inventing a number.
- Report losing rows at full size. Never net a bad item against a good one, and
  never drop a bearish row for balance.
- Small event samples (n < 10) and weak fits get flagged at the point of use.
- If a prior page exists, open with two lines scoring it: which called items
  fired, and where the sizing was wrong.
- A quiet news feed is not proof nothing happened — disclosures land pre-market.

## 5 · Push

Per `.claude/notion-push-rules.md`. Report the title and URL. Nothing else.
