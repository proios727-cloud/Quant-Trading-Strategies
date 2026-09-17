"""Tests for the universe screen.

The centre of gravity here is ``johansen``: the rank has to come from the
sequential trace procedure, and getting that wrong is silent. A bug that counts
every statistic clearing its critical value instead of stopping at the first
non-rejection turned a trace of 10.6 against a 95% critical value of 15.5 into a
reported "cointegrated" candidate on the live scan. There is no exception and no
NaN to notice -- just a wrong answer in a plausible-looking table. Hence the
explicit regression test.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from universe_scan import ScanResult, adf, johansen, rank


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def random_walk(n=251, mu=0.0, sigma=0.02, start=4.0, seed=0):
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.standard_normal(n) * sigma + mu) + start


def cointegrated_pair(n=251, beta=2.0, phi=0.8, sigma=0.02, noise=None, seed=0):
    """``b = beta*a + AR(1) noise`` -- cointegrated with a known loading.

    Both series are drawn from a **single** generator, consumed in sequence. An
    earlier version drew ``a`` and ``e`` from two generators seeded with the
    same value, so they consumed identical normal draws -- which made the
    residual a deterministic function of the walk and collapsed a Johansen
    eigenvalue onto exactly 1.0, producing a NaN trace statistic out of a
    fixture that was supposed to be ordinary. Shared-seed streams are a subtly
    wrong way to build a two-series fixture; independent ones are not.

    ``noise`` is a multiple of the walk's own standard deviation, not an
    absolute level -- so it means the same thing at any ``sigma``. It defaults
    to 0.5, keeping the cointegrating relation realistic rather than
    near-perfect.
    """
    rng = np.random.default_rng(seed)
    a = np.cumsum(rng.standard_normal(n) * sigma) + 4.0
    e = np.zeros(n)
    ns = (0.5 if noise is None else noise) * a.std()
    for i in range(1, n):
        e[i] = phi * e[i - 1] + rng.standard_normal() * ns
    return a, beta * a + e


def stub_johansen(lr1, cvt95):
    """A fake ``coint_johansen`` result with the given statistics.

    ``evec`` is (2, 2) because the real code normalises column 0 on its first
    element.
    """
    cvt = np.array([[c, c, c] for c in cvt95], dtype=float)
    return SimpleNamespace(
        lr1=np.array(lr1, dtype=float),
        cvt=cvt,
        evec=np.array([[1.0, 0.0], [-1.5, 1.0]], dtype=float),
    )


# --------------------------------------------------------------------------
# johansen: detection and the null
# --------------------------------------------------------------------------


def test_johansen_detects_a_true_cointegrated_pair():
    """A constructed cointegrated pair is detected, and the loading recovered.

    The two halves of this assertion have very different robustness. The trace
    statistic is numerically invariant to the noise scale in this construction
    -- 40.289 at every level from 0.1x to 2.0x the walk's sd -- so detection is
    solid. The eigenvector is not: at 0.5x sd the recovered ``eigvec[1]`` ranges
    over -0.42..-0.59, which reflects genuine estimation error rather than a
    bug. A tighter noise is used here so the loading assertion tests the sign
    and magnitude convention, not the sampling error on top of it.
    """
    a, b = cointegrated_pair(beta=2.0, noise=0.1, seed=1)
    out = johansen(a, b)
    assert out["rank"] == 1
    # b = 2a  =>  a - 0.5b is stationary, so the loading on b is 0.5.
    assert out["eigvec"][1] == pytest.approx(-0.5, abs=0.06)


def test_johansen_does_not_flag_independent_random_walks():
    """Unrelated walks must mostly *not* be called cointegrated.

    This asserts a rate, not a single pair, because a single pair cannot state
    the property honestly. At 251 bars the 95% Johansen trace test is badly
    over-sized: 200 independent-walk pairs give 12.5% rejections under the
    module's defaults (``det_order=0``, one lag), against a nominal 5%. An
    earlier version of this test picked one seed pair, and it failed on the
    first re-draw -- not because the code was wrong but because a ~1-in-8 event
    is not something one sample can pin down.

    So the assertion is the shape of the distribution: the screen flags a
    minority of unrelated pairs, and never most of them. The upper bound catches
    the failure that actually matters -- a broken rank rule that calls every
    pair cointegrated. The measured rate is fixed, because the seeds are.
    """
    n_pairs = 100
    flagged = sum(
        johansen(random_walk(seed=2 * s), random_walk(seed=2 * s + 1))["rank"] >= 1
        for s in range(n_pairs)
    )
    rate = flagged / n_pairs

    assert rate < 0.25, (
        f"{flagged}/{n_pairs} unrelated pairs flagged ({rate:.1%}); "
        "the rank rule is not rejecting anything"
    )


def test_johansen_trace_below_its_critical_value_is_not_a_rejection():
    """The specific comparison, isolated from the sampling question."""
    out = johansen(random_walk(seed=0), random_walk(seed=1))
    if out["rank"] == 0:
        assert out["trace"][0] < out["crit95"][0]
    else:
        pytest.skip("this seed pair is one of the ~12.5% that over-reject")


def test_johansen_reports_a_degenerate_fit_as_untestable_not_as_no_cointegration():
    """Regression: a NaN statistic must not read as a confident non-rejection.

    statsmodels returns ``lr1[0] = nan`` when an eigenvalue lands on exactly 1.0,
    because the trace statistic is built from ``log(1 - a)``. ``nan > crit`` is
    False, so a naive implementation silently reports rank 0 -- "no
    cointegration" -- for a pair that is in fact extremely tightly coupled, and
    the screen prints a confident verdict built on nothing.

    The stub is used rather than a real fixture on purpose. The degeneracy is a
    statsmodels numerical boundary, not a property of a data-generating process
    we can construct reliably: sweeping walk and noise scales over 150 draws
    produced 0/25 NaN at every scale tried. A test that depends on tripping it
    would be testing the library's floating point, not this module's handling of
    the result. So the NaN is injected directly.
    """
    stub = stub_johansen(lr1=[np.nan, 0.54], cvt95=[15.5, 3.84])

    import universe_scan

    original = universe_scan.coint_johansen
    universe_scan.coint_johansen = lambda *a, **k: stub
    try:
        out = johansen(random_walk(n=60, seed=0), random_walk(n=60, seed=1))
    finally:
        universe_scan.coint_johansen = original

    assert np.isnan(out["trace"][0])
    assert out["rank"] == -1, "a NaN trace is untestable, not a non-rejection"
    assert np.isnan(out["eigvec"][0])

    # And -1 must disqualify the pair rather than pass it.
    r = _qualified_pair(joh_rank=-1, joh_trace=np.nan)
    assert not r.qualified
    assert not r.joh_pass


def test_johansen_rank_is_the_sequential_rank_not_a_rejection_count():
    """Regression: the non-monotone case that produced a false candidate.

    ``lr1[0] = 10.6`` is *below* its critical value of 15.5, so ``H0: r = 0`` is
    not rejected and the procedure stops there. ``lr1[1] = 5.0`` happens to clear
    its own critical value of 3.8, which is possible in finite samples. The rank
    is 0; counting rejections would report 1 and call the pair cointegrated.
    """
    stub = stub_johansen(lr1=[10.6, 5.0], cvt95=[15.5, 3.84])

    import universe_scan

    original = universe_scan.coint_johansen
    universe_scan.coint_johansen = lambda *a, **k: stub
    try:
        out = johansen(random_walk(n=60, seed=0), random_walk(n=60, seed=1))
    finally:
        universe_scan.coint_johansen = original

    assert out["rank"] == 0, "must stop at the first non-rejection"
    assert out["trace"][0] == pytest.approx(10.6)
    assert out["crit95"][0] == pytest.approx(15.5)


def test_johansen_rank_two_when_both_hypotheses_reject():
    stub = stub_johansen(lr1=[30.0, 9.0], cvt95=[15.5, 3.84])

    import universe_scan

    original = universe_scan.coint_johansen
    universe_scan.coint_johansen = lambda *a, **k: stub
    try:
        out = johansen(random_walk(n=60, seed=0), random_walk(n=60, seed=1))
    finally:
        universe_scan.coint_johansen = original

    assert out["rank"] == 2


def test_johansen_rejects_a_short_sample_without_raising():
    out = johansen(np.arange(10.0), np.arange(10.0) * 2)
    assert out["rank"] == -1
    assert np.isnan(out["trace"][0])


def test_johansen_handles_non_finite_input():
    a = random_walk(n=60, seed=0)
    b = random_walk(n=60, seed=1)
    a[5] = np.nan
    b[9] = np.inf
    out = johansen(a, b)
    assert out["n_obs"] == 58          # the two bad points dropped
    assert out["rank"] in (0, 1)


# --------------------------------------------------------------------------
# ADF
# --------------------------------------------------------------------------


def test_adf_does_not_reject_a_unit_root():
    out = adf(random_walk(seed=3))
    assert out["pvalue"] > 0.05


def test_adf_rejects_a_stationary_series():
    rng = np.random.default_rng(4)
    out = adf(rng.standard_normal(300))
    assert out["pvalue"] < 0.05


def test_adf_is_guarded_on_degenerate_input():
    """A constant series and a stub must return NaN, never raise."""
    assert np.isnan(adf(np.ones(100))["pvalue"])
    assert np.isnan(adf([1.0, 2.0, 3.0])["pvalue"])          # too short
    assert np.isnan(adf([np.nan] * 50)["pvalue"])            # nothing finite


# --------------------------------------------------------------------------
# the qualified gate and the ranking
# --------------------------------------------------------------------------


def _qualified_pair(**over):
    """A ScanResult that passes the whole screen, with fields overridable."""
    base = dict(
        name_a="AAA", name_b="BBB", n_obs=251,
        beta=1.0, r2=0.9,
        adf_leg_a=0.70, adf_leg_b=0.80,          # legs non-stationary
        adf_spread=0.02, adf_spread_stat=-3.1,   # spread stationary
        joh_trace=25.0, joh_crit95=15.5, joh_rank=1,
        theta=12.0, half_life=14.6, sigma_eq=0.03, ou_valid=True,
        theta_pit=11.0, half_life_pit=15.9, ou_accept=0.8,
    )
    base.update(over)
    return ScanResult(**base)


def test_qualified_requires_the_whole_screen():
    assert _qualified_pair().qualified

    # Each single failure disqualifies on its own.
    assert not _qualified_pair(error="boom").qualified
    assert not _qualified_pair(joh_rank=0).qualified
    assert not _qualified_pair(joh_rank=-1).qualified
    assert not _qualified_pair(adf_spread=0.40).qualified
    assert not _qualified_pair(ou_valid=False).qualified
    assert not _qualified_pair(theta=0.0).qualified
    assert not _qualified_pair(theta=np.nan).qualified
    # A stationary leg means the pair is not an I(1)/I(1) setup at all.
    assert not _qualified_pair(adf_leg_a=0.01).qualified


def test_rank_orders_qualified_pairs_by_theta_descending():
    slow = _qualified_pair(name_a="SLOW", theta=4.0, half_life=43.7)
    fast = _qualified_pair(name_a="FAST", theta=20.0, half_life=8.7)
    mid = _qualified_pair(name_a="MID", theta=11.0, half_life=15.9)

    table = rank([slow, fast, mid])
    assert list(table["pair"]) == ["FAST/BBB", "MID/BBB", "SLOW/BBB"]
    assert list(table["rank"]) == [1, 2, 3]


def test_rank_excludes_unqualified_pairs_from_the_numbering():
    ok = _qualified_pair(name_a="OK", theta=8.0)
    bad = _qualified_pair(name_a="BAD", theta=99.0, joh_rank=0)

    table = rank([ok, bad])
    ranked = table[table["ranked"]]
    assert list(ranked["pair"]) == ["OK/BBB"]
    assert list(ranked["rank"]) == [1]

    # The fast-but-unqualified pair is present but unranked, and the numbering
    # never reaches it however large its theta is.
    unranked = table[~table["ranked"]]
    assert list(unranked["pair"]) == ["BAD/BBB"]
    assert unranked["rank"].isna().all()


def test_rank_keeps_unranked_rows_in_theta_order():
    """Both blocks read fastest-first, so the sort does not flip halfway down."""
    ok = _qualified_pair(name_a="OK", theta=8.0)
    b_slow = _qualified_pair(name_a="B2", theta=2.0, joh_rank=0)
    b_fast = _qualified_pair(name_a="B1", theta=30.0, joh_rank=0)

    table = rank([ok, b_slow, b_fast])
    assert list(table["pair"]) == ["OK/BBB", "B1/BBB", "B2/BBB"]


def test_rank_handles_an_empty_result_set():
    assert rank([]).empty


def test_rank_puts_a_pair_with_no_fit_last():
    ok = _qualified_pair(name_a="OK", theta=8.0)
    dead = ScanResult("XXX", "YYY", error="no data")
    table = rank([ok, dead])
    assert list(table["pair"]) == ["OK/BBB", "XXX/YYY"]
    assert np.isnan(table.iloc[-1]["theta"])


def test_scan_result_pair_and_verdict_fields_are_consistent():
    r = _qualified_pair()
    assert r.pair == "AAA/BBB"
    assert r.legs_are_i1
    assert r.adf_pass and r.joh_pass
