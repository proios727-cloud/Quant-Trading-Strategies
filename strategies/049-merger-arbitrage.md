---
rank: 49
slug: merger-arbitrage
title: "Event-Driven — M&A (Merger Arbitrage)"
asset_class: "equities"
style: "event-driven / risk arb"
horizon: "Announce to close (weeks to months). Deal-break is the left tail."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 049. Event-Driven — M&A (Merger Arbitrage)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 49 of 101 |
| Why it sits here | Classic hedge-fund sleeve. Cash deals: long target. Stock deals: long target, short acquirer in the exchange ratio. |
| Aliases | risk arb, merger arb |
| Asset class | equities |
| Style | event-driven / risk arb |
| Typical horizon | Announce to close (weeks to months). Deal-break is the left tail. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Capture the spread between the target’s market price and the deal consideration, bearing completion risk. Size off break probability and estimated break return, not off the gross spread. Unannounced rumours are not deals.

You are betting that the market’s implied $\pi_{\mathrm{break}}$ is too high (or that you are paid enough to warehouse completion risk), not that $V_{\mathrm{close}}-P_A$ is a risk-free arb. You are selling insurance on completion. The left tail is the deal break: target down, and in stock deals acquirer often up.

You are not trading unannounced rumours, not running an unhedged long-target stock deal, and not treating a collar as a fixed $\rho$. Typical user: an event-driven desk with a deal database, public S-4/proxy terms, and a warehouse limit on $\pi_{\mathrm{break}}$. Horizon intuition: announce to close, weeks to months. IRR versus calendar time matters; a $3$ spread over two years is not the same as $3$ over two months.

If you size up because the spread is wide, skip the acquirer short, or enter before the announcement is public, the backtest is not merger arb as specified here.

## 2. First principles

After a deal is announced, the target’s price $P_A$ sits below the value of the consideration if the market assigns a nonzero chance the deal breaks. Let $\pi_{\mathrm{break}}$ be that probability, $V_{\mathrm{close}}$ the consideration if the deal closes, and $V_{\mathrm{break}}$ the target’s expected price if it breaks. Then

$$
P_A \approx (1-\pi_{\mathrm{break}})\, V_{\mathrm{close}} + \pi_{\mathrm{break}}\, V_{\mathrm{break}}
$$

This is a blended value, not an identity you can invert for a free lunch. Rearranged, a wide $V_{\mathrm{close}}-P_A$ can mean high $\pi_{\mathrm{break}}$ or a low $V_{\mathrm{break}}$, not “cheap arb.” You do not observe $\pi_{\mathrm{break}}$; you size off an estimate of it and of the break return. Using this equation as if $P_A$ *must* converge to $V_{\mathrm{close}}$ skips the insurance you are selling.

The gross spread if you buy the target and the deal **closes** is $V_{\mathrm{close}}-P_A$. That number is the **best-case** close P&L before costs and financing. It is not a risk-free arb. You are selling insurance on completion.

Two consideration types:

- **Cash.** $V_{\mathrm{close}}=C$, a cash amount per target share. Book: long 1 share of target A. No acquirer leg.
- **Stock.** $V_{\mathrm{close}}=\rho P_B$ at the ratio (plus any collar). Book: long 1 A, short $\rho$ B.

Cash has no $B$ hedge; you still have financing and gap risk. Stock without the $B$ short is a directional acquirer bet, not the deal. Mixes add the cash piece plus the stock piece. Collars make $V_{\mathrm{close}}$ option-like; a fixed-$\rho$ hedge is then wrong.

That is the whole strategy. Everything below is the two P&L identities, the example numbers, and how not to treat rumours as deals.

### Worked intuition

The file’s stock-deal numbers: $P_A=67$, $P_B=35$, the deal exchanges 1 A for 2 B so $\rho=2$. Gross credit if it closes: $2\times 35-67=3$ per A share. You are long 1 A and short 2 B. If the deal closes at the ratio, that $3$ is the close-case P&L before costs and borrow. If the deal breaks, A might gap to 55 and B to 38: you lose on both legs. Do not treat $3$ as risk-free, and do not scale the book up *because* $3$ looks wide — a wide spread can mean a high break probability. A rumour with no announcement timestamp is refused, not sized.

## 3. Notation

