---
rank: 95
slug: inflation-swaps
title: "Inflation Hedging with Inflation Swaps"
asset_class: "inflation"
style: "swap / breakeven vs realized CPI"
horizon: "Swap tenor $T$ (years)"
instruments: "zero-coupon or year-on-year inflation swaps"
---

# 095. Inflation Hedging with Inflation Swaps

| Field | Value |
|---|---|
| Popularity rank (this kit) | 95 of 101 |
| Why it sits here | Standard inflation overlay: receive floating CPI vs pay a fixed breakeven (TIPS–Treasury style). |
| Aliases | ZCIS overlay, YYIIS, breakeven inflation swap |
| Asset class | inflation |
| Style | swap / breakeven vs realized CPI |
| Typical horizon | Swap tenor $T$ (years) |
| Instruments | zero-coupon or year-on-year inflation swaps |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

The buyer of an inflation swap is long inflation: receive floating CPI, pay a fixed rate $K$. That $K$ is the breakeven, typically close to the T-note minus TIPS yield of matching maturity, up to a basis. Choose a zero-coupon contract (one net flow at $T$) or a year-on-year contract (annual flows) to match the liability you are overlaying, or to match a directional view on the path versus a single terminal print.

You are swapping a known fixed inflation path for the realized index path. The trade is a hedge or a directional view on realized CPI versus $K$. You are not taking a real-rate view: duration and real yields live in TIPS and nominals, not in a pure inflation swap. You are not trading the headline CPI surprise on release morning unless the contract’s lag and reference month say that print is the fixing — usually they do not.

$K$ is read from the swap market at $t-\varepsilon$, not inferred from a TIPS–Treasury breakeven and treated as the same object. The TIPS–Treasury gap omits swap liquidity, seasonality, and lag, and it mixes in real-rate and specials effects. If you substitute TIPS for the swap, you have a different book (see the TIPS–Treasury spec). Collateral, CSA, and the fixing calendar are part of sizing, not footnotes.

## 2. First principles

Let $I(t)$ be the inflation index (CPI-U or the contract index) with the swap’s lag convention. A **zero-coupon inflation swap** (ZCIS) of tenor $T$ has a single net settlement at $T$. Per $\$1$ notional the fixed leg is the compounded breakeven:

$$
C_{\mathrm{fixed}} = (1+K)^T - 1
$$

This is the terminal growth implied by compounding $K$ for $T$ years, minus the original unit of notional. It does not depend on any CPI print. $K$ is an annually compounded rate in the usual US quotation; if the listed contract uses a different compounding, document it and do not reuse this identity. $T$ is the contract tenor in years on the swap’s day-count, not calendar years guessed from the trade date.

The floating leg is the realized index growth from the base fixing $I(0)$ to the final fixing $I(T)$:

$$
C_{\mathrm{floating}} = I(T)/I(0) - 1
$$

$I(0)$ is the base index on the contract, already lagged. $I(T)$ is the final fixing, also lagged. Neither is the headline CPI number released that morning unless the confirmation says so. A later revision of CPI-U does not change a fixing that used the first-release vintage unless the contract says it does — most research books must freeze the vintage that was public at the fixing.

The buyer (long inflation) receives floating and pays fixed. Terminal P&L per $\$1$ is therefore

$$
\mathrm{P\&L}_{\mathrm{ZC}} = C_{\mathrm{floating}} - C_{\mathrm{fixed}} = \frac{I(T)}{I(0)} - (1+K)^T
$$

If realized growth beats the compounded breakeven, the buyer is paid. If it falls short, the buyer pays. At fair $K$ the swap’s time-0 value is zero: $K$ is the rate that equates the two legs under the swap’s discounting. That is the same object as a TIPS–Treasury breakeven, up to a basis (liquidity, seasonality, lag). Mark-to-market before $T$ uses the current ZCIS curve for residual tenor, not a guessed $I(T)$ that has not been published.

A **year-on-year inflation swap** (YoY) pays every anniversary $t = 1,\ldots,T$. The fixed coupon that year is just $K$:

$$
C_{\mathrm{fixed}}(t) = K
$$

There is no compounding inside the YoY coupon. Each year you pay (or receive) the same fixed rate $K$ against that year’s index growth. Mixing $(1+K)^T$ into a YoY coupon is a specification bug. Seasonality in CPI therefore shows up year by year, not only at $T$.

The floating coupon that year is the one-year index growth:

