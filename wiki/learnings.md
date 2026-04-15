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
- **Search:** regime-switching in factor models, volatility-conditional alpha, HMM for equity signals.

---

## Ruled Out

### LOB imbalance as a direct momentum signal
Raw IC is reliably negative over the full 484-day period. This isn't a small-sample artefact — it's consistent with the known retail FOMO mechanism in A-shares. We shouldn't keep re-testing this direction.

---

## What the Next Experiments Should Prioritise

Based on the open hypotheses above, in order:

1. **IC correlation matrix** (hypothesis #1) — highest leverage, costs nothing, determines whether we combine signals
2. **PCA residual signal** (hypothesis #4) — the most novel direction, tests cross-asset information
3. **Intraday LOB split** (hypothesis #3) — directly extends work we've already done on LOB
4. **Momentum check** (hypothesis #2) — sanity check; quick to build, probably negative result but important to know

---

## What the Next Paper Search Should Prioritise

Updated 2026-04-15. Papers found this week (arXiv:2603.10559, arXiv:2602.05580, SSRN:5859882) partially address hypotheses #3 and #4. Remaining open directions:

- **Chinese A-share momentum** — does intermediate-horizon momentum survive (hypothesis #2)? Is it PEAD, earnings-based, or pure price? Still entirely open; no paper found this week addresses it.
- **Signal combination under correlated factors** — how to weight signals that measure overlapping phenomena (hypothesis #1 — IC correlation matrix already computed, showing 3 clusters; the open question is optimal weighting under partial IC correlation).
- **Intraday LOB dynamics, time-of-day effects** — the Kalman paper (SSRN:5859882) partially addresses hypothesis #3 but the morning vs afternoon IC split experiment is still untested. Next search: papers on intraday session-level OFI in Chinese markets specifically.
- **MTP2-GGM whitening validation on Chinese data** — arXiv:2602.05580 uses US/Japan data. Is the MTP2 assumption (positive partial correlations) valid for A-shares where retail-driven common factors are stronger? Search for graphical model approaches applied to high-retail-participation markets.
- **Regime-conditional alpha** (hypothesis #6) — volatility regimes and signal IC stability. Still no dedicated paper found. Search: HMM-based regime detection for equity cross-sectional signals, conditional factor models.
