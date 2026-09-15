---
rank: 26
slug: statistical-arbitrage-optimization
title: "Statistical Arbitrage — Optimization"
asset_class: "equities"
style: "mean-variance / dollar-neutral"
horizon: "Daily to weekly. Alphas from reversal, momentum, ML, etc."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 026. Statistical Arbitrage — Optimization

| Field | Value |
|---|---|
| Popularity rank (this kit) | 26 of 101 |
| Why it sits here | Workhorse live construction: maximize Sharpe (or mean-variance) of expected residual returns subject to dollar neutrality, using a factor covariance — not the sample covariance. |
| Aliases | mean-variance stat-arb, max-Sharpe overlay |
| Asset class | equities |
| Style | mean-variance / dollar-neutral |
| Typical horizon | Daily to weekly. Alphas from reversal, momentum, ML, etc. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Given expected returns $E_i$ and a positive-semidefinite covariance $C$, take max-Sharpe weights, optionally with $\sum_i w_i=0$. This file is the optimizer, not the alpha. $E_i$ comes from some other spec (cluster residual, momentum, a blend). Sample $C$ is singular or unstable unless $T\gg N$; use a multifactor model.

You are betting that the forecast $E$ has sign and relative magnitude worth trading after risk-adjusting by $C^{-1}$, not that the optimizer creates alpha. Garbage $E$ in, a leveraged garbage book out. You are not claiming the closed form survives hard position bounds — those need a QP, and Sharpe $\neq$ mean-variance once inequalities bind.

You are also not fitting $C$ on the same window you forecast $E$ from and then trading that window. That is look-ahead. Typical user: a production stat-arb desk that already has a residual or momentum alpha and needs a dollar-neutral, factor-aware overlay. Horizon intuition: recompute $E$ and $C$ daily to weekly, hold until the next solve. Inverse-vol on a $z$-score is what you get if $C=I$ and units mismatch — match units.

If you invert a raw $N\times N$ sample covariance with $T\le N$, or skip the gross rescale, the backtest is numerical noise or hidden leverage, not max Sharpe.

## 2. First principles

A portfolio is a vector of weights. Over the holding horizon the P&L return is $w^\top R$. Replace $R$ by a forecast $E$ and a covariance $C$. Expected P&L per unit gross is

$$
\mathcal{P} = \sum_i E_i w_i
$$

This is the forecasted book return, $E^\top w$. It is only as honest as $E$. If $E$ is a $z$-score and you treat it as a daily expected return, $\mathcal{P}$ is in the wrong units. The optimizer will still run. This step exists to name the numerator of Sharpe before any invert.

Variance of that P&L is

$$
\mathcal{V}^2 = \sum_{ij} C_{ij} w_i w_j
$$

$w^\top C w$. $C$ must be the covariance of the same return units as $E$, over the same horizon. A factor model for $C$ is required when $N$ is large; a sample $C$ with $T\le N$ is singular and this quadratic form is not a well-defined risk. Skipping $C$ and using $\sum w_i^2$ is the $C=I$ special case, not “no risk model.”

Sharpe (up to the irrelevant $\sqrt{\Delta t}$ factor) is the ratio

$$
\mathcal{S} = \mathcal{P} / \mathcal{V}
$$

Numerator over square-root variance. Scale-invariant in $w$ for $w\mapsto k w$ with $k>0$: that is why an extra budget is required. If $\mathcal{V}=0$, Sharpe is undefined — usually a flat or fully hedged numerical degeneracy; do not invert through it.

$\mathcal{S}$ is invariant to scaling $w$ by a positive constant, so the unconstrained maximizer is determined only up to scale. The unique scale used here is the gross budget

$$
\sum_i \lvert w_i\rvert = 1
$$

Unit gross, with $\mathcal{P}>0$ (flip $w$ if the raw solve produces negative expected P&L). Without this rescale, $\lambda$ in the mean-variance form is an arbitrary lever. Dollar holdings are $D_i = I w_i$. If you skip the rescale and ship $C^{-1}E$ raw, the backtest’s “returns” are a numerical accident.

with $\mathcal{P}>0$. Dollar holdings are $D_i = I w_i$.

