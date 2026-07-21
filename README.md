# US Options Strategy Recommender — 达尔文投资哲学融合版

A Hermes Agent skill that fetches live US stock options data and recommends appropriate trading strategies based on **Darwinian investment philosophy** — integrating the principles from Pulak Prasad's book "Investment Lessons from Darwin" (《我从达尔文那里学到的投资知识》).

[![GitHub](https://img.shields.io/badge/GitHub-gnuhpc%2Fus--options--strategy-blue)](https://github.com/gnuhpc/us-options-strategy)

## 达尔文核心哲学 (Core Philosophy)

This skill is unique: it doesn't just recommend strategies — it tells you when **NOT to trade**.

| Principle | Meaning |
|-----------|---------|
| **Type I Error Avoidance** | The best investors are the best rejectors. Avoiding bad trades > chasing good ones. |
| **Quality Matters** | Only trade options on high-quality businesses (ROCE filter, zero debt, stable industry). |
| **Punctuated Equilibrium** | Most days: do nothing. Wait for market dislocations (2008, 2020 style). |
| **Compound Over Time** | Prefer income strategies (selling premium) for steady compounding. |
| **Be the Bee** | Simple, repeatable process beats complex predictions. |

## Quick Start

```bash
pip install yfinance pandas

# Darwinian options analysis
python3 scripts/fetch_options.py AAPL 3 | python3 scripts/strategies.py
```

### Example Output

```json
{
  "ticker": "AAPL",
  "darwinian_quality": {
    "label": "exceptional",
    "score": 0.75,
    "details": ["Low beta", "Stable sector", "Large cap", "Pays dividend"]
  },
  "punctuated_equilibrium": {
    "is_punctuation": false,
    "type": "none",
    "darwinian_advice": "Most of the time, the best action is no action."
  },
  "recommendations": [
    {
      "name": "Cash-Secured Put (达尔文收入策略)",
      "score": 0.80,
      "recommended": true,
      "darwinian_rationale": "Getting paid to wait for a punctuation event..."
    }
  ]
}
```

## Darwinian Strategy Selection

| Sentiment | Volatility | Quality | Top Recommendation |
|-----------|-----------|---------|-------------------|
| Bullish | High | Good+ | Bull Put Spread (Credit) |
| Bullish | Low/Normal | Exceptional | Long Call (small bet) |
| Bearish | High | Good+ | Bear Call Spread (Credit) |
| Neutral | High | Good+ | Iron Condor |
| Neutral | Normal | Any | Calendar Spread |
| **Any** | **Any** | **Poor** | **🚫 DON'T TRADE** |
| **Punctuation** | **Any** | **Good+** | **Capitalize on dislocation** |

## Scripts

### `scripts/fetch_options.py <TICKER> [NUM_EXPIRATIONS]`
Fetches options chain data from Yahoo Finance. Outputs JSON.

### `scripts/strategies.py [data_file]`
Darwinian strategy recommendation engine. Reads from stdin or file.

Key functions:
- `assess_darwinian_quality()` — evaluates underlying business quality
- `detect_punctuated_equilibrium()` — finds market dislocations
- `recommend_strategies()` — full Darwinian recommendation engine

## Darwinian Quality Signals

| Signal | Source | Darwinian Interpretation |
|--------|--------|------------------------|
| Sector stability | Stock info | Stable = robust (like multicellular organisms) |
| Beta | Stock info | Low = robustness; High = fragile |
| Dividend yield | Stock info | Positive = generates real cash (costly signal) |
| Market cap | Stock info | Large = multi-layered robustness |
| 52-week range | Stock info | Near low = potential punctuation event |
| Put/Call Volume | Options chain | Costly signal — real money at work |
| IV Level | Options chain | High = fear premium; Low = complacency |

## Book Reference

This skill integrates the philosophy from **"Investment Lessons from Darwin"** (《我从达尔文那里学到的投资知识》) by Pulak Prasad, founder of Nalada Capital. Key chapters:

- **Ch 1**: Bumblebees — Type I error avoidance (don't lose money)
- **Ch 2**: Silver Foxes — ROCE as the single filter
- **Ch 3**: Robustness — multi-layered business stability
- **Ch 4**: Pavlovian Responses — ignore short-term noise
- **Ch 5**: Darwin's DCF — historical analysis > predictions
- **Ch 6**: Convergent Evolution — pattern recognition
- **Ch 7**: Green Frogs vs Guppies — costly signals matter
- **Ch 8-9**: Punctuated Equilibrium — use dislocations
- **Ch 10**: Rabbits & Compound Interest — patience pays
- **Conclusion**: Be the Bee — simple, repeatable process

## As a Hermes Agent Skill

```bash
ln -s /path/to/us-options-strategy ~/.hermes/skills/us-options-strategy
```

## Disclaimer

**This is for educational and informational purposes only. Not financial advice.**
As Darwin teaches: **"Survival first, profits second."**
Options trading involves substantial risk. Always do your own due diligence.

## License

MIT