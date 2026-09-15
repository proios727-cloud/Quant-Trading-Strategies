---
rank: 67
slug: diagonal-put-spread
title: "Diagonal Put Spread"
asset_class: "options"
style: "diagonal / bearish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 067. Diagonal Put Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 67 of 101 |
| Why it sits here | Poor-man’s covered put: long deep ITM put, short near OTM puts. |
| Aliases | — |
| Asset class | options |
| Style | diagonal / bearish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long a deep ITM put $K_1$ with expiry $T'$ and short an OTM put $K_2$ with earlier expiry $T < T'$, with $K_1 > S_0 > K_2$. Net debit. The long put mimics short stock more closely than an ATM put calendar, so the structure is more crash-protected than a same-strike put calendar.

You are betting that spot stays in a band above the short strike so you can keep selling OTM puts against a stock-replacement long put. You are not running a calendar pin at a single $K$, and you are not holding short shares. The long is a high-delta put, not an ATM remaining option. A rally is the slow killer: the LEAP-style put decays and you lose up to the debit. A crash is structurally better hedged than in `066`, but American assignment on the short $K_2$ put is still a live operational risk.

The typical user wants a poor-man’s covered put: income from near-dated OTM puts without locating borrow. Horizon is again two-clock: manage at $T$, roll if spot is still above $K_2$ and below the stop, else flatten. If the back-month $K_1$ put is a wide one-sided LEAP quote, skip; $D$ computed off mid will not fill.

Do not warehouse a naked short $K_2$ put. Size off $D$ and off remaining premium on the long, not off the short-put credit. Vol crush on the long is first-order even if spot is unchanged.

## 2. First principles

Two listed puts, different strikes and different expiries. Buy the deferred deep ITM put, sell the nearer OTM put, pay net debit $D$. The strike order $K_1 > S_0 > K_2$ is load-bearing: if you swap them you have a different diagonal (or a calendar). The long is the stock-replacement short; the short is the income overlay.

At the front expiry $t=T$ the short OTM put settles to intrinsic:

$$
-(K_2 - S_T)_+
$$

Above $K_2$ this term is zero and the overlay kept its credit. Below $K_2$ you owe $K_2-S_T$. That is assignment territory on American names. This piece exists so the front-expiry mark includes the short you actually sold, not a same-strike calendar intrinsic.

The long $K_1$ put is still alive. Write $V(S_T)$ for its mark at $t=T$. Front-expiry P&L is

$$
f_T = V(S_T) - (K_2 - S_T)_+ - D
$$

There is no simple closed $f_T$ in the spot alone. Because $K_1$ is deep ITM, $V(S_T)$ tracks $K_1 - S_T$ more tightly than an ATM calendar’s remaining put, which is why a crash is less damaging than in `066`. $V$ is still a mark: rates, dividends, and back-month IV all move it. A surface dated after $T$ is look-ahead. Tests must take a supplied `back_mark`.

The usual working peak is the live mark of the long put when the short expires near its strike, minus the debit. With $V$ that mark (practitioner default: evaluate at the short strike, or at the pin you actually got):

$$
P_{\max} = V - D
$$

This is not a closed intrinsic. If the short expires at $K_2$ and the long is still deep ITM, $V$ can be large relative to $D$ and the overlay looks good. If back-month vol crushed, $V$ can disappoint even with a perfect pin at $K_2$. Store $P_{\max}$ from a mark, not from $K_1-K_2$.

If the long put is crushed by a rally, you cannot lose more than what you paid for the package under European marks:

$$
L_{\max} = D
$$

That is the rally bound: long put $\to 0$, short put expires worthless, you are out the debit. Early exits can be worse if you sell the long into a vol crush before expiry. American assignment on the short still gaps the mark on the way down, so $L_{\max}=D$ is not a crash stress.

After the short expires, residual is a long deep ITM put. Roll another OTM short put when spot stays in the band above $K_2$. That is the poor-man’s covered-put engine. Rolling after a rally through the stop leaves you writing puts against a decaying replacement. Rolling after $S_T \ll K_2$ without covering the old short stacks assignment.

