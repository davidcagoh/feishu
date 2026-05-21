"""
Six-layer evaluation stack — feishu port of `backtesting/scripts/eval_layers.py`.

Layered metrics that complement the competition scoring formula
(0.45*CAGR + 0.30*Sharpe + 0.25*(-MDD)) by exposing failure modes a single
risk-adjusted-return number hides.

Layer map (cross-project frame, see root wiki/learnings.md)
----------------------------------------------------------
L1  return            CAGR
L2  risk-adjusted     Sharpe, Calmar (= CAGR / MDD)
L3  sample size       SQN  ( = sqrt(N) * mean_trade / std_trade )
L4  multiple testing  Deflated Sharpe (see `dsr.py`)
L5  tail / path       skew, excess kurtosis, tail_ratio, CVaR-5%,
                      Ulcer Index, Martin Ratio, Pain Index
L6  portfolio-additive Marginal Diversification Benefit (see `correlation_mdb.py`)

Inputs are pure pandas Series of *portfolio value over time* (indexed by
`trade_day_id` such as 'D000'..'D484'). No datetime arithmetic — feishu uses
ordinal trading-day indices and a flat 242 annualisation factor.

This module is deliberately independent of the competition's `run_backtest`
return shape: pass any wallet curve in, get a `LayeredMetrics` back.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

ANNUALISATION = 242.0  # Chinese A-share trading days per year (locked-in).


# ─── Return / wallet helpers ──────────────────────────────────────────────────


def daily_log_returns(wallet: pd.Series) -> pd.Series:
    """Daily log-returns of the wallet level series."""
    return np.log(wallet / wallet.shift(1)).dropna()


def _drawdown_series(wallet: pd.Series) -> pd.Series:
    """Drawdown percentage from running peak. Always <= 0."""
    running_peak = wallet.cummax()
    return (wallet / running_peak - 1.0) * 100.0


# ─── Layer 1 — Return ─────────────────────────────────────────────────────────


def cagr(wallet: pd.Series, annualisation: float = ANNUALISATION) -> float:
    """CAGR computed from wallet endpoints; assumes len(wallet)-1 trading days."""
    n_steps = len(wallet) - 1
    if n_steps <= 0 or wallet.iloc[0] <= 0:
        return float("nan")
    total = wallet.iloc[-1] / wallet.iloc[0]
    years = n_steps / annualisation
    if years <= 0:
        return float("nan")
    return float(total ** (1.0 / years) - 1.0)


# ─── Layer 2 — Risk-adjusted ──────────────────────────────────────────────────


def sharpe(wallet: pd.Series, annualisation: float = ANNUALISATION) -> float:
    """Annualised Sharpe from daily simple returns of the wallet."""
    r = wallet.pct_change().dropna()
    if len(r) < 2 or r.std() == 0:
        return float("nan")
    return float(r.mean() / r.std() * math.sqrt(annualisation))


def max_drawdown(wallet: pd.Series) -> float:
    """Maximum drawdown as a positive fraction (e.g. 0.15 = 15%)."""
    if len(wallet) < 2:
        return float("nan")
    dd = _drawdown_series(wallet)
    return float(-dd.min() / 100.0)


def calmar(wallet: pd.Series, annualisation: float = ANNUALISATION) -> float:
    """CAGR / MDD. Higher is better."""
    mdd = max_drawdown(wallet)
    if mdd is None or math.isnan(mdd) or mdd == 0:
        return float("nan")
    c = cagr(wallet, annualisation)
    if math.isnan(c):
        return float("nan")
    return float(c / mdd)


# ─── Layer 3 — Sample size ────────────────────────────────────────────────────


def sqn(trade_returns: pd.Series) -> float:
    """System Quality Number: sqrt(N) * mean / std of per-trade returns.

    For feishu, "trades" can be one of:
      • per-stock per-day round-trip P&L ratios (preferred — high N)
      • daily portfolio returns as a fallback (treats each day as a trade)
    """
    if len(trade_returns) < 2:
        return float("nan")
    sd = trade_returns.std()
    if sd == 0:
        return float("nan")
    return float(math.sqrt(len(trade_returns)) * trade_returns.mean() / sd)


# ─── Layer 5 — Tail / Path ────────────────────────────────────────────────────


def skew(returns: pd.Series) -> float:
    """Sample skew of daily log-returns. Negative = left-tailed."""
    if len(returns) < 3:
        return 0.0
    return float(stats.skew(returns, bias=False))


def kurt_excess(returns: pd.Series) -> float:
    """Excess kurtosis (Gaussian = 0; fat tails > 0)."""
    if len(returns) < 4:
        return 0.0
    return float(stats.kurtosis(returns, bias=False, fisher=True))


def tail_ratio(returns: pd.Series) -> float:
    """|P95| / |P5|. > 1 = right-tailed (winners > losers)."""
    if len(returns) < 20:
        return float("nan")
    p95 = float(np.quantile(returns, 0.95))
    p5 = float(np.quantile(returns, 0.05))
    if p5 == 0:
        return float("nan")
    return abs(p95) / abs(p5)


def cvar_5(returns: pd.Series) -> float:
    """Mean of returns in the worst 5% (Expected Shortfall at 5%)."""
    if len(returns) < 20:
        return float("nan")
    p5 = float(np.quantile(returns, 0.05))
    tail = returns[returns <= p5]
    if tail.empty:
        return float("nan")
    return float(tail.mean())


def ulcer_index(wallet: pd.Series) -> float:
    """sqrt(mean(drawdown_pct**2)). Path-aware; rewards quick recovery."""
    if len(wallet) < 2:
        return float("nan")
    dd = _drawdown_series(wallet)
    return float(np.sqrt(np.mean(dd**2)))


def pain_index(wallet: pd.Series) -> float:
    """mean(|drawdown_pct|). Simpler than ulcer (no squaring)."""
    if len(wallet) < 2:
        return float("nan")
    dd = _drawdown_series(wallet)
    return float(np.mean(np.abs(dd)))


def martin_ratio(wallet: pd.Series, annualisation: float = ANNUALISATION) -> float:
    """CAGR / Ulcer. Return per unit of underwater pain."""
    ui = ulcer_index(wallet)
    if ui == 0 or math.isnan(ui):
        return float("nan")
    c = cagr(wallet, annualisation)
    if math.isnan(c):
        return float("nan")
    return float(c * 100.0 / ui)


# ─── Aggregation ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LayeredMetrics:
    # L1
    cagr_pct: float
    # L2
    sharpe: float
    calmar: float
    mdd_pct: float
    # L3
    sqn: float
    # L5
    skew: float
    kurt_excess: float
    tail_ratio: float
    cvar_5_pct: float
    ulcer_index: float
    martin_ratio: float
    pain_index: float
    # context
    n_obs: int
    competition_score: float  # 0.45*CAGR + 0.30*Sharpe + 0.25*(-MDD)


def compute(
    wallet: pd.Series,
    trade_returns: pd.Series | None = None,
    annualisation: float = ANNUALISATION,
) -> LayeredMetrics:
    """Compute the full layered metric set for a single backtest.

    `wallet`         : portfolio value series indexed by trade_day_id
    `trade_returns`  : per-trade P&L ratios for SQN; if None, daily returns are
                       used as a fallback observation set.
    """
    returns = daily_log_returns(wallet)
    if trade_returns is None or len(trade_returns) < 2:
        trade_returns = wallet.pct_change().dropna()

    c = cagr(wallet, annualisation)
    sh = sharpe(wallet, annualisation)
    mdd = max_drawdown(wallet)
    score = 0.45 * c + 0.30 * sh + 0.25 * (-mdd)
    return LayeredMetrics(
        cagr_pct=c * 100.0,
        sharpe=sh,
        calmar=calmar(wallet, annualisation),
        mdd_pct=mdd * 100.0,
        sqn=sqn(trade_returns),
        skew=skew(returns),
        kurt_excess=kurt_excess(returns),
        tail_ratio=tail_ratio(returns),
        cvar_5_pct=cvar_5(returns) * 100.0,
        ulcer_index=ulcer_index(wallet),
        martin_ratio=martin_ratio(wallet, annualisation),
        pain_index=pain_index(wallet),
        n_obs=len(returns),
        competition_score=score,
    )


# ─── Rendering ────────────────────────────────────────────────────────────────


def _skew_reading(s: float) -> str:
    if s > 0.5:
        return "right-tailed (rare big wins)"
    if s < -0.5:
        return "left-tailed (rare big losses)"
    return "near-symmetric"


def _kurt_reading(k: float) -> str:
    if k > 3:
        return "fat-tailed (Sharpe overstates)"
    if k < -1:
        return "thin-tailed"
    return "near-Gaussian"


def _tail_reading(t: float) -> str:
    if math.isnan(t):
        return "n/a (N < 20)"
    if t > 1.2:
        return "winners > losers in size"
    if t < 0.8:
        return "losers > winners in size"
    return "balanced"


def format_markdown_table(m: LayeredMetrics, title: str = "") -> str:
    """Markdown sub-table suitable for paste into wiki/results/*.md."""
    lines: list[str] = []
    if title:
        lines += [f"### {title}", ""]
    lines += [
        "| Layer | Metric | Value | Reading |",
        "|---|---|---:|---|",
        f"| L1 | CAGR | {m.cagr_pct:+.2f}% | competition's first scoring term |",
        f"| L2 | Sharpe | {m.sharpe:.3f} | risk-adjusted return |",
        f"| L2 | Calmar | {m.calmar:.2f} | CAGR / MDD |",
        f"| L2 | MDD | {m.mdd_pct:.2f}% | peak-to-trough |",
        f"| L3 | SQN | {m.sqn:.2f} | sqrt(N)·mean/std (sample-size aware) |",
        f"| L5 | Skew | {m.skew:+.2f} | {_skew_reading(m.skew)} |",
        f"| L5 | Excess kurt | {m.kurt_excess:+.2f} | {_kurt_reading(m.kurt_excess)} |",
        f"| L5 | Tail ratio | {m.tail_ratio:.2f} | {_tail_reading(m.tail_ratio)} |",
        f"| L5 | CVaR-5% | {m.cvar_5_pct:+.2f}% | mean loss in worst 5% of days |",
        f"| L5 | Ulcer | {m.ulcer_index:.2f} | path-aware DD (lower better) |",
        f"| L5 | Martin | {m.martin_ratio:.2f} | CAGR / Ulcer |",
        f"| L5 | Pain | {m.pain_index:.2f} | mean abs DD |",
        f"| —  | Score | {m.competition_score:.4f} | 0.45·CAGR+0.30·SR+0.25·(−MDD) |",
        "",
        f"_N_obs (daily): {m.n_obs}; annualisation = {ANNUALISATION:g} days/yr_",
    ]
    return "\n".join(lines)
