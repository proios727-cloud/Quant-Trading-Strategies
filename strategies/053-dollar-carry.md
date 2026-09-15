---
rank: 53
slug: dollar-carry
title: "Dollar Carry Trade"
asset_class: "foreign exchange"
style: "time-series dollar factor / average forward discount"
horizon: "1–12 month forwards; monthly rebalance"
instruments: "FX spot; FX forwards (typically 1m); G10 and liquid EM pairs"
---

# 053. Dollar Carry Trade

| Field | Value |
|---|---|
| Popularity rank (this kit) | 53 of 101 |
| Why it sits here | Lustig–Roussanov–Verdelhan dollar carry. Times the USD against a basket using the average forward discount; linked to US cyclical conditions. |
| Aliases | dollar factor, average forward-discount timer |
| Asset class | foreign exchange |
| Style | time-series dollar factor / average forward discount |
| Typical horizon | 1–12 month forwards; monthly rebalance |
| Instruments | FX spot; FX forwards (typically 1m); G10 and liquid EM pairs |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Average the cross-section of forward discounts. If the average is positive, go long all foreign currencies versus USD (equal weight). If negative, short all foreign currencies.

You are betting that when US rates are low relative to the rest of the basket ($\bar D>0$), being long foreign versus USD earns the average interest differential plus whatever the dollar actually does — and that this time-series sign continues, rather than being cancelled by an immediate dollar appreciation as UIRP would require. All foreign weights share a sign. It is one bet: USD versus everyone.

You are not ranking high-yield versus low-yield names. That rank version is HML-FX (`027`). Adding a constant to every $D_i$ *does* change $\bar D$ and can flip this book; it must *not* change HML ranks. You are not using US growth prints, recession flags, or NBER dates as inputs. Those are optional diagnostics of why $\bar D$ moves, not a second signal. You are not dollar-neutral in the HML sense.

Typical users are FX factor researchers and overlay desks that want an explicit dollar timer. Universe is G10 ex-USD, all versus USD. Horizon is monthly on 1m forwards (other tenors allowed as separate signals). In a crisis every $D_i$ and every $S_i$ move together; $N$ names are still one bet. Delay-1 on the next fixing after $\bar D$ is known.

## 2. First principles

Each pair versus USD has a forward discount

$$
D_i(t,T) = \ln S_i(t) - \ln F_i(t,T) \approx r_{f,i}-r_{\mathrm{USD}}
$$

Same $D$ as in `006` / `027`, always quoted versus USD. Each term still contains $-r_{\mathrm{USD}}$. Timestamps on $S_i$ and $F_i$ are strictly before the fill. A restated WM print after $t$ does not change $D_i(t)$.

Average them:

$$
\bar D(t,T) = \frac{1}{N}\sum_{i=1}^{N} D_i(t,T) \approx \bar r_f - r_{\mathrm{USD}}
$$

The average of foreign-minus-USD gaps is the basket rate minus the dollar rate. USD itself is **not** in the average: a USD–USD row would be a zero that shrinks $\bar D$ for no economic reason. If one name’s forward is missing, drop it and recompute $\bar D$ and $N$ on the survivors; do not leave a stale $D_i$ in the mean.

$\bar D>0$ means the rest of the world, on average, has higher interest rates than the dollar. Covered interest still prices each forward; uncovered interest says the dollar should appreciate enough to cancel $\bar D$. Dollar carry is the time-series claim that it does not: when US rates are low relative to the basket, being long foreign versus USD earns the average differential plus whatever the dollar actually does.

Empirically $\bar D>0$ more often when the US economy is weak (US rates down). That is a description of the signal, not a second input. The trade uses only $\bar D$. If you splice a GDP print into the sign rule, you have left this spec.

That is the whole strategy. Everything below is the sign rule, the equal-weight basket, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | foreign currencies, all quoted vs USD |
| $S_i, F_i$ | spot and forward, USD per 1 foreign (or a consistent convention) |
| $D_i(t,T)$ | forward discount of $i$ |
| $\bar D(t,T)$ | equal-weight average of $D_i$ |
| $w_i$ | weight on foreign $i$; $w_i>0$ long foreign / short USD |
| $T$ | forward tenor in $\{1,2,3,6,12\}$ months |
| $I$ | gross notional of the foreign basket |

USD itself is **not** in the average. Every pair is vs USD, so including a USD–USD row would be a zero that shrinks $\bar D$.

## 4. Mathematics

### 4.1 Average discount

$$
\bar D(t,T) = \frac{1}{N}\sum_{i=1}^{N} D_i(t,T)
$$

Equal weight across names, not inverse-vol, unless the caller adds a vol target *after* the common sign is set. Default $T=$ 1 month, $N=$ G10 ex-USD. Other tenors in $\{1,2,3,6,12\}$ months are allowed; they are separate signals, not averaged together unless the caller says so. Mixing a 1m $D_i$ with a 12m $D_j$ in one mean is a curve mash, not this timer.

### 4.2 Sign rule

If the average discount is positive, long every foreign forward equally:

$$
\bar D(t,T) > 0 \;\Rightarrow\; w_i = +\frac{1}{N}\quad \forall i
$$

Every survivor gets the same long-foreign weight. There is no high-versus-low split. The whole vector is the dollar-short side of the bet. If $N$ changes because a forward is missing, rebuild $1/N$; do not leave one pair at last month’s weight.

