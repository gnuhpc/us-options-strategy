#!/usr/bin/env python3
"""
Options Strategy Recommender

Analyzes fetched options data and recommends appropriate trading strategies
based on market sentiment, implied volatility, and risk profile.
"""

import json
import sys
from enum import Enum


class Sentiment(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    SLIGHTLY_BULLISH = "slightly_bullish"
    SLIGHTLY_BEARISH = "slightly_bearish"


class Volatility(Enum):
    HIGH = "high"
    LOW = "low"
    NORMAL = "normal"


class StrategyRecommendation:
    def __init__(
        self,
        name: str,
        direction: str,
        risk_level: str,
        max_profit: str,
        max_loss: str,
        description: str,
        when_to_use: str,
        probability: float,
        suggested_strikes: list = None,
    ):
        self.name = name
        self.direction = direction
        self.risk_level = risk_level
        self.max_profit = max_profit
        self.max_loss = max_loss
        self.description = description
        self.when_to_use = when_to_use
        self.probability = probability
        self.suggested_strikes = suggested_strikes or []

    def to_dict(self):
        return {
            "name": self.name,
            "direction": self.direction,
            "risk_level": self.risk_level,
            "max_profit": self.max_profit,
            "max_loss": self.max_loss,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "score": round(self.probability, 2),
            "suggested_strikes": self.suggested_strikes,
        }


def classify_sentiment(data: dict) -> tuple:
    """
    Classify market sentiment from options data.
    Returns (Sentiment, confidence_score).
    """
    sentiment_scores = []

    for exp in data.get("expirations", []):
        summary = exp.get("summary", {})

        # Put/Call volume ratio: >1.0 = bearish, <0.7 = bullish
        pc_vol = summary.get("pc_volume_ratio")
        if pc_vol is not None:
            if pc_vol > 1.3:
                sentiment_scores.append(("bearish", -0.8))
            elif pc_vol > 1.0:
                sentiment_scores.append(("bearish", -0.3))
            elif pc_vol < 0.5:
                sentiment_scores.append(("bullish", 0.8))
            elif pc_vol < 0.7:
                sentiment_scores.append(("bullish", 0.4))
            else:
                sentiment_scores.append(("neutral", 0.0))

        # Put/Call OI ratio
        pc_oi = summary.get("pc_oi_ratio")
        if pc_oi is not None:
            if pc_oi > 1.3:
                sentiment_scores.append(("bearish", -0.6))
            elif pc_oi < 0.6:
                sentiment_scores.append(("bullish", 0.6))
            else:
                sentiment_scores.append(("neutral", 0.0))

        # IV skew: positive = puts more expensive (fear), negative = calls more expensive
        iv_skew = summary.get("iv_skew")
        if iv_skew is not None:
            if iv_skew > 0.05:
                sentiment_scores.append(("bearish", -0.5))
            elif iv_skew < -0.05:
                sentiment_scores.append(("bullish", 0.5))

    if not sentiment_scores:
        return Sentiment.NEUTRAL, 0.0

    # Weighted average
    total_score = sum(s[1] for s in sentiment_scores)
    avg_score = total_score / len(sentiment_scores)

    if avg_score > 0.5:
        return Sentiment.BULLISH, avg_score
    elif avg_score > 0.15:
        return Sentiment.SLIGHTLY_BULLISH, avg_score
    elif avg_score < -0.5:
        return Sentiment.BEARISH, abs(avg_score)
    elif avg_score < -0.15:
        return Sentiment.SLIGHTLY_BEARISH, abs(avg_score)
    else:
        return Sentiment.NEUTRAL, abs(avg_score)


def classify_volatility(data: dict) -> tuple:
    """
    Classify implied volatility regime.
    Returns (Volatility, iv_value).
    """
    ivs = []
    for exp in data.get("expirations", []):
        iv = exp.get("summary", {}).get("avg_implied_volatility")
        if iv:
            ivs.append(iv)

    if not ivs:
        return Volatility.NORMAL, 0.0

    avg_iv = sum(ivs) / len(ivs)

    # Rough guideline: IV > 0.5 is high, IV < 0.2 is low
    if avg_iv > 0.5:
        return Volatility.HIGH, avg_iv
    elif avg_iv < 0.2:
        return Volatility.LOW, avg_iv
    else:
        return Volatility.NORMAL, avg_iv


def find_liquid_strikes(contracts, current_price, direction="atm", count=3):
    """
    Find the most liquid (highest volume + open interest) strikes near the money.
    """
    if not contracts:
        return []

    # Filter to strikes near current price
    nearby = [c for c in contracts if 0.85 * current_price <= c["strike"] <= 1.15 * current_price]
    nearby.sort(key=lambda c: (c["volume"] + c["open_interest"]), reverse=True)
    return nearby[:count]


def recommend_strategies(data: dict) -> list:
    """
    Main recommendation engine. Analyzes data and returns ranked strategies.
    """
    sentiment, confidence = classify_sentiment(data)
    vol_regime, avg_iv = classify_volatility(data)
    current_price = data.get("current_price")
    recommendations = []

    if not current_price:
        return [{"error": "No current price data available"}]

    # Get nearest expiration data
    nearest_exp = data.get("expirations", [{}])[0]
    if not nearest_exp or "error" in nearest_exp:
        return [{"error": "No valid expiration data"}]

    calls = nearest_exp.get("calls", [])
    puts = nearest_exp.get("puts", [])
    days_to_expiry = nearest_exp.get("days_to_expiry", 30)
    expiry = nearest_exp.get("expiration", "N/A")

    # ----- Strategy Selection Logic -----

    if sentiment in (Sentiment.BULLISH, Sentiment.SLIGHTLY_BULLISH):
        # Bullish strategies

        if vol_regime == Volatility.HIGH:
            # High IV + Bullish → sell puts (credit), or bull put spread
            otm_puts = [p for p in puts if p["strike"] < current_price * 0.95]
            if otm_puts:
                liquid_puts = sorted(otm_puts, key=lambda p: p["volume"] + p["open_interest"], reverse=True)[:2]
                strike = liquid_puts[0]["strike"] if liquid_puts else round(current_price * 0.93, 2)
                recommendations.append(StrategyRecommendation(
                    name="Bull Put Spread (Credit Spread)",
                    direction="bullish",
                    risk_level="medium",
                    max_profit="Net credit received",
                    max_loss="Width of strikes - net credit",
                    description=f"Sell a put at ${strike} and buy a lower put as protection. "
                                f"IV is high ({avg_iv:.1%}), so premiums are rich — collect theta decay.",
                    when_to_use="High IV environments where you expect the stock to stay above the short strike. "
                                "Theta works in your favor.",
                    probability=0.75,
                    suggested_strikes=[strike, round(strike - 0.05 * current_price, 2)],
                ))

        # Long Call (if volatility is reasonable)
        if vol_regime in (Volatility.LOW, Volatility.NORMAL):
            otm_calls_1 = [c for c in calls if c["strike"] > current_price * 1.02]
            if otm_calls_1:
                liquid_calls = sorted(otm_calls_1, key=lambda c: c["volume"] + c["open_interest"], reverse=True)[:2]
                strike = liquid_calls[0]["strike"] if liquid_calls else round(current_price * 1.05, 2)
                recommendations.append(StrategyRecommendation(
                    name="Long Call",
                    direction="bullish",
                    risk_level="high",
                    max_profit="Unlimited",
                    max_loss=f"Premium paid (${strike} strike)",
                    description=f"Buy a call option at ${strike}. "
                                f"Sentiment is {sentiment.value} with confidence {confidence:.0%}.",
                    when_to_use="Strong bullish outlook, low IV environment. Define risk with a fixed premium.",
                    probability=0.35,
                    suggested_strikes=[strike],
                ))

        # Bull Call Spread (lower risk)
        otm_calls = [c for c in calls if c["strike"] > current_price * 1.02]
        if len(otm_calls) >= 2:
            lower_strike = otm_calls[0]["strike"]
            higher_strike = otm_calls[min(2, len(otm_calls) - 1)]["strike"]
            recommendations.append(StrategyRecommendation(
                name="Bull Call Spread (Debit Spread)",
                direction="bullish",
                risk_level="medium",
                max_profit="(Higher strike - lower strike) - net debit",
                max_loss="Net debit paid",
                description=f"Buy ${lower_strike} call, sell ${higher_strike} call. "
                            f"Limited risk, defined profit, lower cost than a naked call.",
                when_to_use="Moderately bullish with defined risk. The spread reduces cost basis vs a naked call.",
                probability=0.45,
                suggested_strikes=[lower_strike, higher_strike],
            ))

    elif sentiment in (Sentiment.BEARISH, Sentiment.SLIGHTLY_BEARISH):
        # Bearish strategies

        if vol_regime == Volatility.HIGH:
            # High IV + Bearish → sell calls (credit), or bear call spread
            otm_calls = [c for c in calls if c["strike"] > current_price * 1.05]
            if otm_calls:
                liquid_calls = sorted(otm_calls, key=lambda c: c["volume"] + c["open_interest"], reverse=True)[:2]
                strike = liquid_calls[0]["strike"] if liquid_calls else round(current_price * 1.07, 2)
                recommendations.append(StrategyRecommendation(
                    name="Bear Call Spread (Credit Spread)",
                    direction="bearish",
                    risk_level="medium",
                    max_profit="Net credit received",
                    max_loss="Width of strikes - net credit",
                    description=f"Sell a call at ${strike} and buy a higher call as protection. "
                                f"IV is high ({avg_iv:.1%}), so you collect rich premium.",
                    when_to_use="High IV, bearish or neutral outlook. Theta decay works in your favor.",
                    probability=0.70,
                    suggested_strikes=[strike, round(strike + 0.05 * current_price, 2)],
                ))

        if vol_regime in (Volatility.LOW, Volatility.NORMAL):
            otm_puts = [p for p in puts if p["strike"] < current_price * 0.98]
            if otm_puts:
                liquid_puts = sorted(otm_puts, key=lambda p: p["volume"] + p["open_interest"], reverse=True)[:2]
                strike = liquid_puts[0]["strike"] if liquid_puts else round(current_price * 0.95, 2)
                recommendations.append(StrategyRecommendation(
                    name="Long Put",
                    direction="bearish",
                    risk_level="high",
                    max_profit="Large (up to strike price)",
                    max_loss=f"Premium paid (${strike} strike)",
                    description=f"Buy a put option at ${strike}. "
                                f"Sentiment is {sentiment.value} with confidence {confidence:.0%}.",
                    when_to_use="Strong bearish outlook. Hedge or directional bet.",
                    probability=0.30,
                    suggested_strikes=[strike],
                ))

        # Bear Put Spread
        otm_puts_for_spread = [p for p in puts if p["strike"] < current_price * 0.98]
        if len(otm_puts_for_spread) >= 2:
            higher_strike = otm_puts_for_spread[0]["strike"]
            lower_strike = otm_puts_for_spread[min(1, len(otm_puts_for_spread) - 1)]["strike"]
            recommendations.append(StrategyRecommendation(
                name="Bear Put Spread (Debit Spread)",
                direction="bearish",
                risk_level="medium",
                max_profit="(Higher strike - lower strike) - net debit",
                max_loss="Net debit paid",
                description=f"Buy ${higher_strike} put, sell ${lower_strike} put. "
                            f"Limited risk, defined profit.",
                when_to_use="Moderately bearish with defined risk.",
                probability=0.40,
                suggested_strikes=[higher_strike, lower_strike],
            ))

    else:
        # Neutral sentiment
        if vol_regime == Volatility.HIGH:
            # High IV + Neutral → Iron Condor or Short Straddle
            otm_calls = [c for c in calls if c["strike"] > current_price * 1.08]
            otm_puts = [p for p in puts if p["strike"] < current_price * 0.92]
            if otm_calls and otm_puts:
                call_strike = otm_calls[0]["strike"] if otm_calls else round(current_price * 1.10, 2)
                put_strike = otm_puts[-1]["strike"] if otm_puts else round(current_price * 0.90, 2)
                recommendations.append(StrategyRecommendation(
                    name="Iron Condor",
                    direction="neutral",
                    risk_level="medium",
                    max_profit="Net credit received",
                    max_loss="Width of a wing - net credit",
                    description=f"Sell ${put_strike} put / buy lower put + sell ${call_strike} call / buy higher call. "
                                f"IV is high ({avg_iv:.1%}) — perfect for selling premium.",
                    when_to_use="Neutral outlook with high IV. Collect premium while the stock stays within a range.",
                    probability=0.65,
                    suggested_strikes=[put_strike, call_strike],
                ))

        elif vol_regime == Volatility.LOW:
            # Low IV + Neutral → Long Straddle or Calendar Spread
            atm_strike = nearest_exp.get("summary", {}).get("atm_strike", current_price)
            recommendations.append(StrategyRecommendation(
                name="Long Straddle",
                direction="neutral",
                risk_level="high",
                max_profit="Unlimited (on upside) or large (on downside)",
                max_loss="Combined premium paid",
                description=f"Buy ATM call + buy ATM put at ${atm_strike}. "
                            f"IV is low ({avg_iv:.1%}) — cheap entry for a volatility breakout.",
                when_to_use="Expecting a big move but unsure of direction. Low IV entry is ideal.",
                probability=0.25,
                suggested_strikes=[atm_strike],
            ))

        else:
            # Normal IV + Neutral → Calendar Spread or Covered Call
            recommendations.append(StrategyRecommendation(
                name="Calendar Spread (Time Spread)",
                direction="neutral",
                risk_level="low",
                max_profit="Varies (time decay of short option)",
                max_loss="Net debit paid",
                description=f"Sell a near-term ATM call at ${current_price}, buy a longer-term one. "
                            f"Profits from time decay of the near-term option.",
                when_to_use="Neutral outlook, normal IV. Theta decay in the near expiration benefits you.",
                probability=0.55,
                suggested_strikes=[current_price],
            ))

    # ----- Universal / Income Strategies -----

    # Cash-Secured Put (if there's enough put data)
    if puts and current_price:
        otm_put = [p for p in puts if 0.85 * current_price <= p["strike"] <= 0.97 * current_price]
        if otm_put:
            liquid_put = sorted(otm_put, key=lambda p: p["volume"] + p["open_interest"], reverse=True)[0]
            recommendations.append(StrategyRecommendation(
                name="Cash-Secured Put",
                direction="neutral/bullish",
                risk_level="low",
                max_profit="Premium received",
                max_loss=f"Strike price (${liquid_put['strike']}) - premium, if assigned",
                description=f"Sell a put at ${liquid_put['strike']} to collect premium. "
                            f"Willing to buy the stock at a discount if assigned.",
                when_to_use="Income generation. Bullish-neutral on the stock, willing to buy at a lower price.",
                probability=0.70,
                suggested_strikes=[liquid_put["strike"]],
            ))

    # Covered Call (if expecting sideways/upward)
    if sentiment in (Sentiment.NEUTRAL, Sentiment.SLIGHTLY_BULLISH) and calls and current_price:
        otm_call = [c for c in calls if 1.02 * current_price <= c["strike"] <= 1.15 * current_price]
        if otm_call:
            liquid_call = sorted(otm_call, key=lambda c: c["volume"] + c["open_interest"], reverse=True)[0]
            recommendations.append(StrategyRecommendation(
                name="Covered Call (Buy-Write)",
                direction="neutral/bullish",
                risk_level="low",
                max_profit=f"Premium + stock appreciation up to ${liquid_call['strike']}",
                max_loss="Full stock value (if stock drops to zero)",
                description=f"Own the stock, sell a call at ${liquid_call['strike']}. "
                            f"Collect premium, cap upside.",
                when_to_use="Own the stock, neutral-to-slightly bullish outlook. Generate income.",
                probability=0.65,
                suggested_strikes=[liquid_call["strike"]],
            ))

    # Sort by score (probability) descending
    recommendations.sort(key=lambda r: r.probability, reverse=True)

    # Attach metadata
    return {
        "ticker": data.get("ticker"),
        "company_name": data.get("company_name"),
        "current_price": current_price,
        "analysis_date": data.get("fetch_time", ""),
        "nearest_expiration": expiry,
        "days_to_expiry": days_to_expiry,
        "sentiment": {
            "label": sentiment.value,
            "confidence": round(confidence, 2),
        },
        "volatility": {
            "label": vol_regime.value,
            "implied_volatility": round(avg_iv, 4) if isinstance(avg_iv, float) else avg_iv,
        },
        "recommendations": [r.to_dict() for r in recommendations[:5]],  # Top 5
        "disclaimer": "This is for educational/informational purposes only. Not financial advice. "
                       "Options trading involves substantial risk. Do your own due diligence.",
    }


def main():
    """CLI entry point: read JSON from stdin or file, output recommendations."""
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    result = recommend_strategies(data)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()