---
slug: mean-reversion-ornstein-uhlenbeck
title: "Mean-Reversion — Ornstein-Uhlenbeck"
asset_class: "single series (index ETF, equity, or a cointegration spread)"
style: "time-series mean-reversion"
horizon: "Formation: rolling window. Hold: days to weeks."
instruments: "one liquid series (e.g. SPY), or a stationary spread"
---

# Mean-Reversion — Ornstein-Uhlenbeck

| Field | Value |
|---|---|
| Why it sits here | The continuous-time workhorse for a single mean-reverting series. Pairs-trading spreads, index ETFs, and vol series are all fit this way. |
| Aliases | OU process, elastic random walk, Vasicek model, z-score reversion |
| Asset class | single series (index ETF, equity, or a cointegration spread) |
| Style | time-series mean-reversion |
| Typical horizon | Formation: rolling window (e.g. 60 days). Hold: days to weeks. |
| Instruments | one liquid series (e.g. SPY), or a stationary spread |

Shared symbols live in [`../strategies/_shared-notation.md`](../strategies/_shared-notation.md).

## 1. Overview

A single series that is pulled back toward a level. Fit the pull, measure how far the series has strayed, and fade the stray. Long when it sits below equilibrium, short when it sits above, flat when it is near.

You are betting that the series is **stationary** — that a deviation from its long-run mean decays rather than compounds. The model is a continuous-time Ornstein-Uhlenbeck process, and the traded object is the standardized deviation $z_t$. This is a time-series file: one instrument, one equilibrium, one signal. It is not [`014-mean-reversion-single-cluster.md`](../strategies/014-mean-reversion-single-cluster.md), which is cross-sectional (strip an industry mean, fade the residual across $N$ names, dollar-neutral by construction). Here the mean is temporal, not cross-sectional.

You are not betting that SPY goes up. You are not running price momentum — the sign is the opposite of [`001-price-momentum.md`](../strategies/001-price-momentum.md) on the same window, and if $b\ge 1$ in the fit below, momentum is the correct model and this file refuses to trade. You are not trading a spread you never checked for cointegration.

**The honest failure mode.** Equity index levels trend. A log-price OU fit over a 60-day window will frequently produce $\theta$ near zero and a half-life longer than the window, because an index is close to a random walk with drift. That is not a bug in the implementation — it is the model reporting that its own premise fails. The guard in §4.2 exists so the strategy stands down instead of pretending. Report the fraction of windows that were rejected; if it is high, the series is not OU and this spec does not apply to it.

Typical users are single-name or spread mean-reversion sleeves. Turnover is moderate. Delay-1: the fit and the score at date $t$ use data through $t$ and trade $t+1$.

## 2. First principles

Let $X_t=\log P_t$ be the log price (or any series you believe is stationary; a cointegration spread works unchanged). The Ornstein-Uhlenbeck process is

$$
dX_t = \theta(\mu - X_t)\,dt + \sigma\,dW_t, \qquad \theta>0
$$

$\mu$ is the long-run mean the series is pulled toward. $\theta$ is the speed of that pull. $\sigma$ is the diffusion scale. The drift term is the entire strategy: when $X_t>\mu$ the drift is negative, when $X_t<\mu$ it is positive, and the expected pull is proportional to the distance $X_t-\mu$.

The process is stationary, and its stationary distribution is Gaussian:

$$
X_\infty \sim \mathcal N\!\left(\mu,\ \sigma_{\mathrm{eq}}^2\right),
\qquad
\sigma_{\mathrm{eq}} = \frac{\sigma}{\sqrt{2\theta}}
$$

$\sigma_{\mathrm{eq}}$ is the equilibrium standard deviation — the natural yardstick for "how far has it strayed." That ratio is why $\sigma$ and $\theta$ must both be estimated: a fast pull ($\theta$ large) means a tight equilibrium, a slow pull means a loose one.

The characteristic time of the pull is the half-life:

$$
H = \frac{\ln 2}{\theta}
$$

Half the deviation is gone after $H$. If $H$ is longer than the estimation window, you have not observed a full cycle of the reversion you are claiming to trade.

That is the whole model. Everything below is how to estimate $(\theta,\mu,\sigma)$ without looking ahead, how to size it, and how to stop.

## 3. Notation