$$
C_{\mathrm{floating}}(t) = I(t)/I(t-1) - 1
$$

$I(t)$ and $I(t-1)$ are consecutive annual fixings under the same lag. A missing fixing is not filled with headline CPI. The ratio is simple growth, not a log, matching how the listed coupon is written.

Buyer P&L in year $t$ is again floating minus fixed (long inflation):

$$
\mathrm{P\&L}_{\mathrm{YoY}}(t) = \frac{I(t)}{I(t-1)} - 1 - K
$$

A year of zero index growth pays $-K$ per dollar to the buyer (they pay fixed, receive nothing). A year that prints $K$ exactly pays zero on that coupon. Discount each coupon to the report currency on the swap curve; summing undiscounted coupons is not the book’s P&L.

That is the whole strategy. Everything below is how to pick ZC vs YoY, how to read $K$, and how not to look ahead on the index.

## 3. Notation

| Symbol | Definition |
|---|---|
| $T$ | swap tenor in years |
| $K$ | fixed breakeven rate (quoted) |
| $I(t)$ | inflation index at the fixing dated $t$, lag as on the contract |
| $I(0)$ | base index for the ZCIS |
| $C_{\mathrm{fixed}}$ | ZCIS fixed flow per $\$1$ |
| $C_{\mathrm{floating}}$ | ZCIS floating flow per $\$1$ |
| $C_{\mathrm{fixed}}(t)$ | YoY fixed coupon at anniversary $t$ |
| $C_{\mathrm{floating}}(t)$ | YoY floating coupon at anniversary $t$ |
| $N$ | swap notional (positive = buy inflation / receive floating) |

## 4. Mathematics

### 4.1 Zero-coupon (one flow at $T$)

Per $\$1$ notional the fixed terminal flow is

$$
C_{\mathrm{fixed}} = (1+K)^T - 1
$$

This cash amount is known at inception once $K$ is fixed. It is the hurdle the floating index must beat. Changing $K$ after the trade is an unwind at a new swap rate, not a rewrite of this identity.

The floating terminal flow is realized index growth:

$$
C_{\mathrm{floating}} = I(T)/I(0) - 1
$$

$I(T)$ is unknown until the lagged fixing is public. Using a nowcast or a later revision in a historical blotter is look-ahead. $I(0)$ is locked on the trade’s base date; do not rebase it when CPI is restated.

Net to the buyer:

$$
\mathrm{P\&L}_{\mathrm{ZC}} = N\left(\frac{I(T)}{I(0)} - (1+K)^T\right)
$$

$N>0$ is long inflation. Mark-to-market before $T$ uses the current ZCIS curve for residual tenor, not the still-unreleased $I(T)$. Collateral on that mark is part of holding-period P&L in §4.4, not an optional extra.

### 4.2 Year-on-year (annual payments)

For $t = 1,\ldots,T$ the fixed coupon that year is just $K$:

$$
C_{\mathrm{fixed}}(t) = K
$$

The floating coupon that year is one-year index growth:

$$
C_{\mathrm{floating}}(t) = I(t)/I(t-1) - 1
$$

Buyer P&L is floating minus fixed on each payment date, discounted to the report currency. $K$ is **not** compounded inside the YoY coupon; compounding lives only in the ZCIS identity $(1+K)^T$. YoY is the right overlay when the liability is a stream of annual inflation prints; ZCIS is the right overlay when the liability is one real cash flow at $T$.

### 4.3 Breakeven source

Default $K$ is the quoted swap rate. A research proxy is the matching-maturity T-note yield minus the TIPS real yield. That proxy is not the swap; it omits the TIPS–swap basis. Mixing the proxy into a live blotter while marking the position on the swap curve is two products at once.

### 4.4 Holding-period P&L

On a mark-to-market date, P&L is the change in swap PV minus collateral financing, plus any coupon that fixed on that date:

$$
\mathrm{P\&L} = N\,\Delta\mathrm{PV} + \mathrm{coupons} - \mathrm{collateral} - \mathrm{costs}
$$

$\Delta\mathrm{PV}$ comes from the quoted curve at the mark, using only fixings already public. Coupons are YoY (or the ZCIS terminal flow at $T$). Collateral is the CSA rate on variation margin, not a bond repo. Costs include bid/ask on entry and unwind.

## 5. Step-by-step algorithm

