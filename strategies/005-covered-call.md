---
rank: 5
slug: covered-call
title: "Covered Call"
asset_class: "options"
style: "income / mildly bullish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 005. Covered Call

| Field | Value |
|---|---|
| Popularity rank (this kit) | 5 of 101 |
| Why it sits here | The most common listed-option overlay on long stock. Buy-write indexes (BXM) and covered-call ETFs are institutional products. |
| Aliases | buy-write |
| Asset class | options |
| Style | income / mildly bullish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long the stock and short a call with strike $K$. Same terminal payoff as a short (naked) put, by put-call parity. Income comes from repeated sale of OTM calls against an unchanging long stock book.

You are betting that the stock stays below $K$ through expiry, or that a modest rally is worth less than the credit $C$ you sold. You keep the shares and the premium if $S_T < K$. You are not betting on a large upside: a print through $K$ assigns the stock away and $P_{\max}$ is the whole gain. You are also not running a free-standing short-vol book. The shares you already own are the cover; without them this file is a naked short call, which is a different mandate and a different $L_{\max}$.

Payoff sketch, one share, ignore financing: at $S_T=0$ the stock is a total loss cushioned only by $C$, so $f_T=-(S_0-C)=-L_{\max}$. At $S_T=K$ the call is at the money, the shares can be called at $K$, and $f_T=K-S_0+C=P_{\max}$. Far above $K$ the same cap holds; extra rally is the caller's, not yours.

## 2. First principles

A long share, marked from the purchase price $S_0$, has terminal P&L

$$
S_T - S_0
$$

That line is unbounded above and unbounded below, down to $-S_0$ if the name goes to zero. The covered call exists because you are willing to sell the unbounded top in exchange for cash today. The stock identity does not change; the short call does.

A short European call with strike $K$ pays the opposite of the long-call intrinsic:

$$
-(S_T - K)_+
$$

The kink is at $K$. Below $K$ the call dies and this piece is zero. Above $K$ it falls one-for-one with $S_T$, cancelling the stock's further gain. That cancellation is the designed cap, not a bug. Early exercise on an American call can move the kink in calendar time; the identity above is the European expiry claim.

Selling that call brings in a credit $C$ at $t=0$. Adding the three pieces is the covered call:

$$
f_T = S_T - S_0 - (S_T - K)_+ + C
$$

$C$ is cash you already have. It shifts the whole payoff up by a constant and does not move the kink. Live P&L before expiry is not this identity: theta, implied vol, and dividends sit in the mark. This file's $f_T$ is hold-to-expiry, European-style.

The call–put identity $(S_T-K)_+ - (K-S_T)_+ = S_T-K$ rewrites the same book as a short put plus cash:

$$
f_T = K - S_0 - (K - S_T)_+ + C
$$

That is why a covered call is not a new shape. It is a short put financed with a long stock-plus-bond package. If you already own the shares, you are overlaying income. If you do not own them, you are not in this file.

You are not running a free-standing short-vol book. You already own the shares the call can be assigned against. The designed outcome is: keep $C$ if the stock stays below $K$; if it rallies through $K$, the shares are called away and upside stops.

That is the whole strategy. Everything below is just how to pick $K$, how to size $Q$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying purchase price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | short-call strike |
| $C$ | call premium received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $Q$ | share count (positive = long) |
| $m$ | option multiplier (usually $100$) |

One short call covers $m$ shares. Lot integrity is $Q = n m$ for integer $n \ge 1$.

## 4. Mathematics

### 4.1 Terminal payoff

Stock plus short call, premium $C$ received:

$$
f_T = S_T - S_0 - (S_T - K)_+ + C
= K - S_0 - (K - S_T)_+ + C
$$

The two lines are the same function of $S_T$. The first is the blotter (stock, short call, credit). The second is the short-put rewrite. Tests must match both on a dense grid; matching one and not the other is a sign error in the kink.

Below $K$ the call dies and $f_T = S_T - S_0 + C$. At or above $K$ the shares are called away and $f_T = K - S_0 + C$. Sketch: $S_T=0$ prints $-L_{\max}$; $S_T=K$ prints $P_{\max}$; $S_T\to\infty$ stays at $P_{\max}$.

### 4.2 Break-even

Set $f_T=0$ on the uncalled region $S_T < K$:

$$
S^\ast = S_0 - C
$$

The credit lowers the stock's break-even by $C$. If $S_T$ finishes between $S^\ast$ and $K$, the overlay made money relative to buying the stock alone at $S_0$. If $S_T$ finishes below $S^\ast$, the stock loss ate the premium. There is no second break-even above $K$: that region is the flat cap.

### 4.3 Extrema

Maximum profit is the capped upside at $K$ plus the credit:

$$
P_{\max} = K - S_0 + C
$$

