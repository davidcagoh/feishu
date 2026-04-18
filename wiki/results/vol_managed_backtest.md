# Volatility-Managed Portfolio Backtest Results

![Strategy Overview](strategy_overview.png)

**Last updated:** 2026-04-18  
**Best signal:** `vol_managed_v2` (`signals/vol_managed_v2.py`)  
**Framework:** Wang & Li (2024) — inverse realised variance exposure overlay, parameter-tuned  
**Evaluation:** Full in-sample D001–D484 (484 trading days), N=20 stocks, sell-at-open

---

## Current Best: vol_managed_v2

`vol_managed_v2` is a thin wrapper around `vol_managed` with tuned parameters found via exhaustive grid search over 50+ parameter combinations (2026-04-18).

**Optimal parameters:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| `window` (overlay) | **30** | Slower, more stable market-vol estimate → fewer false triggers |
| `sigma_threshold` | **2.0** | Blanks top ~12% vol days (vs ~5% at σ=3.0) |
| `base_window` | 60 | Rolling std window for stock ranking |
| `excl_illiq` | 0.05 | Exclude bottom 5% by 20d avg turnover |
| N stocks | **20** | Confirmed optimal across all sweeps |
| sell_mode | **open** | Sell-at-close gives MDD=11.83%, much worse |

**Algorithm:**
1. Compute `low_vol.compute(daily, window=60, excl_illiq=0.05)` → base stock-selection signal.
2. Compute market variance proxy: cross-sectional mean of squared adjusted returns, rolling mean over `window=30` days.
3. Identify high-volatility days: `rolling_var > 2.0 × median(rolling_var)`.
4. Set those rows to all-NaN → backtest skips rebalancing, holds prior portfolio.

---

## Leaderboard (D001–D484, N=20, sell-at-open)

| Signal | CAGR | SR | MDD | Score | Δ vs low_vol |
|--------|------|----|-----|-------|--------------|
| **vol_managed_v2** ← submission | **9.64%** | **1.032** | **9.38%** | **0.3296** | **+0.0251** |
| vol_managed (w=20, σ=3.0) | 9.04% | 0.981 | 9.38% | 0.3116 | +0.0071 |
| inv_var_vol (1/σ² weights) | 9.04% | 0.981 | 9.38% | 0.3116 | +0.0071 |
| hmm_regime_vol (HMM soft) | 8.48% | 0.923 | 8.56% | 0.2937 | -0.0108 |
| low_vol (N=20 baseline) | 8.81% | 0.961 | 9.38% | 0.3045 | — |
| low_vol (N=100, sell-close) | 9.32% | 0.850 | 13.30% | 0.2636 | n/a |
| cluster_low_vol (K-means) | 5.18% | 0.441 | 10.76% | 0.1286 | -0.1759 |
| vol_managed_120d | 8.03% | 0.904 | 11.23% | 0.2792 | -0.0253 |

---

## Grid Search Results (2026-04-18)

### Phase 1: N-stocks sweep (sigma_threshold=3.0, window=20)

N=20 is clearly optimal. N=10/15 have lower MDD but CAGR and SR fall more. N=25/30 worsen both.

| N | CAGR | SR | MDD | Score |
|---|------|----|-----|-------|
| 10 | 8.06% | 0.899 | 8.56% | 0.2845 |
| 15 | 8.23% | 0.901 | 8.74% | 0.2856 |
| **20** | **9.04%** | **0.981** | **9.38%** | **0.3116** |
| 25 | 8.53% | 0.856 | 10.42% | 0.2692 |
| 30 | 8.72% | 0.878 | 9.55% | 0.2787 |

### Phase 2: Overlay window sweep (N=20, sell=open)

**Key finding: window=30, sigma_threshold=2.0 is the global optimum.**

| Window | σ | CAGR | SR | MDD | Score |
|--------|---|------|----|-----|-------|
| 5 | 2.0 | 8.75% | 0.962 | 9.38% | 0.3045 |
| 20 | 2.5 | 9.18% | 0.988 | 9.38% | 0.3141 |
| 20 | 3.0 | 9.04% | 0.981 | 9.38% | 0.3116 |
| **30** | **2.0** | **9.64%** | **1.032** | **9.38%** | **0.3296** ← global best |
| 30 | 1.5 | 9.17% | 1.000 | 9.38% | 0.3177 |
| 32 | 1.8 | 9.52% | 1.019 | 9.38% | 0.3250 |
| 35 | 1.8 | 9.35% | 1.003 | 9.38% | 0.3194 |

### Phase 3: base_window and excl_illiq (N=20, window=30, σ=2.0)

`base_window=60, excl_illiq=0.05` confirmed optimal. Shorter windows (40d) collapse CAGR. Longer (75-90d) degrade. More liquidity exclusion (>0.08) shrinks the universe too much.

### Phase 4: Sell mode

Sell-at-open is decisively better. Sell-at-close gives MDD=11.83% across all N=20 configs vs 9.38% for open.

---

## PR Signals Evaluation (merged 2026-04-18)

| Signal | Mechanism | Score | Verdict |
|--------|-----------|-------|---------|
| inv_var_vol (#14) | 1/σ² allocation on vol_managed selection | 0.3113 | ≈ baseline; variance in low-vol portfolio is too homogeneous for the weighting to matter |
| cluster_low_vol (#20) | K-means cluster-constrained selection (K=10, 2 per cluster) | 0.1286 | Much worse; K-means forces picks from bad clusters; high churn (5686 trades) |
| hmm_regime_vol (#19) | HMM stress prob → continuous signal scaling | 0.2937 | Worse; HMM over-blanks, loses CAGR; but MDD is lowest at 8.56% |
| vol_managed_120d (#13) | Same as vol_managed but 120d base window | 0.2792 | Much worse; 120d is too slow, introduces lag and higher MDD |

**All 4 PR signals failed to beat the baseline.** The breakthrough came from tuning the *overlay window* parameter within the existing vol_managed framework.

---

## Key Structural Observations

- **MDD=9.38% is structural** for N=20 portfolios on this dataset. The max drawdown event is a single concentrated period that no vol filter can avoid entirely (it happens within the pre-blanking warmup window).
- **The biggest score lever is Sharpe** (weight=0.30). Pushing SR from 0.981 → 1.032 contributed +0.015 to score.
- **CAGR and SR improve together** with window=30 because the slower rolling estimate generates fewer spurious blanks during mild up-vol periods — so the portfolio rebalances on more good days.
- **N=20 is near-optimal** for the universe size (2,270 assets) and bar to entry (10-stock minimum). Fewer than 20 reduces diversification; more than 20 dilutes into weaker-signal assets.

---

## Submission Command (use when OOS data released May 28)

```bash
python eval/generate_submission.py \
    --daily data/daily_data_oos.parquet \
    --sell-mode open \
    --n-stocks 20 \
    --vol-window 60 \
    --excl-illiq 0.05 \
    --output submissions/submission_v2_sell_open.csv
```

Signal: `vol_managed_v2` (window=30, σ=2.0, base_window=60, excl_illiq=0.05).

---

_Generated 2026-04-18 by grid search + iteration session_
