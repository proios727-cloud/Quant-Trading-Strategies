---
rank: 48
slug: market-making
title: "Market-Making"
asset_class: "equities"
style: "liquidity provision / microstructure"
horizon: "Milliseconds to minutes. Inventory held as short as possible unless a longer-horizon alpha backs it."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 048. Market-Making

| Field | Value |
|---|---|
| Popularity rank (this kit) | 48 of 101 |
| Why it sits here | The bid–ask capture business. Core of every electronic MM. Naive bid/ask scalping dies to toxic flow. |
| Aliases | liquidity provision, spread capture |
| Asset class | equities |
| Style | liquidity provision / microstructure |
| Typical horizon | Milliseconds to minutes. Inventory held as short as possible unless a longer-horizon alpha backs it. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Quote bid and offer; earn the spread on uninformed flow. Survive adverse selection with a short-horizon directional signal, inventory caps, and optionally a longer-horizon alpha that makes some losing fills good trades. This file is a **research spec for a simulator**. It is not a live routing playbook and not a venue-exploit recipe.

You are betting, inside a simulator, that uninformed flow pays you about half the spread and that inventory skew plus a toxic-flow flag can keep $\pi\delta$ from eating that edge. You are not betting that “buy the bid, sell the ask” is a complete strategy. Naive scalping is the $\pi=0$, $q=0$ benchmark — it dies when flow is informed.

You are not implementing spoofing, layering, cancel/replace storms, hidden-order exploits, matching-engine games, or any procedure whose purpose is to game a venue. Live market-making is a regulated activity. This module emits simulator quotes only.

Typical user: a researcher building a fill-and-markout simulator to study spread capture versus adverse selection. Horizon intuition: milliseconds to minutes; inventory held as short as possible unless a slower alpha *explicitly* says keep the position. If you do X = assume every quote fills at mid with $\pi=0$, the simulator backtest lies about the business.

## 2. First principles

A round-trip that buys at the bid $b$ and sells at the ask $a$ on an unchanged mid earns half the spread on each fill. Write the quoted spread as

$$
s = a - b
$$

Quoted width, not earned width. You only earn $s/2$ per side if the mid does not run away and if you actually fill. In a simulator, $s$ is an input to the quote engine, not a guaranteed P&L. Fees $\tau$ sit on top. If you report $s$ as P&L per round trip, the simulator backtest lies by skipping inventory mark and toxic flow.

Decompose arriving flow into uninformed mass $1-\pi$ and informed mass $\pi$. Uninformed fills pay you about $s/2$ per share per side. Informed fills lift (or hit) you because the mid is about to move through your quote by some adverse increment $\delta$. Expected markout per filled share is then

$$
\mathbb{E}[\mathrm{markout}] \approx (1-\pi)\,\frac{s}{2} - \pi\,\delta
$$

This is the whole MM economics in one line. When $\pi=0$, expected markout is $+s/2$. When $\pi$ and $\delta$ are large, expected markout is negative even if you “capture the spread.” Naive always-on quotes are the $\pi=0$ special case. A simulator that never draws informed flow will always look profitable — that backtest lies. $\pi$ and $\delta$ are simulator parameters, not something this spec tells you to estimate from a live matching engine.

Naive “buy at the bid, sell at the ask” is the $\pi=0$ special case. It is **not** a complete strategy. Live P&L is spread captured plus inventory mark minus fees minus adverse selection.

Fair value $m_t$ is the mid, a microprice, or a short-horizon forecast. Inventory $q$ and volatility $\sigma$ widen and skew the quotes around $m_t$ so that you lean against the existing book. A slower alpha, if any, only decides whether to **keep** inventory after a fill.

That is the whole strategy. Everything below is a documented inventory-skew rule in a simulator, plus what this spec refuses to implement.

### Worked intuition

Mid $m=100$, base half-spread $\delta_0=0.02$, no inventory: bid $99.98$, ask $100.02$. Uninformed round trip earns about $0.04$ per share before fees. Now you are long $q>0$: the linear skew backs the bid off and tightens the ask, so you lean to sell. If an informed seller hits your bid because the mid is about to drop $0.10$, that one fill’s markout is about $-0.10$ plus the half-spread — toxic. A simulator that fills every bid at $99.98$ and never moves the mid reports a lie. Pull both sides if $|q|\ge q_{\max}$; that is the inventory cap, not a venue cancel storm.

## 3. Notation

| Symbol | Definition |
|---|---|
| $m_t$ | fair value (mid, microprice, or short-horizon signal) |
| $b_t,\,a_t$ | bid and ask quotes |
| $s = a-b$ | quoted spread |
| $q$ | signed inventory (positive = long) |
| $\sigma$ | short-horizon volatility |
| $\delta^b(q,\sigma),\,\delta^a(q,\sigma)$ | half-spreads including inventory skew |
| $\pi$ | probability a fill is informed (simulator parameter) |
| $\delta$ | adverse mid move conditional on an informed fill |
| $\hat r_{t,t+h}$ | optional short-horizon return forecast |
| $q_{\max}$ | inventory cap |
| $\tau$ | fees per share |