1. **Liability or view.** Choose ZC if the exposure is a single real cash flow at $T$. Choose YoY if the exposure is a stream of annual inflation prints. This step exists so the coupon schedule matches the thing you are hedging, not an adjacent product.
2. **Index.** Fix the index (CPI-U, HICP, etc.) and the lag convention of the listed or OTC contract. Do not mix indexes between $K$ and $I(t)$. This step exists because a US breakeven versus a European fixing is not a hedge.
3. **Quote.** Read $K$ from the swap market at $t-\varepsilon$. Do not use a revised CPI print that was not public at $t-\varepsilon$. This step exists to stop look-ahead on both the rate and the index vintage.
4. **Notional.** Set $N$ so that a 1-point miss of realized inflation versus $K$ matches the hedge budget (liability DV01 or directional risk limit). This step exists so “long inflation” has a dollar meaning.
5. **Collateral.** Treat the position as a swap: variation margin, not a cash bond. Haircut and CSA rules are part of sizing. This step exists because unfunded notionals still consume cash when marks move.
6. **Blotter.** Emit a swap intent (pay fixed $K$, receive floating, or the reverse). Do not route live orders. This step exists to keep the research contract off the venue.
7. **Hold.** Hold to tenor or unwind on the swap market. YoY coupons settle on each anniversary using the lagged index. This step exists so you do not mark a YoY coupon off a headline print that is not the fixing.

## 6. Execution protocol

- Enter as a hedge or a directional breakeven view. Collateralise as a swap.
- Use only index prints that are public under the contract lag. A headline CPI release does not update $I(t)$ until the swap’s reference month and lag say so.
- If using TIPS as a substitute, you have mixed in real-rate risk; that is a different book (see TIPS–Treasury).
- Delay-0 on an unreleased print is forbidden, including in a backtest that “knew” the print after the close.

## 7. Data contract

Required, point-in-time, timestamped $\le t-\varepsilon$:

- Quoted ZCIS and/or YoY inflation-swap rates $K$ by tenor
- Inflation index history $I(t)$ with the contract lag and revision policy (use the first-release vintage for live; document if you use final)
- Discount curve for swap PV
- CSA / collateral rate
- Trading calendar and fixing calendar

Look-ahead that invalidates a historical blotter: swapping in a later CPI revision, using a nowcast as $I(T)$, reading $K$ from a TIPS–Treasury breakeven and labelling it the swap, or applying a lag that is not on the confirmation. First-release versus final must be a documented vintage, not a silent mix.

Not used by this spec: equity prices, convertibles.

No restatement peeking: a later CPI revision must not change a historical blotter.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| contract | ZCIS or YoY | match the liability |
| tenor $T$ | caller-set | years |
| index | CPI-U (US) | or the listed contract index |
| lag | as on the swap | do not invent a lag |
| $K$ | quoted breakeven | TIPS–Treasury is a proxy only |
| delay | 1 fixing | delay-0 on an unreleased print is forbidden |

## 9. Agent implementation contract

Build a Python module `strategies.inflation_swaps` with:

1. `zc_payoff(I_T, I_0, K, T, N) -> float` — $N\bigl(I(T)/I(0) - (1+K)^T\bigr)$.
2. `yoy_coupon(I_t, I_prev, K, N) -> float` — $N\bigl(I(t)/I(t-1) - 1 - K\bigr)$.
3. `pv(K_market, K_fixed, T, curve, N, style) -> float` — mark-to-market of a ZCIS or YoY position.
4. `blotter(style, K, T, N) -> list[OrderIntent]` — swap intent only, never live routing.
5. `pnl(dPV, coupons, collateral, costs) -> float` — matches the P&L identity above.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Index revision and lag.** The swap does not pay headline CPI the morning of the print.
- **Liquidity and counterparty.** OTC inflation swaps gap; CSA terms matter.
- **Real-rate mix.** Substituting TIPS for the swap adds duration and real-rate risk.
- **Seasonality.** YoY coupons inherit CPI seasonality; ZCIS does not pay until $T$.

## 11. Acceptance tests

- ZCIS: $I(T)/I(0) = (1+K)^T$ $\Rightarrow$ payoff $0$ to $10^{-8}$.
- ZCIS: $I(T)/I(0) = (1+K)^T + x$ $\Rightarrow$ payoff $N x$.
- YoY: $I(t) = I(t-1)$ $\Rightarrow$ coupon $N(-K)$.
- Permuting index prints after $t-\varepsilon$ must not change the $t-\varepsilon$ blotter.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
