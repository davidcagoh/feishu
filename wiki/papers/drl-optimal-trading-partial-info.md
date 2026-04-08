# Deep RL for Optimal Trading with Partial Information

**Authors:** Andrea Macrì, Sebastian Jaimungal, Fabrizio Lillo  
**Affiliations:** Scuola Normale Superiore (Pisa) / Univ. Toronto / Oxford-Man / Univ. Bologna  
**arXiv:** 2511.00190v1 (Oct 2025)  
**File:** `strategy_papers/2511.00190v1.pdf`

---

## Core Claim

When trading a mean-reverting signal whose parameters are **latent and regime-switching**, the best RL strategy is to first extract **posterior regime probabilities** from the signal history and feed these into the agent — not raw hidden states, not next-step forecasts. The structure and quality of information given to the RL agent is more important than the sophistication of the RL architecture itself.

---

## Problem Setup

### Market Model
Trading signal `S_t` follows an Ornstein-Uhlenbeck process with **regime-switching parameters**:

```
dS_t = κ_t (θ_t - S_t) dt + σ_t dW_t
```

Where `θ_t` (long-run mean), `κ_t` (mean-reversion speed), and `σ_t` (volatility) each follow **independent Markov chains**. Parameters are **latent** — not directly observable.

### Trading Problem
Agent maximises expected discounted profit:
```
max E[ Σ γ^t r_t(q_t, S_t, S_{t+1}, λ) ]
```
where reward `r_t = I_{t+1}(S_{t+1} - S_t) - λ|q_t|`  
(mark-to-market PnL minus transaction cost `λ` per unit traded)

### Regime Settings (increasing complexity)
1. Only `θ_t` switches (3 regimes: ϕ₁, ϕ₂, ϕ₃)
2. Both `θ_t` and `κ_t` switch
3. All three: `θ_t`, `κ_t`, `σ_t` switch

---

## Three Algorithms (all DDPG + GRU)

All three use a **GRU** to encode the window of past signal values `{S_{t-W}, ..., S_t}` and current inventory `I_t`.

### hid-DDPG (one-step)
- GRU hidden state `o_t` → directly into Actor/Critic
- Treats filtering and trading as a single black-box problem
- No explicit regime estimation

### prob-DDPG (two-step) ← **Best**
- Step 1: Train a GRU classifier to output **posterior probabilities** `P(θ_t = ϕ_j | S_{0:t})` (requires ground-truth labels during training)
- Step 2: Feed `(S_t, I_t, [P(regime=1), P(regime=2), P(regime=3)])` into DDPG
- More interpretable: agent explicitly knows which regime it's likely in
- Dominant performance across all regime settings

### reg-DDPG (two-step)
- Step 1: GRU forecasts next signal value `Ŝ_{t+1}`
- Step 2: Feed `(S_t, I_t, Ŝ_{t+1})` into DDPG
- Provides almost no benefit over hid-DDPG
- Conclusion: raw point forecasts carry less useful structure than regime probabilities

---

## Results Summary

| Algorithm | Performance | Interpretability |
|-----------|-------------|-----------------|
| hid-DDPG | Intermediate | Low |
| prob-DDPG | **Best** | High |
| reg-DDPG | Poor | Medium |

Applied to **real equity pair trading data**, prob-DDPG achieves superior cumulative returns with more stable strategies. The advantage grows as regime complexity increases.

---

## Key Insight

> "The quality and structure of the information supplied to the agent are crucial: embedding probabilistic insights into latent regimes substantially improves both profitability and robustness."

This is the paper's main contribution: a **methodological recipe** for RL trading with latent signals. The regime probability representation acts as a sufficient statistic that compresses the signal history into interpretable state.

---

## Relevance to Feishu Competition

| Feishu situation | Paper analog |
|------------------|--------------|
| LOB imbalance signal drifts across days | Regime-switching OU signal |
| 484 trading days, unknown market regimes | Markov chain on `θ_t` |
| Opaque asset IDs — no fundamental data | Latent parameter setting |

**Implementable ideas:**
- Model the LOB imbalance or daily return residual as an OU process and estimate `θ_t` (rolling mean), `κ_t` (speed), using a Kalman filter or rolling OLS
- Even without RL, the **regime probability** idea is useful: if you can classify each day into "trending" / "mean-reverting" / "volatile" regime and condition your signal on that, performance should improve
- The OU framework directly applies to pairs or spread signals constructed from the daily data

---

## Concepts
→ [[mean-reversion]] | [[reinforcement-learning]] | [[limit-order-book]] | [[statistical-arbitrage]]
