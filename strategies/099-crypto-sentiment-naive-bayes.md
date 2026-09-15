---
rank: 99
slug: crypto-sentiment-naive-bayes
title: "Crypto Sentiment — Naive Bayes Bernoulli"
asset_class: "cryptocurrencies"
style: "text classification / tweet features"
horizon: "Intraday to daily, matched to tweet aggregation window"
instruments: "BTC; tweet (or similar) text stream"
---

# 099. Crypto Sentiment — Naive Bayes Bernoulli

| Field | Value |
|---|---|
| Popularity rank (this kit) | 99 of 101 |
| Why it sits here | Standard NLP-to-price pipeline: bag-of-words Bernoulli naive Bayes on cleaned tweets, used on BTC as specified here. |
| Aliases | tweet sentiment, Bernoulli NB, bag-of-words BTC |
| Asset class | cryptocurrencies |
| Style | text classification / tweet features |
| Typical horizon | Intraday to daily, matched to tweet aggregation window |
| Instruments | BTC; tweet (or similar) text stream |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Clean a public tweet (or similar) stream: drop bots and duplicates, strip stop-words, stem. Represent each document as a binary bag-of-words against a frozen vocabulary $V$. A Bernoulli naive Bayes classifier predicts an up/down class or a return quantile. Trade the predicted class on BTC.

You are betting that a statistical association between public bag-of-words features and the **next** coin bar is strong enough, after costs, to trade. You are not claiming that tweets cause the move, and you are not reading private messages, DMs, or scraped content that violates terms of service. You are not labelling documents with the same bar’s return you are supposed to predict.

The aggregation window ends before the fill. Vocabulary $V$ is frozen at the train cut; it does not grow on the test stream. Priors and appearance probabilities come from training frequencies with Laplace smoothing, using labels built from future returns that are still before the test window. Empty windows are flat. Sentiment is not a fundamental value model.

A tweet stamped 10 milliseconds after $t-\varepsilon$ is out, even if your collector saw it in the same wall-clock second as the window close. Clock skew between the text API and the coin venue is a data bug, not an edge. Language drift is why you freeze $V$: a 2021 meme stem with a 2024 meaning is a different token, and growing $V$ on the test stream lets the classifier peek at which new words later co-moved with BTC. Aligning labels with the tweet bar’s own return is the same leak.

## 2. First principles

Each document $i$ is a binary vector over a vocabulary of $M$ stems $w_a$. The feature is whether the stem appears, not how often:

$$
X_{ia} = 1 \text{ if } w_a \text{ appears in document } i,\quad 0 \text{ otherwise}
$$

Bernoulli features ignore term frequency: a stem that appears once is the same as a stem that appears ten times. That is a modelling choice, not a claim about language. $V$ is frozen at the train cut; a stem that first appears in the live window is unseen and handled by smoothing, not by expanding $M$. Documents timestamped after the window end do not enter $X_{ia}$.

Classes $C_{\alpha}$ are the trading labels (two-way up/down, or $K$ return quantiles). Bayes’ rule says the posterior is likelihood times prior, up to a constant that does not depend on $\alpha$:

$$
P(C_{\alpha}\mid X) = \frac{P(X\mid C_{\alpha})\,P(C_{\alpha})}{P(X)} \propto P(X\mid C_{\alpha})\,P(C_{\alpha})
$$

$P(X)$ does not change the $\arg\max$, so the live classifier never needs it. $P(C_{\alpha})$ is a training frequency, not a live tweet count. Labels that define $C_{\alpha}$ are aligned with **future** BTC returns, not the bar during which the tweets arrived.

The **naive** step is conditional independence of tokens given the class. Under a Bernoulli model each token is a coin flip with class-specific appearance probability $P(w_a\mid C_{\alpha})$, so one document contributes

$$
P(X_i\mid C_{\alpha}) = \prod_{a=1}^{M} \bigl[P(w_a\mid C_{\alpha})\bigr]^{X_{ia}}\bigl[1-P(w_a\mid C_{\alpha})\bigr]^{1-X_{ia}}
$$

