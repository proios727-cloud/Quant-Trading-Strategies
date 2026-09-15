---
rank: 96
slug: tips-treasury-arbitrage
title: "TIPS–Treasury Arbitrage"
asset_class: "inflation / government bonds"
style: "synthetic nominal vs cash Treasury"
horizon: "Hold while $C(0)>0$ after costs; typically months"
instruments: "Treasury, matching-maturity TIPS, zero-coupon inflation swaps, STRIPS"
---

# 096. TIPS–Treasury Arbitrage

| Field | Value |
|---|---|
| Popularity rank (this kit) | 96 of 101 |
| Why it sits here | Empirically Treasuries often rich vs a TIPS + inflation-swap + STRIPS replicating portfolio. A well-known real-vs-nominal basis. |
| Aliases | TIPS–Treasury basis, real-vs-nominal arb, breakeven basis |
| Asset class | inflation / government bonds |
| Style | synthetic nominal vs cash Treasury |
| Typical horizon | Hold while $C(0)>0$ after costs; typically months |
| Instruments | Treasury, matching-maturity TIPS, zero-coupon inflation swaps, STRIPS |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A nominal Treasury is a fixed cash-flow stream. TIPS plus zero-coupon inflation swaps can be wired to **replicate** that stream: the indexation on the TIPS coupons is swapped into a known fixed amount, and a thin strip of STRIPS finishes the match. Empirically the cash Treasury often trades rich versus that replicating portfolio. Short the expensive nominal, buy the synthetic, and hold while time-0 cash $C(0)$ stays positive after costs and repo.

You are betting the cash Treasury is rich versus a matched TIPS + inflation-swap + STRIPS package. You are not taking a directional inflation view: the index ratio is designed to cancel. You are not taking a real-rate view as a standalone TIPS trade. You are not claiming a textbook free lunch: inflation-swap liquidity, TIPS specialness, and financing can eat $C(0)$ and still leave gap risk on unwind.

The hold is typically months, not to maturity, because the basis can close (or widen) as liquidity and specials move. Trade only if $C(0)$ clears a hurdle that includes bid/ask on all four legs, repo, and haircuts. A screen that shows $C(0)>0$ on mid marks with no costs is a necessary filter, not a locked-in profit.

Matching “the 10y Treasury” to “the 10y TIPS” on rounded maturity is not the same as matching coupon dates. A one-month maturity gap leaves a residual nominal duration the STRIPS schedule was not built to cancel. If ZCIS tenors do not exist on every $t_i$, you either interpolate with a documented curve dated $\le t-\varepsilon$ or you skip; inventing a $K$ from the TIPS–Treasury breakeven reimports the basis you are trying to trade.

## 2. First principles

Match maturity $T$. A TIPS with real coupon $r$ pays, at each coupon date $t_i$, an inflation-indexed amount. Per $\$1$ of TIPS principal the indexed notional on that date is the coupon plus the Kronecker principal at maturity:

$$
N_i = r + \delta_{t_i,T}
$$

On a regular coupon date the indexed notional is just the real coupon $r$. At maturity the Kronecker term adds the real principal $1$, so that date’s indexed notional is $r+1$. Coupon calendars must match the TIPS confirmation; inventing a date that is not a payment date creates a ghost $N_i$. Scale $N_i$ by the trade’s TIPS face after the per-dollar identity is written.

The TIPS cash flow is that notional times the index ratio:

$$
C_{\mathrm{TIPS}}(t_i) = N_i\, I(t_i)/I(0)
$$

$I(t_i)/I(0)$ is the TIPS index ratio with the contractual lag, not headline CPI on the coupon date. $I(0)$ is the base reference on the TIPS. A later CPI revision must not rewrite a historical $C_{\mathrm{TIPS}}$ unless you are explicitly using a final-vintage research series and have documented that choice. Live books use the first-release vintage that was public under the lag.

Enter matching zero-coupon inflation swaps with fixed rate $K$ on the same dates and notionals. The swap cash flow that **receives fixed and pays inflation** is

$$
C_{\mathrm{swap}}(t_i) = N_i\bigl[(1+K)^{t_i} - I(t_i)/I(0)\bigr]
$$

