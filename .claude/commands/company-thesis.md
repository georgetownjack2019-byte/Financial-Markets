---
description: Generate and push a single-company Equity Research Pack (Initiate · Thesis · DCF · Comps) to Notion
argument-hint: <TICKER> [optional — as-of date, or "update" to revise today's existing pack]
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, mcp__Notion__notion-fetch, mcp__Notion__notion-create-pages, mcp__Notion__notion-update-page
---

# 🏢 Company Thesis — Equity Research Pack

One page, four memos, on a single name: **① Initiating Coverage · ② Investment
Thesis · ③ DCF Valuation · ④ Comparable Company Analysis.**

Read `.claude/notion-push-rules.md` for formatting and data-integrity rules —
binding here **except for the destination**, which is overridden below.
`.claude/watchlist.md` is context only; this command takes any ticker, on or
off the watchlist.

Subject: `$ARGUMENTS`

## Destination (overrides `notion-push-rules.md`)

- **Parent page:** `4. Company Reports 个股研究`
- **Page ID:** `3bb9de12-4ade-81e5-9c19-fb7b28cc983d`
- **Location:** `Investment Research 投研报告 / 4. Company Reports 个股研究`

New child page via `notion-create-pages` with
`parent: { type: "page_id", page_id: "3bb9de124ade81e59c19fb7b28cc983d" }`.
Never write into the parent. Before creating, `notion-fetch` the parent and
check for an existing pack on this ticker: if I asked for an update, revise
that page; otherwise supersede it with a fresh dated page and leave the old one
in place (the parent has an `Archive` child for retired packs).

## Title & framing

- Title: `<TICKER> — <Company Name> — Equity Research Pack (Initiate · Thesis · DCF · Comps) <YYYY-MM-DD>`
- No page icon.
- Open with an H1 — `# <Company Name> (<EXCHANGE>: <TICKER>) — Thesis Analysis Pack`
  — then a quote block carrying: the four-memo line, **Date**, **Data as of**
  (the close the numbers come from), **Currency**, the **Rating · 12-mo target ·
  current price · implied total return** line, and a **One-liner** that states
  the whole call in one sentence.
- Then a `## Contents` list of the four parts, `---` between parts.

## Data rules

- Financials **dual-sourced** — stockanalysis.com / macrotrends / SEC filings /
  company IR. Any two-source discrepancy >1% is flagged inline, not averaged
  away. Market data (price, market cap, EV, shares) as of the stated close.
- Every forward figure is marked `(est.)` or `(estimate)`. Never present an
  estimate as reported fact.
- **Sanity check, always printed:** price × shares ≈ market cap. Show the
  arithmetic and say whether it reconciles.
- Report native currency (€ for MC.PA / RMS.PA / SHELL.AS; EUR for a European
  DCF). For an ADR, state the ratio explicitly (`1 ADR = 5 ordinary (2330.TW)`)
  and price the ADR.
- Note the issuer structure up front where it changes the framing — a C-corp is
  framed on P/E, EV/EBITDA, FCF yield and total shareholder yield; an MLP/LP on
  distributions, K-1 and DCF/EV per unit.
- A source figure that is obviously spurious (e.g. a reported beta of 0.17 for
  a supermajor) is overridden with a reasoned estimate and the override is
  stated in the cell.

## Part 1 — Initiating Coverage

`## Rating: <BUY / HOLD / NEUTRAL / OVERWEIGHT> — 12-Month Target: <$X>` then a
two-column table: current share price · 12-month price target · implied price
change · dividend yield · **implied 12-mo total return** · market cap ·
enterprise value · shares outstanding · net debt · total shareholder yield
(div + buyback).

Follow with the sanity check, a `*Why <RATING>, not <the obvious alternative>:*`
paragraph, then:

- `## Business Overview` — what it does, segment-by-segment with FY earnings per
  segment, and how the segments interact.
- `## Investment Thesis (Pillars)` — numbered, 4–6 pillars.
- `## Industry & Competitive Moat` — (a) scale, (b) asset/resource quality,
  (c) integration or switching costs, (d) balance sheet — then name the
  vulnerability plainly.
- `## Financial Profile` — table, FY vs TTM columns: revenue · EBITDA (est.) ·
  EBIT · net income · diluted EPS · operating cash flow · capex · free cash flow ·
  ROE · net debt/EBITDA · credit rating.
- `## Valuation Summary` — where it trades vs peers and vs its own history, and
  what the forward multiple is silently assuming.
- `## Key Risks` — bulleted, most decision-relevant first.
- `## Catalysts` — bulleted, with direction (bullish/bearish).
- `## Management & Capital Allocation` — named CEO/CFO, tenure, the actual
  capital-allocation record.

## Part 2 — Investment Thesis

`## One-Line Thesis` · `## Bull Case` · `## Bear Case` ·
`## Key Debate — <the single question the call turns on>` (state the bull view,
the bear view, then **Our read:**) · `## Catalysts & Timeline` (two-column
table: Ongoing / Next 6–12 mo / named years / long-run) ·
`## What Would Change My Mind` (explicit upgrade triggers, then downgrade
triggers) · `## Entry Discipline` (position size, starter vs full weight, the
price band to accumulate in, and what to do if already held).

## Part 3 — DCF Valuation Model

1. `## 1. Key Inputs & Assumptions` — three columns: Input · Value · Basis.
2. `## 2. Cost of Capital (CAPM)` — risk-free · levered beta · ERP ·
   **cost of equity** (show the arithmetic) · pre-tax and after-tax cost of debt ·
   equity/debt weights · **WACC** (show the arithmetic).
3. `## 3. Method A — Unlevered DCF (base case, EV build)` — a 5-year projection
   table (EBITDA → less D&A → EBIT → less tax → NOPAT → plus D&A → less capex →
   less ΔWC → **unlevered FCF**), then terminal value with the g/WACC used and
   an **exit EV/EBITDA cross-check**, then the bridge: PV of FCF + PV of TV =
   EV − net debt = equity ÷ shares = **value/share**.
4. `## 4. Method B — <scenario axis> scenario analysis` — flex the one variable
   the value actually turns on (oil price, AI capex, drug pipeline, rates).
   Columns: Scenario · normalized FCF base · WACC/g · value/share · Read. Include
   a **probability-weighted** row and state which case the market price implies.
5. `## 5. Sensitivity` — WACC × terminal-growth grid, base cell bolded, with a
   sentence on which corner of the grid is needed to justify the market price.
6. `## 6. Conclusion & Implied Value` — a method-vs-value table (DCF base ·
   scenario blend · comps · **blended intrinsic**), then reconcile the published
   12-month target against intrinsic value and say why they differ.

## Part 4 — Comparable Company Analysis

`## Peer Set & Rationale` (two columns: peer · why included — 4–6 peers, each
justified) · `## Multiples Table` (subject bolded in its own column: market cap ·
P/E TTM · fwd P/E · EV/EBITDA · dividend yield · total shareholder yield ·
net debt/EBITDA · ROE · credit rating) · peer mean/median and the subject's
premium or discount to it · `## Where <TICKER> Trades vs. Peers — and Why`
(is the premium deserved, and is its *size* deserved — distinguish the two) ·
`## Implied Value Range` (justified multiple → implied EV → implied equity →
value/share, laddered from no-premium to current market) · `## Conclusion`
(the relative-value read, and the cheaper way to get the same exposure if there
is one).

## Formatting

Per `.claude/notion-push-rules.md`: `##` sections, `###` sub-sections,
`<table header-row="true">` tables, `\$` escaped in cells, percentages signed,
bold only the number that matters. Each of the four parts ends with its own
disclaimer line:

`*Not investment advice. Informational only; not a recommendation or personalized financial advice. Items marked "(estimate)"/"(est.)" are estimates and should be independently verified. All figures <CCY>. The author is not a licensed investment adviser.*`

## Push

Create the child page, then report the title and URL. Nothing else.
