---
rank: 32
slug: index-cash-and-carry
title: "Index Cash-and-Carry Arbitrage"
asset_class: "volatility / indexes"
style: "index arb / futures vs cash basket"
horizon: "Intraday to days, until basis converges"
instruments: "index futures and the cash index basket (or a liquid subset)"
---

# 032. Index Cash-and-Carry Arbitrage

| Field | Value |
|---|---|
| Popularity rank (this kit) | 32 of 101 |
| Why it sits here | The textbook futures fair-value trade. Live edge is HFT; here: fair-value monitor plus costed, delayed paper trade. |
| Aliases | index arb, cash-and-carry, futures fair value |
| Asset class | volatility / indexes |
| Style | index arb / futures vs cash basket |
| Typical horizon | Intraday to days, until basis converges |
| Instruments | index futures and the cash index basket (or a liquid subset) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

An equity-index future is a claim on the cash index plus financing minus dividends. If the quoted future sits away from that carry-adjusted fair value by more than round-trip costs, a delayed research book can record a paper cash-and-carry: short the rich leg, long the cheap leg, and wait for the basis to converge.

This spec is a **delayed identity monitor**, not an HFT playbook. It does not design latency races, queue jumps, or colocation. Opportunities at the tick are assumed to be gone before a delay-1 fill. Residual paper P&L after costs is a diagnostic of identity error, tracking error, and stale dividends, not a capacity estimate for a colocated desk.

You are not betting that the index will rise. A long-cash / short-futures package is designed to be roughly index-neutral if the basket is complete. You are also not running the VRP or VIX-basis files: those trade volatility, this file checks a futures-versus-cash pricing identity on a lag.

Typical users are researchers who want a fair-value tape, a costed paper blotter, and tests that refuse venue-matching logic. Horizon is until the basis is back inside a cost band, or until delivery. A standing inventory that eases borrows is still delay-1 paper, not a queue strategy.

## 2. First principles

Cash-and-carry says you can synthesize a long future by buying the cash basket, borrowing the money, and collecting dividends through delivery. With a constant financing rate $r$ and $D(t,T)$ the present value of dividends to delivery, the no-arbitrage future is

$$
F^\ast(t,T) = \bigl[S(t) - D(t,T)\bigr] e^{r(T-t)}
$$

$S(t)$ is the cash index (the weighted basket). Subtract dividends first because those cash flows will not be in the future; then grow the remainder at $r$ because you financed the purchase. If $r$ or $D(t,T)$ is taken from a stamp after the fill, $F^\ast$ is a restated fair value, not the one a delayed book could have known. If the quoted future $F(t,T)$ exceeds $F^\ast$, the future is rich: sell the future, buy the cash basket, finance it, hold to $T$ (or until the gap closes). If $F$ is cheap, do the reverse — long future, short cash — subject to borrow.

Define the normalized basis

$$
B(t,T) = \frac{F(t,T) - F^\ast(t,T)}{S(t)}
$$

Dividing by $S(t)$ puts the gap in index-fraction units so it can sit next to a cost band built from bid/ask. A five-point ES gap on a 5000 index is not the same object as a five-point gap on a 2000 index. Trade only if $\lvert B\rvert$ exceeds a cost band built from bid/ask, fees, stamp, and borrow. On a delay-1 grid that band will usually contain $B$; the monitor’s job is to record that fact rather than to chase a tick.

That is the whole identity. Everything below is how to measure $F^\ast$ without peeking, how to paper a delayed fill, and how to treat a truncated basket as tracking error rather than as free money.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S(t)$ | cash index level |
| $F(t,T)$ | quoted index future to delivery $T$ |
| $F^\ast(t,T)$ | carry-adjusted fair future |
| $D(t,T)$ | PV of index dividends with ex-dates in $(t,T]$ |
| $r$ | financing rate to $T$, treated as constant on the decision bar |
| $B(t,T)$ | normalized basis $(F-F^\ast)/S$ |
| $c$ | round-trip cost band in the same units as $B$ |
| $w_i$ | index weights in the cash basket |
| $Q_F$ | signed futures contracts (positive = long) |
| $D_i$ | signed dollar holdings in cash name $i$ |
| $I$ | gross dollars in the cash basket |

## 4. Mathematics

### 4.1 Fair future

Freeze $S(t)$, the dividend forecast, and $r$ at stamps **strictly before** $t_{\mathrm{fill}}$. Then

$$
F^\ast(t,T) = \bigl[S(t) - D(t,T)\bigr] e^{r(T-t)}
$$

$D(t,T)$ is the discounted sum of expected index dividends. Do not update $D$ with post-decision revisions. A special dividend announced after $t$ is forecast error, not a reason to restate $F^\ast(t,T)$. Treating $r$ as one number is a research convenience: borrowing cash and lending cash are not the same rate, and reverse cash-and-carry must use the worse side.

