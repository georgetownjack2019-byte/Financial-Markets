# Shared push rules (referenced by the daily report commands)

## Destination

- **Parent page:** `DAILY BRIEFINGS`
- **Page ID:** `3cf9de12-4ade-8005-8cd6-d023cb6fa071`
- **URL:** https://www.notion.so/3cf9de124ade80058cd6d023cb6fa071
- **Location:** `Investment Research 投研报告 / DAILY BRIEFINGS`

Always create a **new child page** under that parent via `notion-create-pages`
with `parent: { type: "page_id", page_id: "3cf9de124ade80058cd6d023cb6fa071" }`.
Never write into the parent page itself.

## Before creating

`notion-fetch` the parent and check for a page with the same title for today.
- I explicitly asked for an update → update that page with `notion-update-page`.
- Otherwise → append a qualifier to the new title (`(update 2)`, `(real-time)`,
  `(intraday)`) rather than overwriting.

## Formatting

- Notion-flavored Markdown. `##` for sections, `###` for sub-sections. No `#`
  H1 — the page title is the heading.
- Tables use the `<table header-row="true">` form with one `<td>` per cell.
- Prices carry their currency symbol (`$`, `€`). Escape `$` as `\$` in table
  cells so Notion does not read it as an equation delimiter.
- Percentages always signed (`+5.59%`, `-1.1%`).
- Bold the number that matters (entry level, verdict), not whole rows.

## Data integrity — non-negotiable

- Every number must come from the fetched data. Never estimate, extrapolate,
  round to a "nicer" figure, or carry a number over from a previous day's
  report.
- If a field is unavailable, print `—`. Do not guess and do not omit the row.
- State the as-of timestamp and the source in the footer of every page. Prices
  are real-time via Financial Modeling Prep — say so, with the actual minute,
  and never describe them as delayed or as a prior close when they are not.
- A row whose data came from a fallback is marked in place: `†` for a
  ~15-min-delayed native listing, `‡` for a US ADR proxy quoted in USD. Footnote
  every marker the page uses, naming the proxy. Never quietly present a proxy as
  the native line.
- If the data fetch fails for more than ~20% of the watchlist, stop and report
  the failure instead of publishing a half-empty page.

## Disclaimer

Any page containing price levels, entries or targets ends with:

`_Research and mechanical levels only — not personalized investment advice._`

## Pushing a long page

A full watchlist briefing runs ~60 KB and does not go through
`notion-create-pages` in one call. Create the page with the first section, then
append the rest with `notion-update-page` (`command: "insert_content"`,
`position: {"type": "end"}`), one `##` section per call. Sections are the split
point — never cut a `<table>` across two calls.

`₿` and other currency signs are rejected as page icons — Notion only accepts
emoji there. Keep the sign in the title and pick an emoji for the icon
(`/crypto-levels` uses `🪙`).

## After pushing

Report the page title and URL. Nothing else.
