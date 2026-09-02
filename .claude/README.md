# Daily report commands

| Command | Report | Cadence |
|---|---|---|
| `/morning-briefing` | ☀️ Morning Entry Briefing — traffic-light watchlist, entries, event calendar | pre-open |
| `/daily-recap` | 🗓️ Daily Recap and Forward Outlook — tape, rotation, next-day + week projection | post-close |
| `/crypto-levels` | ₿ Crypto Levels — mechanical BTC/ETH entry, stop, target | daily |
| `/targets-consensus` | 📊 Targets & Consensus — analyst targets across the full watchlist | weekly / on demand |
| `/push-daily` | Push arbitrary already-written content to the same Notion page | ad hoc |

All five publish as child pages of **DAILY BRIEFINGS**
(`Investment Research 投研报告 / DAILY BRIEFINGS`).

Shared configuration:
- `.claude/watchlist.md` — the name list and groups. Edit here; all commands follow.
- `.claude/notion-push-rules.md` — destination page id, formatting, data-integrity rules.