That number is the whole trade if the name rips. A covered-call index that "underperforms in a bull market" is this identity, not a tracking error. Choosing $K$ further OTM buys back some $P_{\max}$ by giving up some $C$.

Maximum loss is the stock going to zero, cushioned only by $C$:

$$
L_{\max} = S_0 - C
$$

A gap to zero is a stock gap. The short call expires worthless and does not hedge the left tail. Do not describe this overlay as defined-risk insurance; that is the protective put.

Equivalent short-put payoff: $C - (K-S_T)_+$ plus a cash bond of $S_0$, which is put-call parity.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names with a tight option chain. Price and ADV above a minimum. Keep delisted names until the delist date (no survivorship). Illiquid calls make the credit untradeable; a wide bid–ask turns $C$ into a fiction. Survivorship would drop names that went to zero, which is exactly $L_{\max}$.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. Do not use a later print. $S_0$ is the purchase mark in $f_T$. A later print look-aheads the stock P&L and the moneyness of $K$.
3. **Strike.** Choose $K \ge S_0$ (OTM overlay) or $K \approx S_0$ (ATM buy-write). Default OTM ratio $K/S_0$ in $1.02$–$1.10$. Further OTM keeps more upside and collects less $C$. ATM maximizes income and minimizes $P_{\max}$. The choice is the mandate, not a hidden parameter.
4. **Expiry.** Pick the listed expiry in the 20–45 calendar-day cluster unless the mandate says otherwise. That cluster is where listed equity options are usually tightest. A weekly is more theta and more roll cost; a LEAP is a different overlay.
5. **Size.** Buy $Q$ shares, $Q$ a multiple of $m$. Sell $Q/m$ calls. Do not oversell calls against the stock. Extra short calls are naked. Lot integrity exists so assignment delivers a round stock lot, not a residual stub.
6. **Premium.** $C$ is the credit actually received (bid or better on the short). $C$ is not the mid. Using mid inflates $P_{\max}$ and understates $L_{\max}$ by half the spread, twice if you also mark the stock at mid.
7. **Blotter.** Emit intents: long stock, short call. Do not route live orders. The spec stops at intent. Routing is a venue problem this file does not authorize.
8. **Hold / roll.** Hold to expiry, or roll the short call when it is near expiry and still OTM. If assigned, the stock is called away at $K$; that is the designed cap. Rolling is the income engine of buy-write indexes; it is a new trade with a new $C$, not a continuation of this $f_T$.

## 6. Execution protocol

- Default fill: next available auction or limit after $S_0$ and the chain are known. Delay-0 mid is a backtest choice, not a live book.
- Prefer selling the call as a limit at the bid or better; do not lift the offer on a short.
- Assignment risk rises into expiry if the call is ITM and the stock goes ex-dividend.
- Roll rule used in practice: if $S_T < K$ at expiry, sell the next-dated call with the same $K$ or a new OTM strike. That is the covered-call income engine.
- Cap $Q$ by ADV. Do not size off notional without a liquidity filter.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: borrow (the stock leg is long), book value, earnings.

No restatement peeking. Delisted names stay in the sample until the delist date.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K/S_0$ | $1.02$–$1.10$ OTM; $1.00$ ATM | monthly overlay vs buy-write |
| tenor | 20–45 calendar days | liquid monthly/weekly cluster |
| $Q$ | multiple of $m$ | one short call per $m$ shares |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.covered_call` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $Q$ is a multiple of $m$; one short call per $m$ shares; $P_{\max}$ / $L_{\max}$ match closed-form identities on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Capped upside.** A rally through $K$ assigns the stock away; $P_{\max}$ is the whole gain. A name that doubles after you sold a 5% OTM call still pays $K-S_0+C$, not the double.
- **Gap-down.** The left tail is the stock, cushioned only by $C$. Overnight news that halves the name leaves you long the stub plus a now-worthless short call.
- **Dividend assignment.** American short calls go ITM into an ex-date and can be exercised early. You lose the stock before the dividend and keep a short that is no longer covered if you are not filled on the assignment.
- **Covered-call margin.** Some venues still margin the short option even though the call is covered. Treating $C$ as free cash for a new trade can force a liquidation.
- **Roll cost.** Repeatedly selling the next month after a grind higher can pin you into a sequence of assignments; each new $C$ is smaller as $K$ is rolled up, and each missed rally is another $P_{\max}$ left on the table.

## 11. Acceptance tests

- Two-piece identity: on a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $S_T-S_0-(S_T-K)_++C$ and also $K-S_0-(K-S_T)_++C$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=K$, $f_T=P_{\max}$. As $S_T\to 0$, $f_T \to -L_{\max}$.
- Put-call: the covered-call $f_T$ matches a short put with the same $K$ and $C$ plus a cash bond of $S_0$.
- Reject a spec with $Q$ not a multiple of $m$, or with more short calls than $Q/m$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kink at $K$ except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
