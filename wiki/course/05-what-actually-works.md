# Article 5: What Actually Works — The Boring Strategy That Beat the Market

*Part of a five-article series about how we built a quantitative trading strategy for the Feishu/Lark competition.*

---

## The Pivot

After the reversal strategies collapsed in portfolio testing, we needed a strategy whose signal survives the buy window — something where the edge isn't in predicting *which direction* a stock will snap, but in selecting stocks with fundamentally different risk characteristics.

The signal we had been treating as a fallback turned out to be the answer: **minimum volatility**.

---

## The Volatility Anomaly: Why Boring Beats Exciting

Here is one of the most counter-intuitive and well-documented findings in finance. If you rank stocks from most volatile (wild daily swings) to least volatile (steady, boring) and hold only the boring ones, you don't just lose less — you often *make more*, even before adjusting for risk.

This violates something most people intuitively believe: that higher risk should mean higher reward. In stocks, this relationship breaks down. Boring stocks outperform exciting ones on a risk-adjusted basis, and in many markets, on an absolute basis too.

This is called the **volatility anomaly** or the **low-vol effect**, and it's been documented across US, European, emerging, and Asian markets over many decades.

**For China specifically:** A 2021 paper by Blitz, Hanauer, and van Vliet found a spread of **16.1% annualised** between the lowest-volatility and highest-volatility decile of Chinese A-shares. That's the raw, before-cost difference in returns between the ten calmest stocks and the ten wildest ones. The calmest won by 16 percentage points per year.

### Why Does This Happen?

There are three main theories, and all three likely contribute:

**1. Leverage constraints.** Institutional investors (pension funds, insurance companies) are often prohibited from using borrowed money to amplify returns. To generate higher returns without leverage, they buy riskier stocks. This collective demand bids up high-volatility stocks, overpricing them. Low-volatility stocks, left unloved, are underpriced.

**2. The lottery effect.** Individual investors are drawn to "lottery ticket" stocks — ones with a chance of doubling or tripling quickly. They accept low average returns for the excitement of the occasional jackpot. This overpayment for exciting stocks systematically underprices boring ones.

**3. Career risk for fund managers.** A fund manager who holds boring, low-volatility stocks and underperforms in a bull market will be fired, even if their strategy is sound over a full cycle. So managers systematically tilt toward high-beta, market-tracking stocks to protect their careers — even at the expense of their clients' long-term returns.

---

## Our Implementation

The strategy is simple:

1. Compute each stock's **return volatility** over the trailing 60 trading days — the standard deviation of its daily adjusted returns.
2. **Exclude illiquid stocks**: null out the signal for stocks whose 20-day average trading volume puts them in the bottom 5% of the market. Micro-cap stocks can have low volatility statistically but face catastrophic "limit-down cascade" events that destroy returns.
3. **Rank all 2,270 stocks** from lowest volatility to highest.
4. **Hold the 20 least volatile stocks** in equal weight, rebalancing daily.

That's it. No order book data. No sophisticated mathematics. A 60-day rolling standard deviation and a liquidity filter.

---

## The Results

Over the full 484-day in-sample period, against a market that fell approximately 18%:

| Strategy | Annual Return (CAGR) | Sharpe Ratio | Max Drawdown |
|----------|---------------------|--------------|--------------|
| Market (random selection) | −18% | — | — |
| Low volatility (baseline) | **+8.81%** | **0.961** | **9.38%** |
| Vol-managed overlay | **+9.04%** | **0.981** | **9.38%** |

The low-volatility strategy beat the market by approximately **+27 percentage points** over the same period.

---

## The Volatility-Managed Overlay

We added one refinement on top: a technique validated in a 2024 paper by Wang & Li specifically for Chinese equity markets.

The idea: on days when the *overall market* is in extreme turbulence, don't rebalance. Simply hold whatever you already have.

We measure market turbulence by the average squared return across all stocks each day — a proxy for market-wide volatility. If this measure exceeds 3× its normal level (its in-sample median), we blank out the signal and the backtest holds the previous portfolio unchanged rather than reshuffling into a chaotic market.

**Why this helps:** On the most volatile days, signal quality degrades. Your 60-day volatility estimate for individual stocks is noise-contaminated. The stocks moving least in a panic are different from the ones that are structurally low-volatility. Sitting on your hands is the right call.

The improvement is modest — Sharpe from 0.961 to 0.981, CAGR from 8.81% to 9.04% — but it's essentially free: no added risk, no additional transaction costs, just better judgement about when not to trade.

This is the strategy we're submitting.

---