| Symbol | Definition |
|---|---|
| $A$ | target |
| $B$ | acquirer |
| $P_A,\,P_B$ | last prices |
| $C$ | cash consideration per target share (cash deals) |
| $\rho$ | acquirer shares per target share (stock deals) |
| $t_\ast$ | fill time after announcement |
| $\pi_{\mathrm{break}}$ | probability the deal does not close |
| $V_{\mathrm{close}}$ | consideration if close |
| $V_{\mathrm{break}}$ | target value if break |
| $Q_A,\,Q_B$ | signed share holdings |

## 4. Mathematics

### 4.1 Cash merger

Deal cash $C$. Long 1 share of $A$. If the deal closes, terminal P&L per share (before financing) is

$$
C - P_A(t_\ast)
$$

Best-case close P&L: cash minus what you paid for the target. $t_\ast$ is after the announcement is public. Financing between $t_\ast$ and close is a cost, not in this identity. There is no $B$ leg. If you mark this as locked arb, you skipped $\pi_{\mathrm{break}}$.

If the deal breaks, terminal P&L per share is

$$
P_A(\mathrm{break}) - P_A(t_\ast)
$$

usually a loss. There is no $B$ leg. $P_A(\mathrm{break})$ is often closer to the pre-deal price, sometimes worse. Size off this gap times $\pi_{\mathrm{break}}$, not off $C-P_A$. Report IRR versus calendar time so a slow cash deal is not compared as a raw percent to a two-week close.

### 4.2 Stock merger

Exchange ratio $\rho$ (acquirer shares per target share). Long 1 $A$, short $\rho$ $B$. The initial credit per target share is

$$
\rho P_B - P_A
$$

Same object as $V_{\mathrm{close}}-P_A$ when $V_{\mathrm{close}}=\rho P_B$. This is the close-case credit, not expected P&L. If $B$ rallies after you fail to short it, you do not earn this credit; you have a long-A directional book. Hard-to-borrow $B$ → refuse or shrink, do not skip the hedge.

If the deal closes, the two legs converge at the ratio (plus any collar) and that credit is earned as the spread goes to zero. If it breaks, both legs jump — typically $A$ down, $B$ up — and spread losses are large.

Worked identity with the file’s example numbers: $P_A=67$, $P_B=35$, deal exchanges 1 $A$ for 2 $B$ so $\rho=2$. Gross credit if the deal closes:

$$
2\times 35 - 67 = 3
$$

per $A$ share. Do not treat the $3$ as risk-free; it is best-case close P&L before costs. This arithmetic is the acceptance-test fixture. Scaling the book with $I$ multiplies $3$; it does not make $3$ safer. Collar terms would replace $2\times 35$ with an option-like $V_{\mathrm{close}}$.

Do not treat the $3$ as risk-free; it is best-case close P&L before costs.

Stock-deal hedge identity: dollars short in $B$ equal $\rho P_B$ per target share.

$$
Q_A = +1, \qquad Q_B = -\rho
$$

(per one target share; scale by the position size). Collars: optionality belongs in $V_{\mathrm{close}}$; a fixed-$\rho$ hedge is wrong inside a collar.

Plus one target, short $\rho$ acquirer. Dollar short in $B$ is $\rho P_B$ per target share — that is the hedge identity the tests check. If $\rho$ changes in the documents, update $Q_B$ the same day. A cash deal must not emit a $B$ leg.

### 4.3 Sizing and P&L

Size off $\pi_{\mathrm{break}}$ and the estimated break return, not off the gross spread. A wide spread can mean a high break probability, not a free lunch.

Report IRR versus calendar time, not just percent of price. Spread capture if close; gap if break.

If you do X = rank deals by $V_{\mathrm{close}}-P_A$ and put the most capital in the widest, you overweight the most broken-looking deals and the backtest lies about a “high spread” edge. Financing rate belongs in cash-deal P&L; borrow on $B$ belongs in stock-deal P&L.

## 5. Step-by-step algorithm

