---
rank: 97
slug: distress-risk-puzzle
title: "Distress Risk Puzzle"
asset_class: "equities"
style: "long healthy / short distressed"
horizon: "Monthly (or annual) rebalance"
instruments: "listed equities; default-probability model"
---

# 097. Distress Risk Puzzle

| Field | Value |
|---|---|
| Popularity rank (this kit) | 97 of 101 |
| Why it sits here | Academic anomaly: safer firms have earned higher returns than high-default-probability firms. Traded as HMD (healthy-minus-distressed). |
| Aliases | HMD, healthy-minus-distressed, distress anomaly |
| Asset class | equities |
| Style | long healthy / short distressed |
| Typical horizon | Monthly (or annual) rebalance |
| Instruments | listed equities; default-probability model |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Compensation logic says high default probability should mean high expected equity return. The distress-risk puzzle is that the opposite has shown up in the cross-section: safer firms have earned more than firms the model labels as close to bankruptcy. Estimate a point-in-time default probability $P_i$, short the top decile (riskiest), long the bottom decile (safest), and vol-scale that healthy-minus-distressed (HMD) book to a target.

You are trading the puzzle: healthy minus distressed. You are not underwriting credit, and you are not buying a default-risk premium. You are not running a value or low-vol book that happens to correlate with $P_i$; those are different sorts. Distressed shorts are expensive, hard to borrow, and gap on news — that implementation shortfall is part of the result, not an afterthought you can skip in a long-only healthy sleeve.

A long-only top of the healthy decile is a different book: it keeps the puzzle’s long leg and throws away the short, which is where much of the academic HMD return was earned and where live P&L usually dies. If borrow is missing on half the distressed names and you do not rebuild the short dollars, you have that long-only book whether you meant to or not.

The default model is a logistic (or a documented substitute) fit on a window that ends before the sort. Features are public market and accounting fields with filing timestamps. Restated 10-K numbers, a bankruptcy flag known only after the delist, or a $\beta$ fit that includes the holding month will manufacture the puzzle. Large-cap filters are recommended because the short leg is where costs and borrow live. Point-in-time market cap and trailing volatility in $x_i$ must be computed from prices already public at the sort; a trailing-return feature that includes the holding month is the same leak as using month-$t$ returns in a momentum skip.

## 2. First principles

Let $y_i \in \{0,1\}$ be the event “issuer $i$ defaults over the model horizon.” A logistic default model maps a point-in-time feature vector $x_i$ (market and accounting) to a probability

$$
P_i = \mathbb{P}(y_i=1\mid x_i) = \frac{1}{1+\exp(-x_i^{\top}\beta)}
$$

$\beta$ is fit on a window that **ends before** the sort date. Features are Campbell–Hilscher–Szilagyi style (or a documented substitute): market cap, trailing returns, volatility, leverage, cash, profitability, and so on. Document the list; do not change it inside a test window. $x_i$ uses only vintages dated $\le$ the sort: last known filing, last known market fields. Imputing missing leverage with zeros, or using a restated book value, is a different $P_i$.

Compensation would require

$$
\mathbb{E}[R_i^{\mathrm{fwd}} \mid P_i] \quad \text{increasing in } P_i
$$

If that monotone held, you would long distressed and short healthy — a credit-risk premium book. The puzzle is that sorts on $P_i$ have gone the other way: low $P_i$ (healthy) beat high $P_i$ (distressed). The identity above is the null this trade fades, not a pricing equation you estimate live. A sample where the monotone returns is a failure mode, not a “wrong sign” you flip mid-test.

The trade is therefore **long healthy, short distressed** — the opposite of a credit-risk premium book.

Form deciles on $P_i$. Let $H$ be the bottom decile and $D$ the top decile. The zero-cost HMD portfolio is equal- or value-weight long $H$ and short $D$:

$$
\mathrm{HMD} = \sum_{i\in H} w_i^{H} R_i^{\mathrm{fwd}} - \sum_{i\in D} w_i^{D} R_i^{\mathrm{fwd}}
$$

with $\sum_{i\in H} w_i^{H} = \sum_{i\in D} w_i^{D} = 1$. $R_i^{\mathrm{fwd}}$ is the holding-period simple return including dividends, from fill to next rebalance. Names that delist during the hold stay until the delist date; dropping them early is survivorship. Equal-weight versus value-weight inside a leg is a documented choice; mixing them silently is a bug.

Distressed names are high-vol. Scale the whole book to a target volatility using trailing realized vol $\sigma$ of HMD:

$$
\mathrm{HMD}^{\ast} = \frac{\sigma_{\mathrm{target}}}{\sigma}\,\mathrm{HMD}
$$