**Payoff sketch (at the front expiry).** Deep ITM long, OTM short. At $S_T$ far above both strikes, $V\to 0$ and $f_T\to -D$ (rally, lose the debit). At $S_T=K_2$, the short dies and $f_T=V(K_2)-D$ (working peak). At $S_T=0$, the short owes $K_2$ while $V(0)$ is a remaining deep-ITM put, so the long should roughly cover; the residual is mark versus intrinsic, assignment, and $D$. The sketch is a stock-replacement short with an OTM put overlay, not a pin hill at one $K$.

That is the whole strategy. The long is a stock-replacement short; the short puts are the income overlay.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at the **front** expiry $T$ |
| $K_1$ | long put strike (deep ITM), $K_1 > S_0$ |
| $K_2$ | short put strike (OTM), $K_2 < S_0$ |
| $T < T'$ | front and back expiries |
| $V$ | mark of the long $K_1$ put at $t=T$ in the peak scenario |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | P&L at the front expiry, including $D$ |
| $S_{\mathrm{stop\text{-}loss}}$ | upper roll/exit level |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss evaluated at $t=T$ |

One long back-month put, one short front-month put. Quantity ratio $1:1$. Strike order $K_1 > S_0 > K_2$.

## 4. Mathematics

### 4.1 Premium

Net debit $D > 0$: the deep ITM LEAP-style put costs more than the OTM front put brings in. If $D$ is a large fraction of $K_1-S_0$, you are paying up for a synthetic short and the overlay credit does not justify it. Fill at the $K_1$ ask and the $K_2$ bid; mid-to-mid $D$ is not a fill.

### 4.2 Front-expiry mark

$$
f_T = V(S_T) - (K_2 - S_T)_+ - D
$$

$V(S_T)$ is the live (or model) mark of the $K_1$, $T'$ put at $t=T$. The short term is settled intrinsic on $K_2$ only. Do not substitute $(K_1-S_T)_+$ for $V$; that would pretend the long expires at $T$. Deep ITM means $V$ is closer to intrinsic than an ATM calendar, which is the crash improvement versus `066`, not a reason to drop the mark.

### 4.3 Max profit and loss

$$
P_{\max} = V - D
$$

Metrics take a supplied peak mark $V$. Changing the evaluation spot (short strike versus actual $S_T$) changes the number; document which you used.

$$
L_{\max} = D
$$

$L_{\max}=D$ is the rally bound (long put $\to 0$). A crash is structurally better hedged than a calendar because the long is already deep ITM, but American assignment on the short $K_2$ put can still gap the mark. Do not size as if $D$ were a crash cap.

### 4.4 Roll region

Roll the short if

$$
K_2 \le S_T \le S_{\mathrm{stop\text{-}loss}}
$$

Below $K_2$ the old short is in the money; manage assignment before selling another. Above the stop the long put is the decaying residual — flatten or accept $L_{\max}$. The band exists so the overlay repeats only while the replacement short is still intact.

### 4.5 Mark-to-market

Before $T$, mark is the sum of option mids minus initial $D$. Delta-hedging replaces the expiry identities with a Greek book. The long put’s high put delta is the stock-replacement feature; vol crush on that LEAP is a first-order residual. A backtest that ignores vega on $K_1$ will look like a stable covered put and then break on a vol crush with spot unchanged.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed puts. The $K_1$ back-month contract must have a two-sided market; skip if only a wide LEAP quote. This filter exists because $D$ and $V$ are fiction on a one-sided LEAP.
2. **Strikes and tenors.** $K_1 > S_0 > K_2$. Long 3–12 months, short 2–6 weeks, $T < T'$. Long put delta typically high (deep ITM). Same-strike would be `066`; inverted strikes are a different diagonal.
3. **Legs.** Buy 1 put $K_1$ expiry $T'$, sell 1 put $K_2$ expiry $T$. Quantity ratio $1:1$. The ratio keeps this a covered-put analogue, not a ratio backspread.
4. **Premium.** Require $D>0$. Reject if $D$ exceeds a caller cap versus $K_1 - S_0$ (you are paying up for a synthetic short). The cap is how you avoid buying an expensive replacement.
5. **Metrics.** Store $P_{\max}=V-D$ from a mark of the long put, and $L_{\max}=D$. No closed $S^\ast$ in $S_T$ alone.
6. **Blotter.** Emit a diagonal put intent. Do not route live orders. One ticket when both quotes exist.
7. **At $T$.** If $K_2 \le S_T \le S_{\mathrm{stop\text{-}loss}}$, sell another OTM put; if $S_T \ll K_2$, manage assignment; if $S_T$ rallies through $S_{\mathrm{stop\text{-}loss}}$, the decaying long put is the residual risk — flatten or accept $L_{\max}$. This is the income schedule.

