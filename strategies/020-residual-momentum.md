---
rank: 20
slug: residual-momentum
title: "Residual Momentum"
asset_class: "equities"
style: "factor-neutral momentum"
horizon: "36m regression to estimate betas; 12m formation on residuals with 1m skip; hold 1m (can be longer)."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 020. Residual Momentum

| Field | Value |
|---|---|
| Popularity rank (this kit) | 20 of 101 |
| Why it sits here | Momentum that is not just market/size/value beta. Same 12-1 geometry as price momentum, built on factor residuals. |
| Aliases | factor-neutral momentum, FF3 residual momentum |
| Asset class | equities |
| Style | factor-neutral momentum |
| Typical horizon | 36m regression to estimate betas; 12m formation on residuals with 1m skip; hold 1m (can be longer). |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Same as price momentum, but on residuals of returns against Fama–French MKT, SMB, HML. Estimate betas **with** an intercept on a 36-month window. Form residual returns **without** that intercept on a 12-month window with a 1-month skip. Long the top decile of risk-adjusted residual means, short the bottom.

You are betting that residual (idiosyncratic) continuation exists after stripping market, size, and value betas. You are not betting that high-beta names keep outperforming because the market did, and you are not sorting on $\alpha$ from the 36-month fit. Subtracting $\alpha$ on the formation window is the most common spec error: it mixes a slow mean into a momentum score.

You are also not running FF5 residual momentum unless you change the factor set and document it. FF3 vs FF5 is a different residual. Typical user: a quant equity book that already has 12-1 and wants a factor-neutral twin. Horizon intuition: 36 months to estimate loadings (slow), 12-1 on residuals (same as price momentum), hold 1 month. The skip still exists; residual momentum crashes too, just with less raw-market beta in the crash.

If you fit betas on a window that includes the hold, use total returns against excess factors, or include month 0 in formation, the backtest is not this spec.

## 2. First principles

Write excess stock returns as a three-factor linear model plus a residual:

$$
R_i(t) = \alpha_i + \beta_{1,i}\,\mathrm{MKT}(t) + \beta_{2,i}\,\mathrm{SMB}(t) + \beta_{3,i}\,\mathrm{HML}(t) + \epsilon_i(t)
$$

This is the estimation model on the 36-month window. $R_i(t)$ must be excess versus the same risk-free rate the factor files use. $\alpha_i$ is kept in the *fit* so the betas are not forced through the origin; it is not kept in the *formation* residual. If you drop the intercept in the 36-month OLS, you get different $\beta$s. If you use total returns against excess MKT, the residual absorbs the missing $r_f$ and is misspecified.

$R_i(t)$ is the excess return versus the same risk-free rate the factor files use. $\alpha_i$ is a 36-month intercept. The $\beta$s are the factor loadings.

Price momentum on raw $R_i$ mixes continuation of $\beta'\mathrm{factor}$ with continuation of $\epsilon_i$. Residual momentum keeps only the second piece. After the betas are fit, **drop $\alpha_i$** when forming the residual used for ranking:

$$
\epsilon_i(t) = R_i(t) - \beta_{1,i}\,\mathrm{MKT}(t) - \beta_{2,i}\,\mathrm{SMB}(t) - \beta_{3,i}\,\mathrm{HML}(t)
$$

No $\alpha_i$ on the right-hand side. That is deliberate. $\alpha_i$ was estimated on 36 months; subtracting it on the 12-month formation window would mix a slow mean into a momentum score. These $\epsilon_i(t)$ are therefore not the OLS residuals from the 36-month regression restricted to the 12-month slice, unless $\alpha_i=0$. If your formation residual equals the 36-month OLS residual on that slice and $\alpha\neq 0$, the spec is wrong.

$\alpha_i$ was estimated on 36 months; subtracting it on the 12-month formation window would mix a slow mean into a momentum score. The continuation hypothesis is then the same as price momentum, on $\epsilon$ rather than $R$:

