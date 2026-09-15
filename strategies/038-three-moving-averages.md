---
rank: 38
slug: three-moving-averages
title: "Three Moving Averages"
asset_class: "equities"
style: "filtered trend"
horizon: "Daily."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 038. Three Moving Averages

| Field | Value |
|---|---|
| Popularity rank (this kit) | 38 of 101 |
| Why it sits here | Triple MA filter (e.g. 3/10/21) to cut false dual-MA crossovers. Common discretionary overlay. |
| Aliases | triple MA, stacked MA filter |
| Asset class | equities |
| Style | filtered trend |
| Typical horizon | Daily. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Require stacked MAs to enter; flatten when the fast MA crosses back through the middle. The exit is faster than the entry stack, by design. Independent per name.

You are betting that a *triple* agreement of short, medium, and long local levels is a cleaner drift sign than a dual-MA cross, and that you should leave when the fast level merely loses the middle — without waiting for the slow level to roll over. You are not forecasting a target, not ranking names, and not running dual MA ([`004-two-moving-averages.md`](004-two-moving-averages.md)), which enters and exits on the same two-average inequality.

You are also not claiming the filter raises Sharpe on one equity. Typical user: a discretionary overlay automated as 3/10/21, or a CTA-style timer that wants fewer whipsaws than 10/30 at the cost of later entries. Horizon intuition: daily bars; entry waits for the stack (late on purpose); exit is fast by omitting the slow MA from the exit rule.

If you put the slow MA into the exit inequality, or use the fill bar inside all three averages, you have a different strategy and an optimistic delay-0 backtest.

## 2. First principles

A moving average of length $T$ is a local level. Take three lengths $T_1<T_2<T_3$. Then $\mathrm{MA}(T_1)$, $\mathrm{MA}(T_2)$, and $\mathrm{MA}(T_3)$ are short, medium, and long local levels. Index $t=1$ as the most recent bar in the window.

The simple moving average is

$$
\mathrm{SMA}(T) = \frac{1}{T}\sum_{t=1}^{T} P(t)
$$

Equal-weight level, same as in the dual-MA file. Under delay-1 the window ends before the fill. Unadjusted splits break all three averages at once. Warmup needs $T_3$ bars, not $T_1$ — otherwise the “slow” leg is not slow.

The exponential moving average is

$$
\mathrm{EMA}(T,\lambda) = \frac{1-\lambda}{1-\lambda^{T}}\sum_{t=1}^{T} \lambda^{t-1} P(t)
$$

Same EMA identity as elsewhere. Use the same type and the same $\lambda$ on all three lengths. Mixing SMA slow with EMA fast is a fourth rule. Recursive EMAs that see the future are look-ahead.

Use the same type (SMA or EMA) on all three lengths. A **stack** means the three levels are strictly ordered. That is a stronger statement than a dual-MA crossover: short, medium, and long estimates of the level all agree on the drift sign.

Entry requires the full stack. Exit requires only that the fast level cross back through the middle — the slow level is allowed to stay on the old side. That is why the exit is faster than the entry.

That is the whole strategy. Everything below is the four inequalities and the state machine.

### Worked intuition

Fast MA at 102, middle at 100, slow at 98: stacked up → enter long. Later fast falls to 99.5 while middle is 100 and slow is still 98: fast $\le$ middle → exit the long *even though* middle is still above slow. That leftover mid>slow is the point of the fast exit. If you waited for fast < middle < slow (a down-stack) to flatten, you would be using dual-MA-with-confirmation to exit, which is slower and not this file. A delay-0 fill on the bar that completed the stack collects the thrust you were supposed to wait out.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(t)$ | split- and dividend-adjusted price; $t=1$ most recent in the window |
| $T_1<T_2<T_3$ | fast, middle, slow lengths |
| $\mathrm{MA}(T)$ | SMA or EMA, same type on all three |
| $s \in \{\mathrm{flat},\,\mathrm{long},\,\mathrm{short}\}$ | state |
| $Q$ | signed share holdings |

Default lengths: $(T_1,T_2,T_3)=(3,10,21)$.

## 4. Mathematics

### 4.1 Entry and exit

Enter long only when the three levels are strictly stacked up:

$$
\mathrm{MA}(T_1) > \mathrm{MA}(T_2) > \mathrm{MA}(T_3) \quad\Rightarrow\quad \text{enter long}
$$

All three agree: short level above medium above long. Stricter than dual MA’s fast>slow. From *flat*, this is the only long entry. From *short*, whether this reverses in one bar is the state-machine flag. If any equality holds, there is no stack.

Exit a long when the fast level is no longer above the middle:

$$
\mathrm{MA}(T_1) \le \mathrm{MA}(T_2) \quad\Rightarrow\quad \text{exit long}
$$

Fast exit. The slow MA is absent on purpose. A long can die while $\mathrm{MA}(T_2)>\mathrm{MA}(T_3)$ still holds. Putting $T_3$ into this inequality is a different strategy — later exits, more give-back.

Enter short only when the three levels are strictly stacked down:

$$
\mathrm{MA}(T_1) < \mathrm{MA}(T_2) < \mathrm{MA}(T_3) \quad\Rightarrow\quad \text{enter short}
$$

