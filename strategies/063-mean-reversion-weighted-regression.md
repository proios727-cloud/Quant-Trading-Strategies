---
rank: 63
slug: mean-reversion-weighted-regression
title: "Mean-Reversion — Weighted Regression"
asset_class: "equities"
style: "factor-neutral reversal"
horizon: "Daily/intraday."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 063. Mean-Reversion — Weighted Regression

| Field | Value |
|---|---|
| Popularity rank (this kit) | 63 of 101 |
| Why it sits here | The general residual: fade returns orthogonal to an arbitrary loadings matrix (industries + styles), with weights $z_i=1/\sigma_i^2$. |
| Aliases | WLS residual fade, factor-neutral reversal |
| Asset class | equities |
| Style | factor-neutral reversal |
| Typical horizon | Daily/intraday. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Orthogonality $\sum_i \tilde R_i \Omega_{iA}=0$ for a general loading matrix $\Omega$, not only industry dummies. Weighted least squares with $z_i=1/\sigma_i^2$ is the usual weight. Dummy $\Omega$ and $z_i=1$ recover [`062-mean-reversion-multiple-clusters.md`](062-mean-reversion-multiple-clusters.md).

You are betting that whatever is left after stripping an arbitrary factor span (industries and/or styles) still mean-reverts, and that noisy names should vote less in the fit via $z_i=1/\sigma_i^2$. You are not betting on those factors. You are not running PCA factors fit on the same window you trade.

You are also not claiming more columns in $\Omega$ is always better: over-hedging makes $\varepsilon\approx 0$ and the book noise. Typical user: a production stat-arb desk that outgrew dummy industries and wants factor-neutral fade. Horizon intuition: daily or intraday formation like 014/062; $\Omega$ itself is GICS-slow plus optional style snapshots dated $\le t_1$.

If you use tomorrow’s industry, in-sample PCA columns, or skip the intercept when you wanted dollar-neutrality, the residual is a different object and the backtest lies about this spec.

## 2. First principles

Formation returns are a linear factor model with a general loading matrix (binary industries and/or non-binary styles):

$$
R = \Omega f + \varepsilon
$$

Same stacked story as 062, but $\Omega_{iA}$ need not be $0/1$. Style columns (beta, size, residual vol, …) are allowed if dated $\le t_1$. Sample PCA columns fit on the trade window are refused: those factors *are* the residual window. $f$ is not traded; $\varepsilon$ is.

$\Omega_{iA}$ need not be $0/1$. Weighted least squares with weights $z_i>0$ and $Z=\mathrm{diag}(z_i)$ is the minimizer of $(R-\Omega f)^\top Z (R-\Omega f)$. The fitted residual is

$$
\varepsilon = R - \Omega(\Omega^\top Z \Omega)^{-1} \Omega^\top Z R
$$

WLS residual: returns minus fitted factor piece, with noisy names down-weighted in the *fit*. If $Z=I$ and $\Omega$ is dummies, this is cluster demeaning. If $\Omega^\top Z \Omega$ is singular, too many columns or collinear styles — drop columns or ridge; do not pseudoinverse silently. This $\varepsilon$ is not yet the traded vector.

The traded residual in this spec is the **weighted** residual

$$
\tilde R = Z\varepsilon
$$

Multiply by $Z$ so the book that holds $D_i\propto-\tilde R_i$ is orthogonal to $\Omega$ in the weighted metric: $\Omega^\top\tilde R=0$. If you fade $\varepsilon$ instead of $Z\varepsilon$, neutrality $\Omega^\top D=0$ fails when $z_i$ varies. Typical $z_i=1/\sigma_i^2$ therefore both down-weights noisy names in the fit *and* in the traded residual.

By construction $\Omega^\top \tilde R = 0$: the book that holds $D_i \propto -\tilde R_i$ is factor-neutral in the $\Omega$ metric. If $\Omega$ contains an intercept (or columns that span $\mathbf{1}$), then $\sum_i \tilde R_i = 0$ as well (dollar-neutrality). Typical $z_i=1/\sigma_i^2$ down-weights noisy names before the fade.

Mean-reversion is again $\mathbb{E}[\varepsilon_{i,t+1}\mid\varepsilon_{i,t}]\approx -\lambda\varepsilon_{i,t}$. You fade what is left after stripping $\Omega$.

That is the whole strategy. Everything below is the WLS algebra, the weight schemes, and how not to fit $\Omega$ on the window you trade.