$$
\mathbb{E}\bigl[\epsilon_{i,t+H} \bigm| \epsilon_i^{\mathrm{mean}}\bigr] \approx \lambda\, \epsilon_i^{\mathrm{mean}}, \qquad \lambda > 0
$$

Same $\lambda>0$ continuation story as 12-1, now on residual means. You still skip the most recent month. You still hold about a month. The object is not “alpha is positive”; it is “the trailing residual mean continues.” Fitting $\lambda$ on the same hold you trade is look-ahead.

That is the whole strategy. Everything below is the two-window construction, the skip, and the risk-adjusted sort.

### Worked intuition

Name BetaOne is exactly $\beta_{\mathrm{MKT}}=1$, $\beta_{\mathrm{SMB}}=\beta_{\mathrm{HML}}=0$. Its excess return is MKT plus a residual. After subtracting MKT (and not subtracting $\alpha$), residual momentum on this name *is* excess-return momentum of $R-\mathrm{MKT}$. If the name also has $\alpha=+0.5\%$ per month from the 36-month fit, you still do **not** subtract that $0.5\%$ when averaging the 12-1 residuals — otherwise a slow outperformer looks like residual momentum even when the last year’s residual mean was zero. Three names with residual means $+2\%$, $0\%$, $-2\%$ over the skipped year rank long, flat, short on the risk-adjusted score if vols are equal.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the tradable universe after liquidity filters |
| $R_i(t)$ | excess simple return vs the factor-file risk-free rate |
| $\mathrm{MKT},\,\mathrm{SMB},\,\mathrm{HML}$ | Fama–French factors, excess returns, calendar-aligned |
| $\alpha_i,\,\beta_{1,i},\,\beta_{2,i},\,\beta_{3,i}$ | intercept and betas from the 36-month estimation window |
| $\epsilon_i(t)$ | formation residual, intercept **not** subtracted |
| $S$ | skip months (usually 1) |
| $T$ | formation months (usually 12) |
| $\epsilon_i^{\mathrm{mean}}$ | mean residual on the formation window |
| $\sigma_i^2$ | sample variance of formation residuals |
| $R_i^{\mathrm{risk.adj}}$ | $\epsilon_i^{\mathrm{mean}} / \sigma_i$ |
| $w_i$ | portfolio weight (positive = long) |
| $I$ | gross dollars |
| $D_i = I w_i$ | signed dollar holdings |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$.

## 4. Mathematics

### 4.1 Beta estimation

On a 36-month window that **ends before** the formation window (and before the fill), estimate

$$
R_i(t)=\alpha_i+\beta_{1,i}\mathrm{MKT}(t)+\beta_{2,i}\mathrm{SMB}(t)+\beta_{3,i}\mathrm{HML}(t)+\epsilon_i(t)
$$

OLS with intercept, point-in-time factor files, excess $R_i$. The window must not include the holding period and should not include the 12-1 formation months you will rank on (it ends before that region). Rolling 36-month betas; a full-sample beta that uses 2020 data to rank 2015 is look-ahead. Keep $\alpha_i$ from this fit only as a diagnostic; do not feed it into §4.2.

Use point-in-time factor files. $R_i$ must be excess returns. Rolling 36-month betas; do not use a beta fit that includes the holding period.

### 4.2 Formation residuals

On 12 months with a 1-month skip, drop $\alpha_i$ and form

$$
\epsilon_i(t)=R_i(t)-\beta_{1,i}\mathrm{MKT}(t)-\beta_{2,i}\mathrm{SMB}(t)-\beta_{3,i}\mathrm{HML}(t)
$$

Betas from §4.1, residual without intercept, time index matching price momentum: $t=0$ most recent, skip $S=1$, formation length $T=12$. Month $t=0$ must not enter $\epsilon$ used for the rank. If you subtract $\alpha_i$ here, formation residuals become OLS residuals and the sort is no longer residual *momentum*.