| Symbol | Definition |
|---|---|
| $X_t$ | $\log P_t$ (or a stationary spread) |
| $\theta$ | mean-reversion speed, per unit time |
| $\mu$ | long-run mean of $X$ |
| $\sigma$ | diffusion volatility |
| $\sigma_{\mathrm{eq}}$ | equilibrium std, $\sigma/\sqrt{2\theta}$ |
| $H$ | half-life, $\ln 2/\theta$ |
| $b$ | AR(1) coefficient, $e^{-\theta\Delta}$ |
| $z_t$ | standardized deviation, $(X_t-\mu_t)/\sigma_{\mathrm{eq},t}$ |
| $q_t$ | regime, $+1$ long / $-1$ short / $0$ flat |
| $f^\ast$ | full-Kelly leverage |
| $\lambda$ | fractional-Kelly multiplier, $\lambda\in(0,1]$ |
| $D_t$ | signed dollar position |
| $E_t$ | equity |
| $\mathrm{DD}_t$ | peak-to-trough drawdown |

## 4. Mathematics

### 4.1 Exact discretization and the AR(1) fit

Over a step $\Delta$, the OU process has an exact solution, not an Euler approximation:

$$
X_{t+\Delta} = \mu + (X_t-\mu)e^{-\theta\Delta} + \sigma\sqrt{\frac{1-e^{-2\theta\Delta}}{2\theta}}\;\epsilon_t,
\qquad \epsilon_t\sim\mathcal N(0,1)
$$

This is an AR(1) regression with $b=e^{-\theta\Delta}$:

$$
X_{t+\Delta} = a + bX_t + \eta_t,
\qquad a=\mu(1-b)
$$

Estimate $a,b$ by OLS on the window. Then

$$
\hat\theta = -\frac{\ln b}{\Delta},
\qquad
\hat\mu = \frac{a}{1-b},
\qquad
\hat\sigma_{\mathrm{eq}} = \sqrt{\frac{s^2}{1-b^2}},
\qquad
\hat\sigma = \hat\sigma_{\mathrm{eq}}\sqrt{2\hat\theta}
$$

where $s^2$ is the residual variance of the AR(1) with the usual $n-2$ divisor. The $\sigma_{\mathrm{eq}}$ form is used directly rather than routing through $\sigma$ and $\theta$: it is algebraically identical and numerically steadier when $\theta$ is small.

Use the exact discretization, not Euler. Euler on a fast-reverting series biases $\theta$ downward and is the classic silent error in this model.

### 4.2 Identification guard

The fit is only admissible when all of the following hold:

- $0 < b \le 1-\epsilon$ for a small numerical floor $\epsilon$ (implementation: $10^{-6}$). $b\ge 1$ is a unit root or an explosive series — **not mean-reverting**; $b\le 0$ makes $\ln b$ undefined. Either way, refuse. The floor matters: on a deterministic ramp the OLS slope lands within float epsilon of $1$ and which side it falls on is pure rounding noise. If it lands just *below*, the fit passes a naive $b<1$ check while $\hat\sigma_{\mathrm{eq}}=\sqrt{s^2/(1-b^2)}$ becomes a $0/0$ form — both $s^2$ and $1-b^2$ are $\sim 0$ — and $z$ explodes to order $10^{21}$. That opens a real position on a pure trend. The floor admits reversion speeds down to $\sim 2.5\times10^{-4}$/yr, so it never binds on a genuinely stationary series; it exists only to kill the degenerate fit.
- $\hat\theta>0$ and finite.
- $H\le$ the span of the estimation window (implementation: $H\le n_{\mathrm{obs}}-1$ bars). A half-life longer than the window means no full cycle of the claimed reversion was ever observed. This guard is not cosmetic — it is what keeps $\hat\mu$ meaningful. Since $\hat\mu=a/(1-b)$, a tiny $\hat\theta$ makes the estimator a near-$0/0$ divide, so a small $\hat\theta$ does not give a merely *uncertain* $\hat\mu$; it gives a meaningless one. Observed on SPY: a window with $\hat\theta\approx4\times10^{-6}$ produced $\hat\mu=112$ against a log price of $6.6$, and $z=-53$. Bounding $1-b$ away from zero keeps $\hat\mu$ on the scale of the data.
- $\hat\sigma_{\mathrm{eq}}>0$. A zero-variance fit (perfectly constant, or a deterministic ramp with zero residuals) gives an undefined $z$. Refuse rather than divide by zero.
- Enough observations, $n\ge n_{\min}$.

