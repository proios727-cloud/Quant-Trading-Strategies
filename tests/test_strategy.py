"""Pytest suite for the Ornstein-Uhlenbeck mean-reversion model.

Covers the edge cases the spec calls out in section 11: zero volatility,
non-stationary series, market shocks, kill-switch execution, and look-ahead.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from risk import DrawdownKillSwitch, RiskEngine, RiskLimits
from strategy import (
    cointegration_spread,
    fit_hedge_ratio,
    fit_ou,
    kelly_leverage,
    log_price,
    ou_frame,
    ou_signal,
    ou_spread_strategy,
    ou_strategy,
    ou_zscore,
    rolling_hedge_ratio,
    rolling_ou,
    spread_returns,
    target_weights,
)

DT = 1.0 / 252.0


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def simulate_ou(n, theta, mu, sigma, dt=DT, x0=None, seed=7):
    """Exact discretization of dX = theta(mu - X)dt + sigma dW."""
    rng = np.random.default_rng(seed)
    x = np.empty(n, dtype=float)
    x[0] = mu if x0 is None else x0
    b = np.exp(-theta * dt)
    sd = sigma * np.sqrt((1.0 - np.exp(-2.0 * theta * dt)) / (2.0 * theta))
    for i in range(1, n):
        x[i] = mu + (x[i - 1] - mu) * b + sd * rng.standard_normal()
    return pd.Series(x, index=pd.bdate_range("2015-01-01", periods=n))


def flat_index(n, start="2020-01-01"):
    return pd.bdate_range(start, periods=n)


# --------------------------------------------------------------------------
# fitting
# --------------------------------------------------------------------------


def test_fit_recovers_known_parameters():
    # A fast-reverting process, so b is well away from 1 and theta is
    # well identified. The persistent case is covered separately below.
    theta, mu, sigma = 20.0, 4.0, 0.5
    x = simulate_ou(4000, theta, mu, sigma, seed=11)
    p = fit_ou(x)

    assert p.valid
    assert p.theta == pytest.approx(theta, rel=0.10)
    assert p.mu == pytest.approx(mu, abs=0.02)
    assert p.sigma == pytest.approx(sigma, rel=0.15)
    assert p.b == pytest.approx(np.exp(-theta * DT), rel=0.05)


def test_persistent_process_theta_is_noisy_but_consistent():
    """theta=5 -> b~0.98, close to a unit root.

    Single-window theta estimates are high-variance (a Hurwicz-type problem),
    while mu stays tightly identified. This is a property of the AR(1)
    estimator, not a defect -- it is why the spec treats theta as a diagnostic
    and why sizing is fractioned with a hard leverage cap.
    """
    fits = [fit_ou(simulate_ou(5000, 5.0, 4.0, 0.5, seed=s)) for s in range(8)]

    thetas = [p.theta for p in fits]
    mus = [p.mu for p in fits]

    assert np.mean(thetas) == pytest.approx(5.0, rel=0.20)   # consistent
    assert np.std(thetas) > 0.0                              # but noisy
    assert np.mean(mus) == pytest.approx(4.0, abs=0.03)      # mu is tight


def test_half_life_matches_theta():
    x = simulate_ou(2000, 10.0, 4.0, 0.5, seed=3)
    p = fit_ou(x)
    assert p.valid

    # Exact relationship, independent of estimation noise.
    assert p.half_life == pytest.approx(np.log(2.0) / p.theta / DT, rel=1e-9)
    assert p.half_life_years == pytest.approx(p.half_life / 252.0, rel=1e-9)

    # And on a well-identified process, the true half-life.
    p2 = fit_ou(simulate_ou(4000, 20.0, 4.0, 0.5, seed=11))
    assert p2.half_life == pytest.approx(np.log(2.0) / 20.0 / DT, rel=0.10)


def test_sigma_eq_matches_stationary_std():
    x = simulate_ou(6000, 5.0, 4.0, 0.5, seed=5)
    p = fit_ou(x)
    assert p.valid
    # The sample std of the series should match the fitted equilibrium scale.
    assert p.sigma_eq == pytest.approx(float(x.std()), rel=0.20)


def test_fit_ou_degenerate_inputs_do_not_raise():
    assert not fit_ou([]).valid
    assert not fit_ou([1.0]).valid
    assert not fit_ou([1.0, 2.0]).valid
    assert not fit_ou([np.nan] * 50).valid
    assert not fit_ou([np.nan, 1.0, np.nan, 2.0]).valid


# --------------------------------------------------------------------------
# edge case: zero volatility
# --------------------------------------------------------------------------


def test_zero_volatility_constant_series_is_rejected():
    """A constant series has no variation, so no reversion can be estimated."""
    x = pd.Series([4.0] * 200)
    p = fit_ou(x)
    assert not p.valid
    assert np.isnan(p.theta)


def test_zero_volatility_produces_no_positions():
    price = pd.Series([100.0] * 200, index=flat_index(200))
    res = ou_strategy(price, window=60, min_obs=20)

    assert not res["valid"].any()
    assert res["z"].isna().all()
    assert (res["signal"] == 0).all()
    assert (res["weight"] == 0.0).all()
    assert np.isfinite(res["weight"]).all()


def test_kelly_zero_sigma_is_zero_not_inf():
    """sigma_eq = 0 must not divide by zero."""
    z = pd.Series([2.0, -2.0, 0.0])
    se = pd.Series([0.0, 0.0, 0.0])
    f = kelly_leverage(z, se)

    assert np.isfinite(f).all()
    assert (f == 0.0).all()


def test_zero_volatility_engine_leaves_equity_flat():
    price = pd.Series([100.0] * 200, index=flat_index(200))
    res = ou_strategy(price, window=60, min_obs=20)
    returns = price.pct_change().fillna(0.0)

    report = RiskEngine().run(res["signal"], res["z"], res["sigma_eq"], returns)

    assert (report.executed_weights == 0.0).all()
    assert report.equity.iloc[-1] == pytest.approx(1.0)
    assert not report.tripped


# --------------------------------------------------------------------------
# edge case: non-stationary series must not be traded
# --------------------------------------------------------------------------


def test_exponential_trend_is_rejected():
    """b > 1 is explosive -- the guard must refuse it."""
    x = pd.Series(np.log(100.0) + 0.01 * np.arange(300))
    p = fit_ou(x)
    assert p.b >= 1.0
    assert not p.valid


def test_linear_ramp_is_rejected():
    """A perfect ramp gives b == 1 and zero residual variance."""
    x = pd.Series(np.linspace(0.0, 10.0, 300))
    p = fit_ou(x)
    assert not p.valid


def test_trending_price_series_yields_no_valid_windows():
    price = pd.Series(np.exp(np.log(100.0) + 0.01 * np.arange(300)),
                      index=flat_index(300))
    res = ou_strategy(price, window=60, min_obs=20)
    assert not res["valid"].any()
    assert (res["weight"] == 0.0).all()


def test_half_life_longer_than_window_is_rejected():
    """A near-trend window fits an enormous half-life -- the reversion being
    claimed was never observed in the window. This is the exact regime that
    produced the mu blow-up on SPY."""
    rng = np.random.default_rng(0)
    x = pd.Series(4.0 + 0.01 * np.arange(60) + 0.005 * rng.standard_normal(60))

    p = fit_ou(x)
    assert p.half_life > 59.0        # longer than the window span
    assert not p.valid
    assert np.isnan(p.mu)            # no meaningful mu is reported

    # The same trend with enough noise to actually identify reversion passes.
    ok = pd.Series(4.0 + 0.01 * np.arange(60) + 0.03 * rng.standard_normal(60))
    p2 = fit_ou(ok)
    assert p2.valid
    assert p2.half_life <= 59.0


def test_max_half_life_window_parameter_is_enforced():
    x = simulate_ou(500, 10.0, 4.0, 0.5, seed=3)
    assert fit_ou(x).valid              # H ~ 17 days, well inside 499 bars

    # Demanding H fit inside 1% of the span (5 bars) must refuse it.
    assert not fit_ou(x, max_half_life_window=0.01).valid


def test_mu_stays_on_the_scale_of_the_data():
    """Regression: theta -> 0 used to blow mu up via a/(1-b)."""
    rng = np.random.default_rng(4)
    x = pd.Series(np.cumsum(rng.standard_normal(400)) * 0.01 + 4.0)
    res = ou_strategy(np.exp(x), window=60, min_obs=20)

    valid = res["valid"]
    assert valid.any()
    # mu must stay in the neighbourhood of the observed log price.
    lo, hi = float(res["x"].min()), float(res["x"].max())
    pad = 2.0 * (hi - lo)
    assert res.loc[valid, "mu"].between(lo - pad, hi + pad).all()
    # And the score must not explode.
    assert res["z"].abs().max() < 20.0


def test_random_walk_stays_finite():
    """A random walk may sneak under the guard, but must never blow up."""
    rng = np.random.default_rng(2)
    x = pd.Series(np.cumsum(rng.standard_normal(400)) * 0.01 + 4.0)
    price = np.exp(x)
    res = ou_strategy(price, window=60, min_obs=20)

    assert np.isfinite(res["weight"]).all()
    assert np.isfinite(res["z"].dropna()).all()
    assert res["weight"].abs().max() <= 1.0 + 1e-12


# --------------------------------------------------------------------------
# score and signal
# --------------------------------------------------------------------------


def test_zscore_sign_follows_deviation():
    x = pd.Series([1.0, 2.0, 3.0])
    ou = pd.DataFrame(
        {
            "mu": [2.0, 2.0, 2.0],
            "sigma_eq": [1.0, 1.0, 1.0],
            "valid": [True, True, True],
        }
    )
    z = ou_zscore(x, ou)
    assert z.iloc[0] < 0.0   # below equilibrium -> cheap
    assert z.iloc[1] == pytest.approx(0.0)
    assert z.iloc[2] > 0.0   # above equilibrium -> rich


def test_zscore_masks_invalid_windows():
    x = pd.Series([1.0, 2.0, 3.0])
    ou = pd.DataFrame(
        {
            "mu": [2.0, 2.0, 2.0],
            "sigma_eq": [1.0, 0.0, 1.0],
            "valid": [True, False, True],
        }
    )
    z = ou_zscore(x, ou)
    assert np.isnan(z.iloc[1])
    assert np.isfinite(z.dropna()).all()


def test_rolling_ou_flags_only_valid_windows():
    x = simulate_ou(300, 5.0, 4.0, 0.5, seed=13)
    ou = rolling_ou(x, window=60, min_obs=20)

    assert not ou["valid"].iloc[:19].any()   # below min_obs
    assert ou["valid"].iloc[-1]
    assert (ou["theta"].dropna() > 0).all()


def test_signal_entry_exit_and_hold():
    z = pd.Series([0.0, 2.5, 1.0, 0.2, -2.5, -1.0, 0.0])
    sig = ou_signal(z, z_entry=2.0, z_exit=0.5)
    assert sig.tolist() == [0.0, -1.0, -1.0, 0.0, 1.0, 1.0, 0.0]


def test_signal_flips_direction_on_opposite_extreme():
    z = pd.Series([-2.5, 3.0])
    assert ou_signal(z, 2.0, 0.5).tolist() == [1.0, -1.0]


def test_signal_undefined_z_forces_flat():
    z = pd.Series([-2.5, np.nan, -2.5])
    assert ou_signal(z, 2.0, 0.5).tolist() == [1.0, 0.0, 1.0]


def test_signal_holds_inside_band_between_thresholds():
    z = pd.Series([-2.5, -1.5, -1.5, 0.4])
    # z stays between exit and entry -> keep the long; then exit.
    assert ou_signal(z, 2.0, 0.5).tolist() == [1.0, 1.0, 1.0, 0.0]


def test_signal_rejects_inverted_thresholds():
    with pytest.raises(ValueError):
        ou_signal(pd.Series([0.0]), z_entry=1.0, z_exit=1.0)
    with pytest.raises(ValueError):
        ou_signal(pd.Series([0.0]), z_entry=2.0, z_exit=0.0)


# --------------------------------------------------------------------------
# minimum holding period
# --------------------------------------------------------------------------


def test_min_holding_zero_reproduces_the_unconstrained_regime():
    """The default must not perturb the documented section 4.4 behaviour."""
    rng = np.random.default_rng(11)
    z = pd.Series(rng.standard_normal(500) * 2.5)
    pd.testing.assert_series_equal(
        ou_signal(z, 2.0, 0.5, min_holding=0), ou_signal(z, 2.0, 0.5)
    )


def test_min_holding_blocks_an_exit_that_would_otherwise_fire():
    # z exits the band at bar 1; the hold keeps the position through bar 2.
    z = pd.Series([-2.5, 0.1, 0.1, 0.1, 0.1])
    assert ou_signal(z, 2.0, 0.5).tolist() == [1.0, 0.0, 0.0, 0.0, 0.0]
    assert ou_signal(z, 2.0, 0.5, min_holding=3).tolist() == [1.0, 1.0, 1.0, 0.0, 0.0]


def test_min_holding_holds_a_regime_for_at_least_that_many_bars():
    rng = np.random.default_rng(3)
    z = pd.Series(rng.standard_normal(3000) * 3.0)

    for min_holding in (1, 3, 7):
        sig = ou_signal(z, 2.0, 0.5, min_holding=min_holding)
        # Walk the *completed* regimes: each nonzero run must span >= min_holding.
        # A regime still on at the last bar is excluded -- it has not completed,
        # so its length says nothing about whether the constraint held.
        runs = []
        current, length = 0.0, 0
        for value in sig:
            if value == current and value != 0.0:
                length += 1
            else:
                if current != 0.0:
                    runs.append(length)
                current, length = value, (1 if value != 0.0 else 0)
        if current != 0.0 and length >= min_holding:
            runs.append(length)
        assert runs, "expected at least one completed regime"
        assert min(runs) >= min_holding


def test_min_holding_blocks_a_flip_as_well_as_an_exit():
    """A flip is an exit plus an entry, so it pays the spread twice."""
    z = pd.Series([-2.5, 3.0, 3.0, 3.0])
    assert ou_signal(z, 2.0, 0.5).tolist() == [1.0, -1.0, -1.0, -1.0]
    assert ou_signal(z, 2.0, 0.5, min_holding=3).tolist() == [1.0, 1.0, 1.0, -1.0]


def test_min_holding_still_yields_to_the_identification_guard():
    """A broken fit stands the book down mid-hold; the clock does not outrank it."""
    z = pd.Series([-2.5, -2.5, np.nan, -2.5, -2.5])
    assert ou_signal(z, 2.0, 0.5, min_holding=5).tolist() == [1.0, 1.0, 0.0, 1.0, 1.0]


def test_min_holding_does_not_delay_entry():
    """Entering from flat is one trade either way; waiting only forgoes edge."""
    z = pd.Series([0.0, 0.0, 0.0, -2.5, -2.5])
    assert ou_signal(z, 2.0, 0.5, min_holding=5).tolist() == [0.0, 0.0, 0.0, 1.0, 1.0]


def test_min_holding_reduces_churn_when_reentry_beats_the_hold():
    """Churn only falls if a re-entry lands inside the hold window.

    On a series that whipsaws in and out of the band, the hold merges an
    exit + re-entry pair into one continuous position and the trade count drops.
    On a slow, clean reversion the exit is merely delayed, the same trade still
    happens, and the count is unchanged -- so this is a property of the series,
    not of the constraint.
    """
    rng = np.random.default_rng(5)
    z = pd.Series(rng.standard_normal(2000) * 3.0)
    fast = ou_signal(z, 2.0, 0.5, min_holding=0)
    slow = ou_signal(z, 2.0, 0.5, min_holding=3)
    assert (slow.diff().fillna(slow) != 0).sum() < (fast.diff().fillna(fast) != 0).sum()


def test_min_holding_rejects_negative():
    with pytest.raises(ValueError):
        ou_signal(pd.Series([0.0]), min_holding=-1)


def test_min_holding_is_threaded_through_the_spread_pipeline():
    pa, pb = make_pair(n=2000)
    default = ou_spread_strategy(pa, pb, window=60, min_obs=20)
    fast = ou_spread_strategy(pa, pb, window=60, min_obs=20, min_holding=0)
    slow = ou_spread_strategy(pa, pb, window=60, min_obs=20, min_holding=3)

    # Threading: the default is the unconstrained regime, and 3 changes it.
    pd.testing.assert_series_equal(default["weight"], fast["weight"])
    assert (slow["signal"] != fast["signal"]).any()

    f, s = fast["signal"], slow["signal"]

    # The two properties the holding period actually guarantees.
    #
    # 1. It never exits earlier than the unconstrained regime: the held bars are
    #    a superset. Every difference is the constraint staying in, never leaving
    #    sooner -- so it cannot reduce exposure, only extend it.
    assert not ((s == 0.0) & (f != 0.0)).any()
    assert (s != 0.0).sum() >= (f != 0.0).sum()

    # 2. Entry is not delayed, so the number of entries is identical.
    fast_entries = int(((f != 0.0) & (f.shift(1).fillna(0.0) == 0.0)).sum())
    slow_entries = int(((s != 0.0) & (s.shift(1).fillna(0.0) == 0.0)).sum())
    assert slow_entries == fast_entries

    # What it does NOT guarantee is less turnover. Kelly resizes the position
    # every bar (z and sigma_eq both drift), so the weight path varies
    # continuously and a longer hold keeps that path alive for more bars. And
    # delaying an exit does not remove it -- the regime still ends, just later --
    # so the trade count only falls when a re-entry lands inside the hold window
    # and gets merged. On a monotone exit the traded notional is *exactly* the
    # same: one jump of |w| versus three smaller jumps summing to |w|. Dollar
    # turnover here is governed by the continuous resizing, not the regime clock.
    assert (slow["weight"].diff().abs().sum()
            == pytest.approx(fast["weight"].diff().abs().sum(), rel=0.25))


# --------------------------------------------------------------------------
# rebalance buffer (no-trade band)
#
# The band damps *resizing only*: entry, exit and flip always execute. Its whole
# contract lives in the case where the Kelly target is **unsaturated**, because
# only then does the target move in steps smaller than the band. That case is
# reachable, but not at the spec's defaults -- see
# test_rebalance_buffer_is_vacuous_at_the_spec_defaults for the algebra.
# --------------------------------------------------------------------------


def _unsaturated_inputs(n=40):
    """A target that oscillates by less than the band, and is not at the cap.

    With ``lambda=0.25`` and ``sigma_eq=0.25`` the Kelly leverage is
    ``0.5*|z|``, so ``z`` in ``[-1.00, -1.04]`` gives ``|f|`` in
    ``[0.50, 0.52]``: a 0.02 oscillation, well under the 0.05 band, and well
    under the ``max_leverage`` cap of 1.0.
    """
    idx = flat_index(n)
    signal = pd.Series(np.ones(n), index=idx)         # one continuous regime
    z = pd.Series(-1.0 - 0.04 * (np.arange(n) % 2), index=idx)
    sigma_eq = pd.Series(0.25, index=idx)
    return signal, z, sigma_eq


def test_rebalance_buffer_zero_reproduces_the_raw_target():
    """The primitive's default is a pure map: buffer 0 == no band at all."""
    signal, z, sigma_eq = _unsaturated_inputs()
    raw = target_weights(signal, z, sigma_eq, rebalance_buffer=0.0)
    plain = target_weights(signal, z, sigma_eq)
    pd.testing.assert_series_equal(raw, plain)


