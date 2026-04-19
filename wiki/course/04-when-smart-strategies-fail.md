# Article 4: When Smart Strategies Fail — The Gap That Ate Our Alpha

*Part of a five-article series about how we built a quantitative trading strategy for the Feishu/Lark competition.*

---

## The Number That Stopped Us Cold

After building our composite signal — Information Ratio 9.64, hit rate 74%, IC standard deviation half what any individual signal achieved — we ran it through a proper portfolio backtest. The backtest simulated real trades: buying at actual prices, paying transaction costs, respecting the competition's rules.

**Composite signal (IR = 9.64): CAGR −54% over 484 days.**

The market fell about 18% in this same period. We didn't just underperform. We lost three times more than doing nothing.

Every reversal signal we had built — individually or combined — produced the same catastrophic result in real portfolio construction. The "stable turnover momentum" signal, despite months of theoretical development, delivered −47%.

This needed an explanation.

---

## The Timing Trap

Here is what went wrong. Our signals predict the **close-to-close return**: how much a stock will move from tonight's closing price to tomorrow's closing price. That's how IC is calculated — it's the natural definition of "tomorrow's return."

But the competition has a specific rule: **you buy at the opening VWAP**, the average price over the first five minutes of trading (09:30–09:35am). You cannot buy at the closing price. By the time you can act, the market has already opened.

What happens overnight? A lot.

Our reversal signals are betting that today's winners will fall tomorrow. And they often do — but the fall happens *in the gap between yesterday's close and today's open*, before we can buy. A stock that closed up 5% today frequently opens down 2% the next morning. That reversal is real. But it happened while the market was closed. The investors who captured it were the ones who shorted at yesterday's close and bought at this morning's open — not us.

By 09:30am, the reversal trade is largely done. We arrive at the party and buy what's left, paying the post-gap price. Then the stock continues drifting sideways or slightly down for the rest of the day, because we've entered at exactly the wrong moment.

We measured this directly by computing the **execution IC**: the correlation between our signal and the return from the *opening VWAP to the next day's open*. For our best reversal signals, execution IC was around +0.011. For the same signal, IC (close-to-close) was +0.034. The signal is real — it's just that roughly two-thirds of the return happens before we can act.

The signals were right. The timing was wrong.

---

## Two Chinese Market Rules That Made It Worse

### T+1 Settlement

In most global markets, you can buy a stock in the morning and sell it the same afternoon. In China, you cannot. The rule is **T+1**: shares bought today cannot be sold until tomorrow. This is a feature designed to discourage day-trading speculation, but it has a side effect for our strategy.

If we buy into a reversal trade and realise by midday that it's going against us, we cannot exit. We're locked in until tomorrow, accumulating losses. In a reversal strategy where timing is everything, being unable to cut a losing position the same day is brutal.

### Daily Price Limits: ±10%

Chinese stocks also cannot move more than 10% in either direction in a single day. When bad news hits, a stock doesn't crash 30% instantly — it hits the 10% limit-down and trading halts. The following days, it may hit limit-down again and again until the news is fully priced in.

This sounds like protection, but it creates what traders call a "locked limit" situation: you cannot sell at any price because there are no buyers willing to transact at the limit-down price. The reversal signals we built specifically tried to bet against stocks that had moved a lot — which disproportionately includes stocks approaching these limits. We were systematically identifying the most dangerous stocks to hold.

---

## Why This Is a Well-Known Problem

This isn't a mistake unique to us. Every serious quant shop has been burned by some version of the **alpha decay** problem: the gap between how good a signal looks on paper and how much of it survives actual execution.

The reasons are almost always some combination of:
1. **Timing mismatch** — the signal is measured at a different moment than when you trade
2. **Transaction costs** — commissions, bid-ask spread, and market impact eat the edge
3. **Crowding** — if everyone sees the same signal, prices adjust before you can act

Renaissance Technologies — the most successful quantitative hedge fund in history, with annualised returns over 60% in its flagship fund for three decades — built much of its early advantage by solving exactly these execution problems. Their researchers spent years on the question of *when* to trade, not just *what* to trade. The signal is the easy part.

For our competition, the lesson was stark: a signal with IC=0.034 and IR=9.64 was worth almost nothing if the return it predicted occurred during a window when we couldn't trade.

---

## What Execution IC Taught Us

After diagnosing the problem, we computed execution IC — the real measure of whether a signal is useful given the actual buy window — for everything we had built:

| Signal | IC (close-to-close) | Execution IC | Backtest CAGR |
|--------|--------------------|----|---|
| Composite full (IR 9.64) | +0.034 | +0.011 | **−54%** |
| Volume reversal (IR 5.01) | +0.034 | +0.011 | **−54%** |
| Stable turnover momentum | — | −0.023 | **−47%** |
| **Low volatility** | — | **+0.054** | **+9%** |

The low volatility signal, which we had been treating as a boring backup, had nearly **five times** the execution IC of our sophisticated reversal strategies.

Why? Because low-volatility stocks don't have sharp overnight gaps. They're boring by definition. Utilities, banks, state-owned enterprises — these stocks open each morning roughly where they closed. The gap problem that destroyed our reversal strategies simply doesn't apply to stocks that barely move.

This was the pivot.

---

## The Lesson About Backtesting

Professional quant desks distinguish carefully between several types of backtests:

- **Signal backtest**: Does this signal predict returns? (IC, IR)
- **Paper backtest**: Does a simulated portfolio using this signal make money, assuming ideal execution?
- **Realistic backtest**: Does the portfolio make money when you account for actual execution timing, costs, and market impact?
- **Live trading**: Does it work with real money?

We had strong results at the signal level and jumped directly to assuming portfolio success. The realistic backtest — which we eventually built — told a completely different story.

The gap between signal quality and portfolio quality is one of the most important (and humbling) concepts in quantitative finance. It's also, incidentally, why this is a hard problem that still employs thousands of brilliant people.

---

*Next: [Article 5 — What Actually Works: The Boring Strategy That Beat the Market](05-what-actually-works.md)*