If it is negative, short every foreign forward equally:

$$
\bar D(t,T) < 0 \;\Rightarrow\; w_i = -\frac{1}{N}\quad \forall i
$$

Every survivor is short foreign / long USD. If $\bar D=0$, flat. Default: sign filter only, no magnitude dead-band. A dead-band is allowed if the caller wants fewer flips.

All $w_i$ share a sign. This book is **not** dollar-neutral in the HML sense; it is a single bet on USD versus the basket. Optional: scale the whole vector to a vol target, preserving the common sign. Vol of the *basket*, ending before the fill, not per-name vol that reintroduces a cross-sectional tilt.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = \sum_i N_{\mathrm{fx},i}\bigl(S_i(t+T)-F_i(t,T)\bigr) - \mathrm{costs}
$$

Nine G10 names pay nine spreads. A dollar rally hits every long-foreign leg together. Rebalance when $\bar D$ flips sign, or monthly (default monthly even if the sign is unchanged, so notionals stay equal). Report Sharpe on non-overlapping holds and turnover of the $w$ vector. If you do $X$ = skip the monthly rebalance when the sign is unchanged, notionals drift with spots and the book is no longer equal weight.

## 5. Step-by-step algorithm

1. **Universe.** G10 ex-USD, optionally liquid EM, all vs USD. Drop pegs. This step exists because a peg in the average pulls $\bar D$ without being a tradable dollar factor.
2. **Discounts.** $D_i$ from spot and forwards dated $\le t_2<t_{\mathrm{fill}}$. Drop names with missing $F_i$; recompute $\bar D$ on the survivors. This step exists so a missing forward does not freeze last month’s $D_i$ in the mean.
3. **Average.** Equal-weight $\bar D$. Do not include USD. This step exists because the timer is the *mean* gap versus USD, not a rank.
4. **Sign.** $+1/N$ or $-1/N$ on every survivor, or flat. This step exists to map $\bar D$ into a common-sign basket.
5. **Scale.** Optional vol target on the basket return, not per name. This step exists so inverse-vol cannot sneak an HML tilt into dollar carry.
6. **Blotter.** $N$ forward intents with a common sign. Never live routing. This step exists because all legs are one bet; they should be emitted together.
7. **Rebalance.** Monthly, and on a sign flip if you rebalance intra-month. This step exists to keep equal weights after spots move.
8. **Diagnostics.** Store $\bar D$ next to US recession / growth flags if you want the cyclical story; those flags are not inputs. This step exists so a researcher can plot the story without leaking it into $w$.

## 6. Execution protocol

- Default fill: next fixing after $\bar D$ is known. If you do $X$ = use the same WM print for $D$ and the fill, the backtest lies.
- If one pair’s forward is missing, drop it and rebuild $\bar D$ and $1/N$. Do not leave that pair at last month’s sign while the others flip.
- Bid/ask on every leg: a 9-name G10 basket pays nine spreads. Mid-to-mid P&L overstates the timer.

## 7. Data contract

Required, point-in-time:

- Spot and forwards for each foreign currency vs USD
- Fixing calendar
- Optional realized vol of the equal-weight basket for the vol target

Not used by this spec: US growth prints as a **signal**, equity data, HML quantiles (that is `027`).

If you do $X$ = include USD as a zero row, $\bar D$ is shrunk. If you do $X$ = mix quote conventions, some $D_i$ flip sign and $\bar D$ is garbage. If you do $X$ = rebuild $\bar D_t$ after a WM restatement, the live timer was different. No NBER-date look-ahead in diagnostics that get written back into weights.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenor $T$ | 1 month | also $\{2,3,6,12\}$ |
| $N$ | G10 ex-USD | |
| dead-band | off | sign filter only |
| vol target | off | scales the whole basket |
| rebalance | monthly | plus optional sign-flip |
| delay | 1 fixing | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.dollar_carry` with:

1. `discount(spot, forward) -> pd.Series` — $D_i$, no look-ahead.
2. `average_discount(D) -> float` — $\bar D$, USD excluded.
3. `weights(D) -> pd.Series` — all $+1/N$, all $-1/N$, or all $0$; $\sum\lvert w_i\rvert=1$ when not flat.
4. `blotter(weights, forwards, I) -> list[OrderIntent]` — never live routing.
5. `pnl(notionals, spot_T, forward_entry, costs) -> float` — matches the forward identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **USD trend.** A dollar rally can dominate the interest gap for a long time. The sign rule does not cut the long-foreign book until $\bar D$ itself flips, which is slow.
- **Slow signal.** $\bar D$ flips late around US recessions; the first month of a dollar squeeze is often still long foreign.
- **EM correlation.** In a crisis every $D_i$ and every $S_i$ move together; $N$ names are one bet.
- **Missing short.** This is not HML. There is no offsetting long-USD / short-foreign diversification inside the book.

## 11. Acceptance tests

- All $D_i>0$ → every $w_i=+1/N$, $\sum w_i=+1$.
- All $D_i<0$ → every $w_i=-1/N$, $\sum w_i=-1$.
- Adding a constant to every $D_i$ **does** change $\bar D$ and can flip the common sign (unlike HML ranks).
- Permuting forwards after the decision timestamp must not change $\bar D_t$.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
