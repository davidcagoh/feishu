# What We've Learned

Running log of findings from experiments. Each entry is either a **confirmed fact**, an **open hypothesis**, or something **ruled out**. The open hypotheses drive what we look for next — in papers and in experiments.

---

## Confirmed Facts

### Mean-reversion dominates A-shares at daily frequency
All 5 daily signals are positive. IC range 0.019–0.035. This is consistent with the Chinese A-share literature: heavy retail participation → short-term overreaction → reliable next-day reversal. It is not a data artefact.

### Volume is a more stable predictor than price
`volume_reversal` (IC std 0.107) is substantially more day-to-day consistent than all price-based signals (IC std 0.165–0.197). This is likely because volume spikes are discrete, rare events — they mark a specific behavioural moment. Price deviations from a moving average or range are more continuous and noisy.
- **Implication:** when designing new signals, prefer signals that condition on discrete events or threshold crossings over smooth continuous measures.

### EOD LOB imbalance is contrarian, not momentum
Raw imbalance IC = −0.005, IR = −2.40 over 484 days. After inversion: small positive IC (~+0.006). Chinese retail investors pile into bids at end of day (FOMO / closing auction effect) — this is a crowded retail signal that predicts *against* itself. Post-inversion IC is weak, suggesting the contrarian effect is also noisy and may not be consistently exploitable alone.

### T+1 settlement + 10% price limits create specific dynamics
Stocks that hit the ±10% limit are uninvestable (we mask them as NaN). T+1 means retail can't daytrade on the same day, concentrating their activity into next-day opening — this amplifies opening-auction reversal signals.

---

## Open Hypotheses

These are the things we don't know yet, ranked roughly by how much they'd change what we do.

### 1. Are our 5 daily signals actually catching the same thing?
We haven't computed the IC cross-correlation matrix. If `volume_reversal`, `price_to_vwap`, `alpha191_046`, `alpha191_071`, and `short_term_reversal` are all highly correlated (>0.6), combining them won't help — they're all proxies for the same retail overreaction. If some pairs are <0.3, a composite could push IR meaningfully above 5.
- **Test:** compute pairwise IC correlation across 484 days. Do this before building any composite.
- **Search:** papers on signal combination under high IC correlation.

### 2. Does intermediate-horizon momentum exist here?
We've only built reversal signals (1–24 day lookbacks). Most markets show 1-month reversal *and* 12-month momentum. We haven't tested any momentum side. If Chinese A-shares have 3–12 month momentum (e.g. earnings surprise drift, which works even in retail-heavy markets), we're leaving an orthogonal source of IC on the table.
- **Test:** build a simple 3-month or 6-month momentum signal and check IC. Expectation is low or negative given strong reversal, but worth verifying.
- **Search:** Chinese A-share intermediate-horizon momentum, earnings momentum, post-earnings drift.

### 3. Does the LOB signal vary intraday? (Morning momentum vs afternoon reversal)
The EOD contrarian finding is about retail closing pressure. But institutions trade heavily in the morning session. The LOB signal computed on morning snapshots only (09:40–12:00) may behave differently — possibly momentum, not contrarian.
- **Test:** split LOB snapshots into morning (09:40–12:00) and afternoon (13:00–15:00), compute IC separately.
- **Paper evidence (2025-12):** Wei (2025, SSRN:5859882) applies a Kalman filter state-space model to 1-minute Chinese A-share data and extracts a latent "efficient price" signal with IC=0.0077. The paper confirms that full-trajectory intraday information improves on EOD snapshots, though IC is modest standalone. Methodology adapts to our 23-24 LOB snapshots. See signal idea #17.
- **Status:** Partially addressed by paper evidence; experiment (morning vs afternoon IC split) still open.