That is the whole strategy. Everything below is the unconstrained maximizer, the mean-variance form, the dollar-neutral closed form, and when you must abandon the closed form for a QP.

### Worked intuition

Two names, dollar-neutral, $C=I$, forecasts $E=(+3\%,-1\%)$. Closed form collapses to $w \propto E-\bar E = (+2\%,-2\%)$, then rescale to unit gross: $w=(+0.5,-0.5)$. You are long the high forecast, short the low, equal dollars. If instead $E=(+1\%,+1\%)$, the dollar-neutral residual is zero — emit $w=0$, do not invert a zero. If $C$ is singular, `assert_spd` must refuse; “inverting” with a pseudoinverse and calling it max Sharpe is a different, undocumented book.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names after liquidity filters |
| $E_i$ | expected return over the holding horizon |
| $C_{ij}$ | model covariance of returns (PSD, invertible) |
| $w_i$ | portfolio weight; $w_i = D_i / I$ |
| $I$ | gross dollars |
| $D_i$ | signed dollar holdings |
| $\mathcal{P}$ | $E^\top w$ |
| $\mathcal{V}^2$ | $w^\top C w$ |
| $\mathcal{S}$ | $\mathcal{P}/\mathcal{V}$ |
| $\lambda$ | mean-variance risk aversion; also the scale that hits the gross budget |
| $\mu$ | Lagrange multiplier on $\sum_i w_i = 0$ |
| $\mathbf{1}$ | vector of ones |
| $\tau_i$ | linear cost (optional) |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$.

## 4. Mathematics

### 4.1 Unconstrained max Sharpe

Unconstrained max Sharpe (scale-invariant) is

$$
w \propto C^{-1} E
$$

then rescale to $\sum_i \lvert w_i\rvert = 1$ with $\mathcal{P}>0$. If $\mathcal{P}<0$ after the raw solve, flip the sign of $w$ before rescaling.

This is the textbook tangency portfolio when a risk-free asset exists and weights are unconstrained in sign. $C^{-1}$ is why an ill-conditioned $C$ explodes weights. The proportionality is the whole unconstrained answer; the gross rescale is the scale this file chooses. If you skip the invert and set $w\propto E$, you have assumed $C=I$.

### 4.2 Mean-variance form

The same solution without extra constraints is the minimizer of

$$
g(w,\lambda) = \frac{\lambda}{2}\, w^\top C w - E^\top w
$$

Mean-variance utility: penalty on variance minus expected P&L. $\lambda>0$ is risk aversion. This is not a new portfolio; it is the same $C^{-1}E$ family. If bounds exist, this $g$ is what a QP minimizes — then it is no longer unconstrained Sharpe. Skipping the $\lambda/2$ convention and using $\lambda w^\top C w$ only rescales $\lambda$; it does not change the $w$ direction until constraints bind.

The first-order condition is $\lambda C w = E$, hence

$$
w = \frac{1}{\lambda}\, C^{-1} E
$$

Same direction as §4.1. $\lambda>0$ is then fixed by the gross constraint $\sum_i \lvert w_i\rvert = 1$. If $\lambda$ is left as a free “leverage knob” without the gross identity, every reported return is a hidden lever. If $C$ is not SPD, this inverse does not exist; ridge or refuse.

$\lambda>0$ is then fixed by the gross constraint $\sum_i \lvert w_i\rvert = 1$.

### 4.3 Dollar-neutral closed form

Add a Lagrange multiplier $\mu$ on $\sum_i w_i = 0$:

$$
g = \frac{\lambda}{2}\, w^\top C w - E^\top w - \mu\sum_i w_i
$$

Same mean-variance objective plus a dollar-neutrality constraint. $\mu$ is not a trading parameter; it is the multiplier that kills net market dollars. If you add the constraint in words but not in this $g$, the “dollar-neutral” book will still have $\sum w_i \neq 0$.

The stationarity and constraint conditions are

$$
\lambda C w = E + \mu\mathbf{1}
$$

FOC: marginal risk equals forecast plus a constant that enforces neutrality. This is $C w$ parallel to $E$ *shifted* by $\mu$. If $\mu$ is omitted, you are back to unconstrained §4.2.

$$
\sum_i w_i = 0
$$

