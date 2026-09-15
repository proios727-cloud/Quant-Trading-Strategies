---
rank: 80
slug: etf-alpha-rotation
title: "ETF Alpha Rotation"
asset_class: "ETFs"
style: "Jensen alpha ranking of ETFs"
horizon: "~1 year estimation; monthly hold"
instruments: "listed ETFs (equity sector, country, or index)"
---

# 080. ETF Alpha Rotation

| Field | Value |
|---|---|
| Popularity rank (this kit) | 80 of 101 |
| Why it sits here | Rotate into ETFs with high intercept vs Fama–French factors — a simple active-share / residual-return screen used on funds and ETFs. |
| Aliases | Jensen-alpha rotation, FF intercept rank |
| Asset class | ETFs |
| Style | Jensen alpha ranking of ETFs |
| Typical horizon | ~1 year estimation; monthly hold |
| Instruments | listed ETFs (equity sector, country, or index) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Replace raw cumulative return in sector rotation by Jensen’s $\alpha_i$ from a time-series regression on MKT, SMB, and HML. Buy high $\alpha_i$, sell low $\alpha_i$ (or long-only the top decile).

You are betting that leftover return after Fama–French exposure continues for the next month: ETFs with a high trailing intercept keep delivering residual return relative to peers. The sort key is $\hat\alpha_i$, not $R^{\mathrm{cum}}$. A high-beta sector can rank low if its leftover is negative; a lower-beta name can rank high if it beat its betas.

You are not ranking raw momentum (`028`). You are not treating a significant $t$-stat as a trading licence. You are not claiming $\alpha$ is what you *earn* next month — you earn the raw ETF path minus costs. You are not using restated French-library factors that were revised after $t_2$. You are not adding book-to-price as an extra signal; that would double-count HML.

Typical users are fund-rotation and “smart beta residual” sleeves. Estimation is about one year of daily excess returns, hold one month, delay-1. One year of daily data on a sector ETF still leaves $\alpha$ absorbing beta error. Costs and turnover can erase the intercept. Full-sample $\alpha$ fitted through the whole backtest is look-ahead.

## 2. First principles

A factor model says the expected excess return of ETF $i$ is spanned by betas:

$$
\mathbb{E}[R_i^e] = \beta_{1,i}\,\mathbb{E}[\mathrm{MKT}] + \beta_{2,i}\,\mathbb{E}[\mathrm{SMB}] + \beta_{3,i}\,\mathbb{E}[\mathrm{HML}]
$$

If this spanning is correct, there is nothing left to rank. The intercept $\alpha_i$ is the leftover. If the model is the right risk adjustment, $\alpha_i$ is either compensation for missing factors or a mispricing. This spec treats $\alpha_i$ as a **sort key**, the same way `028` treats $R^{\mathrm{cum}}_i$. It does not claim $\alpha$ is tradable after costs, and it does not treat a significant $t$-stat as a trading licence.

Estimation is a trailing window that **ends before** the fill. Betas fitted through $t+1$ are look-ahead. If you do $X$ = run one OLS on the entire sample and reuse $\hat\alpha_i$ every month, every date has seen the future.

That is the whole strategy. Everything below is the regression, the rank book, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $R_i(t)$ | ETF simple return on the estimation bar (daily or weekly) |
| $R_i^e(t)$ | excess return vs the same risk-free series as the factors |
| $\mathrm{MKT},\mathrm{SMB},\mathrm{HML}$ | Fama–French factors, point-in-time |
| $\alpha_i$ | OLS intercept |
| $\beta_{1,i},\beta_{2,i},\beta_{3,i}$ | OLS slopes |
| $\varepsilon_i(t)$ | residual |
| $w_i$ | portfolio weight |
| $I$ | gross dollars |

Carhart MOM is an optional fourth factor, off by default.

## 4. Mathematics

### 4.1 Time-series regression

On a window of $W$ observations ending at $t_2<t_{\mathrm{fill}}$ (default $W=252$ daily), using excess ETF returns versus the same RF as the factors:

$$
R_i(t) = \alpha_i + \beta_{1,i}\,\mathrm{MKT}(t) + \beta_{2,i}\,\mathrm{SMB}(t) + \beta_{3,i}\,\mathrm{HML}(t) + \varepsilon_i(t)
$$

OLS, no shrinkage. The left-hand side must be aligned with the factor dates. If $R_i$ on the left is already excess, the equation is the same with $R_i^e$ on the left. Pick one and document it. Default: excess on both sides. Mixing raw $R_i$ on the left with excess factors on the right dumps RF into $\alpha$.

No overlapping “current” factors that were revised later. French’s library revisions after $t_2$ do not enter the $t_2$ regression. If you do $X$ = download today’s Ken French CSV and overwrite 2018 SMB, the 2018 $\hat\alpha$ was not live.

Optional Carhart: add $\beta_{4,i}\,\mathrm{MOM}(t)$. MOM on by default would change ranks versus this file’s default three-factor intercept.

### 4.2 Rank book