## 6. Execution protocol

- Treat the long put as a stock-replacement short: high put delta, not an ATM calendar. If the long is not deep ITM, you do not have the crash improvement this file claims versus `066`.
- Sell nearer OTM puts against it on a covered-put schedule, without locating borrow. Do not sell a further ITM put as the “overlay”; that is a different ratio.
- Enter as one diagonal when both quotes exist; do not warehouse a naked short $K_2$ put. Legging the short first is a crash-naked put.
- Vol crush on the long is the silent killer on a rally. Size off $D$ and off that remaining premium, not off the short-put credit. A backtest that sizes off credit will over-gear the LEAP.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain on **two expiries and two strikes**: bid/ask, strike, call/put flag, open interest, implied vol, multiplier
- A pricing mark for the long $K_1$ put at $t=T$, used as $V(S_T)$
- Dividends and rates if $V$ is model-based (deep ITM puts are dividend-sensitive)
- At each expiry: settlement print and American early-exercise events

Not used by this spec: book value, earnings, SUE.

These identities treat remaining value as a European-style claim. American early exercise on the short put can invalidate the roll. Do not mark $V$ through $t>T$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K_1$ | deep ITM, $K_1 > S_0$ | high put delta |
| $K_2$ | OTM, $K_2 < S_0$ | short put |
| long tenor $T'$ | 3–12 months | stock-replacement |
| short tenor $T$ | 2–6 weeks | income overlay |
| quantity ratio | $1:1$ | one long, one short |
| $S_{\mathrm{stop\text{-}loss}}$ | caller-set | roll if $K_2 \le S_T \le S_{\mathrm{stop\text{-}loss}}$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.diagonal_put_spread` with:

1. `legs(spec) -> list[Leg]` — long put $K_1,T'$, short put $K_2,T$, with $K_1 > K_2$ and $T < T'$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec, back_mark) -> float` — implements $f_T = V(S_T) - (K_2-S_T)_+ - D$.
4. `metrics(spec, V) -> dict` — `P_max`, `L_max`, debit flag.
5. `validate(spec)` — $K_1 > S_0 > K_2$ (or at least $K_1 > K_2$), $T < T'$, qty $1:1$.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Rally.** Leaves a decaying long put. You lose up to $D$, plus any remaining time-value crush if you exit early. Spot unchanged with vol crush is enough.
- **Vol crush.** The LEAP-style long put can lose vega even if spot is unchanged. That is the silent P&L, not the short-put credit.
- **Crash assignment.** Short $K_2$ put can be assigned; the long $K_1$ put is a hedge, not an automatic offset on American names. You can be short stock versus a still-open long put.
- **Wide LEAP markets.** $D$ computed off mid can be fictional; fill at the ask on $K_1$ and the bid on $K_2$. The backtest then books a debit that never existed.
- **Wrong $V$.** Using a stale or future-dated surface look-aheads the mark and invents roll-time profit.

## 11. Acceptance tests

- Reject $K_1 \le K_2$, $T \ge T'$, or quantity ratio other than $1:1$.
- At a supplied peak mark $V$, $P_{\max} = V - D$.
- If $S_T > K_2$ and the short expires worthless, $f_T = V(S_T) - D$.
- Grid of $S_T$ plus a supplied $V(S_T)$: $f_T$ equals the listed-leg mark minus $D$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