The constraint itself. Together with the FOC it pins $\mu$. After ADV clips this equality can break; repair it. A cash bucket is allowed; silently dropping shorts is not.

The closed form is

$$
w = \frac{1}{\lambda}\left(
C^{-1}E - \frac{\mathbf{1}^\top C^{-1}E}{\mathbf{1}^\top C^{-1}\mathbf{1}}\, C^{-1}\mathbf{1}
\right)
$$

then set $\lambda$ from $\sum_i \lvert w_i\rvert = 1$. This is $C^{-1}E$ projected orthogonal to $C^{-1}\mathbf{1}$.

Spoken: take unconstrained max-Sharpe, subtract the piece that would have produced net dollars, then rescale. The fraction is the regression of $C^{-1}E$ onto $C^{-1}\mathbf{1}$. If all $E_i$ are equal, the term in parentheses is zero — handle explicitly, emit flat. If $C=I$, this collapses to $w \propto E-\bar E$.

If all $E_i$ are equal, the dollar-neutral solution is $w=0$ (Sharpe undefined). Handle that case explicitly: emit a flat book.

If $C=I$ and the book is dollar-neutral, the closed form collapses to $w \propto E - \bar E$.

### 4.4 Factor covariance and bounds

Sample $C$ is singular or unstable unless $T\gg N$. Use a multifactor model. With a factor model, exact factor neutrality appears in the zero-idiosyncratic-risk limit (the weighted-regression residual of [`063-mean-reversion-weighted-regression.md`](063-mean-reversion-weighted-regression.md)).

If bounds $\lvert w_i\rvert \le w_{\max,i}$ or other inequality constraints exist, the closed form no longer applies. Solve a QP and document that the QP solution is mean-variance with bounds, not unconstrained Sharpe.

Optional linear-cost haircut, applied to the forecast **before** the solve:

$$
E_i^{\mathrm{eff}} = \mathrm{sign}(E_i)\,\max\bigl(\lvert E_i\rvert - \tau_i,\, 0\bigr)
$$

Knock out forecasts smaller than costs, keep the sign of the rest. This is a hack, not a full transaction-cost QP. Applying $\tau$ *after* the solve as a P&L subtract is still required for reported net returns. If you do X = haircut $E$ and then forget to subtract costs in P&L, you have double-counted the idea and under-counted the cash.

### 4.5 Holding-period P&L

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Realized P&L is on $R^{\mathrm{fwd}}$, not on $E$. $E$ is only the solve input. If you do X = report $E^\top w$ as if it were P&L, the backtest lies by construction. Delay-1: $E$ and $C$ known before the fill.

Report net return on gross $I$, annualized Sharpe on **non-overlapping** holding-period returns, and one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

Daily solves can turn over violently if $C$ flickers. If you do X = skip costs on a daily max-Sharpe overlay, the backtest lies in the only place turnover lives.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price and ADV filters. Keep delisted names until the delist date. Borrow available for any name that can be short. This step exists so $C^{-1}E$ is not asked to short unborrowable names. Survivorship in the alpha names makes historical $E$ look too tradable.
2. **Alpha.** Produce $E_i$ from a documented source (cluster residual, momentum, combo, ML). All inputs to $E$ must have timestamp before the fill. The optimizer does not create $E$. Look-ahead in $E$ is look-ahead in $w$.
3. **Covariance.** Build a PSD factor (or statistical) $C$. Assert SPD (or PSD with a documented ridge) before invert. Do not invert a raw $N\times N$ sample covariance when $T\le N$. This step exists because the invert is the strategy; a singular $C$ is not a strategy.
4. **Solve.** If unconstrained (plus optional dollar-neutrality, no bounds): use the closed form. If bounds, costs-as-constraints, or nonlinear constraints exist: QP, and document that Sharpe $\neq$ MV in that case. Silent QP with the closed-form label is a spec bug.
5. **Scale.** Set $\lambda$ (or rescale) so $\sum_i \lvert w_i\rvert = 1$ and $\mathcal{P}>0$. If all $E_i$ equal under dollar-neutrality, return $w=0$. Skipping this scale is hidden leverage. Dividing by zero on constant $E$ is a crash, not a book.
6. **Caps.** Clip versus ADV. After clipping, repair dollar-neutrality; do not silently drop the short side. Caps exist because $C^{-1}$ loves small noisy names.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Cash bucket for lots.
8. **Rebalance.** Daily to weekly. Recompute $E$ and $C$ out of sample. Fitting $C$ on the trade window is look-ahead; this step exists to forbid it.

