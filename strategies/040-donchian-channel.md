---
rank: 40
slug: donchian-channel
title: "Channel (Donchian)"
asset_class: "equities"
style: "breakout / trend"
horizon: "Daily. $T$-day high/low channel."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 040. Channel (Donchian)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 40 of 101 |
| Why it sits here | Donchian / Turtle breakout pedigree. This file writes both the fade identity and the breakout inversion; they have opposite signs. |
| Aliases | Donchian channel, Turtle channel |
| Asset class | equities |
| Style | breakout / trend |
| Typical horizon | Daily. $T$-day high/low channel. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A $T$-day high/low channel. The simple rule written here **fades** the channel: long at the floor, short at the ceiling. The Turtle-style inversion **follows** a break: long on a new $T$-day high, short on a new $T$-day low. You must pick one `mode` and not mix them. Wider channel means higher volatility of the signal.

You are betting either that tagging the envelope is cheap/rich versus the window (fade) or that leaving the envelope is a new trend (breakout). Those are opposite signs on the same $B_{\mathrm{up}},B_{\mathrm{down}}$. You are not running pivots, not requiring volume unless you document it, and not mixing modes in one book.

Typical user: a Turtle-style futures overlay (`mode=breakout`) or a short-horizon mean-reversion overlay (`mode=fade`, this file’s default). Horizon intuition: daily bars, $T=20$ common, $T=55$ Turtle. Wider $T$ → fewer tags, larger moves when you do tag.

If you include today’s $P$ in the max/min, “new high” is tautological and the backtest lies. If you mix fade and breakout signs, unit tests must fail.

## 2. First principles

Over a trailing window of $T$ past prices $P(1),\ldots,P(T)$ (not including today), the highest high and lowest low are

$$
B_{\mathrm{up}} = \max\bigl(P(1),\ldots,P(T)\bigr)
$$

Upper band = window max, yesterday back through $T$ days, **not** today. True Donchian uses highs, not only closes; close-only is an approximation you must document. If $P_t$ is inside this max, a new high is automatic whenever price is at the high of the window including today — tautology, delay-0.

$$
B_{\mathrm{down}} = \min\bigl(P(1),\ldots,P(T)\bigr)
$$

Lower band = window min, same delay. True Donchian uses lows. A split without adjustment can print a fake floor. The two bands together are the envelope today’s $P$ is compared to.

Today’s price $P$ sits relative to that envelope. Two opposite readings of the same envelope exist.

**Fade:** tagging the floor is “cheap vs the window,” tagging the ceiling is “rich vs the window.” Mean-reversion inside the band:

$$
\mathbb{E}[P_{\mathrm{fwd}} - P \mid P = B_{\mathrm{down}}] > 0, \qquad \mathbb{E}[P_{\mathrm{fwd}} - P \mid P = B_{\mathrm{up}}] < 0
$$

Empirical fade claim: at the floor, next move expected up; at the ceiling, expected down. This is not an identity. On a running trend the ceiling keeps tagging and the fade dies. On continuous prices equality $P=B$ almost never hits — implement as $\le$ / $\ge$ with the band excluding today.

**Breakout:** leaving the envelope is a new trend. Continuation outside the band — the sign flips relative to fade.

This spec’s default is fade. Breakout is a documented alternative, not a silent default.

That is the whole strategy. Everything below is the two mode tables, the delay (band excludes today), and how equality is relaxed on continuous prices.

### Worked intuition

$T=20$. The last 20 days’ high is 50, low is 45. Today prints 50. **Fade:** at the ceiling → short. **Breakout:** at a new high → long. Same print, opposite books — that is why `mode` is required. If today’s 50 is also folded into the max, the test “is $P$ a new high?” is always yes when $P$ equals the including-today max; delay-1 keeps 50 out of $B_{\mathrm{up}}$ so the comparison is against *yesterday’s* 20-day high.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(1),\ldots,P(T)$ | past prices in the channel window; $P(1)$ is yesterday |
| $P$ | today’s price (decision bar) |
| $B_{\mathrm{up}}$ | window max |
| $B_{\mathrm{down}}$ | window min |
| $T$ | window length |
| `mode` | `{fade, breakout}` |
| $s \in \{-1,0,+1\}$ | position side |
| $Q$ | signed share holdings |

True Donchian uses highs and lows, not only closes. Close-only is an approximation; document it.

## 4. Mathematics

### 4.1 Channel

The upper and lower bands, computed on $t-1,\ldots,t-T$ and compared to $P_t$, are

$$
B_{\mathrm{up}} = \max\bigl(P(1),\ldots,P(T)\bigr)
$$

Window max excluding today. This is the ceiling the fade shorts and the breakout buys. Mixing high/low with close-only mid-sample is a silent spec change.

$$
B_{\mathrm{down}} = \min\bigl(P(1),\ldots,P(T)\bigr)
$$

Window min excluding today. Floor the fade buys and the breakout shorts. Wider $T$ raises the vol of the signal because tags are rarer and further from the middle of the range.

### 4.2 Fade mode (default)

The simple fade rule: long / cover at the floor, short / sell at the ceiling:

$$
P = B_{\mathrm{down}} \quad\Rightarrow\quad \text{long / cover}
$$

At the floor, buy. On continuous prices use $P \le B_{\mathrm{down}}$. The band still excludes today, or a new low is tautological. This is mean-reversion versus the window, not versus a cluster residual.

