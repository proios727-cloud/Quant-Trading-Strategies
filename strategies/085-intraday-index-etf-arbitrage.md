---
rank: 85
slug: intraday-index-etf-arbitrage
title: "Intraday Arbitrage Between Index ETFs"
asset_class: "ETFs"
style: "relative-value / two ETFs on the same index"
horizon: "Seconds to minutes in production; paper-trade at snapshot frequency"
instruments: "two ETFs on the same underlying index (e.g. SPY and IVV)"
---

# 085. Intraday Arbitrage Between Index ETFs

| Field | Value |
|---|---|
| Popularity rank (this kit) | 85 of 101 |
| Why it sits here | SPY vs IVV-style pairs. Classic ETF arb; live edge is HFT. This kit is a **delayed identity + costed paper trade**, not a latency playbook. |
| Aliases | same-index ETF pair, SPY–IVV identity |
| Asset class | ETFs |
| Style | relative-value / two ETFs on the same index |
| Typical horizon | Seconds to minutes in production; paper-trade at snapshot frequency |
| Instruments | two ETFs on the same underlying index (e.g. SPY and IVV) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

When one ETF’s bid exceeds the other’s ask by more than a costed threshold, the paper book buys the cheap name and shorts the rich name, then unwinds when the cross disappears.

This file is a **delayed identity monitor**, not an HFT playbook. Snapshot or lagged NBBO, all-in $\kappa$, fill-or-kill paper intents, modelled latency. No colocation, no multi-venue sniping, no queue jumping. Creation/redemption is the institutional close; it is not this tape trade.

You are checking whether two claims on the same index still line up at *executable* quotes after a lag and after costs. You are not racing a matching engine. You are not designing last-look evasion, venue topology, or queue position. Anything that looks like a lock in a delayed snapshot is usually stale quotes or costs, not a licence to build a matching engine.

Typical users are researchers who want a point-in-time identity log and a conservative paper P&L. Horizon in production would be seconds to minutes; here the clock is the snapshot frequency plus $L_{\mathrm{model}}>0$. Max hold in the simulator is a few minutes, then force flatten. Delay is mandatory: $L_{\mathrm{model}}=0$ “live edge” is refused.

The paper book is a diagnostic of whether the identity still holds after costs on a lag you actually could have seen. It is not a capacity estimate, not a maker-taker routing map, and not a creation/redemption playbook. If the log is empty at a realistic $\kappa$, that is a successful monitor: the identity is holding. Filling the log by shrinking $\kappa$ or dropping the lag is how the file stops being this spec.

## 2. First principles

Two ETFs $1$ and $2$ on the same index $I$ are claims on the same basket, up to fees, share scale, and creation constraints. Ignoring those frictions,

$$
\frac{\mathrm{NAV}_1}{m_1} \approx \frac{\mathrm{NAV}_2}{m_2} \approx I
$$

Here $m_i$ is the share scale. This is the NAV identity, not a tradable mid. Fees and share scale are why SPY and IVV are not tick-for-tick identical even when both track S&P 500. For same-scale products (SPY vs IVV), tradable prices should satisfy $P_1\approx P_2$ at the same instant. At the inside quotes the executable test is **not** mid versus mid. You can only sell at a bid and buy at an ask.

A violation of the identity that is large enough to cover costs is

$$
P^{\mathrm{bid}}_1 \ge \kappa\, P^{\mathrm{ask}}_2
$$

Here $\kappa>1$ is the all-in threshold (spread already in the quotes, plus fees and a latency haircut). Then ETF 1 is rich at the bid relative to ETF 2 at the ask: paper-short $1$, paper-buy $2$. The reverse cross is the other direction. Mids can look locked while executable quotes do not clear $\kappa$. Using mids as if they were fills is how this monitor turns into a fake arb.

If mids are consistent and spreads are zero, no $\kappa>1$ fire ever triggers. That is the identity. Anything that looks like a lock in a delayed snapshot is usually stale quotes or costs, not a licence to build a matching engine.

That is the whole strategy. Everything below is the snapshot rule, dollar neutrality, and the research-only blotter.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i\in\{1,2\}$ | two ETFs on the same index |
| $P^{\mathrm{bid}}_i, P^{\mathrm{ask}}_i$ | snapshot or **lagged** bid and ask |
| $\kappa>1$ | all-in threshold (example $\kappa=1.002$) |
| $Q_i$ | signed shares; $Q>0$ long |
| $D_i=Q_i P_i$ | signed dollars at the executable price |
| $\tau$ | extra linear cost on top of quoted spread |
| $L_{\mathrm{model}}$ | modelled latency; quotes older than this are stale |