A near-unit-root fit that *passes* all of the above is still statistically weak: $b$ close to $1$ makes $\hat\theta$ high-variance, so single-window half-lives are noisy even when $\hat\mu$ is tightly identified. Treat $\hat\theta$ as a diagnostic, not a precise quantity.

A rejected window produces no score and **no position**. It does not fall back to the previous $\mu$, and it does not fill $z$ with zero — zero is a *signal* (dead centre of the band), not a missing value. This is the guard that makes the file honest on trending series.

### 4.3 The score

$$
z_t = \frac{X_t-\hat\mu_t}{\hat\sigma_{\mathrm{eq},t}}
$$

$z_t<0$ is below equilibrium (cheap, candidate long), $z_t>0$ is above (rich, candidate short). Both $\hat\mu_t$ and $\hat\sigma_{\mathrm{eq},t}$ are estimated on a window **ending at $t$**. Estimating them on the full sample, or on the window you trade, is look-ahead and inflates the backtest — the same trap called out in every reversion file in this kit.

### 4.4 Regime

With entry threshold $z_{\mathrm{entry}}$ and exit threshold $z_{\mathrm{exit}}$, requiring $0<z_{\mathrm{exit}}<z_{\mathrm{entry}}$:

- $q_t=0$ and $z_t\le -z_{\mathrm{entry}}$ → $q_t=+1$ (long)
- $q_t=0$ and $z_t\ge +z_{\mathrm{entry}}$ → $q_t=-1$ (short)
- $q_t\neq 0$ and $|z_t|\le z_{\mathrm{exit}}$ → $q_t=0$ (flat)
- $q_t=+1$ and $z_t\ge +z_{\mathrm{entry}}$ → $q_t=-1$ (flip)
- $q_t=-1$ and $z_t\le -z_{\mathrm{entry}}$ → $q_t=+1$ (flip)
- otherwise hold $q_{t-1}$

Two distinct thresholds, so the book does not churn on every wobble across a single line. A rejected or undefined $z_t$ forces $q_t=0$: no model, no position.

**Minimum holding period.** Optionally, once a regime is on it may not exit or flip until it has been in force for $H_{\mathrm{hold}}$ bars (default $3$). Entry is not delayed: opening from flat is one trade either way, so waiting only forgoes part of the deviation being harvested. Exits and flips are where turnover lives — on a fast-reverting spread they are nearly all of it, and each one pays the spread twice. The constraint is *subordinate to the guard*, never an override of it: an undefined $z_t$ flattens the book mid-hold regardless, because a broken fit must stand the strategy down whatever the holding clock says.

This is a cost control, not a signal improvement. It trades a little edge for less turnover, and whether that is a good trade is an empirical question about the pair (see §10).

### 4.5 Kelly sizing

Over the next step the model says the expected change in $X$ is $\theta(\mu-X_t)\Delta$ with variance $\sigma^2\Delta$. Continuous Kelly for a bet with expected excess return $\mu_{\mathrm{ret}}$ and variance $\sigma_{\mathrm{ret}}^2$ is $f^\ast=\mu_{\mathrm{ret}}/\sigma_{\mathrm{ret}}^2$. Substituting and cancelling $\Delta$:

$$
f^\ast = \frac{\theta(\mu-X_t)}{\sigma^2}
      = \frac{\theta(-z_t\sigma_{\mathrm{eq}})}{2\theta\sigma_{\mathrm{eq}}^2}
      = -\frac{z_t}{2\sigma_{\mathrm{eq}}}
$$

The $\Delta$ cancels and $\theta$ cancels — the Kelly leverage depends only on the standardized deviation and the equilibrium scale. $f^\ast>0$ when $z_t<0$ (long the cheap side), as it must.

$f^\ast$ is the **full**-Kelly bet and it is aggressive: with $\sigma_{\mathrm{eq}}\approx 0.04$, a $2\sigma$ deviation implies $f^\ast\approx 25\times$. Full Kelly on an estimated, possibly-misspecified $\mu$ is a ruin machine. So:

$$
f_t = \mathrm{clip}\!\left(\lambda\,f^\ast_t,\ -\ell_{\max},\ +\ell_{\max}\right)
$$

