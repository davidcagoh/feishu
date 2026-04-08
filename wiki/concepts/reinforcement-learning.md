# Reinforcement Learning for Trading

RL frames trading as a sequential decision problem: an agent observes market state, takes actions (buy/sell/hold), receives rewards (P&L minus costs), and learns a policy that maximises cumulative discounted reward.

---

## RL Framing of Trading

| RL element | Trading analog |
|-----------|--------------|
| State `s_t` | Price history, inventory, regime probabilities, LOB snapshot |
| Action `a_t` | New inventory level to hold (or change: buy/sell quantity) |
| Reward `r_t` | Mark-to-market P&L minus transaction costs |
| Policy `π(s_t)` | Trading strategy |
| Objective | `max E[Σ γ^t r_t]` |

---

## DDPG (Deep Deterministic Policy Gradient)

Used in [[drl-optimal-trading-partial-info]]. Handles **continuous action spaces** (unlike DQN which is for discrete actions).

**Architecture:**
- **Actor** `π(s_t)` → deterministic action (inventory level)
- **Critic** `Q(s_t, a_t)` → evaluates quality of action in state

Both are neural networks. Training alternates:
1. Critic update: minimise temporal difference error `(r_t + γQ(s_{t+1}, π(s_{t+1})) - Q(s_t, a_t))^2`
2. Actor update: maximise `Q(s_t, π(s_t))` via policy gradient

**Stability tricks:** experience replay, target networks (slowly updated copies of actor/critic).

---

## GRU (Gated Recurrent Unit)

Used to process the **time-series window** of past signal values before feeding into the RL agent.

```
h_t = GRU(h_{t-1}, S_t)    # hidden state encodes signal history
```

Three variants for how to use `h_t`:
1. **hid-DDPG**: `h_t` directly as input to actor/critic (black-box filtering)
2. **prob-DDPG**: `h_t` → classifier → regime probabilities → actor/critic
3. **reg-DDPG**: `h_t` → regressor → `Ŝ_{t+1}` → actor/critic

**Best approach (prob-DDPG):** Regime probabilities are a structured, interpretable compression of `h_t`. The RL agent can reason about "I'm 80% in a high-reversion regime" explicitly.

---

## Key Lesson: Information Structure Matters

From [[drl-optimal-trading-partial-info]]:

> Raw GRU hidden states (hid-DDPG) < next-step forecasts (reg-DDPG) <<< regime probabilities (prob-DDPG)

This is because:
- Hidden states are unstructured and hard for the actor to interpret
- Next-step forecasts are point estimates that discard regime uncertainty
- Regime probabilities provide a **sufficient statistic** for the filtering problem

**Practical implication**: Before feeding data into an RL agent, extract structured features that capture regime information (e.g., HMM regime probabilities, rolling β estimates, volatility regime classification).

---

## Other RL Approaches in Finance

| Method | Suited for | Limitation |
|--------|-----------|-----------|
| DQN | Discrete actions (buy/hold/sell) | Coarse action space |
| DDPG | Continuous inventory control | Unstable training |
| PPO | Complex environments | Sample-inefficient |
| A2C | Parallel environments | Policy gradient variance |
| SAC | Off-policy, continuous | Complex implementation |

Ensemble approaches (PPO + A2C + DDPG) sometimes outperform single methods by adapting to different market conditions.

---

## RL vs Classical Optimal Control

The OU trading problem has a **known analytical solution** when parameters are observed (just trade proportional to deviation from mean). RL becomes necessary when:
1. Parameters are **latent** (must be filtered)
2. Parameters are **regime-switching** (nonlinear filtering)
3. The signal model is **unknown** (model-free)

For the Feishu competition, parameters (mean-reversion level of LOB imbalance etc.) are unknown and likely regime-switching — this is the regime where RL adds value over a simple Kalman filter strategy.

---

## Feishu Competition Notes

**Simple RL baseline using PPO:**
```python
import gymnasium as gym
import numpy as np

class TradingEnv(gym.Env):
    def __init__(self, returns, lob_imbalance):
        self.returns = returns          # (T, N) adjusted daily returns
        self.imbalance = lob_imbalance  # (T, N) daily mean LOB imbalance
        
    def step(self, action):
        # action = portfolio weights (N,)
        reward = (action * self.returns[self.t]).sum()
        # minus transaction cost for weight changes
        self.t += 1
        obs = self._get_obs()
        return obs, reward, done, info
```

**But note:** For the competition, a clean alpha signal (IC/IR on the full dataset) is likely more valuable than a trained RL policy, which may overfit badly on 484 days.

---

## Papers in This Wiki
- [[drl-optimal-trading-partial-info]] — DDPG with GRU for OU signal trading; prob-DDPG
- [[mean-reversion]] — OU signal model underlying the RL problem
- [[statistical-arbitrage]] — RL as a general trading policy for stat-arb signals
