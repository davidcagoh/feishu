# Decision 001 — Pre-registered evaluation for `trend_vol_v6`

**Date:** 2026-05-20
**Status:** Pre-registered before any v6 backtest

## Hypothesis

v5's regime-conditional *threshold* is responsible for the bulk of any
genuine improvement v5 gets over v4. v5's regime-conditional *breadth
expansion* (N=30 on bull days) is either neutral or slightly harmful at
laptop N because the marginal stocks 21–30 dilute the trend-quality
filter.

**v6 codifies the split:** regime-conditional threshold, fixed N=20.

| Regime | v4 | v5 | v6 (proposed) |
|---|---|---|---|
| neutral/stress | thr=-0.025, N=20 | thr=-0.025, N=20 | thr=-0.025, N=20 |
| bull | thr=-0.025, N=20 | thr=0.00, N=30 | thr=0.00, N=20 |

This isolates the threshold effect from the breadth effect.

## Origin of the hypothesis

The accidental `eval_layers.py` run on 2026-05-20 forced v5's signal
through `n_stocks=20` (driver bug — see methodology doc). The resulting
hybrid scored ~0.4212 vs v4's 0.4023 at sell-open (Δ +0.019). That's
**far beyond** the ±0.01 pre-registered band that gates v5 → v4
acceptance, suggesting the threshold-only perturbation may be a
materially better strategy than either v4 or v5.

But this came from a buggy driver, not from a hypothesis-driven design.
**Risk:** it's a fluke driven by sub-period luck.

## Evaluation protocol

### Partition

- Tuning window: D001–D400 (first 400 trading days, ~83% of IS)
- Held-out window: D401–D484 (last 84 trading days)

Both are within the published IS data. Signal computation is on **full**
D001–D484 daily (so lookback windows are populated at the start of the
held-out window). The backtester is restricted to the partition.

This is **not** a substitute for true OOS — D485–D726 is the only true
OOS. The partition is a sanity check that v6's IS edge isn't entirely
concentrated in D001–D400.

### Pre-registered decision criteria

Compare on **Score** at sell-mode = open, N = 20 (v4/v6 native), N = 30 (v5).

| Decision | Criterion |
|---|---|
| **PROMOTE v6 to candidate book** | Tuning ΔScore(v6 − v4) > +0.01 AND held-out ΔScore(v6 − v4) > 0 |
| **SHELVE v6 (overfit suspected)** | Tuning ΔScore(v6 − v4) > +0.01 AND held-out ΔScore(v6 − v4) ≤ 0 |
| **REJECT v6 (no signal)** | Tuning ΔScore(v6 − v4) ≤ +0.01 |
| **INVESTIGATE** | Held-out ΔScore(v6 − v4) > +0.05 (suspiciously large; check regime alignment) |

### Layered checks (advisory, not gating)

In addition to Score, report on the held-out window:
- L2: Sharpe, Calmar, MDD
- L5: kurt_excess, Ulcer, Martin, Pain
- ΔUlcer should be ≤ +0.5 (don't accept v6 if it has materially worse underwater shape)

### Kill rule for v6 if promoted

Same template as backtesting's `decisions/004` (Davies-Ravagnani
continuous shrinkage). To be drafted **only if v6 promotes** — no
speculative kill rules for unaccepted strategies. Form will be:

- Hard kill: rolling 60d MDD > 1.5× IS-max-MDD, or rolling 60d return < −5%
- Continuous shrinkage: live size = clip(rolling_60d_Calmar / IS_Calmar, 0, 1)

## Notes

- Submission for the locked Feishu run does **not** change as a result
  of this evaluation. v4 stays primary, v5 stays contingency. v6, if
  promoted, becomes a future-work candidate.
- The held-out window is bear-dominated (consistent with IS); a bull
  OOS would expose v6 the same way it could expose v4. v6's regime-bull
  branch will rarely fire on the held-out window, so the comparison
  primarily tests whether v6's non-bull branch (identical to v4's
  branch) reproduces v4 cleanly. This is a *necessary but insufficient*
  bar for promotion.
