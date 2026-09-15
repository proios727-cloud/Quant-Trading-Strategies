---
rank: 19
slug: multi-asset-trend-following
title: "Multi-Asset Trend Following (ETFs)"
asset_class: "ETFs"
style: "long-only trend / risk-weighted ETF book"
horizon: "6–12 month formation; monthly rebalance"
instruments: "sector, country, rates, commodity, and FX ETFs"
---

# 019. Multi-Asset Trend Following (ETFs)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 19 of 101 |
| Why it sits here | The liquid ETF version of managed-futures trend: few tickers, many asset classes. Standard in multi-asset risk-parity-adjacent overlays. |
| Aliases | ETF TSMOM, long-only multi-asset trend |
| Asset class | ETFs |
| Style | long-only trend / risk-weighted ETF book |
| Typical horizon | 6–12 month formation; monthly rebalance |
| Instruments | sector, country, rates, commodity, and FX ETFs |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Keep only ETFs with positive trailing cumulative return (optional moving-average filter). Weight the survivors by momentum, optionally scaled by volatility. Names that fail the sign filter are dropped, not shorted.

You are betting that each ETF’s own 6–12 month excess (here: simple) return continues for the next month, but only on the long side. A bond ETF in an uptrend and a commodity ETF in an uptrend can both be held. A name whose formation return is negative is cash, not a short. Inverse-variance on the survivors is the default because a noisy equity ETF should not eat the same risk budget as a quieter Treasury ETF.

You are not running listed-futures TSMOM (`007`), which shorts the negative-sign names. You are not ranking sectors against each other (`028` / `018`). You are not claiming the inverse-variance book is a crisis hedge: equities, credit, commodities, and FX re-correlate when everyone sells. Tracking error inside commodity and FX ETFs (rolls, implied FX) is part of the traded price; do not swap in the futures generic and call it the same $R^{\mathrm{cum}}$.

Typical users are multi-asset ETF allocators and “liquid CTA” sleeves that cannot or will not hold futures. Panel size is small: a few dozen liquid ETFs across asset classes. Horizon intuition: 12-month formation, monthly rebalance, delay-1. When every asset sells off, the filter goes to cash only after the window turns; the current month still hurts.

## 2. First principles

For each ETF $i$, let $R^{\mathrm{cum}}_i$ be the formation simple return. Time-series trend says a positive trailing return predicts a positive next holding-period return:

$$
\mathbb{E}[R_{i,t+1}^{\mathrm{fwd}} \mid R^{\mathrm{cum}}_{i,t}>0] > 0
$$

The condition is the sign of that name’s own formation return, not its rank versus peers. The inequality is a directional claim, not a calibrated $\lambda$. The long-only constraint of this spec truncates the other side: if $R^{\mathrm{cum}}_i\le 0$, the position is $0$, not a short. Cash (or a T-bill ETF) absorbs the residual weight. If you short the rejects, you have implemented `007` in ETF clothing.

Given the survivors, a diagonal-covariance mean-variance investor with $E_i\propto R^{\mathrm{cum}}_i$ holds $w_i\propto R^{\mathrm{cum}}_i/\sigma_i^2$. The other two schemes in this file are the same idea with weaker vol penalties: proportional to $R^{\mathrm{cum}}$ (no vol), or to $R^{\mathrm{cum}}/\sigma$ (risk parity–adjacent). Inverse-variance is the default.