Independence is false for language; it is the approximation that makes the product tractable. The $1-P$ term matters: absent stems still vote. Without Laplace smoothing, a single unseen stem with $P(w_a\mid C_{\alpha})=0$ zeroes the whole product. Compute in logs to avoid underflow.

For a window of $N$ documents treated as independent given the class, the posterior is proportional to

$$
P(C_{\alpha}\mid X_1,\ldots,X_N)
\propto P(C_{\alpha})\prod_{i=1}^N \prod_{a=1}^{M}
[P(w_a\mid C_{\alpha})]^{X_{ia}}[1-P(w_a\mid C_{\alpha})]^{1-X_{ia}}
$$

Documents in the window are not really independent either; the product is still the spec. $N=0$ (empty window) has no product to maximise — flatten, do not recycle yesterday’s class. Bot filters and dedupe run before this product, with rules dated $\le$ the window end.

The predicted class is the $\alpha$ that maximises that quantity:

$$
C_{\mathrm{pred}}
= \arg\max_{C_{\alpha}} \; P(C_{\alpha})
\prod_i\prod_a [P(w_a\mid C_{\alpha})]^{X_{ia}}[1-P(w_a\mid C_{\alpha})]^{1-X_{ia}}
$$

$P(w_a\mid C_{\alpha})$ and $P(C_{\alpha})$ come from **training** frequencies, with Laplace smoothing so that unseen stems do not zero the product. Map $C_{\mathrm{pred}}$ to buy/sell. Two-class maps up to long and down to short. Quantile classes buy the top, sell the bottom, otherwise flat — the same extreme-only rule as the ANN overlay. Ties in the $\arg\max$ are flat.

That is the whole strategy. Everything below is how to clean text without leaking, how to time the window, and how not to train on contemporaneous returns.

## 3. Notation

| Symbol | Definition |
|---|---|
| $V = \{w_a\}_{a=1}^{M}$ | frozen vocabulary of stems |
| $M$ | vocabulary size |
| $i = 1,\ldots,N$ | documents in the aggregation window |
| $X_{ia}\in\{0,1\}$ | token $w_a$ present in document $i$ |
| $C_{\alpha}$ | class (up/down or quantile) |
| $P(C_{\alpha})$ | class prior from training |
| $P(w_a\mid C_{\alpha})$ | Bernoulli appearance probability |
| $C_{\mathrm{pred}}$ | $\arg\max$ class on the live window |
| $I$ | absolute dollars on BTC |

## 4. Mathematics

### 4.1 Cleaning and features

Deduplicate. Drop bot-like accounts by a documented rule dated $\le$ the window end. Stop-words out. Stem with Porter or equivalent. Feature $X_{ia}=1$ if word $w_a$ appears in tweet $i$. Vocabulary $V$ is frozen at the train cut; do not grow $V$ on the test window. A tweet timestamped after $t-\varepsilon$ does not enter $X_{ia}$. Public text only.

### 4.2 Training frequencies

On the training set, with Laplace pseudo-count $\alpha_{\mathrm{L}} > 0$, the class prior is

$$
P(C_{\alpha}) = \frac{n_{\alpha} + \alpha_{\mathrm{L}}}{n + A\alpha_{\mathrm{L}}}
$$

$n_{\alpha}$ is the training document count in class $\alpha$, $n$ is the training document count, $A$ is the number of classes. The prior is not updated on the live window. Labels behind $n_{\alpha}$ use returns after those documents and before the test cut.

The Bernoulli appearance probability is

$$
P(w_a\mid C_{\alpha}) = \frac{n_{a\alpha} + \alpha_{\mathrm{L}}}{n_{\alpha} + 2\alpha_{\mathrm{L}}}
$$

