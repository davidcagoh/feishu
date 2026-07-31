# Dad's Stock Trading Strategy — Full Brief

*Compiled from direct messages, April 19 2026. Purpose: enable agents to reproduce, automate, optimise, or assist this strategy.*

---

## 1. Strategy Overview

**Style:** Discretionary momentum-quality investing. Sometimes called "momentum value investing" by the trader, though it is closer to **growth-quality momentum with tactical risk management**.

**Core loop:**
1. Identify sectors moving up (macro theme scan)
2. Screen for quality stocks within those sectors using fundamentals
3. Confirm with technical analysis (trend + momentum indicators)
4. Validate with valuation and analyst sentiment
5. Cross-check short interest
6. Buy in pre-market or near close
7. Hold until fundamentals deteriorate, technical signals reverse, or stop-loss triggers

**Philosophy evolution:**
- Pre-COVID: pure buy-and-hold
- Post-COVID: active rotation with risk management (stop-losses, sector tilts)
- Aspiration: move toward longer-term holds (10-year horizon) to reduce news-reading burden

---

## 2. Universe & Constraints

| Parameter | Value |
|---|---|
| **Markets** | US-listed stocks (primary), Singapore stocks (SGX, secondary) |
| **Chinese stocks** | Avoided — data quality too low unless dual-listed on US exchanges |
| **Max holdings** | 15 stocks simultaneously |
| **Min market cap** | ~USD 10 billion |
| **Currency** | USD (US holdings), SGD (SG holdings) |
| **Preferred sector** | Technology (stated "circle of competence") |
| **Excluded** | Crypto — never touched |

**Singapore holdings (long-term, never sell):**
- Sheng Siong (SGX: OV8) — grocery retail
- DBS (SGX: D05) — bank

---

## 3. Idea Generation — Sector Scan

**Primary tool:** MooMoo desktop → Markets → "Saturn icon" → US Investment Themes

**Process:**
1. Check what themes are moving up
2. Check what themes are moving down
3. Recent observed rotations: Semiconductors ↔ Oil & Gas
4. Stick to familiar sectors first (tech); consider adjacent themes secondarily
5. Macro overlays: geopolitical events (e.g. ceasefire breaks → rotate to oil/gas, LNG, helium, fertiliser)

**Theme examples mentioned:**
- 5G (Marvell / MRVL)
- Semiconductors (NVDA, AVGO, MU, SNDK)
- Cruise lines, Silver (observed but outside circle of competence)
- Oil & Gas / LNG
- Helium (Linde / LIN)
- Fertiliser (CF Industries / CF)

**Rule:** Do not concentrate all bets on one theme.

---

## 4. Stock Selection — Fundamental Screen

All data pulled from **MooMoo** (Financials tab → Key Indicators).

### 4a. Hard Filters (Eliminate if failed)

| Criterion | Threshold | Notes |
|---|---|---|
| P/E ratio | Not 3-digit (< 100) | Growth stocks may be exception if YoY growth is 3-digit |
| Market cap | ≥ USD 10 billion | Avoids micro/small caps |
| ROE | ≥ 15% | Key metric; red (falling YoY quarterly) → sell signal |
| Equity ratio (Debt ratio) | ≤ 50% | Signals financial leverage risk |
| Free cash flow (absolute) | Positive | From Financials tab |

### 4b. Soft Filters (Positive weight, not hard cutoff)

| Metric | Desired Direction |
|---|---|
| Gross margin | Positive and stable/growing |
| Net margin | Positive and stable/growing |
| ROA | Positive; falling YoY quarterly is a sell signal |
| ROIC | Positive; falling YoY quarterly is a sell signal |
| Free cash flow (trend) | Increasing YoY quarterly |

**Scoring logic:** Majority of above indicators must be positive. Not all need to pass — especially for growth stocks where some metrics may temporarily be weak. A 3-digit+ YoY quarterly increase on any metric is a strong positive.

**Sell trigger from fundamentals:** ROE, ROA, ROIC all turning red (falling YoY quarterly). Explicitly mentioned example: BYD prompted a sell on this basis.

---

## 5. Technical Analysis Screen

All data from **MooMoo** chart view.

| Indicator | Rule |
|---|---|
| 50-day MA | Buy when price has just started to move up through or near this level |
| 200-day MA | Contextual — buy ideally when price is above or crossing up |
| RSI | Dangerous to buy when RSI has hit 80+ **twice**; single hit to 80 is a caution |
| Entry timing | Look for early uptrend, not extended moves |