def test_rebalance_buffer_damps_sub_band_resizing_to_nothing():
    """An oscillation narrower than the band is held flat, not followed."""
    signal, z, sigma_eq = _unsaturated_inputs(n=40)
    raw = target_weights(signal, z, sigma_eq, rebalance_buffer=0.0)
    banded = target_weights(signal, z, sigma_eq, rebalance_buffer=0.05)

    # The raw path oscillates every bar; the banded path is a constant.
    assert raw.diff().abs().sum() > 0.0
    assert banded.diff().abs().sum() == pytest.approx(0.0, abs=1e-12)
    assert banded.nunique() == 1

    # And it damps by holding, never by going flat.
    assert (banded != 0.0).all()

    # The held weight stays within the band of what the model wanted, so the
    # damping is bounded: the book cannot silently drift away from the target.
    assert float((raw - banded).abs().max()) <= 0.05 + 1e-12


def test_rebalance_buffer_damps_but_still_arrives_at_a_trending_target():
    """A target that walks out of the band is followed, in band-sized steps."""
    n = 200
    idx = flat_index(n)
    signal = pd.Series(np.ones(n), index=idx)
    # |f| = 0.5*|z| walks from 0.30 to 0.89, so it clears the 0.05 band often.
    z = pd.Series(-0.60 - 0.003 * np.arange(n), index=idx)
    sigma_eq = pd.Series(0.25, index=idx)

    raw = target_weights(signal, z, sigma_eq, rebalance_buffer=0.0)
    banded = target_weights(signal, z, sigma_eq, rebalance_buffer=0.05)

    # It tracks, and it tracks to within the band at every bar.
    assert float((raw - banded).abs().max()) <= 0.05 + 1e-12
    assert banded.iloc[-1] > banded.iloc[0]          # followed the trend up

    # Fewer rebalances, and each one is at least band-sized in effect: the
    # number of resizing bars falls even though the total variation is close.
    raw_moves = int((raw.diff().fillna(0.0) != 0.0).sum())
    band_moves = int((banded.diff().fillna(0.0) != 0.0).sum())
    assert band_moves < raw_moves