### Worked intuition

Industries plus an intercept, $z_i=1$: $\tilde R$ equals 062’s cluster residual and sums to zero. Turn on $z_i=1/\sigma_i^2$: a noisy name votes less when estimating industry $f_A$, and its traded $|D_i|$ is smaller for the same raw residual. Add a style column “market beta.” The fade is then orthogonal to beta as well — you are no longer accidentally long high-beta residuals. If you then add ten more style columns estimated on the same 5-day window, $\varepsilon$ collapses toward zero and the book is noise. That is over-hedging, not a better hedge.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names after liquidity filters |
| $A$ | factor index (industries and/or styles) |
| $\Omega_{iA}$ | loading of name $i$ on factor $A$ |
| $z_i>0$ | regression weight |
| $Z$ | $\mathrm{diag}(z_i)$ |
| $R_i$ | formation return |
| $\varepsilon$ | WLS residual $R-\Omega\hat f$ |
| $\tilde R = Z\varepsilon$ | traded residual |
| $\sigma_i$ | trailing vol, used if $z_i=1/\sigma_i^2$ |
| $D_i$ | signed dollar holdings |
| $I$ | gross dollars |
| $\gamma$ | scale $D_i=-\gamma\tilde R_i$ |

## 4. Mathematics

### 4.1 Weighted residual

The WLS residual and the traded residual are

$$
\varepsilon = R - \Omega(\Omega^\top Z \Omega)^{-1} \Omega^\top Z R
$$

Fitted residual after WLS. $\sigma_i$ used in $z_i$ must be estimated on a window that ends *before* formation, or vol looks ahead. Drop names with missing $R_i$ or $z_i$ and rebuild $\Omega$ on survivors; a NaN in one name poisons $\hat f$.

$$
\tilde R = Z\varepsilon
$$

Traded residual. Fade this, not raw $\varepsilon$, if you want $\Omega^\top D=0$. When $Z=I$, $\tilde R=\varepsilon$. When $z_i=1/\sigma_i^2$, noisy names shrink in the book.

Orthogonality to the loadings:

$$
\Omega^\top \tilde R = 0
$$

The acceptance identity. After ADV clips it can break; repair $\Omega^\top D=0$ or cash-bucket. If this fails before clips, `weighted_residual` is wrong. Silent repair by dropping shorts is not allowed.

If $\Omega$ contains an intercept (or columns that span $\mathbf{1}$), then

$$
\sum_i \tilde R_i = 0
$$

Dollar-neutrality of $\tilde R$, hence of $D_i=-\gamma\tilde R_i$ before clips. If you omit the intercept and still claim $\sum D_i=0$, the backtest lies about neutrality. Dummy industries that already span $\mathbf{1}$ (rows sum to one) already contain the intercept — do not add another ones column.

Typical weight:

$$
z_i = \frac{1}{\sigma_i^2}
$$

Inverse-variance: default scheme `inv_var`. $\sigma_i=0$ is refused (infinite $z$). Other documented schemes: $z_i=1/\sigma_i$ (inv-vol) or $z_i=1$ (equal). Switching scheme changes both the fit and the traded residual; it is not a P&L cosmetic.

Other documented schemes: $z_i=1/\sigma_i$ (inv-vol) or $z_i=1$ (equal).

### 4.2 Dollar holdings

Fade the traded residual:

$$
D_i = -\gamma \tilde R_i
$$

Minus sign is the fade. $\gamma$ from $\sum_i\lvert D_i\rvert=I$. If the intercept is in $\Omega$, $\sum_i D_i=0$ automatically before clipping. Dropping the minus is cluster-neutral *momentum*, a different spec.

with $\gamma$ from the gross budget $\sum_i \lvert D_i\rvert = I$. If the intercept is in $\Omega$, $\sum_i D_i=0$ automatically before clipping.

Formation window, delay, and P&L match the single-cluster spec.

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Mark through the hold. Delay-1 fill. If you do X = fit $\Omega$ or $Z$ on a window that includes $R^{\mathrm{fwd}}$, both the hedge and the vol weights look ahead and the backtest lies.

### 4.3 Special cases

Binary $\Omega$ (industry dummies) and $z_i=1$ → identical to multiple-cluster OLS. One dummy column and $z_i=1$ → identical to single-cluster demeaning.

