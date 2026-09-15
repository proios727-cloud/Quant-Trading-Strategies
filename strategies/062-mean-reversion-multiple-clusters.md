---
rank: 62
slug: mean-reversion-multiple-clusters
title: "Mean-Reversion — Multiple Clusters"
asset_class: "equities"
style: "industry-neutral reversal"
horizon: "Daily/weekly, same as single cluster."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 062. Mean-Reversion — Multiple Clusters

| Field | Value |
|---|---|
| Popularity rank (this kit) | 62 of 101 |
| Why it sits here | Production stat-arb: residualize returns on a sector/industry dummy matrix via regression, trade residuals. |
| Aliases | industry-neutral reversal, multi-cluster fade |
| Asset class | equities |
| Style | industry-neutral reversal |
| Typical horizon | Daily/weekly, same as single cluster. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

$K$ clusters. Either run single-cluster mean-reversion inside each cluster and allocate, or one regression on the loadings matrix $\Lambda$. With unit weights and dummy columns, the two are the same: residuals are cluster-demeaned returns. This is [`014-mean-reversion-single-cluster.md`](014-mean-reversion-single-cluster.md) stacked across industries.

You are betting that industry-relative surprises die out **in every cluster at once**, not that any industry itself mean-reverts, and not that the market does. Dummy residualization strips each cluster mean. A day when every bank rallies and every miner sells off produces zeros inside each group if names moved together.

You are not fitting $\Lambda$ on the residual window you trade, not assigning unknown GICS to a junk bucket silently, and not skipping $N_{\min}$. Typical user: a production daily stat-arb book that already understood one-cluster fade and now wants industry-neutral stacking. Horizon intuition: same as 014 — form 1–5 days, hold 1 day to 1 week; $\Lambda$ itself rebuilds slowly (quarterly GICS).

If you use tomorrow’s industry map, or run one regression with a dense style $\Omega$ (that is file 063), the backtest is a different residual.

## 2. First principles

Map each name to one cluster: $G:\{1,\ldots,N\}\to\{1,\ldots,K\}$. The dummy loading is one if name $i$ sits in cluster $A$:

$$
\Lambda_{iA} = \delta_{G(i),A}
$$

One-hot industry (or statistical cluster) membership. Each name in exactly one cluster; unknown cluster → drop, not silently assign. $G$ is point-in-time. Using a GICS assignment dated after $t_1$ regroups history — look-ahead. Statistical $G$ must be fit on a window ending at $t_1$, never on $[t_1,t_2]$.

Each name sits in exactly one cluster, so the rows of $\Lambda$ sum to one:

$$
\sum_{A=1}^{K} \Lambda_{iA} = 1
$$

The intercept is already in $\Lambda$. You do not add another column of ones; that would make $\Lambda$ rank-deficient. Empty clusters ($N_A=0$) must be dropped before regression so $\Lambda^\top\Lambda$ stays invertible on the remaining columns.

Write formation returns as cluster factors plus an idiosyncratic shock:

$$
R = \Lambda f + \varepsilon
$$

Vector form of $R_i = f_{G(i)}+\varepsilon_i$. $f_A$ is the common return of cluster $A$. This is the same story as one cluster, stacked. If $\Lambda$ is wrong, $\varepsilon$ is a fake residual in every $A$ at once.

$f_A$ is the common return of cluster $A$. Ordinary least squares without an extra intercept (the intercept is already in $\Lambda$) gives

$$
f = (\Lambda^\top \Lambda)^{-1} \Lambda^\top R
$$

OLS factor. Because $\Lambda^\top\Lambda=\mathrm{diag}(N_A)$, this inverse is just “divide by cluster size,” and $f_A$ is the equal-weight mean of cluster $A$. You do not need a general solver for dummies; the closed form is demeaning. Weighted $z_i\neq 1$ is file 063.

$\Lambda^\top\Lambda$ is diagonal with the cluster sizes, so $f_A$ is just the equal-weight mean of cluster $A$. The residual is therefore the single-cluster residual, computed in parallel:

$$
\varepsilon_i = R_i - \bar R_{G(i)}
$$

Name minus its own cluster mean. Same residual as running 014 inside each industry. Fade with $D_i=-\gamma\varepsilon_i$. Within-cluster sums of $\varepsilon$ are zero, so a common $\gamma$ (or per-cluster $\gamma_A$) keeps each cluster dollar-neutral.

Mean-reversion is the same bet as in the one-cluster spec: $\mathbb{E}[\varepsilon_{i,t+1}\mid\varepsilon_{i,t}]\approx -\lambda\varepsilon_{i,t}$. Fade $\varepsilon_i$ with $D_i=-\gamma\varepsilon_i$. You are not betting on any industry. You are betting that industry-relative surprises die out, in every cluster at once.

That is the whole strategy. Everything below is the dummy algebra, neutrality per cluster, and how to allocate across clusters.

### Worked intuition

