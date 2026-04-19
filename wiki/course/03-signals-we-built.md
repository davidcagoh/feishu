# Article 3: The Signals We Built — and the Research Behind Them

*Part of a five-article series about how we built a quantitative trading strategy for the Feishu/Lark competition.*

---

## Starting from the Literature

Quantitative finance has accumulated decades of published research on what predicts stock returns. We didn't invent signals from scratch — we read papers, found ideas that had been validated on real data, and translated them into code. This is how professional quant desks work too: the research library is vast, and the craft is in adapting published findings to your specific data and market.

Here are the signals we built, grouped by the intuition behind them.

---

## Group 1: Reversal Signals

These all share the same core idea: **stocks that moved a lot recently tend to snap back**.

### Short-Term Reversal

One of the oldest documented patterns in finance, studied since at least the 1980s. Stocks with the highest return today tend to underperform tomorrow.

**Why it happens:** Retail investors chase momentum. When a stock rises, buyers pile in, pushing it too high. When there's no follow-through, it corrects. In Chinese markets, where retail traders account for roughly 80% of volume, this overreaction is stronger than in most other markets.

**How we built it:** Calculate each stock's daily return. Rank all 2,270 stocks. Bet against the winners (expect them to fall), bet on the losers (expect them to recover). Apply a limit-hit filter: on days when a stock hit the 10% daily price cap, we exclude it since those are special situations, not ordinary overreaction.

**Signal quality:** Information Ratio of 1.84 — a reasonable, well-established finding.

### Price vs. Opening VWAP

A more refined version. Each morning there's a special auction that sets the opening price. A stock that rallies hard *during the day* relative to that opening level has likely been pushed too far by intraday enthusiasm.

**Why it happens:** Intraday momentum driven by retail activity tends to exhaust itself by the close. The next day, it often retraces.

**Signal quality:** IR of 2.58.

### Volume Reversal

High volume often signals overreaction. If a stock trades 3× its normal volume today, something unusual happened — and the price probably overshot.

**Construction:** Compare today's volume to its rolling 20-day average. Rank stocks by how "surprising" their volume is (log-transformed to reduce skew from extreme spikes). Bet on mean-reversion from the high-volume stocks.

**Signal quality:** IR of 5.01 — one of our strongest individual signals.

---

## Group 2: Order Book Signals

These use the live queue of buyers and sellers to read near-term supply and demand directly.

### Level-1 LOB Imbalance

The simplest order book signal: if there are more shares queued to buy than to sell, buying pressure will push prices up.

**Formula:** `(bid_volume - ask_volume) / (bid_volume + ask_volume)`

This ranges from −1 (only sellers) to +1 (only buyers). We take the last snapshot of the day as our signal.

**The Chinese twist:** In our data, the raw signal had to be *inverted*. High bid volume at end of day in China actually predicts *negative* next-day returns. Why? Chinese retail investors pile into the bid at market close trying to participate in expected gains — it's a crowding effect, not genuine institutional demand. The smart-money interpretation is the opposite of the naive one. A 2025 paper (Kang, "Optimal Signal Extraction from Order Flow") confirmed this and gave us a better normalisation method.

**Signal quality:** IR of 2.40 — modest but highly consistent (low IC standard deviation), and importantly, *uncorrelated* with our price-based signals.

### OFI with Matched-Filter Normalization (Kang, 2025)

The standard imbalance divides by total book volume, which is noisy. Kang (2025) showed that the theoretically correct denominator — derived from optimal signal detection theory, the same mathematics used in radar engineering — is the stock's total daily trading amount (a proxy for market capitalisation).

**Why it matters:** Normalising by daily amount gives roughly twice the signal-to-noise ratio compared to the naïve normalisation. In the paper's data, this produced a t-statistic of 9.65 against next-day returns.

**Our result:** IR of 1.05 after this normalisation on our specific dataset. Weaker than the paper's result — likely because our data is daily aggregated rather than intraday, losing some of the signal's precision.