## 4. Mathematics

### 4.1 Naive identity (incomplete)

The incomplete rule is

$$
\text{buy at the bid, sell at the ask}
$$

Use it only as the $\pi=0$, $q=0$ benchmark in the simulator. Do not ship it as the strategy. It has no inventory, no toxic-flow term, and no fees. If a notebook reports this as MM P&L, the research backtest lies. This spec still writes it so the benchmark is explicit.

### 4.2 Reservation quotes

Set fair value $m_t$ from mid, microprice, or $\hat r_{t,t+h}$. Reservation quotes are fair value minus a bid half-spread and plus an ask half-spread that both depend on inventory and vol:

$$
b_t = m_t - \delta^b(q,\sigma)
$$

Bid below fair value by a half-spread that *grows* when you are already long ($q>0$ in the linear example below). $m_t$ must be a simulator field, not a live hidden feed. Enforce $b_t < m_t$. Crossing the spread as “MM” is a taker overlay and must be documented as such.

$$
a_t = m_t + \delta^a(q,\sigma)
$$

Ask above fair value; *tightens* when you are long so you lean to sell. Enforce $m_t < a_t$ and $a_t-b_t$ at least a minimum tick spread. Quotes are emitted to the simulator API only.

A documented linear skew (not an unnamed PDE black box) is enough for this spec. Example, with base half-spread $\delta_0>0$ and skew $\kappa>0$:

$$
\delta^b(q,\sigma) = \delta_0(\sigma) + \kappa q, \qquad \delta^a(q,\sigma) = \delta_0(\sigma) - \kappa q
$$

When $q>0$ (long), the bid backs off and the ask tightens, so you lean toward selling. When $q<0$, the opposite. Flatten at $\lvert q\rvert \ge q_{\max}$: pull the heavy side. This is a linear example, not Avellaneda–Stoikov. If $\kappa=0$, inventory never skews and the simulator will warehouse $q$ until the cap. $\delta_0(\sigma)$ should widen when vol spikes; a constant $\delta_0$ in a vol event is how naive quotes get run over.

When $q>0$ (long), the bid backs off and the ask tightens, so you lean toward selling. When $q<0$, the opposite. Flatten at $\lvert q\rvert \ge q_{\max}$: pull the heavy side.

Avellaneda–Stoikov is a usual reference for a more structured $\delta^b,\delta^a$. This spec does not write that PDE. Implement a documented inventory-skew rule, not an unnamed black box.

### 4.3 Toxic-flow filter (high-level)

Reduce size or pull quotes when a short-horizon probability of an adverse move is high (queue imbalance, trade sign, etc.). High-level only: no spoofing, no cancel-flood recipes, no exchange-specific games, no matching-engine edge cases.

The filter is a simulator flag, not a playbook. If you do X = implement cancel/replace storms to hold queue position, you have left this spec and entered refused venue behavior. Document the flag’s inputs; do not invent a proprietary matching-engine trick.

### 4.4 Two-horizon mix

If a slower alpha agrees with the fill side, you may keep inventory. If it disagrees, flatten. Cents-per-share of the slow signal should exceed the spread you are capturing, or you are just warehousing risk.

Speed and queue position dominate whether you actually earn the spread. That is infrastructure, not a formula, and it is out of scope for this research spec.

A slow alpha does not turn this file into a live MM. It only changes how the *simulator* treats $q$ after a fill. If the slow signal is weaker than $s$, keeping inventory is not “alpha overlay”; it is leftover risk.

### 4.5 Simulator P&L

Spread captured plus inventory mark minus fees minus adverse selection:

$$
\mathrm{P\&L} = \sum_{\mathrm{sells}} a_{\mathrm{fill}} Q_{\mathrm{sell}} - \sum_{\mathrm{buys}} b_{\mathrm{fill}} Q_{\mathrm{buy}} + q_{\mathrm{end}} m_{\mathrm{end}} - q_{\mathrm{start}} m_{\mathrm{start}} - \tau\sum \lvert Q\rvert
$$

Cash from sells minus cash from buys, plus mark of leftover inventory at $m$, minus fees. Adverse selection shows up in $m_{\mathrm{end}}$ and in fill prices versus later mids (markout). If you omit the $q m$ terms, you report spread capture and hide inventory. If you omit $\tau$, you report gross. If you assume every quote fills at the quoted price with $\pi=0$, the simulator backtest lies.

Report fill rate, markout at $+50\mathrm{ms}$ / $+1\mathrm{s}$ / $+1\mathrm{min}$, and the inventory distribution. Do not report a backtest that assumes every quote fills at the quoted price with $\pi=0$.

## 5. Step-by-step algorithm

This algorithm runs **inside a simulator**. It does not route live orders.

