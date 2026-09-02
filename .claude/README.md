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
- `scripts/market_data.py` — the real-time data layer every command pulls from.

## Data layer — `scripts/market_data.py`

Real-time quotes from **Financial Modeling Prep**, plus the indicators the
reports need, computed off 3 years of daily bars with the live print spliced in
as today's in-progress bar. Standard library only — `yfinance` is optional and
used solely as a fallback.

```bash
python3 scripts/market_data.py selftest                       # key + connectivity
python3 scripts/market_data.py watchlist --out out/watchlist.json
python3 scripts/market_data.py backdrop  --out out/backdrop.json
python3 scripts/market_data.py crypto    --out out/crypto.json
python3 scripts/market_data.py calendar --days 90 --out out/calendar.json
```

A full 67-name watchlist pull takes ~90s and stays inside FMP's per-minute cap;
raise `FMP_RATE_LIMIT` if your plan allows more.

**Sourcing chain.** Each row reports the `source` that produced it, and the
reports label the row accordingly:

1. `FMP real-time` — the live quote. Everything US-listed, plus SK hynix,
   spot crypto, `^GSPC` / `^IXIC` / `^DJI` / `^N225` / `^HSI` / `^VIX`,
   S&P futures and Treasury constant-maturity rates.
2. `yfinance (~15-min delayed)` — the native listing, when FMP's plan returns
   402 for it. Reported with a `†` marker. Yahoo is unreachable from the
   Claude Code web sandbox, so this rung only fires locally.
3. `FMP real-time (ADR proxy)` — the US ADR, in USD, when neither of the above
   resolves: `MC.PA → LVMUY`, `RMS.PA → HESAY`, `SHELL.AS → SHEL`. Reported
   with a `‡` marker and never currency-converted.

Anything that resolves to nothing stays `null` so the report prints `—`.

**Known gaps on the current FMP plan** — all print `—`, never an estimate:
Nasdaq futures, the high-yield OAS spread, and analyst fair-value estimates.
Shanghai and the dollar index fall back to labelled proxies (`ASHR`, `UUP`).

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
`financialmodelingprep.com` in the environment's network policy. Without the
network change the key has no effect: outbound requests are refused before the
key is ever used. See https://code.claude.com/docs/en/claude-code-on-the-web

To get the delayed-native-listing rung working on the web too, also allow
`query1.finance.yahoo.com`, `query2.finance.yahoo.com` and `fc.yahoo.com`. Until
then MC.PA, RMS.PA and SHELL.AS resolve through their ADRs in USD.

**Never** paste the key into a chat message, a commit, or a Notion page. If it
happens, rotate it in the FMP dashboard.
