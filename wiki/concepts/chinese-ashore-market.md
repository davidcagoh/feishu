# Chinese A-Share Market Specifics

The Chinese A-share market has structural features that **differ materially from US equity markets**. Strategies from US papers need to be adjusted. This article documents the key differences relevant to alpha signal construction.

**Sources:** Microstructure of the Chinese Stock Market: A Historical Review (2024); Factor models for Chinese A-shares (2024); Innovative Alpha Strategies for the Chinese A-Share Market (2025)

---

## Structural Constraints

### T+1 Settlement (Critical)
- **Rule:** You cannot sell shares purchased on the same day.
- **Impact on signals:** Any alpha signal derived from intraday data is **not actionable the same day**. You can only exit the next day at earliest.
- **Implication for Feishu:** End-of-day LOB imbalance and closing price signals predict the **next day's open/close**, not same-day exits. This is actually the natural holding horizon anyway.

### Daily Price Limits
- **Standard stocks:** ±10% daily limit (Shanghai/Shenzhen main boards)
- **STAR/ChiNext growth stocks:** ±20%
- **ST stocks** (special treatment, distressed): ±5%
- **Feishu implication:** The `high` and `low` columns in daily data will show price limit hits. When `high == low` and `close == open * 1.10`, the stock hit the limit up and may be uninvestable that day.

```python
# Detect limit-hit days
daily['limit_up'] = (daily['high'] == daily['low']) & (daily['close'] > daily['open'] * 1.09)
daily['limit_down'] = (daily['high'] == daily['low']) & (daily['close'] < daily['open'] * 0.91)
# Exclude these from signal evaluation — no execution possible
```

### Short Selling Constraints
- Short selling is heavily restricted and further tightened in 2024
- Most retail/quant strategies are effectively **long-only** or operate with very limited short capacity
- **Implication:** Cross-sectional signals should be evaluated as long-only (top quantile vs equal-weight benchmark) as well as long-short

---

## Investor Composition

### Retail Dominance
- Retail investors account for ~85%+ of trading volume in A-shares (vs ~10–15% in US)
- Key finding from research on 53.4M retail accounts: **retail net buying negatively predicts next-day returns** for all but the largest retail investors
- Retail traders chase price momentum intraday and get caught in reversals

**Implication:** End-of-day retail buying pressure → negative next-day alpha. This is a contrarian signal. You can approximate retail pressure via:
- High volume relative to typical (retail surge)
- Price closing near the high of the day (chasing signal)
- Large positive return on high turnover (momentum chasing)

### Turnover Rate as a Signal
- Chinese retail investors trade very actively → turnover rates are much higher than in developed markets
- **Turnover momentum** (stocks with persistently high relative turnover) is documented as a positive predictor
- But "spiky" one-day turnover predicts reversal; "stable" sustained turnover predicts continuation
- Paper: *Innovative Alpha Strategies for the Chinese A-Share Market* (2025) specifically constructs a "stable turnover momentum" factor using turnover rate stability

```python
# Turnover rate = volume / shares outstanding
# For Feishu data: approximate with amount / (close * volume) is wrong — use volume directly
# Turnover stability = low variance of rolling turnover
daily['turnover_proxy'] = daily['amount']  # total RMB traded
daily['turnover_stability'] = daily.groupby('asset_id')['turnover_proxy'].transform(
    lambda x: 1 / x.rolling(20).std()  # high stability = low vol of turnover
)
```

---

## Factor Zoo: What Works in China

Based on *Factor models for Chinese A-shares* (2024):

| Factor | Works in China? | Notes |
|--------|----------------|-------|
| Market beta | Yes | Basic risk factor |
| Size (small-cap premium) | Weak | Reversed in early 2024; not reliable |
| Value (book-to-market) | Yes | Works, especially earnings-based value |
| Profitability | Mixed | Less consistent than in US |
| Investment | Mixed | Less consistent than in US |
| **Short-term reversal** | **Strong** | 1-week reversal effect is very pronounced |
| Residual momentum | Yes | Momentum after removing factor exposure |
| **Turnover/liquidity** | **Strong** | High turnover predicts reversal |
| Idiosyncratic volatility | Yes | High IVOL → negative returns (low-risk anomaly) |