def test_rebalance_buffer_does_not_delay_entry():
    """Opening from flat is one trade either way; the band must not block it."""
    idx = flat_index(8)
    signal = pd.Series([0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0], index=idx)
    z = pd.Series([-1.0] * 8, index=idx)
    sigma_eq = pd.Series(0.25, index=idx)
    banded = target_weights(signal, z, sigma_eq, rebalance_buffer=0.05)
    assert banded.iloc[2] == 0.0
    assert banded.iloc[3] != 0.0     # entry lands on the same bar as unbuffered


def test_rebalance_buffer_always_executes_exit_however_small():
    """A tiny exit is still an exit: size never gates getting out of the book."""
    idx = flat_index(6)
    signal = pd.Series([1.0, 1.0, 1.0, 0.0, 0.0, 0.0], index=idx)
    # Kelly is exactly constant, so the exit is a pure sign change to zero and
    # the raw target does not move *before* it -- nothing for the band to damp.
    z = pd.Series([-1.0, -1.0, -1.0, -1.0, -1.0, -1.0], index=idx)
    sigma_eq = pd.Series(0.25, index=idx)
    banded = target_weights(signal, z, sigma_eq, rebalance_buffer=0.05)
    assert banded.iloc[2] != 0.0
    assert banded.iloc[3] == 0.0     # exit fires despite a sub-band change


