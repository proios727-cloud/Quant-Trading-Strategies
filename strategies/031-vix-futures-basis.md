---
rank: 31
slug: vix-futures-basis
title: "VIX Futures Basis Trading"
asset_class: "volatility / indexes"
style: "term-structure / mean-reversion in VIX futures"
horizon: "Days to weeks in front-month VIX futures"
instruments: "UX1 VIX futures; optional mini-S&P hedge"
---

# 031. VIX Futures Basis Trading

| Field | Value |
|---|---|
| Popularity rank (this kit) | 31 of 101 |
| Why it sits here | Contango roll-down on UX1. Standard vol-of-vol relative-value; Simon–Campasano style rules are widely copied. |
| Aliases | VIX basis, UX1 roll, VIX futures contango |
| Asset class | volatility / indexes |
| Style | term-structure / mean-reversion in VIX futures |
| Typical horizon | Days to weeks in front-month VIX futures |
| Instruments | UX1 VIX futures; optional mini-S&P hedge |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A VIX future converges toward a special VIX settlement as expiry approaches. The futures–spot basis therefore has a mechanical daily roll. Empirically that roll forecasts the futures price more than it forecasts spot VIX. Short UX1 when the basis is in contango, long UX1 in backwardation.

You are betting that the quoted UX1 will drift toward spot at a pace near $B_{\mathrm{VIX}}/T$ if spot does not explode. You are not betting that VIX itself will fall by that amount, and you are not harvesting the index VRP of file 030: that file sells option premium, this file trades a listed future against the VIX print.

Optional: overlay a mini-S&P hedge so a parallel equity selloff does not dominate the book. The hedge is a variance reducer, not a second alpha. Typical users are vol RV desks running a small, tightly stopped UX1 sleeve. Horizon is days to weeks in the front month, with a hard flatten before the last ten business days so $1/T$ does not blow up.

Expect gaps. A 2008-like VIX event is the sizing path, not the average daily range. Delay-1 is the research default.

## 2. First principles

Let $P_{\mathrm{UX1}}$ be the front-month VIX future and $P_{\mathrm{VIX}}$ the spot VIX index. The basis is the gap that must close (in expectation, not pathwise) by settlement:

$$
B_{\mathrm{VIX}} = P_{\mathrm{UX1}} - P_{\mathrm{VIX}}
$$

VIX is an option-portfolio index, not a deliverable commodity, so this gap can widen before it converges. If you treat $B_{\mathrm{VIX}}$ as an arbitrage residual that must shrink every day, a spike week will look like a bug rather than the risk you are paid for. $B_{\mathrm{VIX}}>0$ is contango: the future sits above spot. $B_{\mathrm{VIX}}<0$ is backwardation. With $T$ business days to settlement, a constant-basis path would roll the future by about $B_{\mathrm{VIX}}/T$ per day:

$$
D = \frac{B_{\mathrm{VIX}}}{T}
$$

$D$ is a daily roll **forecast for the future**, not a forecast that spot VIX will move by $D$. Dividing by $T$ annualizes the remaining gap into a per-day number that can be banded. When $T$ is small, the same dollar gap becomes a huge $D$; that is expiry noise, which is why this spec refuses $T<10$. Shorting UX1 in contango harvests that roll if spot does not explode. Longing UX1 in backwardation harvests the opposite roll if the spike fades.

That is the whole strategy. Everything below is the entry/exit band, the optional equity hedge, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P_{\mathrm{UX1}}$ | front-month VIX futures price |
| $P_{\mathrm{VIX}}$ | spot VIX |
| $B_{\mathrm{VIX}}$ | basis $P_{\mathrm{UX1}}-P_{\mathrm{VIX}}$ |
| $T$ | business days to UX1 settlement |
| $D$ | daily roll $B_{\mathrm{VIX}}/T$ |
| $Q_{\mathrm{UX1}}$ | signed UX1 contracts (positive = long) |
| $h$ | mini-S&P hedge ratio (contracts of ES per UX1) |
| $I$ | gross futures notional budget |
| $R_{\mathrm{ES}}$ | front mini-S&P future return |

## 4. Mathematics

### 4.1 Basis and daily roll

At each decision bar, using only stamps $\le t < t_{\mathrm{fill}}$,