### 4. Does cross-asset information help?
All current signals are purely within-asset (each asset's own price/volume history). The attention factors paper shows that factor residuals — what's left after removing market-wide PCA factors — are more predictable than raw returns. We have now tested basic PCA residuals (vol_rev IR 5.01→11.04) and found strong improvement.
- **PCA residuals confirmed (2026-04-10):** Rolling K=5–10 PCA, residual z-score → vol_rev IR 5.01→11.04 (see `wiki/results/pca_residual.md`). LOB degrades in PCA residual space (captures systematic flow).
- **New paper evidence — cross-market bipartite (2026-03):** Liu et al. (arXiv:2603.10559) confirm that US overnight returns predict Chinese open-to-close returns via a sparse directed bipartite graph. Within our dataset, the analogous test is cluster-lagged returns (see signal #18).
- **New paper evidence — MTP2-GGM whitening (2026-02):** arXiv:2602.05580 shows that PCA residuals still contain latent common structure. Applying MTP2-constrained GGM whitening produces more orthogonal residuals with higher Sharpe ratios and lower CVaR on S&P 500 / TOPIX 500. This directly extends our pca_residual result — see signal #16 (Ledoit-Wolf whitening as practical approximation).
- **Revised status:** Partially confirmed (PCA residuals help). Whether additional MTP2 whitening improves further is an open experiment.

### 5. Why does volume_reversal decay less? Does it saturate on quiet days?
The low IC std of `volume_reversal` is great for IR, but there's a potential downside: on days when volume is normal (no spike), the signal is near-zero — it only fires when there's genuine excess volume. This could mean it covers fewer assets per day, and its capacity is limited.
- **Test:** on days where the top decile of the signal is flat (low signal dispersion), what's the IC? Does the signal concentrate its predictive power on fewer stocks?
- **Search:** volume-based alpha signals, capacity constraints in mean-reversion strategies.

### 6. Is there regime dependence in signal quality?
Signal IC likely varies with market conditions. In high-volatility regimes (e.g. market-wide stress), reversal may be stronger or weaker. The DRL paper shows regime-conditioning significantly improves OU-based strategies.
- **Test:** split days by cross-sectional return std (proxy for market vol). Compute IC of `volume_reversal` and `alpha191_071` per tercile.
- **New paper evidence — Wasserstein HMM (2026-02/03):** Boukardagha (arXiv:2603.04441) shows that a strictly causal Wasserstein HMM feeding regime probabilities into a transaction-cost-aware MV optimiser achieves Sharpe 2.18 vs 1.59 equal-weight, MDD −5.43% vs −14.62% SPX. The key insight is that soft (probabilistic) regime conditioning outperforms both binary thresholds and hard regime-switching. Regime inference stability (not just detection accuracy) is the first-order driver of drawdown reduction.
- **Revised status:** Partially addressed by paper evidence. Concrete next step: replace vol_managed's binary 3×-median threshold with a 2-state Wasserstein HMM stress probability (Signal #19). Still open: whether signal IC itself varies with regime (vs. just the portfolio sizing).

### Any selection signal with a hidden momentum component fails catastrophically (2026-04-20)
Full battery test of 6 new paradigms: `low_beta` (Score=−0.469), `return_consistency` (−0.683), `rolling_sharpe` (−0.877), `quality_composite` (0.061, contaminated by first two), all failed.
- Root cause: every signal that rewards "recent positive performance" has a hidden momentum bias. In Chinese A-shares with T+1 and retail dominance, momentum reverts. Buying at vwap_0930_0935 the day after a stock had high hit-rate / high Sharpe / low beta makes you a bag-holder for the reversal.
- **Rule**: any signal that would select stocks that recently went up is forbidden. Only direction-agnostic signals survive (low_vol, trend-filter as a negative screen, vol-blanking).
- `trend_vol_v2` works because the trend filter is a *negative screen* (remove declining stocks) not a *positive screen* (select recent winners). The low-vol selection does the actual picking; the trend filter only prunes.

### IC/IR metrics do not predict portfolio performance — execution gap is the root cause
**All IC-based reversal signals fail in actual portfolio construction.** Buy execution at `vwap_0930_0935` happens *after* the overnight gap has closed. Reversal alpha is earned close-to-open; by buy time the opportunity is gone. Improving IC (better signal decomposition, PCA whitening, LOB Kalman) does not fix this — it's a structural execution gap, not a signal quality problem.
- Confirmed 2026-04-10: composite_full (IR=9.64) → CAGR=−54%; volume_reversal (IR=5.01) → CAGR=−54%.
- **Implication:** IC/IR is a dead-end for this competition. Do not pursue reversal signal improvements.

### Minimum volatility (low_vol) is the only viable portfolio strategy found
`signals/low_vol.py` (60d rolling std, 5% illiquid exclusion, N=20, sell-at-open) beats the market and all IC-based signals. Baseline: CAGR=+8.81%, SR=0.961, MDD=9.38%, Score=0.3045.
- Mechanism: avoids limit-down spirals and sector blowups in the IS bear-market period. Low turnover → low cost drag.
- Vol-managed overlay (Wang & Li 2024) adds +0.0071 Score by skipping rebalance on top-5% variance days.

### Long-only low-vol implementation is structurally correct (confirmed 2026-04-24)
Soebhag, Baltussen & van Vliet (SSRN:5295002, Jun 2025) show the low-vol premium splits asymmetrically: the long leg (buying low-vol stocks, market-beta-hedged) generates genuine alpha that survives transaction costs; the short leg does not. Our long-only constraint means we implicitly implement only the alpha-generating leg. The bull-market lag is real — low-vol underperforms the market index in bull runs — but the long leg does not generate absolute losses. **Practical implication:** expand N in detected bull regimes to restore beta exposure rather than abandoning the strategy.

### Factor-specific regime detection is feasible from price-only signals (confirmed 2026-04-24)
Shu & Mulvey (arXiv:2410.14841, JPM 2025) demonstrate that a Sparse Jump Model (SJM) applied to factor active-return time series reliably identifies bull/bear regimes for each style factor independently. For the low-vol factor specifically, the SJM confirms underperformance in bull and outperformance in bear — consistent with our IS experience. Feature set is price-only: active return, rolling active vol, market return, market vol. IR improves from 0.05 to ~0.4 via Black-Litterman integration of regime signals. Cross-sectional market volatility is a sufficient proxy for the SJM signal when a full implementation is impractical.

### trend_vol_v5 regime-adaptive wrapper accepted as OOS contingency (2026-04-24)

`signals/trend_vol_v5.py` + `signals/regime.py` — wraps v4 with a price-only bull/neutral/stress detector. On detected bull days, N=30 and trend_threshold=0.00 (from idea #21/#22 paper guidance, not IS sweep). On other days, v4 defaults (N=20, threshold=-0.025).
- IS Score=0.4026 vs v4=0.4024 (ΔScore=+0.0002). Within the pre-registered ±0.01 acceptance band → accepted.
- IS label distribution: 46 bull (9.5%), 57 stress (11.8%), 381 neutral (78.7%). Because IS is bear-dominant, the bull branch rarely fires and the IS penalty is minimal.
- **Known detector weakness:** D458–D481 labeled bull but market declined −13.6%. Low vol ≠ bull; slow-bleed capitulation also has low vol. We did NOT add a return-confirmation guard because that would be IS-fitted. Accepted as structural limitation.
- OOS decision rule pre-committed: if detector flags ≥30% of OOS window as bull, submit v5; else submit v4.

### trend_vol_v4 is the current best strategy (2026-04-21)

`signals/trend_vol_v4.py` — softened trend threshold (-0.025 instead of 0.00) + ERC weights (1/σ).
- CAGR=11.75%, SR=1.207, MDD=**7.98%**, Score=**0.4024** — +1.1% over trend_vol_v3.
- Key improvement: MDD drops from 11.04% → 7.98%. Mechanism is structural: threshold=-0.025 allows stocks that are slightly declining (but not crashing) into the eligible set. On bear-market days when most stocks decline, more candidates → better portfolio diversification → lower peak-to-trough loss.
- Threshold sweep (-0.020 to -0.040) shows MDD improvement is robust across the range (~7.97-8.44% vs 11.04%), confirming the mechanism, not just a lucky number.
- -0.030 has the highest IS score (0.4079 ERC) but is a local spike in equal-weight space; -0.025 chosen as most conservative improvement above noise.

### Max drawdown of trend_vol_v3 occurs mid-IS, NOT in warmup window (confirmed 2026-04-21)

Peak at D265 (54.6% through IS), trough at D367 (75.7% through IS). Duration 102 days. The warmup window is D000–D035 (first 36 days). Prior statement that MDD was "structural floor from warmup" was wrong — it's a mid-period sustained bear episode when most stocks decline and the strict trend filter leaves fewer diversification candidates.

### Counter-trend within low-vol fails (2026-04-21)

`signals/counter_trend_low_vol.py` — same low-vol base, selects stocks with 35d return between -15% and -3% (quiet pullback). Score=-0.1563, MDD=21.37%.
- In a bear IS period, stocks with mild negative 35d trend keep declining; "quiet pullback" is just the early stage of larger declines.
- Daily return correlation with trend_vol_v3 was 0.51 — too high to be useful for diversification.
- 50/50 blend gave Score=0.2475.
- The execution-gap problem is avoided (multi-week signal, not overnight reversal), but the directional thesis is wrong in a bear regime. This could work in a bull OOS period, but we have no IS evidence for it.

### trend_vol_v3 is the current best strategy (2026-04-20)
`signals/trend_vol_v3.py` — trend_vol_v2 selection (low-vol + 35d trend filter + vol-blanking) with 1/σ ERC allocation weights.
- CAGR=12.55%, SR=1.231, MDD=11.04%, Score=**0.3981** — +20.8% over vol_managed_v2.
- Selection mechanism (trend_vol_v2 base): removes "quiet decliners" from the low-vol universe. The 35d trend filter keeps only stocks that are at least holding their price level. Trend_window=35 chosen as robust plateau (30–40d range all beat vol_managed_v2; IS-peak at 37d excluded as noise spike).
- ERC weighting: 1/σᵢ allocation concentrates capital in the quietest holdings within the already-filtered universe. Adds +2.7% relative Score vs equal weight.
- N=20 optimal (N-sweep confirmed; equal-weight N=18 also competitive at Score=0.3936).
- MDD 9.38%→11.04%: trend filter reduces eligible universe on bear-market days → less diversification.

### vol_managed_v2 is the current best strategy (2026-04-18)
`signals/vol_managed_v2.py` — same mechanism as vol_managed but with overlay_window=30 (vs 20) and sigma_threshold=2.0 (vs 3.0), found via exhaustive 50+ combination grid search.
- CAGR=9.64%, SR=1.032, MDD=9.38%, Score=**0.3296** — first SR > 1.0.
- Score improvement: +0.0251 (+8.2%) over baseline low_vol; +0.0180 (+5.8%) over prior best vol_managed.
- Key insight: window=30 produces fewer spurious blanks during mild up-vol periods → more good rebalance days.
- MDD=9.38% is unchanged and structural (see below).

### vol-filter window is the most important overlay parameter; sigma threshold matters less
- window=30 (vs 20): larger rolling window → more stable market-vol estimate → fewer false-positive blanking triggers.
- sigma_threshold=2.0 blanks ~12% of high-vol days vs ~5% at σ=3.0. The higher blanking rate is net positive because the 30d estimate accurately identifies genuine stress.
- Longer windows (≥35) start degrading SR slightly; shorter windows (≤5) degrade MDD.

### All 4 PR signals (inv_var_vol, cluster_low_vol, hmm_regime_vol, vol_managed_120d) failed (2026-04-18)
- `inv_var_vol`: 1/σ² allocation weighting — Score=0.3113 (≈ baseline). Low-vol stocks are too homogeneous for variance-based weights to differentiate.
- `cluster_low_vol`: K-means cluster-constrained selection (K=10, 2/cluster) — Score=0.1286. K-means forces picks from weak clusters; high churn (5,686 trades vs ~1,000 for vol_managed).
- `hmm_regime_vol`: 2-state HMM soft regime scaling — Score=0.2937. Over-blanks: too conservative in detecting "normal" days, loses too much CAGR.
- `vol_managed_120d`: 120d base window — Score=0.2792. Too slow; introduces stale rankings, higher MDD=11.23%.

### 60-day lookback is optimal; longer windows (120–252d) collapse returns
Full sweep (2026-04-17, N=20, sell-at-open): the vol effect literature recommends 120–252d lookbacks, but on D001–D484 they are catastrophically worse. Score at 180d = 0.054, at 252d = −0.023. The IS period is only 484 days with concentrated bear-regime structure — a long lookback window captures stale cross-sectional vol rankings that no longer reflect current risk.

### Sell-at-open dominates sell-at-close for the N=20 vol_managed configuration
At N=20: sell-at-open Score=0.3116 vs sell-at-close Score=0.2826. Sell-at-open captures the post-overnight-gap open price, which for low-vol defensive stocks is more favourable (less adverse selection).

---

## Ruled Out

### LOB imbalance as a direct momentum signal
Raw IC is reliably negative over the full 484-day period. This isn't a small-sample artefact — it's consistent with the known retail FOMO mechanism in A-shares. We shouldn't keep re-testing this direction.

### Intermediate-horizon price momentum in Chinese A-shares (hypothesis #2, closed 2026-04-17)
Liu et al. (SSRN:5130681, Feb 2025) provides a definitive mechanism: Chinese stocks with high past news-day returns are reversed on subsequent non-news days, creating a "tug-of-war" that kills 3–12 month momentum. This is retail-driven (crowding on news events, unwinding on quiet days) and is not present in the US market. Without earnings/news calendar data (unavailable in Feishu), there is no feasible path to isolate the exploitable news-day component. **Do not pursue intermediate-horizon momentum signals.**

---

## What the Next Experiments Should Prioritise

Updated 2026-04-21. Current best: `trend_vol_v4` Score=0.4024. IS parameter space now fully exhausted.

~~1. N-sweep on trend_vol_v2~~ — **Done.** N=20 confirmed optimal with ERC weighting (trend_vol_v3).
~~2. ERC weights on trend_vol_v2~~ — **Done.** trend_vol_v3 = trend_vol_v2 + 1/σ ERC weights. Score 0.3877→0.3981 (+2.7% relative).
~~3. Soften the trend threshold~~ — **Done.** Full sweep -0.07 to +0.03 plus fine sweep around -0.03. Threshold=-0.025 + ERC = trend_vol_v4, Score=0.4024, MDD=7.98%.

4. **Nothing else** — IS parameter space is exhausted. Further tuning is overfitting risk. Remaining OOS risk is structural (bear IS vs unknown OOS regime), not tunable from IS data.

---

## What the Next Paper Search Should Prioritise

Updated 2026-04-29. **Current best:** `trend_vol_v4` (Score=0.4024). IS parameter space exhausted — no further tuning warranted. Paper search should focus solely on OOS regime risk and OOS strategy robustness.

**Do NOT search for:**
- LOB imbalance signals, order flow, microstructure — IC-based, execution gap makes them useless
- Statistical arbitrage, mean-reversion signal construction
- PCA residuals, Kalman filters on LOB data — same problem
- Low-vol factor long/short theory — covered by Soebhag et al. (Jun 2025); long-only validation complete
- Generic SJM / regime-switching factor allocation — covered by Shu & Mulvey (JPM 2025)
- Long-only minimum variance theory / active set characterisation — covered by Kercheval & Sowunmi (Apr 2026)
- OOS regime confirmation (Chinese A-share 2025–2026) — sufficiently addressed; two price-only detectors now available

**Priority 1 — Bull-market resilience (FURTHER ADDRESSED)**
Soebhag et al. (2025) confirm the long leg is robust. Shu & Mulvey (2025) provide the SJM regime detector. Kercheval & Sowunmi (Apr 2026, arXiv:2604.09986) now provide the **formal theoretical proof**: when market betas are all positive (bull environment), the unconstrained LOMV active ratio → 0 (extreme concentration). This formally justifies our N=30 expansion in v5 — without the minimum-N constraint, the portfolio would shrink to ≈ 5 stocks in a bull regime.
- **Remaining open**: Chinese-specific empirical evidence on low-vol bull performance (factor reviews confirm low-vol underperformed in Q1–Q2 2025 Chinese bull, consistent with theory)
- **New beta-std proxy**: Cross-sectional beta variance is a theoretically grounded alternative to vol-ratio for bull detection. Compute 60d rolling betas → cross-sectional std → low std = bull (betas converging). Run on IS data D420–D484 to get independent regime confirmation before May 28.

**Priority 2 — MDD reduction in long-only portfolios (PARTIALLY ADDRESSED)**
Jha et al. (2025) introduce adaptive covariance windows via ARFIMA-FIGARCH. What remains:
- Evidence on regime-aware position sizing specifically in Chinese equity bear episodes
- Stop-loss or drawdown-triggered rebalancing in long-only portfolios
- Whether dynamic vol windows (short in high-vol, long in calm) actually reduce MDD vs. fixed 60d (untested on Feishu IS)

**Priority 3 — Stock selection within the low-vol universe (PARTIALLY ADDRESSED)**
Li & Li (Finance Research Letters, 2025) identify the **MAX filter** as an orthogonal secondary screen for Chinese A-shares: the MAX effect (maximum single-day return in past month) is independent of IV in China. High-MAX stocks are lottery tickets that revert to high IV quickly. Adding a MAX filter (exclude top 25% by max_ret_20d) to the eligible pool after vol-sorting removes post-spike stocks not caught by 60d rolling vol.
- Implementable idea: Signal #24 (see ideas file)
- Caveat: OOS-only test — IS parameter space exhausted
- Still open: quality factors (profitability, earnings stability) — not testable with price/volume-only data; sector-neutral minimum variance — no sector labels in Feishu dataset

**Priority 4 — OOS regime confirmation (PARTIALLY ADDRESSED)**
Two new sources provide OOS regime intelligence:

**Market commentary (analyst consensus, Jan 2026):** Chinese A-share market in H1 2025 was a "slow bull" — CSI 300 +0.03%, CSI 500 +3.31%, CSI 1000 +6.69%. Low-vol and value underperformed Q1–Q2 2025 while growth and small-cap outperformed. Bank of China, Invesco, and Chinadaily consensus: "slow bull" expected to continue into 2026. This means D485+ (≈ H1 2025 onward) is most likely a bull/slow-bull regime → v5 (N=30) is the better OOS submission.

**Pang & Lin (Frontiers in Physics, Aug 2025):** 5-state correlation-based regime classifier for Chinese stocks. Apply their rolling-correlation → MDS → K-means pipeline to our IS data to identify which state D484 is in. If D484 maps to a low-correlation (idiosyncratic) state, that's independent price-only confirmation of the slow-bull regime. Code in wiki/papers/market-state-transitions-crash-warning-china-2025.md.

**Pre-submission action (May 28):** Run both regime checks:
1. regime.py vol-ratio: if ≥30% of OOS days flagged bull → favour v5
2. 5-state correlation classifier on D420–D484 end state: if low-correlation state → corroborates bull

**Remaining search priority:** No longer searching for academic papers on this topic — market commentary + two price-only detectors are sufficient for the decision. Remove from next search priorities.