def test_rebalance_buffer_always_executes_a_flip():
    """A sign change is a risk reversal, not a resize -- never damped."""
    idx = flat_index(6)
    signal = pd.Series([1.0, 1.0, -1.0, -1.0, -1.0, -1.0], index=idx)
    z = pd.Series([-1.0, -1.0, 1.0, 1.0, 1.0, 1.0], index=idx)
    sigma_eq = pd.Series(0.25, index=idx)
    # A band wider than any possible weight: only the flip can get through.
    banded = target_weights(signal, z, sigma_eq, rebalance_buffer=1e6)
    assert banded.iloc[1] > 0.0
    assert banded.iloc[2] < 0.0      # flipped on the bar it was signalled


def test_rebalance_buffer_cannot_exceed_max_leverage():
    """Every emitted value is an accepted (already clipped) target."""
    n = 200
    idx = flat_index(n)
    signal = pd.Series(np.ones(n), index=idx)
    # Drives Kelly far past the cap, so the raw target is pinned at 1.0.
    z = pd.Series(-2.0 - 0.05 * np.arange(n), index=idx)
    sigma_eq = pd.Series(0.02, index=idx)
    raw = target_weights(signal, z, sigma_eq, max_leverage=1.0)
    assert float(raw.abs().max()) == pytest.approx(1.0)

    banded = target_weights(
        signal, z, sigma_eq, max_leverage=1.0, rebalance_buffer=0.05
    )
    assert float(banded.abs().max()) <= 1.0 + 1e-12
    assert float(banded.abs().min()) > 0.0     # still holds, never flat


def test_rebalance_buffer_rejects_negative():
    signal, z, sigma_eq = _unsaturated_inputs(n=5)
    with pytest.raises(ValueError):
        target_weights(signal, z, sigma_eq, rebalance_buffer=-0.01)


