---
rank: 18
slug: dual-momentum-sector-rotation
title: "Dual-Momentum Sector Rotation"
asset_class: "ETFs"
style: "relative + absolute momentum / long-only with flight to safety"
horizon: "1–3 month hold after 6–12 month formation"
instruments: "listed ETFs (equity sector, country, or index)"
---

# 018. Dual-Momentum Sector Rotation

| Field | Value |
|---|---|
| Popularity rank (this kit) | 18 of 101 |
| Why it sits here | Antonacci-style dual momentum applied to sector ETFs. Relative ranking plus a market-trend gate; widely used in tactical ETF sleeves. |
| Aliases | absolute + relative sector momentum |
| Asset class | ETFs |
| Style | relative + absolute momentum / long-only with flight to safety |
| Typical horizon | 1–3 month hold after 6–12 month formation |
| Instruments | listed ETFs (equity sector, country, or index) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Rank sector ETFs by trailing cumulative return. Buy the winners only if a broad-market ETF is itself in an uptrend. Otherwise hold an uncorrelated defensive ETF (Treasuries or gold).

You are betting two things at once. Relative momentum: the sectors that rose over the formation window keep outperforming the laggards for another month. Absolute momentum: when the market itself is below its moving average, that relative rank is being done inside a falling tape, so you do not want the long-only sector book. The defensive name is a flight-to-safety substitute, not a short of the sectors.

You are not shorting sector ETFs in this file. You are not estimating a Fama–French residual (`080`). You are not confirming each winner against *its own* moving average (`079`). The gate here is one market series versus one MA. You are also not claiming the defensive ETF is a hedge that always rises when equities fall; it is a weakly correlated parking spot.

Typical users are tactical ETF allocators and dual-momentum retail/RIA sleeves. Universe is a small listed set: 11 sector SPDRs, or a country ETF panel, plus one market ETF and one defensive ETF. Horizon intuition: 12-month formation, 200-day market MA, 1-month hold. The book can sit 100% in IEF-type paper for months. That is the gate working, not a bug to patch by turning the MA off after a crash.

Whipsaw around the MA is the main operational cost. Delay-1 so month-end ranks do not trade the same close that completed the formation window.

## 2. First principles

Intermediate-horizon returns trend. Inside a sector universe that is the ranking claim: names with high formation return $R^{\mathrm{cum}}_i$ tend to keep outperforming names with low $R^{\mathrm{cum}}_i$ over the next month. That is relative (cross-sectional) momentum.

Absolute momentum is a time-series gate on the market itself. If the market’s own trend is down, the same ranking is being done inside a falling tape, and the long-only sector book inherits that beta. Dual momentum therefore splits the decision:

- If the market is above its moving average, hold the relative winners.
- If not, do not short the sectors in this spec. Move to a defensive ETF whose return is weakly correlated with the market.

You are not estimating a factor model. You are applying a sign gate to a rank book. The gate uses only prices $\le t_2$. If the MA includes the fill close, you traded information you did not have at decision time.