Time index matches price momentum: $t=0$ most recent, skip $S=1$, formation length $T=12$.

### 4.3 Risk-adjusted residual score

The mean residual on the formation window is

$$
\epsilon_i^{\mathrm{mean}}=\frac{1}{T}\sum_{t=S}^{S+T-1}\epsilon_i(t)
$$

Average residual over the skipped year. This is the numerator of the sort. Starting at $t=S$ is the skip. Using $t=0$ in the sum mixes one-month residual reversal into residual momentum.

The sample variance of those residuals is

$$
\sigma_i^2=\frac{1}{T-1}\sum_{t=S}^{S+T-1}\bigl(\epsilon_i(t)-\epsilon_i^{\mathrm{mean}}\bigr)^2
$$

Formation residual vol, so a noisy residual winner does not dominate a steady one. $\sigma_i=0$ → drop, do not emit infinite score. This $\sigma$ is residual vol, not total vol; using total vol would re-import factor vol into the ranking.

The sort key is

$$
R_i^{\mathrm{risk.adj}}=\frac{\epsilon_i^{\mathrm{mean}}}{\sigma_i}
$$

Residual mean per unit residual vol. Long the top decile, short the bottom. This is not $R^{\mathrm{cum}}$ from the price-momentum file; it is the risk-adjusted residual analogue. Default $S=1$, $T=12$.

with $S=1$, $T=12$. Long the top decile of $R_i^{\mathrm{risk.adj}}$, short the bottom.

### 4.4 Weights and P&L

Modulus-uniform dollar-neutral, with $N_L$ longs and $N_S$ shorts:

$$
w_i = \frac{1}{2 N_L}\quad\text{on the longs},\qquad w_i = -\frac{1}{2 N_S}\quad\text{on the shorts}
$$

Half gross in residual winners, half in residual losers. After borrow drops, rebuild the loser leg so $\sum w_i=0$ still holds. Skipping the $1/2$ breaks unit-gross neutrality.

Let $R_i^{\mathrm{fwd}}$ be the simple excess or total return from fill to next rebalance, including dividends, used consistently. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Mark the signed book through the hold. Be consistent: excess vs excess, or total vs total. Mixing total $R^{\mathrm{fwd}}$ with excess formation $R_i$ is acceptable for P&L *reporting* if documented; mixing total $R_i$ with excess factors in the *fit* is not. If you do X = fill on month 0’s close that entered skipped residuals, the skip is broken.

Report net return on gross $I$, annualized Sharpe on **non-overlapping** holding-period returns, and one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

Same one-way definition as price momentum. Residual momentum still turns over; it is not value. Overlapping holds inflate Sharpe if you treat them as independent. If you do X = report overlapping 6-month residual holds as 6 independent months, the backtest lies.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price and ADV filters. Keep delisted names until the delist date. Borrow available for shorts. Survivorship in losers is especially dangerous in momentum crashes. This step exists so the residual sort is tradable.
2. **Factors.** Align Fama–French MKT, SMB, HML with calendar time. Convert stock returns to excess returns vs the same risk-free rate. Calendar mismatch (June factor vs May stock) manufactures residuals. Total returns vs excess factors are a specification error.
3. **Betas.** Rolling 36-month OLS **with intercept**, window ending before the skip/formation region used for ranking. The intercept belongs in the fit so $\beta$s are not through-origin. The window must not include the hold.
4. **Residuals.** On the 12-month formation window with 1-month skip, compute $\epsilon_i(t)$ **without** subtracting $\alpha_i$. This is the load-bearing minus-alpha rule. Including $\alpha$ is the usual bug.
5. **Score.** $\epsilon^{\mathrm{mean}}$, $\sigma$, $R^{\mathrm{risk.adj}}$. Drop names with missing factors or $\sigma_i=0$. Missing factor months are not zero; they are missing.
6. **Rank.** Long top decile, short bottom decile. Enforce dollar-neutrality. Ranking residual scores is what makes this momentum rather than a beta-hedged index.
7. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV. Repair the budget; do not silently drop the short leg. Residual losers can be small; dropping them leaves residual-long factor bets.
8. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Rebalance monthly. Delay-1 fill. Month-0 close is not the fill if it sat in the skip/formation discussion as $t=0$ data.