def test_rebalance_buffer_is_vacuous_at_the_spec_defaults():
    """Documented, not a bug: at spec defaults the band has nothing to damp.

    The regime only opens at ``|z| >= z_entry = 2``. Kelly is
    ``lambda*|z|/(2*sigma_eq)``, so the target is *unsaturated* -- and therefore
    able to move in sub-band steps -- only when

        sigma_eq > lambda * z_entry / (2 * l_max) = 0.25 * 2 / 2 = 0.25.

    A spread whose equilibrium volatility is 25% of its own level is not a
    stationary spread. Every realistic spread sits far below that, so the target
    is pinned at the cap and the raw weight is a pure step function in
    ``{-1, 0, +1}``: turnover comes from regime changes only, and a band that
    damps resizing damps nothing.

    This test pins that structural fact so a reader of the turnover table is not
    left thinking the buffer was tried and simply failed to help.
    """
    pa, pb = make_pair(n=2000)
    off = ou_spread_strategy(pa, pb, window=60, min_obs=20, rebalance_buffer=0.0)
    on = ou_spread_strategy(pa, pb, window=60, min_obs=20, rebalance_buffer=0.05)

    pd.testing.assert_series_equal(off["weight"], on["weight"])

    # The reason: the raw target is a step function pinned at the cap.
    raw = off["weight_raw"]
    in_market = raw[raw != 0.0]
    assert set(in_market.round(9).unique()) <= {-1.0, 1.0}
    assert off.loc[off["signal"] != 0.0, "z"].abs().min() >= 0.5

    # No resizing channel exists: the raw weight never moves except when the
    # regime does.
    raw_moved = raw.diff().fillna(raw) != 0.0
    regime_moved = off["signal"].diff().fillna(0.0) != 0.0
    assert int((raw_moved & ~regime_moved).sum()) == 0

    # And the actual sigma_eq is one to two orders of magnitude below the 0.25
    # that unsaturation would require -- saturated by 10x or more throughout.
    se = off.loc[off["signal"] != 0.0, "sigma_eq"]
    assert float(se.max()) < 0.25 / 10.0
    assert _kelly_is_unsaturated(off) == 0.0

    # Sensitivity: the target has to fall ~250x before it comes off the cap, so
    # the band survives even a large cut to kelly_fraction. At lambda=0.01 it
    # finally starts to bite -- and even then only marginally.
    def turnover(lam, buf):
        f = ou_spread_strategy(pa, pb, window=60, min_obs=20,
                               kelly_fraction=lam, rebalance_buffer=buf)
        return float(f["weight"].diff().abs().sum())

    for lam in (0.25, 0.05):
        assert turnover(lam, 0.05) == pytest.approx(turnover(lam, 0.0), rel=1e-9)
    assert turnover(0.01, 0.05) == pytest.approx(turnover(0.01, 0.0), rel=0.01)


def _kelly_is_unsaturated(frame, lam=0.25, l_max=1.0):
    """Fraction of in-market bars where lambda*f* sits strictly below the cap."""
    m = frame["signal"] != 0.0
    z, se = frame.loc[m, "z"].abs(), frame.loc[m, "sigma_eq"]
    return float(((lam * z / (2.0 * se)) < l_max).mean())


def test_rebalance_buffer_binds_once_kelly_is_unsaturated():
    """The complement of the vacuity test: give the band a target it can damp.

    ``ou_frame`` takes any series, so feed it a synthetic one whose equilibrium
    volatility is large enough to un-saturate Kelly. This is the regime the
    buffer was written for.
    """
    x = simulate_ou(1500, theta=15.0, mu=0.0, sigma=3.0, seed=11)
    off = ou_frame(x, window=60, min_obs=20, z_entry=2.0, z_exit=0.5,
                   rebalance_buffer=0.0)
    on = ou_frame(x, window=60, min_obs=20, z_entry=2.0, z_exit=0.5,
                  rebalance_buffer=0.05)

    se = off.loc[off["signal"] != 0.0, "sigma_eq"]
    assert float(se.median()) > 0.25          # genuinely unsaturated
    assert _kelly_is_unsaturated(off) > 0.5   # most in-market bars below cap
    raw = off["weight"]
    assert raw[raw != 0.0].nunique() > 2      # a real resizing channel exists

    # The band damps it, the regime is untouched, and the gap stays inside it.
    assert (on["weight"].diff().abs().sum() < raw.diff().abs().sum())
    pd.testing.assert_series_equal(off["signal"], on["signal"])
    assert float((raw - on["weight"]).abs().max()) <= 0.05 + 1e-12


def test_rebalance_buffer_is_threaded_through_the_single_series_pipeline():
    """The one-asset path carries the parameter too, and lands on ou_frame."""
    x = simulate_ou(1500, theta=15.0, mu=0.0, sigma=3.0, seed=11)
    default = ou_strategy(x, window=60, min_obs=20)
    on = ou_strategy(x, window=60, min_obs=20, rebalance_buffer=0.05)
    off = ou_strategy(x, window=60, min_obs=20, rebalance_buffer=0.0)

    pd.testing.assert_series_equal(default["weight"], on["weight"])
    pd.testing.assert_series_equal(
        on["weight"],
        ou_frame(log_price(x), window=60, min_obs=20,
                 rebalance_buffer=0.05)["weight"],
    )
    assert (on["weight"].diff().abs().sum() < off["weight"].diff().abs().sum())


def test_rebalance_buffer_is_threaded_through_the_spread_pipeline():
    pa, pb = make_pair(n=2000)
    on = ou_spread_strategy(pa, pb, window=60, min_obs=20, rebalance_buffer=0.05)

    # Threading: the parameter reaches the weight, and the pipeline default is
    # the banded variant, not the raw one.
    default = ou_spread_strategy(pa, pb, window=60, min_obs=20)
    pd.testing.assert_series_equal(default["weight"], on["weight"])

    # It reaches the spread weight *before* the gross normalization, so both
    # legs inherit it and the hedge stays consistent.
    assert on["weight_a"].equals(on["weight"])
    assert np.allclose(
        on["weight_b"].to_numpy(),
        (-on["weight"] * on["beta"]).fillna(0.0).to_numpy(),
    )

    # A different buffer is respected as given (not silently ignored), and the
    # buffer is not the regime rule: the signal is identical either way.
    wide = ou_spread_strategy(pa, pb, window=60, min_obs=20,
                              rebalance_buffer=1e6)
    pd.testing.assert_series_equal(on["signal"], wide["signal"])


# --------------------------------------------------------------------------
# sizing
# --------------------------------------------------------------------------


def test_kelly_is_capped_at_max_leverage():
    z = pd.Series([-10.0, 10.0])
    se = pd.Series([0.04, 0.04])
    f = kelly_leverage(z, se, kelly_fraction=0.25, max_leverage=1.0)
    assert (f.abs() <= 1.0 + 1e-12).all()


def test_kelly_sign_is_long_when_cheap():
    f = kelly_leverage(pd.Series([-1.0]), pd.Series([0.1]),
                       kelly_fraction=1.0, max_leverage=10.0)
    assert f.iloc[0] > 0.0


def test_kelly_scales_with_fraction():
    z, se = pd.Series([-1.0]), pd.Series([0.5])
    full = kelly_leverage(z, se, kelly_fraction=1.0, max_leverage=100.0).iloc[0]
    quarter = kelly_leverage(z, se, kelly_fraction=0.25, max_leverage=100.0).iloc[0]
    assert quarter == pytest.approx(full / 4.0)