$\sigma$ is trailing one-year realized volatility of daily HMD, computed on days that are already complete — no look-ahead into the hold. Allocate 100% only if $\sigma = \sigma_{\mathrm{target}}$; cut when $\sigma$ is higher; optional leverage if $\sigma < \sigma_{\mathrm{target}}$, with a cap. The scale multiplies every dollar holding, healthy and distressed together, so neutrality is preserved.

That is the whole strategy. Everything below is how to estimate $P_i$ without peeking, how to form the legs, and how not to skip the expensive shorts.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names after liquidity filters |
| $x_i$ | point-in-time default-model features |
| $\beta$ | logistic coefficients fit on data dated $<$ sort date |
| $P_i$ | model default probability |
| $H$ | healthy leg: bottom decile of $P_i$ |
| $D$ | distressed leg: top decile of $P_i$ |
| $w_i^{H}, w_i^{D}$ | weights inside each leg (sum to 1) |
| $\mathrm{HMD}$ | healthy-minus-distressed simple return |
| $\sigma$ | trailing 1y realized vol of HMD (daily) |
| $\sigma_{\mathrm{target}}$ | vol target for the scaled book |
| $\mathrm{HMD}^{\ast}$ | vol-scaled HMD |
| $I$ | gross dollars after scaling |

## 4. Mathematics

### 4.1 Default probability

Sort on model $P_i$. The default logistic is

$$
P_i = \frac{1}{1+\exp(-x_i^{\top}\beta)}
$$

Fit $\beta$ by maximum likelihood on a sample that ends before the formation date. Freeze $\beta$ over the holding month (or year). Missing $x_i$ $\Rightarrow$ drop the name; do not impute with zeros unless this file is amended. A $\beta$ that is re-estimated using defaults that occur during the hold is look-ahead. Changing the feature list inside the test window is a different strategy.

### 4.2 Decile book

Zero-cost: short top decile, long bottom. Monthly or annual reconstitution. Inside each leg, equal-weight or value-weight; pick one and keep it.

Dollar holdings on the unscaled book, gross $I_0$, are long half on healthy names:

$$
\sum_{i\in H} D_i = +\tfrac12 I_0
$$

Half the unscaled gross sits in $H$. That is the long healthy sleeve, not a 100% long-only book.

and short half on distressed names, so the book is dollar-neutral:

$$
\sum_{i\in D} D_i = -\tfrac12 I_0
$$

The two identities together give $\sum_i D_i = 0$ and $\sum_i \lvert D_i \rvert = I_0$ before vol scale. If a distressed name cannot be shorted, drop it from $D$ and rebuild the short dollars on the remaining top-decile names so these sums still hold. Keeping $H$ and skipping $D$ is a residual-long healthy bet this spec refuses.

### 4.3 Vol overlay

Let $\sigma$ be the trailing one-year realized volatility of daily HMD (non-overlapping, no look-ahead). The scaled return is

$$
\mathrm{HMD}^{\ast} = \frac{\sigma_{\mathrm{target}}}{\sigma}\,\mathrm{HMD}
$$

$\sigma_{\mathrm{target}}$ default $10\%$–$15\%$ annualized. Scale factor $\sigma_{\mathrm{target}}/\sigma$ multiplies all $D_i$. Cap leverage if $\sigma < \sigma_{\mathrm{target}}$. $\sigma$ uses only HMD returns already realized; including the month you are about to hold is look-ahead. After ADV clipping, re-apply neutrality, then re-apply the scale, or document a cash bucket for the residual.

### 4.4 Holding-period P&L

Over the holding month, with borrow on the distressed short:

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{borrow} - \mathrm{costs}
$$

