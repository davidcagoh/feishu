# Decision 002 — Pre-registered evaluation for `clustering_reversal`

**Date:** 2026-05-20
**Status:** Pre-registered before any clustering_reversal backtest

## Hypothesis

Within-cluster reversal mean-reverts on a *multi-day* horizon, not just
the overnight gap. If true, this rescues a reversal-shaped signal from
feishu's execution-gap problem (buy at `vwap_0930_0935` [t], overnight
gap already realised) because the alpha plays out over 1–5 days, not
overnight.

Paper basis: Jiao & Zheng (Nov 2025), "Clustering-Augmented Reversal
Strategy: Chinese Stock Market" — 2.28–2.50%/month alpha, clustering
contributes 20–45% of returns, no significant factor loadings.
Indexed at `wiki/papers/clustering-augmented-reversal-china-2025.md`.

Note: the paper's indexed note (written before feishu's portfolio
methodology was mature) pivoted to "clustering as a low_vol
diversifier" → became `cluster_low_vol`. This decision tests the
**paper's actual mechanism** instead — within-cluster reversal, not
within-cluster low-vol — and uses a 5d horizon to escape the overnight
gap.

## Mechanism to test

For each day t (after lookback):

1. Cluster the universe by 60d return-series similarity (K-means after
   PCA whitening; same plumbing as `cluster_low_vol`).
2. Compute each stock's 5d cumulative log return.
3. Compute each cluster's mean 5d return.
4. **Signal** = z-score(−(stock_5d_return − cluster_mean_5d_return)).
   Higher = stock has under-performed its cluster recently → reversal long.
5. Backtester selects top-N=20 by signal.

## Pre-registered decision criteria

Sell mode = open, N = 20, partition D001–D400 / D401–D484
(same protocol as `decisions/001`).

### Gate 1 — Standalone viability

| Criterion | Threshold |
|---|---|
| Tuning CAGR | > 0% |
| Held-out CAGR | > 0% |

If either fails, **SHELVE** as another execution-gap victim (same fate as `volume_reversal`).

### Gate 2 — Orthogonality

| Criterion | Threshold |
|---|---|
| Pairwise correlation vs `trend_vol_v4` (daily returns, full IS) | < 0.85 |

If fails, **SHELVE** — not actually diversifying despite the
mechanism difference.

### Gate 3 — Portfolio additivity (MDB)

| Criterion | Threshold |
|---|---|
| MDB-rp against book = `{trend_vol_v4}` (full IS) | > 0 |
| MDB-eq against same book | > 0 |
| MDB-mv against same book | > 0 |

If any fails, **SHELVE** — orthogonal but not actually additive (the
cluster_low_vol pattern: correlation 0.458, but standalone Sharpe too
weak to lift the book).

### Verdict

- **PROMOTE** iff Gates 1, 2, and 3 all pass.
- **SHELVE** if any gate fails.
- **INVESTIGATE** if standalone CAGR > 12% (suspiciously high; check
  execution-IC for hidden look-ahead before promoting).

## Kill rule (drafted only if PROMOTE)

To be written in `wiki/decisions/003-kill-criteria-clustering-reversal-live.md`
after promotion. Form: hard MDD + continuous shrinkage on rolling Calmar.
No speculative kill rule for an unaccepted strategy.

## Notes

- The signal does **not** change the locked Feishu submission (v4
  primary, v5 contingency).
- Hyperparameters fixed in advance: lookback=60, n_clusters=10,
  reversal_window=5, excl_illiq=0.05, vol_blanking same as
  cluster_low_vol. No HP sweep before validation.
- If PROMOTE: a second hyperparameter sweep (reversal_window ∈ {3, 5, 7, 10},
  n_clusters ∈ {5, 10, 15}) is allowed *only on the tuning window*,
  with the held-out window strictly reserved.