## 6. Execution protocol

- Monthly rebalance. Residual momentum still crashes, but the factor strip removes some of the raw-momentum beta bet. If you do X = drop crash months from the sample, the backtest lies about the left tail.
- Do **not** subtract $\alpha$ in the formation residual. If you do X = use OLS residuals from the 36-month fit as the 12-1 score, the backtest lies by mixing slow $\alpha$ into momentum.
- $R_i$ must be excess returns. Using total returns against excess factors is a specification error. If you do X = feed raw total returns into the OLS, betas and residuals are both wrong.
- If a name cannot be shorted, drop it and rebuild the loser leg. If you do X = keep residual-winner longs and skip loser shorts, the backtest lies about factor neutrality of the *book* even if residuals were factor-neutral.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted prices (or excess returns already built from them)
- Risk-free rate matching the factor files
- Fama–French factor files aligned in calendar time (MKT, SMB, HML)
- ADV for liquidity filters and impact caps
- Borrow availability and fees for shorts

Not used by this spec: book value as a sort key, SUE, earnings timestamps, industry map. HML is a factor return series, not a name-level B/P screen.

No restatement peeking. Delisted names stay in the estimation and formation samples until the delist date.

If you do X = use revised factor files that rewrite 2010 MKT after the fact, historical residuals move. If you do X = fit 36-month betas on a sample that includes the hold, $\beta$ looks ahead. If you do X = drop names that later delist from the 36-month window, the backtest lies through survivorship.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| beta window | 36 months | OLS with intercept |
| formation $T$ | 12 months | on residuals |
| skip $S$ | 1 month | same as price momentum |
| hold $H$ | 1 month | can be longer |
| sort key | $R^{\mathrm{risk.adj}}$ | residual mean / residual $\sigma$ |
| factors | FF3 | FF5 is a different spec |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.residual_momentum` with:

1. `fit_betas(excess_returns, factors, window=36) -> (alpha, betas)` — intercept kept for the fit, not for formation residuals.
2. `formation_residual(excess_returns, factors, betas, skip_months, formation_months) -> pd.Series` — does **not** subtract $\alpha$.
3. `weights(risk_adj, mode) -> pd.Series` — budget identities to `1e-8`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.

$R_i$ must be excess returns. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Factor mismatch.** FF5 vs FF3 is a different residual. Mixing definitions silently is a bug. If you do X = swap HML for RMW/CMA mid-sample, the backtest lies about a single residual series.
- **Beta instability.** 36-month loadings move; a name can look like residual momentum because $\beta$ is stale. If you do X = freeze betas from a 5-year full sample, you have a different spec.
- **Momentum crash.** The residual book can still crash after a rebound. If you do X = report only long residual-winners, the backtest lies about the short-leg bounce.
- **Subtracting $\alpha$.** Including the intercept in the formation residual is the most common spec error. If you do X = pass OLS residuals into the rank, the backtest lies by design of this file.

## 11. Acceptance tests

- If a stock is exactly $\beta=1$ on MKT and $0$ on SMB/HML, residual momentum equals excess-return momentum after subtracting MKT (and still without subtracting $\alpha$).
- Formation residuals must **not** equal OLS residuals from the 36-month fit on that same 12-month slice if $\alpha\neq 0$. If they are equal, $\alpha$ was subtracted and the backtest lies about residual momentum.
- Skip window: ranks at month-end $t$ must not use month $t$ residuals.
- Weights satisfy dollar-neutrality to `1e-8`.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