$D_i$ are the scaled, clipped holdings. $R_i^{\mathrm{fwd}}$ includes dividends and delist proceeds. Borrow is the distressed-leg fee, not a footnote. Report net return on scaled gross $I$, annualized Sharpe on non-overlapping holding-period returns, and one-way turnover. Delay-1: ranks from month-end data trade the next month’s first close (or next open). Academic delay-0 is research-only.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price and ADV above minima. Large-cap filter recommended (distressed names are costly). Keep delists until the delist date (no survivorship). Borrow must be available for any name that can land in $D$. This step exists so the short leg is tradable and bankrupt names are not dropped before the event.
2. **Features.** Build $x_i$ from point-in-time market and accounting fields. No restatement peeking. Document the Campbell–Hilscher–Szilagyi (or substitute) list. This step exists so $P_i$ is a public-information score, not a restated 10-K score.
3. **Model.** Fit $\beta$ on history ending before the sort. Compute $P_i$. Drop names with missing $P_i$. This step exists so the logistic cannot see the holding-month default it is supposed to rank before.
4. **Sort.** Rank on $P_i$. Long bottom decile $H$, short top decile $D$. Equal- or value-weight inside legs. This step exists to implement the puzzle sign: healthy minus distressed, not the compensation sign.
5. **Scale.** Compute trailing 1y $\sigma$ of HMD. Set $D_i \leftarrow (\sigma_{\mathrm{target}}/\sigma) D_i$, with a leverage cap. This step exists because distressed names are high-vol; an unscaled book is a vol lottery.
6. **Caps.** Clip $\lvert D_i \rvert$ at a fraction of ADV. After clipping, rebuild neutrality; do not keep the healthy longs and skip the distressed shorts. This step exists so impact and borrow limits cannot silently drop the puzzle’s short leg.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. This step exists to keep the research contract off the venue.
8. **Rebalance.** Monthly (default) or annual. Delay-1: ranks from month-end data trade the next month’s first close (or next open). This step exists so month-$t$ returns do not sit inside the sort that trades month $t$.

## 6. Execution protocol

- Rebalance monthly. Shorts of distressed names have borrow and gap risk — that is part of the puzzle’s implementation shortfall.
- If a name cannot be shorted, drop it from $D$ and **rebuild** the short leg on the remaining top-decile names so that the short dollars still match the long dollars.
- Default fill: next close after $P_i$ is known. Academic delay-0 is a backtest choice, not a live book.
- Filing lag: an accounting field dated $T$ cannot enter $x_i$ before its actual print date.
- Do not refit $\beta$ on a rolling window that includes the holding month’s defaults. The sort is allowed to see only defaults and filings already public.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted prices on the holding window
- Accounting and market features in $x_i$, vintage-dated (no restatements)
- ADV for liquidity filters and impact caps
- Borrow availability and fees for the distressed leg
- Delist / bankruptcy flags dated as of the event (keep the name until then)

Look-ahead that invalidates a historical blotter: restated book or earnings in $x_i$, a $\beta$ fit that includes post-sort defaults, a delist removed before the delist date, or borrow assumed available because it later appeared. Trailing $\sigma$ must not include the holding month’s HMD return. Concrete series that often leak: Compustat restatement overlays used as “as reported,” CRSP delist returns dropped instead of kept through the delist date, and a distance-to-default input that was calibrated on the full sample including the hold. Accounting fields need the filing timestamp, not the fiscal-period end. A 10-K for fiscal year $T$ that prints in March of $T+1$ cannot enter the February sort.

Not used by this spec: convertible prices, CPI.

No restatement peeking. Delisted names stay until the delist date.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $P_i$ model | logistic | Campbell–Hilscher–Szilagyi features; document the list |
| reconstitution | monthly | annual allowed |
| legs | bottom vs top decile | equal- or value-weight inside |
| $\sigma_{\mathrm{target}}$ | $10\%$–$15\%$ ann. | trailing 1y daily $\sigma$ |
| universe | large-cap recommended | distressed names are costly |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.distress_risk_puzzle` with:

1. `default_prob(features, beta) -> pd.Series` — $P_i$, no look-ahead in $x_i$ or $\beta$.
2. `hmd_weights(P, mode) -> pd.Series` — $w_i$ long $H$ / short $D$, $\sum w_i = 0$ and $\sum \lvert w_i \rvert = 1$ to `1e-8` before vol scale.
3. `vol_scale(weights, sigma, sigma_target, lev_cap) -> pd.Series` — applies $\sigma_{\mathrm{target}}/\sigma$.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — shares, residual cash bucket, never live routing.
5. `pnl(D, forward_returns, borrow, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}} - \mathrm{borrow} - \mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Crash beta.** HMD beta goes very negative after market crashes (short squeeze on distressed).
- **Model risk.** A different $x_i$ list is a different strategy.
- **Illiquidity and borrow.** The short leg is where the puzzle is implemented — and where it fails.
- **Survivorship.** Dropping bankrupt names before the delist date manufactures healthy-leg outperformance.

## 11. Acceptance tests

- Two names with $P$ in different deciles after a two-bin split $\to$ equal-dollar opposite positions before vol scale, $\sum D_i = 0$.
- $\sigma = \sigma_{\mathrm{target}}$ $\Rightarrow$ $\mathrm{HMD}^{\ast} = \mathrm{HMD}$.
- $\sigma = 2\sigma_{\mathrm{target}}$ $\Rightarrow$ all $\lvert D_i \rvert$ halved.
- Permuting features after the sort date must not change $P_i$ at the sort.
- Missing borrow on a distressed name: short leg rebuilt, longs not left unhedged.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
