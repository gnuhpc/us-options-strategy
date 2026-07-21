---
name: us-options-strategy
description: >
  Fetch US stock options chain data and recommend appropriate options trading strategies
  based on market sentiment, implied volatility, risk profile, AND Darwinian business quality
  assessment. Integrates the investment philosophy from "Investment Lessons from Darwin"
  by Pulak Prasad (Nalada Capital). Use this skill whenever the user asks about options
  trading, options strategies, stock options analysis, or mentions a stock ticker in the
  context of options trading. The skill fetches live data via yfinance and provides
  strategy recommendations with strike prices, risk metrics, and Darwinian reasoning.
---

# US Options Strategy Recommender
## 达尔文投资哲学融合版

Fetches live US stock options data from Yahoo Finance and recommends suitable options trading strategies based on **Darwinian investment philosophy** — integrating the principles from Pulak Prasad's book "Investment Lessons from Darwin" (《我从达尔文那里学到的投资知识》).

## 达尔文核心投资哲学 (Darwinian Philosophy)

This skill is built on the five core principles from Nalada Capital's approach:

### 1. Type I Error Avoidance (第一类错误优先)
> "The best investors are the best rejectors."
> *— Pulak Prasad*

In options trading, **not losing money is more important than making money**. The skill will actively warn you **NOT to trade** when the underlying stock fails quality checks. Darwinian "no-go zones":
- 🚫 **Fraudsters / poor governance** — never trade options on companies with questionable management
- 🚫 **Turnarounds** — don't bet on "comeback stories"
- 🚫 **High leverage** — avoid companies drowning in debt
- 🚫 **M&A addicts** — companies that binge on acquisitions
- 🚫 **Fast-changing industries** — tech, crypto, biotech hype
- 🚫 **Misaligned owners** — poor corporate governance

### 2. Quality Matters (质量优先)
> "High ROCE is the single filter that brings all other benefits."
> *— Chapter 2, The Silver Fox Experiment*

The skill assesses the **underlying stock's quality** using Darwinian metrics:
- **Business stability** (sector, size, history)
- **Financial robustness** (debt, cash flow, dividends)
- **Competitive moat** (market position, beta)
- **Industry evolution rate** (slow-changing vs fast-changing)

**Only trade options on high-quality businesses.** This is like the silver fox experiment — selecting for one trait (quality) brings many other benefits.

### 3. Punctuated Equilibrium (间断平衡)
> "Use rare discontinuities to buy, not sell."
> *— Chapter 9, From Fossils to Gold*

The skill detects **market dislocations** (punctuated equilibrium events):
- **Fear punctuations** — stock near 52-week low + high IV (like 2008, 2020)
- **IV spikes** — implied volatility surges (premium selling opportunity)
- **Complacency** — near all-time highs with low IV (danger zone)

**Most of the time, the best action is no action.** Be patient. Wait for punctuation events.

### 4. Compound Over Time (复利为王)
> "Darwin's greatest insight: compound interest creates life — and wealth."
> *— Chapter 10, Where Did All the Rabbits Go?*

The skill prioritizes **income-generating strategies** (selling premium) over speculative directional bets:
- **Cash-Secured Puts** — get paid to wait to buy quality at a discount
- **Covered Calls** — generate income from existing holdings
- **Credit Spreads** — defined risk, theta decay works for you

Like the rabbit story: small advantages compound into extraordinary results over time.

### 5. Be the Bee (做蜜蜂)
> "Bees use a simple, repeatable process to find the best hive. We do the same."
> *— Conclusion*

The skill follows a **simple, three-step process**:
1. **Avoid big risks** (Type I error prevention)
2. **Buy quality at fair price** (Darwinian quality filter)
3. **Don't buy easily, don't sell easily** (wait for punctuation events)

## Workflow

### Step 1: Fetch Options Data

```bash
python3 ~/.hermes/skills/us-options-strategy/scripts/fetch_options.py <TICKER> [NUM_EXPIRATIONS]
```

### Step 2: Get Darwinian Strategy Recommendations

```bash
python3 ~/.hermes/skills/us-options-strategy/scripts/fetch_options.py AAPL 3 | \
  python3 ~/.hermes/skills/us-options-strategy/scripts/strategies.py
```

### Step 3: Interpret the Output

The output includes **Darwinian analysis**:

| Section | What It Tells You |
|---------|-------------------|
| **darwinian_quality** | Business quality score (exceptional/good/average/poor/speculative) |
| **punctuated_equilibrium** | Whether a market dislocation is detected |
| **sentiment** | Market sentiment from options data (neutral/bullish/bearish) |
| **volatility** | IV regime (high/low/normal) |
| **warnings** | Darwinian red flags — when to **NOT** trade |
| **recommendations** | Top 7 strategies ranked by Darwinian score |

Each recommendation includes:
- **darwinian_rationale** — why this strategy fits the philosophy
- **recommended** (true/false) — whether to actually do it
- **score** — confidence level (0-1)

## Strategy Selection Logic (Darwinian)

| Sentiment | Volatility | Quality | Top Recommendation |
|-----------|-----------|---------|-------------------|
| Bullish | High | Good+ | Bull Put Spread (Credit) |
| Bullish | Low/Normal | Exceptional | Long Call (small bet) |
| Bullish | Any | Good+ | Cash-Secured Put |
| Bearish | High | Good+ | Bear Call Spread (Credit) |
| Bearish | Any | Poor | 🚫 DON'T TRADE |
| Neutral | High | Good+ | Iron Condor |
| Neutral | Low | Excellent | Long Straddle (rare) |
| Neutral | Normal | Any | Calendar Spread |
| Any | Any | Poor | 🚫 DON'T TRADE |
| Punctuation | Any | Good+ | Capitalize on dislocation |

## Scripts

### `scripts/fetch_options.py`
Fetches options chain data from Yahoo Finance. Outputs JSON.

### `scripts/strategies.py`
Analyzes fetched data and recommends strategies using Darwinian philosophy.
Key functions:
- `assess_darwinian_quality()` — evaluates underlying business quality
- `detect_punctuated_equilibrium()` — finds market dislocations
- `recommend_strategies()` — full recommendation engine

## Dependencies

- `yfinance` — Yahoo Finance data
- `pandas` — Data processing

## References

See `references/strategies.md` for detailed strategy explanations and Darwinian rationale.
See `references/book-to-skill-integration.md` for the workflow used to integrate this philosophy — a reusable pattern for incorporating any book's knowledge into a skill.

## Important Notes

- **This is for educational purposes only. Not financial advice.**
- As Darwin teaches: **"Survival first, profits second."**
- The Darwinian approach means: **most of the time, the best trade is NO trade.**
- Options trading involves substantial risk. Always do your own due diligence.
- The quality assessment is based on limited public data — it's not a substitute for fundamental analysis.