**Preferred entry:** Stock that has just begun moving up — catch the trend early, not at peak.

---

## 6. Valuation & Sentiment Screen

**Tool:** MooMoo → Valuation tab

| Data point | Usage |
|---|---|
| Analyst ratings | Read; factor into decision |
| Morningstar research | Read; prefer wide or narrow moat stocks |
| Company valuation score | Avoid if flagged as overvalued |
| P/E, P/B, P/S ratios | Contextual check — reinforces or overrides momentum signal |
| Moat rating | Wide or narrow moat preferred; no moat is a negative |

**Tool:** Tiger → Analysis tab (for short data)

| Data point | Usage |
|---|---|
| Short ratio | Prefer low short interest; high short interest is a warning |
| Short squeeze potential | Exception: may buy heavily shorted stock if squeeze thesis is strong |

---

## 7. News & Catalyst Monitoring

**Process:** Read news on any stock under consideration before buying.

**Buy-side news use:**
- Confirms thesis (positive catalyst, product launch, contract win)
- Identifies upcoming catalysts (earnings, FDA approval, etc.)

**Sell-side news use:**
- Adverse news triggers review and potential exit
- Earnings misses are evaluated against unrealised gain buffer (see Exit Rules)

**Gap / limitation:** Reading all relevant news manually is time-consuming and stated as the primary burden the trader wants to automate.

---

## 8. Entry Execution

**Timing:**
- Buys executed **1 hour before market open** (pre-market, ~08:30 ET) or **1 hour before market close** (~15:00 ET)
- "Buy the dip" — opportunistic entries on significant intraday pullbacks

**Market open rule (implied):** Pre-market activity watched; react to overnight news or pre-market moves before regular session.

**Position sizing:** Not explicitly stated; implied equal or near-equal weight across ≤15 holdings.

---

## 9. Exit Rules

### 9a. Stop-Loss (Hard)

| Trigger | Action |
|---|---|
| Stock drops > 5% in a single day | Sell (or review immediately) |
| Stock falls > 5% below personal buy price | Sell |

*Note: these are stated as the rules; in practice there is some discretion — e.g. if unrealised gain exists, the 5%-below-buy-price rule effectively gives more downside room.*

### 9b. Fundamental Deterioration (Soft sell signal)

- ROE, ROA, ROIC all falling YoY quarterly (turning "red")
- Stated example: sold BYD when these turned red

### 9c. Profit-Taking

- Take profit opportunistically (mentioned: took profit on MU, SNDK)
- No explicit rule stated — discretionary based on extended gains

### 9d. Adverse News

- Material adverse news triggers a sell review
- Not automatic — weighed against position's unrealised gain

### 9e. Earnings Reaction

- Large single-day drop on earnings (e.g. NFLX −9% on earnings) → hold if unrealised gain covers the loss
- Will sell if price subsequently falls 5% below buy price

---

## 10. Portfolio Management & Rebalancing

- Max 15 stocks; actively managed
- Sector diversification enforced (no single-theme concentration)
- Rotation driven by macro themes and momentum (sectors moving up vs. down)
- "Buy back" discipline: tendency to *not* buy back after selling on a dip, then missing the recovery (acknowledged as a recurring mistake — e.g. DeepSeek, Trump tariff events)
- Hold through volatility if conviction is high (held through Iran war outbreak, rebalanced but did not fully exit)

---

## 11. Current Holdings (as of April 19 2026)

| Ticker | Company | Sector |
|---|---|---|
| MRVL | Marvell Technology | Semiconductors / 5G |
| GOOGL | Alphabet | Tech / AI |
| NVDA | NVIDIA | Semiconductors / AI |
| AVGO | Broadcom | Semiconductors |
| GEV | GE Vernova | Energy / Power |
| NRG | NRG Energy | Utilities / Energy |
| META | Meta Platforms | Tech / Social |
| AMZN | Amazon | Tech / E-commerce / Cloud |
| NFLX | Netflix | Streaming / Entertainment |

*Plus permanent SGX holds: Sheng Siong, DBS (not counted against the 15-stock limit, implied)*

**Recent activity:**
- Took profit: MU (Micron), SNDK (SanDisk/WDC)
- Under watch: NFLX (dropped 9% on earnings; hold if above buy price −5%)
- Watchlist rotation: oil/gas (LNG), helium (LIN), fertiliser (CF) — geopolitical thesis (ceasefire break)