Sort on $\hat\alpha_i$. Long-only: top decile (or top $k$), equal weight. Dollar-neutral: top vs bottom decile, each leg gross $1/2$. Uniform within legs, or $\propto 1/\sigma(\varepsilon_i)$ if you want residual-vol weights.

$\alpha_i$ replaces $R^{\mathrm{cum}}_i$ as the sort key. Portfolio algebra is otherwise `028`. Names with fewer than $W_{\min}$ observations are dropped, not given $\alpha=0$. A zero intercept fill would dump thin histories into the middle or the bottom, depending on the sign convention — either way it is a fake rank.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Forward returns are the **raw** ETF simple returns (plus dividends), not $\alpha$. You do not earn the intercept; you earn the next month’s price path minus costs. A path with $\hat\alpha>0$ but $R^{\mathrm{fwd}}<0$ must lose money in tests. Report Sharpe on non-overlapping holds and turnover. If you compound $\hat\alpha\times\Delta t$ as P&L, you have invented a return that was never traded.

## 5. Step-by-step algorithm

1. **Universe.** Sector, country, or index ETFs. ADV filter. No survivorship. This step exists so dead ETFs that had terrible $\alpha$ stay until delist.
2. **Returns.** Daily or weekly excess returns aligned with MKT/SMB/HML, window ending at $t_2$. This step exists to match RF and factor vintage. Misaligned calendars dump weekends into $\alpha$.
3. **Regress.** OLS of §4.1 per name. Drop names with fewer than $W_{\min}$ observations (default $W_{\min}=200$ of 252). This step exists because a 40-day OLS intercept is noise, not a sort key.
4. **Sort.** Rank $\hat\alpha_i$. Long-only or dollar-neutral. This step exists to turn leftover return into a book the same way `028` turns $R^{\mathrm{cum}}$.
5. **Weights.** Equal or residual-vol. Enforce the mode’s sum constraints. This step exists so tests can check budget identities.
6. **Caps.** ADV clip. Rebuild shorts if locate fails. This step exists so dollar-neutral cannot silently become residual-long.
7. **Blotter.** Intents only. This step exists because the spec does not route live.
8. **Re-estimate.** Rolling window, monthly hold. Never a static full-sample $\alpha$. This step exists to kill the most common look-ahead in this file.

## 6. Execution protocol

- Re-estimate $\alpha$ on a rolling window ending at $t-1$. Trade delay-1. If you do $X$ = include the hold month in the OLS, $\alpha$ peeked at the P&L you are trying to earn.
- Use the same RF series as the factor files. A different T-bill series puts a wedge in every intercept.
- Unstable betas on short windows: if $W$ is cut below $W_{\min}$, skip the name.

## 7. Data contract

Required, point-in-time:

- Adjusted ETF closes (to build $R_i$)
- Fama–French (and optional MOM) factor returns, vintage dated $\le t_2$
- Risk-free series matching the factors
- ADV, borrow for shorts

Not used by this spec: book-to-price as a signal (that would be double-counting HML), creation-unit NAV.

If you do $X$ = use the latest French library revision for all history, SMB/HML at $t_2$ were not the live vintage. If you do $X$ = drop ETFs that later closed, $\alpha$ ranks are survivorship-biased. If you do $X$ = fit $\alpha$ on the full sample, every month peeked. Freeze factor files by vintage date.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $W$ | 252 daily | weekly alternative |
| $W_{\min}$ | 200 | drop thin histories |
| factors | MKT, SMB, HML | MOM off |
| hold | 1 month | |
| mode | long-only | dollar-neutral optional |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.etf_alpha_rotation` with:

1. `alphas(excess_returns, factors, t2) -> pd.Series` — $\hat\alpha_i$, window ending at $t_2$, no look-ahead.
2. `weights(alphas, mode, k) -> pd.Series` — long-only or dollar-neutral constraints to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.
4. `pnl(D, forward_returns, costs) -> float` — uses raw $R^{\mathrm{fwd}}$, not $\alpha$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Unstable betas.** One year of daily data on a sector ETF still wobbles; $\alpha$ absorbs beta error. A name can rank high because $\beta_{\mathrm{MKT}}$ was too low, not because it is “alpha.”
- **Survivorship.** Dead ETFs had $\alpha$ too. Keep them until delist.
- **Costs.** $\alpha$ is not a tradable excess after spreads and turnover.
- **Factor vintage.** Restated SMB/HML after $t$ is look-ahead.

## 11. Acceptance tests

- Toy: $R^e=\alpha^\ast+\beta\,\mathrm{MKT}$ with known $\alpha^\ast$ and no noise → $\hat\alpha=\alpha^\ast$ to $10^{-8}$.
- Permuting factor returns after $t_2$ must not change $\hat\alpha(t_2)$.
- Top-2 long-only → two equal weights summing to 1.
- P&L uses $R^{\mathrm{fwd}}$, not $\hat\alpha\times\Delta t$; a path with $\hat\alpha>0$ but $R^{\mathrm{fwd}}<0$ must lose money.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