$$
B_{\mathrm{VIX}} = P_{\mathrm{UX1}} - P_{\mathrm{VIX}}
$$

Both prints must share a session convention. Mixing a VIX cash close with an ETH UX1 last will manufacture a basis that is not on the tape. Permuting tomorrow’s VIX cannot be allowed to change today’s $B_{\mathrm{VIX}}$.

Divide by remaining life, requiring $T \ge 10$ so the $1/T$ scale is not dominated by expiry noise:

$$
D = \frac{B_{\mathrm{VIX}}}{T}
$$

If $T<10$, flatten or roll to the next contract; do not trade the last days on this rule. $T$ is business days on the VIX futures settlement calendar, not calendar days and not a 365-day fraction. A holiday-adjusted $T$ that still counts a half-session as a full day is acceptable if it is frozen before the fill. The $1/T$ scaling is why a ten-point basis with 50 days left is a quiet roll, and the same basis with 4 days left is noise.

### 4.2 Entry and exit

Open and close UX1 from $D$ with hysteresis so a $0.10$ print does not churn:

- Open **long** UX1 if $D < -0.10$; close the long if $D > -0.05$
- Open **short** UX1 if $D > 0.10$; close the short if $D < 0.05$
- Otherwise hold the previous signed state (or stay flat if none)

$D$ is in VIX futures points per business day, matching the cited band. Hysteresis is load-bearing: without the inner band, a 0.09/0.11 flicker will flip the book every other day and the edge is turnover. The previous state is part of the signal; a stateless sign($D$) is a different rule.

### 4.3 Optional equity hedge

UX1 changes co-move with equity selloffs. On a trailing window that ends before the fill, regress UX1 price changes on front mini-S&P returns and take the slope $\beta$. Against a long UX1 position, short $\lvert\beta\rvert$ minis (and the reverse against a short UX1):

$$
Q_{\mathrm{ES}} = -h\, Q_{\mathrm{UX1}}
$$

with $h$ the OLS hedge ratio in contract units. Rebuild $h$ only on data dated $\le t$. The hedge exists to cut parallel equity risk, not to add a second trend-following sleeve. If ES is halted or the window is too short, skip the overlay and run UX1 standalone; do not invent $h=1$.

### 4.4 Holding-period P&L

Futures P&L is variation margin on the UX1 (and ES) marks from fill to next rebalance, minus costs and roll costs if the contract is switched. Report:

- P&L over $I$ (or over one-contract risk)
- annualized Sharpe on **non-overlapping** holding-period returns
- fraction of days in long / short / flat

$$
\mathrm{P\&L} = Q_{\mathrm{UX1}}\,\Delta P_{\mathrm{UX1}} + Q_{\mathrm{ES}}\,\Delta P_{\mathrm{ES}} - \mathrm{costs}
$$

Multipliers belong in the conversion from $Q$ to dollars; do not hide them inside $\Delta P$ in one test and outside in another. A Sharpe computed only on contango days, dropping spike weeks, is not an acceptance of this spec.

## 5. Step-by-step algorithm

1. **Contract.** Front-month VIX future UX1. Skip if volume or open interest is below a minimum, or if $T<10$. This step exists because the $1/T$ forecast is not defined in a useful way into expiry, and a dead contract will print a basis you cannot trade.
2. **Basis.** Compute $B_{\mathrm{VIX}}$ and $D$ from the last prints before $t_{\mathrm{fill}}$. Using the fill print itself is delay-0. The settlement calendar that produces $T$ must be known at $t$, not revised after a holiday update.
3. **State machine.** Apply the $\pm 0.10$ / $\pm 0.05$ hysteresis to the previous signed state. Without previous state you cannot implement hysteresis; storing only today’s $D$ is a bug.
4. **Size.** One-contract or vol-target UX1 so that a 2008-like VIX event fits the loss budget. Cap by ADV. Average daily range is the wrong scaler: UX1 gaps.
5. **Hedge (optional).** Estimate $h$ on a trailing window ending at $t$. Set $Q_{\mathrm{ES}}=-h Q_{\mathrm{UX1}}$. Skip if the overlay is off or if ES data are missing; do not fall back to a hardcoded mini count.
6. **Blotter.** Emit UX1 (and ES) intents, round to contract size. Do not route live orders. Rounding that silently drops the ES leg leaves the equity risk you just estimated.
7. **Roll.** Switch to the next VIX contract before settlement; recompute $D$ on the new front. Holding old UX1 into special settlement is not this rule.
8. **Rebalance.** Daily. Delay-1: today’s $D$ trades the next close or next open. Intraday state updates on the same bar are research-only.