Those identities are the regression tests: 063 must reproduce 062 and 014 on those fixtures. If it does not, the WLS path is wrong even if `Omega.T @ tilde_R` is numerically small.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price and ADV filters, borrow for shorts. Keep delisted names until the delist date. Survivorship still paints residual shorts too kind. This step exists so $\Omega$ is estimated on tradable names.
2. **Loadings.** Build $\Omega$ point-in-time: GICS dummies plus optional style columns. Do not use sample PCA columns that were fit on the same residual window you trade (in-sample factors). This step exists because in-sample $\Omega$ *is* the residual.
3. **Weights.** Choose `{inv_var, inv_vol, equal}`. Estimate $\sigma_i$ on a window that ends before formation if $z$ needs it. Vol from the hold would look ahead.
4. **Residual.** `weighted_residual(R, Omega, z)`. Drop names with missing $R_i$ or $z_i$; rebuild $\Omega$ on the survivors. Rebuild exists so $\Omega^\top\tilde R=0$ still holds on the traded set.
5. **Size.** $D_i=-\gamma\tilde R_i$ with $\gamma$ from gross $I$. Optional extra vol control is already in $Z$ if `inv_var` is on. Double-shrinking by another $1/\sigma$ without documenting it changes the spec.
6. **Caps.** ADV clip. Repair $\Omega^\top D = 0$ (or cash-bucket the residual). Do not silently drop shorts. Neutrality after clips is the live identity, not only the pre-clip algebra.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Cash bucket for lots.
8. **Rebalance.** Daily or intraday. $\Omega$ on a slower clock if it is GICS; faster if it is a style snapshot dated $\le t_1$. A style snapshot dated $t_2$ is look-ahead.

## 6. Execution protocol

- Same delay-1 fill as the single-cluster spec. If you do X = fill at $t_2$, the backtest lies by trading the print that entered $R$.
- Do not use sample PCA columns fitted on the residual window you trade. If you do X = that, factors are in-sample and the residual is not a fade of a pre-specified span.
- If a name cannot be shorted, drop it and rebuild the WLS residual on the remainder. If you do X = keep longs and skip shorts, $\Omega^\top D\neq 0$ and the backtest lies about factor neutrality.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted prices on the formation and holding windows
- Loadings $\Omega$ dated $\le t_1$ (industry map and/or style exposures)
- Vols for $z_i$ if the weight scheme is `inv_var` or `inv_vol`
- ADV for liquidity filters and impact caps
- Borrow availability and fees for shorts

Not used by this spec: book value as a sort key, SUE, earnings timestamps — unless they enter a style column of $\Omega$, in which case that column’s own point-in-time rule applies.

No restatement peeking. Delisted names stay until the delist date.

If you do X = use GICS dated after $t_1$, taxonomy look-ahead. If you do X = estimate $\sigma_i$ through the hold, $Z$ looks ahead. If you do X = restated style betas from a later model vintage, $\Omega$ is not point-in-time.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| weight scheme | `inv_var` | `{inv_var, inv_vol, equal}` |
| factor set | GICS dummies + intercept | styles optional |
| formation window | 1–5 days | |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.mean_reversion_weighted_regression` with:

1. `weighted_residual(R, Omega, z) -> tilde_R` — assert `Omega.T @ tilde_R == 0` within tolerance.
2. `weights(tilde_R, I) -> pd.Series` — $D_i=-\gamma\tilde R_i$, gross $I$.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.
4. `pnl(D, forward_returns, costs) -> float`.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Over-hedging.** Too many columns in $\Omega$ makes $\varepsilon\approx 0$ and the book noise. If you do X = add factors until in-sample $R^2\approx 1$, the backtest lies by trading residual noise.
- **Unstable style loadings.** Non-dummy columns estimated in-sample are a different, invalid residual. If you do X = regress 5-day returns on 5-day PCA, $\Omega$ is the window you fade.
- **Tomorrow’s industry.** Using a GICS assignment dated after $t_1$ is look-ahead. If you do X = that, the backtest lies by regrouping.

## 11. Acceptance tests

- Binary $\Omega$, $z=1$ → matches the multiple-cluster spec.
- Include intercept → `sum(tilde_R)==0`.
- `Omega.T @ tilde_R == 0` within tolerance. If a fixture fails this, weights are not factor-neutral and a neutrality backtest lies.
- PCA columns fit on the trade window must be refused (or flagged) if that path exists. If they are accepted silently, the residual is in-sample.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