## 4. Mathematics

### 4.1 Open rules

Let $\kappa\approx 1.002$ (example). All quotes on the right-hand side are the same snapshot (or the same lag). Mixing a live bid on name 1 with a lagged ask on name 2 is not a cross; it is two clocks.

Buy ETF 2 and short ETF 1 when ETF 1’s bid is rich versus ETF 2’s ask after $\kappa$:

$$
P^{\mathrm{bid}}_1 \ge P^{\mathrm{ask}}_2 \times \kappa
$$

This is the executable open, not a mid test. $\kappa$ already includes a haircut for the lag. Lowering $\kappa$ to “find fills” manufactures paper trades that would not clear costs. Permuting a later snapshot must not change this snapshot’s flag.

Unwind that book when the reverse executable cross is gone, i.e. when you can buy back 1 and sell 2 without paying the threshold:

$$
P^{\mathrm{bid}}_2 \ge P^{\mathrm{ask}}_1
$$

Unwind does not require $\kappa$ on the way out in this spec: you exit when the reverse executable quotes no longer pay you to stay. A timeout still force-flattens if this inequality never prints.

Buy ETF 1 and short ETF 2 on the opposite open:

$$
P^{\mathrm{bid}}_2 \ge P^{\mathrm{ask}}_1 \times \kappa
$$

Symmetric open the other way. At most one open fires on a snapshot. If both inequalities somehow hold, quotes are crossed garbage: abort, do not double-enter.

Unwind that book when

$$
P^{\mathrm{bid}}_1 \ge P^{\mathrm{ask}}_2
$$

Each of those four lines is a separate check on a timestamped snapshot. They are not a latency schedule. Close-only prices cannot substitute for these quotes.

### 4.2 Share count

Choose $Q_1,Q_2$ so dollar (or NAV-ratio) neutrality holds at the executable prices. For equal-scale ETFs at the open “short 1 / long 2”:

$$
Q_2 P^{\mathrm{ask}}_2 + Q_1 P^{\mathrm{bid}}_1 = 0
$$

Signs are $Q_2>0$, $Q_1<0$. Long dollars at the ask offset short dollars at the bid. If share scales differ, replace prices by $P_i/m_i$ (NAV-ratio neutrality). Round to lots after the identity; residual dollars go to a cash bucket, not to a third ETF. A residual that is “left in the rich name” is a directional leftover, which this spec forbids.

### 4.3 Paper P&L

Entry (short 1 at bid, long 2 at ask) plus unwind at the later snapshot, minus $\tau$ and minus a latency slippage term that **worsens** the fill:

$$
\mathrm{P\&L} = Q_1\bigl(P^{\mathrm{entry}}_1-P^{\mathrm{exit}}_1\bigr) + Q_2\bigl(P^{\mathrm{exit}}_2-P^{\mathrm{entry}}_2\bigr) - \tau\lvert Q_1\rvert P_1 - \tau\lvert Q_2\rvert P_2
$$

Signs: $Q_1<0$ means the first term is bid-to-cover economics. Slippage in the simulator must worsen the fill, never improve it toward the mid. If either leg is not filled in the simulator (partial, halt, stale), abort the synthetic and flatten; do not hold a directional leftover as “arb.”

Max hold: a few minutes in the simulator, then force flatten. An overnight hold of a same-index pair is a beta book, not this monitor.

## 5. Step-by-step algorithm

