# Seven Names — Daily Recap · Targets & Consensus · Sentiment

**Scope:** WULF · IREN · CRCL · PLTR · SPCX · SKHY · BTC-USD
**As of:** equities — close of **Friday 4 September 2026**; BTC — **Sunday 6 September 2026**
**Generated:** 6 September 2026
**Source:** Financial Modeling Prep (quotes, OHLC, analyst grades, price targets)

Combines the `/daily-recap`, `/targets-consensus` and market-sentiment formats into one sheet,
scoped to seven names instead of the full 68-name watchlist.

---

## PART 1 — DAILY RECAP

### The tape, Friday 4 September

| Index / proxy | Close | Day |
|---|---|---|
| SPY | 770.19 | −0.39% |
| QQQ | 718.96 | +0.18% |
| **SMH (semis)** | **567.01** | **+2.61%** |

**This was not a broad rally — it was a semiconductor rally.** SPY closed red. Semis outperformed
the S&P by 300bp on 1.42× normal volume. Any read that "the market ripped" on Friday is wrong;
the money went to one sector.

### The seven

| Name | Close | Day | Volume vs 20d | Day range | Close in range | Read |
|---|---|---|---|---|---|---|
| **SKHY** | $177.00 | **+8.14%** | 1.10× | 164.61 – 177.70 | **95%** | Strongest print. Closed on the high on above-average volume — the cleanest bull bar in the book. |
| **IREN** | $44.68 | **+7.27%** | 0.79× | 41.00 – 44.75 | **98%** | Closed at the very top of its range, but on *below*-average volume. Conviction unconfirmed. |
| **WULF** | $16.51 | +1.73% | **0.66×** | 16.00 – 16.59 | 86% | Good close, weak participation. Lightest volume of the seven relative to normal. |
| **CRCL** | $102.05 | −1.14% | 0.95× | 97.10 – 102.79 | 87% | Gave back but recovered into the close. Held the $100 line. |
| **BTC** | $79,675 | −1.96% | 1.07× | 78,626 – 81,438 | 37% | Rejected at $81,438 and faded. Weekend drift to $79,846. |
| **SPCX** | $147.95 | −1.20% | **0.50×** | 147.32 – 150.85 | 18% | Half normal volume, closed near the low. No one is committing ahead of the lockup. |
| **PLTR** | $174.33 | **−4.49%** | 0.78× | 173.67 – 182.19 | **8%** | **Worst bar in the book.** Closed at 8% of range — on the low — while semis ripped. Full rejection of the intraday rally. |

### Two divergences that matter

1. **PLTR vs everything.** It fell 4.49% and closed on its low on a day semis gained 2.61%.
   Software and AI-hardware have decoupled — the same split visible in AVGO's guidance, where
   semiconductors grew 127% and infrastructure software grew 29%.
2. **Volume did not confirm the winners.** IREN (+7.27%) and WULF (+1.73%) both closed near their
   highs on **below-average volume** (0.79× and 0.66×). SKHY was the only advancer with volume
   above its 20-day average. Rallies on light volume are the ones that give back.

### Two-day context (2 Sep close → 4 Sep close)

| Name | 2 Sep | 4 Sep | Two-day |
|---|---|---|---|
| CRCL | $88.64 | $102.05 | **+15.13%** |
| IREN | $39.60 | $44.68 | **+12.83%** |
| WULF | $14.82 | $16.51 | **+11.40%** |
| SKHY | $164.98 | $177.00 | **+7.29%** |
| SPCX | $140.71 | $147.95 | **+5.15%** |
| BTC | $77,307 | $79,846 *(Sun)* | **+3.28%** |
| PLTR | $169.46 | $174.33 | **+2.87%** |

Driver: August payrolls at **+162k against +56k expected**, with the 10-year *falling* to 4.78
despite hike odds rising to ~62%. Strong growth without a long-end selloff — the combination that
lifts long-duration assets.

---

## PART 2 — TARGETS & CONSENSUS

