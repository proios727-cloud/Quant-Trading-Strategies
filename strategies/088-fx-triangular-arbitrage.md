---
rank: 88
slug: fx-triangular-arbitrage
title: "FX Triangular Arbitrage"
asset_class: "foreign exchange"
style: "market-neutral microstructure / three-pair loop"
horizon: "Intraday, sub-second in production; this kit models the identity only"
instruments: "three FX pairs among currencies A, B, C (spot bid/ask)"
---

# 088. FX Triangular Arbitrage

| Field | Value |
|---|---|
| Popularity rank (this kit) | 88 of 101 |
| Why it sits here | The canonical FX no-arbitrage identity. Live edges last milliseconds; here it is a **research/monitoring** spec, not a latency-war playbook. |
| Aliases | three-pair FX identity, cross-rate loop |
| Asset class | foreign exchange |
| Style | market-neutral microstructure / three-pair loop |
| Typical horizon | Intraday, sub-second in production; this kit models the identity only |
| Instruments | three FX pairs among currencies A, B, C (spot bid/ask) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Loop $A\to B\to C\to A$ using executable bids and asks. Paper-profit if the product of executable rates exceeds $1$ after costs.

This file is a **delayed identity monitor**, not an HFT playbook. Log the identity and a delayed, costed backtest. Do not design an HFT stack, colocation, last-look evasion, or multi-venue sniping. Opportunities are ephemeral; slippage usually eats the edge. This is not a retail-tradable book.

You are checking a three-currency, spot-only no-arbitrage identity at lagged inside quotes. You are not running covered interest (that is two currencies, spot versus forward, `006`). You are not racing last-look LP streams. You are not emitting aggressive multi-venue sniping logic. A product $R>1+\kappa$ on a delayed book is usually a stale or crossed quote, not a licence to colocate.

Typical users are researchers who want a timestamped identity log. Production edges last milliseconds; this kit models the identity only, with $L_{\mathrm{model}}>0$ mandatory. The log of $R$, $\kappa$, lag, and whether it would have cleared **is** the deliverable. Paper FOK on all three legs; any miss aborts. Refuse $L_{\mathrm{model}}=0$ “live” mode.

An empty log at a realistic $\kappa$ means the triangle is holding on the delayed book. That is the point of the monitor. A full log of “hits” after you dropped the lag or used mids is not evidence of a tradable edge; it is evidence that the file was no longer a delayed identity check. Retail sizes and last-look streams are why this is not a playbook.

## 2. First principles

Three currencies $A,B,C$ cannot have three independent prices. At mids with zero spread, exchanging one unit of $A$ around the triangle must return one unit of $A$:

$$
S_{A\to B}\cdot S_{B\to C}\cdot S_{C\to A} = 1
$$

This is the frictionless mid identity. If the product differed from $1$, a frictionless loop would be a money pump. Covered interest is a **two-currency, spot-versus-forward** identity; this is a **three-currency, spot-only** identity. They are not the same trade. Mixing a forward into one leg makes CIP, not a triangle.

At the inside quotes you cannot trade mids. The executable rate $A$ into $B$ is the bid for selling $A$ to buy $B$ (convention documented below). The inverse direction pays the ask. The executable product is therefore $\le 1$ once spreads are on, except when quotes are stale, crossed, or last-look. A research monitor records when that product exceeds $1+\kappa$ after a modelled lag — it does not try to win a race to the matching engine.

That is the whole strategy. Everything below is the executable chain, the FOK abort, and the delay.

## 3. Notation

| Symbol | Definition |
|---|---|
| $A,B,C$ | three currencies |
| $\mathrm{Bid}(X\to Y)$ | executable units of $Y$ per 1 $X$ when selling $X$ into $Y$ at the bid |
| $\mathrm{Ask}(X\to Y)$ | executable units of $Y$ per 1 $X$ when buying $Y$ with $X$ at the ask |
| $R(A\to B\to C\to A)$ | executable product of one loop |
| $\kappa$ | all-in threshold (example $2$–$5$ bp) |
| $L_{\mathrm{model}}$ | modelled latency; quotes newer than this are not usable |
| $N_A$ | starting units of $A$ in the paper loop |

Rate $B$ into $A$ is $1/\mathrm{Ask}(A\to B)$ when the book is quoted the other way; pick one quoting convention and convert once.

## 4. Mathematics

### 4.1 Executable chain

Executable rate $A$ into $B$ is $\mathrm{Bid}(A\to B)$. Rate $B$ into $A$ is $1/\mathrm{Ask}(B\to A)$ when you have to lift the offer.

Chain $A\to B\to C\to A$:

$$
R(A\to B\to C\to A) = \mathrm{Bid}(A\to B)\cdot \mathrm{Bid}(B\to C)\cdot \frac{1}{\mathrm{Ask}(C\to A)}
$$

Bids on the first two legs, lift the offer on the last, under one documented quoting convention. Mixing EURUSD with USDEUR without converting once will make $R$ look like a money pump when it is only a unit error. The swapped chain $A\to C\to B\to A$ is the other direction, with bids and asks rotated the same way. Both products use the *same* lagged snapshot. Aligning pair 1 at $t$ with pair 3 at $t+\varepsilon$ manufactures a triangle.

### 4.2 Trade rule (paper)

Trade only if the delayed product clears costs and a haircut:

$$
R > 1+\kappa
$$

$\kappa$ covers spread already in the quotes (if you used mids by mistake, $\kappa$ must be larger), fees, and latency slippage. Default $\kappa$ in $2$–$5$ bp all-in. Do not shrink $\kappa$ to manufacture hits. The signal is `True` only on the delayed book; a live quote inside $L_{\mathrm{model}}$ is not usable.

