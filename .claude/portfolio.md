# Portfolio — follow-up universe

The names `/portfolio-followup` tracks. Two tiers: **held** (a real position,
with cost basis) and **candidate** (watched, not yet bought).

Edit this file when a position opens, closes or changes size — the command
reads it, so the report follows automatically.

## 🟢 Held

| Ticker | Shares | Avg cost | Lots | Opened |
|---|---|---|---|---|
| ORCL | 100 | 154.00 | 50 @ 155.00 · 50 @ 153.00 | Sep 2026 |
| CRCL | 50 | 94.50 | 50 @ 94.50 | Sep 2026 |

## ⚪ Candidate

| Ticker | Why watched |
|---|---|
| CRM | Dreamforce / Claudeforce–Anthropic cycle; most extended of the four |
| LNG | Cleanest sell-side book on the list; lowest ATR; LNG supply cycle |

## Notes

- Cost basis is **average cost** unless the lots column says otherwise. Where
  lots differ, report P&L on the blended average and note the per-lot split.
- A candidate has no cost basis: report levels and consensus, leave every P&L
  cell `—`. Do not invent an entry price.
- Moving a name between tiers is an edit here, not a change to the command.
- This file contains position data. If you would rather not commit cost basis,
  add `.claude/portfolio.md` to `.gitignore` and keep it local — the command
  degrades to candidate-only reporting for any name it cannot read.
