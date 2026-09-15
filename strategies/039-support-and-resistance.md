---
rank: 39
slug: support-and-resistance
title: "Support and Resistance"
asset_class: "equities"
style: "intraday / pivot technical"
horizon: "Intraday, using previous day’s high/low/close."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 039. Support and Resistance

| Field | Value |
|---|---|
| Popularity rank (this kit) | 39 of 101 |
| Why it sits here | Floor-trader pivots. Extremely common intraday heuristic; weak as a stand-alone academic factor. |
| Aliases | classic pivots, floor-trader pivots |
| Asset class | equities |
| Style | intraday / pivot technical |
| Typical horizon | Intraday, using previous day’s high/low/close. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Pivot $C$ from the prior day. Long above the pivot, exit at resistance; short below the pivot, exit at support. Levels are frozen at the prior session’s high, low, and close. Other pivot formulas exist; this file writes the classic identity only.

You are betting that today’s path versus yesterday’s mirrored range is a tradable intraday rule, not that $C$, $R$, and $S$ are structural supply and demand. The levels are a **mirror identity** of prior high, low, and close. You are not running Donchian, not fading a gap through $R$ or $S$ unless you document a different policy, and not updating $P_H$ with today’s developing high.

Typical user: an intraday discretionary overlay or a teaching example of floor-trader pivots. Horizon intuition: one session. Flatten by the close unless a documented overnight overlay exists. Academic factor strength is weak; treat this as a path rule with honest costs, not as a monthly anomaly.

If you feed today’s developing high into $P_H$, or fill a gap through $R$ as if the spec defined it, the backtest is a different and usually look-ahead object.

## 2. First principles

The prior session is summarized by three prices: high $P_H$, low $P_L$, close $P_C$. Their arithmetic mean is the classic pivot — a one-day central level:

$$
C = \frac{P_H + P_L + P_C}{3}
$$

Yesterday’s typical price, nothing more. It is frozen after the prior close. Using today’s still-forming high, low, or last in this average is a different, invalid pivot. The $1/3$ is the classic formula; Woodie / Camarilla / Fibonacci pivots are not this file.

Resistance is the reflection of the prior low through that pivot:

$$
R = 2C - P_L
$$

Mirror the prior low up through $C$. Algebra: $R-C = C-P_L$. If yesterday’s range was wide, $R$ sits far above $C$. This is an identity, not a forecast that sellers wait at $R$. Compute it once; do not trail it.

Support is the reflection of the prior high through that pivot:

$$
S = 2C - P_H
$$

Mirror the prior high down through $C$. Algebra: $C-S = P_H-C$. Wide prior range → $S$ far below $C$. Same warning: identity, not a magnet. $S$, $C$, $R$ must not move with today’s tape.

Those two lines are identities, not forecasts: $R-C = C-P_L$ and $C-S = P_H-C$. The session’s range is mirrored about $C$. The trade is a **path rule** on today’s price $P$ against those frozen levels: long while $P$ is above the pivot until it tags resistance; short while $P$ is below the pivot until it tags support.

That is the whole strategy. Everything below is the four inequalities, gap handling, and the freeze-at-prior-close rule.

### Worked intuition

Prior session: high 102, low 98, close 100. Pivot $C=(102+98+100)/3=100$. Resistance $R=2\times100-98=102$. Support $S=2\times100-102=98$. Today opens at 100.2: long. Price later prints 102: exit long at resistance. If today instead opens at 103 (through $R$), this spec stays flat until price re-enters $(98,102)$ — it does not silently fade the gap. If you recompute $C$ using today’s high of 103, every level moves and you have look-ahead, not yesterday’s pivot.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P_H,\,P_L,\,P_C$ | prior session high, low, close |
| $C$ | pivot |
| $R$ | resistance |
| $S$ | support |
| $P$ | current-session trade price |
| $s \in \{\mathrm{flat},\,\mathrm{long},\,\mathrm{short}\}$ | state |
| $Q$ | signed share holdings |

## 4. Mathematics

### 4.1 Classic pivot levels

The pivot, resistance, and support are

$$
C = \frac{P_H + P_L + P_C}{3}
$$

Same identity as §2, now as the implemented level. Inputs are **prior** session official OHLC. A split overnight must reset the series rather than stitch a raw jump into $P_H,P_L,P_C$.

$$
R = 2C - P_L
$$

Frozen resistance. If this uses today’s low, the level is invalid. Equality $P=R$ is an exit, not an entry.

$$
S = 2C - P_H
$$

Frozen support. Compute them once from the previous session. Do not update $P_H$ or $P_L$ with the current day’s developing high or low.

Compute them once from the previous session. Do not update $P_H$ or $P_L$ with the current day’s developing high or low.

### 4.2 Path rules

Enter long when price is above the pivot:

$$
P > C \quad\Rightarrow\quad \text{enter long}
$$

Path rule, not a daily rank. From flat, $P>C$ is the long trigger. It does not say hold through $R$; the next inequality exits. Using a bar’s still-forming high as $P$ while the bar is open is a delay-0 last-print rule — document it; default is completed prints.

Exit a long at or through resistance:

$$
P \ge R \quad\Rightarrow\quad \text{exit long}
$$

Tag $R$, flatten. The spec does not reverse to short here unless $P$ is also below $C$ after a new decision — default flatten. A trend day that runs through $R$ stops you out of the only long and leaves the trend on the table.

