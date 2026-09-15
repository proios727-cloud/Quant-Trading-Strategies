---
rank: 28
slug: sector-momentum-rotation
title: "Sector Momentum Rotation"
asset_class: "ETFs"
style: "cross-sectional momentum / sector ETFs"
horizon: "Formation 6–12 months; hold 1–3 months"
instruments: "listed ETFs (equity sector, country, or index)"
---

# 028. Sector Momentum Rotation

| Field | Value |
|---|---|
| Popularity rank (this kit) | 28 of 101 |
| Why it sits here | Industry/sector momentum (Moskowitz–Grinblatt and follow-ons) implemented with sector ETFs instead of stock baskets. |
| Aliases | industry momentum, sector ETF momentum |
| Asset class | ETFs |
| Style | cross-sectional momentum / sector ETFs |
| Typical horizon | Formation 6–12 months; hold 1–3 months |
| Instruments | listed ETFs (equity sector, country, or index) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Overweight sectors with high trailing ETF cumulative return; underweight (or short) laggards. The same sort can be run long-only (top decile) or dollar-neutral (top versus bottom).

You are betting that industry portfolios trend: a sector ETF that beat its peers over the last $T$ months tends to keep beating them over the next month. The grain is the ETF, not the underlying stocks. Long-only holds the winners. Dollar-neutral holds winners versus losers with net zero and gross one.

You are not applying a market-trend gate (`018`) or a per-name MA veto (`079`). There is no flight-to-IEF when SPY is below its 200-day. You are not ranking Jensen $\alpha$ (`080`). You are not fading a one-day IBS print (`081`). Skip-month, the equity-microstructure convention, is optional here and off by default because ETF closes do not have the same one-month reversal microstructure as individual stocks.

Typical users are sector-rotation sleeves and industry-momentum replications that want 11 tickers instead of 500 names. Horizon intuition: 12-month formation, 1-month hold, delay-1 next open. Three of eleven sectors is concentrated by design. ETF premium versus NAV is tracking error in this file, not a signal (`085`).

## 2. First principles

Industry portfolios trend. A sector that outperformed its peers over the last $T$ months tends to keep outperforming over the next month. Write the formation simple return

$$
R^{\mathrm{cum}}_i = \frac{P_i(t_2)}{P_i(t_1)}-1
$$

Two-point simple return on split- and dividend-adjusted ETF prices. Window $[t_1,t_2]$ ends before the fill. Missing prices drop the name; a zero fill creates a fake −100% loser. This $R^{\mathrm{cum}}$ is the sort key, not a forecast of next month’s exact return.

and the claim is

$$
\mathbb{E}[R_{i,t+1}^{\mathrm{fwd}}-R_{j,t+1}^{\mathrm{fwd}} \mid R^{\mathrm{cum}}_i>R^{\mathrm{cum}}_j] > 0
$$

The object is a *spread* of forward returns, not a market timer. Ranking $i$ against $j$ is the whole cross-section. Names in the middle of the rank are flat. Skip-month (dropping the most recent month) is the equity-microstructure convention; at ETF grain it is optional and off by default. Turning skip on without documenting it mixes this file with `001`’s stock convention.

You are ranking $i$ against $j$, not timing each ETF on its own sign. That sign timer is `019` / `007`.

That is the whole strategy. Everything below is how to turn the rank into a long-only or a dollar-neutral book, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | sector ETFs after liquidity filters |
| $P_i(t)$ | split- and dividend-adjusted price |
| $R^{\mathrm{cum}}_i$ | formation simple return on $[t_1,t_2]$ |
| $Q_H, Q_L$ | top and bottom deciles (or top/bottom $k$ of a small set) |
| $w_i$ | signed weight |
| $\sigma_i$ | vol for inverse-vol weights |
| $I$ | gross dollars |

Long-only: $w_i\ge 0$, $\sum_i w_i=1$. Dollar-neutral: $\sum_i w_i=0$, $\sum_i \lvert w_i\rvert=1$.

## 4. Mathematics

### 4.1 Formation return

Window $[t_1,t_2]$ of length $T$ (default 12 months) ending before the fill:

$$
R^{\mathrm{cum}}_i = \frac{P_i(t_2)}{P_i(t_1)}-1
$$

Same identity as in first principles, restated so the algorithm can cite one place. Optional skip: end the window one month before $t_2$ so the most recent month is not in the sort. Default: no skip. If skip is on, $t_2$ in this formula is the skipped endpoint, still strictly before the fill. Using the fill close as $t_2$ is delay-0.

### 4.2 Rank books

Sort on $R^{\mathrm{cum}}_i$. With 11 sector SPDRs, “decile” is not literal: take the top $k$ and bottom $k$ (default $k=3$).

Long-only: buy $Q_H$, equal weight (or $\propto 1/\sigma_i$), hold.

$$
w_i = \frac{1}{n_H}\quad i\in Q_H,\qquad w_i=0\text{ else}
$$

Every winner gets the same capital. Laggards are not shorted in this mode. $n_H$ is the count after liquidity drops. If ADV knocks out a winner, either reduce $n_H$ or replace from the next rank — pick one rule and document it. Silent replacement inflates occupancy.

Dollar-neutral: buy $Q_H$, short $Q_L$, each leg gross $1/2$:

$$
w_i = \frac{1}{2n_H}\quad i\in Q_H,\qquad w_i = -\frac{1}{2n_L}\quad i\in Q_L
$$

Net zero, gross one, middle names flat. Inverse-vol: replace $1/n$ by $1/\sigma_i$ inside the leg, then rescale the leg. $\sigma_i$ ends at $t_2$. If locate fails on a short, rebuild $Q_L$; do not keep the longs and skip the shorts. That leftover is residual sector beta.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

$D_i=I w_i$. $R_i^{\mathrm{fwd}}$ is the simple return from fill to next rebalance, including dividends. You earn the next month’s ETF path, not $R^{\mathrm{cum}}$ again. Short ETFs require locate; borrow fees sit in costs. If borrow is omitted, dollar-neutral paper P&L is too high. Report Sharpe on non-overlapping holds and

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

Names migrating in and out of $Q_H$/$Q_L$ drive turnover. A 3-month hold should be overlapping 1-month books or a true 3-month reconstitution — pick one. Mixing them double-counts.

## 5. Step-by-step algorithm

1. **Universe.** Sector SPDRs or GICS ETFs. ADV minimum. Keep delisted names until delist date. This step exists so industry ETFs that died after a crash remain in the sample until they actually delist.
2. **Formation.** $R^{\mathrm{cum}}_i$ on $[t_1,t_2]$, $t_2<t_{\mathrm{fill}}$. Drop missing prices; do not fill with zero. This step exists to keep the rank honest. A zero fill manufactures a loser.
3. **Rank.** Top/bottom decile, or $k$ of $N$ (default 3 of 11). This step exists because “decile” of 11 names is not 10%. $k$ is a parameter, not a metaphor.
4. **Mode.** Long-only or dollar-neutral, chosen once per run. This step exists so tests know which budget identity to check. Switching mode mid-sample is two strategies.
5. **Weights.** Uniform within legs, or $1/\sigma_i$. Enforce the constraint of the chosen mode. This step exists to turn a rank into dollars.
6. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV. After clipping a short, rebuild the short leg or cash-out the residual; do not silently drop shorts and keep longs. This step exists to stop a residual-long book from masquerading as dollar-neutral.
7. **Blotter.** Shares, lots, intents. Locate on every short. This step exists because some sector ETFs are harder to borrow than the stocks inside them.
8. **Rebalance.** Monthly reconstitution, delay-1. This step exists so month-end ranks fill the next session.

## 6. Execution protocol

- Default fill: next open after month-end ranks. Delay-0 close-to-close is research-only. If you do $X$ = trade the close that completes $R^{\mathrm{cum}}$, the backtest lies.
- Some sector ETFs are harder to borrow than the underlying stocks. If locate fails, drop the name and rebuild $Q_L$ (dollar-neutral) or skip it (long-only).
- ETF premium/discount versus NAV is tracking error, not a signal in this file. Treating a discount as “cheap laggard momentum” mixes this spec with `085`.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted ETF closes
- ADV for filters and caps
- Borrow availability and fees for any short
- AUM as a capacity diagnostic

Not used by this spec: book value, earnings, creation-unit NAV, a market MA gate.

If you do $X$ = drop ETFs that later closed, industry momentum looks cleaner than live. If you do $X$ = use unadjusted closes across a split, $R^{\mathrm{cum}}$ is garbage. If you do $X$ = compute ranks at $t$ with $t$’s return included, you skipped the delay. Frozen point-in-time adjusted prices; no restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation $T$ | 12 months | 6 months allowed |
| skip month | off | equity-momentum convention, optional |
| hold | 1 month | 1–3 months allowed |
| $k$ / decile | 3 of 11, or top/bottom decile | |
| mode | long-only | dollar-neutral optional |
| weights | equal | or $1/\sigma_i$ |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.sector_momentum_rotation` with:

1. `cum_return(prices, t1, t2) -> pd.Series` — $R^{\mathrm{cum}}_i$, no look-ahead.
2. `weights(cum_return, mode, k, sigma=None) -> pd.Series` — long-only $\sum w=1$, $w\ge 0$; or dollar-neutral $\sum w=0$, $\sum\lvert w\rvert=1$, to `1e-8`.
3. `blotter(weights, prices, I, lot, borrow) -> list[OrderIntent]` — never live routing; refuse names with no locate if $w_i<0$.
4. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Industry momentum crashes.** Crowded winners reverse together. Three sectors can all be long the same macro factor.
- **Concentration.** Three of eleven sectors is not a diversified equity book.
- **ETF premium/discount.** The traded price is not NAV; large discounts look like “laggards” even when the industry did not underperform.
- **Short-leg failure.** Losing locates turns dollar-neutral into residual-long sector beta.

## 11. Acceptance tests

- Long-only, two names in $Q_H$ → $w=1/2$ each, others $0$, $\sum w=1$.
- Dollar-neutral, $n_H=n_L=2$ uniform → each long $+1/4$, each short $-1/4$, $\sum w=0$, $\sum\lvert w\rvert=1$.
- Permuting prices after $t_2$ must not change ranks at $t_2$.
- A missing locate on one short, dollar-neutral mode: rebuild or cash-out; the long leg is not left unhedged by silence.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
