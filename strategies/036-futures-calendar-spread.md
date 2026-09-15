---
rank: 36
slug: futures-calendar-spread
title: "Futures Calendar Spread"
asset_class: "futures / commodities"
style: "term-structure / reduced-beta spread"
horizon: "Days to the front expiry; then roll"
instruments: "listed futures"
---

# 036. Futures Calendar Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 36 of 101 |
| Why it sits here | Standard commodity and rates relative-value: near vs deferred month. Cuts raw market beta to focus on the curve. |
| Aliases | near-deferred spread, calendar RV |
| Asset class | futures / commodities |
| Style | term-structure / reduced-beta spread |
| Typical horizon | Days to the front expiry; then roll |
| Instruments | listed futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Trade two expiries of the same root. Bull spread: long near, short deferred (a bet on tightness / low supply at the front). Bear spread: the opposite.

You are betting on the *shape* of the curve: whether the front month gains or loses on the back. A bull calendar profits if the near tightens versus the deferred (more backwardation, less contango). That is often a tightness / low-supply view at the front. A bear calendar is the opposite shape view. Near-month typically reacts more to supply and demand shocks than deferred, which is why a 1:1 contract spread still has some residual beta.

You are not taking an outright long in the commodity. A parallel jump in the spot still leaks a little through the two deltas, so do not call the book market-neutral. You are not trading a crush, crack, or heat-rate spread: those are different roots. You are not holding into first notice as if it were the liquid calendar. Energy and ags have harvest / injection calendars that rates books do not.

Typical users are commodity RV desks and rates curve books that DV01-match instead of 1:1 contracts. Horizon is days to first notice, then an obligatory roll onto the next pair. Delay-1: choose the pair on session $t$ data, fill next session. Both legs are a package; a one-legged fill is a directional residual and must be flattened in the simulator.

## 2. First principles

Cost-of-carry prices a futures on the same underlying at two expiries $T_1<T_2$. With rate $r$, storage $u$, and convenience yield $y$,

$$
F(t,T) \approx S(t)\,e^{(r+u-y)(T-t)}
$$

This is the frictionless term-structure map from spot to a given expiry. Storage and convenience yield are why commodity curves are not just $e^{r(T-t)}$. The formula is the reason two months of the same root cannot wander independently: they share $S(t)$. It is not a trading signal by itself. Using a later $S$ to back out a historical $F(t,T)$ is look-ahead.

The two prices are not free to wander independently. Their ratio is

$$
\phi = \frac{P_1}{P_2}
$$

$\phi$ is greater than $1$ when the curve is in backwardation (near rich to deferred) and less than $1$ in contango. $\phi$ is a diagnostic and, if the caller wants, a rule input. It uses only the two contract prices dated $\le t_{\mathrm{fill}}$. A parallel jump in $S$ moves both $F(t,T_1)$ and $F(t,T_2)$ in the same direction; a 1:1 contract spread cancels most of that beta and leaves the residual that is the front-versus-back wedge.

A **bull calendar** buys the near and sells the deferred: it profits if the front gains on the back (more backwardation, less contango) — the tightness / low-supply view. A **bear calendar** reverses the legs.

That is the whole strategy. Everything below is how to match multipliers, when to roll, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P_1, P_2$ | near-month and deferred-month futures prices, same root |
| $T_1<T_2$ | their expiries |
| $\phi=P_1/P_2$ | front/second price ratio; backwardation if $\phi>1$ |
| $m$ | contract multiplier (same for both months unless noted) |
| $Q$ | number of near contracts; deferred is $-Q$ in a 1:1 bull |
| $R_i$ | excess return of month $i$ over the strategy bar |
| $w_i$ | signed notional weights with $\sum_i\lvert w_i\rvert=1$ unless DV01-scaled |
| $d_{\mathrm{FND}}$ | days to first notice (or last trade) on the near |

## 4. Mathematics

### 4.1 Legs

Bull calendar, 1:1 in contracts:

$$
Q_1 = +Q,\qquad Q_2 = -Q
$$

Long $Q$ near, short $Q$ deferred. Same multiplier assumed. This is the default commodity spec. It is not a DV01-zero book unless the two months happen to have the same dollar duration, which they usually do not in rates.

Bear calendar:

$$
Q_1 = -Q,\qquad Q_2 = +Q
$$

Signs flipped. The $\phi$ rule or the caller’s standing view picks the side before the blotter. Switching side after you have seen the hold’s $\Delta P$ is look-ahead.

Ratio 1:1 in contracts is the default. Rates books may replace this with a DV01 match so $\sum Q_i m_i\,\mathrm{DV01}_i=0$. Energy heat-rate or crush spreads are out of scope; they are not the same root.

### 4.2 Ratio diagnostic

$$
\phi = \frac{P_1}{P_2}
$$

Same $\phi$ as in first principles. $\phi>1$ is backwardation. The signal in this spec can be a standing bull/bear choice, or a rule on $\phi$ (for example bull when $\phi$ is below a threshold you expect to mean-revert, bear when $\phi$ is stretched). Whichever rule you pick, it uses only $\phi$ and term-structure dated $\le t_{\mathrm{fill}}$. If “front” is labelled with $t+1$ volume, $\phi_t$ used a month that was not front at $t$.

### 4.3 Reduced beta

A parallel $dS$ moves both futures by approximately the carry-adjusted delta. The 1:1 spread’s notional beta in the underlying is proportional to

