---
rank: 58
slug: bond-value-factor
title: "Bond Value Factor"
asset_class: "fixed income"
style: "cross-sectional value / credit-spread residual"
horizon: "Monthly"
instruments: "government and/or credit bonds; listed bond futures if used"
---

# 058. Bond Value Factor

| Field | Value |
|---|---|
| Popularity rank (this kit) | 58 of 101 |
| Why it sits here | Houweling–van Vundert value: cheap vs a ratings-and-maturity fitted spread. |
| Aliases | credit-spread residual, Houweling value |
| Asset class | fixed income |
| Style | cross-sectional value / credit-spread residual |
| Typical horizon | Monthly |
| Instruments | government and/or credit bonds; listed bond futures if used |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A credit spread that is wide only because the bond is long-dated or low-rated is not cheap. Regress spreads on rating dummies and maturity, take the residual, and call a positive residual (or a log cheapness versus fitted spread) value. Buy the top decile; optionally short the bottom.

Distress names look cheap. Filters and a long-only variant exist for that reason. You are not ranking on frozen-curve carry (file 057) and you are not trading CDS basis (file 059). You are ranking how wide $S_i$ is versus peers of the same rating and maturity.

Typical users are credit-factor books. Horizon is monthly. The cross-sectional regression is re-estimated each rebalance on that date’s panel only. Reusing last month’s $\beta_r$ on this month’s ratings is a frozen-beta variant you must document. Delay-1 fills. Point-in-time ratings: a downgrade known on $t+1$ does not belong in the $t$ dummies.

## 2. First principles

Let $S_i$ be the credit spread of bond $i$ (yield minus a matched Treasury, or OAS). Spread has a mechanical piece from rating and from maturity. Fit

$$
S_i = \sum_{r=1}^{K} \beta_r I_{ir} + \gamma T_i + \varepsilon_i
$$

$I_{ir}$ is a dummy for rating bucket $r$, $T_i$ is maturity, $\varepsilon_i$ is the residual. Each bond sits in one rating bucket: $\sum_r I_{ir}=1$ (intercept absorbed in the dummies). Empty rating columns must be dropped so the dummy matrix has rank. A column with one junk name will overfit $\beta_r$ and call that name fairly priced.

The fitted (fair) spread is the systematic piece

$$
S_i^\ast = S_i - \varepsilon_i
$$

which is $\sum_r \beta_r I_{ir}+\gamma T_i$. If $S_i^\ast\le 0$, the log score is undefined; drop the name. Value is how wide the actual spread is versus that fit:

$$
V_i=\ln(S_i/S_i^\ast)
$$

or the relative residual $V_i=\varepsilon_i/S_i^\ast$. High $V_i$ means cheap versus peers of the same rating and maturity. Select the top decile by $V_i$. A name about to default often has huge $V_i$; that is why a distress cap on raw $S_i$ is recommended.

That is the whole factor. Everything below is the regression hygiene, the book, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_i$ | credit spread or OAS of bond $i$ |
| $I_{ir}$ | dummy, 1 if bond $i$ has rating $r$ |
| $T_i$ | remaining maturity |
| $\beta_r,\gamma$ | fitted rating and maturity loadings |
| $\varepsilon_i$ | residual spread |
| $S_i^\ast$ | fitted spread $S_i-\varepsilon_i$ |
| $V_i$ | value score |
| $K$ | number of rating buckets ($\le 21$) |
| $w_i$ | portfolio weights |
| $I$ | gross dollars (the budget; not the dummy) |
| $P_c$ | dirty price |

Use $I_{\$}$ in code if $I$ as dollars collides with the dummy $I_{ir}$.

## 4. Mathematics

### 4.1 Cross-sectional regression

Each rebalance, on bonds with non-missing ratings and spreads dated $\le t$:

$$
S_i = \sum_{r=1}^{K} \beta_r I_{ir} + \gamma T_i + \varepsilon_i
$$

Drop empty rating columns so the dummy matrix has full column rank. $K\le 21$ rating buckets (AAA through C on a 21-notch list). Imputing missing ratings as AAA parks junk in the wrong dummy and calls it cheap. Then

$$
S_i^\ast = S_i - \varepsilon_i
$$

$S_i^\ast$ is the fitted systematic spread, not a traded instrument. Permuting next month’s ratings cannot change this month’s $\beta_r$.

### 4.2 Value score

$$
V_i=\ln(S_i/S_i^\ast)
$$

or $V_i=\varepsilon_i/S_i^\ast$. Require $S_i^\ast>0$. Select the top decile by $V_i$. Long-only cheap credits, or long cheap / short rich. Log and relative residual are twins of the same identity; pick one per run. Mixing them across months restates ranks.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

