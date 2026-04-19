# Article 1: What Is the Stock Market, Really?

*Part of a five-article series about how we built a quantitative trading strategy for the Feishu/Lark competition.*

---

## Owning a Piece of a Company

When a company wants to raise money, one option is to divide itself into millions of tiny equal slices — called **shares** — and sell them to the public. If you buy a share, you own a genuine slice of everything the company has: its buildings, its equipment, its patents, and a claim on its future profits.

The stock market is simply the organised marketplace where these slices change hands every day.

Prices move because people constantly disagree about what a company is worth. One investor thinks a battery maker's best days are ahead; another thinks they're overpriced. Every buy and sell order is, in a sense, a small vote. The price at any moment reflects the collective opinion of everyone willing to put money on the line.

---

## The Two Types of Data We Work With

In this competition we have access to two very different windows into the market.

### 1. The Daily Newspaper: OHLCV Data

At the end of each trading day, all the day's drama gets compressed into five numbers:

| Symbol | Meaning |
|--------|---------|
| **O** | Opening price — the first trade of the morning |
| **H** | Highest price reached during the day |
| **L** | Lowest price |
| **C** | Closing price — the last trade before the bell |
| **V** | Volume — total number of shares traded |

Think of this as the newspaper headline version of a day's worth of activity. It tells you roughly what happened, but none of the texture.

We have these numbers for **2,270 Chinese stocks across 484 trading days** — over a million rows of data.

One important wrinkle: companies sometimes split their shares, or pay dividends that adjust the price mechanically. To compare prices fairly across time, we always multiply by an **adjustment factor** that undoes those distortions.

### 2. The Live Queue: The Limit Order Book

The second dataset is far richer. It captures something called the **limit order book** — the live, real-time record of everyone who is *trying* to buy or sell but hasn't traded yet.

Imagine a farmers' market where, instead of haggling privately, every buyer and seller posts a note on a public board:

> "I will buy 500 shares at ¥42.10 or lower."  
> "I will sell 300 shares at ¥42.15 or higher."

The highest willing buyer is called the **best bid**. The lowest willing seller is called the **best ask**. The gap between them is the **spread** — the cost of transacting instantly.

A trade happens the moment someone decides to stop waiting and accept the best available price on the other side.

In our data we can see the top **10 levels** of both sides of this book — the ten most aggressive buyers and ten most aggressive sellers — captured roughly **23 times per day** for each stock. That's nearly 25 million rows of data in total.

A simple but powerful thing we can observe from this: if there are 10,000 shares queued to buy and only 2,000 queued to sell, that **imbalance** suggests buying pressure. Prices probably need to rise until more sellers appear.

---

## One More Piece: The Opening Auction

Chinese markets open with a special auction window from 09:25–09:30am, before regular trading begins. The resulting opening price — technically a **VWAP** (volume-weighted average price) over the first five minutes — is part of our daily dataset. This matters because a lot can happen overnight between yesterday's close and today's open. We'll return to why this is so important in Article 4.

---

## Why Any of This Is Hard

You might wonder: if prices reflect all this information, shouldn't they be basically unpredictable? The short answer is yes — most of the time. Academic finance has spent 60 years documenting how difficult it is to beat the market consistently.

But markets aren't perfectly efficient, especially in China where roughly **80% of trading volume comes from retail investors** — individuals, not professional funds. Retail investors tend to chase recent winners, panic when prices fall, and overreact to news. These patterns leave footprints in the data.

The question our project tries to answer is: *can we find and trade those footprints systematically?*

That's what Article 2 is about.

---

*Next: [Article 2 — The Alpha Hunt: What Quants Are Actually Trying to Do](02-the-alpha-hunt.md)*
