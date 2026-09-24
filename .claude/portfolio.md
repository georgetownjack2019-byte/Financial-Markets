# Portfolio — follow-up universe

The names `/portfolio-followup` tracks. Two tiers: **held** (a real position,
with cost basis) and **candidate** (watched, not yet bought).

Edit this file when a position opens, closes or changes size — the command
reads it, so the report follows automatically.

## 🟢 Held

| Ticker | Shares | Avg cost | Lots | Opened |
|---|---|---|---|---|
| ORCL | 100 | 154.00 | 50 @ 155.00 · 50 @ 153.00 | Sep 2026 |
| CRCL | 80 | 83.00 | 80 @ 83.00 | Sep 2026 |
| LNG | 50 | 267.00 | 50 @ 267.00 | Sep 2026 |
| GOOGL | 40 | 340.00 | 40 @ 340.00 | Sep 2026 |

Book cost **$48,990**. Weights at the 24 Sep close: ORCL 28.5%, LNG 28.2%,
GOOGL 28.0%, CRCL 15.2%.

## ⚪ Candidate

| Ticker | Why watched |
|---|---|
| CRM | Dreamforce / Claudeforce–Anthropic cycle; the momentum name of the group |

## Notes

- Cost basis is **average cost** unless the lots column says otherwise. Where
  lots differ, report P&L on the blended average and note the per-lot split.
- A candidate has no cost basis: report levels and consensus, leave every P&L
  cell `—`. Do not invent an entry price.
- Moving a name between tiers is an edit here, not a change to the command.
- This file contains position data. If you would rather not commit cost basis,
  add `.claude/portfolio.md` to `.gitignore` and keep it local — the command
  degrades to candidate-only reporting for any name it cannot read.

## Ledger history

- **23 Sep 2026** — CRCL restated to 80 @ 83.00 (previously recorded 50 @ 94.50);
  LNG opened at 50 @ 267.00 and promoted from candidate to held; ORCL unchanged.
- **24 Sep 2026** — GOOGL opened at 40 @ 340.00, taken after the close back above
  the 200-day (337.85). The add cuts ORCL from 40.8% to 28.5% of the book.