**Portfolio health:** Within ~1% of all-time high as of April 19 2026.

---

## 12. Tools Used

| Tool | Platform | Primary Use |
|---|---|---|
| MooMoo | Desktop (primary) | Sector themes, financials, charts, valuation, news |
| MooMoo | iOS (secondary) | Mobile access |
| Tiger | iOS | Short ratio / short interest data |

**MooMoo navigation path for idea generation:**
Markets → (Saturn/Themes icon on left sidebar) → US Investment Themes

---

## 13. Stated Goals & Constraints

| Goal | Detail |
|---|---|
| Reduce news burden | Largest time cost; primary automation target |
| Move toward longer holds | Aspires to 10-year hold stocks to minimise active management |
| Maintain simplicity | Won't hold > 15 stocks; avoids crypto |
| Stay within circle of competence | Tech is primary; other sectors require higher conviction |

---

## 14. Automation & Optimisation Opportunities

### High feasibility (data readily available)

| Task | Notes |
|---|---|
| Fundamental screener | PE, market cap, ROE, equity ratio, FCF — all in public financial APIs (e.g. Financial Modeling Prep, Alpha Vantage, Polygon) |
| Technical signals | 50/200-day MA crossover, RSI — standard TA library (e.g. `ta-lib`, `pandas-ta`) |
| Valuation ratios | PE, PB, PS — available via same APIs |
| Stop-loss monitoring | Price alerts at buy_price × 0.95; single-day drop > 5% alert |
| Sector theme scanner | ETF flow data, momentum of sector ETFs as proxy for "what's moving" |
| Portfolio tracker | Real-time P&L vs. buy prices; flag positions near stop-loss |

### Medium feasibility

| Task | Notes |
|---|---|
| News sentiment | NLP on headlines (FinBERT, OpenAI API) — works for coarse buy/sell/hold signal |
| Analyst rating aggregation | Scraped from public sources or paid APIs (Tipranks, Seeking Alpha) |
| Moat classification | Morningstar data requires subscription; proxies possible (gross margin stability, ROIC consistency) |
| Short interest monitoring | FINRA short volume data is public; Tiger/MooMoo API if available |
| Earnings calendar alerts | Widely available via free APIs (Earnings Whispers, Alpha Vantage) |

### Low feasibility / Requires human judgment

| Task | Notes |
|---|---|
| Geopolitical rotation | "Iran ceasefire broken → rotate to oil" — no systematic signal; requires news understanding |
| Moat qualitative assessment | Morningstar moat is a qualitative analyst judgment; hard to automate faithfully |
| "Circle of competence" gating | Domain familiarity filter — inherently human |
| Short squeeze thesis | Requires narrative understanding, not just short ratio threshold |

---

## 15. Key Risks & Known Failure Modes (Self-Reported)

| Risk | Description |
|---|---|
| Selling on panic, missing recovery | Sold on DeepSeek news and Trump tariff; did not buy back when market recovered |
| Not buying back after stop-loss | Triggered stops correctly but then missed the re-entry |
| Overexposure to single theme | Addressed by diversification rule (≤15, multiple sectors) |
| Earnings gap-down on held position | NFLX example — mitigated by unrealised gain buffer |
| News overload | Primary operational burden; all news read manually |

---

## 16. Comparisons to Academic / Systematic Approaches

| Dad's approach | Quant equivalent | Comment |
|---|---|---|
| "What's moving up" theme scan | Cross-sectional momentum (12-1 month) | Dad's version is shorter-term and sector-level |
| RSI < 80, near MA entry | Mean-reversion entry within momentum trend | Hybrid momentum + mean-reversion |
| ROE ≥ 15%, positive FCF | Quality factor (Profitability in Fama-French 5-factor) | Standard quality screen |
| PE < 100, market cap ≥ $10B | Value + size filters | Conservative growth-at-reasonable-price (GARP) |
| Stop-loss at −5% from buy | Time-series momentum with trailing stop | Protects downside, risks whipsaw |
| Moat preference | Competitive advantage period (CAP) models | Qualitative; hard to replicate systematically |
| ≤15 stocks | Concentrated portfolio | Higher idiosyncratic risk; intentional |
| Pre-market / near-close execution | Opening/closing auction participation | Avoids intraday noise |
