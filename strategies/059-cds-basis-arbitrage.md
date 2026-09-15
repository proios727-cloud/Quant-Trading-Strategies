---
rank: 59
slug: cds-basis-arbitrage
title: "CDS Basis Arbitrage"
asset_class: "fixed income"
style: "cash vs synthetic credit"
horizon: "Months; until basis normalises or default"
instruments: "cash bond + CDS on the same name"
---

# 059. CDS Basis Arbitrage

| Field | Value |
|---|---|
| Popularity rank (this kit) | 59 of 101 |
| Why it sits here | Buy cheap cash bonds vs CDS (negative basis). Classic credit RV; funding and haircuts matter. |
| Aliases | negative-basis trade, cash-CDS basis |
| Asset class | fixed income |
| Style | cash vs synthetic credit |
| Typical horizon | Months; until basis normalises or default |
| Instruments | cash bond + CDS on the same name |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A par credit bond plus buying CDS protection is a synthetic risk-free (plus funding and delivery optionality). The CDS spread should therefore line up with the bond’s yield spread to risk-free. When the bond is cheap versus CDS — negative basis — buy the bond and buy protection. Hold until the basis normalises, the bond is called, or a credit event.

This is not risk-free. Funding, haircuts, and cheapest-to-deliver must sit in the P&L engine. You are not ranking credits on a ratings residual (file 058) and you are not harvesting frozen-curve carry (file 057). You are trading the cash-versus-synthetic gap on one name.

Typical users are credit RV desks with repo lines and CDS depth. Horizon is months, until $B$ is back inside a cost band, a call, or a default. Positive-basis shorts of cash bonds are off unless borrow exists. Delay-1: both spreads known before the fill.

2008 is the teaching case: negative basis can widen while repo disappears. Treat that path as $L_{\max}$, not as a footnote.

## 2. First principles

Let $s_{\mathrm{bond}}$ be the bond’s spread to the risk-free curve (z-spread or ASW) and $s_{\mathrm{CDS}}$ the matching-maturity CDS par spread on the same name. The CDS basis is

$$
\text{CDS basis} = \text{CDS spread} - \text{bond spread}
$$

If the basis is zero and there is no CTD option, a financed long bond plus long protection earns about repo minus the risk-free, with default offset by the CDS. Sign: negative basis means the cash spread is wider than CDS, so the bond is cheap versus the swap. Mixing z-spread and par ASW without documenting which one is $s_{\mathrm{bond}}$ will invent a basis. **Negative basis** means $s_{\mathrm{CDS}}<s_{\mathrm{bond}}$: the cash bond is wide versus CDS, so the bond is cheap. Buy the bond and buy protection (insure the long). **Positive basis** unwind is selling the bond and selling protection, usually only if the bond is already owned; locating a short cash credit is often worse than the apparent basis.

Default, funding, and cheapest-to-deliver optionality must be in the P&L engine. That is the whole identity. Everything below is matching notional, the cost gate, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $s_{\mathrm{CDS}}$ | CDS par spread, matching tenor |
| $s_{\mathrm{bond}}$ | bond z-spread or par ASW |
| $B = s_{\mathrm{CDS}}-s_{\mathrm{bond}}$ | CDS basis |
| $c$ | round-trip costs plus expected funding and haircut, in spread units |
| $N$ | matched notional |
| $P_c$ | dirty price of the cash bond |
| $r_{\mathrm{repo}}$ | repo rate on the bond, including specials |
| $h$ | haircut |
| $T$ | matched maturity / CDS tenor |

## 4. Mathematics

### 4.1 Basis

Using stamps $\le t < t_{\mathrm{fill}}$:

$$
\text{CDS basis} = \text{CDS spread} - \text{bond spread}
$$

$B<0$ is negative basis. $c$ must include bid/ask on both legs, expected repo versus the risk-free, haircut drag, and a CTD haircut. A gate that only uses mid spreads will always look open. Sign rule:

- $B < -c$ — negative basis → **buy** the bond, **buy** CDS protection
- $B > +c$ — positive basis → only if the spec allows a short cash bond: **sell** the bond, **sell** protection; default this file to skip unless borrow exists
- $\lvert B\rvert \le c$ — flat

### 4.2 Package

Match notional $N$ and maturity as closely as possible. Account for CTD in the CDS: protection pays on a cheapest-to-deliver bond, which can be worse than the cash bond you hold. Dollar duration of the bond versus IR01 of the CDS is a second-order rates residual; a small rates overlay is allowed but is not the basis trade. Mismatched tenors (5y CDS versus a 8y cash bond) leave a curve residual you will mislabel as basis P&L.

### 4.3 Holding-period P&L

Bond price change plus coupon, minus repo on the financed long, plus CDS mark-to-market (spread change, running coupon, and contingent default payoff), minus costs:

$$
\mathrm{P\&L} = N\bigl(\Delta P_c + \mathrm{coupon} - r_{\mathrm{repo}}\Delta t\bigr) + \mathrm{CDS}_{\mathrm{MtM}} + \mathrm{default\ settlement} - \mathrm{costs}
$$

Haircut $h$ means you fund only $(1-h)P_c$ at repo and the rest at a worse rate. Report P&L, basis path, and a default flag. Sharpe on a book that never defaults is not an acceptance of the spec. If a credit event fires, settle CDS per the protocol; do not assume par recovery.

## 5. Step-by-step algorithm

1. **Pair.** Same issuer, seniority, and as-close tenor for the cash bond and the CDS. This step exists so a holding-company CDS versus an opco bond is not called basis.
2. **Spreads.** $s_{\mathrm{bond}}$ and $s_{\mathrm{CDS}}$ dated $\le t$. Document z-spread vs ASW. Mixing them across names invents $B$.
3. **Costs.** $c$ from bid/ask on both legs, expected repo, haircut, and a CTD haircut. If $c$ is set to 0, the gate is not this spec.
4. **Gate.** Enter only if $\lvert B\rvert$ exceeds $c$ with the sign in 4.1. Flat is the usual state. A more-negative print is not automatically “more alpha” without a funding check.
5. **Size.** Notional $N$ capped by issue size, CDS depth, and funding lines. Haircut $h$ raises cash usage; ignore it and the 2008 path will not fit $L_{\max}$.
6. **Blotter.** Buy bond + buy protection (negative basis). Emit intents. Do not route live orders. Positive-basis shorts only with documented borrow.
7. **Hold.** Until $B$ is inside a tighter exit band, a max-hold clock, a call, or a credit event. Do not add because $B$ widened; that is often a funding stress.
8. **Default.** If a credit event fires, settle CDS per the protocol and deliver or cash-settle; do not assume par. Unpublished determinations after $t$ do not change the $t$ gate.

## 6. Execution protocol

- Default fill: next close after both spreads are known. Delay-0 is research-only.
- Fund the bond in repo; haircut and repo spread are first-order.
- Hold until the basis mean-reverts. Do not treat a more-negative print as “more alpha” without a funding check.
- Positive-basis shorts of cash bonds only with documented borrow.

## 7. Data contract

Required, point-in-time:

- Clean/dirty bond prices, accrued, z-spread or ASW
- CDS par spreads, running coupon, convention, and CTD basket
- Repo, haircuts, and funding availability
- Credit-event calendar / ISDA determinations (for P&L, not for predicting default)

Not used by this spec: equity book value, earnings, SUE, ratings-regression value $V_i$ as the signal (058), frozen-curve carry $C$ as the signal (057).

No look-ahead on CDS spreads or on unpublished determinations. A restated CDS history that revises yesterday’s par spread does not change yesterday’s gate.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| entry | $\lvert B\rvert > c$ | $c$ = bid/ask + funding + CTD |
| exit | $\lvert B\rvert \le c/2$ | or credit event / call |
| positive basis | off | on only with borrow |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.cds_basis_arbitrage` with:

1. `basis(cds_spread, bond_spread) -> float` — $s_{\mathrm{CDS}}-s_{\mathrm{bond}}$.
2. `gate(B, c, borrow) -> str` — `{long_bond_long_cds, short_bond_short_cds, flat}`.
3. `package(N, bond, cds) -> dict` — matched notional, CTD flag.
4. `blotter(gate, package, lot) -> list[OrderIntent]` — cash + CDS intents, never live routing.
5. `pnl(bond_leg, cds_leg, repo, haircut, default_event, costs) -> float` — identity in 4.3, including default settlement.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Funding squeeze.** 2008-style: negative basis widens while repo disappears. Adding to a loser without a funding line is how the package blows up.
- **Cheapest-to-deliver.** CDS pays on a worse bond than the one you own. A toy default that assumes CTD equals the held bond overstates the hedge.
- **Counterparty.** Protection is only as good as the dealer/CCP. Uncleared bilateral CDS is not the same as cleared.
- **Pull-to-par vs default.** A surviving rich bond and a defaulting cheap bond are different P&L paths. Sharpe on a no-default subsample is not an acceptance.
- **Tenor mismatch.** 5y CDS versus a long cash bond is a curve trade plus basis.
- **Look-ahead determinations.** Using the eventual ISDA outcome to decide the $t$ gate is not this spec.

## 11. Acceptance tests

- $B=s_{\mathrm{CDS}}-s_{\mathrm{bond}}$ to `1e-8`.
- $B<-c$ → long bond + long protection; $\lvert B\rvert\le c$ → flat.
- A toy default: bond jumps to recovery $R$, CDS pays $1-R$ on $N$ (up to CTD); package P&L matches that identity to `1e-6` when CTD = the held bond.
- Permuting next month’s spreads must not change the $t$ gate.
- Adding linear costs $\tau$ or a worse repo weakly decreases P&L.
- Missing borrow → positive-basis gate stays flat.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