$$
mQ\bigl(\partial_S F(t,T_1)-\partial_S F(t,T_2)\bigr)
$$

The two partials are close but not equal: the near has a larger carry-adjusted sensitivity to $S$ in the usual map. The difference is much smaller than $mQ\,\partial_S F(t,T_1)$ alone. It is not zero. Do not call the book “market-neutral.” A squeeze in one month independently blows this residual up; that is a risk, not a rounding error.

### 4.4 Holding-period P&L

Futures mark on variation margin. For a 1:1 bull with multiplier $m$,

$$
\mathrm{P\&L} = Q m \bigl[(P_{1,t+1}-P_{1,t})-(P_{2,t+1}-P_{2,t})\bigr] - \mathrm{costs}
$$

If both months mark by the same tick, the difference is zero and P&L is $-$costs. If the near rallies and the deferred does not, the bull earns $Q m$ times that wedge. Include roll P&L explicitly when the near is rolled to a new pair. Report P&L in currency, not as a return on the full notional of both legs. Gross notional $I=\lvert Q m P_1\rvert+\lvert Q m P_2\rvert$ is the capacity clock, not the margin.

A missing deferred price cannot be filled with the generic: that would emit a naked near. If you do $X$ = report return on $I$ as if it were fully funded cash, Sharpe is not comparable to equity files in this kit.

## 5. Step-by-step algorithm

1. **Root.** One listed futures family. Same multiplier unless the contract spec says otherwise. This step exists so you do not mix CL with HO and call it a calendar.
2. **Months.** Near vs next, or near vs $n$th. Drop the near when $d_{\mathrm{FND}}$ is below the filter (liquidity / first notice). This step exists because the liquid calendar is not the same trade as a notice-month position.
3. **Side.** Bull ($+Q,-Q$) or bear ($-Q,+Q$), from the $\phi$ rule or from a standing view documented by the caller. This step exists so the sign is chosen from data $\le t$, not from the hold.
4. **Scale.** Default 1:1 contracts. Optional DV01 scale for rates. Match units before emitting. This step exists because a 1:1 rates calendar is a duration residual, not a pure curve bet.
5. **Caps.** Skip if either month fails an ADV / open-interest floor. Do not pair a liquid front with a thin deferred. This step exists so the “cheap” back month is actually tradable.
6. **Roll.** Before first notice or before a documented liquidity drop, flatten the old near and open the new pair. The roll is not optional because $\phi$ is unchanged. This step exists because holding into notice is a delivery/inventory trade.
7. **Blotter.** Whole contracts, intents only. Never live routing. This step exists to keep both legs a package in the simulator.
8. **Seasonals.** Energy and ags have harvest / injection calendars; do not treat those windows as generic financials. This step exists so a winter nat-gas curve is not sized like a Eurodollar calendar.

## 6. Execution protocol

- Default fill: next session after the pair is chosen. Both legs are a package; a one-legged fill is a directional residual and must be flattened in the simulator. If you do $X$ = keep the filled near when the deferred misses, you are outright long the commodity.
- Watch limit moves. A locked near and a still-trading deferred is not a quoted spread.
- Calendar-spread options as tail hedges are out of scope.

## 7. Data contract

Required, point-in-time:

- Contract-level prices for the two months, not only a generic
- Volumes, open interest, first-notice and last-trade dates
- Multipliers and tick sizes
- Term structure sufficient to compute $\phi$

Not used by this spec: equity fundamentals, FX discounts, COT (optional, off).

No look-ahead on which month is “front”: that flag is a function of the calendar at $t$, not of $t+1$ volume. If you do $X$ = pick the front with tomorrow’s open interest, $\phi_t$ used a pairing you could not have known. If you do $X$ = stitch a generic and treat it as $P_2$, you no longer have a calendar. Freeze notice dates from the exchange calendar as of $t$; a later contract-spec change does not rewrite $d_{\mathrm{FND}}$ at $t$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| pair | near vs next | or near vs $n$th |
| ratio | 1:1 contracts | DV01 optional for rates |
| max days-to-FND | caller-set | roll before the floor |
| side | caller-set | bull / bear / $\phi$ rule |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.futures_calendar_spread` with:

1. `phi(P1, P2) -> float` — $\phi=P_1/P_2$, no look-ahead.
2. `legs(side, Q, dv01=None) -> tuple[int, int]` — $(Q_1,Q_2)$, 1:1 or DV01-matched.
3. `blotter(legs, prices, multiplier) -> list[OrderIntent]` — both legs together, never live routing.
4. `pnl(Q, m, dP1, dP2, costs) -> float` — matches $Qm[(\Delta P_1)-(\Delta P_2)]-\mathrm{costs}$ for a bull.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Squeeze / corner.** One month independently blows out; the “reduced beta” story dies.
- **Limit moves.** One leg marks, the other does not. Variation-margin P&L then looks like an outright.
- **Roll.** Holding into first notice is not the same trade as the liquid spread.
- **Seasonals.** Ags and energy curves are not rates curves.

## 11. Acceptance tests

- Bull, $Q=1$, $\Delta P_1=\Delta P_2$ → P&L $=-\mathrm{costs}$ (parallel mark cancels).
- Bull, $\Delta P_1=+x$, $\Delta P_2=0$ → P&L $=Q m x-\mathrm{costs}$.
- $\phi$ uses only $P_1,P_2$ at $t$; permuting $t+1$ prices must not change $\phi_t$.
- A missing deferred price aborts the pair; it does not emit a naked near.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