| Name | Close | Consensus | Upside | Median | vs median | Low | High | Coverage |
|---|---|---|---|---|---|---|---|---|
| **WULF** | $16.51 | $38.50 | **+133.2%** | $34.00 | +105.9% | $28 | $72 | 14 |
| **IREN** | $44.68 | $84.00 | **+88.0%** | $87.50 | +95.8% | $50 | $100 | 15 |
| **SPCX** | $147.95 | $207.00 | **+39.9%** | $205.00 | +38.6% | $75 | $450 | 10 |
| **SKHY** | $177.00 | $234.86 | **+32.7%** | $204.00 | +15.3% | $200 | $300 | 2 |
| **PLTR** | $174.33 | $176.33 | **+1.1%** | $200.00 | +14.7% | $80 | $215 | 26 |
| **CRCL** | $102.05 | $93.36 | **−8.5%** | $100.00 | −2.0% | $37 | $150 | 15 |
| **BTC** | $79,846 | — | — | — | — | — | — | — |

### What the target sheet is actually saying

- **CRCL has run through consensus.** After a 15% two-day move it trades **8.5% above** the average
  target and 2% above the median. The sell side is now, on average, a seller. Note the targets below
  appear unrevised since 2 September — post-rally updates have not landed yet, so expect this gap to
  close via target *raises* if the price holds.
- **PLTR's consensus is exhausted at +1.1%.** With a range of $80 to $215 and a median 14.7% above
  spot, the disagreement is entirely about the multiple, not the business.
- **WULF and IREN show the widest gaps in the book** (+133% and +88%). Gaps this large historically
  close through target cuts far more often than through the price doubling. IREN's *lowest* target
  ($50) is still 12% above spot — there is no bear case published at current levels.
- **SKHY's +32.7% rests on two analysts** with a median ($204) far below the mean ($234.86). Treat
  as thin, not as signal.
- **SPCX's range is the widest on the sheet** — $75 to $450, a 6× spread. Twelve weeks of listed
  history and no valuation anchor.

**Data-integrity note.** The vendor's `grades-consensus` and `grades-historical` tables disagree on
analyst counts (e.g. SKHY: 2 vs 14; WULF: 14 vs 19). Coverage above uses the consensus table; the
sentiment section below uses the historical distribution table. Both are reported as fetched, and
neither has been reconciled.

---

## PART 3 — SENTIMENT

### Analyst rating distribution and 3-month drift

Distribution as of 1 September (Strong Buy / Buy / Hold / Sell / Strong Sell), with the June 1
reading for comparison.

| Name | 1 Jun | 1 Sep | Bull ratio | Drift |
|---|---|---|---|---|
| **WULF** | 5/12/0/0/0 | **5/14/0/0/0** | **100.0%** | Coverage +2, **zero holds or sells for four straight months** |
| **SKHY** | 2/3/1/0/0 *(1 Jul)* | **4/9/1/0/0** | **92.9%** | Coverage more than doubled post-listing |
| **SPCX** | 1/6/3/1/0 | **6/22/5/2/0** | **80.0%** | Coverage 11 → 35 as post-IPO initiations landed |
| **IREN** | 1/10/4/0/2 | **1/12/3/0/1** | **76.5%** | **Improving** — one Strong Sell dropped, holds 4 → 3 |
| **PLTR** | 2/18/11/1/1 | **1/20/9/1/1** | **65.6%** | Warming — holds 11 → 9 |
| **CRCL** | 2/11/12/2/0 | **2/11/11/3/0** | **48.1%** | **Deteriorating** — sells 2 → 3 while the stock doubled |
| **BTC** | — | — | — | no sell-side coverage |

### Recent rating actions

| Name | Last 3 months | Signal |
|---|---|---|
| **WULF** | 12 consecutive **maintains**, zero upgrades, zero downgrades since May | Frozen consensus. No one is willing to downgrade, no one has new reason to upgrade. |
| **IREN** | Six firms maintained **the day after** the $639m mining writedown (28 Aug). One upgrade (Freedom Broker, hold→buy, 6 Jul). | **The sell side did not blink on the impairment.** Strongest sentiment signal in the book. |
| **CRCL** | Mizuho **downgraded 14 Jul then upgraded 31 Jul**. Wolfe at Underperform, Morgan Stanley at Underweight, Susquehanna and Goldman Neutral. Compass Point sell→neutral 1 Jul. | **The only genuinely contested name.** Real institutional bears with published sell ratings. |
| **PLTR** | Deutsche Bank hold→buy on the 4 Aug print; DA Davidson neutral→buy 2 Jul. Eight firms maintained on earnings day. | Slow, steady warming — but three sells persist. |
| **SPCX** | Argus hold→buy 7 Aug. Oppenheimer maintained Outperform 2 Sep. | Coverage build-out dominates; too new for a real trend. |
| **SKHY** | **Only two rating actions on record** — Barclays 30 Jul, Needham 24 Aug. Both maintains. | Almost no sell-side engagement. Price is running ahead of coverage. |