Two industries, two names each. Banks: A $+3\%$, B $+1\%$ → bank mean $+2\%$, residuals $+1\%$ and $-1\%$. Miners: C $-4\%$, D $-2\%$ → miner mean $-3\%$, residuals $-1\%$ and $+1\%$. Fade: short A, long B, long C, short D (signs of $-\varepsilon$). The book is long/short *inside* banks and *inside* miners; it is not short the mining sector. If both miners had moved $-3\%$, miner residuals would be $0$ and that cluster would be flat even though the sector sold off. One cluster covering all four names would have mixed banks with miners and called those sector moves “idiosyncratic.”

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names after liquidity filters |
| $A = 1,\ldots,K$ | clusters |
| $G(i)$ | cluster of name $i$ |
| $\Lambda_{iA}$ | dummy $\delta_{G(i),A}$ |
| $N_A$ | size of cluster $A$ |
| $R_i$ | formation log return |
| $f_A$ | OLS cluster factor (= $\bar R_A$) |
| $\bar R_A$ | equal-weight mean of cluster $A$ |
| $\varepsilon_i$ | residual $R_i-\bar R_{G(i)}$ |
| $D_i$ | signed dollar holdings |
| $I$ | gross dollars |
| $\gamma$ | scale that maps residuals into dollars |

Each name in exactly one cluster; no empty clusters. Dollar-neutral **inside each cluster** means $\sum_i \varepsilon_i \Lambda_{iA}=0$, hence $\sum_i D_i \Lambda_{iA}=0$ when $D_i=-\gamma\varepsilon_i$ with a common $\gamma$ or with a per-cluster $\gamma_A$.

## 4. Mathematics

### 4.1 Dummy matrix and sizes

Cluster size and the universe size:

$$
N_A = \sum_i \Lambda_{iA} > 0
$$

Count in cluster $A$, strictly positive after dropping empties. $N_A=1$ makes $\varepsilon_i=0$; $N_A=2$ is a pair. Enforce $N_{\min}$ (default 5) so $\bar R_A$ is a real mean. Tiny clusters should be skipped, not padded.

$$
N = \sum_A N_A
$$

Universe size after skips. If unknown-cluster names were silently assigned, this $N$ would include junk membership. Drop them first.

The Gram matrix of the dummies is diagonal:

$$
Q = \Lambda^\top \Lambda = \mathrm{diag}(N_A)
$$

This is why OLS collapses to demeaning. If you accidentally add an intercept column, $Q$ is no longer this diagonal and the solver can become rank-deficient. Do not invert a general $Q$ and then also demean; pick one.

### 4.2 OLS residual equals cluster demeaning

Regression without intercept, unit weights:

$$
R = \Lambda f + \varepsilon
$$

Same stacked factor model. Unit weights: every name votes equally inside its cluster. File 063 puts $Z$ here.

$$
f = (\Lambda^\top \Lambda)^{-1} \Lambda^\top R
$$

OLS. With dummy $\Lambda$ this is cluster means. A general dense $\Omega$ would not simplify; that is why 063 exists.

Because $Q=\mathrm{diag}(N_A)$, the factor is the cluster mean:

$$
\bar R_A = \frac{1}{N_A}\sum_{j:G(j)=A} R_j
$$

Equal-weight mean of cluster $A$. Recompute on survivors after dropping missing $R_i$. Cap-weighting is a different $f_A$.

Residuals are cluster-demeaned returns:

$$
\varepsilon_i = R_i - \bar R_{G(i)}
$$

The traded residual. Must satisfy `Lambda.T @ eps == 0`. If it does not, the demean (or the OLS) is wrong. Formation window and log returns match 014: $R_i=\ln P_i(t_2)/P_i(t_1)$, $t_2<t_{\mathrm{fill}}$.

Cluster neutrality:

$$
\sum_i \varepsilon_i \Lambda_{iA} = 0
$$

Within each cluster, residuals sum to zero. That is the dollar-neutrality seed. After ADV clips, repair per cluster or cash-bucket; do not drop only the shorts in cluster $A$.

The intercept is already in $\Lambda$ because $\sum_A \Lambda_{iA}=1$.

### 4.3 Dollar holdings

Then set

$$
D_i = -\gamma \varepsilon_i
$$

Fade the stacked residual. Common $\gamma$ equalizes dollars by residual size across the whole book; per-cluster $\gamma_A$ equalizes risk or dollars *across clusters*. Proof of within-cluster neutrality: $\sum_i D_i \Lambda_{iA} = -\gamma\sum_i \varepsilon_i \Lambda_{iA}=0$ when $\gamma$ is common (or when $\gamma_A$ is constant on $A$).

with $\gamma$ from the gross budget $\sum_i \lvert D_i\rvert = I$, or a per-cluster $\gamma_A$ if you equalize risk (or dollars) across clusters. Proof of within-cluster neutrality: $\sum_i D_i \Lambda_{iA} = -\gamma\sum_i \varepsilon_i \Lambda_{iA}=0$.

