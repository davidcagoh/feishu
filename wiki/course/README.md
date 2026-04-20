# Mini Course: How We Built a Trading Strategy

A six-article series explaining what we're doing in the Feishu/Lark Quant Competition — written for anyone curious, no finance background required.

---

## Articles

| # | Title | What you'll learn |
|---|-------|------------------|
| 1 | [What Is the Stock Market, Really?](01-what-is-the-stock-market.md) | Shares, prices, OHLCV data, the order book |
| 2 | [The Alpha Hunt](02-the-alpha-hunt.md) | What quants do, IC explained, the competition rules |
| 3 | [The Signals We Built](03-signals-we-built.md) | 10+ strategies from academic papers, and what the data said |
| 4 | [When Smart Strategies Fail](04-when-smart-strategies-fail.md) | IR 9.64 → CAGR −54%: the execution gap that broke everything |
| 5 | [What Actually Works](05-what-actually-works.md) | The boring strategy that beat a falling market by 31 points |
| 6 | [On Clean Slates](06-on-clean-slates.md) | What we learned about using AI as a research partner over time |

---

## The Story in One Paragraph

We built thirteen quantitative trading signals grounded in academic research — reversal signals, order book signals, momentum filters — and combined them into a composite with an Information Ratio of 9.64. When we ran a realistic portfolio backtest simulating actual trade prices, the composite lost 54% while the market fell 18%. The culprit: the reversal alpha happens overnight before the market opens, after which we were forced to buy. The one signal that survived was minimum volatility — selecting the calmest stocks — which returned +8.81%. A volatility-managed overlay improved it to +9.64%. Then, after three months of testing variations of the same underlying idea, we noticed we had never explored the opposite intuition: trend-following. Adding a 35-day trend filter and equal-risk-contribution weights pushed the strategy to +12.55% CAGR with a Sharpe of 1.231. The final article reflects on why that insight took so long, and what it reveals about using AI as a long-term research partner.

---

## Key Numbers

| | Value |
|---|---|
| Strategy | Low volatility + trend filter + ERC weights |
| In-sample period | 484 trading days, 2,270 stocks |
| Portfolio size | 20 stocks |
| CAGR (in-sample) | +12.55% |
| Sharpe ratio | 1.231 |
| Max drawdown | 11.04% |
| Market return (same period) | ≈ −18% |
| Outperformance vs market | ~+31 percentage points |
| Effective independent bets | ~7 |
