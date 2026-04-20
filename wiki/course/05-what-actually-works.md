# Article 5: What Actually Works — The Boring Strategy That Beat the Market

*Part of a six-article series about how we built a quantitative trading strategy for the Feishu/Lark competition.*

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

The baseline strategy is simple:

1. Compute each stock's **return volatility** over the trailing 60 trading days — the standard deviation of its daily adjusted returns.
2. **Exclude illiquid stocks**: null out the signal for stocks whose 20-day average trading volume puts them in the bottom 5% of the market. Micro-cap stocks can have low volatility statistically but face catastrophic "limit-down cascade" events that destroy returns.
3. **Rank all 2,270 stocks** from lowest volatility to highest.
4. **Hold the 20 least volatile stocks** in equal weight, rebalancing daily.

No order book data. No sophisticated mathematics. A 60-day rolling standard deviation and a liquidity filter.

---

## The Volatility-Managed Overlay

We added one refinement on top: a technique validated in a 2024 paper by Wang & Li specifically for Chinese equity markets.

The idea: on days when the *overall market* is in extreme turbulence, don't rebalance. Simply hold whatever you already have.

We measure market turbulence by the average squared return across all stocks each day — a proxy for market-wide volatility. If this measure exceeds twice its normal level, we blank out the signal and hold the previous portfolio unchanged rather than reshuffling into a chaotic market.

**Why this helps:** On the most volatile days, signal quality degrades. Your 60-day volatility estimate for individual stocks is noise-contaminated. Sitting on your hands is the right call.

The improvement was modest but essentially free: no added risk, no additional transaction costs.

---

## One More Step: Adding a Trend Filter

After finding that low-volatility worked, the natural question was whether we could refine it further. We had been testing variations of the same underlying idea — calm stocks, managed turbulence — and the improvements were becoming incremental.

At this point, something more fundamental shifted. We asked: what if we combined the "calm" criterion with a completely different one — *direction*?

Every signal in our research had been some version of mean reversion: betting that what went up will come down, or that volatility will cluster and normalize. The opposite idea is **trend following**: betting that what has been quietly going up will keep going up. These aren't contradictory; they just operate at different timescales and ask different questions.

Applied together: we only want stocks that are both calm *and* rising. Not a stock that barely moved because it's been drifting sideways or slipping slowly downward. A stock on a steady, quiet uptrend.

**Implementation:** For each stock, fit a linear trend line through the last 35 days of prices. If the slope is positive — the stock has been rising on balance — it passes the filter. Low-volatility stocks that fail this trend filter are excluded from consideration that day.

Then one further refinement to weighting: instead of holding the remaining stocks in equal amounts, we weight each one **inversely by its volatility**. The calmest stock gets the largest position. This is called Equal Risk Contribution (ERC): each holding contributes the same amount of risk to the portfolio rather than the same number of dollars, which prevents a slightly-less-calm stock from dominating the portfolio's behaviour.

---

## The Results, In Full

Over the full 484-day in-sample period, against a market that fell approximately 18%:

| Strategy | CAGR | Sharpe Ratio | Max Drawdown | Score |
|----------|------|--------------|--------------|-------|
| Market (random selection) | −18% | — | — | — |
| Low volatility (baseline) | +8.81% | 0.961 | 9.38% | 0.305 |
| + Vol-managed overlay | +9.64% | 1.032 | 9.38% | 0.330 |
| + 35-day trend filter | +12.29% | 1.202 | 11.21% | 0.388 |
| + ERC weights (submitted) | **+12.55%** | **1.231** | **11.04%** | **0.398** |

The low-volatility baseline beat the market by approximately +27 percentage points. Each refinement built on that: the vol-managed overlay improved consistency, the trend filter added meaningful return, and ERC tightened the drawdown slightly by concentrating capital in the genuinely quietest names.

The submitted strategy beats the market by **approximately +31 percentage points** in-sample.

---

## What the Portfolio Actually Looks Like

Despite holding 20 stocks, the portfolio has much less diversification than the number suggests.

After running the full 484-day backtest, we found:

- **12 core stocks** appear in the portfolio on more than 80% of all valid trading days
- One stock, A001224, appears on every single valid day
- **Average daily turnover: roughly 4–5%** — one stock swaps in and out per day on average
- **Effective independent bets: approximately 7** — despite 20 positions, the holdings are highly correlated with each other

This makes intuitive sense. In China, the lowest-volatility stocks in a steady uptrend are overwhelmingly state-owned enterprises (SOEs), utilities, and major banks. They share an implicit characteristic: partial government ownership that limits their downside and backstops their stability. They move together.

This is both the strength of the strategy (these stocks genuinely are more stable in a bear market) and its main risk (if the government-backed defensive sector rotates out of favour, the entire portfolio suffers simultaneously).

---

## Where This Fits in the Industry

Minimum volatility as a systematic strategy is mainstream:

- **BlackRock** manages over $30 billion in minimum-volatility exchange-traded funds (ETFs)
- **AQR Capital Management**, one of the world's largest quantitative hedge funds, has published extensively on the low-vol anomaly across global markets
- **MSCI** publishes minimum-volatility indices for every major market; they've outperformed their cap-weighted parents over long periods

What we built is a simpler version of what institutions have been implementing for 15 years. The key differences: institutions hold hundreds of stocks (better diversification), model transaction costs explicitly, and rebalance less frequently. They also typically combine minimum volatility with other factors to hedge the sector concentration risk we identified.

Adding a trend filter is also not novel — it appears in various forms in practitioner literature as a way to avoid "value traps" (cheap, calm stocks that are cheap because the business is deteriorating). Our version is price-only, but the logic is the same.

---

## Honest Caveats

**The bear market advantage.** Our 484-day in-sample period is a difficult one for the overall market (−18%). Low-volatility and trend-following strategies are defensive and momentum-respecting — they shine when markets fall or trend steadily, and can underperform in sharp recoveries. If the 242 out-of-sample days are a strong bull rally, we'll likely trail.

**Sector concentration.** We are essentially running a concentrated SOE/utilities/bank bet. A policy shift, interest rate shock, or rotation away from defensive sectors could hit the entire portfolio simultaneously.

**In-sample fitting.** The trend window length (35 days) was selected by sweeping values on the in-sample data. It performed best there; whether that window generalises to the OOS period is unknown. We validated that nearby windows (30, 40 days) produced similar results, which suggests the effect is real rather than a precise overfit — but we can't be certain.

We know these risks. Given the constraints — no sector labels, no fundamental data, only price and volume — this is the best-performing strategy we found that survives realistic execution.

---

## Reflections on the Process

The most surprising outcome of this project was that the sophisticated strategies lost and the boring one won — and then the boring one got meaningfully better once we stopped asking variations of the same question.

We spent months building reversal signals grounded in cutting-edge papers: order book mathematics, OU processes, matched-filter normalisations. None of it survived actual trade execution. The strategy that worked is one that a practitioner in the 1990s could have described in a paragraph.

The trend filter, which produced the single biggest score improvement of the whole project, came from a simple conceptual shift: asking "what is the opposite of what we've been doing?" rather than "how do we do more of this?" That question took longer than it should have to arrive. Why, and what that says about how we used AI throughout the project, is the subject of the final article.

---

## What Happens Next

On May 28, 2026, the competition releases 242 days of out-of-sample data. We run one command:

```bash
python eval/generate_submission.py \
    --daily data/daily_data_oos.parquet \
    --sell-mode open --n-stocks 20 \
    --output submissions/submission_v3_trend_vol.csv
```

The output is a CSV specifying which stocks to buy and sell each day. We submit it before June 1 and wait for the score.

If the out-of-sample period resembles the in-sample data — a grinding bear market or a stable trend — the strategy should hold up. If it's a sharp reversal rally, we'll find out quickly how much the low-vol anomaly depends on defensive market conditions.

Either way, we learned a lot.

---

*Next: [Article 6 — On Clean Slates: What We Learned About AI as a Research Partner](06-on-clean-slates.md)*