with $\lambda$ the fractional-Kelly multiplier (default $0.25$) and $\ell_{\max}$ a hard leverage cap (default $1.0$ — no borrowing). $\lambda$ and $\ell_{\max}$ are risk parameters, not free knobs to be tuned until the backtest looks good.

Direction comes from the regime, magnitude from Kelly:

$$
D_t = q_t\,\lvert f_t\rvert
$$

$q_t$ already carries the sign of the deviation, so taking the magnitude of $f_t$ avoids squaring the sign. When $q_t=0$, $D_t=0$.

**No-trade band.** Optionally, the target is not followed bar for bar. With band width $\delta$ (default $0.05$), the *held* weight $w_t$ moves to the new target $\tilde D_t$ only when it has drifted out of the band:

$$
w_t =
\begin{cases}
\tilde D_t & \text{if } w_{t-1}=0 \ \text{or } \tilde D_t=0 \ \text{or } \mathrm{sgn}\,\tilde D_t \neq \mathrm{sgn}\,w_{t-1}\\[2pt]
\tilde D_t & \text{if } |\tilde D_t - w_{t-1}| > \delta\\[2pt]
w_{t-1} & \text{otherwise}
\end{cases}
$$

The band damps ***resizing only***. Entry, exit and flip always execute, whatever their size: they are changes in *risk direction*, not in scale, and gating a reversal on a size threshold would let a stale position survive a sign flip of the signal. So the band is subordinate to §4.4 exactly as the holding period is — the regime decides *whether* there is a position, the band decides only *how often the size is refreshed*. Every value emitted is a previously accepted (already clipped) target, so $|w_t|\le \ell_{\max}$ still holds.

**When the band is vacuous — read this before tuning it.** The band can only damp a target that moves in steps smaller than $\delta$, and that requires Kelly to be *unsaturated*. Since the regime only opens at $|z|\ge z_{\mathrm{entry}}$, unsaturation requires

$$
\lambda\,\frac{|z|}{2\sigma_{\mathrm{eq}}} < \ell_{\max}
\quad\Longrightarrow\quad
\sigma_{\mathrm{eq}} > \frac{\lambda\,z_{\mathrm{entry}}}{2\,\ell_{\max}}
= 0.25 \ \text{at the defaults.}
$$

A spread whose equilibrium volatility is a quarter of its own level is not a stationary spread. On every realistic spread $\lambda f^\ast$ exceeds the cap by one to three orders of magnitude, $|f_t|=\ell_{\max}$ on *every* in-market bar, and

$$
\tilde D_t = q_t\,\ell_{\max} \in \{-1, 0, +1\}
$$

is a pure step function. There is then **no resizing channel at all**: turnover is $100\%$ regime changes, and no band width — $0.05$, $0.15$, $0.30$ — changes a single share traded. This is a corner solution of the sizing rule, not a defect in the band. Report the fraction of in-market bars with unsaturated Kelly; when it is $0$, the band is inert by construction and the only lever on turnover is the regime clock ($z_{\mathrm{entry}}$, $z_{\mathrm{exit}}$, and the §4.2 guard), because every regime change pays the spread twice.

### 4.6 Kill switch

Track the running peak of equity and the peak-to-trough drawdown:

$$
\mathrm{peak}_t=\max_{s\le t}E_s,
\qquad
\mathrm{DD}_t=\frac{\mathrm{peak}_t-E_t}{\mathrm{peak}_t}
$$

When $\mathrm{DD}_t\ge \mathrm{DD}_{\max}$ (default $0.05$), the switch trips: the book is **flattened** and no new position is taken. Default is a hard latch — it does not re-arm.

Timing honesty: $\mathrm{DD}_t$ is known at the close of $t$. You cannot undo the loss that produced it. The earliest honest action is a flat position for $t+1$, which is what the engine does. A backtest that removes the breaching day's loss is lying.

This is a risk overlay, not a signal. It caps the damage from a broken model; it does not detect one.

## 5. Step-by-step algorithm