1. **State.** Read simulator BBO (or L2), last trade, inventory $q$, clock. No unauthorized data feeds. This step exists to freeze the simulated information set. Live exchange sessions are out of scope.
2. **Fair value.** $m_t$ = mid, microprice, or mid plus a documented short-horizon $\hat r$. Document which. A future mid in $m_t$ is look-ahead and the simulator backtest lies.
3. **Skew.** Compute $\delta^b,\delta^a$ from $q$ and $\sigma$. Enforce $b_t < m_t < a_t$ and $a_t-b_t \ge$ a minimum tick spread. Skew exists so inventory leans the book; skipping it is the naive benchmark.
4. **Caps.** If $\lvert q\rvert \ge q_{\max}$, pull the inventory-increasing side. Kill switch: pull both sides on a volatility spike (documented $\sigma$ threshold). Caps exist so $q$ cannot walk to infinity. A kill switch is not a cancel storm.
5. **Filter.** Optionally shrink size when a documented toxic-flow flag is on. Do not implement cancel/replace storms. High-level flag only; this step exists to refuse venue games.
6. **Slow alpha.** If on, keep or flatten inventory after fills according to agreement with the fill side. Optional. Disagreement → flatten, do not “hope the spread comes back.”
7. **Emit quotes.** Simulator API only: bid, ask, size. Never live routing. If a code path can reach a live gateway, the module is out of spec.
8. **On fill.** Update $q$, mark P&L, record markout timestamps. Markout horizons exist so $\pi>0$ is visible. Missing markout is how naive books hide toxic flow.

Quote both sides on names you can hedge. No crossing the spread as a MM unless the slow signal is strong (then you are no longer dumb liquidity — document it as a taker overlay, not as MM).

## 6. Execution protocol

Live MM is a regulated activity. This file is a **research spec** for a simulator: fill model, adverse-selection model, inventory P&L.

Do **not** generate: order-spam, latency-arb versus a particular matching engine, spoofing, layering, hidden-order exploits, cancel/replace storms, or any procedure whose purpose is to game a venue.

If you do X = assume fill-at-mid on every quote, the simulator backtest lies. If you do X = set $\pi=0$ and call it live-ready, the research result lies about toxic flow. If you do X = add a live routing path “just to see,” you have left this spec.

## 7. Data contract

Required, in a **simulator**:

- L2, or at least BBO + last, with timestamps
- Trades with aggressor side if the adverse-selection model needs it
- Fee schedule $\tau$
- Optional: a documented slow-alpha series aligned in time

Not used by this spec: book value, SUE, earnings timestamps, industry map — unless they enter the optional slow alpha, in which case that alpha’s own contract applies.

No restatement peeking. No live exchange sessions.

If you do X = replay tape with future mid as $m_t$, fair value looks ahead and the simulator backtest lies. If you do X = omit fees, P&L is gross. If you do X = use a production colocation feed, you are no longer in the research simulator this file allows.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $q_{\max}$ | caller-set | inventory cap |
| $\kappa$ | caller-set | inventory skew |
| quote size | caller-set | simulator shares |
| hold cap | caller-set | max time to carry $q$ |
| slow-alpha overlay | off | |
| toxic-flow filter | off | high-level flag only |
| environment | simulator | never live routing |

## 9. Agent implementation contract

Build a Python module `strategies.market_making` **simulator API only**:

1. `quotes(state) -> (bid, ask, size)` — reservation quotes from §4.2; no live gateway.
2. `on_fill(side, qty, px) -> None` — update $q$ and P&L.
3. `markout(fills, mids, horizons) -> dict` — $+50\mathrm{ms}$ / $+1\mathrm{s}$ / $+1\mathrm{min}$.
4. `pnl(...)` — matches the identity in §4.5.

Refuse to emit: cancel/replace storms, hidden-order exploits, matching-engine edge cases, spoofing, layering, or any procedure whose purpose is to game a venue. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Toxic flow.** $\pi>0$ makes naive always-on quotes lose; that is the point of the simulator. If you do X = run only $\pi=0$, the research backtest lies about MM.
- **Inventory gaps.** A one-sided run leaves $q$ at the cap with the mid against you. If you do X = omit $qm$ marks, the backtest lies by hiding that gap.
- **Operational.** Stale $m_t$, missed kill switch. If you do X = leave quotes out with a frozen mid in a vol spike, the simulator should lose; if it does not, the fill model is too kind.
- **Legal.** Market-making without registration, spoofing, layering — out of scope and refused. If you do X = add those as “realism,” the spec is violated, not improved.

## 11. Acceptance tests

- Zero-alpha random-walk simulator: average markout should be near $+\tfrac12$ spread minus fees if fills are uninformed.
- With informed flow, naive always-on quotes lose. If they still win, $\pi$ or $\delta$ is not in the fill model and the simulator backtest lies.
- Linear skew: $q>0$ implies $b$ farther from $m$ than $a$ is.
- $\lvert q\rvert \ge q_{\max}$ pulls the increasing side.
- The module has no live order-routing path. If a test can instantiate a gateway, the module is out of spec.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