where $n_{\alpha}$ is the document count in class $\alpha$, $n_{a\alpha}$ is how many of those contain $w_a$, $n$ is the training document count, and $A$ is the number of classes. The $2\alpha_{\mathrm{L}}$ in the denominator is the Bernoulli two-outcome smoother. These are the training frequencies in this spec. Freeze them at the train cut; do not online-update $P(w_a\mid C_{\alpha})$ with test tweets.

### 4.3 Posterior and prediction

With conditional independence, the live posterior (up to $P(X)$) is

$$
P(C_{\alpha}\mid X_1,\ldots,X_N)
\propto P(C_{\alpha})\prod_{i=1}^N \prod_{a=1}^{M}
[P(w_a\mid C_{\alpha})]^{X_{ia}}[1-P(w_a\mid C_{\alpha})]^{1-X_{ia}}
$$

This is the same product as in §2, now evaluated on the live window with frozen training frequencies. Empty $N$ is not a uniform posterior you trade; it is a skip.

The predicted class maximises that quantity:

$$
C_{\mathrm{pred}}
= \arg\max_{C_{\alpha}} \; P(C_{\alpha})
\prod_i\prod_a [P(w_a\mid C_{\alpha})]^{X_{ia}}[1-P(w_a\mid C_{\alpha})]^{1-X_{ia}}
$$

Compute in logs to avoid underflow. Align class labels with **future** returns, not contemporaneous (no leakage). A leakage test that builds labels from $R(t)$ on the tweet bar must fail; the implementation uses $R^{\mathrm{fwd}}$ only.

### 4.4 Holdings and P&L

Two-class: buy if $C_{\mathrm{pred}} = \mathrm{up}$, sell if $\mathrm{down}$. Quantile classes: buy the top class, sell the bottom, otherwise flat (same rule as the ANN overlay). Signed dollars are

$$
D = \begin{cases} +I & C_{\mathrm{pred}}\ \mathrm{maps\ to\ long} \\ -I & C_{\mathrm{pred}}\ \mathrm{maps\ to\ short} \\ 0 & \mathrm{otherwise} \end{cases}
$$

$I$ is absolute dollars on BTC spot or perp, capped by ADV/depth. Interior quantile classes are $D=0$. Empty window is $D=0$.

Holding-period P&L on the next coin bar is

$$
\mathrm{P\&L} = D\, R^{\mathrm{fwd}} - \mathrm{costs} - \mathrm{funding}
$$

Fill is delay-1 into the next coin bar after the aggregation window closes. $R^{\mathrm{fwd}}$ is that bar’s simple return, plus perp funding if the instrument is a perp. Costs include fees and spread. Sentiment $\neq$ causation: this identity is P&L, not a structural model of attention.

## 5. Step-by-step algorithm

1. **Stream.** Public tweet (or similar) text only. No scraping that violates ToS. Timestamp every document. This step exists so the feature clock is a public timestamp, not a scrape time you cannot replay.
2. **Clean.** Dedupe, drop bots, stop-words, Porter stem. Build $X_{ia}$ against frozen $V$. This step exists so $V$ and the bot rule cannot quietly expand on the test stream.
3. **Window.** Aggregate documents in a window that **ends before** the trade. Empty window $\Rightarrow$ flat. This step exists so a tweet after $t-\varepsilon$ cannot vote.
4. **Train cut.** Fit $P(C_{\alpha})$ and $P(w_a\mid C_{\alpha})$ on documents whose labels use returns **after** those documents and **before** the test window. Document the cut. This step exists to stop contemporaneous labelling and test-set frequency peeking.
5. **Predict.** Compute $C_{\mathrm{pred}}$ in log space. Map to buy/sell (two-class or quantile classes). This step exists so underflow does not masquerade as a class, and so interior quantile classes stay flat.
6. **Size.** $\lvert D \rvert = I$ on BTC spot or perp, ADV/depth cap. This step exists so a loud window cannot size through the book.
7. **Blotter.** Single-name intent. Never live routing. This step exists to keep the research contract off the venue.
8. **Rebalance.** At the aggregation-window close, delay-1 into the next coin bar. This step exists so the coin fill is after the text window, not inside it.