This is short inflation on notional $N_i$: you receive the compounded breakeven and pay the same index ratio the TIPS pays you. $K$ is the quoted ZCIS rate for that tenor at $t-\varepsilon$, so a par swap has zero PV at inception. Using a TIPS–Treasury breakeven as $K$ leaves a basis inside the “replicating” package.

Add the two legs. The index ratio cancels:

$$
C_{\mathrm{total}}(t_i) = N_i(1+K)^{t_i}
$$

What remains is a deterministic amount that does not depend on any future CPI print. That is the point of the overlay: inflation risk is swapped out date by date. If the swap lag and the TIPS lag differ, the cancellation is incomplete and $C_{\mathrm{total}}$ is not this identity. If notionals are not matched, a stub index exposure remains.

The synthetic coupon is now deterministic. Write it as an effective coupon on the original real rate:

$$
r_{\mathrm{eff}}(t_i) = r(1+K)^{t_i}
$$

This is the coupon piece of $C_{\mathrm{total}}$ when $N_i$ is just $r$ (off-maturity dates). At maturity the principal piece $(1+K)^{T}$ appears as well through $\delta_{t_i,T}$. $r_{\mathrm{eff}}$ is not the Treasury coupon; it is what the TIPS-plus-swap package actually pays, in nominal dollars, once inflation is swapped out.

A coupon Treasury pays $r_{\mathrm{Treasury}}$ plus principal $1$ at $T$. The remaining hole at each $t_i$ is filled with STRIPS of present value

$$
S(t_i) = D(t_i)\Bigl[r_{\mathrm{Treasury}}-r_{\mathrm{eff}}(t_i)+\delta_{t_i,T}\bigl(1-(1+K)^{t_i}\bigr)\Bigr]
$$

$D(t_i)$ is the discount to $t_i$. Positive $S(t_i)$ is cash you pay today to buy STRIPS that fill a shortfall versus the Treasury’s coupon and principal. Negative $S(t_i)$ is a STRIPS short (cash in today). The discount curve is dated $\le t-\varepsilon$; using a later STRIPS print to compute $S$ and an earlier Treasury print to compute $C(0)$ is look-ahead.

Time-0 cash from **short the Treasury, long the TIPS, par inflation swaps (zero PV), and the STRIPS** is

$$
C(0) = P_{\mathrm{Treasury}} - P_{\mathrm{TIPS}} - \sum_i S(t_i)
$$

You receive the Treasury dirty price, pay the TIPS dirty price, and pay (or receive) the STRIPS package. Par swaps contribute zero PV at inception if $K$ is the market ZCIS rate for each tenor. Empirically $C(0)$ is often $>0$: the cash Treasury is rich. Trade only if $C(0)$ exceeds costs and repo. Unwind if the basis closes.

That is the whole strategy. Everything below is how to match dates, how to sign the legs, and how not to look ahead on CPI.

## 3. Notation

| Symbol | Definition |
|---|---|
| $T$ | matched maturity |
| $t_i$ | coupon dates on the TIPS/Treasury |
| $r$ | TIPS real coupon |
| $r_{\mathrm{Treasury}}$ | nominal Treasury coupon |
| $N_i = r + \delta_{t_i,T}$ | indexed notional at $t_i$ per $\$1$ TIPS principal |
| $I(t)$ | CPI index with the TIPS lag |
| $K$ | ZCIS fixed rate for the matching swap |
| $C_{\mathrm{TIPS}}(t_i)$ | TIPS cash flow |
| $C_{\mathrm{swap}}(t_i)$ | inflation-swap cash flow (receive fixed) |
| $C_{\mathrm{total}}(t_i)$ | combined deterministic flow |
| $r_{\mathrm{eff}}(t_i)$ | $r(1+K)^{t_i}$ |
| $D(t_i)$ | discount factor to $t_i$ |
| $S(t_i)$ | STRIPS present value that finishes the match |
| $C(0)$ | time-0 cash of the packaged trade |
| $P_{\mathrm{Treasury}}, P_{\mathrm{TIPS}}$ | dirty prices |

## 4. Mathematics

### 4.1 Indexed TIPS flows

Per $\$1$ TIPS principal the indexed notional at $t_i$ is

$$
N_i = r + \delta_{t_i,T}
$$

Off-maturity, $\delta_{t_i,T}=0$ so $N_i=r$. At maturity the principal is included. Frequency is as on the bonds (default semiannual); do not annualize $r$ here.