**Best 3-factor model for China after transaction costs:** Market + Size + Earnings-based value

**Key difference from US:** Momentum is weaker and more prone to reversal without the stability filter. Short-term reversal is stronger.

---

## Momentum in China: The Reversal Problem

Standard 12-1 month momentum (standard US anomaly) often **fails or reverses** in China. Reasons:
- Retail investors mean-revert after chasing momentum
- Regulatory interventions reset trends
- High volatility means momentum signals decay quickly

**What does work:**
- **Residual momentum** (after removing factor exposure) — more stable
- **Stable turnover momentum** — momentum conditioned on persistent high turnover
- **Very short-term** momentum (1–5 days) with quick reversal at 1 week

---

## Opening Auction Specifics

- Opening auction: 09:25–09:30 (call auction)
- `vwap_0930_0935` in Feishu data captures the first 5 minutes of continuous trading after the auction
- The gap between opening auction price and early continuous trading VWAP is informative:
  - **Positive gap** (open > prior close): overnight demand, may reverse intraday
  - **Negative gap**: overnight selling, may rebound

**Overnight gap signal:**
```python
daily['adj_close'] = daily['close'] * daily['adj_factor']
daily['overnight_ret'] = daily.groupby('asset_id')['adj_close'].pct_change()
daily['open_to_close'] = (daily['close'] - daily['open']) / daily['open']
daily['gap_signal'] = daily['overnight_ret'] - daily['open_to_close']  # gap vs intraday
```

---

## LOB in Chinese Context

- LOB data starts at 09:40 (10 minutes after continuous trading opens at 09:30)
- The opening auction forms price via call mechanism — LOB is cleared and rebuilt after auction
- **First snapshot (09:40)** is post-auction LOB rebuild; imbalance here reflects early informed trading
- **Last snapshot (~14:55–15:00)** reflects end-of-day positioning

**China-specific LOB behaviour:**
- At limit-up/limit-down: LOB becomes one-sided (all bids at ask limit, no asks; or vice versa)
- Very thick bid side with thin ask → likely to limit up next day
- This "limit order queue" signal has documented predictive power in Chinese HFT literature

---

## Regulatory Risk

Unlike US markets, Chinese regulators intervene frequently:
- Suspend/halt trading in individual stocks or sectors
- Change margin requirements abruptly
- Circuit breakers (tried in 2016, suspended within days due to cascade effect)
- Short-selling bans (2024)

**Implication:** Backtests on Chinese data tend to be less reliable due to regime changes. An IC that is positive in 2018–2021 may be zero in 2022–2024 after a regulatory shift. Evaluate IC stability over rolling windows.

---

## Summary: Adjustments for Feishu Signals

| US assumption | China adjustment needed |
|--------------|------------------------|
| Long-short both sides | Mostly long-only; short side unreliable |
| No price limits | Filter limit-hit days from evaluation |
| T+0 same-day exit | Hold minimum 1 day (T+1) |
| Momentum works 12-1 month | Use residual momentum or stable turnover momentum |
| Retail noise is small | Retail contrarian signal is strong |
| Short selling enforces efficiency | Mispricing can persist longer |

---

## Papers Referenced
- Microstructure of the Chinese stock market: A historical review, *Pacific-Basin Finance Journal* 2024
- Factor models for Chinese A-shares, *International Review of Financial Analysis* 2024
- Innovative Alpha Strategies for the Chinese A-Share Market (2025) — stable turnover momentum + IVOL

## Connects To
→ [[limit-order-book]] | [[statistical-arbitrage]] | [[mean-reversion]] | [[factor-models]]
