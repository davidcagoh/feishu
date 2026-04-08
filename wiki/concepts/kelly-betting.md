# Kelly Criterion and Position Sizing

The Kelly criterion determines the **optimal fraction of wealth to bet** to maximise long-run geometric growth rate.

---

## Discrete Kelly Formula

For a bet with:
- `p` = probability of winning
- `b` = net odds (win $b per $1 bet)
- `q = 1-p` = probability of losing

**Kelly fraction:**
```
f* = (p(b+1) - 1) / b = (p·b - q) / b
```

Example: win $2 per $1 bet (b=2), 60% win rate (p=0.6):
```
f* = (0.6 × 2 - 0.4) / 2 = 0.4 = 40% of wealth
```

---

## Continuous-Time Kelly (Log-Optimal Portfolio)

For a risky asset with expected return `μ` and variance `σ²`:
```
f* = μ / σ²      (Kelly leverage)
```

For multiple assets (Kelly-optimal portfolio = maximum Sharpe ratio portfolio):
```
w* = Σ^{-1} μ   (proportional to Markowitz optimal)
```

**Key insight:** The Kelly portfolio is the same as the Markowitz max-SR portfolio. Kelly and mean-variance optimisation agree on the **direction** of the portfolio; they differ on leverage.

---

## Properties of Kelly

| Property | Description |
|----------|-------------|
| Asymptotic optimality | Maximises long-run geometric growth rate |
| No ruin guarantee | Kelly never reaches zero (in continuous time) |
| Large drawdowns | Kelly portfolios can drawdown 50%+ before recovering |
| Half-Kelly | f*/2 reduces drawdown significantly with moderate growth loss |
| Over-betting | Betting > Kelly reduces growth rate; extreme overbetting → ruin |

---

## Kelly in Practice

**Fractional Kelly** is standard. Full Kelly is theoretically optimal but:
- Requires exact knowledge of `μ` and `σ` (rarely available)
- Leads to extreme position sizes with estimation error
- Produces large drawdowns psychologically difficult to hold through

Half-Kelly (0.5 × f*) or quarter-Kelly are common compromises.

**Parameter estimation risk:** If your IC estimate has error σ_IC, the effective Kelly fraction should be reduced by `IC² / (IC² + σ²_IC)`.

---

## Application to Alpha Signals

If you have a signal with:
- Annualised IR (Information Ratio) = `IR`
- Signal predicts returns with IC per period

Then the Kelly position size (normalised) per period is:
```
w ∝ IR / σ_returns
```

**Practical formula for cross-sectional alpha:**
```python
# Signal → z-score → Kelly-weighted position
z_score = (signal - signal.mean()) / signal.std()
position = z_score * (IR / T**0.5)  # scale by IR and rebalance period
```

---

## Feishu Competition Notes

- Kelly sizing is relevant for determining **how aggressively to allocate** to your alpha signal
- For a competition alpha (Sharpe/IC maximisation), you typically report signal values not position sizes — but understanding Kelly helps you think about signal quality
- The relationship `Kelly leverage ∝ Sharpe ratio` means improving your signal's IR directly improves optimal sizing

**Quick Kelly check:**
```python
# Estimate Kelly fraction from backtest
annual_return = ...
annual_vol = ...
kelly_fraction = annual_return / (annual_vol ** 2)
half_kelly = kelly_fraction / 2
print(f"Half-Kelly leverage: {half_kelly:.2f}x")
```

---

## Papers in This Wiki
- [[jump-start-control-scientist]] — Kelly betting in a stock trading context (Section VI)
- [[statistical-arbitrage]] — sizing stat-arb strategies