### 4.2 Basis and the cost gate

$$
B(t,T) = \frac{F(t,T) - F^\ast(t,T)}{S(t)}
$$

$B$ is signed: positive means the future is rich versus carry. Using last instead of bid/ask will understate how often $\lvert B\rvert$ sits inside costs. Let $c$ be the round-trip cost in index-fraction units (futures bid/ask + cash basket bid/ask + fees + expected borrow). Sign rule:

- $B > c$ — future rich → **short** futures, **long** cash
- $B < -c$ — future cheap → **long** futures, **short** cash
- $\lvert B\rvert \le c$ — flat; the identity is inside costs

Close when $B$ is back inside a tighter exit band (default: $\lvert B\rvert \le c/2$), or at delivery. The exit band exists so a 1-tick flicker around $c$ does not churn the basket. Flat is the usual output of a delay-1 monitor; that is success of the identity, not a failed strategy.

### 4.3 Cash basket

Full replication uses the point-in-time index weights $w_i$ and prices $P_i$ so that

$$
S(t) = \sum_i w_i P_i(t)
$$

If this identity does not hold on the point-in-time map, you are not looking at the index the future settles to. Do not rescale $w_i$ to force the sum; fix the map or log a data error. A liquidity-truncated proxy drops names below an ADV floor and renormalizes weights. That raises tracking error. Treat the residual $\sum_{\mathrm{omitted}} w_i P_i$ as an unhedged notional, not as zero.

Futures notional matches cash gross:

$$
Q_F \cdot M_F \cdot F = -\mathrm{sign}(B)\, I
$$

with $M_F$ the futures multiplier. The sign makes the futures the opposite of the cash: rich future means short $Q_F$ against long $I$. Dollar holdings $D_i = w_i I$ on the long-cash side (and $-w_i I$ on the short-cash side). Rounding contracts without adjusting $I$ leaves a leftover index bet; put that leftover in a residual bucket and report it.

### 4.4 Holding-period P&L

From fill to unwind, cash-and-carry P&L is futures variation plus cash-basket total return minus financing plus dividends minus costs:

$$
\mathrm{P\&L} = Q_F M_F \Delta F + \sum_i D_i R_i^{\mathrm{fwd}} - r I \Delta t + \mathrm{dividends} - \mathrm{costs}
$$

On a perfect full basket held to delivery, this converges to the locked basis at entry, up to the frozen $D(t,T)$ forecast error. Report tracking error of any truncated basket as a separate series. If delay-1 paper P&L is large and positive after honest costs, suspect look-ahead on $D(t,T)$, a truncated basket treated as complete, or fills at mid. Do not interpret that P&L as evidence that an HFT cash-and-carry is being specified here.

## 5. Step-by-step algorithm

1. **Monitor, do not race.** Sample $S$, $F$, and the basket on a delay-1 grid (next close, or a clock bar of several minutes). Do not design sub-millisecond logic. This step exists so an implementer cannot “complete” the spec by adding a latency race. A function whose purpose is to reduce latency, jump a queue, or hit a matching engine is out of contract.
2. **Fair value.** Compute $F^\ast$ from $S$, frozen dividends $D(t,T)$, and $r$ known before the fill. Updating $D$ with a later revision restates history. The freeze is the whole difference between a monitor and a peeking backtest.
3. **Costs.** Build $c$ from contemporaneous bid/ask, fees, and a borrow schedule for any name that can be short. Mid-to-mid $c=0$ will always look like an open gate. Reverse cash-and-carry without borrow is not a cheap-future trade; it is an unlocated short.
4. **Gate.** If $\lvert B\rvert \le c$, emit flat. If $\lvert B\rvert > c$, set the sign as in 4.2. Flat is a first-class output. Forcing a small position when $B$ is inside costs invents a trade the identity does not support.
5. **Basket.** Full weights if tradable; otherwise drop illiquid names, renormalize, and record omitted notional as tracking error. This step exists because a 50-name proxy is not the index; calling the omitted piece zero converts tracking error into fake alpha.
6. **Size.** Match futures notional to cash $I$. Cap each name at a fraction of ADV (default $1\%$). After caps, either restore the futures match or log residual index risk. Do not clip cash names and leave futures at the old $I$.
7. **Blotter.** Convert to shares and contracts, round to lot size, emit intents. Do not route live orders. Intents are the product. Routing, cancel/replace storms, and venue choice are refused.
8. **Unwind.** Exit when $\lvert B\rvert$ is inside the exit band, on a max-hold clock, or at delivery. Rebuild $F^\ast$ each bar with information available at that bar only. Carrying the entry $F^\ast$ forever will not tell you when the live basis has closed.

