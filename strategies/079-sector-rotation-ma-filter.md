---
rank: 79
slug: sector-rotation-ma-filter
title: "Sector Momentum Rotation with MA Filter"
asset_class: "ETFs"
style: "momentum plus trend filter"
horizon: "Same as sector momentum rotation, plus a daily moving-average filter"
instruments: "listed ETFs (equity sector, country, or index)"
---

# 079. Sector Momentum Rotation with MA Filter

| Field | Value |
|---|---|
| Popularity rank (this kit) | 79 of 101 |
| Why it sits here | Same rotation with a moving-average confirmation so winners are not bought in a falling tape. |
| Aliases | sector momentum with MA confirmation |
| Asset class | ETFs |
| Style | momentum plus trend filter |
| Typical horizon | Same as sector momentum rotation, plus a daily moving-average filter |
| Instruments | listed ETFs (equity sector, country, or index) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Run the sector-momentum rank, then trade a winner (loser) only if that ETF also sits above (below) its own moving average. Names that fail the filter go to cash.

You are betting the intersection of two claims. Relative momentum: high trailing $R^{\mathrm{cum}}$ still predicts outperformance versus peers. Absolute momentum *per name*: do not buy a “winner” that only lost less than its peers while its own price is in a downtrend, and do not short a “loser” that is still trading above its own MA. Failed names are cash, not a forced opposite leg.

You are not using a single market ETF gate (`018`). That file asks whether SPY is above its MA; this file asks whether *each* sector ETF is above *its* MA. You are not renormalizing failed weight into the one remaining hot sector unless the caller explicitly asks. Default: three winners filtered to one means that one gets $1/3$ and $2/3$ is cash. You are not claiming the MA removes momentum crashes; it delays re-entry and can whipsaw around the average.

Typical users are sector-rotation sleeves that want a crash veto without going fully dual-momentum. Same 11-SPDR universe as `028`. Horizon: 12-month rank, 200-day MA checked on the rebalance date with data through $t-1$. Near-cash stretches after a crash are a feature.

## 2. First principles

Cross-sectional sector momentum is the rank on formation return

$$
R^{\mathrm{cum}}_i = \frac{P_i(t_2)}{P_i(t_1)}-1
$$

Same two-point simple return as `028`, window ending before the fill. This rank can still put you long a “winner” whose own price is in a downtrend: the name only lost less than its peers. That is the hole the MA is meant to patch. Time-series trend on the same ETF says do not buy $i$ unless $P_i$ is above its trailing average, and do not short $i$ unless $P_i$ is below it.

The intersection is the trade. Failed names are cash, not a forced opposite leg. The book can therefore go near-cash for long stretches after a crash, which is a feature of the filter, not a bug to patch by turning the MA off. If you turn the MA off after the fact because cash “missed the rebound,” you peeked at the rebound.

