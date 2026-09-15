---
rank: 14
slug: mean-reversion-single-cluster
title: "Mean-Reversion — Single Cluster"
asset_class: "equities"
style: "cross-sectional mean-reversion"
horizon: "Formation: days to weeks. Hold: days. Daily or weekly rebalance."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 014. Mean-Reversion — Single Cluster

| Field | Value |
|---|---|
| Popularity rank (this kit) | 14 of 101 |
| Why it sits here | The $N$-stock generalization of pairs. Industry residual reversal is a core daily stat-arb sleeve. |
| Aliases | industry residual reversal, cluster fade, statistical arbitrage (one cluster) |
| Asset class | equities |
| Style | cross-sectional mean-reversion |
| Typical horizon | Formation: 1–5 days. Hold: 1 day to 1 week. Daily or weekly rebalance. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Inside one tight cluster (a GICS industry, or a statistical cluster), names share a common return. Subtract that common piece. What remains is an idiosyncratic residual. Fade it: short names that outperformed the cluster, buy names that underperformed. Keep the book dollar-neutral.

This is pairs trading with $N$ legs instead of two.

You are betting that yesterday’s (or this week’s) *industry-relative* surprise dies out, not that the industry itself mean-reverts, and not that the market mean-reverts. The cluster mean is stripped by construction. A sector rally that lifts every name equally produces a zero residual book.

You are not running price momentum (the opposite sign on a longer window), not picking pairs one at a time, and not forecasting earnings. A print that looks like a residual is often a new mean — flatten or skip around events. Typical user: a daily stat-arb sleeve on liquid names, GICS industry as the cluster. Horizon intuition: form on 1–5 days, hold 1 day to 1 week, rebalance daily or weekly. Stretch the window toward a month and you start mixing momentum back in.

If you fit the cluster on the same window you trade, or drop the shorts and keep the longs, the backtest is not a market-neutral fade.

## 2. First principles

Write each name’s formation return as a common factor plus an idiosyncratic shock:

$$
R_i = F + \varepsilon_i, \qquad i = 1,\ldots,N
$$

Every name in the cluster shares $F$ (sector news, industry flow). The trade lives in $\varepsilon_i$. If the cluster is wrong — banks mixed with miners — $F$ is not a real common move and the residuals are fake relative value. That is why cluster assignment is a first-class input, not a comment.

$F$ is the cluster move (sector news, industry flow). $\varepsilon_i$ is the name-specific surprise.

The equal-weight cluster mean is the sample estimate of $F$:

$$
\bar R = \frac{1}{N}\sum_{i=1}^N R_i = F + \bar\varepsilon
$$

With $N$ names you still cannot recover $F$ exactly; you subtract the equal-weight mean, which estimates $F$ plus the average shock. Cap-weighted means are a different spec. Missing names must be dropped *before* this average, or a NaN poisons $F$ for everyone.

The residual is then

$$
\tilde R_i = R_i - \bar R = \varepsilon_i - \bar\varepsilon
$$

Name versus cluster. Positive: beat the industry (rich → short). Negative: lagged (cheap → long). This is arithmetic. Skip it and you are trading raw returns, i.e. a directional industry book.

By construction the residuals sum to zero:

$$
\sum_{i=1}^N \tilde R_i = 0
$$

That sum-to-zero is why $D_i=-\gamma\tilde R_i$ is dollar-neutral before clipping. If your residuals do not sum to zero, the demean is wrong. After dropping a name you must recompute $\bar R$ on the survivors, or neutrality is gone.

Mean-reversion says a large idiosyncratic shock tends to fade:

$$
\mathbb{E}[\varepsilon_{i,t+1} \mid \varepsilon_{i,t}] \approx -\lambda\,\varepsilon_{i,t}, \qquad \lambda \in (0,1)
$$

The bet, not the identity. $\lambda\in(0,1)$ says the shock shrinks over the next day or week. On a strong momentum day $\lambda$ can go the wrong way and the fade loses. Conditioning is on the past residual; the holding-period residual must not enter $\tilde R$.

So the next-period expected residual has the **opposite sign** of $\tilde R_i$. The trade is to hold a position proportional to $-\tilde R_i$. You are not betting on the sector. You are betting that the sector-relative surprise dies out.

That is the whole strategy. Everything below is just how to measure $\tilde R_i$, how to turn it into dollars, and how not to look ahead.

### Worked intuition

