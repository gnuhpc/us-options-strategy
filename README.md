# US Options Strategy Recommender

A Hermes Agent skill that fetches live US stock options data and recommends appropriate trading strategies based on market sentiment, implied volatility, and risk profile.

[![GitHub](https://img.shields.io/badge/GitHub-gnuhpc%2Fus--options--strategy-blue)](https://github.com/gnuhpc/us-options-strategy)

## What It Does

1. **Fetches** live options chain data from Yahoo Finance (yfinance)
2. **Analyzes** market sentiment via put/call ratios, IV skew, and volume/OI data
3. **Recommends** suitable options strategies with specific strike prices, risk metrics, and reasoning

## Quick Start

```bash
# Install dependencies
pip install yfinance pandas

# Fetch data and get recommendations
python3 scripts/fetch_options.py AAPL 3 | python3 scripts/strategies.py
```

### Example Output

```json
{
  "ticker": "AAPL",
  "sentiment": { "label": "neutral", "confidence": 0.12 },
  "volatility": { "label": "normal", "implied_volatility": 0.28 },
  "recommendations": [
    {
      "name": "Cash-Secured Put",
      "direction": "neutral/bullish",
      "risk_level": "low",
      "score": 0.70,
      "suggested_strikes": [215.0]
    },
    {
      "name": "Iron Condor",
      "direction": "neutral",
      "risk_level": "medium",
      "score": 0.65,
      "suggested_strikes": [200.0, 240.0]
    },
    {
      "name": "Calendar Spread",
      "direction": "neutral",
      "risk_level": "low",
      "score": 0.55
    }
  ]
}
```

## Strategy Selection Logic

| Sentiment | Volatility | Recommended Strategies |
|-----------|-----------|----------------------|
| Bullish | High | Bull Put Spread (credit) |
| Bullish | Low/Normal | Long Call, Bull Call Spread |
| Bearish | High | Bear Call Spread (credit) |
| Bearish | Low/Normal | Long Put, Bear Put Spread |
| Neutral | High | Iron Condor, Short Straddle |
| Neutral | Low | Long Straddle (breakout bet) |
| Neutral | Normal | Calendar Spread, Covered Call |
| Any | Any | Cash-Secured Put (income) |

## Scripts

### `scripts/fetch_options.py <TICKER> [NUM_EXPIRATIONS]`
Fetches options chain data. Outputs JSON to stdout.

### `scripts/strategies.py [data_file]`
Analyzes options data and recommends strategies. Reads from stdin or file.

## Signals Used

| Signal | Source | Interpretation |
|--------|--------|----------------|
| Put/Call Volume Ratio | Options chain | >1.3 = bearish, <0.5 = bullish |
| Put/Call OI Ratio | Options chain | >1.3 = bearish, <0.6 = bullish |
| IV Skew | OTM put IV - OTM call IV | Positive = fear (bearish), Negative = greed (bullish) |
| Implied Volatility | Options chain | >50% = high, <20% = low |
| Liquidity (Volume + OI) | Options chain | Higher = tighter spreads |

## Reference

See `references/strategies.md` for detailed explanations of each strategy (Long Call, Iron Condor, Calendar Spread, Covered Call, Wheel, etc.).

## As a Hermes Agent Skill

This project is structured as a **Hermes Agent skill**. When loaded:

1. The skill auto-loads via `skills_list` when the user mentions options trading
2. It guides the agent through fetching data and analyzing strategies
3. The Python scripts handle the heavy lifting (data fetching, analysis)

To install as a Hermes skill:
```bash
ln -s /path/to/us-options-strategy ~/.hermes/skills/us-options-strategy
```

## Disclaimer

**This is for educational and informational purposes only. Not financial advice.**
Options trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always do your own due diligence and consult a qualified financial advisor.

## License

MIT