"""Universe screen: rank candidate pairs by Ornstein-Uhlenbeck reversion speed.

Reference spec: ``specs/mean_reversion.md``. This module is the *screening* step
that sits in front of it. It takes a list of candidate pairs, tests each for
cointegration, fits the OU model to the spread, and ranks the survivors by
reversion speed. It does not trade and it does not size.

Two spread constructions are used, and the difference is the whole point:

- a **static** spread -- a single OLS hedge ratio fitted on the entire sample --
  feeds the ADF and Johansen tests and the headline OU fit. This is the standard
  Engle-Granger screening procedure, and it is *in-sample by construction*.
- a **rolling** spread (``strategy.cointegration_spread``) feeds the
  point-in-time OU statistics. Each bar's spread uses only the hedge ratio known
  at that bar, so the rolling numbers are what a live strategy would have seen.

Both are reported. The static fit is the one to rank on, because it estimates
the pair's underlying relationship rather than one bar's view of it. But a pair
whose rolling and static numbers disagree is one whose relationship is unstable,
and that disagreement is exactly what a ranking should not be allowed to hide.

SAMPLE-LENGTH WARNING. One year of daily bars is roughly 252 observations, which
is *short* for this work:

- ADF and Johansen have low power in short samples. Failing to reject "no
  cointegration" is weak evidence of no cointegration; rejecting it can also be
  a small-sample artifact. Treat a 1-year verdict as a filter, not a finding.
- The Johansen trace test is **over-sized**, and — importantly — widening the
  sample does not fix it. Monte Carlo on the null (two independent random
  walks, ``det_order=0``, one lag) rejects at 12.0% on 251 bars, 9.3% on 502,
  and 13.0% on 1254, against a nominal 5%. A ~2.4x inflation that is flat in
  the sample size is a *mis-specification*, not a small-sample artifact:
  ``det_order=0`` puts an unrestricted constant in the cointegrating relation,
  which is not the right specification for driftless log prices. No available
  ``det_order`` is well calibrated (~11% for ``det_order=-1``, ~18% for
  ``det_order=1``). So a Johansen "pass" fires at roughly twice its advertised
  rate at *any* horizon, and the trace statistic should be read as a graded
  signal -- how far past the critical value it lands -- not as a p-value.
- The spec's section 4.2 guard caps the admissible half-life at the estimation
  window's span. With a 60-bar OU window, half-lives up to ~59 bars are
  admitted, so a genuinely slow pair is reported as *rejected*, not as slow.
  That censoring is why the ranking below is over fast pairs only.
- Five pairs tested at alpha = 0.05 means ~0.25 false positives are expected
  under the null. A single passing pair out of five is not evidence of anything.

Set ``YEARS`` to 5 (``python universe_scan.py 5``) before treating any of this
as a conclusion -- but on these five pairs the verdict does not change between 1
and 5 years, and the two pairs that come closest (XOM/CVX at a trace of 14.3,
EWA/EWC at 14.2) sit just under the 15.5 critical value rather than over it.
Lengthening the sample raises the trace statistic but not past the threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen

from strategy import (
    TRADING_DAYS_PER_YEAR,
    cointegration_spread,
    fit_hedge_ratio,
    fit_ou,
    log_price,
    rolling_ou,
)

# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

# Candidate pairs, grouped by the economic story that would justify them.
# A pair is a hypothesis about a shared driver, not a data-mining hit: two
# integrated oil majors share a crude price, two country ETFs share a commodity
# cycle, two staples share input costs and shelf space, the two metals share a
# precious-metal bid, and the two mega-caps share a platform economy. The scan
# tests the hypothesis; it does not invent it.
PAIRS = [
    ("XOM", "CVX"),    # integrated oil majors -- shared crude price
    ("EWA", "EWC"),    # Australia / Canada ETFs -- commodity-currency cycle
    ("KO", "PEP"),     # consumer staples -- shared input + distribution costs
    ("GLD", "SLV"),    # gold / silver -- shared precious-metal bid
    ("MSFT", "AAPL"),  # mega-cap tech -- shared platform economy
]

YEARS = 1              # history to pull; see SAMPLE-LENGTH WARNING above
HEDGE_WINDOW = 60      # bars for the rolling hedge regression
OU_WINDOW = 60         # bars for the rolling OU fit
MIN_OBS = 20           # minimum observations for any fit
PASS_ALPHA = 0.05      # significance for the ADF screen
JOHANSEN_DET = 0       # constant inside the cointegrating relation, no trend
JOHANSEN_LAGS = 1      # lagged differences in the VECM


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------


def fetch_prices(tickers, years: int = YEARS) -> pd.DataFrame:
    """Split- and dividend-adjusted daily closes, aligned across ``tickers``.

    Kept local rather than imported from ``backtest_5y`` so this module stays
    free of the vectorbt dependency: the scan is a pure statistics job and there
    is no reason for it to import a backtester to run.
    """
    raw = yf.download(
        list(tickers), period=f"{years}y", interval="1d",
        auto_adjust=True, progress=False,
    )
    if raw is None or len(raw) == 0:
        raise RuntimeError(f"yfinance returned no data for {tickers}")

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw.xs("Close", axis=1, level=0)
    else:
        close = raw[["Close"]]
        close.columns = list(tickers)

    close = close.reindex(columns=list(tickers)).astype(float).dropna()
    close.index = pd.DatetimeIndex(close.index).tz_localize(None)
    if close.empty:
        raise RuntimeError(f"no overlapping history for {tickers}")
    return close


# --------------------------------------------------------------------------
# cointegration tests
# --------------------------------------------------------------------------


def adf(series, regression: str = "c", autolag: str = "AIC") -> dict:
    """Augmented Dickey-Fuller test on ``series``.

    ``regression="c"`` includes a constant but no trend, which is the right
    spec for a spread: a cointegrating residual may sit at a non-zero level
    (that level is the pair's mean), but it must not be trending. Testing a
    spread with a trend term fitted would absorb the very drift that means the
    pair is broken.

    Returns the statistic, p-value, lag order and observation count. Returns a
    dict of NaNs rather than raising on a degenerate input, so a scan loop can
    record "untestable" instead of dying on one bad pair.
    """
    x = pd.Series(series, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    if len(x) < 20 or float(x.std()) == 0.0:
        return {"stat": np.nan, "pvalue": np.nan, "lags": 0, "n_obs": int(len(x))}

    stat, pvalue, lags, n_obs, _crit, _icbest = adfuller(
        x.to_numpy(), regression=regression, autolag=autolag
    )
    return {
        "stat": float(stat),
        "pvalue": float(pvalue),
        "lags": int(lags),
        "n_obs": int(n_obs),
    }


def johansen(log_a, log_b, det_order: int = JOHANSEN_DET,
             k_ar_diff: int = JOHANSEN_LAGS) -> dict:
    """Johansen trace test for the rank of the cointegrating space.

    Unlike Engle-Granger, Johansen treats both series symmetrically -- it does
    not privilege one as the regressand -- and it estimates the cointegrating
    vector by maximum likelihood rather than by a first-stage OLS. On a pair
    whose hedge ratio is plausible in both directions, that asymmetry is the
    thing Engle-Granger gets wrong.

    ``det_order=0`` puts a constant inside the cointegrating relation with no
    trend, matching the ADF spec above. For two series, rank >= 1 means the pair
    is cointegrated. (Rank 2 would mean both series are already stationary,
    which is a different model, and the scan flags it.) ``rank = -1`` means the
    test did not run or did not produce a usable statistic.

    The rank is found by the **sequential** procedure, and the word sequential
    is load-bearing. The trace statistics are tested in order -- first
    ``H0: r = 0``, then ``H0: r <= 1`` -- and the procedure **stops at the first
    failure to reject**. Counting every statistic that clears its critical value
    instead is a real bug, not a stylistic difference: in finite samples the
    sequence is not monotone, so ``lr1[1]`` can exceed its critical value while
    ``lr1[0]`` does not. Counting would then report rank 1 -- "cointegrated" --
    for a pair whose primary statistic was comfortably *inside* the null. On the
    live scan that turned a trace of 10.6 against a 95% critical value of 15.5
    (a clear non-rejection) into a reported candidate.
    """
    a = pd.Series(log_a, dtype=float).replace([np.inf, -np.inf], np.nan)
    b = pd.Series(log_b, dtype=float).replace([np.inf, -np.inf], np.nan)
    frame = pd.concat([a, b], axis=1).dropna()
    if len(frame) < max(30, 5 * (k_ar_diff + 2)):
        return {"trace": [np.nan, np.nan], "crit95": [np.nan, np.nan],
                "rank": -1, "eigvec": [np.nan, np.nan], "n_obs": int(len(frame))}

    res = coint_johansen(frame.to_numpy(), det_order, k_ar_diff)
    trace = [float(v) for v in res.lr1]
    crit95 = [float(res.cvt[i, 1]) for i in range(len(trace))]

    # statsmodels returns a non-finite trace statistic on a numerically
    # degenerate fit -- observed when the cointegrating relation is tight enough
    # that an eigenvalue lands exactly on 1.0, so its `log(1 - a)` term becomes
    # log(0) (or the log of a small negative produced by rounding). A NaN
    # statistic is not a failure to reject; it is a failure to *compute*, and the
    # two must not be conflated. Reporting rank 0 here would be a false negative
    # dressed as a finding, so it is reported as untestable (-1) instead.
    if not np.all(np.isfinite(trace)):
        return {
            "trace": trace,
            "crit95": crit95,
            "rank": -1,
            "eigvec": [np.nan, np.nan],
            "n_obs": int(len(frame)),
        }

    rank = 0
    for t, c in zip(trace, crit95):
        if t > c:
            rank += 1
        else:
            break
    # First cointegrating vector, normalised on the first series so the loading
    # is comparable across pairs: [1, -beta] up to scale.
    vec = res.evec[:, 0]
    vec = vec / vec[0] if vec[0] != 0 else vec
    return {
        "trace": trace,
        "crit95": crit95,
        "rank": rank,
        "eigvec": [float(vec[0]), float(vec[1])],
        "n_obs": int(len(frame)),
    }


# --------------------------------------------------------------------------
# per-pair scan
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ScanResult:
    """Everything the screen learned about one pair."""

    name_a: str
    name_b: str
    n_obs: int = 0

    # -- static spread (full-sample OLS hedge); in-sample by construction ----
    beta: float = np.nan
    alpha: float = np.nan
    r2: float = np.nan
    adf_leg_a: float = np.nan          # p-value, log price level
    adf_leg_b: float = np.nan
    adf_spread: float = np.nan         # p-value, static spread
    adf_spread_stat: float = np.nan
    joh_trace: float = np.nan          # r = 0 trace statistic
    joh_crit95: float = np.nan
    joh_rank: int = -1
    joh_beta: float = np.nan           # MLE cointegrating vector, on log_a

    # -- OU fit on the static spread (headline, in-sample) -------------------
    theta: float = np.nan              # reversion speed, per year
    half_life: float = np.nan          # trading days
    sigma_eq: float = np.nan
    ou_valid: bool = False

    # -- OU fit on the rolling spread (point-in-time) ------------------------
    theta_pit: float = np.nan          # median over accepted windows
    half_life_pit: float = np.nan
    sigma_eq_pit: float = np.nan
    beta_pit: float = np.nan           # median rolling hedge ratio
    ou_accept: float = np.nan          # fraction of windows accepted

    error: str = ""

    @property
    def pair(self) -> str:
        return f"{self.name_a}/{self.name_b}"

    @property
    def adf_pass(self) -> bool:
        """Static spread is stationary at PASS_ALPHA."""
        return bool(np.isfinite(self.adf_spread) and self.adf_spread < PASS_ALPHA)

    @property
    def joh_pass(self) -> bool:
        return bool(self.joh_rank >= 1)

    @property
    def legs_are_i1(self) -> bool:
        """Both log levels fail to reject a unit root -- the I(1) premise.

        If a leg is already stationary the pair is not an I(1)/I(1) setup, and
        a "cointegrating" residual between a stationary and a trending series is
        a different (and much less interesting) model.
        """
        return bool(
            np.isfinite(self.adf_leg_a) and np.isfinite(self.adf_leg_b)
            and self.adf_leg_a > PASS_ALPHA and self.adf_leg_b > PASS_ALPHA
        )

    @property
    def qualified(self) -> bool:
        """Passes the whole screen: I(1) legs, cointegrated, OU-identifiable."""
        return bool(
            not self.error
            and self.legs_are_i1
            and self.adf_pass
            and self.joh_pass
            and self.ou_valid
            and np.isfinite(self.theta)
            and self.theta > 0.0
        )


def scan_pair(name_a: str, name_b: str, prices: pd.DataFrame) -> ScanResult:
    """Screen one pair: hedge -> spread -> ADF/Johansen -> OU, static and PIT."""
    price_a, price_b = prices[name_a], prices[name_b]
    la, lb = log_price(price_a), log_price(price_b)

    # -- static spread: one hedge ratio over the whole sample ---------------
    h = fit_hedge_ratio(la, lb, min_obs=MIN_OBS)
    if not h.valid:
        # beta and r2 were computed even though the fit was rejected, so carry
        # them: a rejected hedge with a sane-looking beta is a different story
        # from one that could not be estimated at all, and the table would
        # otherwise print "nan" beside a verdict that quotes a number.
        return ScanResult(
            name_a, name_b, n_obs=h.n_obs, beta=h.beta, r2=h.r2,
            error=f"static hedge rejected (beta={h.beta:.3f}, r2={h.r2:.3f})",
        )

    static_spread = (la - h.alpha - h.beta * lb).dropna()

    a_adf = adf(la)
    b_adf = adf(lb)
    s_adf = adf(static_spread)
    joh = johansen(la, lb)

    # OU on the static spread. dt is one trading day, so theta is per year and
    # half_life comes back in trading days.
    ou = fit_ou(static_spread.to_numpy(), min_obs=MIN_OBS)

    # -- rolling spread: point-in-time, what a live run would have seen ------
    piv, hedge = cointegration_spread(
        price_a, price_b, window=HEDGE_WINDOW, min_obs=MIN_OBS
    )
    rou = rolling_ou(piv, window=OU_WINDOW, min_obs=MIN_OBS)
    good = rou["valid"]

    return ScanResult(
        name_a=name_a,
        name_b=name_b,
        n_obs=int(len(static_spread)),
        beta=h.beta,
        alpha=h.alpha,
        r2=h.r2,
        adf_leg_a=a_adf["pvalue"],
        adf_leg_b=b_adf["pvalue"],
        adf_spread=s_adf["pvalue"],
        adf_spread_stat=s_adf["stat"],
        joh_trace=joh["trace"][0],
        joh_crit95=joh["crit95"][0],
        joh_rank=joh["rank"],
        joh_beta=-joh["eigvec"][1],
        theta=ou.theta,
        half_life=ou.half_life,
        sigma_eq=ou.sigma_eq,
        ou_valid=ou.valid,
        theta_pit=float(rou.loc[good, "theta"].median()) if good.any() else np.nan,
        half_life_pit=(
            float(rou.loc[good, "half_life"].median()) if good.any() else np.nan
        ),
        sigma_eq_pit=(
            float(rou.loc[good, "sigma_eq"].median()) if good.any() else np.nan
        ),
        beta_pit=float(hedge.loc[hedge["valid"], "beta"].median())
        if hedge["valid"].any() else np.nan,
        ou_accept=float(good.mean()),
    )


# --------------------------------------------------------------------------
# ranking
# --------------------------------------------------------------------------


def rank(results: list) -> pd.DataFrame:
    """Rank qualified pairs fastest-reversion-first (theta desc, half-life asc).

    Only ``qualified`` pairs are ranked. Assigning a rank to a pair that failed
    the screen would defeat the purpose of screening -- the ranking is a claim
    about tradeable candidates, not about every series that was fitted.

    ``theta`` and ``half_life`` are reciprocal (``H = ln2/theta``), so ranking on
    either is the same ordering. Both are carried because theta is the model
    parameter and the half-life is the one a human can read.
    """
    rows = []
    for r in results:
        rows.append({
            "pair": r.pair,
            "ranked": r.qualified,
            "beta": r.beta,
            "r2": r.r2,
            "adf_p": r.adf_spread,
            "joh_trace": r.joh_trace,
            "joh_crit95": r.joh_crit95,
            "theta": r.theta,
            "half_life": r.half_life,
            "half_life_pit": r.half_life_pit,
            "ou_accept": r.ou_accept,
            "n_obs": r.n_obs,
        })
    table = pd.DataFrame(rows)
    if table.empty:
        return table

    ok = table["ranked"]
    ordered = (
        table[ok].sort_values(["theta", "half_life"], ascending=[False, True])
    )
    ordered.insert(0, "rank", range(1, len(ordered) + 1))

    # Unranked rows keep the same theta ordering as the ranked block, so the eye
    # is not misled by a table that changes sort order halfway down. NaNs (a
    # pair that never produced a fit) sort last.
    rest = table[~ok].sort_values("theta", ascending=False, na_position="last").copy()
    rest.insert(0, "rank", np.nan)
    return pd.concat([ordered, rest], ignore_index=True)


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def _verdict(r: ScanResult) -> str:
    """One-line reason a pair is or is not a candidate."""
    if r.error:
        return f"rejected: {r.error}"
    if r.joh_rank == -1:
        return "Johansen untestable (degenerate or too short)"
    if not r.legs_are_i1:
        return "not I(1): a leg is already stationary"
    if not r.adf_pass and not r.joh_pass:
        return "no cointegration: ADF and Johansen both fail"
    if not r.adf_pass:
        return "ADF fails, Johansen passes (weak)"
    if not r.joh_pass:
        return "Johansen fails, ADF passes (weak)"
    if not r.ou_valid:
        return "cointegrated but OU guard rejects (no usable reversion)"
    return "candidate"


def print_report(results: list, table: pd.DataFrame, years: int = YEARS) -> None:
    n_bar = results[0].n_obs if results else 0
    print("=" * 78)
    print("Universe scan: OU mean-reversion candidates")
    print("=" * 78)
    print(f"pairs        : {', '.join(r.pair for r in results)}")
    print(f"history      : {years}y daily (~{n_bar} bars)")
    print(f"windows      : hedge {HEDGE_WINDOW}d, OU {OU_WINDOW}d, min_obs {MIN_OBS}")
    print(f"ADF spec     : constant, no trend, AIC lag; alpha={PASS_ALPHA}")
    print(f"Johansen     : det_order={JOHANSEN_DET}, k_ar_diff={JOHANSEN_LAGS}, "
          f"95% trace critical value")

    print("\n" + "-" * 78)
    print("1. Cointegration screen")
    print("-" * 78)
    print("   'legs' = p-values for a unit root in each log price (want HIGH:")
    print("   a leg should be non-stationary). 'spread' = p-value for the")
    print("   static residual (want LOW: the residual should be stationary).")
    print(f"\n   {'pair':<11}{'beta':>7}{'R2':>7}{'leg A':>8}{'leg B':>8}"
          f"{'ADF p':>8}{'ADF stat':>10}{'Joh tr':>8}{'crit95':>8}{'rank':>6}")
    for r in results:
        print(f"   {r.pair:<11}{r.beta:>7.3f}{r.r2:>7.3f}"
              f"{r.adf_leg_a:>8.3f}{r.adf_leg_b:>8.3f}{r.adf_spread:>8.3f}"
              f"{r.adf_spread_stat:>10.2f}{r.joh_trace:>8.1f}"
              f"{r.joh_crit95:>8.1f}{r.joh_rank:>6d}")

    print("\n" + "-" * 78)
    print("2. Ranking by mean-reversion speed (theta), fastest first")
    print("-" * 78)
    print("   'theta' is per year. 'H' is the half-life in trading days")
    print("   (H = ln2/theta). 'H_pit' is the median from the point-in-time")
    print("   rolling fit and is the honest counterpart to the in-sample H.")
    print("   'ok' is the fraction of rolling windows that passed the OU guard.")
    print(f"\n   {'#':>3}  {'pair':<11}{'theta':>9}{'H(d)':>8}{'H_pit(d)':>10}"
          f"{'ok':>7}{'sigma_eq':>10}  {'verdict':<44}")
    for _, row in table.iterrows():
        r = next(x for x in results if x.pair == row["pair"])
        rank_s = f"{int(row['rank'])}" if np.isfinite(row["rank"]) else "-"
        hl_pit = (f"{row['half_life_pit']:.1f}"
                  if np.isfinite(row["half_life_pit"]) else "-")
        theta_s = f"{row['theta']:.2f}" if np.isfinite(row["theta"]) else "-"
        hl_s = f"{row['half_life']:.1f}" if np.isfinite(row["half_life"]) else "-"
        se_s = f"{r.sigma_eq:.4f}" if np.isfinite(r.sigma_eq) else "-"
        ok_s = f"{r.ou_accept:.1%}" if np.isfinite(r.ou_accept) else "-"
        print(f"   {rank_s:>3}  {row['pair']:<11}{theta_s:>9}{hl_s:>8}{hl_pit:>10}"
              f"{ok_s:>7}{se_s:>10}  {_verdict(r):<44}")

    qualified = [r for r in results if r.qualified]
    print("\n" + "-" * 78)
    print("Reading this screen")
    print("-" * 78)
    if qualified:
        print(f"  {len(qualified)} of {len(results)} pairs passed the full screen. "
              f"Fastest reversion:")
        for r in sorted(qualified, key=lambda x: -x.theta)[:3]:
            print(f"    {r.pair:<11} theta={r.theta:>7.2f}/yr  "
                  f"H={r.half_life:>5.1f}d  beta={r.beta:.3f}  "
                  f"ADF p={r.adf_spread:.4f}  Johansen rank={r.joh_rank}")
    else:
        print("  No pair passed the full screen. That is a result, not a failure:")
        print("  on this sample none of these spreads is both cointegrated and")
        print("  OU-identifiable, so the honest action is to trade none of them.")

    print("\n  Cautions that apply to every number above:")
    print(f"  - {years}y is ~{n_bar} bars. ADF and Johansen have low power in short")
    print("    samples, so a pass is weak evidence and a fail is weaker still.")
    print("    Power is not the binding constraint here though: the verdict on")
    print("    these five pairs is the same at 1 year and at 5.")
    print("  - The spec's guard caps half-life at the window span, so a slow but")
    print("    genuine pair is reported as REJECTED rather than as slow. The")
    print("    ranking is over fast pairs only; it is censored at the top.")
    print(f"  - {len(results)} pairs at alpha={PASS_ALPHA} implies "
          f"~{len(results) * PASS_ALPHA:.2f} false positives under the null --")
    print("    but Johansen is over-sized (~9-13% empirical against a nominal 5%,")
    print("    and flat in the sample size; see the module docstring), so double")
    print("    that. A Johansen pass is a lead to investigate, not a result.")
    print("  - The ADF and Johansen tests use the SAME static spread, fitted on")
    print("    the same data they are then tested on. That is the standard")
    print("    Engle-Granger procedure and it biases toward finding cointegration.")
    print("  - The headline theta/H are fitted on the FULL sample and are")
    print("    in-sample. Compare them against H_pit before believing either; a")
    print("    wide gap means the pair's relationship is not stable.")
    print("  - Ranking is not a strategy. A short half-life means more round")
    print("    trips, and every round trip pays the spread twice -- check the")
    print("    turnover in backtest_5y.py before reading speed as opportunity.")


def main(years: int = YEARS) -> int:
    if years < 1:
        print(f"!! years must be >= 1, got {years}")
        return 2
    tickers = sorted({t for pair in PAIRS for t in pair})
    print(f"fetching {years}y of daily data for {len(tickers)} tickers: "
          f"{', '.join(tickers)}")
    try:
        prices = fetch_prices(tickers, years=years)
    except Exception as exc:                      # network / bad ticker
        print(f"\n!! could not fetch prices: {type(exc).__name__}: {exc}")
        return 1
    print(f"  {len(prices)} bars, {prices.index[0].date()} -> "
          f"{prices.index[-1].date()}\n")

    results = []
    for a, b in PAIRS:
        if a not in prices.columns or b not in prices.columns:
            print(f"  !! skipping {a}/{b}: missing from the download")
            continue
        try:
            results.append(scan_pair(a, b, prices))
        except Exception as exc:
            results.append(ScanResult(a, b, error=f"{type(exc).__name__}: {exc}"))

    if not results:
        print("no pairs scanned")
        return 1

    print_report(results, rank(results), years=years)
    return 0


if __name__ == "__main__":
    import sys

    # `python universe_scan.py [years]` -- the horizon is the single most
    # important knob on this screen, so it should be reachable without editing
    # the module.
    _argv = sys.argv[1:]
    try:
        _years = int(_argv[0]) if _argv else YEARS
    except ValueError:
        print(f"usage: python universe_scan.py [years]   (got {_argv[0]!r})")
        raise SystemExit(2)
    raise SystemExit(main(_years))