Three banks in one cluster. Over the last three days A returned $+3\%$, B $+1\%$, C $-1\%$. Cluster mean $+1\%$. Residuals: A $+2\%$ (short), B $0$ (flat), C $-2\%$ (long). A $\$100$ gross book puts $\$50$ short A and $\$50$ long C; B is unused. If the whole bank index then rallies $2\%$, both remaining legs move together and P&L is about zero before costs — you needed C to *catch up* to A, not for banks to rally. If A gaps on a fraud print, flatten; that residual is not a 1-day fade.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the cluster after liquidity filters |
| $P_i(t)$ | split- and dividend-adjusted price |
| $R_i$ | formation log return on name $i$ |
| $\bar R$ | equal-weight cluster mean of $R_i$ |
| $\tilde R_i$ | residual $R_i - \bar R$ |
| $Q_i$ | signed share holdings (positive = long) |
| $D_i = P_i Q_i$ | signed dollar holdings |
| $I$ | gross investment, $I = \sum_i \lvert D_i\rvert$ |
| $\gamma$ | scale that maps residuals into dollars |
| $w_i = D_i / I$ | portfolio weight |

Dollar-neutral means $\sum_i D_i = 0$. Combined with the gross budget this is $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$.

## 4. Mathematics

### 4.1 Formation return

Take a lookback window $[t_1, t_2]$ that **ends before** the fill. Use log returns so a round-trip of $+x$ then $-x$ nets to zero:

$$
R_i = \ln\frac{P_i(t_2)}{P_i(t_1)}
$$

Log return over the short formation window. $t_2 < t_{\mathrm{fill}}$ is load-bearing: the residual must be known before you trade. Unadjusted prices turn a split into a huge residual. Default 1–5 days; longer windows start to look like momentum of the opposite sign.

Default window: 1 to 5 trading days. Simple returns $P_i(t_2)/P_i(t_1) - 1$ are interchangeable when $\lvert R_i\rvert$ is small.

### 4.2 Cluster residual

$$
\bar R = \frac{1}{N}\sum_{i=1}^N R_i
$$

Equal-weight cluster mean, estimated $F$. Recompute on survivors after dropping missing $R_i$. A cap-weighted mean would overweight large names in $F$ and is a different file.

$$
\tilde R_i = R_i - \bar R
$$

Name minus cluster. This is the signal. Sign rule below is the whole trade. If $\tilde R_i$ uses prices after $t_2$, you looked ahead.

Sign rule:

- $\tilde R_i > 0$ — name beat the cluster → **short**
- $\tilde R_i < 0$ — name lagged the cluster → **long**
- $\tilde R_i = 0$ — flat

### 4.3 Dollar holdings

Gross dollars $I$ and dollar-neutrality:

$$
\sum_i \lvert D_i\rvert = I
$$

Gross budget. Without it, $\gamma$ is arbitrary and every Sharpe is a scale artifact.

$$
\sum_i D_i = 0
$$

Dollar-neutral inside the cluster. After ADV clips this can break; repair or cash-bucket. Silently dropping shorts leaves a residual-long sector bet.

The linear fade that satisfies both (because $\sum_i \tilde R_i = 0$) is

$$
D_i = -\gamma\,\tilde R_i
$$

Minus the residual: fade. Linear in $\tilde R$, so a $2\times$ residual gets $2\times$ dollars (before caps). This is why sum-to-zero residuals give sum-to-zero dollars for any $\gamma$.

with scale

$$
\gamma = \frac{I}{\sum_i \lvert\tilde R_i\rvert}
$$

Pick $\gamma$ so the absolute residuals exhaust the gross. If all residuals are zero (every name moved together), $\gamma$ is undefined — emit a flat book, do not divide by zero. After optional vol scaling, recompute this $\gamma$ on the scaled residuals.

Proof of neutrality: $\sum_i D_i = -\gamma\sum_i \tilde R_i = 0$. Proof of gross: $\sum_i \lvert D_i\rvert = \gamma\sum_i \lvert\tilde R_i\rvert = I$.

Shares, ignoring lot-size until the blotter:

$$
Q_i = \frac{D_i}{P_i(t_{\mathrm{fill}})}
$$

Dollars to shares at the fill. Using $P_i(t_2)$ here if $t_2$ is not the fill bar is a different size. Lots later; cash bucket for residual.

Optional vol control, applied **before** renormalizing $\gamma$: replace $\tilde R_i$ with $\tilde R_i / \sigma_i$ so high-vol residuals do not dominate the book.

### 4.4 Holding-period P&L

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Mark the fade through the next day or week. Delay-0 close-to-close uses the same bar in $\tilde R$ and $R^{\mathrm{fwd}}$ — research-only. If you do X = fill at $t_2$, the backtest lies by trading the print that created the residual.

Report:

- net return on gross $I$
- annualized Sharpe on **non-overlapping** holding-period returns
- one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

