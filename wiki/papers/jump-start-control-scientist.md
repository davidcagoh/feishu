# A Jump Start to Stock Trading Research for the Uninitiated Control Scientist

**Authors:** B. Ross Barmish, Simone Formentin, Chung-Han Hsieh, Anton V. Proskurnikov, Sean Warnick  
**Venue:** IEEE CDC 2024 (63rd Conference on Decision and Control, Milan, Dec 2024)  
**DOI:** 10.1109/cdc56724.2024.10886117  
**File:** `strategy_papers/CDC24_2560_FI.pdf`

---

## Purpose

Tutorial paper bridging **control systems theory** and **algorithmic stock trading**, written for engineers unfamiliar with finance. Useful as a reference for the mathematical foundations underlying all other papers in this wiki.

---

## Framing: Trader as Feedback Controller

The central framing is a **feedback control loop**:

```
Market price S_k  →  [Controller / Trading Algorithm]  →  Order u_k  →  [Market]  →  S_{k+1}
```

- `S_k` = closing price at interval k
- `N_k` = shares held (can be negative = short position)
- `M_k` = cash held
- `V_k = N_k S_k + M_k` = total account value
- Control variable `u_k` = total desired market value of position (bounded: `|u_k| ≤ V_k` under no-leverage assumption)

---

## Key Topics Covered

### Order Types (Section III)
- **Market order**: execute immediately at prevailing price
- **Limit order**: execute only at specified price or better; may not fill
- **Stop order**: becomes market order once price hits trigger level

Mathematical models for fill probability and slippage given each order type.

### Feedback Control Design (Section IV)
**Linear feedback controller:**
```
u_k = G × S_k    (proportional control)
```
where G is the controller gain. Long if G > 0, short if G < 0.

**Simultaneous Long-Short (SLS) controller:**
- Maintains two positions simultaneously: one long, one short
- Designed to profit regardless of market direction
- Requires margin account
- Paper analyses stability conditions and break-even analysis

### Portfolio Optimisation (Section V)
- Single-stock: maximise expected return subject to risk constraint
- Multi-stock: Markowitz mean-variance framework
- Convex optimisation formulation; practical constraints (no short sales, sector limits, etc.)

### Kelly Betting (Section VI)
Kelly criterion: bet fraction `f* = (p(b+1) - 1) / b` of current wealth, where:
- `p` = probability of winning
- `b` = net odds (win b per unit bet)
- Maximises **expected log-wealth** (geometric growth rate)

In continuous-time stock context: Kelly fraction determines optimal leverage. Over-betting Kelly leads to ruin; under-betting is suboptimal growth.

**Key property:** Kelly is asymptotically optimal (maximises long-run growth) but can have large drawdowns. Fractional Kelly (e.g., 0.5 × Kelly) trades off growth for lower variance.

### Limit Order Book (Section VII)
The LOB is the "brain center" of electronic markets:

```
Ask side (sellers):
  ask_price_1 (best ask)  ←  tightest spread
  ask_price_2
  ...

Bid side (buyers):
  bid_price_1 (best bid)
  bid_price_2
  ...
```

**Key LOB concepts:**
- **Spread** = ask_price_1 - bid_price_1 (transaction cost for market orders)
- **Depth** = cumulative volume at each level
- **Order flow imbalance** = (bid_volume - ask_volume) / (bid_volume + ask_volume) — a microstructure predictor of short-term price direction
- **Market impact**: large orders move the market; models for temporary and permanent impact
- **High-frequency data**: LOB snapshots timestamped at nanosecond level enable intraday strategies

---

## Backtesting Example (Section VIII)
Applied to **GBTC** (Grayscale Bitcoin Trust) over 2 years:
- Compared linear feedback controllers with varying gains G
- Showed relationship between gain, turnover, and return
- Illustrated importance of transaction cost modelling in backtests

---

## Relevance to Feishu Competition

This paper is foundational background:

| Topic | Direct relevance |
|-------|-----------------|
| LOB structure | Feishu `lob_data_in_sample.parquet` has exactly the 10-level ask/bid structure described here |
| Order flow imbalance | `(bid_volume_1 - ask_volume_1) / (bid_volume_1 + ask_volume_1)` — the CLAUDE.md explicitly cites this as a key signal |
| Transaction costs | Any signal must account for round-trip costs; Kelly framework helps size positions correctly |
| Feedback framing | Useful mental model: the competition asks for an "alpha signal", which is the controller in this framework |

**Key formula from this paper directly applicable:**
```python
lob_imbalance = (bid_volume_1 - ask_volume_1) / (bid_volume_1 + ask_volume_1)
```

---

## Concepts
→ [[limit-order-book]] | [[kelly-betting]] | [[mean-reversion]] | [[statistical-arbitrage]]