### Technical sentiment — position in the moving-average stack

| Name | Above / available MAs | Extension over 50-day | State |
|---|---|---|---|
| **CRCL** | **5 of 5** | **+40.8%** | 🔴 Most extended reading in the book. Doubled off its Feb low. |
| **BTC** | **5 of 5** | +15.1% | 🟢 Clean uptrend, first pullback not yet delivered. |
| **SPCX** | 3 of 3 *(no 100/200)* | +8.8% | 🟡 Above what it has; lockup supply ahead. |
| **IREN** | 3 of 5 | +11.1% | 🟡 Reclaimed 10/20/50-day; 200-day 2.1% overhead. |
| **PLTR** | 3 of 5 | +16.3% | 🟡 Above 50/100/200, **below 10 and 20** — pullback inside an uptrend. |
| **SKHY** | 2 of 2 *(no 50/100/200)* | — | 🔴 +10.6% over 20-day, **9.1% from all-time high**. |
| **WULF** | 2 of 5 | −10.4% | 🔴 Repairing, but **50-day sits 3.1% below the 200-day — death cross intact**. |

### Composite read

| Name | Sell-side | Technical | Combined | The tension |
|---|---|---|---|---|
| **WULF** | 🟢 unanimous | 🔴 weakest structure | 🟡 | 100% bullish coverage against a stock 44.7% off its high and below three averages. One of the two is wrong. |
| **IREN** | 🟢 improving | 🟡 repairing | 🟢 | Best alignment in the book — sentiment improving *and* structure repairing. Volume has not confirmed. |
| **CRCL** | 🔴 contested | 🔴 extended | 🔴 | Trades above consensus, most stretched chart, only name with real published bears. |
| **PLTR** | 🟡 warming | 🟡 mixed | 🟡 | Consensus upside exhausted at +1.1%; closed Friday on its low. |
| **SPCX** | 🟢 positive | 🟡 fine | 🟡 | Ratings constructive, but a ~6× float expansion is ahead and volume is halving. |
| **SKHY** | 🟢 but thin | 🔴 extended | 🟡 | Strongest tape, weakest coverage. Two rating actions ever. |
| **BTC** | — | 🟢 | 🟢 | Above every average; ETF flows are the variable to watch, not analysts. |

### Sentiment observations worth carrying

1. **Nobody is bearish on WULF or IREN, on paper.** WULF has zero holds and zero sells across 19
   analysts; IREN's lowest target is 12% above spot. In both cases the published sell side offers
   no downside case at all — which means any negative catalyst has no anchor to fall back to.
2. **CRCL is the only name with genuine two-sided institutional opinion** — Wolfe Underperform,
   Morgan Stanley Underweight, three sells. That is healthier than unanimity, but it also means
   the stock has run 15% into an audience that is, on average, no longer buying.
3. **SKHY's price is ahead of its coverage.** Two rating actions on record against an 8.14% Friday
   move and a position 9.1% from an all-time high.
4. **The volume tell.** Of Friday's three advancers, only SKHY traded above its 20-day average.
   IREN and WULF closed near their highs on 0.79× and 0.66× volume respectively.

---

## Watch next

| Date | Event | Affects |
|---|---|---|
| **Thu 10 Sep** | PPI · **Oracle** (after close) · **Adobe** (after close) | IREN, WULF (Oracle) · PLTR (Adobe) |
| **Fri 11 Sep** | **August CPI** — headline est +0.4% m/m, core +0.2% | All seven |
| **Wed 16 Sep** | **FOMC** (3.75% → est 4.00%, ~62% priced) · **Circle Arc mainnet** | All seven; CRCL doubly |
| **Fri 18 Sep** | Quad witching | PLTR, SPCX |
| **late Sep** | SPCX employee lockup tranches — float ~6× | SPCX |
| **Wed 30 Sep** | Micron FQ4 | SKHY |

**The single variable:** the 10-year at **4.78**. Last week showed a priced hike with a stable long
end is not a duration shock. A 10-year at 5.00 is.

---

_Data fetched from Financial Modeling Prep. Equity figures are the 4 Sep 2026 close; BTC is 6 Sep 2026.
Moving averages are simple averages of daily closes over a rolling year. Analyst tables are reported
as fetched and unreconciled where vendor sources disagree. Traffic lights and composite reads are
subjective judgements, not vendor data._

_Research and mechanical levels only — not personalized investment advice._