That is the whole strategy. Everything below is how to filter, how to renormalize, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | ETFs in the panel after liquidity filters |
| $P_i(t)$ | split- and dividend-adjusted price |
| $R^{\mathrm{cum}}_i$ | formation simple return |
| $\mathrm{MA}_i(T')$ | trailing moving average of $P_i$, length $T'$ |
| $\sigma_i$ | realized vol on a window ending before the fill |
| $w_i$ | portfolio weight; $w_i\ge 0$ |
| $\gamma_1,\gamma_2,\gamma_3$ | scales so $\sum_i w_i=1$ on the survivors |
| $w_i^{\max}$ | optional per-name cap |
| $I$ | gross dollars |

Long-only means $w_i\ge 0$ and $\sum_i w_i=1$. Failed filters go to cash, which is a $w_{\mathrm{cash}}$ residual, not a hidden sector.

## 4. Mathematics

### 4.1 Trend filter

Formation window $[t_1,t_2]$ of length $T$ (default 12 months) ending before the fill:

$$
R^{\mathrm{cum}}_i = \frac{P_i(t_2)}{P_i(t_1)}-1
$$

Two-point simple return on adjusted ETF prices. The traded NAV path, including rolls inside a commodity ETF, is already in $P_i$. Substituting a futures generic here is a different $R^{\mathrm{cum}}$. Keep $i$ only if $R^{\mathrm{cum}}_i>0$. Optional second filter: $P_i(t_2)>\mathrm{MA}_i(T')$ with $T'=200$ days, computed on prices $\le t_2$.

If no name survives, $w_{\mathrm{cash}}=1$. That is a valid book, not an error to “fix” by taking the least-negative name. An MA that includes the fill close is delay-0.

### 4.2 Three weighting schemes

On the survivor set, the three schemes are

$$
w_i = \gamma_1 R^{\mathrm{cum}}_i
$$

Proportional to formation return, no vol penalty. A 40% winner gets four times the weight of a 10% winner. This overweights high-vol equity ETFs. $\gamma_1$ is rebuilt so surviving weights sum to 1.

$$
w_i = \gamma_2 \frac{R^{\mathrm{cum}}_i}{\sigma_i}
$$

One power of vol in the denominator. Closer to risk parity with a momentum tilt. $\sigma_i$ must end at $t_2$; a vol that includes the hold peeks at realized risk you were trying to scale.

$$
w_i = \gamma_3 \frac{R^{\mathrm{cum}}_i}{\sigma_i^2}
$$

Each $\gamma$ is chosen so $\sum_i w_i=1$. The third scheme maximises Sharpe if the covariance is diagonal $C_{ij}=\mathrm{diag}(\sigma_i^2)$ and $E_i\propto R^{\mathrm{cum}}_i$. Inverse-variance is the kit default. If $\sigma_i$ is missing, drop the name; $\sigma_i=0$ is undefined and would send weight to infinity.

Optional cap: after the raw $w_i$, enforce $w_i\le w_i^{\max}$ and renormalize the remainder. Default $w^{\max}=0.25$. The cap exists so a single noisy survivor cannot become 100% of the book after a crash filters everyone else. If you refuse to renormalize, leftover weight is cash, which is safer and must be documented.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

$D_i=I w_i$. $R_i^{\mathrm{fwd}}$ is the simple return of the *traded* ETF from fill to next rebalance, including dividends. You do not earn $R^{\mathrm{cum}}$ again; that was the filter. Cash earns the T-bill / money-market series if you model it; otherwise $0$. If cash is a large fraction and you mark it at 0 in a rate-hiking year, the backtest lies about the parking lot. Report Sharpe on non-overlapping holds and

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

Filter flips (in versus cash) dominate turnover. Overlapping holds inflate Sharpe. Use non-overlapping monthly returns.

## 5. Step-by-step algorithm

1. **Universe.** Sector, country, rates, commodity, and FX ETFs. ADV and AUM minima. No survivorship: keep names until delist. This step exists so a commodity ETF that was liquid in-sample and later shut down is not dropped from history.
2. **Formation.** $R^{\mathrm{cum}}_i$ on $[t_1,t_2]$, $t_2<t_{\mathrm{fill}}$. Vol $\sigma_i$ on 60–126 days ending at $t_2$. This step exists to keep both the sign and the risk scaler causal.
3. **Filter.** Drop $R^{\mathrm{cum}}_i\le 0$. Optional: drop $P_i\le\mathrm{MA}_i(T')$. Do not short the rejects. This step exists because this spec is long-only trend; shorting rejects is `007`.
4. **Weight.** Inverse-variance default on survivors; $\gamma_3$ so $\sum w_i=1$. Apply $w^{\max}$ and renormalize. This step exists to turn a survivor list into a budgeted book.
5. **Cash.** If the sum of uncapped weights is $0$, or after caps a residual remains that you choose not to redistribute, hold cash. This step exists so an empty survivor set is a T-bill book, not a forced equity ETF.
6. **Caps vs ADV.** Clip $\lvert D_i\rvert$ at a fraction of ADV. Residual to cash. This step exists so a thin FX ETF cannot take a 25% weight at a size that is the day’s volume.
7. **Blotter.** Shares, lot rounding, intents only. This step exists because the research blotter never routes live.
8. **Rebalance.** Monthly, delay-1. This step exists so month-end filters trade the next session, not the close that completed them.

## 6. Execution protocol

- Default fill: next open after month-end filters. Delay-0 close-to-close is research-only. If you do $X$ = fill at $t_2$ close, formation and fill share a print.
- Dropping a name that failed the sign/MA filter is required. Replacing it with a short is a different spec (`007`).
- If vol is missing, drop the name; do not impute $\sigma_i=0$. Imputation overweights the name with the worst data.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted ETF closes for formation, MA, vol, and hold
- ADV and AUM for capacity
- A cash / T-bill series if $w_{\mathrm{cash}}$ is marked to market

Not used by this spec: book value, earnings, creation-unit NAV, borrow (the book is long-only).

If you do $X$ = use a futures back-adjusted series in place of the ETF close, $R^{\mathrm{cum}}$ is not the tradable product. If you do $X$ = compute $\sigma_i$ through the hold, weights peeked at realized vol. If you do $X$ = drop ETFs that later liquidated, the panel is survivorship-biased. Point-in-time share-class closes matter: a reverse split restated through history can change $P(t_1)$ after the fact if you are not using a frozen adjusted series.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation $T$ | 12 months | 6 months allowed |
| MA $T'$ | 200 days | optional filter, on by default as an AND with $R^{\mathrm{cum}}>0$ if the caller enables it |
| MA filter | off | on $\Rightarrow$ require $P_i>\mathrm{MA}_i$ |
| vol lookback | 60–126 days | 60 default |
| scheme | $R^{\mathrm{cum}}/\sigma^2$ | $\gamma_3$ |
| $w^{\max}$ | $0.25$ | then renormalize |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.multi_asset_trend_following` with:

1. `cum_return(prices, t1, t2) -> pd.Series` — $R^{\mathrm{cum}}_i$, no look-ahead.
2. `survivors(cum_return, prices, ma_length=None) -> pd.Index` — names with $R^{\mathrm{cum}}>0$ and optional MA.
3. `weights(cum_return, sigma, scheme, wmax) -> pd.Series` — $w_i\ge 0$, $\sum w_i=1$ to `1e-8` (cash makes up any gap).
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.
5. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Diagonal covariance.** Crises re-correlate equities, credit, commodities, and FX; the inverse-variance book is not a hedge.
- **Long-only left tail.** When every asset sells off, the filter goes to cash only after the formation window turns; the current month still hurts.
- **Small $N$.** A handful of ETFs plus a 25% cap is still concentrated.
- **FX and commodity ETFs.** Tracking error and roll in the product are not in $R^{\mathrm{cum}}$ unless the price is the traded ETF. Using the index or the futures generic is a different strategy.

## 11. Acceptance tests

- One survivor with $R^{\mathrm{cum}}>0$ → $w=1$ on that name.
- Two survivors, equal $R^{\mathrm{cum}}$, $\sigma_2=2\sigma_1$, inverse-variance scheme → $w_1=4/5$, $w_2=1/5$ before the cap.
- All $R^{\mathrm{cum}}\le 0$ → cash weight $1$, all ETF weights $0$.
- Permuting prices after $t_2$ must not change $R^{\mathrm{cum}}$ or $\sigma$ at $t_2$.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
