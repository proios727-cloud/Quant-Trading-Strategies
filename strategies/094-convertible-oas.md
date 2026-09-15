---
rank: 94
slug: convertible-oas
title: "Convertible Option-Adjusted Spread Pair"
asset_class: "convertibles"
style: "relative value / two converts of one issuer"
horizon: "Until OAS convergence or a corporate event"
instruments: "two convertible bonds of the same issuer"
---

# 094. Convertible Option-Adjusted Spread Pair

| Field | Value |
|---|---|
| Popularity rank (this kit) | 94 of 101 |
| Why it sits here | Long high-OAS convert, short low-OAS convert of the same issuer; profit if OAS gap closes. |
| Aliases | OAS pair, convert relative value, same-issuer convert basis |
| Asset class | convertibles |
| Style | relative value / two converts of one issuer |
| Typical horizon | Until OAS convergence or a corporate event |
| Instruments | two convertible bonds of the same issuer |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Two convertible bonds of the same issuer share credit and, to first order, the same equity. What should not persist is a gap in option-adjusted spread (OAS): the parallel Treasury-curve shift that equates the model convertible price to the market. Buy the cheap (high-OAS) name, sell the rich (low-OAS) name, and match notionals on delta or on dirty present value so the book is a spread, not two separate convert bets.

You are fading the OAS gap. You are not taking issuer credit as a directional view, and you are not taking a naked stock view. Same issuer cancels most of the credit residual only if both names still exist, still convert into the same equity, and are priced with the same frozen model. A pair that is “cheap versus rich” only because one leg’s vol or call schedule was updated after the other’s snapshot is not this strategy.

The hold is until the gap converges inside a cost band, or until a call, put, takeout, or credit event breaks one leg. Liquidity is not symmetric: the rich name is often the one you must short, and a missing locate on that leg leaves a naked long cheap convert. That leftover is convert arb without a hedge, which this file refuses. Solving OAS off the fill print, or retuning vol on the cheap leg because $g$ still looks wide, is look-ahead dressed as relative value.

## 2. First principles

As in convert arb, each convertible decomposes into a straight-bond present value plus an embedded conversion option:

$$
P_C = P_B + V
$$

$P_B$ is the PV of promised coupons and principal on a **shifted** Treasury curve. $V$ is the conversion option on that same curve (and the same credit/equity model). The decomposition is inside one model, used on both names. If you price $A$ with a binomial and $B$ with a closed form, the OAS gap is a model gap, not a market gap. Callability and credit sit in the same place on both legs so that $s$ is comparable.

Market price $P_C^{\mathrm{mkt}}$ will not equal the unshifted model. OAS is the parallel shift $s$ of the Treasury curve that restores equality. Iterate $s$ until the model option equals the market residual above the bond floor:

$$
V(s) = P_C^{\mathrm{mkt}} - P_B(s)
$$

Raising $s$ cheapens the bond floor and typically cheapens the option on that curve, so the right-hand side (market minus a smaller $P_B$) grows while the left-hand side falls until they meet. If they never meet inside a documented bracket, there is no OAS for that name and the pair is dropped. $P_C^{\mathrm{mkt}}$ is the dirty price at $t-\varepsilon$; using a later print to solve $s$ and an earlier print to fill is look-ahead.

Equivalently, the shifted model price matches the market:

$$
P_B(s) + V(s) = P_C^{\mathrm{mkt}}
$$

That shift $s$ is the OAS. A larger $s$ means a larger discount rate, hence a cheaper convert. The two writings are the same root; pick one solver residual and keep it. OAS is quoted as a parallel shift of the Treasury curve used by the model, not as a Z-spread on a credit curve you swapped in after the fact. Cross-sectionally:

- high OAS $\Rightarrow$ cheap $\Rightarrow$ **long**
- low OAS $\Rightarrow$ rich $\Rightarrow$ **short**

Same issuer cancels most of the credit residual. If the two names’ equity deltas differ, a small stock overlay (or a notional match on delta) removes the leftover equity. Remaining maturity, coupon, and callability will not cancel; those residuals are why a pair can stay open after the headline credit has not moved.