That is the whole strategy. Everything below is the AND rule, the cash residual, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | sector ETFs after liquidity filters |
| $P_i(t)$ | split- and dividend-adjusted price |
| $R^{\mathrm{cum}}_i$ | formation simple return |
| $\mathrm{MA}_i(T')$ | trailing average of $P_i$, length $T'$ |
| $Q_H, Q_L$ | top and bottom momentum groups |
| $w_i$ | signed weight |
| $w_{\mathrm{cash}}$ | residual after filters |
| $I$ | gross dollars allocated to ETFs plus cash |

## 4. Mathematics

### 4.1 Momentum rank

Same formation as `028`: window $[t_1,t_2]$ of length $T=12$ months, $t_2$ before the fill. Rank $R^{\mathrm{cum}}_i$. Top/bottom decile, or $k$ of $N$ (default 3 of 11). The MA does not replace this rank; it vetoes members of $Q_H$ and $Q_L$. Computing $R^{\mathrm{cum}}$ through the fill bar is still look-ahead, filter or not.

### 4.2 MA confirmation

Using prices $\le t_2$ (on the rebalance date, data through $t-1$ for delay-1):

Buy a top-decile ETF only if it is above its MA:

$$
i\in Q_H \;\text{and}\; P_i > \mathrm{MA}_i(T') \;\Rightarrow\; \text{eligible long}
$$

Both clauses are required. Rank without MA is `028`. MA without rank is a single-name trend overlay (`037`) on sector ETFs, not this file. $P_i$ and $\mathrm{MA}_i$ use data through $t_2$ / $t-1$, never the fill close.

Short a bottom-decile ETF only if it is below its MA:

$$
i\in Q_L \;\text{and}\; P_i < \mathrm{MA}_i(T') \;\Rightarrow\; \text{eligible short}
$$

A laggard that has already turned up and sits above its MA is not shorted here. Names that fail the AND go to cash. Long-only mode ignores $Q_L$. Dollar-neutral mode still requires both eligible legs; if one leg is empty after the filter, do not keep the other as a one-sided sector bet — cash out or rebuild as documented, default cash out.

### 4.3 Weights

Equal weight (or $1/\sigma_i$) on eligible longs, and on eligible shorts if dollar-neutral. Renormalize so that long-only has $\sum w_i=1$ on remaining names **or** $\sum w_i + w_{\mathrm{cash}}=1$ if you keep failed weight in cash (default: cash, do not renormalize into the two remaining hot sectors unless the caller asks). Default here: **do not** renormalize away the cash. If three winners are filtered to one, that one gets $1/3$ of gross and $2/3$ is cash, not $100\%$ in one sector.

That default is load-bearing. Renormalizing into one survivor is a concentrated sector bet that the MA was supposed to avoid. `renormalize=False` is the kit default in the agent contract.

### 4.4 Holding-period P&L

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Cash marks to the T-bill series if modelled, else $0$. A large cash residual with a 0 mark in a hiking cycle understates the parking lot. Short ETFs need locate. Turnover includes the cash bucket: moving from sectors to cash is real turnover, not a free flatten.

## 5. Step-by-step algorithm

1. **Universe.** Same as `028`. This step exists so the MA overlay does not secretly change the sector set.
2. **Rank.** $R^{\mathrm{cum}}_i$ on $[t_1,t_2]$. Form $Q_H$ and optional $Q_L$. This step exists because the MA is a veto, not a replacement sort.
3. **MA.** $\mathrm{MA}_i(T')$ with $T'=200$ days, data through $t_2$ (delay-1: through $t-1$ on the rebalance date). This step exists to keep the average causal. An MA that includes the fill close is delay-0.
4. **Filter.** AND with $P_i>\mathrm{MA}_i$ for longs and $P_i<\mathrm{MA}_i$ for shorts. This step exists to drop winners that are still in a downtrend and losers that have already turned.
5. **Allocate.** Equal weight inside eligible names **without** stuffing failed weight into survivors (default). Residual is cash. This step exists so concentration cannot sneak back in through renormalization.
6. **Dollar-neutral.** If shorts are empty after the filter, flatten; do not remain long-only by accident. This step exists so a missing short leg is not silent equity beta.
7. **Blotter.** Shares, locates, intents. Never live routing. This step exists because shorts still need locate even after the MA passes.
8. **Rebalance.** Monthly ranks, daily MA allowed but default is check MA on the rebalance date only. This step exists so a daily MA check does not become a daily reconstitution unless the caller asked for that turnover.

## 6. Execution protocol

- Check the MA on the rebalance date using data through $t-1$. Do not use the same close you trade. If you do $X$ = include today’s close in the MA and fill today, the backtest lies.
- Filter delays re-entry after crashes. That is intended. Turning it off after you see the rebound is look-ahead.
- If ADV fails, the name is ineligible even if rank and MA pass.

## 7. Data contract

Required, point-in-time:

- Adjusted ETF closes for formation and for the MA
- ADV, borrow for shorts
- Cash / T-bill series if $w_{\mathrm{cash}}$ is marked

Not used by this spec: a single market ETF gate (that is `018`), book value, earnings, NAV arb.

If you do $X$ = compute $\mathrm{MA}_i$ on the full sample including future prices, the filter peeked. If you do $X$ = drop ETFs that later delisted, crash names disappear from $Q_H$. If you do $X$ = renormalize after the fact because cash lagged, you peeked at the rebound. Frozen adjusted closes; MA uses $\le t-1$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation $T$ | 12 months | as in `028` |
| MA $T'$ | 200 days | 100–200 typical |
| $k$ | 3 of 11 | or decile |
| cash residual | on | do not renormalize into survivors |
| mode | long-only | dollar-neutral optional |
| delay | 1 bar | MA uses $\le t-1$ |

## 9. Agent implementation contract

Build a Python module `strategies.sector_rotation_ma_filter` with:

1. `cum_return(prices, t1, t2) -> pd.Series` — $R^{\mathrm{cum}}_i$, no look-ahead.
2. `ma_ok(prices, Tprime, side) -> pd.Series[bool]` — $P>\mathrm{MA}$ for longs, $P<\mathrm{MA}$ for shorts, data $\le t_2$.
3. `weights(cum_return, ma_ok, mode, k, renormalize=False) -> pd.Series` — includes `cash` if `renormalize=False`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.
5. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Delayed re-entry.** The MA keeps you in cash after the first month of a new bull.
- **Near-cash stretches.** Opportunity cost versus always-on `028`.
- **Whipsaw.** Price oscillates around $\mathrm{MA}(T')$ and eligible sets churn.
- **Accidental beta.** Renormalizing into one surviving winner is a concentrated sector bet; default is not to do that.

## 11. Acceptance tests

- Name in $Q_H$ but $P<\mathrm{MA}$ → not long; its default weight sits in cash.
- Name in $Q_L$ but $P>\mathrm{MA}$ → not short.
- Three winners, two fail MA, `renormalize=False` → one name at $1/3$, cash $2/3$.
- Permuting prices after $t_2$ must not change ranks or MA flags at $t_2$.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
