# New Signals: Performance Improvement Experiments (2026-04-18)

**Baseline to beat:** `vol_managed` — Score=0.3116, CAGR=9.04%, SR=0.981, MDD=9.38%

## Signals Added This Session

All four signals target confirmed weaknesses from prior analysis.

### Signal #14: `inv_var_vol` — Inverse-Variance Portfolio Weighting

**File:** `signals/inv_var_vol.py`  
**Mechanism:** Same stock selection as `vol_managed`. Allocation changes: weight_i ∝ 1/σ²_i (60-day variance). Lowest-variance stocks get the most capital — theoretically optimal for uncorrelated assets.  
**Backtest integration:** `backtest.py` now accepts optional `weights` DataFrame. `inv_var_vol` exposes `compute_weights()` which `backtest.py` auto-detects and uses.  
**Expected improvement:** Wang & Li (2024) show OOS Sharpe ~1.50 vs ~0.99 unmanaged (+52%). Even partial improvement = significant score gain (Sharpe is the highest-leverage metric: +0.1 SR → +0.003 score).

**Run:**
```bash
python eval/backtest.py --signal inv_var_vol --n-stocks 20 --sell-mode open
```

---

### Signal #20: `cluster_low_vol` — K-Means Cluster-Constrained Low-Vol

**File:** `signals/cluster_low_vol.py`  
**Mechanism:** K-means cluster assets into K=10 groups by 60-day return correlation (PCA-reduced). Select top-2 lowest-vol stocks per cluster → 20 stocks with guaranteed cross-sector diversification.  
**Addresses:** Sector concentration (7 effective bets → up to 10 effective bets).  
**Expected improvement:** Jiao & Zheng (Nov 2025) show 2.28–2.50%/month alpha from cluster-constrained selection. MDD may reduce as concentration drops.  
**Requires:** `scikit-learn` (already in requirements.txt).

**Run:**
```bash
python eval/backtest.py --signal cluster_low_vol --n-stocks 20 --sell-mode open
```

---

### Signal #19: `hmm_regime_vol` — HMM Soft Regime Overlay

**File:** `signals/hmm_regime_vol.py`  
**Mechanism:** Fit 2-state Gaussian HMM on daily cross-sectional features (market return, vol, down-breadth, skewness). Use P(stress state | observations) to continuously scale the low_vol signal: `signal × (1 − P_stress)`. Replaces binary blanking with smooth de-risking.  
**Addresses:** Bull-market risk (soft scaling lets strategy participate in calm bull regimes) and MDD (gradual position reduction as stress builds).  
**Expected improvement:** Boukardagha (2026) Wasserstein HMM achieves Sharpe 2.18 vs 1.59 equal-weight. Soft scaling should push Sharpe above current 0.981 without sacrificing CAGR.  
**Requires:** `hmmlearn` (install via `pip install hmmlearn`). Falls back to rolling-vol percentile proxy if hmmlearn unavailable.

**Run:**
```bash
pip install hmmlearn  # if not installed
python eval/backtest.py --signal hmm_regime_vol --n-stocks 20 --sell-mode open
```

---

### Signal #13: `vol_managed_120d` — Longer Lookback Low-Vol

**File:** `signals/vol_managed_120d.py`  
**Mechanism:** Identical to `vol_managed` but uses 120-day (instead of 60-day) rolling std for stock ranking. Lower turnover → lower transaction costs → net CAGR improvement.

**Run:**
```bash
python eval/backtest.py --signal vol_managed_120d --n-stocks 20 --sell-mode open
```

---

## Backtest Engine Enhancement

`eval/backtest.py` updated to accept `weights: pd.DataFrame | None` in `run_backtest()`.  
When a signal module exposes `compute_weights()`, the CLI auto-detects and uses it for proportional capital allocation instead of equal-weighting.

---

## Expected Comparison Table (fill in after local run)

| Signal | CAGR | Sharpe | MDD | Score | vs Baseline |
|--------|------|--------|-----|-------|-------------|
| vol_managed (baseline) | 9.04% | 0.981 | 9.38% | 0.3116 | — |
| inv_var_vol | TBD | TBD | TBD | TBD | TBD |
| cluster_low_vol | TBD | TBD | TBD | TBD | TBD |
| hmm_regime_vol | TBD | TBD | TBD | TBD | TBD |
| vol_managed_120d | TBD | TBD | TBD | TBD | TBD |

## Priority Order for Submission

Run experiments in this order; update submission if Score > 0.3116:
1. `inv_var_vol` — highest expected Sharpe gain (VMP theory + paper evidence)
2. `hmm_regime_vol` — addresses bull-market risk (soft regime scaling)
3. `cluster_low_vol` — diversification (may also reduce MDD)
4. `vol_managed_120d` — quick win (lower turnover costs)

Best performer → `python eval/generate_submission.py --signal <best>`
