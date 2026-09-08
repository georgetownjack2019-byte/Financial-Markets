# Report commands

| Command | Report | Cadence |
|---|---|---|
| `/morning-briefing` | ☀️ Morning Entry Briefing — traffic-light watchlist, entries, event calendar | pre-open |
| `/daily-recap` | 🗓️ Daily Recap and Forward Outlook — tape, rotation, next-day + week projection | post-close |
| `/crypto-levels` | ₿ Crypto Levels — mechanical BTC/ETH entry, stop, target | daily |
| `/targets-consensus` | 📊 Targets & Consensus — analyst targets across the full watchlist | weekly / on demand |
| `/push-daily` | Push arbitrary already-written content to the same Notion page | ad hoc |
| `/company-thesis` | 🏢 Equity Research Pack — Initiate · Thesis · DCF · Comps, one name | on demand |

The first five publish as child pages of **DAILY BRIEFINGS**
(`Investment Research 投研报告 / DAILY BRIEFINGS`).

`/company-thesis` is the exception: it publishes under **4. Company Reports
个股研究** (`Investment Research 投研报告 / 4. Company Reports 个股研究`), one
page per name, and takes a ticker rather than reading the watchlist.

Shared configuration:
- `.claude/watchlist.md` — the name list and groups. Edit here; all commands follow.
- `.claude/notion-push-rules.md` — destination page id, formatting, data-integrity rules.

## API key (FMP)

The report commands read the key from the `FMP_API_KEY` environment variable.
They never take it as a command argument and never write it into a report.

**Local Claude Code** — either:
- `cp .env.example .env` and fill it in, or
- `cp .claude/settings.local.json.example .claude/settings.local.json` and fill
  it in (Claude Code loads its `env` block automatically).

Both paths are gitignored.

**Claude Code on the web** — set `FMP_API_KEY` as an environment variable on the
environment itself (claude.ai/code → environment settings), and allow
`api.financialmodelingprep.com` in the environment's network policy. Without the
network change the key has no effect: outbound requests are refused before the
key is ever used. See https://code.claude.com/docs/en/claude-code-on-the-web

**Never** paste the key into a chat message, a commit, or a Notion page. If it
happens, rotate it in the FMP dashboard.