$R_i^{\mathrm{fwd}}$ is dirty-price total return including coupon. Duration P&L $\approx -\mathrm{DD}\,\Delta y$. Report return on gross, default counts in the cheap tail, and turnover. A Sharpe that quietly drops defaulted names is survivorship, not this spec.

## 5. Step-by-step algorithm

1. **Universe.** Corporate (or sovereign-spread) bonds with a point-in-time rating and a spread. Drop missing ratings. This step exists so the dummy matrix is defined. Do not impute.
2. **Spreads.** $S_i$ from yields versus a matched Treasury or from OAS, stamps $\le t$. Mixing z-spread and OAS in one cross-section is a units mess; pick one.
3. **Regression.** Estimate $(\beta_r,\gamma)$ on that date’s cross-section only. Drop empty rating columns. Frozen-beta from last month is a documented variant, not the default.
4. **Score.** $V_i=\ln(S_i/S_i^\ast)$ or $\varepsilon_i/S_i^\ast$. Drop $S_i^\ast\le 0$.
5. **Book.** Top decile long; optional bottom decile short. Equal-weight or duration-weight. Duration-weighting reduces the residual rates bet.
6. **Distress filter (recommended).** Cap or drop the widest raw $S_i$ names so $V_i$ is not a default lottery. Turning this off must be explicit.
7. **Blotter.** Face amounts, round, emit intents. Do not route live orders. Cheap high-$V$ bonds are often off-the-run; cap by issue size.
8. **Rebalance.** Monthly. Delay-1. Daily regression on noisy OAS will churn names without new rating information.

## 6. Execution protocol

- Cross-sectional regression each rebalance. Do not reuse last month’s $\beta_r$ on this month’s ratings unless you document a frozen-beta variant.
- Drop missing ratings; do not impute AAA.
- Liquidity: cheap high-$V$ bonds are often off-the-run. Cap by issue size.

## 7. Data contract

Required, point-in-time:

- Clean/dirty prices, yields or OAS, durations
- Point-in-time credit ratings (issuer or issue)
- Remaining maturity $T_i$
- Matched Treasury curve if $S_i$ is a yield spread

Not used by this spec: frozen-curve carry $C$ as the signal (that is 057), equity book value, earnings, SUE.

No restatement of ratings after $t$. A downgrade known on $t+1$ does not belong in the $t$ dummies. Agency restatements and issuer-versus-issue rating mismatches must be frozen as of $t$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| sort | top decile | long-only or long/short |
| ratings | AAA…C, 21 notches | $K\le 21$, no empty columns |
| $V_i$ | $\ln(S_i/S_i^\ast)$ | or $\varepsilon_i/S_i^\ast$ |
| distress cap | on | drop extreme raw $S_i$ |
| rebalance | monthly | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.bond_value_factor` with:

1. `fit_spreads(S, ratings, T) -> dict` — $\beta_r,\gamma,\varepsilon_i,S_i^\ast$ on date $t$ only.
2. `value(S, S_star) -> pd.Series` — $V_i$, defined only for $S^\ast>0$.
3. `weights(V, I, long_only=True) -> pd.Series` — decile book, constraints to `1e-8`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — face, never live routing.
5. `pnl(D, forward_returns, costs) -> float` — matches the P&L identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Distress.** Names about to default look cheap on $V_i$. The distress cap is how you stop the factor from being a default lottery. Turning it off because it “hurts backtest Sharpe” is a different spec.
- **Rating lag.** Agency ratings move after spreads. $V_i$ will look cheap on names the market has already downgraded in price.
- **Illiquidity.** High-$V$ bonds may not trade at the model price. Screen OAS is not a fill.
- **Empty buckets.** A dummy column with one junk name overfits $\beta_r$. Drop empty columns; do not regularize in silence unless documented.
- **Look-ahead ratings.** Using the terminal rating path in every month’s dummies is not point-in-time.
- **Mixing carry.** Residualizing $S_i$ and then ranking on $C$ is two factors; this file is $V_i$ only.

## 11. Acceptance tests

- Toy: two ratings, same $T$, $S$ higher in one name → that name has $\varepsilon>0$ and higher $V$.
- $\sum_r I_{ir}=1$ for every row; empty rating columns are dropped before the fit.
- $S_i^\ast=S_i-\varepsilon_i$ to `1e-8`.
- Permuting next month’s ratings and spreads must not change $V_t$.
- Adding linear costs $\tau$ weakly decreases P&L.
- $S_i^\ast\le 0$ names are absent from $V$, not logged as $-\infty$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
