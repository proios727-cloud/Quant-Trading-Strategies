"""Ornstein-Uhlenbeck mean-reversion model.

Reference spec: ``specs/mean_reversion.md``.

The series ``X_t`` is modelled as

    dX_t = theta * (mu - X_t) dt + sigma dW_t

Two ways to obtain ``X_t``:

- :func:`ou_spread_strategy` -- a **cointegration spread** between two
  correlated assets: ``log_a - alpha - beta * log_b``, with the hedge ratio
  re-estimated point-in-time. This is the intended use. An equity index log
  price is close to a random walk, so the stationarity premise is weak on it;
  a spread of two co-moving assets is where the model belongs.
- :func:`ou_strategy` -- a single log price, kept for the one-asset case.

Everything here is estimated **point-in-time**: the rolling window that
produces ``(theta, mu, sigma)`` at date ``t`` ends at ``t`` and never sees
``t+1``. The same is true of the hedge ratio, which is the second place this
model can leak the future (spec section 4.3).

A window that fails the identification guard in spec section 4.2 -- a unit
root, a non-positive reversion speed, or zero variance -- yields no score and
**no position**. It does not fall back to the previous ``mu`` and it does not
fill ``z`` with zero, because zero is a signal (dead centre of the band), not
a missing value.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = [
    "TRADING_DAYS_PER_YEAR",
    "OUParams",
    "HedgeParams",
    "fit_ou",
    "rolling_ou",
    "ou_zscore",
    "ou_signal",
    "kelly_leverage",
    "target_weights",
    "ou_frame",
    "ou_strategy",
    "log_price",
    "fit_hedge_ratio",
    "rolling_hedge_ratio",
    "cointegration_spread",
    "spread_returns",
    "ou_spread_strategy",
]

TRADING_DAYS_PER_YEAR = 252

# Numerical floor on (1 - b). b must be bounded away from 1, not merely below
# it. On a deterministic ramp the OLS slope lands within float epsilon of 1 and
# which side it falls on is pure rounding noise; if it lands just below, then
# sigma_eq = sqrt(s2 / (1 - b^2)) becomes a 0/0 form (s2 ~ 0 too) and produces a
# garbage z of order 1e21 -- a real position opened on a pure trend. A floor of
# 1e-6 admits reversion speeds down to ~2.5e-4/year (a half-life of millennia),
# so it never binds on a genuinely mean-reverting series; it exists only to kill
# the degenerate fit. See spec section 4.2.
MIN_ONE_MINUS_B = 1e-6

# Default no-trade band on the target weight, in weight units (0.05 = 5% of
# capital). Applied by the strategy pipelines, not by the `target_weights`
# primitive, whose own default stays 0.0 so it remains a pure map and so
# risk.RiskEngine.run() -- which calls it without this argument -- keeps sizing
# exactly as documented in spec section 4.5.
DEFAULT_REBALANCE_BUFFER = 0.05


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class OUParams:
    """Fitted Ornstein-Uhlenbeck parameters for one window.

    ``valid`` is the section 4.2 identification guard. When it is ``False`` the
    numeric fields are not meaningful and the caller must not trade on them.
    """

    theta: float = np.nan          # reversion speed, per year
    mu: float = np.nan             # long-run mean of X
    sigma: float = np.nan          # diffusion vol, per sqrt(year)
    sigma_eq: float = np.nan       # equilibrium std, sigma / sqrt(2 theta)
    half_life: float = np.nan      # ln2 / theta, in trading days
    b: float = np.nan              # AR(1) coefficient, exp(-theta * dt)
    n_obs: int = 0                 # observations used in the fit
    valid: bool = False

    @property
    def half_life_years(self) -> float:
        return self.half_life / TRADING_DAYS_PER_YEAR


_INVALID = OUParams()


# --------------------------------------------------------------------------
# Fitting
# --------------------------------------------------------------------------


def fit_ou(
    x,
    dt: float = 1.0 / TRADING_DAYS_PER_YEAR,
    min_obs: int = 3,
    max_half_life_window: float = 1.0,
) -> OUParams:
    """Fit an OU process to ``x`` by OLS on the exact AR(1) discretization.

    ``X_{t+dt} = a + b X_t + eta`` with ``b = exp(-theta*dt)`` and
    ``a = mu * (1 - b)``. Uses the exact solution, not an Euler step: Euler
    biases ``theta`` downward on fast-reverting series.

    Returns ``OUParams(valid=False)`` for any degenerate window rather than
    raising, so a rolling loop can simply skip rejected windows.

    ``max_half_life_window`` is the statistical guard from spec section 4.2: the
    fitted half-life may not exceed this multiple of the estimation window's
    span. A half-life longer than the window means no full cycle of the claimed
    reversion was ever observed, and -- because ``mu = a/(1-b)`` -- it is also
    the regime where ``mu`` explodes.
    """
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    n = int(arr.size)
    if n < max(3, int(min_obs)):
        return OUParams(n_obs=n, valid=False)

    prev, nxt = arr[:-1], arr[1:]

    prev_mean = prev.mean()
    sxx = float(((prev - prev_mean) ** 2).sum())
    if not np.isfinite(sxx) or sxx <= 0.0:
        # Constant window: no variation, so no reversion to estimate.
        return OUParams(n_obs=n, valid=False)

    b = float(((prev - prev_mean) * (nxt - nxt.mean())).sum() / sxx)
    a = float(nxt.mean() - b * prev_mean)

    # Guard (spec 4.2). b >= 1 is a unit root or explosive -- not mean
    # reverting. b <= 0 makes ln(b) undefined. The floor on (1 - b) rejects the
    # degenerate near-unit-root fit described at MIN_ONE_MINUS_B.
    if not np.isfinite(b) or b <= 0.0 or (1.0 - b) < MIN_ONE_MINUS_B:
        return OUParams(b=b, n_obs=n, valid=False)

    resid = nxt - (a + b * prev)
    dof = max(n - 2, 1)
    s2 = float((resid**2).sum() / dof)

    theta = -np.log(b) / dt
    if not np.isfinite(theta) or theta <= 0.0:
        return OUParams(b=b, n_obs=n, valid=False)

    half_life = float(np.log(2.0) / theta / dt)

    # Statistical guard (spec 4.2). theta -> 0 makes mu = a/(1-b) a near-0/0
    # divide, so a tiny theta does not give a merely uncertain mu, it gives a
    # meaningless one. Observed on SPY: a window with theta ~ 4e-6 produced
    # mu = 112 against a log price of 6.6 and z = -53. Requiring the half-life
    # to fit inside the estimation window bounds 1-b well away from zero and
    # keeps mu on the scale of the data.
    span = float(max(n - 1, 1))
    if not np.isfinite(half_life) or half_life > span * max_half_life_window:
        return OUParams(
            b=b, theta=theta, half_life=half_life, n_obs=n, valid=False
        )

    # sigma_eq = sqrt(s2 / (1 - b^2)); algebraically identical to
    # sigma/sqrt(2*theta) but numerically steadier when theta is small.
    denom = 1.0 - b * b
    if denom <= 0.0:
        return OUParams(b=b, n_obs=n, valid=False)
    sigma_eq = float(np.sqrt(max(s2, 0.0) / denom))

    # Zero-variance fit (constant, or a deterministic ramp with no residual)
    # gives an undefined z. Refuse rather than divide by zero.
    if not np.isfinite(sigma_eq) or sigma_eq <= 0.0:
        return OUParams(b=b, theta=theta, n_obs=n, valid=False)

    mu = a / (1.0 - b)
    sigma = sigma_eq * np.sqrt(2.0 * theta)

    if not (np.isfinite(mu) and np.isfinite(sigma) and np.isfinite(half_life)):
        return OUParams(b=b, n_obs=n, valid=False)

    return OUParams(
        theta=float(theta),
        mu=float(mu),
        sigma=float(sigma),
        sigma_eq=sigma_eq,
        half_life=half_life,
        b=b,
        n_obs=n,
        valid=True,
    )


def rolling_ou(
    x,
    window: int = 60,
    dt: float = 1.0 / TRADING_DAYS_PER_YEAR,
    min_obs: int = 20,
    max_half_life_window: float = 1.0,
) -> pd.DataFrame:
    """Point-in-time OU parameters, one row per observation of ``x``.

    Row ``t`` is fit on ``x[t-window+1 : t+1]`` inclusive, so it uses only data
    available at ``t``. Rejected windows carry ``valid=False`` and ``NaN``
    parameters.
    """
    series = pd.Series(x, dtype=float)
    values = series.to_numpy()
    window = int(window)
    if window < 1:
        raise ValueError("window must be >= 1")

    records = [_INVALID] * len(values)
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        records[i] = fit_ou(
            values[lo : i + 1],
            dt=dt,
            min_obs=min_obs,
            max_half_life_window=max_half_life_window,
        )

    return pd.DataFrame(
        {
            "theta": [p.theta for p in records],
            "mu": [p.mu for p in records],
            "sigma": [p.sigma for p in records],
            "sigma_eq": [p.sigma_eq for p in records],
            "half_life": [p.half_life for p in records],
            "b": [p.b for p in records],
            "n_obs": [p.n_obs for p in records],
            "valid": [p.valid for p in records],
        },
        index=series.index,
    )


# --------------------------------------------------------------------------
# Score and regime
# --------------------------------------------------------------------------


def ou_zscore(x, ou: pd.DataFrame) -> pd.Series:
    """Standardized deviation ``z_t = (X_t - mu_t) / sigma_eq_t``.

    ``NaN`` where the fit is invalid or ``sigma_eq <= 0``. Never ``+-inf``.
    """
    series = pd.Series(x, dtype=float)
    mu = pd.Series(ou["mu"]).reindex(series.index)
    sigma_eq = pd.Series(ou["sigma_eq"]).reindex(series.index)
    valid = pd.Series(ou["valid"]).reindex(series.index).fillna(False).astype(bool)

    safe = sigma_eq.where((sigma_eq > 0.0) & valid)
    z = (series - mu) / safe
    return z.replace([np.inf, -np.inf], np.nan).rename("z")


def ou_signal(
    z,
    z_entry: float = 2.0,
    z_exit: float = 0.5,
    min_holding: int = 0,
) -> pd.Series:
    """Regime ``q_t`` in ``{-1, 0, +1}`` per spec section 4.4.

    Two thresholds so the book does not churn on every wobble across one line.
    An undefined ``z_t`` forces ``q_t = 0``: no model, no position.

    ``min_holding`` (bars, default 0 = off) blocks an exit or a flip until the
    current regime has been in force for that many bars. It deliberately does
    **not** delay entry: entering from flat is a single trade either way, so
    waiting only forgoes part of the deviation being harvested. Exits and flips
    are where the turnover is, and on a fast-reverting spread they are nearly
    all of it.

    ``min_holding`` is subordinate to the identification guard, not an override
    of it: an undefined ``z_t`` flattens the book mid-hold regardless, because a
    broken fit must stand the strategy down whatever the holding clock says.
    """
    if not 0.0 < z_exit < z_entry:
        raise ValueError("require 0 < z_exit < z_entry")
    if min_holding < 0:
        raise ValueError("min_holding must be >= 0")

    series = pd.Series(z, dtype=float)
    out = np.zeros(len(series), dtype=float)
    regime = 0
    # Bars already committed to the current regime, not counting the one being
    # decided. A transition at bar j means the regime lasted `bars_held` bars.
    bars_held = 0

    for i, zi in enumerate(series.to_numpy()):
        if not np.isfinite(zi):
            regime = 0
            bars_held = 0
        elif regime == 0:
            if zi <= -z_entry:
                regime = 1
            elif zi >= z_entry:
                regime = -1
            bars_held = 1 if regime != 0 else 0
        elif bars_held < min_holding:
            bars_held += 1
        else:
            new_regime = regime
            if abs(zi) <= z_exit:
                new_regime = 0
            elif regime == 1 and zi >= z_entry:
                new_regime = -1
            elif regime == -1 and zi <= -z_entry:
                new_regime = 1
            if new_regime != regime:
                regime = new_regime
                bars_held = 1 if regime != 0 else 0
            else:
                bars_held += 1
        out[i] = regime

    return pd.Series(out, index=series.index, name="signal")


# --------------------------------------------------------------------------
# Sizing
# --------------------------------------------------------------------------


def kelly_leverage(
    z,
    sigma_eq,
    kelly_fraction: float = 0.25,
    max_leverage: float = 1.0,
) -> pd.Series:
    """Signed fractional-Kelly leverage ``f_t = clip(lambda * f*, +-l_max)``.

    Full Kelly is ``f* = -z / (2 * sigma_eq)`` (spec 4.5): the ``dt`` and
    ``theta`` terms cancel. Finite everywhere -- a non-positive ``sigma_eq``
    yields ``0.0``, never ``inf`` or ``NaN``.
    """
    z_s = pd.Series(z, dtype=float)
    se = pd.Series(sigma_eq, dtype=float).reindex(z_s.index)

    raw = -z_s / (2.0 * se.where(se > 0.0))
    sized = kelly_fraction * raw
    return (
        sized.replace([np.inf, -np.inf], np.nan)
        .clip(-abs(max_leverage), abs(max_leverage))
        .fillna(0.0)
        .rename("kelly")
    )


def target_weights(
    signal,
    z,
    sigma_eq,
    kelly_fraction: float = 0.25,
    max_leverage: float = 1.0,
    rebalance_buffer: float = 0.0,
) -> pd.Series:
    """Signed target dollar weight ``D_t = q_t * |f_t|``.

    Direction comes from the regime, magnitude from Kelly. ``q_t`` already
    carries the sign of the deviation, so taking ``|f_t|`` avoids squaring the
    sign and inverting the trade.

    ``rebalance_buffer`` (default 0.0 = off) turns the result into the weight to
    *hold* rather than the raw model target: an existing position is left alone
    until the fresh target differs from it by more than the buffer. This matters
    because both inputs to the sizing drift every bar -- ``z`` moves and
    ``sigma_eq`` is re-estimated on a rolling window -- so the raw target path
    varies continuously and trading to it each bar pays the spread for almost no
    change in risk.

    The band damps *resizing only*. Entry, exit and flip always execute, whatever
    their size:

    - from flat, entering is a signal decision, and a band able to suppress it
      would mean never opening a position smaller than the buffer;
    - to flat (``q_t = 0``, which includes a rejected fit) the book has to be
      able to stand down;
    - a sign change means the model now points the other way. That is a
      direction error, not a sizing one, and must not be damped.

    The output is bounded by ``max_leverage`` whenever the raw target is, since
    every value emitted is a previously accepted (already clipped) target.
    """
    if rebalance_buffer < 0.0:
        raise ValueError("rebalance_buffer must be >= 0")

    q = pd.Series(signal, dtype=float).reindex(pd.Series(z).index).fillna(0.0)
    f = kelly_leverage(z, sigma_eq, kelly_fraction, max_leverage)
    target = (q * f.abs()).fillna(0.0)
    if rebalance_buffer <= 0.0:
        return target.rename("weight")

    held = 0.0
    out = np.zeros(len(target), dtype=float)
    for i, w in enumerate(target.to_numpy(dtype=float)):
        if not np.isfinite(w):
            w = 0.0
        if held == 0.0 or w == 0.0 or np.sign(w) != np.sign(held):
            held = w                      # entry, exit or flip: always execute
        elif abs(w - held) > rebalance_buffer:
            held = w                      # drift cleared the band: rebalance
        out[i] = held                   # otherwise leave the position alone

    return pd.Series(out, index=target.index, name="weight")


# --------------------------------------------------------------------------
# Convenience wrapper
# --------------------------------------------------------------------------


def log_price(price) -> pd.Series:
    """``X_t = log P_t``. Non-positive prices become ``NaN``, not ``-inf``."""
    p = pd.Series(price, dtype=float)
    return np.log(p.where(p > 0.0)).rename("x")


def ou_frame(
    x,
    window: int = 60,
    z_entry: float = 2.0,
    z_exit: float = 0.5,
    kelly_fraction: float = 0.25,
    max_leverage: float = 1.0,
    min_obs: int = 20,
    min_holding: int = 0,
    rebalance_buffer: float = DEFAULT_REBALANCE_BUFFER,
    dt: float = 1.0 / TRADING_DAYS_PER_YEAR,
    max_half_life_window: float = 1.0,
) -> pd.DataFrame:
    """Core signal pipeline on a series that is *already* the stationary object.

    ``x`` may be a log price (see :func:`ou_strategy`) or a cointegration spread
    (see :func:`ou_spread_strategy`). It is used exactly as given and is **never
    logged** -- feeding a raw price here is a caller error.

    Returns a frame holding the fitted parameters, the score, the regime, and
    the target weight at each date. Sizing here is pre-risk-engine; apply
    :class:`risk.RiskEngine` to get executed weights.
    """
    x = pd.Series(x, dtype=float).rename("x")
    ou = rolling_ou(
        x,
        window=window,
        dt=dt,
        min_obs=min_obs,
        max_half_life_window=max_half_life_window,
    )
    z = ou_zscore(x, ou)
    signal = ou_signal(z, z_entry=z_entry, z_exit=z_exit, min_holding=min_holding)
    weight = target_weights(
        signal, z, ou["sigma_eq"], kelly_fraction=kelly_fraction,
        max_leverage=max_leverage, rebalance_buffer=rebalance_buffer,
    )

    return pd.DataFrame(
        {
            "x": x,
            "theta": ou["theta"],
            "mu": ou["mu"],
            "sigma": ou["sigma"],
            "sigma_eq": ou["sigma_eq"],
            "half_life": ou["half_life"],
            "b": ou["b"],
            "valid": ou["valid"],
            "z": z,
            "signal": signal,
            "weight": weight,
        }
    )


def ou_strategy(
    price,
    window: int = 60,
    z_entry: float = 2.0,
    z_exit: float = 0.5,
    kelly_fraction: float = 0.25,
    max_leverage: float = 1.0,
    min_obs: int = 20,
    min_holding: int = 0,
    rebalance_buffer: float = DEFAULT_REBALANCE_BUFFER,
    dt: float = 1.0 / TRADING_DAYS_PER_YEAR,
    max_half_life_window: float = 1.0,
) -> pd.DataFrame:
    """Single-series pipeline: ``X_t = log P_t``, then :func:`ou_frame`.

    Thin wrapper kept for the one-asset case. For two correlated assets, use
    :func:`ou_spread_strategy`, which is the form the model is actually meant
    for -- an equity index log price is close to a random walk, so the
    stationarity premise is weak on it.
    """
    return ou_frame(
        log_price(price),
        window=window,
        z_entry=z_entry,
        z_exit=z_exit,
        kelly_fraction=kelly_fraction,
        max_leverage=max_leverage,
        min_obs=min_obs,
        min_holding=min_holding,
        rebalance_buffer=rebalance_buffer,
        dt=dt,
        max_half_life_window=max_half_life_window,
    )


# --------------------------------------------------------------------------
# Cointegration: a stationary spread between two correlated assets
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class HedgeParams:
    """Engle-Granger hedge parameters for one window.

    ``log_a = alpha + beta * log_b + eps``. ``valid`` is the screen; when it is
    ``False`` the numeric fields are not meaningful and no position may be taken.
    """

    alpha: float = np.nan
    beta: float = np.nan
    r2: float = np.nan
    n_obs: int = 0
    valid: bool = False


_INVALID_HEDGE = HedgeParams()


def fit_hedge_ratio(
    log_a,
    log_b,
    min_obs: int = 3,
    min_r2: float = 0.0,
) -> HedgeParams:
    """OLS of ``log_a`` on ``log_b`` over one window (Engle-Granger step 1).

    Screens, per spec section 4.2 (spread form):

    - enough observations,
    - ``log_b`` not constant (otherwise the slope is undefined),
    - ``beta > 0``. A negative hedge ratio means the "spread" is really a
      long-long bet on two inversely-related assets, not relative value.
    - ``R^2 >= min_r2``. Two unrelated series produce a spread that is just a
      random combination; a real pair must co-move.

    Returns ``HedgeParams(valid=False)`` rather than raising, so a rolling loop
    can skip rejected windows.
    """
    a = np.asarray(log_a, dtype=float)
    b = np.asarray(log_b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("log_a and log_b must have the same length")

    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    n = int(a.size)
    if n < max(3, int(min_obs)):
        return HedgeParams(n_obs=n)

    b_mean = b.mean()
    sxx = float(((b - b_mean) ** 2).sum())
    if not np.isfinite(sxx) or sxx <= 0.0:
        return HedgeParams(n_obs=n)

    beta = float(((b - b_mean) * (a - a.mean())).sum() / sxx)
    alpha = float(a.mean() - beta * b_mean)
    if not (np.isfinite(beta) and np.isfinite(alpha)):
        return HedgeParams(n_obs=n)

    if beta <= 0.0:
        return HedgeParams(alpha=alpha, beta=beta, n_obs=n)

    resid = a - (alpha + beta * b)
    ss_tot = float(((a - a.mean()) ** 2).sum())
    r2 = 1.0 - float((resid**2).sum()) / ss_tot if ss_tot > 0.0 else np.nan
    if not np.isfinite(r2) or r2 < min_r2:
        return HedgeParams(alpha=alpha, beta=beta, r2=r2, n_obs=n)

    return HedgeParams(alpha=alpha, beta=beta, r2=r2, n_obs=n, valid=True)


def rolling_hedge_ratio(
    log_a,
    log_b,
    window: int = 60,
    min_obs: int = 20,
    min_r2: float = 0.0,
) -> pd.DataFrame:
    """Point-in-time hedge ratio: row ``t`` uses only data through ``t``.

    Re-estimating ``beta`` on the full sample and then applying it backwards is
    look-ahead: the hedge ratio would already know the future relationship.
    """
    la = pd.Series(log_a, dtype=float)
    lb = pd.Series(log_b, dtype=float).reindex(la.index)
    window = int(window)
    if window < 1:
        raise ValueError("window must be >= 1")

    va, vb = la.to_numpy(), lb.to_numpy()
    records = [_INVALID_HEDGE] * len(la)
    for i in range(len(la)):
        lo = max(0, i - window + 1)
        records[i] = fit_hedge_ratio(
            va[lo : i + 1], vb[lo : i + 1], min_obs=min_obs, min_r2=min_r2
        )

    return pd.DataFrame(
        {
            "alpha": [h.alpha for h in records],
            "beta": [h.beta for h in records],
            "r2": [h.r2 for h in records],
            "n_obs": [h.n_obs for h in records],
            "valid": [h.valid for h in records],
        },
        index=la.index,
    )


def cointegration_spread(
    price_a,
    price_b,
    window: int = 60,
    min_obs: int = 20,
    min_r2: float = 0.0,
) -> tuple[pd.Series, pd.DataFrame]:
    """Rolling Engle-Granger spread ``log_a - alpha_t - beta_t * log_b``.

    Returns ``(spread, hedge)``. The spread is ``NaN`` wherever the hedge screen
    rejected the window, so no downstream fit can trade on a rejected pair.

    Note the rolling hedge ratio is re-estimated every bar, so the spread series
    is a concatenation of residuals from slightly different regressions. That is
    standard for a rolling backtest and is not look-ahead, but it does mean the
    series is not a single fixed cointegrating vector.
    """
    la = log_price(price_a)
    lb = log_price(price_b).reindex(la.index)
    hedge = rolling_hedge_ratio(la, lb, window=window, min_obs=min_obs, min_r2=min_r2)

    spread = la - hedge["alpha"] - hedge["beta"] * lb
    return spread.where(hedge["valid"]).rename("spread"), hedge


def spread_returns(price_a, price_b, hedge, lag: int = 1) -> pd.Series:
    """Return on holding the spread: ``r_a - beta_{t-lag} * r_b``.

    The hedge ratio is lagged because the ratio *used to put the trade on* was
    the one estimated at the decision bar, not the one observed over the return
    interval. Using the contemporaneous ``beta`` here would smuggle in the
    future relationship between the legs.
    """
    pa = pd.Series(price_a, dtype=float)
    pb = pd.Series(price_b, dtype=float).reindex(pa.index)
    ra = pa.pct_change()
    rb = pb.pct_change()
    beta_lag = pd.Series(hedge["beta"], dtype=float).reindex(pa.index).shift(lag)
    return (ra - beta_lag * rb).fillna(0.0).rename("spread_return")


def ou_spread_strategy(
    price_a,
    price_b,
    window: int = 60,
    ou_window: int | None = None,
    z_entry: float = 2.0,
    z_exit: float = 0.5,
    kelly_fraction: float = 0.25,
    max_leverage: float = 1.0,
    min_obs: int = 20,
    min_r2: float = 0.0,
    min_holding: int = 0,
    rebalance_buffer: float = DEFAULT_REBALANCE_BUFFER,
    dt: float = 1.0 / TRADING_DAYS_PER_YEAR,
    max_half_life_window: float = 1.0,
    leverage_on_gross: bool = True,
) -> pd.DataFrame:
    """Two-asset pipeline: hedge -> spread -> OU fit -> z -> regime -> weights.

    ``window`` sets the hedge-ratio regression; ``ou_window`` (default: the same)
    sets the OU estimation window on the spread.

    ``leverage_on_gross`` controls what ``max_leverage`` bounds. A spread
    position of weight ``w`` is ``w`` long A and ``w*beta`` short B, so its
    gross notional is ``|w| * (1 + |beta|)``. With the flag on (default) the
    weight is scaled down so ``max_leverage`` bounds *gross* exposure, which is
    what a risk limit should mean. With it off, ``max_leverage`` bounds only the
    spread weight and true gross can reach ``max_leverage * (1 + |beta|)``.

    Adds ``beta``, ``alpha``, ``r2``, ``weight_raw``, ``weight_a`` and
    ``weight_b`` to the frame from :func:`ou_frame`. ``x`` is the spread.

    ``rebalance_buffer`` is the no-trade band passed through to
    :func:`target_weights` (default 0.05). It is applied to the *spread* weight
    before the gross normalization, so the band is in units of the spread
    position, and ``weight_a``/``weight_b`` inherit it unchanged.
    """
    spread, hedge = cointegration_spread(
        price_a, price_b, window=window, min_obs=min_obs, min_r2=min_r2
    )

    frame = ou_frame(
        spread,
        window=window if ou_window is None else int(ou_window),
        z_entry=z_entry,
        z_exit=z_exit,
        kelly_fraction=kelly_fraction,
        max_leverage=max_leverage,
        min_obs=min_obs,
        min_holding=min_holding,
        rebalance_buffer=rebalance_buffer,
        dt=dt,
        max_half_life_window=max_half_life_window,
    )

    beta = hedge["beta"].reindex(frame.index)
    frame["alpha"] = hedge["alpha"].reindex(frame.index)
    frame["beta"] = beta
    frame["r2"] = hedge["r2"].reindex(frame.index)

    frame["weight_raw"] = frame["weight"]
    if leverage_on_gross:
        # 1 + |beta| >= 1, so dividing never levers the position up.
        gross_per_unit = (1.0 + beta.abs()).clip(lower=1.0).fillna(1.0)
        frame["weight"] = (frame["weight"] / gross_per_unit).fillna(0.0)

    frame["weight_a"] = frame["weight"]
    frame["weight_b"] = (-frame["weight"] * beta).fillna(0.0)
    return frame