With consistent mids and zero spread, $R=1$ exactly (up to quoting roundoff). Widening any ask weakly decreases $R$. That monotonicity is an acceptance test. Last-look on OTC FX is a refusal to fill, not a signal to chase a printed $R$.

### 4.3 Paper P&L

Start with $N_A$ units of $A$. If all three FOK legs fill at the delayed quotes, you end with $N_A R$ units of $A$:

$$
\mathrm{P\&L} = N_A(R-1) - \mathrm{fees}
$$

If `filled` is false, P&L is $0$ after abort, not a one- or two-leg FX position. If any leg misses, abort the synthetic. Model the miss as a **failed arb**, not as a directional FX book. Flatten residual risk immediately in the simulator. Timeout: fail if all three fills are not acknowledged within the model latency budget.

A two-leg leftover is a cross, not a triangle. Booking it as arb P&L is how the monitor becomes a directional book.

## 5. Step-by-step algorithm

1. **Triangle.** Choose $A,B,C$ and a quoting convention for each pair. This step exists so unit errors are converted once, not discovered as fake $R>1$.
2. **Snapshot.** Bid/ask on all three pairs, one timestamp (or one lag $L_{\mathrm{model}}>0$). This step exists to keep the identity on one clock. $L_{\mathrm{model}}=0$ is refused.
3. **Convert.** Map every quote into $X\to Y$ executable units. This step exists because venues quote EURUSD and USDEUR differently.
4. **Products.** Compute $R(A\to B\to C\to A)$ and $R(A\to C\to B\to A)$. This step exists to check both loop directions on the same snapshot.
5. **Gate.** Fire a paper loop only if $R>1+\kappa$ on the **delayed** book. This step exists so mids and live quotes cannot sneak in.
6. **FOK.** Three-leg fill-or-kill. Any miss → abort, no leftover. This step exists because a partial loop is directional FX.
7. **Log.** Store $R$, $\kappa$, lag, and whether it would have cleared. That log **is** the deliverable. This step exists because the research output is the identity monitor, not a live fill.
8. **Blotter.** Paper intents only. Never live routing. This step exists because the agent contract refuses an HFT stack.

## 6. Execution protocol

**Agent rule:** log the identity and a delayed, costed backtest. Do not design an HFT stack. Opportunities are ephemeral; slippage usually eats the edge.

This is a pricing-identity checker and delayed paper-trade. Do not emit aggressive multi-venue sniping logic, queue-jumping, or colocation exploits. Last-look on OTC FX is a refusal to fill, not a signal to chase.

If you do $X$ = set $L_{\mathrm{model}}=0$ and treat printed $R$ as a fill, you have left this spec. If you do $X$ = shrink $\kappa$ until the log is full, the monitor is no longer costed. If you do $X$ = keep two legs when the third misses, you are running a cross.

## 7. Data contract

Required, delayed:

- Spot bid/ask on all three pairs, timestamps
- Quoting convention (EURUSD vs USDEUR)
- A lag $L_{\mathrm{model}}>0$
- Calendar / session flags (weekend gaps)

Not used by this spec: forwards (this is not CIP), equity data, a “sub-millisecond” venue graph.

No look-ahead on fixing timestamps. A revised print after $t$ does not change $R_t$. If you do $X$ = align the three pairs on different clocks, you manufactured a triangle. If you do $X$ = use mids in $R$ and a tiny $\kappa$, you ignored executable spread. If you do $X$ = replay last-look accepts as if they were firm quotes, $R$ was never executable. Weekend gaps: a Friday quote is not a Sunday triangle.

Three pairs must share one snapshot clock. If EURUSD is 40 ms newer than USDJPY inside the same “tick,” $R$ is not a triangle; it is two clocks. Drop that row. Do not interpolate the stale pair forward to the live pair’s time: that interpolation is look-ahead if the live print had not yet been seen when the stale print was the only one you had.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $\kappa$ | $2$–$5$ bp all-in | do not shrink it to manufacture hits |
| timeout | model latency budget | fail the arb if exceeded |
| $L_{\mathrm{model}}$ | caller-set, $>0$ | delay is mandatory |
| legs | three FOK | abort on any miss |

## 9. Agent implementation contract

Build a Python module `strategies.fx_triangular_arbitrage` with:

1. `executable_product(bids, asks, chain) -> float` — $R$ for one directed loop.
2. `signal(R, k) -> bool` — `True` iff $R>1+\kappa$ on the delayed snapshot.
3. `blotter(chain, N_A, quotes, fok=True) -> list[OrderIntent]` — three paper FOK legs or empty; never live routing; refuse $L_{\mathrm{model}}=0$ “live” mode.
4. `pnl(N_A, R, filled, fees) -> float` — $N_A(R-1)-\mathrm{fees}$ if `filled` else $0$ after abort.

Refuse venue exploits, spoofing, unauthorized access, last-look evasion, and any HFT stack.

## 10. Risks and failure modes

- **Partial fills** leave directional residue. Abort.
- **Stale quotes** make $R>1+\kappa$ on a book that no longer exists. That is the usual “hit” in a delayed log, not a tradable edge.
- **Last-look** on OTC FX: the quoted $R$ was never executable.
- **Not retail-tradable.** Spreads and minimum sizes eat $\kappa$.

## 11. Acceptance tests

- Consistent mids, zero spread → $R=1$ to $10^{-8}$.
- Widening any ask weakly decreases $R$.
- Permuting quotes after $t$ must not change $R_t$.
- `filled=False` → P&L $=0$ (abort), not a one- or two-leg FX position.
- Adding fees or raising $\kappa$ weakly reduces the number of `True` signals and weakly decreases P&L on filled paper loops.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