That is the whole strategy. Everything below is how to solve for $s$, how to match notionals, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $A,B$ | two converts of the same issuer |
| $P_C$ | model convertible price |
| $P_C^{\mathrm{mkt}}$ | market dirty price |
| $P_B$ | straight-bond PV on the shifted curve |
| $V$ | embedded conversion option |
| $s$ | parallel Treasury-curve shift (OAS) |
| $\mathrm{OAS}_A, \mathrm{OAS}_B$ | solved shifts for each name |
| $\Delta_A, \Delta_B$ | model equity deltas (per bond) |
| $N_A, N_B$ | signed bond notionals (positive = long) |
| $\varepsilon_{\mathrm{OAS}}$ | bisection tolerance on $s$ |

## 4. Mathematics

### 4.1 OAS solver

Freeze the model (vol, credit, borrow, call schedule, dividends) at $t-\varepsilon$. For a candidate parallel shift $s$, reprice $P_B(s)$ and $V(s)$. The root is the $s$ that satisfies

$$
V(s) = P_C^{\mathrm{mkt}} - P_B(s)
$$

Solve by bisection (or a safeguarded Newton) until the price residual is inside $\varepsilon_{\mathrm{OAS}}$. OAS is not unique if the model is misspecified or if $V$ is not monotone in $s$; document the bracket and refuse a trade if no root exists. Both names must use the same unshifted Treasury curve, the same vol engine, and the same credit input dated $\le t-\varepsilon$. Retuning vol on $A$ because the pair still looks wide is a different strategy.

### 4.2 Pair signal

For names $A$ and $B$ of the same issuer,

$$
g = \mathrm{OAS}_A - \mathrm{OAS}_B
$$

If $g > 0$, $A$ is cheap relative to $B$: long $A$, short $B$. If $g < 0$, reverse. Flat if $\lvert g \rvert$ is inside a cost band. The band must include expected bid/ask on both converts, borrow on the short, and a buffer for solver noise at $\varepsilon_{\mathrm{OAS}}$. A gap that exists only on delay-0 prints is research-only.

### 4.3 Notional match

Two hedge modes.

**Delta-neutral.** Match equity exposure so the pair’s net delta is zero:

$$
N_A \Delta_A + N_B \Delta_B = 0
$$

with gross $\lvert N_A \rvert P_A^{\mathrm{mkt}} + \lvert N_B \rvert P_B^{\mathrm{mkt}} = I$. Same-sign deltas (both long equity, typical for converts) imply opposite bond signs, which is what the OAS signal already wants. $\Delta_A$ and $\Delta_B$ come from the same frozen snapshot as the OAS solves; do not hedge with a later delta. After lot rounding the identity will not be exact — residual shares go to a stock overlay or a cash bucket, not into a silent directional stub.

**Cash-neutral.** Match dirty PV:

$$
N_A P_A^{\mathrm{mkt}} + N_B P_B^{\mathrm{mkt}} = 0
$$

and the same gross $I$. Residual equity/credit must then be hedged separately if $\Delta_A \neq \Delta_B$. Cash-neutral is not “safer”; it is a different residual. If you pick cash-neutral and skip the stock overlay, you have a leftover equity bet this file does not authorize.

### 4.4 Holding-period P&L

$$
\mathrm{P\&L} = N_A \Delta P_A^{\mathrm{mkt}} + N_B \Delta P_B^{\mathrm{mkt}} + \mathrm{coupons} - \mathrm{borrow} - \mathrm{financing} - \mathrm{costs}
$$

Marks are dirty. Coupons accrue on both legs; the short convert pays the coupon. Borrow and financing include the short bond locate and any stock overlay. Exit when $g$ converges inside the cost band, or on a call, put, or takeout of either leg. A corporate event is not “wait for OAS to recompute”; the pair is done.

## 5. Step-by-step algorithm

