# Six-Layer Evaluation Stack — feishu adaptation

Ported from the cross-project frame in root `wiki/learnings.md`. The full
rationale and each layer's failure-mode-of-the-layer-above logic lives there;
this doc only records feishu-specific adaptations and the wiring on this side.

**Port date:** 2026-05-20
**Modules:** `eval/layers.py`, `eval/dsr.py`, `eval/correlation_mdb.py`
**Driver:** `scripts/eval_layers.py`

## Layer map

| Layer | What it adds | Feishu module |
|---|---|---|
| L1 | Return — CAGR | `layers.cagr` |
| L2 | Risk-adjusted — Sharpe, Calmar, MDD | `layers.sharpe`, `layers.calmar`, `layers.max_drawdown` |
| L3 | Sample size — SQN | `layers.sqn` |
| L4 | Multiple testing — Deflated Sharpe | `dsr.compute_dsr_table` |
| L5 | Tail / Path — skew, kurt_excess, tail_ratio, CVaR-5%, Ulcer, Martin, Pain | `layers.compute` |
| L6 | Portfolio-additive — pairwise correlation, MDB | `correlation_mdb` |

Each layer catches a failure mode of the layer above:
- L2 catches "high CAGR with huge drawdowns."
- L3 catches "high Sharpe on tiny N."
- L4 catches "looked great because we tested 50 variants."
- L5 catches "Sharpe lies when kurtosis is high" and "MDD lies about *shape* of the underwater curve."
- L6 catches "this candidate looks good but is 0.95-correlated with what we already hold."

## Feishu-specific adaptations vs the backtesting port

1. **Annualisation = 242, not 365.** Chinese A-share trading-day count, locked-in. Lives as `eval.layers.ANNUALISATION`.
2. **Ordinal day index.** Feishu uses `trade_day_id` strings (`D000`..`D484`) rather than datetimes. Year math is `n_days / 242`, not `(date_end - date_start).days / 365.25`.
3. **No freqtrade-zip loaders.** Operates directly on the `pd.Series` returned by `eval.backtest.run_backtest(...)["portfolio_value"]`. Zero coupling to backtesting's storage format.
4. **Trade-return source for SQN.** The competition backtester records buy/sell legs but not signed round-trip P&L per position, so SQN defaults to *daily-portfolio* returns. When a per-position P&L stream is added, pass it via `trade_returns=` to `eval.layers.compute(...)`. This is a known approximation — SQN is interpreted as a Sharpe-like number scaled by sqrt(N), not a strict System Quality Number in the Van Tharp sense.

## Where this matters most in feishu

Cross-project learning #4 from root `wiki/learnings.md`: feishu is allowed to *lag* on L4 and L6 until N grows. The binding gate for now is **L2 + L3 + L5**, with L4 reported as a humility check and L6 reserved for the day a real candidate book exists (more than the v4 / v5 / baseline triplet).

Headline implication for strategy selection at feishu's N:
- **Path metrics (Ulcer, Pain, Martin) are more informative than MDD alone** when comparing strategies with similar Score but different underwater shapes. Pre-port we only had MDD; post-port we can distinguish a "fast deep dip" from a "chronic underwater drift."
- **CVaR-5%** is the single most useful loss-tail metric for a long-only A-share strategy because the floor (−10% daily limit-down) bounds the worst case in a way that left-tail kurtosis already understates.
- **Cross-strategy correlation under fill-zero alignment** is structurally pulled toward zero (strategies share dates but not trades on flat days). Treat correlation ≥ 0.85 as the alert threshold here, not the 0.95 used in backtesting.

## CLI

```bash
# Sample-data smoke test
python scripts/eval_layers.py --sample --signals low_vol

# Full IS run on the submission triplet + baseline, write to wiki/results/
python scripts/eval_layers.py \
    --signals trend_vol_v4 trend_vol_v5 vol_managed_v2 low_vol \
    --sell-mode close --n-stocks 20 --write
```

Writes:
- `wiki/results/layered_leaderboard.md` — markdown table per strategy + DSR + correlation + MDB
- `wiki/results/_layered_table.json` — structured rows for downstream consumers

## When DSR becomes binding

Per the cross-project learning, DSR is demoted to a humility check whenever
winning-trade kurtosis is high (the `(kurt-1)/4 · SR²` term dominates the
denominator). Promote it back to a binding gate when *either*:
1. A strategy passes N > ~200 daily observations with bounded kurtosis (< ~3 excess), or
2. We evaluate PBO / CSCV head-to-head and one of them is less kurtosis-sensitive on this data.

Until then: report DSR, do not gate on it.

## Trap to remember: per-signal N is a load-bearing config