def test_target_weight_direction_matches_regime():
    z = pd.Series([-3.0, 3.0])
    sig = pd.Series([1.0, -1.0])
    se = pd.Series([0.05, 0.05])
    w = target_weights(sig, z, se, kelly_fraction=0.25, max_leverage=1.0)
    assert w.iloc[0] > 0.0    # cheap -> long
    assert w.iloc[1] < 0.0    # rich  -> short


def test_target_weight_is_zero_when_flat():
    z = pd.Series([-3.0, 3.0])
    sig = pd.Series([0.0, 0.0])
    se = pd.Series([0.05, 0.05])
    w = target_weights(sig, z, se)
    assert (w == 0.0).all()


def test_risk_limits_validation():
    with pytest.raises(ValueError):
        RiskLimits(kelly_fraction=0.0)
    with pytest.raises(ValueError):
        RiskLimits(kelly_fraction=1.5)
    with pytest.raises(ValueError):
        RiskLimits(max_drawdown=0.0)
    with pytest.raises(ValueError):
        RiskLimits(max_drawdown=1.0)
    with pytest.raises(ValueError):
        RiskLimits(max_leverage=0.0)


# --------------------------------------------------------------------------
# kill switch
# --------------------------------------------------------------------------


def test_kill_switch_trips_at_exactly_five_percent():
    ks = DrawdownKillSwitch(max_drawdown=0.05)
    assert ks.update(1.00) is False
    assert ks.update(0.95) is True
    assert ks.breaches == 1


def test_kill_switch_does_not_trip_below_threshold():
    ks = DrawdownKillSwitch(max_drawdown=0.05)
    ks.update(1.00)
    assert ks.update(0.96) is False
    assert ks.drawdown == pytest.approx(0.04)   # 4% off the peak
    assert ks.update(0.97) is False             # partial recovery
    assert ks.breaches == 0


def test_kill_switch_measures_peak_to_trough_not_start():
    ks = DrawdownKillSwitch(max_drawdown=0.05)
    ks.update(1.00)
    ks.update(1.20)          # new peak
    assert ks.update(1.15) is False   # 4.2% off peak, not off start
    assert ks.update(1.13) is True    # 5.8% off peak


def test_kill_switch_flattens_the_book():
    idx = flat_index(6)
    weights = pd.Series([1.0] * 6, index=idx)
    returns = pd.Series([0.0, -0.06, 0.02, 0.02, 0.02, 0.02], index=idx)

    report = RiskEngine(RiskLimits(max_drawdown=0.05)).apply(weights, returns)

    assert report.tripped
    assert report.first_breach == idx[1]
    # Breach seen at t=1 -> flat from t=2 onward.
    assert (report.executed_weights.iloc[2:] == 0.0).all()
    # The breaching day's loss is taken, not retroactively removed.
    assert report.equity.iloc[1] == pytest.approx(0.94)


def test_market_shock_trips_switch_and_bounds_the_loss():
    idx = flat_index(10)
    weights = pd.Series([1.0] * 10, index=idx)
    returns = pd.Series([0.0, -0.20] + [0.05] * 8, index=idx)

    report = RiskEngine(RiskLimits(max_drawdown=0.05)).apply(weights, returns)

    assert report.tripped
    assert report.first_breach == idx[1]
    loss_at_breach = report.equity.iloc[1]
    assert loss_at_breach == pytest.approx(0.80)
    # A 20% shock fires the switch; the book is flat, so recovery is forgone
    # and the loss does not grow. This is the intended trade.
    assert (report.executed_weights.iloc[2:] == 0.0).all()
    assert report.equity.iloc[-1] == pytest.approx(loss_at_breach)


def test_kill_switch_never_rearms_by_default():
    idx = flat_index(5)
    weights = pd.Series([1.0] * 5, index=idx)
    returns = pd.Series([0.0, -0.06, 0.10, 0.10, 0.10], index=idx)

    report = RiskEngine(RiskLimits(max_drawdown=0.05)).apply(weights, returns)

    assert (report.executed_weights.iloc[2:] == 0.0).all()
    assert report.halted_at_end


def test_kill_switch_rearm_resumes_after_cooldown():
    idx = flat_index(5)
    weights = pd.Series([1.0] * 5, index=idx)
    returns = pd.Series([0.0, -0.06, 0.0, 0.0, 0.0], index=idx)

    limits = RiskLimits(max_drawdown=0.05, rearm=True, cooldown_days=1)
    report = RiskEngine(limits).apply(weights, returns)

    assert report.tripped
    assert report.executed_weights.iloc[2] == 0.0   # cooldown bar
    assert report.executed_weights.iloc[3] == 0.0   # cooldown elapses
    assert report.executed_weights.iloc[4] == 1.0   # resumed


def test_kill_switch_survives_equity_recovery_above_old_peak():
    """A latched switch must not silently reopen at a new high."""
    ks = DrawdownKillSwitch(max_drawdown=0.05)
    ks.update(1.0)
    ks.update(0.90)          # trips
    assert ks.halted
    ks.update(1.50)          # book is flat, but even if equity jumps
    assert ks.halted


# --------------------------------------------------------------------------
# engine integration
# --------------------------------------------------------------------------


def test_engine_run_on_synthetic_ou():
    x = simulate_ou(800, 5.0, 4.0, 0.5, seed=17)
    price = np.exp(x)
    res = ou_strategy(price, window=60, z_entry=2.0, z_exit=0.5, min_obs=20)
    returns = price.pct_change().fillna(0.0)

    report = RiskEngine(RiskLimits(max_drawdown=0.05)).run(
        res["signal"], res["z"], res["sigma_eq"], returns
    )

    frame = report.frame
    assert list(frame.columns) == [
        "target_weight", "executed_weight", "returns",
        "equity", "drawdown", "halted",
    ]
    assert len(frame) == len(price)
    assert np.isfinite(frame["equity"]).all()
    assert (frame["equity"] > 0).all()
    # Drawdown is bounded by the switch plus the one bar it cannot undo.
    assert report.max_drawdown_realized < 0.30
    # Executed never exceeds the target in magnitude, and is flat once halted.
    assert (frame["executed_weight"].abs()
            <= frame["target_weight"].abs() + 1e-12).all()
    if report.tripped:
        # The latch closes at the close of the breach bar, so that bar still
        # traded (the loss is taken, not retroactively removed). From the
        # *next* bar onward the book is flat.
        already_halted = frame["halted"].shift(1, fill_value=False)
        assert (frame.loc[already_halted, "executed_weight"] == 0.0).all()