1. **Series.** Build $X_t=\log P_t$ from split- and dividend-adjusted closes. This step exists because an unadjusted series has jumps at corporate actions that the fit reads as reversion.
2. **Window.** Select the trailing window ending at $t$ (default 60 days). This step exists so nothing after $t$ can enter $\hat\mu_t$ or $\hat\sigma_{\mathrm{eq},t}$.
3. **Fit.** OLS AR(1) on the window, then $\hat\theta,\hat\mu,\hat\sigma_{\mathrm{eq}}$. This step exists to recover the continuous-time parameters from the discrete series via the exact solution.
4. **Guard.** Reject the window unless $0<b<1$, $\hat\theta>0$, $\hat\sigma_{\mathrm{eq}}>0$, $n\ge n_{\min}$. This step exists because a trending series must produce no trade, not a default trade.
5. **Score.** $z_t=(X_t-\hat\mu_t)/\hat\sigma_{\mathrm{eq},t}$. This step exists to make deviations comparable across windows with different volatility.
6. **Regime.** Apply the entry/exit/flip rules with $q_t\in\{-1,0,+1\}$. This step exists to stop single-line churn.
7. **Size.** $f_t=\mathrm{clip}(\lambda f^\ast_t,-\ell_{\max},\ell_{\max})$, $D_t=q_t\lvert f_t\rvert$. This step exists because the Kelly bet is far too large unfractioned.
8. **Guard the book.** Apply the drawdown kill switch to the equity path. This step exists to bound the loss when the stationarity premise is wrong.
9. **Blotter.** Delay-1 intents. Never live routing.

## 6. Execution protocol

- Decide with information strictly before the fill. Fit and score at $t$, trade $t+1$.
- One series, so there is no cross-sectional neutrality to enforce and no short-locate basket to rebuild — but a short leg still needs borrow.
- If the series is halted or the print is stale, do not fill from the previous close.

## 7. Data contract

Required, point-in-time:

- Adjusted close (splits and dividends) for the single series
- Enough history for the longest window plus warmup
- Borrow, if the short leg is used

Not used by this spec: cross-sectional ranks, industry maps, factor loadings, options surfaces.

If you do $X$ = fit on the full sample, $\hat\mu$ and $\hat\sigma_{\mathrm{eq}}$ have seen the future and every $z_t$ is contaminated. If you do $X$ = use unadjusted closes, the fit reads splits as reversion. If you do $X$ = treat a rejected window as $z=0$, you have manufactured a signal out of a missing value.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $X$ | $\log P$ | or a stationary spread |
| window | 60 days | trailing, ends at $t$ |
| $n_{\min}$ | 20 | minimum observations for a fit |
| $z_{\mathrm{entry}}$ | 2.0 | open threshold |
| $z_{\mathrm{exit}}$ | 0.5 | close threshold, $<z_{\mathrm{entry}}$ |
| $H_{\mathrm{hold}}$ | 3 bars | minimum holding period; $0$ disables |
| $\delta$ | 0.05 | no-trade band on the target weight; $0$ disables. Vacuous when Kelly is saturated (§4.5) |
| $\lambda$ | 0.25 | fractional Kelly |
| $\ell_{\max}$ | 1.0 | hard leverage cap |
| $\mathrm{DD}_{\max}$ | 0.05 | kill switch, peak-to-trough |
| delay | 1 day | fit at $t$, trade $t+1$ |

## 9. Agent implementation contract

Build three Python modules.

`strategy.py`:

1. `fit_ou(x, dt, min_obs) -> OUParams` — OLS AR(1) → $(\hat\theta,\hat\mu,\hat\sigma_{\mathrm{eq}},\hat\sigma,H,b)$, with a `valid` flag implementing the §4.2 guard. Never raises on a degenerate window; returns `valid=False`.
2. `rolling_ou(x, window, dt, min_obs) -> pd.DataFrame` — point-in-time parameters, one row per date, each using only data through that date.
3. `ou_zscore(x, ou) -> pd.Series` — $z_t$, `NaN` where the fit is invalid or $\hat\sigma_{\mathrm{eq}}\le 0$. Never returns $\pm\infty$.
4. `ou_signal(z, z_entry, z_exit, min_holding) -> pd.Series` — regime $q_t$ in $\{-1,0,+1\}$ per §4.4, including the optional minimum holding period. An undefined $z_t$ still forces $0$, even mid-hold.
5. `kelly_leverage(z, sigma_eq, kelly_fraction, max_leverage) -> pd.Series` — signed $f_t$, finite everywhere.
6. `target_weights(signal, z, sigma_eq, kelly_fraction, max_leverage, rebalance_buffer) -> pd.Series` — $D_t=q_t\lvert f_t\rvert$ per §4.5, with the optional no-trade band $\delta$ applied as the *last* step. The band must never suppress an entry, an exit or a flip, and the primitive's own default is $\delta=0$ so that a caller which does not ask for a band gets the pure map.
   - `ou_spread_strategy(..., rebalance_buffer)` and `ou_strategy(..., rebalance_buffer)` thread $\delta$ through to it, defaulting to $0.05$.

