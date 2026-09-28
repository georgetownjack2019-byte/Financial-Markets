---
description: A written briefing on the day's bullish and bearish news for my holdings and what's coming this week, explaining how each story moves the price
argument-hint: [optional — "today", "week", or a ticker to focus on]
allowed-tools: Bash, Read, Write, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# ⚖️ Book Catalysts

A briefing in **plain prose** on four things:

1. What was **bullish** for my names today
2. What was **bearish** today
3. What **bullish** news is coming this week
4. What **bearish** news is coming this week

and for every item, **how it moves the price** — the actual chain from the
headline to the share price.

Read `.claude/portfolio.md` for the list of held names. That file is the name
source only: **do not report position sizes, cost basis, P&L, portfolio value
or weights anywhere in this report.** This is about the stocks, not the account.
`.claude/watchlist.md` is not used.

Scope (if given): `$ARGUMENTS`

## How to write it

**Prose, with exactly one table section.** The four news sections are written
out in paragraphs — the point is explanation, and a table cannot carry a causal
chain. Short paragraphs, one story at a time, biggest mover first.

The single exception is the **At a glance** section (below), which condenses
everything already argued in prose into two scannable tables. It adds no new
claims: every row must trace to a paragraph above it.

**Readable in five minutes.** If a section is empty, say so in a line and move
on — never pad.

Write like a good analyst explaining it out loud: name the story, say who it
hits, then walk the mechanism. "Oracle asked for relief on a data-centre
contract, which makes the delivery of its backlog look less certain, and the
backlog is the whole reason the stock carries the multiple it does" — not
"negative datacenter sentiment".

**Size the move in the stock's own terms**, in words. A name that normally moves
2% a day getting a 5% story is a big deal; the same 5% in a name that swings 6%
daily is ordinary. Say which. Percentages and price levels are fine. **Dollar
amounts tied to my holdings are not.**

## 1 · Data

FMP `/stable`, key from `FMP_API_KEY`. Per held name: `quote`,
`historical-price-eod/full` (≥ 13 months), `news/stock`,
`price-target-consensus`, `price-target-summary`, `grades-consensus`. Plus
`economic-calendar` (the week ahead, and 12 months back for reaction sizing),
`earnings-calendar`, `treasury-rates`, `news/general-latest`,
`news/crypto-latest`.

Day-over-day from **consecutive closes** — the provider's EOD `change` field is
open-to-close and must not be used. State the as-of time and whether the market
was open.

Work out quietly, for your own use and never printed as a table: each name's
typical daily move, how much of it the market explains, and how big a move each
type of scheduled release has historically produced. That is how you judge
whether a story is large or small, and it belongs in the prose as a phrase
("about twice a normal day for Oracle"), not as a figure in a grid.

When fitting factors, fit them **together in one regression**, never separately
and added — rate moves already drive much of the index, so a standalone rates
beta double-counts. On this book that error overstated rates sensitivity by
roughly 13x.

## 2 · The report

### `## Today — bullish`

Each real positive story, biggest first. Name it, say which holding it touches,
then explain the mechanism: what changed, why that changes what someone will
pay for the shares, and whether the market appeared to agree today.

### `## Today — bearish`

The same for negatives, including **unresolved carry-over** — overhangs from
earlier that got neither better nor worse. Silence is not resolution, and a
story that is still open is still a risk.

If a stock moved hard with **no story in any feed**, say exactly that and flag
it for follow-through. An unexplained large move usually means news the feed
missed or someone repositioning; pretending to explain it is worse than
admitting it.

If a stock barely moved on loud headlines, say the news was already priced
rather than implying it drove anything.

### `## This week — bullish`

Dated. Scheduled releases, earnings and live storylines that lean positive.
For each: when it lands, which holding cares, what a good outcome looks like,
and how it would reach the price. Where history gives a sense of the size, say
so in words — "Oracle has moved roughly twice its normal amount on past JOLTS
days".

### `## This week — bearish`

The same for the downside. Include the **ordinary-week risk** where it applies:
if a stock's normal weekly range already reaches a level that matters, say that
plainly — a likely touch is a base case, not a tail, and should be described
that way.

### `## At a glance — what moves what`

Two tables, and the only tables in the report. They summarise; they never
introduce a story that the prose did not already explain.

**Table one — the session's news.** Columns: `News · Stock · 🟢/🔴 · How it
reaches the price · How hard`. Order by how hard it hit, not chronologically.
The mechanism column is one line, causal, no adjectives. The strength column
carries the measured comparison — the actual percentage move, or how it
compares with that stock's normal day. Give backwards-looking disclosures a row
with an em dash for direction and "Not news" in the mechanism, so a reader
scanning only the table is not misled by them.

**Table two — the week ahead.** Columns: `When · Event · Hits · Good outcome →
price · Bad outcome → price · How hard`. Every scheduled item gets **both**
directions, because a calendar entry is two-sided until it prints. Include the
unscheduled and continuous items — a pending announcement, the level of
long-end yields — with "Any day" as the timing. Mark anything unmeasured as
**judgement** in the strength column.

### `## How these move the price`

The teaching section, and the reason the report exists. In plain language, walk
the two or three chains that actually did the work this week. Why a hot
inflation print reaches a software company at all. Why oil reaches a fee-based
energy name only weakly. Why a CFO leaving matters more at a young company than
an old one.

Call out any story that **cuts both ways across the holdings** — helps one name
and hurts another through a different channel. Explain both sides rather than
picking the convenient one.

### `## What to watch`

Three to five lines. The specific things that would change the picture: a level,
a scheduled number, a story that resolves.

## 3 · Rules that keep this honest

- **Sort the news, don't just list it.** Separate real new events from
  backward-looking disclosures — 13F filings, insider sales executed weeks
  earlier, re-reported prior stories. They trip a keyword filter and carry
  almost no information. Say so rather than reporting them as news.
- A name with **zero** articles is worth stating, especially after a big move or
  alongside thin analyst coverage.
- Name what you **cannot** judge — diffuse Fed-speaker risk, an untested
  read-through from another company's earnings — instead of inventing a number
  or a confidence you do not have.
- Never soften a bearish story by pairing it with a bullish one, and never drop
  one for balance.
- Distinguish what is **measured** from what is **assumed**, and say which.
- Small samples and weak relationships get flagged where they are used.
- If a prior page exists, open with two lines: which of last time's expected
  stories actually landed, and where the read was wrong.
- A quiet feed is not proof nothing happened — disclosures land pre-market.

## 4 · Push

Per `.claude/notion-push-rules.md` for destination and formatting — but the
body stays prose, and the no-P&L rule above overrides any table convention in
those rules. Report the title and URL. Nothing else.