## 6. Execution protocol

- Stem with Porter or equivalent. Drop duplicates. Align class labels with **future** returns, not contemporaneous (no leakage).
- Aggregate tweets in a window ending before the trade. A tweet timestamped after $t-\varepsilon$ does not enter $X_{ia}$.
- Public text only. No scraping that violates ToS. Sentiment $\neq$ causation.
- Deleted tweets: if they were public at $t-\varepsilon$, a research replay may keep them; a live book cannot retrieve what the API no longer serves. Document the choice.

## 7. Data contract

Required, point-in-time:

- Document text, unique id, timestamp, and (if used) account id for bot filters
- Frozen vocabulary $V$ dated at the train cut
- BTC prices on the holding bar, plus fees/funding if a perp
- Train/test cut timestamp

Look-ahead that invalidates a historical blotter: a tweet after the window end, a vocabulary grown on test text, labels from contemporaneous $R(t)$, bot filters that use later account status, or training frequencies updated with test documents. Non-public messages and ToS-violating scrapes are out of contract, not “alternative data.” A restored tweet that was not public at $t-\varepsilon$ must not re-enter a historical window; a deleted tweet that was public at $t-\varepsilon$ is a documented replay choice, not a silent drop that correlates with later dumps.

Not used by this spec: non-public messages, scraped content that violates ToS, equity fundamentals.

Deleted tweets: if they were public at $t-\varepsilon$, a research replay may keep them; a live book cannot retrieve what the API no longer serves. Document the choice.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $M$ | caller-set | vocabulary size |
| window | matched to horizon | ends before the fill |
| smoothing | Laplace $\alpha_{\mathrm{L}} > 0$ | on $P(w_a\mid C_{\alpha})$ and priors |
| stemmer | Porter | or documented equivalent |
| classes | up/down or quantiles | freeze before test |
| delay | 1 bar after window end | no contemporaneous label |

## 9. Agent implementation contract

Build a Python module `strategies.crypto_sentiment_naive_bayes` with:

1. `featurize(docs, vocab) -> np.ndarray` — binary $X_{ia}$, stems, no future docs.
2. `fit(X, labels, alpha) -> tuple` — $P(C_{\alpha})$, $P(w_a\mid C_{\alpha})$ with Laplace smoothing.
3. `predict(X_window, priors, cond) -> class` — $C_{\mathrm{pred}}$, log-space $\arg\max$.
4. `blotter(C_pred, I, px, lot) -> list[OrderIntent]` — BTC intent, never live routing.
5. `pnl(D, forward_return, costs, funding) -> float` — matches $D R^{\mathrm{fwd}} - \mathrm{costs} - \mathrm{funding}$.

Public text only. No scraping that violates ToS. Document train/test cut. Sentiment $\neq$ causation. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Bots, deleted tweets, language shift.** The vocabulary ages; $P(w_a\mid C_{\alpha})$ does not.
- **Exchange-specific pumps.** Text can be promotional, not informational.
- **Sparse $V$.** A rare stem with a noisy $P(w_a\mid C_{\alpha})$ can dominate the product unless smoothed.
- **Look-ahead in labelling.** Contemporaneous returns turn the classifier into a readout of the bar you are supposed to predict.

## 11. Acceptance tests

- Empty window $\Rightarrow$ no trade.
- Two-class toy: a document whose only token has $P(w\mid\mathrm{up})=1$ and $P(w\mid\mathrm{down})=0$ (after smoothing, near 1 vs near 0) $\Rightarrow$ $C_{\mathrm{pred}}=\mathrm{up}$.
- Permuting tweets after the window end must not change $C_{\mathrm{pred}}$ at that window.
- Labels built from contemporaneous $R(t)$ must fail a leakage test: the implementation uses $R^{\mathrm{fwd}}$ only.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