1. **Pair.** Two ETFs on the **same** index. Document share scale $m_i$. This step exists so SPY versus QQQ cannot sneak in as a pair.
2. **Quotes.** Snapshot or lagged NBBO, timestamps. Close-only prices are not a live arb signal and are not a delayed identity either. This step exists because the identity is quote-based.
3. **Latency.** Apply $L_{\mathrm{model}}$: you cannot act on a quote newer than the lag. Do not design colocation. This step exists to keep the file a delayed monitor. $L_{\mathrm{model}}=0$ live mode is refused.
4. **Test.** Evaluate the four inequalities on that delayed book. Fire at most one open. This step exists so the cross is a snapshot predicate, not a race.
5. **Size.** Dollar- or NAV-neutral $Q_i$. ADV cap. Borrow on the short. This step exists so a paper FOK is still a hedged pair.
6. **Paper FOK.** Both legs fill-or-kill in the simulator. Any miss → abort, no residual. This step exists because a one-leg fill is directional SPX, not arb.
7. **Unwind or timeout.** Opposite inequality, or max-hold flatten. This step exists so stale paper books do not sit overnight.
8. **Blotter.** Paper intents only. Never live routing. This step exists because the agent contract refuses matching-engine work.

## 6. Execution protocol

**Research / delayed identity monitor, not an HFT playbook.** Snapshot bid/ask (or a lagged NBBO), apply $\kappa$ and all-in costs, emit fill-or-kill paper intents. Model latency; do not design colocation or multi-venue sniping. Creation/redemption is the institutional close, not this tape trade.

Fill-or-kill paper intents only. No spoofing, no multi-venue queue jumping, no unauthorized access. If you do $X$ = use delay-0 NBBO as if it were a fill, you have left this spec. If you do $X$ = lower $\kappa$ until the log is full of hits, the monitor is no longer costed.

## 7. Data contract

Required, point-in-time (delayed):

- Snapshot or lagged NBBO (bid/ask) for both ETFs, with timestamps
- Share scale / NAV if you use NAV-ratio neutrality
- ADV, borrow availability
- Halt flags

Not used by this spec: close-only prices as a signal, order-book replay for queue position, colocation topology.

If you do $X$ = align name 1’s quote at $t$ with name 2’s quote at $t+\varepsilon$ without a lag model, you manufactured a cross. If you do $X$ = use official closes, you do not have an executable identity. If you do $X$ = replay queue position to “improve” FOK, you have started an HFT stack, which is refused. Halt flags as of the snapshot; a later halt restatement does not rewrite $t$.

A same-index pair can still have a stale bid on one name and a live ask on the other inside one “snapshot” if the feed is not locked to a single clock. Treat mismatched timestamps as missing data, not as a cross. Creation-unit NAV prints belong to the close, not to this tape monitor; mixing NAV into $\kappa$ is a different identity.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $\kappa$ | $1.002$ | all-in; raise it, do not lower it to “find fills” |
| max hold | a few minutes | then force flatten |
| latency $L_{\mathrm{model}}$ | caller-set | must be $>0$ |
| neutrality | dollar | or NAV-ratio |
| delay | lagged snapshot | not delay-0 NBBO |

## 9. Agent implementation contract

Build a Python module `strategies.intraday_index_etf_arbitrage` with:

1. `cross(bid1, ask1, bid2, ask2, k) -> str` — `"short1_long2"`, `"short2_long1"`, `"unwind"`, or `"flat"` on **one** snapshot.
2. `shares(side, prices, I, m=None) -> tuple[int, int]` — dollar- or NAV-neutral lots.
3. `blotter(side, shares, snapshot, fok=True) -> list[OrderIntent]` — paper FOK only; never live routing; refuse if latency lag is zero and the caller asked for a “live” edge.
4. `pnl(Q, entry, exit, tau) -> float` — matches §4.3.

Refuse venue exploits, spoofing, unauthorized access, and any attempt to turn this into a matching-engine or colocation spec.

## 10. Risks and failure modes

- **Partial fills.** One leg on, one leg off: directional residue. Simulator must abort.
- **Stale NBBO.** Delayed identity fires on a quote that is already gone. That is why $\kappa$ and $L_{\mathrm{model}}$ exist, not why you should shrink them.
- **Halt on one name.** Pair identity is broken by regulation, not by NAV.
- **Slippage.** Typically consumes the theoretical basis; $\kappa$ exists for this reason.

## 11. Acceptance tests

- Identical mids, zero spread, $\kappa>1$ → `cross` is `"flat"`.
- $P^{\mathrm{bid}}_1 \ge \kappa P^{\mathrm{ask}}_2$ on the snapshot → `"short1_long2"`; permuting a later snapshot must not change this snapshot’s flag.
- Widening either ask weakly reduces the chance of an open (monotonic in $\kappa$).
- A FOK miss on one leg → empty or flatten blotter, not a one-leg hold.
- Adding linear $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