Daily residual books turn over a lot; costs are first-order. If you do X = report Sharpe before costs on a 1-day formation, the backtest lies about the only regime where the sleeve actually trades.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price above a minimum, ADV above a minimum, borrow available for any name that can be short. Keep delisted names until the delist date (no survivorship). This step exists because the short residual is often the news-y, hard-to-borrow name. Survivorship makes historical fades look safer.
2. **Cluster.** Assign each name to one cluster. Default: GICS industry, point-in-time. Alternative: a statistical cluster fit on a window that ends at $t_1$, never on the residual window you trade. Wrong clusters manufacture fake residuals. Fitting clusters on $[t_1,t_2]$ selects names *because* they just co-moved.
3. **Formation.** For each cluster with $N \ge N_{\min}$ (default 5), compute $R_i$ on $[t_1, t_2]$ using only prices with timestamp $\le t_2 < t_{\mathrm{fill}}$. Tiny clusters are pairs or single names; $N_{\min}$ exists so $\bar R$ is a real mean.
4. **Residual.** Demean inside the cluster. Drop names with missing $R_i$; recompute $\bar R$ on the survivors. Skipping the recompute after a drop breaks $\sum\tilde R_i=0$.
5. **Size.** $D_i = -\gamma \tilde R_i$ with $\gamma$ as above. Optional: divide by $\sigma_i$ first, then recompute $\gamma$. The minus sign is the fade; dropping it is momentum inside the cluster.
6. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV (default $1\%$). After clipping, if neutrality is broken, cash-out the residual into the largest opposite names or into a residual cash bucket; do not silently drop the short leg. Caps exist because residual tails are illiquid.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Cash bucket so rounding does not masquerade as P&L.
8. **Rebalance.** Daily close (delay-1: ranks from day’s data trade the next close) or next open. Intraday versions must still use information strictly before the fill. Delay-0 is a research switch, not the live default.

## 6. Execution protocol

- Default fill: next close after the residual is known. Academic delay-0 close-to-close is a backtest choice, not a live book. If you do X = rank and fill on the same close, the backtest lies by capturing the bar that made $\tilde R$.
- Cap names by ADV. Suppress $D_i$ by $1/\sigma_i$ if you do not want to overweight noisy residuals. If you do X = equal-dollar a 5-day $40\%$ residual in a micro name, the backtest lies about a fill you could not get.
- If a name cannot be shorted, drop it and rebuild $\bar R$ and $\gamma$ on the remaining cluster. Do not keep the longs and skip the shorts. If you do X = omit hard-to-borrow rich names, the backtest lies by turning a fade into a residual-long industry bet.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted prices on the formation and holding windows
- Point-in-time industry map (or the statistical cluster membership dated $\le t_1$)
- ADV for liquidity filters and impact caps
- Borrow availability and fees for any short

Not used by this spec: book value, earnings, SUE.

No restatement peeking. Delisted names stay in the formation sample until the delist date.

If you do X = use today’s GICS for a 2015 residual, taxonomy look-ahead regroups history. If you do X = fit statistical clusters on the trade window, the backtest lies by grouping names *because* they just dislocated. If you do X = unadjusted prices, splits look like residuals.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation window | 1–5 days | shorter = more reversal, more turnover |
| cluster | GICS industry | statistical clusters allowed if fit out of sample |
| $N_{\min}$ | 5 | skip tiny clusters |
| $I$ | caller-set | gross dollars |
| ADV cap | $1\%$ of ADV | per name |
| vol suppress | off | on → use $\tilde R_i/\sigma_i$ |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.mean_reversion_single_cluster` with:

1. `residuals(prices, clusters, t1, t2) -> pd.Series` — $\tilde R_i$, no look-ahead.
2. `weights(residuals, I, vol=None) -> pd.Series` — $w_i$ with $\sum w_i = 0$ and $\sum \lvert w_i\rvert = 1$ to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — shares $Q_i$, residual cash bucket, never live routing.
4. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}} - \mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Momentum days.** A cluster-wide trend day makes residuals keep going; the fade loses. If you do X = drop those days from the sample, the backtest lies by keeping only mean-reverting sessions.
- **Wrong cluster.** Mixing banks with miners creates fake residuals. If you do X = one “market” cluster, this file collapses to simple reversal, a different (weaker) object.
- **Earnings.** A print looks like an idiosyncratic residual and is not mean-reverting on a 1-day horizon. If you do X = fade through earnings without a skip, the backtest lies about a shock that was information.
- **Short-leg failure.** Losing the shorts turns a market-neutral fade into a residual-long sector bet. If you do X = clip shorts to zero, the backtest lies about neutrality.

## 11. Acceptance tests

- Two names, residuals $+x$ and $-x$ → equal-dollar opposite positions, $\sum D_i = 0$, $\sum \lvert D_i\rvert = I$.
- Three equal residuals summing to zero → three equal-magnitude weights, two of one sign and one of the other matching the signs of $-\tilde R_i$.
- Permuting all prices after $t_2$ must not change the $t_2$ residual. If shuffled future prices change $\tilde R$, the implementation looks ahead and the backtest lies.
- After ADV clipping, either neutrality still holds or the cash bucket absorbs the residual; the short leg is never silently dropped.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