1. **Universe.** Pairs of listed converts from the **same** issuer, both with conversion ratios, call schedules, and locates if either leg is short. This step exists so a cross-issuer OAS rank cannot sneak in as a pair, and so a short you cannot locate never ships.
2. **Freeze.** Same model and same input snapshot for both names, timestamp $\le t-\varepsilon$. This step exists so $g$ is a market gap, not a mix of two models or two clocks.
3. **OAS.** Bisect $s$ on each name until $V(s) = P_C^{\mathrm{mkt}} - P_B(s)$ within $\varepsilon_{\mathrm{OAS}}$. Drop the pair if either root fails. This step exists because a missing root is not “use last good OAS”; it is no trade.
4. **Signal.** $g = \mathrm{OAS}_{\mathrm{high}} - \mathrm{OAS}_{\mathrm{low}}$ after assigning long = high OAS, short = low OAS. Skip if $\lvert g \rvert$ is inside costs. This step exists so you do not pay two bid/asks to fade noise.
5. **Size.** Apply delta-neutral or cash-neutral matching as specified. If deltas differ and the mode is cash-neutral, add a stock overlay to flatten residual $\Delta$. This step exists so leftover equity is explicit, not an accident of notionals.
6. **Caps.** Cap each leg by issue size and by ADV of any stock overlay. After clipping, rebuild the match; do not drop only the short convert. This step exists because skipping the rich leg leaves a naked cheap convert.
7. **Blotter.** Emit two bond intents (and stock if needed). Lot residual to a cash bucket. Do not route live orders. This step exists to keep the research contract off the venue.
8. **Exit.** Recompute OAS on the frozen model each day. Flatten on convergence, call/put, takeout, or a credit event. This step exists because the identity $P_C = P_B + V$ dies when one contract is taken out.

## 6. Execution protocol

- Recompute OAS with a **frozen** model. Do not retune vol or credit on the same day you trade the pair.
- Exit on convergence or on a call/put/takeout. A corporate event breaks the identity $P_C = P_B + V$ for one leg.
- Locate the short convert (or the stock overlay) before lifting the long. Same-issuer does not mean same liquidity.
- Default fill: next snapshot after both OAS values are solved from $t-\varepsilon$ inputs. Delay-0 using the fill print as $P_C^{\mathrm{mkt}}$ in the solver is research-only.

## 7. Data contract

Required, point-in-time, timestamped $\le t-\varepsilon$:

- Dirty/clean prices, accrued, conversion ratios, call/put/takeout schedules for both names
- Issuer identifier (must match)
- Treasury curve used by the OAS shift
- Model inputs: vol, credit, borrow, dividends
- ADV and issue size; borrow for any short leg
- Optional: issuer common price if a residual-delta overlay is on

Look-ahead that invalidates a historical blotter: a vol or CDS update after $t-\varepsilon$ on one leg only, a call announcement not yet public, or pairing on a restated conversion ratio. Issuer match is a legal-entity identifier, not a ticker that changed in a merger without a documented map.

Not used by this spec: cross-issuer OAS ranks (this file is a **pair** of one issuer).

No restatement peeking. If one name is called, the pair is done.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| OAS solver | bisection | tolerance $\varepsilon_{\mathrm{OAS}}$ caller-set |
| hedge mode | delta-neutral | alternative: cash-neutral |
| issuer match | required | do not pair across issuers |
| exit | OAS gap inside cost band | or call/put/takeout |
| model | frozen | same model both legs |
| delay | 1 snapshot | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.convertible_oas` with:

1. `oas(market_price, model_inputs, curve) -> float` — solved $s$, no look-ahead; raise if no root.
2. `pair_signal(oas_a, oas_b) -> float` — $g$, sign = long $A$ iff $A$ is cheaper.
3. `notionals(mode, prices, deltas, I) -> tuple[float, float]` — $(N_A, N_B)$ delta-neutral or cash-neutral, gross $I$.
4. `blotter(notionals, prices, lot) -> list[OrderIntent]` — two bond legs plus optional stock overlay; never live routing.
5. `pnl(N_A, N_B, dP_A, dP_B, coupons, borrow, financing, costs) -> float` — matches the P&L identity above.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Model OAS is not unique.** Vol, credit split, and call treatment all move $s$.
- **Takeovers, calls, and credit events** break the pair; one leg can disappear.
- **Liquidity of one leg.** The rich name may be hard to short; skipping it leaves a naked cheap convert.
- **Residual delta/credit.** Same issuer is not the same delta or the same remaining maturity.

## 11. Acceptance tests

- Identical names: $\mathrm{OAS}_A = \mathrm{OAS}_B$ $\Rightarrow$ $g = 0$, no trade.
- Parallel shift: adding the same $s_0$ to both solved OAS values leaves $g$ unchanged.
- Delta-neutral: $N_A \Delta_A + N_B \Delta_B = 0$ to $10^{-8}$ before lot rounding.
- Cash-neutral: $N_A P_A + N_B P_B = 0$ to $10^{-8}$ before lot rounding.
- Permuting prices after $t-\varepsilon$ must not change the frozen OAS.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
