# Article 2: The Alpha Hunt — What Quants Are Actually Trying to Do

*Part of a five-article series about how we built a quantitative trading strategy for the Feishu/Lark competition.*

---

## The Dream

Here is the dream: wake up every morning, look at yesterday's data, and know — with reasonable confidence — which stocks will rise today and which will fall. Then buy the risers and short the fallers. Repeat 250 times a year.

If you could do this reliably, even a little bit, you'd compound extraordinary returns. A 1% daily edge, held consistently, would produce returns that dwarf any other investment in history.

Nobody can do this perfectly. But quantitative traders — "quants" — spend their careers searching for *partial* versions of it. Not certainty, but a systematic tilt. Not 100% accuracy, but 55%. Repeated thousands of times across thousands of stocks, small edges become large returns.

These tilts are called **alpha signals**.

---

## What Is an Alpha Signal?

An alpha signal is any measurable thing about a stock today that predicts its return tomorrow. It could be:

- A pattern in its recent price history
- Something unusual about its trading volume
- The balance of buyers versus sellers in its order book
- Some mathematical combination of all three

The word "alpha" specifically means return *beyond* what you'd get just from riding the market up and down. If the whole market falls 2% today and your stock falls 2.1%, that's not alpha — that's just being a stock. Alpha is the part that's specific to your strategy's skill.

---

## How We Measure If a Signal Works: Information Coefficient

The standard metric for judging a signal is the **Information Coefficient** (IC). It measures the correlation between your signal's ranking of stocks and the actual ranking of their next-day returns.

A useful analogy: imagine you give 100 friends tips on which horse to bet on at the races. IC measures how often the horse you said would win actually came first. An IC of 0 means your tips are pure noise — no better than random. An IC of 1.0 means you predicted the exact order perfectly every single time.

In practice, an IC of **0.02–0.05** is considered very good in quantitative finance. Our best signals reached **0.034**. That sounds tiny, but applied across 2,270 stocks every day, it's a real edge.

There's also the **Information Ratio** (IR): how consistent is that IC? A signal with IC=0.03 on average but wildly variable (sometimes +0.15, sometimes −0.12) is much less useful than one that quietly delivers 0.03 day after day. IR penalises inconsistency, which is exactly what you want.

---

## The Competition We're In

The Feishu/Lark Quant Competition gives us:
- **2,270 Chinese A-share stocks** (opaque IDs, so we don't know which companies they are)
- **484 days** of historical data to learn from
- **242 unseen days** (released May 28, 2026) on which we'll actually be scored

Each day we must decide which stocks to hold. The competition scores our strategy on three things:

| Metric | Weight | Meaning |
|--------|--------|---------|
| **CAGR** | 45% | Compound annual growth rate — how much we made |
| **Sharpe ratio** | 30% | Return divided by risk — consistency |
| **Max drawdown** | 25% | The worst peak-to-trough loss — how bad was the worst stretch |

The portfolio must hold at least 10 stocks at all times. We start with RMB 50 million. Every trade incurs small transaction costs.

---

## Where This Sits in the Industry

Quantitative trading is one of the most competitive fields in finance. The firms at the frontier — Renaissance Technologies, Two Sigma, DE Shaw, Jane Street — employ hundreds of researchers with PhDs in physics, mathematics, and computer science, operating with microsecond execution systems and terabytes of data.

Their ICs and IRs are closely guarded secrets. But academic research on publicly available signals suggests that even the best published factors produce ICs around 0.02–0.05, with IRs rarely above 2–3 sustained over long periods after transaction costs.

What we built in this competition, working from academic papers with clean data and no transaction friction in the signal itself, got raw IRs as high as **9.64**. That's exciting — and also a warning sign. We'll explain why in Article 4.

---

## How Signals Become a Portfolio

A single signal tells you "this stock looks better than that one today." To turn that into actual trades, you:

1. **Cross-sectionally z-score** the signal: within each day, convert raw scores to standard deviations above or below the mean. This removes any day-to-day scale differences.
2. **Rank** all 2,270 stocks from best signal to worst.
3. **Hold the top N** stocks in equal weight, rebalancing daily.

The choice of N matters. We tested N=20 and N=100. Holding fewer stocks means more concentration and higher tracking error; holding more dilutes the signal but smooths the ride.

---

## The Research Process

We built thirteen distinct signals, each grounded in a published academic paper or well-documented financial phenomenon. Some are based purely on price and volume data (available daily). Others use the order book's real-time queue of buyers and sellers.

Article 3 walks through what each one was, where it came from, and what the data said about it.

Some performed beautifully — at least by one measure.

---

*Next: [Article 3 — The Signals We Built](03-signals-we-built.md)*