The TIPS cash flow is that notional times the index ratio:

$$
C_{\mathrm{TIPS}}(t_i) = N_i\, I(t_i)/I(0)
$$

Use the TIPS index lag, not the headline CPI print date. First-release vintage for live; a later revision must not change a historical blotter unless the file is amended to a final-vintage research mode.

### 4.2 Inflation-swap overlay

Matching ZC inflation swaps with fixed $K$:

$$
C_{\mathrm{swap}}(t_i) = N_i\bigl[(1+K)^{t_i} - I(t_i)/I(0)\bigr]
$$

Receive-fixed / pay-floating on notional $N_i$ (short inflation). Combined with long TIPS:

$$
C_{\mathrm{total}}(t_i) = N_i(1+K)^{t_i}
$$

The inflation ratio has cancelled. Par swaps contribute zero to $C(0)$ at inception if $K$ is the market ZCIS rate for each tenor. If you cannot trade the matching ZCIS tenors, the residual index risk is not this package.

### 4.3 Effective coupon and STRIPS

The synthetic coupon on the original real rate is

$$
r_{\mathrm{eff}}(t_i) = r(1+K)^{t_i}
$$

STRIPS close the gap to the Treasury’s coupon and principal:

$$
S(t_i) = D(t_i)\Bigl[r_{\mathrm{Treasury}}-r_{\mathrm{eff}}(t_i)+\delta_{t_i,T}\bigl(1-(1+K)^{t_i}\bigr)\Bigr]
$$

Positive $S(t_i)$ is a STRIPS **purchase** (cash out at $t=0$). Negative $S(t_i)$ is a STRIPS short. $D(t_i)$ comes from STRIPS prices or a Treasury discount curve dated $\le t-\varepsilon$. Specials on individual STRIPS can make the screen $S$ untradeable at that size.

### 4.4 Time-0 cash and the trade

Time-0 cash of the packaged trade is

$$
C(0) = P_{\mathrm{Treasury}} - P_{\mathrm{TIPS}} - \sum_i S(t_i)
$$

Signs: short Treasury (receive $P_{\mathrm{Treasury}}$), long TIPS (pay $P_{\mathrm{TIPS}}$), short inflation via the receive-fixed swaps, plus STRIPS $S(t_i)$. Trade only if $C(0)$ exceeds transaction costs and repo. Positive textbook $C(0)$ is not a riskless print.

Holding-period P&L is the mark of all four legs minus financing:

$$
\mathrm{P\&L} = -\Delta P_{\mathrm{Treasury}} + \Delta P_{\mathrm{TIPS}} + \Delta\mathrm{PV}_{\mathrm{swap}} + \sum_i \Delta S(t_i) + \mathrm{coupons} - \mathrm{repo} - \mathrm{costs}
$$

The Treasury mark enters with a minus because you are short. Swap PV starts at zero on par ZCIS and then moves with $K$ and with realized fixings. Repo includes specials and haircuts on both the short Treasury and the long TIPS. Unwind costs on the swap leg can exceed the original $C(0)$.

## 5. Step-by-step algorithm

1. **Match.** Pick a nominal Treasury and a TIPS with the same maturity $T$ (or the closest pair). Align coupon calendars; do not mix CPI indexes. This step exists so the replicating package is aiming at one cash-flow schedule, not two adjacent bonds.
2. **Fix $K$.** Read ZCIS rates for each $t_i$ at $t-\varepsilon$. Use the TIPS lag convention for $I(0)$. This step exists so $K$ and the index base are market data, not a breakeven inferred from yields.
3. **Build $N_i$.** $N_i = r + \delta_{t_i,T}$ per $\$1$ TIPS. Scale to the trade notional. This step exists so swap notionals match TIPS indexation, including principal at $T$.
4. **Swaps.** For each $t_i$, enter receive-fixed ZCIS on notional $N_i$ so $C_{\mathrm{total}}(t_i) = N_i(1+K)^{t_i}$. This step exists to cancel the index ratio; skipping a tenor leaves inflation risk.
5. **STRIPS.** Compute $S(t_i)$ from the discount curve at $t-\varepsilon$. Buy or short those STRIPS. This step exists to finish the coupon and principal match versus the cash Treasury.
6. **Cash test.** Compute $C(0)$. If $C(0)$ does not exceed costs and repo, skip. This step exists so a mid-market curiosity does not become a trade that loses on haircuts.
7. **Blotter.** Short Treasury, long TIPS, swaps, STRIPS. Lot residuals to a cash bucket. Do not route live orders. This step exists to keep the research contract off the venue.
8. **Hold.** Hold while $C(0)>0$ after costs, typically months. Unwind if the basis closes or on CPI-print risk events that breach limits. This step exists because $C(0)$ is a filter, not a clock to maturity.