Symmetric down-stack. Long-only books suppress this branch. Delay-1 still applies: none of the three MAs may contain the fill bar.

Exit a short when the fast level is no longer below the middle:

$$
\mathrm{MA}(T_1) \ge \mathrm{MA}(T_2) \quad\Rightarrow\quad \text{exit short}
$$

Symmetric fast exit from a short. Again no slow MA. If both this exit and the up-stack fire on one bar, the default state machine reverses to long; document if you prefer flatten-then-wait.

The slow MA does not appear in the exit rules. A long can exit while $\mathrm{MA}(T_2)>\mathrm{MA}(T_3)$ still holds.

### 4.2 State machine

States: flat / long / short. Do not reverse in one bar unless both an exit and the opposite entry fire; document that choice. Default: if both fire, go to the new stacked side (reverse). If only exit fires, go flat.

The state machine exists so a single bar cannot be both “still long” and “newly short” without a rule. Default reverse-in-one-bar is aggressive; flatten-only is slower to re-enter. Either is allowed; silent mixing is a bug. Warmup state is flat until $T_3$ bars exist.

### 4.3 Holding-period P&L

Independent per name. Per-name P&L from entry to exit, $Q<0$ on shorts:

$$
\mathrm{P\&L} = Q\bigl(P_{\mathrm{exit}} - P_{\mathrm{entry}}\bigr) - \mathrm{costs}
$$

Share P&L minus costs. Late entries and fast exits are the design; do not “give the trade more room” in P&L by delaying the exit in code. If you do X = fill on the stack-completion close, the backtest lies by taking the bar that created the stack.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, adjusted daily OHLC. Keep delisted names until the delist date. Unadjusted splits fake stacks. Survivorship paints old overlays too clean. This step exists so the three levels are comparable across time.
2. **MA type.** SMA or EMA, same type on $T_1,T_2,T_3$. Default lengths $(3,10,21)$. Lengths must stay strictly increasing; $10/10/21$ is not a triple.
3. **Warmup.** Require $T_3$ bars. Until then, state = flat. Trading on a partial slow MA is a shorter, different filter.
4. **Levels.** At each bar, compute the three MAs on a window that ends before the fill (delay-1 default). This step exists so the fill bar is not inside any average.
5. **Transition.** From flat: enter only on a full stack. From long: exit on $\mathrm{MA}(T_1)\le\mathrm{MA}(T_2)$; reverse only if the down-stack also holds and the documented reverse rule allows it. Symmetric from short. The asymmetric exit is the product; do not “complete” it with $T_3$.
6. **Size.** Independent per name. Caller sets $Q$. No dollar-neutrality constraint — these are timers, not a cross-section.
7. **Blotter.** Round to lot size, emit intents. Do not route live orders. The spec stops at intents.

## 6. Execution protocol

- Delay-1. Decide at the close, trade the next open. If you do X = fill at the stack close, the backtest lies by trading the print that ordered the three MAs.
- The exit is faster than the entry stack, by design. Do not add the slow MA to the exit inequality. If you do X = require a full opposite stack to flatten, you have dual-MA-with-confirmation, not this file, and the backtest lies about the spec you named.
- Borrow required for shorts. Cap vs ADV if needed. If you do X = short without borrow, the two-way backtest lies.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted daily OHLC (close is enough)
- ADV if you cap participation
- Borrow availability for shorts

Not used by this spec: book value, earnings, SUE, industry map, option IV.

No restatement peeking. Delisted names stay until the delist date.

If you do X = unadjusted closes, splits manufacture stacks. If you do X = recompute EMAs after a later price fix, old states move. If you do X = ADV from the hold, the cap looks ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $(T_1,T_2,T_3)$ | $(3,10,21)$ | must remain strictly increasing |
| MA type | SMA | EMA requires $\lambda$ |
| reverse in one bar | true | if exit and opposite entry both fire |
| delay | 1 bar | delay-0 is research-only |
| long-only | false | if true, suppress shorts |

## 9. Agent implementation contract

Build a Python module `strategies.three_moving_averages` with:

1. `levels(prices, T1, T2, T3, ma_type) -> (ma1, ma2, ma3)`.
2. `step(state, levels) -> state` — state machine flat / long / short; document reverse-in-one-bar.
3. `pnl(Q, P_entry, P_exit, costs) -> float`.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Late entry.** Waiting for three stacked levels misses the front of the trend. If you do X = backfill an entry on the first dual cross, the backtest lies about this filter.
- **Short lengths.** If all three windows are short, the filter still whipsaws. If you do X = set $(2,3,4)$ and compare to 50/200 dual MA, you are not testing the same idea.
- **Exit vs entry mismatch.** Putting the slow MA into the exit rule is a different strategy. If you do X = exit only on a full opposite stack, the backtest lies about the fast-exit identity.

## 11. Acceptance tests

- Strictly increasing prices → long after warmup.
- Exit when fast $\le$ mid even if mid $>$ slow. If the test requires mid $<$ slow to flatten, the exit rule is wrong and a backtest using that code lies about this spec.
- Symmetric: strictly decreasing prices → short after warmup.
- Delay-1: the fill bar is not inside the MA sample. If including the fill close changes any of the three delay-1 MAs, the implementation looks ahead.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