Enter short when price is below the pivot:

$$
P < C \quad\Rightarrow\quad \text{enter short}
$$

Symmetric short entry. Long-only books suppress this. Borrow required.

Exit a short at or through support:

$$
P \le S \quad\Rightarrow\quad \text{exit short}
$$

Tag $S$, flatten. Same “no silent reverse” default. If both an exit and an opposite entry could fire on one print (gap through $C$), apply the gap policy in §4.3 first.

### 4.3 Gaps

If the session opens through $R$ or $S$, this spec does not define a fill. Default: no trade until price re-enters $(S,R)$. Do not silently switch to a fade-the-gap rule.

A gap through $R$ is not “long from $C$.” Treating the open as an entry would assume a path from $C$ that did not happen. Fade-the-gap is a different, must-document policy. If you do X = enter long because the open is above $C$ even though it is also above $R$, you skipped the gap rule and the backtest lies about this spec.

### 4.4 Holding-period P&L

Round-trip vs open fills on the current session. Report gap days separately.

$$
\mathrm{P\&L} = Q\bigl(P_{\mathrm{exit}} - P_{\mathrm{entry}}\bigr) - \mathrm{costs}
$$

Intraday round-trip minus costs. Gap days that stayed flat contribute zero by design; do not drop them from the sample to inflate hit rate. If you do X = fill at $R$ on a gap-through open, the backtest lies by taking a print the gap policy forbade.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names. Corporate actions overnight must reset the prior session’s OHLC. This step exists so a split does not look like a 50-point pivot. Illiquid names have meaningless session highs.
2. **Freeze levels.** After the prior close, compute $C,R,S$ from that session’s $P_H,P_L,P_C$. Lock them for the next session. Locking is the product; a trailing pivot is a different file.
3. **Session.** On each print (or bar close) of the current session, apply the four inequalities. Using the current day’s developing high is a bug. Completed prints exist so $P$ is knowable.
4. **Gaps.** If the open is through $R$ or $S$, stay flat until $P$ re-enters $(S,R)$. This step exists because the path rule assumed a path through $C$.
5. **Size.** Caller sets $Q$. Independent per name. No cross-sectional budget — these are per-name path rules.
6. **Blotter.** Emit intents. Do not route live orders. Flatten by the session close unless a documented overnight overlay exists (default: flatten). Overnight is a different risk book.
7. **Next day.** Recompute levels from the session that just closed. Yesterday’s $C$ must not persist; that would be a multi-day Donchian-like object.

## 6. Execution protocol

- Intraday prints. Levels are prior-session objects. If you do X = rebuild $C$ every hour from the developing range, the backtest lies by using information the classic pivot does not have.
- Gap through $R$ or $S$ at the open: skip until re-entry. Off-script alternatives (skip vs fade) must be documented; default is no trade until re-entry. If you do X = fade the gap without a flag, you are not testing this file.
- Delay: a bar’s decision must not use that bar’s still-forming high as if it were $P_H$. If you do X = set $P_H=$ today’s high so far, levels move intra-bar and the backtest lies.

## 7. Data contract

Required, point-in-time:

- Prior session official high, low, close
- Current session prints or bars (timestamped)
- Corporate-action flags overnight (so prior OHLC is the post-action session)
- ADV if you cap participation
- Borrow availability for shorts

Use unadjusted OHLC for the session’s levels; a split overnight must reset the series rather than stitch a raw jump into $P_H,P_L,P_C$.

Not used by this spec: book value, earnings, SUE, industry map, option IV.

If you do X = use a split-adjusted historical high as yesterday’s $P_H$ after an overnight split, levels are in the wrong units. If you do X = take “official high” from a series that revises hours later, restatement peeking moves $R$. If you do X = use tomorrow’s OHLC to set today’s $C$, the backtest is fiction.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| pivot formula | classic | `{classic}` only unless you add documented variants |
| gap policy | no trade until re-entry | do not fade unless documented |
| flatten at close | true | |
| delay | use completed prints | developing high is forbidden as $P_H$ |

## 9. Agent implementation contract

Build a Python module `strategies.support_and_resistance` with:

1. `levels(prior_H, prior_L, prior_C) -> (C, R, S)` — exact identities.
2. `step(state, P, C, R, S, gap_policy) -> state`.
3. `pnl(Q, P_entry, P_exit, costs) -> float`.

Levels frozen at prior close. Using the current day’s developing high is a bug. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Arbitrary levels.** $C,R,S$ are a mirror identity, not a structural support. If you do X = drop days that did not tag $R$ or $S$, the backtest lies by keeping only path-rule successes.
- **Trend days.** A session that runs from $C$ through $R$ and keeps going stops you out of the only trade and leaves the trend on the table (or worse, if you reverse off-script). If you do X = reverse at $R$ without documenting it, you are not this spec.
- **Look-ahead high.** Feeding today’s high into $P_H$ is a different, invalid pivot. If you do X = that, the backtest lies by construction.

## 11. Acceptance tests

- Synthetic prior $H/L/C$ → exact $C,R,S$ matching $R=2C-P_L$ and $S=2C-P_H$.
- A price path $C\to R$ is long then flat.
- A price path $C\to S$ is short then flat.
- Developing high of the current day must not change $C,R,S$. If bumping today’s high moves $R$, the implementation looks ahead and the backtest lies.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