## 6. Execution protocol

- Recompute $E$ and $C$ out of sample. Fitting $C$ on the same window you forecast $E$ from, then trading that window, is look-ahead. If you do X = estimate $C$ through $t$ and fill at $t$, the backtest lies about a covariance the live book would not have had in full.
- Bound participation vs ADV. If you do X = allow $C^{-1}$ to put $20\%$ of ADV in a residual name, the backtest lies about fills.
- Linear costs: the $E^{\mathrm{eff}}$ haircut is a simple hack, not a full transaction-cost QP. If you do X = haircut and then omit $\tau$ from P&L, net returns are still gross.
- Reimplement the formulas in this file. Do not copy unnamed appendix source.

## 7. Data contract

Required, point-in-time:

- The alpha vector $E_i$ and a written provenance (which spec produced it)
- Factor returns and loadings for $C$, or a statistical PCA model fit on a window that **ends before** the trade
- Split- and dividend-adjusted prices for fills and P&L
- ADV for liquidity filters and impact caps
- Borrow availability and fees for shorts

Not used by this spec unless the **alpha** spec uses them: book value, SUE, earnings timestamps.

No restatement peeking. Delisted names stay until the delist date.

If you do X = fit PCA on the holding window, $C$ looks ahead. If you do X = take $E$ from a model that used $R^{\mathrm{fwd}}$, the optimizer is in-sample. If you do X = use a non-PSD $C$ with a silent pseudoinverse, weights are not the closed form. If you do X = drop names that later delist from $E$, survivorship inflates alpha.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| dollar-neutral | true | closed form in §4.3 |
| $\lambda$ or $I$ | caller-set | scale / gross |
| factor count | caller-set | for model $C$ |
| ADV cap | $1\%$ of ADV | per name; forces QP if treated as a hard bound inside the solve |
| cost $\tau_i$ | 0 | optional haircut on $E$ |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.statistical_arbitrage_optimization` with:

1. `assert_spd(C)` — refuse the invert if $C$ is not SPD (unless a documented ridge is applied first).
2. `optimize(E, C, dollar_neutral=True) -> w` — closed form when unconstrained; $\sum w_i=0$ and $\sum \lvert w_i\rvert=1$ to `1e-8` when dollar-neutral and $E$ is not constant.
3. `optimize_qp(E, C, bounds, ...) -> w` — only if bounds/costs/nonlinear constraints exist; document that this is not unconstrained Sharpe.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Ill-conditioned $C$.** Invert explodes; weights become numerical noise. If you do X = skip `assert_spd` and invert anyway, the backtest lies with a random levered book.
- **Unscaled alpha.** If $E$ is a $z$-score and $C$ is daily variance, $C^{-1}E$ is just inverse-vol on the $z$-score. Match units. If you do X = mix monthly $E$ with daily $C$, the backtest lies about risk.
- **Hidden leverage.** Dropping the $\sum\lvert w\rvert=1$ rescale leaves an arbitrary $\lambda$-scale book. If you do X = report returns on raw $C^{-1}E$, Sharpe is not comparable.
- **Constant $E$.** Dollar-neutral Sharpe is undefined; emit flat, do not invert a zero residual. If you do X = return a tiny numerical $w$ from a near-constant $E$, the backtest lies with noise-as-position.

## 11. Acceptance tests

- If $C=I$ and dollar-neutral, $w \propto E-\bar E$.
- If all $E_i$ equal, dollar-neutral solution is $w=0$ (or undefined Sharpe) — handle explicitly. If the solver returns a huge $w$, the test must fail — that backtest would lie.
- Unconstrained $w$ is parallel to $C^{-1}E$ before the gross rescale.
- `assert_spd` rejects a singular $C$. If a singular $C$ produces weights, the invert is undocumented and the backtest lies.
- After ADV clipping, dollar-neutrality still holds or the cash bucket absorbs the residual.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