**First-run-bug (2026-05-20):** the driver originally passed a single `--n-stocks` to every signal. `trend_vol_v5` exposes `BULL_PARAMS.n_stocks = 30` because its regime overlay caps daily breadth at 30 on bull days and 20 elsewhere. Capping it at the CLI default of 20 silently turned v5 into a different strategy (stricter threshold *without* breadth expansion), which scored ~0.019 higher than v4 — a phantom finding that disappeared once the driver respected the signal's own N contract.

**Fix:** `scripts/eval_layers.py::_resolve_n_stocks(module, cli_default)` checks `module.N_STOCKS`, then `module.BULL_PARAMS.n_stocks`, then falls back to CLI default. When a per-signal override fires, the run logs `[n_stocks override] <name>: <N>`.

**Generalisation:** any signal-level config that the backtester needs and the driver doesn't pass through is a place this trap can recur (excl_illiq, vol_window, sell_mode-per-signal, etc.). When adding a new signal that needs non-default plumbing, expose it as a module attribute and extend `_resolve_*` rather than relying on a CLI flag.

## Where the layered cut adds real insight beyond Score

Confirmed once the driver was fixed (sell-open, N per signal):

| Signal | Score | Sharpe | Kurt (excess) | Ulcer | Martin | Reading |
|---|---:|---:|---:|---:|---:|---|
| trend_vol_v5 | 0.4026 | 1.232 | +2.63 | 3.16 | 3.74 | Near-Gaussian, honest Sharpe |
| trend_vol_v4 | 0.4024 | 1.231 | **+3.41** | 3.09 | 3.81 | **Fat-tailed — Sharpe overstates** |
| trend_vol_v3 | 0.3981 | 1.231 | +2.73 | 4.36 | 2.88 | Uglier underwater shape |

v4 and v5 tie on Score and Sharpe but differ meaningfully on **L5 kurtosis**: v4's excess kurtosis crosses the "fat-tailed" threshold; v5 sits comfortably below. The regime overlay *reduces* tail risk without sacrificing return. Score-scalarization cannot see this; L5 can.

`vol_managed_v2` and `low_vol` have **negative MDB-rp** vs the trend_vol triplet — they add no diversification and should not occupy slots in any candidate book that already holds a trend_vol strategy.

## Competition Score is percentile-based — what this means for L5

PDF Section 7.1 (verified 2026-05-20): the official competition Score is

> Score = 0.45·CAGR_pct + 0.30·SR_pct + 0.25·MDD_pct

where each `*_pct` is the **percentile ranking across all submitted teams**. The raw scalarization `0.45·CAGR + 0.30·Sharpe + 0.25·(−MDD)` reported by the eval driver is an *IS comparison* convenience, not the competition score.

**Implications for which layers matter:**

- **L2 (Sharpe, MDD) percentile rank carries 0.55 of the score, vs CAGR's 0.45.** A strategy that maximises raw Sharpe and minimises raw MDD percentile-dominates one that maximises raw CAGR, even at a CAGR cost. This is the structural reason v4 sell-open was chosen as the submission: it sacrifices CAGR (11.75% vs 12.46% at sell-close) to gain MDD (7.98% vs 9.30%) and SR (1.231 vs 1.196) — the percentile maths favours the latter for any reasonable competitor distribution.
- **L5 (tail metrics) become more important than they would be under absolute scoring.** Under percentile, a strategy with kurtosis-honest Sharpe (like v5: kurt_excess +2.63) percentile-ranks more reliably than one whose Sharpe is overstated by fat tails (v4: kurt_excess +3.41) — the *expected percentile rank* of the honest Sharpe is higher because it's less likely to collapse on OOS. v4 vs v5 Sharpe is a 1.231 vs 1.232 tie in IS; v5's expected percentile rank on OOS should be slightly higher, all else equal. This is one of the few cases where L5 actually changes the read between two tied strategies.
- **The MDB / Layer-6 picture doesn't apply** to competition selection because feishu submits a single strategy, not a book.

**Take-away:** L2 + L5 are the two layers that matter most for feishu submission selection. L3 (SQN) is a sanity check; L4 (DSR) is a humility check for the writeup; L6 is irrelevant pre-submission and relevant only if a book of strategies is ever built.

## Cross-references

- Root `wiki/learnings.md` — full layer rationale + cross-project facts
- `backtesting/scripts/eval_layers.py` — sibling implementation (freqtrade-zip-coupled)
- `backtesting/wiki/methodology/correlation-and-mdb.md` — original MDB methodology doc
- `eval/backtest.py` — competition-mechanics simulator that produces the wallet curves consumed here