def test_engine_equity_matches_manual_compounding():
    idx = flat_index(4)
    weights = pd.Series([0.5, 0.5, 0.0, 0.25], index=idx)
    returns = pd.Series([0.10, -0.20, 0.05, 0.04], index=idx)

    report = RiskEngine(RiskLimits(max_drawdown=0.90, max_leverage=1.0))
    rep = report.apply(weights, returns)

    expected = 1.0
    for w, r in zip(weights, returns):
        expected *= 1.0 + w * r
    assert rep.equity.iloc[-1] == pytest.approx(expected)


# --------------------------------------------------------------------------
# look-ahead
# --------------------------------------------------------------------------


def test_permuting_future_data_cannot_change_past_signals():
    x = simulate_ou(400, 5.0, 4.0, 0.5, seed=23)
    price = np.exp(x)

    base = ou_strategy(price, window=60, min_obs=20)

    cutoff = 300
    perturbed_price = price.copy()
    perturbed_price.iloc[cutoff:] = perturbed_price.iloc[cutoff:] * 3.0

    alt = ou_strategy(perturbed_price, window=60, min_obs=20)

    for column in ("z", "signal", "weight", "mu", "sigma_eq", "theta"):
        pd.testing.assert_series_equal(
            base[column].iloc[:cutoff],
            alt[column].iloc[:cutoff],
            check_names=False,
        )


def test_rolling_fit_uses_only_data_through_t():
    """Row t must be identical whether or not later data exists."""
    x = simulate_ou(200, 5.0, 4.0, 0.5, seed=29)
    full = rolling_ou(x, window=60, min_obs=20)

    truncated = rolling_ou(x.iloc[:120], window=60, min_obs=20)
    pd.testing.assert_series_equal(
        full["theta"].iloc[:120], truncated["theta"], check_names=False
    )
    pd.testing.assert_series_equal(
        full["mu"].iloc[:120], truncated["mu"], check_names=False
    )


# --------------------------------------------------------------------------
# cointegration spread (two-asset form)
# --------------------------------------------------------------------------


def make_pair(n=600, beta=1.5, alpha=0.2, theta=15.0, mu=0.0, sigma=0.02, seed=5):
    """A cointegrated pair: ``log_b`` is a random walk and
    ``log_a = alpha + beta*log_b +`` a stationary OU spread."""
    rng = np.random.default_rng(seed)
    lb = 4.0 + np.cumsum(0.01 * rng.standard_normal(n))
    spread = simulate_ou(n, theta, mu, sigma, seed=seed + 1).to_numpy()
    la = alpha + beta * lb + spread
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.Series(np.exp(la), index=idx), pd.Series(np.exp(lb), index=idx)


