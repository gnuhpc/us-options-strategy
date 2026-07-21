---
name: us-options-strategy
description: >
  Fetch US stock options chain data and recommend appropriate options trading strategies
  based on market sentiment, implied volatility, and risk profile. Use this skill whenever
  the user asks about options trading, options strategies, stock options analysis, or mentions
  a stock ticker in the context of options trading. The skill fetches live data via yfinance
  and provides strategy recommendations with strike prices, risk metrics, and reasoning.
---

# US Options Strategy Recommender

Fetches live US stock options data from Yahoo Finance and recommends suitable options trading strategies based on market sentiment, implied volatility, and risk profile.

## When to Use

- User asks "what options strategy should I use for [ticker]?"
- User wants to analyze options chain data for a stock
- User asks for put/call ratios, IV analysis, or strategy ideas
- User mentions a ticker in the context of trading options

## Workflow

### Step 1: Fetch Options Data

Use the `fetch_options.py` script to get live options chain data for the requested ticker:

```bash
python3 ~/.hermes/skills/us-options-strategy/scripts/fetch_options.py <TICKER> [NUM_EXPIRATIONS]
```

- `TICKER`: US stock symbol (e.g. AAPL, SPY, TSLA, AMZN)
- `NUM_EXPIRATIONS`: Number of near-term expiration dates to fetch (default: 3)

Example:
```bash
python3 ~/.hermes/skills/us-options-strategy/scripts/fetch_options.py AAPL 3
```

This outputs structured JSON with:
- Current stock price and company info
- Options chain for each expiration (calls and puts)
- Summary statistics: put/call ratios, IV, IV skew, volume, open interest

### Step 2: Get Strategy Recommendations

Pipe the output into the strategy analyzer:

```bash
python3 ~/.hermes/skills/us-options-strategy/scripts/fetch_options.py AAPL 3 | \
  python3 ~/.hermes/skills/us-options-strategy/scripts/strategies.py
```

Or run in two steps:
```bash
python3 ~/.hermes/skills/us-options-strategy/scripts/fetch_options.py AAPL -o /tmp/aapl_data.json
python3 ~/.hermes/skills/us-options-strategy/scripts/strategies.py /tmp/aapl_data.json
```

### Step 3: Present to User

The output includes:
- **Sentiment analysis** (bullish/bearish/neutral with confidence score)
- **Volatility regime** (high/low/normal with current IV value)
- **Top 5 strategies** ranked by probability score, each with:
  - Strategy name and direction
  - Risk level
  - Suggested strike prices
  - Max profit / max loss description
  - When to use guidance
  - Confidence score

## Strategy Reference

See `references/strategies.md` for detailed explanations of each strategy.

## Strategy Selection Logic

The engine uses these signals:

| Signal | Source | Interpretation |
|--------|--------|----------------|
| Put/Call Volume Ratio | Options chain | >1.3 = bearish, <0.5 = bullish |
| Put/Call OI Ratio | Options chain | >1.3 = bearish, <0.6 = bullish |
| IV Skew | OTM put IV - OTM call IV | Positive = fear (bearish), Negative = greed (bullish) |
| Implied Volatility Level | Options chain | >50% = high, <20% = low |
| Liquidity (Volume + OI) | Options chain | Higher = tighter spreads, easier execution |

### Strategy Mapping

| Sentiment | Volatility | Recommended Strategies |
|-----------|-----------|----------------------|
| Bullish | High | Bull Put Spread (credit), Short Put |
| Bullish | Low/Normal | Long Call, Bull Call Spread |
| Bearish | High | Bear Call Spread (credit) |
| Bearish | Low/Normal | Long Put, Bear Put Spread |
| Neutral | High | Iron Condor, Short Straddle |
| Neutral | Low | Long Straddle (breakout bet) |
| Neutral | Normal | Calendar Spread, Covered Call |
| Any | Any | Cash-Secured Put (income) |

## Scripts

### `scripts/fetch_options.py`
Fetches options chain data from Yahoo Finance. Outputs JSON.

Usage: `python3 scripts/fetch_options.py <TICKER> [NUM_EXPIRATIONS]`

### `scripts/strategies.py`
Analyzes fetched data and recommends strategies. Reads JSON from stdin or file.

Usage: `python3 scripts/strategies.py [data_file]`

## Dependencies

- `yfinance` - Yahoo Finance data
- `pandas` - Data processing

Install: `pip install yfinance pandas`

## Important Notes

- This is for **educational and informational purposes only**. Not financial advice.
- Options trading involves substantial risk and is not suitable for all investors.
- Always verify liquidity (volume + open interest) before trading.
- The analysis uses near-term expirations only — adjust for longer-dated strategies.
- Consider your own risk tolerance and portfolio context before acting on any recommendation.