# 101 Quantitative Trading Strategies

This repo is a catalog of **101 trading strategy specs** I put together: equities, options, FX, futures, fixed income, volatility, ETFs, convertibles, crypto, and macro.

Each file in [`strategies/`](strategies/) is one strategy: the idea, the math, the signal, portfolio construction, data, risks, tests, and an agent contract. Start from the [full index](strategies/INDEX.md). Shared symbols are in [`strategies/_shared-notation.md`](strategies/_shared-notation.md).

These files are research specs. They do not place live orders by themselves. To turn a spec into a real model, use **[AgenKit](https://agenkit.xyz)** with Astra, Claude Code, Cursor, or Codex CLI.

## Build a strategy with AgenKit

### 1. Install AgenKit

Get it from [agenkit.xyz](https://agenkit.xyz) and install it into the agent you already use (Cursor, Claude Code, Codex CLI, OpenCode, Antigravity CLI, GitHub Copilot).

### 2. Open this repo

Clone the repo and open it in that agent.

### 3. Pick one spec

Open one markdown file from `strategies/`. Attach it in the chat. One strategy per run.

### 4. Run the command

**Cursor, Claude Code, and most other agents** — slash command:

```text
/agenkit build a production research system from strategies/001-price-momentum.md
```

**Codex CLI (Astra)** — `@` mention, not a slash command:

```text
@agenkit build a production research system from strategies/001-price-momentum.md
```

Copy, paste, run. AgenKit walks spec → architecture → plan → test-first build. Approve the spec, architecture, and plan before code is written.

## Copy commands

Price momentum:

```text
/agenkit build a production research system from strategies/001-price-momentum.md
```

```text
@agenkit build a production research system from strategies/001-price-momentum.md
```

Covered call:

```text
/agenkit implement strategies/005-covered-call.md as a payoff engine with expiry-grid tests
```

FX carry:

```text
/agenkit implement strategies/006-fx-carry.md as a research backtest with costs, delay-1 execution, and no live routing
```

Market making (simulator only):

```text
/agenkit build an Avellaneda-Stoikov market making model for Hyperliquid perps from strategies/048-market-making.md
```

```text
@agenkit build an Avellaneda-Stoikov market making model for Hyperliquid perps from strategies/048-market-making.md
```

Swap the path for any other file in the [index](strategies/INDEX.md). Add a short note for universe, venue, or delay if you want. You do not need to restate the math. It is already in the file.

## What AgenKit is

AgenKit is not another model. It is the harness that turns Astra (or Claude, Cursor, Codex) into a full engineering team: brainstorm, architecture, plan, build, review, ship.

Grab it at [agenkit.xyz](https://agenkit.xyz).

## Disclaimer

Not investment, legal, or tax advice. Research specs only.