$$
P = B_{\mathrm{up}} \quad\Rightarrow\quad \text{short / sell}
$$

At the ceiling, short. Use $P \ge B_{\mathrm{up}}$ in code. A running high keeps you short — that is how fade dies in trends. Default `mode=fade`.

Equality $P=B$ almost never hits on continuous prices. Implement as $P \le B_{\mathrm{down}}$ / $P \ge B_{\mathrm{up}}$ with the band **excluding** today (delay).

### 4.3 Breakout mode (Turtle-style inversion)

If `mode='breakout'`, reverse the signs: follow a new $T$-day high or low:

$$
P \ge B_{\mathrm{up}} \quad\Rightarrow\quad \text{long / cover}
$$

New high versus the trailing max (excluding today) → long. Turtle pedigree. Same $B_{\mathrm{up}}$ as fade, opposite sign. If this fires in a fade book, `mode` is wrong.

$$
P \le B_{\mathrm{down}} \quad\Rightarrow\quad \text{short / sell}
$$

New low → short. Ranges that tag both bands repeatedly whipsaw this reading — that is how breakout dies in chop. Volume confirmation is optional and not part of the identities.

A new high vs a trailing max must signal **short** in fade mode and **long** in breakout mode. Mixing the two modes in one book is a bug.

Wider channel $\Rightarrow$ higher volatility. Volume confirmation is optional and not part of the identities.

### 4.4 Holding-period P&L

Per-name P&L from entry to exit, $Q<0$ on shorts:

$$
\mathrm{P\&L} = Q\bigl(P_{\mathrm{exit}} - P_{\mathrm{entry}}\bigr) - \mathrm{costs}
$$

Share P&L minus costs. Breakout and fade have opposite signs; a test that only checks “a tag produces a nonzero $Q$” is too weak. If you do X = include $P_t$ in the max and fill on $P_t$, the backtest lies by trading a tautological new high.

Breakout and fade have opposite signs. Unit tests must not confuse them.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, adjusted highs and lows (or closes if approximating). Keep delisted names until the delist date. Unadjusted highs make fake channels. This step exists so $B_{\mathrm{up}}$ is a real past high.
2. **Mode.** Required argument `{fade, breakout}`. Default implementation: fade. Required so signs cannot be mixed silently. Turtle lore is breakout; this file’s simple displayed rule is fade.
3. **Channel.** At bar $t$, compute $B_{\mathrm{up}}, B_{\mathrm{down}}$ on $t-1,\ldots,t-T$. Do not include $P_t$ in the max/min. Excluding today is the delay. Including $P_t$ makes “new high” always true at the high.
4. **Signal.** Apply the inequalities for the chosen mode. Optional: require volume confirmation; if used, document the rule. Volume is not in the identities; adding it is a different filter.
5. **Size.** Independent per name. Caller sets $Q$. Optional vol scale (wider channel already implies larger moves). No dollar-neutrality — these are timers.
6. **Blotter.** Round to lot size, emit intents. Do not route live orders. Intents only.
7. **Hold.** Until the opposite band triggers, or a documented time stop. Holding through the opposite tag “because the trend is intact” is off-script.

## 6. Execution protocol

- Delay: band excludes today. Including $P_t$ in the max makes “new high” tautological. If you do X = that, the backtest lies by construction.
- Default fill: next open after the close that tags the band (delay-1). If you do X = fill at the tag close, you trade the print that touched $B$.
- Borrow required for shorts. Cap vs ADV if needed. If you do X = short a new low in a name with no borrow, the breakout short side is fiction.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted highs and lows for true Donchian (closes only if `price_field=close` is documented)
- ADV if you cap participation
- Borrow availability for shorts
- Optional volume if confirmation is on

Not used by this spec: book value, earnings, SUE, industry map, option IV.

No restatement peeking. Delisted names stay until the delist date.

If you do X = mix close-only $B$ with high/low tags, the channel is undefined. If you do X = use unadjusted highs, splits fake breakouts. If you do X = include the hold in the trailing max, the band looks ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $T$ | 20 | also 55 (Turtle) |
| `mode` | `fade` | required; `{fade, breakout}` |
| price field | high/low | close-only is an approximation |
| volume confirm | off | |
| delay | 1 bar | band excludes today |

## 9. Agent implementation contract

Build a Python module `strategies.donchian_channel` with:

1. `channel(prices, T) -> (B_up, B_down)` — window $t-1,\ldots,t-T$.
2. `signal(P, B_up, B_down, mode) -> {-1,0,+1}` — `mode` required.
3. `pnl(Q, P_entry, P_exit, costs) -> float`.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Fade dies in trends.** A running high keeps you short. If you do X = drop trending years from a fade backtest, the backtest lies by keeping only ranges.
- **Breakout dies in ranges.** Repeated tags of the band whipsaw the Turtle reading. If you do X = skip costs on a $T=20$ breakout in chop, the backtest lies about the failure mode.
- **Mode mix.** Turtle lore is breakout; the displayed simple rule is fade. Document `mode`. If you do X = label a fade book “Turtle,” the backtest lies about pedigree and sign.

## 11. Acceptance tests

- A new high vs a trailing max must signal short in fade mode and long in breakout mode. If both modes return the same sign, the test must fail — a mixed-mode backtest lies.
- $P_t$ must not enter the max/min used at $t$. If including $P_t$ changes $B_{\mathrm{up}}$ at $t$, delay is broken and the backtest lies.
- Close-only vs high/low must not be mixed silently.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