Formation return, default window, optional vol control, and P&L match the single-cluster spec: $R_i=\ln P_i(t_2)/P_i(t_1)$, fade the residual, delay-1 fill.

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Mark the stacked fade through the hold. Delay-0 uses the same bar in $\varepsilon$ and $R^{\mathrm{fwd}}$. If you do X = fill at $t_2$, the backtest lies. Costs on daily books are first-order; skipping them lies about the sleeve that actually turns over.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price and ADV filters, borrow for shorts. Keep delisted names until the delist date. Survivorship in residual shorts still paints fades too kind. This step exists so every cluster is tradable on both legs.
2. **Clusters.** Assign $G(i)$ point-in-time (default: GICS industry). Rebuild $\Lambda$ on a slow clock (quarterly for GICS). Names with unknown cluster are dropped, not silently assigned. Skip clusters with $N_A < N_{\min}$ (default 5). Point-in-time $G$ exists so tomorrow’s taxonomy cannot regroup yesterday’s residual.
3. **Formation.** Compute $R_i$ on $[t_1,t_2]$ with $t_2 < t_{\mathrm{fill}}$, same window as the single-cluster spec. Same delay reason as 014: residual known before fill.
4. **Residualize.** `residualize(R, Lambda)` via OLS or, equivalently, demean inside each cluster. Drop missing $R_i$; recompute $\bar R_A$ on survivors. Equivalence is the spec; a general solver that disagrees with demeaning is a bug for dummy $\Lambda$.
5. **Allocate.** Equal-risk across clusters or equal dollar (common $\gamma$). Then $D_i=-\gamma\varepsilon_i$ (or $-\gamma_A\varepsilon_i$). Allocation exists so one huge industry does not eat $I$.
6. **Caps.** ADV clip. After clipping, repair within-cluster neutrality or park the residual in a cash bucket; do not silently drop shorts. Caps exist because residual tails are illiquid in every $A$.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Cash bucket for lots.
8. **Rebalance.** Residuals daily (or weekly). $\Lambda$ slower. Rebuilding $\Lambda$ daily on a statistical cluster fit on the trade window is look-ahead.

## 6. Execution protocol

- Rebuild $\Lambda$ on a slow clock (quarterly for GICS). Residuals daily. If you do X = restate historical GICS to today’s map, the backtest lies by regrouping the past.
- Statistical clusters allowed only if fit on a window that ends at $t_1$, never on the residual window you trade. If you do X = cluster on $[t_1,t_2]$, you select groups *because* they just co-moved.
- If a name cannot be shorted, drop it and rebuild $\bar R_A$ and $\gamma$ on the remaining cluster. If you do X = keep longs in $A$ and skip shorts, that cluster becomes a residual-long industry bet and the backtest lies about neutrality.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted prices on the formation and holding windows
- Point-in-time industry map (or statistical cluster membership dated $\le t_1$)
- ADV for liquidity filters and impact caps
- Borrow availability and fees for any short

Not used by this spec: book value, earnings, SUE.

No restatement peeking. Delisted names stay in the formation sample until the delist date.

If you do X = use current GICS for 2015 residuals, taxonomy look-ahead. If you do X = unadjusted prices, splits look like residuals in one name and poison $\bar R_A$. If you do X = assign unknown industry to “Other” without documenting it, $N_{\mathrm{Other}}$ is a junk cluster.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation window | 1–5 days | same as single cluster |
| cluster | GICS industry | statistical clusters if fit out of sample |
| $N_{\min}$ | 5 | skip tiny clusters |
| allocation | equal dollar | or equal-risk $\gamma_A$ |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.mean_reversion_multiple_clusters` with:

1. `loadings(clusters) -> Lambda` — one-hot; unknown cluster → drop, not assign.
2. `residualize(R, Lambda) -> eps` — must return `Lambda.T @ eps == 0` within tolerance.
3. `weights(eps, I, allocation) -> pd.Series` — $\sum_i w_i \Lambda_{iA} = 0$ per cluster (or documented cash bucket).
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Wrong taxonomy.** Mixing banks with miners creates fake residuals (same as one cluster, now in every $A$). If you do X = one market dummy, this file collapses to simple reversal.
- **Single-name news.** Still in $\varepsilon$; a print is not a 1-day fade. If you do X = fade through earnings in every industry, the backtest lies about information shocks.
- **Empty / tiny clusters.** $N_A=1$ makes $\varepsilon_i=0$; $N_A=2$ is a pair. Enforce $N_{\min}$. If you do X = keep $N_A=1$, you get a zero residual and think you are hedged.

## 11. Acceptance tests

- One cluster $\Rightarrow$ identical to the single-cluster spec.
- Two equal clusters, opposite means, within-cluster returns equal → all residuals 0.
- `Lambda.T @ eps == 0` after residualize.
- Names with unknown cluster are dropped, not silently assigned. If they appear in $\Lambda$, membership look-ahead or junk assignment and the backtest lies.
- Permuting prices after $t_2$ must not change the $t_2$ residual. If shuffled future prices change $\varepsilon$, delay is broken.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