def make_independent_pair(n=600, seed=9):
    """Two unrelated random walks -- not a pair."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-01", periods=n)
    a = np.exp(4.0 + np.cumsum(0.01 * rng.standard_normal(n)))
    b = np.exp(4.0 + np.cumsum(0.01 * rng.standard_normal(n)))
    return pd.Series(a, index=idx), pd.Series(b, index=idx)


def test_hedge_ratio_recovers_known_beta():
    pa, pb = make_pair(n=600, beta=1.5, alpha=0.2)
    la, lb = log_price(pa), log_price(pb)
    h = fit_hedge_ratio(la, lb)

    assert h.valid
    assert h.beta == pytest.approx(1.5, rel=0.01)
    assert h.r2 > 0.99

    # alpha is only weakly identified here: log_b sits near 4, so a 1% error in
    # beta shifts the intercept by roughly beta_err * mean(log_b) ~ 0.04. That
    # level shift is harmless, because the OU fit estimates mu from the spread
    # itself -- only the *shape* of the spread has to be recovered.
    assert h.alpha == pytest.approx(0.2, abs=0.10)

    recovered = la - h.alpha - h.beta * lb
    truth = la - 0.2 - 1.5 * lb
    assert float(np.corrcoef(recovered, truth)[0, 1]) > 0.95
    assert float(recovered.std()) == pytest.approx(float(truth.std()), rel=0.10)


def test_hedge_ratio_rejects_negative_beta():
    """A negative hedge ratio is a long-long bet, not relative value."""
    idx = flat_index(200)
    rng = np.random.default_rng(1)
    lb = np.log(50.0) + np.cumsum(0.01 * rng.standard_normal(200))
    la = 2.0 - 1.5 * lb + 0.01 * rng.standard_normal(200)

    h = fit_hedge_ratio(pd.Series(la, index=idx), pd.Series(lb, index=idx))
    assert h.beta < 0.0
    assert not h.valid


def test_hedge_ratio_rejects_constant_leg():
    idx = flat_index(100)
    a = pd.Series(np.linspace(1.0, 2.0, 100), index=idx)
    b = pd.Series([3.0] * 100, index=idx)   # constant -> slope undefined

    h = fit_hedge_ratio(a, b)
    assert not h.valid
    assert np.isnan(h.beta)


def test_fit_hedge_ratio_degenerate_inputs_do_not_raise():
    assert not fit_hedge_ratio([], []).valid
    assert not fit_hedge_ratio([1.0], [1.0]).valid
    assert not fit_hedge_ratio([np.nan] * 30, [np.nan] * 30).valid
    with pytest.raises(ValueError):
        fit_hedge_ratio([1.0, 2.0], [1.0])


def test_min_r2_screen_rejects_unrelated_series():
    pa, pb = make_independent_pair()
    la, lb = log_price(pa), log_price(pb)

    h = fit_hedge_ratio(la, lb, min_obs=200)
    assert not np.isfinite(h.r2) or h.r2 < 0.5   # no real co-movement

    # A meaningful screen must refuse the pair outright.
    assert not fit_hedge_ratio(la, lb, min_obs=200, min_r2=0.5).valid


def test_cointegration_spread_is_stationary_for_cointegrated_pair():
    pa, pb = make_pair(n=800, theta=20.0)
    spread, hedge = cointegration_spread(pa, pb, window=60, min_obs=20)

    assert hedge["valid"].iloc[-1]
    p = fit_ou(spread.dropna())
    assert p.valid
    assert p.half_life < 60.0


def test_rolling_hedge_ratio_is_point_in_time():
    pa, pb = make_pair(n=400)
    la, lb = log_price(pa), log_price(pb)
    base = rolling_hedge_ratio(la, lb, window=60, min_obs=20)

    cutoff = 300
    pb_perturbed = pb.copy()
    pb_perturbed.iloc[cutoff:] *= 2.0
    alt = rolling_hedge_ratio(la, log_price(pb_perturbed), window=60, min_obs=20)

    for column in ("beta", "alpha", "r2"):
        pd.testing.assert_series_equal(
            base[column].iloc[:cutoff], alt[column].iloc[:cutoff], check_names=False
        )


def test_spread_leg_weights_are_consistent():
    pa, pb = make_pair(n=800)
    res = ou_spread_strategy(pa, pb, window=60, min_obs=20)

    pd.testing.assert_series_equal(
        res["weight_a"], res["weight"], check_names=False
    )
    expected_b = (-res["weight"] * res["beta"]).fillna(0.0)
    pd.testing.assert_series_equal(
        res["weight_b"].fillna(0.0), expected_b, check_names=False
    )


def test_spread_gross_leverage_is_bounded_by_the_cap():
    """max_leverage must bound |w| * (1 + |beta|), not just |w|."""
    pa, pb = make_pair(n=900, theta=25.0)
    res = ou_spread_strategy(
        pa, pb, window=60, min_obs=20, kelly_fraction=1.0, max_leverage=1.0
    )

    beta = res["beta"].fillna(0.0)
    gross = res["weight"].abs() * (1.0 + beta.abs())
    assert np.isfinite(gross).all()
    assert float(gross.max()) <= 1.0 + 1e-9


def test_spread_strategy_cannot_see_the_future():
    pa, pb = make_pair(n=500)
    base = ou_spread_strategy(pa, pb, window=60, min_obs=20)

    cutoff = 380
    pa2, pb2 = pa.copy(), pb.copy()
    pa2.iloc[cutoff:] *= 3.0
    pb2.iloc[cutoff:] *= 0.4
    alt = ou_spread_strategy(pa2, pb2, window=60, min_obs=20)

    for column in ("z", "signal", "weight", "beta", "weight_a", "weight_b"):
        pd.testing.assert_series_equal(
            base[column].iloc[:cutoff], alt[column].iloc[:cutoff], check_names=False
        )


def test_spread_returns_use_the_lagged_hedge_ratio():
    pa, pb = make_pair(n=300)
    _, hedge = cointegration_spread(pa, pb, window=60, min_obs=20)

    r = spread_returns(pa, pb, hedge, lag=1)
    expected = (pa.pct_change() - hedge["beta"].shift(1) * pb.pct_change()).fillna(0.0)
    pd.testing.assert_series_equal(r, expected, check_names=False)


def test_ou_strategy_matches_ou_frame_on_log_price():
    """Refactor guard: the single-asset path is ou_frame(log price)."""
    price = np.exp(simulate_ou(300, 8.0, 4.0, 0.5, seed=31))
    pd.testing.assert_frame_equal(
        ou_strategy(price, window=60, min_obs=20),
        ou_frame(log_price(price), window=60, min_obs=20),
    )


def test_spread_strategy_runs_through_the_risk_engine():
    pa, pb = make_pair(n=800)
    res = ou_spread_strategy(pa, pb, window=60, min_obs=20)
    _, hedge = cointegration_spread(pa, pb, window=60, min_obs=20)
    returns = spread_returns(pa, pb, hedge)

    # apply() takes the spread weights directly; run() would re-derive plain
    # single-series weights and drop the gross-leverage normalisation.
    held = res["weight"].shift(1).fillna(0.0)
    report = RiskEngine(RiskLimits(max_drawdown=0.05)).apply(held, returns)

    assert len(report.frame) == len(pa)
    assert np.isfinite(report.frame["equity"]).all()
    assert (report.frame["equity"] > 0).all()
    assert report.max_drawdown_realized < 1.0


def test_engine_weight_return_interval_is_delay_one():
    """`weights[t]` must earn the return over (t, t+1], never (t-1, t].

    This is the alignment that silently breaks. Pair the weight with the return
    that *created* its signal and the equity path is look-ahead -- and for a
    mean-reversion signal, inverted look-ahead, because z_t is extreme precisely
    because r_t just moved. So the contaminated path can come out *worse*, which
    makes it easy to mistake for conservatism rather than a bug.
    """
    idx = flat_index(3)
    # The position that earns the +10% move is the one decided the bar before it.
    returns = pd.Series([0.0, 0.10, 0.0], index=idx)
    decided = pd.Series([1.0, 0.0, 0.0], index=idx)

    engine = RiskEngine(RiskLimits(max_drawdown=0.99))
    assert engine.apply(decided.shift(1).fillna(0.0), returns).equity.iloc[-1] \
        == pytest.approx(1.10)
    # The raw weight against the same returns earns nothing: no bar pairs a
    # decision with a move that preceded it.
    assert engine.apply(decided, returns).equity.iloc[-1] == pytest.approx(1.0)


def test_returned_legs_reproduce_the_engine_equity():
    """`leg_a * r_a + leg_b * r_b` must equal the engine's spread return.

    The short leg's ratio has to be the hedge ratio known when the position was
    set (beta at t-1, the lag `spread_returns` uses), not the contemporaneous
    beta. Using the latter looks harmless -- beta barely moves bar to bar -- and
    silently decouples the reported exposure from the traded P&L.
    """
    pa, pb = make_pair(n=800)
    res = ou_spread_strategy(pa, pb, window=60, min_obs=20)
    _, hedge = cointegration_spread(pa, pb, window=60, min_obs=20)
    returns = spread_returns(pa, pb, hedge)

    held = res["weight"].shift(1).fillna(0.0)
    executed = RiskEngine(RiskLimits(max_drawdown=0.99)).apply(
        held, returns
    ).executed_weights.fillna(0.0)

    beta_held = res["beta"].reindex(executed.index).shift(1).fillna(0.0)
    leg_a = executed
    leg_b = (-executed * beta_held).fillna(0.0)

    # The first bar has no prior close, so its return is undefined and no
    # position is held into it.
    ra, rb = pa.pct_change().fillna(0.0), pb.pct_change().fillna(0.0)
    replicated = (1.0 + leg_a * ra + leg_b * rb).cumprod()
    engine_eq = RiskEngine(RiskLimits(max_drawdown=0.99)).apply(held, returns).equity

    pd.testing.assert_series_equal(
        replicated, engine_eq, check_names=False, rtol=1e-9
    )
    # And the contemporaneous beta genuinely would not have matched.
    wrong = (1.0 + leg_a * ra
             - executed * res["beta"].reindex(executed.index).fillna(0.0) * rb
             ).cumprod()
    assert not np.allclose(wrong.to_numpy(), engine_eq.to_numpy())