## What the Portfolio Actually Looks Like

An interesting detail: despite holding 20 stocks (we also tested 100), the portfolio has much less diversification than you might expect.

After running the full 484-day backtest, we analysed which stocks were selected most frequently:

- **12 core stocks** appear in the portfolio on more than 80% of all valid trading days
- One stock, A001224, appears on every single valid day
- The portfolio holds 556 different stocks *across* the full period, but on any given day it's almost the same list as the day before
- **Average daily turnover: 4.3%** — roughly one stock swaps in and out per day on average

We also computed the statistical "effective number of independent bets" among the top holdings. Despite holding 20 positions, the effective diversification is closer to **7 independent bets** — the stocks are highly correlated with each other.

This makes intuitive sense. In China, the lowest-volatility stocks are overwhelmingly state-owned enterprises (SOEs), utilities, and major banks. They share an implicit characteristic: partial government ownership that limits their downside. They move together. They're essentially the same bet expressed in 20 different tickers.

This is both the strength of the strategy (these stocks genuinely are more stable in a bear market) and its main risk (if the government-backed defensive sector rotates out of favour, the entire portfolio suffers simultaneously).

---

## Where This Fits in the Industry

Minimum volatility as a systematic strategy is not obscure. It's mainstream:

- **BlackRock** manages over $30 billion in minimum-volatility exchange-traded funds (ETFs)
- **AQR Capital Management**, one of the world's largest quantitative hedge funds, has published extensively on the low-vol anomaly across global markets
- **MSCI** publishes minimum-volatility indices for every major market; they've outperformed their cap-weighted parents over long periods
- The **factor** is now included in most institutional multi-factor models alongside value, momentum, and quality

What we built is a simpler version of what institutions have been implementing for 15 years. The key differences: institutions hold hundreds or thousands of stocks (better diversification), model transaction costs explicitly, and rebalance less frequently to reduce cost drag. They also typically combine minimum volatility with other factors — value, profitability — to hedge the sector concentration risk we identified.

---

## Honest Caveats

**The bear market advantage.** Our 484-day in-sample period is a difficult one for the overall market (−18%). Low-volatility strategies are defensive — they shine when markets fall and underperform when markets rally strongly. If the 242 out-of-sample days we'll be scored on are a bull market recovery, we'll likely trail the market. This is the main risk.

**Sector concentration.** As noted above, we're essentially running a concentrated SOE/utilities/bank bet. A policy shift, interest rate shock, or rotation away from defensive sectors could hit the entire portfolio at once.

**Seven independent bets.** Despite holding 20 positions, the correlation structure means we're not as diversified as the stock count suggests. A portfolio of 20 truly uncorrelated positions would be far more robust.

We know these risks. Given the constraints — no sector labels, no fundamental data, only price/volume — this is the best-performing strategy we found that survives realistic execution.

---

## Reflections on the Process

The most surprising outcome of this project was that the sophisticated strategies lost and the boring one won.

We built signals grounded in cutting-edge academic papers, combined them with portfolio optimisation mathematics, achieved IC and IR numbers that would look excellent in any finance journal — and they all collapsed when we applied them to real trading mechanics.

The low-volatility signal is 40 years old. The underlying intuition (buy the calm, avoid the wild) predates quantitative finance entirely. It has no order book data, no mathematical elegance, no clever normalization. It just selects stocks that don't move much, and it turns out that in a bear market on a retail-dominated exchange, those stocks quietly compound while everything else is volatile.

Warren Buffett has made a version of this argument for his entire career: in investing, complexity is often the enemy of returns. The simplest strategy that survives execution is usually the right one.

That said — the sophisticated signals were not wasted effort. Understanding *why* they failed taught us things about market microstructure, execution mechanics, and Chinese market rules that we wouldn't have learned otherwise. And a few of those signals (particularly the LOB imbalance ones, which are uncorrelated with the low-vol strategy and have positive execution IC) remain candidates to blend in at the margin if we have time before submission.

---

## What Happens Next

On May 28, 2026, the competition releases 242 days of out-of-sample data. We run one command:

```bash
python eval/generate_submission.py --daily data/daily_data_oos.parquet
```

The output is a CSV file specifying which stocks to buy and sell each day. We submit it before June 1 and wait for the score.

If the out-of-sample period is a bear market like the in-sample data, we should do well. If it's a recovery rally, we'll find out just how much the low-vol anomaly relies on defensive market conditions.

Either way, we learned a lot.

---

*[Back to Article 1 — What Is the Stock Market, Really?](01-what-is-the-stock-market.md)*