`risk.py`:

7. `RiskLimits` — $\lambda$, $\ell_{\max}$, $\mathrm{DD}_{\max}$, re-arm options.
8. `DrawdownKillSwitch.update(equity) -> bool` — running peak, drawdown, latch.
9. `RiskEngine.run(signal, z, sigma_eq, returns) -> RiskReport` — sizing plus the kill switch applied to the equity path, returning executed weights, equity, drawdown, and breach metadata.

`tests/`:

10. A pytest suite covering zero volatility, the identification guard, market shocks, kill-switch execution, and look-ahead.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Non-stationarity.** The dominant failure. An index log price is near a random walk; the fit says so and the guard must stand the strategy down rather than trade a fictional $\mu$.
- **Regime shift in $\mu$.** A structural break moves the true equilibrium. The rolling window makes this a slow bleed, not an instant error.
- **$\theta$ estimation bias.** $\theta$ is biased and noisy in short windows; the half-life can be badly wrong. This is why $\lambda<1$ and the leverage cap are not optional.
- **Full-Kelly ruin.** $f^\ast$ is enormous at $2\sigma$. Unfractioned Kelly on an estimated drift destroys the account.
- **Kill-switch whipsaw.** A hard latch exits and never returns. That is the intended trade: bounded loss in exchange for forgoing recovery.
- **Look-ahead in the window.** Full-sample $\hat\mu$ is the single most common way this backtest lies.

## 11. Acceptance tests

- Constant series → fit `valid=False`, no position, no divide-by-zero.
- Deterministic ramp (zero residual variance) → `valid=False`, no position.
- Random walk ($b\ge1$) → `valid=False`, no position.
- Synthetic OU with known $(\theta,\mu,\sigma)$ → recovered parameters within tolerance; $H=\ln2/\theta$.
- $X_t<\hat\mu_t$ → $z_t<0$ → regime $+1$ at the entry threshold.
- $z$ undefined → regime $0$, and it stays $0$ until a valid $z$ returns.
- $\lvert f_t\rvert\le\ell_{\max}$ always; $\sigma_{\mathrm{eq}}=0$ → $f_t=0$, never `inf`/`NaN`.
- $H_{\mathrm{hold}}=3$ → every completed regime spans at least $3$ bars; $H_{\mathrm{hold}}=0$ reproduces the unconstrained §4.4 regime exactly. An undefined $z_t$ still forces $q_t=0$ mid-hold.
- $\delta=0$ → `target_weights` reproduces the pure map $D_t=q_t\lvert f_t\rvert$ exactly.
- $\delta>0$ → a target oscillating by less than $\delta$ within one regime is held flat; an entry, an exit and a flip each execute on the bar they are signalled regardless of size, including with $\delta$ set larger than any attainable weight; and $\lvert w_t\rvert\le\ell_{\max}$ always.
- The band is inert when Kelly is saturated: with $\lambda f^\ast>\ell_{\max}$ on every in-market bar, $\delta\in\{0.05,0.15,0.30\}$ leaves the traded notional bit-for-bit unchanged. A spread with large enough $\sigma_{\mathrm{eq}}$ to unsaturate Kelly must show the band biting.
- $\mathrm{DD}\ge 5\%$ → switch trips; executed weight is $0$ from the next bar and stays $0$.
- $\mathrm{DD}=4.9\%$ → switch does not trip.
- Permuting future data must not change any past $z_t$, $q_t$, or $D_t$.
- A single $-20\%$ shock trips the switch and the loss stops growing afterward.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.
- Uhlenbeck & Ornstein (1930); Vasicek (1977) for the equivalent rate form.
- [`../strategies/003-pairs-trading.md`](../strategies/003-pairs-trading.md) and [`../strategies/014-mean-reversion-single-cluster.md`](../strategies/014-mean-reversion-single-cluster.md) for the cross-sectional relatives.

---

*Research spec for quantitative work. Not investment advice.*