1. **Deal object.** From public announcement text and S-4/proxy: consideration type (cash / stock / mix), $\rho$, collars, go-shop, MAC, regulatory. Refuse unannounced rumours. This step exists so the book is a documented deal, not a headline. No insider information.
2. **Hedge.** Cash: `{A: +1}`. Stock: `{A: +1, B: -rho}`. Mixed: cash piece plus stock piece. Apply collars if present. The hedge *is* the strategy on stock deals; skipping $B$ is directional.
3. **Spread.** Compute $V_{\mathrm{close}}-P_A$ (cash: $C-P_A$; stock: $\rho P_B-P_A$). This is the close-case credit, not a forecast of P&L. Reporting it as expected return skips $\pi_{\mathrm{break}}$.
4. **Size.** Cap gross per deal. Skip or shrink if $\pi_{\mathrm{break}}$ exceeds the warehouse limit. Do not scale up because the spread is wide. Warehouse limits exist so one antitrust blow-up cannot sink the book.
5. **Borrow.** Stock deals need borrow on $B$. If $B$ is hard-to-borrow, refuse or shrink; do not run an unhedged long-$A$ stock deal. Missing borrow is a hard fail, not a warning.
6. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Both legs of a stock deal together, or neither.
7. **Monitor.** Deal status until close or break. Flatten on break. Corporate actions: adjust $\rho$ if the ratio changes in the documents. Status jumps; a gentle spread widen is not the only path to broken.
8. **Horizon.** Announce to close (weeks to months). Filling before the announcement timestamp is not this spec.

## 6. Execution protocol

- Hard-to-borrow acquirer in stock deals. Cash deals still have financing and gap risk. If you do X = assume $B$ is always borrowable at 50 bp, the stock-deal backtest lies.
- Collars: optionality belongs in the model. If you do X = hedge a collar with fixed $\rho$, the hedge is wrong when the ratio steps.
- Delay: trade only after the announcement is public. No insider information. If you do X = fill on the rumour print the day before the 8-K, the backtest lies and the spec is refused.
- Default fill: next available auction or delay-1 close after the terms are in the deal object. If you do X = fill at the halt print, you are assuming a fill that may not have existed.

## 7. Data contract

Required, point-in-time, **public**:

- Announcement text and timestamps
- S-4 / proxy terms: cash $C$, ratio $\rho$, collars, conditions
- Deal status (pending / closed / broken)
- Split-adjusted prices for $A$ and (if stock) $B$
- Borrow availability and fees on $B$ for stock deals
- Financing rate for the cash book

No insider information. Not used by this spec: SUE, book-to-price as a sort key, industry residual, option IV (unless a collar is marked as options, which is a documented extension).

Delisted names: if $A$ delists because the deal closed, that is close P&L, not a survivorship hole.

If you do X = treat a delist-on-close as a missing return, the backtest lies by dropping successful closes. If you do X = use a rumour timestamp as `announce`, refuse failed. If you do X = take $\rho$ from a later amended S-4 at the original announce date, terms look ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| max $\pi_{\mathrm{break}}$ | caller-set | warehouse limit |
| gross per deal | caller-set | |
| hedge ratio | $\rho$ from documents | cash deals: no $B$ |
| rumour policy | refuse | not a deal |
| delay | after public announce | |

## 9. Agent implementation contract

Build a Python module `strategies.merger_arbitrage` with:

1. `position(deal) -> {A: +1}` for cash, `{A: +1, B: -rho}` for stock — terms from the deal object only.
2. `spread(deal, prices) -> float` — $C-P_A$ or $\rho P_B-P_A$.
3. `blotter(position, prices, size, lot) -> list[OrderIntent]` — never live routing.
4. `pnl_close` / `pnl_break` matching §4.

Refuse unannounced rumours as if they were deals. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Deal break.** The left tail. This is insurance-selling on completion. If you do X = drop broken deals from the historical sample, the backtest lies by keeping only closes.
- **Collars and MAC.** $V_{\mathrm{close}}$ is not a fixed number. If you do X = ignore MAC language, status can jump to broken without a gentle spread widen and the model never saw it.
- **Financing fails / antitrust.** Status can jump to broken without a gentle spread widen. If you do X = assume every pending deal glides to $C$, the backtest lies.
- **Unhedged stock deal.** Missing the $B$ short is a directional acquirer bet. If you do X = skip $B$ when borrow fails, the backtest lies about merger arb P&L.

## 11. Acceptance tests

- Stock-deal identity: dollars short in $B$ equal $\rho P_B$ per target share.
- Cash deal has no $B$ leg.
- Example fixture: $P_A=67$, $P_B=35$, $\rho=2$ → credit $3$ per $A$ share.
- Rumour with no announcement timestamp → refuse. If a rumour emits a blotter, the test must fail — that backtest would lie about a deal.
- Adding linear costs $\tau$ weakly decreases close-case P&L. If adding $\tau$ increases close P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