### OFI with OU Dynamics (Hu & Zhang, 2025)

This is the most mathematically sophisticated order book signal. Rather than just asking "is today's imbalance high?", it asks "how *unusually* high is it, given how quickly it typically reverts?"

The framework is the **Ornstein-Uhlenbeck process** — the mathematics of a stretched spring. Applied to order flow, it says: order book imbalance is pulled toward a long-run average, with some speed (κ) and some noise (σ). The trading signal is:

```
signal = (long-run mean − today's OFI) × reversion speed / noise level
```

This is called a "quasi-Sharpe ratio" — you're essentially asking "how confident are we that this imbalance will revert, given what we know about this stock's dynamics?"

**Our result:** IR of 1.77. Crucially, when we estimated the OU half-life for our stocks, the median was 0.31 days — meaning daily OFI reverts so fast it's nearly random from one day to the next. The signal still works, but the OU refinement adds less than it would for slower-moving processes.

---

## Group 3: Academic Factor Signals

### Alpha191 Factors 046 and 071

Chinese quant researchers have compiled a widely-used library of 191 hand-crafted signals, known as "Alpha191." A 2026 paper tested all 191 of them with a statistical technique called double-selection LASSO — identifying which signals survive when you control for all the others simultaneously, and which also work in the more informationally efficient US market (a tough hurdle).

Two passed: **Factor 046** and **Factor 071**.

**Factor 046 — Range Position:** Where does today's price sit within the last 20 days' high-low range? A stock trading near its 20-day high is "overbought"; near its low, it's "oversold." Expect mean reversion.

**Factor 071 — Deviation from Moving Average:** How far is today's price from its 24-day moving average, expressed as a percentage? Far above = extended; expect pullback.

Both are conceptually related to short-term reversal but capture the exhaustion from a different angle.

**Signal quality:** IR 2.38 and 2.79 respectively.

### Stable Turnover Momentum (Zhang, Chen & Xu, 2025)

A more complex signal: momentum (past winners keep winning) filtered by *stability*. The idea was to find stocks on a steady, monotone uptrend with consistent trading activity — filtering out the noisy momentum that tends to reverse.

We computed four factors for each stock: 20-day return, how "linear" the price path was (R²), how consistent daily turnover was (inverse standard deviation), and idiosyncratic volatility. Multiplied together, they were supposed to isolate genuine, durable momentum.

**Result:** The signal failed completely in actual portfolio construction. We'll explain why in Article 4 — the failure illuminated something fundamental.

---

## Combining Signals: The Composite

When you have multiple signals, the smart move is to combine them. Signals are useful for different reasons — some have higher IC, some have lower noise, some capture different market regimes. A portfolio of signals diversifies the same way a portfolio of stocks does.

We computed the **IC correlation matrix** across all our daily signals and found they cluster into three groups:
- Cluster A: Short-term reversal ↔ Price-vs-VWAP (very similar, r=0.93)
- Cluster B: Alpha191-046 ↔ Alpha191-071 (very similar, r=0.94)
- Cluster C: Volume reversal (standalone)

Rather than use all signals, we picked the best representative from each cluster and weighted them using portfolio optimisation mathematics (maximising information ratio given estimated covariances):

> 85% volume reversal + 15% price-vs-VWAP = **composite daily signal, IR 5.08**

When we added the order book signals — which are *negatively* correlated with the price signals (r = −0.24 to −0.57) — the diversification was dramatic:

> 35% OFI-OU + 28% LOB imbalance + 25% volume reversal + 12% price-vs-VWAP = **composite full signal, IR 9.64, hit rate 74%**

An IR of 9.64 is extraordinary by academic standards. Our IC standard deviation dropped from ~0.11 (daily signals alone) to 0.056 (combined with LOB signals) — meaning the composite was not just more accurate on average, but far more consistent day to day.

A strategy working 74% of days, with those IC numbers, should be a straightforward winner.

It was not.

---

*Next: [Article 4 — When Smart Strategies Fail](04-when-smart-strategies-fail.md)*