## 6. Execution protocol

- Default fill: next close (or next coarse clock bar) after $B$ is known. Academic delay-0 is a backtest choice, not a live book. Same-tick cash-and-carry is outside this file.
- Paper the identity with realistic costs and partial-basket tracking error. A backtest that ignores borrow on the reverse cash-and-carry is not this spec.
- Incomplete baskets omit illiquid names and must be risk-managed as a mishedge. Report omitted notional every bar the book is open.
- A standing long-cash / short-futures inventory can ease borrows; it is still delay-1 paper, not a queue strategy.
- No latency-war, no cancel/replace storms, no venue exploits. If a design document starts describing colocation, stop: that is not this spec.

## 7. Data contract

Required, point-in-time:

- Index future: bid/ask, last, multiplier, delivery date $T$
- Cash index level $S$ and the constituent map dated $\le t$ (weights, prices)
- Dividend forecast frozen at $t$ (ex-dates and amounts as known then)
- Financing rate $r$ to $T$
- ADV for liquidity filters; borrow availability and fees for reverse cash-and-carry

Not used by this spec: VIX, option chains, book value, earnings, SUE, variance swaps.

No restatement of dividends after $t$. Delisted names stay until the delist date. A constituent change announced after $t$ does not belong in $S(t)$ or in $w_i(t)$. If you cannot get the point-in-time map, you cannot run this monitor; substituting a current-day reconstitution is look-ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| delay | 1 bar (close or coarse clock) | delay-0 is research-only |
| cost band $c$ | bid/ask + fees + borrow | in units of $B$ |
| exit band | $c/2$ | or hold to delivery |
| basket | full index | truncated proxy allowed with TE logged |
| ADV cap | $1\%$ of ADV | per cash name |
| $I$ | caller-set | cash gross |
| reverse carry | on only if borrow exists | else skip $B<0$ |

## 9. Agent implementation contract

Build a Python module `strategies.index_cash_and_carry` with:

1. `fair_future(S, D, r, t, T) -> float` — $F^\ast(t,T)$, dividends frozen at $t$.
2. `basis(F, F_star, S) -> float` — $B=(F-F^\ast)/S$.
3. `gate(B, c) -> str` — `{long_fut_short_cash, short_fut_long_cash, flat}`.
4. `basket(weights, prices, adv, borrow) -> pd.Series` — cash dollars, omitted names in a residual bucket, no look-ahead.
5. `blotter(gate, basket, F, I, lot) -> list[OrderIntent]` — shares and futures, never live routing.
6. `pnl(Q_F, dF, D, forward_returns, r, dividends, costs) -> float` — matches the P&L identity.

Refuse venue exploits, spoofing, unauthorized access, latency races, and queue-jumping designs.

## 10. Risks and failure modes

- **Dividend mis-estimate.** $F^\ast$ is only as good as the frozen $D(t,T)$. Using the realized dividend stream, known at $T$, as if it were the $t$ forecast is look-ahead and will lock in a fake basis.
- **Interest asymmetry.** Borrowing cash and lending cash are not the same $r$. A single mid rate makes reverse cash-and-carry look cheaper than it is.
- **Hard-to-borrow names.** Reverse cash-and-carry fails if the short basket cannot be located. Skipping those names without logging tracking error converts a locate problem into alpha.
- **Truncated basket.** Tracking error can exceed the apparent basis. A 20-name proxy on a 500-name index is a sector bet, not cash-and-carry.
- **Delay.** At delay-1 the quoted $B$ is usually already inside costs. Treat residual P&L as a monitor of identity error, not as a capacity estimate for an HFT desk.
- **Corporate actions.** Splits, specials, and late reconstitutions break $S=\sum w_i P_i$ if the map is stale.
- **Turning the monitor into a race.** Any attempt to reduce latency or jump a queue is outside the contract, even if labeled “just for the test venue.”

## 11. Acceptance tests

- Toy zeros: $D=0$, $r=0$ → $F^\ast=S$. Then $B=(F-S)/S$.
- Toy carry: $D=0$, $r$ constant → $F^\ast=S e^{r(T-t)}$ to `1e-8`.
- $\lvert B\rvert \le c$ → flat blotter; $\lvert B\rvert > c$ → signs match Section 4.2.
- Permuting $F$, $S$, and dividends after $t$ must not change $F^\ast(t,T)$ or $B(t,T)$.
- Dropping a name from the basket must increase reported tracking-error notional, not silently change $F^\ast$.
- Adding linear costs $\tau$ weakly decreases P&L.
- The module exposes no function whose purpose is to reduce latency, jump a queue, or hit a particular venue matching engine.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