## 6. Execution protocol

- Trade only if $C(0)$ exceeds costs and repo. Unwind if the basis closes or on CPI-print risk events.
- Freeze CPI vintages: first-release for live; never a later revision on a historical date.
- Repo the short Treasury; haircut and specialness are first-order. TIPS can go special too.
- Default fill: next snapshot after $C(0)$ is computed from $t-\varepsilon$ marks. Delay-0 using the fill prints inside $C(0)$ is research-only.

## 7. Data contract

Required, point-in-time, timestamped $\le t-\varepsilon$:

- Dirty/clean prices and coupons for the Treasury and the matching TIPS
- TIPS reference CPI series with the contractual lag and revision vintage
- Zero-coupon inflation-swap curve $K(t_i)$
- STRIPS prices or a Treasury discount curve $D(t_i)$
- Repo rates and haircuts on Treasury and TIPS
- Coupon frequency (default semiannual)

Look-ahead that invalidates a historical blotter: a later CPI revision, a ZCIS rate printed after $t-\varepsilon$, a STRIPS curve from the next session, or matching a TIPS to a Treasury with a different CPI index (for example mixing CPI-U and a seasonally adjusted research series). Specials must be the repo actually available, not a GC average.

Not used by this spec: equities, convertibles.

No restatement peeking on CPI. Delist or called bonds: flatten the package.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| coupon frequency | semiannual | as on the bonds |
| CPI lag | as on TIPS | do not invent a lag |
| $K$ | quoted ZCIS | par swaps at inception |
| entry | $C(0)$ after costs and repo | skip otherwise |
| hold | while $C(0)>0$ after costs | typically months |
| delay | 1 snapshot | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.tips_treasury_arbitrage` with:

1. `indexed_flows(r, dates, T, I, I0) -> pd.Series` — $C_{\mathrm{TIPS}}(t_i)$, no look-ahead on $I$.
2. `swap_flows(N, K, dates, I, I0) -> pd.Series` — $C_{\mathrm{swap}}(t_i)$.
3. `strips(r_treas, r_eff, D, dates, T, K) -> pd.Series` — $S(t_i)$.
4. `cash0(P_treas, P_tips, S) -> float` — $C(0)$.
5. `blotter(C0, prices, notionals, costs, repo) -> list[OrderIntent]` — four legs if $C(0)$ clears the hurdle; never live routing.
6. `pnl(dP_treas, dP_tips, dPV_swap, dS, coupons, repo, costs) -> float` — matches the P&L identity above.

Include transaction costs and repo. Positive textbook $C(0)$ is not a riskless print. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Inflation-swap liquidity.** Unwinding $C_{\mathrm{swap}}$ can cost more than $C(0)$.
- **TIPS specialness and financing.** Repo and haircuts flip the sign of net cash.
- **CPI revisions.** The TIPS index is lagged and can revise; the swap may not match one-for-one.
- **Not textbook-arb after costs.** $C(0)>0$ on a screen is a necessary filter, not a locked-in profit.

## 11. Acceptance tests

- Index cancellation: $C_{\mathrm{TIPS}}(t_i) + C_{\mathrm{swap}}(t_i) = N_i(1+K)^{t_i}$ to $10^{-8}$ for any $I(t_i)$.
- Kronecker: at $t_i \neq T$, $\delta_{t_i,T} = 0$ so $N_i = r$.
- Identical prices and zero STRIPS: $P_{\mathrm{Treasury}} = P_{\mathrm{TIPS}}$ and $S\equiv 0$ $\Rightarrow$ $C(0) = 0$.
- Permuting CPI after $t-\varepsilon$ must not change the $t-\varepsilon$ blotter.
- Adding linear costs $\tau$ weakly decreases P&L; if $C(0)$ falls through the hurdle, no trade.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