That is the whole strategy. Everything below is how to measure $R^{\mathrm{cum}}$, how to build the MA gate, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | sector (or country) ETFs after liquidity filters |
| $P_i(t)$ | split- and dividend-adjusted ETF price |
| $P(t)$ | broad-market ETF price used for the gate |
| $R^{\mathrm{cum}}_i$ | formation simple return of name $i$ |
| $\mathrm{MA}(T')$ | trailing moving average of $P$ with length $T'$ |
| $k$ | number of winners held (top decile, or top $k$ of a small set) |
| $w_i$ | portfolio weight; this spec is long-only, $w_i\ge 0$ |
| $I$ | gross dollars, $\sum_i w_i=1$ |

Defensive name $d$ is a Treasury or gold ETF treated as a single substitute book, not ranked with the sectors.

## 4. Mathematics

### 4.1 Relative momentum

Formation window $[t_1,t_2]$ of length $T$ that **ends before** the fill. Cumulative simple return:

$$
R^{\mathrm{cum}}_i = \frac{P_i(t_2)}{P_i(t_1)}-1
$$

This is a two-point simple return, not a sum of monthly logs. Missing $P_i(t_1)$ or $P_i(t_2)$ drops the name; filling with zero manufactures a −100% formation return and can dump a live ETF into the bottom of the rank for the wrong reason. Default $T=12$ months. Rank $R^{\mathrm{cum}}_i$ descending. Winners are the top decile, or the top $k$ names when $N$ is a small sector set (11 SPDRs $\Rightarrow$ typically $k=1$ or $2$).

With 11 names, “decile” is not ten percent of a thousand stocks. Document $k$. Changing $k$ from 1 to 3 is a different concentration, not a robustness overlay you can average without saying so.

### 4.2 Absolute-momentum gate

Let $P$ be the broad-market ETF and $\mathrm{MA}(T')$ its trailing average using only prices $\le t_2$.

If the market is in an uptrend, $P>\mathrm{MA}(T')$, hold the winners:

$$
w_i = \frac{1}{k}\quad\text{for }i\text{ in the top }k,\quad w_i=0\text{ otherwise}
$$

Equal weight among winners is the default because the universe is already coarse. Inverse-vol is allowed but not required; a 25% vol energy ETF versus a 12% staples ETF will otherwise dominate. Names outside the top $k$ are flat, including last month’s winner if it fell out of the set.

If the market is not, $P\le\mathrm{MA}(T')$, hold the defensive ETF:

$$
w_d = 1,\qquad w_i=0\text{ for all sector }i
$$

The entire sector book goes to zero. There is no “half risk-off.” If you leak 50% into the old winners when the gate is off, you no longer have dual momentum; you have a blended overlay this file does not specify. The gate is a binary on $P$ versus $\mathrm{MA}(T')$. It is not a smooth allocation in this spec.

### 4.3 Long-only constraint

$$
w_i \ge 0,\qquad \sum_i w_i + w_d = 1
$$

Weights cannot go negative. Cash is only the residual after ADV clips, not a third sleeve. This file does not short sector ETFs. A dollar-neutral sibling lives in `028-sector-momentum-rotation.md`. If you add shorts “because the gate is off,” you have left this spec.

### 4.4 Holding-period P&L

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends.

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

$D_i=I w_i$ and $D_d=I w_d$. The defensive return is part of P&L whenever $w_d=1$. If you mark $d$ at 0 while holding IEF, the backtest lies in every risk-off month. Report net return on gross $I$ (equal to net capital here), Sharpe on non-overlapping holds, and

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

A gate flip from all-sectors to all-defensive is turnover $1$ (one-way). That is intended. Smoothing the gate to cut turnover is a different strategy.

## 5. Step-by-step algorithm

1. **Universe.** Listed sector, country, or index ETFs. Price and ADV above minima. Keep delisted ETFs until the delist date (no survivorship). This step exists so dead sector products that crashed stay in the formation sample until they actually disappear.
2. **Formation.** Compute $R^{\mathrm{cum}}_i$ on $[t_1,t_2]$ with $t_2<t_{\mathrm{fill}}$. Drop names with missing prices on $t_1$ or $t_2$. This step exists to keep the rank causal. Using $t_{\mathrm{fill}}$ as $t_2$ is delay-0.
3. **Rank.** Sort remaining names on $R^{\mathrm{cum}}_i$. Take top decile or top $k$. This step exists because dual momentum still needs a horse; the gate only decides whether to ride it.
4. **Gate.** Compute $\mathrm{MA}(T')$ of the market ETF using data $\le t_2$. Compare to $P(t_2)$. This step exists so a falling market vetoes the long-only rank. An MA that includes the fill bar looks ahead.
5. **Allocate.** If $P>\mathrm{MA}(T')$, equal-weight the winners. Else $w_d=1$. This step exists to implement the binary. Partial allocations are out of spec.
6. **Caps.** Clip each name at a fraction of ADV (default $1\%$). Residual goes to cash, not to a silent extra sector. This step exists so a thin country ETF cannot absorb the whole book.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. This step exists because ETFs still have lots and a cash residual after rounding.
8. **Rebalance.** Monthly. Month-end $t_2$ formation trades the next open or next close (delay-1). This step exists so ranks known after the close are not filled at that same close.

## 6. Execution protocol

- Default fill: next open after month-end ranks are known. Academic delay-0 month-end close-to-close is a backtest choice, not a live book. If you do $X$ = trade the close that completes $R^{\mathrm{cum}}$, the backtest lies.
- Skip a winner that fails the ADV screen; do not replace it with the next rank unless $k$ is defined as “top $k$ after liquidity.” Document which rule you use. Silent replacement inflates backtest occupancy.
- The defensive ETF must itself pass ADV. If it fails, go to cash, not back into sectors against the gate. Overriding the gate because $d$ is halted is how you re-acquire equity beta in a crash.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted ETF closes on the formation and holding windows
- Broad-market ETF series for the MA gate, same delay
- ADV for liquidity filters and impact caps
- AUM / shares outstanding as a capacity diagnostic (not in the signal)

Not used by this spec: book value, earnings, SUE, creation-unit NAV (that is the arb file, not this rotation).

No restatement peeking. Delisted sector ETFs stay until the delist date. If you do $X$ = drop names that later delisted from the whole history, winners look cleaner than they were. If you do $X$ = use a revised split-adjusted history that changes $P(t_1)$ after the fact, $R^{\mathrm{cum}}$ at $t_2$ was not the number you would have computed live. The market MA must be the same product throughout; splicing SPY into a total-return index without documenting it changes the gate.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation $T$ | 12 months | 6 months allowed |
| MA length $T'$ | 200 days | 100–200 typical |
| $k$ / decile | top decile | or top $k$ of a small set |
| hold | 1 month | 1–3 months allowed |
| defensive $d$ | IEF / TLT / GLD-type | pick one; uncorrelated with the market ETF |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.dual_momentum_sector_rotation` with:

1. `cum_return(prices, t1, t2) -> pd.Series` — $R^{\mathrm{cum}}_i$, no look-ahead.
2. `gate(market_price, ma_length) -> bool` — `True` iff $P>\mathrm{MA}(T')$ at $t_2$.
3. `weights(cum_return, gate, k, defensive) -> pd.Series` — $w_i\ge 0$, $\sum w=1$ to `1e-8`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — shares, never live routing.
5. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Whipsaw.** The market oscillates around $\mathrm{MA}(T')$ and the book flips sector $\leftrightarrow$ defensive. Each flip pays two ETF spreads and can sell winners the day before they resume.
- **Sector concentration.** Top $k$ of 11 names is one or two industries. A single energy spike is the whole long book.
- **Defensive failure.** Treasuries fall with the market in a rates shock; gold can dump on the same day the gate fires. The gate does not guarantee a positive $R_d^{\mathrm{fwd}}$.
- **Relative momentum crash.** Winners keep reversing after the rank is set. The gate only asks whether the *market* is up, not whether the winner’s industry is still trending.

## 11. Acceptance tests

- Gate on: two winners, equal $R^{\mathrm{cum}}$ in the top $k$ → $w=1/k$ each, $w_d=0$, $\sum w=1$.
- Gate off: $w_d=1$, all sector weights $0$, regardless of ranks.
- Permuting all prices after $t_2$ must not change $R^{\mathrm{cum}}$ or the gate at $t_2$.
- A name missing $P(t_1)$ is dropped, not filled with $0$.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