## 6. Execution protocol

- Default fill: next close after $D$ is known. Delay-0 is research-only.
- Gaps on VIX spikes are first-order. Size for a 2008-like vol event, not for average daily range. A backtest that clips UX1 moves at 5 points is not this spec.
- If UX1 is halted or the quote is crossed, stay flat. Do not interpolate VIX into a fake future. A synthetic $P_{\mathrm{UX1}}$ from a vol surface is a different product.
- Flatten into the last 10 business days rather than holding into settlement. The $T<10$ rule is a flatten, not a “trade smaller.”

## 7. Data contract

Required, point-in-time:

- VIX spot and UX1 futures prices, with settlement calendar and $T$
- Contract multiplier and RTH/ETH session stamps
- Volume / open interest for liquidity filters

Optional: front mini-S&P future for the OLS hedge.

Not used by this spec: option chains, book value, earnings, SUE, index constituent weights, borrow for equity shorts (unless you overlay a short-vol ETN, which this file does not).

No look-ahead on $T$, rolls, or VIX prints. A roll date announced after $t$ does not change the $t$ contract choice. Revised VIX after the close does not change $B_{\mathrm{VIX}}(t)$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| open long | $D < -0.10$ | backwardation |
| close long | $D > -0.05$ | hysteresis |
| open short | $D > 0.10$ | contango |
| close short | $D < 0.05$ | hysteresis |
| min $T$ | 10 business days | flatten below this |
| equity hedge | off | on → OLS mini-S&P |
| hedge window | 60 days | ends before fill |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.vix_futures_basis` with:

1. `basis(ux1, vix) -> float` — $B_{\mathrm{VIX}}$.
2. `daily_roll(basis, T) -> float` — $D=B_{\mathrm{VIX}}/T$; refuse $T<10$.
3. `state(D, prev_state, thresholds) -> str` — `{long, short, flat}` with hysteresis, no look-ahead.
4. `hedge_ratio(ux1_changes, es_returns, window) -> float` — OLS $h$ on a window ending at $t$.
5. `blotter(state, h, I, lot) -> list[OrderIntent]` — UX1 and optional ES, never live routing.
6. `pnl(Q_ux1, dP_ux1, Q_es, dP_es, costs) -> float` — matches the P&L identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Vol explosion.** Short UX1 in a spike; basis can widen before it converges. The hysteresis will keep you short through $D=0.07$ even as P&L is already large and negative.
- **Sticky richness.** Contango can persist while $D$ stays above the close-short band. Harvesting roll every day is not the same as mean-reversion of $B_{\mathrm{VIX}}$ to zero this week.
- **Futures–spot dislocation.** VIX is an option portfolio, not a deliverable; UX1 need not track $P_{\mathrm{VIX}}$ tick for tick. Special settlement can still gap versus the cash index you used in $B_{\mathrm{VIX}}$.
- **Expiry.** Trading $T<10$ turns $D$ into noise. Ignoring the flatten rule to “capture the last roll” is a different spec.
- **Hedge residual.** OLS $h$ fitted in calm markets under-hedges a crash because UX1 convexity versus ES is not constant.
- **Crossed or halted tape.** Interpolating a basis through a halt manufactures fills that did not exist.

## 11. Acceptance tests

- $B_{\mathrm{VIX}}=P_{\mathrm{UX1}}-P_{\mathrm{VIX}}$ and $D=B_{\mathrm{VIX}}/T$ to `1e-8` on a toy quote.
- $D=0.12$ from flat → short; then $D=0.07$ → still short; $D=0.04$ → flat.
- $D=-0.12$ from flat → long; then $D=-0.07$ → still long; $D=-0.04$ → flat.
- Permuting UX1 and VIX after $t$ must not change the $t$ state.
- $T<10$ → no new open; existing position is flattened or rolled.
- Adding linear costs $\tau$ weakly decreases P&L.
- A test that drops all days with $\lvert\Delta P_{\mathrm{UX1}}\rvert$ above a cap is not a pass: those days are the risk.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
